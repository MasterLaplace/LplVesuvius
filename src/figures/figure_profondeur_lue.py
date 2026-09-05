#!/usr/bin/env python3
"""Ce que le détecteur rend quand seule la PROFONDEUR lue change — trois cartes, une échelle.

⚠⚠ POURQUOI CETTE FIGURE EXISTE. Le résultat est une **réfutation** : on attendait que ramener
la fenêtre au régime d'entraînement (62 → 182 µm) fasse monter la réponse du détecteur, et elle
**tombe**, de façon monotone. Trois nombres se lisent comme un tableau ; trois cartes à la même
échelle se lisent d'un coup — et surtout elles montrent *comment* elle tombe : la carte ne
devient pas bruitée, elle devient **terne**.

⭐⭐⭐ ET L'ÉCHELLE EST COMMUNE AUX TROIS, ce qui est tout le sujet. Rendre chaque carte à sa
propre plage ferait paraître la fenêtre la plus épaisse aussi contrastée que la plus mince,
c'est-à-dire effacerait le résultat. Une seule plage, prise sur les trois.

⚠ Les nombres sont LUS dans `docs/mesures/la_profondeur_lue.json` et les cartes dans
`docs/mesures/profondeur_lue_cartes/`, jamais retapés.

Usage :
    uv run python src/figures/figure_profondeur_lue.py --verifier
    uv run python src/figures/figure_profondeur_lue.py \\
        --sortie docs/images/75_la_profondeur_lue.png
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figure_commune import police, prose_tracable  # noqa: E402
from figure_le_nul_verso import bornes_communes, en_gris  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
CARTES = RACINE / "docs" / "mesures" / "profondeur_lue_cartes"

FOND = (16, 16, 16)
TEXTE = (235, 232, 224)
DISCRET = (140, 136, 128)
AMBRE = (214, 143, 42)
ROUGE = (188, 68, 52)


def prose(m: dict) -> list[str]:
    """Ce que la figure dit en toutes lettres, pour qu'un lecteur pressé ne devine pas."""
    lots = [x for x in m["lots"] if not x.get("echec")]
    sigmas = [x["sigma"] for x in lots]
    sens = "TOMBE" if all(a > b for a, b in zip(sigmas, sigmas[1:])) else "monte"
    return [
        f"on attendait que sigma MONTE en ramenant la fenetre au regime d'entrainement.",
        f"il {sens} : {' -> '.join(f'{s:.3f}' for s in sigmas)} de "
        f"{lots[0]['profondeur_um']:.0f} a {lots[-1]['profondeur_um']:.0f} um.",
        f"et a la profondeur ACTUELLE il vaut {sigmas[0]:.3f}, soit l'etalon d'un modele "
        f"VIVANT (0,771), pas d'un modele muet (0,017).",
        "donc la fenetre trop mince n'explique pas ce que le nul verso mesure.",
    ]


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    lots = [x for x in m["lots"] if not x.get("echec")]
    if len(lots) < 2:
        raise SystemExit("moins de deux profondeurs mesurées : rien à comparer")
    cartes = [np.load(CARTES / f"{m['segment']}_pas{x['pas']}.npy") for x in lots]

    # ⚠⚠ LA PLAGE VIENT DES TROIS CARTES. `bornes_communes` en prend deux ; on la replie sur
    # l'ensemble en la passant deux fois plutôt qu'en réécrivant la règle des percentiles —
    # deux définitions de « la plage commune » finiraient par ne pas s'accorder.
    lo, hi = bornes_communes(cartes[0], cartes[1])
    for autre in cartes[2:]:
        lo2, hi2 = bornes_communes(np.array([[lo, hi]]), autre)
        lo, hi = min(lo, lo2), max(hi, hi2)

    cote, marge = 268, 36
    L = marge * 2 + len(cartes) * cote + (len(cartes) - 1) * 16
    H = 104 + cote + 44 + 4 * 19 + 24
    toile = Image.new("RGB", (L, H), FOND)
    d = ImageDraw.Draw(toile)
    d.text((marge, 22), "la meme fenetre, lue a trois profondeurs", fill=TEXTE, font=gros)
    d.text((marge, 48), f"{m['segment']} — meme pile, meme modele, meme debut de surface ; "
                        "seul le pas de couches change", fill=DISCRET, font=moyen)

    for i, (x, carte) in enumerate(zip(lots, cartes)):
        gx = marge + i * (cote + 16)
        gy = 104
        toile.paste(Image.fromarray(en_gris(carte, lo, hi)).resize((cote, cote), Image.NEAREST),
                    (gx, gy))
        d.rectangle([gx, gy, gx + cote, gy + cote], outline=(70, 70, 70))
        d.text((gx, gy - 38), f"pas {x['pas']} — {x['profondeur_um']:.0f} µm",
               fill=TEXTE, font=moyen)
        # ⚠ σ EN COULEUR DE SON SENS : le résultat est une baisse, et la faire lire comme un
        # chiffre parmi d'autres serait la taire.
        d.text((gx, gy - 20), f"sigma {x['sigma']:.3f}   mediane {x['mediane']:+.3f}",
               fill=ROUGE if i and x["sigma"] < lots[0]["sigma"] else TEXTE, font=petit)
        d.text((gx + 4, gy + cote + 6), f"couches {x['debut']}..{x['derniere_couche']}",
               fill=DISCRET, font=petit)

    bas = 104 + cote + 30
    d.text((marge, bas), f"meme echelle de gris : {lo:+.2f} a {hi:+.2f} (percentiles 1 et 99 "
                         "des TROIS cartes)", fill=AMBRE, font=petit)
    for k, ligne in enumerate(prose(m)):
        d.text((marge, bas + 22 + k * 19), ligne, fill=TEXTE, font=moyen)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"plage": [lo, hi], "sigmas": [x["sigma"] for x in lots], "sortie": str(sortie)}


def verifier() -> int:
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        print(f"  {'ok  ' if cond else 'ECHEC'}  {nom}" + (f"  — {detail}" if detail else ""))
        if not cond:
            echecs += 1

    faux = {"segment": "s", "lots": [
        {"pas": 1, "profondeur_um": 62.4, "sigma": 0.7179, "mediane": -0.812},
        {"pas": 2, "profondeur_um": 122.3, "sigma": 0.5543, "mediane": -1.046},
        {"pas": 3, "profondeur_um": 182.3, "sigma": 0.4230, "mediane": -1.137}]}
    lignes = prose(faux)
    v("la prose est tracable", prose_tracable(lignes), str(lignes))
    # ⚠⚠⚠ LA PHRASE SUIT LA MESURE, ELLE N'EST PAS ÉCRITE EN DUR. Le résultat est une baisse ;
    # si un jour σ montait, la figure doit le DIRE et non répéter « il tombe ».
    v("... et elle dit que sigma TOMBE quand il tombe",
      any("TOMBE" in l for l in lignes), str(lignes[1]))
    monte = {"segment": "s", "lots": [dict(faux["lots"][0], sigma=0.30),
                                      dict(faux["lots"][1], sigma=0.50),
                                      dict(faux["lots"][2], sigma=0.70)]}
    v("... et qu'il monte quand il monte",
      any("monte" in l for l in prose(monte)), str(prose(monte)[1]))
    v("... et elle nomme l'etalon vivant", any("0,771" in l for l in lignes), str(lignes))
    # ⚠ Une seule profondeur ne se compare a rien : la figure doit refuser plutot que dessiner
    # un panneau unique qui aurait l'air d'une comparaison.
    v("une seule profondeur ne produit pas de figure",
      _leve(lambda: dessiner({"segment": "s", "lots": [faux["lots"][0]]}, Path("/tmp/x.png"))))

    print(f"  {'ECHEC' if echecs else 'ALL PASS'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def _leve(f) -> bool:
    try:
        f()
    except SystemExit:
        return True
    except Exception:  # noqa: BLE001 — une autre panne n'est pas le refus attendu
        return False
    return False


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--mesure", type=Path,
                   default=RACINE / "docs" / "mesures" / "la_profondeur_lue.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "75_la_profondeur_lue.png")
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
