#!/usr/bin/env python3
"""Le pas inter-feuilles, lu sur les transferts que l'humain a reussis.

⚠⚠⚠ CETTE FIGURE PORTE UNE RETRACTATION FAITE AVANT PUBLICATION. Le panneau A montre que
l'etendue declaree d'une bande EST son nombre de tours mesure. Le panneau B montre le pas — et le
balayage de fenetre qui refute le « gradient » que la pente brute suggerait.

Usage :
    uv run python src/figures/figure_le_pas_lu_sur_les_transferts.py --verifier
    uv run python src/figures/figure_le_pas_lu_sur_les_transferts.py \\
        --sortie docs/images/91_le_pas_lu_sur_les_transferts.png
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "commun"))
from figure_commune import Tracee, police, prose_tracable  # noqa: E402
from figure_le_residu_est_une_translation import couper  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
MESURE = RACINE / "docs" / "mesures" / "le_pas_lu_sur_les_transferts.json"
ATLAS_UM = 182.4

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
ROUGE = (188, 68, 52)
VERT = (76, 122, 84)
BLEU = (54, 88, 132)
AMBRE = (176, 132, 44)
PALE = (231, 240, 231)
GRIS = (196, 196, 196)
CADRE = (200, 200, 200)


def prose(m: dict) -> list[str]:
    e, p, c = (m["letendue_est_le_nombre_de_tours"], m["pas_sur_les_bandes_longues_um"],
               m["pas_sur_les_bandes_courtes_um"])
    bal = m["balayage_de_fenetre_sur_une_seule_bande"]
    o = m["orientation_de_la_grille"]
    return [
        f"`84` etablit que {m['fragment']} publie 92 franchissements de spire contenus dans une "
        "seule maille, et zero partout ailleurs. une bande est donc un transfert de spire a spire "
        "DEJA FAIT A LA MAIN, et sa geometrie se lit sans toucher au volume — c'est la seule "
        "verite de terrain du goulot.",
        f"★★★ PANNEAU A — L'ETENDUE DECLAREE EST LE NOMBRE DE TOURS. en deroulant l'angle le long "
        f"d'une ligne de grille, l'ecart median vaut {e['ecart_median_tours']:+.2f} tour, et "
        f"{e['bandes_a_moins_dun_dixieme_de_tour']} bandes sur {m['bandes']} sont a moins d'un "
        f"dixieme de tour. les noms ne sont pas des etiquettes, c'est la geometrie. ⚠ une "
        f"exception nommee : {e['la_pire']}, {e['pire_ecart']:.2f} tour d'ecart.",
        f"⚠ et la lecture est valide parce qu'une LIGNE de grille est iso-z — ecart-type "
        f"{o['ecart_type_z_le_long_dune_ligne_mm']} mm contre "
        f"{o['ecart_type_z_le_long_dune_colonne_mm']} mm pour une colonne, qui court sur tout le "
        "rouleau. la pente est donc lue a hauteur constante. verifie, pas suppose.",
        f"★★ PANNEAU B — LE PAS VAUT {p['median']:.0f} µm sur les {p['bandes']} bandes d'au moins "
        f"{m['tours_minimum']} tours ({p['min']:.0f} a {p['max']:.0f}). l'atlas `winding-ruler` "
        f"publie {ATLAS_UM} µm pour cet objet, par un chemin ENTIEREMENT INDEPENDANT — "
        "predictions de surface le long de rayons contre maillages publies par des humains. deux "
        "instruments qui ne partagent rien s'accordent.",
        f"⚠⚠⚠ ET UN GRADIENT RETRACTE AVANT D'ETRE PUBLIE. les {c['bandes']} bandes courtes "
        f"rendent {c['median']:.0f} µm, soit un facteur "
        f"{c['median'] / p['median']:.1f} qu'on lirait comme une delamination du bord. controle "
        "sur UNE SEULE bande de dix tours, donc a pas constant par construction : "
        + " · ".join(f"{x['fenetre_tours']} tour(s) → {x['pente_um_par_tour']:.0f} µm"
                     for x in bal)
        + ". le pas ne change pas, seule la fenetre change.",
        "★ LA REGLE QUI EN SORT, ET ELLE VAUT POUR TOUT MARCHEUR : on ne mesure pas le pas d'un "
        "enroulement sur un arc court. les bandes du bord n'en couvrent que deux, donc elles ne "
        "peuvent pas le mesurer — et les croire ferait croire a une delamination qui n'est pas "
        "mesuree ici.",
        "⚠⚠ ET LA CAUSE N'EST PAS ETABLIE, ce qui est ecrit plutot que devine. deux mecanismes "
        "testes sur fixture, aucun ne rend l'ampleur : une section OVALE ne gonfle pas la pente, "
        "elle la DEGONFLE (200,3 sur huit tours contre 183,2 sur un — c'etait ma premiere "
        "explication, et elle est fausse) ; un centre DECALE gonfle bien, 200 / 216 / 233 / 270 "
        "pour 0, 0,5, 1 et 2 mm, mais il faudrait des dizaines de millimetres pour atteindre "
        "1817.",
        "★ le controle tient SANS la cause : reproduire un biais sur des donnees dont on connait "
        "la reponse n'exige pas de l'expliquer pour le refuter. les deux explications refutees "
        "sont gardees dans les controles, pour qu'on ne les re-propose pas.",
    ]


def panneau_tours(art, x0, y0, pw, ph, m, petit) -> int:
    """Les tours mesurés contre l'étendue déclarée."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "tours mesurés contre étendue déclarée",
             fill=DISCRET, font=petit)
    lignes = m["lignes"]
    gauche, droite = x0 + 56, x0 + pw - 24
    base, sommet = y0 + ph - 44, y0 + 34
    hi = max(max(x["etendue"] for x in lignes),
             max(x["tours_median"] for x in lignes)) * 1.05

    def p(v):
        return gauche + (droite - gauche) * v / hi

    def q(v):
        return base - (base - sommet) * v / hi

    # ⚠⚠ LA DIAGONALE EST TRACEE : « mesuré == déclaré » est une identité, et sans la droite
    # y = x le lecteur devrait la reconstituer de tête.
    art.line([p(0), q(0), p(hi), q(hi)], fill=GRIS)
    art.text((p(hi) - 60, q(hi) + 6), "mesuré = déclaré", fill=DISCRET, font=petit)
    art.line([gauche, base, droite, base], fill=TEXTE)
    art.line([gauche, base, gauche, sommet], fill=TEXTE)
    for g in (0, int(hi / 2), int(hi)):
        art.text((p(g) - 6, base + 6), str(g), fill=DISCRET, font=petit)
        art.text((gauche - 22, q(g) - 6), str(g), fill=DISCRET, font=petit)
    hors = 0
    for x in lignes:
        cx, cy = p(x["etendue"]), q(x["tours_median"])
        loin = abs(x["ecart_tours"]) > 0.5
        art.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=ROUGE if loin else BLEU)
        if loin:
            hors += 1
            art.text((cx + 7, cy - 6),
                     f"w{x['de']:03d}-{x['a']:03d} : {x['tours_median']:.2f} pour "
                     f"{x['etendue']}", fill=ROUGE, font=petit)
    art.text((x0 + 8, y0 + ph - 18),
             "abscisse : étendue déclarée · ordonnée : tours mesurés", fill=DISCRET, font=petit)
    return hors


def panneau_pas(art, x0, y0, pw, ph, m, petit) -> int:
    """Le pas par bande, et le balayage de fenêtre qui réfute le gradient."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "pas mesuré par bande, et le balayage qui réfute le gradient",
             fill=DISCRET, font=petit)
    lignes = m["lignes"]
    bal = m["balayage_de_fenetre_sur_une_seule_bande"]
    gauche, droite = x0 + 60, x0 + pw - 24
    # ⚠⚠ LA HAUTEUR DES DEUX SOUS-GRAPHES EST CALCULEE POUR LAISSER LEUR PLACE AUX
    # GRADUATIONS ET A LA LEGENDE : ma premiere version posait les graduations du bas
    # exactement sur la ligne de legende, et les deux se lisaient l'une par-dessus l'autre.
    h = (ph - 140) / 2
    haut = y0 + 32
    hi = max(max(x["pente_um_par_tour"] for x in lignes),
             max(x["pente_um_par_tour"] for x in bal)) * 1.05

    def q(v, base_y):
        return base_y - (base_y - (base_y - h)) * v / hi

    base1 = haut + h
    art.line([gauche, base1, droite, base1], fill=TEXTE)
    # ⭐ L'atlas est tracé : c'est la valeur avec laquelle on se compare.
    ya = q(ATLAS_UM, base1)
    art.line([gauche, ya, droite, ya], fill=VERT)
    art.text((gauche + 4, ya - 13), f"l'atlas : {ATLAS_UM} µm", fill=VERT, font=petit)
    pas_ = m["pas_sur_les_bandes_longues_um"]
    art.rectangle([gauche, q(pas_["max"], base1), droite, q(pas_["min"], base1)], fill=PALE)
    n = len(lignes)
    longues = 0
    for i, x in enumerate(lignes):
        cx = gauche + (droite - gauche) * i / max(1, n - 1)
        assez = x["etendue"] >= m["tours_minimum"]
        longues += assez
        art.ellipse([cx - 3, q(x["pente_um_par_tour"], base1) - 3,
                     cx + 3, q(x["pente_um_par_tour"], base1) + 3],
                    fill=BLEU if assez else ROUGE)
    art.text((x0 + 8, haut - 2), f"{int(hi)}", fill=DISCRET, font=petit)
    art.text((x0 + 8, base1 - 12), "0", fill=DISCRET, font=petit)
    art.text((x0 + 8, base1 + 6),
             f"bleu : ≥ {m['tours_minimum']} tours, la mesure · rouge : trop court",
             fill=DISCRET, font=petit)

    # --- le balayage, en dessous
    haut2 = base1 + 40
    base2 = haut2 + h
    art.line([gauche, base2, droite, base2], fill=TEXTE)
    art.line([gauche, q(ATLAS_UM, base2), droite, q(ATLAS_UM, base2)], fill=VERT)
    pts = []
    for i, x in enumerate(bal):
        cx = gauche + (droite - gauche) * i / max(1, len(bal) - 1)
        cy = q(x["pente_um_par_tour"], base2)
        pts.append((cx, cy))
        art.text((cx - 10, base2 + 6), f"{x['fenetre_tours']}", fill=DISCRET, font=petit)
    art.line(pts, fill=AMBRE, width=2)
    for (cx, cy), x in zip(pts, bal):
        art.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=AMBRE)
    art.text((x0 + 8, haut2 - 2), f"{int(hi)}", fill=DISCRET, font=petit)
    # ⚠ Le zero du second sous-graphe manquait : une ordonnee sans son origine laisse juger
    # l'amplitude a l'oeil.
    art.text((x0 + 8, base2 - 12), "0", fill=DISCRET, font=petit)
    art.text((gauche + 4, haut2 - 16),
             "UNE SEULE bande de 10 tours — pas constant par construction",
             fill=AMBRE, font=petit)
    art.text((x0 + 8, y0 + ph - 18),
             "abscisse du bas : largeur de la fenêtre d'ajustement, en tours",
             fill=DISCRET, font=petit)
    # ⚠⚠ L'ECART entre la derniere graduation et la legende est RENDU, pour qu'un controle
    # puisse refuser une superposition au lieu de la laisser a l'oeil.
    return longues, float(y0 + ph - 18 - (base2 + 6 + 12))


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    marge, pw, ecart, ph = 38, 470, 34, 400
    largeur_utile = pw * 2 + ecart
    for coupe in (140, 132, 124, 116, 108, 100):
        lignes = couper(prose(m), coupe)
        if max(moyen.getbbox(x)[2] for x in lignes) <= largeur_utile:
            break
    L = marge * 2 + largeur_utile
    H = 104 + ph + 42 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = Tracee(ImageDraw.Draw(toile))
    p = m["pas_sur_les_bandes_longues_um"]
    art.text((marge, 16),
             "Le pas inter-feuilles, lu sur les transferts que l'humain a réussis",
             fill=TEXTE, font=gros)
    art.text((marge, 40),
             f"{m['fragment']} · {m['bandes']} bandes · l'étendue déclarée EST le nombre de "
             f"tours · le pas vaut {p['median']:.0f} µm contre {ATLAS_UM} à l'atlas",
             fill=DISCRET, font=moyen)
    titres = ("A · les tours mesurés contre l'étendue déclarée",
              "B · le pas, et le balayage qui réfute le gradient")
    for j, t in enumerate(titres):
        art.text((marge + j * (pw + ecart), 76), t, fill=TEXTE, font=moyen)
    hors = panneau_tours(art, marge, 104, pw, ph, m, petit)
    longues, marge_legende = panneau_pas(art, marge + pw + ecart, 104, pw, ph, m, petit)
    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"titres": titres, "hors_diagonale": hors, "bandes_longues": longues,
            "marge_sous_les_graduations": marge_legende,
            "textes_dessines": art.textes,
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
    d = dessiner(m, RACINE / "docs" / "images" / "91_le_pas_lu_sur_les_transferts.png")
    v("la figure est écrite", Path(d["sortie"]).stat().st_size > 8000,
      f"{Path(d['sortie']).stat().st_size} octets")
    v("aucune ligne de prose ne déborde",
      all(w <= d["largeur_utile"] for _, w in d["prose"]),
      f"max {max(w for _, w in d['prose'])} pour {d['largeur_utile']}")
    from figure_commune import glyphes_manquants  # noqa: PLC0415
    absents = sorted(glyphes_manquants("".join(d["textes_dessines"])))
    v("aucun glyphe du texte DESSINÉ n'est manquant", not absents, str(absents))
    # ⭐⭐⭐ L'EXCEPTION EST MARQUÉE : une figure qui ne montrerait que l'accord cacherait la
    # seule bande qui n'accorde pas.
    e = m["letendue_est_le_nombre_de_tours"]
    v("la bande hors diagonale est marquée", d["hors_diagonale"] == 1,
      f"{d['hors_diagonale']} — {e['la_pire']}")
    v("... et l'accord est celui de la mesure", abs(e["ecart_median_tours"]) < 0.05)
    # ⭐⭐ LE BALAYAGE EST DESSINÉ : c'est lui la rétractation, et l'écrire sans le montrer
    # demanderait qu'on le croie.
    v("le balayage de fenêtre est dessiné",
      len(m["balayage_de_fenetre_sur_une_seule_bande"]) >= 4,
      str(len(m["balayage_de_fenetre_sur_une_seule_bande"])))
    v("... et il gonfle bien quand la fenêtre rétrécit", m["le_gradient_est_un_artefact"])
    # ⚠⚠ LES DEUX EXPLICATIONS RÉFUTÉES SONT DANS LA PROSE, sinon on les re-proposerait.
    v("la prose dit que l'ovale DÉGONFLE", any("DEGONFLE" in x for x in prose(m)))
    v("... et que le centre décalé ne suffit pas",
      any("des dizaines de millimetres" in x for x in prose(m)))
    v("... et que la cause n'est PAS établie",
      any("CAUSE N'EST PAS ETABLIE" in x for x in prose(m)))
    # ⚠ La condition de validité de la lecture est dite.
    v("la prose dit que les lignes sont iso-z",
      any("iso-z" in x for x in prose(m)) and m["orientation_de_la_grille"]["les_lignes_sont_iso_z"])
    # ⚠⚠ LA LEGENDE NE DOIT PAS RECOUVRIR LES GRADUATIONS. Ma premiere version les posait sur
    # la meme ligne, et les deux se lisaient l'une par-dessus l'autre.
    v("la légende du bas ne recouvre pas les graduations",
      d["marge_sous_les_graduations"] > 0,
      f"{d['marge_sous_les_graduations']:.0f} px de marge")
    v("les deux panneaux sont titrés", len(d["titres"]) == 2)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "91_le_pas_lu_sur_les_transferts.png")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    d = dessiner(json.loads(MESURE.read_text()), a.sortie)
    print(f"écrit : {d['sortie']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
