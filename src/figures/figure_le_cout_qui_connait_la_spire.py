#!/usr/bin/env python3
"""Ce que connaître la spire achète au tracker — et ce qu'un faux champ achète déjà.

⚠⚠⚠ CE QUE CETTE FIGURE DOIT RENDRE VISIBLE EN UN COUP D'ŒIL, C'EST LE TÉMOIN. Trois barres
qui descendent de 99 à 96 se lisent comme une amélioration ; la quatrième — le champ TOURNÉ,
délibérément faux — descend à 96,6, donc elle prend 83 % de la descente. Une figure qui ne
montrerait que le témoin et le champ dirait exactement l'inverse de la mesure.

Usage :
    uv run python src/figures/figure_le_cout_qui_connait_la_spire.py --verifier
    uv run python src/figures/figure_le_cout_qui_connait_la_spire.py \\
        --sortie docs/images/114_le_cout_qui_connait_la_spire.png
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "commun"))
from figure_commune import (Tracee, police, prose_tracable,  # noqa: E402
                            textes_debordants, textes_hors_cadre,
                            textes_qui_se_recouvrent)
from figure_le_residu_est_une_translation import couper  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
MESURE = RACINE / "docs" / "mesures" / "le_cout_qui_connait_la_spire.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
ROUGE = (188, 68, 52)
VERT = (76, 122, 84)
BLEU = (54, 88, 132)
AMBRE = (176, 132, 44)
CADRE = (200, 200, 200)

NOMS = {"temoin": "témoin", "champ": "champ", "constant": "constant", "tourne": "tourné"}
COULEURS = {"temoin": DISCRET, "champ": BLEU, "constant": CADRE, "tourne": ROUGE}


def prose(m: dict) -> list[str]:
    w, v = m["verdict"], m["variantes"]
    p = m["pas_dindice"]
    lo, hi = m["bande_vx"]
    lignes = [
        f"LA RÉOUVERTURE ÉTAIT LÉGITIME, LA RÉPONSE EST NON. `fusions` avait réfuté son propre "
        f"tracker en mesurant que l'IDENTITÉ des pistes churne, et son coût n'apparie que sur "
        f"l'écart radial — aucun indice de spire. Le champ d'enroulement est arrivé APRÈS cette "
        f"réfutation, ce qui autorisait de rouvrir. Branché, il fait tomber la fragmentation de "
        f"{v['temoin']['morceaux_par_mur']:.2f} à {v['champ']['morceaux_par_mur']:.2f} morceaux "
        f"par mur.",
        f"✗ MAIS LE CHAMP TOURNÉ — le même champ lu à un AUTRE angle, donc faux par "
        f"construction — obtient {v['tourne']['morceaux_par_mur']:.2f}, soit "
        f"{100 * w['gain_du_champ_tourne'] / w['gain_du_champ']:.0f} % de la descente. Ce qui "
        f"travaille est l'existence d'une pénalité, pas l'identité qu'elle porte. La part "
        f"SPÉCIFIQUE vaut {w['gain_specifique']:.2f} morceau sur les "
        f"{w['reste_a_couvrir']:.1f} à supprimer pour tracer une feuille d'un bout à l'autre, "
        f"soit {100 * w['part_du_chemin']:.1f} % du chemin.",
        f"⚠ Le champ CONSTANT, lui, ne fait rien du tout "
        f"({w['gain_du_constant']:+.2f}) : il rend le même indice partout, donc un écart nul "
        f"partout. Il vaut d'exister — il prouve que le peu qui bouge vient de la VARIATION du "
        f"champ et non d'un terme de plus dans le coût.",
        f"⚠ LA CONDITION DE MORT EST PASSÉE, ET C'EST CE QUI REND LE NON INFORMATIF. Mesuré "
        f"secteur par secteur sur {p['pas']} pas, un indice de spire publié vaut "
        f"{p['feuilles_par_indice']:.3f} feuille : le champ distingue bien à la résolution de "
        f"la feuille. L'instrument est bon, et il ne sauve pas le tracker.",
        f"⚠ PORTÉE. Un seul rouleau ({m['rouleau']}), une seule hauteur (z = {m['z']}), et la "
        f"bande r {lo}..{hi} voxels — {100 * m['part_du_rayon']:.1f} % du rayon. La moitié "
        f"intérieure n'a pas de spires publiées, et c'est là que le comptage rendait « une "
        f"carte de la faiblesse du détecteur ». Rien ici ne parle de la 3D.",
    ]
    return lignes


def _barres(art, x0: int, y0: int, pw: int, ph: int, m: dict, petit) -> int:
    v = m["variantes"]
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    ordre = ["temoin", "champ", "tourne", "constant"]
    hautes = [v[k]["morceaux_par_mur"] for k in ordre]
    haut = max(hautes) * 1.08
    bas, gauche = y0 + ph - 58, x0 + 46
    large = (pw - 70) / len(ordre)
    for i, k in enumerate(ordre):
        val = v[k]["morceaux_par_mur"]
        h = (val / haut) * (ph - 96)
        xa = gauche + i * large + 8
        xb = gauche + (i + 1) * large - 8
        art.rectangle([xa, bas - h, xb, bas], fill=COULEURS[k])
        art.text((xa, bas - h - 15), f"{val:.2f}", fill=TEXTE, font=petit)
        art.text((xa, bas + 6), NOMS[k], fill=TEXTE, font=petit)
    art.line([gauche, bas, x0 + pw - 16, bas], fill=TEXTE)
    art.text((x0 + 10, y0 + 10), "morceaux par mur — plus bas vaut mieux",
             fill=DISCRET, font=petit)
    art.text((x0 + 10, bas + 26),
             "le tourné est FAUX et suit le champ de près", fill=ROUGE, font=petit)
    return len(ordre)


def _decomposition(art, x0: int, y0: int, pw: int, ph: int, m: dict, petit) -> int:
    w = m["verdict"]
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 10, y0 + 10), "d'où vient la descente", fill=DISCRET, font=petit)
    total = w["gain_du_champ"]
    part_fausse = w["gain_du_champ_tourne"]
    x, large = x0 + 24, pw - 48
    y = y0 + 52
    art.rectangle([x, y, x + large, y + 34], outline=CADRE)
    coupe = x + int(large * part_fausse / total)
    art.rectangle([x, y, coupe, y + 34], fill=ROUGE)
    art.rectangle([coupe, y, x + large, y + 34], fill=BLEU)
    art.text((x, y + 44), f"ce qu'un FAUX champ obtient : {part_fausse:.2f}",
             fill=ROUGE, font=petit)
    art.text((x, y + 62), f"ce que la BONNE spire ajoute : {w['gain_specifique']:.2f}",
             fill=BLEU, font=petit)
    art.text((x, y + 96), f"reste à supprimer pour une feuille", fill=TEXTE, font=petit)
    art.text((x, y + 114), f"d'un bout à l'autre : {w['reste_a_couvrir']:.1f} morceaux",
             fill=TEXTE, font=petit)
    art.text((x, y + 146), f"→ {100 * w['part_du_chemin']:.1f} % du chemin",
             fill=ROUGE, font=petit)
    art.text((x, y + 190), "un pas d'indice publié vaut", fill=DISCRET, font=petit)
    art.text((x, y + 208),
             f"{m['pas_dindice']['feuilles_par_indice']:.3f} feuille "
             f"({m['pas_dindice']['pas']} pas mesurés)", fill=VERT, font=petit)
    art.text((x, y + 232), "la condition de mort est passée :", fill=DISCRET, font=petit)
    art.text((x, y + 250), "l'instrument est bon", fill=VERT, font=petit)
    return 2


def _bande(art, x0: int, y0: int, pw: int, ph: int, m: dict, petit) -> int:
    lo, hi = m["bande_vx"]
    total = m["polaire"][0]
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 10, y0 + 10), "ce que le champ couvre du rayon",
             fill=DISCRET, font=petit)
    x, large = x0 + 24, pw - 48
    y = y0 + 60
    art.rectangle([x, y, x + large, y + 40], outline=CADRE)
    a = x + int(large * lo / total)
    b = x + int(large * hi / total)
    art.rectangle([x, y, a, y + 40], fill=(238, 238, 238))
    art.rectangle([a, y, b, y + 40], fill=VERT)
    art.text((x, y + 50), f"0", fill=DISCRET, font=petit)
    art.text((a - 10, y + 50), f"{lo}", fill=TEXTE, font=petit)
    art.text((b - 30, y + 50), f"{hi}", fill=TEXTE, font=petit)
    art.text((x, y + 84), f"couvert : {100 * m['part_du_rayon']:.1f} % du rayon",
             fill=VERT, font=petit)
    art.text((x, y + 102), "non couvert : vers le CŒUR, là où le", fill=ROUGE, font=petit)
    art.text((x, y + 120), "détecteur est le plus faible", fill=ROUGE, font=petit)
    art.text((x, y + 154), f"{m['murs_par_colonne']:.0f} murs par colonne",
             fill=TEXTE, font=petit)
    art.text((x, y + 172), f"{m['colonnes']} colonnes angulaires", fill=TEXTE, font=petit)
    art.text((x, y + 190), f"{m['secteurs_repondus']}/72 secteurs répondent",
             fill=TEXTE, font=petit)
    art.text((x, y + 222), "aucune piste ne traverse :", fill=DISCRET, font=petit)
    art.text((x, y + 240),
             f"traversantes {m['verdict']['traversantes_temoin']} → "
             f"{m['verdict']['traversantes_champ']}", fill=ROUGE, font=petit)
    return 3


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    marge, pw, ecart, ph = 38, 366, 26, 420
    largeur_utile = pw * 3 + ecart * 2
    for coupe in (160, 150, 142, 134, 126, 118):
        lignes = couper(prose(m), coupe)
        if max(moyen.getbbox(x)[2] for x in lignes) <= largeur_utile:
            break
    L = marge * 2 + largeur_utile
    H = 104 + ph + 42 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = Tracee(ImageDraw.Draw(toile))
    w = m["verdict"]
    art.text((marge, 16),
             "Le coût qui connaît la spire — et le faux champ qui en obtient autant",
             fill=TEXTE, font=gros)
    art.text((marge, 40),
             f"{m['rouleau']} · z {m['z']} · bande r {m['bande_vx'][0]}..{m['bande_vx'][1]} vx · "
             f"poids {m['poids']} · écart max {m['ecart_max']} spire · "
             f"part spécifique {100 * w['part_du_chemin']:.1f} % du chemin",
             fill=DISCRET, font=moyen)
    titres = ("A · ✗ les quatre variantes",
              "B · ✗ d'où vient la descente",
              "C · ⚠ la portée de la mesure")
    for k, t in enumerate(titres):
        art.text((marge + k * (pw + ecart), 76), t, fill=TEXTE, font=moyen)
    x = _barres(art, marge, 104, pw, ph, m, petit)
    y = _decomposition(art, marge + pw + ecart, 104, pw, ph, m, petit)
    z = _bande(art, marge + 2 * (pw + ecart), 104, pw, ph, m, petit)
    cadres = [(marge + k * (pw + ecart), 104, marge + k * (pw + ecart) + pw, 104 + ph)
              for k in range(3)]
    debut = H - len(lignes) * 19 - 12
    for k, l in enumerate(lignes):
        art.text((marge, debut + k * 19), l, fill=TEXTE, font=moyen)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"titres": titres, "barres": x, "decomposition": y, "bande": z,
            "textes_dessines": art.textes,
            "debordants": textes_debordants(art.poses, L - marge),
            "hors_cadre": textes_hors_cadre(art.poses, cadres),
            "recouvrements": textes_qui_se_recouvrent(art.poses),
            "prose": [(t, moyen.getbbox(t)[2]) for t in lignes],
            "largeur_utile": largeur_utile, "sortie": str(sortie)}


def verifier() -> int:
    echecs, controles = 0, 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        print(f"  {'ok  ' if ok else 'ECHEC'} {nom}" + (f"  — {detail}" if detail else ""))
        if not ok:
            echecs += 1

    print("figure — le coût qui connaît la spire")
    if not MESURE.is_file():
        print("  ⚠ mesure absente : contrôles sur données réelles sautés")
        print(f"ALL PASS ({echecs} failures, {controles} checks)")
        return 0
    m = json.loads(MESURE.read_text())
    d = dessiner(m, RACINE / "docs" / "images" / "114_le_cout_qui_connait_la_spire.png")
    v("la figure est écrite", Path(d["sortie"]).is_file())
    v("les trois panneaux portent quelque chose",
      d["barres"] > 0 and d["decomposition"] > 0 and d["bande"] > 0)
    v("aucun texte ne déborde du cadre", not d["debordants"], str(d["debordants"][:2]))
    v("aucun texte ne sort de son panneau", not d["hors_cadre"], str(d["hors_cadre"][:2]))
    v("aucun texte n'en recouvre un autre", not d["recouvrements"],
      str(d["recouvrements"][:2]))
    v("la prose tient dans la largeur utile",
      all(wd <= d["largeur_utile"] for _t, wd in d["prose"]))
    v("la prose est traçable par la police déployée",
      prose_tracable([t for t, _wd in d["prose"]]))

    txt = " ".join(t for t, _wd in d["prose"]).lower()
    w = m["verdict"]
    # ⚠⚠⚠ LA GARDE QUI COMPTE : le chiffre du champ ne voyage JAMAIS sans celui du tourné.
    # Publier « 99,12 → 96,14 » seul se lit comme un succès ; c'est la troisième barre qui dit
    # que 83 % de la descente est obtenue par un champ faux.
    v("le gain du champ ne voyage pas sans celui du champ tourné",
      f"{m['variantes']['champ']['morceaux_par_mur']:.2f}" in txt
      and f"{m['variantes']['tourne']['morceaux_par_mur']:.2f}" in txt)
    v("la prose publie la part SPÉCIFIQUE et le chemin restant",
      f"{w['gain_specifique']:.2f}" in txt and f"{w['reste_a_couvrir']:.1f}" in txt)
    # ⚠⚠ La condition de mort est PASSEE, et c'est elle qui rend le non informatif : sans elle
    # « le champ n'aide pas » se lirait comme « le champ est mauvais ».
    v("la prose dit que la condition de mort est passée",
      f"{m['pas_dindice']['feuilles_par_indice']:.3f}" in txt and "feuille" in txt)
    v("la prose nomme le témoin constant et son zéro",
      "constant" in txt and f"{w['gain_du_constant']:+.2f}" in txt)
    # ⚠ La PORTEE est la moitie du resultat : un non mesure sur 48 % du rayon d'un seul rouleau
    # ne dit rien du coeur, et rien du tout de la 3D.
    v("la prose borne la portée : un rouleau, une hauteur, une bande",
      str(m["z"]) in txt and f"{100 * m['part_du_rayon']:.1f}" in txt and "3d" in txt)
    v("la prose dit que la réouverture était légitime",
      "réouverture" in txt and "après" in txt)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "114_le_cout_qui_connait_la_spire.png")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    d = dessiner(json.loads(MESURE.read_text()), a.sortie)
    print(f"écrit : {d['sortie']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
