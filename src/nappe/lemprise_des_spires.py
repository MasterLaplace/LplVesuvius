#!/usr/bin/env python3
"""Les treize spires et le segment de C1 couvrent-ils la même surface, ou des surfaces voisines ?

⚠⚠ POURQUOI CE FICHIER EXISTE. `les_wraps_publies` a établi que treize surfaces publiées de
`PHerc0500P2` sont des tours consécutifs, séparés de **135,5 µm**. Reste la question que cette
mesure a laissée ouverte, et dont tout C1 dépend : **le segment `500P2_front`, sur lequel toute la
colonne C a été bâtie, est-il l'une de ces spires, un morceau de l'une d'elles, ou une région
autre ?**

⭐⭐ Les trois réponses n'ouvrent pas les mêmes portes. S'il **est** une spire, C1 hérite d'un
voisinage connu de part et d'autre. S'il en **chevauche** plusieurs, c'est un morceau recousu.
S'il est **ailleurs**, les treize spires sont une seconde région du fragment et le corpus double.

⚠⚠⚠ LE SEUIL EST DÉRIVÉ, PAS CHOISI : deux surfaces distantes de moins d'une **demi**-épaisseur
de feuille sont la même feuille, puisqu'une feuille voisine est à une épaisseur entière. La
demi-épaisseur vient de l'écart mesuré entre spires consécutives — **lu** dans
`les_wraps_publies.json`, jamais retapé ici.

Usage :
    uv run python src/nappe/lemprise_des_spires.py --verifier
    uv run python src/nappe/lemprise_des_spires.py --json docs/mesures/lemprise_des_spires.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "commun"))
sys.path.insert(0, str(RACINE / "src" / "encre"))
sys.path.insert(0, str(RACINE / "src" / "nappe"))

WRAPS = RACINE / "docs" / "mesures" / "les_wraps_publies.json"
SEGMENT_C1 = dict(nom="20250628074500-500P2_front", rang=0,
                  horodatage="20250628074500")


def demi_epaisseur_um(chemin: Path = WRAPS) -> float | None:
    """La moitié de l'écart mesuré entre spires consécutives — LUE, jamais retapée.

    ⚠⚠ C'est ce qui rend le seuil dérivé : une feuille voisine est à une épaisseur entière, donc
    tout ce qui est à moins d'une demi-épaisseur est la **même** feuille. Écrire 68 µm ici serait
    un nombre choisi pour que le résultat du jour passe.
    """
    if not chemin.is_file():
        return None
    d = json.loads(chemin.read_text())
    e = d.get("resume", {}).get("1", {}).get("mediane_um")
    return None if e is None else e / 2.0


def recouvrement(a: np.ndarray, b: np.ndarray, seuil_um: float,
                 voxel_um: float = 2.215) -> float:
    """La part des points de `a` qui sont à moins de `seuil_um` de la surface `b`.

    ⚠ Asymétrique par construction, et c'est voulu : « le segment est-il contenu dans les
    spires » et « les spires sont-elles contenues dans le segment » sont deux questions
    différentes, et les confondre ferait passer un morceau pour un tout.
    """
    from scipy.spatial import cKDTree  # noqa: PLC0415

    if a.size == 0 or b.size == 0:
        return 0.0
    d = cKDTree(b).query(a, k=1)[0] * voxel_um
    return float((d <= seuil_um).mean())


def distances(a: np.ndarray, b: np.ndarray, voxel_um: float = 2.215) -> dict:
    """La distribution des distances de `a` à `b`, en micromètres.

    ⚠⚠⚠ POURQUOI ÇA ACCOMPAGNE OBLIGATOIREMENT UNE PART DE RECOUVREMENT. Une part de **0 %** ne
    dit pas si les deux surfaces se manquent de soixante-dix micromètres ou de sept millimètres —
    et les deux lectures n'ouvrent pas les mêmes portes : la première est une feuille voisine, la
    seconde une autre région. Publier un zéro sans son échelle, c'est publier un verdict sans sa
    mesure.
    """
    from scipy.spatial import cKDTree  # noqa: PLC0415

    if a.size == 0 or b.size == 0:
        return {}
    d = cKDTree(b).query(a, k=1)[0] * voxel_um
    return dict(minimum_um=round(float(d.min()), 1),
                p10_um=round(float(np.percentile(d, 10)), 1),
                mediane_um=round(float(np.median(d)), 1),
                p90_um=round(float(np.percentile(d, 90)), 1))


def mesurer(pas: int = 1) -> dict:
    """Le segment de C1 contre chacune des treize spires, et contre leur union."""
    from les_wraps_publies import VOLUME, VOXEL_UM, surface, wraps_du_fragment  # noqa: PLC0415

    seuil = demi_epaisseur_um()
    if seuil is None:
        raise SystemExit("écart entre spires non mesuré : lancer les_wraps_publies d'abord")

    sc1 = surface(SEGMENT_C1, VOLUME, pas=pas)
    if sc1 is None or sc1.size == 0:
        raise SystemExit("surface du segment de C1 absente")

    lignes, surfaces = [], []
    for w in wraps_du_fragment():
        s = surface(w, VOLUME, pas=pas)
        if s is None or s.size == 0:
            continue
        surfaces.append(s)
        lignes.append(dict(rang=w["rang"], points=int(s.shape[0]),
                           part_du_segment_sur_la_spire=round(
                               recouvrement(sc1, s, seuil, VOXEL_UM), 4),
                           part_de_la_spire_sur_le_segment=round(
                               recouvrement(s, sc1, seuil, VOXEL_UM), 4)))
    # ⚠⚠⚠ LA CALIBRATION REMPLACE LES SEUILS CHOISIS, et c'est la donnée qui la fournit. Une
    # spire couvre une AUTRE spire d'une certaine part — c'est le « mode feuilles différentes »
    # de cette mesure — et elle se couvre elle-même à 1 par identité. Le plafond entre spires
    # distinctes est donc la barre qu'il faut franchir pour dire « c'est la même feuille », et
    # personne ne l'a choisie : elle est mesurée sur les treize.
    entre = []
    for i, a_ in enumerate(surfaces):
        for j, b_ in enumerate(surfaces):
            if i != j:
                entre.append(recouvrement(a_, b_, seuil, VOXEL_UM))
    plafond = max(entre) if entre else 0.0

    union = np.vstack(surfaces) if surfaces else np.zeros((0, 3))
    part_union = recouvrement(sc1, union, seuil, VOXEL_UM)
    d_vers = distances(sc1, union, VOXEL_UM)
    d_depuis = distances(union, sc1, VOXEL_UM)
    meilleure = max(lignes, key=lambda e: e["part_du_segment_sur_la_spire"]) if lignes else None

    # ⚠⚠⚠ LE VERDICT EST NOMMÉ ET SA BARRE EST MESURÉE. Ma première version comparait à 0,8 et
    # 0,2 — deux nombres choisis pour que la lecture du jour passe, c'est-à-dire le piège que ce
    # dépôt attrape en boucle. La barre est le **plafond entre spires distinctes** : franchir ce
    # que deux feuilles différentes atteignent au mieux, c'est être la même feuille.
    m_ = meilleure["part_du_segment_sur_la_spire"] if meilleure else 0.0
    if m_ > plafond:
        verdict = ("le segment de C1 EST une des spires : il colle mieux à l'une d'elles "
                   "que deux spires distinctes ne se collent entre elles")
    elif part_union > plafond:
        verdict = ("le segment de C1 est RECOUSU de plusieurs spires : aucune seule ne le "
                   "couvre, leur union dépasse le plafond entre spires")
    else:
        verdict = ("le segment de C1 est AILLEURS : il ne colle pas mieux aux spires que deux "
                   "spires distinctes ne collent entre elles")

    # ⚠ La trace du segment est publiée pour la figure, au même format et au même compte que
    # celles des spires : deux nuages tracés à deux densités se compareraient à l'œil sur leur
    # densité et non sur leur place.
    k = max(1, sc1.shape[0] // 400)
    trace = [[round(float(x), 1), round(float(z), 1)] for x, _, z in sc1[::k][:400]]
    return dict(volume=VOLUME, voxel_um=VOXEL_UM, pas=pas, trace_xz_du_segment=trace,
                seuil_um=round(seuil, 2),
                seuil_derive_de="la moitié de l'écart médian entre spires consécutives",
                segment_de_c1=SEGMENT_C1["nom"], points_du_segment=int(sc1.shape[0]),
                spires=lignes,
                part_du_segment_sur_l_union=round(part_union, 4),
                distance_du_segment_a_l_union=d_vers,
                distance_de_l_union_au_segment=d_depuis,
                # ⚠ L'écart minimal EXPRIMÉ EN FEUILLES : « 2 134 µm » est un nombre, « seize
                # épaisseurs » est une position dans le rouleau, et c'est celle-là qui décide.
                ecart_minimal_en_feuilles=(
                    round(d_vers["minimum_um"] / (seuil * 2), 1) if d_vers else None),
                plafond_entre_spires=round(plafond, 4),
                plafond_derive_de="la part maximale d'une spire couverte par une AUTRE spire",
                calibration_entre_spires=dict(
                    paires=len(entre),
                    mediane=round(float(np.median(entre)), 4) if entre else None,
                    p90=round(float(np.percentile(entre, 90)), 4) if entre else None,
                    maximum=round(plafond, 4)),
                meilleure_spire=meilleure, verdict=verdict)


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    d = demi_epaisseur_um()
    v("le seuil est LU dans la mesure des spires", d is not None and d > 0, str(d))
    if d is not None:
        e = json.loads(WRAPS.read_text())["resume"]["1"]["mediane_um"]
        v("... et c'est bien la moitié de l'écart mesuré", abs(d * 2 - e) < 1e-9,
          f"{d} pour {e}")
    v("un fichier absent rend None plutôt qu'un nombre inventé",
      demi_epaisseur_um(RACINE / "docs" / "mesures" / "nexiste-pas.json") is None)

    xx, yy = np.meshgrid(np.arange(0, 40, 2.0), np.arange(0, 40, 2.0))
    plat = np.stack([xx.ravel(), yy.ravel(), np.zeros(xx.size)], axis=1)
    v("une surface est entièrement sur elle-même",
      recouvrement(plat, plat, 10.0, 2.0) == 1.0)
    # ⚠⚠⚠ LES DEUX CAS QUE LE SEUIL DOIT SÉPARER : une copie décalée d'un tiers d'épaisseur est
    # la MÊME feuille, une voisine à une épaisseur entière ne l'est pas. Sans les deux, le seuil
    # pourrait tout accepter ou tout refuser sans que rien ne le dise.
    meme = plat + np.array([0.0, 0.0, 45.0 / 3.0 / 2.0])
    voisine = plat + np.array([0.0, 0.0, 45.0 / 2.0])
    v("une copie à un tiers d'épaisseur compte comme la même feuille",
      recouvrement(plat, meme, 45.0 / 2.0, 2.0) == 1.0)
    v("... et une voisine à une épaisseur entière ne compte pas",
      recouvrement(plat, voisine, 45.0 / 2.0, 2.0) == 0.0)
    # ⚠ L'asymétrie est réelle et voulue : un morceau est entièrement dans le tout, pas l'inverse.
    morceau = plat[:40]
    v("un morceau est contenu dans le tout", recouvrement(morceau, plat, 5.0, 2.0) == 1.0)
    v("... mais le tout n'est pas contenu dans le morceau",
      recouvrement(plat, morceau, 5.0, 2.0) < 0.5,
      str(round(recouvrement(plat, morceau, 5.0, 2.0), 3)))
    v("une surface vide ne recouvre rien", recouvrement(np.zeros((0, 3)), plat, 5.0) == 0.0)

    # ⚠⚠⚠ UNE PART NULLE DOIT VENIR AVEC SON ÉCHELLE. Deux surfaces qui se manquent de peu et
    # deux qui se manquent de beaucoup rendent le même 0 % ; seule la distance les sépare, et
    # c'est elle qui distingue une feuille voisine d'une autre région.
    proche = plat + np.array([0.0, 0.0, 30.0])
    loin = plat + np.array([0.0, 0.0, 3000.0])
    v("deux surfaces qui se manquent rendent la même part nulle",
      recouvrement(plat, proche, 45.0 / 2.0, 2.0) == recouvrement(plat, loin, 45.0 / 2.0, 2.0)
      == 0.0)
    v("... mais leurs distances les séparent",
      distances(plat, proche, 2.0)["minimum_um"] < distances(plat, loin, 2.0)["minimum_um"],
      f"{distances(plat, proche, 2.0)['minimum_um']} contre "
      f"{distances(plat, loin, 2.0)['minimum_um']}")
    v("... et la distance est exacte", distances(plat, proche, 2.0)["minimum_um"] == 60.0)
    v("une surface vide ne rend aucune distance", distances(np.zeros((0, 3)), plat) == {})

    # ⚠⚠⚠ LA CALIBRATION, DANS LES DEUX SENS. Sur une pile de feuilles séparées d'une épaisseur,
    # le plafond entre feuilles DISTINCTES doit être bas ; une copie de l'une d'elles doit le
    # dépasser. Sans les deux, la barre pourrait être franchie par tout ou par rien.
    pile = [plat + np.array([0.0, 0.0, k * 45.0]) for k in range(4)]
    entre = [recouvrement(a_, b_, 45.0 / 2.0, 2.0)
             for i, a_ in enumerate(pile) for j, b_ in enumerate(pile) if i != j]
    v("le plafond entre feuilles distinctes est bas", max(entre) < 0.01, str(max(entre)))
    copie = pile[1] + np.array([0.0, 0.0, 45.0 / 4.0])
    v("... et une copie décalée d'un quart d'épaisseur le dépasse",
      recouvrement(copie, pile[1], 45.0 / 2.0, 2.0) > max(entre),
      f"{recouvrement(copie, pile[1], 45.0 / 2.0, 2.0)} contre {max(entre)}")

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--pas", type=int, default=1)
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(a.pas)
    print(f"segment de C1 : {r['segment_de_c1']}  ({r['points_du_segment']} points)")
    print(f"seuil : {r['seuil_um']} µm — {r['seuil_derive_de']}\n")
    print(f"{'spire':>6} {'points':>9} {'segment sur spire':>19} {'spire sur segment':>19}")
    print("-" * 58)
    for e in r["spires"]:
        print(f"{e['rang']:>6} {e['points']:>9} "
              f"{e['part_du_segment_sur_la_spire'] * 100:>18.1f}% "
              f"{e['part_de_la_spire_sur_le_segment'] * 100:>18.1f}%")
    print(f"\nsur l'UNION des spires : {r['part_du_segment_sur_l_union'] * 100:.1f} %")
    dv = r["distance_du_segment_a_l_union"]
    print(f"distance segment → union : min {dv['minimum_um']:.0f} µm, médiane "
          f"{dv['mediane_um']:.0f} µm  —  soit {r['ecart_minimal_en_feuilles']} feuilles au plus près")
    print(f"plafond entre spires distinctes : {r['plafond_entre_spires'] * 100:.2f} %")
    print(f"\n→ {r['verdict']}")
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
