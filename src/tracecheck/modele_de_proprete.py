#!/usr/bin/env python3
"""Le contrôle P1 bis : le basculement de propreté est-il plus raide que la seule taille ?

⚠⚠⚠ POURQUOI CE FICHIER EXISTE, ET C'EST UNE DETTE QUE JE ME SUIS FAITE. Le rapport
`docs/archive/registres/anteriorite_resultats_de_tete.md` §P1 bis annonce en toutes lettres
*« Vérification reproductible : `scratchpad/check_windcheck_model.py` (calcul dans l'arbre, pas
en ligne de commande) »* — **et ce fichier n'existe pas**. Le ×15,9 sur lequel repose tout
l'argument est donc un nombre publié dont le producteur n'est nulle part, c'est-à-dire
exactement ce que ce dépôt refuse ailleurs.

⚠⚠ ET LE REGISTRE DES TÂCHES DISAIT `D2` BLOQUÉ « sur une source absente de l'arbre ». C'était
faux : le rapport EST dans l'arbre, à `docs/archive/registres/anteriorite_resultats_de_tete.md:593`.
J'avais cherché un fichier *nommé* « budget » au lieu de chercher le **concept** — la règle que
ce dépôt écrit partout, et que j'ai enfreinte.

⭐⭐ LE MODÈLE PUBLIÉ. `windcheck` établit qu'une trace est propre avec une probabilité qui
décroît exponentiellement avec le nombre de cellules valides : @f$P(\\text{propre}) =
e^{-qN}@f$ avec @f$q = 7{,}2\\times 10^{-6}@f$ par cellule. Passer de **11 tirages propres sur
12** à **3 sur 12** exige donc :

$$N = \\frac{-\\ln p}{q} \\quad\\Rightarrow\\quad 12\\,085 \\to 192\\,540 \\text{ cellules},
\\ \\text{soit } \\times 15{,}9$$

pendant que l'aire observée ne fait que **×3,8** (19,83 → 75,85 cm², moyenne des deux rouleaux
au verdict). Si les cellules valides croissent proportionnellement à l'aire, le basculement est
**plus raide que l'arithmétique de taille** — donc le budget ferait quelque chose au-delà de
grandir.

⚠⚠⚠ ET C'EST CETTE HYPOTHÈSE-LÀ QUE LE RAPPORT LAISSE OUVERTE : *« cellules ∝ aire est une
hypothèse que l'article n'a pas vérifiée et qu'il peut trancher sur ses propres grilles »*. Les
grilles sont sur le disque, aux **deux** plafonds (`data/tirages/` à 120, `data/tirages_plafond/`
à 400). Ce fichier les compte.

⚠ Ce qu'il ne fait PAS : juger le modèle publié. `q` est repris tel quel ; si `windcheck` le
révise, le nombre bouge. Ce qui est mesuré ici est le **rapport** entre deux croissances, et un
rapport ne dépend pas de la valeur de `q` — c'est ce qui le rend robuste à cette reprise.

Usage :
    uv run python src/tracecheck/modele_de_proprete.py --verifier
    uv run python src/tracecheck/modele_de_proprete.py --json docs/mesures/p1bis.json
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path


RACINE = Path(__file__).resolve().parents[2]
ORIGINE = RACINE / "data" / "tirages"
RELEVE = RACINE / "data" / "tirages_plafond"

Q_PAR_CELLULE = 7.2e-6
"""Taux du modèle publié par `windcheck`, par cellule valide.

⚠ Repris tel quel, jamais réajusté sur nos données : le réajuster ferait de la confrontation
avec le modèle publié une confrontation avec nous-mêmes."""

MANQUANT = -1.0
"""Sentinelle d'une cellule absente dans un `.tifxyz`, comme dans `excision/proximity.py`.

⚠ La même valeur est écrite là-bas ; deux définitions d'« absent » compteraient deux
populations différentes sous un seul nom."""

ROULEAUX = ("PHerc0125", "PHerc0191")
"""Les deux rouleaux du verdict de `35` §3bis.

⚠⚠ `PHerc0358` est **exclu et nommé**, comme `comparer_plafond.py` l'exclut : il n'a qu'un seul
tirage, et un seul nombre ne se disperse pas. L'inclure ferait baisser la dispersion médiane
sans rien mesurer — et son aire monte ×10,7, donc l'inclure remonterait aussi le facteur observé
pour une raison qui n'est pas une mesure."""


def cellules_pour_proprete(part_propre: float, q: float = Q_PAR_CELLULE) -> float:
    """
    @brief Combien de cellules valides le modèle publié exige pour cette part de tirages propres.

    ⚠ `part_propre` est une PROBABILITÉ, pas un compte : passer 11 au lieu de 11/12 rendrait un
    logarithme de nombre positif, donc un compte négatif, sans lever.
    """
    if not 0.0 < part_propre <= 1.0:
        raise ValueError(f"part propre hors ]0, 1] : {part_propre}")
    return -math.log(part_propre) / q


def cellules_valides(grille: Path) -> int:
    """
    @brief Le nombre de cellules d'un `.tifxyz` dont les trois plans sont renseignés.

    ⚠ Les TROIS plans, pas un seul : une cellule dont `x` est posé et `z` absent n'est pas un
    point, et la compter gonflerait la population du côté où l'on cherche une croissance.
    """
    import tifffile

    valides = None
    for axe in ("x", "y", "z"):
        chemin = grille / f"{axe}.tif"
        if not chemin.is_file():
            raise FileNotFoundError(f"plan absent : {chemin}")
        plan = tifffile.imread(chemin)
        present = plan != MANQUANT
        valides = present if valides is None else (valides & present)
    return int(valides.sum())


def concordance_des_plans(grille: Path) -> dict:
    """
    @brief Les trois plans d'un `.tifxyz` déclarent-ils les mêmes cellules absentes ?

    ⚠⚠⚠ ÉCRIT PARCE QUE DEUX SONDES N'ONT RIEN TROUVÉ, ET C'EST LA BONNE RÉACTION. J'ai saboté
    `cellules_valides` de deux façons — compter **toutes** les cellules de la grille, puis
    n'en lire qu'**un seul** plan — et la batterie est restée verte les deux fois. Ce n'est pas
    une faiblesse du contrôle : c'est que sur ces grilles les trois plans s'accordent et que le
    remplissage est presque total, donc les trois comptages coïncident.

    ⚠⚠ Mais « ils coïncident ici » est une PROPRIÉTÉ DES DONNÉES, et s'y fier sans la mesurer
    est exactement ce que ce dépôt paie en boucle. Cette fonction la mesure, donc le jour où une
    grille aurait un `z` manquant là où son `x` est posé, le contrôle le dira au lieu de
    continuer à compter une population pour une autre.
    """
    import tifffile

    comptes, valides = {}, None
    for axe in ("x", "y", "z"):
        plan = tifffile.imread(grille / f"{axe}.tif")
        present = plan != MANQUANT
        comptes[axe] = int(present.sum())
        valides = present if valides is None else (valides & present)
    total = int(valides.size)
    return dict(par_plan=comptes, intersection=int(valides.sum()), total=total,
                plans_concordants=len(set(comptes.values())) == 1
                and comptes["x"] == int(valides.sum()),
                part_remplie=int(valides.sum()) / total if total else 0.0)


def _grille(tirage: Path) -> Path | None:
    """La grille `auto_grown_*` d'un tirage, ou None s'il n'a rien produit."""
    grilles = sorted(tirage.glob("auto_grown_*"))
    return grilles[0] if grilles else None


def _aire(tirage: Path) -> float | None:
    resume = tirage / "resume.json"
    if not resume.is_file():
        return None
    return json.loads(resume.read_text()).get("aire_cm2")


def recenser(racine: Path, rouleau: str) -> list[dict]:
    """
    @brief Chaque tirage d'un rouleau : ses cellules valides et son aire.

    ⚠ Les tirages sans grille sont rendus avec `cellules = None` plutôt que sautés : un tirage
    tué et un tirage vide ne sont pas la même chose, et les confondre ferait passer une campagne
    incomplète pour une campagne dont les traces sont petites.
    """
    dossier = racine / rouleau
    if not dossier.is_dir():
        return []
    out = []
    for tirage in sorted(dossier.iterdir()):
        if not tirage.is_dir():
            continue
        grille = _grille(tirage)
        out.append(dict(tirage=tirage.name,
                        cellules=cellules_valides(grille) if grille else None,
                        aire_cm2=_aire(tirage)))
    return out


def mediane(valeurs: list[float]) -> float | None:
    bons = sorted(v for v in valeurs if v is not None)
    if not bons:
        return None
    n = len(bons)
    return bons[n // 2] if n % 2 else 0.5 * (bons[n // 2 - 1] + bons[n // 2])


def confronter() -> dict:
    """
    @brief Le contrôle : la croissance des cellules valides suit-elle celle de l'aire ?

    ⚠⚠ MÉDIANES ET NON MOYENNES, comme `comparer_plafond.py`. Une campagne à plafond relevé
    porte des tirages qui atteignent le délai, donc des aires tronquées vers le bas ; une
    moyenne les laisserait tirer le facteur, une médiane non.
    """
    lignes = []
    densites = []
    for rouleau in ROULEAUX:
        avant, apres = recenser(ORIGINE, rouleau), recenser(RELEVE, rouleau)
        c_av, c_ap = mediane([x["cellules"] for x in avant]), mediane([x["cellules"] for x in apres])
        a_av, a_ap = mediane([x["aire_cm2"] for x in avant]), mediane([x["aire_cm2"] for x in apres])
        # ⚠⚠⚠ LA VRAIE FORME DU CONTRÔLE EST UNE DENSITÉ, PAS UN RAPPORT DE MÉDIANES. « Les
        # cellules croissent comme l'aire » se teste en regardant si le nombre de cellules PAR
        # cm² bouge : un rapport de médianes peut coïncider pour deux raisons et ne distingue
        # pas « proportionnel » de « également multiplié par hasard ».
        for lot, plafond in ((avant, 120), (apres, 400)):
            for x in lot:
                if x["cellules"] and x["aire_cm2"]:
                    densites.append(dict(rouleau=rouleau, plafond=plafond, tirage=x["tirage"],
                                         cellules=x["cellules"], aire_cm2=x["aire_cm2"],
                                         par_cm2=x["cellules"] / x["aire_cm2"]))
        lignes.append(dict(
            rouleau=rouleau, tirages_avant=len(avant), tirages_apres=len(apres),
            cellules_avant=c_av, cellules_apres=c_ap,
            aire_avant=a_av, aire_apres=a_ap,
            facteur_cellules=(c_ap / c_av) if c_av else None,
            facteur_aire=(a_ap / a_av) if a_av else None,
            # ⚠ Mesuré, et il faut le DIRE : au plafond d'origine les douze tirages des deux
            # rouleaux rendent EXACTEMENT 56 644 cellules valides sur une grille 242x242. Le
            # compte y est donc fixé par le PLAFOND, pas par la trace — c'est « la stabilité
            # était une troncature » vue d'un autre angle, et ça rend le point de départ
            # dégénéré. Ce qui sauve le contrôle est que la DENSITÉ, elle, est la même avant
            # et après.
            cellules_toutes_egales_avant=len({x["cellules"] for x in avant if x["cellules"]}) == 1))
    exige = cellules_pour_proprete(3 / 12) / cellules_pour_proprete(11 / 12)
    par_cm2 = [d["par_cm2"] for d in densites]
    return dict(q=Q_PAR_CELLULE, densites=densites,
                par_cm2_min=min(par_cm2) if par_cm2 else None,
                par_cm2_max=max(par_cm2) if par_cm2 else None,
                par_cm2_etendue_relative=((max(par_cm2) - min(par_cm2)) / min(par_cm2)
                                          if par_cm2 else None),
                cellules_pour_11_sur_12=cellules_pour_proprete(11 / 12),
                cellules_pour_3_sur_12=cellules_pour_proprete(3 / 12),
                facteur_exige=exige, lignes=lignes,
                rouleau_ecarte="PHerc0358 (un seul tirage : un nombre ne se disperse pas)")


def _verifier(r: dict | None = None) -> int:
    echecs = comptes = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, comptes
        comptes += 1
        print(f"  {'ok  ' if ok else 'FAIL'}  {nom}" + (f"   [{detail}]" if detail else ""))
        if not ok:
            echecs += 1

    # ⚠⚠ LES TROIS NOMBRES DU RAPPORT, REPRODUITS. C'est la dette que ce fichier rembourse : ils
    # étaient publiés et leur calcul n'était nulle part.
    n1, n2 = cellules_pour_proprete(11 / 12), cellules_pour_proprete(3 / 12)
    v("le modèle rend les 12 085 cellules du rapport pour 11 propres sur 12",
      abs(n1 - 12085) < 5, f"{n1:.0f}")
    v("... et les 192 540 pour 3 sur 12", abs(n2 - 192540) < 5, f"{n2:.0f}")
    v("... donc le facteur exigé de 15,9", abs(n2 / n1 - 15.9) < 0.1, f"{n2 / n1:.2f}")
    # ⚠⚠⚠ LE FACTEUR NE DÉPEND PAS DE q, et c'est ce qui rend le contrôle robuste à une révision
    # du modèle publié : c'est un rapport de deux logarithmes.
    v("... et ce facteur est indépendant de q",
      abs(cellules_pour_proprete(3 / 12, 1e-3) / cellules_pour_proprete(11 / 12, 1e-3)
          - n2 / n1) < 1e-9)
    v("une part propre hors ]0,1] est refusée",
      _leve(lambda: cellules_pour_proprete(0.0)) and _leve(lambda: cellules_pour_proprete(1.5)))
    # ⚠ Une part de 1 (tout propre) n'exige aucune cellule : c'est la borne, pas une erreur.
    v("... et tout-propre exige zéro cellule", cellules_pour_proprete(1.0) == 0.0)

    v("la médiane d'un compte pair prend le milieu", mediane([1.0, 3.0]) == 2.0)
    v("... et elle ignore les absents", mediane([None, 4.0, None]) == 4.0)
    v("... et rend None quand tout est absent", mediane([None, None]) is None)

    # ⚠⚠ SUR UNE VRAIE GRILLE, pas une fixture : la question est de savoir ce que CES données
    # font. Sautée si le corpus est absent — un contrôle qui exigerait 71 Mo de données pour
    # tourner ne tournerait jamais.
    temoin = _grille(ORIGINE / ROULEAUX[0] / "r1")
    if temoin:
        c = concordance_des_plans(temoin)
        v("les trois plans d'un .tifxyz déclarent les mêmes absents",
          c["plans_concordants"], str(c["par_plan"]))
        v("... et la grille est presque entièrement remplie",
          c["part_remplie"] > 0.9, f"{100 * c['part_remplie']:.1f} % de {c['total']} cellules")
        print("      ⚠ c'est POUR ÇA que compter un seul plan, ou toute la grille, rend ici le "
              "même verdict :\n        l'équivalence est une propriété de ces données, "
              "désormais mesurée plutôt que supposée.")
    else:
        print("      ⚠ corpus absent : la concordance des plans n'est pas vérifiée ici")

    if r:
        print("\net la mesure")
        for l in r["lignes"]:
            print(f"      {l['rouleau']:10s} {l['tirages_avant']} → {l['tirages_apres']} tirages · "
                  f"cellules {l['cellules_avant']:.0f} → {l['cellules_apres']:.0f} "
                  f"(×{l['facteur_cellules']:.2f}) · "
                  f"aire {l['aire_avant']:.2f} → {l['aire_apres']:.2f} cm² "
                  f"(×{l['facteur_aire']:.2f})")
        # ⚠⚠⚠ LE CONTRÔLE, ÉCRIT POUR TOMBER DANS LES DEUX SENS ET LES DEUX SONT PUBLIABLES.
        # Si les cellules suivent l'aire, l'hypothèse du rapport tient et le basculement est
        # plus raide que la taille — c'est un résultat neuf. Si elles croissent bien plus vite,
        # l'écart au modèle s'explique par la seule arithmétique et P1 bis tombe.
        rc = [l["facteur_cellules"] for l in r["lignes"] if l["facteur_cellules"]]
        ra = [l["facteur_aire"] for l in r["lignes"] if l["facteur_aire"]]
        ecarts = [c / a for c, a in zip(rc, ra)]
        v("les cellules valides croissent à peu près comme l'aire",
          all(0.7 < e < 1.4 for e in ecarts),
          " · ".join(f"×{c:.2f} cellules contre ×{a:.2f} aire (rapport {e:.2f})"
                     for c, a, e in zip(rc, ra, ecarts)))
        # ⚠⚠⚠ LA FORME FORTE, ET C'EST ELLE QUI TRANCHE. Sur les 24 tirages des deux rouleaux
        # et des deux plafonds, la densité de cellules par cm² ne bouge que de quelques
        # pourcents : « cellules proportionnelles à l'aire » n'est plus une hypothèse.
        v("... et la densité de cellules par cm² est la même sur les DEUX plafonds",
          r["par_cm2_etendue_relative"] < 0.05,
          f"{r['par_cm2_min']:.0f} à {r['par_cm2_max']:.0f} par cm² sur "
          f"{len(r['densites'])} tirages — étendue relative "
          f"{100 * r['par_cm2_etendue_relative']:.1f} %")
        # ⚠⚠ ET LE POINT DE DÉPART EST DÉGÉNÉRÉ, dit plutôt que masqué : au plafond d'origine
        # les douze tirages rendent le MÊME compte au bit près. Le contrôle ne tient donc pas
        # par ce point-là mais par la densité, qui est mesurée des deux côtés.
        v("... alors qu'au plafond d'origine tous les tirages ont le MÊME compte",
          all(l["cellules_toutes_egales_avant"] for l in r["lignes"]),
          f"{r['lignes'][0]['cellules_avant']:.0f} cellules pour les 12")
        v("... donc le basculement observé reste sous ce que le modèle exige",
          max(rc) < r["facteur_exige"],
          f"observé au plus ×{max(rc):.1f}, exigé ×{r['facteur_exige']:.1f}")

    print()
    print(f"  {'ECHEC' if echecs else 'ALL PASS'} ({echecs} failures, {comptes} checks)")
    return echecs


def _leve(f) -> bool:
    try:
        f()
    except ValueError:
        return True
    return False


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()

    if a.verifier and not a.json:
        cible = RACINE / "docs" / "mesures" / "p1bis.json"
        return 1 if _verifier(json.loads(cible.read_text()) if cible.is_file() else None) else 0

    r = confronter()
    print(f"modèle publié : q = {r['q']:.1e} par cellule")
    print(f"  11 propres sur 12 → {r['cellules_pour_11_sur_12']:>9.0f} cellules")
    print(f"   3 propres sur 12 → {r['cellules_pour_3_sur_12']:>9.0f} cellules"
          f"   (facteur exigé ×{r['facteur_exige']:.1f})")
    print()
    for l in r["lignes"]:
        if l["facteur_cellules"] is None:
            print(f"  {l['rouleau']:10s} — pas de grille lisible")
            continue
        print(f"  {l['rouleau']:10s} {l['tirages_avant']} → {l['tirages_apres']} tirages")
        print(f"     cellules valides {l['cellules_avant']:>9.0f} → {l['cellules_apres']:>9.0f}"
              f"   ×{l['facteur_cellules']:.2f}")
        print(f"     aire cm²        {l['aire_avant']:>9.2f} → {l['aire_apres']:>9.2f}"
              f"   ×{l['facteur_aire']:.2f}")
    print(f"\n  ⚠ écarté : {r['rouleau_ecarte']}")
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nécrit : {a.json}")
    if a.verifier:
        print()
        return 1 if _verifier(r) else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
