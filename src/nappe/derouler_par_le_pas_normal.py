#!/usr/bin/env python3
"""Combien de tours un dérouleur naïf survit-il ? — le pas normal ITÉRÉ, contre treize spires.

⚠⚠⚠ POURQUOI CE FICHIER EXISTE, ET C'EST LE GRAAL EN MINIATURE. `le_pas_normal_atteint_la_spire`
a montré qu'**un** pas d'une épaisseur le long de la normale tombe à 60 µm de la feuille voisine.
Dérouler, ce n'est pas faire un pas : c'est les enchaîner. La question qui décide est donc *au
bout de combien de tours l'erreur devient plus grande qu'une feuille* — car à ce moment-là le
dérouleur ne sait plus sur quelle feuille il est, et tout ce qu'il écrit ensuite est faux.

⭐⭐ **Les treize spires publiées permettent de le mesurer sans rien supposer** : après `k` pas
depuis la spire 1, on compare à la spire `1 + k`. La grille est conservée à chaque pas, donc les
normales se recalculent sur la surface **prédite** — c'est bien un dérouleur aveugle, pas un
transport guidé par la réponse.

⚠⚠⚠ LE SEUL BIT DE SUPERVISION EST LE SENS, ET IL EST DÉCLARÉ. Le signe d'une normale vient du
paramétrage de la grille : le choisir à chaque pas en regardant la cible reviendrait à souffler
la route au dérouleur. Il est donc fixé **une fois**, au premier pas, et les suivants sont
aveugles. Ce bit est compté et rendu.

⚠⚠ LE TÉMOIN EST LE PAS NUL : ne pas bouger éloigne de la spire `1 + k` d'environ `k` épaisseurs.
Un dérouleur qui ne battrait pas l'immobilité ne déroulerait rien.

Usage :
    uv run python src/nappe/derouler_par_le_pas_normal.py --verifier
    uv run python src/nappe/derouler_par_le_pas_normal.py \\
        --json docs/mesures/derouler_par_le_pas_normal.json
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


def un_pas(a: np.ndarray, ok: np.ndarray, pas_vx: float,
           sens: float) -> tuple[np.ndarray, np.ndarray]:
    """Une grille avancée d'un pas le long de ses propres normales.

    ⚠⚠ La GRILLE est conservée, pas seulement le nuage : sans elle les normales du pas suivant
    ne seraient pas calculables, et l'itération s'arrêterait au premier tour. C'est aussi ce qui
    rend le dérouleur **aveugle** — il n'a jamais besoin de la cible pour avancer.

    ⚠ Le masque rétrécit à chaque pas, parce qu'une normale demande quatre voisins valides. Le
    compte de cellules survivantes est donc rendu par l'appelant : un dérouleur qui « réussit »
    en ne gardant que trois cellules n'a pas déroulé, il a rétréci.
    """
    from le_pas_normal_atteint_la_spire import normales  # noqa: PLC0415

    n, bon = normales(a, ok)
    avance = a.copy()
    avance[bon] = a[bon] + sens * pas_vx * n[bon]
    return avance, bon


def derouler(depart: np.ndarray, ok: np.ndarray, cibles: dict[int, np.ndarray],
             pas_vx: float, voxel_um: float, sens: float,
             echantillon: int, graine: int = 42) -> list[dict]:
    """Le pas itéré, comparé à la spire de même rang à chaque tour.

    ⚠⚠ La comparaison se fait sur les cellules **encore vivantes**, et leur compte est rendu à
    côté de la distance : les deux ensemble disent si l'erreur est petite parce que le dérouleur
    est bon ou parce qu'il ne reste presque rien à juger.
    """
    from le_pas_normal_atteint_la_spire import distance_a  # noqa: PLC0415

    rng = np.random.default_rng(graine)
    a, m = depart.copy(), ok.copy()
    sur_place = depart.copy()
    out = []
    for k in sorted(cibles):
        a, m = un_pas(a, m, pas_vx, sens)
        pts = a[m]
        if pts.shape[0] == 0:
            break
        idx = rng.choice(pts.shape[0], size=min(echantillon, pts.shape[0]), replace=False)
        d = distance_a(pts[idx], cibles[k], voxel_um)
        # ⚠ Le témoin est mesuré sur LES MÊMES cellules, pas sur toute la grille de départ :
        # comparer deux populations différentes ferait dire au témoin ce qu'on veut.
        d0 = distance_a(sur_place[m][idx], cibles[k], voxel_um)
        out.append(dict(tours=k, cellules=int(m.sum()), juges=int(len(idx)),
                        erreur_um=round(float(np.median(d)), 1),
                        erreur_p90_um=round(float(np.percentile(d, 90)), 1),
                        temoin_sur_place_um=round(float(np.median(d0)), 1)))
    return out


def mesurer(echantillon: int = 4000, depuis: int = 1) -> dict:
    """Le déroulement aveugle depuis une spire, jusqu'à perdre la feuille."""
    from le_pas_normal_atteint_la_spire import distance_a, grille  # noqa: PLC0415
    from les_wraps_publies import VOLUME, VOXEL_UM, wraps_du_fragment  # noqa: PLC0415

    if not WRAPS.is_file():
        raise SystemExit("écart entre spires non mesuré : lancer les_wraps_publies d'abord")
    ecart_um = json.loads(WRAPS.read_text())["resume"]["1"]["mediane_um"]
    pas_vx = ecart_um / VOXEL_UM

    grilles = {}
    for w in wraps_du_fragment():
        g = grille(w, VOLUME, VOXEL_UM)
        if g is not None:
            grilles[w["rang"]] = g
    if depuis not in grilles:
        raise SystemExit(f"spire {depuis} absente")
    a, ok = grilles[depuis]
    cibles = {r - depuis: grilles[r][0][grilles[r][1]]
              for r in sorted(grilles) if r > depuis}

    # ⚠⚠⚠ LE SEUL BIT DE SUPERVISION : le sens, choisi au PREMIER pas seulement. Le rechoisir à
    # chaque tour en regardant la cible serait souffler la route au dérouleur.
    from le_pas_normal_atteint_la_spire import essayer_le_pas, normales  # noqa: PLC0415

    n0, bon0 = normales(a, ok)
    essai = essayer_le_pas(a[bon0], n0[bon0], cibles[1], pas_vx, VOXEL_UM)
    sens = 1.0 if essai["retenu"] == "+" else -1.0

    marche = derouler(a, ok, cibles, pas_vx, VOXEL_UM, sens, echantillon)
    # ⚠⚠ « Perdu » est DÉFINI, pas ressenti : l'erreur dépasse une demi-épaisseur, donc le
    # dérouleur ne peut plus dire sur quelle feuille il est. C'est la même règle que la
    # coïncidence de `lemprise_des_spires`, et elle vient de la même mesure.
    demi = ecart_um / 2.0
    perdu = next((e["tours"] for e in marche if e["erreur_um"] > demi), None)
    return dict(volume=VOLUME, voxel_um=VOXEL_UM, depuis=depuis,
                ecart_lu_um=ecart_um, pas_en_voxels=round(pas_vx, 2),
                demi_epaisseur_um=round(demi, 2), sens_retenu=essai["retenu"],
                bits_de_supervision=1,
                tours_avant_de_perdre_la_feuille=perdu,
                tours_mesures=len(marche), marche=marche)


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok_: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok_:
            echecs += 1
        print(f"  {'✅' if ok_ else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    from le_pas_normal_atteint_la_spire import distance_a  # noqa: PLC0415

    uu, vv = np.meshgrid(np.arange(14.0), np.arange(12.0), indexing="ij")
    plan = np.stack([uu * 3.0, vv * 3.0, np.zeros(uu.shape)], axis=-1)
    ok = np.ones(plan.shape[:2], dtype=bool)

    a1, m1 = un_pas(plan, ok, 20.0, 1.0)
    v("un pas déplace la grille d'exactement le pas",
      bool(np.allclose(a1[m1][:, 2], 20.0)), str(a1[m1][0]))
    v("... et le sens négatif va dans l'autre sens",
      bool(np.allclose(un_pas(plan, ok, 20.0, -1.0)[0][m1][:, 2], -20.0)))
    v("... et la GRILLE est conservée, donc le pas suivant est calculable",
      a1.shape == plan.shape and un_pas(a1, m1, 20.0, 1.0)[1].any())
    # ⚠⚠ Le masque doit RÉTRÉCIR : une normale demande quatre voisins, donc un tour perd un
    # anneau. Un pas qui garderait tout ne calculerait pas de normale au bord.
    m2 = un_pas(a1, m1, 20.0, 1.0)[1]
    v("le masque rétrécit à chaque tour", int(m2.sum()) < int(m1.sum()),
      f"{int(m1.sum())} puis {int(m2.sum())}")

    # --- une pile de plans : le déroulement parfait ---
    cibles = {k: (plan + np.array([0.0, 0.0, 20.0 * k]))[ok].reshape(-1, 3) for k in (1, 2, 3)}
    marche = derouler(plan, ok, cibles, 20.0, 2.0, 1.0, 500)
    v("sur une pile parfaite, le déroulement ne dérive pas",
      all(e["erreur_um"] == 0.0 for e in marche), str([e["erreur_um"] for e in marche]))
    # ⚠⚠⚠ ET LE TÉMOIN DOIT S'ÉLOIGNER : rester sur place s'écarte d'une épaisseur par tour.
    # Sans lui, une erreur nulle ne prouverait pas qu'on a avancé — un dérouleur qui ne bouge
    # pas a lui aussi une erreur stable.
    v("... et le témoin sur place s'éloigne d'une épaisseur par tour",
      [e["temoin_sur_place_um"] for e in marche] == [40.0, 80.0, 120.0],
      str([e["temoin_sur_place_um"] for e in marche]))
    v("le compte de cellules jugées est rendu à côté de l'erreur",
      all(e["cellules"] > 0 and e["juges"] > 0 for e in marche))

    # ⚠ Un pas trop court doit DÉRIVER, et la dérive doit croître : sinon la mesure ne saurait
    # pas distinguer un bon dérouleur d'un mauvais.
    court = derouler(plan, ok, cibles, 14.0, 2.0, 1.0, 500)
    v("un pas trop court dérive, et la dérive croît",
      [e["erreur_um"] for e in court] == sorted(e["erreur_um"] for e in court)
      and court[-1]["erreur_um"] > court[0]["erreur_um"],
      str([e["erreur_um"] for e in court]))
    v("... et il reste meilleur que ne pas bouger",
      all(e["erreur_um"] < e["temoin_sur_place_um"] for e in court))

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--echantillon", type=int, default=4000)
    p.add_argument("--depuis", type=int, default=1)
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(a.echantillon, a.depuis)
    print(f"déroulement aveugle depuis la spire {r['depuis']} — pas {r['pas_en_voxels']} voxels, "
          f"sens « {r['sens_retenu']} » ({r['bits_de_supervision']} bit de supervision)\n")
    print(f"{'tours':>6} {'cellules':>10} {'erreur':>10} {'p90':>9} {'sur place':>11}")
    print("-" * 50)
    for e in r["marche"]:
        print(f"{e['tours']:>6} {e['cellules']:>10} {e['erreur_um']:>9.0f}µ "
              f"{e['erreur_p90_um']:>8.0f}µ {e['temoin_sur_place_um']:>10.0f}µ")
    seuil = r["demi_epaisseur_um"]
    perdu = r["tours_avant_de_perdre_la_feuille"]
    print(f"\ndemi-épaisseur : {seuil:.0f} µm")
    print(f"→ la feuille est perdue au tour {perdu}" if perdu
          else f"→ la feuille n'est JAMAIS perdue sur les {r['tours_mesures']} tours mesurés")
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
