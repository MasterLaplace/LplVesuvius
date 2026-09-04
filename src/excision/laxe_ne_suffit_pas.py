#!/usr/bin/env python3
"""L'axe et le pas ne suffisent PAS à dire sur quelle feuille on est — et de combien.

⚠⚠⚠ CE FICHIER EST UN RÉSULTAT NÉGATIF, ET IL EXISTE PARCE QUE L'ESPOIR ÉTAIT RAISONNABLE.
`78` a trouvé que cinq rouleaux publient leur axe. Un nombre d'enroulement se construit en
principe depuis **l'axe et le pas seuls** — le modèle d'Archimède, $w = (r - r_0)/\\lambda + \\theta/2\\pi$ — et un tel champ répondrait **partout**, ce qui est exactement la limite dure du
champ de `77` (il interpole entre spires connues et refuse au-delà).

**Mesuré : ça ne marche pas, et de très loin.**

    dispersion radiale d'UNE SEULE spire, autour de l'axe publié   44,5 feuilles
    erreur du modèle d'Archimède (axe + pas)                       11,4 feuilles
    erreur du champ bâti sur les spires (`77`)                      0,088 feuille

⭐⭐ **La forme des spires vaut donc un facteur ~130**, et c'est le vrai contenu de ce fichier :
il chiffre ce qu'un champ dérivé du volume devra **retrouver**, et il dit d'où vient la
difficulté. Un rouleau d'Herculanum est **écrasé** : le rayon d'une seule spire varie de
44 feuilles autour de l'axe, donc aucun modèle en $(r, \\theta)$ à section circulaire ne peut
séparer des feuilles distantes d'une.

⚠ Le modèle d'Archimède n'est pas *inutile* pour autant — il fait mieux que la dispersion brute
(11,4 contre 44,5), donc il capte bien la spirale. Il est simplement **quatre fois trop
grossier** pour la question posée, qui se joue à une feuille près.

⚠⚠ CE QUE CE FICHIER NE DIT PAS, et c'est la nuance qui compte pour la suite :

**Il ne condamne pas A2 bis, il en fixe le cahier des charges.** Un champ dérivé du volume n'a
pas à supposer une section circulaire : il peut suivre les feuilles là où elles sont. Ce que ce
fichier établit, c'est qu'un tel champ devra fournir **la forme**, et pas seulement l'axe et le
pas — donc que l'axe publié, à lui seul, ne débloque rien.

⚠ Une nuance de mesure à ne pas confondre. La dispersion de 44,5 feuilles est prise autour de
l'**axe publié** ; autour du centre **ajusté par tranche** elle vaut ~17 feuilles. C'est normal
et ce n'est pas une contradiction : l'ajustement minimise cette dispersion **par construction**.<<<<<<
Les deux axes restent équivalents pour la mesure **appariée** (`78`), qui ne lit jamais un rayon
absolu.

Usage :
    uv run python src/excision/laxe_ne_suffit_pas.py --verifier
    uv run python src/excision/laxe_ne_suffit_pas.py --json docs/mesures/laxe_ne_suffit_pas.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
MESURES = RACINE / "docs" / "mesures"
sys.path[:0] = [str(RACINE / "src" / "excision")]
import le_champ_denroulement as champ  # noqa: E402
from le_sens_des_indices import charger, _spires  # noqa: E402
from lombilic_publie import _centres_publies, charger_axe, voxel_de  # noqa: E402

PAS_UM = 154.1
"""L'écart inter-feuilles de `PHerc0139`, mesuré par `76`. ⚠ Pris de la mesure et non ajusté
ici : ajuster le pas sur les mêmes spires qu'on juge donnerait au modèle d'Archimède un
avantage qu'il n'aurait pas à l'usage, où le pas vient d'ailleurs (`winding-ruler`, `16`)."""

VOXEL_UM = 9.362


def _echantillons(rouleau: str) -> tuple[list, float]:
    """
    @brief Par (spire, tranche) : les rayons et angles autour de l'AXE PUBLIÉ.
    """
    dossiers = _spires(rouleau)
    nuages = {k: v for k, v in ((k, charger(d)) for k, d in dossiers.items()) if v}
    if len(nuages) < 5:
        raise SystemExit(f"moins de cinq spires en cache pour {rouleau}")
    bords_z, _, _ = champ._grille(nuages)
    charge = charger_axe(rouleau)
    if not charge:
        raise SystemExit(
            f"ombilic absent pour {rouleau}\n"
            "  le rapatrier :  uv run python src/excision/lombilic_publie.py --rapatrier")
    points, meta = charge
    centres = _centres_publies(points, (voxel_de(meta) or VOXEL_UM) / VOXEL_UM, bords_z)

    lignes = []
    for k, (x, y, z) in nuages.items():
        for i, (lo, hi) in enumerate(zip(bords_z, bords_z[1:])):
            m = (z >= lo) & (z < hi)
            if m.sum() < 200 or i not in centres:
                continue
            cx, cy = centres[i]
            lignes.append((k,
                           np.hypot(x[m] - cx, y[m] - cy),
                           np.arctan2(y[m] - cy, x[m] - cx)))
    return lignes, PAS_UM / VOXEL_UM


def mesurer(rouleau: str = "PHerc0139") -> dict:
    lignes, pas_vx = _echantillons(rouleau)

    # 1. ce qu'une seule spire couvre en rayon — la mesure de l'ecrasement
    dispersion = [float((np.percentile(r, 90) - np.percentile(r, 10)) / pas_vx)
                  for _, r, _ in lignes]

    # 2. le modele d'Archimede. ⚠ `r0` est ajuste GLOBALEMENT sur les spires : c'est le
    # meilleur cas pour le modele, donc son echec ne peut pas etre impute a un mauvais calage.
    meilleur = None
    for sens in (+1, -1):
        cales = [float(np.median(r - pas_vx * (k - sens * t / (2 * np.pi))))
                 for k, r, t in lignes]
        r0 = float(np.median(cales))
        erreurs = [float(np.median(np.abs((r - r0) / pas_vx + sens * t / (2 * np.pi) - k)))
                   for k, r, t in lignes]
        candidat = dict(sens=sens, r0_vx=r0,
                        erreur_mediane=float(np.median(erreurs)),
                        erreur_p90=float(np.percentile(erreurs, 90)))
        if meilleur is None or candidat["erreur_mediane"] < meilleur["erreur_mediane"]:
            meilleur = candidat

    # 3. le champ bati sur les spires, relu de SA mesure plutot que recalcule
    champ_json = MESURES / "le_champ_denroulement.json"
    erreur_champ = (json.loads(champ_json.read_text())["erreur_mediane"]
                    if champ_json.is_file() else None)

    return dict(
        rouleau=rouleau, pas_um=PAS_UM, voxel_um=VOXEL_UM,
        echantillons=len(lignes),
        dispersion_intra_spire_feuilles=float(np.median(dispersion)),
        archimede=meilleur,
        erreur_du_champ=erreur_champ,
        facteur_de_la_forme=(meilleur["erreur_mediane"] / erreur_champ)
        if erreur_champ else None,
    )


def _verifier(r: dict) -> int:
    echecs = 0
    comptees = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, comptees
        comptees += 1
        print(f"  {'ok  ' if ok else 'FAIL'}  {nom}" + (f"   [{detail}]" if detail else ""))
        if not ok:
            echecs += 1

    a = r["archimede"]
    print("le rouleau est écrasé — c'est la cause, et elle se mesure")
    v("une seule spire couvre des dizaines de feuilles en rayon",
      r["dispersion_intra_spire_feuilles"] > 10.0,
      f"{r['dispersion_intra_spire_feuilles']:.1f} feuilles (p10–p90)")

    print("l'axe et le pas ne suffisent pas — le résultat négatif")
    # ⚠ Ecrit dans le sens « ça ECHOUE ». Si un jour le modele passait sous une feuille, ce
    # controle tomberait, et ce serait une EXCELLENTE nouvelle a lire immediatement : A2 bis
    # serait resolu par trois lignes de trigonometrie. C'est pour ca qu'il est asserte ainsi.
    v("le modèle d'Archimède se trompe de plusieurs feuilles",
      a["erreur_mediane"] > 2.0,
      f"{a['erreur_mediane']:.2f} feuilles (p90 {a['erreur_p90']:.2f})")
    v("... mais il fait mieux que la dispersion brute, donc il capte la spirale",
      a["erreur_mediane"] < r["dispersion_intra_spire_feuilles"],
      f"{a['erreur_mediane']:.2f} contre {r['dispersion_intra_spire_feuilles']:.1f}")

    print("et la FORME des spires est ce qui fait la différence")
    if r["erreur_du_champ"] is not None:
        v("le champ bâti sur les spires est meilleur de deux ordres de grandeur",
          r["facteur_de_la_forme"] > 30.0,
          f"×{r['facteur_de_la_forme']:.0f} — {a['erreur_mediane']:.2f} contre "
          f"{r['erreur_du_champ']:.3f} feuille")
    else:
        print("  --    (mesure du champ absente — lancer le_champ_denroulement.py --json)")

    print()
    if echecs:
        print(f"  ECHEC ({echecs} failures)")
    else:
        print(f"  ALL PASS (0 failures, {comptees} checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--rouleau", default="PHerc0139")
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    args = p.parse_args()

    r = mesurer(args.rouleau)
    if not args.verifier or args.json:
        a = r["archimede"]
        print(f"{r['rouleau']} — {r['echantillons']} échantillons (spire × tranche), "
              f"axe publié, pas {r['pas_um']} µm\n")
        print(f"  1. dispersion radiale d'UNE spire   "
              f"{r['dispersion_intra_spire_feuilles']:8.2f} feuilles")
        print(f"  2. modèle d'Archimède (axe + pas)   "
              f"{a['erreur_mediane']:8.2f} feuilles  (p90 {a['erreur_p90']:.2f})")
        if r["erreur_du_champ"] is not None:
            print(f"  3. champ bâti sur les spires (`77`) "
                  f"{r['erreur_du_champ']:8.3f} feuille")
            print(f"\n  ce que la FORME vaut : ×{r['facteur_de_la_forme']:.0f}")

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nécrit : {args.json}")
    if args.verifier:
        print()
        return 1 if _verifier(r) else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
