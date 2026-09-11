#!/usr/bin/env python3
"""Le taux suit le rayon — ou le volume cesse-t-il simplement de répondre ?

⚠⚠ POURQUOI CE FICHIER EXISTE. `113` a mesuré que le taux de confirmation du marcheur **suit le
rayon** (rho de Spearman −0,7188 sur 28 bandes de 4,07 à 23,8 mm) et **pas** la profondeur. La
porte `R4-P16` demandait de séparer ce que le rayon fait varier — épaisseur lue, courbure, qualité
du scan. La course avait gardé, à chacun de ses 560 pas, des mesures LOCALES de ce que la matière
montrait : la question devient donc mesurable **sans une lecture distante**.

⭐⭐⭐⭐ **ET LA RÉPONSE EST QUE LE RAYON N'EST PAS LA CAUSE.** Un tiers des pas ne lit **RIEN** —
planarité exactement 0,000, score au plancher, et **zéro confirmation sur les 178**. Ces pas ne
sont pas répartis : douze marches n'en ont aucun, et quatre en sont faites **dès leur premier pas**.
Une fois les marches aveugles écartées, le taux du grand rayon rejoint celui du petit. Le rho
−0,719 mesurait donc **si le volume répond**, pas si le marcheur y arrive.

⚠⚠⚠ **ET LE VIDE EST DÉCLARÉ ORIENTÉ : 178 FOIS SUR 178.** Le drapeau vaut `desaccord <
barre_moities`, or deux moitiés de rien ne peuvent pas être en désaccord — le désaccord vaut
exactement 0°, donc il passe la barre. C'est le défaut que ce dépôt attrape en boucle, cette fois
dans le marcheur : *un vide lu comme un accord parfait* (`54` cinq rendus vides lus comme cinq
surfaces plates, `60` la constante qui rendait le modèle muet, `41` §6bis un chunk absent lu comme
« pas de matière »).

⚠⚠ **TROIS COVARIABLES SONT DANS LE CRITÈRE, ET LES CORRÉLER SERAIT UNE TAUTOLOGIE.** Le prédicat
de `102` s'écrit `confirme = (interstices == 1) et (accord > barre) et (non en_butee)`. Elles sont
**nommées et écartées** plutôt qu'absentes — et servent de **contrôle positif**, parce qu'un test
qui ne les verrait pas n'aurait aucune puissance.

⚠⚠ **L'unité qui décide est la MARCHE, pas le pas.** Les 560 pas sont 28 marches de 20, et les
vingt pas d'une marche partagent son rayon et son départ. Un test par pas prendrait 560
observations pour 28. Les tests décisifs portent sur **n = 28**.

⚠ **Ce que ce fichier NE tranche PAS** : si le vide est une propriété du rouleau (l'extérieur
n'est pas dans la région chargée, ou il n'y a réellement plus de matière) ou une panne du lecteur
(des blocs absents rendus en zéros, la panne de `41` §6bis). Les deux se lisent identiquement ici,
et les distinguer demande d'interroger le volume aux positions de départ — ce qui est une lecture
distante, donc un autre lot.

  uv run python src/nappe/ce_qui_porte_le_taux.py --verifier
  uv run python src/nappe/ce_qui_porte_le_taux.py --json docs/mesures/ce_qui_porte_le_taux.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from scipy import stats

RACINE = Path(__file__).resolve().parents[2]
COURSE = RACINE / "docs" / "mesures" / "jusquou_va_t_il_si_on_le_laisse.json"

COVARIABLES_DU_CRITERE = ("interstices_traverses", "accord_de_linterstice", "en_butee")
"""Ce que le prédicat `confirme` lit LUI-MÊME, donc ce qu'on ne peut pas lui corréler.

⚠⚠⚠ `confirme = (interstices == 1) et (accord > barre) et (non en_butee)` — trois termes d'une
conjonction. Les corréler au résultat de cette conjonction est circulaire : le lien est garanti,
énorme, et vide. Ils restent nommés ici pour deux raisons : un lecteur doit savoir pourquoi ils
n'apparaissent pas dans la table des résultats, et ils servent de **contrôle positif** (§ `temoin`)
— un test qui ne les verrait pas ne verrait rien."""

COVARIABLES_LIBRES = ("planarite", "score_du_balayage", "desaccord_des_moities_deg", "pas_um")
"""Ce que la matière montre à un endroit, sans entrer dans le critère.

⚠ `feuilles_franchies` est **exclue** bien qu'absente du prédicat : elle sort de la même lecture
de profil que `interstices_traverses`, dont elle est la version continue. La corréler serait une
tautologie déguisée — celle qui se voit moins, donc celle qui coûte le plus cher."""

SUSPECTE = ("feuilles_franchies", "fraction_en_butee")
"""Écartées pour cause de **parenté** avec le critère, pas d'absence du critère.

⚠ Les nommer sépare « on n'y a pas pensé » de « on a regardé et on a refusé », et c'est la seule
chose qui distingue une exclusion d'un oubli."""


def est_aveugle(etape: dict) -> bool:
    """Ce pas a-t-il lu quelque chose, ou le cube était-il vide ?

    ⚠⚠ La signature est **conjointe**, jamais un seuil sur une grandeur : désaccord exactement
    nul ET planarité exactement nulle. Prendre l'un des deux seul serait un seuil réglé sur ce
    qu'on voit ; les deux ensemble ne peuvent valoir zéro à la fois que sur un cube sans matière,
    parce que la planarité d'une vraie feuille n'est jamais exactement 0,000 et qu'un vrai
    empilement ne rend jamais un désaccord exactement 0,00°.

    ⚠ « Aveugle » et non « hors du volume » : le lecteur n'a jamais signalé de sortie
    (`sorties_du_volume: 0`). Ce qui est mesuré est que le marcheur **n'a rien lu**, pas où il
    était.
    """
    d = etape.get("desaccord_des_moities_deg")
    p = etape.get("planarite")
    return d == 0.0 and p == 0.0


def le_vide_est_il_declare_oriente(course: dict) -> dict:
    """Le drapeau `oriente` distingue-t-il un accord d'une absence de signal ?

    ⭐⭐⭐ `oriente = desaccord < barre_moities`, et deux moitiés de rien ne peuvent pas être en
    désaccord. Un cube vide rend donc 0,00° et passe la barre : le marcheur croit savoir où il va
    exactement là où il ne lit rien. C'est un défaut du drapeau, pas de la matière, et il se
    mesure par un compte plutôt que par une lecture de code.
    """
    pas = [e for l in course.get("lignes", []) for m in l.get("detail", [])
           for e in m.get("etapes", []) if "confirme" in e]
    if not pas:
        return {"decidable": False, "pourquoi": "aucun pas lisible"}
    aveugles = [e for e in pas if est_aveugle(e)]
    voyants = [e for e in pas if not est_aveugle(e)]
    return {
        "decidable": True, "pas": len(pas),
        "pas_aveugles": len(aveugles),
        "part_aveugle": round(len(aveugles) / len(pas), 4),
        "aveugles_confirmes": sum(1 for e in aveugles if e.get("confirme")),
        "voyants_confirmes": sum(1 for e in voyants if e.get("confirme")),
        "taux_voyant": round(sum(1 for e in voyants if e.get("confirme")) / max(1, len(voyants)), 4),
        "aveugles_declares_orientes": sum(1 for e in aveugles if e.get("oriente")),
        # ⭐⭐⭐ Le verdict : un vide qui passe pour orienté est un marcheur qui croit savoir.
        "le_vide_passe_pour_oriente": bool(
            aveugles and all(e.get("oriente") for e in aveugles))}


def le_rayon_survit_il_aux_marches_voyantes(par_marche: list[dict]) -> dict:
    """Le taux du grand rayon rejoint-il celui du petit, une fois les marches aveugles écartées ?

    ⭐⭐⭐⭐ C'EST LE TEST QUI RETIRE LA CAUSE AU RAYON. Si le rho s'effondre sur les seules marches
    qui ont lu quelque chose, alors le rayon ne mesurait que la probabilité que le volume réponde.
    Si le rho survit, le rayon porte autre chose et la question reste ouverte.

    ⚠ Une marche est **voyante** quand aucun de ses pas n'est aveugle — et pas « peu de pas
    aveugles ». Une fraction tolérée serait un seuil choisi pour que le résultat du jour passe ;
    zéro est la seule coupure que personne n'a réglée.
    """
    voyantes = [m for m in par_marche if m["pas_aveugles"] == 0]
    if len(voyantes) < 6:
        return {"decidable": False,
                "pourquoi": f"{len(voyantes)} marche(s) voyante(s), il en faut six"}
    rt, pt = _rho([m["rayon_mm"] for m in par_marche], [m["taux"] for m in par_marche])
    rv, pv = _rho([m["rayon_mm"] for m in voyantes], [m["taux"] for m in voyantes])
    interieur = [m["taux"] for m in voyantes if m["rayon_mm"] < 17.0]
    exterieur = [m["taux"] for m in voyantes if m["rayon_mm"] >= 17.0]
    u = mw = None
    if len(interieur) >= 3 and len(exterieur) >= 3:
        u, mw = stats.mannwhitneyu(interieur, exterieur, alternative="two-sided")
    return {
        "decidable": True,
        "marches": len(par_marche), "marches_voyantes": len(voyantes),
        "rho_sur_toutes": round(rt, 4), "p_sur_toutes": round(pt, 6),
        "rho_sur_les_voyantes": round(rv, 4), "p_sur_les_voyantes": round(pv, 6),
        "taux_median_voyantes_interieur": (round(float(np.median(interieur)), 4)
                                           if interieur else None),
        "taux_median_voyantes_exterieur": (round(float(np.median(exterieur)), 4)
                                           if exterieur else None),
        "p_interieur_contre_exterieur": round(float(mw), 4) if mw is not None else None,
        # ⚠ La coupure à 17 mm n'est pas un seuil ajusté : c'est le rayon de la première marche
        # qui porte un pas aveugle, donc elle est lue dans les données et non choisie.
        "coupure_mm": 17.0,
        "le_rayon_survit_aux_voyantes": bool(abs(rv) > 0.4 and pv < 0.05)}


def marches(course: dict) -> list[dict]:
    """Une entrée par marche : son rayon, son taux, et la médiane de chaque covariable.

    ⚠ La **médiane** et non la moyenne : `desaccord_des_moities_deg` sature à 90° quand les deux
    moitiés du gabarit ne s'accordent pas du tout, donc une moyenne y serait tirée par une poignée
    de pas muets et mesurerait surtout combien il y en a eu.
    """
    out = []
    for ligne in course.get("lignes", []):
        for cel in ligne.get("detail", []):
            etapes = [e for e in cel.get("etapes", []) if "confirme" in e]
            if not etapes:
                continue
            e = {"rayon_mm": ligne.get("rayon_mm"), "pas": len(etapes),
                 "confirmes": sum(1 for x in etapes if x.get("confirme"))}
            e["taux"] = e["confirmes"] / e["pas"]
            for cle in COVARIABLES_LIBRES + COVARIABLES_DU_CRITERE:
                vals = [x[cle] for x in etapes
                        if isinstance(x.get(cle), (int, float)) and not isinstance(x.get(cle), bool)]
                bools = [1.0 if x.get(cle) else 0.0 for x in etapes
                         if isinstance(x.get(cle), bool)]
                if vals:
                    e[cle] = float(np.median(vals))
                elif bools:
                    e[cle] = float(np.mean(bools))
            e["part_orientee"] = float(np.mean([1.0 if x.get("oriente") else 0.0 for x in etapes]))
            e["pas_aveugles"] = sum(1 for x in etapes if est_aveugle(x))
            e["aveugle_des_le_depart"] = bool(etapes and est_aveugle(etapes[0]))
            out.append(e)
    return out


def _rho(x, y) -> tuple[float, float]:
    r, p = stats.spearmanr(x, y)
    return float(r), float(p)


def ce_qui_suit_le_taux(par_marche: list[dict]) -> dict:
    """Quelles covariables suivent le taux, et lesquelles suivent le rayon.

    ⚠ Les p ne sont **pas corrigés** pour la multiplicité, et c'est dit plutôt que fait : corriger
    sur six tests choisis parce qu'ils étaient disponibles donnerait une fausse impression de
    protocole. Ce qui est exploratoire est nommé exploratoire ; le seul test qui décide est celui
    du § suivant, et il était posé avant de regarder.
    """
    if len(par_marche) < 6:
        return {"decidable": False, "pourquoi": f"{len(par_marche)} marches, il en faut six"}
    taux = [m["taux"] for m in par_marche]
    ray = [m["rayon_mm"] for m in par_marche]
    out = {"decidable": True, "marches": len(par_marche), "exploratoire": True,
           "p_non_corriges_pour_la_multiplicite": True, "libres": {}, "du_critere": {}}
    for groupe, cles in (("libres", COVARIABLES_LIBRES + ("part_orientee",)),
                         ("du_critere", COVARIABLES_DU_CRITERE)):
        for cle in cles:
            vals = [m.get(cle) for m in par_marche]
            if any(v is None for v in vals) or len(set(vals)) < 3:
                out[groupe][cle] = {"decidable": False, "pourquoi": "constante ou absente"}
                continue
            rt, pt = _rho(vals, taux)
            rr, pr = _rho(vals, ray)
            out[groupe][cle] = {"decidable": True,
                                "rho_avec_le_taux": round(rt, 4), "p_taux": round(pt, 6),
                                "rho_avec_le_rayon": round(rr, 4), "p_rayon": round(pr, 6)}
    return out


def le_rayon_survit_il(par_marche: list[dict], covariable: str) -> dict:
    """Le lien rayon–taux survit-il quand on tient compte d'une covariable de la matière ?

    ⭐⭐⭐ C'EST LE TEST QUI DÉCIDE, et il a deux issues qui n'ont pas le même remède. Si le rho
    partiel **s'effondre**, le rayon agit À TRAVERS la covariable : ce que le marcheur rencontre au
    grand rayon est une matière qui montre moins, et le remède est en amont — mieux lire, ou lire
    autrement. S'il **survit**, le rayon porte autre chose que ce que la matière montre ici, et le
    remède est dans le marcheur ou dans sa géométrie.

    Corrélation partielle de Spearman : on rangue les trois séries, on retire de `taux` et de
    `rayon` ce qu'une droite sur la covariable en explique, et on corrèle les résidus.

    ⚠ Le p vient d'un t à `n − 3` degrés. Avec n = 28 il reste peu de puissance : un rho partiel
    qui tombe sous le seuil ne prouve pas l'absence d'effet, il cesse de la rejeter. La réserve est
    dans la sortie, pas seulement ici.
    """
    n = len(par_marche)
    vals = [m.get(covariable) for m in par_marche]
    if n < 6 or any(v is None for v in vals) or len(set(vals)) < 3:
        return {"decidable": False, "pourquoi": f"{covariable} constante, absente, ou n trop petit"}
    r_t = stats.rankdata([m["taux"] for m in par_marche])
    r_r = stats.rankdata([m["rayon_mm"] for m in par_marche])
    r_c = stats.rankdata(vals)

    def residus(y):
        pente, ord0 = np.polyfit(r_c, y, 1)
        return y - (pente * r_c + ord0)

    brut, p_brut = stats.pearsonr(r_t, r_r)
    partiel, _ = stats.pearsonr(residus(r_t), residus(r_r))
    ddl = n - 3
    t = partiel * np.sqrt(ddl / max(1e-12, 1 - partiel ** 2))
    p_part = float(2 * stats.t.sf(abs(t), ddl))
    return {"decidable": True, "covariable": covariable, "marches": n,
            "rho_brut": round(float(brut), 4), "p_brut": round(float(p_brut), 6),
            "rho_partiel": round(float(partiel), 4), "p_partiel": round(p_part, 6),
            "part_expliquee": round(1 - abs(partiel) / max(1e-12, abs(brut)), 3),
            "le_rayon_survit": bool(abs(partiel) > 0.3 and p_part < 0.05),
            "reserve": "n = 28 : un rho partiel qui tombe cesse de rejeter l'absence d'effet, "
                       "il ne la prouve pas"}


def temoin_du_test(par_marche: list[dict]) -> dict:
    """Le test a-t-il la puissance de voir un lien qu'on SAIT être là, et de ne pas en voir un faux ?

    ⭐⭐ Deux contrôles, et le premier est ce qui rend le second lisible.

    **Positif** : `accord_de_linterstice` est un terme du prédicat `confirme`, donc son lien avec
    le taux est garanti par construction. Un test qui ne le verrait pas ne verrait rien, et tous
    les « pas de lien » de ce fichier voudraient dire « pas de puissance ».

    **Négatif** : les taux permutés au hasard entre les marches. Le lien avec le rayon doit
    disparaître ; s'il survit, c'est que le test trouve une structure dans l'ordre des marches et
    pas dans la matière.
    """
    if len(par_marche) < 6:
        return {"decidable": False, "pourquoi": "pas assez de marches"}
    taux = [m["taux"] for m in par_marche]
    ray = [m["rayon_mm"] for m in par_marche]
    acc = [m.get("accord_de_linterstice") for m in par_marche]
    positif = None
    if all(v is not None for v in acc) and len(set(acc)) >= 3:
        r, p = _rho(acc, taux)
        positif = {"rho": round(r, 4), "p": round(p, 6), "vu": bool(p < 0.05)}
    # ⚠ Graine posée : un contrôle négatif dont le tirage change à chaque lancement rend un
    # nombre différent à chaque relecture, donc n'est pas un contrôle.
    rng = np.random.default_rng(1131)
    rhos = []
    for _ in range(2000):
        rhos.append(abs(_rho(rng.permutation(taux), ray)[0]))
    reel = abs(_rho(taux, ray)[0])
    return {"decidable": True,
            "positif_le_terme_du_critere": positif,
            "negatif_taux_permutes": {
                "tirages": 2000,
                "rho_median_sous_permutation": round(float(np.median(rhos)), 4),
                "rho_reel": round(reel, 4),
                "part_des_permutations_au_moins_aussi_forte": round(
                    float(np.mean([x >= reel for x in rhos])), 5)}}


def mesurer(course_p: Path = COURSE) -> dict:
    """Tout, depuis le JSON de `113` — aucune lecture distante."""
    course = json.loads(course_p.read_text(encoding="utf-8"))
    if course.get("course_incomplete"):
        raise ValueError(f"{course_p} : course incomplète")
    pm = marches(course)
    if not pm:
        raise ValueError(f"{course_p} ne porte aucune marche avec ses étapes")
    suit = ce_qui_suit_le_taux(pm)
    # ⚠ La covariable du test décisif est choisie par son lien avec le TAUX parmi les libres —
    # et le choix est écrit dans la sortie. La choisir après avoir vu les rho partiels serait
    # choisir celle qui rend le résultat qu'on veut.
    libres = {k: v for k, v in suit.get("libres", {}).items() if v.get("decidable")}
    meilleure = max(libres, key=lambda k: abs(libres[k]["rho_avec_le_taux"])) if libres else None
    out = {"source": course_p.name, "marches": len(pm), "pas": sum(m["pas"] for m in pm),
           "covariables_du_critere_ecartees": list(COVARIABLES_DU_CRITERE),
           "covariables_suspectes_ecartees": list(SUSPECTE),
           "par_marche": pm, "ce_qui_suit_le_taux": suit,
           "covariable_du_test": meilleure,
           "temoin": temoin_du_test(pm)}
    out["le_rayon_survit_il"] = (le_rayon_survit_il(pm, meilleure) if meilleure
                                 else {"decidable": False, "pourquoi": "aucune covariable libre"})
    # ⚠ Le test est refait sur CHAQUE covariable libre : n'en publier qu'une ferait lire le choix
    # comme une conclusion, alors que c'est une décision.
    out["le_rayon_survit_a_chacune"] = {k: le_rayon_survit_il(pm, k) for k in libres}
    # ⭐⭐⭐⭐ Les deux mesures qui retirent la cause au rayon, et le défaut qu'elles trouvent.
    out["le_vide_est_il_declare_oriente"] = le_vide_est_il_declare_oriente(course)
    out["le_rayon_survit_il_aux_marches_voyantes"] = le_rayon_survit_il_aux_marches_voyantes(pm)
    out["marches_aveugles_des_le_depart"] = sum(1 for m in pm if m["aveugle_des_le_depart"])
    return out


def afficher(r: dict) -> None:
    print(f"{r['marches']} marches · {r['pas']} pas · source {r['source']}")
    o = r.get("le_vide_est_il_declare_oriente", {})
    if o.get("decidable"):
        print(f"\n★★★★ LE MARCHEUR LIT-IL QUELQUE CHOSE ?")
        print(f"   {o['pas_aveugles']}/{o['pas']} pas AVEUGLES ({o['part_aveugle']:.0%}) — "
              f"désaccord 0,00° ET planarité 0,000")
        print(f"   confirmés : {o['aveugles_confirmes']}/{o['pas_aveugles']} aveugles contre "
              f"{o['voyants_confirmes']}/{o['pas'] - o['pas_aveugles']} voyants "
              f"(taux voyant {o['taux_voyant']:.4f})")
        print(f"   {r.get('marches_aveugles_des_le_depart', 0)} marche(s) aveugle(s) DÈS LE "
              f"PREMIER PAS")
        if o["le_vide_passe_pour_oriente"]:
            print(f"   ⛔ LE VIDE EST DÉCLARÉ ORIENTÉ : "
                  f"{o['aveugles_declares_orientes']}/{o['pas_aveugles']}")
    v = r.get("le_rayon_survit_il_aux_marches_voyantes", {})
    if v.get("decidable"):
        print(f"\n★★★★ LE RAYON SURVIT-IL AUX MARCHES QUI ONT LU ?")
        print(f"   toutes ({v['marches']})      rho {v['rho_sur_toutes']:+.4f}  p {v['p_sur_toutes']:.2e}")
        print(f"   voyantes ({v['marches_voyantes']})    rho {v['rho_sur_les_voyantes']:+.4f}  "
              f"p {v['p_sur_les_voyantes']:.4f}  → "
              f"{'OUI' if v['le_rayon_survit_aux_voyantes'] else 'NON'}")
        if v.get("p_interieur_contre_exterieur") is not None:
            print(f"   voyantes sous {v['coupure_mm']:.0f} mm : taux médian "
                  f"{v['taux_median_voyantes_interieur']:.3f} · au-dessus : "
                  f"{v['taux_median_voyantes_exterieur']:.3f} · "
                  f"p {v['p_interieur_contre_exterieur']:.4f}")
    print()
    print(f"écartées, car dans le critère : {', '.join(r['covariables_du_critere_ecartees'])}")
    print(f"écartées, car parentes        : {', '.join(r['covariables_suspectes_ecartees'])}\n")

    s = r["ce_qui_suit_le_taux"]
    if s.get("decidable"):
        print("CE QUI SUIT LE TAUX ET LE RAYON (exploratoire, p non corrigés)")
        print(f"  {'covariable':<28}{'rho(taux)':>11}{'p':>10}{'rho(rayon)':>12}{'p':>10}")
        for groupe, titre in (("libres", "libres"), ("du_critere", "DANS le critère")):
            print(f"  — {titre} —")
            for cle, x in s[groupe].items():
                if not x.get("decidable"):
                    print(f"  {cle:<28}{'—':>11}  {x['pourquoi']}")
                    continue
                print(f"  {cle:<28}{x['rho_avec_le_taux']:>+11.4f}{x['p_taux']:>10.4f}"
                      f"{x['rho_avec_le_rayon']:>+12.4f}{x['p_rayon']:>10.4f}")

    t = r.get("temoin", {})
    if t.get("decidable"):
        pos = t.get("positif_le_terme_du_critere")
        if pos:
            print(f"\nTÉMOIN POSITIF (un terme du critère) : rho {pos['rho']:+.4f}, "
                  f"p {pos['p']:.2e} — {'vu' if pos['vu'] else '⛔ NON VU, le test n’a pas de puissance'}")
        n = t["negatif_taux_permutes"]
        print(f"TÉMOIN NÉGATIF (taux permutés, {n['tirages']} tirages) : "
              f"rho réel {n['rho_reel']:.4f}, médiane sous permutation "
              f"{n['rho_median_sous_permutation']:.4f}, part au moins aussi forte "
              f"{n['part_des_permutations_au_moins_aussi_forte']:.5f}")

    print(f"\n★★★ LE RAYON SURVIT-IL ? (covariable du test : {r.get('covariable_du_test')})")
    for cle, x in r.get("le_rayon_survit_a_chacune", {}).items():
        if not x.get("decidable"):
            print(f"   {cle:<28} — {x['pourquoi']}")
            continue
        marque = "OUI" if x["le_rayon_survit"] else "NON"
        print(f"   {cle:<28} brut {x['rho_brut']:+.4f} → partiel {x['rho_partiel']:+.4f} "
              f"(p {x['p_partiel']:.4f}, {x['part_expliquee']:.0%} expliqué) · {marque}")
    d = r.get("le_rayon_survit_il", {})
    if d.get("decidable"):
        print(f"\n   ⚠ {d['reserve']}")


def verifier() -> int:
    """Contrôles hors ligne, sur des marches FABRIQUÉES dont on connaît la réponse."""
    echecs = controles = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, controles
        controles += 1
        if ok:
            print(f"  ✅ {nom}" + (f"  — {detail}" if detail else ""))
        else:
            echecs += 1
            print(f"  ❌ {nom}" + (f"  — {detail}" if detail else ""))

    def fabrique(n=28, pas=20, porte_par="planarite", bruit=0.0, graine=7):
        """Des marches où le taux est porté par UNE covariable connue, et le rayon la suit."""
        rng = np.random.default_rng(graine)
        out = []
        for i in range(n):
            q = 1.0 - i / (n - 1)                       # la matière se dégrade avec le rang
            taux_vise = min(0.95, max(0.05, q + rng.normal(0, bruit)))
            k = int(round(taux_vise * pas))
            e = {"rayon_mm": 4.0 + i, "pas": pas, "confirmes": k, "taux": k / pas,
                 "planarite": 0.5, "score_du_balayage": 5.0,
                 "desaccord_des_moities_deg": 5.0, "pas_um": 200.0,
                 "part_orientee": 0.7, "interstices_traverses": 1.0,
                 "accord_de_linterstice": 0.5, "en_butee": 0.1}
            e[porte_par] = q
            out.append(e)
        return out

    # ⭐ Le cas où la réponse est connue : le taux est porté par la planarité, le rayon la suit.
    pm = fabrique()
    s = ce_qui_suit_le_taux(pm)
    v("la covariable porteuse est vue", s["libres"]["planarite"]["p_taux"] < 0.001,
      f"rho {s['libres']['planarite']['rho_avec_le_taux']:+.3f}")
    d = le_rayon_survit_il(pm, "planarite")
    v("... et le rayon NE survit PAS quand elle est tenue", not d["le_rayon_survit"],
      f"brut {d['rho_brut']:+.3f} → partiel {d['rho_partiel']:+.3f}")
    v("... ce qui se lit comme une part expliquée élevée", d["part_expliquee"] > 0.8,
      f"{d['part_expliquee']:.0%}")

    # ⭐⭐ LA sonde : si le rayon porte le taux SANS passer par une covariable, il doit SURVIVRE.
    # Sans ce cas, un test qui répondrait toujours « non » passerait le contrôle du dessus.
    pm2 = fabrique(porte_par="pas_um")          # la porteuse est ailleurs
    for i, m in enumerate(pm2):                  # et la planarité ne dit rien
        m["planarite"] = 0.5 + 0.001 * (i % 3)
    d2 = le_rayon_survit_il(pm2, "planarite")
    v("sonde : le rayon SURVIT à une covariable qui ne dit rien", d2["le_rayon_survit"],
      f"partiel {d2['rho_partiel']:+.3f}, p {d2['p_partiel']:.4f}")

    # ⚠ Une covariable constante est INDÉCIDABLE, jamais « pas de lien » : rendre « aucun effet »
    # pour une colonne qui ne varie pas ferait lire une absence de données comme un résultat.
    pm3 = fabrique()
    for m in pm3:
        m["score_du_balayage"] = 5.0
    v("une covariable constante est indécidable",
      not ce_qui_suit_le_taux(pm3)["libres"]["score_du_balayage"]["decidable"])
    v("... et le test décisif la refuse aussi",
      not le_rayon_survit_il(pm3, "score_du_balayage")["decidable"])

    # ⚠⚠ Les trois termes du prédicat sont écartés de la table des libres, et nommés.
    v("les covariables du critère ne sont pas dans les libres",
      all(c not in COVARIABLES_LIBRES for c in COVARIABLES_DU_CRITERE))
    v("... et elles sont rendues à part, pour servir de témoin positif",
      set(s["du_critere"]) == set(COVARIABLES_DU_CRITERE))
    v("`feuilles_franchies` est écartée pour PARENTÉ, pas oubliée",
      "feuilles_franchies" in SUSPECTE and "feuilles_franchies" not in COVARIABLES_LIBRES)

    # ⭐⭐ Le témoin, dans ses deux sens.
    t = temoin_du_test(pm)
    v("le témoin négatif détruit le lien", t["negatif_taux_permutes"][
        "part_des_permutations_au_moins_aussi_forte"] < 0.05,
      f"part {t['negatif_taux_permutes']['part_des_permutations_au_moins_aussi_forte']:.4f}")
    t2 = temoin_du_test(fabrique(bruit=10.0, graine=3))
    v("... et sur du bruit pur, le lien réel n'est plus distinguable",
      t2["negatif_taux_permutes"]["part_des_permutations_au_moins_aussi_forte"] > 0.05,
      f"part {t2['negatif_taux_permutes']['part_des_permutations_au_moins_aussi_forte']:.4f}")

    # ⚠ La médiane et non la moyenne : une covariable qui sature doit être lue par sa médiane.
    course = {"lignes": [{"rayon_mm": 4.0, "detail": [{"etapes": [
        {"confirme": True, "planarite": 0.5, "score_du_balayage": 1.0,
         "desaccord_des_moities_deg": 5.0, "pas_um": 200.0, "oriente": True,
         "interstices_traverses": 1, "accord_de_linterstice": 0.5, "en_butee": False}
        for _ in range(19)] + [
        {"confirme": False, "planarite": 0.5, "score_du_balayage": 1.0,
         "desaccord_des_moities_deg": 90.0, "pas_um": 200.0, "oriente": False,
         "interstices_traverses": 3, "accord_de_linterstice": 0.0, "en_butee": True}]}]}]}
    m = marches(course)[0]
    v("un pas muet ne tire pas la médiane du désaccord", m["desaccord_des_moities_deg"] == 5.0,
      f"médiane {m['desaccord_des_moities_deg']}")
    v("le taux est celui des étapes lues", abs(m["taux"] - 19 / 20) < 1e-9)
    v("la part orientée est une MOYENNE de booléens", abs(m["part_orientee"] - 0.95) < 1e-9)

    # ⭐⭐⭐⭐ LE PAS AVEUGLE, ET LE DRAPEAU QUI LE DÉCLARE ORIENTÉ.
    def etape(d, pl, conf=False, ori=True):
        return {"confirme": conf, "oriente": ori, "desaccord_des_moities_deg": d,
                "planarite": pl, "score_du_balayage": 1.0, "pas_um": 200.0,
                "interstices_traverses": 1, "accord_de_linterstice": 0.5, "en_butee": False}

    v("un cube vide est aveugle", est_aveugle(etape(0.0, 0.0)))
    v("une vraie feuille ne l'est pas", not est_aveugle(etape(5.1, 0.68)))
    # ⚠⚠ LA sonde de la signature CONJOINTE : un seul des deux critères classerait mal. Un
    # désaccord nul sur une matière planaire arrive (deux moitiés qui s'accordent vraiment) ;
    # c'est la CONJONCTION qui ne peut venir que d'un cube sans matière.
    v("sonde : un désaccord nul sur une VRAIE planarité n'est pas aveugle",
      not est_aveugle(etape(0.0, 0.68)))
    v("sonde : une planarité nulle avec un vrai désaccord non plus",
      not est_aveugle(etape(12.0, 0.0)))

    course_ko = {"lignes": [{"rayon_mm": 4.0, "detail": [{"etapes":
                 [etape(0.0, 0.0) for _ in range(5)] + [etape(5.0, 0.6, True) for _ in range(5)]}]}]}
    o = le_vide_est_il_declare_oriente(course_ko)
    v("les pas aveugles sont comptés", o["pas_aveugles"] == 5, f"{o['pas_aveugles']}/10")
    v("... aucun ne confirme", o["aveugles_confirmes"] == 0)
    v("⛔ le vide déclaré orienté est SIGNALÉ", o["le_vide_passe_pour_oriente"],
      f"{o['aveugles_declares_orientes']}/{o['pas_aveugles']}")
    # ⚠⚠ LA sonde qui compte : un drapeau CORRECT ne doit pas être signalé. Sans elle, une garde
    # qui répondrait « défaut » à tout passerait le contrôle du dessus.
    course_ok = {"lignes": [{"rayon_mm": 4.0, "detail": [{"etapes":
                 [etape(0.0, 0.0, ori=False) for _ in range(5)]
                 + [etape(5.0, 0.6, True) for _ in range(5)]}]}]}
    v("sonde : un drapeau qui refuse le vide n'est PAS signalé",
      not le_vide_est_il_declare_oriente(course_ok)["le_vide_passe_pour_oriente"])

    # ⭐⭐⭐⭐ Le rayon, une fois les marches aveugles écartées.
    def marche(r, taux, aveugles=0, pas=20):
        return {"rayon_mm": r, "pas": pas, "confirmes": int(taux * pas), "taux": taux,
                "pas_aveugles": aveugles, "aveugle_des_le_depart": aveugles == pas}

    # douze marches voyantes au même taux, six aveugles au grand rayon : le rho brut est porté
    # par les aveugles et doit S'EFFONDRER sur les voyantes.
    pm4 = ([marche(4.0 + i, 0.75 + 0.01 * (i % 3)) for i in range(12)]
           + [marche(20.0 + i, 0.0, aveugles=20) for i in range(6)])
    d4 = le_rayon_survit_il_aux_marches_voyantes(pm4)
    # ⚠ L'assertion porte sur ce qui est REVENDIQUÉ — le brut rejette, les voyantes non — et pas
    # sur une valeur de rho. Ma première version exigeait |rho| > 0,7 ; l'arithmétique en rend
    # 0,624 sur cette fixture, et le contrôle a attrapé mon attendu deviné plutôt qu'un défaut.
    v("le rho brut rejette quand les aveugles sont au grand rayon",
      d4["p_sur_toutes"] < 0.05 and d4["rho_sur_toutes"] < 0,
      f"{d4['rho_sur_toutes']:+.3f}, p {d4['p_sur_toutes']:.4f}")
    v("... et il NE survit PAS aux voyantes", not d4["le_rayon_survit_aux_voyantes"],
      f"{d4['rho_sur_les_voyantes']:+.3f}, p {d4['p_sur_les_voyantes']:.3f}")
    # ⚠⚠ LA sonde symétrique : si le taux baisse VRAIMENT avec le rayon sur des marches toutes
    # voyantes, le rayon doit SURVIVRE. Sans elle, un test répondant toujours « non » passerait.
    pm5 = [marche(4.0 + i, max(0.05, 0.95 - 0.05 * i)) for i in range(18)]
    d5 = le_rayon_survit_il_aux_marches_voyantes(pm5)
    v("sonde : un vrai effet du rayon SURVIT aux voyantes", d5["le_rayon_survit_aux_voyantes"],
      f"{d5['rho_sur_les_voyantes']:+.3f}, p {d5['p_sur_les_voyantes']:.2e}")
    v("moins de six marches voyantes est indécidable",
      not le_rayon_survit_il_aux_marches_voyantes(pm4[:3] + pm4[12:])["decidable"])

    # ⚠ Une course incomplète est refusée plutôt que mesurée à moitié.
    import tempfile
    with tempfile.TemporaryDirectory() as dd:
        p = Path(dd) / "c.json"
        p.write_text(json.dumps({"course_incomplete": True, "lignes": []}), encoding="utf-8")
        try:
            mesurer(p)
            v("une course incomplète est refusée", False)
        except ValueError:
            v("une course incomplète est refusée", True)
        p.write_text(json.dumps({"lignes": []}), encoding="utf-8")
        try:
            mesurer(p)
            v("une course sans marche est refusée", False)
        except ValueError:
            v("une course sans marche est refusée", True)

        # ⚠ Et une course VALIDE traverse `mesurer` PUIS `afficher`. Sans ce passage, le chemin
        # qui met les nombres sous les yeux n'est exercé par rien — donc une `KeyError` dans
        # l'affichage n'apparaîtrait qu'au moment de publier, sur la seule exécution qui compte.
        pleine = {"lignes": [{"rayon_mm": 4.0 + i, "detail": [{"etapes":
                  [etape(0.0, 0.0) for _ in range(3 if i >= 12 else 0)]
                  + [etape(5.0 + (i % 4), 0.4 + 0.05 * (i % 5), (i + k) % 3 == 0)
                     for k in range(20 - (3 if i >= 12 else 0))]}]}
                  for i in range(18)]}
        p.write_text(json.dumps(pleine), encoding="utf-8")
        r = mesurer(p)
        v("une course valide est mesurée", r["marches"] == 18, f"{r['marches']}")
        v("... et ses trois sections sont rendues",
          all(k in r for k in ("le_vide_est_il_declare_oriente", "temoin",
                               "le_rayon_survit_il_aux_marches_voyantes")))
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
