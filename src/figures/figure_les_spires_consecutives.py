#!/usr/bin/env python3
"""Sur quel objet peut-on VERIFIER trente et une spires ?

⚠⚠⚠ CETTE FIGURE NE CLASSE PAS LES ROULEAUX PAR DIFFICULTE — elle dit lesquels publient de quoi
VERIFIER quoi que ce soit. `31` §10 inscrit au calendrier de choisir le rouleau par sa part
comprimee, et `combien_de_fenetres` a montre que ce critere coute 315 fois son budget. La
question qui le precede est gratuite, et sa reponse elimine les treize d'un coup.

⚠⚠ LE PANNEAU A porte la grandeur de l'OBJECTIF, pas celle de l'encre : le nombre de spires
CONSECUTIVES publiees, parce que c'est exactement la longueur de marche contre laquelle une
portee peut se mesurer. LE PANNEAU B montre pourquoi un compte ne suffit pas : deux corpus de
meme taille ne se valent pas si l'un est troue, le trou etant precisement l'endroit ou la marche
cesserait d'etre verifiable.

Usage :
    uv run python src/figures/figure_les_spires_consecutives.py --verifier
    uv run python src/figures/figure_les_spires_consecutives.py \\
        --sortie docs/images/81_les_spires_consecutives.png
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
MESURE = RACINE / "docs" / "mesures" / "les_spires_consecutives_publiees.json"
# ⚠⚠ LA LIMITE DU CRITERE EST LUE DANS LA MESURE DE LA MARCHE, jamais retapee : le saut
# geometrique du bras 7 est ce qui empeche de lire un compte de rangs comme une portee, donc son
# chiffre doit venir du fichier qui l'a mesure.
MARCHE = RACINE / "docs" / "mesures" / "la_portee_du_raccrochage.json"
OBJET_COURANT = "PHerc0500P2"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
ROUGE = (188, 68, 52)
VERT = (76, 122, 84)
BLEU = (54, 88, 132)
GRIS = (196, 196, 196)
CADRE = (200, 200, 200)


def avec_corpus(m: dict) -> list[dict]:
    """Les objets qui publient au moins un rang, du plus long corpus au plus court."""
    return [x for x in m["lignes"] if x["rangs"] > 0]


def le_trou_de_la_marche() -> dict | None:
    """Le bras que le corpus publie hors du pas nominal, lu dans la mesure de la marche.

    ⚠⚠⚠ C'EST LA LIMITE DU CRITERE DE CETTE FIGURE. Compter des rangs compte des NOMS ; deux
    spires voisines par leur numero peuvent etre a sept feuilles l'une de l'autre dans la
    matiere. Sans ce chiffre, la figure se lirait comme si un compte de rangs etait une portee.
    """
    if not MARCHE.is_file():
        return None
    d = json.loads(MARCHE.read_text())
    hors = [b for b in d.get("bras_du_corpus", []) if not b["au_pas_nominal"]]
    if not hors:
        return None
    pire = max(hors, key=lambda b: b["ecart_au_pas_um"])
    return {"bras": pire["bras"], "de": pire["de"], "vers": pire["vers"],
            "ecart_um": pire["ecart_um"], "feuilles": pire["ecart_um"] / d["demi_feuille_um"] / 2,
            "autorise": d["bras_au_pas_nominal"], "bras": pire["bras"],
            "communs": d["bras_communs"]}


def prose(m: dict) -> list[str]:
    porteurs = m["portent_le_prix"]
    par = {x["nom"]: x for x in m["lignes"]}
    courant = par[OBJET_COURANT]
    trou = le_trou_de_la_marche()
    limite = ([f"⚠⚠⚠ ET LA LIMITE DU CRITERE, MESUREE : compter des rangs compte des NOMS. sur "
               f"{OBJET_COURANT}, les spires {trou['de']} et {trou['vers']} se suivent par leur "
               f"NUMERO et sont a {trou['ecart_um']:.1f} µm l'une de l'autre, soit "
               f"{trou['feuilles']:.1f} feuilles — donc le corpus n'autorise que "
               f"{trou['autorise']} bras sur {trou['communs']}. un corpus de 120 rangs peut "
               "porter le meme saut, et le compte des noms ne le verra pas : le critere est "
               "NECESSAIRE et NON SUFFISANT, et le verifier coute un telechargement."]
              if trou else [])
    return [
        f"le prix demande {m['spires_du_prix']} spires — c'est l'etat de l'art, "
        "PHerc1667 deroule a la main, ~25 h par spire, ~775 h au total. une portee est un "
        "nombre de spires traversees avant que l'erreur depasse la demi-feuille, donc elle ne "
        "se mesure que jusqu'ou le corpus publie des spires CONSECUTIVES : au-dela du dernier "
        "rang d'affilee il n'existe plus rien contre quoi dire qu'on a franchi une spire de "
        "plus.",
        f"⚠⚠⚠ PANNEAU A — LES TREIZE ROULEAUX DU PRIX SONT A ZERO. "
        f"{len(m['du_prix_sans_segment'])} des treize ne publient AUCUN segment ; les deux qui "
        "en publient (PHerc0800, PHerc1447) ne publient que des auto_grown_*, des morceaux SANS "
        f"RANG DE SPIRE. les {len(m['du_prix_sans_rang'])} sont donc a zero rang publie : le "
        "classement de `16` designe un objet sur lequel il n'existe ni ancre pour partir, ni "
        "verite de terrain pour dire jusqu'ou on est alle. ce n'est pas que le critere coute "
        "cher, c'est que sa reponse n'est pas executable.",
        f"⚠⚠ PANNEAU B — UN COMPTE NE SUFFIT PAS, IL FAUT UNE SUITE. PHerc1667, l'objet des 775 "
        f"heures, publie {par['PHerc1667']['rangs']} rangs sur une etendue de "
        f"{par['PHerc1667']['etendue']} — donc {par['PHerc1667']['trous']} trous, et sa plus "
        f"longue suite tombe a {par['PHerc1667']['suite']}. un trou ne se recolle pas : c'est "
        "exactement l'endroit ou la marche cesserait d'etre verifiable.",
        f"★★ TROIS OBJETS SEULEMENT portent les {m['spires_du_prix']} spires : "
        + " · ".join(f"{n} ({par[n]['suite']})" for n in porteurs)
        + f". et l'objet courant, {OBJET_COURANT}, plafonne a {courant['suite']} — moins de la "
        f"moitie. sur lui, tenir {m['spires_du_prix']} spires n'est pas seulement difficile : "
        "c'est INVERIFIABLE, faute de quoi que ce soit a comparer au-dela de la treizieme.",
        "⚠ ce que la mesure ne dit PAS : que les treize soient des rouleaux difficiles. zero "
        "segment publie est un fait sur l'effort de la communaute, pas sur le papyrus. mais le "
        "prix se gagne en livrant une image docker qu'ILS lancent sur un resultat verifiable, "
        "et un objet sans verite de terrain ne permet ni de developper ni de prouver quoi que "
        "ce soit — donc le fait, quelle qu'en soit la cause, decide quand meme.",
        "⚠ l'index est un CACHE, pas une autorite. les comptes cites ont ete confrontes a S3 "
        "pour les objets nommes ici ; un seul ecart trouve (PHerc1447 : 15 en cache, 16 sur "
        "S3), sans effet sur le verdict puisqu'aucun de ses segments ne porte de rang. le "
        "changement d'objet, lui, reste une decision de l'auteur : cette figure lui donne le "
        "chiffre, pas le choix.",
        *limite,
    ]


def panneau_barres(art, x0, y0, pw, ph, m, petit) -> None:
    """Le nombre de spires consecutives par objet, contre les 31 que le prix demande."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "spires CONSECUTIVES publiees · ★ = l'un des treize du prix",
             fill=DISCRET, font=petit)
    lignes = [x for x in m["lignes"] if x["rangs"] > 0 or x["du_prix"]]
    gauche, droite = x0 + 96, x0 + pw - 36
    haut = y0 + 40
    pas = min(17, (ph - 62) / max(1, len(lignes)))
    maxi = max(1, max(x["suite"] for x in lignes))

    def px(v: float) -> float:
        return gauche + (droite - gauche) * v / maxi

    # ⚠⚠ LES 31 DU PRIX SONT TRACEES SUR LE GRAPHE, pas racontees dans la prose : c'est le seuil
    # qui trie les objets, donc il doit se lire sans etre cherche.
    xs = px(m["spires_du_prix"])
    art.line([xs, haut - 4, xs, haut + pas * len(lignes) + 4], fill=ROUGE)
    art.text((xs + 3, haut - 15), f"les {m['spires_du_prix']} du prix", fill=ROUGE, font=petit)
    for i, x in enumerate(lignes):
        y = haut + i * pas
        marque = "★" if x["du_prix"] else " "
        coul = ROUGE if x["du_prix"] else (VERT if x["porte_le_prix"] else BLEU)
        art.text((x0 + 8, y - 1), f"{marque}{x['nom']}", fill=coul, font=petit)
        if x["suite"]:
            art.rectangle([gauche, y + 1, px(x["suite"]), y + pas - 4], fill=coul)
            art.text((px(x["suite"]) + 4, y - 1), str(x["suite"]), fill=coul, font=petit)
        else:
            # ⚠ UN ZERO DOIT SE VOIR. Une barre de longueur nulle est indistinguable d'une ligne
            # qu'on a oublie de dessiner, et c'est justement le zero qui porte le verdict.
            art.line([gauche, y + pas / 2 - 1, gauche + 6, y + pas / 2 - 1], fill=GRIS, width=2)
            art.text((gauche + 10, y - 1), "aucun rang publie", fill=GRIS, font=petit)
        if x["nom"] == OBJET_COURANT:
            art.text((px(x["suite"]) + 26, y - 1), "← l'objet courant", fill=TEXTE, font=petit)
    art.text((x0 + 8, y0 + ph - 18), "abscisse : plus longue suite de rangs sans trou",
             fill=DISCRET, font=petit)


def panneau_bande(art, x0, y0, pw, ph, m, petit) -> int:
    """Chaque rang publie, objet par objet : une suite pleine contre un corpus troue.

    Rend le nombre de cellules PEINTES, et ce n'est pas un detail de sortie : c'est ce qui
    permet a la batterie de verifier que la legende dit vrai. Un panneau qui ne peindrait que
    les plus longues suites rendrait un compte plus petit que le nombre de rangs publies.
    """
    peintes = 0
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "les rangs publies, un par cellule · plein : publie · vide : non",
             fill=DISCRET, font=petit)
    corpus = avec_corpus(m)
    rang_max = max(x["suite_a"] for x in corpus)
    gauche, droite = x0 + 96, x0 + pw - 58
    haut = y0 + 40
    pas = min(46, (ph - 66) / max(1, len(corpus)))
    cell = (droite - gauche) / (rang_max + 1)
    for i, x in enumerate(corpus):
        y = haut + i * pas
        coul = VERT if x["porte_le_prix"] else BLEU
        art.text((x0 + 8, y + pas / 2 - 12), x["nom"], fill=coul, font=petit)
        rangs = x["rangs_liste"]
        # ⚠⚠ L'ETENDUE EST DESSINEE EN CREUX SOUS LES RANGS, sinon un corpus troue et un corpus
        # court se ressemblent : c'est le contraste entre les deux qui porte l'information.
        art.rectangle([gauche + min(rangs) * cell, y + 1,
                       gauche + (max(rangs) + 1) * cell, y + pas - 7], outline=GRIS)
        # ⚠⚠⚠ CHAQUE RANG PUBLIE EST PEINT, y compris les isoles. La legende dit « plein :
        # publie » : n'en dessiner que la plus longue suite ferait passer les trois spires
        # isolees de PHerc1667 pour non publiees, donc mentir a l'endroit exact ou cette
        # figure prend son verdict.
        for r in rangs:
            art.rectangle([gauche + r * cell, y + 1, gauche + (r + 1) * cell, y + pas - 7],
                          fill=coul)
            peintes += 1
        # ⭐ La plus longue suite est SOULIGNEE, parce que c'est elle qui plafonne la portee —
        # et sur un corpus troue elle ne se voit pas dans le remplissage seul.
        a, b = x["suite_de"], x["suite_a"]
        art.line([gauche + a * cell, y + pas - 5, gauche + (b + 1) * cell, y + pas - 5],
                 fill=TEXTE, width=2)
        art.text((gauche + (max(rangs) + 1) * cell + 4, y + pas / 2 - 12),
                 f"{x['suite']}" + (f" · {x['trous']} trous" if x["trous"] else ""),
                 fill=coul, font=petit)
    for g in (0, 30, 60, 90, 120):
        if g <= rang_max:
            art.line([gauche + g * cell, haut - 8, gauche + g * cell, haut - 3], fill=DISCRET)
            art.text((gauche + g * cell - 7, haut - 20), str(g), fill=DISCRET, font=petit)
    # ⚠ LA LEGENDE EST MESUREE CONTRE LE PANNEAU, pas ajustee a l'oeil : une legende plus large
    # que son cadre est coupee a l'affichage, donc une legende qu'on croit ecrite et qui ne l'est
    # pas. La premiere version debordait de dix-neuf pixels.
    bas = (f"abscisse : le rang, 0 a {rang_max} · cadre : l'etendue · trait : la suite")
    art.text((x0 + 8, y0 + ph - 18), bas, fill=DISCRET, font=petit)
    return peintes, petit.getbbox(bas)[2] + 16


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    marge, pw, ecart, ph = 38, 470, 34, 396
    largeur_utile = pw * 2 + ecart
    for coupe in (140, 132, 124, 116, 108, 100):
        lignes = couper(prose(m), coupe)
        if max(moyen.getbbox(x)[2] for x in lignes) <= largeur_utile:
            break
    L = marge * 2 + largeur_utile
    H = 104 + ph + 42 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(toile)
    art.text((marge, 16), "Sur quel objet peut-on VERIFIER trente et une spires ?",
             fill=TEXTE, font=gros)
    art.text((marge, 40),
             f"{m['echantillons']} echantillons publies · {len(m['du_prix_sans_rang'])}/13 "
             f"rouleaux du prix sans un seul rang de spire · {len(m['portent_le_prix'])} objets "
             f"portent les {m['spires_du_prix']}",
             fill=DISCRET, font=moyen)
    titres = ("A · combien de spires d'affilee chaque objet publie",
              "B · ou elles tombent, et ou le corpus est troue")
    for j, t in enumerate(titres):
        art.text((marge + j * (pw + ecart), 76), t, fill=TEXTE, font=moyen)
    panneau_barres(art, marge, 104, pw, ph, m, petit)
    peintes, legende_bande = panneau_bande(art, marge + pw + ecart, 104, pw, ph, m, petit)
    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"objets": len(m["lignes"]), "corpus": len(avec_corpus(m)), "titres": titres,
            "cellules_peintes": peintes, "legende_bande": legende_bande,
            "panneau": pw,
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
    # ⚠⚠ LE VERDICT DE LA FIGURE DOIT ÊTRE CELUI DE LA MESURE, jamais une phrase qui a survécu à
    # un changement de chiffre. Chacun de ces contrôles lit le JSON, pas le texte.
    v("les treize du prix sont bien tous à zéro rang", len(m["du_prix_sans_rang"]) == 13,
      str(m["du_prix_sans_rang"]))
    par = {x["nom"]: x for x in m["lignes"]}
    v("l'objet courant est dans la mesure", OBJET_COURANT in par)
    v("... et il ne porte pas les 31", not par[OBJET_COURANT]["porte_le_prix"],
      f"suite={par[OBJET_COURANT]['suite']}")
    v("les porteurs cités par la prose sont ceux de la mesure",
      all(n in par and par[n]["porte_le_prix"] for n in m["portent_le_prix"]),
      str(m["portent_le_prix"]))
    # ⚠ LE PANNEAU B N'A DE SENS QUE S'IL Y A UN CORPUS TROUÉ À MONTRER : sans lui, l'étendue en
    # creux serait partout confondue avec la suite pleine et le panneau ne dirait rien.
    troues = [x["nom"] for x in avec_corpus(m) if x["trous"]]
    v("au moins un corpus est troué, sinon le panneau B ne montre rien", bool(troues),
      str(troues))
    v("... et PHerc1667, l'objet des 775 heures, en est un", "PHerc1667" in troues)
    # ⚠⚠⚠ LA FIGURE DOIT PORTER SA PROPRE LIMITE, sinon elle fait lire un compte de rangs comme
    # une portee. Le chiffre du saut est LU dans la mesure de la marche, donc il ne peut pas
    # dériver du fichier qui l'a établi.
    trou = le_trou_de_la_marche()
    v("le saut géométrique est lu dans la mesure de la marche, pas retapé",
      trou is not None and trou["ecart_um"] > 900, str(trou))
    if trou:
        v("... et la prose de la figure le porte",
          any(f"{trou['ecart_um']:.1f}" in x for x in prose(m)))
        v("... et il dit bien que le corpus autorise moins de bras qu'il en publie",
          trou["autorise"] < trou["communs"],
          f"{trou['autorise']} sur {trou['communs']}")

    sortie = RACINE / "docs" / "images" / "81_les_spires_consecutives.png"
    d = dessiner(m, sortie)
    v("la figure est écrite", sortie.is_file() and sortie.stat().st_size > 8000,
      f"{sortie.stat().st_size if sortie.is_file() else 0} octets")
    # ⚠ Une ligne de prose plus large que la toile est une ligne coupée à l'affichage, donc un
    # chiffre publié que personne ne lit.
    v("aucune ligne de prose ne déborde",
      all(w <= d["largeur_utile"] for _, w in d["prose"]),
      f"max {max(w for _, w in d['prose'])} pour {d['largeur_utile']}")
    v("les deux panneaux sont titrés", len(d["titres"]) == 2)
    # ⚠⚠⚠ LA LÉGENDE DIT « plein : publié », DONC CHAQUE RANG PUBLIÉ DOIT ÊTRE PEINT. La
    # première version ne peignait que la plus longue suite : les trois spires isolées de
    # PHerc1667 sortaient vides sous une légende qui affirmait le contraire. Ce contrôle est ce
    # qui empêche la figure de mentir à l'endroit exact où elle prend son verdict.
    attendu = sum(x["rangs"] for x in avec_corpus(m))
    v("chaque rang publié est peint, pas seulement les suites",
      d["cellules_peintes"] == attendu, f"{d['cellules_peintes']} peintes pour {attendu} rangs")
    v("... et la liste des rangs est complète dans la mesure",
      all(len(x["rangs_liste"]) == x["rangs"] for x in m["lignes"]))
    v("la légende du panneau B tient dans son cadre",
      d["legende_bande"] <= d["panneau"], f"{d['legende_bande']} pour {d['panneau']}")

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "81_les_spires_consecutives.png")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    m = json.loads(MESURE.read_text())
    d = dessiner(m, a.sortie)
    print(f"écrit : {d['sortie']}  ({d['objets']} objets, {d['corpus']} avec corpus)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
