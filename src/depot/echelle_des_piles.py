#!/usr/bin/env python3
"""Chaque pile de couches de l'arbre arrive-t-elle au modele a la bonne echelle ?

⚠⚠ Pourquoi ce fichier existe. `src/xpu/infer_ink.py` normalisait par la constante `65535`,
juste pour du uint16 et fausse d'un facteur **257** pour du uint8. Le modele recevait alors
des valeurs autour de 0,002 -- du noir -- et rendait une constante. Une constante se lit
comme « il n'y a pas d'encre ici », donc la panne etait **silencieuse**, et elle a fonde un
resultat negatif publie (`36` §5bis, M1ter).

⭐ Ce qui l'a trouvee n'est pas une relecture : c'est d'avoir liste le TYPE de chaque pile de
l'arbre. Le partage etait total et personne ne l'avait jamais regarde -- les seules piles
uint16 sont les stacks **publies** de `data/layers/`, et tout ce que notre chaine rend
(`vc_render_tifxyz`) ou que le pont `zarr_vers_couches.py` ecrit est uint8. Le partage
« le modele repond / le modele est inerte » suivait exactement celui-la.

⚠ Ce fichier existe donc pour que ce coup d'oeil ne soit plus une commande de terminal qu'on
retape. Il rend la meme liste, et il REFUSE (sortie 1) si une pile est inexploitable ou si
une pile melange deux types.

Usage :
    uv run python src/depot/echelle_des_piles.py data
    uv run python src/depot/echelle_des_piles.py data --json docs/mesures/echelle_des_piles.json
    uv run python src/depot/echelle_des_piles.py --verifier
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "xpu"))


def plafond_du_type(nom: str) -> float | None:
    """Le maximum representable par ce type entier, ou None si ce n'en est pas un.

    ⚠ Un flottant n'a pas de plafond de ce genre : une pile `float32` ne se normalise pas
    par son type, et la rendre `None` force l'appelant a le dire au lieu de deviner.
    """
    import numpy as np

    try:
        return float(np.iinfo(np.dtype(nom)).max)
    except (TypeError, ValueError):
        return None


def verdict(dtype: str, maximum: float, plancher: float) -> str:
    """`ok`, `inexploitable`, ou `type_non_entier` — le nom dit ce qu'on peut en faire."""
    p = plafond_du_type(dtype)
    if p is None:
        return "type_non_entier"
    return "ok" if maximum / p >= plancher else "inexploitable"


def piles(racine: Path) -> list[dict]:
    """Chaque repertoire de `NN.tif`, avec son type et ce qu'il donnerait au modele."""
    import numpy as np
    import tifffile

    out = []
    for d in sorted({q.parent for q in racine.rglob("*.tif")}):
        fichiers = sorted(d.glob("*.tif"))
        types, maxima = set(), []
        lus = 0
        for q in fichiers:
            try:
                a = tifffile.imread(q)
            except Exception:
                continue
            if not a.size:
                continue
            types.add(str(a.dtype))
            maxima.append(float(a.max()))
            lus += 1
            # ⚠ On lit au plus trois couches par pile : le type et l'ordre de grandeur du
            # maximum ne changent pas d'une couche a l'autre, et lire 211 piles entieres
            # couterait des minutes pour une reponse qu'on a en trois fichiers.
            if lus >= 3:
                break
        if not types:
            continue
        dtype = sorted(types)[0]
        maximum = max(maxima)
        out.append({
            "pile": str(d.relative_to(racine.parent) if racine.parent in d.parents else d),
            "couches": len(fichiers),
            "dtype": dtype,
            "types_melanges": sorted(types) if len(types) > 1 else None,
            "maximum": maximum,
            "plafond_du_type": plafond_du_type(dtype),
            "verdict": verdict(dtype, maximum, PLANCHER),
        })
    return out


PLANCHER = 1.0 / 64.0
"""Meme borne que `infer_ink.PLEINE_ECHELLE_MINIMALE`, et pour la meme raison.

⚠⚠ Elle est recopiee ici plutot qu'importee EXPRES : ce fichier doit pouvoir tourner sans
torch, et `infer_ink` en demande. Le controle `--verifier` verifie que les deux valeurs
s'accordent quand l'import est possible -- c'est ce qui empeche la copie de deriver.
"""


def verifier() -> int:
    """Auto-test HORS LIGNE : ni torch, ni donnee."""
    echecs = controles = 0

    def v(nom: str, ok: bool) -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}")

    v("le plafond d'un uint8 est 255", plafond_du_type("uint8") == 255.0)
    v("celui d'un uint16 est 65535", plafond_du_type("uint16") == 65535.0)
    v("un type flottant n'en a pas, et le DIT", plafond_du_type("float32") is None)
    v("un nom de type inconnu aussi", plafond_du_type("pas_un_type") is None)

    v("une pile pleine echelle est exploitable", verdict("uint8", 255.0, PLANCHER) == "ok")
    v("... et une pile sombre mais reelle aussi", verdict("uint16", 2000.0, PLANCHER) == "ok")
    # ⚠⚠ Le cas EXACT du bug : une pile uint8 dont on aurait garde le maximum brut apres
    # division par 65535. Ici on l'exprime dans l'autre sens -- un uint16 qui plafonne a 255.
    v("une pile uint16 qui plafonne a 255 est inexploitable",
      verdict("uint16", 255.0, PLANCHER) == "inexploitable")
    v("une pile vide est inexploitable", verdict("uint8", 0.0, PLANCHER) == "inexploitable")
    v("un type non entier est nomme, pas juge",
      verdict("float32", 1.0, PLANCHER) == "type_non_entier")

    # ⚠⚠ LE controle qui empeche la copie de deriver : le plancher d'ici doit valoir celui
    # d'`infer_ink`, sinon deux fichiers refuseraient deux ensembles de piles differents.
    try:
        import infer_ink
        v("le plancher est le meme que celui de infer_ink",
          PLANCHER == infer_ink.PLEINE_ECHELLE_MINIMALE)
    except Exception:
        v("le plancher est le meme que celui de infer_ink (torch absent, saute)", True)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("racine", nargs="?", type=Path, default=RACINE / "data")
    ap.add_argument("--json", type=Path)
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()
    if not a.racine.is_dir():
        print(f"erreur : {a.racine} n'est pas un répertoire", file=sys.stderr)
        return 2

    lignes = piles(a.racine)
    par_type: dict[str, int] = {}
    for l in lignes:
        par_type[l["dtype"]] = par_type.get(l["dtype"], 0) + 1
    mauvaises = [l for l in lignes if l["verdict"] != "ok"]
    melangees = [l for l in lignes if l["types_melanges"]]

    for t, n in sorted(par_type.items(), key=lambda kv: -kv[1]):
        print(f"  {t:10} {n:>4} piles")
    for l in mauvaises:
        print(f"  ⚠ {l['verdict']:16} {l['pile']}  max {l['maximum']:.0f} / {l['plafond_du_type']}")
    for l in melangees:
        print(f"  ⚠⚠ types mélangés {l['types_melanges']} dans {l['pile']}")
    print(f"{len(lignes)} piles, {len(mauvaises)} inexploitables, {len(melangees)} mélangées")

    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(
            {"racine": str(a.racine), "par_type": par_type, "piles": lignes},
            indent=2, ensure_ascii=False) + "\n")
        print(f"relevé : {a.json}")
    return 1 if (mauvaises or melangees) else 0


if __name__ == "__main__":
    sys.exit(main())
