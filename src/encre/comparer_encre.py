#!/usr/bin/env python3
"""Un detecteur d'encre a-t-il RENDU quelque chose ? -- juge par un temoin ou il marche.

⚠⚠ Pourquoi ce fichier existe. Une sortie de detecteur d'encre ne vient avec aucune echelle :
un tableau de nombres autour de -1,1 peut etre « pas d'encre ici » ou « le modele ne
s'applique pas a cette donnee », et rien dans le tableau ne les separe. La seule facon de
lire un « rien » est de le mettre a cote d'un « quelque chose » PRODUIT PAR LE MEME MODELE.

⭐ La grandeur qui tranche est l'ECART-TYPE de la sortie, pas sa moyenne. Un modele qui ne
s'accroche a rien rend une constante ; sa mediane peut tomber n'importe ou, mais son sigma
s'effondre. Sur le temoin positif de ce depot -- le segment de Scroll 1 ou le modele atteint
AUC 0,925 -- sigma vaut 0,771 ; sur un rendu de rouleau du prix a 8,64 µm, 0,017.

⚠ Ce que ca n'etablit PAS, et qu'il faut dire a chaque usage : un sigma effondre ne prouve
pas qu'il n'y a pas d'encre a cet endroit. Il prouve que **ce modele-la n'y voit rien**, ce
qui peut venir de la resolution, du rouleau, de la surface, ou d'un papyrus reellement
vierge. Separer ces causes demande d'autres mesures.

⚠ Les pixels non couverts sont ecartes (`-inf` ou sentinelle tres negative) : les compter
melangerait « hors surface » et « pas d'encre », et ferait varier sigma avec la forme du
segment plutot qu'avec son contenu.

Usage :
    uv run python src/encre/comparer_encre.py CIBLE.npy --temoin TEMOIN.npy \\
        --nom-cible "PHerc1447 (prix, 8,64 µm)" --nom-temoin "Scroll 1 (AUC 0,925)" \\
        --json docs/m1ter_encre_a_9um.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SENTINELLE = -9e9


def statistiques(chemin: Path) -> dict:
    import numpy as np

    x = np.load(chemin)
    v = x[np.isfinite(x)]
    v = v[v > SENTINELLE]
    if v.size == 0:
        raise ValueError(f"{chemin} : aucun pixel couvert")
    return {"fichier": chemin.name, "n": int(v.size),
            "min": float(v.min()), "median": float(np.median(v)),
            "max": float(v.max()), "etendue": float(v.max() - v.min()),
            "sigma": float(v.std())}


def verifier() -> int:
    """Temoin hors ligne : sigma separe une constante d'un signal, la mediane non."""
    import tempfile

    import numpy as np

    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        rng = np.random.default_rng(0)
        # ⭐ Deux sorties de MEME mediane : l'une constante, l'autre structuree. Si
        # l'instrument regardait la mediane, il les confondrait.
        plat = np.full((200, 200), -1.1, dtype=np.float32) + rng.normal(0, 0.01, (200, 200))
        vif = np.full((200, 200), -1.1, dtype=np.float32) + rng.normal(0, 0.8, (200, 200))
        # Des pixels non couverts, qui ne doivent pas entrer dans sigma.
        vif_troue = vif.copy()
        vif_troue[:50, :] = SENTINELLE * 10
        np.save(d / "plat.npy", plat)
        np.save(d / "vif.npy", vif)
        np.save(d / "vif_troue.npy", vif_troue)

        sp, sv, st = (statistiques(d / f) for f in ("plat.npy", "vif.npy", "vif_troue.npy"))
        v("les médianes sont proches", abs(sp["median"] - sv["median"]) < 0.05,
          f"{sp['median']} vs {sv['median']}")
        v("mais sigma les sépare d'un facteur > 20", sv["sigma"] / sp["sigma"] > 20,
          f"{sv['sigma'] / sp['sigma']:.1f}")
        v("les pixels non couverts sont écartés", st["n"] == 150 * 200, str(st["n"]))
        v("... et ne changent pas sigma", abs(st["sigma"] - sv["sigma"]) < 0.05,
          f"{st['sigma']} vs {sv['sigma']}")
        v("un fichier tout non couvert est refusé, pas rendu à zéro",
          _refuse(d, np.full((10, 10), SENTINELLE * 10, dtype=np.float32)))

    if echecs:
        print(f"\nECHEC ({echecs} failures, {controles} checks)")
        return 1
    print(f"ALL PASS ({echecs} failures, {controles} checks)")
    return 0


def _refuse(d: Path, tableau) -> bool:
    import numpy as np
    np.save(d / "vide.npy", tableau)
    try:
        statistiques(d / "vide.npy")
    except ValueError:
        return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cible", nargs="?", type=Path)
    ap.add_argument("--temoin", type=Path)
    ap.add_argument("--nom-cible", default="cible")
    ap.add_argument("--nom-temoin", default="témoin positif")
    ap.add_argument("--question", default="")
    ap.add_argument("--contexte", default="{}",
                    help="JSON de contexte à joindre (modèle, voxel, fenêtre…)")
    ap.add_argument("--json")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()
    if not a.cible or not a.temoin:
        ap.error("donner une cible et un --temoin, ou --verifier")

    c, t = statistiques(a.cible), statistiques(a.temoin)
    rapport = t["sigma"] / c["sigma"] if c["sigma"] else float("inf")

    print(f"{'':<32} {'n':>10} {'min':>8} {'méd':>8} {'max':>8} {'étendue':>8} {'σ':>9}")
    for nom, s in ((a.nom_temoin, t), (a.nom_cible, c)):
        print(f"{nom:<32} {s['n']:>10} {s['min']:>+8.3f} {s['median']:>+8.3f} "
              f"{s['max']:>+8.3f} {s['etendue']:>8.3f} {s['sigma']:>9.4f}")
    print(f"\n  σ du témoin / σ de la cible : **{rapport:.1f}×**")
    if rapport > 10:
        print("  ⚠⚠ Le modèle sort une CONSTANTE sur la cible. Ce n'est pas « peu d'encre »,")
        print("     c'est aucun signal — et ça ne dit pas pourquoi.")
    elif rapport > 3:
        print("  ⚠ Signal nettement plus faible que sur le témoin, sans être nul.")
    else:
        print("  ✅ La cible a une dynamique comparable au témoin.")

    if a.json:
        Path(a.json).write_text(json.dumps({
            "question": a.question, "contexte": json.loads(a.contexte),
            "temoin_positif": {"nom": a.nom_temoin, **t},
            "cible": {"nom": a.nom_cible, **c},
            "rapport_sigma": rapport,
        }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"\n  écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
