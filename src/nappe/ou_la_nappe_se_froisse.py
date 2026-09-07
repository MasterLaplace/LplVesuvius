#!/usr/bin/env python3
"""OÙ la nappe se froisse, et est-ce le même endroit pour tous les marcheurs ?

⚠⚠⚠ POURQUOI CE FICHIER EXISTE, et il vient d'une IMAGE. `la_portee_du_raccrochage` publie la
rugosité de nappe en médianes — 5,11 µm pour le pas normal au bras 6, 151,81 pour le raccrochage.
Une médiane dit **combien** et jamais **où** : regarder les cartes a montré que le froissement du
pas normal n'est pas distribué du tout, mais concentré en **taches** qui apparaissent au bras 3 et
grandissent, le gros de la nappe restant lisse. Une médiane sur une nappe surtout lisse avec
quelques régions ruinées, et une médiane sur une nappe uniformément tiède, sont le même nombre.

⭐⭐ ET LA QUESTION QUE L'IMAGE POSE : les taches sont-elles au MÊME ENDROIT d'un marcheur à
l'autre ? Si oui, elles sont une propriété du **lieu** — de la matière à ces cellules — et pas du
marcheur, et c'est une information actionnable : un dérouleur peut refuser d'avancer là plutôt que
d'y avancer faux.

⚠⚠⚠ ET ELLE NE SE RÉPOND PAS SANS TÉMOIN. Deux ensembles de taches occupant chacun 40 % d'une
même région se recouvrent déjà largement **par construction** : le recouvrement brut n'est donc
pas une mesure de coïncidence. Le témoin est le recouvrement de deux ensembles de MÊMES TAILLES
tirés au hasard dans les mêmes cellules — sans lui, « les taches coïncident » est vrai de
n'importe quoi.

⚠ Le seuil qui définit une tache vient de la matière : la **demi-feuille**. Un point qui s'écarte
de ses voisins de plus que ça est plus près de la feuille voisine que du plan de ses propres
voisins, donc la nappe y est localement pliée et non bosselée.

Usage :
    uv run python src/nappe/ou_la_nappe_se_froisse.py --verifier
    uv run python src/nappe/ou_la_nappe_se_froisse.py --cote 960 \\
        --json docs/mesures/ou_la_nappe_se_froisse.json
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "commun"))
from le_corpus_des_spires import corpus_fabrique, volume_fabrique  # noqa: E402

MARCHEURS = ("rien", "rien_lisse", "raccroche", "oracle")
TIRAGES = 200


def champ_de_froissement(grille: np.ndarray, masque: np.ndarray,
                         voxel_um: float) -> tuple[np.ndarray, np.ndarray]:
    """L'écart de chaque point à la médiane de ses voisins, en µm, ET les cellules où il existe.

    ⚠ C'est le champ dont `rugosite_de_la_nappe` publie la médiane : la même arithmétique, mais
    rendue cellule par cellule. Deux implémentations finiraient par ne plus s'accorder sur ce que
    « l'écart au voisinage » veut dire, donc la médiane de ce champ est contrôlée contre elle.
    """
    from le_raccrochage_a_la_matiere import accorder_les_voisins  # noqa: PLC0415

    if grille.ndim != 3 or grille.shape[2] != 3:
        raise ValueError("une nappe porte trois coordonnées par cellule")
    garde = masque & np.all(np.isfinite(grille), axis=-1)
    ecarts = np.zeros(grille.shape, dtype=float)
    for c in range(3):
        lisse, assez = accorder_les_voisins(grille[:, :, c], garde)
        garde = garde & assez & np.isfinite(lisse)
        ecarts[:, :, c] = grille[:, :, c] - lisse
    champ = np.linalg.norm(np.where(garde[..., None], ecarts, 0.0), axis=-1) * voxel_um
    return champ, garde


def recouvrement(a: np.ndarray, b: np.ndarray) -> float:
    """Le recouvrement de Jaccard de deux ensembles de cellules."""
    union = int((a | b).sum())
    return round(float(int((a & b).sum()) / union), 3) if union else 0.0


def temoin_du_recouvrement(a: np.ndarray, b: np.ndarray, dans: np.ndarray,
                           tirages: int = TIRAGES, graine: int = 7) -> float:
    """Ce que deux ensembles de MÊMES TAILLES tirés au hasard dans `dans` se recouvrent.

    ⚠⚠⚠ SANS CE TÉMOIN, « LES TACHES COÏNCIDENT » EST VRAI DE N'IMPORTE QUOI. Deux ensembles
    occupant chacun 40 % d'une même région se recouvrent déjà largement par construction ; le
    recouvrement brut mesure donc surtout leurs TAILLES. Ce qui a du sens est l'écart entre ce
    qu'on observe et ce que le hasard donnerait à tailles égales.

    ⚠ Les tailles sont conservées EXACTEMENT, et le tirage est sans remise dans les cellules
    réellement disponibles : tirer dans toute la grille donnerait un témoin trop bas, donc une
    coïncidence apparente là où il n'y en a pas.
    """
    ou = np.argwhere(dans)
    na, nb = int((a & dans).sum()), int((b & dans).sum())
    if len(ou) < 2 or na == 0 or nb == 0:
        return 0.0
    rng = np.random.default_rng(graine)
    valeurs = []
    for _ in range(max(1, int(tirages))):
        ia = rng.choice(len(ou), min(na, len(ou)), replace=False)
        ib = rng.choice(len(ou), min(nb, len(ou)), replace=False)
        sa = np.zeros(dans.shape, dtype=bool)
        sb = np.zeros(dans.shape, dtype=bool)
        sa[ou[ia][:, 0], ou[ia][:, 1]] = True
        sb[ou[ib][:, 0], ou[ib][:, 1]] = True
        valeurs.append(recouvrement(sa, sb))
    return round(float(np.median(valeurs)), 3)


def mesurer(graine: int = 42, minimum: int = 30, cache_actif: bool = True,
            cote: float | None = None, bras_max: int = 8,
            corpus: dict | None = None, volume=None, decalage_ancre: int = 0) -> dict:
    """Où chaque marcheur froisse sa nappe, et si les taches coïncident entre marcheurs."""
    from la_portee_du_raccrochage import mesurer as marche  # noqa: E402, PLC0415

    with contextlib.redirect_stdout(io.StringIO()):
        r = marche(graine=graine, minimum=minimum, cache_actif=cache_actif, cote=cote,
                   bras_max=bras_max, corpus=corpus, volume=volume,
                   decalage_ancre=decalage_ancre, marcheurs=MARCHEURS,
                   champs_de_froissement=True)
    seuil = float(r["demi_feuille_um"])
    champs = r.pop("champs")
    bras_communs = min(len(champs[n]) for n in MARCHEURS)
    if bras_communs == 0:
        raise RuntimeError("aucun marcheur n'a fait un bras : rien à comparer")

    lignes = []
    for nom in MARCHEURS:
        parts, taches = [], []
        for champ, garde in champs[nom]:
            vus = int(garde.sum())
            t = int(((champ >= seuil) & garde).sum())
            taches.append(t)
            parts.append(round(t / vus, 4) if vus else None)
        lignes.append(dict(marcheur=nom, taches=taches, part_froissee=parts,
                           cellules=[int(g.sum()) for _, g in champs[nom]]))

    # ⚠⚠ LA COMPARAISON PORTE SUR LE DERNIER BRAS COMMUN et sur les cellules que TOUS ont
    # gardées : comparer deux masques différents comparerait des régions, pas des taches.
    k = bras_communs - 1
    dans = champs[MARCHEURS[0]][k][1].copy()
    for nom in MARCHEURS[1:]:
        dans &= champs[nom][k][1]
    ens = {nom: (champs[nom][k][0] >= seuil) & dans for nom in MARCHEURS}
    paires = []
    for i, a in enumerate(MARCHEURS):
        for b in MARCHEURS[i + 1:]:
            obs = recouvrement(ens[a], ens[b])
            att = temoin_du_recouvrement(ens[a], ens[b], dans, graine=graine)
            # ⚠⚠⚠ LE RAPPORT, PAS SEULEMENT LE SIGNE. « Au-dessus du témoin » est satisfait par
            # un rapport de 1,01, et deux ensembles qui couvrent chacun 90 % d'une région sont
            # au-dessus de leur témoin par construction ou presque. C'est le rapport qui dit de
            # COMBIEN, et c'est lui qu'un lecteur doit voir à côté du oui.
            paires.append(dict(a=a, b=b, recouvrement=obs, temoin=att,
                               rapport=round(obs / att, 2) if att > 0 else None,
                               au_dessus_du_temoin=bool(obs > att),
                               taches_a=int(ens[a].sum()), taches_b=int(ens[b].sum())))
    return dict(
        fragment=r["fragment"], ancre=r["ancre"], spires_visees=r["spires_visees"],
        demi_feuille_um=r["demi_feuille_um"], bras_communs=bras_communs,
        cellules_comparees=int(dans.sum()), marcheurs=list(MARCHEURS), lignes=lignes,
        # ⭐⭐ LE VERDICT, et il est posé contre le témoin et jamais sur le recouvrement brut.
        paires_au_dessus_du_temoin=sum(p["au_dessus_du_temoin"] for p in paires),
        paires=paires,
        les_taches_coincident=bool(
            paires and all(p["au_dessus_du_temoin"] for p in paires)),
        # ⚠⚠ ET LA PAIRE LA PLUS FAIBLE, nommée : c'est elle qui dit ce que le verdict vaut.
        # Un « oui » porté par une paire à 1,01 est un oui qui ne survivrait pas à un autre
        # tirage, et le lecteur doit pouvoir le voir sans relire le tableau.
        rapport_le_plus_faible=round(min((p["rapport"] for p in paires
                                          if p["rapport"] is not None), default=0.0), 2),
        # ⚠ ET LE RAPPORT OBSERVÉ / ATTENDU, qui dit de COMBIEN elles coïncident. Un rapport de
        # 1,1 et un rapport de 5 sont deux faits très différents sous un même « oui ».
        rapport_median=round(float(np.median([p["recouvrement"] / max(p["temoin"], 1e-9)
                                              for p in paires])), 2) if paires else None)


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # ⚠⚠ LE RECOUVREMENT EST EXERCÉ SUR DES CAS DONT LA RÉPONSE EST CONNUE D'AVANCE.
    a = np.zeros((4, 4), dtype=bool)
    a[0, :2] = True
    v("deux ensembles identiques se recouvrent entièrement", recouvrement(a, a) == 1.0)
    b = np.zeros((4, 4), dtype=bool)
    b[3, :2] = True
    v("... deux ensembles disjoints ne se recouvrent pas", recouvrement(a, b) == 0.0)
    v("... et deux ensembles vides rendent zéro, pas une division par zéro",
      recouvrement(np.zeros((2, 2), bool), np.zeros((2, 2), bool)) == 0.0)
    # ⚠⚠⚠ LE TÉMOIN EST CE QUI REND LE CHIFFRE LISIBLE : deux ensembles qui couvrent presque
    # toute la région se recouvrent presque totalement PAR CONSTRUCTION, donc le témoin doit
    # être haut ; deux ensembles minuscules dans une grande région, il doit être bas.
    grand = np.zeros((20, 20), dtype=bool)
    grand[:18] = True
    tout = np.ones((20, 20), dtype=bool)
    v("le témoin est HAUT quand les deux ensembles couvrent presque tout",
      temoin_du_recouvrement(grand, grand, tout) > 0.7,
      str(temoin_du_recouvrement(grand, grand, tout)))
    petit = np.zeros((20, 20), dtype=bool)
    petit[0, :3] = True
    v("... et BAS quand ils sont minuscules dans une grande région",
      temoin_du_recouvrement(petit, petit, tout) < 0.2,
      str(temoin_du_recouvrement(petit, petit, tout)))
    # ⚠ Le tirage est SANS REMISE dans les cellules disponibles : tirer dans toute la grille
    # donnerait un témoin trop bas, donc une coïncidence apparente là où il n'y en a pas.
    v("... le témoin tire dans les cellules DISPONIBLES, pas dans toute la grille",
      temoin_du_recouvrement(petit, petit, petit) == 1.0,
      str(temoin_du_recouvrement(petit, petit, petit)))

    # ⚠⚠⚠ LE CHEMIN QUI PRODUIT LE NOMBRE PUBLIÉ, HORS LIGNE.
    from la_lissite_de_la_feuille import rugosite_de_la_nappe  # noqa: PLC0415
    from le_corpus_des_spires import geometrie_fabriquee  # noqa: PLC0415

    c, vol = corpus_fabrique(), volume_fabrique(geometrie_fabriquee())
    fab = mesurer(minimum=20, corpus=c, volume=vol)
    v("la mesure tourne de bout en bout sur des matières fabriquées",
      fab["bras_communs"] >= 2, f"{fab['bras_communs']} bras · "
      f"{fab['cellules_comparees']} cellules comparées")
    v("... chaque marcheur publie sa part froissée bras par bras",
      all(len(x["part_froissee"]) >= fab["bras_communs"] for x in fab["lignes"]),
      str({x["marcheur"]: x["part_froissee"][:3] for x in fab["lignes"]}))
    # ⚠⚠ CHAQUE PAIRE PORTE SON TÉMOIN : un recouvrement publié sans lui se lirait comme une
    # coïncidence alors qu'il mesure surtout la taille des deux ensembles.
    # ⚠⚠⚠ LE RAPPORT EST CE QUI DIT DE COMBIEN : sans lui, « au-dessus du témoin » se lit comme
    # une coïncidence forte alors qu'il est satisfait par un rapport de 1,01.
    v("... et le rapport observé/attendu est publié pour chaque paire, plus le plus faible",
      all("rapport" in p for p in fab["paires"]) and "rapport_le_plus_faible" in fab,
      f"le plus faible {fab['rapport_le_plus_faible']}")
    v("... chaque paire publie son recouvrement ET son témoin",
      all("temoin" in p and p["recouvrement"] is not None for p in fab["paires"]),
      str([(p["a"], p["b"], p["recouvrement"], p["temoin"]) for p in fab["paires"]][:2]))
    v("... et le verdict n'est vrai que si TOUTES les paires passent leur témoin",
      fab["les_taches_coincident"]
      == (fab["paires_au_dessus_du_temoin"] == len(fab["paires"])),
      f"{fab['paires_au_dessus_du_temoin']}/{len(fab['paires'])} · "
      f"{fab['les_taches_coincident']}")
    # ⚠⚠⚠ LE CHAMP EST CELUI DONT `rugosite_de_la_nappe` PUBLIE LA MÉDIANE : deux arithmétiques
    # de « l'écart au voisinage » finiraient par ne plus s'accorder, donc l'une contrôle l'autre.
    g0 = geometrie_fabriquee()
    grille, ok = c["grilles"][min(c["grilles"])]
    champ, garde = champ_de_froissement(grille, ok, c["voxel_um"])
    attendu = rugosite_de_la_nappe(grille, ok, c["voxel_um"])
    obtenu = round(float(np.median(champ[garde])), 2) if garde.any() else None
    v("le champ rendu ici a exactement la médiane que publie `rugosite_de_la_nappe`",
      obtenu == attendu, f"{obtenu} contre {attendu}")
    v("... le résultat est sérialisable tel quel, sans type qui traîne",
      isinstance(json.dumps(fab), str))
    souci = None
    try:
        afficher(fab)
    except Exception as exc:  # noqa: BLE001
        souci = f"{type(exc).__name__}: {exc}"
    v("... et l'affichage tourne sur ce résultat", souci is None, str(souci))
    souci = None
    try:
        champ_de_froissement(grille[:, :, :2], ok, 1.0)
    except ValueError as exc:
        souci = str(exc)
    v("une nappe qui n'a pas trois coordonnées est REFUSÉE, pas devinée",
      souci is not None, str(souci))
    del g0

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def afficher(r: dict) -> None:
    """Le compte rendu lisible : la part froissée bras par bras, puis les coïncidences."""
    print(f"ancre {r['ancre']} · vise {r['spires_visees']} · seuil = demi-feuille "
          f"{r['demi_feuille_um']} µm · {r['bras_communs']} bras communs")
    print()
    n = max(len(x["part_froissee"]) for x in r["lignes"])
    print(f"{'marcheur':>12} " + " ".join(f"{k:>7}" for k in range(1, n + 1)))
    print("-" * (13 + 8 * n))
    for x in r["lignes"]:
        cases = " ".join(f"{p:>7.3f}" if p is not None else "      —"
                         for p in x["part_froissee"])
        print(f"{x['marcheur']:>12} {cases}")
    print()
    print("part des cellules dont l'écart au voisinage dépasse la demi-feuille")
    print()
    print(f"coïncidence des taches au dernier bras commun, sur {r['cellules_comparees']} "
          "cellules gardées par TOUS :")
    for p in r["paires"]:
        print(f"  {p['a']:>11} / {p['b']:<12} recouvrement {p['recouvrement']:.3f} · "
              f"témoin {p['temoin']:.3f} · rapport "
              f"{('×%.2f' % p['rapport']) if p['rapport'] else '—':>6} · "
              f"{'au-dessus' if p['au_dessus_du_temoin'] else 'SOUS le témoin'}")
    print()
    print(f"→ ⭐ les taches coïncident (toutes les paires au-dessus du témoin) : "
          f"{'OUI' if r['les_taches_coincident'] else 'NON'} · "
          f"{r['paires_au_dessus_du_temoin']}/{len(r['paires'])} paires · "
          f"rapport observé/attendu médian {r['rapport_median']} · "
          f"le plus faible {r['rapport_le_plus_faible']}")
    if r["rapport_le_plus_faible"] < 1.1:
        print("→ ⚠⚠ mais la paire la plus faible est à peine au-dessus de son témoin : le "
              "verdict tient sur un signe, pas sur une marge")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--cote", type=float, default=None)
    p.add_argument("--bras-max", type=int, default=8, dest="bras_max")
    p.add_argument("--ancre", type=int, default=0, dest="decalage_ancre")
    p.add_argument("--json", type=Path, default=None)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(cote=a.cote, bras_max=a.bras_max, decalage_ancre=a.decalage_ancre)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False))
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
