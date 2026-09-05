#!/usr/bin/env python3
"""À quel pas les `normal-grids` publiées échantillonnent-elles ? — et ce que ça interdit.

⚠⚠ POURQUOI CE FICHIER EXISTE. La tâche **A2 ter** du registre `75` demande le test d'identité
par les **résidus** : intégrer le champ d'orientation sur une petite boucle et compter les
charges topologiques ±2π, comme le dépliage de phase InSAR que `69` §3.2 transporte. Le
registre écarte explicitement `lasagna` — ses `nx`/`ny` sont un champ **2D**, `26` l'a payé —
et désigne les grilles `xy`/`xz`/`yz` des **`normal-grids`**.

⭐⭐⭐ **Avant d'intégrer quoi que ce soit, il faut savoir à quel pas le champ est
échantillonné**, et c'est écrit dans le produit : `metadata.json` déclare `grid-step: 64`, et
l'en-tête binaire de chaque `.grid` le redit. Sur `PHerc0139`, 64 voxels de 9,362 µm font
**599 µm**, soit **3,9 écarts inter-feuilles** (154,1 µm mesurés par `76`).

  ⚠⚠⚠ Un résidu est une intégrale de boucle **feuille à feuille** : la grandeur intégrée est
    @f$\\nabla\\psi@f$ dont la norme vaut @f$2\\pi/b@f$ avec @f$b@f$ le pas local. Un champ dont
    **une cellule couvre presque quatre feuilles** ne porte pas ce gradient — il est replié.
    Il faut au moins deux échantillons par écart (Nyquist), donc un pas de grille **≤ 8
    voxels** ici : le produit publié est **7,8 fois trop grossier**.

⭐ C'est la même classe de borne que celle qui a fermé **A2 bis** — *« ce qui borne vraiment
A2 bis, c'est la RÉSOLUTION, pas le `nz` manquant »* — sur un autre produit et pour une autre
raison. Ce n'est pas la même mesure refaite : là c'était le niveau de pyramide d'un champ de
fibres, ici c'est le pas d'échantillonnage d'un champ de normales.

⚠ Ce fichier ne dit PAS que les grilles sont inutiles. Il dit qu'elles ne portent pas la
grandeur qu'A2 ter intégrerait. `26` §7 nomme déjà la sortie : `vc_gen_normalgrids` sait
générer des grilles **depuis un volume** plutôt que depuis une prédiction — et rien n'oblige à
garder le pas de 64.

Usage :
    uv run python src/nappe/le_pas_de_la_grille.py --verifier
    uv run python src/nappe/le_pas_de_la_grille.py \\
        --json docs/mesures/le_pas_de_la_grille.json
"""

from __future__ import annotations

import argparse
import json
import struct
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
BUCKET = "https://vesuvius-challenge-open-data.s3.amazonaws.com"

MAGIE = b"VCGS"
"""Les quatre premiers octets d'un `.grid`. ⚠ Vérifiés : lire un pas dans un fichier qui n'est
pas une grille rendrait un entier plausible pris n'importe où."""

MOT_DU_PAS = 6
"""Le pas de grille est le 7ᵉ mot de 32 bits, gros-boutiste. ⚠ Cet indice n'est PAS deviné : il
est **recoupé** avec `grid-step` de `metadata.json`, et un désaccord est un refus."""

PRODUITS = {
    "PHerc0139": ("PHerc0139/representations/predictions/surfaces/"
                  "20250728140407-surface-20260413222639-surface-m7-L0-th0.2.normal-grids",
                  9.362, 154.1),
    "PHerc0358": ("PHerc0358/representations/predictions/surfaces/"
                  "20250821151737-surface-20260413222639-surface-m7-L0-th0.2.normal-grids",
                  9.362, 150.0),
}
"""Les `normal-grids` publiées, avec le voxel du volume et le pas inter-feuilles du rouleau.

⚠⚠ Le pas de `PHerc0139` est **mesuré** (`docs/mesures/le_sens_des_indices.json`, 154,1 µm sur
37 spires approuvées), pas emprunté. Celui de `PHerc0358` est celui du corpus et sert de
comparaison : c'est le rouleau que `26` a inventorié.
⚠ `PHerc0172`, l'autre rouleau à indices de spire publiés, **ne publie aucune grille**."""


def entete_de_grille(octets: bytes) -> dict:
    """
    @brief Ce que l'en-tête d'un `.grid` déclare — magie, version, étendues, pas.

    ⚠ REFUSE un fichier qui ne porte pas la magie : sans ce contrôle, un fichier tronqué ou une
    page d'erreur S3 rendrait un pas, et un pas faux se lit exactement comme un pas juste.
    """
    if len(octets) < 4 * (MOT_DU_PAS + 1):
        raise SystemExit(f"en-tête trop court : {len(octets)} octets")
    if octets[:4] != MAGIE:
        raise SystemExit(f"magie inattendue : {octets[:4]!r} au lieu de {MAGIE!r}")
    mots = struct.unpack(">%dI" % (MOT_DU_PAS + 1), octets[: 4 * (MOT_DU_PAS + 1)])
    return {"version": mots[1], "etendue": [mots[4], mots[5]], "pas_grille": mots[MOT_DU_PAS]}


def accorder(pas_entete: int, pas_metadata) -> int:
    """
    @brief Le pas déclaré par les DEUX sources du produit, ou un refus.

    ⚠⚠ Deux sources qui s'accordent valent une lecture ; une seule vaudrait une supposition,
    et deux qui divergent valent un **refus** — jamais une moyenne ni un choix. C'est aussi ce
    qui garde `MOT_DU_PAS` honnête : l'indice du mot dans l'en-tête n'est pas deviné, il est
    celui qui reproduit le `grid-step` déclaré.
    """
    if pas_metadata is None:
        raise SystemExit("metadata.json ne déclare pas de grid-step")
    if int(pas_entete) != int(pas_metadata):
        raise SystemExit(f"désaccord sur le pas : en-tête {pas_entete} contre "
                         f"metadata {pas_metadata}")
    return int(pas_entete)


def cellules_par_pas(pas_grille: int, voxel_um: float, pas_um: float) -> float:
    """Combien d'écarts inter-feuilles une seule cellule de la grille recouvre."""
    return pas_grille * voxel_um / pas_um


def pas_maximal_utile(voxel_um: float, pas_um: float) -> float:
    """
    @brief Le plus grand pas de grille qui échantillonne encore le réseau de feuilles.

    ⚠⚠ C'est **Nyquist et rien d'autre** : deux échantillons par période, donc un pas de grille
    d'au plus une demi-période. Ce n'est pas un seuil choisi — le prendre plus grand ne dégrade
    pas la mesure, il la **replie**, et un gradient replié rend un résidu qui n'a aucun rapport
    avec la feuille.
    """
    return pas_um / (2.0 * voxel_um)


def resout_le_pas(pas_grille: int, voxel_um: float, pas_um: float) -> bool:
    """Le champ échantillonné à ce pas peut-il porter un gradient feuille-à-feuille ?"""
    return pas_grille <= pas_maximal_utile(voxel_um, pas_um)


def _obtenir(url: str, timeout: float = 90.0, plage: str | None = None) -> bytes | None:
    cmd = ["curl", "-s", "--fail", "--max-time", str(int(timeout))]
    if plage:
        cmd += ["-r", plage]
    r = subprocess.run(cmd + [url], capture_output=True)
    return r.stdout if r.returncode == 0 else None


def sonder(prefixe: str, voxel_um: float, pas_um: float, tranche: int = 500) -> dict:
    """Le pas déclaré par les DEUX sources du produit, et ce qu'il vaut en feuilles.

    ⚠⚠ `metadata.json` et l'en-tête binaire disent la même chose ou le produit est refusé.
    Deux sources qui s'accordent valent une lecture ; une seule vaudrait une supposition, et
    deux qui divergent valent un refus — jamais une moyenne.
    """
    meta = _obtenir(f"{BUCKET}/{prefixe}/metadata.json")
    if meta is None:
        raise SystemExit(f"metadata.json absent : {prefixe}")
    m = json.loads(meta)
    # ⚠ Les 64 premiers octets suffisent : demander le fichier entier coûterait 300 ko par
    # tranche pour lire sept entiers.
    tete = _obtenir(f"{BUCKET}/{prefixe}/xy/{tranche:06d}.grid", plage="0-63")
    if tete is None:
        raise SystemExit(f"tranche xy/{tranche:06d}.grid absente : {prefixe}")
    e = entete_de_grille(tete)
    pas = accorder(e["pas_grille"], m.get("grid-step"))
    maxi = pas_maximal_utile(voxel_um, pas_um)
    return {"prefixe": prefixe, "voxel_um": voxel_um, "pas_inter_feuilles_um": pas_um,
            "pas_grille_vox": pas, "niveau_entree": m.get("input-level"),
            "pas_spirale": m.get("spiral-step"), "version_grille": e["version"],
            "etendue": e["etendue"],
            "pas_grille_um": pas * voxel_um,
            "cellules_par_pas": round(cellules_par_pas(pas, voxel_um, pas_um), 3),
            "pas_maximal_utile_vox": round(maxi, 2),
            "trop_grossier_de": round(pas / maxi, 2),
            "resout_le_pas": resout_le_pas(pas, voxel_um, pas_um)}


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # --- l'en-tête ---
    bon = MAGIE + struct.pack(">6I", 3, 0, 0, 6621, 6621, 64)
    e = entete_de_grille(bon)
    v("l'en-tête rend le pas de grille", e["pas_grille"] == 64, str(e))
    v("... et la version et l'étendue", e["version"] == 3 and e["etendue"] == [6621, 6621])
    # ⚠⚠ Sans le contrôle de magie, une page d'erreur S3 rendrait un entier plausible, et un
    # pas faux se lit exactement comme un pas juste.
    v("un fichier sans la magie est REFUSÉ",
      _leve(lambda: entete_de_grille(b"XXXX" + bon[4:])))
    v("... et un en-tête tronqué aussi", _leve(lambda: entete_de_grille(bon[:12])))

    # --- l'arithmétique, et son contrôle ---
    # ⚠ 64 voxels de 9,362 µm = 599 µm ; l'écart mesuré vaut 154,1 → 3,89 feuilles par cellule.
    v("une cellule de 64 voxels couvre 3,9 écarts sur PHerc0139",
      abs(cellules_par_pas(64, 9.362, 154.1) - 3.89) < 0.01,
      f"{cellules_par_pas(64, 9.362, 154.1):.3f}")
    v("le pas maximal utile est la DEMI-période, en voxels",
      abs(pas_maximal_utile(9.362, 154.1) - 8.23) < 0.01,
      f"{pas_maximal_utile(9.362, 154.1):.2f} voxels")
    v("... donc 64 ne résout pas", not resout_le_pas(64, 9.362, 154.1))
    # ⭐ Le contrôle qui empêche « ne résout jamais » d'être une propriété du calcul : à un pas
    # assez fin, la réponse doit basculer. Sans lui, la fonction pourrait rendre faux toujours.
    v("... mais 8 résout, donc la borne n'est pas une propriété du calcul",
      resout_le_pas(8, 9.362, 154.1), "8 ≤ 8,23")
    v("... et le basculement est exactement à la demi-période",
      resout_le_pas(8, 9.362, 154.1) and not resout_le_pas(9, 9.362, 154.1))
    # ⚠ La borne SUIT le rouleau : un pas inter-feuilles deux fois plus large la double.
    v("la borne suit le pas inter-feuilles, elle n'est pas écrite en dur",
      abs(pas_maximal_utile(9.362, 2 * 154.1) - 2 * pas_maximal_utile(9.362, 154.1)) < 1e-9)
    # ⚠⚠ Et le compte de feuilles par cellule doit VARIER avec ses trois entrées : sans ce
    # contrôle, une constante écrite en dur satisferait le contrôle précédent, qui ne porte
    # que sur la borne. Mesuré le 2026-09-05 : la sonde « 3,89 en dur » rendait ALL PASS.
    v("... et les feuilles par cellule varient avec les trois entrées",
      abs(cellules_par_pas(128, 9.362, 154.1) - 2 * cellules_par_pas(64, 9.362, 154.1)) < 1e-9
      and cellules_par_pas(64, 9.362, 2 * 154.1) < cellules_par_pas(64, 9.362, 154.1)
      and cellules_par_pas(64, 2 * 9.362, 154.1) > cellules_par_pas(64, 9.362, 154.1),
      f"64→{cellules_par_pas(64, 9.362, 154.1):.2f}, "
      f"128→{cellules_par_pas(128, 9.362, 154.1):.2f}")

    # ⚠⚠⚠ LE RECOUPEMENT DES DEUX SOURCES, testé hors ligne parce que sur le vrai produit
    # elles s'accordent — donc retirer le contrôle n'y changerait rien et il passerait pour
    # bon sans rien vérifier. Mesuré : la sonde rendait ALL PASS avant ce contrôle.
    v("deux sources d'accord rendent le pas", accorder(64, 64) == 64)
    v("... deux sources qui DIVERGENT sont un refus, jamais une moyenne",
      _leve(lambda: accorder(64, 32)))
    v("... et un metadata muet aussi", _leve(lambda: accorder(64, None)))

    # --- contre le VRAI produit ---
    try:
        r = sonder(*PRODUITS["PHerc0139"])
    except SystemExit as err:
        print(f"  ⚠ produit injoignable : {err}")
        r = None
    if r:
        v(f"le pas publié de PHerc0139 est {r['pas_grille_vox']} voxels, "
          f"déclaré DEUX fois et d'accord", r["pas_grille_vox"] == 64,
          f"metadata + en-tête · niveau {r['niveau_entree']}")
        v(f"... soit {r['cellules_par_pas']} écarts inter-feuilles par cellule",
          r["cellules_par_pas"] > 3.0)
        # ⭐⭐ LA CONCLUSION, assertée dans le sens où elle a été mesurée : elle tombe le jour où
        # un produit plus fin est publié, et ce serait une bonne nouvelle.
        v("... donc le champ publié NE PORTE PAS un gradient feuille-à-feuille",
          not r["resout_le_pas"], f"trop grossier d'un facteur {r['trop_grossier_de']}")

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def _leve(f) -> bool:
    try:
        f()
    except SystemExit:
        return True
    except Exception:  # noqa: BLE001
        return False
    return False


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    out = []
    for nom, (prefixe, voxel, pas) in PRODUITS.items():
        try:
            out.append({"rouleau": nom, **sonder(prefixe, voxel, pas)})
        except SystemExit as err:
            out.append({"rouleau": nom, "refus": str(err)})
    print(f"{'rouleau':12s} {'pas grille':>11s} {'en µm':>8s} {'feuilles/cellule':>17s} "
          f"{'pas max utile':>14s} {'résout ?':>9s}")
    print("-" * 78)
    for r in out:
        if "refus" in r:
            print(f"{r['rouleau']:12s}  ⚠ {r['refus']}")
            continue
        print(f"{r['rouleau']:12s} {r['pas_grille_vox']:11d} {r['pas_grille_um']:8.0f} "
              f"{r['cellules_par_pas']:17.2f} {r['pas_maximal_utile_vox']:14.2f} "
              f"{'oui' if r['resout_le_pas'] else 'NON':>9s}")
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
