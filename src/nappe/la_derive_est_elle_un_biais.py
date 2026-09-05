#!/usr/bin/env python3
"""La dérive de 53 µm par tour est-elle un BIAIS de longueur de pas, ou irréductible ?

⚠⚠⚠ POURQUOI CETTE QUESTION VIENT AVANT TOUTE AUTRE. `derouler_par_le_pas_normal` mesure une
dérive de **53 µm par tour**, soit 39 % d'une feuille, et nomme le remède attendu : un recalage
sur la matière à chaque pas. Mais un recalage est **cher** — il faut lire le volume — et il
serait absurde de le construire si la dérive vient simplement d'une **longueur de pas mal
estimée**. Un biais est une constante : il se retranche une fois et disparaît. Une dispersion,
non.

⭐⭐ **Le test est bon marché et il tranche** : balayer la longueur du pas, et regarder si une
autre valeur que l'épaisseur nominale annule la dérive. Si oui, le remède est un nombre. Si non,
la dérive est **locale**, et seul un raccrochage à la matière peut la tuer.

⚠⚠⚠ ET LE PIÈGE EST ÉVIDENT : choisir la longueur qui minimise l'erreur **sur les mêmes spires**
qu'on mesure ensuite, c'est ajuster sur la réponse. La longueur est donc **ajustée sur la
première moitié** des spires et **jugée sur la seconde**, qu'elle n'a jamais vue.

⚠ Le témoin est la longueur **nominale** — l'écart médian déjà publié. Une longueur ajustée qui
ne battrait pas la nominale sur la moitié réservée n'aurait rien appris.

Usage :
    uv run python src/nappe/la_derive_est_elle_un_biais.py --verifier
    uv run python src/nappe/la_derive_est_elle_un_biais.py \\
        --json docs/mesures/la_derive_est_elle_un_biais.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "commun"))
sys.path.insert(0, str(RACINE / "src" / "nappe"))

WRAPS = RACINE / "docs" / "mesures" / "les_wraps_publies.json"


def erreur_du_pas(depart: np.ndarray, normale: np.ndarray, cible: np.ndarray,
                  pas_vx: float, sens: float, voxel_um: float) -> float:
    """L'erreur médiane d'un pas d'une longueur donnée, dans un sens fixé."""
    from le_pas_normal_atteint_la_spire import distance_a  # noqa: PLC0415

    if depart.size == 0 or cible.size == 0:
        return float("nan")
    return float(np.median(distance_a(depart + sens * normale * pas_vx, cible, voxel_um)))


def balayer(paires: list[dict], longueurs_um, sens: float, voxel_um: float) -> list[dict]:
    """L'erreur médiane sur un jeu de paires, pour chaque longueur de pas essayée.

    ⚠ Rendue par longueur ET par paire agrégée en médiane : une longueur qui gagnerait sur une
    paire en cassant les autres serait choisie par une moyenne, pas par une médiane.
    """
    out = []
    for L in longueurs_um:
        errs = [erreur_du_pas(p["depart"], p["normale"], p["cible"], L / voxel_um, sens,
                              voxel_um) for p in paires]
        errs = [e for e in errs if np.isfinite(e)]
        if errs:
            out.append(dict(longueur_um=round(float(L), 1),
                            erreur_um=round(float(np.median(errs)), 1),
                            paires=len(errs)))
    return out


def meilleure(balayage: list[dict]) -> dict | None:
    """La longueur de moindre erreur, et si elle touche le bord du balayage.

    ⚠⚠ Un minimum au bord ne désigne pas une longueur, il dit que le balayage était trop court —
    ce dépôt a déjà publié un optimum au bord et l'a payé.
    """
    if not balayage:
        return None
    b = min(balayage, key=lambda e: e["erreur_um"])
    return dict(**b, au_bord=bool(b is balayage[0] or b is balayage[-1]))


def _paires(echantillon: int, graine: int = 42) -> tuple[list[dict], float, float, float]:
    """Les paires de spires consécutives, avec leurs départs, normales et cibles."""
    from le_pas_normal_atteint_la_spire import essayer_le_pas, grille, normales  # noqa: PLC0415
    from les_wraps_publies import VOLUME, VOXEL_UM, wraps_du_fragment  # noqa: PLC0415

    if not WRAPS.is_file():
        raise SystemExit("écart entre spires non mesuré : lancer les_wraps_publies d'abord")
    ecart_um = json.loads(WRAPS.read_text())["resume"]["1"]["mediane_um"]

    rng = np.random.default_rng(graine)
    g = {}
    for w in wraps_du_fragment():
        lu = grille(w, VOLUME, VOXEL_UM)
        if lu is None:
            continue
        a, ok = lu
        n, bon = normales(a, ok)
        g[w["rang"]] = dict(points=a[ok], depart=a[bon], normale=n[bon])

    paires = []
    for r in sorted(g):
        if r + 1 not in g:
            continue
        d, n = g[r]["depart"], g[r]["normale"]
        if d.shape[0] == 0:
            continue
        k = rng.choice(d.shape[0], size=min(echantillon, d.shape[0]), replace=False)
        paires.append(dict(rang=r, depart=d[k], normale=n[k], cible=g[r + 1]["points"]))
    if not paires:
        raise SystemExit("aucune paire lisible")

    e = essayer_le_pas(paires[0]["depart"], paires[0]["normale"], paires[0]["cible"],
                       ecart_um / VOXEL_UM, VOXEL_UM)
    return paires, ecart_um, VOXEL_UM, (1.0 if e["retenu"] == "+" else -1.0)


def mesurer(echantillon: int = 3000, portee: float = 0.6, pas: int = 25) -> dict:
    """Le balayage de longueur, ajusté sur la première moitié et jugé sur la seconde."""
    paires, ecart_um, voxel_um, sens = _paires(echantillon)
    longueurs = np.linspace(ecart_um * (1.0 - portee), ecart_um * (1.0 + portee), pas)

    # ⚠⚠⚠ LA COUPURE EST FAITE SUR LE RANG, pas au hasard : deux spires voisines partagent leur
    # géométrie, donc un tirage aléatoire mettrait la même région des deux côtés et la « moitié
    # réservée » n'en serait pas une.
    milieu = len(paires) // 2
    ajust, reserve = paires[:milieu], paires[milieu:]

    b_ajust = balayer(ajust, longueurs, sens, voxel_um)
    b_reserve = balayer(reserve, longueurs, sens, voxel_um)
    b_tout = balayer(paires, longueurs, sens, voxel_um)
    choisie = meilleure(b_ajust)
    if choisie is None:
        raise SystemExit("balayage vide")

    def sur(jeu, L):
        errs = [erreur_du_pas(p["depart"], p["normale"], p["cible"], L / voxel_um, sens,
                              voxel_um) for p in jeu]
        errs = [e for e in errs if np.isfinite(e)]
        return round(float(np.median(errs)), 1) if errs else None

    nominale_reserve = sur(reserve, ecart_um)
    ajustee_reserve = sur(reserve, choisie["longueur_um"])
    return dict(voxel_um=voxel_um, sens=("+" if sens > 0 else "-"),
                ecart_nominal_um=ecart_um, echantillon=echantillon,
                paires=len(paires), paires_ajustement=len(ajust), paires_reservees=len(reserve),
                longueurs_essayees=len(longueurs),
                balayage_ajustement=b_ajust, balayage_reserve=b_reserve, balayage_tout=b_tout,
                longueur_ajustee_um=choisie["longueur_um"],
                minimum_au_bord=choisie["au_bord"],
                erreur_sur_la_reserve=dict(nominale_um=nominale_reserve,
                                           ajustee_um=ajustee_reserve),
                ecart_des_deux_longueurs_um=round(
                    abs(choisie["longueur_um"] - ecart_um), 1),
                # ⚠⚠ LE VERDICT : la longueur ajustée doit battre la nominale SUR LA MOITIÉ
                # RÉSERVÉE. Gagner sur celle qui l'a choisie ne prouverait rien.
                le_biais_explique_la_derive=bool(
                    nominale_reserve is not None and ajustee_reserve is not None
                    and ajustee_reserve < nominale_reserve),
                part_de_la_derive_expliquee=(
                    round(1.0 - ajustee_reserve / nominale_reserve, 4)
                    if nominale_reserve and ajustee_reserve is not None else None))


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    uu, vv = np.meshgrid(np.arange(20.0), np.arange(16.0), indexing="ij")
    plan = np.stack([uu * 3.0, vv * 3.0, np.zeros(uu.shape)], axis=-1).reshape(-1, 3)
    nrm = np.tile(np.array([0.0, 0.0, 1.0]), (plan.shape[0], 1))

    cible = plan + np.array([0.0, 0.0, 25.0])
    v("un pas de la bonne longueur ne fait aucune erreur",
      erreur_du_pas(plan, nrm, cible, 25.0, 1.0, 2.0) == 0.0)
    v("... et un pas trop court laisse exactement ce qui manque",
      erreur_du_pas(plan, nrm, cible, 15.0, 1.0, 2.0) == 20.0)
    v("... et un pas trop long dépasse d'autant",
      erreur_du_pas(plan, nrm, cible, 35.0, 1.0, 2.0) == 20.0)

    # ⚠⚠⚠ LE CAS « BIAIS » ET LE CAS « DISPERSION », et il faut les deux : sans le second, une
    # mesure qui trouverait toujours un minimum passerait pour une explication.
    biais = [dict(depart=plan, normale=nrm, cible=plan + np.array([0.0, 0.0, 30.0])),
             dict(depart=plan, normale=nrm, cible=plan + np.array([0.0, 0.0, 30.0]))]
    # ⚠ Le balayage est en MICROMÈTRES et la cible en voxels : à 2 µm/voxel, 30 voxels valent
    # 60 µm. Ma première version balayait 20 à 40 µm et ne pouvait donc pas atteindre l'optimum —
    # c'est `au_bord` qui l'a dit, et c'est exactement à ça qu'il sert.
    b = balayer(biais, np.linspace(40.0, 80.0, 21), 1.0, 2.0)
    m = meilleure(b)
    v("un biais pur est retrouvé par le balayage",
      abs(m["longueur_um"] - 60.0) < 1e-6, f"{m['longueur_um']} µm attendu 60")
    v("... et son minimum n'est pas au bord", not m["au_bord"])
    disp = [dict(depart=plan, normale=nrm, cible=plan + np.array([0.0, 0.0, 10.0])),
            dict(depart=plan, normale=nrm, cible=plan + np.array([0.0, 0.0, 50.0]))]
    d = balayer(disp, np.linspace(10.0, 110.0, 21), 1.0, 2.0)
    md = meilleure(d)
    v("une dispersion pure laisse une erreur qu'aucune longueur n'annule",
      md["erreur_um"] > 30.0, f"{md['erreur_um']} µm au mieux")
    # ⚠ Et le contrôle qui rend le précédent lisible : sur le biais, le minimum EST nul.
    v("... alors que sur le biais elle est nulle", m["erreur_um"] == 0.0, str(m["erreur_um"]))

    # ⚠⚠ Un minimum au bord doit être DÉCLARÉ, sinon on republie un optimum qui ne désigne rien.
    court = balayer(biais, np.linspace(20.0, 45.0, 6), 1.0, 2.0)
    v("un balayage trop court se déclare au bord", meilleure(court)["au_bord"],
      str(meilleure(court)))
    v("un balayage vide ne rend rien", meilleure([]) is None)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--echantillon", type=int, default=3000)
    p.add_argument("--portee", type=float, default=0.6)
    p.add_argument("--pas", type=int, default=25)
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(a.echantillon, a.portee, a.pas)
    print(f"écart nominal {r['ecart_nominal_um']:.1f} µm — {r['paires']} paires "
          f"({r['paires_ajustement']} pour ajuster, {r['paires_reservees']} réservées)\n")
    print(f"{'longueur µm':>12} {'ajustement':>12} {'réservée':>11}")
    print("-" * 38)
    res = {e["longueur_um"]: e["erreur_um"] for e in r["balayage_reserve"]}
    for e in r["balayage_ajustement"]:
        marque = " ←" if e["longueur_um"] == r["longueur_ajustee_um"] else ""
        print(f"{e['longueur_um']:>12.1f} {e['erreur_um']:>11.1f}µ "
              f"{res.get(e['longueur_um'], float('nan')):>10.1f}µ{marque}")
    er = r["erreur_sur_la_reserve"]
    print(f"\nlongueur ajustée : {r['longueur_ajustee_um']:.1f} µm "
          f"({r['ecart_des_deux_longueurs_um']:.1f} µm de la nominale)"
          f"{'  ⚠ AU BORD' if r['minimum_au_bord'] else ''}")
    print(f"sur la moitié RÉSERVÉE : nominale {er['nominale_um']:.1f} µm, "
          f"ajustée {er['ajustee_um']:.1f} µm")
    print(f"\n→ le biais explique la dérive : "
          f"{'OUI' if r['le_biais_explique_la_derive'] else 'NON'}"
          + (f"  ({r['part_de_la_derive_expliquee'] * 100:.0f} %)"
             if r["part_de_la_derive_expliquee"] is not None else ""))
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
