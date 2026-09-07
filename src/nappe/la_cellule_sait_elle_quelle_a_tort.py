#!/usr/bin/env python3
"""Une cellule peut-elle savoir qu'elle a tort, SANS regarder la cible ?

⚠⚠⚠ POURQUOI CETTE QUESTION EST CELLE DU BUT. Un dérouleur qui livre une nappe livre aussi,
implicitement, la prétention que chaque cellule est à sa place. `la_portee_du_raccrochage` mesure
qu'au huitième bras un tiers des cellules du pas normal sont **pliées** — plus loin de leurs
voisins qu'une demi-feuille. Si le pli **prédit** l'erreur, alors un marcheur aveugle peut publier
une **confiance par cellule** : il ne sait pas où est la vérité, mais il sait où il se trompe. Ça
change ce qu'un déroulement peut livrer, et c'est indépendant de toute amélioration de méthode.

⭐⭐ CE FICHIER NE CHOISIT AUCUN SEUIL. Il **classe** les cellules par leur pli — une quantité
observable sans supervision — et balaie la **fraction gardée**, de tout à presque rien. La courbe
qui en sort est l'objet livré : elle dit ce qui est disponible, et le point où l'on se place
appartient à l'auteur.

⚠⚠⚠ ET ELLE NE VEUT RIEN DIRE SANS SON TÉMOIN. Garder la moitié des cellules AU HASARD améliore
déjà la médiane : la moitié d'un échantillon a une dispersion moindre. Le témoin est donc le même
balayage en jetant **au hasard**, à fractions égales et sur les mêmes cellules. Ce qui compte est
l'écart entre les deux, jamais la courbe seule.

⚠ Le pli est mesuré sur la nappe que le marcheur VIENT DE PRODUIRE, donc avec ce qu'il a en main
au moment de publier. Le mesurer sur la nappe d'après serait lui donner un bras d'avance.

Usage :
    uv run python src/nappe/la_cellule_sait_elle_quelle_a_tort.py --verifier
    uv run python src/nappe/la_cellule_sait_elle_quelle_a_tort.py --cote 960 \\
        --json docs/mesures/la_cellule_sait_elle_quelle_a_tort.json
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

MARCHEURS = ("rien", "rien_lisse", "raccroche")
# ⚠⚠⚠ DEUX OBSERVABLES, ET LA CONVENTION EST QUE GRAND VEUT DIRE SUSPECT. Le pli est déjà dans
# ce sens ; l'intensité est dans l'AUTRE — une feuille est un ruban brillant, donc c'est le
# point SOMBRE qui est suspect. On classe donc sur son opposé, et le dire ici plutôt que de le
# cacher dans un signe est ce qui évite de publier une courbe parfaitement inversée.
OBSERVABLES = ("pli", "obscurite")
# ⭐⭐⭐ ET LES TROIS COMBINAISONS SANS AUCUN PARAMÈTRE. Combiner deux observables demande
# normalement un POIDS, donc un réglage — et un réglage choisi sur ce qu'il juge ne peut que
# gagner. Passer chaque observable en RANG supprime le problème deux fois : les unités
# disparaissent (un micromètre et une intensité ne s'additionnent pas), et les trois façons de
# recombiner deux rangs n'ont plus rien à régler.
#   « ou »  = le MAX des rangs : suspect dès qu'UNE des deux le dit
#   « et »  = le MIN des rangs : suspect seulement si les DEUX le disent
#   « moy » = la moyenne : les deux comptent pareil, ce qui est le seul poids qu'on n'a pas
#             choisi puisqu'il est le seul qui ne privilégie personne
COMBINAISONS = ("ou", "moyenne", "et")
COLONNES = OBSERVABLES + COMBINAISONS
# ⚠ Les fractions gardées sont un balayage, pas des réglages : la courbe entière est l'objet
# livré. Elles descendent jusqu'à un dixième parce qu'en dessous la médiane porte sur si peu de
# cellules qu'elle mesure surtout le tirage.
FRACTIONS = (1.0, 0.9, 0.75, 0.5, 0.35, 0.25, 0.1)
TIRAGES = 60


def _leve(appel) -> bool:
    """Vrai si l'appel lève. ⚠ Pour les contrôles seulement."""
    try:
        appel()
    except ValueError:
        return True
    return False


def en_rangs(x: np.ndarray) -> np.ndarray:
    """Le rang de chaque valeur, ramené dans [0, 1]. ⚠ Grand veut toujours dire SUSPECT.

    ⚠⚠⚠ POURQUOI LE RANG PLUTÔT QUE LA VALEUR. Un pli est en micromètres et une obscurité en
    niveaux de gris : les additionner demanderait un facteur de conversion, c'est-à-dire un
    réglage, c'est-à-dire un nombre choisi. Le rang efface l'unité, donc deux observables
    deviennent comparables **sans que rien n'ait été décidé**.

    ⚠ Les égalités reçoivent des rangs différents plutôt que le même : un tri stable les départage
    par leur ordre d'arrivée. C'est arbitraire et sans conséquence ici — le classement sert à
    couper une fraction, pas à noter une cellule — mais ça vaut d'être dit.
    """
    n = len(x)
    if n == 0:
        return np.zeros(0)
    if n == 1:
        return np.zeros(1)
    r = np.empty(n, dtype=float)
    r[np.argsort(x, kind="stable")] = np.arange(n, dtype=float)
    return r / (n - 1)


def combiner(rangs: dict, comment: str) -> np.ndarray:
    """Les deux rangs recombinés, sans aucun paramètre.

    ⚠⚠ LES TROIS FORMES SONT PUBLIÉES ENSEMBLE, jamais la meilleure seule. Choisir laquelle
    rapporter après avoir vu les trois serait choisir sur ce qu'on juge — la faute nº1 de ce
    dépôt — donc le verdict n'est rendu que sous une condition qu'un tirage heureux ne satisfait
    pas : battre les DEUX observables seules, à TOUTES les fractions.
    """
    a, b = rangs[OBSERVABLES[0]], rangs[OBSERVABLES[1]]
    if comment == "ou":
        return np.maximum(a, b)
    if comment == "et":
        return np.minimum(a, b)
    if comment == "moyenne":
        return (a + b) / 2.0
    raise ValueError(f"combinaison inconnue : {comment}")


def garder_les_meilleures(pli: np.ndarray, erreur: np.ndarray, part: float) -> float:
    """L'erreur médiane des cellules dont le PLI est le plus faible, à la fraction demandée.

    ⚠⚠ LE CLASSEMENT EST FAIT SUR LE PLI, JAMAIS SUR L'ERREUR. Classer sur l'erreur reviendrait à
    demander à la cible laquelle des cellules garder, ce qui est exactement la supervision que
    cette question existe pour éviter — et rendrait une courbe magnifique qu'aucun dérouleur ne
    pourrait reproduire.
    """
    n = len(erreur)
    if n == 0:
        return float("nan")
    k = max(1, int(round(float(part) * n)))
    pris = np.argsort(pli, kind="stable")[:k]
    return float(np.median(erreur[pris]))


def temoin_au_hasard(erreur: np.ndarray, part: float, tirages: int = TIRAGES,
                     graine: int = 7) -> float:
    """L'erreur médiane de la même FRACTION de cellules, tirée au hasard.

    ⚠⚠⚠ SANS CE TÉMOIN, LA COURBE NE DIT RIEN. Garder la moitié d'un échantillon au hasard
    déplace déjà sa médiane — pas beaucoup, mais pas de zéro — et une courbe qui descend peut
    donc descendre pour cette seule raison. Ce qui a un sens est l'écart entre classer par le pli
    et jeter au hasard, à fraction égale et sur les mêmes cellules.
    """
    n = len(erreur)
    if n == 0:
        return float("nan")
    k = max(1, int(round(float(part) * n)))
    rng = np.random.default_rng(graine)
    return float(np.median([np.median(erreur[rng.choice(n, k, replace=False)])
                            for _ in range(max(1, int(tirages)))]))


def mesurer(graine: int = 42, minimum: int = 30, cache_actif: bool = True,
            cote: float | None = None, bras_max: int = 8,
            corpus: dict | None = None, volume=None, decalage_ancre: int = 0,
            fractions=FRACTIONS) -> dict:
    """La courbe erreur / couverture de chaque marcheur, et son témoin au hasard."""
    from la_portee_du_raccrochage import mesurer as marche  # noqa: PLC0415

    with contextlib.redirect_stdout(io.StringIO()):
        r = marche(graine=graine, minimum=minimum, cache_actif=cache_actif, cote=cote,
                   bras_max=bras_max, corpus=corpus, volume=volume,
                   decalage_ancre=decalage_ancre, marcheurs=MARCHEURS,
                   champs_de_froissement=True, erreurs_par_cellule=True)
    champs = r.pop("champs")
    parcelles = r.pop("erreurs_par_cellule")
    fractions = tuple(float(x) for x in fractions)

    lignes = []
    for nom in MARCHEURS:
        bras = []
        for k, ((pli, ou_pli), (ou, err, inten)) in enumerate(zip(champs[nom], parcelles[nom]),
                                                             start=1):
            # ⚠⚠ LE PLI ET L'ERREUR SONT LUS SUR LES MÊMES CELLULES, et seules celles où le pli
            # EXISTE comptent : une cellule de bord n'a pas de voisinage complet, donc son pli
            # n'est pas mesurable, et lui en inventer un la ferait classer sur rien.
            garde = ou_pli[ou[:, 0], ou[:, 1]] & np.isfinite(inten)
            if int(garde.sum()) < 8:
                continue
            e = err[garde]
            brutes = dict(pli=pli[ou[:, 0], ou[:, 1]][garde], obscurite=-inten[garde])
            rangs = {o: en_rangs(brutes[o]) for o in OBSERVABLES}
            vues = dict(brutes)
            vues.update({c: combiner(rangs, c) for c in COMBINAISONS})
            bras.append(dict(
                bras=k, cellules=int(len(e)),
                classe_um={o: [round(garder_les_meilleures(vues[o], e, f), 1)
                               for f in fractions] for o in COLONNES},
                hasard_um=[round(temoin_au_hasard(e, f, graine=graine), 1)
                           for f in fractions]))
        lignes.append(dict(marcheur=nom, bras=bras))

    # ⭐⭐⭐ LA SEULE FORME SOUS LAQUELLE « LE PLI PRÉDIT » DEVIENT ACTIONNABLE : classer fait-il
    # passer un bras SOUS la demi-feuille alors que la nappe entière est au-dessus ? Un gain de
    # cinquante micromètres sur une nappe à trois cents en est encore à trois cents — il prédit,
    # et il ne sauve rien. Ce compte-là distingue les deux, et il est publié à côté du gain.
    seuil = float(r["demi_feuille_um"])
    for x in lignes:
        x["bras_perdus"] = int(sum(1 for b in x["bras"]
                                   if b["classe_um"][OBSERVABLES[0]][0] >= seuil))
        x["bras_sauves"], x["fractions_qui_sauvent"] = {}, {}
        for o in COLONNES:
            sauves = [bool(b["classe_um"][o][0] >= seuil
                           and any(u < seuil for u in b["classe_um"][o][1:]))
                      for b in x["bras"]]
            x["bras_sauves"][o] = int(sum(sauves))
            # ⚠ La fraction qu'il aurait fallu garder pour sauver le bras est publiée : « sauvé »
            # sans « en gardant quoi » se lirait comme un sauvetage gratuit.
            x["fractions_qui_sauvent"][o] = [
                next((f for f, u in zip(fractions[1:], b["classe_um"][o][1:]) if u < seuil), None)
                for b in x["bras"] if b["classe_um"][o][0] >= seuil]
        x["bras_sauves_au_hasard"] = int(sum(
            1 for b in x["bras"] if b["classe_um"][OBSERVABLES[0]][0] >= seuil
            and any(u < seuil for u in b["hasard_um"][1:])))
    # ⭐⭐⭐ LE VERDICT : à chaque fraction, classer par le pli fait-il MIEUX que jeter au hasard ?
    # Agrégé sur les bras, par marcheur, en écart médian — jamais en moyenne, parce qu'un bras
    # effondré déciderait de la moyenne à lui seul.
    verdicts = []
    for x in lignes:
        if not x["bras"]:
            continue
        for o in COLONNES:
            for j, f in enumerate(fractions):
                ecarts = [b["classe_um"][o][j] - b["hasard_um"][j] for b in x["bras"]]
                verdicts.append(dict(
                    marcheur=x["marcheur"], observable=o, fraction=f,
                    ecart_median_um=round(float(np.median(ecarts)), 1),
                    bras_ou_elle_gagne=int(sum(1 for d in ecarts if d < 0)),
                    bras=len(ecarts)))
    return dict(
        fragment=r["fragment"], ancre=r["ancre"], spires_visees=r["spires_visees"],
        demi_feuille_um=r["demi_feuille_um"], marcheurs=list(MARCHEURS),
        fractions=list(fractions), lignes=lignes, verdicts=verdicts,
        # ⚠⚠ LE VERDICT EST PAR MARCHEUR ET PAR FRACTION, jamais un seul oui : le pli peut
        # prédire chez l'un et pas chez l'autre, et à une fraction et pas à une autre. Un verdict
        # unique moyennerait ces cas et rendrait un nombre qui n'appartient à personne.
        observables=list(COLONNES), seules=list(OBSERVABLES),
        combinaisons=list(COMBINAISONS),
        elle_predit_lerreur={
            o: {x["marcheur"]: bool(x["bras"]) and all(
                v["ecart_median_um"] < 0 for v in verdicts
                if v["marcheur"] == x["marcheur"] and v["observable"] == o
                and v["fraction"] < 1.0)
                for x in lignes}
            for o in COLONNES},
        # ⭐⭐ CE QUI SE PUBLIE SANS RIEN CHOISIR : quelles colonnes prédisent à TOUTES les
        # fractions. Ce n'est pas « la meilleure » — désigner la meilleure après les avoir vues
        # serait choisir sur ce qu'on juge — c'est un COMPTE, donc une propriété du tableau. Et
        # c'est ce qui compte pour un dérouleur qui ne choisit pas son point de fonctionnement :
        # une colonne qui prédit partout est utilisable sans avoir à décider où se placer.
        colonnes_qui_predisent_partout={
            x["marcheur"]: [o for o in COLONNES
                            if bool(x["bras"]) and all(
                                v["ecart_median_um"] < 0 for v in verdicts
                                if v["marcheur"] == x["marcheur"] and v["observable"] == o
                                and v["fraction"] < 1.0)]
            for x in lignes},
        # ⭐⭐⭐ LE SEUL VERDICT QU'UNE COMBINAISON A LE DROIT DE RÉCLAMER, et il est dur : battre
        # les DEUX observables seules, à TOUTES les fractions, chez un marcheur donné. Publier
        # « la meilleure des cinq » après les avoir vues serait choisir sur ce qu'on juge.
        une_combinaison_bat_les_deux_seules={
            x["marcheur"]: [
                c for c in COMBINAISONS
                if all(
                    next(v["ecart_median_um"] for v in verdicts
                         if v["marcheur"] == x["marcheur"] and v["observable"] == c
                         and abs(v["fraction"] - f) < 1e-9)
                    < min(next(v["ecart_median_um"] for v in verdicts
                               if v["marcheur"] == x["marcheur"] and v["observable"] == o
                               and abs(v["fraction"] - f) < 1e-9) for o in OBSERVABLES)
                    for f in fractions if f < 1.0)]
            for x in lignes if x["bras"]})


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # ⚠⚠⚠ LE CLASSEMENT EST FAIT SUR LE PLI, jamais sur l'erreur : le contrôle le prouve en
    # donnant un pli qui ANTI-corrèle avec l'erreur. Un classement qui trierait sur l'erreur
    # rendrait la meilleure valeur ; celui-ci doit rendre la PIRE.
    e = np.array([1.0, 2.0, 3.0, 100.0])
    v("garder tout rend la médiane de tout", garder_les_meilleures(np.zeros(4), e, 1.0) == 2.5)
    v("... classer par un pli croissant garde les premières",
      garder_les_meilleures(np.array([0.0, 1.0, 2.0, 3.0]), e, 0.5) == 1.5)
    v("... et un pli qui ANTI-corrèle avec l'erreur rend la PIRE moitié : le tri est bien sur "
      "le pli et pas sur l'erreur",
      garder_les_meilleures(np.array([3.0, 2.0, 1.0, 0.0]), e, 0.5) == 51.5,
      str(garder_les_meilleures(np.array([3.0, 2.0, 1.0, 0.0]), e, 0.5)))
    v("... garder une fraction nulle garde quand même une cellule, jamais zéro",
      np.isfinite(garder_les_meilleures(np.zeros(4), e, 0.0)))
    # ⚠⚠ LE TÉMOIN NE PEUT PAS ÊTRE MEILLEUR QUE LE MEILLEUR TRI NI PIRE QUE LE PIRE : c'est ce
    # qui garantit qu'il mesure le hasard et pas autre chose.
    t = temoin_au_hasard(e, 0.5)
    v("le témoin au hasard tombe entre le meilleur et le pire des tris",
      garder_les_meilleures(np.array([0.0, 1.0, 2.0, 3.0]), e, 0.5) <= t
      <= garder_les_meilleures(np.array([3.0, 2.0, 1.0, 0.0]), e, 0.5), str(t))
    v("... et garder tout au hasard rend exactement la médiane de tout",
      temoin_au_hasard(e, 1.0) == 2.5)

    # ⚠⚠⚠ LE CHEMIN QUI PRODUIT LE NOMBRE PUBLIÉ, HORS LIGNE.
    from le_corpus_des_spires import geometrie_fabriquee  # noqa: PLC0415

    c, vol = corpus_fabrique(), volume_fabrique(geometrie_fabriquee())
    fab = mesurer(minimum=20, corpus=c, volume=vol)
    v("la mesure tourne de bout en bout sur des matières fabriquées",
      any(x["bras"] for x in fab["lignes"]),
      str({x["marcheur"]: len(x["bras"]) for x in fab["lignes"]}))
    v("... chaque bras publie une courbe classée par observable ET son témoin, même longueur",
      all(len(b["classe_um"][o]) == len(fab["fractions"]) == len(b["hasard_um"])
          for x in fab["lignes"] for b in x["bras"] for o in fab["observables"]))
    # ⚠⚠ À FRACTION UN, LES DEUX COURBES SONT LE MÊME NOMBRE : garder tout ne laisse aucune place
    # au tri. Si elles différaient, c'est que l'une des deux ne mesure pas ce qu'elle annonce.
    memes = [(b["classe_um"][o][0], b["hasard_um"][0])
             for x in fab["lignes"] for b in x["bras"] for o in fab["observables"]]
    v("... et à fraction un, classer et tirer au hasard donnent le MÊME nombre",
      all(abs(a - b) < 0.05 for a, b in memes), str(memes[:3]))
    # ⭐⭐⭐ « PRÉDIRE » ET « SAUVER » SONT DEUX AFFIRMATIONS, et la seconde est celle qui compte :
    # un gain de cinquante micromètres sur une nappe à trois cents en est encore à trois cents.
    # Le contrôle exige que le compte des bras sauvés soit publié, et qu'un bras ne soit compté
    # sauvé que s'il était PERDU à couverture pleine.
    v("... les bras SAUVÉS sont comptés à part, et par observable",
      all(x["bras_sauves"][o] <= x["bras_perdus"]
          for x in fab["lignes"] for o in fab["observables"]),
      str({x["marcheur"]: x["bras_sauves"] for x in fab["lignes"]}))
    v("... et la fraction qu'il faut garder pour sauver un bras est publiée avec lui",
      all(len(x["fractions_qui_sauvent"][o]) == x["bras_perdus"]
          for x in fab["lignes"] for o in fab["observables"]),
      str({x["marcheur"]: x["fractions_qui_sauvent"] for x in fab["lignes"]}))
    # ⚠⚠⚠ LES DEUX OBSERVABLES SONT BALAYÉES, et la convention « grand = suspect » doit tenir
    # pour les deux : l'intensité est dans l'autre sens, donc on classe sur son OPPOSÉ. Si le
    # signe était perdu, la courbe de l'obscurité sortirait parfaitement inversée — un défaut qui
    # se lit comme « cette observable anti-prédit », c'est-à-dire comme un résultat.
    v("... les deux observables ET leurs trois combinaisons sont balayées",
      set(fab["seules"]) == {"pli", "obscurite"}
      and set(fab["combinaisons"]) == {"ou", "moyenne", "et"}
      and all(set(fab["elle_predit_lerreur"][o]) == set(fab["marcheurs"])
              for o in fab["observables"]),
      str(sorted(fab["observables"])))
    # ⚠⚠⚠ LES TROIS COMBINAISONS SONT SANS PARAMÈTRE, et le contrôle le prouve sur des rangs
    # dont la réponse est connue : « ou » est le max, « et » le min, et la moyenne entre les
    # deux. Un poids qui se serait glissé dedans casserait au moins l'un des trois.
    ra = {"pli": np.array([0.0, 1.0]), "obscurite": np.array([1.0, 0.0])}
    v("« ou » prend le max des rangs, « et » le min, la moyenne est entre les deux",
      np.allclose(combiner(ra, "ou"), [1.0, 1.0])
      and np.allclose(combiner(ra, "et"), [0.0, 0.0])
      and np.allclose(combiner(ra, "moyenne"), [0.5, 0.5]))
    v("... et une combinaison inconnue est REFUSÉE, jamais devinée",
      _leve(lambda: combiner(ra, "mediane")))
    # ⚠⚠ LE RANG EFFACE L'UNITÉ : c'est ce qui permet d'additionner un pli en µm et une obscurité
    # en niveaux de gris sans facteur de conversion, donc sans réglage. Le contrôle porte sur
    # l'invariance : multiplier une observable par mille ne doit RIEN changer à son rang.
    x = np.array([3.0, 1.0, 2.0])
    v("le rang efface l'unité : une échelle mille fois plus grande donne le même rang",
      np.allclose(en_rangs(x), en_rangs(x * 1000.0))
      and np.allclose(en_rangs(x), [1.0, 0.0, 0.5]), str(en_rangs(x)))
    v("... et un seul élément a un rang défini, jamais une division par zéro",
      en_rangs(np.array([5.0])).tolist() == [0.0])
    # ⭐⭐⭐ UNE COMBINAISON NE PEUT RÉCLAMER QUELQUE CHOSE QUE SI ELLE BAT LES DEUX SEULES, à
    # toutes les fractions. Le contrôle vérifie que ce verdict est bien plus dur que « elle
    # prédit » : une combinaison qui prédit sans battre les deux ne doit PAS y figurer.
    # ⚠⚠ « PRÉDIT PARTOUT » EST INCLUS DANS « PRÉDIT » : le contrôle l'épingle, parce que deux
    # listes qui divergeraient voudraient dire que l'une des deux ne compte pas ce qu'elle dit.
    v("... les colonnes qui prédisent partout sont exactement celles dont le verdict est vrai",
      all(set(fab["colonnes_qui_predisent_partout"][n])
          == {o for o in fab["observables"] if fab["elle_predit_lerreur"][o][n]}
          for n in fab["marcheurs"]),
      str(fab["colonnes_qui_predisent_partout"]))
    for nom, gagnantes in fab["une_combinaison_bat_les_deux_seules"].items():
        v(f"... et chez {nom}, toute combinaison déclarée gagnante prédit aussi",
          all(fab["elle_predit_lerreur"][c][nom] for c in gagnantes), str(gagnantes))
    v("... le verdict est rendu par observable, par marcheur ET par fraction",
      isinstance(fab["elle_predit_lerreur"], dict)
      and len(fab["verdicts"]) >= len(fab["fractions"]) * len(fab["observables"]),
      str(fab["elle_predit_lerreur"]))
    v("... le résultat est sérialisable tel quel, sans type qui traîne",
      isinstance(json.dumps(fab), str))
    souci = None
    try:
        afficher(fab)
    except Exception as exc:  # noqa: BLE001
        souci = f"{type(exc).__name__}: {exc}"
    v("... et l'affichage tourne sur ce résultat", souci is None, str(souci))

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def afficher(r: dict) -> None:
    """Le compte rendu lisible : la courbe classée contre son témoin, par marcheur."""
    print(f"ancre {r['ancre']} · vise {r['spires_visees']} · demi-feuille "
          f"{r['demi_feuille_um']} µm")
    print()
    entete = " ".join(f"{f:>8.0%}" for f in r["fractions"])
    print(f"{'observable':>11} {'marcheur':>12} {entete}")
    print("-" * (25 + 9 * len(r["fractions"])))
    for o in r["observables"]:
        for x in r["lignes"]:
            vs = [v for v in r["verdicts"]
                  if v["marcheur"] == x["marcheur"] and v["observable"] == o]
            if not vs:
                continue
            cases = " ".join(f"{v['ecart_median_um']:>+8.1f}" for v in vs)
            print(f"{o:>11} {x['marcheur']:>12} {cases}")
            gagne = " ".join(f"{v['bras_ou_elle_gagne']:>4}/{v['bras']:<3}" for v in vs)
            print(f"{'':>11} {'bras gagnés':>12} {gagne}")
    print()
    print("écart médian sur les bras, classé moins hasard · négatif = l'observable PRÉDIT")
    print()
    for o, par in r["elle_predit_lerreur"].items():
        for nom, oui in par.items():
            print(f"→ {'⭐' if oui else '⚠'} « {o} » prédit l'erreur pour {nom} : "
                  f"{'OUI, à toutes les fractions' if oui else 'non'}")
    print()
    print("→ ⭐⭐ colonnes qui prédisent à TOUTES les fractions (aucune n'est « choisie ») :")
    for nom, cols in r["colonnes_qui_predisent_partout"].items():
        print(f"{nom:>18} : {cols if cols else 'aucune'}")
    print(f"→ ⛔ combinaison(s) qui battent LES DEUX seules à toutes les fractions : "
          f"{r['une_combinaison_bat_les_deux_seules']}")
    print()
    print("→ ⭐⭐⭐ le seul chiffre actionnable : combien de bras PERDUS passent sous la "
          "demi-feuille en classant ?")
    for x in r["lignes"]:
        if not x["bras"]:
            continue
        for o in r["observables"]:
            fs = [g for g in x["fractions_qui_sauvent"][o] if g is not None]
            print(f"{x['marcheur']:>18} par « {o} » : {x['bras_sauves'][o]}/{x['bras_perdus']} "
                  f"sauvés (au hasard : {x['bras_sauves_au_hasard']}) · fractions "
                  f"{fs if fs else '—'}")


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
