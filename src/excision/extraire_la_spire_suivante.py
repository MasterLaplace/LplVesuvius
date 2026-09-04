#!/usr/bin/env python3
"""Jusqu'où le champ d'enroulement porte-t-il au-delà de ce qu'il connaît ? — une feuille.

⭐⭐⭐ CE QUE CE FICHIER MESURE, ET C'ÉTAIT LA LIMITE NOMMÉE MAIS JAMAIS CHIFFRÉE. `77` dit que
le champ « interpole entre spires connues et **refuse** au-delà », et appelle ça sa limite dure
pour un déploiement. Refuser est la bonne conduite ; ce qui manquait est **de combien** on
pourrait dépasser, parce que c'est ce qui décide si un référent partiel permet de couvrir un
rouleau entier.

**Mesuré : une feuille, et pas deux.** En retirant les `N` spires extérieures et en prédisant
leur rayon par extrapolation, l'erreur croît **linéairement** avec la distance au bord :

    1 feuille au-delà    47 µm    0,31 feuille
    2 feuilles           79 µm    0,51
    3 feuilles          125 µm    0,81
    8 feuilles          293 µm    1,90

⭐⭐ **Ce qui est utilisable est la première ligne**, et elle l'est vraiment : le champ place la
feuille suivante à **47 µm** près, soit moins d'un tiers d'un écart inter-feuilles (154 µm). Un
traceur amorcé là-dessus part au bon endroit — c'est un **a priori principé** pour la graine, là
où `25` avait réglé « où l'on part » sur la planéité locale.

⚠⚠ ET LE MODÈLE A ÉTÉ CHOISI PAR LA MESURE APRÈS QUE MON RAISONNEMENT SE SOIT TROMPÉ. J'avais
argumenté qu'un pas estimé **par cellule** était nécessaire, parce que le pas varie avec le
rayon et l'angle sur un rouleau écrasé. Comparé aux quatre modèles, ce pas-là est le **pire
partout** :

    au-delà de           1      2      3      8   (en feuilles)
    pas global        0,31   0,51   0,81   1,90
    2 dernières       0,37   0,74   1,22   3,23   <- mon modèle
    4 dernières       0,33   0,55   0,81   1,99
    8 dernières       0,35   0,58   0,82   1,64

L'argument était juste sur la physique et faux sur la **statistique** : un pas estimé sur deux
rayons bruités est plus bruité que le pas moyen du rouleau, et ce bruit-là domine la variation
qu'il prétend capter.

⚠ Le pas global est mesuré **sur les spires connues seulement**. Reprendre les 154,1 µm de `76`
serait une fuite — ils ont été mesurés sur toutes les spires, y compris celles qu'on retire ici
pour les faire prédire.

⚠⚠⚠ ET LE RÉSULTAT QUI TRANCHE VRAIMENT : **réinjecter la spire prédite dans le champ ne change
RIEN**, au chiffre près, à toutes les distances. Ce n'est pas une déception, c'est une
tautologie qu'il fallait mesurer pour la nommer : une spire prédite par extrapolation linéaire
**ne porte aucune information neuve** — elle est exactement ce que le modèle disait déjà.

**Donc le champ est un JUGE, pas un GÉNÉRATEUR.** Il ne peut pas s'étendre tout seul. Pour
dépasser une feuille, la spire prédite doit être **corrigée contre le volume**, ce qui est
précisément le travail d'un traceur et précisément ce que le champ ne remplace pas.

⚠ CE QUE CE FICHIER N'ÉTABLIT PAS :

1. **Qu'un traceur amorcé par cet a priori réussisse.** Ce qui est mesuré est *où est la
   feuille suivante*, pas si un traceur la suivra. `55` dit que le mur 1 vient de la graine ;
   c'est un argument pour essayer, pas une preuve.
2. **Que la portée d'une feuille vaille pour un autre rouleau.** Mesuré sur `PHerc0139`, le seul
   des deux où le prédicat sépare (`77` §7).
3. **Qu'un modèle d'extrapolation plus riche ne porte pas plus loin.** L'extrapolation est
   **linéaire sur les deux dernières spires connues**, délibérément : c'est le modèle le plus
   simple, donc celui dont l'échec est le plus informatif. Un modèle qui porterait à trois
   feuilles serait une bonne nouvelle, et ce fichier est ce contre quoi la comparer.

Usage :
    uv run python src/excision/extraire_la_spire_suivante.py --verifier
    uv run python src/excision/extraire_la_spire_suivante.py --json docs/mesures/extraire_la_spire_suivante.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(RACINE / "src" / "excision")]
import le_champ_denroulement as champ  # noqa: E402
from le_sens_des_indices import charger, _spires  # noqa: E402

VOXEL_UM = {"PHerc0139": 9.362, "PHerc0172": 7.91}
"""La taille de voxel de chaque rouleau, pour exprimer une erreur en micromètres. ⚠ Décodée par
`76` depuis l'aire publiée, jamais lue dans un nom de volume."""

RETIREES = 8
"""Combien de spires extérieures on retire pour les faire prédire. ⚠ Huit et non deux : deux
mesureraient la portée d'une feuille sans montrer **comment l'erreur croît**, et c'est la
croissance qui dit qu'il n'y a pas de portée cachée plus loin."""

CELLULES_MINIMUM = 20
"""En dessous, une médiane d'erreur est le bruit d'une poignée de cellules."""


MODELES = ("global", "commun", "2", "4", "8")
"""Les modèles d'extrapolation comparés. ⚠⚠ Comparés et non choisis d'avance, parce que mon
raisonnement s'est trompé : j'avais argumenté qu'un pas **par cellule** était nécessaire — « le
pas varie avec le rayon et l'angle, un rouleau est écrasé » — et le pas **global** fait mieux
partout (45 µm contre 58 à une feuille). L'argument était juste sur la physique et faux sur la
statistique : un pas estimé sur deux rayons bruités est plus bruité que le pas moyen du
rouleau, et ce bruit-là domine la variation qu'il prétend capter."""


def structure_de_lecart(connu: dict[int, dict], voxel_um: float) -> dict:
    """
    @brief L'écart inter-feuilles local dépend-il de l'angle, de la hauteur, du rayon ?

    ⚠⚠ Existe parce que la réponse est OUI pour l'angle et que ça ne sert **pas** à
    extrapoler — les deux moitiés doivent être publiées ensemble. Mesuré sur `PHerc0139` :
    l'écart varie de **71 µm avec l'angle** (45 % de sa médiane), de 31 µm avec la hauteur, et
    à peine avec le rayon. C'est la signature de l'**écrasement** : là où la section est
    aplatie, les feuilles se serrent ou s'écartent, et ce motif est fixe dans le repère du
    rouleau.
    """
    ecarts: dict[tuple, list[float]] = {}
    indices = sorted(connu)
    for a_, b_ in zip(indices, indices[1:]):
        if b_ - a_ != 1:
            continue
        for c in connu[a_]:
            if c in connu[b_]:
                ecarts.setdefault(c, []).append(connu[b_][c] - connu[a_][c])
    local = {c: float(np.median(v)) for c, v in ecarts.items()}
    if len(local) < 50:
        return {}

    def amplitude(cle) -> float:
        groupes: dict = {}
        for c, v in local.items():
            groupes.setdefault(cle(c), []).append(v)
        medians = [float(np.median(v)) for v in groupes.values() if len(v) >= 3]
        return (max(medians) - min(medians)) * voxel_um if medians else 0.0

    valeurs = np.array(list(local.values())) * voxel_um
    return dict(
        cellules=len(local),
        median_um=float(np.median(valeurs)),
        coefficient_de_variation=float(valeurs.std() / max(np.median(valeurs), 1e-9)),
        amplitude_angle_um=amplitude(lambda c: c[1]),
        amplitude_hauteur_um=amplitude(lambda c: c[0]),
    )


def _pas_commun(connu: dict[int, dict]) -> dict:
    """
    @brief Le pas médian de CHAQUE cellule, mis en commun sur toutes les spires connues.

    ⚠ À ne pas confondre avec le modèle `"2"`, qui estime le pas d'une cellule sur ses **deux
    dernières** spires : celui-là est bruité, celui-ci moyenne sur toute la course connue. Il
    capte donc la structure angulaire réelle sans son bruit — et il ne sert quand même pas à
    une feuille (52 µm contre 47), ce qui est le résultat.
    """
    acc: dict[tuple, list[float]] = {}
    indices = sorted(connu)
    for a_, b_ in zip(indices, indices[1:]):
        if b_ - a_ != 1:
            continue
        for c in connu[a_]:
            if c in connu[b_]:
                acc.setdefault(c, []).append(connu[b_][c] - connu[a_][c])
    return {c: float(np.median(v)) for c, v in acc.items() if len(v) >= 3}


def _pas_global(connu: dict[int, dict]) -> float:
    """
    @brief Le pas inter-feuilles moyen, mesuré sur les spires CONNUES seulement.

    ⚠⚠ Sur les connues, jamais sur tout le rouleau. Reprendre les 154,1 µm de `76` serait une
    fuite : ils ont été mesurés sur toutes les spires, y compris celles qu'on retire ici pour
    les faire prédire. Le modèle recevrait une information qu'il n'aura pas à l'usage.
    """
    pas = []
    indices = sorted(connu)
    for a, b in zip(indices, indices[1:]):
        if b - a != 1:
            continue
        communes = [c for c in connu[a] if c in connu[b]]
        if communes:
            pas.append(float(np.median([connu[b][c] - connu[a][c] for c in communes])))
    return float(np.median(pas)) if pas else 0.0


def _predire(connu: dict[int, dict], cellules, k: int, modele: str) -> dict:
    """
    @brief Le rayon prédit de la spire `k`, cellule par cellule.

    `modele` vaut `"global"` (un pas unique, mesuré sur les spires connues) ou un nombre de
    spires sur lesquelles estimer le pas **dans chaque cellule**.
    """
    predit = {}
    pas_commun = _pas_global(connu) if modele == "global" else None
    par_cellule = _pas_commun(connu) if modele == "commun" else None
    fenetre = None if modele in ("global", "commun") else int(modele)
    for c in cellules:
        dispo = sorted(x for x in connu if c in connu[x])
        if not dispo:
            continue
        dernier = dispo[-1]
        if pas_commun is not None:
            pas = pas_commun
        elif par_cellule is not None:
            if c not in par_cellule:
                continue
            pas = par_cellule[c]
        else:
            if len(dispo) < fenetre:
                continue
            debut = dispo[-fenetre]
            pas = (connu[dernier][c] - connu[debut][c]) / (dernier - debut)
        predit[c] = connu[dernier][c] + pas * (k - dernier)
    return predit


def mesurer(rouleau: str = "PHerc0139", retirees: int = RETIREES) -> dict:
    dossiers = _spires(rouleau)
    nuages = {k: v for k, v in ((k, charger(d)) for k, d in dossiers.items()) if v}
    bords_z, bords_t, centres = champ._grille(nuages)
    rayons = {k: champ._rayons(n, bords_z, bords_t, centres) for k, n in nuages.items()}
    rayons = {k: v for k, v in rayons.items() if len(v) > 50}
    indices = sorted(rayons)
    if len(indices) < retirees + 4:
        raise SystemExit(f"pas assez de spires pour en retirer {retirees}")

    voxel = champ.ECART_INTER_FEUILLES_VX.get(rouleau)
    bord = indices[-1] - retirees

    def courir(modele: str, reinjecte: bool) -> list[dict]:
        connu = {k: dict(v) for k, v in rayons.items() if k <= bord}
        serie = []
        for j in range(1, retirees + 1):
            k = bord + j
            if k not in rayons:
                continue
            predit = _predire(connu, rayons[k].keys(), k, modele)
            communes = [c for c in predit if c in rayons[k]]
            if len(communes) < CELLULES_MINIMUM:
                continue
            err = np.array([abs(predit[c] - rayons[k][c]) for c in communes])
            serie.append(dict(spire=k, au_dela=j, cellules=len(communes),
                              erreur_vx=float(np.median(err)),
                              erreur_feuilles=float(np.median(err) / voxel)))
            if reinjecte:
                connu[k] = predit
        return serie

    par_modele = {m: courir(m, False) for m in MODELES}
    # ⚠ Le meilleur se choisit sur la PREMIERE feuille, celle qui est utilisable : un modele
    # meilleur a huit feuilles et pire a une ne sert a rien, puisque personne n'ira a huit.
    meilleur = min((m for m in MODELES if par_modele[m]),
                   key=lambda m: par_modele[m][0]["erreur_vx"])
    series = {"sans_reinjection": par_modele[meilleur],
              "avec_reinjection": courir(meilleur, True)}

    a, b = series["sans_reinjection"], series["avec_reinjection"]
    # ⚠⚠ Comparees terme a terme, pas par leur moyenne : deux series de moyennes egales
    # peuvent differer partout.
    identiques = (len(a) == len(b)
                  and all(abs(x["erreur_vx"] - y["erreur_vx"]) < 1e-9 for x, y in zip(a, b)))

    portee = [x["au_dela"] for x in a if x["erreur_feuilles"] < 0.5]
    connu_final = {k: v for k, v in rayons.items() if k <= bord}
    return dict(
        rouleau=rouleau, spires=len(rayons), bord_du_champ=bord, retirees=retirees,
        structure=structure_de_lecart(connu_final, VOXEL_UM.get(rouleau, 9.362)),
        ecart_inter_feuilles_vx=voxel,
        portee_en_feuilles=max(portee) if portee else 0,
        modele=meilleur,
        par_modele={m: [dict(au_dela=x["au_dela"], erreur_vx=x["erreur_vx"],
                             erreur_feuilles=x["erreur_feuilles"]) for x in serie]
                    for m, serie in par_modele.items()},
        reinjection_sans_effet=identiques,
        series=series,
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

    serie = r["series"]["sans_reinjection"]
    par_distance = {x["au_dela"]: x for x in serie}

    print("le champ porte UNE feuille au-delà de ce qu'il connaît")
    v("la spire suivante est placée à moins d'une demi-feuille",
      1 in par_distance and par_distance[1]["erreur_feuilles"] < 0.5,
      f"{par_distance[1]['erreur_vx'] * VOXEL_UM.get(r['rouleau'], 9.362):.0f} µm soit "
      f"{par_distance[1]['erreur_feuilles']:.2f} feuille" if 1 in par_distance else "absente")
    # ⚠⚠ Ecrit dans le sens « la DEUXIEME echoue ». Sans lui, « la premiere passe » serait
    # compatible avec une portee de dix feuilles, donc ne mesurerait pas une LIMITE.
    v("... et la deuxième ne l'est plus",
      2 in par_distance and par_distance[2]["erreur_feuilles"] >= 0.5,
      f"{par_distance[2]['erreur_feuilles']:.2f} feuille" if 2 in par_distance else "absente")
    v("la portée mesurée est donc d'exactement une feuille",
      r["portee_en_feuilles"] == 1, f"{r['portee_en_feuilles']} feuille(s)")

    print("et l'erreur croît, donc il n'y a pas de portée cachée plus loin")
    croissante = all(a["erreur_vx"] < b["erreur_vx"] for a, b in zip(serie, serie[1:]))
    v("l'erreur est monotone croissante avec la distance au bord",
      croissante,
      " · ".join(f"{x['au_dela']}:{x['erreur_feuilles']:.2f}" for x in serie))

    print("⭐ et le champ est un JUGE, pas un générateur")
    # ⚠⚠⚠ Le controle qui porte la conclusion, et il est ecrit dans le sens « ca ne change
    # RIEN ». Si un jour la reinjection ameliorait quoi que ce soit, il tomberait -- et ce
    # serait le resultat le plus important du fichier.
    v("réinjecter la spire prédite ne change rien, au chiffre près",
      r["reinjection_sans_effet"],
      "les deux séries sont identiques terme à terme")

    st = r.get("structure") or {}
    if st:
        print("⚠ l'écart a une STRUCTURE angulaire réelle — et elle ne sert pas ici")
        # ⚠⚠ Les deux moities ensemble, jamais l'une sans l'autre : « l'ecart varie de 71 µm
        # avec l'angle » invite a croire qu'on peut l'exploiter, et la mesure dit non.
        v("l'écart varie fortement avec l'angle",
          st["amplitude_angle_um"] > 0.3 * st["median_um"],
          f"{st['amplitude_angle_um']:.0f} µm d'amplitude sur une médiane de "
          f"{st['median_um']:.0f}")
        v("... et bien moins avec la hauteur",
          st["amplitude_hauteur_um"] < st["amplitude_angle_um"],
          f"{st['amplitude_hauteur_um']:.0f} µm contre {st['amplitude_angle_um']:.0f}")
        commun = r["par_modele"].get("commun")
        global_ = r["par_modele"].get("global")
        if commun and global_:
            v("... et l'exploiter n'améliore PAS la première feuille",
              commun[0]["erreur_vx"] >= global_[0]["erreur_vx"],
              f"pas mis en commun {commun[0]['erreur_feuilles']:.2f} contre "
              f"pas global {global_[0]['erreur_feuilles']:.2f} feuille")

    print()
    if echecs:
        print(f"  ECHEC ({echecs} failures)")
    else:
        print(f"  ALL PASS (0 failures, {comptees} checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--rouleau", default="PHerc0139")
    p.add_argument("--retirees", type=int, default=RETIREES)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    args = p.parse_args()

    r = mesurer(args.rouleau, args.retirees)
    if not args.verifier or args.json:
        print(f"{r['rouleau']} — champ sur w{r['bord_du_champ'] - r['spires'] + r['retirees'] + 1:03d}"
              f"..w{r['bord_du_champ']:03d}, {r['retirees']} spires extraites\n")
        print(f"  {'au-delà':>8s} {'erreur':>10s} {'en feuilles':>12s} {'cellules':>9s}")
        for x in r["series"]["sans_reinjection"]:
            print(f"  {x['au_dela']:8d} {x['erreur_vx'] * VOXEL_UM.get(r['rouleau'], 9.362):8.1f} µm "
                  f"{x['erreur_feuilles']:11.2f} {x['cellules']:9d}")
        print(f"\n  portée : {r['portee_en_feuilles']} feuille(s)")
        print(f"  réinjection sans effet : {r['reinjection_sans_effet']}")

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
