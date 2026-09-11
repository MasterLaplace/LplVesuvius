#!/usr/bin/env python3
"""La cécité est-elle absorbante — et donne-t-elle au marcheur l'arrêt qu'il n'a jamais eu ?

⚠⚠⚠ POURQUOI CE FICHIER EXISTE. `113` a levé le plafond de six pas à vingt et a mesuré que **rien
n'arrête une marche** : 28 sur 28 au plafond, zéro sortie de volume. La portée est donc restée
**entièrement censurée**, et c'est le mur que la porte `R4-P20` nomme : un plafond n'est pas une
portée, c'est un budget. `115` a ensuite trouvé qu'un pas sur trois **ne lit rien**. La question
devient : la cécité est-elle l'arrêt qui manquait ?

⭐⭐⭐⭐ **LA RÉPONSE DÉCIDE DE CE QU'ON LIVRE**, et les deux issues n'ont pas le même remède. Si la
cécité est **absorbante** — une marche qui cesse de lire ne relit plus jamais — alors s'arrêter
dessus ne coûte rien, et la portée devient mesurable pour les marches concernées, pour la première
fois de ce dépôt. Si elle est **transitoire**, s'arrêter tronquerait de bonnes marches, et le
remède n'est pas de s'arrêter mais de traverser.

⚠⚠ **ET IL Y A UN CONTRÔLE SANS LEQUEL RIEN N'EST PROUVÉ.** Avec des marches qui portent beaucoup
de pas aveugles, la contiguïté arrive par hasard : une marche dont dix-neuf pas sur vingt sont
aveugles a peu d'occasions de faire revenir la vue. Les positions aveugles sont donc **permutées à
l'intérieur de chaque marche**, à compte constant, et l'observé doit être extrême contre ce
tirage. Sans ce témoin, « la cécité est absorbante » ne dirait que « la cécité est fréquente ».

⚠ **Ce que ce fichier NE tranche PAS** : pourquoi le volume cesse de répondre (`R4-P22`), ni si
une autre direction au même endroit aurait lu quelque chose. La course n'a gardé que la direction
choisie, pas les candidates ; cette question-là demande une re-course, donc des lectures distantes.

⚠ Aucune lecture distante ici : tout se calcule sur les 560 étapes que `113` a gardées.

  uv run python src/nappe/la_cecite_est_elle_absorbante.py --verifier
  uv run python src/nappe/la_cecite_est_elle_absorbante.py \
      --json docs/mesures/la_cecite_est_elle_absorbante.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
COURSE = RACINE / "docs" / "mesures" / "jusquou_va_t_il_si_on_le_laisse.json"

from ce_qui_porte_le_taux import est_aveugle  # noqa: E402
"""⚠⚠ La définition d'un pas aveugle est **importée**, jamais recopiée. Deux définitions de « ce
pas n'a rien lu » finiraient par ne pas s'accorder, et les deux tranches publieraient alors des
comptes différents du même phénomène sans que rien ne le dise."""

PLAFOND = 20
"""Le plafond de `113`, relu ici pour distinguer « la marche s'est arrêtée » de « le budget a été
épuisé ». ⚠ Il n'est pas deviné : la course le porte dans `pas_max`, et `marches()` le vérifie."""


def marches(course: dict) -> list[dict]:
    """Une entrée par marche : son rayon, et la suite de ses pas dans l'ordre.

    ⚠ L'ORDRE est tout ce qui compte ici, alors que `115` n'avait besoin que de comptes. Un pas
    est donc gardé avec son rang, sa cécité et sa longueur parcourue cumulée — et rien d'autre.
    """
    out = []
    for ligne in course.get("lignes", []):
        for cel in ligne.get("detail", []):
            etapes = [e for e in cel.get("etapes", []) if "confirme" in e]
            if not etapes:
                continue
            out.append({
                "rayon_mm": ligne.get("rayon_mm"),
                "pas": len(etapes),
                "aveugles": [est_aveugle(e) for e in etapes],
                "confirmes": [bool(e.get("confirme")) for e in etapes],
                "parcouru_um": [float(e.get("parcouru_um", 0.0)) for e in etapes]})
    return out


def transitions(par_marche: list[dict]) -> dict:
    """Ce qui suit un pas aveugle, et ce qui suit un pas voyant.

    ⭐⭐⭐ Le nombre qui décide est `aveugle_puis_voyant` : c'est **le retour de la vue**. S'il vaut
    zéro, l'état aveugle n'a aucune sortie observée, et c'est ce qu'« absorbant » veut dire.

    ⚠ Les transitions sont comptées **à l'intérieur d'une marche**, jamais d'une marche à la
    suivante : deux marches n'ont ni le même départ ni la même matière, donc un enchaînement entre
    elles ne serait pas une transition mais une concaténation.
    """
    c = {"voyant_puis_voyant": 0, "voyant_puis_aveugle": 0,
         "aveugle_puis_aveugle": 0, "aveugle_puis_voyant": 0}
    for m in par_marche:
        for a, b in zip(m["aveugles"], m["aveugles"][1:]):
            c[("aveugle" if a else "voyant") + "_puis_" + ("aveugle" if b else "voyant")] += 1
    return c


def la_cecite_est_elle_absorbante(par_marche: list[dict]) -> dict:
    """Une marche qui a cessé de lire relit-elle ?

    ⭐⭐⭐⭐ C'EST LE TEST. Il porte sur les seules marches qui ont **au moins un pas aveugle**, et
    il compte celles où un pas voyant apparaît **après** le premier aveugle.

    ⚠⚠ Une marche dont le seul pas aveugle est le **dernier** n'a aucune occasion de relire : elle
    ne peut donc pas réfuter l'absorption et elle est comptée à part (`sans_occasion`). La garder
    dans le compte ferait passer pour une confirmation une marche qui n'avait rien à dire — et
    c'est ce qui rend le verdict faux quand toutes les marches sont dans ce cas.

    ⚠ En revanche une marche **entièrement** aveugle a bien des occasions : dix-neuf pas de suite
    où la vue aurait pu revenir et n'est pas revenue. C'est une preuve, pas une abstention.
    """
    concernees = [m for m in par_marche if any(m["aveugles"])]
    if not concernees:
        return {"decidable": False, "pourquoi": "aucune marche ne porte de pas aveugle"}
    retours, sans_occasion = 0, 0
    for m in concernees:
        i = m["aveugles"].index(True)
        apres = m["aveugles"][i + 1:]
        if not apres:
            sans_occasion += 1
        elif not all(apres):
            retours += 1
    avec_occasion = len(concernees) - sans_occasion
    return {
        "decidable": True,
        "marches": len(par_marche),
        "marches_avec_un_pas_aveugle": len(concernees),
        "marches_ou_la_vue_revient": retours,
        "marches_sans_occasion_de_revenir": sans_occasion,
        "marches_avec_occasion": avec_occasion,
        "transitions": transitions(par_marche),
        # ⭐⭐⭐⭐ Le verdict, et il exige qu'il y ait eu des occasions : « zéro retour sur zéro
        # occasion » est vrai et ne dit rien.
        "la_cecite_est_absorbante": bool(avec_occasion > 0 and retours == 0)}


def temoin_de_labsorption(par_marche: list[dict], tirages: int = 2000,
                          graine: int = 1161) -> dict:
    """Zéro retour de la vue, est-ce que le hasard le rendrait aussi ?

    ⭐⭐⭐ LE CONTRÔLE QUI REND LE RÉSULTAT LISIBLE. Les positions aveugles sont permutées **à
    l'intérieur de chaque marche**, à compte constant : chaque marche garde exactement son nombre
    de pas aveugles, et seul leur ORDRE change. Si le hasard rend lui aussi zéro retour, la
    contiguïté observée n'est qu'une conséquence de la fréquence et ne prouve rien.

    ⚠ La permutation est **intra-marche** et non globale : mélanger tous les pas du corpus
    détruirait aussi la concentration des aveugles dans certaines marches, donc testerait deux
    choses à la fois et ne dirait laquelle a bougé.

    ⚠ Graine posée : un témoin dont le tirage change à chaque lancement rend un nombre différent à
    chaque relecture, donc n'est pas un témoin.
    """
    concernees = [m for m in par_marche if any(m["aveugles"])]
    if not concernees:
        return {"decidable": False, "pourquoi": "aucune marche ne porte de pas aveugle"}
    rng = np.random.default_rng(graine)

    def retours(listes) -> int:
        n = 0
        for av in listes:
            i = av.index(True)
            apres = av[i + 1:]
            if apres and not all(apres):
                n += 1
        return n

    reel = retours([m["aveugles"] for m in concernees])
    tirage = []
    for _ in range(tirages):
        tirage.append(retours([list(rng.permutation(m["aveugles"])) for m in concernees]))
    tirage = np.asarray(tirage)
    return {
        "decidable": True, "tirages": tirages, "graine": graine,
        "retours_observes": reel,
        # ⚠ La distribution est GARDÉE, pas seulement résumée : la figure du témoin la dessine, et
        # une figure qui la recalculerait serait un second producteur du même nombre.
        "distribution_des_retours": {str(k): int(v) for k, v in
                                     zip(*np.unique(tirage, return_counts=True))},
        "retours_medians_sous_permutation": float(np.median(tirage)),
        "retours_min_sous_permutation": int(tirage.min()),
        # ⚠ Unilatéral à gauche, et c'est dit : l'hypothèse est que l'observé est plus BAS que le
        # hasard. Un p bilatéral mélangerait ici deux questions dont une seule est posée.
        "part_des_permutations_aussi_basse": round(float(np.mean(tirage <= reel)), 5),
        "le_hasard_rendrait_la_meme_chose": bool(np.mean(tirage <= reel) > 0.05)}


def la_portee_quand_on_sarrete_a_laveugle(par_marche: list[dict],
                                          plafond: int = PLAFOND) -> dict:
    """Si le marcheur s'arrêtait au premier pas aveugle, jusqu'où irait-il ?

    ⭐⭐⭐⭐ C'EST LA PREMIÈRE PORTÉE NON CENSURÉE DE CE DÉPÔT, et seulement pour une partie des
    marches. Une marche qui rencontre un pas aveugle s'arrête **pour une raison** : sa longueur est
    mesurée. Une marche qui ne rencontre rien atteint encore le plafond : sa longueur reste une
    **borne inférieure**, exactement comme à `107` et `113`.

    ⚠⚠ Les deux populations sont rendues SÉPARÉMENT et jamais mélangées dans une médiane commune.
    Mêler une longueur mesurée et une longueur censurée rendrait un nombre qui n'est ni l'une ni
    l'autre, et ce dépôt a déjà payé une fois un plafond lu comme une limite de matière.

    ⚠ La longueur retenue est celle du dernier pas VOYANT : le pas aveugle n'a rien lu, donc le
    compter dans la portée ferait entrer dans la mesure la distance parcourue dans le vide.
    """
    if not par_marche:
        return {"decidable": False, "pourquoi": "aucune marche"}
    mesurees, censurees = [], []
    for m in par_marche:
        if any(m["aveugles"]):
            i = m["aveugles"].index(True)
            mesurees.append({
                "rayon_mm": m["rayon_mm"], "pas_voyants": i,
                "longueur_um": m["parcouru_um"][i - 1] if i > 0 else 0.0,
                "confirmes": sum(m["confirmes"][:i])})
        else:
            censurees.append({
                "rayon_mm": m["rayon_mm"], "pas_voyants": m["pas"],
                "longueur_um": m["parcouru_um"][-1] if m["parcouru_um"] else 0.0,
                "au_plafond": m["pas"] >= plafond})
    out = {
        "decidable": True, "plafond": plafond,
        "marches": len(par_marche),
        "marches_qui_sarretent_pour_une_raison": len(mesurees),
        "marches_encore_censurees": len(censurees),
        "marches_arretees_des_le_premier_pas": sum(1 for m in mesurees if m["pas_voyants"] == 0)}
    if mesurees:
        out["portee_mesuree"] = {
            "marches": len(mesurees),
            "pas_median": float(np.median([m["pas_voyants"] for m in mesurees])),
            "pas_max": int(max(m["pas_voyants"] for m in mesurees)),
            "longueur_mediane_um": round(float(np.median([m["longueur_um"] for m in mesurees])), 1),
            "longueur_max_um": round(float(max(m["longueur_um"] for m in mesurees)), 1)}
    if censurees:
        out["portee_encore_censuree"] = {
            "marches": len(censurees),
            "toutes_au_plafond": bool(all(m["au_plafond"] for m in censurees)),
            "longueur_mediane_um": round(float(np.median([m["longueur_um"] for m in censurees])), 1),
            "cest_une_borne_inferieure": True}
    out["detail_mesurees"] = mesurees
    out["detail_censurees"] = censurees
    return out


def le_vide_est_il_une_frontiere(par_marche: list[dict], tirages: int = 2000,
                                 graine: int = 1162) -> dict:
    """Le vide commence-t-il à un rayon, ou vient-il par plaques ?

    ⭐⭐⭐⭐ C'EST LE TEST QUI RETIRE UNE DES TROIS CAUSES. Si l'extérieur du rouleau n'a plus de
    matière, alors le vide est une **frontière** : rangées par rayon croissant, les marches
    voyantes viennent toutes d'abord et les aveugles toutes ensuite, soit **deux plages**. Si le
    vide vient par plaques, la suite alterne, et une frontière radiale est réfutée.

    ⚠⚠ Et il faut les DEUX bornes pour que le nombre veuille dire quelque chose. Beaucoup de
    plages contredit la frontière ; mais il faut aussi savoir combien le hasard en rendrait, sinon
    « ça alterne » ne dit pas si le rayon organise quoi que ce soit. Les étiquettes sont donc
    permutées sur l'ordre des rayons, à compte constant.

    ⚠ Ce que ce test ne tranche pas : « la matière extérieure est elle-même en morceaux » et « des
    blocs manquent au chargement » prédisent tous deux des plaques. Ce qui tombe est la frontière
    nette, pas l'une des deux autres causes.
    """
    ordre = sorted([m for m in par_marche if m.get("rayon_mm") is not None],
                   key=lambda m: m["rayon_mm"])
    etiquettes = [any(m["aveugles"]) for m in ordre]
    if len(set(etiquettes)) < 2:
        return {"decidable": False, "pourquoi": "toutes les marches sont du même côté"}

    def plages(seq) -> int:
        return 1 + sum(1 for a, b in zip(seq, seq[1:]) if a != b)

    rng = np.random.default_rng(graine)
    obs = plages(etiquettes)
    tire = np.asarray([plages(list(rng.permutation(etiquettes))) for _ in range(tirages)])
    aveugles = [m for m, e in zip(ordre, etiquettes) if e]
    return {
        "decidable": True, "marches": len(ordre),
        "marches_aveugles": len(aveugles),
        "rayon_de_la_premiere_aveugle_mm": aveugles[0]["rayon_mm"],
        "rayon_de_la_derniere_voyante_mm": max(
            m["rayon_mm"] for m, e in zip(ordre, etiquettes) if not e),
        "plages_observees": obs,
        "plages_sous_une_frontiere": 2,
        "plages_medianes_sous_permutation": float(np.median(tire)),
        "part_des_permutations_aussi_peu_de_plages": round(float(np.mean(tire <= obs)), 5),
        # ⭐⭐⭐⭐ Les deux verdicts, et ils sont indépendants : la frontière peut tomber pendant
        # que le rayon organise quand même quelque chose, et c'est exactement le cas intéressant.
        "le_vide_est_une_frontiere": bool(obs <= 2),
        "le_rayon_organise_quand_meme": bool(np.mean(tire <= obs) < 0.05),
        "graine": graine, "tirages": tirages}


def mesurer(course_p: Path = COURSE) -> dict:
    """Tout, depuis le JSON de `113` — aucune lecture distante."""
    course = json.loads(course_p.read_text(encoding="utf-8"))
    if course.get("course_incomplete"):
        raise ValueError(f"{course_p} : course incomplète")
    pm = marches(course)
    if not pm:
        raise ValueError(f"{course_p} ne porte aucune marche avec ses étapes")
    plafond = int(course.get("pas_max") or PLAFOND)
    return {
        "source": course_p.name, "marches": len(pm), "pas": sum(m["pas"] for m in pm),
        "plafond_de_la_course": plafond,
        # ⚠⚠ Les suites elles-mêmes sont gardées. Sans elles la figure devrait rouvrir la course
        # de `113`, donc lire deux fichiers pour dessiner un seul résultat — et un dessin qui ne
        # vient pas de la mesure qu'il illustre est libre de ne plus lui correspondre.
        "par_marche": [{"rayon_mm": m["rayon_mm"], "aveugles": m["aveugles"],
                        "confirmes": m["confirmes"]} for m in pm],
        "la_cecite_est_elle_absorbante": la_cecite_est_elle_absorbante(pm),
        "temoin": temoin_de_labsorption(pm),
        "la_portee_quand_on_sarrete_a_laveugle": la_portee_quand_on_sarrete_a_laveugle(pm, plafond),
        "le_vide_est_il_une_frontiere": le_vide_est_il_une_frontiere(pm)}


def afficher(r: dict) -> None:
    print(f"{r['marches']} marches · {r['pas']} pas · source {r['source']}")
    a = r["la_cecite_est_elle_absorbante"]
    if a.get("decidable"):
        t = a["transitions"]
        print(f"\n  {a['marches_avec_un_pas_aveugle']} marche(s) portent un pas aveugle, "
              f"{a['marches_avec_occasion']} avaient l'occasion de relire")
        print(f"  la vue revient dans {a['marches_ou_la_vue_revient']} marche(s)")
        print(f"  transitions : aveugle→aveugle {t['aveugle_puis_aveugle']}, "
              f"aveugle→voyant {t['aveugle_puis_voyant']}, "
              f"voyant→aveugle {t['voyant_puis_aveugle']}, "
              f"voyant→voyant {t['voyant_puis_voyant']}")
        print(f"  ⭐ la cécité est absorbante : {a['la_cecite_est_absorbante']}")
    w = r["temoin"]
    if w.get("decidable"):
        print(f"\n  témoin ({w['tirages']} permutations intra-marche, graine {w['graine']}) : "
              f"observé {w['retours_observes']}, "
              f"médian sous permutation {w['retours_medians_sous_permutation']}, "
              f"min {w['retours_min_sous_permutation']}")
        print(f"  part des permutations aussi basse : {w['part_des_permutations_aussi_basse']}")
    f = r.get("le_vide_est_il_une_frontiere", {})
    if f.get("decidable"):
        print(f"\n  rangées par rayon : {f['plages_observees']} plages, "
              f"contre 2 sous une frontière et "
              f"{f['plages_medianes_sous_permutation']:.0f} sous permutation")
        print(f"  ⭐ le vide est une frontière : {f['le_vide_est_une_frontiere']} · "
              f"le rayon organise quand même : {f['le_rayon_organise_quand_meme']}")
    p = r["la_portee_quand_on_sarrete_a_laveugle"]
    if p.get("decidable"):
        print(f"\n  s'arrêter au premier pas aveugle : "
              f"{p['marches_qui_sarretent_pour_une_raison']} marche(s) s'arrêtent pour une raison, "
              f"{p['marches_encore_censurees']} restent censurées")
        if "portee_mesuree" in p:
            m = p["portee_mesuree"]
            print(f"  ⭐ portée MESURÉE : médiane {m['pas_median']:.1f} pas "
                  f"({m['longueur_mediane_um']} µm), max {m['pas_max']} pas "
                  f"({m['longueur_max_um']} µm)")
        if "portee_encore_censuree" in p:
            c = p["portee_encore_censuree"]
            print(f"  ⚠ portée encore censurée : {c['marches']} marche(s), "
                  f"médiane {c['longueur_mediane_um']} µm — borne inférieure")


def verifier() -> int:
    """La batterie, hors ligne, sur des courses FABRIQUÉES.

    ⚠⚠ Les contrôles ne lisent pas l'arbre : un contrôle qui mesure la course du jour passe au
    vert le jour où elle change. Chaque défaut est remis par une sonde, et doit rougir.
    """
    import tempfile
    echecs = controles = 0

    def v(nom, obtenu, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not obtenu:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f" — {detail}" if detail else ""))

    def etape(aveugle: bool, confirme: bool = False, parcouru: float = 0.0) -> dict:
        """Un pas fabriqué. ⚠ La cécité passe par les MÊMES champs que la vraie course
        (`desaccord_des_moities_deg` et `planarite` exactement nuls), sinon la fixture testerait
        une définition que `est_aveugle` n'applique pas."""
        return {"pas": 1, "confirme": confirme, "parcouru_um": parcouru,
                "desaccord_des_moities_deg": 0.0 if aveugle else 12.5,
                "planarite": 0.0 if aveugle else 0.4}

    def course(marches_aveugles: list[list[bool]], rayons=None) -> dict:
        rayons = rayons or [4.0 + i for i in range(len(marches_aveugles))]
        return {"pas_max": 20, "lignes": [
            {"rayon_mm": r, "detail": [{"etapes": [
                etape(a, confirme=not a, parcouru=100.0 * (i + 1))
                for i, a in enumerate(av)]}]}
            for r, av in zip(rayons, marches_aveugles)]}

    # ⭐ La définition importée est bien celle de `115`, et non une copie locale.
    v("un pas aveugle est un désaccord ET une planarité exactement nuls",
      est_aveugle(etape(True)) and not est_aveugle(etape(False)))
    v("un désaccord nul sur une vraie planarité n'est PAS aveugle",
      not est_aveugle({"desaccord_des_moities_deg": 0.0, "planarite": 0.4}))

    # ⭐⭐⭐⭐ LE TEST : une cécité absorbante, et sa symétrique.
    absorbante = [[False] * 20, [False] * 20,
                  [False] * 5 + [True] * 15, [False] * 12 + [True] * 8,
                  [True] * 20, [False] * 3 + [True] * 17]
    pm = marches(course(absorbante))
    v("les six marches fabriquées sont relues", len(pm) == 6, f"{len(pm)}")
    a = la_cecite_est_elle_absorbante(pm)
    v("quatre marches portent un pas aveugle", a["marches_avec_un_pas_aveugle"] == 4,
      f"{a['marches_avec_un_pas_aveugle']}")
    v("la vue ne revient jamais", a["marches_ou_la_vue_revient"] == 0,
      f"{a['marches_ou_la_vue_revient']}")
    v("... et la cécité est déclarée absorbante", a["la_cecite_est_absorbante"])
    v("aucune transition aveugle→voyant", a["transitions"]["aveugle_puis_voyant"] == 0)
    v("les transitions voyant→aveugle sont comptées", a["transitions"]["voyant_puis_aveugle"] == 3,
      f"{a['transitions']['voyant_puis_aveugle']}")

    # ⚠⚠ LA SONDE SYMÉTRIQUE : sans elle, un test qui répondrait toujours « absorbante » passerait.
    transitoire = [[False] * 20, [False] * 5 + [True] * 3 + [False] * 12,
                   [False] * 12 + [True] * 8, [False] * 2 + [True] + [False] * 17]
    at = la_cecite_est_elle_absorbante(marches(course(transitoire)))
    v("sonde : une vue qui revient est vue", at["marches_ou_la_vue_revient"] == 2,
      f"{at['marches_ou_la_vue_revient']}")
    v("... et la cécité n'est PAS déclarée absorbante", not at["la_cecite_est_absorbante"])
    v("... et la transition aveugle→voyant est comptée",
      at["transitions"]["aveugle_puis_voyant"] == 2,
      f"{at['transitions']['aveugle_puis_voyant']}")

    # ⚠⚠ CE QUI COMPTE COMME UNE OCCASION. Une marche dont le seul pas aveugle est le DERNIER
    # n'en a aucune ; une marche entièrement aveugle en a dix-neuf et les laisse toutes passer.
    # Confondre les deux ferait dire « absorbante » à un corpus qui n'a jamais pu le montrer.
    fin = la_cecite_est_elle_absorbante(marches(course([[False] * 19 + [True]] * 3)))
    v("un pas aveugle en dernière position ne laisse aucune occasion",
      fin["marches_sans_occasion_de_revenir"] == 3, f"{fin['marches_sans_occasion_de_revenir']}")
    v("... et « absorbante » est REFUSÉ faute d'occasion", not fin["la_cecite_est_absorbante"])
    tout = la_cecite_est_elle_absorbante(marches(course([[True] * 20, [True] * 20])))
    v("une marche entièrement aveugle, elle, A eu des occasions",
      tout["marches_avec_occasion"] == 2, f"{tout['marches_avec_occasion']}")
    v("... donc elle prouve l'absorption", tout["la_cecite_est_absorbante"])
    v("aucune marche aveugle rend indécidable",
      not la_cecite_est_elle_absorbante(marches(course([[False] * 20])))["decidable"])

    # ⭐⭐⭐ LE TÉMOIN. Sur la fixture absorbante, le hasard doit faire revenir la vue.
    w = temoin_de_labsorption(pm, tirages=400)
    v("témoin : le hasard fait revenir la vue", w["retours_medians_sous_permutation"] > 0,
      f"{w['retours_medians_sous_permutation']}")
    v("... donc l'observé est extrême", w["part_des_permutations_aussi_basse"] < 0.05,
      f"{w['part_des_permutations_aussi_basse']}")
    v("... et le témoin le dit", not w["le_hasard_rendrait_la_meme_chose"])
    # ⚠⚠ LA SONDE DU TÉMOIN : une marche dont TOUS les pas sauf un sont aveugles a peu d'occasions
    # de faire revenir la vue, donc le hasard rend souvent zéro retour. Le témoin doit alors
    # refuser de conclure — sans ça, « absorbante » serait satisfait par la seule fréquence.
    rare = [[True] * 19 + [False]] * 4
    wr = temoin_de_labsorption(marches(course(rare)), tirages=400)
    v("sonde : quand le hasard rend souvent zéro retour, le témoin le dit",
      wr["le_hasard_rendrait_la_meme_chose"], f"{wr['part_des_permutations_aussi_basse']}")
    v("le témoin est reproductible", temoin_de_labsorption(pm, tirages=400)[
        "part_des_permutations_aussi_basse"] == w["part_des_permutations_aussi_basse"])

    # ⭐⭐⭐⭐ FRONTIÈRE OU PLAQUES. Les deux sondes sont symétriques, et il en faut deux : un test
    # qui répondrait toujours « pas une frontière » passerait la seconde seule.
    voyant, aveugle = [False] * 20, [True] * 20
    monotone = marches(course([voyant] * 9 + [aveugle] * 9))
    fm = le_vide_est_il_une_frontiere(monotone, tirages=400)
    v("sonde : un vide qui commence à un rayon rend deux plages", fm["plages_observees"] == 2,
      f"{fm['plages_observees']}")
    v("... et il est déclaré frontière", fm["le_vide_est_une_frontiere"])
    v("... et le rayon organise, évidemment", fm["le_rayon_organise_quand_meme"])
    alterne = marches(course([voyant, aveugle] * 9))
    fa = le_vide_est_il_une_frontiere(alterne, tirages=400)
    v("sonde : un vide qui alterne n'est PAS une frontière",
      not fa["le_vide_est_une_frontiere"], f"{fa['plages_observees']} plages")
    v("... et il alterne PLUS que le hasard, donc le rayon n'explique rien de moins",
      not fa["le_rayon_organise_quand_meme"],
      f"{fa['part_des_permutations_aussi_peu_de_plages']}")
    v("toutes les marches du même côté rendent indécidable",
      not le_vide_est_il_une_frontiere(marches(course([voyant] * 6)))["decidable"])
    v("le rayon de la première aveugle est lu, jamais choisi",
      fm["rayon_de_la_premiere_aveugle_mm"] == 13.0,
      f"{fm['rayon_de_la_premiere_aveugle_mm']}")

    # ⭐⭐⭐⭐ LA PORTÉE : mesurée pour les unes, encore censurée pour les autres.
    p = la_portee_quand_on_sarrete_a_laveugle(pm)
    v("quatre marches s'arrêtent pour une raison",
      p["marches_qui_sarretent_pour_une_raison"] == 4,
      f"{p['marches_qui_sarretent_pour_une_raison']}")
    v("deux restent censurées", p["marches_encore_censurees"] == 2,
      f"{p['marches_encore_censurees']}")
    # les quatre mesurées ont 5, 12, 0 et 3 pas voyants -> médiane (3+5)/2 = 4,0
    v("la médiane des portées mesurées est calculée sur les pas VOYANTS",
      p["portee_mesuree"]["pas_median"] == 4.0, f"{p['portee_mesuree']['pas_median']}")
    # la longueur est celle du dernier pas voyant : 5 pas -> 500 um
    v("la longueur exclut le pas aveugle", p["portee_mesuree"]["longueur_max_um"] == 1200.0,
      f"{p['portee_mesuree']['longueur_max_um']}")
    v("une marche aveugle dès le premier pas a une portée nulle",
      p["marches_arretees_des_le_premier_pas"] == 1,
      f"{p['marches_arretees_des_le_premier_pas']}")
    v("les censurées sont toutes au plafond", p["portee_encore_censuree"]["toutes_au_plafond"])
    v("... et leur longueur est dite borne inférieure",
      p["portee_encore_censuree"]["cest_une_borne_inferieure"])
    # ⚠ LA SONDE QUI COMPTE : mesurées et censurées ne sont jamais dans la même médiane.
    v("sonde : la médiane mesurée ignore les censurées",
      p["portee_mesuree"]["marches"] + p["portee_encore_censuree"]["marches"] == p["marches"])
    v("une course sans marche aveugle ne mesure aucune portée",
      "portee_mesuree" not in la_portee_quand_on_sarrete_a_laveugle(
          marches(course([[False] * 20, [False] * 20]))))

    # ⚠ Une course incomplète est refusée plutôt que mesurée à moitié.
    with tempfile.TemporaryDirectory() as dd:
        f = Path(dd) / "c.json"
        f.write_text(json.dumps({"course_incomplete": True, "lignes": []}), encoding="utf-8")
        try:
            mesurer(f)
            v("une course incomplète est refusée", False)
        except ValueError:
            v("une course incomplète est refusée", True)
        f.write_text(json.dumps({"lignes": []}), encoding="utf-8")
        try:
            mesurer(f)
            v("une course sans marche est refusée", False)
        except ValueError:
            v("une course sans marche est refusée", True)
        f.write_text(json.dumps(course(absorbante), ensure_ascii=False), encoding="utf-8")
        r = mesurer(f)
        v("mesurer lit le plafond dans la course", r["plafond_de_la_course"] == 20)
        v("... et rend les trois sections",
          all(k in r for k in ("la_cecite_est_elle_absorbante", "temoin",
                               "la_portee_quand_on_sarrete_a_laveugle")))
        afficher(r)

    print(f"\n{'ALL PASS' if echecs == 0 else 'ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--course", type=Path, default=COURSE)
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(a.course)
    afficher(r)
    if a.json:
        a.json.write_text(json.dumps(r, indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
