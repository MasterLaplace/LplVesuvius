#!/usr/bin/env python3
"""Trouver un point de départ pour `vc_grow_seg_from_seed`, à distance.

Le traceur part d'**une** coordonnée posée sur une prédiction de surface. Dans VC3D on la
pose à la souris ; ici on la cherche dans le zarr publié, sans rien télécharger.

⚠⚠ **L'ordre des axes est le piège de ce fichier, et il échoue en silence.** Le zarr est
indexé `(z, y, x)` — son `.zattrs` le dit — alors que `vc_grow_seg_from_seed -s` attend
**`x y z`**. Inverser ne produit aucune erreur : ça pose la graine ailleurs dans le
rouleau, et le traceur part sur ce qu'il trouve là. La conversion est donc faite **une
fois**, ici, et la sortie est écrite dans l'ordre de l'outil.

## Deux critères, et pourquoi le premier ne suffit pas

**`voisinage`** — la moyenne d'un cube autour du point. Il répond à « y a-t-il beaucoup de
surface ici ». C'est ce qui a choisi la graine de `docs/24`.

⚠⚠ **Et il a rendu 255 pour les huit candidats.** La prédiction est **seuillée** (`th0.2`)
donc binaire : tout bloc entièrement dans la matière prédite atteint le plafond du format,
et huit candidats à égalité ne sont pas un classement — c'est un tirage au sort déguisé en
mesure. C'est le piège nº 2 du dépôt (*une valeur identique partout = saturation contre sa
propre borne*), et rien ne le signalait.

**`planarite`** — l'anisotropie du **tenseur de structure 3D**, la grandeur que la
saturation ne touche pas :

    J = <∇f ∇fᵀ>       λ₁ ≥ λ₂ ≥ λ₃       planarité = (λ₁ − λ₂) / λ₁

Le raisonnement est physique, pas statistique. Dans un bloc traversé par **une** feuille,
tous les gradients pointent le long de sa normale : une seule direction, donc λ₁ ≫ λ₂ et
la planéité vaut ~1. Deux feuilles **parallèles** ne changent rien — les normales sont
encore alignées, et c'est voulu : un empilement régulier est exactement l'endroit où l'on
veut poser une graine. Ce qui fait tomber la planéité, c'est une **jonction** : deux
nappes qui se rejoignent en biais peuplent deux directions, λ₂ monte, et le score
s'effondre. Or une jonction est précisément l'endroit où le traceur peut passer d'une
spire à l'autre sans que rien dans la prédiction ne l'en empêche.

⚠⚠ **Et un `argmax` sur les blocs d'un chunk sature à son tour** — payé ici, une passe
après avoir écrit le paragraphe ci-dessus. Un chunk de 192³ contient 13 824 blocs de côté
8 ; le maximum d'un score borné par 1 sur autant de tirages vaut ~1 quel que soit le
terrain, donc **quatre candidats sortaient à 1,0000 exactement**. C'est le même défaut que
la saturation du voisinage, à un étage de plus : *le maximum d'un échantillon nombreux ne
décrit pas l'échantillon*.

Le score classé est donc la **moyenne de la planéité sur le voisinage 3³ du bloc**, limitée
aux blocs qui passent la barrière, et les égalités sont tranchées par le **nombre de
voisins valides** : une graine au milieu d'un empilement propre et étendu vaut mieux qu'une
graine sur le bord d'un éclat isolé qui, lui, est planaire par accident. Chaque chunk
rapporte en plus sa **part planaire**, qui est une propriété de la *région* et ne peut pas
être fabriquée par un maximum.

⚠ **La planéité n'est définie que là où il y a du gradient.** Un bloc uniforme — tout vide
ou tout plein — a un tenseur nul, et ses valeurs propres sont alors du bruit numérique
ordonné, c'est-à-dire un score parfaitement défini et parfaitement dénué de sens. D'où la
double barrière : une **occupation** dans une bande, et un plancher sur la trace de J.

⚠⚠ **La planéité est biaisée vers les feuilles alignées sur la grille**, et c'est
mesuré, pas supposé : une prédiction seuillée est binaire, donc un plan incliné y est un
**escalier**, et les marches peuplent une seconde direction de gradient. Sur un plan
synthétique tourné de 0° à 90°, la planéité brute descend de 1,000 à **0,828** (écart
0,172). Un lissage 3³ avant les gradients ramène l'écart à **0,053** sur un bloc 16³ — et
le biais résiduel reste très en dessous du signal, puisqu'une **jonction** à 90° rend
**0,000**. C'est pour ça que `--lissage` vaut 1 par défaut et non 0.

⚠ **La graine rendue est un voxel ALLUMÉ**, pas le centre du bloc. Le centre géométrique
d'un bloc traversé par une feuille en diagonale tombe dans le vide, et le traceur part
alors de rien. L'ancienne version rendait le centre ; elle a marché par chance, sur un
bloc saturé.
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from zarr_depth import BUCKET, array_meta, chunk_key, decode, get  # noqa: E402


def lire_chunk(url: str, level: int, meta: dict, cz: int, cy: int, cx: int,
               timeout: float):
    dz, dy, dx = meta["chunks"]
    raw = get(f"{url}/{chunk_key(meta, level, cy, cx, cz)}", timeout)
    if raw is None:
        return None
    data = decode(raw, meta, dz * dy * dx)
    if data is None:
        return None
    return np.frombuffer(data, dtype=np.dtype(meta["dtype"])).reshape(dz, dy, dx)


def lire_bloc(url: str, level: int, meta: dict, z: float, y: float, x: float,
              rayon: int, timeout: float, parallele: int = 8):
    """Lire un CUBE de cote 2*rayon+1 autour de (z, y, x), en assemblant les chunks.

    ⚠ `lire_chunk` rend un chunk entier et le point demande tombe rarement en son centre :
    une marche partie du bord sortirait du bloc au troisieme pas et l'arret se lirait comme
    « la nappe finit ici ». Ce lecteur recouvre donc le cube VOULU, quitte a tirer quatre
    chunks, et rend aussi le coin du bloc dans le volume pour que les points ecrits soient
    absolus.

    ⚠ Les chunks absents (hors volume, ou jamais ecrits) sont laisses a ZERO et comptes.
    Un trou silencieux ferait croire a une fin de nappe la ou il n'y a qu'une lacune de
    stockage -- deux faits que la marche doit pouvoir distinguer.

    Retourne (bloc, origine (z0, y0, x0), nombre de chunks manquants).
    """
    import concurrent.futures as cf

    nz, ny, nx = meta["shape"]
    dz, dy, dx = meta["chunks"]
    z0 = max(0, int(z) - rayon); y0 = max(0, int(y) - rayon); x0 = max(0, int(x) - rayon)
    z1 = min(nz, int(z) + rayon + 1); y1 = min(ny, int(y) + rayon + 1)
    x1 = min(nx, int(x) + rayon + 1)
    if z1 <= z0 or y1 <= y0 or x1 <= x0:
        return None, (0, 0, 0), 0

    bloc = np.zeros((z1 - z0, y1 - y0, x1 - x0), dtype=np.dtype(meta["dtype"]))
    taches = [(cz, cy, cx)
              for cz in range(z0 // dz, (z1 - 1) // dz + 1)
              for cy in range(y0 // dy, (y1 - 1) // dy + 1)
              for cx in range(x0 // dx, (x1 - 1) // dx + 1)]
    manquants = 0
    with cf.ThreadPoolExecutor(max_workers=parallele) as ex:
        for (cz, cy, cx), data in zip(
                taches, ex.map(lambda t: lire_chunk(url, level, meta, *t, timeout), taches)):
            if data is None:
                manquants += 1
                continue
            az, ay, ax = cz * dz, cy * dy, cx * dx
            sz0, sy0, sx0 = max(z0, az), max(y0, ay), max(x0, ax)
            sz1 = min(z1, az + dz); sy1 = min(y1, ay + dy); sx1 = min(x1, ax + dx)
            bloc[sz0 - z0:sz1 - z0, sy0 - y0:sy1 - y0, sx0 - x0:sx1 - x0] = \
                data[sz0 - az:sz1 - az, sy0 - ay:sy1 - ay, sx0 - ax:sx1 - ax]
    return bloc, (z0, y0, x0), manquants


def _reduire(a: np.ndarray, k: int) -> np.ndarray:
    """Moyenne par blocs cubiques de côté k. Le reste non divisible est écarté."""
    nz, ny, nx = a.shape
    a = a[: nz - nz % k, : ny - ny % k, : nx - nx % k]
    nz, ny, nx = a.shape
    return a.reshape(nz // k, k, ny // k, k, nx // k, k).mean(axis=(1, 3, 5))


def _lisser(f: np.ndarray, r: int) -> np.ndarray:
    """Moyenne de boîte séparable, de rayon r, à bords répliqués.

    ⚠ Répliquer plutôt qu'enrouler : `np.roll` ramènerait la face opposée du chunk contre
    son bord, donc les blocs du bord seraient jugés sur de la matière située à deux
    millimètres de là.
    """
    if r <= 0:
        return f
    for axe in range(3):
        pad = [(0, 0)] * 3
        pad[axe] = (r, r)
        g = np.pad(f, pad, mode="edge")
        acc = np.zeros_like(f)
        for d in range(2 * r + 1):
            sl = [slice(None)] * 3
            sl[axe] = slice(d, d + f.shape[axe])
            acc += g[tuple(sl)]
        f = acc / (2 * r + 1)
    return f


def _gradients(f: np.ndarray) -> tuple:
    """Différences centrées, bords mis à zéro pour garder la forme du bloc.

    ⚠ Garder la forme est ce qui permet de réduire gradients et occupation par la MÊME
    découpe : un décalage d'un voxel entre les deux ferait juger un bloc sur l'occupation
    de son voisin.
    """
    g = []
    for axe in range(3):
        d = np.zeros_like(f)
        avant = [slice(None)] * 3
        apres = [slice(None)] * 3
        cible = [slice(None)] * 3
        avant[axe] = slice(2, None)
        apres[axe] = slice(0, -2)
        cible[axe] = slice(1, -1)
        d[tuple(cible)] = 0.5 * (f[tuple(avant)] - f[tuple(apres)])
        g.append(d)
    return tuple(g)


def _agreger_voisins(valeur: np.ndarray, valide: np.ndarray) -> tuple:
    """Somme et compte sur le voisinage 3³ de blocs, en ne comptant que les valides.

    ⚠ Remplissage à zéro et non enroulement : un bloc de bord doit voir moins de voisins,
    pas les voisins de l'autre face.
    """
    somme = np.zeros(valeur.shape, dtype=np.float64)
    compte = np.zeros(valeur.shape, dtype=np.int32)
    v = (valeur * valide).astype(np.float64)
    m = valide.astype(np.int32)
    for dz in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                pad = [(max(dz, 0), max(-dz, 0)), (max(dy, 0), max(-dy, 0)),
                       (max(dx, 0), max(-dx, 0))]
                sl = tuple(slice(max(-d, 0), max(-d, 0) + n)
                           for d, n in zip((dz, dy, dx), valeur.shape))
                somme += np.pad(v, pad)[sl]
                compte += np.pad(m, pad)[sl]
    return somme, compte


def scores_du_chunk(bloc: np.ndarray, k: int, lissage: int = 1) -> dict | None:
    """Rend, pour chaque bloc de côté k, l'occupation, le voisinage et la planéité.

    ⚠ L'occupation et le voisinage se mesurent sur la donnée BRUTE, la planéité sur la
    donnée lissée. Lisser l'occupation en ferait une grandeur floue qui ne répond plus à
    « ce bloc contient-il de la matière », qui est la question à laquelle elle sert de
    barrière.
    """
    brut = bloc.astype(np.float32)
    occupation = _reduire((brut > 0).astype(np.float32), k)
    voisinage = _reduire(brut, k)
    f = _lisser(brut, lissage)

    gz, gy, gx = _gradients(f)
    # Les six composantes indépendantes de J, réduites une par une pour ne jamais tenir
    # six volumes complets en mémoire en même temps.
    composantes = []
    for a, b in ((gz, gz), (gy, gy), (gx, gx), (gz, gy), (gz, gx), (gy, gx)):
        composantes.append(_reduire(a * b, k))
    jzz, jyy, jxx, jzy, jzx, jyx = composantes

    forme = jzz.shape
    n = int(np.prod(forme))
    J = np.empty((n, 3, 3), dtype=np.float32)
    J[:, 0, 0] = jzz.ravel()
    J[:, 1, 1] = jyy.ravel()
    J[:, 2, 2] = jxx.ravel()
    J[:, 0, 1] = J[:, 1, 0] = jzy.ravel()
    J[:, 0, 2] = J[:, 2, 0] = jzx.ravel()
    J[:, 1, 2] = J[:, 2, 1] = jyx.ravel()

    vals, vecs = np.linalg.eigh(J)          # croissantes
    lam1 = vals[:, 2]
    lam2 = vals[:, 1]
    trace = vals.sum(axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        planarite = np.where(lam1 > 0, (lam1 - lam2) / np.maximum(lam1, 1e-12), 0.0)
    normale = vecs[:, :, 2]                 # vecteur propre de lambda1, en (z, y, x)

    return {"occupation": occupation.ravel(), "voisinage": voisinage.ravel(),
            "planarite": planarite.astype(np.float32), "trace": trace.astype(np.float32),
            "normale": normale.astype(np.float32), "forme": forme}


def classement(s: dict, occupation_min: float, occupation_max: float,
               voisins_min: int, seuil_planaire: float) -> dict:
    """Le score de tri : planéité MOYENNÉE sur le voisinage 3³ de blocs.

    Rend aussi `part_planaire`, la fraction des blocs valides du chunk au-dessus du seuil.
    ⚠ Celle-là décrit la région et non son meilleur point : c'est la seule des trois qu'un
    maximum ne peut pas fabriquer.
    """
    valide = ((s["occupation"] >= occupation_min) & (s["occupation"] <= occupation_max)
              & (s["trace"] > 0))
    forme = s["forme"]
    somme, compte = _agreger_voisins(s["planarite"].reshape(forme),
                                     valide.reshape(forme))
    somme, compte = somme.ravel(), compte.ravel()
    with np.errstate(invalid="ignore", divide="ignore"):
        moyenne = np.where(compte > 0, somme / np.maximum(compte, 1), 0.0)
    retenu = valide & (compte >= voisins_min)
    part = (float((valide & (s["planarite"] >= seuil_planaire)).sum())
            / max(1, int(valide.sum())))
    return {"score": moyenne, "voisins": compte, "retenu": retenu,
            "valides": int(valide.sum()), "part_planaire": part}


def voxel_allume(bloc: np.ndarray, k: int, iz: int, iy: int, ix: int) -> tuple | None:
    """Le voxel allumé le plus proche du centre du bloc (iz, iy, ix).

    ⚠ Rendre le centre géométrique du bloc pose la graine dans le vide dès que la feuille
    le traverse en biais. Le traceur ne s'en plaint pas : il part de ce qu'il trouve là.
    """
    sous = bloc[iz * k:(iz + 1) * k, iy * k:(iy + 1) * k, ix * k:(ix + 1) * k]
    allumes = np.argwhere(sous > 0)
    if allumes.size == 0:
        return None
    centre = np.array([k / 2.0 - 0.5] * 3)
    d = ((allumes - centre) ** 2).sum(axis=1)
    z, y, x = allumes[int(np.argmin(d))]
    return int(iz * k + z), int(iy * k + y), int(ix * k + x)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Chercher une graine sur une prediction de surface publiee.",
        epilog="La sortie est dans l'ordre x y z, celui de vc_grow_seg_from_seed.")
    parser.add_argument("zarr", help="cle S3 de la prediction de surface")
    parser.add_argument("--level", type=int, default=2,
                        help="niveau de recherche. ⚠ Les coordonnees sont converties au "
                             "NIVEAU 0, seul repere que le traceur comprend")
    parser.add_argument("--critere", choices=("planarite", "voisinage"),
                        default="planarite",
                        help="cle de tri. 'voisinage' est celui de docs/24 : il SATURE "
                             "sur une prediction seuillee et ne classe donc rien")
    parser.add_argument("--z-fraction", type=float, default=0.5,
                        help="hauteur relative ou chercher (0 = bas, 1 = haut)")
    parser.add_argument("--chunks", type=int, default=24, help="chunks sondes")
    parser.add_argument("--candidats", type=int, default=8)
    parser.add_argument("--bloc", type=int, default=8,
                        help="cote du cube, en voxels du niveau demande. Trop petit, le "
                             "tenseur est du bruit ; trop grand, la courbure de la spire "
                             "le remplit de deux orientations")
    parser.add_argument("--lissage", type=int, default=1,
                        help="rayon du lissage avant les gradients. ⚠ 0 rend le critere "
                             "sensible a l'orientation de la feuille dans la grille "
                             "(ecart mesure 0,172 contre 0,053 a rayon 1)")
    parser.add_argument("--voisins-min", type=int, default=6,
                        help="voisins valides exiges sur les 26+1. ⚠ En dessous, la "
                             "moyenne porte sur un eclat isole")
    parser.add_argument("--seuil-planaire", type=float, default=0.90,
                        help="seuil de la « part planaire » du chunk, qui decrit la "
                             "REGION et non son meilleur point")
    parser.add_argument("--occupation-min", type=float, default=0.02,
                        help="⚠ sous ce taux le bloc est du vide : son tenseur est nul et "
                             "ses valeurs propres sont du bruit ordonne")
    parser.add_argument("--occupation-max", type=float, default=0.80,
                        help="⚠ au-dessus le bloc est PLEIN : gradient nul, meme piege")
    parser.add_argument("--voxel-um", type=float, default=None,
                        help="taille du voxel au niveau 0, pour rapporter le bloc en µm")
    parser.add_argument("--fils", type=int, default=12)
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    url = args.zarr if args.zarr.startswith("http") else f"{BUCKET}/{args.zarr}"
    meta = array_meta(url, args.level, args.timeout)
    dz, dy, dx = meta["chunks"]
    nz, ny, nx = meta["shape"]
    facteur = 2 ** args.level
    k = args.bloc

    gz, gy, gx = -(-nz // dz), -(-ny // dy), -(-nx // dx)
    cz = min(gz - 1, max(0, int(round(args.z_fraction * (gz - 1)))))

    # Balayage REGULIER du plan de chunks a cette hauteur : deux executions doivent rendre
    # la meme graine, sinon on ne peut pas reprendre un trace la ou on l'a laisse.
    par_axe = max(1, int(np.sqrt(args.chunks)))
    points = sorted({(int(y), int(x))
                     for y in np.linspace(0, gy - 1, par_axe)
                     for x in np.linspace(0, gx - 1, par_axe)})

    bloc_um = (f" = {k * facteur * args.voxel_um:.0f} µm"
               if args.voxel_um else "")
    print(f"niveau {args.level} · grille {gz}x{gy}x{gx} chunks de {dz}x{dy}x{dx} · "
          f"plan z={cz} · {len(points)} chunks sondes · bloc {k}³{bloc_um} · "
          f"lissage r={args.lissage} · tri sur « {args.critere} »")

    with cf.ThreadPoolExecutor(max_workers=args.fils) as pool:
        blocs = list(pool.map(
            lambda p: lire_chunk(url, args.level, meta, cz, p[0], p[1], args.timeout),
            points))

    candidats = []
    vides = 0
    rejetes_occupation = 0
    for (cy, cx), bloc in zip(points, blocs):
        if bloc is None or bloc.max() == 0:
            vides += 1
            continue
        s = scores_du_chunk(bloc, k, args.lissage)
        if s is None:
            vides += 1
            continue
        cl = classement(s, args.occupation_min, args.occupation_max,
                        args.voisins_min, args.seuil_planaire)
        if not cl["retenu"].any():
            rejetes_occupation += 1
            continue
        if args.critere == "voisinage":
            cle = s["voisinage"].astype(np.float64).copy()
        else:
            # ⚠ Tri lexicographique : la planéité de voisinage d'abord, le NOMBRE de
            # voisins valides pour trancher les ex aequo. Sans le second, un éclat isolé
            # planaire par accident bat un empilement propre et étendu.
            cle = cl["score"] + 1e-6 * cl["voisins"]
        cle = np.where(cl["retenu"], cle, -np.inf)
        idx = int(np.argmax(cle))
        iz, iy, ix = np.unravel_index(idx, s["forme"])
        pose = voxel_allume(bloc, k, int(iz), int(iy), int(ix))
        if pose is None:
            rejetes_occupation += 1
            continue
        lz, ly, lx = pose
        z = (cz * dz + lz) * facteur
        y = (cy * dy + ly) * facteur
        x = (cx * dx + lx) * facteur
        nz_, ny_, nx_ = (float(v) for v in s["normale"][idx])
        candidats.append({
            "planarite": round(float(cl["score"][idx]), 4),
            "planarite_bloc": round(float(s["planarite"][idx]), 4),
            "voisins": int(cl["voisins"][idx]),
            "part_planaire": round(cl["part_planaire"], 4),
            "blocs_valides": cl["valides"],
            "voisinage": round(float(s["voisinage"][idx]), 1),
            "occupation": round(float(s["occupation"][idx]), 4),
            "valeur": int(bloc[lz, ly, lx]),
            "normale_zyx": [round(nz_, 4), round(ny_, 4), round(nx_, 4)],
            "x": int(x), "y": int(y), "z": int(z)})

    if not candidats:
        print(f"aucun bloc exploitable ({vides} chunks vides, "
              f"{rejetes_occupation} sans bloc dans la bande d'occupation) "
              f"sur {len(points)}", file=sys.stderr)
        return 1

    candidats.sort(key=lambda c: -c[args.critere])
    candidats = candidats[: args.candidats]
    print(f"{vides} chunks vides · {rejetes_occupation} sans bloc utile · "
          f"{len(candidats)} candidats\n")
    print(f"{'planar.3³':>9} {'vois':>5} {'part':>6} {'voisinage':>9} {'occup.':>7} "
          f"{'val':>4}  {'-s x y z (niveau 0)':<28}")
    for c in candidats:
        print(f"{c['planarite']:>9.4f} {c['voisins']:>5} {c['part_planaire']:>6.3f} "
              f"{c['voisinage']:>9.1f} {c['occupation']:>7.3f} "
              f"{c['valeur']:>4}  {c['x']} {c['y']} {c['z']}")

    # ⚠ Un classement dont tous les candidats sont a egalite n'est pas un classement.
    # C'est ce qui s'est produit dans docs/24 et rien ne l'a dit.
    cles = [c[args.critere] for c in candidats]
    if len(cles) > 1 and max(cles) - min(cles) < 1e-6:
        print(f"\n⚠⚠ les {len(cles)} candidats ont le MEME score « {args.critere} » "
              f"({cles[0]}) : ce critere ne classe rien ici, la graine retenue est un "
              f"tirage au sort. Voir l'en-tete de ce fichier.")
    print(f"\n⚠ ordre x y z, celui de vc_grow_seg_from_seed — le zarr, lui, est (z,y,x)")

    if args.out:
        args.out.write_text(json.dumps(
            {"zarr": args.zarr, "level": args.level, "critere": args.critere,
             "bloc": k, "lissage": args.lissage,
             "voisins_min": args.voisins_min, "seuil_planaire": args.seuil_planaire,
             "occupation_min": args.occupation_min,
             "occupation_max": args.occupation_max,
             "shape_zyx": list(meta["shape"]), "candidats": candidats}, indent=2) + "\n")
        print(f"ecrit : {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
