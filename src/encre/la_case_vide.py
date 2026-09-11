#!/usr/bin/env python3
"""Le plan d'expérience du régime du prix est publié, et il lui manque exactement une case.

⚠⚠⚠ POURQUOI CE FICHIER EXISTE, et c'est une RÉOUVERTURE. Deux conclusions de ce dépôt
disent que la mesure décisive est hors de portée :

  - `docs/archive/HANDOFF.md` : « **énergie** isolée contre étiquettes ❌ **impossible en l'état** :
    `Frag1`–`Frag3` ont les labels sans recalage, `Frag5`/`Frag6` le recalage sans labels, et
    les volumes d'une paire n'ont pas la même forme » ;
  - `ou_la_verite_existe.py` : **zéro rouleau mesurable sur cinq**.

Les deux étaient vraies de ce qu'elles regardaient — l'ancien layout `fragments/` et cinq
rouleaux. Elles sont **fausses du corpus ESRF publié depuis**, et c'est la lecture intégrale
du papier de référence (Angelotti et al., arXiv 2606.29085) qui l'a montré, parce que le
papier nomme ses fragments de supervision et que le corpus les publie autrement.

⭐⭐⭐ CE QUE LE CORPUS PORTE, ET QUE PERSONNE N'AVAIT REGARDÉ. `data/metadata.min.json`
publie un champ `volume_transforms` : des matrices de recalage **entre volumes d'un même
objet**. Dix objets en portent. Et six d'entre eux relient le **régime du prix** (8,6–9,4 µm
à 1,2 m, cf. `nombre_de_fresnel.py`) au **régime de production** (2,2–2,4 µm à 0,2–0,4 m).
Trois de ces six sont exactement les trois fragments dont le papier tire **toute** sa
supervision d'encre : `PHerc0009B`, `PHerc0343P`, `PHerc0500P2`.

⭐⭐⭐ ET LA CASE VIDE. Pour `PHerc0500P2`, le segment `20250628074500-500P2_front` — celui
que l'Extended Data Fig. 5 du papier montre comme l'exemple de supervision, avec sa
photographie infrarouge recalée dessus — est publié avec :

  - la **même surface** transformée dans les trois repères de volume (2,215 / 4,317 / 9,362 µm) ;
  - les **piles de couches rendues** dans les trois ;
  - et une carte d'encre **uniquement depuis le volume à 2,215 µm**.

Donc : même objet, même surface, même aplatissement, une vérité terrain infrarouge, un
témoin positif publié — et **la case du régime du prix est vide**. Personne n'a publié ce
que l'encre donne à 9,362 µm sur un fragment dont on connaît la réponse.

⭐⭐ POURQUOI C'EST LA MESURE QUI DÉCIDE. Le Grand Prix demande 70 % des caractères lisibles
sur des rouleaux qui n'existent QUE dans le régime du prix. Remplir cette case répond à la
question dont tout le reste dépend, et elle ne demande **ni faisceau, ni annotation
manuelle, ni rescan** : les couches sont déjà rendues, il n'y a qu'à faire tourner un modèle
dessus et à scorer contre les mêmes étiquettes.

⚠⚠ ET LE PIÈGE QUE LE NOM DE FICHIER PUBLIÉ RÉVÈLE. Les deux cartes d'encre publiées de ce
segment portent `tile256-stride128`. À 2,215 µm une tuile de 256 pixels couvre **567 µm**,
donc moins qu'une lettre — et c'est là toute la défense anti-hallucination du papier :
*« This input size is smaller than all letters detected […] making full-letterform
hallucinations from linguistic or word-level priors practically impossible. »* À 9,362 µm,
la même tuile de 256 pixels couvre **2397 µm**, soit BIEN PLUS qu'une lettre. **La garantie
ne se transporte pas.** Qui rendrait cette case avec la tuile héritée obtiendrait un
résultat sans la propriété qui rendait l'original crédible. Pour conserver la garantie il
faut une tuile d'environ 61 pixels.

⚠ CE QUE CE FICHIER NE FAIT PAS : il ne télécharge rien et ne rend aucune carte. Il établit
quelles cases existent, laquelle manque, et ce que la remplir exigerait. C'est un relevé,
pas une mesure d'encre.

Sources :
  - `data/metadata.min.json`, index publié du bucket `vesuvius-challenge-open-data` ;
  - papier : `data/site/scrollprize.org/pdf/main.pdf`, Extended Data Fig. 5 (p. 38, le
    segment `500P2_front` et sa photographie infrarouge) et Fig. 6 (p. 39, la tuile de
    256 pixels valant 614 µm à 2,4 µm).

Usage :
    uv run python src/encre/la_case_vide.py --verifier
    uv run python src/encre/la_case_vide.py --json docs/mesures/la_case_vide.json
"""

from __future__ import annotations

import argparse
import gzip
import json
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src"))

from encre.nombre_de_fresnel import nombre_de_fresnel  # noqa: E402

INDEX = RACINE / "data" / "metadata.min.json"

SEUIL_DISTANCE_M = 1.0
"""⚠⚠ CE QUI SÉPARE LES DEUX RÉGIMES EST LA DISTANCE DE PROPAGATION, et rien d'autre —
parce que c'est la variable autour de laquelle les campagnes sont organisées, et parce que
c'est un fait publié plutôt qu'un score dérivé.

⚠ Ma première version classait par le nombre de Fresnel, avec un seuil à 0,60. Une sonde l'a
tuée, et elle avait raison deux fois : le plus grand vide de la distribution de $F$ n'est pas
entre les deux campagnes mais tout en haut (1,82 → 2,51), et surtout un scan de production
(`PHercParis4`, 2,4 µm / 0,2 m / **137 keV**) tombe à $F = 0{,}561$, donc **sous** le seuil,
alors qu'il est à courte propagation. $F$ explique la qualité — c'est la thèse de
`nombre_de_fresnel.py` — mais il ne classe pas les campagnes, et s'en servir pour ça
introduisait un nombre qu'il fallait défendre.

La distance, elle, n'en demande aucun : le corpus publie 0,07 / 0,1 / 0,2 / 0,22 / 0,3 /
0,4 m d'un côté, **1,2 et 11 m** de l'autre. Un vide d'un facteur trois, sans une seule
valeur au milieu. `--verifier` contrôle que ce vide existe encore."""

# Les trois fragments dont le papier tire TOUTE sa supervision d'encre (Methods, « Ink
# detection: from fragments to sealed scrolls » : « a dataset composed of PHerc. 9B,
# PHerc. 343P and PHerc. 500P2 »).
FRAGMENTS_DE_SUPERVISION = ("PHerc0009B", "PHerc0343P", "PHerc0500P2")

BORNES_DU_PRIX_UM = (8.0, 10.0)
"""⚠⚠ Toutes les cases vides ne se valent pas, et les confondre gonflerait le résultat. Le
corpus contient aussi des scans de **repérage grossier** à 45,5 µm sur 11 m — des vues
d'ensemble, jamais destinées à porter de l'encre. Leur case est vide pour une raison sans
intérêt. Seules comptent celles du régime dans lequel vivent les 13 rouleaux du prix."""

TUILE_DU_PAPIER_PX = 256
PAS_DU_PAPIER_UM = 2.4
"""Extended Data Fig. 6 : « The model input is a 256 × 256 × 62-voxel cuboid », à 2,4 µm,
soit 614 µm — « smaller than all letters detected »."""

_PARAMS = re.compile(r"(?P<px>[\d.]+)um-(?P<d>[\d.]+)m-(?P<e>[\d.]+)keV")


def _charger() -> dict:
    brut = INDEX.read_bytes()
    try:
        texte = gzip.decompress(brut).decode()
    except (OSError, gzip.BadGzipFile):
        texte = brut.decode()
    return json.loads(texte)["samples"]


def tuile_equivalente(pas_um: float) -> int:
    """
    @brief La tuile qui, au pas donné, couvre la même longueur physique que celle du papier.

    ⚠ C'est la seule façon de transporter la garantie anti-hallucination : ce qui la produit
    n'est pas « 256 pixels » mais « moins qu'une lettre ». Garder 256 en changeant de pas,
    c'est garder le nombre et jeter la propriété.
    """
    return max(1, round(TUILE_DU_PAPIER_PX * PAS_DU_PAPIER_UM / pas_um))


def _regime(distance_m: float) -> str:
    """
    @brief Repérage ou production, décidé par la seule distance de propagation.
    """
    return "reperage" if distance_m >= SEUIL_DISTANCE_M else "production"


def relever() -> dict:
    """
    @brief Le relevé : qui a deux régimes recalés, et quelles représentations existent où.
    """
    index = _charger()

    objets: list[dict] = []
    for nom, fiche in sorted(index.items()):
        transformes = fiche.get("sample", {}).get("properties", {}).get("volume_transforms")
        if not transformes:
            continue

        # Le régime de chaque volume, via le scan dont il vient.
        scans = fiche.get("scans", {})
        par_volume: dict[str, dict] = {}
        for vid, v in fiche.get("volumes", {}).items():
            scan = scans.get(v.get("scan_id"), {})
            trouve = _PARAMS.search(scan.get("long_id", ""))
            if not trouve:
                continue
            px, dist, ene = (float(trouve.group("px")), float(trouve.group("d")),
                             float(trouve.group("e")))
            par_volume[vid] = dict(volume=vid, pas_um=px, distance_m=dist, energie_kev=ene,
                                   fresnel=nombre_de_fresnel(px, dist, ene),
                                   regime=_regime(dist))

        # Les paires effectivement recalées, et ce qu'elles franchissent.
        paires = set()
        for t in transformes:
            src = t.get("from_volume_id")
            for to in t.get("transforms", []):
                dst = to.get("to_volume_id")
                if src in par_volume and dst in par_volume and src != dst:
                    paires.add(tuple(sorted((src, dst))))
        franchissantes = [
            p for p in sorted(paires)
            if par_volume[p[0]]["regime"] != par_volume[p[1]]["regime"]
        ]
        if not franchissantes:
            continue

        # Sur quels volumes une pile de couches / une carte d'encre est publiée.
        couches: set[str] = set()
        encre: set[str] = set()
        segments_utiles: list[dict] = []
        for sid, seg in fiche.get("segments", {}).items():
            c_seg: set[str] = set()
            e_seg: set[str] = set()
            for entree in seg.get("data", []):
                chemin = entree.get("origins", [{}])[0].get("path", "")
                trouve = _PARAMS.search(chemin)
                if not trouve:
                    continue
                cle = f"{trouve.group('px')}um-{trouve.group('d')}m-{trouve.group('e')}keV"
                if entree.get("type") == "layers-zarr":
                    c_seg.add(cle)
                elif entree.get("type") == "ink-detection":
                    e_seg.add(cle)
            couches |= c_seg
            encre |= e_seg
            # ⚠ Ce qui nous intéresse : un segment dont les couches existent dans les DEUX
            # régimes. C'est lui, et lui seul, qui rend la comparaison contrôlée.
            regimes_du_segment = {_regime(float(_PARAMS.search(c).group("d"))) for c in c_seg}
            if len(regimes_du_segment) > 1:
                sans_encre = sorted(
                    c for c in c_seg
                    if c not in e_seg
                    and _regime(float(_PARAMS.search(c).group("d"))) == "reperage"
                )
                segments_utiles.append(dict(
                    segment=seg.get("long_id", sid),
                    couches=sorted(c_seg), encre=sorted(e_seg),
                    couches_sans_encre_en_reperage=sans_encre,
                ))

        objets.append(dict(
            objet=nom,
            type=fiche.get("sample", {}).get("properties", {}).get("type"),
            de_supervision=nom in FRAGMENTS_DE_SUPERVISION,
            volumes=sorted(par_volume.values(), key=lambda v: v["fresnel"]),
            n_paires_franchissantes=len(franchissantes),
            segments_a_deux_regimes=segments_utiles,
        ))

    # Le vide des distances publiées, qui est ce qui rend le seuil non ajustable.
    distances = sorted({v["distance_m"] for o in objets for v in o["volumes"]})
    sous = [d for d in distances if d < SEUIL_DISTANCE_M]
    sur = [d for d in distances if d >= SEUIL_DISTANCE_M]

    cases_vides = []
    for o in objets:
        for s in o["segments_a_deux_regimes"]:
            for cle in s["couches_sans_encre_en_reperage"]:
                px = float(_PARAMS.search(cle).group("px"))
                cases_vides.append(dict(
                    objet=o["objet"], segment=s["segment"], couches=cle,
                    encre_publiee=s["encre"],
                    du_regime_du_prix=BORNES_DU_PRIX_UM[0] < px < BORNES_DU_PRIX_UM[1],
                ))

    du_prix = [c for c in cases_vides if c["du_regime_du_prix"]]
    par_objet: dict[str, int] = {}
    for c in du_prix:
        par_objet[c["objet"]] = par_objet.get(c["objet"], 0) + 1

    return dict(
        n_objets_recales=len(objets),
        n_de_supervision=sum(1 for o in objets if o["de_supervision"]),
        distances_publiees=distances,
        vide_du_seuil=dict(sous=max(sous) if sous else None, sur=min(sur) if sur else None),
        tuile_a_9362nm=tuile_equivalente(9.362),
        tuile_heritee=TUILE_DU_PAPIER_PX,
        largeur_tuile_heritee_a_9362nm_um=TUILE_DU_PAPIER_PX * 9.362,
        largeur_tuile_du_papier_um=TUILE_DU_PAPIER_PX * PAS_DU_PAPIER_UM,
        n_cases_vides=len(cases_vides),
        n_cases_vides_du_prix=len(du_prix),
        cases_vides_du_prix_par_objet=dict(sorted(par_objet.items(),
                                                  key=lambda kv: -kv[1])),
        cases_vides=cases_vides,
        objets=objets,
    )


def _verifier(m: dict) -> int:
    echecs = 0

    def v(intitule: str, condition: bool, detail: str = "") -> None:
        nonlocal echecs
        if not condition:
            echecs += 1
        print(f"  [{'ok  ' if condition else 'FAIL'}] {intitule}"
              f"{(' — ' + detail) if detail else ''}")

    print("le corpus porte bien des paires recalées franchissant les régimes")
    v("plusieurs objets ont un recalage inter-régimes", m["n_objets_recales"] >= 5,
      f"{m['n_objets_recales']} objets")
    v("les trois fragments de supervision du papier en sont",
      m["n_de_supervision"] == 3, f"{m['n_de_supervision']} sur 3")

    print("le seuil de régime n'est pas un nombre choisi après coup")
    # ⚠⚠ Une sonde a tué la version précédente, qui classait par le nombre de Fresnel : elle
    # passait encore avec un seuil posé en plein milieu du groupe de production. Le contrôle
    # porte donc sur ce qui n'est pas ajustable — le vide des distances RÉELLEMENT publiées.
    sous, sur = m["vide_du_seuil"]["sous"], m["vide_du_seuil"]["sur"]
    # ⚠ Comparé à 2,5 et non à 3 : le rapport vaut exactement trois, et un `>= 3.0` sur des
    # flottants échoue sur 1,2/0,4 = 2,9999999999999996. Le facteur mesuré est imprimé.
    v("un vide large sépare les distances publiées",
      sous is not None and sur is not None and sur / sous > 2.5,
      f"{sous} m … {sur} m, facteur {sur / sous:.1f} "
      f"({', '.join(str(d) for d in m['distances_publiees'])})")
    v("le seuil tombe dedans", sous < SEUIL_DISTANCE_M <= sur,
      f"{sous} < {SEUIL_DISTANCE_M} ≤ {sur}")

    print("la case vide")
    v("des cases du RÉGIME DU PRIX sont publiées en couches et sans encre",
      m["n_cases_vides_du_prix"] >= 1,
      f"{m['n_cases_vides_du_prix']} sur {m['n_cases_vides']} cases vides "
      f"(le reste est du repérage grossier à 45,5 µm, sans intérêt)")
    # ⚠⚠ LE CONTRÔLE QUI DISCRIMINE : il ne suffit pas qu'une case soit vide. Il faut qu'un
    # TÉMOIN POSITIF existe sur le même segment — une carte d'encre publiée dans l'autre
    # régime. Sans lui, une case vide voudrait dire « personne n'a rendu ce segment », ce
    # qui ne prouve rien. Avec lui, elle veut dire « on a rendu l'un et pas l'autre ».
    avec_temoin = [c for c in m["cases_vides"] if c["du_regime_du_prix"] and c["encre_publiee"]]
    v("... et le même segment porte une carte d'encre dans l'AUTRE régime (témoin positif)",
      len(avec_temoin) >= 1,
      f"{len(avec_temoin)} case(s) avec témoin ; "
      + (f"{avec_temoin[0]['objet']} {avec_temoin[0]['segment']}" if avec_temoin else "aucune"))

    print("la garantie anti-hallucination ne se transporte pas telle quelle")
    v("la tuile héritée couvre bien plus qu'une lettre au pas du prix",
      m["largeur_tuile_heritee_a_9362nm_um"] > 3 * m["largeur_tuile_du_papier_um"],
      f"{m['largeur_tuile_heritee_a_9362nm_um']:.0f} µm contre "
      f"{m['largeur_tuile_du_papier_um']:.0f} µm chez les auteurs")
    v("la tuile équivalente au pas du prix est bien plus petite que 256",
      m["tuile_a_9362nm"] < 100, f"{m['tuile_a_9362nm']} px")

    print()
    if echecs:
        print(f"  ECHEC ({echecs} failures)")
    else:
        print("  ALL PASS (0 failures, 8 checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    args = p.parse_args()

    m = relever()

    if not args.verifier or args.json is None:
        print(f"{m['n_objets_recales']} objets publient un recalage franchissant les deux "
              f"régimes, dont {m['n_de_supervision']} des 3 fragments de supervision.\n")
        for o in m["objets"]:
            marque = " ⭐ supervision" if o["de_supervision"] else ""
            print(f"{o['objet']} ({o['type']}){marque}")
            for v_ in o["volumes"]:
                print(f"   F={v_['fresnel']:.3f}  {v_['pas_um']:g}µm/{v_['distance_m']:g}m/"
                      f"{v_['energie_kev']:g}keV  [{v_['regime']}]")
            for s in o["segments_a_deux_regimes"]:
                print(f"   segment {s['segment']}")
                print(f"      couches : {', '.join(s['couches'])}")
                print(f"      encre   : {', '.join(s['encre']) or '— aucune —'}")
                if s["couches_sans_encre_en_reperage"]:
                    print(f"      ⭐ CASE VIDE : "
                          f"{', '.join(s['couches_sans_encre_en_reperage'])}")
            print()
        print(f"cases vides dans le RÉGIME DU PRIX : {m['n_cases_vides_du_prix']} "
              f"(sur {m['n_cases_vides']} au total ; le reste est du repérage à 45,5 µm)")
        for objet, n in m["cases_vides_du_prix_par_objet"].items():
            print(f"   {n:4d}  {objet}")
        print()
        print(f"tuile : {m['tuile_heritee']} px valent {m['largeur_tuile_du_papier_um']:.0f} µm "
              f"à 2,4 µm (moins qu'une lettre), et "
              f"{m['largeur_tuile_heritee_a_9362nm_um']:.0f} µm à 9,362 µm.")
        print(f"        pour garder la propriété il faut {m['tuile_a_9362nm']} px.")

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(m, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nécrit : {args.json}")

    if args.verifier:
        print()
        return 1 if _verifier(m) else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
