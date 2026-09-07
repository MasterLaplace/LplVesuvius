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
# ⚠ Les fractions gardées sont un balayage, pas des réglages : la courbe entière est l'objet
# livré. Elles descendent jusqu'à un dixième parce qu'en dessous la médiane porte sur si peu de
# cellules qu'elle mesure surtout le tirage.
FRACTIONS = (1.0, 0.9, 0.75, 0.5, 0.35, 0.25, 0.1)
TIRAGES = 60


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
        for k, ((pli, ou_pli), (ou, err)) in enumerate(zip(champs[nom], parcelles[nom]),
                                                       start=1):
            # ⚠⚠ LE PLI ET L'ERREUR SONT LUS SUR LES MÊMES CELLULES, et seules celles où le pli
            # EXISTE comptent : une cellule de bord n'a pas de voisinage complet, donc son pli
            # n'est pas mesurable, et lui en inventer un la ferait classer sur rien.
            garde = ou_pli[ou[:, 0], ou[:, 1]]
            if int(garde.sum()) < 8:
                continue
            p, e = pli[ou[:, 0], ou[:, 1]][garde], err[garde]
            bras.append(dict(
                bras=k, cellules=int(len(e)),
                classe_um=[round(garder_les_meilleures(p, e, f), 1) for f in fractions],
                hasard_um=[round(temoin_au_hasard(e, f, graine=graine), 1)
                           for f in fractions]))
        lignes.append(dict(marcheur=nom, bras=bras))

    # ⭐⭐⭐ LA SEULE FORME SOUS LAQUELLE « LE PLI PRÉDIT » DEVIENT ACTIONNABLE : classer fait-il
    # passer un bras SOUS la demi-feuille alors que la nappe entière est au-dessus ? Un gain de
    # cinquante micromètres sur une nappe à trois cents en est encore à trois cents — il prédit,
    # et il ne sauve rien. Ce compte-là distingue les deux, et il est publié à côté du gain.
    seuil = float(r["demi_feuille_um"])
    for x in lignes:
        sauves, sauves_au_hasard = [], []
        for b in x["bras"]:
            perdu = b["classe_um"][0] >= seuil
            sauves.append(bool(perdu and any(u < seuil for u in b["classe_um"][1:])))
            sauves_au_hasard.append(bool(perdu and any(u < seuil for u in b["hasard_um"][1:])))
        x["bras_sauves"] = int(sum(sauves))
        x["bras_sauves_au_hasard"] = int(sum(sauves_au_hasard))
        x["bras_perdus"] = int(sum(1 for b in x["bras"] if b["classe_um"][0] >= seuil))
        # ⚠ La fraction qu'il aurait fallu garder pour sauver le bras est publiée : « sauvé »
        # sans « en gardant quoi » se lirait comme un sauvetage gratuit.
        x["fractions_qui_sauvent"] = [
            next((f for f, u in zip(fractions[1:], b["classe_um"][1:]) if u < seuil), None)
            for b in x["bras"] if b["classe_um"][0] >= seuil]
    # ⭐⭐⭐ LE VERDICT : à chaque fraction, classer par le pli fait-il MIEUX que jeter au hasard ?
    # Agrégé sur les bras, par marcheur, en écart médian — jamais en moyenne, parce qu'un bras
    # effondré déciderait de la moyenne à lui seul.
    verdicts = []
    for x in lignes:
        if not x["bras"]:
            continue
        for j, f in enumerate(fractions):
            ecarts = [b["classe_um"][j] - b["hasard_um"][j] for b in x["bras"]]
            verdicts.append(dict(
                marcheur=x["marcheur"], fraction=f,
                ecart_median_um=round(float(np.median(ecarts)), 1),
                bras_ou_le_pli_gagne=int(sum(1 for d in ecarts if d < 0)),
                bras=len(ecarts)))
    return dict(
        fragment=r["fragment"], ancre=r["ancre"], spires_visees=r["spires_visees"],
        demi_feuille_um=r["demi_feuille_um"], marcheurs=list(MARCHEURS),
        fractions=list(fractions), lignes=lignes, verdicts=verdicts,
        # ⚠⚠ LE VERDICT EST PAR MARCHEUR ET PAR FRACTION, jamais un seul oui : le pli peut
        # prédire chez l'un et pas chez l'autre, et à une fraction et pas à une autre. Un verdict
        # unique moyennerait ces cas et rendrait un nombre qui n'appartient à personne.
        le_pli_predit_lerreur={
            x["marcheur"]: bool(x["bras"]) and all(
                v["ecart_median_um"] < 0
                for v in verdicts if v["marcheur"] == x["marcheur"] and v["fraction"] < 1.0)
            for x in lignes})


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
    v("... chaque bras publie une courbe classée ET son témoin, de même longueur",
      all(len(b["classe_um"]) == len(fab["fractions"]) == len(b["hasard_um"])
          for x in fab["lignes"] for b in x["bras"]))
    # ⚠⚠ À FRACTION UN, LES DEUX COURBES SONT LE MÊME NOMBRE : garder tout ne laisse aucune place
    # au tri. Si elles différaient, c'est que l'une des deux ne mesure pas ce qu'elle annonce.
    memes = [(b["classe_um"][0], b["hasard_um"][0])
             for x in fab["lignes"] for b in x["bras"]]
    v("... et à fraction un, classer et tirer au hasard donnent le MÊME nombre",
      all(abs(a - b) < 0.05 for a, b in memes), str(memes[:3]))
    # ⭐⭐⭐ « PRÉDIRE » ET « SAUVER » SONT DEUX AFFIRMATIONS, et la seconde est celle qui compte :
    # un gain de cinquante micromètres sur une nappe à trois cents en est encore à trois cents.
    # Le contrôle exige que le compte des bras sauvés soit publié, et qu'un bras ne soit compté
    # sauvé que s'il était PERDU à couverture pleine.
    v("... les bras SAUVÉS sont comptés à part des bras où le pli prédit",
      all("bras_sauves" in x and x["bras_sauves"] <= x["bras_perdus"] for x in fab["lignes"]),
      str({x["marcheur"]: (x["bras_sauves"], x["bras_perdus"]) for x in fab["lignes"]}))
    v("... et la fraction qu'il faut garder pour sauver un bras est publiée avec lui",
      all(len(x["fractions_qui_sauvent"]) == x["bras_perdus"] for x in fab["lignes"]),
      str({x["marcheur"]: x["fractions_qui_sauvent"] for x in fab["lignes"]}))
    v("... le verdict est rendu par marcheur ET par fraction, jamais en un seul oui",
      isinstance(fab["le_pli_predit_lerreur"], dict)
      and len(fab["verdicts"]) >= len(fab["fractions"]),
      str(fab["le_pli_predit_lerreur"]))
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
    for x in r["lignes"]:
        if not x["bras"]:
            continue
        print(f"{x['marcheur']} — erreur médiane (µm) selon la part de nappe GARDÉE")
        print(f"{'bras':>6} {entete}")
        for b in x["bras"]:
            cl = " ".join(f"{u:>8.1f}" for u in b["classe_um"])
            ha = " ".join(f"{u:>8.1f}" for u in b["hasard_um"])
            print(f"{b['bras']:>6} {cl}   classé par le pli")
            print(f"{'':>6} {ha}   au hasard")
        print()
    print("→ écart médian sur les bras, classé moins hasard (négatif = le pli prédit) :")
    for x in r["lignes"]:
        vs = [v for v in r["verdicts"] if v["marcheur"] == x["marcheur"]]
        if not vs:
            continue
        cases = " ".join(f"{v['ecart_median_um']:>+8.1f}" for v in vs)
        print(f"{x['marcheur']:>18} {cases}")
        gagne = " ".join(f"{v['bras_ou_le_pli_gagne']:>4}/{v['bras']:<3}" for v in vs)
        print(f"{'bras où il gagne':>18} {gagne}")
    print()
    for nom, oui in r["le_pli_predit_lerreur"].items():
        print(f"→ {'⭐' if oui else '⚠'} le pli prédit l'erreur pour {nom} : "
              f"{'OUI, à toutes les fractions' if oui else 'NON, pas à toutes les fractions'}")
    print()
    print("→ ⭐⭐⭐ et le seul chiffre actionnable : combien de bras PERDUS passent sous la "
          "demi-feuille en classant ?")
    for x in r["lignes"]:
        if not x["bras"]:
            continue
        print(f"{x['marcheur']:>18} : {x['bras_sauves']}/{x['bras_perdus']} bras perdus sauvés "
              f"(au hasard : {x['bras_sauves_au_hasard']}) · fractions qui sauvent "
              f"{x['fractions_qui_sauvent']}")


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
