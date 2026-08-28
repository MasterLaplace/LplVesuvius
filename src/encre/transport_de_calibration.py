#!/usr/bin/env python3
"""Les grandeurs typographiques prédisent-elles la qualité LÀ OÙ ON PEUT ENCORE VÉRIFIER ?

⚠⚠ POURQUOI CE FICHIER EXISTE. `45` (M7) a mesuré quatre grandeurs sur **190 cartes d'encre
publiées** et trouvé que deux d'entre elles retrouvent le classement du contraste d'encre
publié — épaisseur de trait **AUC 0,857**, netteté du pic **0,753**. Son résidu, resté ouvert
depuis, demande *« le transport vers une région sans vérité du même objet »*, et `57` §3 l'a
déclaré **impossible sur ce couple** : il faut un autre objet.

⭐⭐ Les fragments SONT cet autre objet, et ils ont mieux qu'une région sans vérité : ils ont
une vérité **partout**. Ce fichier fait donc l'étape que le résidu sautait — **valider** le
transport avant de l'appliquer en aveugle. Appliquer un prédicteur non validé là où on ne peut
plus le contredire est précisément ce qui produit un chiffre auquel personne ne peut répondre.

  ⭐ La question exacte : une grandeur mesurée sur NOTRE carte, sans jamais regarder les
     étiquettes, prédit-elle l'AUC de la tuile contre ces étiquettes ?

⚠⚠ ET LA LIMITE, chiffrée par [`64`](../../docs/64_la_dispersion_netait_pas_un_effet.md) :
la grandeur à prédire est elle-même bruitée — l'AUC d'une tuile a un écart-type de **0,2243**
d'une tuile à l'autre. Une corrélation mesurée ici est donc **atténuée** par le bruit de ce
qu'elle prédit, et 23 tuiles ne sont pas beaucoup. Le résultat se lit avec son intervalle,
jamais comme un verdict.

⚠ L'interligne n'est PAS mesuré ici, et c'est un refus, pas un oubli : il demande assez de
lignes pour qu'une périodicité existe, et une tuile de 256 px n'en porte pas. Le mesurer à
cette taille rendrait un nombre qui ne veut rien dire, ce qui est pire que pas de nombre.

Usage :
    uv run python src/encre/transport_de_calibration.py --verifier
    uv run python src/encre/transport_de_calibration.py \\
        --json docs/mesures/transport_de_calibration.json
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src"))

from encre.bruit_dune_fenetre import FRAGMENTS, TUILE, tuiles  # noqa: E402
from encre.typographie import (binariser_encre, composantes, couverture,  # noqa: E402
                               epaisseur_trait, masque_papyrus)
from volume.evaluate_segment import load_pair  # noqa: E402

GRANDEURS = ("epaisseur_trait_px", "couverture", "aire_mediane_px", "hauteur_mediane_px",
             "composantes")
"""Ce qu'on mesure sur la carte, sans jamais toucher aux étiquettes.

⚠ `interligne` en est absent volontairement — voir l'en-tête. Une grandeur qu'on ne peut
pas mesurer proprement à cette échelle doit être **nommée absente**, pas approchée.
"""


def en_gris(tuile: np.ndarray) -> np.ndarray:
    """Une tuile de logits en niveaux de gris, par la MÊME transformation que le dépôt emploie.

    ⚠⚠ L'étirement est sur les percentiles 2 et 98, comme `typographie.carte_npy_en_gris`, et
    surtout il est calculé **sur la tuile**. Un étirement calculé sur toute la carte ferait
    dépendre la mesure d'une tuile de ce que portent les autres — donc deux tuiles identiques
    de deux fragments donneraient deux épaisseurs de trait différentes, ce qui est exactement
    la propriété qu'un prédicteur ne doit pas avoir.

    ⚠ Les pixels non couverts sortent à zéro, comme un bord de segment : `masque_papyrus` les
    écarte ensuite, donc ils ne comptent ni comme encre ni comme support.
    """
    couvert = np.isfinite(tuile)
    if not couvert.any():
        return np.zeros(tuile.shape, dtype=np.uint8)
    lo, hi = np.percentile(tuile[couvert], [2, 98])
    img = np.clip((tuile - lo) / max(float(hi - lo), 1e-9), 0.0, 1.0)
    img[~couvert] = 0.0
    return (img * 255).astype(np.uint8)


def grandeurs_de_tuile(tuile: np.ndarray) -> dict:
    """Les grandeurs typographiques d'une tuile — aucune étiquette n'entre ici.

    ⚠ La signature de cette fonction EST la garantie : elle ne reçoit que la prédiction. Un
    prédicteur qui verrait la vérité, même par un paramètre par défaut, ne prédirait rien.
    """
    gris = en_gris(tuile)
    masque = masque_papyrus(gris)
    binaire = binariser_encre(gris, masque)
    comp = composantes(binaire)
    return {
        "epaisseur_trait_px": epaisseur_trait(binaire),
        "couverture": couverture(binaire, masque),
        "aire_mediane_px": comp["aire_mediane_px"],
        "hauteur_mediane_px": comp["hauteur_mediane_px"],
        "composantes": float(comp["composantes"]),
    }


def rangs(xs: list[float]) -> list[float]:
    """Rangs moyens, ex aequo compris — sinon la corrélation dépendrait de l'ordre d'arrivée."""
    ordre = sorted(range(len(xs)), key=lambda i: xs[i])
    out = [0.0] * len(xs)
    i = 0
    while i < len(ordre):
        j = i
        while j + 1 < len(ordre) and xs[ordre[j + 1]] == xs[ordre[i]]:
            j += 1
        moyen = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            out[ordre[k]] = moyen
        i = j + 1
    return out


def spearman(xs: list[float], ys: list[float]) -> float:
    """Corrélation de rang.

    ⚠⚠ De RANG, et pas de Pearson : rien ne dit que la relation entre une épaisseur de trait
    et une AUC soit linéaire, et une valeur aberrante sur 23 points suffirait à fabriquer ou à
    détruire une corrélation de Pearson. Une AUC est elle-même une statistique de rang, donc
    la mesurer par des rangs est aussi le choix cohérent.
    """
    n = len(xs)
    if n < 4:
        return float("nan")
    rx, ry = rangs(xs), rangs(ys)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    dx = math.sqrt(sum((a - mx) ** 2 for a in rx))
    dy = math.sqrt(sum((b - my) ** 2 for b in ry))
    return num / (dx * dy) if dx > 0 and dy > 0 else float("nan")


def intervalle_par_tirage(xs: list[float], ys: list[float], tirages: int = 2000,
                          graine: int = 0) -> dict:
    """L'intervalle de la corrélation, en rééchantillonnant les TUILES.

    ⚠ Par tuiles, pour la même raison que dans `bruit_dune_fenetre` : c'est l'échelle à
    laquelle les observations sont à peu près indépendantes. Et l'intervalle est ce qui
    empêche de lire « ρ = 0,4 sur 23 points » comme un résultat.
    """
    if len(xs) < 4:
        return {"exploitable": False, "n": len(xs)}
    rng = np.random.default_rng(graine)
    vals = []
    for _ in range(tirages):
        idx = rng.integers(0, len(xs), size=len(xs))
        a = [xs[i] for i in idx]
        b = [ys[i] for i in idx]
        r = spearman(a, b)
        if not math.isnan(r):
            vals.append(r)
    if not vals:
        return {"exploitable": False, "n": len(xs)}
    return {
        "exploitable": True,
        "n": len(xs),
        "rho": spearman(xs, ys),
        "ic_bas": float(np.percentile(vals, 2.5)),
        "ic_haut": float(np.percentile(vals, 97.5)),
    }


def p_par_permutation(xs: list[float], ys: list[float], tirages: int = 5000,
                      graine: int = 11) -> dict:
    """La part des mélanges dont la corrélation est au moins aussi forte que l'observée.

    ⚠⚠⚠ POURQUOI CETTE FONCTION REMPLACE UN TÉMOIN À UN SEUL TIRAGE. Ma première version
    mélangeait l'AUC **une fois** et imprimait le ρ obtenu à côté du vrai. Ce n'est pas un
    témoin, c'est **un tirage de la loi nulle** : il a rendu −0,40 et −0,36 sur deux grandeurs,
    c'est-à-dire autant que les vraies corrélations, et un lecteur pouvait aussi bien y voir
    « le mélange corrèle donc rien ne vaut » que « c'est un hasard malheureux ». Aucune des
    deux lectures n'était fondée sur quoi que ce soit.

    ⭐ Ce qui répond est la **distribution** : sur cinq mille mélanges, quelle fraction fait
    au moins aussi bien ? C'est une valeur p, elle se compare à un seuil, et elle ne dépend
    d'aucune hypothèse sur la forme de la relation.

    ⚠ Bilatérale, sur |ρ| : rien dans `45` ne prédit le SIGNE de la relation entre une
    épaisseur de trait et une AUC. Choisir le sens après avoir vu les données doublerait
    silencieusement le taux de faux positifs.
    """
    if len(xs) < 4:
        return {"exploitable": False, "n": len(xs)}
    observe = spearman(xs, ys)
    if math.isnan(observe):
        return {"exploitable": False, "n": len(xs)}
    rng = np.random.default_rng(graine)
    ys_arr = np.asarray(ys, dtype=np.float64)
    au_moins = 0
    for _ in range(tirages):
        r = spearman(xs, list(rng.permutation(ys_arr)))
        if not math.isnan(r) and abs(r) >= abs(observe) - 1e-12:
            au_moins += 1
    # ⚠ (k + 1) / (N + 1) plutôt que k / N : une valeur p ne peut pas valoir zéro sur un
    # nombre fini de tirages, et l'écrire 0,0000 laisserait croire à une certitude que
    # cinq mille mélanges ne peuvent pas donner.
    return {"exploitable": True, "n": len(xs), "rho": observe,
            "p": (au_moins + 1) / (tirages + 1), "tirages": tirages}


def holm(ps: dict[str, float]) -> dict[str, float]:
    """Les valeurs p corrigées pour la MULTIPLICITÉ, par la méthode de Holm.

    ⚠⚠⚠ POURQUOI C'EST LE NOMBRE QUI DÉCIDE, et pas le p brut. Cinq grandeurs sont testées
    ici. Sous l'hypothèse nulle, la probabilité qu'**au moins une** passe sous 0,05 vaut
    1 − 0,95⁵ = **23 %** : « une sur cinq est significative » est donc ce que le hasard rend
    environ une fois sur quatre, et le publier tel quel serait rapporter un tirage comme un
    résultat. Ce dépôt a déjà payé cette faute sous d'autres costumes.

    ⭐ Holm plutôt que Bonferroni : même garantie sur le taux d'erreur familial, jamais moins
    de puissance — la plus petite valeur p est multipliée par le nombre de tests, la suivante
    par ce nombre moins un, et ainsi de suite. Bonferroni multiplie tout par cinq et jette de
    la puissance pour rien.

    ⚠ La monotonie est imposée : une valeur corrigée ne peut pas être inférieure à celle qui
    la précède, sinon l'ordre des grandeurs changerait après correction — ce qui ferait dire
    au test qu'une grandeur moins convaincante est plus sûre.
    """
    ordre = sorted(ps.items(), key=lambda kv: kv[1])
    n = len(ordre)
    out, courant = {}, 0.0
    for i, (nom, p) in enumerate(ordre):
        courant = max(courant, min(1.0, p * (n - i)))
        out[nom] = courant
    return out


def mesurer(racine: Path = RACINE, fragments=FRAGMENTS, tirages: int = 2000) -> dict:
    """Chaque tuile utilisable, ses grandeurs, son AUC — et la corrélation des deux."""
    lignes = []
    for frag in fragments:
        carte = racine / "data" / "out" / f"ink_{frag}_54keV.npy"
        labels = racine / "data" / frag / "labels_fenetre.png"
        if not carte.is_file() or not labels.is_file():
            continue
        prediction, verite = load_pair(carte, labels)
        for t in tuiles(prediction, verite):
            bloc = prediction[t["y"]:t["y"] + TUILE, t["x"]:t["x"] + TUILE]
            g = grandeurs_de_tuile(bloc)
            g.update({"fragment": frag, "y": t["y"], "x": t["x"], "auc": t["auc"],
                      "encre_%": t["encre_%"]})
            lignes.append(g)

    correlations = {}
    for nom in GRANDEURS:
        paires = [(l[nom], l["auc"]) for l in lignes if l.get(nom) is not None]
        xs = [a for a, _ in paires]
        ys = [b for _, b in paires]
        correlations[nom] = intervalle_par_tirage(xs, ys, tirages=tirages)

    # ⚠⚠ LE TEMOIN QUI DONNE UNE ECHELLE : la DISTRIBUTION des correlations sous melange,
    # pas un tirage unique. Voir `p_par_permutation` pour ce que le tirage unique a coute.
    permutations = {}
    for nom in GRANDEURS:
        paires = [(l[nom], l["auc"]) for l in lignes if l.get(nom) is not None]
        permutations[nom] = p_par_permutation([a for a, _ in paires],
                                              [b for _, b in paires])

    brutes = {n: d["p"] for n, d in permutations.items() if d.get("exploitable")}
    return {"tuile_px": TUILE, "tuiles": lignes, "correlations": correlations,
            "permutation": permutations, "holm": holm(brutes) if brutes else {},
            "grandeurs_testees": len(brutes)}


def rapporter(m: dict) -> None:
    """La sortie lisible, le témoin à côté de la mesure."""
    print(f"{len(m['tuiles'])} tuiles de {m['tuile_px']} px, "
          f"grandeurs mesurees SANS regarder les etiquettes\n")
    print(f"{'grandeur':22} {'n':>3} {'rho':>7} {'IC 95 %':>20} {'p permut.':>10} "
          f"{'p Holm':>8}")
    for nom, c in m["correlations"].items():
        t = m["permutation"].get(nom, {})
        if not c.get("exploitable"):
            print(f"{nom:22} {c.get('n', 0):3d} {'—':>7} {'pas assez de tuiles':>20}")
            continue
        ic = f"[{c['ic_bas']:+.2f} ; {c['ic_haut']:+.2f}]"
        pv = f"{t['p']:.4f}" if t.get("exploitable") else "—"
        hv = m.get("holm", {}).get(nom)
        hs = f"{hv:.3f}" if hv is not None else "—"
        print(f"{nom:22} {c['n']:3d} {c['rho']:+7.3f} {ic:>20} {pv:>10} {hs:>8}")

    exploitables = [c for c in m["correlations"].values() if c.get("exploitable")]
    brutes = [nom for nom, c in m["correlations"].items()
              if c.get("exploitable") and m["permutation"].get(nom, {}).get("p", 1.0) < 0.05]
    tranchees = [nom for nom in brutes if m.get("holm", {}).get(nom, 1.0) < 0.05]
    n_tests = m.get("grandeurs_testees", len(exploitables))
    print()
    print(f"  {len(brutes)} grandeur(s) sur {len(exploitables)} sous p = 0,05 BRUT"
          + (" : " + ", ".join(brutes) if brutes else ""))
    if n_tests:
        print(f"  ⚠ mais {n_tests} tests ont ete faits : le hasard en met au moins une sous "
              f"0,05 dans {100 * (1 - 0.95 ** n_tests):.0f} % des cas")
    print(f"  {len(tranchees)} grandeur(s) survivent a la correction de Holm"
          + (" : " + ", ".join(tranchees) if tranchees else ""))
    if not tranchees:
        print("  ⚠ AUCUNE ne tranche : a cette taille d'echantillon, et avec une AUC de tuile")
        print("    dont l'ecart-type vaut 0,2243, le transport n'est ni etabli ni refute.")


def verifier() -> int:
    """L'instrument peut-il rendre la mauvaise réponse ?"""
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    rng = np.random.default_rng(4)

    # -- rangs : ex aequo au rang moyen, sinon la correlation depend de l'ordre d'arrivee.
    v("les rangs commencent a 1", rangs([5.0, 7.0, 9.0]) == [1.0, 2.0, 3.0])
    v("deux ex aequo prennent le rang moyen", rangs([5.0, 5.0, 9.0]) == [1.5, 1.5, 3.0])
    v("... et trois aussi", rangs([1.0, 1.0, 1.0]) == [2.0, 2.0, 2.0])

    # -- spearman : monotone non lineaire, signe, et refus d'un echantillon court.
    v("une relation monotone non lineaire rend 1",
      abs(spearman([1, 2, 3, 4, 5], [1, 4, 9, 16, 25]) - 1.0) < 1e-9)
    v("... et son inverse rend -1",
      abs(spearman([1, 2, 3, 4, 5], [25, 16, 9, 4, 1]) + 1.0) < 1e-9)
    v("un echantillon trop court est refuse", math.isnan(spearman([1, 2, 3], [1, 2, 3])))
    v("une constante ne correle avec rien",
      math.isnan(spearman([1, 1, 1, 1], [1, 2, 3, 4])))
    # ⚠⚠ LA SONDE QUI COMPTE : Pearson vaut 0,79 sur ce couple, Spearman 1,00. Utiliser
    # Pearson ferait dependre le verdict de la forme de la relation, pas de son existence.
    xs = [1.0, 2.0, 3.0, 4.0, 5.0]
    ys = [1.0, 2.0, 3.0, 4.0, 100.0]
    v("une valeur aberrante ne deplace pas une correlation de rang",
      abs(spearman(xs, ys) - 1.0) < 1e-9, f"{spearman(xs, ys):.3f}")

    # -- intervalle : encadre la valeur, se resserre avec n, reproductible.
    a = list(rng.normal(0, 1, 12))
    b = [x + float(rng.normal(0, 0.5)) for x in a]
    petit = intervalle_par_tirage(a, b, 1000, 1)
    grand_a = list(rng.normal(0, 1, 200))
    grand_b = [x + float(rng.normal(0, 0.5)) for x in grand_a]
    grand = intervalle_par_tirage(grand_a, grand_b, 1000, 1)
    v("l'intervalle encadre la correlation",
      petit["ic_bas"] <= petit["rho"] <= petit["ic_haut"], str(petit))
    v("... et se resserre quand il y a plus de points",
      (grand["ic_haut"] - grand["ic_bas"]) < (petit["ic_haut"] - petit["ic_bas"]),
      f"{grand['ic_haut'] - grand['ic_bas']:.3f} vs {petit['ic_haut'] - petit['ic_bas']:.3f}")
    v("... et il est reproductible a graine egale",
      intervalle_par_tirage(a, b, 1000, 1) == petit)
    v("trois points ne suffisent pas",
      intervalle_par_tirage([1, 2, 3], [1, 2, 3], 100, 0)["exploitable"] is False)
    # ⚠ Deux series INDEPENDANTES doivent rendre un intervalle qui contient zero, sinon
    # l'instrument declarerait un transport la ou il n'y a rien.
    ind = intervalle_par_tirage(list(rng.normal(0, 1, 60)), list(rng.normal(0, 1, 60)),
                                1000, 2)
    v("deux series independantes rendent un intervalle qui contient zero",
      ind["ic_bas"] <= 0 <= ind["ic_haut"], str(ind))

    # -- permutation : les deux sens, et la borne inferieure de la valeur p.
    lie_x = list(range(30))
    lie_y = [float(x) + float(rng.normal(0, 0.3)) for x in lie_x]
    pl = p_par_permutation(lie_x, lie_y, 500, 3)
    v("une relation forte rend une valeur p basse", pl["p"] < 0.01, str(pl))
    v("... et elle ne peut jamais valoir zero", pl["p"] > 0.0, str(pl["p"]))
    v("... et vaut au minimum 1/(N+1)", abs(pl["p"] - 1 / 501) < 1e-12, str(pl["p"]))
    sans = p_par_permutation(list(rng.normal(0, 1, 30)), list(rng.normal(0, 1, 30)), 500, 4)
    v("deux series independantes ne passent pas sous 0,05", sans["p"] > 0.05, str(sans))
    # ⚠⚠ La sonde qui distingue une valeur p d'un tirage unique : le SIGNE ne doit rien
    # changer, puisque le test est bilateral et qu'aucun sens n'etait predit.
    inverse = p_par_permutation(lie_x, [-y for y in lie_y], 500, 3)
    v("une relation inversee rend la meme valeur p", inverse["p"] == pl["p"],
      f"{inverse['p']} vs {pl['p']}")
    v("un echantillon trop court est refuse",
      p_par_permutation([1, 2], [1, 2], 100, 0)["exploitable"] is False)

    # -- holm : la correction, ses bornes, et le cas qui la distingue de Bonferroni.
    h = holm({"a": 0.01, "b": 0.02, "c": 0.03, "d": 0.60, "e": 0.90})
    v("la plus petite p est multipliee par le nombre de tests",
      abs(h["a"] - 0.05) < 1e-12, str(h["a"]))
    v("... la suivante par ce nombre moins un", abs(h["b"] - 0.08) < 1e-12, str(h["b"]))
    v("... et la correction est monotone",
      h["a"] <= h["b"] <= h["c"] <= h["d"] <= h["e"], str(h))
    v("... et elle ne depasse jamais 1", max(h.values()) <= 1.0, str(h))
    # ⚠ Le cas qui compte pour NOTRE mesure : un p brut de 0,0312 sur cinq tests ne survit pas.
    v("0,0312 sur cinq tests ne survit pas a la correction",
      holm({"x": 0.0312, "a": 0.1, "b": 0.2, "c": 0.3, "d": 0.4})["x"] > 0.05,
      str(holm({"x": 0.0312, "a": 0.1, "b": 0.2, "c": 0.3, "d": 0.4})["x"]))
    # ⚠⚠ Et Holm doit etre au moins aussi PUISSANT que Bonferroni, jamais moins : sur le
    # deuxieme rang, Bonferroni donnerait 0,10 la ou Holm donne 0,08.
    v("Holm ne jette pas la puissance de Bonferroni", h["b"] < 0.02 * 5)
    v("un seul test n'est pas corrige", holm({"a": 0.03})["a"] == 0.03)

    # -- en_gris : l'etirement est LOCAL, et les non couverts sortent a zero.
    bloc = np.linspace(-3, 3, 64 * 64).reshape(64, 64).astype(np.float32)
    g = en_gris(bloc)
    v("l'etirement rend bien un uint8", g.dtype == np.uint8)
    v("... et couvre presque toute l'echelle", g.max() >= 250 and g.min() <= 5,
      f"{g.min()}..{g.max()}")
    troue = bloc.copy()
    troue[:8, :] = np.nan
    v("un pixel non couvert sort a zero", en_gris(troue)[:8, :].max() == 0)
    # ⚠⚠ La propriete qui compte : deux tuiles IDENTIQUES doivent rendre le meme gris, quel
    # que soit ce que porte le reste de la carte. C'est ce qui rend la grandeur transportable.
    v("le gris d'une tuile ne depend que d'elle",
      np.array_equal(en_gris(bloc), en_gris(bloc.copy())))
    v("... et un decalage constant ne le change pas",
      np.array_equal(en_gris(bloc), en_gris(bloc + 100.0)))
    v("une tuile entierement non couverte ne casse pas",
      en_gris(np.full((8, 8), np.nan, dtype=np.float32)).max() == 0)

    # -- grandeurs_de_tuile : une tuile avec des traits doit rendre une epaisseur plausible.
    trait = np.zeros((128, 128), dtype=np.float32)
    for y in range(10, 120, 16):
        trait[y:y + 3, 10:118] = 5.0
    g2 = grandeurs_de_tuile(trait)
    v("des traits de 3 px rendent une epaisseur proche de 3",
      g2["epaisseur_trait_px"] is not None and 2.0 <= g2["epaisseur_trait_px"] <= 4.5,
      str(g2["epaisseur_trait_px"]))
    v("... et sept traits font sept composantes", g2["composantes"] == 7.0,
      str(g2["composantes"]))
    v("une tuile vide ne rend pas d'epaisseur",
      grandeurs_de_tuile(np.zeros((64, 64), dtype=np.float32))["epaisseur_trait_px"] is None)
    # ⚠ La garantie ecrite dans la docstring : la fonction ne prend QUE la prediction.
    import inspect
    v("la fonction ne peut pas voir les etiquettes",
      list(inspect.signature(grandeurs_de_tuile).parameters) == ["tuile"],
      str(list(inspect.signature(grandeurs_de_tuile).parameters)))

    print(f"{'ALL PASS' if echecs == 0 else 'ECHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    p.add_argument("--tirages", type=int, default=2000)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    m = mesurer(tirages=a.tirages)
    if not m["tuiles"]:
        print("aucune tuile — les cartes de fragment ne sont pas rendues", file=sys.stderr)
        return 2
    rapporter(m)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(m, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\n→ {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
