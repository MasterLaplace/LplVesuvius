"""Où le chunk se trouve-t-il, et est-ce que ça dit où une surface pourra se poser ?

⭐⭐⭐⭐ POURQUOI CE FICHIER, ET C'EST `R4-P41` QUI LE NOMME. `191` a cherché parmi **19** observables
et n'a rien établi ; `192` a confirmé que la piste qu'elle avait nommée ne se retrouve pas sur
soixante chunks neufs. Mais les dix-neuf observables de `191` sont TOUS INTRINSÈQUES : ils décrivent
la texture d'un cube de matière sans jamais dire **où** ce cube se trouve. Un chunk au bord d'un
segment, là où la segmentation est la moins sûre, n'est pas un chunk du milieu.

⭐⭐⭐⭐ ET C'EST UNE NOUVELLE RECHERCHE, DONC ELLE PAIE SA PROPRE FAMILLE ENTIÈRE. Ce n'est pas un
élargissement de la liste de `191` — qui rendrait son plancher faux rétroactivement — mais une liste
neuve, déclarée et fermée avant de regarder, d'un genre différent, et payée en entier par des
mélanges de l'étiquette qui reprennent le maximum sur TOUTE la liste.

⭐⭐ ET ELLE SE JOUE SUR QUATRE-VINGT-UN CHUNKS, contre vingt et un pour `191`. Les observables
extrinsèques ne coûtent AUCUN téléchargement de matière : ils se lisent dans l'adresse du chunk et
dans la forme de la grille de son segment. Les soixante chunks que `192` a étiquetés rejoignent donc
les vingt et un de `190`, et le plancher de détection descend d'autant.

⚠⚠⚠ ET UNE LIMITE EST NOMMÉE PLUTÔT QUE TUE : une permutation libre suppose les chunks
ÉCHANGEABLES, or deux chunks d'un même segment partagent la matière. Un second nul, qui mélange
l'étiquette À L'INTÉRIEUR de chaque segment, est donc mesuré à côté — et il rend zéro pour toute
colonne constante dans un segment, ce qui est exactement ce qu'il doit dire.

Usage :
    uv run python src/nappe/ou_le_chunk_se_trouve_t_il.py --verifier
    uv run python src/nappe/ou_le_chunk_se_trouve_t_il.py \\
        --json docs/mesures/ou_le_chunk_se_trouve_t_il.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))

from la_ou_le_rouleau_se_laisse_suivre import (LETIQUETTE, _colonne,  # noqa: E402
                                               juger_une_liste, la_separation,
                                               laire_sous_la_courbe,
                                               le_maximum_de_la_famille)
from la_piste_tient_elle_sur_des_chunks_neufs import REPLICATS_DE_LETALON  # noqa: E402
from la_recette_posee_sur_le_rouleau import (COTE_DU_TREILLIS, DELAI,  # noqa: E402
                                             PERMUTATIONS, les_chunks, les_volumes)
from zarr_depth import BUCKET, array_meta  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
CE_QUE_LA_MARCHE_A_RENDU = MESURES / "une_surface_qui_choisit_sa_couche.json"
CE_QUE_LA_CONFIRMATION_A_RENDU = MESURES / "la_piste_tient_elle_sur_des_chunks_neufs.json"
CE_QUE_LA_RECHERCHE_A_RENDU = MESURES / "la_ou_le_rouleau_se_laisse_suivre.json"
GRAINE = 20261003
# ⚠⚠ LE BRUIT DE LA COLONNE PORTEUSE EST CELUI DE `191` ET DE `192`, RELU ET NON CHOISI : une
# colonne qui SERAIT l'etiquette rendrait une separation parfaite qu'aucun observable reel n'atteint,
# donc l'etalon serait plus facile qu'il ne doit l'etre. Son aire VRAIE vaut 0,8807.
BRUIT_DE_LA_PORTEUSE = 0.6

# ⚠⚠⚠ LA LISTE EST DECLAREE ICI, FERMEE, ET SON NOMBRE EST PUBLIE. Chaque entree se calcule depuis
# l'ADRESSE du chunk et la FORME de la grille de son segment — jamais depuis sa matiere. Aucune ne
# demande de telechargement, ce qui est precisement pourquoi elles couvrent les quatre-vingt-un
# chunks etiquetes et non les vingt et un de `191`.
LES_OBSERVABLES_EXTRINSEQUES = (
    ("ligne", "la ligne du chunk dans la grille"),
    ("colonne", "la colonne du chunk dans la grille"),
    ("part_de_la_hauteur", "sa position relative en hauteur"),
    ("part_de_la_largeur", "sa position relative en largeur"),
    ("distance_au_bord", "sa distance au bord de la grille, en chunks"),
    ("distance_au_bord_relative", "sa distance au bord, rapportée à la grille"),
    ("hauteur_de_la_grille", "la hauteur de la grille du segment"),
    ("largeur_de_la_grille", "la largeur de la grille du segment"),
    ("chunks_de_la_grille", "les chunks de la grille entière"),
    ("rang_du_segment", "le rang du segment dans le dépôt"),
    ("chunks_lus_du_segment", "les chunks lus du segment"),
    ("part_lue_du_segment", "la part du treillis rendue"),
)


def les_etiquettes(marche: Path = CE_QUE_LA_MARCHE_A_RENDU,
                   confirmation: Path = CE_QUE_LA_CONFIRMATION_A_RENDU) -> dict:
    """Les chunks étiquetés par `190` ET par `192`, réunis — quatre-vingt-un au lieu de vingt et un.

    ⭐⭐⭐⭐ LES DEUX JEUX SE RÉUNISSENT PARCE QU'ILS PORTENT LA MÊME ÉTIQUETTE, produite par le MÊME
    `un_segment` de `190` avec les mêmes départs, le même pas forcé et les mêmes dix-neuf tirages.
    `192` n'a pas rejoué la marche autrement : il l'a rejouée ailleurs.

    ⚠⚠ LES DEUX JEUX NE SE RECOUVRENT PAS, et c'est vérifié plutôt que supposé : `192` saute
    exactement les segments de `190`. Un chunk compté deux fois pèserait double dans une permutation
    qui le suppose unique.

    ⚠ Un chunk dont l'étiquette manque est écarté, jamais défauté à « ne retient pas » : une valeur
    inventée serait une étiquette que personne n'a mesurée.
    """
    out = {}
    if marche.is_file():
        d = json.loads(marche.read_text(encoding="utf-8"))
        for s in (d.get("les_segments") or []):
            for c in (s.get("chunks") or []):
                if c.get(LETIQUETTE) is None or not c.get("chunk"):
                    continue
                out[(str(s.get("segment")), int(c["chunk"][0]), int(c["chunk"][1]))] = {
                    "etiquette": bool(c[LETIQUETTE]), "venu_de": "190"}
    doubles = 0
    if confirmation.is_file():
        d = json.loads(confirmation.read_text(encoding="utf-8"))
        for x in (d.get("les_chunks") or []):
            k = (str(x.get("segment")), int(x["chunk"][0]), int(x["chunk"][1]))
            if k in out:
                doubles += 1
                continue
            out[k] = {"etiquette": bool(x["etiquette"]), "venu_de": "192"}
    return {"chunks": out, "doubles": int(doubles),
            "venus_de_190": int(sum(1 for v in out.values() if v["venu_de"] == "190")),
            "venus_de_192": int(sum(1 for v in out.values() if v["venu_de"] == "192")),
            "qui_retiennent": int(sum(1 for v in out.values() if v["etiquette"]))}


def les_grilles(segments, cote: int = COTE_DU_TREILLIS, delai: float = DELAI) -> dict:
    """La forme de la grille de chaque segment — une requête de métadonnées, aucune matière.

    ⭐ C'EST TOUTE LA RAISON POUR LAQUELLE CETTE LISTE COUVRE QUATRE-VINGT-UN CHUNKS. Un observable
    extrinsèque ne demande pas de lire le cube : il se lit dans la forme du volume, qui tient dans
    une seule requête par segment.

    ⚠ Le rang est celui de l'ordre du dépôt, jamais un tri : un segment choisi pour sa taille ou sa
    texture ferait mesurer le choix.
    """
    voulus = {str(s) for s in segments}
    out = {}
    for rang, v in enumerate(les_volumes(combien=10 ** 6)):
        if str(v["segment"]) not in voulus:
            continue
        try:
            meta = array_meta(f"{BUCKET}/{v['cle']}", 0, delai)
        except Exception as e:  # noqa: BLE001
            out[str(v["segment"])] = {"decidable": False,
                                      "raison": f"{type(e).__name__}"}
            continue
        _, hy, hx = meta["chunks"]
        _, rows, cols = meta["shape"]
        gy, gx = -(-rows // hy), -(-cols // hx)
        out[str(v["segment"])] = {"decidable": True, "rang": int(rang),
                                  "hauteur": int(gy), "largeur": int(gx),
                                  "positions_du_treillis": len(les_chunks(gy, gx, cote))}
    return out


def la_table(etiquettes: dict, grilles: dict) -> dict:
    """Une ligne par chunk étiqueté, une colonne par observable extrinsèque déclaré.

    ⚠⚠ UN CHUNK DONT LE SEGMENT N'A PAS RENDU SA GRILLE EST ÉCARTÉ, jamais complété : une position
    relative calculée sur une grille inventée serait une position que rien ne mesure.
    """
    lus = {}
    for seg in {k[0] for k in etiquettes}:
        g = grilles.get(seg) or {}
        if g.get("decidable"):
            lus[seg] = g
    cles = sorted(k for k in etiquettes if k[0] in lus)
    if not cles:
        return {"decidable": False, "raison": "aucun chunk dont la grille soit lisible"}
    par_segment = {}
    for k in cles:
        par_segment[k[0]] = par_segment.get(k[0], 0) + 1
    valeurs = {nom: [] for nom, _n in LES_OBSERVABLES_EXTRINSEQUES}
    for seg, cy, cx in cles:
        g = lus[seg]
        gy, gx = float(g["hauteur"]), float(g["largeur"])
        bord = float(min(cy, cx, g["hauteur"] - 1 - cy, g["largeur"] - 1 - cx))
        v = {
            "ligne": float(cy), "colonne": float(cx),
            "part_de_la_hauteur": (float(cy) / (gy - 1.0)) if gy > 1 else 0.0,
            "part_de_la_largeur": (float(cx) / (gx - 1.0)) if gx > 1 else 0.0,
            "distance_au_bord": bord,
            "distance_au_bord_relative": bord / max(1.0, min(gy, gx) / 2.0),
            "hauteur_de_la_grille": gy, "largeur_de_la_grille": gx,
            "chunks_de_la_grille": gy * gx,
            "rang_du_segment": float(g["rang"]),
            "chunks_lus_du_segment": float(par_segment[seg]),
            "part_lue_du_segment": (float(par_segment[seg])
                                    / max(1.0, float(g["positions_du_treillis"]))),
        }
        for nom, _n in LES_OBSERVABLES_EXTRINSEQUES:
            valeurs[nom].append(v[nom])
    # ⚠ LA PROVENANCE EST ECRITE, JAMAIS EMPRUNTEE : ces colonnes ne viennent d'aucune mesure de
    # matiere, elles se calculent depuis l'adresse du chunk et la forme de sa grille, et le dire
    # evite qu'on les prenne un jour pour des lectures du rouleau.
    colonnes = [{"mesure": "l'adresse du chunk et la grille de son segment", "cle": cle,
                 "nom": nom, "valeurs": [float(x) for x in valeurs[cle]],
                 "chunks_couverts": len(valeurs[cle])}
                for cle, nom in LES_OBSERVABLES_EXTRINSEQUES]
    return {"decidable": True, "chunks": [list(k) for k in cles],
            "segments_de_chaque_chunk": [k[0] for k in cles],
            "etiquettes": [bool(etiquettes[k]["etiquette"]) for k in cles],
            "chunks_etiquetes": len(cles),
            "chunks_qui_retiennent": int(sum(1 for k in cles
                                             if etiquettes[k]["etiquette"])),
            "observables_declares": len(LES_OBSERVABLES_EXTRINSEQUES),
            "colonnes": colonnes}


def contre_le_melange_dans_chaque_segment(colonnes, etiquettes, segments,
                                          tirages: int = PERMUTATIONS,
                                          graine: int = GRAINE) -> dict:
    """Le second nul : l'étiquette mélangée À L'INTÉRIEUR de chaque segment, jamais entre eux.

    ⭐⭐⭐⭐ IL EXISTE PARCE QU'UNE PERMUTATION LIBRE SUPPOSE LES CHUNKS ÉCHANGEABLES, ET ILS NE LE
    SONT PAS TOUT À FAIT : deux chunks d'un même segment partagent la matière, donc leurs étiquettes
    peuvent se ressembler pour une raison qui n'a rien à voir avec l'observable. Un mélange
    stratifié garde chaque segment avec exactement ses étiquettes et ne redistribue qu'à l'intérieur.

    ⚠⚠ ET IL REND ZÉRO POUR TOUTE COLONNE CONSTANTE DANS UN SEGMENT — la hauteur de la grille, le
    rang, la part lue. C'est ce qu'il DOIT dire : une colonne qui ne varie pas à l'intérieur d'un
    segment ne peut pas être distinguée du regroupement des étiquettes par segment, et prétendre le
    contraire serait lire la structure du dépôt pour une propriété de la matière.
    """
    r = np.random.default_rng(int(graine))
    e = np.asarray(etiquettes, dtype=bool)
    par_segment = {}
    for i, s in enumerate(segments):
        par_segment.setdefault(str(s), []).append(i)
    maxima = []
    for _ in range(int(tirages)):
        melange = e.copy()
        for idx in par_segment.values():
            melange[idx] = r.permutation(e[list(idx)])
        m = le_maximum_de_la_famille(colonnes, list(melange))
        if m.get("decidable"):
            maxima.append(float(m["la_separation_maximale"]))
    if not maxima:
        return {"decidable": False, "raison": "aucun mélange lisible"}
    return {"decidable": True, "tirages": int(tirages),
            "le_plus_grand_maximum": round(max(maxima), 4),
            "les_maxima": [round(x, 4) for x in maxima]}


def les_colonnes_constantes_par_segment(colonnes, segments) -> list[str]:
    """Les colonnes qui ne varient pas à l'intérieur d'un segment — nommées, jamais retirées.

    ⚠⚠ ELLES SONT LÉGITIMES DANS LA LISTE : « ce segment est grand » est un fait sur le chunk autant
    que « ce chunk est au bord ». Mais le mélange stratifié ne peut rien en dire, et le taire
    laisserait croire qu'il les a jugées.
    """
    par_segment = {}
    for i, s in enumerate(segments):
        par_segment.setdefault(str(s), []).append(i)
    out = []
    for c in colonnes:
        v = c["valeurs"]
        if all(len({v[i] for i in idx if v[i] is not None}) <= 1
               for idx in par_segment.values()):
            out.append(c["nom"])
    return out


def la_sensibilite(n: int, k: int, combien: int, bruit: float = BRUIT_DE_LA_PORTEUSE,
                   replicats: int = REPLICATS_DE_LETALON, tirages: int = PERMUTATIONS,
                   graine: int = GRAINE) -> float:
    """À quelle fréquence l'instrument retrouve une colonne qui PORTE l'étiquette, à ce compte-là.

    ⭐⭐⭐⭐ ET C'EST CE QUE `191` N'AVAIT PAS MESURÉ. Son étalon était un TIRAGE UNIQUE, et un tirage
    unique d'une aire estimée sur six chunks contre quinze varie de près d'un dixième : il pouvait
    tomber du bon côté par chance. Mesurée sur des réplicats, la sensibilité dit combien de fois sur
    combien l'instrument voit ce qu'il doit voir, et c'est elle qui rend un silence lisible.

    ⚠⚠ Elle ne regarde QUE le compte et le nombre d'observables — jamais la matière, jamais
    l'étiquette réelle. C'est une propriété de l'instrument, pas du rouleau.
    """
    if int(k) <= 0 or int(k) >= int(n):
        return 0.0
    vus = 0
    for t in range(int(replicats)):
        r = np.random.default_rng(int(graine) + 811 * (t + 1))
        e = [True] * int(k) + [False] * (int(n) - int(k))
        colonnes = [_colonne(f"du bruit pur {i}", list(r.normal(0.0, 1.0, int(n))))
                    for i in range(int(combien) - 1)]
        porteuse = _colonne("l'ingrédient de l'étiquette, bruité",
                            [(1.0 if x else 0.0) + float(val)
                             for x, val in zip(e, r.normal(0.0, float(bruit), int(n)))])
        j_ = juger_une_liste([porteuse] + colonnes, e, tirages,
                             int(graine) + 811 * (t + 1))
        vus += int(bool(j_.get("un_observable_separe")))
    return round(vus / float(replicats), 4)


def sur_letalon(etiquettes, combien: int, bruit: float = BRUIT_DE_LA_PORTEUSE,
                replicats: int = REPLICATS_DE_LETALON, tirages: int = PERMUTATIONS,
                graine: int = GRAINE) -> dict:
    """Deux listes dont la réponse est CONNUE, mesurées sur des RÉPLICATS et non sur un tirage.

    ⭐⭐⭐⭐ LA FACE POSITIVE PORTE L'INGRÉDIENT DE L'ÉTIQUETTE, noyé dans autant de colonnes de bruit
    que la liste déclarée en compte, et l'instrument DOIT le retrouver à TOUS les réplicats.
    ⭐⭐⭐⭐ LA FACE NÉGATIVE n'est que du bruit, en même nombre, et il ne DOIT le retrouver à AUCUN.

    ⚠⚠⚠ ET C'EST LA RÉPARATION QUE `193` APPORTE À `191` : là-bas l'étalon était un tirage unique.
    Mesurée ici sur des réplicats, la sensibilité à la configuration de `191` — vingt et un chunks,
    six qui retiennent, dix-neuf observables — ne vaut pas un, ce qui veut dire que son étalon
    pouvait passer par chance.

    ⚠⚠ Les deux listes ont la MÊME longueur que la liste déclarée ici, et non celle de `191` : le
    prix de la liberté dépend du nombre, donc un étalon emprunté à une autre liste serait d'un autre
    prix.
    """
    n = len(etiquettes)
    k = int(sum(1 for x in etiquettes if x))
    vue = la_sensibilite(n, k, combien, bruit, replicats, tirages, graine)
    r = np.random.default_rng(int(graine) + 7)
    bruits = [_colonne(f"du bruit pur {i}", list(r.normal(0.0, 1.0, n)))
              for i in range(int(combien))]
    faux = juger_une_liste(bruits, etiquettes, tirages, graine)
    return {"combien_dobservables": int(combien), "bruit_de_la_porteuse": float(bruit),
            "replicats": int(replicats),
            "la_part_vue_avec_lingredient": vue,
            "rien_que_du_bruit": faux,
            # ⭐⭐⭐⭐ LES DEUX FACES ENSEMBLE : l'instrument doit voir ce qui est la, a TOUS les
            # replicats, et ne rien voir dans ce qui n'y est pas.
            "letalon_separe_les_deux": bool(float(vue) >= 1.0
                                            and not faux.get("un_observable_separe"))}


def ce_que_la_recherche_intrinseque_a_rendu(chemin: Path = CE_QUE_LA_RECHERCHE_A_RENDU) -> dict:
    """Ce que `191` a rendu sur sa liste INTRINSÈQUE — relu pour que les deux prix se comparent."""
    if not chemin.is_file():
        return {}
    d = json.loads(chemin.read_text(encoding="utf-8"))
    v = d.get("le_verdict") or {}
    return {"observables": v.get("observables_declares"),
            "chunks": v.get("chunks_etiquetes"),
            "separation_maximale": v.get("la_separation_maximale"),
            "plancher": v.get("le_plancher_de_detection")}


def mesurer(tirages: int = PERMUTATIONS, cote: int = COTE_DU_TREILLIS,
            graine: int = GRAINE) -> dict:
    marques = les_etiquettes()
    if not marques["chunks"]:
        return {"message": "aucun chunk étiqueté ; relancer `190` et `192` d'abord"}
    grilles = les_grilles({k[0] for k in marques["chunks"]}, cote)
    table = la_table(marques["chunks"], grilles)
    if not table.get("decidable"):
        return {"message": f"la table ne se construit pas : {table.get('raison')}"}
    e, segs = table["etiquettes"], table["segments_de_chaque_chunk"]
    verdict = juger_une_liste(table["colonnes"], e, tirages, graine)
    stratifie = contre_le_melange_dans_chaque_segment(table["colonnes"], e, segs, tirages, graine)
    constantes = les_colonnes_constantes_par_segment(table["colonnes"], segs)
    etalon = sur_letalon(e, table["observables_declares"], BRUIT_DE_LA_PORTEUSE,
                         REPLICATS_DE_LETALON, tirages, graine)
    intrinseque = ce_que_la_recherche_intrinseque_a_rendu()
    # ⭐⭐⭐⭐ LA SENSIBILITE A LA CONFIGURATION DE `191`, MESUREE ICI : c'est ce que sa tranche
    # n'avait pas, et ce qui dit si son etalon a pu passer par chance.
    sens_191 = (la_sensibilite(int(intrinseque["chunks"]),
                               int(round(float(intrinseque["chunks"]) * 6.0 / 21.0)),
                               int(intrinseque["observables"]), BRUIT_DE_LA_PORTEUSE,
                               REPLICATS_DE_LETALON, tirages, graine)
                if intrinseque.get("chunks") and intrinseque.get("observables") else None)
    return {"graine": int(graine), "tirages": int(tirages),
            "letiquette": LETIQUETTE,
            "letiquetage": {k: v for k, v in marques.items() if k != "chunks"},
            "les_grilles": grilles,
            "les_colonnes": [{k: v for k, v in c.items() if k != "valeurs"}
                             for c in table["colonnes"]],
            "les_colonnes_constantes_par_segment": constantes,
            "la_recherche_intrinseque_de_191": intrinseque,
            "la_sensibilite_a_la_configuration_de_191": sens_191,
            "letalon": etalon,
            "le_nul_stratifie": stratifie,
            "le_verdict": {
                **verdict,
                "chunks_etiquetes": table["chunks_etiquetes"],
                "chunks_qui_retiennent": table["chunks_qui_retiennent"],
                "observables_declares": table["observables_declares"],
                "venus_de_190": marques["venus_de_190"],
                "venus_de_192": marques["venus_de_192"],
                "chunks_comptes_deux_fois": marques["doubles"],
                "le_plancher_stratifie": stratifie.get("le_plus_grand_maximum"),
                # ⚠⚠⚠ LE SECOND NUL EST UNE EXIGENCE DE PLUS, JAMAIS UN REMPLACEMENT : un observable
                # qui ne battrait que le mélange libre pourrait n'avoir lu que le regroupement des
                # étiquettes par segment.
                "un_observable_separe_aussi_dans_chaque_segment": bool(
                    verdict.get("la_separation_maximale") is not None
                    and stratifie.get("le_plus_grand_maximum") is not None
                    and float(verdict["la_separation_maximale"])
                    > float(stratifie["le_plus_grand_maximum"])),
                "les_colonnes_constantes_par_segment": constantes,
                "observables_intrinseques_de_191": intrinseque.get("observables"),
                "chunks_de_191": intrinseque.get("chunks"),
                "plancher_de_191": intrinseque.get("plancher"),
                "separation_maximale_de_191": intrinseque.get("separation_maximale"),
                "la_part_vue_avec_lingredient": etalon.get("la_part_vue_avec_lingredient"),
                "la_part_vue_a_la_configuration_de_191": sens_191,
                "letalon_separe_les_deux": bool(etalon.get("letalon_separe_les_deux"))}}


def afficher(r: dict) -> None:
    if "message" in r:
        print(r["message"])
        return
    v, e = r["le_verdict"], r["letalon"]
    print("OÙ LE CHUNK SE TROUVE-T-IL, ET EST-CE QUE ÇA DIT QUELQUE CHOSE ?")
    print(f"  {v['chunks_qui_retiennent']} chunks qui retiennent sur {v['chunks_etiquetes']} "
          f"({v['venus_de_190']} de `190`, {v['venus_de_192']} de `192`, "
          f"{v['chunks_comptes_deux_fois']} comptés deux fois) · "
          f"{v['observables_declares']} observables EXTRINSÈQUES déclarés · {r['tirages']} mélanges")
    print()
    print("  L'ÉTALON — mêmes chunks, même étiquette, deux listes connues")
    print(f"     {'la liste porte l ingrédient':<34} vue à "
          f"{e.get('la_part_vue_avec_lingredient')} des {e.get('replicats')} réplicats")
    x = e.get("rien_que_du_bruit") or {}
    print(f"     {'la liste n est que du bruit':<34} sépare {x.get('un_observable_separe')} · "
          f"maximum {x.get('la_separation_maximale')} contre un plancher de "
          f"{x.get('le_plancher_de_detection')}")
    print(f"     {'la même mesure à la configuration de `191`':<34} vue à "
          f"{v.get('la_part_vue_a_la_configuration_de_191')}")
    print()
    print("  LES OBSERVABLES EXTRINSÈQUES, DU PLUS SÉPARANT AU MOINS")
    for x in sorted(v.get("tous") or [], key=lambda y: -y["separation"]):
        fige = " (constante dans un segment)" if x["nom"] in v.get(
            "les_colonnes_constantes_par_segment", []) else ""
        print(f"     {x['separation']:>7} · aire {x['aire']:>7} · {x['nom']}{fige}")
    print()
    print("  ★ LE VERDICT")
    for cle in ("chunks_etiquetes", "chunks_qui_retiennent", "observables_declares",
                "observables_lus", "la_separation_maximale", "le_plancher_de_detection",
                "le_plancher_stratifie", "un_observable_separe",
                "un_observable_separe_aussi_dans_chaque_segment",
                "observables_intrinseques_de_191", "chunks_de_191", "plancher_de_191",
                "separation_maximale_de_191", "la_part_vue_avec_lingredient",
                "la_part_vue_a_la_configuration_de_191", "letalon_separe_les_deux"):
        print(f"     {cle:<48} {v.get(cle)}")
    print(f"     {'le_meilleur':<48} {v.get('le_meilleur')}")


def verifier() -> int:
    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        if not ok:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    # ⚠⚠⚠ LA LISTE EST FERMEE, DECLAREE, ET D'UN GENRE DIFFERENT DE CELLE DE `191`.
    v("★ la liste des observables est fermée",
      isinstance(LES_OBSERVABLES_EXTRINSEQUES, tuple))
    v("aucun observable n'est déclaré deux fois",
      len({c for c, _n in LES_OBSERVABLES_EXTRINSEQUES}) == len(LES_OBSERVABLES_EXTRINSEQUES))
    from la_ou_le_rouleau_se_laisse_suivre import LES_OBSERVABLES  # noqa: PLC0415
    v("★★★★ aucun observable n'est repris de la liste INTRINSÈQUE de `191`",
      not ({c for c, _n in LES_OBSERVABLES_EXTRINSEQUES}
           & {c for _m, c, _n in LES_OBSERVABLES}),
      str({c for c, _n in LES_OBSERVABLES_EXTRINSEQUES}
          & {c for _m, c, _n in LES_OBSERVABLES}))

    # ⭐⭐ LES DEUX JEUX D'ETIQUETTES SE REUNISSENT SANS SE RECOUVRIR.
    m = les_etiquettes()
    v("les étiquettes de `190` et de `192` se relisent", bool(m["chunks"]), str(len(m["chunks"])))
    v("★★★ et elles ne se recouvrent PAS", m["doubles"] == 0, str(m["doubles"]))
    v("★★ le compte réuni dépasse celui de `191`",
      len(m["chunks"]) > 21, f"{len(m['chunks'])} contre 21")
    v("les deux camps sont non vides", 0 < m["qui_retiennent"] < len(m["chunks"]),
      f"{m['qui_retiennent']} sur {len(m['chunks'])}")
    v("une source absente ne casse rien",
      les_etiquettes(Path("/n/existe/pas.json"), Path("/n/plus.json"))["chunks"] == {})

    # ⚠⚠ LA TABLE REFUSE UN CHUNK DONT LA GRILLE N'EST PAS LISIBLE, jamais ne la complete.
    faux_e = {("A", 0, 0): {"etiquette": True}, ("A", 3, 4): {"etiquette": False},
              ("B", 1, 1): {"etiquette": True}, ("B", 2, 2): {"etiquette": False}}
    g_ok = {"A": {"decidable": True, "rang": 0, "hauteur": 5, "largeur": 6,
                  "positions_du_treillis": 25},
            "B": {"decidable": False, "raison": "pas de réponse"}}
    t = la_table(faux_e, g_ok)
    v("★★★ un chunk dont la grille est illisible est ÉCARTÉ",
      t.get("decidable") and t["chunks_etiquetes"] == 2,
      str(t.get("chunks_etiquetes")))
    v("et si aucune grille ne répond, la table est refusée",
      la_table(faux_e, {"A": {"decidable": False}, "B": {"decidable": False}}).get("decidable")
      is False)
    v("★ elle porte une colonne par observable déclaré",
      len(t["colonnes"]) == len(LES_OBSERVABLES_EXTRINSEQUES), str(len(t["colonnes"])))
    par_nom = {c["cle"]: c["valeurs"] for c in t["colonnes"]}
    v("★ chaque colonne dit d'où elle vient, et ce n'est aucune mesure de matière",
      all("adresse" in c["mesure"] for c in t["colonnes"]),
      str({c["mesure"] for c in t["colonnes"]}))
    v("la ligne et la colonne sont celles de l'adresse",
      par_nom["ligne"] == [0.0, 3.0] and par_nom["colonne"] == [0.0, 4.0], str(par_nom["ligne"]))
    v("★★ la distance au bord est nulle dans un coin",
      par_nom["distance_au_bord"][0] == 0.0, str(par_nom["distance_au_bord"]))
    v("★★ et la part de la hauteur va de zéro à un",
      par_nom["part_de_la_hauteur"] == [0.0, 0.75], str(par_nom["part_de_la_hauteur"]))

    # ⭐⭐⭐⭐ LA FAMILLE PAIE LE CHOIX, ET LES DEUX FACES DE L'ETALON LE VERIFIENT — meme regle que
    # `191`, relue et non recopiee.
    e = [True] * 15 + [False] * 66
    et = sur_letalon(e, len(LES_OBSERVABLES_EXTRINSEQUES), BRUIT_DE_LA_PORTEUSE, 8, 19, 4242)
    v("★★★★ l'étalon sépare ses deux faces", bool(et.get("letalon_separe_les_deux")),
      f"porteuse vue à {et.get('la_part_vue_avec_lingredient')} · bruit seul "
      f"{(et.get('rien_que_du_bruit') or {}).get('un_observable_separe')}")
    v("★★ et le plancher de douze observables est plus bas que celui de dix-neuf sur vingt et un",
      float((et.get("rien_que_du_bruit") or {})["le_plancher_de_detection"]) < 0.4286,
      str((et.get("rien_que_du_bruit") or {}).get("le_plancher_de_detection")))

    # ⭐⭐⭐⭐ LA SENSIBILITE EST UNE PROPRIETE DE L'INSTRUMENT, ET ELLE REPARE `191` : a sa
    # configuration — vingt et un chunks, six qui retiennent, dix-neuf observables — l'instrument
    # ne voit PAS a tous les coups une colonne qui porte l'etiquette, donc son etalon a un tirage
    # unique pouvait passer par chance.
    ici = la_sensibilite(81, 15, 12, BRUIT_DE_LA_PORTEUSE, 12, 19, 4242)
    la_bas = la_sensibilite(21, 6, 19, BRUIT_DE_LA_PORTEUSE, 12, 19, 4242)
    v("★★★★ l'instrument voit à TOUS les réplicats au compte d'ici", float(ici) >= 1.0, str(ici))
    v("★★★★ et PAS à la configuration de `191`", float(la_bas) < 1.0, str(la_bas))
    v("★★★ donc la sensibilité monte avec le compte", float(ici) > float(la_bas),
      f"{la_bas} là-bas contre {ici} ici")
    v("un camp vide rend une sensibilité nulle",
      la_sensibilite(10, 0, 4, BRUIT_DE_LA_PORTEUSE, 3, 9) == 0.0)

    # ⭐⭐⭐⭐ LE NUL STRATIFIE REND ZERO POUR UNE COLONNE CONSTANTE DANS UN SEGMENT, et c'est ce
    # qu'il doit dire : une telle colonne ne se distingue pas du regroupement des etiquettes.
    segs = ["A"] * 8 + ["B"] * 8
    lab = [True, True, False, False, False, False, False, False] * 2
    fige = _colonne("constante par segment", [1.0] * 8 + [2.0] * 8)
    varie = _colonne("varie dans le segment", [1.0 if x else 0.0 for x in lab])
    st = contre_le_melange_dans_chaque_segment([fige], lab, segs, 9, 11)
    v("★★★★ le nul stratifié rend zéro pour une colonne constante dans un segment",
      float(st["le_plus_grand_maximum"]) == 0.0, str(st["le_plus_grand_maximum"]))
    v("★★★ et la colonne constante est NOMMÉE",
      les_colonnes_constantes_par_segment([fige, varie], segs) == ["constante par segment"],
      str(les_colonnes_constantes_par_segment([fige, varie], segs)))
    st2 = contre_le_melange_dans_chaque_segment([varie], lab, segs, 9, 11)
    v("★★ une colonne qui varie dans le segment, elle, a un nul non nul",
      float(st2["le_plus_grand_maximum"]) > 0.0, str(st2["le_plus_grand_maximum"]))
    # ⚠⚠ LE MELANGE STRATIFIE GARDE CHAQUE SEGMENT AVEC EXACTEMENT SES ETIQUETTES : sans cela il ne
    # serait qu'un mélange libre sous un autre nom.
    r_ = np.random.default_rng(5)
    e_ = np.asarray(lab, dtype=bool)
    idx = {s: [i for i, x in enumerate(segs) if x == s] for s in set(segs)}
    garde = True
    for _ in range(20):
        mel = e_.copy()
        for ii in idx.values():
            mel[ii] = r_.permutation(e_[list(ii)])
        garde = garde and all(int(mel[ii].sum()) == int(e_[ii].sum()) for ii in idx.values())
    v("★★★ chaque segment garde exactement son compte d'étiquettes", garde)

    v("ce que `191` a rendu est relu", bool(ce_que_la_recherche_intrinseque_a_rendu()))
    v("et absent quand la mesure l'est",
      ce_que_la_recherche_intrinseque_a_rendu(Path("/n/existe/pas.json")) == {})

    # ⚠⚠ LA SORTIE REND LE COMPTE D'ECHECS, PAS UN LITTERAL.
    nom = "ou_le_chunk_se_trouve_t_il.py"
    if echecs:
        print(f"{nom}   {len(echecs)} ÉCHECS sur {faits}")
        for e_ in echecs:
            print(f"   ✗ {e_}")
    else:
        print(f"{nom:<46} ALL PASS (0 failures, {faits} checks)")
    return len(echecs)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer()
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
