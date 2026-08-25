#!/usr/bin/env python3
"""Rendre la fenêtre LARGE donne la fenêtre ÉTROITE — l'arithmétique, dite une seule fois.

⚠⚠ POURQUOI CE FICHIER EXISTE. Mesuré le 2026-08-25 sur `data/` : **58,6 % du contenu
identique du dépôt** sont des tranches partagées entre deux largeurs de fenêtre. Une fenêtre de
31 couches est le **centre** d'une fenêtre de 81 rendue au même endroit, donc la tranche `i` de
l'une **est** la tranche `i + 25` de l'autre, octet pour octet — 2232 groupes pour la paire
(31, 81), 861 pour (41, 161), c'est-à-dire exactement la série de convergence du dépôt.

  ⭐ La conséquence n'est pas du disque, c'est du TEMPS DE RENDU : une campagne de convergence
    peut rendre UNE fois à la fenêtre la plus large et dériver les autres.

⭐ Et il n'y a **rien à construire** : `depth_profile.py` porte déjà `--from-layer`,
`--to-layer` et `--traced-layer`. Ce qui manquait n'est pas une capacité, c'est **l'arithmétique
énoncée une fois** au lieu d'être recalculée à chaque site d'appel. Vérifié sur
`spires_pas0125_compense/spire06` : les 31 tranches identiques, et **23 mesures de profil
identiques sur 23**, zéro différence.

⚠⚠ CE QUI FAIT REFUSER, et chacun est une panne évitée :

  - **des parités différentes.** Le dépôt indexe le centre d'une pile de N tranches à `N // 2`
    (c'est ce que `profiler_une_surface.sh` passe en `--traced-layer`). Deux piles dont les
    largeurs n'ont pas la même parité ont donc des centres physiques décalés d'une DEMI-tranche,
    et aucun découpage entier ne les fait coïncider. Dériver quand même rendrait un profil
    décalé, ce qui est pire qu'un rendu de plus : c'est un résultat faux qui a l'air d'un
    résultat.
  - **une fenêtre plus large que la large.** Il n'y a rien à en extraire.
  - **la même largeur.** Ce n'est pas une dérivation, c'est le fichier lui-même, et le dire
    ainsi évite qu'un appelant croie avoir économisé un rendu.

⚠ La formule est `D = N_large // 2 - N_étroite // 2`, et **pas** `(N_large - N_étroite) / 2`.
Les deux coïncident quand les parités sont les mêmes — donc sur toute la série du dépôt, qui
est impaire — mais la première suit la convention du dépôt (`N // 2`) tandis que la seconde
n'est même pas entière dès que les parités diffèrent. Écrire celle qui est toujours définie
rend le refus explicite au lieu d'être un plantage.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


class PileInexploitable(ValueError):
    """La pile ne porte pas les tranches que la dérivation suppose."""


def verifier_pile(dossier: Path, largeur: int) -> None:
    """La pile est-elle exactement `largeur` tranches numérotées 0..largeur-1 ?

    ⚠⚠ POURQUOI CE CONTRÔLE EXISTE. `depth_profile.py` filtre sur `first <= int(p.stem) <= last`
    (ligne 54) : **D et F sont des NUMÉROS DE FICHIER, pas des positions**. Sur une pile trouée
    ou numérotée autrement, la sous-plage ne désigne donc pas les tranches qu'on croit — et
    elle **échoue en silence**, en rendant un profil plus court plutôt qu'une erreur. Trouvé par
    réfutation adversariale le 2026-08-25, sur une condition que rien ne vérifiait.

    ⚠ Le remplissage de zéros n'a aucune importance : `060.tif` et `60.tif` valent tous deux 60,
    et une pile de ce dépôt utilise réellement trois chiffres. Ce qui compte est l'ENSEMBLE des
    numéros, pas la forme des noms.
    """
    if not dossier.is_dir():
        raise PileInexploitable(f"{dossier} n'est pas un dossier de rendu")
    numeros = []
    for f in dossier.iterdir():
        if f.suffix != ".tif":
            continue
        try:
            numeros.append(int(f.stem))
        except ValueError:
            raise PileInexploitable(
                f"{dossier} contient « {f.name} », dont le nom n'est pas un numéro de tranche : "
                f"la sous-plage désigne des NUMÉROS, donc elle ne saurait pas quoi en faire")
    attendus = set(range(largeur))
    vus = set(numeros)
    if len(numeros) != len(vus):
        raise PileInexploitable(f"{dossier} porte des numéros de tranche en double")
    if vus != attendus:
        manque = sorted(attendus - vus)[:5]
        trop = sorted(vus - attendus)[:5]
        raise PileInexploitable(
            f"{dossier} devrait porter les tranches 0..{largeur - 1} et ne les porte pas"
            + (f" — manquent {manque}" if manque else "")
            + (f" — en trop {trop}" if trop else ""))


class DerivationImpossible(ValueError):
    """La fenêtre étroite ne se découpe pas exactement dans la large."""


def centre(largeur: int) -> int:
    """L'indice de la tranche centrale, selon la convention du dépôt : `N // 2`.

    ⚠ C'est exactement ce que `profiler_une_surface.sh` passe en `--traced-layer`. Une seconde
    convention ici ferait diverger la dérivation de ce qu'elle prétend reproduire.
    """
    return largeur // 2


def peut_deriver(large: int, etroite: int) -> tuple[bool, str]:
    """La fenêtre étroite se découpe-t-elle exactement dans la large, et sinon pourquoi."""
    if large <= 0 or etroite <= 0:
        return False, "une largeur de fenêtre est un entier strictement positif"
    if etroite > large:
        return False, f"la fenêtre {etroite} est plus large que {large} : rien à en extraire"
    if etroite == large:
        return False, f"{etroite} == {large} : c'est le rendu lui-même, pas une dérivation"
    if large % 2 != etroite % 2:
        return False, (f"parités différentes ({large} et {etroite}) : les centres sont décalés "
                       f"d'une demi-tranche et aucun découpage entier ne les fait coïncider")
    return True, ""


def arguments_sous_fenetre(large: int, etroite: int) -> dict:
    """Les trois arguments à passer à `depth_profile.py` sur le rendu LARGE.

    Rend `from_layer`, `to_layer`, `traced_layer` — plus `decalage` et `couches`, pour qu'un
    lecteur puisse vérifier le compte sans refaire l'arithmétique.
    """
    ok, raison = peut_deriver(large, etroite)
    if not ok:
        raise DerivationImpossible(raison)
    d = centre(large) - centre(etroite)
    return {
        "from_layer": d,
        "to_layer": d + etroite - 1,
        "traced_layer": centre(large),
        "decalage": d,
        "couches": etroite,
    }


def plan_de_campagne(fenetres: list[int]) -> dict:
    """Pour une série de fenêtres, ce qu'il faut rendre et ce qui se dérive.

    ⚠ La plus large est rendue ; toute fenêtre de même parité s'en dérive. Une fenêtre de
    parité différente est RENDUE elle aussi, et le plan le dit : la taire ferait croire que la
    campagne coûte moins qu'elle ne coûte.
    """
    if not fenetres:
        return {"rendues": [], "derivees": [], "economie": 0}
    uniques = sorted(set(fenetres), reverse=True)
    rendues, derivees = [], []
    for f in uniques:
        pere = next((r for r in rendues if peut_deriver(r, f)[0]), None)
        if pere is None:
            rendues.append(f)
        else:
            derivees.append({"fenetre": f, "depuis": pere, **arguments_sous_fenetre(pere, f)})
    return {"rendues": rendues, "derivees": derivees, "economie": len(derivees)}


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool) -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}")

    # --- la paire mesurée sur le disque, celle qui a tout déclenché ---
    a = arguments_sous_fenetre(81, 31)
    v("(31 dans 81) donne le décalage MESURÉ sur le disque", a["decalage"] == 25)
    v("... et la plage couvre exactement 31 couches",
      a["to_layer"] - a["from_layer"] + 1 == 31 and a["from_layer"] == 25 and a["to_layer"] == 55)
    v("... et la couche tracée est le centre de la LARGE", a["traced_layer"] == 40)

    b = arguments_sous_fenetre(161, 41)
    v("(41 dans 161) donne le décalage mesuré", b["decalage"] == 60)
    v("... et la plage couvre exactement 41 couches",
      b["to_layer"] - b["from_layer"] + 1 == 41 and b["from_layer"] == 60 and b["to_layer"] == 100)
    v("... et la couche tracée est le centre de la large", b["traced_layer"] == 80)

    # ⭐ La propriété qui fait tenir l'ensemble : la tranche centrale de l'étroite tombe sur la
    # tranche centrale de la large. C'est ce que « le même endroit » veut dire.
    for large, etroite in ((81, 31), (161, 41), (161, 81), (81, 41), (999, 3)):
        x = arguments_sous_fenetre(large, etroite)
        if x["from_layer"] + centre(etroite) != centre(large):
            v(f"le centre de {etroite} tombe sur le centre de {large}", False)
            break
    else:
        v("le centre de l'étroite tombe TOUJOURS sur le centre de la large", True)

    # ⚠ Et la sous-plage ne déborde jamais de la pile large.
    for large, etroite in ((81, 31), (161, 41), (161, 159), (81, 79), (7, 1)):
        x = arguments_sous_fenetre(large, etroite)
        if x["from_layer"] < 0 or x["to_layer"] > large - 1:
            v(f"la plage de {etroite} tient dans {large}", False)
            break
    else:
        v("la sous-plage tient TOUJOURS dans la pile large", True)

    # --- les refus, un par panne ---
    cas = [
        ((81, 82), "plus large"), ((81, 81), "elle-même"), ((80, 31), "parités"),
        ((81, 30), "parités"), ((0, 3), "positif"), ((81, -1), "positif"),
    ]
    for (large, etroite), attendu in cas:
        try:
            arguments_sous_fenetre(large, etroite)
            v(f"({etroite} dans {large}) est refusé", False)
        except DerivationImpossible as e:
            v(f"({etroite} dans {large}) est refusé — {str(e)[:34]}…", True)

    # ⚠⚠ Le contrôle qui empêche le raccourci de mentir : la formule naïve
    # `(large - etroite) / 2` coïncide sur toute la série du dépôt, et n'est même pas entière
    # dès que les parités diffèrent. C'est pour ça que le refus existe.
    v("sur la série du dépôt, la formule du dépôt et la naïve coïncident",
      all(arguments_sous_fenetre(L, E)["decalage"] == (L - E) // 2
          for L, E in ((81, 31), (161, 41), (161, 81), (81, 41))))
    v("... et la naïve serait fractionnaire là où on refuse", (80 - 31) % 2 == 1)

    # --- la pile elle-meme : la condition que RIEN ne verifiait ---
    # ⚠⚠ D et F sont des NUMEROS DE FICHIER (depth_profile.py:54), pas des positions. Sur une
    # pile trouee, la sous-plage ne designe pas les tranches qu'on croit -- et elle echoue en
    # SILENCE, en rendant un profil plus court. Trouve par refutation adversariale.
    import shutil as _sh
    import tempfile as _tf
    d = Path(_tf.mkdtemp())
    (d / "saine").mkdir()
    for i in range(5):
        (d / "saine" / f"{i:02d}.tif").write_bytes(b"x")
    verifier_pile(d / "saine", 5)
    v("une pile contigue de 0 a N-1 passe", True)

    # ⚠ Le remplissage de zeros n'a aucune importance : une pile du depot utilise VRAIMENT
    # trois chiffres (data/paris4_candidats/m7_c0/rendu_161 : 060.tif).
    (d / "trois").mkdir()
    for i in range(5):
        (d / "trois" / f"{i:03d}.tif").write_bytes(b"x")
    verifier_pile(d / "trois", 5)
    v("... quel que soit le remplissage de zeros du nom", True)

    for nom, fab, attendu in (
        ("trouee", lambda p: [(p / f"{i:02d}.tif").write_bytes(b"x") for i in (0, 1, 3, 4, 5)], "manquent"),
        ("decalee", lambda p: [(p / f"{i:02d}.tif").write_bytes(b"x") for i in range(1, 6)], "manquent"),
        ("nommee", lambda p: [(p / n).write_bytes(b"x") for n in
                              ("00.tif", "01.tif", "02.tif", "03.tif", "tranche.tif")], "numéro"),
    ):
        (d / nom).mkdir()
        fab(d / nom)
        try:
            verifier_pile(d / nom, 5)
            v(f"une pile {nom} est REFUSEE", False)
        except PileInexploitable as e:
            v(f"une pile {nom} est REFUSEE — {attendu in str(e)}", attendu in str(e))

    try:
        verifier_pile(d / "nexiste_pas", 5)
        v("un dossier absent est refuse", False)
    except PileInexploitable:
        v("un dossier absent est refuse", True)
    _sh.rmtree(d, ignore_errors=True)

    # --- le plan de campagne ---
    p = plan_de_campagne([31, 81])
    v("une série de deux ne rend que la plus large", p["rendues"] == [81])
    v("... et dérive l'autre", [d["fenetre"] for d in p["derivees"]] == [31])
    p = plan_de_campagne([31, 41, 81, 161])
    v("une série de quatre ne rend QU'UNE fenêtre", p["rendues"] == [161])
    v("... et en dérive trois", p["economie"] == 3)
    v("... toutes depuis la plus large",
      all(d["depuis"] == 161 for d in p["derivees"]))
    # ⚠ Une parité différente est RENDUE, et le plan le DIT : la taire ferait croire que la
    # campagne coûte moins qu'elle ne coûte.
    p = plan_de_campagne([31, 80, 81])
    v("une fenêtre de parité différente est rendue, pas dérivée en silence",
      sorted(p["rendues"]) == [80, 81] and p["economie"] == 1)
    v("une série vide ne fait pas planter", plan_de_campagne([]) == {"rendues": [], "derivees": [], "economie": 0})
    v("un doublon dans la série ne compte qu'une fois",
      plan_de_campagne([81, 81, 31])["rendues"] == [81])

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("fenetres", nargs="*", type=int, help="la série de fenêtres d'une campagne")
    p.add_argument("--json", action="store_true", help="sortie machine")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if not a.fenetres:
        p.error("au moins une largeur de fenêtre est requise")
    plan = plan_de_campagne(a.fenetres)
    if a.json:
        print(json.dumps(plan, indent=1))
        return 0
    print(f"à rendre : {', '.join(str(f) for f in plan['rendues'])}")
    for d in plan["derivees"]:
        print(f"  n={d['fenetre']:<4} se dérive de n={d['depuis']} : "
              f"--from-layer {d['from_layer']} --to-layer {d['to_layer']} "
              f"--traced-layer {d['traced_layer']}")
    print(f"  {plan['economie']} rendu(s) évité(s) sur {len(set(a.fenetres))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
