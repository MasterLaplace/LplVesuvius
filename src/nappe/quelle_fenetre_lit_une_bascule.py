"""Quelle fenêtre lit une bascule ? — et celle de la campagne ne pouvait pas.

⭐⭐⭐⭐ POURQUOI CE FICHIER. `14` §3 mesure sur le vrai rouleau, à 2,4 µm, que l'orientation ne
bascule PAS en traversant une feuille — elle reste entre 90 et 97° sur **109** couches — et il
laisse TROIS explications non départagées : le contraste entre les deux plis trop faible, la fenêtre
mal centrée sur la feuille, ou la fenêtre plus courte qu'une épaisseur de feuille. `172` a construit
la matière qui permet de les départager : `VolumeFabriqueAFibres`, dont la direction de chaque pli
est **choisie**, donc l'instrument peut échouer et on voit à quoi.

⚠⚠ L'ÉNONCÉ EST UNE COMPARAISON, PAS UN SEUIL. On lit DEUX écarts avec le MÊME estimateur : la
**bascule**, entre les deux moitiés de la fenêtre, et le **témoin**, entre les deux quarts de sa
première moitié. Sur une matière à deux plis, la bascule doit dépasser le témoin ; un réglage où
elle ne le dépasse pas ne lit pas la bascule, quelle que soit sa valeur.

⚠⚠⚠ ET UNE LONGUEUR DE FENÊTRE N'EST FIABLE QUE SI ELLE LIT LA BASCULE À TOUS LES DÉCALAGES. La
phase de la fenêtre dans la feuille n'est pas connue sur données réelles — c'est précisément
l'explication nº 2 — donc une longueur qui ne marche qu'à un décalage sur deux est une loterie, et
la forme jointe du dépôt est ici la seule honnête.

⚠ CONTRÔLE OBLIGATOIRE ET VIDE : à `plis_par_feuille=1` il n'y a AUCUNE bascule à lire. La bascule
ne doit donc jamais y dépasser le témoin, à aucune longueur ni aucun décalage. Un réglage qui y
« lirait » une bascule mesurerait sa propre fenêtre.

⚠⚠ CE QUE CE FICHIER NE PEUT PAS DIRE : si un vrai papyrus a cette structure à cette échelle. Il
répond sur le PROTOCOLE — telle fenêtre peut-elle lire une bascule qui existe — et pas sur la
matière. Un résultat négatif obtenu avec une fenêtre qui ne peut pas lire n'est pas un résultat sur
la matière.

Usage :
    uv run python src/nappe/quelle_fenetre_lit_une_bascule.py --verifier
    uv run python src/nappe/quelle_fenetre_lit_une_bascule.py \\
        --json docs/mesures/quelle_fenetre_lit_une_bascule.json
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))

from fiber_orientation import orientation_profile  # noqa: E402
from langle_publie_est_il_celui_des_fibres import (LES_CAMPAGNES,  # noqa: E402
                                                   ecart_entre_deux_tranches)

MESURES = RACINE / "docs" / "mesures"
COTE = 48
DECALAGES = 12
ANGLE_DU_PREMIER_PLI_DEG = 30.0
LONGUEUR_DE_FIBRE_UM = 30.0
# ⚠ Les longueurs sont dites EN FEUILLES et jamais en couches : c'est le rapport a l'epaisseur qui
# est la question, et un nombre de couches ne veut rien dire sans le pas et le voxel.
LONGUEURS_EN_FEUILLES = (0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 3.0)
CONTRASTES = (0.0, 0.02, 0.05, 0.1, 0.2, 0.5)
# ⚠ La fenetre de la campagne : 109 couches a 2,4 µm, telle que `14` §3 la lit.
COUCHES_DE_LA_CAMPAGNE = 109


def _volume(contraste: float, plis: int, voxel_um: float, pas_um: float,
            transition_um: float = 0.0, bruit: float = 0.0,
            feuilles_independantes: bool = False):
    from combien_de_pas_la_matiere_porte import VolumeFabriqueAFibres  # noqa: PLC0415

    return VolumeFabriqueAFibres(
        pas_um, longueur_de_fibre_um=LONGUEUR_DE_FIBRE_UM, contraste_des_fibres=float(contraste),
        angle_du_premier_pli_deg=ANGLE_DU_PREMIER_PLI_DEG, plis_par_feuille=int(plis),
        transition_um=float(transition_um), bruit=float(bruit),
        feuilles_independantes=bool(feuilles_independantes),
        voxel_um=voxel_um, forme=(4000, 4000, 4000))


def courbe_de_la_fixture(couches: int, decalage_um: float, contraste: float, plis: int,
                         voxel_um: float, pas_um: float, cote: int = COTE,
                         transition_um: float = 0.0, bruit: float = 0.0,
                         feuilles_independantes: bool = False) -> list:
    """La courbe (angle, cohérence) d'une fenêtre posée à un DÉCALAGE choisi dans la feuille.

    ⚠⚠ LE DÉPART EST RECALÉ SUR UN DÉBUT DE FEUILLE PUIS DÉCALÉ, jamais posé au hasard : sans le
    recalage, « décalage zéro » voudrait dire « là où le centre du volume est tombé », donc le
    balayage mesurerait un décalage inconnu plus le sien.

    ⚠ `transition_um`, `bruit` et `feuilles_independantes` valent leur valeur neutre par défaut,
    donc toute campagne antérieure lit la matière qu'elle a toujours lue : les ajouter avec une
    valeur active par défaut aurait déplacé en silence ce que `173`, `177` et `179` publient.

    ⚠⚠ `feuilles_independantes` donne à chaque FEUILLE un angle tiré, donc une matière dont les
    seules frontières d'orientation sont aux frontières de FEUILLE — un pas de `pas_um` et non de
    `pas_um / plis`. C'est l'analogue de l'interstice, et c'est ce que `181` oppose au pli.
    """
    bloc = bloc_de_la_fixture(couches, decalage_um, contraste, plis, voxel_um, pas_um, cote,
                              transition_um, bruit, feuilles_independantes)
    ang, coh = orientation_profile(bloc)
    return [[float(x), float(y)] for x, y in zip(ang, coh)]


def bloc_de_la_fixture(couches: int, decalage_um: float, contraste: float, plis: int,
                       voxel_um: float, pas_um: float, cote: int = COTE,
                       transition_um: float = 0.0, bruit: float = 0.0,
                       feuilles_independantes: bool = False) -> np.ndarray:
    """La MATIERE elle-meme, avant qu'aucun estimateur ne la lise.

    ⚠⚠ ELLE EST SORTIE DE `courbe_de_la_fixture` ET NON RECOPIEE. Une seconde ecriture du volume
    serait une seconde definition de la fixture, libre de diverger sur le recalage, sur l'ordre des
    axes ou sur le pas d'echantillonnage — et toutes les tranches qui comparent leurs chiffres a
    ceux d'une autre liraient alors deux matieres sous un seul nom. C'est la raison pour laquelle
    `179` a deja sorti `modulation_des_fibres` de `lire`.

    ⚠ Le depart est recale sur un debut de feuille puis decale, comme il l'a toujours ete : le
    contrat de `courbe_de_la_fixture` est inchange, et les batteries anterieures le verifient.
    """
    vol = _volume(contraste, plis, voxel_um, pas_um, transition_um, bruit,
                  feuilles_independantes)
    centre = np.array([2000.0, 2000.0, 2000.0])
    proj0 = float(centre @ vol.normale) * vol.voxel_um
    recale = (np.floor(proj0 / vol.pas_um) * vol.pas_um + float(decalage_um) - proj0)
    base = centre + (recale / vol.voxel_um) * vol.normale
    d = np.arange(int(couches)) * (voxel_um / vol.voxel_um)
    a = (np.arange(int(cote)) - cote / 2.0) * (voxel_um / vol.voxel_um)
    D, I, J = np.meshgrid(d, a, a, indexing="ij")
    pts = (base[None, None, None, :] + D[..., None] * vol.normale
           + I[..., None] * vol.e2 + J[..., None] * vol.e1)
    return vol.lire(pts.reshape(-1, 3)).reshape(int(couches), cote, cote)


def la_paire(courbe, coupe: int | None = None) -> dict:
    """La BASCULE et son TÉMOIN, lus avec le même estimateur, autour d'une coupe.

    ⭐⭐⭐⭐ LE TÉMOIN EST CE QUI REND LA BASCULE LISIBLE. Il est l'écart entre les deux MOITIÉS de
    la première part — donc entre deux tranches qui, sur une matière à deux plis bien coupée,
    tombent DANS le même pli. Une bascule qui ne dépasse pas son témoin ne dit rien : la fenêtre lit
    alors la même chose des deux côtés, ou du bruit.

    ⚠⚠ `coupe=None` est la recette du producteur : couper AU MILIEU, sans rien savoir de la phase.
    C'est celle que `fiber_orientation.survey` emploie, et c'est elle que cette tranche met à
    l'épreuve.

    ⚠ `None` des deux côtés quand les tranches n'ont pas assez de couches texturées — un écart pris
    sur du bruit est un angle aléatoire mais parfaitement défini.
    """
    n = len(courbe)
    if n < 8:
        return {"decidable": False, "raison": "moins de huit couches", "couches": n}
    k = n // 2 if coupe is None else int(coupe)
    if k < 4 or n - k < 4:
        return {"decidable": False, "raison": "une part n'a pas quatre couches", "couches": n,
                "coupe": k}
    bascule = ecart_entre_deux_tranches(courbe, 0, k, k, n)
    temoin = ecart_entre_deux_tranches(courbe, 0, k // 2, k // 2, k)
    if bascule is None or temoin is None:
        return {"decidable": False, "raison": "une tranche n'a pas assez de couches texturées",
                "couches": n, "coupe": k, "bascule_deg": bascule, "temoin_deg": temoin}
    return {"decidable": True, "couches": n, "coupe": k,
            "bascule_deg": round(float(bascule), 3), "temoin_deg": round(float(temoin), 3),
            "la_bascule_depasse_le_temoin": bool(bascule > temoin)}


def la_meilleure_coupe(courbe) -> dict:
    """La coupe qui MAXIMISE l'écart entre les deux parts, et ce qu'elle rend.

    ⭐⭐⭐⭐ POURQUOI ELLE EXISTE. Une bascule est à un endroit PRÉCIS dans l'épaisseur, et la phase
    de la fenêtre n'est pas connue sur données réelles. Une coupe au milieu tombe donc où elle
    tombe ; chercher la coupe revient à chercher la frontière plutôt qu'à espérer être dessus.

    ⚠⚠⚠ ET MAXIMISER EST EXACTEMENT CE QUI PEUT TROUVER DU BRUIT. C'est pour cela que son TÉMOIN
    est lu à la coupe retenue, avec le même estimateur, et que le contrôle vide de cette tranche
    porte sur ELLE autant que sur la coupe aveugle : une recette qui « lirait » une bascule sur une
    matière à un seul pli mesurerait sa propre liberté de choisir.

    ⚠ La coupe est cherchée sur toutes les positions qui laissent quatre couches de chaque côté ;
    aucune n'est écartée à l'avance, donc le maximum est celui du balayage entier.
    """
    n = len(courbe)
    if n < 16:
        return {"decidable": False, "raison": "moins de seize couches", "couches": n}
    lus = [la_paire(courbe, k) for k in range(4, n - 3)]
    lus = [x for x in lus if x.get("decidable")]
    if not lus:
        return {"decidable": False, "raison": "aucune coupe lisible", "couches": n}
    meilleur = max(lus, key=lambda x: x["bascule_deg"])
    return {**meilleur, "coupes_essayees": len(lus),
            "coupe_en_part_de_fenetre": round(meilleur["coupe"] / float(n), 3)}


def _med(v):
    return round(float(statistics.median(v)), 3) if v else None


LES_RECETTES = ("aveugle", "meilleure")


def _lire(courbe, recette: str) -> dict:
    return la_paire(courbe) if recette == "aveugle" else la_meilleure_coupe(courbe)


def balayer_le_decalage(couches: int, contraste: float, voxel_um: float, pas_um: float,
                        decalages: int = DECALAGES) -> dict:
    """La même fenêtre à tous les décalages d'une feuille, sur DEUX matières APPARIÉES.

    ⭐⭐⭐⭐ LE CONTRÔLE EST APPARIÉ, ET C'EST CE QUI LE REND CAPABLE DE MORDRE. À chaque décalage on
    lit la MÊME fenêtre sur une matière à **deux** plis et sur une matière à **un** pli, tout étant
    égal par ailleurs — même pas, même voxel, même contraste, même position. La question n'est donc
    pas « la bascule est-elle grande » mais « est-elle plus grande que sur une matière qui n'en a
    pas », ce qui est la forme jointe que ce dépôt emploie depuis `165` et où aucun seuil n'entre.

    ⚠⚠ DEUX CONTRÔLES DIFFÉRENTS, ET IL FAUT LES DEUX. Le **témoin** demande si la recette voit une
    différence là où il n'y en a pas DANS la matière ; l'**apparié à un pli** demande si elle en
    voit une sur une matière qui n'en a pas DU TOUT. Une recette qui maximise passe le premier et
    échoue le second, une recette aveugle peut faire l'inverse.

    ⚠ La courbe est construite UNE fois par matière et par décalage, puis lue par les deux
    recettes : deux constructions seraient deux matières, et la comparaison cesserait d'être
    appariée.
    """
    par_recette = {r: [] for r in LES_RECETTES}
    # ⚠⚠⚠ COMBIEN DE DECALAGES RENDENT DEUX MATIERES REELLEMENT DIFFERENTES. Sans ce compte, un
    # controle apparie neutralise — la meme matiere lue des deux cotes — resterait invisible : une
    # sonde l'a verifie, la batterie passait au vert. Le compte est structurel, il ne juge rien.
    differentes = 0
    for k in range(int(decalages)):
        dec = float(pas_um) * k / float(decalages)
        deux = courbe_de_la_fixture(couches, dec, contraste, 2, voxel_um, pas_um)
        une = courbe_de_la_fixture(couches, dec, contraste, 1, voxel_um, pas_um)
        differentes += int(deux != une)
        for r in LES_RECETTES:
            a, b = _lire(deux, r), _lire(une, r)
            ligne = {"decalage_um": round(dec, 3), "deux_plis": a, "un_pli": b,
                     "decidable": bool(a.get("decidable") and b.get("decidable"))}
            if ligne["decidable"]:
                ligne["la_bascule_depasse_le_temoin"] = bool(a["la_bascule_depasse_le_temoin"])
                ligne["elle_depasse_la_matiere_sans_bascule"] = bool(
                    a["bascule_deg"] > b["bascule_deg"])
                ligne["elle_lit_la_bascule"] = bool(
                    ligne["la_bascule_depasse_le_temoin"]
                    and ligne["elle_depasse_la_matiere_sans_bascule"])
            par_recette[r].append(ligne)
    out = {"couches": int(couches), "contraste": float(contraste),
           "decalages_ou_les_deux_matieres_different": int(differentes),
           "epaisseur_um": round(float(couches) * voxel_um, 1),
           "en_feuilles": round(float(couches) * voxel_um / float(pas_um), 3),
           "decalages": int(decalages), "par_recette": {}}
    for r in LES_RECETTES:
        lus = [x for x in par_recette[r] if x["decidable"]]
        out["par_recette"][r] = {
            "decidable": bool(lus), "decalages_lus": len(lus),
            "bascule_mediane_deg": _med([x["deux_plis"]["bascule_deg"] for x in lus]),
            "temoin_median_deg": _med([x["deux_plis"]["temoin_deg"] for x in lus]),
            "bascule_a_un_pli_mediane_deg": _med([x["un_pli"]["bascule_deg"] for x in lus]),
            "depassent_le_temoin": int(sum(1 for x in lus
                                           if x["la_bascule_depasse_le_temoin"])),
            "depassent_la_matiere_sans_bascule": int(
                sum(1 for x in lus if x["elle_depasse_la_matiere_sans_bascule"])),
            "lisent_la_bascule": int(sum(1 for x in lus if x["elle_lit_la_bascule"])),
            # ⚠⚠ LA FORME JOINTE : une recette est FIABLE quand elle lit la bascule a TOUS les
            # decalages lus. Une majorite serait une loterie qu'on aurait eu la chance de gagner.
            "elle_lit_la_bascule_partout": bool(lus and all(x["elle_lit_la_bascule"]
                                                            for x in lus)),
            "lignes": par_recette[r]}
    out["decidable"] = any(out["par_recette"][r]["decidable"] for r in LES_RECETTES)
    return out


def balayer_la_longueur(voxel_um: float, pas_um: float, contraste: float = 0.5,
                        longueurs=LONGUEURS_EN_FEUILLES, decalages: int = DECALAGES) -> dict:
    """Pour chaque longueur de fenêtre, exprimée EN FEUILLES, ce que chaque recette lit."""
    lignes = []
    for f in longueurs:
        couches = max(16, int(round(float(f) * float(pas_um) / float(voxel_um))))
        lignes.append({"demande_en_feuilles": float(f),
                       **balayer_le_decalage(couches, contraste, voxel_um, pas_um, decalages)})
    return {"decidable": bool(lignes), "lignes": lignes, "longueurs_essayees": len(lignes),
            "longueurs_fiables": {
                r: [x["demande_en_feuilles"] for x in lignes
                    if x["par_recette"][r]["elle_lit_la_bascule_partout"]]
                for r in LES_RECETTES}}


def balayer_le_contraste(voxel_um: float, pas_um: float, longueur_en_feuilles: float,
                         contrastes=CONTRASTES, decalages: int = DECALAGES) -> dict:
    """À la longueur retenue, jusqu'où le contraste entre plis peut-il descendre ?

    ⚠ Le contraste NUL est le premier point du balayage, et c'est un contrôle vide de plus : sans
    texture il n'y a pas d'orientation, donc pas de bascule à lire.
    """
    couches = max(16, int(round(float(longueur_en_feuilles) * float(pas_um) / float(voxel_um))))
    lignes = [{"contraste": float(c),
               **balayer_le_decalage(couches, c, voxel_um, pas_um, decalages)}
              for c in contrastes]
    return {"decidable": bool(lignes), "couches": int(couches),
            "longueur_en_feuilles": float(longueur_en_feuilles), "lignes": lignes,
            "contrastes_qui_tiennent": {
                r: [x["contraste"] for x in lignes
                    if x["par_recette"][r]["elle_lit_la_bascule_partout"]]
                for r in LES_RECETTES}}


def ce_que_la_campagne_a_lu(voxel_um: float, pas_um: float,
                            couches: int = COUCHES_DE_LA_CAMPAGNE,
                            campagnes=LES_CAMPAGNES, racine: Path = MESURES,
                            decalages: int = DECALAGES) -> dict:
    """La fenêtre de `14` §3, et ce que les deux recettes y lisent sur une matière qui bascule.

    ⭐⭐⭐⭐ C'EST LA JONCTION. Poser la fenêtre de la campagne sur une matière dont la bascule est
    CONSTRUITE dit si le protocole POUVAIT répondre — et un résultat négatif obtenu avec une
    fenêtre qui ne peut pas lire n'est pas un résultat sur la matière.

    ⚠⚠ CE N'EST PAS UNE RELECTURE DES DONNÉES RÉELLES. Le nombre de couches est lu dans les
    campagnes stockées, rien d'autre : la fixture ne sait pas ce qu'un vrai papyrus porte.
    """
    couches_publiees = []
    for nom in campagnes:
        chemin = racine / nom
        if not chemin.is_file():
            continue
        d = json.loads(chemin.read_text(encoding="utf-8"))
        for s_ in (d if isinstance(d, list) else [d]):
            if isinstance(s_, dict) and s_.get("layers") is not None:
                couches_publiees.append(int(s_["layers"]))
    return {"decidable": True, "couches_de_la_campagne": int(couches),
            "couches_publiees_distinctes": sorted(set(couches_publiees)),
            "segments_lus": len(couches_publiees),
            "epaisseur_um": round(float(couches) * voxel_um, 1),
            "en_feuilles": round(float(couches) * voxel_um / float(pas_um), 3),
            "sur_une_matiere_qui_bascule": balayer_le_decalage(
                couches, 0.5, voxel_um, pas_um, decalages)}


def juger(longueurs: dict, campagne: dict, contraste: dict | None) -> dict:
    """Ce que les balayages disent, recette par recette, sans les fondre en un chiffre."""
    camp = (campagne.get("sur_une_matiere_qui_bascule") or {}).get("par_recette") or {}
    fiables = longueurs.get("longueurs_fiables") or {}
    out = {"decidable": bool(longueurs.get("decidable")),
           "la_fenetre_de_la_campagne_en_feuilles": campagne.get("en_feuilles"),
           "par_recette": {}}
    for r in LES_RECETTES:
        c = camp.get(r) or {}
        out["par_recette"][r] = {
            "longueurs_fiables": fiables.get(r) or [],
            "une_longueur_la_rend_fiable": bool(fiables.get(r)),
            "sur_la_fenetre_de_la_campagne": {
                "lisent_la_bascule": c.get("lisent_la_bascule"),
                "decalages_lus": c.get("decalages_lus"),
                "elle_lit_la_bascule_partout": bool(c.get("elle_lit_la_bascule_partout"))},
            "contrastes_qui_tiennent": ((contraste or {}).get("contrastes_qui_tiennent")
                                        or {}).get(r)}
    # ⚠⚠⚠ LE VERDICT EST JOINT ET IL PORTE SUR LES DEUX RECETTES : aucune ne repond. Si l'une
    # d'elles etait fiable, `14` serait a refaire avec elle ; comme aucune ne l'est, ce qui manque
    # n'est pas un reglage mais une facon de trouver la frontiere sans la chercher dans le bruit.
    out["aucune_recette_ne_repond"] = bool(
        out["decidable"] and not any(out["par_recette"][r]["une_longueur_la_rend_fiable"]
                                     for r in LES_RECETTES))
    out["la_campagne_ne_pouvait_pas_repondre"] = bool(
        out["decidable"]
        and not out["par_recette"]["aveugle"]["sur_la_fenetre_de_la_campagne"][
            "elle_lit_la_bascule_partout"])
    return out


def mesurer() -> dict:
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    vx, pas = C.VOXEL_FIN_UM, C.PAS_UM
    longueurs = balayer_la_longueur(vx, pas)
    campagne = ce_que_la_campagne_a_lu(vx, pas)
    contraste = balayer_le_contraste(vx, pas, 1.0)
    return {"pas_um": float(pas), "voxel_um": float(vx),
            "couches_par_feuille": round(float(pas) / float(vx), 1),
            "les_longueurs": longueurs, "la_campagne": campagne, "le_contraste": contraste,
            "le_verdict": juger(longueurs, campagne, contraste)}


def _ligne(x: dict, r: str, etiquette: str) -> str:
    b = x["par_recette"][r]
    marq = "★" if b["elle_lit_la_bascule_partout"] else "✗"
    return (f"   {marq} {etiquette:<22} bascule {str(b['bascule_mediane_deg']):>7} · témoin "
            f"{str(b['temoin_median_deg']):>7} · à un pli "
            f"{str(b['bascule_a_un_pli_mediane_deg']):>7} · lit "
            f"{b['lisent_la_bascule']}/{b['decalages_lus']}")


def afficher(r: dict) -> None:
    lo, ca, ct, v = r["les_longueurs"], r["la_campagne"], r["le_contraste"], r["le_verdict"]
    print("QUELLE FENÊTRE LIT UNE BASCULE ?")
    print(f"  pas {r['pas_um']} µm, voxel {r['voxel_um']} µm → une feuille = "
          f"{r['couches_par_feuille']} couches")
    for rec in LES_RECETTES:
        print()
        print(f"  RECETTE « {rec} » · les longueurs, matière à deux plis contre matière à un pli")
        for x in lo["lignes"]:
            print(_ligne(x, rec, f"{x['demande_en_feuilles']:.2f} feuille ({x['couches']} c)"))
        print(f"   ★ longueurs fiables : {lo['longueurs_fiables'][rec]}")
        print(_ligne(ca["sur_une_matiere_qui_bascule"], rec,
                     f"LA CAMPAGNE, {ca['en_feuilles']} f"))
    print()
    print(f"  LE CONTRASTE · à {ct['longueur_en_feuilles']} feuille ({ct['couches']} couches)")
    for rec in LES_RECETTES:
        for x in ct["lignes"]:
            print(_ligne(x, rec, f"{rec[:4]} contraste {x['contraste']:.2f}"))
        print(f"   ★ contrastes qui tiennent ({rec}) : {ct['contrastes_qui_tiennent'][rec]}")
    print()
    print(f"  LA CAMPAGNE · {ca['couches_de_la_campagne']} couches = {ca['epaisseur_um']} µm = "
          f"{ca['en_feuilles']} feuille · couches publiées "
          f"{ca['couches_publiees_distinctes']} sur {ca['segments_lus']} segments")
    print()
    print("  ★ LE VERDICT")
    for rec in LES_RECETTES:
        b = v["par_recette"][rec]
        print(f"     {rec:<10} fiable quelque part : {b['une_longueur_la_rend_fiable']} "
              f"{b['longueurs_fiables']} · sur la fenêtre de la campagne : "
              f"{b['sur_la_fenetre_de_la_campagne']['lisent_la_bascule']}/"
              f"{b['sur_la_fenetre_de_la_campagne']['decalages_lus']}")
    print(f"     {'aucune recette ne répond':<44} {v['aucune_recette_ne_repond']}")
    print(f"     {'la campagne ne pouvait pas répondre':<44} "
          f"{v['la_campagne_ne_pouvait_pas_repondre']}")


def verifier() -> int:
    echecs = controles = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    import combien_dinterstices_traverses as C  # noqa: PLC0415
    vx, pas = C.VOXEL_FIN_UM, C.PAS_UM

    # ---- la paire, sur des courbes fabriquées dont la réponse se dérive d'elles
    v("une courbe trop courte n'est pas décidable",
      la_paire([[10.0, 0.9]] * 6).get("decidable") is False)
    # ⚠⚠ L'ATTENDU SE DERIVE DE LA FIXTURE : une courbe dont la seconde moitie tourne d'un quart
    # rend une bascule de 90 et un temoin de 0, parce que les deux moities de la PREMIERE part y
    # sont identiques. Si la paire lisait deux fois la meme tranche, les deux vaudraient 0.
    droite = [[20.0, 0.9]] * 16 + [[110.0, 0.9]] * 16
    p = la_paire(droite)
    v("⭐⭐⭐⭐ la bascule lit les deux PARTS et le témoin les deux moitiés de la première",
      p["decidable"] and abs(p["bascule_deg"] - 90.0) < 1e-6
      and abs(p["temoin_deg"]) < 1e-6 and p["la_bascule_depasse_le_temoin"],
      f"bascule {p.get('bascule_deg')}°, témoin {p.get('temoin_deg')}°")
    q = la_paire([[20.0, 0.9]] * 8 + [[110.0, 0.9]] * 24)
    v("... et une courbe qui tourne au QUART rend un témoin haut, donc la bascule ne dit rien",
      q["decidable"] and q["temoin_deg"] > q["bascule_deg"]
      and not q["la_bascule_depasse_le_temoin"],
      f"bascule {q.get('bascule_deg')}°, témoin {q.get('temoin_deg')}°")
    plate = la_paire([[10.0, 0.0]] * 40)
    v("⚠ une courbe sans couche texturée n'est pas décidable, elle ne rend pas zéro",
      plate.get("decidable") is False, plate.get("raison"))
    # ⭐⭐⭐ LA MEILLEURE COUPE TROUVE LA FRONTIERE QUAND LA COUPE AVEUGLE LA MANQUE.
    decalee = [[20.0, 0.9]] * 8 + [[110.0, 0.9]] * 24
    mc = la_meilleure_coupe(decalee)
    v("⭐⭐⭐ la meilleure coupe trouve la frontière que la coupe aveugle manque",
      mc["decidable"] and mc["coupe"] == 8 and abs(mc["bascule_deg"] - 90.0) < 1e-6,
      f"coupe {mc.get('coupe')} sur {mc.get('couches')}, bascule {mc.get('bascule_deg')}°")
    # ⚠⚠ LA BORNE SE VERIFIE PAR SA PROPRIETE, PAS PAR UN RECOMPTE. Recalculer le nombre de coupes
    # ici serait une seconde definition de « quelles coupes sont admissibles », libre de diverger
    # de celle du code. Ce qui se teste est la REGLE : une coupe qui laisserait moins de quatre
    # couches dans une tranche n'est pas lisible, celle qui en laisse quatre l'est.
    v("... et une coupe qui laisse moins de quatre couches dans une tranche n'est pas lisible",
      la_paire(decalee, 7).get("decidable") is False
      and la_paire(decalee, 8).get("decidable") is True
      and la_paire(decalee, len(decalee) - 4).get("decidable") is True
      and la_paire(decalee, len(decalee) - 3).get("decidable") is False,
      f"{mc.get('coupes_essayees')} coupes essayées sur {len(decalee)} couches")

    # ---- le balayage APPARIÉ
    un = int(round(pas / vx))
    bal = balayer_le_decalage(un, 0.5, vx, pas, decalages=4)
    v("le balayage lit les deux recettes sur les mêmes courbes",
      set(bal["par_recette"]) == set(LES_RECETTES)
      and all(len(bal["par_recette"][r]["lignes"]) == 4 for r in LES_RECETTES))
    v("⚠⚠ chaque décalage porte la matière à deux plis ET celle à un pli",
      all(x["deux_plis"]["decidable"] and x["un_pli"]["decidable"]
          for x in bal["par_recette"]["aveugle"]["lignes"]))
    # ⚠⚠⚠ ET LES DEUX MATIERES SONT REELLEMENT DEUX. Une sonde a neutralise le controle apparie en
    # relisant la matiere a deux plis des deux cotes, et la batterie est restee VERTE : c'etait une
    # verification incapable d'echouer. Ce compte est ce qui la rend capable de tomber.
    v("⚠⚠⚠ ... et ce sont deux matières DIFFÉRENTES, à chaque décalage",
      bal["decalages_ou_les_deux_matieres_different"] == bal["decalages"],
      f"{bal['decalages_ou_les_deux_matieres_different']}/{bal['decalages']}")
    # ⭐⭐⭐⭐ LES DEUX CONDITIONS SONT EXIGEES ENSEMBLE, et la sonde le verifie sur les comptes :
    # « lit la bascule » ne peut jamais depasser le plus petit des deux.
    for r in LES_RECETTES:
        b = bal["par_recette"][r]
        v(f"⭐⭐⭐⭐ « {r} » n'a lu la bascule qu'où les DEUX conditions tiennent",
          b["lisent_la_bascule"] <= min(b["depassent_le_temoin"],
                                        b["depassent_la_matiere_sans_bascule"]),
          f"{b['lisent_la_bascule']} contre témoin {b['depassent_le_temoin']} et un pli "
          f"{b['depassent_la_matiere_sans_bascule']}")
    v("⚠⚠ et « partout » est exactement « à tous les décalages lus »",
      all(bal["par_recette"][r]["elle_lit_la_bascule_partout"]
          == (bal["par_recette"][r]["lisent_la_bascule"]
              == bal["par_recette"][r]["decalages_lus"]) for r in LES_RECETTES))
    # ⚠ CONTROLE VIDE : sans texture, il n'y a pas de bascule a lire.
    sans = balayer_le_decalage(un, 0.0, vx, pas, decalages=4)
    v("⚠ contrôle vide : sans texture, aucune recette ne lit de bascule",
      not any(sans["par_recette"][r]["elle_lit_la_bascule_partout"] for r in LES_RECETTES),
      " · ".join(f"{r} {sans['par_recette'][r]['lisent_la_bascule']}/"
                 f"{sans['par_recette'][r]['decalages_lus']}" for r in LES_RECETTES))

    # ---- la fenêtre de la campagne
    camp = ce_que_la_campagne_a_lu(vx, pas, decalages=4)
    v("la fenêtre de la campagne est lue depuis les campagnes stockées",
      camp["segments_lus"] > 0 and COUCHES_DE_LA_CAMPAGNE in camp["couches_publiees_distinctes"],
      f"{camp['segments_lus']} segments, couches {camp['couches_publiees_distinctes']}")
    v("⭐⭐⭐⭐ ... et sa longueur n'est PAS un nombre entier de feuilles",
      abs(camp["en_feuilles"] - round(camp["en_feuilles"])) > 0.01,
      f"{camp['en_feuilles']} feuille")

    # ---- le verdict est JOINT
    faux = juger({"decidable": True,
                  "longueurs_fiables": {"aveugle": [1.0], "meilleure": []}}, camp, None)
    v("⚠⚠ le verdict « aucune recette ne répond » tombe dès qu'une seule est fiable",
      faux["aucune_recette_ne_repond"] is False)
    vrai = juger({"decidable": True,
                  "longueurs_fiables": {"aveugle": [], "meilleure": []}}, camp, None)
    v("... et il tient quand aucune ne l'est", vrai["aucune_recette_ne_repond"] is True)

    print()
    if echecs:
        print(f"ÉCHEC ({echecs} failures, {controles} checks)")
    else:
        print(f"ALL PASS (0 failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path, default=None)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer()
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False))
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
