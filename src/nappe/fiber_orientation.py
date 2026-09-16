#!/usr/bin/env python3
"""La direction des fibres change-t-elle avec la profondeur ? (problème ouvert nº 5)

⚠⚠ **Pourquoi c'est du DÉROULEMENT et pas de la lecture.** Une feuille de papyrus est
faite de deux plis collés, fibres **perpendiculaires** l'un a l'autre : le recto est
horizontal, le verso vertical. C'est une propriete **physique** de la feuille, visible
sans encre. Deux consequences :

1. En traversant une feuille, l'orientation dominante doit **basculer d'environ 90°**.
2. Deux feuilles voisines n'ont aucune raison d'avoir le meme sens ; une trace qui
   **saute d'une spire a l'autre** traverse donc une discontinuite d'orientation.

C'est un discriminant que l'encre ne peut pas donner, et il ne demande ni verite
terrain, ni modele, ni juge.

**Le tenseur de structure**, et pourquoi lui. On cherche la direction le long de
laquelle l'image varie le MOINS, parce que c'est celle des fibres. La covariance
des gradients la donne en forme close, A UN QUART DE TOUR PRES :

    J = [[<gx²>, <gx·gy>], [<gx·gy>, <gy²>]]     θ = ½·atan2(2·<gx·gy>, <gx²> − <gy²>)

⚠⚠⚠ CE θ EST CELUI DU PLUS GRAND VECTEUR PROPRE, DONC LA DIRECTION DU GRADIENT :
la perpendiculaire aux fibres, et non les fibres. Mesure : sur un motif dont les
cretes sont choisies a 0, 45, 90 et 135 degres, `orientation_profile` rend
exactement 90 degres de plus (`172`). Les fibres sont a
`langle_publie_est_il_celui_des_fibres.direction_des_fibres_deg(θ)`.

⚠⚠ LA VALEUR RENDUE N'EST PAS CORRIGEE, ET C'EST DELIBERE : les courbes publiees
par les campagnes portent ce θ, et le tourner ici deplacerait 10791 angles deja
publies pour reparer un NOM. Tout ce que les campagnes publient d'AUTRE est un
ECART — desaccord entre voisins, bascule en profondeur, parts au-dela d'un angle —
et un ecart est invariant par un decalage constant, ce que `172` mesure plutot que
de l'affirmer.

⚠ **Une orientation est modulo 180°, pas 360°** : une fibre n'a pas de sens. Moyenner
des angles bruts ferait de 179° et 1° une moyenne de 90°, soit exactement la
perpendiculaire de ce qu'ils sont. Tout se moyenne donc en **angle double**.

⚠ **La coherence est rapportee a cote de l'angle**, et ce n'est pas decoratif : un
angle calcule sur une zone sans texture est un angle **aleatoire mais bien defini**.
Sans la coherence, du bruit se lit comme une direction.

    coherence = sqrt((<gx²> − <gy²>)² + 4·<gx·gy>²) / (<gx²> + <gy²>)   dans [0, 1]

⚠ Exige un volume assez fin pour resoudre les fibres (~10-20 µm) : a 7,91 µm elles font
1 a 2 voxels, a 2,4 µm elles en font 4 a 8, a 1,129 µm une quinzaine. La mesure est
donc faite sur les volumes de surface ESRF, lus **chunk par chunk a distance**
(`zarr_depth.py` explique pourquoi c'est abordable).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

from zarr_depth import BUCKET, array_meta, chunk_key, decode, get  # noqa: E402


def orientation_profile(block: np.ndarray) -> tuple:
    """Angle du GRADIENT dominant (degres, modulo 180) et coherence, couche par couche.

    ⚠⚠⚠ CE N'EST PAS LA DIRECTION DES FIBRES mais sa PERPENDICULAIRE — voir l'en-tete du
    fichier. Le nom historique est garde parce que les campagnes publient cette valeur ;
    la conversion vit dans `langle_publie_est_il_celui_des_fibres`.

    ⚠ L'angle se compte depuis l'axe 2 du bloc vers l'axe 1, parce que `gx` derive sur
    l'axe 2 et `gy` sur l'axe 1.
    """
    patch = block.astype(np.float32)
    gy = patch[:, 2:, 1:-1] - patch[:, :-2, 1:-1]
    gx = patch[:, 1:-1, 2:] - patch[:, 1:-1, :-2]
    jxx = (gx * gx).mean(axis=(1, 2))
    jyy = (gy * gy).mean(axis=(1, 2))
    jxy = (gx * gy).mean(axis=(1, 2))
    angle = 0.5 * np.arctan2(2.0 * jxy, jxx - jyy)
    trace = jxx + jyy
    coherence = np.where(trace > 0,
                         np.sqrt((jxx - jyy) ** 2 + 4.0 * jxy ** 2) / np.maximum(trace, 1e-9),
                         0.0)
    return np.degrees(angle) % 180.0, coherence


def circular_mean(angles: np.ndarray, weights: np.ndarray) -> float:
    """Moyenne d'orientations, en angle DOUBLE — voir l'en-tete."""
    doubled = np.radians(2.0 * angles)
    x = float((weights * np.cos(doubled)).sum())
    y = float((weights * np.sin(doubled)).sum())
    return float(np.degrees(np.arctan2(y, x)) / 2.0) % 180.0


def angular_gap(a: float, b: float) -> float:
    """Ecart entre deux orientations, dans [0, 90] — une fibre n'a pas de sens."""
    gap = abs(a - b) % 180.0
    return min(gap, 180.0 - gap)


def survey(zarr_url: str, level: int, windows: int, timeout: float) -> dict:
    meta = array_meta(zarr_url, level, timeout)
    depth, hy, hx = meta["chunks"]
    _, rows, cols = meta["shape"]
    grid_y, grid_x = -(-rows // hy), -(-cols // hx)
    # ⚠⚠ On echantillonne des AMAS de 2x2 chunks, pas des points isoles. Un desaccord
    # « entre voisins » exige des voisins : des fenetres tirees sur une grille lache sont
    # separees de vingt chunks et ne sont voisines de rien. Premiere version : 0 paire
    # comparee, et la statistique rendait NaN au lieu de signaler qu'elle n'avait rien
    # mesure.
    #
    # Des amas repartis donnent la bonne chose : plusieurs mesures LOCALES de dispersion,
    # a plusieurs endroits du segment.
    clusters = max(2, windows // 4)
    steps = max(1, int(np.sqrt(clusters)))
    picks = []
    for y in np.linspace(0, max(0, grid_y - 2), steps):
        for x in np.linspace(0, max(0, grid_x - 2), min(steps * 2, max(1, grid_x - 1))):
            for dy in (0, 1):
                for dx in (0, 1):
                    picks.append((min(int(y) + dy, grid_y - 1), min(int(x) + dx, grid_x - 1)))
    picks = sorted(set(picks))

    # ⚠⚠ PIVOT MESURE, ET LA RAISON EST DANS LA DONNEE. La bascule recto/verso avec la
    # profondeur ne se voit pas : mesuree sur un volume a 2,4 µm, l'orientation reste a
    # ~90-97° sur les 109 couches, et ne devient erratique que la ou la coherence
    # s'effondre (entre deux feuilles). Ce qui EST exploitable, c'est que l'orientation
    # est une propriete SPATIALE de la feuille : deux fenetres voisines posees sur la
    # meme feuille doivent s'accorder, et une trace qui saute d'une spire a l'autre fait
    # sauter l'orientation.
    #
    # ⚠ La dispersion se mesure entre fenetres VOISINES et non globalement : la courbure
    # du rouleau fait varier l'orientation lentement d'un bout a l'autre d'un segment, et
    # une dispersion globale confondrait cette variation legitime avec un saut.
    flips, coherences, curves, empty = [], [], [], 0
    field = {}
    for cy, cx in picks:
        raw = get(f"{zarr_url}/{chunk_key(meta, level, cy, cx)}", timeout)
        data = decode(raw, meta, depth * hy * hx) if raw is not None else None
        if data is None:
            empty += 1
            continue
        block = np.frombuffer(data, dtype=np.dtype(meta["dtype"])).reshape(depth, hy, hx)
        if block.max() == 0:
            empty += 1
            continue
        angle, coherence = orientation_profile(block)
        # ⚠ Seules les couches assez texturees comptent : ailleurs l'angle est du bruit.
        strong = coherence > 0.15
        if strong.sum() < depth // 4:
            continue
        half = depth // 2
        top = strong[:half]
        bottom = strong[half:]
        if top.sum() < 4 or bottom.sum() < 4:
            continue
        a_top = circular_mean(angle[:half][top], coherence[:half][top])
        a_bottom = circular_mean(angle[half:][bottom], coherence[half:][bottom])
        flips.append(angular_gap(a_top, a_bottom))
        coherences.append(float(coherence[strong].mean()))
        curves.append((angle, coherence))
        # L'orientation de la fenetre : moyenne ponderee par la coherence sur les
        # couches texturees. C'est « dans quel sens vont les fibres ICI ».
        field[(cy, cx)] = (circular_mean(angle[strong], coherence[strong]),
                           float(coherence[strong].mean()))

    if not flips:
        raise RuntimeError("aucune fenetre assez texturee pour une orientation")
    # Ecarts entre fenetres adjacentes dans la grille de chunks.
    ordered = sorted(field)
    gaps = []
    for (ay, ax) in ordered:
        for (by, bx) in ordered:
            if (by, bx) <= (ay, ax):
                continue
            near_y = abs(by - ay) <= 1
            near_x = abs(bx - ax) <= 1
            if near_y and near_x:
                gaps.append(angular_gap(field[(ay, ax)][0], field[(by, bx)][0]))
    flips = np.asarray(flips)
    return {
        "voisins_compares": len(gaps),
        "desaccord_voisins_median_deg": float(np.median(gaps)) if gaps else float("nan"),
        "part_voisins_sup_30": float((np.asarray(gaps) > 30.0).mean()) if gaps else float("nan"),
        "zarr": zarr_url.rsplit("/", 1)[-1], "layers": int(depth),
        "sondees": len(picks), "utilisables": int(flips.size), "vides": empty,
        "coherence_mediane": float(np.median(coherences)),
        "bascule_mediane_deg": float(np.median(flips)),
        "part_bascule_sup_45": float((flips > 45.0).mean()),
        # ⚠ La courbe d'une SEULE fenetre, la plus coherente : moyenner des orientations
        # de fenetres differentes melangerait des feuilles differentes, et la bascule
        # qu'on cherche disparaitrait dans la moyenne.
        "courbe": [[float(a), float(c)] for a, c in
                   zip(*curves[int(np.argmax(coherences))])] if curves else [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Orientation des fibres en fonction de la profondeur.",
        epilog="Une orientation est modulo 180 : tout se moyenne en angle double.",
    )
    parser.add_argument("zarr", nargs="+")
    parser.add_argument("--level", type=int, default=0)
    parser.add_argument("--windows", type=int, default=16)
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--courbe", action="store_true")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    report = []
    for key in args.zarr:
        url = key if key.startswith("http") else f"{BUCKET}/{key}"
        try:
            data = survey(url, args.level, args.windows, args.timeout)
        except RuntimeError as error:
            print(f"{key[:60]} : {error}", file=sys.stderr)
            continue
        segment = key.split("/segments/")[1].split("/")[0] if "/segments/" in key else key
        data["segment"] = segment
        print(f"{segment[:30]:30} coh {data['coherence_mediane']:.3f}  "
              f"bascule {data['bascule_mediane_deg']:5.1f}°  "
              f"⭐ desaccord voisins {data['desaccord_voisins_median_deg']:5.1f}° "
              f"(> 30° : {data['part_voisins_sup_30'] * 100:3.0f} %, "
              f"{data['voisins_compares']} paires)  "
              f"[{data['utilisables']}/{data['sondees']}]", flush=True)
        if args.courbe and data["courbe"]:
            print(f"    {'couche':>6} {'angle':>7} {'coherence':>10}")
            c = data["courbe"]
            for k in range(0, len(c), max(1, len(c) // 20)):
                bar = "#" * int(c[k][1] * 60)
                print(f"    {k:>6} {c[k][0]:>7.1f} {c[k][1]:>10.3f}  {bar}")
        report.append(data)

    if args.out:
        args.out.write_text(json.dumps(report, indent=2) + "\n")
        print(f"\necrit : {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
