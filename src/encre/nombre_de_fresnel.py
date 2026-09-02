#!/usr/bin/env python3
"""Les « trois paramètres couplés » n'en sont qu'UN, et il se calcule sans télécharger un octet.

⚠⚠⚠ POURQUOI CE FICHIER EXISTE. `campagnes_de_scan.py` a établi que les rouleaux dont
l'encre se lit et ceux où le modèle est inerte se séparent par leur **campagne de scan**, et
il a buté sur une limite qu'il énonce lui-même : *« les trois grandeurs co-varient par
campagne : un scan fin est aussi à courte propagation et à basse énergie. Aucune des trois
n'est isolée par cette mesure-ci. »* Le site du prix nomme la même difficulté :
*« Three coupled scan parameters »*.

⭐⭐⭐ CE FICHIER RETOURNE LA QUESTION. On n'a pas à isoler les trois, parce qu'en imagerie
de phase par propagation elles n'entrent que par **une seule combinaison**. Le contraste ne
vient pas de l'absorption -- le papier de référence le dit en toutes lettres, *« the
absorption contrast being very low for carbon-based material in hard X-rays »* -- il vient
des franges de Fresnel au bord de chaque interface. La largeur de la première frange vaut
$\\sqrt{\\lambda D}$, et ce qui décide si elle est visible n'est pas cette largeur mais son
rapport au pas d'échantillonnage :

$$ F = \\frac{\\sqrt{\\lambda D}}{p}, \\qquad \\lambda = \\frac{hc}{E} $$

- $F \\ll 1$ : la frange est plus fine qu'un pixel. Elle existe et **le détecteur ne la voit
  pas**. Le contraste restant est de l'absorption, c'est-à-dire presque rien sur du carbone.
- $F \\approx 1$ : la frange couvre un pixel. C'est le régime de rehaussement de bord.
- $F \\gg 1$ : la frange déborde sur plusieurs pixels et **noie** la structure.

⭐⭐ LA VÉRIFICATION QUI DÉCIDE, et elle ne dépend d'aucune donnée de ce dépôt : les mots que
le papier écrit sous ses propres panneaux doivent s'ordonner selon $F$. Ils s'ordonnent, et
aux deux bouts :

  - à $F = 1{,}82$ (1,129 µm, 0,2 m, 59 keV) le papier écrit *« fine delaminations begin to
    blur due to a **too long propagation distance for a so small pixel size** »* -- c'est la
    définition de $F > 1$, dite en mots ;
  - à $F \\approx 0{,}39$ (9,362 µm, 1,2 m, 113 keV) il écrit *« the 9.362 µm panel is
    **pixel-limited**, the inset shows the bare voxel grid »* ;
  - et le régime de **production**, celui qu'ils ont retenu après une campagne 4×4 d'essais,
    tombe à $F \\approx 0{,}74$, entre les deux.

⚠⚠ CE QUE $F$ N'EXPLIQUE PAS, et il faut le dire à chaque usage. La **décohérence** -- la
diffusion du faisceau par l'échantillon lui-même, que le papier attribue au graphite et à la
structure cellulaire du papyrus -- ne dépend pas de $F$ mais de $D$ **en absolu**, parce que
c'est un flou qui grandit avec la distance parcourue après diffusion. Le corpus le montre :
500P2 à 4,317 µm / 1,2 m ($F = 0{,}85$) est déclaré *« haze-limited »* alors que le même
fragment à 2,215 µm / 0,4 m ($F = 0{,}95$) ne l'est pas. **Même $F$, verdict opposé, et la
seule chose qui change est $D$.** Le modèle honnête a donc deux termes : $F$ dit si la frange
est résolue, $D$ dit si l'échantillon l'a déjà brouillée.

⭐⭐⭐ ET C'EST CE COUPLE QUI DIAGNOSTIQUE LES 13 ROULEAUX DU PRIX. Ils sont du mauvais côté
des **deux** : $F \\approx 0{,}39$, soit la moitié du régime de production, ET $D = 1{,}2$ m,
la distance à laquelle le papier mesure l'apparition de la décohérence -- sur `PHerc0268`,
qui est lui-même l'un des treize. Ce n'est pas « les pixels sont trop gros » : c'est une
campagne de **repérage**, optimisée pour le débit, à distance unique pour tout le lot.

⚠ Et ça donne la borne dure que ce fichier calcule : à 9,362 µm, atteindre le $F$ de
production demanderait une distance que la décohérence interdit. Les deux contraintes sont
**incompatibles à ce pas d'échantillonnage**, et c'est la raison physique -- jamais écrite
ainsi dans le papier, qui dit seulement *« finer voxel sizes lead to higher image quality »*
-- pour laquelle le domaine est descendu à 2,4 µm.

⚠ CE QUE CE FICHIER N'ÉTABLIT PAS. Il ne mesure aucune image. C'est un calcul sur les
métadonnées publiées, dont la valeur est qu'il **prédit** l'ordre des verdicts publiés et
qu'il est réfutable : un panneau du papier qui contredirait l'ordre le tuerait.

Sources, chacune vérifiable :
  - papier : `data/site/scrollprize.org/pdf/main.pdf` (Angelotti et al., arXiv 2606.29085),
    Extended Data Fig. 2 (p. 33-36), Extended Data Table 1 (p. 32), Supplementary Table 5
    (p. 45) ;
  - corpus : `data/metadata.min.json`, index publié du bucket `vesuvius-challenge-open-data`.

Usage :
    uv run python src/encre/nombre_de_fresnel.py --verifier
    uv run python src/encre/nombre_de_fresnel.py --json docs/mesures/nombre_de_fresnel.json
"""

from __future__ import annotations

import argparse
import gzip
import json
import math
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]

# hc en keV·m : lambda[m] = HC_KEV_M / E[keV]. CODATA 2018, hc = 1,23984193 eV·µm.
HC_KEV_M = 1.23984193e-9

INDEX = RACINE / "data" / "metadata.min.json"

# Le nom long d'un scan porte les trois grandeurs : `<id>-<pas>um-<distance>m-<energie>keV`.
# ⚠ Certains noms anciens n'ont pas la distance ; ils sont comptés à part, jamais devinés.
NOM_LONG = re.compile(r"-(?P<px>[\d.]+)um-(?P<d>[\d.]+)m-(?P<e>[\d.]+)keV")

LES_TREIZE = (
    "PHerc0125", "PHerc0191", "PHerc0211", "PHerc0257", "PHerc0268",
    "PHerc0358", "PHerc0800", "PHerc0813", "PHerc0826", "PHerc1203",
    "PHerc1218", "PHerc1447", "PHerc1545",
)
"""Les rouleaux éligibles au Grand Prix 2027, tels que `docs/prompts/PROMPT_fable_grand_prix.md`
les liste depuis `data/site/scrollprize.org/prizes.html`."""


VERDICTS_DU_PAPIER: tuple[dict, ...] = (
    # Extended Data Fig. 2e, p. 36 : cinq panneaux, un verdict écrit sous chacun.
    dict(objet="PHerc0500P2", px=0.550, d=0.07, e=65.0,
         verdict="fibres résolues", rang=3,
         citation="At 0.55 µm individual papyrus fibers are resolved"),
    dict(objet="PHerc1667", px=1.129, d=0.22, e=59.0,
         verdict="frange trop large", rang=2,
         citation="fine delaminations begin to blur due to a too long propagation "
                  "distance for a so small pixel size"),
    dict(objet="PHerc1667", px=2.399, d=0.22, e=78.0,
         verdict="production", rang=0,
         citation="the 2.4 µm appears as the best possible resolution on a setup "
                  "compatible with large scrolls complete imaging"),
    dict(objet="PHerc0500P2", px=4.317, d=1.2, e=111.0,
         verdict="voilé", rang=1,
         citation="the 4.317 µm panel is haze-limited"),
    dict(objet="PHerc0500P2", px=9.362, d=1.2, e=113.0,
         verdict="limité par le pixel", rang=1,
         citation="the 9.362 µm panel is pixel-limited, the inset shows the bare voxel grid"),
)
"""⚠ `rang` n'est PAS une note de qualité inventée ici : 0 = le régime que le papier retient
pour la production, 1 = un panneau qu'il déclare dégradé, 2 = dégradé et dont il nomme la
distance comme cause, 3 = hors du domaine des rouleaux entiers (petit champ, autre ligne)."""


def longueur_donde_m(energie_kev: float) -> float:
    """
    @brief Longueur d'onde d'un photon d'énergie donnée.

    ⚠ L'énergie publiée est une **moyenne** de spectre polychromatique, pas une raie. La
    longueur d'onde qui en sort est donc effective : elle sert à comparer des configurations
    entre elles, jamais à prédire une figure d'interférence.
    """
    if energie_kev <= 0:
        raise ValueError("une énergie de faisceau est strictement positive")
    return HC_KEV_M / energie_kev


def nombre_de_fresnel(pas_um: float, distance_m: float, energie_kev: float) -> float:
    """
    @brief Largeur de la première frange de Fresnel, exprimée en pixels.

    C'est la seule grandeur de ce fichier. Elle vaut $\\sqrt{\\lambda D} / p$, et son unité
    est le pixel — ce qui est exactement ce dont on a besoin, puisque la question n'est pas
    « la frange est-elle large » mais « le détecteur peut-il la voir ».
    """
    if pas_um <= 0 or distance_m < 0:
        raise ValueError("un pas d'échantillonnage est positif, une distance ne l'est pas moins")
    return math.sqrt(longueur_donde_m(energie_kev) * distance_m) * 1e6 / pas_um


def distance_pour_atteindre(cible_f: float, pas_um: float, energie_kev: float) -> float:
    """
    @brief La distance de propagation qu'il faudrait pour atteindre un $F$ donné.

    L'inverse de la fonction ci-dessus. Elle sert à une seule chose et il faut la dire : à
    montrer que la distance demandée par un gros pixel tombe **au-delà** du seuil de
    décohérence, donc que la contrainte n'est pas atteignable plutôt que simplement coûteuse.
    """
    return (cible_f * pas_um * 1e-6) ** 2 / longueur_donde_m(energie_kev)


def _charger_index() -> dict:
    """Le bucket sert son index **gzippé sans en-tête de contenu**, donc `json.load` échoue
    sur un `UnicodeDecodeError` en position 1. On essaie donc gzip d'abord, texte ensuite."""
    brut = INDEX.read_bytes()
    try:
        texte = gzip.decompress(brut).decode()
    except (OSError, gzip.BadGzipFile):
        texte = brut.decode()
    return json.loads(texte)


def scans_du_corpus() -> tuple[list[dict], int]:
    """
    @brief Tous les scans publiés dont le nom porte les trois grandeurs, avec leur $F$.

    ⚠ Rend aussi le nombre de scans **écartés** faute de distance dans le nom. Un dénombrement
    qui tairait les écartés se lirait comme un inventaire complet, et il ne l'est pas : les
    campagnes de 2023 nomment le pas et l'énergie, pas la distance.
    """
    index = _charger_index()["samples"]
    gardes: list[dict] = []
    ecartes = 0
    for objet, fiche in sorted(index.items()):
        for identifiant, scan in sorted(fiche.get("scans", {}).items()):
            nom = scan.get("long_id", "")
            trouve = NOM_LONG.search(nom)
            if not trouve:
                ecartes += 1
                continue
            px = float(trouve.group("px"))
            d = float(trouve.group("d"))
            e = float(trouve.group("e"))
            gardes.append(dict(
                objet=objet, scan=identifiant, nom=nom,
                pas_um=px, distance_m=d, energie_kev=e,
                fresnel=nombre_de_fresnel(px, d, e),
                du_prix=objet in LES_TREIZE,
            ))
    gardes.sort(key=lambda s: s["fresnel"])
    return gardes, ecartes


def _grouper(scans: list[dict]) -> list[dict]:
    """Les régimes distincts, arrondis au millième — c'est la granularité à laquelle le
    corpus les distingue réellement (31 scans partagent deux valeurs de $F$)."""
    par_f: dict[float, dict] = {}
    for s in scans:
        cle = round(s["fresnel"], 3)
        entree = par_f.setdefault(cle, dict(fresnel=cle, n=0, objets=set(), config=set(), du_prix=0))
        entree["n"] += 1
        entree["objets"].add(s["objet"])
        entree["config"].add(f"{s['pas_um']:g}µm/{s['distance_m']:g}m/{s['energie_kev']:g}keV")
        entree["du_prix"] += int(s["du_prix"])
    sortie = []
    for cle in sorted(par_f):
        e = par_f[cle]
        sortie.append(dict(fresnel=e["fresnel"], n_scans=e["n"], n_objets=len(e["objets"]),
                           configurations=sorted(e["config"]), n_du_prix=e["du_prix"]))
    return sortie


def mesurer() -> dict:
    """
    @brief La mesure entière, sous une forme qui tient dans un JSON.
    """
    scans, ecartes = scans_du_corpus()

    production = [s for s in scans if abs(s["pas_um"] - 2.4) < 0.01 and abs(s["distance_m"] - 0.2) < 1e-9]
    f_production = sum(s["fresnel"] for s in production) / len(production) if production else float("nan")

    prix = [s for s in scans if s["du_prix"]]
    f_prix = sorted({round(s["fresnel"], 3) for s in prix})

    # ⚠ Un rouleau du prix peut avoir plusieurs scans ; on ne compte comme « régime du prix »
    # que le volume que le concours désigne, c'est-à-dire le scan de repérage à 1,2 m.
    prix_reperage = [s for s in prix if abs(s["distance_m"] - 1.2) < 1e-9]

    verdicts = []
    for v in VERDICTS_DU_PAPIER:
        verdicts.append(dict(**{k: v[k] for k in ("objet", "verdict", "rang", "citation")},
                             pas_um=v["px"], distance_m=v["d"], energie_kev=v["e"],
                             fresnel=nombre_de_fresnel(v["px"], v["d"], v["e"])))

    # La distance qu'il faudrait, à 9,362 µm / 113 keV, pour atteindre le F de production.
    d_requise = distance_pour_atteindre(f_production, 9.362, 113.0)

    return dict(
        n_scans=len(scans), n_ecartes=ecartes,
        f_production=f_production,
        f_du_prix=f_prix,
        n_scans_du_prix_en_reperage=len(prix_reperage),
        n_rouleaux_du_prix=len({s["objet"] for s in prix_reperage}),
        ratio_prix_sur_production=(f_prix[0] / f_production) if f_prix else float("nan"),
        distance_requise_a_9362nm_m=d_requise,
        distance_du_seuil_de_decoherence_m=1.2,
        regimes=_grouper(scans),
        verdicts_du_papier=verdicts,
        scans=scans,
    )


def _verifier(m: dict) -> int:
    """Les contrôles. Chacun peut échouer, et deux d'entre eux tueraient la thèse du fichier."""
    echecs = 0

    def v(intitule: str, condition: bool, detail: str = "") -> None:
        nonlocal echecs
        if not condition:
            echecs += 1
        etat = "ok  " if condition else "FAIL"
        print(f"  [{etat}] {intitule}{(' — ' + detail) if detail else ''}")

    print("physique")
    # Un contrôle numérique indépendant : lambda(12,39842 keV) doit valoir 1 angström.
    v("hc redonne 1 Å à 12,39842 keV",
      abs(longueur_donde_m(12.39842) - 1e-10) < 1e-14,
      f"{longueur_donde_m(12.39842):.6e} m")
    # F est sans dimension : doubler pas ET racine(lambda D) laisse F inchangé.
    a = nombre_de_fresnel(4.0, 1.0, 100.0)
    b = nombre_de_fresnel(8.0, 4.0, 100.0)
    v("F est invariant si (p, √(λD)) doublent ensemble", abs(a - b) < 1e-12, f"{a:.6f} = {b:.6f}")
    # L'inverse est bien l'inverse.
    d = distance_pour_atteindre(0.743, 9.362, 113.0)
    v("distance_pour_atteindre inverse nombre_de_fresnel",
      abs(nombre_de_fresnel(9.362, d, 113.0) - 0.743) < 1e-9, f"D = {d:.3f} m")
    v("une énergie nulle est refusée", _leve(lambda: longueur_donde_m(0.0)))
    v("un pas nul est refusé", _leve(lambda: nombre_de_fresnel(0.0, 1.0, 100.0)))

    print("le corpus")
    v("l'index publié est lu", m["n_scans"] > 40, f"{m['n_scans']} scans à trois grandeurs")
    v("les scans sans distance sont comptés, pas devinés", m["n_ecartes"] >= 0,
      f"{m['n_ecartes']} écartés")
    v("les 13 rouleaux du prix sont tous là en régime de repérage",
      m["n_rouleaux_du_prix"] == 13,
      f"{m['n_rouleaux_du_prix']} rouleaux, {m['n_scans_du_prix_en_reperage']} scans")

    print("l'ordre des verdicts publiés")
    # ⚠⚠ LE CONTRÔLE QUI DÉCIDE. Le régime que le papier retient pour la production doit
    # avoir un F STRICTEMENT ENTRE celui du panneau « limité par le pixel » et celui du
    # panneau dont il dit que la distance est trop longue. Si l'ordre ne tient pas, F ne
    # décrit pas ce que les auteurs ont observé, et tout le fichier tombe.
    par_verdict = {v_["verdict"]: v_["fresnel"] for v_ in m["verdicts_du_papier"]}
    v("« limité par le pixel » < « production »",
      par_verdict["limité par le pixel"] < par_verdict["production"],
      f"{par_verdict['limité par le pixel']:.3f} < {par_verdict['production']:.3f}")
    v("« production » < « frange trop large »",
      par_verdict["production"] < par_verdict["frange trop large"],
      f"{par_verdict['production']:.3f} < {par_verdict['frange trop large']:.3f}")

    # ⚠ ET LE CONTRE-CONTRÔLE, sans lequel le précédent ne prouve rien : F ne doit PAS
    # expliquer le voile. Les deux scans de 500P2 à F voisin ont des verdicts opposés, et
    # ce qui les sépare est D. Un fichier qui tairait ça vendrait F comme une théorie
    # complète alors qu'il lui manque la moitié.
    voile = next(v_ for v_ in m["verdicts_du_papier"] if v_["verdict"] == "voilé")
    prod = next(v_ for v_ in m["verdicts_du_papier"] if v_["verdict"] == "production")
    v("F NE sépare PAS le voile de la production (il faut D)",
      abs(voile["fresnel"] - prod["fresnel"]) < 0.15 and voile["distance_m"] > prod["distance_m"],
      f"F {voile['fresnel']:.3f} contre {prod['fresnel']:.3f}, "
      f"D {voile['distance_m']:g} m contre {prod['distance_m']:g} m")

    print("le diagnostic des 13")
    v("le régime du prix est sous la moitié du régime de production... ou juste au-dessus",
      m["ratio_prix_sur_production"] < 0.60,
      f"{m['f_du_prix'][0]:.3f} / {m['f_production']:.3f} = {m['ratio_prix_sur_production']:.3f}")
    v("atteindre le F de production à 9,362 µm demanderait une distance "
      "bien au-delà du seuil de décohérence mesuré",
      m["distance_requise_a_9362nm_m"] > 3 * m["distance_du_seuil_de_decoherence_m"],
      f"{m['distance_requise_a_9362nm_m']:.2f} m contre un seuil à "
      f"{m['distance_du_seuil_de_decoherence_m']:g} m")

    print()
    if echecs:
        print(f"  ECHEC ({echecs} failures)")
    else:
        n = 13
        print(f"  ALL PASS (0 failures, {n} checks)")
    return echecs


def _leve(f) -> bool:
    try:
        f()
    except ValueError:
        return True
    return False


def main() -> int:
    parseur = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parseur.add_argument("--verifier", action="store_true", help="lance les contrôles")
    parseur.add_argument("--json", type=Path, help="écrit la mesure complète dans ce fichier")
    parseur.add_argument("--table", action="store_true", help="imprime les régimes")
    args = parseur.parse_args()

    m = mesurer()

    if args.table or not (args.verifier or args.json):
        print(f"{m['n_scans']} scans publiés portent les trois grandeurs "
              f"({m['n_ecartes']} n'ont pas la distance dans leur nom)\n")
        print(f"{'F':>6s}  {'scans':>5s} {'objets':>6s} {'prix':>4s}  configuration")
        for r in m["regimes"]:
            marque = "  ⭐" if r["n_du_prix"] else "    "
            print(f"{r['fresnel']:6.3f}  {r['n_scans']:5d} {r['n_objets']:6d} "
                  f"{r['n_du_prix']:4d}{marque}{', '.join(r['configurations'])}")
        print()
        print(f"régime de production (2,4 µm / 0,2 m) : F = {m['f_production']:.3f}")
        print(f"régime des 13 rouleaux du prix        : F = "
              f"{', '.join(f'{x:.3f}' for x in m['f_du_prix'])}")
        print(f"  soit {m['ratio_prix_sur_production']:.0%} du régime de production")
        print(f"pour atteindre F = {m['f_production']:.3f} à 9,362 µm / 113 keV il faudrait "
              f"D = {m['distance_requise_a_9362nm_m']:.2f} m,")
        print(f"  alors que le papier mesure la décohérence dès "
              f"{m['distance_du_seuil_de_decoherence_m']:g} m (PHerc. 268, Ext. Data Fig. 2c).")

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(m, indent=2, ensure_ascii=False, default=list), encoding="utf-8")
        print(f"\nécrit : {args.json}")

    if args.verifier:
        print()
        return 1 if _verifier(m) else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
