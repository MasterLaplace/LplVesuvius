"""La planche en profondeur — trente coupes qui traversent l'empilement, et rien qui les nomme.

⚠⚠ **Ce que cette image doit rendre évident.** Trente tuiles numérotées, chacune la coupe
(couche, colonne) à la rangée médiane d'un chunk du rouleau. Quinze viennent de chunks où la marche
de `190` tient sa feuille, quinze de contrôles appariés DANS LE MÊME SEGMENT. Contrairement à la
planche de `195`, qui montrait un plan DANS une couche, celle-ci coupe l'empilement **en travers** :
c'est la vue où une propriété de la relation entre couches peut apparaître.

⭐ **Le dessinateur est celui de `195`**, et c'est délibéré : deux modules qui dessineraient « une
planche aveugle » seraient deux définitions de ce qui fuit et de ce qui ne fuit pas. Ce fichier ne
porte que les défauts de chemin et sa propre batterie.

  uv run python src/figures/figure_la_planche_en_profondeur.py \\
      --json docs/mesures/regarder_dans_la_profondeur.json \\
      --sortie docs/images/196_la_planche_en_profondeur.png
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

from figure_la_planche_a_laveugle import (AGRANDISSEMENT, BANDEAU,  # noqa: E402
                                          ECART, _forme, dessiner, lire, lire_dict)

from PIL import Image  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]


def verifier(json_path: Path, sortie: Path) -> int:
    echecs, faits = 0, 0

    def v(nom, ok, detail=""):
        nonlocal echecs, faits
        faits += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '⛔'} {nom}" + (f"  — {detail}" if detail else ""))

    import copy  # noqa: PLC0415

    d = lire(json_path)
    chemin, poses, cadres = dessiner(d, sortie)
    img = Image.open(chemin)
    p = d["la_planche"]
    hau, lar = _forme(p)
    attendue = (ECART + int(p["colonnes"]) * (lar * AGRANDISSEMENT + ECART),
                104 + int(p["rangs"]) * (hau * AGRANDISSEMENT + BANDEAU + ECART) + 72)
    v("l'image est écrite et a la taille que la planche impose", img.size == attendue,
      f"{img.size} contre {attendue}")
    v("★★★★ la tuile est une COUPE, donc plus haute que large en voxels ne l'est pas — "
      "elle est moins haute", hau < lar, f"{hau}×{lar}")
    v("★★★ chaque place porte son numéro, une fois et une seule",
      sorted(int(t) for _x, _y, t, _f in poses if t.isdigit())
      == list(range(1, len(p["ordre"]) + 1)))
    v("il y a un cadre par tuile", len(cadres) == len(p["ordre"]), f"{len(cadres)} cadres")
    v("★★★★ la vue DÉCLARÉE est écrite sur la planche",
      any("couche, colonne" in t for _x, _y, t, _f in poses),
      str([t for _x, _y, t, _f in poses][:2])[:120])

    octets = chemin.read_bytes()
    dessiner(d, sortie)
    v("★ le re-rendu est bit-identique", chemin.read_bytes() == octets)

    # ⚠⚠⚠ LA GARDE QUI FAIT TOUT LE TRAVAIL : LA PLANCHE EST LA MEME AVEC ET SANS CLEF NI PLAN.
    brut = json.loads(json_path.read_text(encoding="utf-8"))
    avec = copy.deepcopy(brut)
    avec["la_cle"] = list(range(1, len(p["ordre"]) // 2 + 1))
    avec["la_note"] = {"les_justes": 15}
    avec["la_planche"]["adresses"] = [["X", 0, 0]] * len(p["ordre"])
    tmp = sortie.with_name(sortie.stem + "_avec_clef.png")
    dessiner(lire_dict(avec), tmp)
    v("★★★★ la planche est bit-identique que la mesure porte sa clef et son plan ou non",
      tmp.read_bytes() == octets)
    tmp.unlink(missing_ok=True)

    for place in (0, 11, len(p["ordre"]) - 1):
        faux = copy.deepcopy(brut)
        faux["la_planche"]["octets"][place] = "ff" * (hau * lar)
        tmp2 = sortie.with_name(sortie.stem + "_sonde.png")
        dessiner(lire_dict(faux), tmp2)
        v(f"★★★★ la tuile {place + 1} vient bien de la mesure", tmp2.read_bytes() != octets)
        tmp2.unlink(missing_ok=True)

    faux = copy.deepcopy(brut)
    faux["la_planche"]["octets"] = list(reversed(faux["la_planche"]["octets"]))
    tmp3 = sortie.with_name(sortie.stem + "_ordre.png")
    dessiner(lire_dict(faux), tmp3)
    v("★★★ l'ordre posé est celui que la mesure a tiré", tmp3.read_bytes() != octets)
    tmp3.unlink(missing_ok=True)

    # ⚠⚠ UNE COUPE DE LA MAUVAISE FORME EST REFUSEE, JAMAIS ETIREE.
    faux = copy.deepcopy(brut)
    faux["la_planche"]["hauteur"] = int(faux["la_planche"]["largeur"])
    refuse = False
    try:
        lire_dict(faux)
    except ValueError:
        refuse = True
    v("★★★★ une planche dont la forme annoncée ne colle pas aux octets est refusée", refuse)

    print(f"figure_la_planche_en_profondeur.py  "
          f"{'ALL PASS' if not echecs else str(echecs) + ' ÉCHECS'} "
          f"({echecs} failures, {faits} checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs" / "mesures" / "regarder_dans_la_profondeur.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "196_la_planche_en_profondeur.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, _p, _c = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
