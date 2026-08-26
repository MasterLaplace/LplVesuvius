#!/usr/bin/env python3
"""Le champ de correction d'une trace : de combien, et est-ce RÉPARABLE ?

⚠⚠ **Ce fichier fait passer l'instrument du jugement à la production.** `docs/12`
sait dire qu'une trace est décalée de 63 µm ; ça condamne un segment sans dire quoi
en faire. La question utile est ailleurs, et elle a une réponse mesurable :

> Le décalage est-il **cohérent** d'une fenêtre à l'autre ?

Un décalage cohérent est une **erreur de pose** — la trace suit la bonne feuille, à
côté. On la répare en déplaçant le maillage le long de sa normale, et le champ dit de
combien, fenêtre par fenêtre. Un décalage incohérent est un **saut de feuille** : la
trace change de spire en cours de route, et aucun déplacement rigide ne la rattrape.

⚠ **Les deux se ressemblent parfaitement dans une médiane.** Un segment à ±60 µm de
médiane 63 µm et un segment uniformément à 63 µm rendent le même chiffre. C'est
exactement la distinction que `docs/12` ne pouvait pas faire, et c'est celle qui décide
si on répare ou si on jette.

## Ce qui est mesuré

Trois grandeurs, sur la grille de chunks du volume de surface :

- **`decalage_median`** — le déplacement rigide qui minimise l'écart, en µm.
- **`residuel`** — ce qui reste APRÈS ce déplacement. C'est le vrai coût : un segment
  dont le résiduel est nul est intégralement réparable par une translation.
- **`coherence_voisins`** — la corrélation entre l'écart d'une fenêtre et celui de ses
  voisines de grille. ⚠ Voisin *de grille* veut dire voisin *sur la feuille*, parce
  qu'un volume de surface est déjà paramétré : c'est ce qui rend la mesure licite.

⚠ **Le témoin est un mélange.** Les mêmes écarts, réattribués au hasard à d'autres
fenêtres, doivent effondrer la cohérence. Sans lui, une cohérence élevée peut n'être
qu'un artefact de la façon dont on la calcule — et une vérification incapable
d'échouer ne prouve rien (`HANDOFF` §9.3).
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]
from zarr_depth import BUCKET, array_meta, au_bord, chunk_profile  # noqa: E402


# ⚠ **Une DECLARATION, pas une mesure.** Le rendu d'un volume de surface empile ses
# couches a un voxel d'ecart le long de la normale, et c'est ce que ce depot suppose
# depuis toujours pour convertir un ecart en µm. La constante existe pour que les deux
# vues -- le resume et l'export fenetre par fenetre -- ne puissent pas diverger sur la
# conversion, et pour qu'un rendu fait a un autre pas ait de quoi remettre a l'echelle.
PAS_COUCHE_VOX = 1.0


def mesurer(zarr_url: str, level: int, cote: int, blocs: int, timeout: float,
            threads: int, voxel_um: float) -> tuple[dict, dict]:
    """Une seule campagne de requêtes, deux vues : le résumé et les fenêtres.

    ⚠ Les deux sortent de la **même** grille. Un second échantillonnage rendrait deux
    réponses à une seule question, et rien ne dirait laquelle a été publiée.
    """
    grille, meta, sondees, coins = grille_ecarts(zarr_url, level, cote, blocs, timeout,
                                                 threads)
    resume = _statistiques(grille, 1, meta["chunks"][0], voxel_um, sondees, zarr_url)
    return resume, fenetres(grille, meta, coins, cote, voxel_um, zarr_url, level)


def champ(zarr_url: str, level: int, cote: int, blocs: int, timeout: float,
          threads: int, voxel_um: float) -> dict:
    """Statistiques du champ. La grille brute passe par `grille_ecarts`."""
    return mesurer(zarr_url, level, cote, blocs, timeout, threads, voxel_um)[0]


def grille_ecarts(zarr_url: str, level: int, cote: int, blocs: int, timeout: float,
                  threads: int):
    """Écart pic↔trace sur des BLOCS contigus de fenêtres, répartis sur le segment.

    ⚠⚠ **Des blocs contigus, et non une grille clairsemée**, parce que la grandeur
    cherchée est une cohérence entre VOISINS. Un pas de six chunks sur toute la grille
    donne 4228 requêtes — plusieurs minutes par segment — pour des « voisins » distants
    de 768 voxels, c'est-à-dire pas des voisins. Quelques blocs de côté `cote` coûtent
    cent requêtes et rendent des paires réellement adjacentes. C'est la leçon déjà payée
    sur les fibres (`HANDOFF` §8.22), appliquée d'avance.

    ⚠ Les blocs sont posés **régulièrement**, pas tirés au sort : deux exécutions du même
    segment doivent rendre le même chiffre, sinon la comparaison entre segments mélange
    le tirage et l'objet.
    """
    meta = array_meta(zarr_url, level, timeout)
    depth, hy, hx = meta["chunks"]
    _, rows, cols = meta["shape"]
    grid_y, grid_x = -(-rows // hy), -(-cols // hx)
    traced = depth // 2

    def lire(liste):
        with cf.ThreadPoolExecutor(max_workers=threads) as pool:
            return list(pool.map(
                lambda p: chunk_profile(zarr_url, level, meta, p[0], p[1], timeout),
                liste))

    # ⚠⚠ **Il faut TROUVER la matiere avant de l'echantillonner.** Un volume de surface
    # est majoritairement du remplissage : le segment est une bande tordue dans un
    # canevas rectangulaire. Des blocs poses a intervalles reguliers tombent presque tous
    # dans le vide -- mesure : 6 fenetres utiles sur 96. La passe grossiere ci-dessous
    # coute une centaine de requetes et dit OU regarder ; sans elle la campagne rapporte
    # « pas assez de matiere » sur des segments qui en sont pleins.
    reperage = [(int(y), int(x))
                for y in np.linspace(0, grid_y - 1, 10)
                for x in np.linspace(0, grid_x - 1, 20)]
    reperage = sorted(set(reperage))
    trouves = [pt for pt, got in zip(reperage, lire(reperage)) if not isinstance(got, str)]
    if not trouves:
        raise RuntimeError(f"aucune matiere sur {len(reperage)} fenetres de reperage")

    # Les blocs sont ancres sur des sites TROUVES, repartis regulierement dans la liste
    # -- donc sur le segment, puisque le reperage la parcourt dans l'ordre de la grille.
    pas_ancre = max(1, len(trouves) // blocs)
    coins = [(max(0, y - cote // 2), max(0, x - cote // 2))
             for (y, x) in trouves[::pas_ancre][:blocs]]

    picks = sorted({(min(oy + dy, grid_y - 1), min(ox + dx, grid_x - 1))
                    for (oy, ox) in coins
                    for dy in range(cote)
                    for dx in range(cote)})

    profils = lire(picks)

    grille = np.full((grid_y, grid_x), np.nan, dtype=np.float64)
    for (cy, cx), got in zip(picks, profils):
        if isinstance(got, str):
            continue
        mean, _ = got
        grille[cy, cx] = int(np.argmax(mean)) - traced

    return grille, meta, len(picks) + len(reperage), coins


def fenetres(grille: np.ndarray, meta: dict, coins, cote: int, voxel_um: float,
             zarr_url: str, level: int) -> dict:
    """Le champ **fenêtre par fenêtre**, dans les coordonnées du volume de surface.

    ⚠⚠ **Ce que le résumé ne peut pas livrer.** `champ()` rend une médiane, et une
    médiane ne dit à personne *où* déplacer quoi : c'est exactement le reproche que
    ce fichier adresse à `docs/12`, et il vaut aussi pour sa propre sortie. Un tiers
    qui possède la chaîne maillage → paramétrisation → rendu a besoin de trois
    choses, et il lui en manquait trois.

    | groupe | ce qu'il répond |
    |---|---|
    | `geometrie` | ce qu'un index de fenêtre veut dire : forme, chunks, couche tracée |
    | `fenetres` | où et de combien, une ligne par fenêtre qui porte de la matière |
    | `blocs` | jusqu'où l'adjacence est vraie |

    ⚠⚠ **L'écart sort en index de couche, jamais en « µm le long de +n ».** Une
    normale n'a pas de sens — `valider_champ_normal.py` l'écrit, et le maillage se
    retourne par `--flip-normals` sans que rien ne change —, donc un champ exprimé
    le long de la normale demande à son lecteur une convention que personne n'a
    écrite, et s'en tromper **double** l'erreur au lieu de l'annuler. « La matière
    est à la couche `couche_pic`, la trace est à `couche_tracee` » n'a, elle, aucune
    ambiguïté : c'est le rendu lui-même qui a ordonné ces couches. Les µm voyagent
    à côté, par `PAS_COUCHE_VOX`, pour qui veut une longueur.

    ⚠ **Une fenêtre saturée n'est pas une mesure.** Son pic est à la première ou à la
    dernière couche de la pile, donc le vrai pic peut être **en dehors** — `12` §9 en
    a mesuré 61 % sur Scroll 4, et `20` en tire que le volume ne contient pas ce
    qu'il faudrait atteindre. Le drapeau voyage sur chaque enregistrement plutôt que
    dans une note de bas de page, parce qu'un lecteur qui applique ces écarts-là
    déplace son maillage d'une valeur tronquée sans qu'aucun symptôme n'apparaisse.

    ⚠ **Les blocs sortent, et ce n'est pas de la décoration.** L'adjacence n'existe
    qu'à l'intérieur d'un bloc : deux blocs sont posés loin l'un de l'autre sur le
    segment. Une liste plate se lirait comme une grille continue, et lisser sur de
    tels « voisins » mélangerait des endroits distants de milliers de voxels.
    """
    depth, hy, hx = meta["chunks"]
    _, rows, cols = meta["shape"]
    tracee = depth // 2

    appartenance: dict[tuple[int, int], int] = {}
    listes = []
    for indice, (oy, ox) in enumerate(coins):
        # ⚠ Les cellules sont DEDUPLIQUEES : un bloc pose au bord de la grille voit
        # plusieurs de ses cases se rabattre sur la meme, et les compter deux fois
        # gonflerait `avec_matiere` pour les seuls blocs de bord.
        cellules = sorted({(min(oy + dy, grille.shape[0] - 1),
                            min(ox + dx, grille.shape[1] - 1))
                           for dy in range(cote) for dx in range(cote)})
        for cle in cellules:
            appartenance.setdefault(cle, indice)
        listes.append({
            "bloc": int(indice),
            "fenetre_y": int(oy), "fenetre_x": int(ox),
            "ligne0": int(oy * hy), "colonne0": int(ox * hx),
            "cote_fenetres": int(cote),
            "fenetres": len(cellules),
            "avec_matiere": int(sum(1 for c in cellules if np.isfinite(grille[c]))),
        })

    releves = []
    for cy, cx in zip(*np.nonzero(np.isfinite(grille))):
        cy, cx = int(cy), int(cx)
        ecart = int(grille[cy, cx])
        pic = ecart + tracee
        releves.append({
            "bloc": int(appartenance.get((cy, cx), -1)),
            "fenetre_y": cy,
            "fenetre_x": cx,
            "ligne0": cy * hy, "ligne1": min((cy + 1) * hy, rows),
            "colonne0": cx * hx, "colonne1": min((cx + 1) * hx, cols),
            "couche_pic": pic,
            "ecart_couches": ecart,
            "ecart_um": ecart * PAS_COUCHE_VOX * voxel_um,
            "sature": bool(au_bord(pic, depth)),
        })

    return {
        "zarr": zarr_url.rsplit("/", 1)[-1],
        "niveau": int(level),
        "geometrie": {
            "forme": [int(v) for v in meta["shape"]],
            "chunks": [int(v) for v in meta["chunks"]],
            "grille": [int(grille.shape[0]), int(grille.shape[1])],
            "couche_tracee": int(tracee),
            "voxel_um": float(voxel_um),
            "pas_couche_vox": PAS_COUCHE_VOX,
        },
        "blocs": listes,
        "fenetres": releves,
    }


def _paires_voisines(grille: np.ndarray, pas: int) -> tuple[np.ndarray, np.ndarray]:
    """Couples (fenêtre, voisine) le long des deux axes de la grille.

    ⚠ Une mesure « entre voisins » exige des voisins : la première version de la
    campagne de fibres tirait des fenêtres à vingt chunks d'écart et rendait `NaN` sur
    zéro paire comparée (`HANDOFF` §8.22). Ici le pas de grille EST le pas
    d'échantillonnage, donc deux fenêtres consécutives de la liste sont adjacentes.
    """
    gauche, droite = [], []
    for dy, dx in ((0, pas), (pas, 0)):
        a = grille[: grille.shape[0] - dy, : grille.shape[1] - dx]
        b = grille[dy:, dx:]
        bon = np.isfinite(a) & np.isfinite(b)
        gauche.append(a[bon])
        droite.append(b[bon])
    return np.concatenate(gauche), np.concatenate(droite)


def _correlation(a: np.ndarray, b: np.ndarray) -> float:
    if a.size < 3 or a.std() == 0 or b.std() == 0:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def _statistiques(grille: np.ndarray, pas: int, depth: int, voxel_um: float,
                  sondees: int, zarr_url: str) -> dict:
    valeurs = grille[np.isfinite(grille)]
    if valeurs.size < 8:
        raise RuntimeError(f"seulement {valeurs.size} fenetres avec de la matiere")

    decalage = float(np.median(valeurs))
    residuel = np.abs(valeurs - decalage)

    a, b = _paires_voisines(grille, pas)
    coherence = _correlation(a, b)

    # ⚠⚠ Le temoin : les MEMES ecarts, redistribues au hasard sur la grille. Si la
    # coherence survit a ce melange, elle ne vient pas de la geometrie mais de la
    # facon de compter. Graine fixe : deux executions doivent rendre le meme temoin,
    # sinon on compare l'objet au tirage.
    rng = np.random.default_rng(0)
    melange = grille.copy()
    positions = np.argwhere(np.isfinite(grille))
    permutee = rng.permutation(valeurs)
    for (y, x), v in zip(positions, permutee):
        melange[y, x] = v
    am, bm = _paires_voisines(melange, pas)
    coherence_temoin = _correlation(am, bm)

    return {
        "zarr": zarr_url.rsplit("/", 1)[-1],
        "layers": int(depth),
        "voxel_um": voxel_um,
        "sondees": sondees,
        "avec_matiere": int(valeurs.size),
        "decalage_median_vx": decalage,
        "decalage_median_um": decalage * PAS_COUCHE_VOX * voxel_um,
        "residuel_median_um": float(np.median(residuel)) * PAS_COUCHE_VOX * voxel_um,
        "residuel_p90_um": float(np.percentile(residuel, 90)) * PAS_COUCHE_VOX * voxel_um,
        "part_au_bord": float(np.mean(au_bord(valeurs + depth // 2, depth))),
        "paires_voisines": int(a.size),
        "coherence_voisins": coherence,
        "coherence_temoin_melange": coherence_temoin,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Champ de correction d'une trace : le decalage, et s'il est reparable.",
        epilog="Un residuel nul = une trace reparable par une simple translation.")
    parser.add_argument("zarr", nargs="+", help="cles S3 des .zarr (sans le bucket)")
    parser.add_argument("--level", type=int, default=0)
    parser.add_argument("--cote", type=int, default=4,
                        help="cote d'un bloc, en chunks. Les paires de voisins sortent "
                             "d'ICI : un bloc de cote 1 n'en produit aucune")
    parser.add_argument("--blocs", type=int, default=6,
                        help="nombre de blocs repartis sur le segment")
    parser.add_argument("--voxel-um", type=float, required=True)
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--fils", type=int, default=16)
    parser.add_argument("--out", type=Path, default=None,
                        help="le RESUME : une ligne de statistiques par segment")
    parser.add_argument("--fenetres", type=Path, default=None,
                        help="repertoire ou ecrire le champ FENETRE PAR FENETRE, un "
                             "fichier par segment. C'est la forme utilisable par qui "
                             "possede la chaine maillage -> rendu : le resume ne dit "
                             "pas OU deplacer quoi")
    args = parser.parse_args()

    rapport = []
    for key in args.zarr:
        url = key if key.startswith("http") else f"{BUCKET}/{key}"
        segment = key.split("/segments/")[1].split("/")[0] if "/segments/" in key else key
        try:
            data, vues = mesurer(url, args.level, args.cote, args.blocs, args.timeout,
                                 args.fils, args.voxel_um)
        except RuntimeError as error:
            print(f"{segment} : {error}", file=sys.stderr)
            continue
        data["segment"] = segment
        print(f"{segment[:30]:30} decalage {data['decalage_median_um']:+8.1f} um  "
              f"residuel {data['residuel_median_um']:6.1f} um (p90 {data['residuel_p90_um']:6.1f})  "
              f"coherence {data['coherence_voisins']:+.3f} "
              f"(melange {data['coherence_temoin_melange']:+.3f})  "
              f"{data['avec_matiere']}/{data['sondees']} fen.", flush=True)
        rapport.append(data)

        if args.fenetres:
            args.fenetres.mkdir(parents=True, exist_ok=True)
            vues["segment"] = segment
            cible = args.fenetres / f"{segment}.json"
            cible.write_text(json.dumps(vues, indent=2) + "\n")
            satures = sum(1 for f in vues["fenetres"] if f["sature"])
            print(f"{'':30} champ : {len(vues['fenetres'])} fenetres "
                  f"({satures} saturees, a NE PAS appliquer) -> {cible}", flush=True)

    if args.out:
        args.out.write_text(json.dumps(rapport, indent=2) + "\n")
        print(f"\necrit : {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
