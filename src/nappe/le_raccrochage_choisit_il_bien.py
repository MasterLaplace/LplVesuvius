#!/usr/bin/env python3
"""Le raccrochage choisit-il le bon décalage ? — sa lecture, contre celle d'un oracle

⚠⚠⚠ POURQUOI CE FICHIER EXISTE. `le_cout_dun_seul_pas` a chiffré les trois postes du coût d'un
pas : la longueur vaut 33 %, la direction 3 %, et la correction **point par point** 19 %. Ce
dernier poste est exactement le domaine du raccrochage, et sa borne parfaite laisse 19,1 µm —
largement sous la demi-feuille. Or le raccrochage mesuré n'en prend presque **rien**. Deux
explications restent, et elles demandent des remèdes opposés :

- soit **il lit bien** et la géométrie refuse le gain — alors il n'y a rien à réparer dans la
  lecture, et le poste est illusoire ;
- soit **il lit mal** — alors la lecture est le chantier, et 19 % attendent.

⭐⭐ CE FICHIER LES SÉPARE EN CONFRONTANT LES DEUX CHOIX SUR LES MÊMES CELLULES. Le raccrochage
choisit un décalage par corrélation avec un gabarit lu sur la spire de départ ; l'oracle choisit
celui qui minimise vraiment la distance à la cible. Si les deux se ressemblent, la lecture est
bonne ; s'ils divergent, elle ne l'est pas.

⚠⚠ L'ORACLE EST BORNÉ À LA MÊME FENÊTRE. Le laisser choisir hors de la fenêtre du raccrochage
ferait de la comparaison une mesure de la fenêtre et non de la lecture : il pourrait viser un
décalage que l'autre ne peut pas atteindre, et son avance ne dirait rien de leur accord.

⚠⚠ ET LE TÉMOIN EST LE GABARIT MÉLANGÉ — même géométrie, même fenêtre, même recherche, seule la
FORME cherchée est détruite. Une corrélation avec l'oracle qui ne battrait pas celle du mélange
voudrait dire que le raccrochage ne lit rien du tout.

Usage :
    uv run python src/nappe/le_raccrochage_choisit_il_bien.py --verifier
    uv run python src/nappe/le_raccrochage_choisit_il_bien.py \\
        --json docs/mesures/le_raccrochage_choisit_il_bien.json
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
for _d in ("commun", "nappe", "encre"):
    sys.path.insert(0, str(RACINE / "src" / _d))

# ⚠ Un seul lecteur de corpus pour tous les dérouleurs, et ses deux fixtures hors ligne.
from le_corpus_des_spires import corpus_fabrique, corpus_publie, volume_fabrique  # noqa: E402


def decalage_de_loracle(points: np.ndarray, directions: np.ndarray, decalages: np.ndarray,
                        cible: np.ndarray, voxel_um: float) -> tuple[np.ndarray, np.ndarray]:
    """Le décalage qui minimise VRAIMENT la distance à la cible, et l'erreur qu'il laisse.

    ⚠⚠ IL EST CHERCHÉ DANS LA MÊME FENÊTRE QUE LE RACCROCHAGE, et c'est ce qui rend la
    comparaison honnête : un oracle libre de viser hors de cette fenêtre gagnerait pour une
    raison qui n'a rien à voir avec la qualité d'une lecture.

    ⚠ Il regarde la cible une fois par cellule. Ce n'est donc pas un contendant mais une borne,
    et le lire comme une performance serait lire la réponse comme une méthode.
    """
    from le_pas_normal_atteint_la_spire import distance_a  # noqa: PLC0415

    table = np.stack([distance_a(points + t * directions, cible, voxel_um)
                      for t in decalages], axis=1)
    i = table.argmin(axis=1)
    return decalages[i], table[np.arange(len(table)), i]


def accord_des_decalages(a: np.ndarray, b: np.ndarray) -> dict:
    """L'accord de rang entre deux choix de décalage, et l'écart médian entre eux.

    ⚠ La corrélation est de RANG : on demande si les deux choisissent grand là où l'autre
    choisit grand, pas si l'un vaut l'autre à un facteur près. Une lecture décalée d'un biais
    constant garde tout son rang, et c'est une lecture réparable — le rang la distingue d'une
    lecture qui ne voit rien.
    """
    from scipy.stats import spearmanr  # noqa: PLC0415

    if len(a) < 3 or float(np.std(a)) == 0.0 or float(np.std(b)) == 0.0:
        return dict(rho=None, p=None, n=int(len(a)), ecart_median=None)
    rho, pval = spearmanr(a, b)
    return dict(rho=round(float(rho), 3), p=float(f"{pval:.3g}"), n=int(len(a)),
                ecart_median=round(float(np.median(np.abs(a - b))), 2))


def mesurer(echantillon: int = 800, graine: int = 42, minimum: int = 30,
            cache_actif: bool = True, cote: float | None = None,
            corpus: dict | None = None, volume=None) -> dict:
    """Le décalage que le raccrochage choisit, contre celui que l'oracle choisirait."""
    from le_pas_normal_atteint_la_spire import distance_a, normales  # noqa: PLC0415
    from le_raccrochage_a_la_matiere import (  # noqa: PLC0415
        BOITE_CENTRE, BOITE_COTE, CacheDisque, Volume, ZARR, accorde_aux_spires, correler,
        decalage_retenu, le_long, profil_autour, url_du_volume,
    )

    c = corpus_publie() if corpus is None else corpus
    volume_nom, voxel_um = c["volume"], float(c["voxel_um"])
    ecart_um = float(c["ecart_um"])
    pas_vx = ecart_um / voxel_um
    demi_vx = pas_vx / 2.0
    demi_gab = round(demi_vx / 2.0)
    if volume is None and not accorde_aux_spires():
        raise RuntimeError(f"le volume {ZARR} n'est pas celui des spires ({volume_nom})")
    if volume is None:
        import tracecheck as tc  # noqa: PLC0415

        url = url_du_volume()
        vol = Volume(url, tc.array_meta(url, 0, 120), CacheDisque(actif=cache_actif))
    else:
        vol = volume

    cote = BOITE_COTE if cote is None else float(cote)
    centre = np.array(BOITE_CENTRE)
    lo, hi = centre - cote / 2, centre + cote / 2
    rng = np.random.default_rng(graine)
    t_gab = np.arange(-demi_gab, demi_gab + 1e-9, 1.0)
    t_ligne = np.arange(-(demi_vx + demi_gab), demi_vx + demi_gab + 1e-9, 1.0)

    grilles, nuages = {}, {}
    for rang, (a, ok) in sorted(c["grilles"].items()):
        dans = ok & ((a >= lo) & (a <= hi)).all(axis=-1)
        if int(dans.sum()) < minimum:
            continue
        grilles[rang] = (a, dans)
        nuages[rang] = a[ok]

    lignes, tous = [], {"racc": [], "mel": [], "oracle": []}
    for r in sorted(grilles):
        if r + 1 not in nuages:
            continue
        a0, dans = grilles[r]
        n0, bon = normales(a0, dans)
        garde0 = bon & dans
        if int(garde0.sum()) < minimum:
            continue
        p, d = a0[garde0], n0[garde0]
        if len(p) > echantillon:
            pris = rng.choice(len(p), size=echantillon, replace=False)
            p, d = p[pris], d[pris]
        cible = nuages[r + 1]
        # ⚠ Le sens est le bit de supervision unique, fixé une fois et de la même façon que dans
        # `le_raccrochage_a_la_matiere` : importer son geste serait mieux, mais il est enfoui
        # dans une boucle ; il est donc récrit à l'identique et le contrôle l'épingle.
        sortant = float(np.median(distance_a(p + d * pas_vx, cible, voxel_um)))
        rentrant = float(np.median(distance_a(p - d * pas_vx, cible, voxel_um)))
        sens = 1.0 if sortant <= rentrant else -1.0

        vg, okg = le_long(p, d, t_gab, vol)
        if int(okg.sum()) < minimum:
            continue
        gab = profil_autour(vg[okg])
        gab_oriente = gab if sens > 0 else gab[::-1]
        prevu, dd = p + d * (sens * pas_vx), d * sens
        v_, okv = le_long(prevu, dd, t_ligne, vol)
        if int(okv.sum()) < minimum:
            continue
        P, D, L = prevu[okv], dd[okv], v_[okv]

        corr, centres = correler(L, gab_oriente, t_ligne)
        t_racc = decalage_retenu(corr, centres)
        corr_m, _ = correler(L, rng.permuted(gab_oriente), t_ligne)
        t_mel = decalage_retenu(corr_m, centres)
        # ⚠⚠ L'ORACLE CHERCHE DANS `centres`, pas dans `t_ligne` : `decalage_retenu` ne rend que
        # des décalages de cette grille-là, donc laisser l'oracle en balayer une autre
        # comparerait deux choix qui ne peuvent pas coïncider même en accord parfait.
        t_oracle, e_oracle = decalage_de_loracle(P, D, centres, cible, voxel_um)

        bons = np.isfinite(t_racc) & np.isfinite(t_mel)
        if int(bons.sum()) < minimum:
            continue
        t_racc, t_mel, t_oracle = t_racc[bons], t_mel[bons], t_oracle[bons]
        P, D, e_oracle = P[bons], D[bons], e_oracle[bons]
        tous["racc"].append(t_racc)
        tous["mel"].append(t_mel)
        tous["oracle"].append(t_oracle)

        def erreur(t):
            return float(np.median(distance_a(P + t[:, None] * D, cible, voxel_um)))

        lignes.append(dict(
            de=r, vers=r + 1, cellules=int(len(t_racc)),
            fenetre_vx=[round(float(centres.min()), 1), round(float(centres.max()), 1)],
            decalage_raccroche_median_vx=round(float(np.median(t_racc)), 2),
            decalage_melange_median_vx=round(float(np.median(t_mel)), 2),
            decalage_oracle_median_vx=round(float(np.median(t_oracle)), 2),
            accord_du_raccrochage=accord_des_decalages(t_racc, t_oracle),
            accord_du_melange=accord_des_decalages(t_mel, t_oracle),
            erreur_sans_bouger_um=round(erreur(np.zeros(len(t_racc))), 1),
            erreur_raccrochee_um=round(erreur(t_racc), 1),
            # ⚠⚠⚠ LE CONTENDANT QUI SÉPARE « IL RECENTRE » DE « IL LIT PAR CELLULE » : la
            # MÉDIANE de ses propres décalages, appliquée à toutes les cellules. Elle garde
            # exactement le déplacement d'ensemble que le raccrochage a trouvé et jette toute
            # l'information par cellule. S'il ne fait pas mieux qu'elle, sa lecture par point
            # ne sert à rien — et son gain n'est qu'un recentrage du pas déguisé.
            erreur_raccroche_constant_um=round(
                erreur(np.full(len(t_racc), float(np.median(t_racc)))), 1),
            # ⚠⚠⚠ ET LE REMÈDE D'UNE LIGNE, MESURÉ PLUTÔT QU'ÉCRIT COMME UNE PISTE : le même
            # raccrochage, son biais d'ensemble retiré. Il garde exactement sa lecture par
            # cellule et jette le déplacement médian, celui dont la mesure dit qu'il NUIT.
            erreur_raccroche_centre_um=round(
                erreur(t_racc - float(np.median(t_racc))), 1),
            erreur_melangee_um=round(erreur(t_mel), 1),
            erreur_oracle_um=round(float(np.median(e_oracle)), 1),
            bits_de_supervision=1))

    if not lignes:
        raise RuntimeError("aucune paire lisible dans la boîte")

    def med(cle):
        return round(float(np.median([e[cle] for e in lignes])), 1)

    racc = np.concatenate(tous["racc"])
    mel = np.concatenate(tous["mel"])
    orc = np.concatenate(tous["oracle"])
    r = dict(
        fragment="PHerc0500P2", volume=volume_nom, voxel_um=voxel_um,
        boite=dict(centre=list(BOITE_CENTRE), cote_voxels=cote),
        pas_nominal_um=ecart_um, demi_epaisseur_um=round(ecart_um / 2, 2),
        paires=len(lignes), cellules=int(len(racc)), lignes=lignes,
        cout=vol.cache.cout() | dict(voxels_absents=vol.absents, reprises_reseau=vol.reprises),
        erreur_sans_bouger_mediane_um=med("erreur_sans_bouger_um"),
        erreur_raccrochee_mediane_um=med("erreur_raccrochee_um"),
        erreur_melangee_mediane_um=med("erreur_melangee_um"),
        erreur_raccroche_constant_mediane_um=med("erreur_raccroche_constant_um"),
        erreur_raccroche_centre_mediane_um=med("erreur_raccroche_centre_um"),
        erreur_oracle_mediane_um=med("erreur_oracle_um"))
    # ⚠⚠⚠ LA COMPARAISON QUI DÉCIDE, ET IL EN FAUT DEUX. L'accord du raccrochage avec l'oracle
    # dit s'il LIT quelque chose ; celui du mélange dit ce que le hasard d'une même géométrie
    # rend déjà. Sans le second, une corrélation faible se lirait comme une lecture faible alors
    # qu'elle pourrait être du bruit de fenêtre.
    r["accord_du_raccrochage"] = accord_des_decalages(racc, orc)
    r["accord_du_melange"] = accord_des_decalages(mel, orc)
    ra, rm = r["accord_du_raccrochage"]["rho"], r["accord_du_melange"]["rho"]
    r["le_raccrochage_lit_quelque_chose"] = bool(
        ra is not None and rm is not None and ra > 0 and ra > abs(rm))
    r["ecart_median_a_loracle_vx"] = r["accord_du_raccrochage"]["ecart_median"]
    r["ecart_median_du_melange_vx"] = r["accord_du_melange"]["ecart_median"]
    r["ecart_median_sans_bouger_vx"] = round(float(np.median(np.abs(orc))), 2)
    # ⚠⚠ ET LA QUESTION QUE TOUT CE FICHIER POSE : le raccrochage prend-il ce que sa borne
    # prendrait ? Les deux gains sont publiés côte à côte, et leur rapport dit ce qu'il reste.
    r["gain_du_raccrochage_um"] = round(
        r["erreur_sans_bouger_mediane_um"] - r["erreur_raccrochee_mediane_um"], 1)
    r["gain_de_loracle_um"] = round(
        r["erreur_sans_bouger_mediane_um"] - r["erreur_oracle_mediane_um"], 1)
    r["part_du_gain_de_loracle_prise"] = (
        round(r["gain_du_raccrochage_um"] / r["gain_de_loracle_um"], 3)
        if r["gain_de_loracle_um"] > 1.0 else None)
    # ⚠⚠⚠ ET LE VERDICT QUE TOUT CE FICHIER EXISTE POUR RENDRE : le raccrochage bat-il sa
    # propre médiane ? Elle a le même déplacement d'ensemble et aucune information par cellule,
    # donc la battre est la seule preuve que la lecture point par point serve à quelque chose.
    r["paires_ou_le_raccrochage_bat_sa_mediane"] = sum(
        1 for e in lignes if e["erreur_raccrochee_um"] < e["erreur_raccroche_constant_um"])
    r["la_lecture_par_cellule_sert"] = bool(
        r["erreur_raccrochee_mediane_um"] < r["erreur_raccroche_constant_mediane_um"]
        and r["paires_ou_le_raccrochage_bat_sa_mediane"] > len(lignes) / 2)
    r["gain_du_recentrage_seul_um"] = round(
        r["erreur_sans_bouger_mediane_um"] - r["erreur_raccroche_constant_mediane_um"], 1)
    # ⚠⚠⚠ LE REMÈDE, JUGÉ. Retirer le biais d'ensemble doit rendre ce que ce biais coûte — si
    # c'est vrai, c'est le premier gain que la campagne obtient en CHANGEANT quelque chose
    # plutôt qu'en mesurant une borne.
    r["paires_ou_le_centrage_ameliore"] = sum(
        1 for e in lignes if e["erreur_raccroche_centre_um"] < e["erreur_raccrochee_um"])
    r["retirer_le_biais_ameliore"] = bool(
        r["erreur_raccroche_centre_mediane_um"] < r["erreur_raccrochee_mediane_um"]
        and r["paires_ou_le_centrage_ameliore"] > len(lignes) / 2)
    r["gain_du_retrait_du_biais_um"] = round(
        r["erreur_raccrochee_mediane_um"] - r["erreur_raccroche_centre_mediane_um"], 1)
    r["le_raccrochage_bat_son_melange"] = bool(
        r["erreur_raccrochee_mediane_um"] < r["erreur_melangee_mediane_um"]
        and sum(1 for e in lignes
                if e["erreur_raccrochee_um"] < e["erreur_melangee_um"]) > len(lignes) / 2)
    r["paires_ou_le_raccrochage_bat_son_melange"] = sum(
        1 for e in lignes if e["erreur_raccrochee_um"] < e["erreur_melangee_um"])
    return r


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # --- l'oracle ---
    p = np.array([[0.0, 0.0, 0.0], [10.0, 0.0, 0.0]])
    d = np.array([[0.0, 0.0, 1.0], [0.0, 0.0, 1.0]])
    cible = np.array([[0.0, 0.0, 3.0], [10.0, 0.0, -2.0]])
    t = np.arange(-5.0, 5.1, 1.0)
    choix, err = decalage_de_loracle(p, d, t, cible, 1.0)
    v("l'oracle trouve le décalage qui annule vraiment la distance",
      choix.tolist() == [3.0, -2.0] and np.allclose(err, 0.0), str(choix.tolist()))
    # ⚠⚠ IL EST BORNÉ À SA FENÊTRE : hors d'elle il ne peut pas viser, et c'est ce qui rend la
    # comparaison avec le raccrochage honnête. Un oracle libre gagnerait pour une raison qui n'a
    # rien à voir avec la qualité d'une lecture.
    etroit = np.arange(-1.0, 1.1, 1.0)
    choix2, err2 = decalage_de_loracle(p, d, etroit, cible, 1.0)
    v("... mais il ne sort JAMAIS de la fenêtre qu'on lui donne",
      choix2.tolist() == [1.0, -1.0] and err2.min() > 0, str(choix2.tolist()))

    # --- l'accord de rang ---
    a_ = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    v("deux choix identiques s'accordent parfaitement",
      accord_des_decalages(a_, a_)["rho"] == 1.0)
    v("... un biais constant garde tout le rang, parce qu'il est réparable",
      accord_des_decalages(a_, a_ + 7.0)["rho"] == 1.0,
      str(accord_des_decalages(a_, a_ + 7.0)["ecart_median"]))
    v("... et l'écart médian, lui, le voit",
      accord_des_decalages(a_, a_ + 7.0)["ecart_median"] == 7.0)
    v("deux choix opposés s'accordent à moins un",
      accord_des_decalages(a_, -a_)["rho"] == -1.0)
    # ⚠ Un choix constant n'a pas de rang : rendre une corrélation dessus serait rendre un
    # nombre qu'aucune donnée ne porte.
    v("un choix constant ne rend pas de corrélation",
      accord_des_decalages(a_, np.ones(5))["rho"] is None)
    v("... et un échantillon trop petit non plus",
      accord_des_decalages(a_[:2], a_[:2])["rho"] is None)

    # ⚠⚠⚠ LE CHEMIN QUI PRODUIT LE NOMBRE PUBLIÉ, HORS LIGNE, avec ses DEUX matières.
    from le_corpus_des_spires import geometrie_fabriquee  # noqa: PLC0415

    g0 = geometrie_fabriquee()
    fab = mesurer(echantillon=120, minimum=20, corpus=corpus_fabrique(),
                  volume=volume_fabrique(g0))
    v("la mesure tourne de bout en bout sur des matières fabriquées, sans rien lire",
      fab["paires"] > 0 and fab["cellules"] > 0,
      f"{fab['paires']} paires, {fab['cellules']} cellules")
    # ⚠⚠⚠ L'ORACLE EST UNE BORNE : il ne peut pas être battu par un contendant qui ne regarde
    # pas la cible. S'il l'était, c'est que quelque chose de la réponse aurait fui.
    v("... l'oracle n'est battu par aucun contendant aveugle",
      all(e["erreur_oracle_um"] <= min(e["erreur_raccrochee_um"], e["erreur_melangee_um"],
                                       e["erreur_sans_bouger_um"]) + 0.05
          for e in fab["lignes"]),
      str([(e["erreur_oracle_um"], e["erreur_raccrochee_um"]) for e in fab["lignes"]][:2]))
    # ⚠⚠ LES TROIS CHOIX SONT DANS LA MÊME FENÊTRE : sans ça, leur comparaison mesurerait des
    # fenêtres et non des lectures.
    v("... les trois décalages restent dans la fenêtre commune",
      all(e["fenetre_vx"][0] <= x <= e["fenetre_vx"][1] for e in fab["lignes"]
          for x in (e["decalage_raccroche_median_vx"], e["decalage_melange_median_vx"],
                    e["decalage_oracle_median_vx"])),
      str(fab["lignes"][0]["fenetre_vx"]))
    # ⚠⚠⚠ LA MÉDIANE DE SES PROPRES DÉCALAGES EST UN CONTENDANT, PAS UN TÉMOIN : elle a le
    # même déplacement d'ensemble et aucune information par cellule, donc l'écart entre les deux
    # EST ce que la lecture point par point vaut. Sans elle, un simple recentrage du pas se
    # lirait comme une lecture.
    # ⚠⚠ LE REMÈDE EST MESURÉ, PAS PROPOSÉ : le même raccrochage sans son biais d'ensemble.
    # Écrire « il suffirait de le recentrer » sans le mesurer serait publier une piste comme un
    # résultat, ce que ce dépôt a déjà eu à retirer.
    v("... le raccrochage sans son biais d'ensemble est mesuré lui aussi",
      all(e["erreur_raccroche_centre_um"] > 0 for e in fab["lignes"])
      and "retirer_le_biais_ameliore" in fab,
      str([e["erreur_raccroche_centre_um"] for e in fab["lignes"]][:3]))
    v("... et sa propre médiane est mesurée comme contendant",
      all(e["erreur_raccroche_constant_um"] > 0 for e in fab["lignes"]),
      str([e["erreur_raccroche_constant_um"] for e in fab["lignes"]][:3]))
    v("... et les deux accords sont rendus, quel que soit leur signe",
      all(k in fab for k in ("accord_du_raccrochage", "accord_du_melange",
                             "le_raccrochage_lit_quelque_chose")))
    v("le résultat est sérialisable tel quel, sans type qui traîne",
      isinstance(json.dumps(fab), str))
    tampon, souci = io.StringIO(), None
    try:
        with contextlib.redirect_stdout(tampon):
            afficher(fab)
    except Exception as exc:  # noqa: BLE001
        souci = f"{type(exc).__name__}: {exc}"
    v("l'affichage tourne sur ce résultat et va jusqu'à son verdict",
      souci is None and "LIT quelque chose" in tampon.getvalue(),
      souci or f"{len(tampon.getvalue().splitlines())} lignes")
    hors = None
    try:
        mesurer(echantillon=120, minimum=20, corpus=corpus_fabrique(decalage_vx=5000.0),
                volume=volume_fabrique(geometrie_fabriquee(decalage_vx=5000.0)))
    except RuntimeError as exc:
        hors = str(exc)
    v("un objet entier posé hors de la boîte est REFUSÉ, pas rendu vide",
      hors is not None, str(hors))

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def afficher(r: dict) -> None:
    """Le compte rendu lisible d'une mesure."""
    print(f"pas nominal {r['pas_nominal_um']} µm · demi-épaisseur {r['demi_epaisseur_um']} µm · "
          f"{r['paires']} paires, {r['cellules']} cellules\n")
    print(f"{'de':>4} {'vers':>5} {'cell.':>7} {'rho racc.':>10} {'rho mêlé':>9} "
          f"{'sans bouger':>12} {'RACCROCHÉ':>10} {'mélangé':>9} {'oracle':>8}")
    print("-" * 84)
    for e in r["lignes"]:
        ra = e["accord_du_raccrochage"]["rho"]
        rm = e["accord_du_melange"]["rho"]
        print(f"{e['de']:>4} {e['vers']:>5} {e['cellules']:>7} "
              f"{('—' if ra is None else f'{ra:+.3f}'):>10} "
              f"{('—' if rm is None else f'{rm:+.3f}'):>9} "
              f"{e['erreur_sans_bouger_um']:>11.1f}µ {e['erreur_raccrochee_um']:>9.1f}µ "
              f"{e['erreur_melangee_um']:>8.1f}µ {e['erreur_oracle_um']:>7.1f}µ")
    a_, m_ = r["accord_du_raccrochage"], r["accord_du_melange"]
    print(f"\nsur toutes les cellules : rho du RACCROCHAGE {a_['rho']} (p {a_['p']}, n "
          f"{a_['n']}) · rho du MÉLANGE {m_['rho']} (p {m_['p']})")
    print(f"écart médian au décalage de l'oracle : raccroché {r['ecart_median_a_loracle_vx']} "
          f"voxels · mélangé {r['ecart_median_du_melange_vx']} · ne pas bouger "
          f"{r['ecart_median_sans_bouger_vx']}")
    print(f"\nmédianes : sans bouger {r['erreur_sans_bouger_mediane_um']} µm · RACCROCHÉ "
          f"{r['erreur_raccrochee_mediane_um']} · son biais RETIRÉ "
          f"{r['erreur_raccroche_centre_mediane_um']} · sa MÉDIANE seule "
          f"{r['erreur_raccroche_constant_mediane_um']} · mélangé "
          f"{r['erreur_melangee_mediane_um']} · oracle {r['erreur_oracle_mediane_um']} µm")
    print(f"gains : raccrochage {r['gain_du_raccrochage_um']} µm · son recentrage seul "
          f"{r['gain_du_recentrage_seul_um']} · oracle {r['gain_de_loracle_um']} µm — il en "
          f"prend {r['part_du_gain_de_loracle_prise']}")
    print(f"→ RETIRER son biais d'ensemble améliore : "
          f"{'OUI' if r['retirer_le_biais_ameliore'] else 'NON'} "
          f"({r['gain_du_retrait_du_biais_um']:+.1f} µm, "
          f"{r['paires_ou_le_centrage_ameliore']} paires sur {r['paires']})")
    print(f"→ sa lecture PAR CELLULE sert à quelque chose (il bat sa propre médiane) : "
          f"{'OUI' if r['la_lecture_par_cellule_sert'] else 'NON'} "
          f"({r['paires_ou_le_raccrochage_bat_sa_mediane']} paires sur {r['paires']})")
    print(f"→ le raccrochage LIT quelque chose (son accord bat celui du mélange) : "
          f"{'OUI' if r['le_raccrochage_lit_quelque_chose'] else 'NON'}")
    print(f"→ et son erreur bat celle de son mélange : "
          f"{'OUI' if r['le_raccrochage_bat_son_melange'] else 'NON'} "
          f"({r['paires_ou_le_raccrochage_bat_son_melange']} paires sur {r['paires']})")
    print(f"coût : {r['cout']['blocs_telecharges']} blocs, {r['cout']['mebioctets']} Mio")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--echantillon", type=int, default=800)
    p.add_argument("--cote", type=float, default=None)
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(echantillon=a.echantillon, cote=a.cote)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
