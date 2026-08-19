#!/usr/bin/env python3
"""Le champ de normales publié dit-il la même chose que la géométrie de la prédiction ?

⚠⚠ **Ce fichier existe pour ne pas deviner un encodage.** `vc_grow_seg_from_seed` accepte
un `direction_fields` — trois tableaux `x/ y/ z/` — et les rouleaux publient `nx` et `ny`
en **uint8**. Rien ne documente ce que ces octets valent. Se tromper de convention ne
produit aucune erreur : le traceur suit un champ faux, et le résultat ressemble à
« les champs de direction ne servent à rien ».

La vérification n'a besoin d'aucune donnée nouvelle : le **tenseur de structure** que
`trouver_graine.py` calcule déjà sur la prédiction rend la normale locale de la feuille.
Si le champ publié dit la même chose, l'angle entre les deux est petit. Sinon, non.

⚠ **Une normale n'a pas de sens** : (n) et (−n) décrivent la même feuille. On compare donc
des `|cos|`, jamais des cosinus signés — sinon la moitié d'un champ parfaitement correct
compterait comme opposée.

⚠ **Le témoin est le même champ MÉLANGÉ.** Sans lui, un `|cos|` médian de 0,7 ne veut rien
dire : deux directions tirées au hasard dans un plan donnent déjà 0,707 en moyenne, et
0,5 seulement en trois dimensions. C'est le témoin qui fixe le zéro.
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from trouver_graine import scores_du_chunk  # noqa: E402
from zarr_depth import BUCKET, array_meta, chunk_key, decode, get  # noqa: E402


def lire(url: str, level: int, meta: dict, cz: int, cy: int, cx: int, timeout: float):
    dz, dy, dx = meta["chunks"]
    raw = get(f"{url}/{chunk_key(meta, level, cy, cx, cz)}", timeout)
    if raw is None:
        return None
    d = decode(raw, meta, dz * dy * dx)
    if d is None:
        return None
    return np.frombuffer(d, dtype=np.dtype(meta["dtype"])).reshape(dz, dy, dx)


def pave(url: str, level: int, meta: dict, z0: int, y0: int, x0: int,
         forme: tuple, timeout: float, fils: int = 16):
    """Un pavé arbitraire, assemblé depuis les chunks qui le recouvrent.

    ⚠ Les chunks du champ de normales font 32³ quand ceux d'une prédiction en font 192³ :
    un pavé de 192 en demande **216 par composante**. Les lire en série prend des minutes
    pour quelques mégaoctets — c'est de la latence, pas du débit, donc ça se parallélise
    sans rien coordonner (le même argument que `zarr_depth`, mesuré à ×8,35).
    """
    dz, dy, dx = meta["chunks"]
    sz, sy, sx = forme
    out = np.zeros(forme, dtype=np.dtype(meta["dtype"]))
    coords = [(cz, cy, cx)
              for cz in range(z0 // dz, (z0 + sz - 1) // dz + 1)
              for cy in range(y0 // dy, (y0 + sy - 1) // dy + 1)
              for cx in range(x0 // dx, (x0 + sx - 1) // dx + 1)]
    with cf.ThreadPoolExecutor(max_workers=fils) as pool:
        blocs = list(pool.map(lambda c: lire(url, level, meta, *c, timeout), coords))
    for (cz, cy, cx), bloc in zip(coords, blocs):
                if bloc is None:
                    continue
                az, ay, ax = cz * dz, cy * dy, cx * dx
                dz0, dy0, dx0 = max(0, z0 - az), max(0, y0 - ay), max(0, x0 - ax)
                oz, oy, ox = az + dz0 - z0, ay + dy0 - y0, ax + dx0 - x0
                nz_, ny_, nx_ = (min(dz - dz0, sz - oz), min(dy - dy0, sy - oy),
                                 min(dx - dx0, sx - ox))
                if nz_ <= 0 or ny_ <= 0 or nx_ <= 0:
                    continue
                out[oz:oz + nz_, oy:oy + ny_, ox:ox + nx_] = \
                    bloc[dz0:dz0 + nz_, dy0:dy0 + ny_, dx0:dx0 + nx_]
    return out


def main() -> int:
    p = argparse.ArgumentParser(
        description="Comparer le champ de normales publie a la geometrie de la prediction.")
    p.add_argument("prediction", help="cle S3 de la prediction de surface")
    p.add_argument("lasagna", help="prefixe S3 du dossier lasagna")
    p.add_argument("--rouleau", required=True, help="prefixe des fichiers nx/ny")
    p.add_argument("--level", type=int, default=2)
    p.add_argument("--centre", type=int, nargs=3, required=True,
                   metavar=("X", "Y", "Z"), help="point au NIVEAU 0, ordre x y z")
    p.add_argument("--cote", type=int, default=192, help="cote du pave, au niveau demande")
    p.add_argument("--bloc", type=int, default=8)
    p.add_argument("--occupation-min", type=float, default=0.02)
    p.add_argument("--occupation-max", type=float, default=0.80)
    p.add_argument("--centre-encode", type=float, default=128.0,
                   help="valeur uint8 correspondant a zero. ⚠ C'est l'hypothese testee")
    p.add_argument("--balayage-centre", type=float, nargs="*", default=None,
                   help="⚠⚠ LE controle qui tranche : rejouer la comparaison pour "
                        "plusieurs hypotheses d'encodage, sur les MEMES donnees. Le "
                        "temoin melange ne suffit pas -- dans une fenetre de 192 voxels "
                        "les normales pointent deja presque toutes pareil, donc il rend "
                        "0,89 et ne discrimine rien")
    p.add_argument("--timeout", type=float, default=120.0)
    p.add_argument("--out", type=Path, default=None)
    args = p.parse_args()

    facteur = 2 ** args.level
    x0 = args.centre[0] // facteur - args.cote // 2
    y0 = args.centre[1] // facteur - args.cote // 2
    z0 = args.centre[2] // facteur - args.cote // 2
    x0, y0, z0 = max(0, x0), max(0, y0), max(0, z0)
    forme = (args.cote,) * 3

    upred = args.prediction if args.prediction.startswith("http") \
        else f"{BUCKET}/{args.prediction}"
    mpred = array_meta(upred, args.level, args.timeout)
    pred = pave(upred, args.level, mpred, z0, y0, x0, forme, args.timeout)
    if pred.max() == 0:
        print("le pave de prediction est vide", file=sys.stderr)
        return 1

    comps = {}
    for nom in ("nx", "ny"):
        u = f"{BUCKET}/{args.lasagna.rstrip('/')}/{args.rouleau}_{nom}.ome.zarr"
        m = array_meta(u, args.level, args.timeout)
        comps[nom] = pave(u, args.level, m, z0, y0, x0, forme, args.timeout).astype(np.float64)

    s = scores_du_chunk(pred, args.bloc)
    forme_bloc = s["forme"]
    valide = ((s["occupation"] >= args.occupation_min)
              & (s["occupation"] <= args.occupation_max) & (s["trace"] > 0))
    # la normale du tenseur est en (z, y, x)
    nos = s["normale"]
    k = args.bloc
    # moyenne du champ publie sur les memes blocs
    def reduire(a):
        nz_, ny_, nx_ = a.shape
        a = a[: nz_ - nz_ % k, : ny_ - ny_ % k, : nx_ - nx_ % k]
        nz_, ny_, nx_ = a.shape
        return a.reshape(nz_ // k, k, ny_ // k, k, nx_ // k, k).mean(axis=(1, 3, 5)).ravel()

    cx = (reduire(comps["nx"]) - args.centre_encode) / 127.0
    cy = (reduire(comps["ny"]) - args.centre_encode) / 127.0
    norme = np.hypot(cx, cy)
    # ⚠ On compare les composantes (x, y) : le champ publie n'a pas de composante z, et
    # la normale d'une spire est horizontale quand l'axe du rouleau est z.
    nx_nous, ny_nous = nos[:, 2], nos[:, 1]
    n_nous = np.hypot(nx_nous, ny_nous)
    bon = valide & (norme > 1e-3) & (n_nous > 1e-3)
    if not bon.any():
        print("aucun bloc comparable", file=sys.stderr)
        return 1
    cos = np.abs((cx[bon] * nx_nous[bon] + cy[bon] * ny_nous[bon])
                 / (norme[bon] * n_nous[bon]))

    if args.balayage_centre:
        print(f"{bon.sum()} blocs comparables — balayage de l'hypothese d'encodage\n")
        print(f"  {'centre':>8}  {'|cos| median':>13}  {'ecart':>8}")
        lignes = []
        for c in args.balayage_centre:
            ax = (reduire(comps["nx"]) - c) / 127.0
            ay = (reduire(comps["ny"]) - c) / 127.0
            na = np.hypot(ax, ay)
            ok = bon & (na > 1e-3)
            v = np.abs((ax[ok] * nx_nous[ok] + ay[ok] * ny_nous[ok])
                       / (na[ok] * n_nous[ok]))
            med = float(np.median(v))
            deg = float(np.degrees(np.arccos(min(1.0, med))))
            print(f"  {c:>8.0f}  {med:>13.4f}  {deg:>7.1f}°")
            lignes.append({"centre": c, "cos_median": med, "angle_deg": deg})
        meilleur = min(lignes, key=lambda l: l["angle_deg"])
        print(f"\n⭐ meilleur : centre {meilleur['centre']:.0f} a "
              f"{meilleur['angle_deg']:.1f}°")
        if args.out:
            args.out.write_text(json.dumps(
                {"blocs_compares": int(bon.sum()), "balayage": lignes,
                 "meilleur_centre": meilleur["centre"],
                 "meilleur_angle_deg": meilleur["angle_deg"]}, indent=2) + "\n")
            print(f"ecrit : {args.out}")
        return 0

    rng = np.random.default_rng(0)
    perm = rng.permutation(np.flatnonzero(bon))
    cos_temoin = np.abs((cx[perm] * nx_nous[bon] + cy[perm] * ny_nous[bon])
                        / (norme[perm] * n_nous[bon]))

    res = {"blocs_compares": int(bon.sum()),
           "cos_median": float(np.median(cos)),
           "cos_p10": float(np.percentile(cos, 10)),
           "angle_median_deg": float(np.degrees(np.arccos(np.clip(np.median(cos), 0, 1)))),
           "cos_median_temoin": float(np.median(cos_temoin)),
           "norme_publiee_mediane": float(np.median(norme[bon])),
           "centre_encode": args.centre_encode}
    print(f"{res['blocs_compares']} blocs comparables")
    print(f"  |cos| median        {res['cos_median']:.4f}   "
          f"soit {res['angle_median_deg']:.1f}° d'ecart")
    print(f"  |cos| p10           {res['cos_p10']:.4f}")
    print(f"  ⚠ temoin melange    {res['cos_median_temoin']:.4f}")
    print(f"  norme du champ publie (mediane) {res['norme_publiee_mediane']:.3f}")
    if res["cos_median"] <= res["cos_median_temoin"] + 0.05:
        print("  ⚠⚠ le champ publie ne dit RIEN de plus que le hasard avec cet encodage")
    if args.out:
        args.out.write_text(json.dumps(res, indent=2) + "\n")
        print(f"ecrit : {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
