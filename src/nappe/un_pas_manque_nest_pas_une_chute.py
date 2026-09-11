#!/usr/bin/env python3
"""Un pas non confirme est-il une CHUTE ? — la portee publiee est une lecture, pas une matiere.

⚠⚠⚠ POURQUOI CE FICHIER, ET IL VIENT D'UNE SONDE SUR DES DONNEES DEJA PAYEES. `102` a publie que
« la matiere porte deux pas confirmes » et `107` l'a refait avec le bon pas. Les deux comptent les
pas confirmes **CONSECUTIFS DEPUIS LE DEPART**. Or ce compte est BORNE PAR LA POSITION DU PREMIER
MANQUE : une marche qui confirme cinq pas sur six mais manque le deuxieme vaut **un**, exactement
comme une marche qui s'effondre au premier. Ce n'est pas un defaut de mesure, c'est un defaut de
DEFINITION, et il se demontre par l'arithmetique avant d'etre mesure.

⭐⭐⭐ ET LE CHIFFRE QUE CELA DEPLACE EST CELUI QUI A DECLARE LE GRAAL MORT. `107` calcule la survie
de cent vingt spires comme `(1 - risque)^120` en traitant un pas non confirme comme une CHUTE. Si
un manque est rattrapable — si la marche continue de franchir ses feuilles a travers lui — alors ce
n'est pas une chute mais une **confirmation manquee**, et l'exponentielle ne s'applique pas.

⭐⭐⭐ LE TEST QUI TRANCHE N'EST PAS CIRCULAIRE, ET C'EST LE GROUPEMENT DES MANQUES. Une marche qui
se PERD manque ses pas en rafale : une fois a cote de la feuille, elle y reste. Une marche qui
franchit correctement mais dont le critere rate une confirmation manque au hasard. La difference se
mesure sans jamais regarder le registre du trajet : on compare la plus longue rafale de manques a
ce qu'un tirage independant de MEME TAUX produirait.

⚠⚠ CE QUE CE FICHIER NE REVENDIQUE PAS. Six pas ne sont pas cent vingt, le mode qui ne compte rien
existe toujours, et rien ici ne dit qu'un marcheur tiendrait une spire entiere. Ce qui est montre
est que **la portee publiee mesurait une lecture du critere**, et que sous l'autre lecture les
memes donnees disent autre chose.

Usage :
    uv run python src/nappe/un_pas_manque_nest_pas_une_chute.py --verifier
    uv run python src/nappe/un_pas_manque_nest_pas_une_chute.py \\
        --json docs/mesures/un_pas_manque_nest_pas_une_chute.json
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

CHEMIN_DE_107 = RACINE / "docs" / "mesures" / "le_marcheur_avec_le_bon_pas.json"

# ⚠ Le seuil de mode vient de `107` et n'est pas regle ici, exactement comme dans `108` : le
# redefinir ferait de cette tranche le juge de sa propre partition.
PART_DU_COMPTE_ATTENDU = 0.5
SPIRES = 120
TIRAGES = 5000
GRAINE = 109


def run_depuis_le_depart(conf) -> int:
    """Le compte de pas confirmes CONSECUTIFS depuis le depart — la lecture que `102` publie.

    ⚠⚠⚠ ELLE EST BORNEE PAR LA POSITION DU PREMIER MANQUE, et c'est tout le sujet de la tranche.
    Sur `[True, False, True, True, True, True]` elle rend **un** alors que cinq pas sur six sont
    confirmes. Elle ne peut donc pas prendre la valeur qui signale la reussite partielle : c'est le
    peche recense de ce depot — *une quantite qui ne peut pas prendre la valeur qui signale ce
    qu'on cherche*.
    """
    n = 0
    for v in conf:
        if not v:
            break
        n += 1
    return n


def plus_longue_rafale_de_manques(conf) -> int:
    """La plus longue suite de pas NON confirmes, qui est la forme qu'une chute prend.

    ⭐ Une marche qui se perd reste perdue : ses manques se suivent. Une marche qui franchit
    correctement mais dont le critere rate une confirmation manque au hasard. C'est cette
    difference-la que le nul teste, et elle ne regarde jamais le registre du trajet.
    """
    meilleur = courant = 0
    for v in conf:
        courant = 0 if v else courant + 1
        meilleur = max(meilleur, courant)
    return meilleur


def attendu_geometrique(taux: float, pas: int) -> float:
    """L'esperance du run depuis le depart si les manques etaient INDEPENDANTS, de meme taux.

    ⭐⭐⭐ ELLE EST LA DEMONSTRATION, PAS UNE MESURE. Sous des manques independants de taux `p`, le
    run depuis le depart vaut `p + p^2 + ... + p^k` — donc il est entierement determine par `p`. Si
    l'observe y colle, le compte consecutif ne porte AUCUNE information que le taux ne porte deja,
    et publier « la matiere porte deux pas » est une facon couteuse de dire « le critere confirme
    huit fois sur dix ».
    """
    return float(sum(taux ** k for k in range(1, pas + 1)))


def confirmations_de_107(brut: dict,
                         part: float = PART_DU_COMPTE_ATTENDU) -> list[dict]:
    """Une ligne par marche : ses confirmations pas a pas, son mode, son registre.

    ⚠ Une marche dont le registre du trajet n'est pas decidable est gardee mais son mode vaut
    None : « le profil est plat » n'est pas « la marche n'a rien franchi », et la ranger dans le
    mode bas mettrait dans une population des marches dont on ne sait rien. Les comptes par mode
    l'ecartent ; les comptes globaux la gardent, parce que ses confirmations, elles, sont lues.
    """
    out = []
    for ligne in brut.get("lignes", []):
        for cellule in ligne.get("detail", []):
            for sel in ("calibre", "deux_roles"):
                m = cellule.get(sel)
                if not m or not m.get("etapes"):
                    continue
                conf = [bool(x.get("confirme")) for x in m["etapes"]]
                t = m.get("trajet_entier") or {}
                mode = None
                if t.get("decidable"):
                    mode = bool(float(t["feuilles_franchies"])
                                >= part * int(t["pas_parcourus"]))
                out.append({
                    "bande": int(ligne["de"]), "selecteur": sel,
                    "rayon_mm": float(ligne["rayon_mm"]),
                    "confirmations": conf, "pas": len(conf),
                    "confirmes": int(sum(conf)),
                    "run_depuis_le_depart": run_depuis_le_depart(conf),
                    "plus_longue_rafale": plus_longue_rafale_de_manques(conf),
                    "mode_haut": mode,
                    "feuilles_par_pas": (None if not t.get("decidable") else
                                         round(float(t["feuilles_franchies"])
                                               / max(int(t["pas_parcourus"]), 1), 3))})
    return out


def ce_que_la_lecture_consecutive_jette(marches: list[dict]) -> dict:
    """Combien de marches confirment presque tout et sont creditees de presque rien ?

    ⭐⭐⭐ C'EST LE CHIFFRE DE LA TRANCHE, ET IL NE DEMANDE AUCUN MODELE. Les deux colonnes sont
    deux lectures des MEMES pas ; leur ecart est entierement du a la definition du run. Publier les
    deux distributions cote a cote est ce qui rend visible qu'un seul nombre a ete publie.
    """
    if not marches:
        return {"decidable": False, "pourquoi": "aucune marche"}
    k = max(x["pas"] for x in marches)
    tot = np.bincount([x["confirmes"] for x in marches], minlength=k + 1).tolist()
    run = np.bincount([x["run_depuis_le_depart"] for x in marches],
                      minlength=k + 1).tolist()
    presque = [x for x in marches if x["confirmes"] >= k - 1]
    jetees = [x for x in presque if x["run_depuis_le_depart"] <= 1]
    return {"decidable": True, "marches": len(marches), "pas": k,
            "distribution_des_confirmes": tot,
            "distribution_du_run": run,
            "confirment_presque_tout": len(presque),
            "... et sont creditees de zero ou un": len(jetees),
            "part_jetee_parmi_les_presque_complets": round(
                len(jetees) / len(presque), 3) if presque else None,
            "confirmes_median": float(np.median([x["confirmes"] for x in marches])),
            "run_median": float(np.median([x["run_depuis_le_depart"] for x in marches])),
            # ⭐⭐⭐ LE VERDICT : les deux lectures rendent-elles des nombres differents ? Si elles
            # coincidaient, la tranche n'aurait rien a dire.
            "les_deux_lectures_different": bool(
                float(np.median([x["confirmes"] for x in marches]))
                != float(np.median([x["run_depuis_le_depart"] for x in marches])))}


def le_run_est_il_une_paraphrase_du_taux(marches: list[dict],
                                         tolerance: float = 0.75) -> dict:
    """Le run observe colle-t-il a ce que des manques INDEPENDANTS de meme taux produiraient ?

    ⭐⭐ S'IL Y COLLE, LE RUN NE PORTE RIEN QUE LE TAUX NE PORTE DEJA — donc « la matiere porte deux
    pas » est une facon couteuse de dire « le critere confirme sept fois sur dix », et c'est la
    seconde moitie de la demonstration.

    ⚠ La tolerance est en PAS, pas en pourcentage, parce que c'est en pas que le chiffre est
    publie : trois quarts de pas est plus fin que le cran auquel `102` et `107` rapportent leur
    portee (un pas entier).
    """
    if not marches:
        return {"decidable": False, "pourquoi": "aucune marche"}
    k = max(x["pas"] for x in marches)
    taux = float(np.mean([x["confirmes"] / max(x["pas"], 1) for x in marches]))
    att = attendu_geometrique(taux, k)
    obs = float(np.mean([x["run_depuis_le_depart"] for x in marches]))
    return {"decidable": True, "marches": len(marches), "pas": k,
            "taux_de_confirmation": round(taux, 4),
            "run_moyen_observe": round(obs, 3),
            "run_moyen_si_les_manques_sont_independants": round(att, 3),
            "ecart_en_pas": round(obs - att, 3),
            "le_run_est_une_paraphrase_du_taux": bool(abs(obs - att) <= tolerance)}


def les_manques_sont_ils_groupes(marches: list[dict], tirages: int = TIRAGES,
                                 graine: int = GRAINE) -> dict:
    """Les manques se suivent-ils PLUS que si chaque pas manquait independamment ?

    ⭐⭐⭐ C'EST LE TEST QUI TRANCHE, ET IL NE REGARDE JAMAIS LE REGISTRE DU TRAJET. Une marche qui
    se PERD manque en rafale : une fois a cote de la feuille elle y reste, donc sa plus longue
    rafale est plus longue qu'un tirage independant n'en produirait. Une marche qui franchit
    correctement et dont le critere rate une confirmation manque au hasard. La question « un
    manque est-il une chute ? » devient donc une question sur le GROUPEMENT, mesurable sans
    circularite.

    ⚠⚠ LE NUL CONSERVE LE TAUX DE CHAQUE MARCHE, pas seulement le taux global : une marche qui
    confirme deux pas sur six produit des rafales longues sans etre perdue pour autant, et un nul
    a taux commun le lui reprocherait. Ce qui est teste est le groupement A TAUX EGAL.

    ⚠⚠⚠ ET CE NUL EST CONSERVATEUR, DONC « NON GROUPE » NE VEUT PAS DIRE « AUCUN GROUPEMENT ». Il
    ne detecte que ce qui depasse ce que le taux de la marche explique deja. A taux eleve une
    rafale saute aux yeux, donc un « non » y est informatif ; a taux moyen une rafale est banale,
    donc un « non » y dit surtout que le test manque de puissance. La lecture doit donc se faire
    PAR MODE, avec le taux de chaque mode a cote du verdict.
    """
    if len(marches) < 4:
        return {"decidable": False, "pourquoi": "moins de quatre marches"}
    obs = float(np.mean([x["plus_longue_rafale"] for x in marches]))
    rng = np.random.default_rng(graine)
    taux = np.asarray([x["confirmes"] / max(x["pas"], 1) for x in marches])
    k = np.asarray([x["pas"] for x in marches])
    nul = np.empty(tirages)
    for t in range(tirages):
        val = []
        for p, n in zip(taux, k):
            val.append(plus_longue_rafale_de_manques(rng.random(n) < p))
        nul[t] = float(np.mean(val))
    p_val = float((np.sum(nul >= obs) + 1) / (tirages + 1))
    return {"decidable": True, "marches": len(marches), "tirages": int(tirages),
            "rafale_moyenne_observee": round(obs, 3),
            "rafale_moyenne_sous_lindependance": round(float(nul.mean()), 3),
            "p95_du_nul": round(float(np.percentile(nul, 95)), 3),
            "p_les_manques_sont_groupes": round(p_val, 4),
            # ⭐ Le verdict, et il peut dire NON — c'est ce qui en fait un test.
            "les_manques_sont_groupes": bool(p_val < 0.05)}


def le_nul_a_taux_commun_se_trompe(marches: list[dict], tirages: int = 2000,
                                   graine: int = GRAINE + 1) -> dict:
    """Ce que rendrait le meme test avec un nul a taux COMMUN, et pourquoi c'est faux.

    ⭐⭐ ELLE DEMONTRE UN CHOIX DE CONCEPTION AU LIEU DE L'ARGUMENTER. Un nul qui donne a toutes les
    marches le taux MOYEN reproche a une marche qui confirme deux pas sur six d'avoir des rafales
    longues — alors qu'a ce taux-la des rafales longues sont la norme, pas un symptome. Le
    groupement se teste A TAUX EGAL ; ma premiere sonde ne le faisait pas, et elle declarait le
    mode bas groupe a p = 0,04.

    ⚠ Elle n'est pas un second verdict : elle est le chiffre qui dit combien le mauvais nul se
    trompe, et il est publie a cote du bon.
    """
    if len(marches) < 4:
        return {"decidable": False, "pourquoi": "moins de quatre marches"}
    obs = float(np.mean([x["plus_longue_rafale"] for x in marches]))
    taux = float(np.mean([x["confirmes"] / max(x["pas"], 1) for x in marches]))
    k = np.asarray([x["pas"] for x in marches])
    rng = np.random.default_rng(graine)
    nul = np.empty(tirages)
    for t in range(tirages):
        nul[t] = float(np.mean([plus_longue_rafale_de_manques(rng.random(n) < taux)
                                for n in k]))
    p_val = float((np.sum(nul >= obs) + 1) / (tirages + 1))
    return {"decidable": True, "taux_commun": round(taux, 4),
            "p_avec_un_nul_a_taux_commun": round(p_val, 4),
            "declare_groupe_a_taux_commun": bool(p_val < 0.05)}


def un_manque_coute_t_il_des_feuilles(marches: list[dict],
                                      tirages: int = 4000,
                                      graine: int = GRAINE + 2) -> dict:
    """DANS le mode qui compte, une marche qui manque un pas compte-t-elle plus MAL ?

    ⭐⭐⭐ C'EST LA SECONDE MOITIE DE « UN MANQUE N'EST PAS UNE CHUTE ». La premiere montre que les
    manques ne se suivent pas ; celle-ci demande ce qu'ils coutent au compte de feuilles.

    ⚠⚠⚠ ET CE QUI SE MESURE EST L'ECART A UN, JAMAIS LE NOMBRE BRUT. Ma premiere version lisait
    « plus de feuilles » comme « mieux » et rendait donc le verdict a l'envers : la cible d'un pas
    juste est **exactement une feuille**, donc franchir 1,29 est aussi faux que franchir 0,71, et
    dans l'autre sens. C'est la faute que `104` avait deja nommee — le critere accepte de 0,68 a
    1,38 — reecrite dans une fonction qui devait la mesurer.

    ⚠⚠ LA COMPARAISON EST FAITE A L'INTERIEUR DU MODE HAUT, et c'est ce qui la rend non circulaire :
    l'appartenance au mode est la meme pour les deux groupes, seul le nombre de manques varie.
    Comparer les deux MODES serait tautologique, puisque le mode est defini par le registre. Et les
    deux instruments sont independants : le compte de confirmations vient du critere pas a pas, le
    compte de feuilles du profil de la polyligne entiere.

    ⚠ L'effectif est rendu avec le resultat : trois marches d'un cote ne decident de rien.
    """
    jeu = [x for x in marches if x["mode_haut"] is True
           and x["feuilles_par_pas"] is not None]
    if len(jeu) < 6:
        return {"decidable": False, "pourquoi": "moins de six marches dans le mode haut"}
    complets = [x for x in jeu if x["confirmes"] == x["pas"]]
    manquants = [x for x in jeu if x["confirmes"] < x["pas"]]
    if len(complets) < 3 or len(manquants) < 3:
        return {"decidable": False,
                "pourquoi": "un des deux groupes a moins de trois marches"}
    a = float(np.median([x["feuilles_par_pas"] for x in complets]))
    b = float(np.median([x["feuilles_par_pas"] for x in manquants]))
    ea = np.asarray([abs(x["feuilles_par_pas"] - 1.0) for x in complets])
    eb = np.asarray([abs(x["feuilles_par_pas"] - 1.0) for x in manquants])
    # ⚠ Le nul echange les etiquettes « complete » et « avec manque » : c'est le seul nul qui
    # teste ce qui est affirme, a savoir que le NOMBRE DE MANQUES change l'ecart a un.
    obs = float(np.median(eb) - np.median(ea))
    tous = np.concatenate([ea, eb])
    rng = np.random.default_rng(graine)
    nul = np.empty(tirages)
    for t in range(tirages):
        idx = rng.permutation(tous.size)
        nul[t] = float(np.median(tous[idx[ea.size:]]) - np.median(tous[idx[:ea.size]]))
    p_val = float((np.sum(np.abs(nul) >= abs(obs)) + 1) / (tirages + 1))
    return {"decidable": True,
            "marches_completes": len(complets), "marches_avec_manque": len(manquants),
            "feuilles_par_pas_des_completes": round(a, 3),
            "feuilles_par_pas_des_manquantes": round(b, 3),
            "ecart_a_un_des_completes": round(float(np.median(ea)), 3),
            "ecart_a_un_des_manquantes": round(float(np.median(eb)), 3),
            "difference_des_ecarts": round(obs, 3),
            "p_bilaterale": round(p_val, 4),
            # ⚠⚠ « Compte plus mal » veut dire « s'ecarte PLUS de un ». Une marche qui franchit
            # 1,29 feuille par pas ne compte pas mieux qu'une qui en franchit 1,00 : elle depasse.
            "un_manque_fait_compter_plus_mal": bool(obs > 0.0),
            "les_completes_depassent": bool(a > 1.0),
            "le_depassement_des_completes": round(a - 1.0, 3)}


def ce_que_ca_change_pour_la_survie(taux: float, spires: int = SPIRES,
                                    pas_par_spire: float = 1.0) -> dict:
    """Les deux arithmetiques enchainees, cote a cote : le manque comme CHUTE, ou comme MANQUE.

    ⚠⚠⚠ ELLE NE PROUVE PAS QU'UN MARCHEUR TIENT CENT VINGT SPIRES. Elle montre que les deux
    lectures d'un meme taux rendent deux nombres separes par des ordres de grandeur, donc que le
    nombre publie depend d'une hypothese — « un manque est une chute » — qui n'avait jamais ete
    testee. Le test, lui, est dans `les_manques_sont_groupes`.

    ⚠ La lecture « chute » est exactement celle de `107` : chaque pas non confirme termine la
    marche, donc la survie est `taux^n`. La lecture « manque » suppose que la marche continue, donc
    ce qui compte n'est plus la survie mais la DERIVE, et elle est rendue a part parce qu'un
    nombre de spires n'est pas une probabilite.
    """
    n = int(round(spires * pas_par_spire))
    survie = float(taux) ** n
    return {"pas_enchaines": n, "taux_de_confirmation": round(float(taux), 4),
            "survie_si_un_manque_est_une_chute": survie,
            "manques_attendus_si_un_manque_est_un_manque": round((1.0 - float(taux)) * n, 1),
            "rapport_des_deux_lectures": (None if survie <= 0.0 else
                                          round(1.0 / survie, 1)),
            "ce_que_la_seconde_lecture_ne_dit_pas":
                "qu'un marcheur tient cent vingt spires : elle dit que le nombre publie depend "
                "d'une hypothese qui n'avait pas ete testee"}


def par_mode(marches: list[dict], tirages: int = TIRAGES,
             graine: int = GRAINE) -> dict:
    """Les memes mesures, separees par le mode que `107` a trouve."""
    out = {}
    for nom, garde in (("mode_haut", lambda x: x["mode_haut"] is True),
                       ("mode_bas", lambda x: x["mode_haut"] is False),
                       ("sans_registre", lambda x: x["mode_haut"] is None)):
        jeu = [x for x in marches if garde(x)]
        if not jeu:
            out[nom] = {"marches": 0}
            continue
        out[nom] = {
            "marches": len(jeu),
            "taux_de_confirmation": round(
                float(np.mean([x["confirmes"] / max(x["pas"], 1) for x in jeu])), 4),
            "confirmes_median": float(np.median([x["confirmes"] for x in jeu])),
            "run_median": float(np.median([x["run_depuis_le_depart"] for x in jeu])),
            "paraphrase": le_run_est_il_une_paraphrase_du_taux(jeu),
            "groupement": les_manques_sont_ils_groupes(jeu, tirages, graine)}
    return out


def mesurer(chemin: Path = CHEMIN_DE_107, tirages: int = TIRAGES,
            graine: int = GRAINE) -> dict:
    """La tranche entiere, sur les etapes que `107` a gardees. Zero lecture distante."""
    brut = json.loads(Path(chemin).read_text())
    marches = confirmations_de_107(brut)
    r = {"source": str(Path(chemin).relative_to(RACINE)),
         "fragment": brut.get("fragment"), "volume_fin": brut.get("volume_fin"),
         "marches": len(marches),
         "portee_publiee_par_107": (brut.get("resume") or {}).get(
             "pas_confirmes_corrige"),
         "ce_que_la_lecture_consecutive_jette": ce_que_la_lecture_consecutive_jette(marches),
         "paraphrase": le_run_est_il_une_paraphrase_du_taux(marches),
         "groupement": les_manques_sont_ils_groupes(marches, tirages, graine),
         "nul_a_taux_commun": le_nul_a_taux_commun_se_trompe(marches),
         "un_manque_coute_t_il_des_feuilles": un_manque_coute_t_il_des_feuilles(marches),
         "par_mode": par_mode(marches, tirages, graine)}
    taux = r["paraphrase"].get("taux_de_confirmation")
    if taux is not None:
        r["survie"] = ce_que_ca_change_pour_la_survie(taux)
        h = r["par_mode"].get("mode_haut", {})
        if h.get("taux_de_confirmation") is not None:
            r["survie_du_mode_haut"] = ce_que_ca_change_pour_la_survie(
                h["taux_de_confirmation"])
    return r


def afficher(r: dict) -> None:
    j = r.get("ce_que_la_lecture_consecutive_jette", {})
    print(f"\n{r.get('fragment')} · {r['marches']} marches de `107` · "
          f"portée publiée {r.get('portee_publiee_par_107')} pas confirmés\n")
    if j.get("decidable"):
        print(f"{'pas confirmés sur ' + str(j['pas']):>26} : "
              + "  ".join(f"{k}→{v}" for k, v in enumerate(j["distribution_des_confirmes"])))
        print(f"{'run depuis le départ':>26} : "
              + "  ".join(f"{k}→{v}" for k, v in enumerate(j["distribution_du_run"])))
        print(f"\n★★★ {j['confirment_presque_tout']} marches confirment "
              f"{j['pas'] - 1} ou {j['pas']} pas sur {j['pas']}, et "
              f"{j['... et sont creditees de zero ou un']} d'entre elles sont créditées de "
              f"ZÉRO ou UN")
        print(f"    médiane des confirmés {j['confirmes_median']} contre médiane du run "
              f"{j['run_median']}")
    p = r.get("paraphrase", {})
    if p.get("decidable"):
        print(f"\nLE RUN EST-IL UNE PARAPHRASE DU TAUX ? "
              f"{'OUI' if p['le_run_est_une_paraphrase_du_taux'] else 'NON'}")
        print(f"   taux {p['taux_de_confirmation']} · run observé "
              f"{p['run_moyen_observe']} · attendu sous l'indépendance "
              f"{p['run_moyen_si_les_manques_sont_independants']} · écart "
              f"{p['ecart_en_pas']:+.3f} pas")
    g = r.get("groupement", {})
    if g.get("decidable"):
        print(f"\n★★★ LES MANQUES SONT-ILS GROUPÉS (donc des CHUTES) ? "
              f"{'OUI' if g['les_manques_sont_groupes'] else 'NON'}")
        print(f"   rafale moyenne {g['rafale_moyenne_observee']} contre "
              f"{g['rafale_moyenne_sous_lindependance']} sous l'indépendance "
              f"(p95 {g['p95_du_nul']}) · p = {g['p_les_manques_sont_groupes']}")
    nc = r.get("nul_a_taux_commun", {})
    if nc.get("decidable") and g.get("decidable"):
        print(f"   ⚠ avec un nul à taux COMMUN — celui de ma première sonde — le même test rend "
              f"p = {nc['p_avec_un_nul_a_taux_commun']} "
              f"({'groupé' if nc['declare_groupe_a_taux_commun'] else 'non groupé'}) : "
              f"le groupement se teste À TAUX ÉGAL")
    c = r.get("un_manque_coute_t_il_des_feuilles", {})
    if c.get("decidable"):
        print(f"\n★★★ DANS LE MODE QUI COMPTE, UN MANQUE FAIT-IL COMPTER PLUS MAL ? "
              f"{'OUI' if c['un_manque_fait_compter_plus_mal'] else 'NON'}")
        print(f"   {c['marches_completes']} marches complètes à "
              f"{c['feuilles_par_pas_des_completes']} feuille par pas contre "
              f"{c['marches_avec_manque']} avec manque à "
              f"{c['feuilles_par_pas_des_manquantes']}")
        print(f"   écart À UN : {c['ecart_a_un_des_completes']} contre "
              f"{c['ecart_a_un_des_manquantes']} — différence "
              f"{c['difference_des_ecarts']:+.3f}, p = {c['p_bilaterale']}")
        if c["les_completes_depassent"]:
            print(f"   ⚠⚠ et les marches ENTIÈREMENT confirmées DÉPASSENT de "
                  f"{c['le_depassement_des_completes']:+.3f} feuille par pas : le critère "
                  f"confirme des pas qui traversent trop")
    print("\nPAR MODE")
    print(f"   {'':<16} {'marches':>8} {'taux':>7} {'confirmés':>10} {'run':>6} "
          f"{'groupés ?':>10} {'p':>8}")
    for nom, m in (r.get("par_mode") or {}).items():
        if not m.get("marches"):
            continue
        gg = m.get("groupement", {})
        print(f"   {nom:<16} {m['marches']:>8} {m['taux_de_confirmation']:>7.3f} "
              f"{m['confirmes_median']:>10.1f} {m['run_median']:>6.1f} "
              f"{str(gg.get('les_manques_sont_groupes')):>10} "
              f"{gg.get('p_les_manques_sont_groupes', float('nan')):>8.4f}")
    for cle, titre in (("survie", "TOUTES LES MARCHES"),
                       ("survie_du_mode_haut", "LE MODE QUI COMPTE")):
        s = r.get(cle)
        if not s:
            continue
        print(f"\nCE QUE ÇA CHANGE POUR L'ARITHMÉTIQUE ENCHAÎNÉE — {titre}")
        print(f"   taux {s['taux_de_confirmation']} sur {s['pas_enchaines']} pas")
        print(f"   si un manque est une CHUTE : {s['survie_si_un_manque_est_une_chute']:.2e} "
              f"de survie")
        print(f"   si un manque est un MANQUE : "
              f"{s['manques_attendus_si_un_manque_est_un_manque']} confirmations manquées, "
              f"et la marche continue")
    print(f"\n⚠ {(r.get('survie') or {}).get('ce_que_la_seconde_lecture_ne_dit_pas', '')}")


def _marches(confs, modes=None) -> list[dict]:
    """Des marches fabriquees a partir de suites de confirmations ecrites a la main."""
    out = []
    for i, c in enumerate(confs):
        out.append({"bande": i, "selecteur": "fabrique", "rayon_mm": 10.0,
                    "confirmations": list(c), "pas": len(c),
                    "confirmes": int(sum(c)),
                    "run_depuis_le_depart": run_depuis_le_depart(c),
                    "plus_longue_rafale": plus_longue_rafale_de_manques(c),
                    "mode_haut": None if modes is None else modes[i],
                    "feuilles_par_pas": None})
    return out


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # === LES DEUX LECTURES D'UNE MEME SUITE ==================================================
    # ⚠⚠⚠ LE DEFAUT EST DANS LA DEFINITION, ET IL SE DEMONTRE SANS DONNEES : cinq pas confirmes
    # sur six valent UN des que le deuxieme manque. La garde l'ecrit en clair, parce que c'est
    # l'enonce que toute la tranche developpe.
    presque = [True, False, True, True, True, True]
    v("cinq pas confirmés sur six, dont le deuxième manque, sont crédités de UN",
      run_depuis_le_depart(presque) == 1 and sum(presque) == 5,
      f"run {run_depuis_le_depart(presque)}, confirmés {sum(presque)}")
    v("... et une marche qui s'effondre au premier pas est créditée de UN aussi",
      run_depuis_le_depart([True, False, False, False, False, False]) == 1)
    v("... donc les deux marches sont INDISCERNABLES par la lecture publiée",
      run_depuis_le_depart(presque)
      == run_depuis_le_depart([True, False, False, False, False, False]))
    v("une marche entièrement confirmée est créditée de tout",
      run_depuis_le_depart([True] * 6) == 6)
    v("... et une marche dont le premier pas manque, de rien",
      run_depuis_le_depart([False] + [True] * 5) == 0)

    # === LA PLUS LONGUE RAFALE ==============================================================
    v("la rafale d'une marche sans manque est nulle",
      plus_longue_rafale_de_manques([True] * 6) == 0)
    v("... celle d'une marche qui s'effondre au pas 3 vaut quatre",
      plus_longue_rafale_de_manques([True, True, False, False, False, False]) == 4)
    # ⚠ Deux manques ISOLES ne font pas une rafale de deux : c'est exactement ce qui distingue une
    # marche qui rate des confirmations d'une marche qui s'est perdue.
    v("... et deux manques isolés font une rafale de UN, pas de deux",
      plus_longue_rafale_de_manques([True, False, True, False, True, True]) == 1)

    # === LE RUN COMME PARAPHRASE DU TAUX ====================================================
    # ⭐⭐ L'ARITHMETIQUE D'ABORD : sous des manques independants, le run est entierement determine
    # par le taux. La valeur est verifiee a la main sur un cas ou elle se calcule de tete.
    v("l'attendu géométrique se calcule et vaut la somme des puissances",
      abs(attendu_geometrique(0.5, 3) - (0.5 + 0.25 + 0.125)) < 1e-12,
      f"{attendu_geometrique(0.5, 3)}")
    v("... et il vaut le nombre de pas quand tout est confirmé",
      abs(attendu_geometrique(1.0, 6) - 6.0) < 1e-12)
    v("... et zéro quand rien ne l'est", abs(attendu_geometrique(0.0, 6)) < 1e-12)
    rng = np.random.default_rng(4)
    tire = _marches([(rng.random(6) < 0.8).tolist() for _ in range(400)])
    pa = le_run_est_il_une_paraphrase_du_taux(tire)
    v("sur des manques tirés INDÉPENDAMMENT, le run est une paraphrase du taux",
      pa["le_run_est_une_paraphrase_du_taux"] is True,
      f"observé {pa['run_moyen_observe']} contre {pa['run_moyen_si_les_manques_sont_independants']}")
    # ⚠⚠ ET LA GARDE DOIT POUVOIR DIRE NON : des marches qui s'effondrent franchement rendent un
    # run bien plus COURT que le taux ne le prédit, parce que leurs manques sont groupés en fin
    # de marche. Sans ce contrôle, « paraphrase » serait un verdict qui ne peut pas échouer.
    chutes = _marches([[True] * k + [False] * (6 - k) for k in (5, 5, 5, 5)]
                      + [[False] * 6 for _ in range(6)])
    pb = le_run_est_il_une_paraphrase_du_taux(chutes)
    v("... et sur des marches qui s'effondrent, il ne l'est PAS",
      pb["le_run_est_une_paraphrase_du_taux"] is False,
      f"observé {pb['run_moyen_observe']} contre {pb['run_moyen_si_les_manques_sont_independants']}")

    # === LE GROUPEMENT DES MANQUES ==========================================================
    # ⭐⭐⭐ LA GARDE CENTRALE, ET ELLE DOIT TRANCHER DANS LES DEUX SENS. Une marche qui se PERD
    # manque en rafale ; une marche qui rate des confirmations manque au hasard. Si le test ne
    # savait pas distinguer les deux, toute la tranche reposerait sur rien.
    perdues = _marches([[True] * 2 + [False] * 4 for _ in range(20)])
    gp = les_manques_sont_ils_groupes(perdues, tirages=1500, graine=2)
    v("des marches qui se PERDENT ont des manques groupés",
      gp["les_manques_sont_groupes"] is True,
      f"rafale {gp['rafale_moyenne_observee']} contre "
      f"{gp['rafale_moyenne_sous_lindependance']}, p = {gp['p_les_manques_sont_groupes']}")
    epars = _marches([(np.random.default_rng(100 + i).random(6) < 0.667).tolist()
                      for i in range(40)])
    ge = les_manques_sont_ils_groupes(epars, tirages=1500, graine=2)
    v("... et des manques tirés au hasard ne le sont PAS",
      ge["les_manques_sont_groupes"] is False,
      f"p = {ge['p_les_manques_sont_groupes']}")
    # ⚠⚠ LE NUL CONSERVE LE TAUX DE CHAQUE MARCHE : sans cela, une marche qui confirme peu
    # produirait des rafales longues et serait declaree « perdue » pour son seul taux. Le controle
    # melange des taux tres differents sans aucun groupement.
    melange = _marches([[True] * 6, [True] * 6,
                        [True, False, True, False, True, False],
                        [False, True, False, True, False, True],
                        [True, False, True, True, False, True],
                        [False, True, True, False, True, False]] * 4)
    gm = les_manques_sont_ils_groupes(melange, tirages=1500, graine=2)
    v("... et un mélange de taux très différents sans groupement n'est pas déclaré groupé",
      gm["les_manques_sont_groupes"] is False,
      f"p = {gm['p_les_manques_sont_groupes']}")
    v("le groupement se refuse sur moins de quatre marches",
      les_manques_sont_ils_groupes(_marches([[True] * 6] * 3))["decidable"] is False)

    # === LE NUL A TAUX COMMUN, ET POURQUOI IL EST FAUX ======================================
    # ⭐⭐ LA DEMONSTRATION PLUTOT QUE L'ARGUMENT : un jeu de taux TRES differents, sans aucun
    # groupement, doit etre declare groupe par le nul a taux commun et PAS par le bon. C'est
    # exactement l'erreur que ma premiere sonde a commise, et elle est reproduite ici.
    # ⚠ Le jeu est construit pour EXHIBER l'erreur : des marches tout confirmees a cote de
    # marches qui ne confirment qu'un pas sur six. La rafale de ces dernieres est parfaitement
    # normale POUR LEUR TAUX, et aberrante pour le taux moyen.
    ecarts = _marches([[True] * 6] * 6
                      + [[True, False, False, False, False, False]] * 6)
    gt = le_nul_a_taux_commun_se_trompe(ecarts, tirages=2000)
    gv = les_manques_sont_ils_groupes(ecarts, tirages=2000, graine=2)
    v("un nul à taux COMMUN déclare groupé un mélange de taux sans groupement",
      gt["declare_groupe_a_taux_commun"] is True,
      f"p = {gt['p_avec_un_nul_a_taux_commun']} au taux commun {gt['taux_commun']}")
    v("... là où le nul qui conserve chaque taux ne le déclare PAS",
      gv["les_manques_sont_groupes"] is False,
      f"p = {gv['p_les_manques_sont_groupes']}, rafale {gv['rafale_moyenne_observee']} "
      f"contre {gv['rafale_moyenne_sous_lindependance']}")

    # === CE QU'UN MANQUE COUTE AU COMPTE DE FEUILLES ========================================
    # ⚠⚠⚠ LA CIBLE EST UNE FEUILLE PAR PAS, donc franchir 1,3 est aussi faux que franchir 0,7.
    # Ma premiere version lisait « plus de feuilles » comme « mieux » et rendait le verdict a
    # l'envers ; la garde l'asserte dans les deux sens.
    def _avec(f, conf):
        m = _marches([conf] * len(f), modes=[True] * len(f))
        for x, val in zip(m, f):
            x["feuilles_par_pas"] = val
        return m

    jeu = (_avec([1.00, 1.02, 0.98, 1.01], [True] * 6)
           + _avec([1.60, 1.55, 0.40, 1.62], [True, False] + [True] * 4))
    c = un_manque_coute_t_il_des_feuilles(jeu, tirages=2000)
    v("un manque qui éloigne du compte juste est annoncé comme tel",
      c["un_manque_fait_compter_plus_mal"] is True,
      f"écarts {c['ecart_a_un_des_completes']} contre {c['ecart_a_un_des_manquantes']}")
    jeu = (_avec([1.60, 1.55, 1.62, 1.58], [True] * 6)
           + _avec([1.00, 1.02, 0.98, 1.01], [True, False] + [True] * 4))
    c2 = un_manque_coute_t_il_des_feuilles(jeu, tirages=2000)
    v("... et un manque qui en rapproche ne l'est PAS",
      c2["un_manque_fait_compter_plus_mal"] is False,
      f"écarts {c2['ecart_a_un_des_completes']} contre {c2['ecart_a_un_des_manquantes']}")
    # ⚠⚠ ET LE DEPASSEMENT DES COMPLETES EST RENDU A PART : « franchir 1,6 » et « s'ecarter de
    # 0,6 » sont deux faits, et seul le premier dit DANS QUEL SENS le critere se trompe.
    v("... et le dépassement des marches entièrement confirmées est publié avec son signe",
      c2["les_completes_depassent"] is True
      and abs(c2["le_depassement_des_completes"] - 0.59) < 0.02,
      f"{c2['le_depassement_des_completes']:+.3f}")
    v("la comparaison se refuse quand un groupe est trop petit",
      un_manque_coute_t_il_des_feuilles(
          _avec([1.0] * 8, [True] * 6))["decidable"] is False)

    # === CE QUE LA LECTURE JETTE ============================================================
    j = ce_que_la_lecture_consecutive_jette(
        _marches([presque] * 5 + [[True] * 6] * 3 + [[False] * 6] * 2))
    v("les marches presque complètes sont comptées, et celles qu'on jette aussi",
      j["confirment_presque_tout"] == 8 and j["... et sont creditees de zero ou un"] == 5,
      f"{j['confirment_presque_tout']} presque complètes, "
      f"{j['... et sont creditees de zero ou un']} jetées")
    v("... et les deux lectures diffèrent sur ce jeu",
      j["les_deux_lectures_different"] is True,
      f"médianes {j['confirmes_median']} contre {j['run_median']}")
    # ⚠ ET ELLES DOIVENT COINCIDER QUAND IL N'Y A RIEN A JETER, sinon le verdict serait un oui
    # deguise qui ne depend pas des donnees.
    j2 = ce_que_la_lecture_consecutive_jette(_marches([[True] * 6] * 10))
    v("... et coïncident quand aucune marche ne manque un pas",
      j2["les_deux_lectures_different"] is False,
      f"médianes {j2['confirmes_median']} contre {j2['run_median']}")

    # === L'ARITHMETIQUE ENCHAINEE ===========================================================
    s = ce_que_ca_change_pour_la_survie(0.848, spires=120)
    v("les deux lectures d'un même taux rendent deux nombres séparés par des ordres de grandeur",
      s["survie_si_un_manque_est_une_chute"] < 1e-8
      and s["manques_attendus_si_un_manque_est_un_manque"] > 10,
      f"{s['survie_si_un_manque_est_une_chute']:.2e} contre "
      f"{s['manques_attendus_si_un_manque_est_un_manque']} manques")
    # ⚠⚠⚠ ET ELLE DIT CE QU'ELLE NE PROUVE PAS : sans cette phrase, deux ordres de grandeur se
    # liraient comme la preuve qu'un marcheur tient cent vingt spires.
    v("... et la fonction dit explicitement ce qu'elle ne prouve pas",
      "pas ete testee" in s["ce_que_la_seconde_lecture_ne_dit_pas"])

    # === LA LECTURE DE `107` ================================================================
    if CHEMIN_DE_107.is_file():
        m = confirmations_de_107(json.loads(CHEMIN_DE_107.read_text()))
        v("les marches de `107` sont lisibles", len(m) >= 24, f"{len(m)} marches")
        v("... et chacune porte autant de confirmations que de pas",
          all(len(x["confirmations"]) == x["pas"] for x in m))
        # ⚠ Une marche sans registre est gardee mais son mode vaut None : « le profil est plat »
        # n'est pas « la marche n'a rien franchi ».
        v("... et une marche sans registre décidable garde ses confirmations, sans mode",
          all(x["mode_haut"] is None or isinstance(x["mode_haut"], bool) for x in m))
    else:
        v("la mesure de `107` est présente", False, str(CHEMIN_DE_107))

    print(f"\n{'ALL PASS' if echecs == 0 else 'ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 0 if echecs == 0 else 1


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--source", type=Path, default=CHEMIN_DE_107)
    p.add_argument("--tirages", type=int, default=TIRAGES)
    p.add_argument("--graine", type=int, default=GRAINE)
    p.add_argument("--json", type=Path, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(chemin=a.source, tirages=a.tirages, graine=a.graine)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False))
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
