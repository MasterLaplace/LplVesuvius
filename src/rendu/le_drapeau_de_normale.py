#!/usr/bin/env python3
"""`--flip-normals` renumérote-t-il la pile, ou en rend-il une AUTRE ?

⚠⚠ POURQUOI CE FICHIER EXISTE. `src/outils/sens_de_la_normale.sh` pose une bonne question —
*« la pile est-elle rendue du mauvais côté de la surface ? »* — et l'expérience qu'il monte
**ne peut pas y répondre**. Elle rend la même surface deux fois, avec et sans le drapeau,
puis compare l'écart médian entre le pic de matière et la **couche tracée**. Or cette
couche est prise au **milieu** de la pile (`--traced-layer $((COUCHES / 2))`, soit 20 de 41),
et renverser l'ordre envoie la couche @f$p@f$ sur @f$n-1-p@f$ :

$$|(n-1-p) - m| = |p - m| \\quad\\text{lorsque } m = \\frac{n-1}{2}$$

**L'écart est donc identique par construction, quel que soit le volume.** Sur les trois
verdicts que le script sait imprimer — « inverser divise l'écart », « le sens actuel est le
bon », « les deux se valent » — un seul est atteignable, et c'est celui qu'il a imprimé.

  ⭐ C'est le péché cardinal du dépôt sous un costume de plus : non pas une vérification
    incapable d'échouer, mais une expérience dont **l'arithmétique fixe la réponse avant
    qu'elle ne tourne**.

⭐⭐ **Et la question de fond a une réponse, plus forte que celle qui était visée.** Mesuré
ici : les deux rendus contiennent **exactement les mêmes images**, en ordre inverse. Le
drapeau **renumérote**, il ne redéplace pas la fenêtre — donc la pile est **centrée sur la
surface** et il n'existe aucun « mauvais côté » où elle aurait pu être. L'hypothèse « nos
maillages ont leurs normales à l'envers, donc la pile part du mauvais côté » n'est pas
« non confirmée » : elle est **inexprimable** avec ce drapeau.

⚠ Le contrôle qui sépare les deux lectures est **l'égalité octet pour octet**, pas une
ressemblance : deux rendus d'une même fenêtre à un demi-voxel près se ressembleraient
beaucoup et ne prouveraient rien. Ce qui est établi ici est une **identité**.

⚠ L'ancienne conclusion tenait sur **une seule fenêtre** (`windows: 1`) — le dépouillement à
`--step 200` sur une trace de 0,98 cm² n'en trouve qu'une. Un verdict à n = 1 sur une
grandeur qui est de toute façon constante ne mesure rien deux fois.

Usage :
    uv run python src/rendu/le_drapeau_de_normale.py --verifier
    uv run python src/rendu/le_drapeau_de_normale.py \\
        data/sens_normale/rendu_normal data/sens_normale/rendu_inverse \\
        --json docs/mesures/le_drapeau_de_normale.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]


def couches(dossier: Path) -> list[Path]:
    """Les `.tif` d'une pile, dans l'ordre de leur nom.

    ⚠ Trié sur le NOM et non sur l'ordre du système de fichiers : un `iterdir` rend ce que
    l'inode veut, donc deux machines compareraient deux appariements différents.
    """
    return sorted(dossier.glob("*.tif"))


def ecart_invariant_par_renversement(pic: int, couche_tracee: int, couches_n: int) -> bool:
    """
    @brief L'écart pic↔couche tracée survit-il au renversement de la pile ?

    ⚠⚠ C'est la démonstration que l'expérience du sens de la normale ne pouvait pas
    trancher : quand la couche tracée est au milieu, la réponse est **oui pour tout pic**.
    Le script qui compare les deux écarts compare donc un nombre à lui-même.
    """
    renverse = couches_n - 1 - pic
    return abs(renverse - couche_tracee) == abs(pic - couche_tracee)


def confronter(normale: Path, inverse: Path) -> dict:
    """Les deux piles, comparées dans les DEUX appariements possibles.

    ⚠ Les deux comptes sont rendus ensemble, et c'est ce qui rend le résultat lisible :
    « renversé, tout est identique » ne veut rien dire sans « à l'endroit, presque rien ne
    l'est ». Une pile constante satisferait le premier seul.
    """
    import numpy as np
    import tifffile

    a, b = couches(normale), couches(inverse)
    if not a or not b:
        raise SystemExit(f"pile vide : {normale} ({len(a)}) / {inverse} ({len(b)})")
    if len(a) != len(b):
        raise SystemExit(f"piles de tailles différentes : {len(a)} contre {len(b)}")
    n = len(a)
    renverse = aligne = 0
    for k in range(n):
        x = tifffile.imread(a[k])
        if np.array_equal(x, tifffile.imread(b[n - 1 - k])):
            renverse += 1
        if np.array_equal(x, tifffile.imread(b[k])):
            aligne += 1
    return {"couches": n, "identiques_apres_renversement": renverse,
            "identiques_sans_renversement": aligne,
            "le_drapeau_renumerote": renverse == n,
            "milieu": (n - 1) // 2}


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # --- l'arithmétique qui rend l'ancienne expérience vacuoue ---
    # ⚠⚠ La couche tracée au MILIEU : l'écart est invariant pour TOUT pic, donc les deux
    # rendus rendent le même nombre quoi qu'il y ait dans le volume.
    v("au milieu d'une pile impaire, l'écart survit au renversement pour tout pic",
      all(ecart_invariant_par_renversement(p, 20, 41) for p in range(41)))
    # ⭐ Le contrôle qui empêche ce constat d'être une tautologie : hors du milieu,
    # l'invariance TOMBE. Sans lui, « invariant » pourrait vouloir dire « la fonction rend
    # toujours vrai », ce qui ne dirait rien de l'expérience.
    v("... et hors du milieu elle tombe, donc l'invariance n'est pas une propriété du calcul",
      not all(ecart_invariant_par_renversement(p, 5, 41) for p in range(41)),
      "couche tracée 5 sur 41")
    v("... y compris sur une pile paire, où il n'y a pas de milieu exact",
      not all(ecart_invariant_par_renversement(p, 20, 40) for p in range(40)))

    # --- la confrontation des piles, sur des fixtures ---
    import shutil
    import tempfile

    import numpy as np
    import tifffile

    d = Path(tempfile.mkdtemp())

    def pile(nom: str, plans: list) -> Path:
        p = d / nom
        p.mkdir()
        for k, plan in enumerate(plans):
            tifffile.imwrite(p / f"{k:02d}.tif", np.asarray(plan, dtype=np.uint8))
        return p

    plans = [[[k, k + 1], [k + 2, k + 3]] for k in range(5)]
    a = pile("a", plans)
    b = pile("b", list(reversed(plans)))
    r = confronter(a, b)
    v("une pile renversée est reconnue comme telle", r["le_drapeau_renumerote"], str(r))
    # ⚠ Le second compte est ce qui distingue « renversée » de « constante » : sur une pile
    # dont tous les plans seraient égaux, les deux appariements vaudraient n, et « renversée »
    # serait vrai sans rien dire.
    v("... et l'appariement à l'endroit ne matche que le milieu",
      r["identiques_sans_renversement"] == 1, str(r))
    plate = pile("plat_a", [[[7, 7], [7, 7]]] * 5)
    plate2 = pile("plat_b", [[[7, 7], [7, 7]]] * 5)
    rp = confronter(plate, plate2)
    v("une pile CONSTANTE satisfait les deux appariements — donc le second compte est requis",
      rp["identiques_apres_renversement"] == 5 and rp["identiques_sans_renversement"] == 5)
    c = pile("c", [[[k, k], [k, k]] for k in (9, 8, 7, 1, 0)])
    v("deux piles sans rapport ne sont pas déclarées renversées",
      not confronter(a, c)["le_drapeau_renumerote"])
    v("des piles de tailles différentes sont REFUSÉES, pas tronquées",
      _leve(lambda: confronter(a, pile("court", plans[:3]))))
    v("une pile vide est refusée", _leve(lambda: confronter(a, pile("vide", []))))
    v("les couches sont prises dans l'ordre de leur NOM",
      [p.name for p in couches(a)] == sorted(p.name for p in couches(a)))

    shutil.rmtree(d, ignore_errors=True)

    # --- contre les VRAIS rendus, s'ils sont là ---
    reel_n = RACINE / "data" / "sens_normale" / "rendu_normal"
    reel_i = RACINE / "data" / "sens_normale" / "rendu_inverse"
    if reel_n.is_dir() and reel_i.is_dir():
        rr = confronter(reel_n, reel_i)
        v(f"le drapeau du concours RENUMÉROTE la pile ({rr['identiques_apres_renversement']}"
          f"/{rr['couches']})", rr["le_drapeau_renumerote"])
        v("... et il ne rend donc pas une autre fenêtre",
          rr["identiques_sans_renversement"] < rr["couches"],
          f"{rr['identiques_sans_renversement']} plan(s) inchangé(s) à l'endroit")
    else:
        print("  ⚠ rendus absents : la partie « vrai arbre » n'a pas tourné")

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def _leve(f) -> bool:
    try:
        f()
    except SystemExit:
        return True
    except Exception:  # noqa: BLE001
        return False
    return False


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("normale", type=Path, nargs="?")
    p.add_argument("inverse", type=Path, nargs="?")
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if not a.normale or not a.inverse:
        raise SystemExit("donner les deux piles, ou --verifier")
    r = confronter(a.normale, a.inverse)
    print(json.dumps(r, indent=2, ensure_ascii=False))
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
