#!/usr/bin/env python3
"""Quel rayon de recherche a produit chaque fichier de mesure de l'arc d'excision ?

⚠⚠⚠ CE FICHIER EXISTE PARCE QU'UN FICHIER DE MESURE NE PORTE PAS SON INSTRUMENT. `07` §9 a
divisé le rayon de recherche par quatre le 2026-08-18 — il trouvait la spire **voisine**, qui est
de la géométrie normale, et noyait l'anomalie dedans. Rien dans `docs/mesures/` ne dit quel rayon
a produit quoi. `proximity_scroll1.jsonl` a donc traversé la correction sans être régénéré, et
`07` §8 en tire encore des conclusions — c'est la panne que `07` §11 documente.

⭐ ET LA REPONSE EST DANS LA DONNEE, pas dans les dates. `measured` — le nombre de cellules qui
ont trouvé un vis-à-vis non adjacent **dans le rayon** — est une fonction du rayon à maillage
fixé. Deux fichiers qui portent le même `measured` pour une même trace ont été mesurés au même
rayon, quel qu'il soit ; deux fichiers qui divergent ne l'ont pas été. Aucune date n'est
nécessaire, et aucune n'est fiable : un fichier peut être recopié, déplacé, ou régénéré sans que
son horodatage le dise.

⚠ CE QU'IL NE JUGE PAS : les fichiers `sweep_*_rNN` **balaient** le rayon exprès, et leur nom le
dit. Un rayon différent y est le sujet de la mesure, pas un défaut. Ce module **rapporte** l'écart
et nomme la référence ; c'est un lecteur qui décide si un fichier est périmé pour ce qu'il en
fait.

Usage :
    uv run python src/excision/le_rayon_des_mesures.py
    uv run python src/excision/le_rayon_des_mesures.py --verifier
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
MESURES = RACINE / "docs" / "mesures"
REFERENCE = MESURES / "proximity_scroll1_rayon_corrige.jsonl"
"""Le fichier dont on SAIT qu'il porte le rayon corrigé : il vient d'être produit par le
producteur réparé, et `07` §11 le montre retrouvant le +0,840 que `07` §9 publie."""


def compte_mesure(chemin: Path) -> dict[str, int]:
    """
    @brief `label -> measured` pour un fichier de mesure de proximité, quelle que soit sa forme.

    ⚠⚠ Deux formes coexistent dans `docs/mesures/` : la plate (`proximity_*.jsonl`, un
    enregistrement par trace) et celle à variantes (`sweep_*`, `baseline_sweep_*`,
    `contamination_*`, qui portent un sous-dictionnaire `variants`). Les deux exposent
    `measured` **au premier niveau**, parce que le nombre de cellules mesurables dépend du rayon
    et non de la variante de ligne de base. C'est ce qui rend la comparaison possible entre
    formes.
    """
    out: dict[str, int] = {}
    if not chemin.is_file():
        return out
    for ligne in chemin.read_text(errors="replace").splitlines():
        ligne = ligne.strip()
        if not ligne.startswith("{"):
            continue
        try:
            r = json.loads(ligne)
        except json.JSONDecodeError:
            continue
        if "label" in r and isinstance(r.get("measured"), int):
            out[r["label"]] = r["measured"]
    return out


PAS_ENTRE_FEUILLES_UM = 142.8
"""Le pas inter-feuilles, **mesuré ailleurs et avant** (`11` §3, cv 1,8 %). C'est lui qui fixe le
rayon corrigé, et c'est ce qui rend ce choix non ajustable — il ne vient pas de la corrélation
qu'il améliore."""


def borne_du_rayon(chemin: Path) -> float | None:
    """
    @brief La borne INFÉRIEURE du rayon qui a produit un fichier, lue dans ses propres distances.

    ⚠⚠ Une distance rendue par `proximity.py` est **plafonnée par le rayon de recherche** : au
    delà, rien n'est trouvé et la cellule n'est pas mesurée. Donc la plus grande distance médiane
    du fichier est un **minorant** du rayon employé, sans qu'aucune date, aucun nom de fichier ni
    aucun journal soit nécessaire.

    ⚠ C'est un minorant et pas le rayon : une médiane est en deçà du maximum, et aucune trace
    n'oblige la mesure à atteindre le bord. Le dire évite de publier « le rayon valait X » depuis
    une grandeur qui ne peut établir que « au moins X ».
    """
    valeurs = []
    if not chemin.is_file():
        return None
    for ligne in chemin.read_text(errors="replace").splitlines():
        ligne = ligne.strip()
        if not ligne.startswith("{"):
            continue
        try:
            r = json.loads(ligne)
        except json.JSONDecodeError:
            continue
        if isinstance(r.get("spacing_um_median"), (int, float)):
            valeurs.append(float(r["spacing_um_median"]))
    return max(valeurs) if valeurs else None


def comparer(reference: Path = REFERENCE, dossier: Path = MESURES) -> dict:
    """
    @brief Chaque fichier de mesure, comparé à la référence sur les traces qu'ils partagent.
    """
    ref = compte_mesure(reference)
    if not ref:
        raise SystemExit(
            f"référence absente ou vide : {reference}\n"
            "  la produire : ./src/excision/run_proximity.sh "
            "data/repos/windcheck/data/scroll1_tifxyz "
            "docs/mesures/proximity_scroll1_rayon_corrige.jsonl")
    lignes = []
    for f in sorted(dossier.glob("*.jsonl")):
        if f == reference:
            continue
        m = compte_mesure(f)
        communes = sorted(set(m) & set(ref))
        if not communes:
            # ⚠ Une absence de trace commune n'est PAS un desaccord : c'est un autre rouleau,
            # ou un autre corpus. Rapporte comme tel, jamais confondu avec « different ».
            lignes.append(dict(fichier=f.name, traces=len(m), communes=0,
                               identiques=0, verdict="sans trace commune"))
            continue
        identiques = sum(1 for t in communes if m[t] == ref[t])
        rapports = [m[t] / ref[t] for t in communes if ref[t]]
        median = sorted(rapports)[len(rapports) // 2] if rapports else None
        lignes.append(dict(
            fichier=f.name, traces=len(m), communes=len(communes),
            identiques=identiques,
            rapport_median=median,
            verdict=("même rayon" if identiques == len(communes)
                     else "AUTRE rayon" if identiques == 0
                     else "mélangé"),
        ))
    return dict(reference=reference.name, traces_reference=len(ref), fichiers=lignes,
                pas_entre_feuilles_um=PAS_ENTRE_FEUILLES_UM,
                borne_du_rayon={f.name: borne_du_rayon(f)
                                for f in sorted(dossier.glob("proximity_*.jsonl"))})


def _verifier(r: dict | None = None) -> int:
    echecs = comptees = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, comptees
        comptees += 1
        print(f"  {'ok  ' if ok else 'FAIL'}  {nom}" + (f"   [{detail}]" if detail else ""))
        if not ok:
            echecs += 1

    # ⚠⚠ LE DISCRIMINATEUR, teste DANS LES DEUX SENS sur des fichiers fabriques : un compte
    # identique doit dire « meme rayon », un compte different doit dire « AUTRE », et une forme
    # a variantes doit se lire comme la forme plate. Sans le troisieme, le module ne saurait
    # comparer que des fichiers de meme forme -- ce qui est precisement ce qu'il existe pour
    # depasser.
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        t = Path(d)
        (t / "ref.jsonl").write_text(
            '{"label": "a", "measured": 100}\n{"label": "b", "measured": 200}\n')
        (t / "meme.jsonl").write_text(
            '{"label": "a", "measured": 100}\n{"label": "b", "measured": 200}\n')
        (t / "autre.jsonl").write_text(
            '{"label": "a", "measured": 900}\n{"label": "b", "measured": 800}\n')
        (t / "variantes.jsonl").write_text(
            '{"label": "a", "measured": 100, "variants": {"colonnes_150": {"usable": 100}}}\n')
        (t / "ailleurs.jsonl").write_text('{"label": "z", "measured": 5}\n')
        res = {x["fichier"]: x for x in comparer(t / "ref.jsonl", t)["fichiers"]}
        v("un fichier au même compte est lu « même rayon »",
          res["meme.jsonl"]["verdict"] == "même rayon", res["meme.jsonl"]["verdict"])
        v("... et un fichier à comptes différents « AUTRE rayon »",
          res["autre.jsonl"]["verdict"] == "AUTRE rayon", res["autre.jsonl"]["verdict"])
        v("... et la forme à variantes se lit comme la forme plate",
          res["variantes.jsonl"]["verdict"] == "même rayon"
          and res["variantes.jsonl"]["communes"] == 1,
          res["variantes.jsonl"]["verdict"])
        # ⚠ « aucune trace commune » n'est PAS « autre rayon » : c'est un autre corpus, et les
        # confondre ferait declarer perimes tous les fichiers des autres rouleaux.
        v("... et l'absence de trace commune n'est pas un désaccord",
          res["ailleurs.jsonl"]["verdict"] == "sans trace commune",
          res["ailleurs.jsonl"]["verdict"])

    if r and r.get("fichiers"):
        print("\net sur le dépôt réel")
        par_nom = {x["fichier"]: x for x in r["fichiers"]}
        # ⚠⚠⚠ LE RESULTAT QUI COMPTE : le fichier sur lequel `07` §8 conclut porte un AUTRE
        # rayon que le fichier corrige. Ecrit comme une assertion pour qu'un run futur qui le
        # verrait s'accorder -- parce que quelqu'un l'aurait regenere -- FASSE TOMBER ce
        # controle, et donc oblige a relire `07` §8 et §11.
        p = par_nom.get("proximity_scroll1.jsonl")
        v("le fichier de `07` §8 porte un AUTRE rayon que la référence",
          p is not None and p["verdict"] == "AUTRE rayon",
          f"{p['identiques']}/{p['communes']} traces au même compte · "
          f"rapport médian {p['rapport_median']:.2f}" if p else "absent")
        # ⚠⚠⚠ ET LE FICHIER DIT LUI-MEME JUSQU'OU SON RAYON PORTAIT. Une distance est plafonnee
        # par le rayon, donc la plus grande mediane du fichier en est un minorant. Exprime en
        # PAS INTER-FEUILLES, ca dit directement ce que `07` §9 diagnostique : l'ancien rayon
        # atteignait la spire VOISINE, qui est de la geometrie normale.
        bornes = r.get("borne_du_rayon") or {}
        pas = r.get("pas_entre_feuilles_um") or PAS_ENTRE_FEUILLES_UM
        ba = bornes.get("proximity_scroll1.jsonl")
        bc = bornes.get("proximity_scroll1_rayon_corrige.jsonl")
        if ba and bc:
            v("l'ancien fichier atteignait AU MOINS deux pas de feuille",
              ba / pas >= 2.0,
              f"{ba:.1f} µm, soit {ba / pas:.1f} pas de {pas:.1f} µm")
            v("... et le corrigé ne dépasse pas un seul pas",
              bc / pas <= 1.0, f"{bc:.1f} µm, soit {bc / pas:.2f} pas")
        autres = [x["fichier"] for x in r["fichiers"] if x["verdict"] == "AUTRE rayon"]
        v("... et il n'est pas le seul", len(autres) >= 2,
          ", ".join(autres[:6]) + (" …" if len(autres) > 6 else ""))

    print()
    if echecs:
        print(f"  ECHEC ({echecs} failures)")
    else:
        print(f"  ALL PASS (0 failures, {comptees} checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    a = p.parse_args()

    r = comparer()
    print(f"référence : {r['reference']} ({r['traces_reference']} traces)\n")
    print(f"  {'fichier':44s} {'traces':>7s} {'communes':>9s} {'identiques':>11s}  verdict")
    for x in r["fichiers"]:
        print(f"  {x['fichier']:44s} {x['traces']:7d} {x['communes']:9d} "
              f"{x['identiques']:11d}  {x['verdict']}")
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nécrit : {a.json}")
    if a.verifier:
        print()
        return 1 if _verifier(r) else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
