#!/usr/bin/env python3
"""Le corpus des champs de correction : qui est réparable, et est-ce que ça se voit ?

`champ_correction.py` mesure un segment. Ce fichier lit la campagne entière et pose la
seule question qui compte pour la production :

> **Un segment dont le décalage est COHÉRENT rend-il une meilleure carte d'encre qu'un
> segment aussi décalé mais incohérent ?**

Si oui, alors le champ ne dit pas seulement *à quel point c'est raté* — il dit **ce
qu'il faut en faire** : translater le maillage, ou reprendre le traçage.

⚠⚠ **Le piège que cette comparaison évite.** Comparer « cohérents » et « incohérents »
sans plus de précaution mesurerait surtout que les premiers sont moins décalés. On
apparie donc sur le **décalage médian** : à décalage comparable, la cohérence
change-t-elle quelque chose ? Sans cet appariement, le résultat serait une redite de
`19`, déguisée.

⚠ Toutes les coupures sont des **médianes de la population**, jamais des valeurs
absolues (règle nº 1 du dépôt) : un seuil en µm ne se transporterait pas d'un rouleau à
l'autre, et un seuil en corrélation encore moins.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from croiser_instruments import detectable_rho  # noqa: E402


def charger(dossier: Path) -> list[dict]:
    lignes = []
    for f in sorted(dossier.glob("*.json")):
        contenu = json.loads(f.read_text())
        for rec in (contenu if isinstance(contenu, list) else [contenu]):
            if rec.get("segment"):
                lignes.append(rec)
    return lignes


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Agreger la campagne de champs de correction et la confronter.")
    parser.add_argument("champs", type=Path, help="repertoire des JSON de champ_correction")
    parser.add_argument("--encre", type=Path, default=None,
                        help="rapport de croiser_encre.py, pour la confrontation")
    parser.add_argument("--index", type=Path, default=None,
                        help="results/index.json de windcheck, pour les croisements")
    parser.add_argument("--cible", default="encre_contraste_p90_p50")
    parser.add_argument("--pas-um", type=float, default=142.8,
                        help="pas inter-feuilles, MESURE ailleurs et avant (11 §3, "
                             "cv 1,8 %%). ⚠ Il sert de seuil entre « la trace ondule "
                             "dans sa feuille » et « elle a change de feuille » : un "
                             "seuil qui viendrait de cette mesure-ci serait circulaire")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    from scipy.stats import mannwhitneyu, spearmanr

    pas = args.pas_um
    lignes = charger(args.champs)
    if len(lignes) < 8:
        print(f"seulement {len(lignes)} segments", file=sys.stderr)
        return 1

    coh = np.array([r["coherence_voisins"] for r in lignes], dtype=float)
    tem = np.array([r["coherence_temoin_melange"] for r in lignes], dtype=float)
    dec = np.array([abs(r["decalage_median_um"]) for r in lignes], dtype=float)
    res = np.array([r["residuel_median_um"] for r in lignes], dtype=float)
    bon = np.isfinite(coh) & np.isfinite(tem)

    print(f"{len(lignes)} segments, {int(bon.sum())} avec une coherence calculable\n")
    print(f"{'grandeur':>26} {'min':>8} {'mediane':>9} {'max':>8}")
    for nom, v in (("|decalage| median (um)", dec), ("residuel median (um)", res),
                   ("coherence voisins", coh), ("coherence TEMOIN melange", tem)):
        w = v[np.isfinite(v)]
        print(f"{nom:>26} {w.min():>8.3f} {float(np.median(w)):>9.3f} {w.max():>8.3f}")

    # ⚠⚠ LE CONTROLE de la mesure elle-meme : la coherence doit battre son propre
    # temoin de melange, segment par segment. Si elle ne le bat pas, tout ce qui suit
    # porte sur un artefact de calcul et non sur la geometrie.
    gagne = int((coh[bon] > tem[bon]).sum())
    u, pu = mannwhitneyu(coh[bon], tem[bon], alternative="greater")
    print(f"\ncoherence > temoin melange : {gagne} / {int(bon.sum())} segments  "
          f"(Mann-Whitney p = {pu:.2e})")
    if gagne <= bon.sum() * 0.6:
        print("⚠⚠ la coherence ne bat pas son temoin : la suite ne veut rien dire")

    # ⚠⚠ LE RAPPORT QUI DIT QUELLE REPARATION EST LA BONNE. Le decalage median est la
    # part de l'erreur qu'une TRANSLATION du maillage enleverait ; le residuel est ce
    # qu'elle laisserait. Si le residuel domine, translater ne repare presque rien --
    # l'erreur est une deformation locale, pas une pose ratee, et le remede n'est pas le
    # meme. C'est la question de production, et elle se lit dans un seul rapport.
    part_rigide = dec / np.maximum(dec + res, 1e-9)
    print(f"\npart de l'erreur qu'une TRANSLATION enleverait : "
          f"mediane {float(np.median(part_rigide)) * 100:.1f} %  "
          f"(p90 {float(np.percentile(part_rigide, 90)) * 100:.1f} %)")
    print(f"⚠ le pas inter-feuilles vaut ~{pas:.1f} um ; le residuel median vaut "
          f"{float(np.median(res)) / pas:.2f} ecart(s) inter-feuilles")

    # ⚠⚠ LE LIEN AVEC LE MODE D'ECHEC DOMINANT. Un residuel sous un ecart inter-feuilles
    # veut dire que la trace ondule DANS sa feuille -- genant, pas fatal. Un residuel
    # au-dessus veut dire qu'elle a change de feuille en route, ce qui est le saut de
    # spire, la panne que tout ce depot cherche. Le seuil n'est pas choisi : c'est le
    # pas mesure independamment (11 §3, cv 1,8 %).
    p90 = np.array([r["residuel_p90_um"] for r in lignes], dtype=float)
    saut = p90 > pas
    print(f"segments dont le residuel p90 depasse UN ecart inter-feuilles : "
          f"{int(saut.sum())} / {len(lignes)} ({100 * saut.mean():.0f} %)")
    # ⚠ Un detecteur qui ne NOMME pas ce qu'il signale n'est pas exploitable : la sortie
    # utile n'est pas un taux, c'est une liste de segments a rouvrir.
    for i in np.flatnonzero(saut):
        print(f"    ⚑ {lignes[i]['segment'][:44]:44} p90 {p90[i]:6.1f} um "
              f"({p90[i] / pas:.2f} ecarts)  coherence {coh[i]:+.3f}")

    rapport = {
        "segments": len(lignes),
        "part_rigide_mediane": float(np.median(part_rigide)),
        "pas_inter_feuilles_um": pas,
        "residuel_en_ecarts_inter_feuilles": float(np.median(res)) / pas,
        "segments_residuel_p90_sup_un_ecart": int(saut.sum()),
        "signales": [lignes[int(i)]["segment"] for i in np.flatnonzero(saut)],
        "coherence_mediane": float(np.median(coh[bon])),
        "temoin_median": float(np.median(tem[bon])),
        "coherence_bat_temoin": gagne,
        "p_mann_whitney": float(pu),
        "rho_detectable": detectable_rho(int(bon.sum())),
    }

    # ⚠⚠ LA QUALITE DE TRACE EST-ELLE UNE FONCTION DE LA POSITION DANS LE ROULEAU ?
    # Les segments portent leur indice de fenetre dans leur nom (`w107-109`). Si les
    # defauts se groupaient dans une plage, ce ne serait pas un accident de tracage mais
    # une propriete du rouleau a cet endroit -- et ca dit ou porter l'effort, ce qu'un
    # taux global ne dit pas.
    rapport_w: dict = {}
    fenetres, res_f, coh_f, p90_f = [], [], [], []
    for i, r in enumerate(lignes):
        m = re.search(r"[-_]w(\d+)", r["segment"])
        if m:
            fenetres.append(int(m.group(1)))
            res_f.append(res[i]); coh_f.append(coh[i]); p90_f.append(p90[i])
    if len(fenetres) >= 10:
        w = np.array(fenetres, dtype=float)
        print(f"\n{len(w)} segments portent un indice de fenetre "
              f"(w{int(w.min())} a w{int(w.max())})")
        print(f"{'grandeur':>26} {'rho ~ fenetre':>14} {'p':>9}")
        rapport_w = {}
        for nom, v in (("residuel_median_um", res_f), ("residuel_p90_um", p90_f),
                       ("coherence_voisins", coh_f)):
            x = np.array(v, dtype=float)
            m2 = np.isfinite(x)
            rho, pv = spearmanr(w[m2], x[m2])
            rapport_w[nom] = {"rho": float(rho), "p": float(pv), "n": int(m2.sum())}
            print(f"{nom:>26} {rho:>+14.3f} {pv:>9.4f}{' *' if pv < 0.05 else ''}")

    rapport["par_fenetre"] = rapport_w or None

    if args.encre is not None and args.encre.exists():
        enc = {r["segment"]: r for r in json.loads(args.encre.read_text())["segments"]}
        paires = [(r, enc[r["segment"]]) for r in lignes if r["segment"] in enc]
        if len(paires) >= 8:
            y = np.array([e[args.cible] for _, e in paires], dtype=float)
            print(f"\n{len(paires)} segments ont un champ ET une carte d'encre publiee")
            print(f"⚠ a n = {len(paires)}, rho detectable {detectable_rho(len(paires)):.2f}")
            print(f"\n{'champ':>26} {'rho ~ encre':>12} {'p':>9}")
            correls = {}
            for nom, v in (("coherence_voisins", [c["coherence_voisins"] for c, _ in paires]),
                           ("residuel_median_um", [c["residuel_median_um"] for c, _ in paires]),
                           ("|decalage_median_um|", [abs(c["decalage_median_um"]) for c, _ in paires]),
                           ("part_au_bord", [c["part_au_bord"] for c, _ in paires])):
                x = np.array(v, dtype=float)
                m = np.isfinite(x) & np.isfinite(y)
                if m.sum() < 8:
                    continue
                rho, p = spearmanr(x[m], y[m])
                correls[nom] = {"rho": float(rho), "p": float(p), "n": int(m.sum())}
                print(f"{nom:>26} {rho:>+12.3f} {p:>9.4f}{' *' if p < 0.05 else ''}")
            rapport["correlations_encre"] = correls

            # ⭐ LA question : a decalage COMPARABLE, la coherence change-t-elle l'encre ?
            d = np.array([abs(c["decalage_median_um"]) for c, _ in paires], dtype=float)
            c_ = np.array([c["coherence_voisins"] for c, _ in paires], dtype=float)
            m = np.isfinite(d) & np.isfinite(c_) & np.isfinite(y)
            haut_dec = d[m] > np.median(d[m])
            print(f"\nAPPARIE sur le decalage — moitie la plus DECALEE "
                  f"({int(haut_dec.sum())} segments)")
            sous_y, sous_c = y[m][haut_dec], c_[m][haut_dec]
            if sous_y.size >= 8:
                coherents = sous_c > np.median(sous_c)
                u2, p2 = mannwhitneyu(sous_y[coherents], sous_y[~coherents],
                                      alternative="greater")
                print(f"  encre mediane, decalage COHERENT   : "
                      f"{float(np.median(sous_y[coherents])):.3f}")
                print(f"  encre mediane, decalage INCOHERENT : "
                      f"{float(np.median(sous_y[~coherents])):.3f}")
                print(f"  Mann-Whitney unilateral p = {p2:.4f}"
                      f"{' *' if p2 < 0.05 else ''}")
                rapport["apparie_decalage"] = {
                    "n": int(sous_y.size),
                    "encre_coherent": float(np.median(sous_y[coherents])),
                    "encre_incoherent": float(np.median(sous_y[~coherents])),
                    "p": float(p2),
                }

    if args.index is not None and args.index.exists():
        publie = {r["segment"]: r for r in json.loads(args.index.read_text())}
        paires = [(r, publie[r["segment"]]) for r in lignes if r["segment"] in publie]
        if len(paires) >= 8:
            ev = np.array([len(p.get("events", []) or []) for _, p in paires], dtype=float)
            print(f"\n{len(paires)} segments ont un champ ET des croisements publies")
            print(f"{'champ':>26} {'rho ~ croisements':>18} {'p':>9}")
            croix = {}
            for nom, v in (("coherence_voisins", [c["coherence_voisins"] for c, _ in paires]),
                           ("residuel_median_um", [c["residuel_median_um"] for c, _ in paires])):
                x = np.array(v, dtype=float)
                m = np.isfinite(x)
                rho, p = spearmanr(x[m], ev[m])
                croix[nom] = {"rho": float(rho), "p": float(p), "n": int(m.sum())}
                print(f"{nom:>26} {rho:>+18.3f} {p:>9.4f}{' *' if p < 0.05 else ''}")
            rapport["correlations_croisements"] = croix

    if args.out:
        args.out.write_text(json.dumps(rapport, indent=2) + "\n")
        print(f"\necrit : {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
