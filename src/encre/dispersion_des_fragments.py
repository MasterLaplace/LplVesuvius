#!/usr/bin/env python3
"""Trois fragments, trois AUC — et le DOMAINE rapporté décide laquelle est l'exception.

⚠⚠⚠ Pourquoi ce fichier existe, et c'est une correction de ma propre lecture.
[`63`](../../docs/63_la_premiere_verite_terrain.md) §2 bis publiait « entre 0,60 et 0,75
selon le fragment » sur la foi de deux points, lus sur le domaine **tout le segment**. Le
troisième point montre que ce domaine est contaminé : il compte tout le papyrus **vierge**
que la fenêtre contient par hasard, et une fenêtre à 1,5 % d'encre y est tirée vers le bas
sans que le modèle y soit pour rien.

⭐ Sur le domaine **tuiles annotées** — celles qui portent réellement de l'encre — le
classement change : `Frag3` passe de 0,575 à **0,704** et dépasse `Frag1`. Ce n'est pas un
détail de présentation : **quel fragment est l'exception dépend du domaine qu'on choisit de
publier**, et publier un seul domaine sans le dire serait choisir.

⚠ Ce que ce fichier N'EST PAS : une façon de trouver le domaine le plus flatteur. Les trois
sont rapportés ensemble, et l'écart entre eux **est** le résultat.

Usage :
    uv run python src/encre/dispersion_des_fragments.py --verifier
    uv run python src/encre/dispersion_des_fragments.py --json docs/mesures/dispersion_fragments.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]

FRAGMENTS = ("frag1", "frag2", "frag3")
"""Les fragments mesurés, écrits plutôt que découverts : un quatrième doit être ajouté ici,
donc vu, plutôt que d'élargir la dispersion en silence."""

DOMAINES = ("tout le segment", "lignes annotees", "tuiles annotees (256px)")


def lire(chemin: Path) -> dict:
    """Les trois domaines d'un rapport `evaluate_segment`, indexés par nom."""
    d = json.loads(chemin.read_text())
    lot = d.get("domaines") or d.get("domains") or []
    return {x["domaine"]: x for x in lot if "domaine" in x}


def etendue(valeurs: list[float]) -> dict:
    """Le minimum, le maximum et leur écart — jamais la moyenne seule.

    ⚠⚠ Une moyenne de trois AUC dispersées se lit comme une performance, alors que la
    dispersion **est** ce qu'on a mesuré. Publier `0,64` ferait disparaître le fait.
    """
    if not valeurs:
        return {"n": 0, "min": None, "max": None, "etendue": None}
    return {"n": len(valeurs), "min": min(valeurs), "max": max(valeurs),
            "etendue": round(max(valeurs) - min(valeurs), 4)}


def qui_est_lexception(par_domaine: dict) -> dict:
    """Pour chaque domaine, le fragment le plus éloigné des deux autres.

    ⚠⚠⚠ C'est la question qui compte : si l'exception CHANGE d'un domaine à l'autre, alors
    « l'exception » n'est pas une propriété du fragment mais du domaine choisi, et aucune
    des deux lectures ne peut être publiée seule.
    """
    out = {}
    for domaine, valeurs in par_domaine.items():
        if len(valeurs) < 3:
            out[domaine] = None
            continue
        ecarts = {f: sum(abs(v - w) for g, w in valeurs.items() if g != f)
                  for f, v in valeurs.items()}
        out[domaine] = max(ecarts, key=ecarts.get)
    return out


def verifier() -> int:
    """Auto-test HORS LIGNE : l'étendue et la désignation de l'exception."""
    echecs = controles = 0

    def v(nom: str, ok: bool) -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}")

    # --- L'ETENDUE, jamais la moyenne seule ---------------------------------------------
    e = etendue([0.746, 0.600, 0.575])
    v("l'etendue est max moins min", abs(e["etendue"] - 0.171) < 1e-9)
    v("le minimum et le maximum sont rendus", e["min"] == 0.575 and e["max"] == 0.746)
    v("une liste vide le dit plutot que de lever", etendue([])["n"] == 0)
    # ⚠⚠ Le controle qui porte la regle : une moyenne ferait DISPARAITRE la dispersion,
    # et deux jeux tres differents rendraient la meme moyenne.
    a, b = [0.5, 0.7, 0.9], [0.69, 0.70, 0.71]
    v("deux jeux de meme moyenne ont des etendues tres differentes",
      abs(sum(a) / 3 - sum(b) / 3) < 1e-9 and etendue(a)["etendue"] > 5 * etendue(b)["etendue"])

    # --- L'EXCEPTION, et le fait qu'elle CHANGE de domaine ------------------------------
    par_domaine = {
        "tout le segment": {"frag1": 0.746, "frag2": 0.600, "frag3": 0.575},
        "tuiles annotees (256px)": {"frag1": 0.677, "frag2": 0.581, "frag3": 0.704},
    }
    q = qui_est_lexception(par_domaine)
    v("sur tout le segment, l'exception est frag1", q["tout le segment"] == "frag1")
    v("sur les tuiles annotees, c'est frag2", q["tuiles annotees (256px)"] == "frag2")
    # ⚠⚠⚠ LE CONTROLE QUI DONNE SON SENS AU FICHIER : l'exception CHANGE selon le domaine,
    # donc « l'exception » est une propriete du domaine choisi, pas du fragment.
    v("l'exception CHANGE d'un domaine a l'autre",
      q["tout le segment"] != q["tuiles annotees (256px)"])
    v("moins de trois fragments ne designent aucune exception",
      qui_est_lexception({"d": {"a": 0.5, "b": 0.6}})["d"] is None)

    print(f"\n{'ALL PASS' if not echecs else 'ECHEC'} "
          f"({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", type=Path)
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()

    par_domaine, lignes = {d: {} for d in DOMAINES}, []
    for f in FRAGMENTS:
        chemin = RACINE / "docs/mesures" / f"{f}_verite_terrain.json"
        if not chemin.exists():
            print(f"  ⚠ mesure absente : {chemin.name}", file=sys.stderr)
            continue
        dom = lire(chemin)
        for d in DOMAINES:
            if d in dom:
                par_domaine[d][f] = dom[d]["auc"]
        lignes.append({"fragment": f, "domaines": dom})

    exception = qui_est_lexception(par_domaine)
    resume = {
        "fragments": lignes,
        "auc_par_domaine": par_domaine,
        "etendue_par_domaine": {d: etendue(list(v.values())) for d, v in par_domaine.items()},
        "exception_par_domaine": exception,
        "lecture": ("L'exception CHANGE selon le domaine rapporte : sur tout le segment c'est "
                    "frag1 qui se detache, sur les tuiles annotees c'est frag2. « L'exception » "
                    "est donc une propriete du domaine choisi, pas du fragment, et publier un "
                    "seul domaine sans le dire reviendrait a choisir."),
    }
    print("  fragment   " + "  ".join(f"{d[:18]:>18}" for d in DOMAINES))
    for f in FRAGMENTS:
        vals = "  ".join(f"{par_domaine[d].get(f, float('nan')):>18.3f}" for d in DOMAINES)
        print(f"  {f:9s}  {vals}")
    print()
    for d in DOMAINES:
        e = resume["etendue_par_domaine"][d]
        if e["n"]:
            print(f"  {d:26s} étendue {e['etendue']:.3f}   exception : {exception[d]}")
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(resume, indent=2, ensure_ascii=False) + "\n")
        print(f"\n→ {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
