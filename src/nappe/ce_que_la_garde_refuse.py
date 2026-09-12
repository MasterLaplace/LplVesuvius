#!/usr/bin/env python3
"""Ce que la garde refuse, et ce que ça coûte — sur la vraie matière.

⚠⚠⚠ POURQUOI CE FICHIER. `128` mesure qu'une faille fractionnaire fait crier la garde des moitiés
(88,52° pour une barre de 10,06°) **et que le pas est pris quand même** : `oriente` est calculé,
enregistré, et la boucle avance dans cette direction. La question devient : sur la vraie matière,
combien de pas sont pris contre la garde, et qu'est-ce que ça change ?

⭐⭐⭐⭐ **ET `128` SUGGÉRAIT UN REMÈDE QUE CE FICHIER RÉFUTE.** J'y écrivais qu'un marcheur qui ne
prend pas le pas que sa garde refuse n'irait pas se faire chasser. Sur la vraie matière, ne pas le
prendre arrêterait la marche **deux fois sur cinq**, et la moitié de ces arrêts tomberait sur une
marche qui se serait redressée au pas suivant. Le remède de `116` — s'arrêter, parce que la cécité
est absorbante — ne se transporte PAS au désaccord.

⚠⚠⚠ **`oriente` EST RECALCULÉ, JAMAIS LU.** Le drapeau enregistré dans cette course date d'AVANT
la réparation de `120` : il déclarait `oriente` les 178 pas qui ne lisent rien, c'est-à-dire la
confiance maximale exactement là où le marcheur ne lit rien. Le lire ici rendrait une mesure de ce
bug et non de la garde. Il est donc reconstruit de la même façon que `est_aveugle` reconstruit la
cécité : depuis le désaccord enregistré et la barre de la course.

⚠ Aucune lecture distante : tout se calcule sur les 560 étapes que `113` a gardées.

  uv run python src/nappe/ce_que_la_garde_refuse.py --verifier
  uv run python src/nappe/ce_que_la_garde_refuse.py \
      --json docs/mesures/ce_que_la_garde_refuse.json
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

AVEUGLE, ORIENTE, DESORIENTE = "A", "O", "D"


def etats(course: dict) -> list[dict]:
    """Une entrée par marche : l'état de chacun de ses pas, dans l'ordre.

    ⭐⭐⭐ TROIS ÉTATS ET NON DEUX, et c'est ce que `116` ne pouvait pas voir. Il partageait les
    pas en aveugles et voyants ; `120` a depuis séparé « ne rien lire » de « lire mal ». Un pas
    voyant dont les deux moitiés du cube ne s'accordent pas est un troisième cas, et c'est celui
    qu'une faille produit (`128`).

    ⚠⚠ `oriente` est RECONSTRUIT depuis le désaccord et la barre, jamais lu : le drapeau
    enregistré est celui d'avant `120`, qui déclarait orientés les pas aveugles.

    ⚠ Un pas aveugle n'est PAS désorienté : deux moitiés de rien ne peuvent pas être en désaccord,
    donc leur angle vaut exactement 0,00° et passerait n'importe quelle barre. C'est `R4-L15`, et
    confondre les deux remettrait le bug que `120` a fermé.
    """
    barre = float(course["barre_daccord_des_moities_deg"])
    out = []
    for ligne in course.get("lignes", []):
        for cel in ligne.get("detail", []):
            etapes = [e for e in cel.get("etapes", []) if "confirme" in e]
            if not etapes:
                continue
            suite = []
            for e in etapes:
                if est_aveugle(e):
                    suite.append(AVEUGLE)
                    continue
                d = e.get("desaccord_des_moities_deg")
                suite.append(ORIENTE if (d is not None and float(d) < barre) else DESORIENTE)
            out.append({
                "rayon_mm": ligne.get("rayon_mm"),
                "pas": len(etapes),
                "barre_deg": barre,
                "etats": suite,
                "confirmes": [bool(e.get("confirme")) for e in etapes],
                "desaccords": [(None if e.get("desaccord_des_moities_deg") is None
                                else float(e["desaccord_des_moities_deg"])) for e in etapes],
                "avances_um": [float(e.get("avance_um", 0.0)) for e in etapes]})
    return out


def combien_la_garde_refuse(par_marche: list[dict]) -> dict:
    """Combien de pas VOYANTS sont pris dans une direction que la garde refuse.

    ⚠⚠ La part est rapportée sur les pas VOYANTS, pas sur tous : un pas aveugle n'a pas de
    direction à refuser, donc le mettre au dénominateur diluerait la mesure d'un tiers et la
    ferait passer pour moins grave qu'elle n'est.
    """
    voyants = sum(1 for m in par_marche for s in m["etats"] if s != AVEUGLE)
    des = sum(1 for m in par_marche for s in m["etats"] if s == DESORIENTE)
    concernees = sum(1 for m in par_marche if DESORIENTE in m["etats"])
    tous_des = [d for m in par_marche
                for s, d in zip(m["etats"], m["desaccords"])
                if s == DESORIENTE and d is not None]
    return {"marches": len(par_marche),
            "pas": sum(m["pas"] for m in par_marche),
            "aveugles": sum(1 for m in par_marche for s in m["etats"] if s == AVEUGLE),
            "voyants": voyants,
            "voyants_desorientes": des,
            "part_des_voyants_refusee": round(des / voyants, 4) if voyants else None,
            "marches_concernees": concernees,
            "barre_deg": par_marche[0]["barre_deg"] if par_marche else None,
            "desaccord_median_des_refuses": (round(float(np.median(tous_des)), 2)
                                             if tous_des else None),
            # ⚠⚠ DES QUANTILES ET NON UN SEUIL. `128` mesure qu'une faille fabriquée fait crier
            # la garde à 88° ; savoir combien de pas réels atteignent ce régime demanderait de
            # choisir où commence « ce régime », c'est-à-dire un seuil réglé sur ce qui passe.
            # La distribution est publiée à la place, et le lecteur voit où elle est dense.
            "desaccord_p75_des_refuses": (round(float(np.percentile(tous_des, 75)), 2)
                                          if tous_des else None),
            "desaccord_p90_des_refuses": (round(float(np.percentile(tous_des, 90)), 2)
                                          if tous_des else None),
            "desaccord_p99_des_refuses": (round(float(np.percentile(tous_des, 99)), 2)
                                          if tous_des else None),
            "desaccord_maximal": (round(float(max(tous_des)), 2) if tous_des else None)}


def _wilcoxon(ecarts) -> float | None:
    """Le p apparié, ou None si la série est dégénérée.

    ⚠ Une série toute nulle n'a aucune paire informative : rendre 1,0 se lirait comme « testé et
    non significatif » alors que rien n'a été testé.
    """
    x = np.asarray([v for v in ecarts if v is not None and np.isfinite(v)], dtype=np.float64)
    x = x[x != 0.0]
    if len(x) < 3:
        return None
    from scipy.stats import wilcoxon  # noqa: PLC0415
    return float(wilcoxon(x).pvalue)


def le_taux_distingue_t_il(par_marche: list[dict]) -> dict:
    """Le prédicat publié `confirme` fait-il la différence entre un pas orienté et un refusé ?

    ⭐⭐⭐⭐ C'EST LA QUESTION QUI DÉCIDE DE CE QUE LE TAUX VEUT DIRE. Le taux publié se lit comme
    « le marcheur suit la matière ». S'il ne distingue pas un pas dont la direction est refusée par
    la garde, alors il compte comme réussis des pas pris n'importe où, et « 0,76 » ne veut plus
    dire ce qu'on lui fait dire.

    ⚠⚠ LE TEST EST APPARIÉ PAR MARCHE, et c'est la réserve de grappe du dépôt : 382 pas voyants
    sont 28 marches, pas 382 tirages. Chaque marche qui porte les deux états rend un écart, et
    l'unité décisive est la marche.

    ⚠ Une absence de différence n'est PAS une preuve d'égalité : ce qui est rendu est le p et le
    nombre de marches, donc de quoi voir que le test ÉCHOUE À REJETER plutôt que d'affirmer.
    """
    ecarts, det = [], []
    for m in par_marche:
        o = [c for s, c in zip(m["etats"], m["confirmes"]) if s == ORIENTE]
        d = [c for s, c in zip(m["etats"], m["confirmes"]) if s == DESORIENTE]
        if not o or not d:
            continue
        to, td = float(np.mean(o)), float(np.mean(d))
        ecarts.append(to - td)
        det.append({"rayon_mm": m["rayon_mm"], "pas_orientes": len(o), "pas_refuses": len(d),
                    "taux_oriente": round(to, 4), "taux_refuse": round(td, 4),
                    "ecart": round(to - td, 4)})
    tous_o = [c for m in par_marche for s, c in zip(m["etats"], m["confirmes"]) if s == ORIENTE]
    tous_d = [c for m in par_marche for s, c in zip(m["etats"], m["confirmes"]) if s == DESORIENTE]
    p = _wilcoxon(ecarts)
    return {"marches_avec_les_deux_etats": len(ecarts),
            "taux_des_orientes": round(float(np.mean(tous_o)), 4) if tous_o else None,
            "taux_des_refuses": round(float(np.mean(tous_d)), 4) if tous_d else None,
            "pas_orientes": len(tous_o), "pas_refuses": len(tous_d),
            "ecart_median_par_marche": round(float(np.median(ecarts)), 4) if ecarts else None,
            "p_appariee": None if p is None else round(p, 4),
            # ⭐⭐⭐⭐ Le verdict, et il est prudent dans le bon sens : « le taux ne distingue
            # pas » veut dire que le test échoue à rejeter, à ce n-là.
            "le_taux_distingue": bool(p is not None and p < 0.01)}


def transitions(par_marche: list[dict]) -> dict:
    """Ce qui suit chaque état, compté À L'INTÉRIEUR d'une marche.

    ⚠ Jamais d'une marche à la suivante : deux marches n'ont ni le même départ ni la même matière,
    donc un enchaînement entre elles serait une concaténation et pas une transition.
    """
    c: dict[str, int] = {}
    for m in par_marche:
        for a, b in zip(m["etats"], m["etats"][1:]):
            c[f"{a}->{b}"] = c.get(f"{a}->{b}", 0) + 1
    return c


def le_desaccord_est_il_absorbant(par_marche: list[dict], tirages: int = 2000,
                                  graine: int = 1291) -> dict:
    """Un pas refusé est-il le dernier, comme un pas aveugle l'est ?

    ⭐⭐⭐⭐ LA RÉPONSE DÉCIDE DU REMÈDE. `116` a établi que la cécité est absorbante, donc que
    s'arrêter dessus ne coûte rien. Si le désaccord l'était aussi, `128` aurait raison et il
    suffirait de ne pas prendre le pas. S'il est transitoire, s'arrêter tronquerait des marches qui
    allaient se redresser, et le remède est ailleurs.

    ⚠⚠ ET LE TÉMOIN EST NÉCESSAIRE DANS LES DEUX SENS. Si le retour était rare, la rareté pourrait
    venir de la fréquence des refus et non d'une absorption ; s'il est fréquent, il faut savoir si
    c'est plus ou moins que ce qu'un placement au hasard rendrait. Les positions refusées sont donc
    permutées à l'intérieur de chaque marche, à compte constant : c'est la discipline de `116`.
    """
    concernees = [m for m in par_marche if DESORIENTE in m["etats"]]
    if not concernees:
        return {"decidable": False, "pourquoi": "aucune marche ne porte de pas refuse"}
    retours, sans_occasion = 0, 0
    for m in concernees:
        i = m["etats"].index(DESORIENTE)
        apres = m["etats"][i + 1:]
        if not apres:
            sans_occasion += 1
        elif any(s == ORIENTE for s in apres):
            retours += 1
    avec_occasion = len(concernees) - sans_occasion
    t = transitions(par_marche)
    depuis_d = sum(v for k, v in t.items() if k.startswith(f"{DESORIENTE}->"))
    r = np.random.default_rng(graine)
    tirages_retours = []
    for _ in range(tirages):
        n = 0
        for m in concernees:
            s = list(m["etats"])
            # ⚠ Seules les positions VOYANTES sont permutées entre elles : mélanger les aveugles
            # avec le reste deplacerait un etat que `116` a deja montre absorbant, donc le tirage
            # ne repondrait plus a la question posee.
            idx = [i for i, x in enumerate(s) if x != AVEUGLE]
            vals = [s[i] for i in idx]
            r.shuffle(vals)
            for i, v in zip(idx, vals):
                s[i] = v
            if DESORIENTE not in s:
                continue
            i0 = s.index(DESORIENTE)
            if any(x == ORIENTE for x in s[i0 + 1:]):
                n += 1
        tirages_retours.append(n)
    tirages_retours = np.asarray(tirages_retours)
    return {"decidable": True,
            "marches_avec_un_pas_refuse": len(concernees),
            "marches_ou_lorientation_revient": retours,
            "marches_sans_occasion_de_revenir": sans_occasion,
            "marches_avec_occasion": avec_occasion,
            "transitions": t,
            "part_de_retour_apres_un_refus": (
                round(t.get(f"{DESORIENTE}->{ORIENTE}", 0) / depuis_d, 4) if depuis_d else None),
            "retours_attendus_au_hasard_median": float(np.median(tirages_retours)),
            "tirages": tirages,
            # ⭐⭐⭐⭐ Le verdict, et il exige qu'il y ait eu des occasions : « zéro retour sur
            # zéro occasion » est vrai et ne dit rien.
            "le_desaccord_est_absorbant": bool(avec_occasion > 0 and retours == 0)}


def _fisher(a: list[bool], b: list[bool]) -> float | None:
    """Fisher exact entre deux paquets de booléens, ou None si l'un est vide.

    ⚠ Exact et non asymptotique : le rang 0 ne porte qu'une vingtaine de pas, et un chi-deux y
    serait une approximation dont rien ne dit qu'elle vaut à ce compte.
    """
    if not a or not b:
        return None
    from scipy.stats import fisher_exact  # noqa: PLC0415
    t = [[sum(a), len(a) - sum(a)], [sum(b), len(b) - sum(b)]]
    # ⚠ Trois chiffres SIGNIFICATIFS et non quatre décimales : un p de 10⁻⁹ arrondi à quatre
    # décimales devient 0,0, et un zéro publié se lit comme une valeur manquante.
    return float(f"{float(fisher_exact(t).pvalue):.3g}")


def le_refus_depend_il_du_rang(par_marche: list[dict]) -> dict:
    """Le premier pas est-il refusé plus souvent que les suivants ?

    ⭐⭐⭐⭐ SANS ÇA LE COMPTE DE REFUS NE SE LIT PAS. `128` a mesuré sur pile fabriquée que 12
    marches sur 12 refusent leur PREMIER pas, parce qu'elles partent recalées sur une pile et
    posees à côté de leur feuille sur l'autre. Si le même effet existe ici, une part des 42 %
    n'est pas un fait sur la matière mais un artefact du départ, et le remede n'est pas le meme :
    on répare un départ, on ne répare pas une matiere.

    ⚠ La comparaison est le rang 0 contre TOUS les autres, pas contre le rang 1 : un effet de
    départ peut durer deux ou trois pas, et ne regarder que le suivant le manquerait.
    """
    au_rang: dict[int, list[bool]] = {}
    for m in par_marche:
        for i, s in enumerate(m["etats"]):
            if s == AVEUGLE:
                continue
            au_rang.setdefault(i, []).append(s == DESORIENTE)
    premier = au_rang.get(0, [])
    suivants = [x for i, v in au_rang.items() if i > 0 for x in v]
    p_rang = _fisher(premier, suivants)
    return {"marches_au_rang_0": len(premier),
            "part_refusee_au_rang_0": (round(float(np.mean(premier)), 4) if premier else None),
            "pas_aux_rangs_suivants": len(suivants),
            "part_refusee_aux_rangs_suivants": (round(float(np.mean(suivants)), 4)
                                                if suivants else None),
            "par_rang": {str(i): round(float(np.mean(v)), 4)
                         for i, v in sorted(au_rang.items()) if len(v) >= 5},
            # ⭐⭐⭐⭐ Le verdict est un TEST, jamais un facteur. Ma première version demandait un
            # rapport supérieur à 1,5 et la mesure a rendu 1,533 : un seuil posé à quelques
            # millièmes du résultat est un seuil réglé sur ce qui passe, même quand on ne l'a pas
            # voulu. Fisher exact sur les deux comptes ne demande aucun choix, et le facteur reste
            # publié à côté parce qu'un écart de deux points et un écart de dix ne se réparent
            # pas pareil.
            "facteur_du_premier_rang": (
                round(float(np.mean(premier)) / float(np.mean(suivants)), 3)
                if premier and suivants and np.mean(suivants) > 0 else None),
            "p_du_premier_rang": p_rang,
            # ⚠⚠ `is not None` et pas `or 1.0` : en Python `0.0 or 1.0` vaut 1,0, donc un p
            # PARFAITEMENT significatif ressortait en « non significatif ». C'est la sonde de la
            # batterie qui l'a trouvé, pas une relecture.
            "le_premier_pas_est_un_cas_a_part": bool(p_rang is not None and p_rang < 0.01)}


def ce_que_couterait_larret(par_marche: list[dict]) -> dict:
    """Ce qu'on jetterait en s'arrêtant au premier pas refusé.

    ⭐⭐⭐⭐ C'EST LE PRIX DU REMÈDE QUE `128` SUGGÉRAIT, et il se calcule sans rien relire : la
    course est gardée, donc on sait exactement ce qui vient après le premier refus.

    ⚠ Les pas jetés sont comptés à part de ceux qui étaient CONFIRMÉS : jeter un pas déjà perdu ne
    coûte rien, jeter un pas confirmé coûte la portée qu'il apportait.
    """
    jetes = confirmes_jetes = parcouru = 0
    gardes = 0
    marches_tronquees = 0
    for m in par_marche:
        if DESORIENTE not in m["etats"]:
            gardes += m["pas"]
            continue
        i = m["etats"].index(DESORIENTE)
        marches_tronquees += 1
        gardes += i
        jetes += m["pas"] - i
        confirmes_jetes += sum(m["confirmes"][i:])
        parcouru += float(sum(m["avances_um"][i:]))
    total = sum(m["pas"] for m in par_marche)
    return {"marches_tronquees": marches_tronquees,
            "pas_gardes": gardes, "pas_jetes": jetes,
            "part_des_pas_jetes": round(jetes / total, 4) if total else None,
            "pas_confirmes_jetes": confirmes_jetes,
            "micrometres_jetes": round(parcouru, 1),
            "rang_median_du_premier_refus": round(float(np.median(
                [m["etats"].index(DESORIENTE) for m in par_marche
                 if DESORIENTE in m["etats"]])), 1)}


def mesurer(course_p: Path = COURSE) -> dict:
    """Tout, sur la course déjà gardée."""
    course = json.loads(Path(course_p).read_text(encoding="utf-8"))
    par_marche = etats(course)
    return {"source": Path(course_p).name,
            "fragment": course.get("fragment"),
            "combien_la_garde_refuse": combien_la_garde_refuse(par_marche),
            "le_taux_distingue_t_il": le_taux_distingue_t_il(par_marche),
            "le_desaccord_est_il_absorbant": le_desaccord_est_il_absorbant(par_marche),
            "le_refus_depend_il_du_rang": le_refus_depend_il_du_rang(par_marche),
            "ce_que_couterait_larret": ce_que_couterait_larret(par_marche),
            "par_marche": [{"rayon_mm": m["rayon_mm"], "etats": "".join(m["etats"])}
                           for m in par_marche]}


def afficher(r: dict) -> None:
    c = r["combien_la_garde_refuse"]
    print(f"{r['fragment']} · {c['marches']} marches · {c['pas']} pas · barre {c['barre_deg']}°\n")
    print(f"  {c['aveugles']} pas aveugles, {c['voyants']} voyants, dont "
          f"{c['voyants_desorientes']} REFUSÉS par la garde "
          f"({c['part_des_voyants_refusee']}) sur {c['marches_concernees']} marches")
    print(f"  désaccord des refusés : médiane {c['desaccord_median_des_refuses']}° · "
          f"p75 {c['desaccord_p75_des_refuses']} · p90 {c['desaccord_p90_des_refuses']} · "
          f"p99 {c['desaccord_p99_des_refuses']} · maximum {c['desaccord_maximal']}°")
    t = r["le_taux_distingue_t_il"]
    print(f"\n  taux confirmé des ORIENTÉS {t['taux_des_orientes']} ({t['pas_orientes']} pas) "
          f"contre {t['taux_des_refuses']} des REFUSÉS ({t['pas_refuses']} pas)")
    print(f"    écart médian par marche {t['ecart_median_par_marche']} · p {t['p_appariee']} "
          f"sur {t['marches_avec_les_deux_etats']} marches")
    print(f"    ⭐ le taux distingue un pas refusé : {t['le_taux_distingue']}")
    a = r["le_desaccord_est_il_absorbant"]
    if a.get("decidable"):
        print(f"\n  transitions {a['transitions']}")
        print(f"    l'orientation revient sur {a['marches_ou_lorientation_revient']} marches "
              f"sur {a['marches_avec_occasion']} qui en avaient l'occasion "
              f"(hasard : {a['retours_attendus_au_hasard_median']})")
        print(f"    part de retour après un refus : {a['part_de_retour_apres_un_refus']}")
        print(f"    ⭐ le désaccord est absorbant : {a['le_desaccord_est_absorbant']}")
    g = r.get("le_refus_depend_il_du_rang")
    if g:
        print(f"\n  part refusée au rang 0 : {g['part_refusee_au_rang_0']} "
              f"({g['marches_au_rang_0']} marches) contre "
              f"{g['part_refusee_aux_rangs_suivants']} aux rangs suivants "
              f"({g['pas_aux_rangs_suivants']} pas) · facteur "
              f"{g['facteur_du_premier_rang']} · p {g['p_du_premier_rang']}")
        print(f"    ⭐ le premier pas est un cas à part : "
              f"{g['le_premier_pas_est_un_cas_a_part']}")
    q = r["ce_que_couterait_larret"]
    print(f"\n  s'arrêter au premier refus coûterait {q['pas_jetes']} pas "
          f"({q['part_des_pas_jetes']}), dont {q['pas_confirmes_jetes']} CONFIRMÉS, "
          f"et {q['micrometres_jetes']} µm")
    print(f"    sur {q['marches_tronquees']} marches tronquées, rang médian du premier refus "
          f"{q['rang_median_du_premier_refus']}")


def verifier() -> int:
    """La batterie, hors ligne, sur la course gardée."""
    echecs = controles = 0

    def v(nom, obtenu, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not obtenu:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f" — {detail}" if detail else ""))

    course = json.loads(COURSE.read_text(encoding="utf-8"))
    par = etats(course)
    v("la course est lue", len(par) == 28, f"{len(par)}")
    v("... et chaque marche porte ses pas", all(m["pas"] > 0 for m in par))

    # ⚠⚠⚠ LE CONTROLE QUI JUSTIFIE LE RECALCUL : le drapeau ENREGISTRE declare orientes les pas
    # aveugles, ce que `120` a ferme. Si un jour la course est refaite avec le drapeau repare, ce
    # controle echouera — et il faudra alors LIRE le drapeau au lieu de le reconstruire.
    aveugles_dits_orientes = sum(
        1 for ligne in course["lignes"] for cel in ligne["detail"]
        for e in cel["etapes"]
        if "confirme" in e and est_aveugle(e) and e.get("oriente"))
    aveugles = sum(1 for m in par for s in m["etats"] if s == AVEUGLE)
    v("⚠ le drapeau enregistré déclare orientés les pas aveugles",
      aveugles_dits_orientes == aveugles and aveugles > 0,
      f"{aveugles_dits_orientes} sur {aveugles}")
    v("... et l'état reconstruit ne le fait pas",
      not any(s == ORIENTE for m in par for s in m["etats"] if s == AVEUGLE))

    c = combien_la_garde_refuse(par)
    v("les trois états pavent les pas",
      c["aveugles"] + c["voyants"] == c["pas"], f"{c['aveugles']}+{c['voyants']}={c['pas']}")
    # ⚠ La tolérance est celle de l'ARRONDI publié (quatre décimales), pas zéro : comparer une
    # valeur arrondie à un quotient brut avec une tolérance de 1e-9 échoue toujours, et ma
    # première version le faisait.
    v("la part est rapportée aux VOYANTS, pas à tous",
      abs(c["part_des_voyants_refusee"] - c["voyants_desorientes"] / c["voyants"]) < 5e-5)
    v("... et elle serait plus basse rapportée à tous les pas",
      c["voyants_desorientes"] / c["pas"] < c["part_des_voyants_refusee"])
    v("le désaccord des refusés dépasse la barre",
      c["desaccord_median_des_refuses"] >= c["barre_deg"],
      f"{c['desaccord_median_des_refuses']} contre {c['barre_deg']}")

    # ⭐⭐ Le compte de `115` doit se retrouver : 382 pas voyants, et leur taux vaut 0,7618.
    t = le_taux_distingue_t_il(par)
    v("⭐ le compte de pas voyants est celui de `115`", c["voyants"] == 382, f"{c['voyants']}")
    tous = (t["taux_des_orientes"] * t["pas_orientes"]
            + t["taux_des_refuses"] * t["pas_refuses"]) / c["voyants"]
    v("... et les deux taux se recomposent en celui de `115`", abs(tous - 0.7618) < 5e-4,
      f"{tous:.4f}")

    # ⚠ Sonde : un jeu où les refusés ne sont JAMAIS confirmés doit faire dire au test qu'il
    # distingue. Sans elle, « le taux ne distingue pas » serait vrai de n'importe quel jeu.
    faux = [{"rayon_mm": 1.0, "pas": 8, "barre_deg": 8.88,
             "etats": list("OOOODDDD"),
             "confirmes": [True] * 4 + [False] * 4,
             "desaccords": [1.0] * 4 + [20.0] * 4,
             "avances_um": [173.0] * 8} for _ in range(8)]
    v("⭐ sonde : un jeu où les refusés échouent est DISTINGUÉ",
      le_taux_distingue_t_il(faux)["le_taux_distingue"], )
    v("... alors que la vraie course ne l'est pas", not t["le_taux_distingue"],
      f"p {t['p_appariee']}")

    a = le_desaccord_est_il_absorbant(par, tirages=200)
    v("l'absorption est décidable", a.get("decidable"))
    v("... et les marches sans occasion sont comptées à part",
      a["marches_avec_occasion"] + a["marches_sans_occasion_de_revenir"]
      == a["marches_avec_un_pas_refuse"])
    v("⭐ le désaccord n'est PAS absorbant", not a["le_desaccord_est_absorbant"],
      f"{a['marches_ou_lorientation_revient']} retours")
    v("... et la cécité, elle, l'est toujours dans les mêmes données",
      a["transitions"].get(f"{AVEUGLE}->{ORIENTE}", 0) == 0
      and a["transitions"].get(f"{AVEUGLE}->{DESORIENTE}", 0) == 0,
      f"{a['transitions']}")
    # ⚠ Sonde : un jeu où le refus est le dernier état doit être declare absorbant, sinon le
    # verdict ne pourrait jamais rendre vrai et ne dirait rien.
    colle = [{"rayon_mm": 1.0, "pas": 6, "barre_deg": 8.88, "etats": list("OODDDD"),
              "confirmes": [True] * 6, "desaccords": [1.0] * 6,
              "avances_um": [173.0] * 6} for _ in range(6)]
    v("⭐ sonde : un refus qui ne se lève jamais EST déclaré absorbant",
      le_desaccord_est_il_absorbant(colle, tirages=50)["le_desaccord_est_absorbant"])

    g = le_refus_depend_il_du_rang(par)
    v("le rang 0 est comparé à TOUS les suivants",
      g["marches_au_rang_0"] + g["pas_aux_rangs_suivants"] == c["voyants"],
      f"{g['marches_au_rang_0']}+{g['pas_aux_rangs_suivants']} contre {c['voyants']}")
    # ⚠ Sonde : un jeu dont TOUS les premiers pas sont refuses et aucun autre doit être declare
    # cas à part, sinon le verdict ne pourrait jamais rendre vrai.
    depart = [{"rayon_mm": 1.0, "pas": 6, "barre_deg": 8.88, "etats": list("DOOOOO"),
               "confirmes": [True] * 6, "desaccords": [20.0] + [1.0] * 5,
               "avances_um": [173.0] * 6} for _ in range(6)]
    v("⭐ sonde : un refus systématique au départ EST déclaré cas à part",
      le_refus_depend_il_du_rang(depart)["le_premier_pas_est_un_cas_a_part"])

    q = ce_que_couterait_larret(par)
    v("le prix de l'arrêt est compté", q["pas_jetes"] > 0)
    v("... et les pas jetés déjà CONFIRMÉS sont comptés à part",
      0 < q["pas_confirmes_jetes"] <= q["pas_jetes"],
      f"{q['pas_confirmes_jetes']} sur {q['pas_jetes']}")
    v("... et gardés plus jetés font le total",
      q["pas_gardes"] + q["pas_jetes"] == c["pas"],
      f"{q['pas_gardes']}+{q['pas_jetes']} contre {c['pas']}")

    r = mesurer()
    afficher(r)
    v("l'affichage tourne sur ce résultat", True)

    print(f"\n{'ALL PASS' if echecs == 0 else 'ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path)
    p.add_argument("--course", type=Path, default=COURSE)
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
