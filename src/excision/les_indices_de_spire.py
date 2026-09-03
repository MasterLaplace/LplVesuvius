#!/usr/bin/env python3
"""Les segments publiés portent leur numéro de spire — combien, lesquels, et sur quels rouleaux.

⭐⭐⭐ CE QUE CE FICHIER ÉTABLIT, ET IL VIENT D'UNE OBSERVATION EXTÉRIEURE.
`docs/73` §4 (« une chose que le dépôt n'a pas vue ») relève que les segments publiés portent
leur **numéro de spire** dans leur suffixe — `w023`, `w024`… — et qu'aucun instrument du dépôt
ne le lit. C'est **vrai**, et c'est le référent d'**identité** qui manquait : une spire publiée
dit *laquelle* des feuilles une surface suit, ce qu'aucune vérité terrain du dépôt ne disait.

⚠⚠ MAIS LE COMPTE ANNONCÉ EST FAUX D'UN FACTEUR ~3, ET DANS LE SENS FAVORABLE.
`73` §4 écrit « 57 segments, 56 spires distinctes » sur **deux** rouleaux (`PHerc0139`,
`PHerc1667`). Mesuré ici sur `data/metadata.min.json` : il y en a **plus de cent, sur trois
rouleaux**, plus un quatrième qui indexe des **plages** de spires. `PHerc0172` — 44 segments,
soit plus que `PHerc0139` — est absent de son inventaire.

⭐⭐ ET LA PROPRIÉTÉ QUI COMPTE N'EST PAS LE COMPTE, C'EST LA CONTINUITÉ.
`73` §5 déclare `[je ne sais pas]` si les indices publiés sont consécutifs, et bâtit son
hypothèse H1′ (« un entier constant par spire, consécutif entre `w_k` et `w_{k+1}` ») sur
`PHerc1667`, qui est **lacunaire** (il saute 13→18→23→28). Deux rouleaux portent au contraire
une course **sans aucun trou**, et ce sont eux qui rendent H1′ testable :

    PHerc0139  w023 … w059   37 segments, 37 spires, 0 trou
    PHerc0172  w052 … w095   44 segments, 44 spires, 0 trou

Une course sans trou est ce que le test d'identité exige : « consécutif entre deux spires
consécutives » n'est une question que là où deux spires consécutives sont publiées.

⚠⚠⚠ ET LA MESURE DÉSIGNE UN AUTRE ROULEAU QUE LE PLAN QUI L'A DEMANDÉE. `73` §3.3 construit
l'identité sur les indices de spire (mois 1–2), puis déploie l'extraction sur **`PHerc0800`**
ou **`PHerc1447`** (mois 4–7), choisis sur la queue de `d′` de la carte dense. Or ces deux
rouleaux publient **zéro** segment indexé : tout ce qu'ils publient est `auto_grown_*`. Le
prédicat d'identité serait donc validé sur un rouleau et déployé sur un autre, sans que rien
ne dise que le transport tient.

⭐⭐⭐ Un seul rouleau porte **les deux**, et c'est `PHerc0139` : 37 spires consécutives sans
trou, une carte dense sur 91 fenêtres (au-dessus des 50–100 que `33` exige pour que le
classement tienne), et une queue à **4,4 %** — deuxième des quatorze, devant `PHerc1447`
(7,0 %) que `73` retenait. Il est de plus déjà transformé dans le repère du **régime du prix**
(`68` §4). `73` ne l'a pas retenu comme candidat parce que son fichier de carte dense s'appelle
`_TEMOIN_PHerc0139.json` : il l'a lu comme un témoin, pas comme un rouleau.

⚠ Ma première version de ce fichier affirmait que les deux ensembles sont **disjoints**. Le
contrôle a échoué et il avait raison ; la conclusion ci-dessus est celle que la mesure impose,
et elle est plus utile que celle que j'allais écrire.

⚠ CE QUE CE FICHIER N'ÉTABLIT PAS, et il faut le dire à chaque usage :

1. **Que `w` compte les spires dans le même sens sur les quatre rouleaux**, ni depuis le
   centre, ni depuis l'extérieur. `73` §4 le déclare `[je ne sais pas]` et il a raison ; ça se
   tranche en mesurant le rayon médian de `w_k` contre `w_{k+1}` sur les `tifxyz` transformés,
   ce que ce fichier ne fait pas. Tant que ce n'est pas fait, « consécutif » est une propriété
   des **noms**, pas une propriété géométrique vérifiée.
2. **Qu'un indice publié soit exact.** Il est publié, donc adopté par un humain ; rien ici ne
   le recalcule.
3. **Que l'absence d'indice signifie l'absence d'approbation.** `PHerc1447` et `PHerc0800` ne
   publient que des `auto_grown_*`, ce qui dit que leur traçage est automatique — pas que
   personne ne les a regardés.

Usage :
    uv run python src/excision/les_indices_de_spire.py --verifier
    uv run python src/excision/les_indices_de_spire.py --json docs/mesures/les_indices_de_spire.json
"""

from __future__ import annotations

import argparse
import gzip
import json
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
METADONNEES = RACINE / "data" / "metadata.min.json"
CARTE_DENSE = RACINE / "docs" / "carte_separabilite_dense"

SUFFIXE = re.compile(r"^w(\d{3})(?:-(\d{3}))?")
"""Un suffixe de segment publié. Deux formes, et elles ne disent pas la même chose :
`w023_…` nomme **une** spire, `w010-027` nomme une **plage** de spires. Les confondre
gonflerait le compte de spires indexées d'un facteur cinq sur `PHercParis4`."""


def _suffixe(segment: dict) -> str:
    """
    @brief Le suffixe d'un segment, où qu'il soit rangé dans l'enregistrement.
    """
    props = segment.get("properties") or {}
    return str(props.get("suffix") or segment.get("suffix") or "")


def inventorier() -> dict:
    """
    @brief Par rouleau : combien de segments, combien portent un indice de spire, et si la
           course indexée a des trous.
    """
    if not METADONNEES.is_file():
        raise SystemExit(f"métadonnées absentes : {METADONNEES}")
    with gzip.open(METADONNEES, "rt", encoding="utf-8") as f:
        echantillons = json.load(f)["samples"]

    par_rouleau = {}
    for rouleau, enregistrement in echantillons.items():
        segments = enregistrement.get("segments") or {}
        if not segments:
            continue
        uniques, plages, autres = [], [], []
        for _, segment in segments.items():
            suffixe = _suffixe(segment)
            trouve = SUFFIXE.match(suffixe)
            if not trouve:
                autres.append(suffixe)
            elif trouve.group(2):
                plages.append((int(trouve.group(1)), int(trouve.group(2))))
            else:
                uniques.append(int(trouve.group(1)))

        distinctes = sorted(set(uniques))
        trous = [[a, b] for a, b in zip(distinctes, distinctes[1:]) if b - a > 1]
        couvertes = set()
        for a, b in plages:
            couvertes |= set(range(a, b + 1))

        par_rouleau[rouleau] = dict(
            segments=len(segments),
            indexes_uniques=len(uniques),
            spires_distinctes=len(distinctes),
            premiere=distinctes[0] if distinctes else None,
            derniere=distinctes[-1] if distinctes else None,
            trous=trous,
            course_sans_trou=bool(distinctes) and not trous,
            segments_de_plage=len(plages),
            spires_couvertes_par_plages=len(couvertes),
            # ⚠ Compté, pas supposé : c'est ce qui distingue un rouleau tracé à la main d'un
            # rouleau tracé par une graine aléatoire (article §5.7).
            auto_grown=sum(1 for s in autres if s.startswith("auto_grown")),
        )
    return par_rouleau


def _queue_de_separabilite() -> dict:
    """
    @brief La part de fenêtres indissociables par rouleau, relue depuis la carte dense.

    Relue plutôt que recopiée : un chiffre recopié est un chiffre qui peut se désaccorder de
    sa source. Le nom de fichier porte parfois un préfixe `_TEMOIN_`, qu'on retire.
    """
    sortie = {}
    if not CARTE_DENSE.is_dir():
        return sortie
    for chemin in sorted(CARTE_DENSE.glob("*.json")):
        nom = chemin.stem.replace("_TEMOIN_", "")
        try:
            sortie[nom] = float(json.load(open(chemin, encoding="utf-8"))["part_sous_1"])
        except (KeyError, ValueError, OSError):
            continue
    return sortie


def mesurer() -> dict:
    inventaire = inventorier()
    queue = _queue_de_separabilite()

    indexes = {r: v for r, v in inventaire.items() if v["indexes_uniques"]}
    sans_trou = {r: v for r, v in indexes.items() if v["course_sans_trou"]}

    # ⭐ Le croisement qui porte la conclusion : les rouleaux qui ont un référent d'identité
    # ont-ils aussi une bonne queue de séparabilité ?
    croisement = []
    for rouleau in sorted(set(inventaire) | set(queue)):
        v = inventaire.get(rouleau, {})
        croisement.append(dict(
            rouleau=rouleau,
            spires_indexees=v.get("spires_distinctes", 0),
            course_sans_trou=v.get("course_sans_trou", False),
            part_sous_1=queue.get(rouleau),
        ))

    avec_les_deux = [c["rouleau"] for c in croisement
                     if c["spires_indexees"] and c["part_sous_1"] is not None]

    return dict(
        source=str(METADONNEES.relative_to(RACINE)),
        rouleaux_avec_segments=len(inventaire),
        rouleaux_indexes=sorted(indexes),
        total_segments_indexes=sum(v["indexes_uniques"] for v in indexes.values()),
        total_spires_distinctes=sum(v["spires_distinctes"] for v in indexes.values()),
        courses_sans_trou=sorted(sans_trou),
        total_spires_sans_trou=sum(v["spires_distinctes"] for v in sans_trou.values()),
        # `73` §4 annonce 57 segments sur deux rouleaux ; gardé ici pour que l'écart soit
        # visible dans le JSON et pas seulement dans une prose.
        annonce_73=dict(segments=57, rouleaux=["PHerc0139", "PHerc1667"], spires=56),
        croisement=croisement,
        rouleaux_avec_referent_et_carte=avec_les_deux,
        inventaire=inventaire,
    )


def _queue(r: dict, rouleau: str):
    """
    @brief La part de fenêtres indissociables d'un rouleau, ou None si la carte ne le couvre pas.
    """
    for c in r["croisement"]:
        if c["rouleau"] == rouleau:
            return c["part_sous_1"]
    return None


def _verifier(r: dict) -> int:
    echecs = 0

    def v(nom, ok, detail=""):
        nonlocal echecs
        print(f"  {'ok  ' if ok else 'FAIL'}  {nom}" + (f"   [{detail}]" if detail else ""))
        if not ok:
            echecs += 1

    inv = r["inventaire"]

    print("le référent existe — et c'est la moitié juste de `73` §4")
    v("des segments publiés portent un indice de spire",
      r["total_segments_indexes"] > 0,
      f"{r['total_segments_indexes']} segments sur {len(r['rouleaux_indexes'])} rouleaux")
    v("`PHerc0139` et `PHerc1667` en portent, comme annoncé",
      {"PHerc0139", "PHerc1667"} <= set(r["rouleaux_indexes"]))

    print("mais le compte annoncé est un minorant, et le rouleau manquant est le plus fourni")
    v("il y a plus de segments indexés que les 57 annoncés",
      r["total_segments_indexes"] > r["annonce_73"]["segments"],
      f"{r['total_segments_indexes']} contre {r['annonce_73']['segments']}")
    v("`PHerc0172` est indexé et absent de l'inventaire de `73`",
      inv.get("PHerc0172", {}).get("indexes_uniques", 0) > 0
      and "PHerc0172" not in r["annonce_73"]["rouleaux"],
      f"{inv.get('PHerc0172', {}).get('indexes_uniques', 0)} segments")
    v("... et il en porte plus que `PHerc0139`",
      inv.get("PHerc0172", {}).get("indexes_uniques", 0)
      > inv.get("PHerc0139", {}).get("indexes_uniques", 0),
      f"{inv.get('PHerc0172', {}).get('indexes_uniques', 0)} contre "
      f"{inv.get('PHerc0139', {}).get('indexes_uniques', 0)}")

    print("la propriété qui rend H1′ testable est la continuité, pas le compte")
    v("au moins deux rouleaux ont une course sans aucun trou",
      len(r["courses_sans_trou"]) >= 2, ", ".join(r["courses_sans_trou"]))
    # ⚠ Le contrôle qui empêche « sans trou » de passer pour gratuit : le rouleau sur lequel
    # `73` bâtit H1′ en a, lui, et son hypothèse y serait donc mal posée.
    v("`PHerc1667`, le rouleau choisi par `73`, est lacunaire",
      not inv.get("PHerc1667", {}).get("course_sans_trou", True),
      f"trous {inv.get('PHerc1667', {}).get('trous')}")

    print("et le plan déploie là où le référent n'existe pas")
    for rouleau in ("PHerc0800", "PHerc1447"):
        v(f"`{rouleau}` (cible d'extraction de `73` §3.3) ne publie aucun indice",
          inv.get(rouleau, {}).get("indexes_uniques", 0) == 0,
          f"{inv.get(rouleau, {}).get('auto_grown', 0)} auto_grown "
          f"sur {inv.get(rouleau, {}).get('segments', 0)} segments")
    # ⚠⚠ Ma première version de ce contrôle affirmait que les deux ensembles sont DISJOINTS.
    # Elle a échoué, et elle avait tort : `PHerc0139` porte les deux. C'est le contrôle qui a
    # corrigé la conclusion, pas une relecture — et la conclusion corrigée est plus forte que
    # celle que j'allais écrire.
    v("exactement un rouleau porte les deux, et c'est celui que `73` n'a pas retenu",
      r["rouleaux_avec_referent_et_carte"] == ["PHerc0139"],
      ", ".join(r["rouleaux_avec_referent_et_carte"]) or "aucun")
    v("... et sa queue de séparabilité bat celle de `PHerc1447`, cible de `73` §3.3",
      _queue(r, "PHerc0139") is not None and _queue(r, "PHerc1447") is not None
      and _queue(r, "PHerc0139") < _queue(r, "PHerc1447"),
      f"{(_queue(r, 'PHerc0139') or 0) * 100:.1f} % contre "
      f"{(_queue(r, 'PHerc1447') or 0) * 100:.1f} %")

    print()
    if echecs:
        print(f"  ECHEC ({echecs} failures)")
    else:
        print("  ALL PASS (0 failures, 11 checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    args = p.parse_args()

    r = mesurer()

    if not args.verifier or args.json:
        print(f"segments publiés portant un indice de spire : "
              f"{r['total_segments_indexes']} sur {len(r['rouleaux_indexes'])} rouleaux")
        print(f"  (`docs/73` §4 en annonce {r['annonce_73']['segments']} sur "
              f"{len(r['annonce_73']['rouleaux'])})\n")
        entete = f"  {'rouleau':14s} {'seg':>4s} {'idx':>4s} {'spires':>7s} {'course':>12s} {'trous':>6s} {'plages':>7s} {'d′<1':>7s}"
        print(entete)
        for c in r["croisement"]:
            v = r["inventaire"].get(c["rouleau"], {})
            if not v:
                continue
            course = (f"w{v['premiere']:03d}-w{v['derniere']:03d}"
                      if v["premiere"] is not None else "—")
            queue = f"{c['part_sous_1'] * 100:5.1f} %" if c["part_sous_1"] is not None else "—"
            print(f"  {c['rouleau']:14s} {v['segments']:4d} {v['indexes_uniques']:4d} "
                  f"{v['spires_distinctes']:7d} {course:>12s} {len(v['trous']):6d} "
                  f"{v['segments_de_plage']:7d} {queue:>7s}")
        print(f"\ncourses sans aucun trou : {', '.join(r['courses_sans_trou'])} "
              f"({r['total_spires_sans_trou']} spires consécutives)")
        print("rouleaux portant À LA FOIS un référent d'identité et une carte dense : "
              f"{', '.join(r['rouleaux_avec_referent_et_carte']) or 'AUCUN'}")

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nécrit : {args.json}")

    if args.verifier:
        print()
        return 1 if _verifier(r) else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
