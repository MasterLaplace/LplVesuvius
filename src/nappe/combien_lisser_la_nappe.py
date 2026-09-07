#!/usr/bin/env python3
"""Combien faut-il lisser la NAPPE entre deux bras ? Choisi HORS ÉCHANTILLON.

⚠⚠⚠ POURQUOI CE FICHIER EXISTE. `la_portee_du_raccrochage` mesure que lisser la nappe entre deux
bras rend 3 à 9 µm sur une marche, avec le voisinage **déjà déployé** : demi-largeur un, une
passe. Ce réglage n'a jamais été balayé **sur une marche** — la tranche qui l'a balayé le faisait
sur **un** pas, où elle a conclu que la largeur s'épuise à 3×3. Une marche est un autre régime :
ce qu'un pas gagne à lisser peu, huit bras peuvent le perdre.

⚠⚠⚠ ET LE BALAYAGE NE PEUT PAS CHOISIR SUR CE QU'IL JUGE. Essayer sept étages et publier le
meilleur, c'est publier le hasard du meilleur tirage. Chaque ancre est donc jugée à l'étage que
les **autres** ancres ont préféré — `lecart_apparie.choisir_hors_echantillon`, l'instrument que
`le_gabarit_lu_ailleurs` et `la_direction_du_pas` utilisent déjà, et pour la même raison.

⭐⭐ CE QUE CE FICHIER PEUT DIRE, et rien de plus : à l'étage que les autres ancres choisissent,
une ancre fait-elle mieux qu'à l'étage **déployé** (1, une passe) et qu'**au brut** (aucun
lissage) ? Trois colonnes, appariées ancre par ancre.

⚠ Le pas normal ne lit PAS le volume : un balayage de cette famille ne coûte donc que les grilles
de spires, ce qui est ce qui le rend faisable. Seuls `rien` et `rien_lisse` sont parcourus.

Usage :
    uv run python src/nappe/combien_lisser_la_nappe.py --verifier
    uv run python src/nappe/combien_lisser_la_nappe.py --cote 960 --ancres 5 \\
        --json docs/mesures/combien_lisser_la_nappe.json
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "commun"))
from la_lissite_de_la_feuille import etages  # noqa: E402
from la_portee_du_raccrochage import mesurer as marche_depuis  # noqa: E402
from le_corpus_des_spires import corpus_fabrique, volume_fabrique  # noqa: E402
from lecart_apparie import choisir_hors_echantillon, ecart_apparie, tranche  # noqa: E402

# ⚠⚠ LES DEUX SEULS MARCHEURS DONT CE BALAYAGE A BESOIN. Le pas normal ne lit pas le volume et le
# lissage est de l'arithmétique de grille : faire marcher les six autres à chaque étage coûterait
# des lectures pour des colonnes que ce fichier ne regarde pas.
MARCHEURS = ("rien", "rien_lisse")
DEPLOYE = (1, 1)
BRUT = (0, 0)
# ⚠⚠⚠ LA FAMILLE VA AU-DELÀ DE CELLE D'UN PAS, et c'est une correction de méthode plutôt qu'un
# élargissement d'humeur. `la_lissite_de_la_feuille` s'arrête à une demi-largeur de huit parce
# qu'un PAS s'y épuise ; sur une marche, l'optimum est tombé exactement sur ce dernier étage —
# c'est-à-dire au BORD du balayage, et un optimum au bord est un plancher de ce qu'on a essayé
# et non une propriété de la matière. C'est la faute que le balayage du cône de directions a déjà
# payée. La famille s'étend donc jusqu'à ce que l'optimum soit INTÉRIEUR, ou que le balayage dise
# qu'il ne l'est pas.
DEMI_LARGEURS = (1, 2, 4, 8, 16, 32)


def cout_en_bras_perdus(portee: int, bras: int) -> float:
    """Ce que coûte un étage EN BRAS : combien de bras la marche n'atteint pas.

    ⚠⚠⚠ POURQUOI CE SECOND COÛT EXISTE, et c'est une correction. Le premier coût est la médiane
    des erreurs par bras — or cette médiane inclut les bras où la marche est **DÉJÀ PERDUE**.
    Passer de 120 à 70 µm sur une marche perdue n'est pas un progrès : les deux sont au-delà de
    la demi-feuille, et rien en aval ne peut s'en servir. Un réglage choisi sur cette grandeur
    est donc choisi sur la qualité de ses échecs.

    ⚠⚠ Ce coût-ci répond à la question du BUT : combien de spires la marche traverse. Il est
    grossier — c'est un entier — et c'est précisément pourquoi les deux sont publiés : quand ils
    se contredisent, c'est le second qui parle du but, et le premier qui a l'air d'un résultat.
    """
    return float(max(0, int(bras) - int(portee)))


def cout_dun_etage(erreurs: list[float]) -> float:
    """Ce que coûte un étage sur une marche : la MÉDIANE de ses erreurs par bras.

    ⚠⚠ LA MÉDIANE, PAS LA SOMME NI LA DERNIÈRE. Une somme laisse le bras dont l'erreur varie le
    plus décider ; la dernière n'est qu'un bras, et c'est celui qui a le plus de chances d'être
    déjà perdu. La médiane est aussi la statistique par laquelle chaque bras est résumé, donc
    ajuster et juger sur la même grandeur.

    ⚠ Une marche sans bras coûte l'infini : c'est un étage qui n'a pas pu marcher, et lui donner
    un coût fini le rendrait choisissable.
    """
    return float(np.median(erreurs)) if erreurs else float("inf")


def mesurer(ancres: int = 5, graine: int = 42, minimum: int = 30, cache_actif: bool = True,
            cote: float | None = None, bras_max: int = 8,
            corpus: dict | None = None, volume=None,
            familles=None) -> dict:
    """Le coût de chaque étage de lissage, à chaque ancre, puis le choix hors échantillon."""
    # ⚠ La famille d'étages est celle de `la_lissite_de_la_feuille`, déclarée une seule fois :
    # deux échelles de lissage finiraient par ne plus s'accorder sur ce que « x2 » veut dire.
    etage_liste = (etages(demi_largeurs=DEMI_LARGEURS) if familles is None
                   else list(familles))
    # ⚠⚠⚠ LE CORPUS EST CHARGÉ UNE FOIS, et c'est autant une question de justesse que de coût :
    # trente-cinq marches qui rechargeraient chacune l'index compareraient des étages sur des
    # lectures séparées du même corpus, et rien ne garantirait qu'elles rendent la même chose.
    # Une seule lecture, un seul corpus, et tous les étages jugés dessus.
    if corpus is None:
        from le_corpus_des_spires import corpus_publie  # noqa: PLC0415

        corpus = corpus_publie()
    reglages = [(int(d), int(n)) for _, d, n in etage_liste]
    noms = [nom for nom, _, _ in etage_liste]

    lignes, soucis = [], []
    for k in range(max(1, int(ancres))):
        couts, portees, parts = [], [], []
        rupture = None
        for d, n in reglages:
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    r = marche_depuis(graine=graine, minimum=minimum, cache_actif=cache_actif,
                                      cote=cote, bras_max=bras_max, corpus=corpus,
                                      volume=volume, decalage_ancre=k,
                                      lissage_nappe=(max(1, d), n), marcheurs=MARCHEURS)
            except RuntimeError as exc:
                rupture = str(exc)
                break
            ligne = next(x for x in r["lignes"] if x["marcheur"] == "rien_lisse")
            couts.append(cout_dun_etage(ligne["erreurs_um"]))
            portees.append(ligne["portee"])
            # ⚠⚠ CE QUE LA FENÊTRE FAIT RÉELLEMENT : au premier bras, quelle part de la nappe
            # a été lissée. Une fenêtre refusée partout ne lisse rien, et son coût ne mesure
            # alors plus le lissage mais son absence.
            parts.append(ligne["parts_lissees"][0] if ligne["parts_lissees"] else 0.0)
        if rupture is not None:
            # ⚠ Une ancre trop haute n'a plus de spire devant elle : fin normale du balayage,
            # comptée et nommée plutôt qu'avalée.
            soucis.append(dict(decalage=k, raison=rupture))
            break
        lignes.append(dict(decalage=k, ancre=r["ancre"], bras=len(r["spires_visees"]),
                           forme_grille=r["forme_grille"],
                           couts_um=[round(x, 1) for x in couts], portees=portees,
                           parts_lissees=[round(x, 3) for x in parts]))
    if len(lignes) < 2:
        raise RuntimeError(f"il faut au moins deux ancres pour choisir hors échantillon "
                           f"({len(lignes)} obtenue(s)) : {soucis}")

    # ⚠⚠⚠ LE CHOIX EST FAIT SUR LES AUTRES ANCRES, jamais sur celle qui le juge. `valeurs` est
    # l'INDICE de l'étage : la fonction ne sait pas ce qu'est un réglage, et c'est ce qui lui
    # permet de servir un facteur d'échelle, une rotation et un lissage sans trois copies.
    courbes = [np.array(x["couts_um"], dtype=float) for x in lignes]
    valeurs = np.arange(len(reglages), dtype=float)
    dedans, pris, couts_hors = choisir_hors_echantillon(courbes, valeurs)
    # ⚠⚠⚠ ET LE MÊME CHOIX SUR LE COÛT EN BRAS, qui est celui du but. Deux coûts, deux choix,
    # et c'est leur DÉSACCORD qui est le résultat quand il y en a un.
    en_bras = [np.array([cout_en_bras_perdus(pp, x["bras"]) for pp in x["portees"]],
                        dtype=float) for x in lignes]
    dedans_b, pris_b, couts_b = choisir_hors_echantillon(en_bras, valeurs)
    i_dep, i_brut = reglages.index(DEPLOYE), reglages.index(BRUT) if BRUT in reglages else 0
    for x, j, c in zip(lignes, pris_b, couts_b):
        x["etage_choisi_en_bras"] = noms[int(j)]
        x["bras_perdus_hors_echantillon"] = int(c)
        x["portee_hors_echantillon_en_bras"] = x["portees"][int(j)]
    for x, j, c in zip(lignes, pris, couts_hors):
        x["etage_choisi_par_les_autres"] = noms[int(j)]
        x["cout_hors_echantillon_um"] = round(c, 1)
        x["cout_deploye_um"] = x["couts_um"][i_dep]
        x["cout_brut_um"] = x["couts_um"][i_brut]
        x["portee_hors_echantillon"] = x["portees"][int(j)]
        x["portee_deployee"] = x["portees"][i_dep]
        x["portee_brute"] = x["portees"][i_brut]

    hors = [x["cout_hors_echantillon_um"] for x in lignes]
    dep = [x["cout_deploye_um"] for x in lignes]
    brut = [x["cout_brut_um"] for x in lignes]
    return dict(
        etages=noms, reglages=[list(x) for x in reglages], ancres=len(lignes),
        lignes=lignes, ancres_refusees=soucis,
        etage_ajuste_sur_tout=noms[int(dedans)],
        etage_ajuste_sur_tout_en_bras=noms[int(dedans_b)],
        etages_choisis_en_bras=[x["etage_choisi_en_bras"] for x in lignes],
        # ⚠⚠⚠ LE COÛT EN BRAS EST GROSSIER, et il faut le dire : si la plupart des ancres ont la
        # même portée à tous les étages, sa médiane ne peut RIEN discriminer et son « choix »
        # est le premier étage de la liste. Ce compte le mesure au lieu de le supposer.
        ancres_dont_la_portee_ne_bouge_jamais=[x["decalage"] for x in lignes
                                               if len(set(x["portees"])) == 1],
        # ⚠⚠⚠ UN OPTIMUM AU BORD DU BALAYAGE EST UN PLANCHER DE CE QU'ON A ESSAYÉ, jamais une
        # propriété de la matière. Ce drapeau est publié à côté du choix, et il vaut mieux qu'il
        # soit faux : vrai, il dit que la famille est trop courte et que le nombre retenu ne
        # tranche rien.
        loptimum_est_au_bord=bool(any(int(j) in (0, len(reglages) - 1) for j in pris)),
        etages_au_bord=[noms[int(j)] for j in pris if int(j) in (0, len(reglages) - 1)],
        parts_lissees_par_etage=[
            round(float(np.median([x["parts_lissees"][j] for x in lignes])), 3)
            for j in range(len(reglages))],
        etages_choisis_par_les_autres=[x["etage_choisi_par_les_autres"] for x in lignes],
        # ⭐⭐⭐ LES DEUX SEULES QUESTIONS QUE CE BALAYAGE A LE DROIT DE POSER, et les deux sont
        # appariées ancre par ancre : le choix hors échantillon bat-il l'étage DÉPLOYÉ, et
        # bat-il le BRUT ? La première dit s'il y avait quelque chose à gagner en réglant ; la
        # seconde redit, sur un balayage entier, que lisser vaut mieux que ne pas lisser.
        ecart_au_deploye=ecart_apparie(hors, dep),
        le_reglage_bat_le_deploye=bool(tranche(ecart_apparie(hors, dep))),
        ecart_au_brut=ecart_apparie(hors, brut),
        le_reglage_bat_le_brut=bool(tranche(ecart_apparie(hors, brut))),
        # ⚠⚠ ET LE DÉPLOYÉ CONTRE LE BRUT, sur le même appariement : c'est le résultat de la
        # tranche précédente, refait ici sur les mêmes ancres. S'il ne se reproduisait pas, ce
        # serait le balayage qu'il faudrait suspecter, pas la tranche.
        ecart_du_deploye_au_brut=ecart_apparie(dep, brut),
        le_deploye_bat_le_brut=bool(tranche(ecart_apparie(dep, brut))),
        # ⭐⭐⭐ LA SEULE PORTE QUI COMPTE, et elle est fermée par défaut. Un balayage n'autorise à
        # changer le réglage déployé que si TOUT tient ensemble : l'optimum n'est pas au bord de
        # la famille, le gain sur l'erreur tranche, ET aucune ancre ne voit sa PORTÉE diminuer.
        # Sans la dernière condition, un gain médian sur des marches déjà perdues suffirait à
        # déplacer un réglage qui fait s'effondrer la seule marche encore vivante.
        ancres_dont_la_portee_empire=[
            x["decalage"] for x in lignes
            if x["portee_hors_echantillon"] < x["portee_deployee"]],
        le_balayage_autorise_un_changement=bool(
            not any(int(j) in (0, len(reglages) - 1) for j in pris)
            and tranche(ecart_apparie(hors, dep))
            and not [x for x in lignes
                     if x["portee_hors_echantillon"] < x["portee_deployee"]]))


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # ⚠⚠ LE COÛT D'UN ÉTAGE EST UNE MÉDIANE, et un étage qui n'a pas marché coûte l'infini —
    # sans quoi il serait choisissable, et « le meilleur étage » serait celui qui a échoué.
    v("le coût d'un étage est la médiane de ses erreurs par bras",
      cout_dun_etage([10.0, 20.0, 90.0]) == 20.0, str(cout_dun_etage([10.0, 20.0, 90.0])))
    v("... et une marche sans bras coûte l'infini, donc n'est jamais choisie",
      cout_dun_etage([]) == float("inf"))
    # ⚠ La famille vient de `la_lissite_de_la_feuille`, et elle contient l'étage DÉPLOYÉ et le
    # BRUT : sans ces deux-là, le balayage n'aurait rien contre quoi se juger.
    regs = [(d, n) for _, d, n in etages()]
    v("la famille d'étages contient le brut ET l'étage déployé",
      BRUT in regs and DEPLOYE in regs, str(regs))

    # ⚠⚠⚠ LE CHEMIN QUI PRODUIT LE NOMBRE PUBLIÉ, HORS LIGNE.
    from le_corpus_des_spires import geometrie_fabriquee  # noqa: PLC0415

    c, vol = corpus_fabrique(), volume_fabrique(geometrie_fabriquee())
    fab = mesurer(ancres=3, minimum=20, corpus=c, volume=vol)
    v("la mesure tourne de bout en bout sur des matières fabriquées",
      fab["ancres"] >= 2, f"{fab['ancres']} ancres · étages {fab['etages']}")
    v("... chaque ancre publie un coût par étage",
      all(len(x["couts_um"]) == len(fab["etages"]) for x in fab["lignes"]),
      str([len(x["couts_um"]) for x in fab["lignes"]]))
    # ⚠⚠⚠ HORS ÉCHANTILLON VEUT DIRE QUE LE CHOIX NE VOIT PAS LE CAS QUI LE JUGE. Le contrôle
    # qui le prouve : le coût retenu pour un cas n'est JAMAIS meilleur que le minimum de ses
    # propres coûts, et il est presque toujours pire — sinon le choix aurait triché.
    v("... le coût hors échantillon n'est jamais meilleur que le meilleur du cas lui-même",
      all(x["cout_hors_echantillon_um"] >= min(x["couts_um"]) - 1e-9 for x in fab["lignes"]),
      str([(x["cout_hors_echantillon_um"], min(x["couts_um"])) for x in fab["lignes"]]))
    # ⚠⚠ ET LE CHOIX D'UN CAS EST CELUI DES AUTRES : refait à la main ici, parce qu'un contrôle
    # qui relirait la sortie de la fonction ne testerait que sa cohérence avec elle-même.
    pile = np.stack([np.array(x["couts_um"], dtype=float) for x in fab["lignes"]])
    attendu = [fab["etages"][int(np.argmin(np.median(np.delete(pile, i, axis=0), axis=0)))]
               for i in range(len(fab["lignes"]))]
    v("... et l'étage retenu pour un cas est bien celui que les AUTRES préfèrent",
      fab["etages_choisis_par_les_autres"] == attendu,
      f"{fab['etages_choisis_par_les_autres']} contre {attendu}")
    # ⚠⚠⚠ LE CONTRÔLE QUI EMPÊCHE DE REFAIRE LA FAUTE DU CÔNE : un optimum au bord doit être
    # SIGNALÉ, pas publié comme un résultat. Le drapeau est vérifié dans les deux sens.
    court = mesurer(ancres=3, minimum=20, corpus=c, volume=vol,
                    familles=[("brut", 0, 0), ("median_1", 1, 1)])
    v("... un optimum au bord du balayage est SIGNALÉ",
      court["loptimum_est_au_bord"] and court["etages_au_bord"],
      str(court["etages_au_bord"]))
    # ⚠⚠ LA PART LISSÉE DÉCROÎT AVEC LA LARGEUR, et ce n'est pas un ornement : c'est le nombre
    # qui distingue « cette fenêtre gagne » de « cette fenêtre ne s'applique plus ». Les étages
    # de largeur occupent les indices 1 à len(DEMI_LARGEURS) ; le brut est à zéro et les étages
    # itérés sont après, à largeur constante, donc ils ne font pas partie de cette monotonie.
    nl = len(DEMI_LARGEURS)
    larges = fab["parts_lissees_par_etage"][1:1 + nl]
    v("... la part de nappe lissée est publiée, et décroît quand la fenêtre s'élargit",
      len(fab["parts_lissees_par_etage"]) == len(fab["etages"])
      and fab["parts_lissees_par_etage"][0] == 0.0
      and larges == sorted(larges, reverse=True),
      str(dict(zip(fab["etages"], fab["parts_lissees_par_etage"]))))
    # ⚠⚠⚠ ET UN ÉTAGE QUI NE LISSE RIEN NE PEUT PAS ÊTRE MEILLEUR QUE LE BRUT : il EST le brut.
    # Ce contrôle attrape le mode de panne qui rendrait tout le balayage faux — une fenêtre
    # refusée partout dont le coût différerait du brut voudrait dire que le coût mesure autre
    # chose que ce que la fenêtre a fait.
    faux = [(fab["etages"][j], fab["parts_lissees_par_etage"][j], x["couts_um"][j],
             x["couts_um"][0])
            for x in fab["lignes"] for j in range(len(fab["etages"]))
            if fab["parts_lissees_par_etage"][j] == 0.0 and j > 0
            and abs(x["couts_um"][j] - x["couts_um"][0]) > 1e-6]
    v("... et un étage qui ne lisse RIEN coûte exactement ce que coûte le brut",
      not faux, str(faux[:2]))
    # ⚠⚠ LE COÛT EN BRAS EST EXERCÉ À PART : il ne se lit pas dans le premier, et une marche qui
    # atteint tous ses bras ne perd rien.
    v("le coût en bras est le nombre de bras que la marche n'atteint pas",
      cout_en_bras_perdus(5, 8) == 3.0 and cout_en_bras_perdus(8, 8) == 0.0)
    v("... et une portée aberrante ne rend jamais un coût négatif",
      cout_en_bras_perdus(9, 8) == 0.0)
    # ⭐⭐⭐ LA PORTE EST FERMÉE PAR DÉFAUT, et le contrôle vérifie qu'une portée qui empire la
    # ferme — c'est la condition sans laquelle un gain médian sur des marches déjà perdues
    # suffirait à déplacer le réglage qui tourne.
    v("... et une ancre dont la portée EMPIRE ferme la porte du changement",
      not (fab["ancres_dont_la_portee_empire"]
           and fab["le_balayage_autorise_un_changement"]),
      f"empire {fab['ancres_dont_la_portee_empire']} · autorise "
      f"{fab['le_balayage_autorise_un_changement']}")
    v("... les trois écarts appariés sont publiés avec leur intervalle",
      all(fab[k] and fab[k]["intervalle_um"] is not None
          for k in ("ecart_au_deploye", "ecart_au_brut", "ecart_du_deploye_au_brut")),
      str(fab["ecart_au_deploye"]))
    v("... le résultat est sérialisable tel quel, sans type qui traîne",
      isinstance(json.dumps(fab), str))
    souci = None
    try:
        afficher(fab)
    except Exception as exc:  # noqa: BLE001
        souci = f"{type(exc).__name__}: {exc}"
    v("... et l'affichage tourne sur ce résultat", souci is None, str(souci))
    # ⚠⚠ UNE SEULE ANCRE EST REFUSÉE, pas rendue : avec un cas il n'y a aucun « autre cas », donc
    # le réglage serait noté sur sa propre copie. Rendre un résultat là serait publier un choix
    # dans l'échantillon sous une étiquette qui dit le contraire.
    seule = None
    try:
        mesurer(ancres=1, minimum=20, corpus=c, volume=vol)
    except RuntimeError as exc:
        seule = str(exc)
    v("une seule ancre est REFUSÉE : hors échantillon demande un autre cas",
      seule is not None, str(seule))

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def afficher(r: dict) -> None:
    """Le compte rendu lisible : une ligne par ancre, les étages en colonnes."""
    print(f"{r['ancres']} ancre(s) · étages : {', '.join(r['etages'])}")
    print()
    entete = " ".join(f"{n[:9]:>10}" for n in r["etages"])
    print(f"{'ancre':>6} {entete} {'choisi par les autres':>24} {'coût hors éch.':>15}")
    print("-" * (7 + 11 * len(r["etages"]) + 42))
    for x in r["lignes"]:
        cases = " ".join(f"{c:>10.1f}" for c in x["couts_um"])
        print(f"{x['ancre']:>6} {cases} {x['etage_choisi_par_les_autres']:>24} "
              f"{x['cout_hors_echantillon_um']:>15.1f}")
    print()
    print(f"{'part lissée':>6} " + " ".join(f"{g:>10.2f}" for g in
                                            r["parts_lissees_par_etage"]))
    print()
    print(f"→ étage ajusté sur TOUTES les ancres (donc DANS l'échantillon, publié pour "
          f"comparaison seulement) : {r['etage_ajuste_sur_tout']}")
    print(f"→ {'⚠⚠⚠ ' if r['loptimum_est_au_bord'] else ''}l'optimum est-il AU BORD du "
          f"balayage : {'OUI — la famille est trop courte' if r['loptimum_est_au_bord'] else 'non'}"
          + (f" ({r['etages_au_bord']})" if r["etages_au_bord"] else ""))
    for cle, nom in (("ecart_au_deploye", "le réglage hors échantillon contre le DÉPLOYÉ"),
                     ("ecart_au_brut", "le réglage hors échantillon contre le BRUT"),
                     ("ecart_du_deploye_au_brut", "le DÉPLOYÉ contre le BRUT")):
        e = r[cle]
        print(f"→ {nom} : {e['ecart_median_um']:+.1f} µm · {e['pas_ameliores']}/{e['pas']} "
              f"ancres · {e['intervalle_um']} · "
              f"{'TRANCHE' if tranche(e) else 'ne tranche pas'}")
    print(f"→ choix sur le coût EN BRAS (celui du but) : "
          f"{r['etages_choisis_en_bras']} · ajusté sur tout : "
          f"{r['etage_ajuste_sur_tout_en_bras']}")
    if r["ancres_dont_la_portee_ne_bouge_jamais"]:
        print(f"→ ⚠⚠ le coût en bras ne discrimine RIEN aux ancres "
              f"{r['ancres_dont_la_portee_ne_bouge_jamais']} : leur portée est la même à tous "
              "les étages")
    if r["ancres_dont_la_portee_empire"]:
        print(f"→ ⚠⚠⚠ la PORTÉE EMPIRE aux ancres {r['ancres_dont_la_portee_empire']} avec "
              "l'étage que les autres ont choisi")
    print(f"→ {'⭐⭐⭐' if r['le_balayage_autorise_un_changement'] else '⛔'} le balayage "
          f"autorise-t-il à changer le réglage déployé : "
          f"{'OUI' if r['le_balayage_autorise_un_changement'] else 'NON'}")
    for x in r["ancres_refusees"]:
        print(f"→ ancre {x['decalage']} refusée : {x['raison']}")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--ancres", type=int, default=5)
    p.add_argument("--cote", type=float, default=None)
    p.add_argument("--bras-max", type=int, default=8)
    p.add_argument("--minimum", type=int, default=30)
    p.add_argument("--sans-cache", action="store_true")
    p.add_argument("--json", type=Path, default=None)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(ancres=a.ancres, minimum=a.minimum, cache_actif=not a.sans_cache,
                cote=a.cote, bras_max=a.bras_max)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False))
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
