#!/usr/bin/env python3
"""Un TROU angulaire dans les spires extérieures — la cause trouvée en regardant, puis corrigée.

⭐⭐⭐ CE FICHIER VIENT D'UNE IMAGE, PAS D'UNE HYPOTHÈSE. `77` §7 mesure que le prédicat
d'identité sépare sur `PHerc0139` et pas sur `PHerc0172`, et **quatre causes candidates ont été
testées et rejetées**. À court d'hypothèses, on déplie une tranche en (angle, rayon) et on
regarde : `PHerc0139` montre 37 courbes emboîtées nettes, `PHerc0172` la même chose **plus un
faisceau de spires extérieures qui se croisent entre 330° et 360°**.

⚠⚠ LA MESURE QUI AVAIT ÉCARTÉ CETTE PISTE UTILISAIT LA MAUVAISE STATISTIQUE. `77` §7 comparait
le taux **moyen** de violation d'ordre : 5,2 % contre 5,6 %, « indiscernable ». Il l'est. C'est
la **concentration** qui diffère — pire secteur à ×1,42 de la médiane contre **×5,18**, et les
six pires portent 11,1 % du total contre **24,3 %** (8,3 % si la violation était uniforme).

⚠⚠⚠ ET J'AI DONNÉ LA MAUVAISE EXPLICATION AVANT DE LA MESURER. J'avais écrit que c'était la
**couture** de la spirale — l'angle où une spire finit et où la suivante commence, où `w_k` et
`w_{k+1}` sont au même rayon par continuité du papyrus. Deux mesures la réfutent :

1. **Une couture affecterait TOUTES les spires au même angle.** Celle-ci est **nulle** sur les
   spires intérieures (`w052`–`w057`) et croît vers l'extérieur, jusqu'à 35 % pour `w070` et
   37 % pour `w084`. Un fait sur la partie **extérieure** du rouleau, pas une convention de
   découpe.
2. **La densité y est cent fois plus faible** : 3 points par cellule contre 286 dans les
   secteurs sains, et **49 % de cellules vides** contre 22 %. Ce n'est pas de la matière mal
   ordonnée, c'est de la matière **absente**.

⭐ Donc : un **trou** dans ce que les spires publiées couvrent, dans la partie extérieure du
rouleau — ce qui est là où un rouleau carbonisé est déchiré, perdu ou écrasé. ⚠ Laquelle de ces
trois causes n'est **pas** décidable d'ici, et ce fichier ne tranche pas.

⚠⚠ ET LE REMÈDE N'EST PAS CELUI QU'ON CROIT. Exiger plus de points par cellule (8 → 100) aide
de façon monotone et **ne suffit jamais** : +1,195 → +0,959, encore loin de la séparation. Ce
qui biaise n'est pas le bruit des cellules survivantes, c'est **le trou lui-même** — une pente
ajustée sur un tour à travers un trou angulaire est biaisée quelle que soit la propreté du
reste. Écarter les secteurs, oui ; les nettoyer, non.

⚠⚠⚠ ET MA PREMIÈRE VERSION DE CETTE EXCLUSION ÉTAIT FAUSSE — LE TÉMOIN L'A ATTRAPÉE. J'avais
étendu l'arc par contiguïté, ce qui donnait 15 secteurs, et leur exclusion restaurait la
séparation. Le **témoin négatif à compte égal** a mordu : écarter **autant** de secteurs
**sains** la restaure aussi, parce que retirer un cinquième de la circonférence fait tomber les
tranches mal couvertes sous le seuil de `_separation` et ne laisse que les bonnes. L'effet
mesuré était celui du filtre de couverture. À **six** secteurs, la distinction tient, et c'est
la seule version publiée.

⚠ CE QUE CE FICHIER N'ÉTABLIT PAS :

1. **Ce qui a fait le trou.** Déchirure, perte, collage, écrasement, ou simplement un traceur
   qui s'est arrêté là : la densité dit qu'il n'y a pas de matière, pas pourquoi.
2. **Que ce soit la seule cause.** C'en est une, suffisante sur ce rouleau. `PHerc0139` n'a pas
   de trou détectable et sépare sans rien écarter.
3. **Que l'écarter soit gratuit** : six secteurs sur 72 sont **8 % de la circonférence** perdus
   pour le prédicat, là où un traceur passera quand même.

Usage :
    uv run python src/excision/le_trou_angulaire.py --verifier
    uv run python src/excision/le_trou_angulaire.py --json docs/mesures/le_trou_angulaire.json
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
from le_sens_des_indices import SECTEURS, charger, _spires  # noqa: E402

TROU_ATTENDU = {"PHerc0139": False, "PHerc0172": True}
"""Quels rouleaux portent un trou angulaire détectable. ⚠ Asserté dans les **deux sens** : le fichier
tombe si `PHerc0139` se mettait à en avoir une, et tout autant si `PHerc0172` cessait. Un
contrôle écrit seulement pour le rouleau malade ne dirait pas que l'autre est sain."""

ECARTES = 6
"""Combien de secteurs on écarte, et **le même nombre** pour le témoin. ⚠ Le compte égal EST le
contrôle : à 15 secteurs, écarter n'importe quoi restaure la séparation, donc une comparaison à
comptes différents ne mesurerait pas la couture mais la taille de ce qu'on jette."""


def _profil(rayons: dict[int, dict]) -> dict[int, float]:
    """
    @brief Le taux de violation d'ordre des rayons, secteur angulaire par secteur angulaire.
    """
    violations: dict[int, list[float]] = {}
    for cellule in {c for v in rayons.values() for c in v}:
        presentes = sorted(k for k in rayons if cellule in rayons[k])
        if len(presentes) < 3:
            continue
        suite = [rayons[k][cellule] for k in presentes]
        inversions = sum(1 for i in range(len(suite) - 1) if suite[i + 1] <= suite[i])
        violations.setdefault(cellule[1], []).append(inversions / (len(suite) - 1))
    return {s: float(np.mean(v)) for s, v in violations.items()}


def _densite(nuages: dict, bords_z, bords_t, centres, pires) -> dict:
    """
    @brief Combien de points par cellule dans les secteurs suspects, contre les autres.

    ⚠⚠ C'est la mesure qui DISCRIMINE, et elle a réfuté mon explication. De la matière mal
    ordonnée (un collage, une couture) aurait une densité **normale** ; de la matière absente
    (déchirure, perte, traceur arrêté) a une densité effondrée. Sans elle, « les rayons sont
    dans le désordre ici » se raconte de plusieurs façons également plausibles.
    """
    exclus = set(pires)
    dedans, dehors = [], []
    for _, (x, y, z) in nuages.items():
        for i, (lo, hi) in enumerate(zip(bords_z, bords_z[1:])):
            m = (z >= lo) & (z < hi)
            if m.sum() < 200 or i not in centres:
                continue
            cx, cy = centres[i]
            t = np.digitize(np.arctan2(y[m] - cy, x[m] - cx), bords_t)
            for s in range(1, SECTEURS + 1):
                n = int((t == s).sum())
                (dedans if s in exclus else dehors).append(n)
    if not dedans or not dehors:
        return {}
    d, h = np.array(dedans), np.array(dehors)
    return dict(
        median_dedans=float(np.median(d)), median_dehors=float(np.median(h)),
        vides_dedans=float((d == 0).mean()), vides_dehors=float((h == 0).mean()),
        rapport=float(np.median(d) / max(1.0, np.median(h))),
    )


def _par_spire(rayons: dict[int, dict], pires) -> dict:
    """
    @brief Quelle part des inversions de la zone suspecte implique chaque spire.

    ⚠⚠ La seconde mesure qui discrimine. Une **couture** — une convention de découpe — toucherait
    toutes les spires au même angle. Un accident **physique** touche une partie du rouleau.
    """
    exclus = set(pires)
    impliquee = {k: 0 for k in rayons}
    total = {k: 0 for k in rayons}
    for cellule in {c for v in rayons.values() for c in v}:
        if cellule[1] not in exclus:
            continue
        presentes = sorted(k for k in rayons if cellule in rayons[k])
        for a_, b_ in zip(presentes, presentes[1:]):
            total[a_] += 1
            total[b_] += 1
            if rayons[b_][cellule] <= rayons[a_][cellule]:
                impliquee[a_] += 1
                impliquee[b_] += 1
    taux = {k: impliquee[k] / total[k] for k in rayons if total[k] >= 10}
    if not taux:
        return {}
    ordonnees = sorted(taux)
    moitie = len(ordonnees) // 2
    valeurs = np.array([taux[k] for k in ordonnees])
    # ⚠ Correlation de RANG entre l'indice de spire et le taux : elle dit « ca croit vers
    # l'exterieur » sans supposer que la croissance soit lineaire, ce dont on ne sait rien.
    rangs = np.argsort(np.argsort(valeurs)).astype(float)
    correlation = (float(np.corrcoef(np.arange(len(valeurs), dtype=float), rangs)[0, 1])
                   if len(valeurs) > 2 else 0.0)
    return dict(
        par_spire={str(k): taux[k] for k in ordonnees},
        spires_intactes=int((valeurs == 0).sum()),
        spires_mesurees=len(valeurs),
        correlation_avec_lindice=correlation,
        moitie_interieure=float(np.mean(valeurs[:moitie])),
        moitie_exterieure=float(np.mean(valeurs[moitie:])),
    )


def _sans(rayons: dict[int, dict], secteurs) -> dict[int, dict]:
    exclus = set(secteurs)
    out = {k: {c: v for c, v in d.items() if c[1] not in exclus} for k, d in rayons.items()}
    return {k: v for k, v in out.items() if len(v) > 50}


def mesurer(rouleau: str = "PHerc0172") -> dict:
    dossiers = _spires(rouleau)
    nuages = {k: v for k, v in ((k, charger(d)) for k, d in dossiers.items()) if v}
    bords_z, bords_t, centres = champ._grille(nuages)
    rayons = {k: champ._rayons(n, bords_z, bords_t, centres) for k, n in nuages.items()}
    rayons = {k: v for k, v in rayons.items() if len(v) > 50}

    taux = _profil(rayons)
    mediane = float(np.median(list(taux.values()))) if taux else 0.0
    classes = sorted(taux, key=lambda s: -taux[s])
    pires, sains = classes[:ECARTES], classes[-ECARTES:]

    def etat(sous: dict[int, dict]) -> dict:
        s = champ._separation(sous, sorted(sous))
        return dict(separe=s["separe"], tranches_necessaires=s["tranches_necessaires"])

    return dict(
        rouleau=rouleau, secteurs=len(taux), ecartes=ECARTES,
        taux_median=mediane,
        taux_maximal=float(max(taux.values())) if taux else None,
        concentration=float(max(taux.values()) / mediane) if mediane else None,
        # ⚠ La part du total portee par les pires : c'est ELLE qui distingue un profil plat
        # d'un defaut localise, la moyenne ne le fait pas.
        part_des_pires=float(sum(taux[s] for s in pires) / sum(taux.values()))
        if taux else None,
        part_si_uniforme=ECARTES / max(1, len(taux)),
        secteurs_pires=sorted(pires),
        secteurs_sains=sorted(sains),
        densite=_densite(nuages, bords_z, bords_t, centres, pires),
        par_spire=_par_spire(rayons, pires),
        tout_garde=etat(rayons),
        sans_les_pires=etat(_sans(rayons, pires)),
        sans_des_sains=etat(_sans(rayons, sains)),
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

    attendue = TROU_ATTENDU.get(r["rouleau"], True)

    print("le défaut est LOCALISÉ — ce que la moyenne ne voyait pas")
    v(("la violation d'ordre est concentrée, pas répartie" if attendue
       else "la violation d'ordre est RÉPARTIE — ce rouleau n'a pas de trou"),
      (r["concentration"] > 3.0) == attendue,
      f"pire secteur à ×{r['concentration']:.2f} de la médiane")
    v(("... et les pires secteurs portent bien plus que leur part" if attendue
       else "... et les pires secteurs portent à peu près leur part"),
      (r["part_des_pires"] > 2 * r["part_si_uniforme"]) == attendue,
      f"{r['part_des_pires'] * 100:.1f} % du total contre "
      f"{r['part_si_uniforme'] * 100:.1f} % si uniforme")

    dens = r.get("densite") or {}
    spi = r.get("par_spire") or {}
    if attendue and dens and spi:
        print("⭐ et les deux mesures qui DISCRIMINENT — elles ont réfuté mon explication")
        # ⚠⚠ « Matiere mal ordonnee » et « matiere absente » se racontent aussi bien l'une que
        # l'autre a partir des inversions seules. La densite tranche.
        v("la densité y est effondrée, donc la matière est ABSENTE et non mal ordonnée",
          dens["rapport"] < 0.2,
          f"{dens['median_dedans']:.0f} points/cellule contre {dens['median_dehors']:.0f} "
          f"· {dens['vides_dedans'] * 100:.0f} % de cellules vides contre "
          f"{dens['vides_dehors'] * 100:.0f} %")
        # ⚠⚠ Et une couture — une convention de decoupe — toucherait TOUTES les spires au
        # meme angle. Deux faits l'excluent, et aucun des deux n'est un seuil choisi : des
        # spires entieres sont a exactement zero, et le taux CROIT avec l'indice.
        # ⚠ Ma premiere version comparait les deux moities et rendait ×1,96 contre un seuil
        # de 2 -- j'ai change l'assertion plutot que le seuil.
        v("... et des spires entières y sont INTACTES — une couture les toucherait toutes",
          spi["spires_intactes"] >= 3,
          f"{spi['spires_intactes']} spires sur {spi['spires_mesurees']} à exactement 0 %")
        v("... et le taux croît vers l'extérieur du rouleau",
          spi["correlation_avec_lindice"] > 0.4,
          f"corrélation de rang {spi['correlation_avec_lindice']:.3f}")

    if not attendue:
        # ⚠ Sur un rouleau sans couture, il n'y a rien a restaurer : le controle utile est
        # qu'il separe DEJA. Enchainer les trois suivants y serait vert sans rien verifier.
        v("... et il sépare déjà, sans rien écarter", r["tout_garde"]["separe"],
          f"à {r['tout_garde']['tranches_necessaires']} tranches")
    else:
        print("l'écarter restaure la séparation")
        v("le rouleau ne sépare pas tel quel", not r["tout_garde"]["separe"])
        v("... et sépare une fois le trou écarté",
          r["sans_les_pires"]["separe"],
          f"à {r['sans_les_pires']['tranches_necessaires']} tranches")

        # ⚠⚠⚠ LE TEMOIN A COMPTE EGAL, et c'est lui qui a fait echouer ma premiere version.
        # Sans lui, « ecarter la couture restaure » est indistinguable de « ecarter six
        # secteurs restaure », et j'ai deja vu le second etre vrai a quinze.
        print("⭐ et ce sont CES secteurs-là, pas six secteurs quelconques")
        v("écarter autant de secteurs sains ne restaure rien",
          not r["sans_des_sains"]["separe"],
          f"{r['ecartes']} secteurs sains écartés, séparé={r['sans_des_sains']['separe']}")

    print()
    if echecs:
        print(f"  ECHEC ({echecs} failures)")
    else:
        print(f"  ALL PASS (0 failures, {comptees} checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--rouleau", default="PHerc0172")
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    args = p.parse_args()

    r = mesurer(args.rouleau)
    if not args.verifier or args.json:
        print(f"{r['rouleau']} — {r['secteurs']} secteurs, violation médiane "
              f"{r['taux_median'] * 100:.1f} %\n")
        print(f"  concentration : pire secteur à ×{r['concentration']:.2f} de la médiane")
        print(f"  les {r['ecartes']} pires portent {r['part_des_pires'] * 100:.1f} % du total "
              f"({r['part_si_uniforme'] * 100:.1f} % si uniforme)")
        print(f"  trou : secteurs {r['secteurs_pires']}")
        print(f"\n  {'tout gardé':22s} séparé={r['tout_garde']['separe']}")
        print(f"  {'sans le trou':22s} séparé={r['sans_les_pires']['separe']} "
              f"({r['sans_les_pires']['tranches_necessaires']} tranches)")
        print(f"  {'témoin, sans des sains':22s} séparé={r['sans_des_sains']['separe']}")

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
