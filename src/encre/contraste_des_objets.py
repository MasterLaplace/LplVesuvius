#!/usr/bin/env python3
"""Le contraste que le modèle reçoit, sur l'objet où il marche et sur celui où il échoue.

⚠⚠ Pourquoi ce fichier existe. [`58`](../../docs/archive/58_resolution_ou_rouleau.md) §8 donne le
patron du découpage de M1ter : *rendre l'objet qui marche semblable à celui qui ne marche
pas, une propriété à la fois*. `deux_objets.py` a chiffré l'écart des campagnes de scan —
**9 %** sur la résolution, **115 %** sur l'énergie du faisceau. Reste à savoir ce que cet
écart fait au **signal**, et c'est ça qui atteint le modèle.

⭐ Ce qui est mesuré ici est le **contraste dans le papyrus**, normalisé par le plafond du
type de chaque pile — la règle exacte que `infer_ink` applique, celle dont
[`60`](../../docs/archive/60_la_constante_qui_rendait_le_modele_muet.md) a montré qu'elle valait 257
fois le résultat quand on la rate. Comparer deux piles sans elle comparerait deux formats.

⚠⚠⚠ CE QUE ÇA N'EST PAS : le contraste de l'**encre**. On ne sait pas où est l'encre sur
`PHerc1447` — c'est la question même. Ce qui est mesuré est la dispersion de TOUT ce qui est
dans le papyrus, dont l'encre n'est qu'une part. Un contraste global effondré rend un
contraste d'encre effondré très probable ; l'inverse ne suit pas, et une pile riche en
texture de papyrus peut très bien n'avoir aucune encre.

⚠ Les deux piles ne viennent pas du même endroit : celle du témoin est un rendu `tifxyz`
`uint16`, celle de l'objet vient du volume de surface **publié** en `uint8`
(vérifié à la source : le `.zarray` déclare `|u1`, donc les huit bits sont ceux du dépôt et
non de notre pont). C'est une différence réelle entre les deux objets, pas un artefact de
notre chaîne, et elle fait partie de ce qu'on mesure plutôt que d'être corrigée.

Usage :
    uv run python src/encre/contraste_des_objets.py --verifier
    uv run python src/encre/contraste_des_objets.py \\
        --temoin data/layers/20230909121925 --echoue data/couches/PHerc1447_complet \\
        --json docs/mesures/contraste_des_objets.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]

COUCHES_ECHANTILLONNEES = 8
"""Couches lues par pile. ⚠ Un échantillon et non la pile entière : une pile `uint16` de
11591 × 3882 sur 26 couches pèse 2,3 Gio, et le contraste ne dépend pas de la profondeur
au point qu'il faille tout lire. Le nombre est un PARAMÈTRE, et il voyage dans le résultat."""

COTE_FENETRE = 1024
"""Côté de la fenêtre lue au centre de chaque couche. ⚠ Au centre, parce qu'un bord de rendu
porte du vide et ferait passer une pile pour moins pleine qu'elle n'est."""


def normaliser(bloc: np.ndarray) -> np.ndarray:
    """La pile ramenée dans [0,1] par le plafond de SON type, jamais par une constante.

    ⚠⚠ C'est la règle de `infer_ink.load_layer_stack`, et la seule qui rende deux piles de
    types différents comparables. `60` a mesuré ce que coûte de s'en écarter : un facteur 257.
    """
    if not np.issubdtype(bloc.dtype, np.integer):
        raise ValueError(f"type non entier : {bloc.dtype}")
    return bloc.astype(np.float32) / float(np.iinfo(bloc.dtype).max)


def contraste(valeurs: np.ndarray) -> dict:
    """Les mesures de dispersion d'un échantillon déjà normalisé et déjà masqué.

    ⚠ Trois mesures et non une : l'écart-type est sensible aux valeurs aberrantes, l'écart
    interquartile ne l'est pas, et `p95 − p50` est celui que `temoin_negatif.py` emploie déjà.
    Publier une seule d'entre elles laisserait le lecteur sans moyen de voir si le résultat
    tient à la mesure choisie.
    """
    if valeurs.size == 0:
        return {"n": 0, "sigma": None, "interquartile": None, "p95_moins_p50": None,
                "mediane": None}
    p05, p25, p50, p75, p95 = np.percentile(valeurs, [5, 25, 50, 75, 95])
    return {"n": int(valeurs.size), "sigma": float(valeurs.std()),
            "interquartile": float(p75 - p25), "p95_moins_p50": float(p95 - p50),
            "mediane": float(p50), "p05": float(p05), "p95": float(p95)}


def fenetre_centrale(a: np.ndarray, cote: int) -> np.ndarray:
    """Le carré de `cote` au centre d'une couche, ou la couche entière si elle est plus petite."""
    h, w = a.shape
    if h <= cote and w <= cote:
        return a
    top, left = max(0, (h - cote) // 2), max(0, (w - cote) // 2)
    return a[top:top + min(cote, h), left:left + min(cote, w)]


def mesurer_pile(dossier: Path, couches: int = COUCHES_ECHANTILLONNEES,
                 cote: int = COTE_FENETRE) -> dict:
    """Le contraste dans le papyrus d'une pile, sur un échantillon de ses couches."""
    import tifffile

    fichiers = sorted(dossier.glob("*.tif"))
    if not fichiers:
        raise ValueError(f"aucune couche dans {dossier}")
    pas = max(1, len(fichiers) // couches)
    choisies = fichiers[::pas][:couches]
    morceaux, dtype = [], None
    for f in choisies:
        a = fenetre_centrale(tifffile.imread(str(f)), cote)
        if dtype is not None and a.dtype != dtype:
            raise ValueError(f"{f.name} en {a.dtype} alors que la pile est en {dtype}")
        dtype = a.dtype
        n = normaliser(a)
        # ⚠ Le masque est « non nul », comme `masque_papyrus` : le fond d'un rendu est
        # exactement zéro, et le compter écraserait la dispersion vers le bas.
        morceaux.append(n[n > 0])
    valeurs = np.concatenate(morceaux) if morceaux else np.array([], dtype=np.float32)
    return {"pile": str(dossier), "couches_lues": len(choisies),
            "couches_totales": len(fichiers), "dtype": str(dtype), "cote": cote,
            "part_papyrus": float(valeurs.size / (len(choisies) * cote * cote))
            if choisies else 0.0,
            **contraste(valeurs)}


def comparer(temoin: dict, echoue: dict) -> dict:
    """Le rapport des contrastes, sur les trois mesures, dans le sens témoin / échoue."""
    rapports = {}
    for cle in ("sigma", "interquartile", "p95_moins_p50"):
        a, b = temoin.get(cle), echoue.get(cle)
        rapports[cle] = round(a / b, 3) if a and b else None
    return {"temoin": temoin, "echoue": echoue, "rapports_temoin_sur_echoue": rapports}


def verifier() -> int:
    """Auto-test HORS LIGNE : la normalisation, le masque et les trois mesures."""
    echecs = controles = 0

    def v(nom: str, ok: bool) -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}")

    # --- LA NORMALISATION, la regle de `60` --------------------------------------------
    huit = np.array([[0, 128, 255]], dtype=np.uint8)
    seize = np.array([[0, 32896, 65535]], dtype=np.uint16)
    v("un uint8 est divise par 255", abs(float(normaliser(huit).max()) - 1.0) < 1e-6)
    v("un uint16 est divise par 65535", abs(float(normaliser(seize).max()) - 1.0) < 1e-6)
    # ⚠⚠ Le controle qui compte : la MEME image dans les deux types se normalise pareil.
    v("la meme image en uint8 et uint16 arrive au meme endroit",
      abs(float(normaliser(huit).mean()) - float(normaliser(seize).mean())) < 1e-3)
    try:
        normaliser(np.zeros((2, 2), dtype=np.float32))
        v("un type non entier est refuse", False)
    except ValueError:
        v("un type non entier est refuse", True)

    # --- LES TROIS MESURES --------------------------------------------------------------
    plat = np.full(1000, 0.5, dtype=np.float32)
    c = contraste(plat)
    v("une plage plate a un contraste nul", c["sigma"] == 0.0 and c["interquartile"] == 0.0)
    varie = np.linspace(0.0, 1.0, 1001, dtype=np.float32)
    d = contraste(varie)
    v("une plage etalee a un contraste positif", d["sigma"] > 0.2)
    v("l'interquartile d'une uniforme vaut la moitie",
      abs(d["interquartile"] - 0.5) < 0.01)
    # ⚠ Trois mesures et non une : elles ne bougent pas ensemble sur une distribution a
    # valeurs aberrantes, et c'est justement pourquoi on les publie toutes les trois.
    sale = np.concatenate([np.full(999, 0.5, dtype=np.float32),
                           np.array([1.0], dtype=np.float32)])
    e = contraste(sale)
    v("une seule valeur aberrante bouge le sigma", e["sigma"] > 0.0)
    v("... et ne bouge pas l'interquartile", e["interquartile"] == 0.0)
    v("un echantillon vide le dit plutot que de lever", contraste(np.array([]))["n"] == 0)

    # --- LA FENETRE CENTRALE -------------------------------------------------------------
    grand = np.arange(100 * 100, dtype=np.uint8).reshape(100, 100)
    v("la fenetre centrale a le cote demande", fenetre_centrale(grand, 10).shape == (10, 10))
    v("... et elle est bien au centre",
      int(fenetre_centrale(grand, 2)[0, 0]) == int(grand[49, 49]))
    v("une couche plus petite que la fenetre est rendue entiere",
      fenetre_centrale(grand, 500).shape == (100, 100))

    # --- LE RAPPORT -----------------------------------------------------------------------
    r = comparer({"sigma": 0.2, "interquartile": 0.1, "p95_moins_p50": 0.3},
                 {"sigma": 0.1, "interquartile": 0.05, "p95_moins_p50": 0.1})
    v("le rapport va du temoin vers l'objet qui echoue",
      r["rapports_temoin_sur_echoue"]["sigma"] == 2.0)
    v("une mesure absente rend None",
      comparer({"sigma": 0.2}, {})["rapports_temoin_sur_echoue"]["sigma"] is None)

    print(f"\n{'ALL PASS' if not echecs else 'ECHEC'} "
          f"({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--temoin", type=Path)
    ap.add_argument("--echoue", type=Path)
    ap.add_argument("--couches", type=int, default=COUCHES_ECHANTILLONNEES)
    ap.add_argument("--cote", type=int, default=COTE_FENETRE)
    ap.add_argument("--json", type=Path)
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()
    if not (a.temoin and a.echoue):
        ap.error("donner --temoin et --echoue, ou --verifier")

    d = comparer(mesurer_pile(a.temoin, a.couches, a.cote),
                 mesurer_pile(a.echoue, a.couches, a.cote))
    for role in ("temoin", "echoue"):
        l = d[role]
        print(f"  {role:8s} {Path(l['pile']).name:26s} {l['dtype']:>7}  "
              f"papyrus {100 * l['part_papyrus']:5.1f} %  "
              f"σ {l['sigma']:.4f}  IQR {l['interquartile']:.4f}  "
              f"p95−p50 {l['p95_moins_p50']:.4f}")
    print("\n  rapport témoin / échoue :", {k: v for k, v in
                                            d["rapports_temoin_sur_echoue"].items()})
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
        print(f"→ {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
