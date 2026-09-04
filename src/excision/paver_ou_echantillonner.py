#!/usr/bin/env python3
"""Un corpus publié PAVE-t-il le rouleau, ou l'échantillonne-t-il ? — et la réponse dépend de qui l'a fait.

⭐⭐⭐ CE QUE CE FICHIER ÉTABLIT, ET IL AFFINE UN RÉSULTAT DE L'ARTICLE. Le §5.7 mesure sur les
15 segments de `PHerc1447` que « les segments publiés ne pavent pas une feuille » — c'est juste,
et `73` §2.6 a corrigé la formulation : ces quinze-là sont des `auto_grown_<horodatage>`, les
sorties d'un traceur à graine aléatoire. Le résultat portait donc sur le **traçage
automatique**, pas sur « ce que le concours publie ».

Or `PHerc0139` publie 37 spires **curatées**, et elles pavent. La bonne formulation n'est donc
pas « les segments publiés ne pavent pas » mais :

    le traçage automatique ÉCHANTILLONNE le rouleau ; une segmentation curatée le PAVE.

⚠⚠ LA COMPARAISON QUI SERAIT FAUSSE, et c'est celle qu'on fait spontanément. Comparer la
distribution de TOUTES les paires des deux corpus ne veut rien dire : `PHerc0139` publie 37
spires consécutives, donc ses paires lointaines (w023 contre w059) sont à 36 feuilles et
tireraient sa médiane exactement là où est celle de `PHerc1447`. Les deux corpus paraîtraient
identiques.

La question qui décide est une question de **couverture**, pas de moyenne :

    combien de segments ont un VOISIN à une feuille — c'est-à-dire de quoi former une chaîne ?

⚠ CE QUE CE FICHIER N'ÉTABLIT PAS :

1. **Que `PHerc0139` soit pavé en ENTIER.** 37 spires sur ~110, donc une bande, pas le rouleau.
   Ce qui est mesuré est que la bande publiée est **contiguë**, pas qu'elle est complète.
2. **Que la différence vienne de la curation et non du rouleau.** Les deux corpus sont sur deux
   rouleaux différents, donc le facteur « curaté / automatique » est confondu avec le facteur
   « rouleau ». Ce qui l'appuie quand même : `PHerc0172`, un troisième rouleau, publie lui aussi
   des spires curatées **et** des `auto_grown`, et seules les premières sont indexées.
3. **Que l'aire d'une spire curatée soit utilisable telle quelle.** Elle est publiée
   (`76`, 38,4 cm² médian) ; rien ici ne dit ce qu'un prédicat d'approbation en garderait.

Usage :
    uv run python src/excision/paver_ou_echantillonner.py --verifier
    uv run python src/excision/paver_ou_echantillonner.py --json docs/mesures/paver_ou_echantillonner.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
MESURES = RACINE / "docs" / "mesures"

VOISINES_UM = 250.0
"""Deux surfaces distantes de moins que ça sont des feuilles adjacentes. ⚠ Le seuil n'est pas
choisi ici : c'est celui de `commun/carte_segments.py`, que l'article §5.7 emploie déjà. Un
second seuil pour la même question serait une seconde réponse."""


def _chaine(ecarts_au_plus_proche: list[float]) -> dict:
    """
    @brief De ces écarts au plus proche voisin, combien composent une chaîne de feuilles ?
    """
    proches = [e for e in ecarts_au_plus_proche if e is not None and e < VOISINES_UM]
    return dict(
        segments=len(ecarts_au_plus_proche),
        avec_un_voisin=len(proches),
        part_avec_un_voisin=len(proches) / max(1, len(ecarts_au_plus_proche)),
        ecart_median_au_voisin=float(np.median(proches)) if proches else None,
    )


def _automatique() -> dict:
    """
    @brief `PHerc1447` : 15 segments `auto_grown`, relus de la mesure qui les a comparés.

    ⚠ Relus plutôt que recalculés : `carte_segments.py` a déjà payé les 105 paires, et deux
    calculs d'une même chose finiraient par ne pas s'accorder.
    """
    source = MESURES / "segments_PHerc1447.json"
    if not source.is_file():
        return {}
    d = json.loads(source.read_text())
    noms = [x["nom"] if isinstance(x, dict) else str(x) for x in d["segments"]]
    # ⚠ Un segment dont AUCUNE paire n'a pu etre mesuree n'a pas « aucun voisin proche » : il
    # n'a pas ete mesure. Les deux se distinguent, sinon on compterait une lacune d'instrument
    # comme un fait sur le rouleau.
    au_plus_proche: dict[str, float] = {}
    for paire in d["paires"]:
        e = paire.get("ecart_um")
        if e is None:
            continue
        for cote in ("a", "b"):
            nom = paire[cote]
            au_plus_proche[nom] = min(au_plus_proche.get(nom, 1e18), float(e))
    r = _chaine([au_plus_proche.get(n) for n in noms if n in au_plus_proche])
    r.update(rouleau=d.get("rouleau", "PHerc1447"), genre="auto_grown",
             segments_publies=len(noms), segments_mesures=len(au_plus_proche),
             paires_mesurees=sum(1 for p in d["paires"] if p.get("ecart_um") is not None))
    return r


def _curatee(nom: str = "PHerc0139") -> dict:
    """
    @brief Un rouleau à spires indexées : chaque spire a-t-elle une voisine à une feuille ?

    L'écart au plus proche voisin d'une spire `w_k` est le plus petit de ses écarts à `w_{k-1}`
    et `w_{k+1}`, déjà mesurés par `le_sens_des_indices.py`.
    """
    fichier = "le_sens_des_indices.json" if nom == "PHerc0139" \
        else f"le_sens_des_indices_{nom}.json"
    source = MESURES / fichier
    if not source.is_file():
        return {}
    d = json.loads(source.read_text())
    voxel = d["voxel_um"]
    ecarts: dict[int, float] = {}
    for c in d["consecutives"]:
        e = abs(c["median_vx"]) * voxel
        for k in (c["de"], c["vers"]):
            ecarts[k] = min(ecarts.get(k, 1e18), e)
    r = _chaine(list(ecarts.values()))
    r.update(rouleau=nom, genre="spires curatées", segments_publies=d["spires_en_cache"],
             segments_mesures=len(ecarts), paires_mesurees=d["paires_consecutives"])
    return r


def _mediane_toutes_paires_um(d: dict) -> float | None:
    """
    @brief L'écart médian sur TOUTES les paires d'un corpus de spires consécutives.

    ⚠⚠ Ce nombre existe ici pour être montré FAUX comme discriminant, pas pour être utilisé.
    Il n'est pas mesuré paire par paire — il se dérive de la linéarité établie par `76` : sur
    `n` spires consécutives, l'écart d'indice médian entre deux spires tirées au hasard vaut
    environ `n/3`, et un pas d'indice vaut un écart constant.
    """
    n = d.get("spires_en_cache", 0)
    if n < 3 or not d.get("ecart_median_um"):
        return None
    # mediane de |i-j| sur les paires d'un intervalle de n entiers : ~ n/3
    return float(d["ecart_median_um"] * n / 3.0)


def _le_piege() -> dict:
    """
    @brief Ce que rendrait la comparaison qu'on fait spontanément — et pourquoi elle ne discrimine pas.
    """
    auto = MESURES / "segments_PHerc1447.json"
    cur = MESURES / "le_sens_des_indices.json"
    if not auto.is_file() or not cur.is_file():
        return {}
    paires = [p["ecart_um"] for p in json.loads(auto.read_text())["paires"]
              if p.get("ecart_um") is not None]
    d = json.loads(cur.read_text())
    return dict(
        automatique_um=float(np.median(paires)) if paires else None,
        curatee_um=_mediane_toutes_paires_um(d),
    )


def mesurer() -> dict:
    auto = _automatique()
    cur = [c for c in (_curatee("PHerc0139"), _curatee("PHerc0172")) if c]
    return dict(automatique=auto, curatees=cur, seuil_voisines_um=VOISINES_UM,
                le_piege=_le_piege())


def _verifier(r: dict) -> int:
    echecs = 0
    comptees = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, comptees
        comptees += 1
        print(f"  {'ok  ' if ok else 'FAIL'}  {nom}" + (f"   [{detail}]" if detail else ""))
        if not ok:
            echecs += 1

    a = r["automatique"]
    print("le traçage automatique échantillonne — ce que l'article §5.7 mesure")
    v("des segments `auto_grown` ont été comparés",
      a.get("paires_mesurees", 0) > 20, f"{a.get('paires_mesurees')} paires mesurées")
    v("presque aucun n'a de voisin à une feuille",
      a.get("part_avec_un_voisin", 1.0) < 0.35,
      f"{a.get('avec_un_voisin')}/{a.get('segments')} segments "
      f"({a.get('part_avec_un_voisin', 0) * 100:.0f} %)")

    print("une segmentation curatée pave — ce que l'article ne dit pas encore")
    for c in r["curatees"]:
        v(f"{c['rouleau']} : chaque spire a une voisine à une feuille",
          c["part_avec_un_voisin"] > 0.90,
          f"{c['avec_un_voisin']}/{c['segments']} ({c['part_avec_un_voisin'] * 100:.0f} %), "
          f"écart médian {c['ecart_median_au_voisin']:.0f} µm")

    # ⚠⚠ LE CONTROLE QUI FAIT DE CA UN CONTRASTE ET NON DEUX MESURES : la difference doit etre
    # ENORME, pas seulement du bon signe. Deux corpus a 60 % et 70 % raconteraient la meme
    # histoire avec des mots differents.
    if r["curatees"] and a:
        meilleure = max(c["part_avec_un_voisin"] for c in r["curatees"])
        v("l'écart entre les deux régimes est un facteur, pas une nuance",
          meilleure > 3 * max(a.get("part_avec_un_voisin", 0.0), 1e-9),
          f"{meilleure * 100:.0f} % contre {a.get('part_avec_un_voisin', 0) * 100:.0f} %")

    # ⚠⚠⚠ LA DEMONSTRATION QUE LA MESURE DE COUVERTURE EST NECESSAIRE, et elle est ecrite dans
    # le sens « les deux se RESSEMBLENT ». Un lecteur qui compare les distributions de toutes
    # les paires trouve deux corpus indiscernables -- alors que l'un pave et l'autre non. Sans
    # ce controle, le paragraphe d'avertissement en tete du fichier serait une opinion.
    piege = r.get("le_piege") or {}
    print("le piège : la comparaison spontanée ne discrimine PAS")
    if piege.get("automatique_um") and piege.get("curatee_um"):
        a_um, c_um = piege["automatique_um"], piege["curatee_um"]
        v("l'écart médian sur toutes les paires est du même ordre dans les deux corpus",
          0.5 < c_um / a_um < 2.0,
          f"{a_um:.0f} µm (auto) contre {c_um:.0f} µm (curaté), rapport {c_um / a_um:.2f}")
    else:
        print("  --    (mesures amont absentes)")

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
    args = p.parse_args()

    r = mesurer()
    if not r["automatique"] or not r["curatees"]:
        raise SystemExit(
            "mesures amont absentes. Les produire :\n"
            "  uv run python src/commun/carte_segments.py --rouleau PHerc1447 "
            "--json docs/mesures/segments_PHerc1447.json\n"
            "  uv run python src/excision/le_sens_des_indices.py "
            "--json docs/mesures/le_sens_des_indices.json")

    if not args.verifier or args.json:
        entete = f"  {'corpus':24s} {'genre':16s} {'seg':>4s} {'voisin ≤250µm':>14s} {'écart méd.':>11s}"
        print(entete)
        a = r["automatique"]
        print(f"  {a['rouleau']:24s} {a['genre']:16s} {a['segments']:4d} "
              f"{a['avec_un_voisin']:6d} ({a['part_avec_un_voisin'] * 100:3.0f} %) "
              f"{a['ecart_median_au_voisin'] or 0:9.0f} µm")
        for c in r["curatees"]:
            print(f"  {c['rouleau']:24s} {c['genre']:16s} {c['segments']:4d} "
                  f"{c['avec_un_voisin']:6d} ({c['part_avec_un_voisin'] * 100:3.0f} %) "
                  f"{c['ecart_median_au_voisin']:9.0f} µm")

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
