#!/usr/bin/env python3
"""Un pas d'UNE épaisseur le long de la normale mène-t-il à la feuille suivante ? — sur vérité de terrain.

⚠⚠⚠ POURQUOI CE FICHIER EXISTE, ET C'EST LA PRIMITIVE DU DÉROULEMENT. Toute la colonne « chaîne »
du dépôt repose sur une supposition jamais testée contre une vérité extérieure : *depuis une
feuille, avancer d'un écart inter-feuilles le long de la normale tombe sur la feuille voisine*.
C'est ce que fait un dérouleur, pas après pas, et si c'est faux tout ce qui suit dérive.

⭐⭐⭐ **Les treize spires publiées de `PHerc0500P2` permettent enfin de le falsifier** : elles
sont des tours consécutifs, leur écart est mesuré (135,5 µm), et la question devient exacte —
*le pas normal depuis la spire k tombe-t-il sur la spire k+1 ?*

⚠⚠ LE CONTRÔLE EST LE PAS NUL, et il n'est pas décoratif : sans bouger, la distance à la spire
suivante vaut déjà l'écart inter-feuilles. Un pas qui ne ferait pas mieux que **ne rien faire**
ne mesure rien, et c'est exactement le champ nul que ce dépôt oppose à chacun de ses modèles.

⚠ Le SIGNE de la normale est une propriété du paramétrage, pas de la matière : une grille peut
être orientée dans un sens ou dans l'autre sans que rien ne le dise. Les deux sens sont donc
essayés et **celui qui est retenu est rendu**, parce qu'un pas dont on ne dit pas la direction
est un pas qu'on peut toujours déclarer réussi.

Usage :
    uv run python src/nappe/le_pas_normal_atteint_la_spire.py --verifier
    uv run python src/nappe/le_pas_normal_atteint_la_spire.py \\
        --json docs/mesures/le_pas_normal_atteint_la_spire.json
"""

from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "commun"))
sys.path.insert(0, str(RACINE / "src" / "nappe"))

WRAPS = RACINE / "docs" / "mesures" / "les_wraps_publies.json"


def grille(wrap: dict, volume: str, voxel_um: float,
           fragment: str = "PHerc0500P2") -> tuple[np.ndarray, np.ndarray] | None:
    """La surface d'une spire **en gardant la structure de grille**, et son masque de validité.

    ⚠⚠ `les_wraps_publies.surface` rend un nuage de points, ce qui suffit à mesurer des
    distances et **pas** à calculer une normale : une normale est une dérivée, donc elle a besoin
    des voisins dans la grille. Les deux lectures coexistent parce qu'elles répondent à deux
    questions, pas parce que l'une remplace l'autre.
    """
    from PIL import Image  # noqa: PLC0415

    from zarr_depth import BUCKET, get  # noqa: PLC0415

    Image.MAX_IMAGE_PIXELS = None
    base = (f"{BUCKET}/{fragment}/segments/{wrap['nom']}/mesh/"
            f"{wrap['horodatage']}-on-{volume}-{voxel_um}um.tifxyz")
    canaux = []
    for c in "xyz":
        brut = get(f"{base}/{c}.tif", 300)
        if brut is None:
            return None
        canaux.append(np.asarray(Image.open(io.BytesIO(brut)), dtype=np.float64))
    a = np.stack(canaux, axis=-1)
    ok = np.all(np.isfinite(a), axis=-1) & np.all(a > 0, axis=-1)
    return a, ok


def normales(a: np.ndarray, ok: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """La normale unitaire en chaque cellule, par produit vectoriel des deux tangentes de grille.

    ⚠⚠ Les différences sont **centrées** et une cellule n'est retenue que si ses quatre voisins
    sont valides : une différence prise contre un voisin absent lit la valeur de remplissage du
    format, donc fabrique une tangente qui pointe vers l'origine du volume.

    ⚠ Les normales dégénérées — norme nulle, là où la surface se replie sur elle-même dans la
    grille — sont écartées et **comptées**, pas normalisées de force : diviser par zéro rendrait
    une direction arbitraire qui aurait l'air d'une mesure.
    """
    du = np.zeros_like(a)
    dv = np.zeros_like(a)
    du[1:-1] = a[2:] - a[:-2]
    dv[:, 1:-1] = a[:, 2:] - a[:, :-2]
    n = np.cross(du, dv)
    norme = np.linalg.norm(n, axis=-1)
    voisins = np.zeros_like(ok)
    voisins[1:-1, 1:-1] = (ok[2:, 1:-1] & ok[:-2, 1:-1]
                           & ok[1:-1, 2:] & ok[1:-1, :-2] & ok[1:-1, 1:-1])
    bon = voisins & (norme > 1e-9)
    unite = np.zeros_like(a)
    unite[bon] = n[bon] / norme[bon][:, None]
    return unite, bon


def distance_a(points: np.ndarray, cible: np.ndarray, voxel_um: float) -> np.ndarray:
    """La distance de chaque point à la surface cible, en micromètres."""
    from scipy.spatial import cKDTree  # noqa: PLC0415

    if points.size == 0 or cible.size == 0:
        return np.zeros(0)
    return cKDTree(cible).query(points, k=1)[0] * voxel_um


def essayer_le_pas(depart: np.ndarray, normale: np.ndarray, cible: np.ndarray,
                   pas_vx: float, voxel_um: float) -> dict:
    """Le pas normal dans les DEUX sens, et celui qui s'approche le plus.

    ⚠⚠⚠ Le sens retenu est **rendu**, jamais tu : le signe d'une normale vient du paramétrage de
    la grille, pas de la matière, donc essayer les deux est honnête — mais ne pas dire lequel a
    gagné permettrait de déclarer un succès dans tous les cas.
    """
    sortant = float(np.median(distance_a(depart + normale * pas_vx, cible, voxel_um)))
    rentrant = float(np.median(distance_a(depart - normale * pas_vx, cible, voxel_um)))
    return dict(sens_positif_um=round(sortant, 1), sens_negatif_um=round(rentrant, 1),
                retenu="+" if sortant <= rentrant else "-",
                atteint_um=round(min(sortant, rentrant), 1))


def mesurer(echantillon: int = 4000, graine: int = 42) -> dict:
    """Le pas normal depuis chaque spire vers la suivante, contre le pas NUL."""
    from les_wraps_publies import VOLUME, VOXEL_UM, wraps_du_fragment  # noqa: PLC0415

    if not WRAPS.is_file():
        raise SystemExit("écart entre spires non mesuré : lancer les_wraps_publies d'abord")
    ecart_um = json.loads(WRAPS.read_text())["resume"]["1"]["mediane_um"]
    pas_vx = ecart_um / VOXEL_UM

    rng = np.random.default_rng(graine)
    grilles = {}
    for w in wraps_du_fragment():
        g = grille(w, VOLUME, VOXEL_UM)
        if g is None:
            continue
        a, ok = g
        n, bon = normales(a, ok)
        grilles[w["rang"]] = dict(points=a[ok], depart=a[bon], normale=n[bon],
                                  cellules=int(ok.sum()), avec_normale=int(bon.sum()))

    lignes = []
    for r in sorted(grilles):
        if r + 1 not in grilles:
            continue
        g, cible = grilles[r], grilles[r + 1]["points"]
        m = g["depart"].shape[0]
        if m == 0:
            continue
        k = rng.choice(m, size=min(echantillon, m), replace=False)
        depart, normale = g["depart"][k], g["normale"][k]
        # ⚠⚠ LE PAS NUL EST MESURÉ SUR LES MÊMES POINTS que le pas normal : le comparer à une
        # distance calculée sur toute la spire comparerait deux populations.
        nul = float(np.median(distance_a(depart, cible, VOXEL_UM)))
        essai = essayer_le_pas(depart, normale, cible, pas_vx, VOXEL_UM)
        # ⚠ Et le contrôle du DOUBLE pas : s'il fait aussi bien que le simple, ce n'est pas la
        # distance d'une feuille que le pas franchit, c'est du bruit.
        double = essayer_le_pas(depart, normale, cible, 2.0 * pas_vx, VOXEL_UM)
        lignes.append(dict(de=r, vers=r + 1, points_juges=int(len(k)),
                           cellules=g["cellules"], avec_normale=g["avec_normale"],
                           pas_nul_um=round(nul, 1),
                           pas_simple=essai, pas_double=double,
                           gain_um=round(nul - essai["atteint_um"], 1),
                           rapproche=bool(essai["atteint_um"] < nul)))
    if not lignes:
        raise SystemExit("aucune paire de spires consécutives lisible")

    gains = [e["gain_um"] for e in lignes]
    rapproches = sum(e["rapproche"] for e in lignes)
    return dict(volume=VOLUME, voxel_um=VOXEL_UM,
                ecart_lu_um=ecart_um, pas_en_voxels=round(pas_vx, 2),
                echantillon=echantillon, paires=len(lignes), paires_rapprochees=rapproches,
                gain_median_um=round(float(np.median(gains)), 1),
                pas_nul_median_um=round(float(np.median([e["pas_nul_um"] for e in lignes])), 1),
                pas_simple_median_um=round(
                    float(np.median([e["pas_simple"]["atteint_um"] for e in lignes])), 1),
                pas_double_median_um=round(
                    float(np.median([e["pas_double"]["atteint_um"] for e in lignes])), 1),
                # ⚠⚠⚠ LE VERDICT TIENT À LA MAJORITÉ DES PAIRES, pas à la médiane seule : une
                # médiane qui gagne en cassant la moitié des paires n'est pas une primitive.
                le_pas_normal_atteint_la_spire=bool(rapproches > len(lignes) / 2
                                                    and np.median(gains) > 0),
                lignes=lignes)


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # --- une grille dont la normale est connue : un plan z = 0 ---
    uu, vv = np.meshgrid(np.arange(12.0), np.arange(10.0), indexing="ij")
    plan = np.stack([uu * 3.0 + 100.0, vv * 3.0 + 100.0, np.full(uu.shape, 50.0)], axis=-1)
    ok = np.ones(plan.shape[:2], dtype=bool)
    n, bon = normales(plan, ok)
    v("la normale d'un plan est perpendiculaire au plan",
      bool(np.allclose(np.abs(n[bon]), np.array([0.0, 0.0, 1.0]))), str(n[bon][0]))
    v("... et elle est unitaire", bool(np.allclose(np.linalg.norm(n[bon], axis=-1), 1.0)))
    # ⚠⚠ Le bord n'a pas de différence centrée : il doit être ÉCARTÉ, pas rempli.
    v("le bord de la grille n'a pas de normale",
      not bon[0].any() and not bon[-1].any() and not bon[:, 0].any() and not bon[:, -1].any())
    v("... et l'intérieur en a une", bon[1:-1, 1:-1].all())
    # ⚠⚠⚠ UNE CELLULE DONT UN VOISIN MANQUE DOIT ÊTRE ÉCARTÉE : sans ça la tangente est prise
    # contre la valeur de remplissage et pointe vers l'origine du volume.
    troue = ok.copy()
    troue[5, 5] = False
    v("un voisin absent retire la normale de ses quatre voisins",
      not normales(plan, troue)[1][5, 4] and not normales(plan, troue)[1][4, 5])

    # --- le pas, dans les deux sens, sur des plans dont l'écart est connu ---
    depart = plan[1:-1, 1:-1].reshape(-1, 3)
    nrm = n[bon]
    cible = depart + np.array([0.0, 0.0, 20.0])
    e = essayer_le_pas(depart, nrm, cible, 20.0, 2.0)
    v("le pas d'un écart exact tombe sur la cible", e["atteint_um"] == 0.0, str(e))
    v("... et le sens retenu est rendu", e["retenu"] in "+-", e["retenu"])
    v("... et l'autre sens est deux fois plus loin",
      max(e["sens_positif_um"], e["sens_negatif_um"]) == 80.0, str(e))
    # ⚠⚠ LE CONTRÔLE DU PAS NUL : sans bouger, la distance vaut déjà l'écart. Un pas qui ne fait
    # pas mieux que ne rien faire ne mesure rien.
    nul = float(np.median(distance_a(depart, cible, 2.0)))
    v("le pas nul vaut l'écart, et le pas simple fait mieux",
      nul == 40.0 and e["atteint_um"] < nul, f"{nul} contre {e['atteint_um']}")
    # ⚠ Et le double pas doit dépasser : s'il faisait aussi bien, la distance franchie ne serait
    # pas celle d'une feuille.
    d = essayer_le_pas(depart, nrm, cible, 40.0, 2.0)
    v("... et le double pas dépasse la cible", d["atteint_um"] > e["atteint_um"],
      f"{d['atteint_um']} contre {e['atteint_um']}")
    v("une cible vide ne rend aucune distance",
      distance_a(depart, np.zeros((0, 3)), 2.0).size == 0)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--echantillon", type=int, default=4000)
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(a.echantillon)
    print(f"écart lu : {r['ecart_lu_um']} µm = {r['pas_en_voxels']} voxels\n")
    print(f"{'de':>4} {'vers':>5} {'pas nul':>10} {'pas simple':>12} {'sens':>6} "
          f"{'double':>9} {'gain':>9}")
    print("-" * 60)
    for e in r["lignes"]:
        print(f"{e['de']:>4} {e['vers']:>5} {e['pas_nul_um']:>9.0f}µ "
              f"{e['pas_simple']['atteint_um']:>11.0f}µ {e['pas_simple']['retenu']:>6} "
              f"{e['pas_double']['atteint_um']:>8.0f}µ {e['gain_um']:>+8.0f}µ")
    print(f"\nmédianes : nul {r['pas_nul_median_um']:.0f} µm, simple "
          f"{r['pas_simple_median_um']:.0f} µm, double {r['pas_double_median_um']:.0f} µm")
    print(f"paires rapprochées par le pas : {r['paires_rapprochees']} sur {r['paires']}")
    print(f"\n→ le pas normal atteint la spire suivante : "
          f"{'OUI' if r['le_pas_normal_atteint_la_spire'] else 'NON'}")
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
