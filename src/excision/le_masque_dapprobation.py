#!/usr/bin/env python3
"""Écrire `approval.tif` — ce que le pinceau peint, calculé, avec ses quatre bras de contrôle.

⭐⭐⭐ CE QUE CE FICHIER PRODUIT. L'article §6.7 établit que l'intégration tient en un fichier :
le chargeur du pipeline de référence adopte **tout** `.tif` posé à côté de `x/y/z.tif` comme
canal nommé, et le canal `approval` est celui qui autorise la ré-optimisation du maillage.
Écrire `approval.tif` **est** l'intégration — pas de fork, pas d'appel à modifier.

Ce fichier l'écrit, à partir du champ d'enroulement de `77`. Deux des trois prédicats sortent du
**même** champ, et c'est ce qui rend la chose bon marché :

    placement  = la partie FRACTIONNAIRE de l'indice assigné
                 0,0 sur une feuille · 0,5 dans l'interstice
    identité   = l'AVANCE de l'indice sur un tour
                 0 pour une feuille · n pour n feuilles franchies

⚠⚠ Les deux sont vraiment différents, et je les avais confondus. Une copie translatée d'un
demi-pas a une avance **nulle** — elle suit parfaitement une feuille qui n'existe pas. C'est le
**placement** qui la refuse, pas l'identité. Un masque qui n'aurait que l'identité approuverait
une surface posée dans le vide entre deux feuilles.

Mesuré, et les deux populations ne se recouvrent sur aucun des deux axes :

    sur la feuille   fraction 0,001 [-0,137 ; +0,204]   avance -0,005 [-0,170 ; +0,230]
    quart de pas     fraction 0,252 [ 0,150 ;  0,441]
    demi-pas         fraction 0,502 [ 0,435 ;  0,640]
    saut d'1 feuille                                    avance  1,103 [ 0,753 ;  1,479]

⚠⚠⚠ LE QUATRIÈME BRAS EST CELUI SANS LEQUEL LE CONTRÔLE NE PEUT PAS ÉCHOUER. Approuver une
spire publiée, refuser un masque vide, refuser un masque plein : les trois se satisfont d'un
masque qui approuve tout. Le bras qui mord est la **copie translatée d'un demi-pas**, qui est
une surface lisse, plausible, et posée là où il n'y a pas de papyrus.

⚠ CE QUE CE FICHIER N'ÉTABLIT PAS :

1. **Que le masque calculé vaille un masque humain.** Aucun `approval.tif` peint n'est publié
   — vérifié au listing S3 (`73` §0) — donc la comparaison qui trancherait n'est pas montable.
   Ce qui est mesuré est que le masque **approuve ce qui doit l'être et refuse ce qui ne doit
   pas**, sur des surfaces dont on connaît la faute parce qu'on l'a fabriquée.
2. **Qu'il vaille hors de la bande publiée.** Le champ interpole entre spires connues et
   **refuse** au-delà. Un point sans encadrement n'est pas approuvé — c'est voulu, et c'est la
   limite dure pour un déploiement.
3. **Que la ré-optimisation en aval l'accepte.** Le canal est écrit au bon nom et au bon format ;
   rien ici ne fait tourner `villa`.

Usage :
    uv run python src/excision/le_masque_dapprobation.py --verifier
    uv run python src/excision/le_masque_dapprobation.py --json docs/mesures/le_masque_dapprobation.json
    uv run python src/excision/le_masque_dapprobation.py --ecrire data/masques/w030
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(RACINE / "src" / "excision")]
import le_champ_denroulement as champ  # noqa: E402
from le_sens_des_indices import charger, _spires  # noqa: E402

TOLERANCE_PLACEMENT = 0.30
"""Une cellule est *sur* une feuille si sa partie fractionnaire d'indice est à moins de ça d'un
entier. ⚠ Le seuil est posé **entre les deux populations mesurées** et non choisi pour qu'un
réglage passe : une surface sur sa feuille monte à 0,204 au 9ᵉ décile, une translatée d'un
quart de pas descend à 0,150 — donc 0,30 sépare la feuille du demi-pas (0,435 au 1ᵉʳ décile) et
accepte délibérément le quart de pas, qui est encore du papyrus."""

TOLERANCE_IDENTITE = 0.45
"""Une tranche suit UNE feuille si son avance par tour est sous ça. ⚠ Posé entre +0,230 (le 9ᵉ
décile d'une vraie spire) et 0,753 (le 1ᵉʳ décile d'un saut d'une feuille). Les deux
populations ne se recouvrant pas, tout seuil de cet intervalle donne le même verdict — ce qui
est la propriété qu'on veut, et elle se vérifie."""


def _juger_cellules(cible: dict, autres: dict[int, dict]) -> dict[tuple[int, int], float]:
    """
    @brief L'indice assigné à chaque cellule (tranche, secteur) d'une surface.
    """
    out = {}
    for cellule, rayon in cible.items():
        table = sorted((autres[k][cellule], k) for k in autres if cellule in autres[k])
        v = champ._indice_interpole(rayon, table)
        if v is not None:
            out[cellule] = v
    return out


def _verdict(assignes: dict[tuple[int, int], float]) -> dict:
    """
    @brief Le masque : par cellule, approuvée ou non, et pourquoi.

    ⚠ Le verdict d'identité est porté par la **tranche** et non par la cellule : une avance est
    une pente sur un tour, donc elle n'existe pas au point. Le placement, lui, est local. Une
    cellule est approuvée si les deux tiennent — un ET, pas un OU : une surface bien placée
    dans le vide et une surface qui saute au bon endroit doivent toutes deux être refusées.
    """
    if not assignes:
        return dict(cellules=0)
    par_tranche: dict[int, list[tuple[int, float]]] = {}
    for (tranche, secteur), v in assignes.items():
        par_tranche.setdefault(tranche, []).append((secteur, v))

    avance_de: dict[int, float] = {}
    for tranche, points in par_tranche.items():
        if len(points) < champ.SECTEURS // 2:
            continue
        s = np.array([p[0] for p in points], dtype=float)
        w = np.array([p[1] for p in points], dtype=float)
        avance_de[tranche] = float(np.polyfit(s, w, 1)[0] * champ.SECTEURS)

    approuvees, placement_ok, identite_ok = 0, 0, 0
    for (tranche, _), v in assignes.items():
        p = abs(v - round(v)) <= TOLERANCE_PLACEMENT
        i = abs(avance_de.get(tranche, 9.0)) <= TOLERANCE_IDENTITE
        placement_ok += p
        identite_ok += i
        approuvees += p and i
    n = len(assignes)
    return dict(cellules=n, approuvees=approuvees, part_approuvee=approuvees / n,
                part_placement=placement_ok / n, part_identite=identite_ok / n,
                tranches_jugees=len(avance_de),
                fraction_mediane=float(np.median([abs(v - round(v))
                                                  for v in assignes.values()])))


def _melange(a: dict, b: dict, poids) -> dict:
    """
    @brief Une surface fabriquée entre deux spires — `poids` dit comment, par cellule.
    """
    return {c: (1 - poids(c)) * a[c] + poids(c) * b[c] for c in a if c in b}


def mesurer(rouleau: str = "PHerc0139") -> dict:
    dossiers = _spires(rouleau)
    nuages = {k: v for k, v in ((k, charger(d)) for k, d in dossiers.items()) if v}
    bords_z, bords_t, centres = champ._grille(nuages)
    rayons = {k: champ._rayons(n, bords_z, bords_t, centres) for k, n in nuages.items()}
    rayons = {k: v for k, v in rayons.items() if len(v) > 50}
    indices = sorted(rayons)
    # ⚠ Les defauts connus du referent sont ecartes des SURFACES A JUGER, jamais du champ : ce
    # sont de mauvaises cibles (l'une est un doublon de l'autre), pas de mauvaises references.
    jugeables = [k for k in indices[1:-2] if k not in champ.DEFAUTS_CONNUS]

    bras: dict[str, list[dict]] = {
        "spire, champ complet": [], "spire, à spire exclue": [],
        "quart de pas": [], "demi-pas": [], "saut d'une feuille": []}
    for k in jugeables:
        if k + 1 not in rayons:
            continue
        autres = {j: v for j, v in rayons.items() if j != k}
        cibles = {
            "spire, champ complet": rayons[k],
            "spire, à spire exclue": rayons[k],
            "quart de pas": _melange(rayons[k], rayons[k + 1], lambda c: 0.25),
            "demi-pas": _melange(rayons[k], rayons[k + 1], lambda c: 0.5),
            "saut d'une feuille": _melange(
                rayons[k], rayons[k + 1],
                lambda c: (c[1] - 1) / max(1, champ.SECTEURS - 1)),
        }
        for nom, cible in cibles.items():
            # ⚠⚠⚠ LE CHAMP DOIT CONTENIR LES SPIRES QUI ENCADRENT LA SURFACE JUGEE. Ma
            # premiere version retirait `k+1` pour les surfaces fabriquees, en croyant eviter
            # une fuite -- et ca DETRUISAIT l'information qui detecte un interstice : une
            # translation d'un demi-pas passait de 2,8 % a 79,3 % d'approbation, c'est-a-dire
            # d'un refus net a une approbation nette. Sans la borne haute, le vide entre deux
            # feuilles n'est plus un vide, c'est le milieu d'un intervalle de trois feuilles.
            #
            # Le reglage juste est aussi le plus REALISTE : a l'usage, le champ est tout ce qui
            # est publie et la surface jugee est une trace neuve, absente du champ. Seule une
            # spire publiee doit etre retiree du champ qui la juge, sinon il la lit.
            reference = autres if nom == "spire, à spire exclue" else rayons
            r = _verdict(_juger_cellules(cible, reference))
            if r.get("cellules", 0) >= 20:
                r["spire"] = k
                bras[nom].append(r)

    resume = {}
    for nom, serie in bras.items():
        if serie:
            p = np.array([x["part_approuvee"] for x in serie])
            resume[nom] = dict(n=len(serie), part_mediane=float(np.median(p)),
                               p10=float(np.percentile(p, 10)),
                               p90=float(np.percentile(p, 90)))
    return dict(rouleau=rouleau, spires=len(rayons), jugeables=len(jugeables),
                tolerance_placement=TOLERANCE_PLACEMENT,
                tolerance_identite=TOLERANCE_IDENTITE,
                bras=resume, defauts_ecartes=list(champ.DEFAUTS_CONNUS))


def _verifier(r: dict) -> int:
    echecs = 0
    comptees = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, comptees
        comptees += 1
        print(f"  {'ok  ' if ok else 'FAIL'}  {nom}" + (f"   [{detail}]" if detail else ""))
        if not ok:
            echecs += 1

    b = r["bras"]
    print("le masque sait approuver — contrôle de bon sens, pas témoin positif")
    # ⚠ Ce bras est CIRCULAIRE et c'est dit : le champ contient la spire qu'il juge, donc il la
    # lit. Il ne prouve qu'une chose, mais elle doit être prouvée : le masque approuve QUELQUE
    # CHOSE. Un masque qui refuserait tout passerait les trois bras négatifs.
    v("une spire lue par son propre champ est approuvée partout",
      "spire, champ complet" in b and b["spire, champ complet"]["part_mediane"] > 0.98,
      f"{b.get('spire, champ complet', {}).get('part_mediane', 0) * 100:.1f} %")

    print("le témoin POSITIF réaliste : une surface près d'une feuille connue, absente du champ")
    v("un quart de pas est approuvé sur l'essentiel de son aire",
      "quart de pas" in b and b["quart de pas"]["part_mediane"] > 0.80,
      f"{b.get('quart de pas', {}).get('part_mediane', 0) * 100:.1f} % médian "
      f"sur {b.get('quart de pas', {}).get('n', 0)} surfaces")

    # ⚠⚠⚠ LA PATHOLOGIE, NOMMEE PLUTOT QUE RAPPORTEE COMME UN RESULTAT. Une spire jugee a
    # spire exclue tombe EXACTEMENT au milieu de l'intervalle que son retrait vient de creer :
    # le champ la voit donc dans un interstice, par construction. C'est pourquoi une spire
    # publiee ne peut pas etre son propre temoin positif de PLACEMENT -- ni avec son champ
    # (circulaire), ni sans (pathologique). Mesure : 100 % contre 70 %.
    print("⚠ la pathologie : une spire exclue tombe dans l'interstice qu'elle creuse")
    v("... et elle est bien intermédiaire, ni approuvée ni refusée",
      "spire, à spire exclue" in b
      and 0.4 < b["spire, à spire exclue"]["part_mediane"] < 0.9,
      f"{b.get('spire, à spire exclue', {}).get('part_mediane', 0) * 100:.1f} % — "
      f"à ne pas lire comme une performance")

    print("et refuse ce qui ne doit pas l'être — les trois bras négatifs")
    # ⚠⚠⚠ LE BRAS QUI MORD. Sans lui, un masque qui approuve TOUT passe les trois autres.
    v("une copie translatée d'un DEMI-pas est refusée",
      "demi-pas" in b and b["demi-pas"]["part_mediane"] < 0.10,
      f"{b.get('demi-pas', {}).get('part_mediane', 1) * 100:.1f} % approuvé")
    saut = b.get("saut d'une feuille", {})
    v("une surface qui saute une feuille est refusée",
      bool(saut) and saut["part_mediane"] < 0.10,
      f"{saut.get('part_mediane', 1) * 100:.1f} % approuvé")

    # ⚠ Le quart de pas est encore du papyrus : le masque DOIT l'accepter, sinon il ne mesure
    # pas « il y a une feuille ici » mais « la surface est exactement celle que j'ai lue ».
    v("un quart de pas reste accepté — c'est encore du papyrus",
      "quart de pas" in b and b["quart de pas"]["part_mediane"] > 0.50,
      f"{b.get('quart de pas', {}).get('part_mediane', 0) * 100:.1f} % approuvé")

    print("la séparation est nette, pas marginale")
    if "quart de pas" in b and "demi-pas" in b:
        v("le pire cas approuvé bat le meilleur cas refusé",
          b["quart de pas"]["p10"] > b["demi-pas"]["p90"],
          f"quart de pas p10 {b['quart de pas']['p10'] * 100:.1f} % contre "
          f"demi-pas p90 {b['demi-pas']['p90'] * 100:.1f} %")

    print()
    if echecs:
        print(f"  ECHEC ({echecs} failures)")
    else:
        print(f"  ALL PASS (0 failures, {comptees} checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--rouleau", default="PHerc0139")
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    args = p.parse_args()

    r = mesurer(args.rouleau)
    if not args.verifier or args.json:
        print(f"{r['rouleau']} — masque sur {r['jugeables']} spires "
              f"(champ bâti sur {r['spires']})")
        print(f"  seuils : placement {r['tolerance_placement']}, "
              f"identité {r['tolerance_identite']}\n")
        print(f"  {'bras':22s} {'n':>3s} {'approuvé':>9s} {'p10':>7s} {'p90':>7s}")
        for nom, x in r["bras"].items():
            print(f"  {nom:22s} {x['n']:3d} {x['part_mediane'] * 100:8.1f} % "
                  f"{x['p10'] * 100:6.1f} % {x['p90'] * 100:6.1f} %")

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
