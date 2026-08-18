#!/usr/bin/env python3
"""Un site suspect fait-il UN millimetre de haut, ou DERIVE-t-il sur plusieurs ?

C'est la question laissee ouverte par `docs/11` §10, et elle n'est pas academique :
les deux lectures decrivent des objets differents. Un defaut d'un millimetre est une
irregularite locale ; un defaut qui monte en derivant est une **soudure portee par une
feuille**, donc exactement ce qui fait sauter une spire au deroulement.

Ce que la mesure precedente a etabli, et ou elle s'arrete :

    distance en z | 0,8 mm | 1,6 mm | 2,4 mm | 3,2-6,3 mm
    coincidences  |  9,3 % |  0,0 % |  0,0 % |     3,5 %

Tout le signal est entre coupes ADJACENTES. Lu naivement : « les defauts font un
millimetre ». Mais §8 a mesure que le site MIGRE — **+2,4 mm de rayon sur 2,4 mm de
hauteur**. Un objet qui derive d'un millimetre de rayon par millimetre de hauteur
**sort de la fenetre d'appariement au bout d'une seule coupe**, par construction : la
fenetre fait justement 1 mm. L'absence de coincidence lointaine est donc ce que les
deux lectures predisent, et elle ne peut pas les departager.

⚠⚠ **CE QUI CHANGE ICI, ET C'EST LA SEULE CHOSE QUI CHANGE : le centre de la fenetre.**
La tolerance reste celle de la mesure publiee — **1,0 mm en rayon, 1000 colonnes en
angle** — mais elle est posee autour d'une position **predite** au lieu de la derniere
position vue. Aucun bouton n'est elargi. Une piste dont la vitesse est nulle retombe
donc **exactement** sur l'appariement a fenetre fixe : tout gain est attribuable a la
prediction, et a rien d'autre. Elargir la tolerance aurait rendu la comparaison
ininterpretable — on aurait mesure la permissivite de l'outil.

Trois bras, et il en faut trois :

1. **predictif sur les donnees** — ce qu'on veut mesurer ;
2. **fenetre fixe sur les donnees** (vitesse forcee a zero) — sans lui, une piste
   longue prouverait seulement qu'un suiveur suit, pas que la prediction sert ;
3. **predictif sur du hasard** — sans lui, un suiveur permissif enchaine du bruit et
   rend des pistes magnifiques. Le hasard par defaut est une **permutation** : le
   multiensemble exact des cellules est conserve et seule leur repartition entre
   coupes est detruite, donc l'hypothese nulle est precisement « l'ordre en z ne veut
   rien dire ». Un tirage uniforme est aussi disponible, mais il est plus faible : il
   detruit en meme temps la distribution radiale, donc il repond a deux questions a
   la fois.

⚠ **La rectitude est la grandeur qui tranche, pas la longueur.** Un suiveur qui
autorise une derive enchainera des points au hasard, et ces chaines **zigzaguent** :
leur deplacement net est petit devant le chemin parcouru. Un defaut porte par une
feuille va dans **un** sens. On rapporte donc `|r_fin - r_debut| / somme|dr|`, qui vaut
1 pour une piste monotone et tend vers zero pour une marche aleatoire.

⚠ Aucun saut de coupe n'est autorise : une piste se rompt des qu'une coupe ne fournit
pas de successeur. C'est le choix conservateur — tolerer les trous rendrait le suiveur
plus permissif, donc gonflerait aussi le bras nul.

⚠ L'appariement est glouton mais **ordonne globalement par erreur de prediction**, pas
par ordre de piste : sinon la premiere piste creee servirait la premiere et le
resultat dependrait d'un ordre arbitraire.

Lit les JSON produits par `fusion_scan.py`. Ne demande ni volume ni relecture du CT.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

VOXEL_UM = 7.91  # niveau 0 ; le champ `slice` des JSON est deja en voxels niveau 0


def load_slices(path: Path) -> list[dict]:
    """Coupes d'un JSON de `fusion_scan`, triees par z croissant."""
    data = json.loads(path.read_text())
    slices = [{"z": int(s["slice"]),
               "cells": [(float(c["radius_mm"]), float(c["column"])) for c in s["anomalous"]]}
              for s in data["slices"]]
    return sorted(slices, key=lambda s: s["z"])


def track(slices: list[dict], radial_mm: float, angular: float,
          predictive: bool) -> list[list[tuple]]:
    """Chaine les cellules de coupe en coupe. Rend des pistes [(z, r, col), ...].

    `predictive=False` force la vitesse a zero : la fenetre est alors centree sur la
    derniere position vue, ce qui EST l'appariement a fenetre fixe deja publie.
    """
    open_tracks: list[list[tuple]] = []
    closed: list[list[tuple]] = []

    for index, current in enumerate(slices):
        if index == 0:
            open_tracks = [[(current["z"], r, c)] for r, c in current["cells"]]
            continue

        dz = current["z"] - slices[index - 1]["z"]
        # Position predite de chaque piste dans CETTE coupe.
        predictions = []
        for piste in open_tracks:
            z_last, r_last, c_last = piste[-1]
            if predictive and len(piste) >= 2:
                z_prev, r_prev, c_prev = piste[-2]
                span = z_last - z_prev
                if span > 0:
                    rate_r = (r_last - r_prev) / span
                    rate_c = (c_last - c_prev) / span
                    predictions.append((r_last + rate_r * dz, c_last + rate_c * dz))
                    continue
            predictions.append((r_last, c_last))

        # Toutes les paires (piste, cellule) dans la tolerance, triees par erreur
        # NORMALISEE -- les deux axes n'ont ni la meme unite ni la meme echelle, donc
        # comparer des erreurs brutes reviendrait a trier sur l'angle seul.
        candidates = []
        for t, (pr, pc) in enumerate(predictions):
            for k, (r, c) in enumerate(current["cells"]):
                er = abs(r - pr) / radial_mm
                ec = abs(c - pc) / angular
                if er <= 1.0 and ec <= 1.0:
                    candidates.append((max(er, ec), t, k))
        candidates.sort()

        used_tracks: set[int] = set()
        used_cells: set[int] = set()
        for _, t, k in candidates:
            if t in used_tracks or k in used_cells:
                continue
            used_tracks.add(t)
            used_cells.add(k)
            r, c = current["cells"][k]
            open_tracks[t].append((current["z"], r, c))

        still_open = [p for t, p in enumerate(open_tracks) if t in used_tracks]
        closed.extend(p for t, p in enumerate(open_tracks) if t not in used_tracks)
        for k, (r, c) in enumerate(current["cells"]):
            if k not in used_cells:
                still_open.append([(current["z"], r, c)])
        open_tracks = still_open

    return closed + open_tracks


def straightness(piste: list[tuple]) -> float:
    """Deplacement NET rapporte au chemin parcouru, en rayon. 1 = monotone."""
    radii = np.array([r for _, r, _ in piste])
    steps = np.abs(np.diff(radii))
    path = float(steps.sum())
    if path <= 0.0:
        return float("nan")
    return float(abs(radii[-1] - radii[0]) / path)


def summarise(tracks: list[list[tuple]]) -> dict:
    """Ce qu'on rapporte d'un jeu de pistes."""
    lengths = np.array([len(p) for p in tracks]) if tracks else np.array([0])
    long_ones = [p for p in tracks if len(p) >= 3]
    straights = np.array([s for s in (straightness(p) for p in long_ones)
                          if np.isfinite(s)])
    drifts = []
    for piste in long_ones:
        dz_mm = (piste[-1][0] - piste[0][0]) * VOXEL_UM / 1000.0
        if dz_mm > 0:
            drifts.append((piste[-1][1] - piste[0][1]) / dz_mm)
    # ⚠ L'ETENDUE de la piste la plus longue est la grandeur qui porte l'information,
    # pas sa longueur : une longueur est un entier sur une plage de 2 a 9 coupes, donc
    # une statistique trop grossiere pour separer un effet de son hypothese nulle. Une
    # etendue en millimetres est continue, et c'est elle qui dit « ce defaut a traverse
    # six millimetres de rayon » -- l'enonce meme qu'on cherche a etablir.
    best = max(tracks, key=len) if tracks else []
    span = abs(best[-1][1] - best[0][1]) if len(best) >= 2 else 0.0
    return {
        "tracks": len(tracks),
        "longest": int(lengths.max()),
        "span_mm": float(span),
        "at_least_3": int((lengths >= 3).sum()),
        "at_least_4": int((lengths >= 4).sum()),
        "at_least_5": int((lengths >= 5).sum()),
        "straightness_mean": float(straights.mean()) if straights.size else float("nan"),
        "drift_mm_per_mm": float(np.median(drifts)) if drifts else float("nan"),
    }


def permute(slices: list[dict], generator) -> list[dict]:
    """Meme multiensemble de cellules, repartition entre coupes detruite.

    Les EFFECTIFS par coupe sont conserves : sinon on testerait aussi le fait qu'une
    coupe porte quatre cellules et non une, qui n'est pas la question.
    """
    pool = [cell for s in slices for cell in s["cells"]]
    order = generator.permutation(len(pool))
    shuffled, cursor = [], 0
    for s in slices:
        take = len(s["cells"])
        shuffled.append({"z": s["z"], "cells": [pool[i] for i in order[cursor:cursor + take]]})
        cursor += take
    return shuffled


def uniform(slices: list[dict], generator, radial_span: tuple, angular_span: float) -> list[dict]:
    """Cellules tirees uniformement -- le meme nul que `fusion_scan`, plus faible."""
    return [{"z": s["z"],
             "cells": [(float(generator.uniform(*radial_span)),
                        float(generator.integers(0, int(angular_span))))
                       for _ in s["cells"]]}
            for s in slices]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Les sites suspects derivent-ils, ou font-ils un millimetre de haut ?",
        epilog="Meme tolerance que la mesure publiee ; seul le CENTRE de la fenetre change.",
    )
    parser.add_argument("scans", type=Path, nargs="+", help="JSON produits par fusion_scan.py")
    parser.add_argument("--radial-mm", type=float, default=1.0,
                        help="tolerance radiale, celle de la mesure publiee (defaut: 1,0)")
    parser.add_argument("--angular", type=float, default=1000.0,
                        help="tolerance angulaire en colonnes (defaut: 1000)")
    parser.add_argument("--reach", type=float, default=3000.0)
    parser.add_argument("--level", type=int, default=0,
                        help="niveau de pyramide du scan : divise l'etendue angulaire")
    parser.add_argument("--null", choices=("permutation", "uniforme"), default="permutation")
    parser.add_argument("--trials", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out", type=Path, default=None, help="ecrire le rapport JSON")
    args = parser.parse_args()

    # ⚠⚠ La tolerance angulaire est en COLONNES, donc c'est une longueur, donc elle
    # suit le niveau de pyramide comme tout le reste. Au niveau 2 la circonference
    # entiere ne fait plus que 4712 colonnes : y laisser 1000 colonnes ferait une
    # fenetre de 21 % du tour au lieu de 5,3 %, et le suiveur apparierait des sites
    # separes par un cinquieme du rouleau. C'est exactement le piege nº1 du depot --
    # un seuil cale sur un niveau ne se transporte pas a un autre.
    scale = 2 ** args.level
    angular_span = 2.0 * np.pi * args.reach / scale
    args.angular = args.angular / scale
    if scale != 1:
        print(f"⚠ niveau {args.level} : tolerance angulaire {args.angular:.0f} colonnes "
              f"sur {angular_span:.0f} ({args.angular / angular_span * 100:.1f} % du tour)")
    generator = np.random.default_rng(args.seed)
    report = []

    for path in args.scans:
        slices = load_slices(path)
        counts = [len(s["cells"]) for s in slices]
        if sum(counts) < 4:
            print(f"{path.name}: {sum(counts)} cellules -- trop peu, saute")
            continue

        tracks_obs = track(slices, args.radial_mm, args.angular, True)
        observed = summarise(tracks_obs)
        fixed = summarise(track(slices, args.radial_mm, args.angular, False))

        all_radii = [r for s in slices for r, _ in s["cells"]]
        span = (min(all_radii), max(all_radii))
        null_runs = []
        for _ in range(args.trials):
            fake = (permute(slices, generator) if args.null == "permutation"
                    else uniform(slices, generator, span, angular_span))
            null_runs.append(summarise(track(fake, args.radial_mm, args.angular, True)))
        # ⚠ Une p-valeur, pas seulement un p95 : « 5 contre un p95 de 4 » ne dit pas
        # si on est a 4 % ou a 0,01 %. La convention (compte + 1) / (tirages + 1) evite
        # d'annoncer p = 0 quand aucun tirage n'atteint la valeur observee -- ce qui
        # serait une certitude que 2000 tirages ne peuvent pas donner.
        null = {}
        for key in ("longest", "span_mm", "at_least_3", "at_least_4", "straightness_mean"):
            draws = np.asarray([r[key] for r in null_runs], dtype=float)
            good = draws[np.isfinite(draws)]
            reached = int((good >= observed[key]).sum()) if np.isfinite(observed[key]) else 0
            null[key] = {"mean": float(good.mean()) if good.size else float("nan"),
                         "p95": float(np.percentile(good, 95)) if good.size else float("nan"),
                         "p": (reached + 1) / (good.size + 1) if good.size else float("nan")}

        print(f"\n=== {path.name} — {len(slices)} coupes, {sum(counts)} cellules "
              f"(pas {slices[1]['z'] - slices[0]['z']} vx "
              f"= {(slices[1]['z'] - slices[0]['z']) * VOXEL_UM / 1000:.2f} mm) ===")
        print(f"  {'':22} {'predictif':>10} {'fixe':>10} {'hasard':>10} {'p':>8}")
        for key, label, fmt in (("longest", "piste la plus longue", "d"),
                                ("span_mm", "  son etendue (mm)", ".2f"),
                                ("at_least_3", "pistes >= 3 coupes", "d"),
                                ("at_least_4", "pistes >= 4 coupes", "d"),
                                ("straightness_mean", "rectitude (>= 3)", ".3f")):
            print(f"  {label:22} {observed[key]:>10{fmt}} {fixed[key]:>10{fmt}} "
                  f"{null[key]['mean']:>10.2f} {null[key]['p']:>8.4f}")
        print(f"  {'derive mediane':22} {observed['drift_mm_per_mm']:>10.2f} mm/mm")
        best = max(tracks_obs, key=len)
        print("  la piste : " + " -> ".join(f"z{z}:r{r:.1f}" for z, r, _ in best))

        gain = observed["longest"] > fixed["longest"]
        beats = null["span_mm"]["p"] < 0.05
        straight = (np.isfinite(observed["straightness_mean"])
                    and observed["straightness_mean"] > null["straightness_mean"]["p95"])
        if beats and gain and straight:
            verdict = "DERIVE : plus longue que le hasard, plus longue qu'a fenetre fixe, et DROITE"
        elif beats and gain:
            verdict = "plus longue que le hasard et que la fenetre fixe, mais pas plus droite"
        elif gain:
            verdict = "la prediction allonge, mais pas au-dela du hasard"
        else:
            verdict = "la prediction n'apporte rien -- lecture « defaut d'un millimetre » tenue"
        print(f"  VERDICT : {verdict}")

        report.append({"scan": path.name, "slices": len(slices), "cells": sum(counts),
                       "predictive": observed, "fixed": fixed, "null": null,
                       "null_kind": args.null, "verdict": verdict})

    # ⚠ Une bande de cinq coupes ne peut pas, seule, rendre une p-valeur convaincante :
    # la piste la plus longue y est plafonnee a 5. Ce qui se teste a l'echelle du
    # rouleau, c'est l'ENSEMBLE des bandes -- et la methode de Fisher combine des
    # p-valeurs INDEPENDANTES, ce qu'elles sont ici puisque les bandes sont disjointes
    # en z et separees de plus d'un centimetre.
    spans = [r["null"]["span_mm"]["p"] for r in report if np.isfinite(r["null"]["span_mm"]["p"])]
    if len(spans) > 1:
        from scipy.stats import chi2
        statistic = -2.0 * float(np.log(spans).sum())
        combined = float(chi2.sf(statistic, 2 * len(spans)))
        print(f"\nFISHER sur {len(spans)} bandes (etendue de la piste) : "
              f"khi2 = {statistic:.1f}, p = {combined:.2e}")
        print(f"  bandes a p < 0,05 : {sum(1 for v in spans if v < 0.05)} / {len(spans)} "
              f"(attendu au hasard : {0.05 * len(spans):.1f})")
        report.append({"fisher": {"bands": len(spans), "chi2": statistic, "p": combined,
                                  "below_05": sum(1 for v in spans if v < 0.05)}})

    if args.out:
        args.out.write_text(json.dumps(report, indent=2) + "\n")
        print(f"\necrit : {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
