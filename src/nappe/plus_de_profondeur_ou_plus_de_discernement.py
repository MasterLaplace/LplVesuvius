"""Plus de profondeur, ou plus de discernement ? — on n'a pas les deux.

⭐⭐⭐⭐ POURQUOI CE FICHIER. `177` construit le troisième énoncé qui sépare une dérive d'une marche
et mesure son domaine : la seule ligne entièrement tenue est le QUART DE TOUR, alors que la bascule
que `176` a lue sur le rouleau vaut **0,0762** fois ce plancher. `R4-P31` nomme la voie la moins
chère pour abaisser ce plancher : la fenêtre de `177` fait un PLI uniquement parce qu'un ajustement
en DEUX SEGMENTS ne décrit qu'une frontière (`175`), et un ajustement AFFINE n'a pas cette limite.
Sur toute la profondeur, le tour ACCUMULÉ est plus grand, donc le plancher devrait descendre.

⭐⭐⭐⭐ IL DESCEND. Et il s'achète exactement là où la question se pose.

⚠⚠⚠ CE QUI ABAISSE LE PLANCHER EST LE TOUR ACCUMULÉ, ET ACCUMULER DU TOUR VEUT DIRE TRAVERSER DES
FRONTIÈRES DE PLI. Un rouleau n'est pas une matière qui tourne : c'est un EMPILEMENT, et `175`
mesure que les 109 couches de la campagne en portent **3,024 plis**. La matière que ce juge
rencontrera au fond n'est donc pas une dérive ni une marche, c'est un ESCALIER — une orientation
constante par morceaux, qui saute à chaque frontière et ne tourne jamais.

⚠⚠⚠ ET C'EST LÀ QUE LE COMPROMIS MORD : un escalier est lu comme une DÉRIVE dès qu'il a plus d'une
marche. Rien n'y tourne, et le juge dit qu'une rotation l'explique. Le plancher gagné en profondeur
est donc payé par l'incapacité à distinguer un empilement d'une rotation — c'est-à-dire par la seule
distinction pour laquelle ce juge existe.

⚠⚠ L'ÉCHELLE DES LARGEURS EST DÉRIVÉE, PAS CHOISIE : un pli, deux plis, trois plis. Le pli vient du
pas et du voxel comme dans `175` et `176`, et trois plis est, à un dixième près, la profondeur
entière du volume de surface — donc l'échelle va de la fenêtre que `175` a dérivée jusqu'à la
profondeur que `R4-P31` propose, sans un barreau inventé.

⚠⚠ ET L'ESCALIER PORTE LE MÊME TOUR TOTAL QUE LA MARCHE ET QUE LA DÉRIVE auxquelles il est comparé,
ses sauts étant posés aux frontières de pli. Sans cette égalité, le verdict mesurerait l'amplitude
au lieu de la FORME, et l'amplitude est ce que `176` a déjà mesuré.

⚠ CE QUE CETTE TRANCHE NE FAIT PAS : elle ne touche toujours pas le vrai rouleau. Le juge n'est pas
devenu lisible ; il a échangé un défaut contre un autre, et pointer l'un ou l'autre sur la matière
rendrait un nombre sans garantie sous un nom qui en promet une.

Usage :
    uv run python src/nappe/plus_de_profondeur_ou_plus_de_discernement.py --verifier
    uv run python src/nappe/plus_de_profondeur_ou_plus_de_discernement.py \\
        --json docs/mesures/plus_de_profondeur_ou_plus_de_discernement.json
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

from la_coupe_cherchee_trouve_t_elle_la_frontiere import (  # noqa: E402
    COUCHES_DE_LA_CAMPAGNE, COUCHES_MINIMALES)
from la_profondeur_tourne_t_elle_ou_bascule_t_elle import (  # noqa: E402
    GRAINE, GRAINES_PAR_CELLULE, LE_QUART_DE_TOUR, PERMUTATIONS, ce_que_le_rouleau_a_rendu,
    lechelle_des_dispersions, lechelle_des_tours, le_verdict, une_courbe_bruitee)

PLIS_DE_LECHELLE = 3


def les_frontieres_de_pli(couches: int, pli: int, phase: int = 0) -> list[int]:
    """Les couches où l'empilement change de pli — les seules qu'un rouleau porte.

    ⚠ Elles sont DÉRIVÉES de la largeur d'un pli, jamais posées : une frontière placée ailleurs
    ferait mesurer un escalier que la matière ne fabrique pas.

    ⚠⚠ UNE FRONTIÈRE QUI NE LAISSE PAS UN SEGMENT DERRIÈRE ELLE N'EN EST PAS UNE, et la borne se
    DÉRIVE de l'estimateur : `174` refuse une tranche de moins de quatre couches, donc un saut à la
    couche 108 d'un volume qui en a 109 ne laisse rien qu'une direction puisse lire. Sans cette
    règle, `109` couches et un pli de `36` rendaient TROIS frontières dont la dernière laissait une
    seule couche, alors que `175` mesure **3,024 plis**.

    ⚠ La PHASE dit où tombe la première frontière. `175` a mesuré que la lecture en dépend, donc
    elle est un paramètre et non zéro : les graines la balayent sur une largeur de pli.
    """
    depart = int(pli) + (int(phase) % int(pli))
    return [k for k in range(depart, int(couches), int(pli))
            if int(couches) - k >= int(COUCHES_MINIMALES)]


def un_escalier(couches: int, tour: float, pli: int, dispersion: float,
                graine: int, phase: int = 0) -> list:
    """Un EMPILEMENT : une orientation constante par morceaux, qui saute à chaque frontière de pli.

    ⭐⭐⭐⭐ RIEN N'Y TOURNE, ET C'EST TOUT L'ÉNONCÉ. Un escalier est fait de marches ; si un juge le
    lit comme une rotation, il se trompe sur le MÉCANISME, et le mécanisme est exactement ce que la
    question du rouleau demande — un empilement de feuilles n'est pas une matière qui pivote.

    ⚠ Le tour TOTAL est celui de la marche et de la dérive auxquelles il est comparé, réparti
    également entre ses sauts : sans cette égalité, le verdict mesurerait l'amplitude.
    """
    fr = les_frontieres_de_pli(int(couches), int(pli), int(phase))
    base = np.zeros(int(couches))
    if fr:
        pas = float(tour) / float(len(fr))
        for k in fr:
            base[k:] += pas
    r = np.random.default_rng(int(graine))
    ecart = (r.normal(0.0, float(dispersion), int(couches)) if dispersion > 0.0
             else np.zeros(int(couches)))
    return [[float((a + b) % 180.0), 0.9] for a, b in zip(base, ecart)]


def lechelle_des_largeurs(pli: int, plis: int = PLIS_DE_LECHELLE) -> list[int]:
    """Un pli, deux plis, trois plis — de la fenêtre de `175` à la profondeur de la campagne.

    ⚠ DÉRIVÉE : le pli vient du pas et du voxel, et trois plis est à un dixième près la profondeur
    entière du volume de surface (`175` : **3,024 plis**). Aucun barreau n'est inventé.
    """
    return [int(pli) * k for k in range(1, int(plis) + 1)]


def le_plancher(largeur: int, couches: int, pli: int, bascule_deg: float,
                temoin_deg: float, graines: int = GRAINES_PAR_CELLULE,
                permutations: int = PERMUTATIONS, graine: int = GRAINE) -> dict:
    """Le tableau tour × dispersion à une largeur donnée, et le plus petit tour entièrement tenu.

    ⚠ C'est exactement le tableau de `177`, à une largeur près : la comparaison entre largeurs n'a
    de sens que si rien d'autre ne bouge.
    """
    tours = lechelle_des_tours(bascule_deg)
    dispersions = lechelle_des_dispersions(temoin_deg)
    # ⚠⚠ UNE LARGEUR EGALE A LA PROFONDEUR VEUT DIRE « PAS DE FENETRE » : decouper une courbe en une
    # seule fenetre et la lire entiere sont la meme chose, et passer par le decoupage ferait
    # dependre le resultat d'un detail d'ecriture.
    fenetre = None if int(largeur) >= int(couches) else int(largeur)
    cellules = []
    for tour in tours:
        for disp in dispersions:
            justes = {}
            for forme in ("marche", "derive"):
                n = 0
                for g in range(int(graines)):
                    c = une_courbe_bruitee(forme, int(couches), tour, disp,
                                           int(graine) + 1000 * g)
                    n += int(le_verdict(c, fenetre, permutations)["gagnant"] == forme)
                justes[forme] = int(n)
            cellules.append({"tour_deg": tour, "dispersion_deg": disp,
                             "marches_justes": justes["marche"],
                             "derives_justes": justes["derive"],
                             "les_deux_formes_sont_rendues": bool(
                                 justes["marche"] == int(graines)
                                 and justes["derive"] == int(graines))})
    tenus = [t for t in tours
             if all(c["les_deux_formes_sont_rendues"] for c in cellules if c["tour_deg"] == t)]
    return {"largeur": int(largeur), "en_plis": int(round(float(largeur) / float(pli))),
            "lit_toute_la_profondeur": bool(fenetre is None),
            "tours": tours, "dispersions": dispersions, "cellules": cellules,
            "le_plus_petit_tour_tenu_deg": (min(tenus) if tenus else None)}


def lescalier(largeur: int, couches: int, pli: int, bascule_deg: float, temoin_deg: float,
              graines: int = GRAINES_PAR_CELLULE, permutations: int = PERMUTATIONS,
              graine: int = GRAINE, tours: list | None = None,
              dispersions: list | None = None) -> dict:
    """Ce que le juge dit d'un EMPILEMENT, à cette largeur — le contrôle qui décide.

    ⭐⭐⭐⭐ SANS CE CONTRÔLE, UN PLANCHER PLUS BAS SE LIRAIT COMME UN GAIN. Un escalier ne tourne
    pas ; le lire « dérive » est une erreur sur le mécanisme, et c'est la seule erreur qui compte
    ici, puisque le rouleau EST un empilement.

    ⚠ L'escalier est lu aux mêmes tours et aux mêmes dispersions que le reste, et le verdict attendu
    est « marche » : ses sauts sont des marches, même quand il y en a plusieurs.
    """
    tours = list(tours) if tours else lechelle_des_tours(bascule_deg)
    dispersions = (list(dispersions) if dispersions is not None
                   else lechelle_des_dispersions(temoin_deg))
    fenetre = None if int(largeur) >= int(couches) else int(largeur)
    cellules, phases = [], set()
    for tour in tours:
        for disp in dispersions:
            compte = {"marche": 0, "derive": 0, "rien": 0}
            for g in range(int(graines)):
                # ⚠⚠ CHAQUE GRAINE PREND UNE PHASE DIFFERENTE, etalees sur une largeur de pli :
                # `175` mesure que la lecture depend du decalage, et balayer la phase ne coute
                # rien puisqu'il faut de toute facon plusieurs tirages par cellule.
                phase = (int(g) * int(pli)) // max(1, int(graines))
                phases.add(int(phase))
                c = un_escalier(int(couches), tour, int(pli), disp,
                                int(graine) + 1000 * g, phase)
                lu = le_verdict(c, fenetre, permutations)["gagnant"]
                compte["rien" if lu is None else lu] += 1
            cellules.append({"tour_deg": tour, "dispersion_deg": disp,
                             "lus_marche": compte["marche"], "lus_derive": compte["derive"],
                             "sans_verdict": compte["rien"]})
    total = sum(c["lus_marche"] + c["lus_derive"] + c["sans_verdict"] for c in cellules)
    return {"largeur": int(largeur), "frontieres": len(les_frontieres_de_pli(couches, pli)),
            "phases_balayees": sorted(phases),
            "cellules": cellules, "lectures": int(total),
            "lus_marche": int(sum(c["lus_marche"] for c in cellules)),
            "lus_derive": int(sum(c["lus_derive"] for c in cellules)),
            "sans_verdict": int(sum(c["sans_verdict"] for c in cellules)),
            # ⚠⚠⚠ « RESTE UN EMPILEMENT » EST UNE MAJORITE, PAS UN ZERO, ET C'EST LA MESURE QUI
            # L'A IMPOSE : meme a un pli un escalier passe parfois pour une rotation. Exiger zero
            # aurait ete une affirmation que rien ne soutient ; ce qui se mesure est le SENS de la
            # lecture dominante, et il bascule d'une largeur a l'autre.
            "lu_plus_souvent_comme_un_empilement": bool(
                sum(c["lus_marche"] for c in cellules)
                > sum(c["lus_derive"] for c in cellules))}


def juger(barreaux: list[dict], bascule_deg: float) -> dict:
    """Le compromis, et s'il existe une largeur qui donne les deux.

    ⚠⚠⚠ LA QUESTION N'EST PAS « LE PLANCHER DESCEND-IL » MAIS « DESCEND-IL SANS COÛTER LA
    DISTINCTION ». Un plancher plus bas obtenu par un juge qui lit un empilement comme une rotation
    ne sert à rien sur un rouleau, puisqu'un rouleau EST un empilement.
    """
    utiles = [b for b in barreaux
              if b["plancher"]["le_plus_petit_tour_tenu_deg"] is not None
              and b["plancher"]["le_plus_petit_tour_tenu_deg"] <= float(bascule_deg)
              and b["escalier"]["lu_plus_souvent_comme_un_empilement"]]
    tenus = [b for b in barreaux if b["plancher"]["le_plus_petit_tour_tenu_deg"] is not None]
    plus_bas = (min(tenus, key=lambda b: b["plancher"]["le_plus_petit_tour_tenu_deg"])
                if tenus else None)
    fidele = [b for b in barreaux if b["escalier"]["lu_plus_souvent_comme_un_empilement"]]
    return {"decidable": bool(tenus),
            "largeurs": [b["largeur"] for b in barreaux],
            "le_plancher_le_plus_bas_deg": (
                plus_bas["plancher"]["le_plus_petit_tour_tenu_deg"] if plus_bas else None),
            "a_la_largeur": (plus_bas["largeur"] if plus_bas else None),
            "il_vaut_le_quart_de_tour_fois": (
                round(plus_bas["plancher"]["le_plus_petit_tour_tenu_deg"] / LE_QUART_DE_TOUR, 4)
                if plus_bas else None),
            "la_bascule_du_rouleau_deg": float(bascule_deg),
            "largeurs_ou_lempilement_reste_lisible": [b["largeur"] for b in fidele],
            "la_plus_large_qui_tient_lempilement": (max(b["largeur"] for b in fidele)
                                                    if fidele else None),
            "le_plancher_descend_avec_la_largeur": bool(
                len(tenus) >= 2
                and all(tenus[k]["plancher"]["le_plus_petit_tour_tenu_deg"]
                        >= tenus[k + 1]["plancher"]["le_plus_petit_tour_tenu_deg"]
                        for k in range(len(tenus) - 1))),
            # ⚠⚠⚠ LA SECONDE BORNE EST INDEPENDANTE DE L'ECHANGE, et elle tient meme si on
            # acceptait de perdre la distinction : le plancher le plus bas ATTEIGNABLE sur ce
            # volume reste au-dessus de la bascule du rouleau. La profondeur disponible est
            # bornee par la campagne elle-meme, qui lit 109 couches.
            "le_plancher_le_plus_bas_vaut_la_bascule_fois": (
                round(plus_bas["plancher"]["le_plus_petit_tour_tenu_deg"] / float(bascule_deg), 4)
                if plus_bas else None),
            "le_plancher_par_largeur_deg": [
                b["plancher"]["le_plus_petit_tour_tenu_deg"] for b in barreaux],
            "les_empilements_lus_rotation_par_largeur": [
                b["escalier"]["lus_derive"] for b in barreaux],
            "les_empilements_lus_marche_par_largeur": [
                b["escalier"]["lus_marche"] for b in barreaux],
            "une_largeur_donne_les_deux": bool(utiles),
            "largeurs_qui_donnent_les_deux": [b["largeur"] for b in utiles]}


def mesurer(graines: int = GRAINES_PAR_CELLULE, permutations: int = PERMUTATIONS,
            plis: int = PLIS_DE_LECHELLE) -> dict:
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    pli = int(round(C.PAS_UM / 2.0 / C.VOXEL_FIN_UM))
    rouleau = ce_que_le_rouleau_a_rendu()
    if rouleau is None:
        return {"message": "la mesure de `176` est absente : son verdict donne l'échelle"}
    couches = int(COUCHES_DE_LA_CAMPAGNE)
    barreaux = []
    for largeur in lechelle_des_largeurs(pli, plis):
        barreaux.append({
            "largeur": int(largeur), "en_plis": int(round(float(largeur) / float(pli))),
            "plancher": le_plancher(largeur, couches, pli, rouleau["bascule_deg"],
                                    rouleau["temoin_deg"], graines, permutations),
            "escalier": lescalier(largeur, couches, pli, rouleau["bascule_deg"],
                                  rouleau["temoin_deg"], graines, permutations)})
    return {"pli_en_couches": pli, "couches": couches, "pas_um": float(C.PAS_UM),
            "voxel_um": float(C.VOXEL_FIN_UM), "permutations": int(permutations),
            "graines_par_cellule": int(graines), "graine": int(GRAINE),
            "le_quart_de_tour_deg": float(LE_QUART_DE_TOUR),
            "frontieres_de_pli": les_frontieres_de_pli(couches, pli),
            "le_rouleau": rouleau, "les_barreaux": barreaux,
            "le_verdict": juger(barreaux, rouleau["bascule_deg"])}


def afficher(r: dict) -> None:
    if "message" in r:
        print(r["message"])
        return
    v = r["le_verdict"]
    print("PLUS DE PROFONDEUR, OU PLUS DE DISCERNEMENT ?")
    print(f"  pli {r['pli_en_couches']} couches sur {r['couches']} · frontières de pli "
          f"{r['frontieres_de_pli']} · {r['permutations']} permutations · "
          f"{r['graines_par_cellule']} graines par cellule")
    print()
    for b in r["les_barreaux"]:
        pl, es = b["plancher"], b["escalier"]
        print(f"  {b['en_plis']} pli(s) — {b['largeur']} couches"
              + ("  (toute la profondeur)" if pl["lit_toute_la_profondeur"] else ""))
        print(f"     plancher {pl['le_plus_petit_tour_tenu_deg']}° · "
              f"un empilement est lu : marche {es['lus_marche']} · dérive {es['lus_derive']} · "
              f"rien {es['sans_verdict']} sur {es['lectures']} — "
              + ("★ il reste un empilement" if es["lu_plus_souvent_comme_un_empilement"]
                 else "✗ il devient une rotation"))
        entete = "  ".join(f"{x:>11.3f}" for x in pl["dispersions"])
        print(f"     {'tour °':>9}   {entete}")
        for tour in pl["tours"]:
            cells = [c for c in pl["cellules"] if c["tour_deg"] == tour]
            ligne = "  ".join(f"{c['marches_justes']:>4}/{c['derives_justes']:<6}" for c in cells)
            marque = "★" if all(c["les_deux_formes_sont_rendues"] for c in cells) else " "
            print(f"     {tour:>9.3f} {marque} {ligne}")
        print()
    print(f"  ★ LE VERDICT · la bascule du rouleau vaut {v['la_bascule_du_rouleau_deg']}°")
    for cle in ("le_plancher_le_plus_bas_deg", "a_la_largeur", "il_vaut_le_quart_de_tour_fois",
                "le_plancher_le_plus_bas_vaut_la_bascule_fois",
                "le_plancher_par_largeur_deg", "le_plancher_descend_avec_la_largeur",
                "largeurs_ou_lempilement_reste_lisible",
                "la_plus_large_qui_tient_lempilement", "une_largeur_donne_les_deux"):
        print(f"     {cle:<48} {v.get(cle)}")


def verifier() -> int:
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        if not ok:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    pli = int(round(C.PAS_UM / 2.0 / C.VOXEL_FIN_UM))
    couches = int(COUCHES_DE_LA_CAMPAGNE)
    rouleau = ce_que_le_rouleau_a_rendu()
    v("la mesure de `176` donne l'échelle", rouleau is not None)
    if rouleau is None:
        print(f"plus_de_profondeur_ou_plus_de_discernement.py   {len(echecs)} ÉCHECS sur {faits}")
        return 1

    # ⚠⚠ L'ECHELLE DES LARGEURS EST DERIVEE : un pli, deux plis, trois plis, et trois plis est a
    # un dixieme pres la profondeur entiere. Un barreau invente ferait mesurer le barreau.
    largeurs = lechelle_des_largeurs(pli, PLIS_DE_LECHELLE)
    v("l'échelle part d'un pli", largeurs[0] == pli, str(largeurs))
    v("l'échelle atteint la profondeur de la campagne",
      0 <= couches - largeurs[-1] < pli, f"{largeurs[-1]} pour {couches} couches")

    # ⭐⭐⭐⭐ UN ESCALIER NE TOURNE PAS, ET C'EST TOUT L'ENONCE : il est constant par morceaux et
    # saute autant de fois qu'il y a de frontieres de pli.
    fr = les_frontieres_de_pli(couches, pli)
    v("les frontières de pli sont celles de la campagne", len(fr) >= 2, str(fr))
    # ⚠⚠ LA BORNE SE DERIVE DE L'ESTIMATEUR, et la regle est exercee sur une entree FABRIQUEE
    # plutot que recalculee : a 112 couches le dernier saut laisse exactement le minimum et il
    # tient, a 111 il en laisse un de moins et il tombe.
    v("une frontière qui laisse le minimum de couches tient",
      les_frontieres_de_pli(int(pli) * 3 + int(COUCHES_MINIMALES), pli)[-1] == int(pli) * 3,
      str(les_frontieres_de_pli(int(pli) * 3 + int(COUCHES_MINIMALES), pli)))
    v("une frontière qui en laisse moins tombe",
      les_frontieres_de_pli(int(pli) * 3 + int(COUCHES_MINIMALES) - 1, pli)[-1] == int(pli) * 2,
      str(les_frontieres_de_pli(int(pli) * 3 + int(COUCHES_MINIMALES) - 1, pli)))
    # ⚠ ET LA PHASE DEPLACE REELLEMENT LES FRONTIERES : `175` mesure que la lecture en depend, donc
    # une phase qui ne deplacerait rien ferait balayer un seul cas en croyant en balayer vingt.
    v("la phase déplace les frontières",
      les_frontieres_de_pli(couches, pli, pli // 2) != fr
      and len(les_frontieres_de_pli(couches, pli, pli // 2)) == len(fr),
      f"{les_frontieres_de_pli(couches, pli, pli // 2)} contre {fr}")
    esc = [x[0] for x in un_escalier(couches, LE_QUART_DE_TOUR, pli, 0.0, GRAINE)]
    v("un escalier a autant de paliers que de frontières, plus un",
      len(set(round(x, 9) for x in esc)) == len(fr) + 1,
      f"{len(set(round(x, 9) for x in esc))} paliers pour {len(fr)} frontières")
    v("un escalier ne tourne pas à l'intérieur d'un pli",
      len(set(round(x, 9) for x in esc[:pli])) == 1, str(sorted(set(esc[:pli]))[:3]))
    # ⚠⚠ ET IL PORTE LE MEME TOUR TOTAL QUE LA MARCHE ET QUE LA DERIVE : sans cette egalite, le
    # verdict mesurerait l'amplitude, que `176` a deja mesuree, au lieu de la FORME.
    for tour in (LE_QUART_DE_TOUR, rouleau["bascule_deg"]):
        tours_lus = [round(max(esc_) - min(esc_), 6) for esc_ in (
            [x[0] for x in un_escalier(couches, tour, pli, 0.0, GRAINE)],
            [x[0] for x in une_courbe_bruitee("marche", couches, tour, 0.0, GRAINE)],
            [x[0] for x in une_courbe_bruitee("derive", couches, tour, 0.0, GRAINE)])]
        v(f"les trois formes portent le même tour à {round(tour, 3)}°",
          len(set(tours_lus)) == 1 and tours_lus[0] == round(float(tour), 6), str(tours_lus))

    # ⚠⚠ UNE LARGEUR EGALE A LA PROFONDEUR VEUT DIRE « PAS DE FENETRE ».
    pl = le_plancher(couches, couches, pli, rouleau["bascule_deg"], rouleau["temoin_deg"], 1, 3)
    v("une largeur qui couvre la profondeur lit sans fenêtre", pl["lit_toute_la_profondeur"])

    # ⭐⭐⭐⭐ LE COMPROMIS, ET C'EST LA MESURE QUI DECIDE : la profondeur ABAISSE le plancher, et
    # elle fait lire un EMPILEMENT comme une rotation. Les deux moities sont exercees sur la meme
    # cellule, celle ou `177` echoue.
    cellule_tour, cellule_disp = 22.5, rouleau["temoin_deg"]
    justes = {}
    for largeur in (pli, couches):
        fenetre = None if largeur >= couches else largeur
        n = 0
        for g in range(7):
            c = une_courbe_bruitee("derive", couches, cellule_tour, cellule_disp,
                                   GRAINE + 1000 * g)
            n += int(le_verdict(c, fenetre, PERMUTATIONS)["gagnant"] == "derive")
        justes[largeur] = n
    v("⭐ la profondeur entière lit une dérive que la fenêtre d'un pli rate",
      justes[couches] > justes[pli],
      f"{justes[couches]}/7 à {couches} couches contre {justes[pli]}/7 à {pli}")

    lus = {}
    for largeur in (pli, couches):
        fenetre = None if largeur >= couches else largeur
        compte = {"marche": 0, "derive": 0, "rien": 0}
        for g in range(7):
            c = un_escalier(couches, cellule_tour, pli, cellule_disp, GRAINE + 1000 * g)
            lu = le_verdict(c, fenetre, PERMUTATIONS)["gagnant"]
            compte["rien" if lu is None else lu] += 1
        lus[largeur] = compte
    v("⭐⭐⭐⭐ à la profondeur entière, un empilement devient une rotation",
      lus[couches]["derive"] > lus[pli]["derive"],
      f"dérive {lus[couches]['derive']}/7 à {couches} couches contre "
      f"{lus[pli]['derive']}/7 à {pli}")
    # ⚠⚠⚠ LE CONTRASTE EST ASSERTE DANS LES DEUX SENS, parce qu'un seul cote serait satisfait par
    # un juge qui dirait toujours la meme chose. Et ce n'est pas un zero : meme a un pli un
    # escalier passe parfois pour une rotation, ce que la mesure a impose contre ma premiere
    # redaction.
    v("⭐ à un pli, un empilement est lu comme un empilement",
      lus[pli]["marche"] > lus[pli]["derive"],
      f"marche {lus[pli]['marche']} · dérive {lus[pli]['derive']} · rien {lus[pli]['rien']}")
    # ⚠⚠⚠ LE BALAYAGE DE PHASE DOIT ETRE EXERCE : une sonde qui le remettait a zero PASSAIT AU
    # VERT, donc rien ne le mesurait. Il est asserte sur une cellule unique, en sortie de la
    # fonction qui le fait, jamais recalcule a cote.
    une = lescalier(pli, couches, pli, rouleau["bascule_deg"], rouleau["temoin_deg"],
                    4, 3, GRAINE, [LE_QUART_DE_TOUR], [0.0])
    v("⭐⭐ les graines balayent la phase sur une largeur de pli",
      len(une["phases_balayees"]) == 4 and max(une["phases_balayees"]) < pli
      and min(une["phases_balayees"]) == 0, str(une["phases_balayees"]))

    v("⭐⭐⭐⭐ ... et à la profondeur entière il est lu comme une rotation",
      lus[couches]["derive"] > lus[couches]["marche"],
      f"marche {lus[couches]['marche']} · dérive {lus[couches]['derive']} · "
      f"rien {lus[couches]['rien']}")

    nom = "plus_de_profondeur_ou_plus_de_discernement.py"
    if echecs:
        print(f"{nom}   {len(echecs)} ÉCHECS sur {faits}")
        for e in echecs:
            print(f"   ✗ {e}")
        return 1
    print(f"{nom:<46} ALL PASS (0 failures, {faits} checks)")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    p.add_argument("--graines", type=int, default=GRAINES_PAR_CELLULE)
    p.add_argument("--permutations", type=int, default=PERMUTATIONS)
    p.add_argument("--plis", type=int, default=PLIS_DE_LECHELLE)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(a.graines, a.permutations, a.plis)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
