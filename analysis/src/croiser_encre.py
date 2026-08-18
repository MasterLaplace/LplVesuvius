#!/usr/bin/env python3
"""L'instrument change-t-il une DÉCISION ? — profondeur de trace contre encre publiée.

⚠⚠ **C'est le pas que `docs/00` §9 nomme comme manquant.** Tout ce que ce dépôt a
construit JUGE : la profondeur de surface dit qu'une trace est décalée, la séparabilité
dit qu'un scan résout mal, la proximité dit qu'une trace se recoupe. Aucun de ces
verdicts n'a encore *changé* quoi que ce soit. Le tableau des goulots du concours
demande, littéralement, de la **détection conservative d'échec** — c'est-à-dire une
règle qui écarte ce qui va rater, avant de payer le calcul.

La décision testée ici est la plus simple qui soit :

> **Écarter les segments dont l'écart pic↔trace est le plus grand améliore-t-il ce que
> le corpus rend ?**

## Pourquoi les cartes d'encre PUBLIÉES

Elles sont le résultat d'un **autre** pipeline que le nôtre, récupéré tel quel. Une
corrélation entre notre mesure de trace et leur résultat ne peut donc pas être un
artefact partagé : rien de notre chaîne n'entre dans leur sortie.

⚠ **Le confond à nommer, parce qu'il est réel** : une carte d'encre vide peut vouloir
dire « la trace a raté la feuille » *ou* « ce morceau de papyrus est vierge ». Aucune
mesure ne les sépare ici. C'est pourquoi le résultat se lit comme un *tri de corpus*,
jamais comme un diagnostic de segment.

## Le témoin, et pourquoi il est indispensable

Écarter un quart d'un corpus déplace presque toujours une médiane. La question n'est
donc pas « est-ce que ça monte », mais « est-ce que ça monte **plus qu'un tirage au
hasard de même taille** ». D'où la permutation : mêmes effectifs, choix aléatoire,
mille fois. Sans elle, la vérification ne peut pas échouer (`HANDOFF` §9.3).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from croiser_instruments import detectable_rho  # noqa: E402


def mesures_encre(chemin: Path) -> dict:
    """Quantité d'encre d'une carte publiée, dans l'emprise du segment.

    ⚠ **Aucun seuil absolu** (`HANDOFF` §9.1) : les trois grandeurs sont soit des
    moments de la distribution, soit des rapports de centiles. Un seuil en niveaux de
    gris ne se transporterait pas d'un rendu à l'autre.

    ⚠ Le remplissage (valeur exactement nulle) est **exclu de l'emprise**, sinon un
    segment étroit dans un grand canevas paraît vide alors qu'il est plein.
    """
    from PIL import Image

    Image.MAX_IMAGE_PIXELS = None
    im = np.asarray(Image.open(chemin).convert("L"), dtype=np.float32)
    emprise = im[im > 0]
    if emprise.size < 1000:
        return {}
    p50, p90, p99 = np.percentile(emprise, [50, 90, 99])
    return {
        "emprise_px": int(emprise.size),
        "encre_moyenne": float(emprise.mean()),
        "encre_ecart_type": float(emprise.std()),
        # ⚠ Un rapport de centiles est SANS UNITE et sans seuil : il dit « le haut de la
        # distribution est-il loin du milieu », ce qui est exactement la difference entre
        # une carte bimodale (des lettres) et une carte plate (rien).
        "encre_contraste_p90_p50": float(p90 / p50) if p50 > 0 else float("nan"),
        "encre_contraste_p99_p50": float(p99 / p50) if p50 > 0 else float("nan"),
    }


def decision(ecarts: np.ndarray, encre: np.ndarray, part: float,
             tirages: int, graine: int) -> dict:
    """Écarter la pire fraction par écart : est-ce mieux qu'un tirage au hasard ?"""
    n = ecarts.size
    a_jeter = max(1, int(round(n * part)))
    garde = np.argsort(ecarts)[: n - a_jeter]
    apres = float(np.median(encre[garde]))
    avant = float(np.median(encre))

    rng = np.random.default_rng(graine)
    temoins = np.array([float(np.median(encre[rng.permutation(n)[: n - a_jeter]]))
                        for _ in range(tirages)])
    # ⚠ p unilateral : l'hypothese testee est « la regle fait MIEUX qu'un hasard », pas
    # « elle fait autre chose ». Le +1 au numerateur et au denominateur est la correction
    # usuelle qui interdit un p exactement nul sur un nombre fini de tirages.
    p = float((np.sum(temoins >= apres) + 1) / (tirages + 1))
    return {
        "part_ecartee": part,
        "segments_gardes": int(n - a_jeter),
        "encre_mediane_avant": avant,
        "encre_mediane_apres": apres,
        "gain": apres - avant,
        "temoin_median": float(np.median(temoins)),
        "temoin_p95": float(np.percentile(temoins, 95)),
        "p_permutation": p,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Croiser la profondeur de trace avec les cartes d'encre publiees.",
        epilog="Une regle qui ne bat pas un tirage au hasard n'est pas une regle.")
    parser.add_argument("profondeur", type=Path, help="JSON de zarr_depth.py")
    parser.add_argument("cartes", type=Path, help="repertoire des cartes d'encre .jpg")
    parser.add_argument("--grandeur", default="ecart_a_la_trace",
                        help="la mesure de trace qui decide")
    parser.add_argument("--cible", default="encre_contraste_p90_p50",
                        help="la grandeur d'encre qu'on cherche a ameliorer")
    parser.add_argument("--parts", type=float, nargs="+",
                        default=[0.10, 0.20, 0.25, 0.33, 0.50])
    parser.add_argument("--tirages", type=int, default=2000)
    parser.add_argument("--graine", type=int, default=0)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    from scipy.stats import spearmanr

    profond = {r["segment"]: r for r in json.loads(args.profondeur.read_text())
               if r.get("segment")}
    lignes = []
    for seg, rec in sorted(profond.items()):
        carte = args.cartes / f"{seg}.jpg"
        if not carte.exists():
            continue
        enc = mesures_encre(carte)
        if not enc:
            continue
        lignes.append({"segment": seg, **{k: v for k, v in rec.items()
                                          if isinstance(v, (int, float))}, **enc})

    if len(lignes) < 8:
        print(f"seulement {len(lignes)} segments appaires", file=sys.stderr)
        return 1

    n = len(lignes)
    print(f"{n} segments ont a la fois une mesure de trace et une carte d'encre publiee")
    print(f"⚠ a n = {n}, la mesure detecte un rho de {detectable_rho(n):.2f} "
          f"a 80 % de puissance\n")

    champs_trace = ["ecart_a_la_trace", "au_bord", "tiers_central", "iqr", "avec_matiere"]
    champs_encre = ["encre_moyenne", "encre_ecart_type",
                    "encre_contraste_p90_p50", "encre_contraste_p99_p50"]
    correlations = []
    print(f"{'trace':>18} {'encre':>26} {'rho':>8} {'p':>9}")
    for ct in champs_trace:
        for ce in champs_encre:
            a = np.array([l.get(ct, np.nan) for l in lignes], dtype=float)
            b = np.array([l.get(ce, np.nan) for l in lignes], dtype=float)
            bon = np.isfinite(a) & np.isfinite(b)
            if bon.sum() < 8:
                continue
            rho, p = spearmanr(a[bon], b[bon])
            correlations.append({"trace": ct, "encre": ce, "n": int(bon.sum()),
                                 "rho": float(rho), "p": float(p)})
            marque = " *" if p < 0.05 else ""
            print(f"{ct:>18} {ce:>26} {rho:>+8.3f} {p:>9.4f}{marque}")

    # ⚠ Le confond de taille : si l'encre ne suivait que l'etendue du segment, tout ce
    # qui precede serait une mesure de surface deguisee. On le mesure au lieu de l'exclure.
    aire = np.array([l["emprise_px"] for l in lignes], dtype=float)
    print()
    for ce in champs_encre:
        b = np.array([l.get(ce, np.nan) for l in lignes], dtype=float)
        bon = np.isfinite(b)
        rho, p = spearmanr(aire[bon], b[bon])
        print(f"{'CONFOND emprise':>18} {ce:>26} {rho:>+8.3f} {p:>9.4f}")

    ecarts = np.array([l.get(args.grandeur, np.nan) for l in lignes], dtype=float)
    cible = np.array([l.get(args.cible, np.nan) for l in lignes], dtype=float)
    bon = np.isfinite(ecarts) & np.isfinite(cible)
    print(f"\nDECISION : ecarter les pires « {args.grandeur} », "
          f"cible « {args.cible} », {int(bon.sum())} segments")
    print(f"{'part':>6} {'gardes':>7} {'avant':>8} {'apres':>8} {'gain':>8} "
          f"{'temoin p95':>11} {'p':>8}")
    decisions = []
    for part in args.parts:
        d = decision(ecarts[bon], cible[bon], part, args.tirages, args.graine)
        decisions.append(d)
        marque = " *" if d["p_permutation"] < 0.05 else ""
        print(f"{part:>6.2f} {d['segments_gardes']:>7} {d['encre_mediane_avant']:>8.3f} "
              f"{d['encre_mediane_apres']:>8.3f} {d['gain']:>+8.3f} "
              f"{d['temoin_p95']:>11.3f} {d['p_permutation']:>8.4f}{marque}")

    if args.out:
        args.out.write_text(json.dumps(
            {"n": n, "rho_detectable": detectable_rho(n),
             "correlations": correlations, "decisions": decisions,
             "segments": lignes}, indent=2) + "\n")
        print(f"\necrit : {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
