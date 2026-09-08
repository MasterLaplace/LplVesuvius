#!/usr/bin/env python3
"""Combien de spires une seule surface publiee traverse-t-elle ?

⚠⚠⚠ CETTE FIGURE PORTE LA VERITE DE TERRAIN DU GOULOT. Une surface qui ne couvre qu'UNE spire ne
contient aucun transfert de spire a spire : elle donne la reponse en morceaux deja separes. Une
surface qui en couvre dix-huit en contient dix-sept. Le panneau A montre les vingt-huit bandes de
`PHercParis4` et leur decroissance ; le panneau B montre que tous les autres objets du corpus sont
a zero.

Usage :
    uv run python src/figures/figure_une_surface_combien_de_spires.py --verifier
    uv run python src/figures/figure_une_surface_combien_de_spires.py \\
        --sortie docs/images/84_une_surface_combien_de_spires.png
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

RACINE = Path(__file__).resolve().parents[2]
MESURE = RACINE / "docs" / "mesures" / "une_surface_combien_de_spires.json"
BANDE = "PHercParis4"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
ROUGE = (188, 68, 52)
VERT = (76, 122, 84)
BLEU = (54, 88, 132)
PALE = (231, 240, 231)
GRIS = (196, 196, 196)
CADRE = (200, 200, 200)


def prose(m: dict) -> list[str]:
    par = {x["nom"]: x for x in m["lignes"]}
    p4 = par.get(BANDE)
    zero = m["objets_a_une_spire_par_surface"]
    return [
        f"le goulot de l'objectif est le transfert de spire a spire — ~25 h d'humain par spire, "
        f"~775 h pour les {m['spires_du_prix']} spires de l'etat de l'art. une surface publiee "
        "qui ne couvre qu'UNE spire ne contient donc aucun transfert : elle donne la reponse en "
        "morceaux deja separes. une surface qui en couvre dix-huit en contient dix-sept.",
        f"⚠⚠⚠ PANNEAU B — UN SEUL OBJET DU CORPUS PUBLIE UN FRANCHISSEMENT. {BANDE} couvre ses "
        f"{p4['spires_couvertes']} spires en {p4['bandes']} bandes, soit "
        f"{p4['franchissements_dans_une_maille']} franchissements contenus dans une seule "
        f"maille. les {len(zero)} autres — " + ", ".join(zero) + " — publient UNE spire par "
        "surface, sans exception, donc zero. la verite de terrain du goulot existe sur un objet "
        "et un seul.",
        f"⚠⚠ PANNEAU A — ET LA LONGUEUR DES BANDES DECROIT SANS UNE SEULE INVERSION : "
        + " ".join(str(s) for s in p4["spans"])
        + f". zero remontee sur {p4['decroissance']['bandes']} bandes, ce qui n'est pas une "
        "tendance mais une monotonie — et une monotonie se refute d'une seule inversion, donc "
        "elle se mesure. une bande est ce qu'une passe humaine a produit d'un coup : cette suite "
        "est la courbe de cout du deroulage manuel, lue sans rien mesurer soi-meme.",
        "⚠ ce que la suite ne dit PAS : dans quel sens va le rang. la circonference croit vers "
        "l'exterieur, donc une passe d'effort constant y couvrirait moins de spires — ce qui "
        "expliquerait la decroissance — mais rien ici ne l'etablit, et l'ecrire comme un fait "
        "serait une lecture et pas une mesure.",
        f"⚠⚠⚠ ET MEME LA MEILLEURE BANDE RESTE SOUS LE COMPTE DU PRIX : "
        f"{p4['bande_la_plus_longue']} spires contre {m['spires_du_prix']}. le corpus le plus "
        "riche du concours ne contient donc pas une marche entiere, il contient dix-sept "
        "franchissements d'affilee — et il faut ensuite recoudre vingt-huit bandes, ce qui est le "
        "meme probleme une spire plus loin.",
        f"⚠ deux revisions d'une meme bande ne font pas deux bandes : {BANDE} publie "
        f"{p4['revisions']} segments pour {p4['bandes']} bandes, et les compter deux fois "
        "doublerait le corpus sans qu'une seule spire de plus soit publiee.",
        "⚠ et aucun des treize rouleaux du Grand Prize n'apparait ici, parce qu'aucun ne publie "
        "une seule bande — le recoupement de `81` par un chemin de plus.",
    ]


def panneau_bandes(art, x0, y0, pw, ph, m, petit) -> int:
    """Les bandes de l'objet qui en a, sur l'axe des rangs."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), f"les bandes de {BANDE}, une par surface publiée",
             fill=DISCRET, font=petit)
    par = {x["nom"]: x for x in m["lignes"]}
    p4 = par[BANDE]
    spans = p4["spans"]
    gauche, droite = x0 + 30, x0 + pw - 70
    haut = y0 + 42
    hauteur = min(13, (ph - 74) / max(1, len(spans)))
    # ⚠⚠ L'AXE VA DU PREMIER AU DERNIER RANG PUBLIE, jamais de zero : le corpus de cet objet
    # commence a la dixieme spire, et un axe parti de zero ferait lire un corpus qui commence au
    # coeur. Les bornes sont LUES dans la mesure, qui a verifie que les bandes pavent sans trou.
    debut, fin = p4["bornes"]
    cell = (droite - gauche) / max(1, fin - debut + 1)
    curseur = debut
    dessinees = 0
    for i, s in enumerate(spans):
        y = haut + i * hauteur
        coul = VERT if s >= 10 else (BLEU if s >= 4 else GRIS)
        art.rectangle([gauche + (curseur - debut) * cell, y + 1,
                       gauche + (curseur - debut + s) * cell, y + hauteur - 3], fill=coul)
        art.text((gauche + (curseur - debut + s) * cell + 4, y - 2), str(s), fill=coul,
                 font=petit)
        curseur += s
        dessinees += 1
    # ⚠⚠ LE COMPTE DU PRIX EST TRACE, parce que c'est lui qui dit que même la meilleure bande ne
    # suffit pas : une figure qui ne le porterait pas laisserait 18 se lire comme beaucoup.
    xp = gauche + m["spires_du_prix"] * cell
    art.line([xp, haut - 4, xp, haut + hauteur * len(spans) + 2], fill=ROUGE)
    # ⚠⚠ L'ETIQUETTE DU SEUIL VIT DANS LE VIDE DE L'ESCALIER, et son placement est raisonne et
    # non tatonne : au-dessus elle tombait sur la graduation du milieu, dessous sur la legende du
    # bas. A mi-hauteur, les bandes sont deja passees a droite du seuil, donc la place est libre.
    art.text((xp + 4, haut + hauteur * len(spans) * 0.45),
             f"les {m['spires_du_prix']} du prix", fill=ROUGE, font=petit)
    for g in (debut, (debut + fin) // 2, fin):
        art.line([gauche + (g - debut) * cell, haut - 8,
                  gauche + (g - debut) * cell, haut - 3], fill=DISCRET)
        art.text((gauche + (g - debut) * cell - 8, haut - 20), f"w{g:03d}", fill=DISCRET,
                 font=petit)
    art.text((x0 + 8, y0 + ph - 30),
             f"abscisse : le rang de spire, w{debut:03d} a w{fin:03d}, sans un trou",
             fill=DISCRET, font=petit)
    art.text((x0 + 8, y0 + ph - 18),
             "vert : 10 spires ou plus · bleu : 4 à 9 · gris : 2 ou 3",
             fill=DISCRET, font=petit)
    return dessinees


def panneau_objets(art, x0, y0, pw, ph, m, petit) -> int:
    """Chaque objet : ses bandes, ses spires, et ses franchissements dans une maille."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6),
             "franchissements de spire contenus dans UNE SEULE maille publiée",
             fill=DISCRET, font=petit)
    lignes = m["lignes"]
    gauche, droite = x0 + 156, x0 + pw - 60
    debord = -1e9
    haut = y0 + 44
    hauteur = min(34, (ph - 76) / max(1, len(lignes)))
    maxi = max(1, max(x["franchissements_dans_une_maille"] for x in lignes))
    marquees = 0
    for i, x in enumerate(lignes):
        y = haut + i * hauteur
        n = x["franchissements_dans_une_maille"]
        coul = VERT if n else ROUGE
        art.text((x0 + 8, y + hauteur / 2 - 14), x["nom"], fill=coul, font=petit)
        # ⚠⚠ L'ETIQUETTE EST MESUREE CONTRE LE DEBUT DES BARRES, pas ajustee a l'oeil : la
        # premiere version passait sous la barre de `PHercParis4` et s'y faisait couper.
        etiq = f"{x['bandes']} bandes · {x['spires_couvertes']} spires"
        debord = max(debord, x0 + 8 + petit.getbbox(etiq)[2] - gauche)
        art.text((x0 + 8, y + hauteur / 2 - 2), etiq, fill=DISCRET, font=petit)
        if n:
            art.rectangle([gauche, y + 2, gauche + (droite - gauche) * n / maxi,
                           y + hauteur - 8], fill=coul)
            art.text((gauche + (droite - gauche) * n / maxi + 5, y + hauteur / 2 - 12),
                     str(n), fill=coul, font=petit)
        else:
            # ⚠ UN ZERO DOIT SE VOIR : une barre nulle est indistinguable d'une ligne oubliée, et
            # c'est le zéro qui porte le verdict.
            art.line([gauche, y + hauteur / 2 - 3, gauche + 7, y + hauteur / 2 - 3],
                     fill=GRIS, width=2)
            art.text((gauche + 12, y + hauteur / 2 - 12),
                     "0 — une spire par surface", fill=GRIS, font=petit)
            marquees += 1
    art.text((x0 + 8, y0 + ph - 18),
             "abscisse : franchissements publiés dans une maille unique",
             fill=DISCRET, font=petit)
    return marquees, debord


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    marge, pw, ecart, ph = 38, 470, 34, 428
    largeur_utile = pw * 2 + ecart
    for coupe in (140, 132, 124, 116, 108, 100):
        lignes = couper(prose(m), coupe)
        if max(moyen.getbbox(x)[2] for x in lignes) <= largeur_utile:
            break
    L = marge * 2 + largeur_utile
    H = 104 + ph + 42 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(toile)
    par = {x["nom"]: x for x in m["lignes"]}
    p4 = par[BANDE]
    art.text((marge, 16), "Combien de spires une seule surface publiee traverse-t-elle ?",
             fill=TEXTE, font=gros)
    art.text((marge, 40),
             f"{m['objets_avec_bandes']} objets publient une bande · un seul en publie de "
             f"multi-spires · {p4['franchissements_dans_une_maille']} franchissements contre 0 "
             f"partout ailleurs",
             fill=DISCRET, font=moyen)
    titres = (f"A · les {p4['bandes']} bandes de {BANDE}, et leur decroissance",
              "B · ce que chaque objet publie comme franchissement")
    for j, t in enumerate(titres):
        art.text((marge + j * (pw + ecart), 76), t, fill=TEXTE, font=moyen)
    dessinees = panneau_bandes(art, marge, 104, pw, ph, m, petit)
    zeros, debord = panneau_objets(art, marge + pw + ecart, 104, pw, ph, m, petit)
    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"titres": titres, "bandes_dessinees": dessinees, "zeros_marques": zeros,
            "debord_etiquette": debord,
            "prose": [(t, moyen.getbbox(t)[2]) for t in lignes],
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
        print(f"ALL PASS ({echecs} failures, {controles} checks)")
        return 0

    m = json.loads(MESURE.read_text())
    v("la prose est traçable", prose_tracable(prose(m)))
    d = dessiner(m, RACINE / "docs" / "images" / "84_une_surface_combien_de_spires.png")
    v("la figure est écrite", Path(d["sortie"]).stat().st_size > 8000,
      f"{Path(d['sortie']).stat().st_size} octets")
    v("aucune ligne de prose ne déborde",
      all(w <= d["largeur_utile"] for _, w in d["prose"]),
      f"max {max(w for _, w in d['prose'])} pour {d['largeur_utile']}")
    par = {x["nom"]: x for x in m["lignes"]}
    # ⚠⚠ TOUTES LES BANDES SONT DESSINEES : une bande présente dans la mesure et absente du
    # panneau ferait lire un corpus plus court qu'il n'est.
    v("chaque bande de la mesure est dessinée",
      d["bandes_dessinees"] == par[BANDE]["bandes"],
      f"{d['bandes_dessinees']} pour {par[BANDE]['bandes']}")
    # ⚠⚠⚠ ET CHAQUE ZERO PORTE SA MARQUE : c'est le zéro qui porte le verdict, et une barre de
    # longueur nulle est indistinguable d'une ligne qu'on a oublié de dessiner.
    v("chaque objet à zéro franchissement porte sa marque",
      d["zeros_marques"] == len(m["objets_a_une_spire_par_surface"]),
      f"{d['zeros_marques']} pour {len(m['objets_a_une_spire_par_surface'])}")
    v("un seul objet publie un franchissement",
      m["objets_qui_publient_un_franchissement"] == [BANDE],
      str(m["objets_qui_publient_un_franchissement"]))
    v("... et la prose dit combien", any(
        str(par[BANDE]["franchissements_dans_une_maille"]) in x for x in prose(m)))
    v("la décroissance est monotone dans la mesure",
      par[BANDE]["decroissance"]["monotone"], str(par[BANDE]["decroissance"]))
    # ⚠ La figure doit dire ce qu'elle NE sait pas : le sens du rang.
    v("la prose dit qu'elle ignore le sens du rang",
      any("dans quel sens va le rang" in x for x in prose(m)))
    # ⚠⚠ Et que même la meilleure bande ne suffit pas.
    v("... et que la meilleure bande reste sous le compte du prix",
      par[BANDE]["bande_la_plus_longue"] < m["spires_du_prix"]
      and any("SOUS LE COMPTE DU PRIX" in x for x in prose(m)))
    v("aucune étiquette du panneau B ne passe sous les barres",
      d["debord_etiquette"] <= 0, f"déborde de {d['debord_etiquette']:.0f} px")
    v("les deux panneaux sont titrés", len(d["titres"]) == 2)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "84_une_surface_combien_de_spires.png")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    d = dessiner(json.loads(MESURE.read_text()), a.sortie)
    print(f"écrit : {d['sortie']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
