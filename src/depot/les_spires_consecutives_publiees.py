#!/usr/bin/env python3
"""Sur quel objet peut-on VÉRIFIER trente et une spires ?

⚠⚠⚠ POURQUOI CE FICHIER EXISTE, ET C'EST LA QUESTION QUE `31` §10 POSE MAL. La feuille de route
inscrit au calendrier « mesurer la part comprimée rouleau par rouleau » pour décider **sur lequel
des treize** dépenser six mois. `combien_de_fenetres` vient de montrer que ce critère-là coûte
**315 fois** son budget. Ce fichier pose la question qui le précède, et elle est gratuite : *sur
lequel des treize a-t-on de quoi vérifier quoi que ce soit ?*

⭐⭐⭐ LA RÉPONSE ÉLIMINE ONZE DES TREIZE SANS AUCUNE MESURE DE DIFFICULTÉ : ils ne publient
**aucun segment**. Pas un de moins bonne qualité — aucun. Les deux qui en publient
(`PHerc0800`, `PHerc1447`) ne publient que des `auto_grown_*`, des morceaux **sans rang de
spire**, donc qu'on ne peut pas ordonner en spirale sans les remesurer. Le classement de `16` ne
peut donc pas être exécuté : il désigne un objet sur lequel il n'existe ni ancre pour partir, ni
vérité de terrain pour dire jusqu'où on est allé.

⭐⭐ ET LE CRITÈRE QUI RESTE EST CELUI DE L'OBJECTIF, PAS CELUI DE L'ENCRE. La portée est un
**nombre de spires traversées** avant que l'erreur dépasse la demi-feuille. On ne peut donc la
mesurer que jusqu'où le corpus publie des spires **consécutives** : un corpus de morceaux épars
ne borne aucune portée, et un corpus de treize spires ne peut pas témoigner d'une marche de
trente et une. Le prix demande 31 (l'état de l'art, `00_etat_de_lart` : 31 spires sur
`PHerc1667`, ~775 h d'humain). **Le corpus dit lesquels des objets peuvent porter cette
preuve.**

⚠⚠ UNE ERREUR QUE J'AI FAITE ET QUI EST DANS LE FICHIER POUR NE PAS ÊTRE REFAITE : un suffixe
`w046-052` nomme un **intervalle** de spires, pas un rang. En lisant le premier nombre seul,
`PHercParis4` rendait 28 spires et **91 trous** — alors qu'il en publie **120 d'affilée, sans un
seul trou**. Une lecture qui invente des trous ne se lit pas comme un bug : elle se lit comme un
corpus lacunaire, et elle aurait éliminé le meilleur objet du dépôt.

⚠ ET LE FAUX POSITIF SYMÉTRIQUE EST GARDÉ : `auto_grown_20251115002740308_5_flatboi` finit par
`_5_`, qui n'est **pas** un rang de spire mais un indice de morceau. Un rang se nomme par un
préfixe `w`/`wrap`, jamais par un nombre isolé. Confondre les deux ferait passer une pile de
patches pour une spirale ordonnée — exactement l'inverse du service rendu.

⚠ L'INDEX EST UN CACHE, PAS UNE AUTORITÉ. `data/metadata.min.json` date du jour où il a été
tiré ; `ce_que_les_serveurs_publient` interroge S3 et l'a confirmé pour les objets cités, à une
exception près (`PHerc1447` : 15 en cache, 16 sur S3). Ce fichier ne prétend donc jamais dire ce
que les serveurs publient **aujourd'hui** ; il dit ce que l'index connaît, et nomme l'outil qui
tranche.

Usage :
    uv run python src/depot/les_spires_consecutives_publiees.py
    uv run python src/depot/les_spires_consecutives_publiees.py --verifier
    uv run python src/depot/les_spires_consecutives_publiees.py \\
        --json docs/mesures/les_spires_consecutives_publiees.json
"""

from __future__ import annotations

import argparse
import gzip
import json
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
INDEX = RACINE / "data" / "metadata.min.json"

# ⚠ Les treize du Grand Prize, lus du dossier des parts publiées plutôt que retapés : une liste
# écrite ici pourrait cesser d'être celle de `16` sans que rien ne le dise.
CARTE = RACINE / "docs" / "carte_separabilite"

# ⭐ Ce que le prix demande, et il vient de l'état de l'art, pas d'un choix : 31 spires déroulées
# à la main sur `PHerc1667` (arXiv 2606.29085), ~25 h chacune, ~775 h au total.
SPIRES_DU_PRIX = 31

# ⚠⚠ CE QUI COMPTE COMME GÉOMÉTRIE, ET C'EST LU DU DÉPÔT, PAS SUPPOSÉ. `deux_aplatissements`
# établit que `tifxyz-transformed` publie **une position 3D par cellule** — donc la marche peut le
# consommer exactement comme `tifxyz`. Filtrer sur `tifxyz` seul aurait publié « PHerc0172 n'a
# qu'UNE spire marchable » alors qu'il en a quarante-quatre : une limite de mon filtre présentée
# comme une limite du corpus, ce que ce dépôt appelle son péché numéro un.
# ⚠ `tifxyz-flattened` et `tifxyz-normalized` sont volontairement DEHORS : aucune mesure du dépôt
# n'a établi ce qu'ils portent, et les compter serait affirmer sans avoir regardé.
GEOMETRIE = ("tifxyz", "tifxyz-transformed")

# ⚠⚠ LE RANG SE NOMME, IL NE SE DEVINE PAS. `w052_...`, `wrap01_...`, `w0_...` et l'intervalle
# `w046-052`. Le groupe 2 est la borne haute d'un intervalle ; il est optionnel, et son absence
# veut dire « une seule spire », jamais « je n'ai pas su lire ».
RANG = re.compile(r"(?:^|[^0-9a-z])w(?:rap)?_?0*([0-9]{1,3})(?:\s*-\s*w?0*([0-9]{1,3}))?(?![0-9])",
                  re.I)


def charger_index(chemin: Path = INDEX) -> dict:
    """Les échantillons de l'index, que le fichier soit gzippé ou non.

    ⚠ LE NOM DIT `.json` ET LE CONTENU EST DU GZIP. Un `json.load` direct rend une
    `UnicodeDecodeError` sur l'octet 0x8b, ce qui ne ressemble pas du tout à « ce fichier est
    compressé ». La signature est donc **reniflée** plutôt que déduite de l'extension : si un
    jour l'index est publié en clair, ce lecteur continue de marcher.
    """
    brut = chemin.read_bytes()
    if brut[:2] == b"\x1f\x8b":
        brut = gzip.decompress(brut)
    return json.loads(brut)["samples"]


def rangs_du_suffixe(suffixe: str) -> set[int]:
    """Les rangs de spire que ce nom de segment revendique.

    ⚠⚠ UN INTERVALLE EST DÉPLIÉ, PAS RÉDUIT À SA BORNE BASSE. `w046-052` publie sept spires ;
    n'en compter qu'une invente six trous qui n'existent pas, et un corpus faussement lacunaire
    se lit comme un corpus pauvre.

    ⚠ Un intervalle décroissant est **refusé** plutôt que retourné : `w052-046` n'a pas de
    lecture évidente, et en choisir une en silence serait décider à la place de qui a nommé.
    """
    trouves: set[int] = set()
    for m in RANG.finditer(suffixe):
        debut = int(m.group(1))
        fin = int(m.group(2)) if m.group(2) is not None else debut
        if fin < debut:
            continue
        trouves.update(range(debut, fin + 1))
    return trouves


def spires_publiees(echantillon: dict, types: tuple[str, ...] | None = None) -> set[int]:
    """Les rangs de spire publiés par cet échantillon, éventuellement filtrés sur un type.

    ⚠ LE TYPE COMPTE POUR LA MARCHE. Une marche a besoin d'une **position 3D par cellule** ;
    `obj` n'a pas la topologie de grille, et `ink-detection` n'est pas de la géométrie. Compter
    tous les types confondrait « cette spire est publiée » avec « cette spire est marchable ».
    """
    rangs: set[int] = set()
    for seg in echantillon.get("segments", {}).values():
        if types is not None:
            portes = {d.get("type") for d in seg.get("data", [])}
            if not portes & set(types):
                continue
        rangs |= rangs_du_suffixe(seg.get("suffix", ""))
    return rangs


def plus_longue_suite(rangs: set[int]) -> tuple[int, int, int]:
    """La plus longue suite de rangs consécutifs : (longueur, premier, dernier).

    ⭐ C'EST LA GRANDEUR QUI PLAFONNE LA PORTÉE. Une portée est un nombre de spires traversées
    avant échec ; au-delà du dernier rang publié d'affilée, il n'existe plus rien contre quoi
    dire qu'on a franchi une spire de plus. Deux tronçons séparés par un trou ne se recollent
    pas : le trou est précisément l'endroit où la marche ne serait plus vérifiable.
    """
    if not rangs:
        return (0, 0, 0)
    ordonnes = sorted(rangs)
    meilleur = courant = 1
    debut = fin = premier = ordonnes[0]
    for a, b in zip(ordonnes, ordonnes[1:]):
        if b == a + 1:
            courant += 1
        else:
            courant, premier = 1, b
        if courant > meilleur:
            meilleur, debut, fin = courant, premier, b
    if meilleur == 1:
        debut = fin = ordonnes[0]
    return (meilleur, debut, fin)


def les_treize(carte: Path = CARTE) -> list[str]:
    """Les treize rouleaux du Grand Prize, lus du dossier des parts publiées."""
    return sorted(f.stem for f in carte.glob("*.json") if not f.stem.startswith("_TEMOIN_"))


def mesurer(chemin: Path = INDEX, carte: Path = CARTE) -> dict:
    """Le corpus de spires consécutives de chaque échantillon de l'index."""
    ech = charger_index(chemin)
    treize = set(les_treize(carte))
    lignes = []
    for nom, e in ech.items():
        rangs = spires_publiees(e)
        marchables = spires_publiees(e, types=GEOMETRIE)
        n, a, b = plus_longue_suite(rangs)
        nm, ma, mb = plus_longue_suite(marchables)
        etendue = (max(rangs) - min(rangs) + 1) if rangs else 0
        lignes.append({
            "nom": nom,
            "du_prix": nom in treize,
            "segments": len(e.get("segments", {})),
            "rangs": len(rangs),
            "etendue": etendue,
            "trous": etendue - len(rangs),
            "suite": n, "suite_de": a, "suite_a": b,
            "rangs_geometrie": len(marchables), "suite_geometrie": nm,
            "geometrie_de": ma, "geometrie_a": mb,
            "porte_le_prix": n >= SPIRES_DU_PRIX,
            # ⭐⭐ LA PORTÉE MAXIMALE MESURABLE, DÉRIVÉE ET JAMAIS CHOISIE. Une portée est un
            # nombre de spires TRAVERSÉES, et `la_portee_du_raccrochage` ancre sur la spire la
            # plus BASSE de la boîte puis monte : depuis une suite de N spires on en traverse
            # donc au plus N-1. C'est la traduction du corpus dans l'unité de l'objectif.
            # ⚠⚠⚠ C'EST UN MAJORANT, ET IL COMPTE DES NOMS. Mesuré sur `PHerc0500P2` : les
            # spires 10 et 11 se suivent par leur numéro et sont à **1000,6 µm** l'une de
            # l'autre, soit 7,4 feuilles — donc le corpus n'autorise en fait que 6 bras. Compter
            # les rangs est NÉCESSAIRE et NON SUFFISANT ; vérifier que deux voisines par leur
            # nom le sont dans la matière coûte un téléchargement (`les_wraps_publies`).
            "portee_maximale_par_les_noms": max(0, n - 1),
            # ⚠⚠ LA LISTE, PAS SEULEMENT LE RESUME. Une figure qui annonce « plein : publie »
            # en ne dessinant que la plus longue suite dessine faux : les rangs isoles de
            # `PHerc1667` sont publies et sortaient vides. Un resume ne peut pas porter une
            # legende qui parle de chaque cellule.
            "rangs_liste": sorted(rangs),
        })
    lignes.sort(key=lambda r: (-r["suite"], -r["segments"], r["nom"]))
    duprix = [r for r in lignes if r["du_prix"]]
    return {
        "index": str(chemin.relative_to(RACINE)),
        "echantillons": len(lignes),
        "spires_du_prix": SPIRES_DU_PRIX,
        "lignes": lignes,
        "du_prix_sans_segment": sorted(r["nom"] for r in duprix if r["segments"] == 0),
        "du_prix_sans_rang": sorted(r["nom"] for r in duprix if r["rangs"] == 0),
        "portent_le_prix": [r["nom"] for r in lignes if r["porte_le_prix"]],
    }


def verifier() -> int:
    echecs = 0
    controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  FAIL {nom} — {detail}")

    # --- le lecteur de rangs, et ses deux pièges ---------------------------------------------
    v("un rang simple est lu", rangs_du_suffixe("w052_20251212105627148_flatboi") == {52})
    v("... un `wrap01` aussi", rangs_du_suffixe("0500P2-wrap01_0919") == {1})
    v("... et un `w0`", rangs_du_suffixe("w0_20251218010446110") == {0})
    # ⭐⭐ L'INTERVALLE : c'est l'erreur qui aurait éliminé le meilleur objet du dépôt.
    v("un intervalle est déplié en entier", rangs_du_suffixe("w046-052") == set(range(46, 53)),
      str(sorted(rangs_du_suffixe("w046-052"))))
    v("... y compris suffixé", rangs_du_suffixe("w046-052_jordi") == set(range(46, 53)))
    v("... et un intervalle décroissant est refusé, pas deviné",
      rangs_du_suffixe("w052-046") == set())
    # ⚠⚠ LE FAUX POSITIF : un nombre isolé n'est pas un rang de spire.
    v("un indice de morceau n'est PAS un rang",
      rangs_du_suffixe("auto_grown_20251115002740308_5_flatboi") == set(),
      str(sorted(rangs_du_suffixe("auto_grown_20251115002740308_5_flatboi"))))
    v("... ni un horodatage", rangs_du_suffixe("20230702185753_v14") == set())
    v("... ni un nom sans rang du tout", rangs_du_suffixe("z_dbg_gen_00225_inp_hr") == set())

    # --- la plus longue suite ----------------------------------------------------------------
    v("une suite pleine est rendue entière", plus_longue_suite({4, 5, 6, 7}) == (4, 4, 7))
    # ⚠ UN TROU COUPE : deux tronçons ne se recollent pas, parce que c'est au trou que la marche
    # cesserait d'être vérifiable.
    v("un trou coupe la suite en deux", plus_longue_suite({1, 2, 3, 9, 10}) == (3, 1, 3),
      str(plus_longue_suite({1, 2, 3, 9, 10})))
    v("... et le plus long tronçon gagne, où qu'il soit",
      plus_longue_suite({1, 2, 5, 6, 7, 8}) == (4, 5, 8), str(plus_longue_suite({1, 2, 5, 6, 7, 8})))
    v("un rang isolé est une suite de un", plus_longue_suite({42}) == (1, 42, 42))
    v("un corpus vide ne porte aucune suite", plus_longue_suite(set()) == (0, 0, 0))

    # --- le lecteur d'index ------------------------------------------------------------------
    # ⚠ L'index est gzippé sous un nom `.json` : un lecteur qui croit l'extension casse.
    v("l'index gzippé s'ouvre quand même", INDEX.exists() and len(charger_index()) > 40,
      f"{len(charger_index()) if INDEX.exists() else 'absent'} échantillons")

    r = mesurer()
    treize = les_treize()
    v("les treize du prix sont lus du dossier, pas retapés", len(treize) == 13, str(treize))

    # --- le verdict sur le dépôt réel --------------------------------------------------------
    # ⭐⭐⭐ ONZE DES TREIZE NE PUBLIENT RIEN. C'est ça, la réponse à « sur lequel dépenser six
    # mois » : la question de `31` §10 n'a pas de réponse exécutable.
    v("onze des treize rouleaux du prix ne publient aucun segment",
      len(r["du_prix_sans_segment"]) == 11, str(r["du_prix_sans_segment"]))
    # ⚠ ET LES DEUX QUI EN PUBLIENT N'EN ORDONNENT AUCUN : des `auto_grown_*` sans rang.
    v("... et les treize, sans exception, ne publient aucun rang de spire",
      len(r["du_prix_sans_rang"]) == 13, str(r["du_prix_sans_rang"]))

    par_nom = {x["nom"]: x for x in r["lignes"]}
    # ⭐⭐ L'objet qui porte le plus long corpus consécutif du dépôt.
    v("PHercParis4 publie 120 spires d'affilée, sans un trou",
      par_nom["PHercParis4"]["suite"] == 120 and par_nom["PHercParis4"]["trous"] == 0,
      f"suite={par_nom['PHercParis4']['suite']} trous={par_nom['PHercParis4']['trous']}")
    v("... de w010 à w129",
      (par_nom["PHercParis4"]["suite_de"], par_nom["PHercParis4"]["suite_a"]) == (10, 129))
    v("PHerc0172 en publie 44 d'affilée", par_nom["PHerc0172"]["suite"] == 44,
      str(par_nom["PHerc0172"]))
    v("le témoin PHerc0139 en publie 37", par_nom["PHerc0139"]["suite"] == 37,
      str(par_nom["PHerc0139"]))
    # ⚠⚠⚠ L'OBJET COURANT PLAFONNE SOUS LA MOITIÉ DE CE QUE LE PRIX DEMANDE.
    v("l'objet courant PHerc0500P2 plafonne à 13 spires",
      par_nom["PHerc0500P2"]["suite"] == 13, str(par_nom["PHerc0500P2"]))
    v("... donc il ne peut PAS porter la preuve des 31",
      not par_nom["PHerc0500P2"]["porte_le_prix"])
    # ⚠⚠⚠ CE MAJORANT NE DOIT PAS ÊTRE LU COMME LA PORTÉE QUE LE CORPUS AUTORISE. J'ai d'abord
    # cru y recouper le 6 que `la_portee_du_raccrochage` publie : coïncidence. Ce 6 vient d'un
    # TROU GÉOMÉTRIQUE — les spires 10 et 11, voisines par leur numéro, sont à 1000,6 µm — et
    # non d'un compte de spires. Deux routes qui rendent le même nombre pour deux raisons sans
    # rapport se lisent comme une confirmation : c'est le faux verdict le plus dur à voir.
    v("treize spires majorent la portée mesurable à 12, par les NOMS seulement",
      par_nom["PHerc0500P2"]["portee_maximale_par_les_noms"] == 12,
      str(par_nom["PHerc0500P2"]["portee_maximale_par_les_noms"]))
    # ⚠ Une portée est un nombre de FRANCHISSEMENTS, donc strictement inférieure au nombre de
    # spires : les confondre publierait une portée de plus que ce que le corpus peut montrer.
    v("le majorant est toujours d'une unité sous la suite",
      all(x["portee_maximale_par_les_noms"] == max(0, x["suite"] - 1) for x in r["lignes"]))
    # ⭐ Trois objets seulement dépassent les 31 spires du prix.
    v("trois objets portent les 31 spires du prix",
      set(r["portent_le_prix"]) == {"PHercParis4", "PHerc0172", "PHerc0139"},
      str(r["portent_le_prix"]))
    # ⚠⚠⚠ LA CORRECTION DE MA PROPRE LECTURE, GARDÉE ICI. En filtrant sur `tifxyz` seul,
    # `PHerc0172` rendait UNE spire marchable au lieu de quarante-quatre — une limite de filtre
    # publiée comme une limite de corpus. Ce contrôle est ce qui l'empêche de revenir.
    v("PHerc0172 publie ses 44 spires avec une géométrie 3D, pas une seule",
      par_nom["PHerc0172"]["suite_geometrie"] == 44,
      f"suite_geometrie={par_nom['PHerc0172']['suite_geometrie']}")
    v("... et PHercParis4 ses 120", par_nom["PHercParis4"]["suite_geometrie"] == 120,
      str(par_nom["PHercParis4"]["suite_geometrie"]))
    # ⚠ `tifxyz-transformed` compte parce que `deux_aplatissements` a établi qu'il porte une
    # position 3D par cellule ; les deux autres variantes ne sont pas comptées faute de l'avoir
    # établi, et cette abstention est une décision, pas un oubli.
    v("la géométrie retenue est exactement celle que le dépôt a établie",
      GEOMETRIE == ("tifxyz", "tifxyz-transformed"), str(GEOMETRIE))
    # ⭐ Un corpus publié sans géométrie n'est pas marchable, et il faut que ça se voie.
    v("aucune spire du prix n'est marchable non plus",
      all(par_nom[n]["rangs_geometrie"] == 0 for n in treize),
      str({n: par_nom[n]["rangs_geometrie"] for n in treize if par_nom[n]["rangs_geometrie"]}))

    # ⚠ L'objet de l'état de l'art publie 19 de ses 31 spires, sur une étendue de 31 exactement.
    v("PHerc1667, l'objet des 775 heures, publie 19 rangs sur une étendue de 31",
      par_nom["PHerc1667"]["rangs"] == 19 and par_nom["PHerc1667"]["etendue"] == 31,
      str(par_nom["PHerc1667"]))

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    a = p.parse_args()
    if a.verifier:
        return verifier()

    r = mesurer()
    print(f"{r['echantillons']} échantillons de {r['index']} · le prix demande "
          f"{r['spires_du_prix']} spires\n")
    print(f"{'objet':16} {'seg':>4} {'rangs':>6} {'suite':>6} {'de..à':>10} "
          f"{"geom":>7}  prix")
    for x in r["lignes"]:
        if x["segments"] == 0 and not x["du_prix"]:
            continue
        marque = "★" if x["du_prix"] else " "
        plage = f"{x['suite_de']}..{x['suite_a']}" if x["suite"] else "—"
        porte = "✅" if x["porte_le_prix"] else ("⛔" if x["suite"] else "—")
        print(f"{marque}{x['nom']:15} {x['segments']:>4} {x['rangs']:>6} {x['suite']:>6} "
              f"{plage:>10} {x['suite_geometrie']:>7}  {porte}")
    print("\n★ = l'un des treize rouleaux du Grand Prize")
    print(f"\n⛔ {len(r['du_prix_sans_segment'])}/13 rouleaux du prix ne publient AUCUN segment")
    print(f"⛔ {len(r['du_prix_sans_rang'])}/13 ne publient aucun rang de spire — donc aucun "
          f"d'eux ne peut borner une portée")
    print(f"✅ {len(r['portent_le_prix'])} objets portent les {r['spires_du_prix']} spires : "
          f"{', '.join(r['portent_le_prix'])}")
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False) + "\n")
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
