#!/usr/bin/env python3
"""Une mesure qui portait des lignes et n'en porte plus : une donnée perdue, pas un négatif.

⚠⚠⚠ CE GARDE EXISTE PARCE QUE C'EST ARRIVÉ DEUX FOIS, LE MÊME JOUR, PAR LE MÊME COMMIT. Le
rangement `a5901be` (2026-08-26) a écrit `"lignes": []` par-dessus **deux** mesures qui portaient
la donnée de résultats publiés et cités :

- `sensibilite_maillage.json` (4 lignes) → la figure de `34` ;
- `sans_filtre.json` (4 lignes) → le tableau de `26` §.

Dans les deux cas le maillage source avait disparu, l'outil échouait à chaque facteur, sortait à
zéro ligne, et **écrivait le fichier quand même**. Les deux ont été restaurées depuis
l'historique et vérifiées — l'image de `34` se régénère **octet pour octet**, et les quatre
lignes de `sans_filtre` sont exactement les quatre du tableau de `26`.

⭐⭐ ET LE CONTRÔLE NE PEUT PAS ÊTRE « CE FICHIER EST VIDE ». Cinq autres mesures de
`docs/mesures/` portent des listes vides **depuis toujours**, et leur vide **est le résultat** :
`temoin_negatif.json` ne trouve aucune fenêtre vide, `ecarts_0172.json` aucun site signalé. Les
signaler serait crier au loup sur des négatifs légitimes, ce qui est la meilleure façon de faire
cesser de lire un garde.

⭐ Le discriminant est donc la **régression** : un fichier que l'historique a vu plein et qui est
vide maintenant. Ça ne dit rien des négatifs, ça ne demande aucun jugement, et ça ne peut pas
manquer le cas qui a coûté deux résultats.

⚠ CE QU'IL NE VOIT PAS : une mesure vidée avant son premier commit, et une mesure dont les lignes
ont été **remplacées** plutôt que retirées. Le premier cas est hors de portée de tout garde ; le
second demanderait de savoir ce qu'une ligne doit contenir.

Usage :
    uv run python src/depot/mesures_videes.py
    uv run python src/depot/mesures_videes.py --verifier
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
MESURES = RACINE / "docs" / "mesures"


def compte_des_lignes(texte: str) -> dict[str, int] | None:
    """
    @brief Les longueurs des listes d'un document de mesure, ou None s'il n'en porte aucune.

    ⚠ Une mesure au format JSON Lines n'a pas de liste : ses enregistrements SONT les lignes.
    Les deux formes coexistent dans `docs/mesures/`, donc les deux sont comptées.
    """
    texte = texte.strip()
    if not texte:
        return {"": 0}
    if texte.startswith("{") and "\n{" in texte:
        return {"": sum(1 for l in texte.splitlines() if l.strip().startswith("{"))}
    try:
        d = json.loads(texte)
    except json.JSONDecodeError:
        return None
    if isinstance(d, list):
        return {"": len(d)}
    if not isinstance(d, dict):
        return None
    listes = {k: len(v) for k, v in d.items() if isinstance(v, list)}
    return listes or None


def contenu_a(commit: str, chemin: Path) -> str | None:
    """
    @brief Le contenu d'un fichier à un commit, ou None s'il n'y était pas.
    """
    rel = chemin.relative_to(RACINE)
    r = subprocess.run(["git", "show", f"{commit}:{rel}"],
                       capture_output=True, text=True, cwd=RACINE)
    return r.stdout if r.returncode == 0 else None


def historique(chemin: Path, limite: int = 12) -> list[str]:
    """
    @brief Les commits qui ont touché ce fichier, du plus récent au plus ancien.
    """
    rel = chemin.relative_to(RACINE)
    r = subprocess.run(["git", "log", "--format=%h", f"-{limite}", "--", str(rel)],
                       capture_output=True, text=True, cwd=RACINE)
    return [x for x in r.stdout.split() if x]


def vidées(dossier: Path = MESURES, limite: int = 12) -> list[dict]:
    """
    @brief Les mesures qui portaient des lignes dans l'historique et n'en portent plus.
    """
    out = []
    for f in sorted(list(dossier.glob("*.json")) + list(dossier.glob("*.jsonl"))):
        if not f.is_file():
            continue
        actuel = compte_des_lignes(f.read_text(errors="replace"))
        if actuel is None or any(v > 0 for v in actuel.values()):
            continue
        # ⚠ Vide MAINTENANT. L'a-t-il toujours ete ? C'est la seule question qui distingue une
        # perte d'un negatif legitime.
        for c in historique(f, limite):
            texte = contenu_a(c, f)
            if texte is None:
                continue
            passe = compte_des_lignes(texte)
            if passe and any(v > 0 for v in passe.values()):
                out.append(dict(fichier=f.name, commit=c,
                                avait={k: v for k, v in passe.items() if v},
                                a_maintenant=actuel))
                break
    return out


def _verifier(pertes: list[dict] | None = None) -> int:
    echecs = comptees = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, comptees
        comptees += 1
        print(f"  {'ok  ' if ok else 'FAIL'}  {nom}" + (f"   [{detail}]" if detail else ""))
        if not ok:
            echecs += 1

    # ⚠⚠ LE DISCRIMINATEUR, teste DANS LES DEUX SENS sur des contenus fabriques : un fichier
    # plein doit compter, un fichier vide doit compter zero, et un negatif legitime -- vide
    # depuis toujours -- ne doit PAS ressembler a une perte. Sans le dernier, le garde crierait
    # au loup sur cinq mesures de ce depot.
    v("un document a listes pleines est compté",
      compte_des_lignes('{"lignes": [1, 2, 3]}') == {"lignes": 3})
    v("... et un document à listes vides rend zéro",
      compte_des_lignes('{"lignes": []}') == {"lignes": 0})
    v("... un JSON Lines compte ses enregistrements",
      compte_des_lignes('{"a": 1}\n{"a": 2}\n') == {"": 2})
    v("... un document SANS liste n'est pas jugé",
      compte_des_lignes('{"a": 1, "b": "x"}') is None)
    v("... et un document illisible non plus",
      compte_des_lignes("pas du json") is None)
    v("un fichier vide rend zéro plutôt que None", compte_des_lignes("  ") == {"": 0})

    if pertes is not None:
        print("\net sur le dépôt réel")
        # ⚠⚠⚠ ZERO PERTE EST LE VERDICT ATTENDU, et il ne va pas de soi : deux mesures ont ete
        # vidées le 2026-08-26 et restaurées le 2026-09-04. Ce controle tombe si une troisieme
        # arrive, ou si l'une des deux est re-vidée.
        v("aucune mesure n'a perdu ses lignes", not pertes,
          " · ".join(f"{p['fichier']} (plein à {p['commit']})" for p in pertes) or "aucune")

    print()
    if echecs:
        print(f"  ECHEC ({echecs} failures)")
    else:
        print(f"  ALL PASS (0 failures, {comptees} checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--limite", type=int, default=12,
                   help="profondeur d'historique inspectée par fichier")
    a = p.parse_args()

    pertes = vidées(limite=a.limite)
    if a.verifier:
        return 1 if _verifier(pertes) else 0
    if not pertes:
        print("aucune mesure vidée : tout fichier vide de `docs/mesures/` l'a toujours été.")
        return 0
    for p_ in pertes:
        print(f"  ⚠ {p_['fichier']} : {p_['avait']} au commit {p_['commit']}, "
              f"{p_['a_maintenant']} maintenant")
    print(f"{len(pertes)} mesure(s) vidée(s) — restaurer depuis l'historique.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
