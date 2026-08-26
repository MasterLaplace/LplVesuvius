#!/usr/bin/env python3
"""Déplacer une nappe LE LONG DE SA NORMALE — la moitié « appliquer » du champ.

⚠⚠ **Ce fichier existe parce que `20` §4 écrivait que corriger était hors de portée**,
*« parce que la chaîne maillage → rendu n'est pas ici »*. Elle y est depuis le
2026-08-19 (`24`), et rien n'avait été écrit pour s'en servir. `champ_correction.py`
mesure **de combien** une trace est décalée ; ce fichier **le fait**.

⚠ Et il ne prétend pas gauchir. Un gauchissement déplace chaque point de sa propre
quantité, et le champ que le dépôt sait produire aujourd'hui est un **résumé par
segment** (`depth_profile --grid` rend une médiane, pas une carte). Ce qui est
implémenté ici est donc la translation **le long de la normale locale**, qui n'est déjà
pas une translation rigide : chaque point suit SA normale. Le champ par fenêtre de
`20` §8 se branchera ici quand un producteur le rendra en coordonnées de maillage.

## Ce que le déplacement ne peut pas faire, et qu'il faut dire

⚠⚠ **Le signe n'est pas connu a priori.** L'ordre des couches d'un rendu est celui du
rendeur, et une normale n'a pas de sens (`valider_champ_normal.py`). Le protocole
honnête est donc empirique : déplacer, re-rendre, mesurer. Si le pic s'éloigne, c'est
l'autre signe. Deux rendus, aucune convention inventée.

⚠ **Un point sans normale n'est pas déplacé — il est INVALIDÉ, et compté.** Le laisser
en place pendant que ses voisins bougent cisaillerait la nappe, et un cisaillement se
lit comme du relief. Un point qu'on ne sait pas orienter est un point qu'on ne sait pas
corriger, et c'est ce qu'il faut dire plutôt que de le laisser mentir.

⚠ **La bbox du `meta.json` est RECALCULÉE.** Elle décrit où la nappe se trouve ; la
recopier après un déplacement livrerait un maillage dont les métadonnées décrivent la
place qu'il occupait avant.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

INVALIDE = -1.0


def lire(dossier: Path) -> tuple[dict, dict]:
    """Les trois plans et la métadonnée d'un `.tifxyz`."""
    import tifffile

    plans = {n: tifffile.imread(str(dossier / f"{n}.tif")) for n in ("x", "y", "z")}
    meta_p = dossier / "meta.json"
    meta = json.loads(meta_p.read_text()) if meta_p.exists() else {}
    return plans, meta


def deplacer(plans: dict, voxels: float) -> tuple[dict, dict]:
    """Chaque point valide avance de `voxels` le long de sa propre normale.

    ⚠ La normale vient de `recaler_sur_la_matiere.normales`, qui la tire des DEUX
    tangentes du maillage et refuse de la calculer à travers un trou. On ne la
    recalcule pas ici : deux définitions de « la normale de cette nappe » finiraient
    par ne pas s'accorder, et c'est le genre d'écart qu'aucun rendu ne montre.
    """
    import numpy as np
    import projeter_tangentiel as pt
    import recaler_sur_la_matiere as rsm

    normale, orientable = rsm.normales(plans)
    bon = pt.valide(plans)

    sortie = {c: plans[c].astype(np.float32).copy() for c in ("x", "y", "z")}
    a_deplacer = bon & orientable
    for i, c in enumerate(("x", "y", "z")):
        sortie[c][a_deplacer] = (plans[c][a_deplacer].astype(np.float64)
                                 + voxels * normale[..., i][a_deplacer]).astype(np.float32)

    # ⚠⚠ Valide mais NON orientable : on ne peut pas le corriger, donc on ne le garde pas.
    perdus = bon & ~orientable
    for c in ("x", "y", "z"):
        sortie[c][perdus] = INVALIDE

    return sortie, {
        "points": int(bon.size),
        "valides": int(bon.sum()),
        "deplaces": int(a_deplacer.sum()),
        "invalides_faute_de_normale": int(perdus.sum()),
        "voxels": float(voxels),
    }


def ecrire(dossier: Path, plans: dict, meta: dict, comptes: dict) -> None:
    """Écrit le `.tifxyz`, **bbox recalculée** sur les points réellement valides."""
    import numpy as np
    import tifffile

    dossier.mkdir(parents=True, exist_ok=True)
    for c in ("x", "y", "z"):
        tifffile.imwrite(str(dossier / f"{c}.tif"), plans[c].astype(np.float32))

    bon = ((plans["x"] > INVALIDE) & (plans["y"] > INVALIDE) & (plans["z"] > INVALIDE))
    neuf = dict(meta)
    if bon.any():
        bas = [float(plans[c][bon].min()) for c in ("x", "y", "z")]
        haut = [float(plans[c][bon].max()) for c in ("x", "y", "z")]
        neuf["bbox"] = [bas, haut]
    neuf["deplacement_voxels"] = comptes["voxels"]
    (dossier / "meta.json").write_text(json.dumps(neuf, indent=4) + "\n")


def verifier() -> int:
    """Les contrôles hors ligne, chacun avec son cas négatif."""
    import tempfile

    import numpy as np
    import projeter_tangentiel as pt
    import recaler_sur_la_matiere as rsm

    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    # Un plan z = 5 dans le plan xy : sa normale est ±z, donc un deplacement de d
    # doit changer z de exactement d et laisser x et y intacts.
    h, w = 6, 7
    gy, gx = np.mgrid[0:h, 0:w]
    plans = {"x": gx.astype(np.float32) + 10.0,
             "y": gy.astype(np.float32) + 20.0,
             "z": np.full((h, w), 5.0, np.float32)}
    out, c = deplacer(plans, 3.0)
    v("tous les points sont deplaces", c["deplaces"] == h * w, str(c))
    v("le plan bouge de exactement d, sur z seul",
      np.allclose(np.abs(out["z"] - plans["z"]), 3.0) and np.allclose(out["x"], plans["x"]),
      f"z {float(out['z'][2, 2])}")
    # ⚠⚠ LE controle qui compte : le signe doit s'INVERSER avec le signe demande.
    # Sans lui, un deplacement qui ignorerait son argument passerait.
    inv, _ = deplacer(plans, -3.0)
    v("le signe inverse le sens", np.allclose(out["z"] + inv["z"], 2 * plans["z"]),
      f"{float(out['z'][2, 2])} / {float(inv['z'][2, 2])}")
    # ... et un deplacement NUL est l'identite.
    zero, _ = deplacer(plans, 0.0)
    v("un deplacement nul ne bouge rien",
      all(np.array_equal(zero[c2], plans[c2]) for c2 in ("x", "y", "z")))

    # Un point invalide le reste, et ne devient jamais un point valide deplace.
    troue = {c2: a.copy() for c2, a in plans.items()}
    for c2 in ("x", "y", "z"):
        troue[c2][3, 3] = INVALIDE
    out2, c2n = deplacer(troue, 3.0)
    v("un point invalide le reste", out2["z"][3, 3] == INVALIDE, str(out2["z"][3, 3]))
    v("... et il n'est pas compte comme deplace", c2n["deplaces"] < h * w, str(c2n))
    # ⚠ Ma premiere version assertait `>= 0`, une TAUTOLOGIE. Et sa fixture ne pouvait de
    # toute facon pas produire un point valide sans normale : mesure, un trou d'un point
    # laisse `orientable` exactement egal a `valide`. Il faut un point ISOLE.
    isole = {c2: np.full((5, 5), INVALIDE, np.float32) for c2 in ("x", "y", "z")}
    isole["x"][2, 2], isole["y"][2, 2], isole["z"][2, 2] = 1.0, 2.0, 3.0
    out3, c3n = deplacer(isole, 3.0)
    v("un point valide SANS voisins n'a pas de normale",
      c3n["invalides_faute_de_normale"] == 1 and c3n["deplaces"] == 0, str(c3n))
    v("... et il est invalide en sortie, pas laisse en place",
      out3["z"][2, 2] == INVALIDE, str(out3["z"][2, 2]))

    # ⚠⚠ LE CONTRAT avec `normales`, plutot que la redondance qu'il rend invisible :
    # aucun point ne doit etre orientable sans etre valide. Tant qu'il tient, le `bon &`
    # de `a_deplacer` est une ceinture ; s'il cede un jour, ce controle le dira au lieu
    # de laisser un point invalide se faire deplacer et devenir un point valide invente.
    n_t, orient_t = rsm.normales(troue)
    v("aucun point orientable n'est invalide",
      not bool((~pt.valide(troue) & orient_t).any()))
    v("le compte de valides est celui du masque", c2n["valides"] == h * w - 1, str(c2n))

    # L'ecriture : la bbox suit les points, elle ne recopie pas l'ancienne.
    with tempfile.TemporaryDirectory() as d:
        cible = Path(d) / "sortie.tifxyz"
        ecrire(cible, out, {"bbox": [[0, 0, 0], [1, 1, 1]], "uuid": "x"}, c)
        relu = json.loads((cible / "meta.json").read_text())
        # ⚠ Une PROPRIETE, pas une valeur attendue. Ma premiere version asserait z = 8,0
        # -- la normale pointe en fait vers -z, donc z vaut 2,0 -- et c'etait l'assertion
        # qui avait tort, pas le code. Une bbox se juge sur ce qu'elle doit etre : serree
        # et contenante. Le SIGNE de la normale, lui, ne s'assere pas : il se mesure.
        bon_r = ((replans_ok := True) and
                 (out["x"] > INVALIDE) & (out["y"] > INVALIDE) & (out["z"] > INVALIDE))
        v("la bbox contient tous les points valides",
          all(relu["bbox"][0][i] <= float(out[c3][bon_r].min()) + 1e-6 and
              relu["bbox"][1][i] >= float(out[c3][bon_r].max()) - 1e-6
              for i, c3 in enumerate(("x", "y", "z"))), str(relu["bbox"]))
        v("... et elle est SERREE, donc ce n'est plus l'ancienne",
          relu["bbox"][0] != [0, 0, 0] and relu["bbox"][1] != [1, 1, 1], str(relu["bbox"]))
        v("... et le reste de la metadonnee survit", relu["uuid"] == "x")
        v("le deplacement voyage avec le maillage", relu["deplacement_voxels"] == 3.0)
        replans, _ = lire(cible)
        v("ce qui est ecrit se relit a l'identique",
          np.array_equal(replans["z"], out["z"]))

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Deplacer une nappe le long de sa normale, de N voxels.",
        epilog="⚠ Le SIGNE se determine en mesurant : deplacer, re-rendre, comparer.")
    parser.add_argument("--verifier", action="store_true")
    parser.add_argument("entree", type=Path, nargs="?", help="dossier .tifxyz")
    parser.add_argument("sortie", type=Path, nargs="?", help="dossier .tifxyz a ecrire")
    parser.add_argument("--voxels", type=float, default=None,
                        help="deplacement le long de la normale, en voxels du volume")
    a = parser.parse_args()

    if a.verifier:
        return verifier()
    if a.entree is None or a.sortie is None or a.voxels is None:
        parser.error("entree, sortie et --voxels sont requis")

    plans, meta = lire(a.entree)
    out, comptes = deplacer(plans, a.voxels)
    ecrire(a.sortie, out, meta, comptes)
    print(f"{comptes['deplaces']} / {comptes['valides']} points deplaces de "
          f"{a.voxels:+.2f} voxels ; {comptes['invalides_faute_de_normale']} invalides "
          f"faute de normale")
    print(f"ecrit : {a.sortie}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
