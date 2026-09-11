#!/usr/bin/env python3
"""Le marcheur dérive-t-il ? — un pas confirmé n'est pas un pas droit.

⚠⚠⚠ POURQUOI CE FICHIER EXISTE. `117` a mesuré que le **taux** de confirmation ne baisse pas avec
la profondeur. Ça ne dit rien de la **trajectoire** : une marche peut confirmer ses vingt pas en
tournant lentement pour longer la feuille au lieu de la traverser, et chaque pas serait
parfaitement confirmé pendant que la marche s'en va. C'est exactement la panne que l'humain corrige
d'une spire à l'autre, et c'est la seule qu'aucune des tranches précédentes n'a regardée.

⭐⭐⭐⭐ **ET LE MARCHEUR N'ACCUMULE PAS.** La rectitude — le déplacement net rapporté au chemin
parcouru — vaut **0,944** sur la première moitié d'une marche et **0,942** sur la seconde
(Wilcoxon p **0,8906**). Le virage d'un pas au suivant ne grandit pas non plus, et la rotation
cumulée autour de l'axe du rouleau ne montre pas de sens privilégié (médiane **+13,2°**,
p **0,1564**).

⭐⭐⭐⭐ **MIEUX : SES VIRAGES SE COMPENSENT.** Contre une marche simulée qui garde **exactement**
le même virage à chaque pas mais en tire la direction au hasard, la marche réelle est plus droite —
**0,928 contre 0,803**, sur **17 marches sur 19**, Wilcoxon apparié p **0,00141**. Le marcheur ne
se contente donc pas de ne pas empirer : il **corrige**.

⚠⚠ **CE QUE CE FICHIER NE PROUVE PAS.** Vingt pas font environ quatre millimètres, soit un sixième
de l'étendue radiale des départs (4,07 à 23,8 mm). Rien ici ne dit que la marche reste droite sur
les cent et quelques transferts qu'un rouleau entier demande : la porte `R4-P20` reste ouverte, et
ce document ne la referme pas.

⚠ L'angle au radial **de départ** croît le long d'une marche (42° au premier pas, 57° au vingtième),
et il est rendu comme **description et non comme résultat** : une marche qui avance aussi
circonférentiellement voit le radial LOCAL tourner sous elle, donc l'angle au radial initial
croîtrait même sur une trajectoire parfaite. Au niveau de la marche, l'écart n'est d'ailleurs pas
établi (p 0,3321).

⚠ Aucune lecture distante : la trajectoire est **reconstruite exactement** depuis les directions et
les avances que `113` a gardées, et le contrôle est qu'elle retrouve le `parcouru_um` de la course.

  uv run python src/nappe/le_marcheur_derive_t_il.py --verifier
  uv run python src/nappe/le_marcheur_derive_t_il.py --json docs/mesures/le_marcheur_derive_t_il.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from scipy import stats

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
COURSE = RACINE / "docs" / "mesures" / "jusquou_va_t_il_si_on_le_laisse.json"

from ce_qui_porte_le_taux import est_aveugle  # noqa: E402

PAS_MINIMUM = 6
"""Le nombre de pas voyants sous lequel une marche n'est pas coupée en deux moitiés.

⚠ Six et pas deux : la rectitude d'une moitié de trois pas est dominée par un seul virage, donc
comparer deux moitiés d'une marche de quatre pas compare deux bruits. Le seuil est déclaré ici,
en amont du résultat, et il est le même pour toutes les mesures du fichier."""

TIRAGES = 400
GRAINE = 1191


def marches(course: dict) -> list[dict]:
    """Les marches, coupées à leur premier pas aveugle, avec ce qu'il faut pour la trajectoire.

    ⚠⚠ Coupées, parce que `116` a mesuré que la cécité est **absorbante** : les pas qui suivent le
    premier aveugle sont des pas dont la direction a été choisie sans rien lire. Les garder
    mesurerait la trajectoire d'un marcheur aveugle et l'appellerait une dérive.
    """
    out = []
    for ligne in course.get("lignes", []):
        for cel in ligne.get("detail", []):
            etapes = [e for e in cel.get("etapes", []) if "confirme" in e]
            n = next((i for i, e in enumerate(etapes) if est_aveugle(e)), len(etapes))
            voyants = etapes[:n]
            if not voyants:
                continue
            out.append({
                "rayon_mm": ligne.get("rayon_mm"),
                "radial": [float(x) for x in cel.get("radial_zyx", (0.0, 0.0, 0.0))],
                "pas_voyants": len(voyants),
                "directions": [[float(x) for x in e["direction"]] for e in voyants],
                "avances_um": [float(e["avance_um"]) for e in voyants],
                "parcouru_um": [float(e["parcouru_um"]) for e in voyants]})
    return out


def la_trajectoire_est_elle_celle_de_la_course(par_marche: list[dict],
                                               tolerance_um: float = 1.0) -> dict:
    """Le chemin reconstruit retrouve-t-il le `parcouru_um` que la course a écrit ?

    ⭐⭐⭐⭐ C'EST LA GARDE SANS LAQUELLE TOUT CE FICHIER MESURE UNE AUTRE MARCHE. La trajectoire
    est reconstruite en sommant `direction × avance` ; si ce cumul ne retrouve pas le
    `parcouru_um` de la course, c'est que les deux champs ne décrivent pas le même pas.

    ⚠ La tolérance n'est pas un réglage : `avance_um` est écrit à la décimale, donc vingt pas
    portent au plus un micromètre d'arrondi cumulé. Une tolérance plus large accepterait un vrai
    désaccord, une plus étroite refuserait l'écriture du JSON.
    """
    if not par_marche:
        return {"decidable": False, "pourquoi": "aucune marche"}
    ecarts = []
    for m in par_marche:
        cum = 0.0
        for a, p in zip(m["avances_um"], m["parcouru_um"]):
            cum += a
            ecarts.append(abs(cum - p))
    pire = max(ecarts)
    return {"decidable": True, "marches": len(par_marche), "pas": len(ecarts),
            "ecart_max_um": round(pire, 4), "tolerance_um": tolerance_um,
            "normes_des_directions_unitaires": bool(all(
                abs(float(np.linalg.norm(d)) - 1.0) < 1e-4
                for m in par_marche for d in m["directions"])),
            "la_trajectoire_est_celle_de_la_course": bool(pire <= tolerance_um)}


def _wilcoxon(a, b=None) -> float | None:
    """Le p d'un Wilcoxon apparié, ou `None` si la série est DÉGÉNÉRÉE.

    ⚠⚠ Des différences toutes nulles ne disent pas « pas d'effet », elles disent qu'il n'y a rien
    à tester : `scipy` y rend un p de 1,0 sur une division invalide, et ce 1,0 se lit exactement
    comme un vrai « pas d'écart ». C'est la forme d'une vérification qui ne peut pas échouer, et
    ce dépôt l'a déjà payée deux fois aujourd'hui.
    """
    d = np.asarray(a, dtype=float) - (0.0 if b is None else np.asarray(b, dtype=float))
    if not np.any(d):
        return None
    return float(stats.wilcoxon(d).pvalue)


def _rectitude(directions, avances) -> float:
    d = np.asarray(directions, dtype=float)
    a = np.asarray(avances, dtype=float)
    return float(np.linalg.norm((d * a[:, None]).sum(axis=0)) / a.sum())


def _virages(directions) -> list[float]:
    d = np.asarray(directions, dtype=float)
    return [float(np.degrees(np.arccos(np.clip(float(a @ b), -1.0, 1.0))))
            for a, b in zip(d, d[1:])]


def la_marche_se_degrade_t_elle(par_marche: list[dict]) -> dict:
    """La rectitude de la seconde moitié d'une marche est-elle moindre que celle de la première ?

    ⭐⭐⭐⭐ C'EST LE TEST DE L'ACCUMULATION, et il porte sur la trajectoire et non sur le taux.
    Une marche qui dérive devient moins droite à mesure qu'elle avance, même si chacun de ses pas
    reste confirmé.

    ⚠⚠ La comparaison est **appariée à l'intérieur d'une marche** : deux marches n'ont ni le même
    départ ni la même matière, donc comparer la première moitié des unes à la seconde des autres
    mesurerait surtout laquelle est tombée dans quelle bande.
    """
    utiles = [m for m in par_marche if m["pas_voyants"] >= PAS_MINIMUM]
    if len(utiles) < 6:
        return {"decidable": False, "pourquoi": f"{len(utiles)} marches d'au moins "
                                                f"{PAS_MINIMUM} pas voyants"}
    r1, r2, ang = [], [], []
    for m in utiles:
        h = m["pas_voyants"] // 2
        r1.append(_rectitude(m["directions"][:h], m["avances_um"][:h]))
        r2.append(_rectitude(m["directions"][h:], m["avances_um"][h:]))
        d = np.asarray(m["directions"], dtype=float)
        a = np.asarray(m["avances_um"], dtype=float)
        n1 = (d[:h] * a[:h, None]).sum(axis=0)
        n2 = (d[h:] * a[h:, None]).sum(axis=0)
        ang.append(float(np.degrees(np.arccos(np.clip(
            float(n1 @ n2) / (np.linalg.norm(n1) * np.linalg.norm(n2)), -1.0, 1.0)))))
    p = _wilcoxon(r1, r2)
    return {"decidable": True, "marches": len(utiles), "test_decidable": p is not None,
            "rectitude_premiere_moitie": round(float(np.median(r1)), 3),
            "rectitude_seconde_moitie": round(float(np.median(r2)), 3),
            "p_appariee": round(p, 4) if p is not None else None,
            "angle_entre_les_deux_moities_deg": round(float(np.median(ang)), 1),
            "angle_max_deg": round(float(max(ang)), 1),
            "la_marche_se_degrade": bool(p is not None
                                         and float(np.median(r2)) < float(np.median(r1))
                                         and p < 0.05)}


def le_virage_a_t_il_un_sens(par_marche: list[dict]) -> dict:
    """La marche tourne-t-elle toujours du même côté autour de l'axe du rouleau ?

    ⭐⭐⭐ Un virage **systématique** est la signature d'une spirale : une marche qui tourne
    toujours du même côté finit par longer la feuille au lieu de la traverser. Un virage sans sens
    privilégié est du bruit, et il se compense.

    ⚠ L'axe du rouleau est l'axe `z` du volume, c'est-à-dire la première coordonnée d'un triplet
    `zyx`. La rotation est donc mesurée dans le plan `(y, x)`, celui où un enroulement se voit.
    """
    utiles = [m for m in par_marche if m["pas_voyants"] >= PAS_MINIMUM]
    if len(utiles) < 6:
        return {"decidable": False, "pourquoi": f"{len(utiles)} marches exploitables"}
    cumules = []
    for m in utiles:
        d = np.asarray(m["directions"], dtype=float)
        s = 0.0
        for a, b in zip(d, d[1:]):
            s += float(np.degrees(np.arctan2(float(np.cross(a, b)[0]), float(a @ b))))
        cumules.append(s)
    p = _wilcoxon(cumules)
    return {"decidable": True, "marches": len(utiles), "test_decidable": p is not None,
            "rotation_cumulee_mediane_deg": round(float(np.median(cumules)), 1),
            "rotation_min_deg": round(float(min(cumules)), 1),
            "rotation_max_deg": round(float(max(cumules)), 1),
            "p_contre_zero": round(p, 4) if p is not None else None,
            "le_virage_a_un_sens": bool(p is not None and p < 0.05)}


def temoin_les_virages_se_compensent(par_marche: list[dict], tirages: int = TIRAGES,
                                     graine: int = GRAINE) -> dict:
    """La marche est-elle plus droite qu'un tirage qui virerait AUTANT mais n'importe où ?

    ⭐⭐⭐⭐ C'EST LE CONTRÔLE QUI DISTINGUE « NE PAS EMPIRER » DE « CORRIGER ». Le virage de chaque
    pas est **gardé exactement** ; seule sa direction dans le plan normal au pas précédent est
    tirée au hasard. Si la marche réelle est plus droite que ce tirage, ses virages se compensent —
    c'est-à-dire qu'elle revient vers quelque chose.

    ⚠ Sans ce témoin, une rectitude de 0,93 ne dirait rien : une marche dont les pas ne virent
    presque pas serait droite sans rien corriger, et le nombre serait le même.

    ⚠ Graine posée : un témoin dont le tirage change à chaque lancement rend un nombre différent à
    chaque relecture, donc n'est pas un témoin.
    """
    utiles = [m for m in par_marche if m["pas_voyants"] >= PAS_MINIMUM]
    if len(utiles) < 6:
        return {"decidable": False, "pourquoi": f"{len(utiles)} marches exploitables"}
    rng = np.random.default_rng(graine)
    reel, simule = [], []
    for m in utiles:
        d = np.asarray(m["directions"], dtype=float)
        a = np.asarray(m["avances_um"], dtype=float)
        reel.append(_rectitude(d, a))
        angles = [np.arccos(np.clip(float(x @ y), -1.0, 1.0)) for x, y in zip(d, d[1:])]
        tire = []
        for _ in range(tirages):
            suite = [d[0]]
            for th in angles:
                u = suite[-1]
                v = rng.normal(size=3)
                v -= (v @ u) * u
                n = np.linalg.norm(v)
                if n < 1e-12:
                    v, n = np.array([1.0, 0.0, 0.0]) - u * u[0], 1.0
                v = v / n
                suite.append(np.cos(th) * u + np.sin(th) * v)
            tire.append(_rectitude(np.asarray(suite), a))
        simule.append(float(np.median(tire)))
    p = _wilcoxon(reel, simule)
    return {"decidable": True, "marches": len(utiles), "tirages": tirages, "graine": graine,
            "test_decidable": p is not None,
            "rectitude_reelle": round(float(np.median(reel)), 3),
            "rectitude_simulee": round(float(np.median(simule)), 3),
            # ⚠ Les deux séries appariées sont GARDÉES : la figure trace un segment par marche, et
            # une figure qui referait la simulation en serait un second producteur — avec sa
            # propre graine, donc ses propres nombres.
            "reels": [round(x, 4) for x in reel],
            "simules": [round(x, 4) for x in simule],
            "marches_ou_le_reel_est_plus_droit": sum(1 for x, y in zip(reel, simule) if x > y),
            "p_appariee": round(p, 5) if p is not None else None,
            "les_virages_se_compensent": bool(
                p is not None and float(np.median(reel)) > float(np.median(simule)) and p < 0.05)}


def le_virage_grandit_il(par_marche: list[dict]) -> dict:
    """Le virage d'un pas au suivant grandit-il quand la marche s'enfonce ?

    ⚠ Rendu comme **description**, avec son test apparié : un virage par pas qui grandirait dirait
    que la marche devient erratique même si sa rectitude globale tient.
    """
    utiles = [m for m in par_marche if m["pas_voyants"] >= PAS_MINIMUM]
    if len(utiles) < 6:
        return {"decidable": False, "pourquoi": f"{len(utiles)} marches exploitables"}
    a1, a2, par_rang = [], [], {}
    for m in utiles:
        v = _virages(m["directions"])
        t = max(1, len(v) // 3)
        a1.append(float(np.median(v[:t])))
        a2.append(float(np.median(v[-t:])))
        for k, x in enumerate(v, 1):
            par_rang.setdefault(k, []).append(x)
    p = _wilcoxon(a1, a2)
    return {"decidable": True, "marches": len(utiles), "test_decidable": p is not None,
            "virage_premier_tiers_deg": round(float(np.median(a1)), 1),
            "virage_dernier_tiers_deg": round(float(np.median(a2)), 1),
            "p_appariee": round(p, 4) if p is not None else None,
            "par_rang": [{"pas": k, "marches": len(v),
                          "virage_median_deg": round(float(np.median(v)), 1)}
                         for k, v in sorted(par_rang.items())],
            "le_virage_grandit": bool(p is not None
                                      and float(np.median(a2)) > float(np.median(a1))
                                      and p < 0.05)}


def langle_au_radial_initial(par_marche: list[dict]) -> dict:
    """L'angle au radial de DÉPART, rendu comme description et jamais comme résultat.

    ⚠⚠ IL EST CONFONDU, ET C'EST POURQUOI IL N'EST PAS UN RÉSULTAT. Une marche qui avance aussi
    circonférentiellement voit le radial **local** tourner sous elle : l'angle au radial initial
    croîtrait donc même sur une trajectoire parfaite. Le mesurer contre le radial local demanderait
    l'axe du rouleau, qui est une **courbe** (`laxe_est_une_courbe.py`) et pas une droite, donc une
    autre mesure et un autre lot.
    """
    utiles = [m for m in par_marche if m["pas_voyants"] >= PAS_MINIMUM]
    if len(utiles) < 6:
        return {"decidable": False, "pourquoi": f"{len(utiles)} marches exploitables"}
    a1, a2 = [], []
    for m in utiles:
        rad = np.asarray(m["radial"], dtype=float)
        ang = [float(np.degrees(np.arccos(np.clip(float(np.asarray(x) @ rad), -1.0, 1.0))))
               for x in m["directions"]]
        t = max(1, len(ang) // 3)
        a1.append(float(np.median(ang[:t])))
        a2.append(float(np.median(ang[-t:])))
    return {"decidable": True, "marches": len(utiles), "description_seulement": True,
            "angle_premier_tiers_deg": round(float(np.median(a1)), 1),
            "angle_dernier_tiers_deg": round(float(np.median(a2)), 1),
            "p_appariee": (lambda q: round(q, 4) if q is not None else None)(_wilcoxon(a1, a2)),
            "confondu_par": "le radial local tourne quand la marche avance circonférentiellement"}


def traces_projetees(par_marche: list[dict]) -> list[dict]:
    """Chaque trajectoire, aplatie dans SON propre plan, pour que la figure la dessine.

    ⚠⚠ Le plan est celui des deux premières composantes principales du chemin, et ce choix est le
    plus DÉFAVORABLE possible : c'est le plan où l'écart à la droite est maximal. Projeter sur le
    plan du déplacement net donnerait des trajectoires plus droites qu'elles ne sont, ce qui est
    exactement le biais qu'une figure de rectitude ne doit pas avoir.

    ⚠ La projection est faite ICI, chez le producteur, et pas dans la figure : un dessin qui
    calculerait sa propre projection serait un second producteur du même chemin.

    ⚠ Chaque trace est tournée pour que son déplacement net pointe vers `+x` — sinon dix-neuf
    trajectoires se superposeraient dans dix-neuf directions et la figure ne montrerait qu'une
    rosace.
    """
    out = []
    for m in par_marche:
        if m["pas_voyants"] < PAS_MINIMUM:
            continue
        d = np.asarray(m["directions"], dtype=float)
        a = np.asarray(m["avances_um"], dtype=float)
        pts = np.vstack([np.zeros(3), np.cumsum(d * a[:, None], axis=0)])
        centre = pts - pts.mean(axis=0)
        # ⚠ `full_matrices=False` : on ne veut que les deux axes du plan, pas une base complète.
        _, _, vt = np.linalg.svd(centre, full_matrices=False)
        plan = np.asarray([vt[0], vt[1]])
        xy = centre @ plan.T
        xy = xy - xy[0]
        net = xy[-1]
        n = float(np.linalg.norm(net))
        if n > 1e-9:
            c, s = float(net[0]) / n, float(net[1]) / n
            xy = xy @ np.asarray([[c, -s], [s, c]])
        out.append({"rayon_mm": m["rayon_mm"], "pas": m["pas_voyants"],
                    "rectitude": round(_rectitude(d, a), 3),
                    "xy_um": [[round(float(x), 1), round(float(y), 1)] for x, y in xy]})
    return out


def mesurer(course_p: Path = COURSE) -> dict:
    """Tout, depuis le JSON de `113` — aucune lecture distante."""
    course = json.loads(course_p.read_text(encoding="utf-8"))
    if course.get("course_incomplete"):
        raise ValueError(f"{course_p} : course incomplète")
    pm = marches(course)
    if not pm:
        raise ValueError(f"{course_p} ne porte aucune marche avec ses étapes")
    garde = la_trajectoire_est_elle_celle_de_la_course(pm)
    if garde.get("decidable") and not garde["la_trajectoire_est_celle_de_la_course"]:
        raise ValueError(
            f"{course_p} : la trajectoire reconstruite ne retrouve pas `parcouru_um` "
            f"(écart max {garde['ecart_max_um']} µm) — elle décrit une autre marche")
    return {"source": course_p.name, "marches": len(pm),
            "pas_voyants": sum(m["pas_voyants"] for m in pm),
            "la_trajectoire_est_elle_celle_de_la_course": garde,
            "la_marche_se_degrade_t_elle": la_marche_se_degrade_t_elle(pm),
            "le_virage_a_t_il_un_sens": le_virage_a_t_il_un_sens(pm),
            "le_virage_grandit_il": le_virage_grandit_il(pm),
            "temoin_les_virages_se_compensent": temoin_les_virages_se_compensent(pm),
            "langle_au_radial_initial": langle_au_radial_initial(pm),
            "traces": traces_projetees(pm)}


def afficher(r: dict) -> None:
    g = r["la_trajectoire_est_elle_celle_de_la_course"]
    print(f"source {r['source']} · {r['marches']} marches · {r['pas_voyants']} pas voyants")
    if g.get("decidable"):
        print(f"  trajectoire reconstruite : écart max {g['ecart_max_um']} µm "
              f"(tolérance {g['tolerance_um']}) — celle de la course : "
              f"{g['la_trajectoire_est_celle_de_la_course']}")
    d = r["la_marche_se_degrade_t_elle"]
    if d.get("decidable"):
        print(f"\n  rectitude : {d['rectitude_premiere_moitie']} sur la 1re moitié, "
              f"{d['rectitude_seconde_moitie']} sur la 2e (p {d['p_appariee']}) "
              f"sur {d['marches']} marches")
        print(f"  angle entre les deux moitiés : {d['angle_entre_les_deux_moities_deg']}° "
              f"médian, {d['angle_max_deg']}° au pire")
        print(f"  ⭐ la marche se dégrade : {d['la_marche_se_degrade']}")
    v = r["le_virage_grandit_il"]
    if v.get("decidable"):
        print(f"  virage par pas : {v['virage_premier_tiers_deg']}° → "
              f"{v['virage_dernier_tiers_deg']}° (p {v['p_appariee']}) · "
              f"grandit : {v['le_virage_grandit']}")
    s = r["le_virage_a_t_il_un_sens"]
    if s.get("decidable"):
        print(f"  rotation cumulée autour de l'axe : médiane "
              f"{s['rotation_cumulee_mediane_deg']:+}° "
              f"[{s['rotation_min_deg']} ; {s['rotation_max_deg']}] (p {s['p_contre_zero']}) · "
              f"un sens : {s['le_virage_a_un_sens']}")
    t = r["temoin_les_virages_se_compensent"]
    if t.get("decidable"):
        print(f"\n  témoin ({t['tirages']} tirages, graine {t['graine']}) : réel "
              f"{t['rectitude_reelle']} contre simulé {t['rectitude_simulee']}, "
              f"{t['marches_ou_le_reel_est_plus_droit']}/{t['marches']} marches, "
              f"p {t['p_appariee']}")
        print(f"  ⭐ les virages se compensent : {t['les_virages_se_compensent']}")
    a = r["langle_au_radial_initial"]
    if a.get("decidable"):
        print(f"\n  ⚠ description seule — angle au radial INITIAL : "
              f"{a['angle_premier_tiers_deg']}° → {a['angle_dernier_tiers_deg']}° "
              f"(p {a['p_appariee']}), confondu par : {a['confondu_par']}")


def verifier() -> int:
    """La batterie, hors ligne, sur des marches FABRIQUÉES — et six sondes."""
    import tempfile
    echecs = controles = 0

    def v(nom, obtenu, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not obtenu:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f" — {detail}" if detail else ""))

    def marche(directions, avance=100.0, rayon=4.0, radial=(0.0, 0.0, 1.0), parcouru=None):
        d = [list(np.asarray(x, dtype=float) / np.linalg.norm(x)) for x in directions]
        n = len(d)
        return {"rayon_mm": rayon, "radial": list(radial), "pas_voyants": n,
                "directions": d, "avances_um": [avance] * n,
                "parcouru_um": parcouru or [avance * (k + 1) for k in range(n)]}

    droite = [marche([(0.0, 0.0, 1.0)] * 12, rayon=4.0 + i) for i in range(10)]

    # ⭐⭐⭐⭐ LA GARDE DE RECONSTRUCTION.
    g = la_trajectoire_est_elle_celle_de_la_course(droite)
    v("le chemin reconstruit retrouve parcouru_um", g["la_trajectoire_est_celle_de_la_course"],
      f"écart {g['ecart_max_um']}")
    v("... et les directions sont unitaires", g["normes_des_directions_unitaires"])
    faux = [dict(m) for m in droite]
    faux[0] = dict(faux[0]); faux[0]["parcouru_um"] = [x + 5.0 for x in faux[0]["parcouru_um"]]
    v("sonde : un parcouru qui ne suit pas les avances est signalé",
      not la_trajectoire_est_elle_celle_de_la_course(faux)[
          "la_trajectoire_est_celle_de_la_course"])

    # ⭐⭐⭐⭐ UNE MARCHE DROITE EST DROITE, ET UNE MARCHE QUI DÉRIVE EST VUE.
    d0 = la_marche_se_degrade_t_elle(droite)
    v("une marche parfaitement droite a une rectitude de 1",
      d0["rectitude_premiere_moitie"] == 1.0 and d0["rectitude_seconde_moitie"] == 1.0,
      f"{d0['rectitude_premiere_moitie']}/{d0['rectitude_seconde_moitie']}")
    v("... et son test se déclare indécidable plutôt que de rendre un p de 1",
      not d0["test_decidable"] and d0["p_appariee"] is None)
    v("... et elle n'est pas déclarée en dégradation", not d0["la_marche_se_degrade"])
    # ⚠⚠ LA SONDE SYMÉTRIQUE : sans elle, un test qui répondrait toujours « pas de dégradation »
    # passerait le contrôle du dessus.
    def derive(n=12, virage=25.0):
        out, th = [], 0.0
        for k in range(n):
            if k >= n // 2:
                th += np.radians(virage)
            out.append((0.0, np.sin(th), np.cos(th)))
        return out
    qui_derive = [marche(derive(), rayon=4.0 + i) for i in range(10)]
    dd = la_marche_se_degrade_t_elle(qui_derive)
    v("sonde : une marche qui tourne dans sa seconde moitié est VUE",
      dd["la_marche_se_degrade"],
      f"{dd['rectitude_premiere_moitie']} → {dd['rectitude_seconde_moitie']}, p {dd['p_appariee']}")
    v("moins de six marches exploitables rend indécidable",
      not la_marche_se_degrade_t_elle(droite[:3])["decidable"])
    v("une marche trop courte n'est pas coupée en deux",
      not la_marche_se_degrade_t_elle(
          [marche([(0.0, 0.0, 1.0)] * 4, rayon=4.0 + i) for i in range(10)])["decidable"])

    # ⭐⭐⭐ LE SENS DU VIRAGE.
    s0 = le_virage_a_t_il_un_sens(droite)
    v("une marche droite ne tourne pas", s0["rotation_cumulee_mediane_deg"] == 0.0)
    # ⚠⚠ Et le TEST se déclare indécidable plutôt que de rendre « pas de sens » : des rotations
    # toutes nulles n'ont rien à tester, et `scipy` y rend un p de 1,0 qui se lit comme un
    # résultat.
    v("... et le test se déclare indécidable", not s0["test_decidable"])
    v("... donc aucun sens n'est affirmé", not s0["le_virage_a_un_sens"])
    # ⚠ La spirale tourne dans le plan (y, x) — les indices 1 et 2 d'un triplet `zyx` — parce que
    # c'est là qu'un enroulement se voit. Ma première version tournait dans le plan (z, y) et le
    # contrôle a rendu 0°, ce qui était le bon compte pour la mauvaise fixture.
    spirale = [marche([(0.0, np.cos(np.radians(15.0 * k)), np.sin(np.radians(15.0 * k)))
                       for k in range(12)], rayon=4.0 + i) for i in range(10)]
    ss = le_virage_a_t_il_un_sens(spirale)
    v("sonde : une spirale a un sens de rotation", ss["le_virage_a_un_sens"],
      f"{ss['rotation_cumulee_mediane_deg']}°, p {ss['p_contre_zero']}")

    # ⭐⭐⭐⭐ LE TÉMOIN.
    # ⚠⚠ Une marche DROITE ne vire pas, donc le simulé ne peut pas être moins droit : le témoin
    # doit alors répondre « ne se compensent pas » plutôt que d'inventer un écart. C'est ce qui
    # distingue « corriger » de « ne pas virer ».
    t0 = temoin_les_virages_se_compensent(droite, tirages=40)
    v("sur une marche droite, le témoin ne trouve rien à compenser",
      not t0["les_virages_se_compensent"],
      f"réel {t0['rectitude_reelle']} contre simulé {t0['rectitude_simulee']}")
    # une marche en zigzag PLAN : elle vire beaucoup et revient, donc elle doit battre le tirage
    zig = [marche([(0.0, 0.30 * (-1) ** k, 1.0) for k in range(12)], rayon=4.0 + i)
           for i in range(10)]
    tz = temoin_les_virages_se_compensent(zig, tirages=120)
    v("sonde : un zigzag qui revient bat le tirage au hasard", tz["les_virages_se_compensent"],
      f"réel {tz['rectitude_reelle']} contre simulé {tz['rectitude_simulee']}, p {tz['p_appariee']}")
    v("... et le témoin garde exactement le virage de chaque pas",
      tz["rectitude_simulee"] < tz["rectitude_reelle"])
    v("le témoin garde ses deux séries appariées",
      len(tz["reels"]) == len(tz["simules"]) == tz["marches"],
      f"{len(tz['reels'])}/{len(tz['simules'])}/{tz['marches']}")
    v("... et leurs médianes sont celles publiées",
      round(float(np.median(tz["reels"])), 3) == tz["rectitude_reelle"]
      and round(float(np.median(tz["simules"])), 3) == tz["rectitude_simulee"])
    v("le témoin est reproductible",
      temoin_les_virages_se_compensent(zig, tirages=120)["rectitude_simulee"]
      == tz["rectitude_simulee"])

    # ⭐ LE VIRAGE PAR PAS.
    vg = le_virage_grandit_il(zig)
    v("le virage par pas est mesuré", vg["decidable"] and vg["virage_premier_tiers_deg"] > 0)
    v("... et il ne grandit pas sur un zigzag régulier", not vg["le_virage_grandit"])
    grandit = [marche([(0.0, 0.05 * k * (-1) ** k, 1.0) for k in range(12)], rayon=4.0 + i)
               for i in range(10)]
    v("sonde : un virage qui grandit est VU", le_virage_grandit_il(grandit)["le_virage_grandit"])

    # ⭐⭐ LES TRACES PROJETÉES, que la figure dessine.
    tr = traces_projetees(droite)
    v("une trace par marche exploitable", len(tr) == 10, f"{len(tr)}")
    v("une trace a un point de plus que de pas", len(tr[0]["xy_um"]) == 13,
      f"{len(tr[0]['xy_um'])}")
    v("elle part de l'origine", tr[0]["xy_um"][0] == [0.0, 0.0], f"{tr[0]['xy_um'][0]}")
    # ⚠ Une marche droite de douze pas de 100 µm finit à 1200 µm sur +x, et à zéro de côté.
    v("... et une marche droite finit sur +x", tr[0]["xy_um"][-1] == [1200.0, 0.0],
      f"{tr[0]['xy_um'][-1]}")
    tz = traces_projetees(zig)
    v("un zigzag s'écarte de l'axe", max(abs(y) for _, y in tz[0]["xy_um"]) > 10.0,
      f"{max(abs(y) for _, y in tz[0]['xy_um'])}")
    v("... et revient à +x à la fin", abs(tz[0]["xy_um"][-1][1]) < 1e-6,
      f"{tz[0]['xy_um'][-1]}")
    v("les marches trop courtes n'ont pas de trace",
      traces_projetees([marche([(0.0, 0.0, 1.0)] * 4)]) == [])

    # ⚠ L'angle au radial est rendu comme description, et il le DIT.
    ar = langle_au_radial_initial(droite)
    v("l'angle au radial se déclare description seulement", ar["description_seulement"])
    v("... et une marche droite le long du radial rend zéro",
      ar["angle_premier_tiers_deg"] == 0.0, f"{ar['angle_premier_tiers_deg']}")

    # ⚠ Les refus d'entrée.
    with tempfile.TemporaryDirectory() as dd_:
        p = Path(dd_) / "c.json"
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
        # ⚠⚠ Et une course dont la trajectoire ne se reconstruit pas est REFUSÉE : mesurer une
        # dérive sur un chemin qui n'est pas celui de la course serait mesurer autre chose.
        cassee = {"lignes": [{"rayon_mm": 4.0 + i, "detail": [{
            "radial_zyx": [0.0, 0.0, 1.0],
            "etapes": [{"confirme": True, "direction": [0.0, 0.0, 1.0], "avance_um": 100.0,
                        "parcouru_um": 100.0 * (k + 1) + 9.0,
                        "desaccord_des_moities_deg": 10.0, "planarite": 0.4}
                       for k in range(12)]}]} for i in range(8)]}
        p.write_text(json.dumps(cassee), encoding="utf-8")
        try:
            mesurer(p)
            v("une trajectoire irréconciliable est refusée", False)
        except ValueError:
            v("une trajectoire irréconciliable est refusée", True)
        # ⚠ La coupe au premier pas aveugle est celle de `116`.
        avec = json.loads(json.dumps(cassee))
        for ligne in avec["lignes"]:
            for cel in ligne["detail"]:
                for k, e in enumerate(cel["etapes"]):
                    e["parcouru_um"] = 100.0 * (k + 1)
                    if k >= 8:
                        e["desaccord_des_moities_deg"] = 0.0
                        e["planarite"] = 0.0
        p.write_text(json.dumps(avec), encoding="utf-8")
        r = mesurer(p)
        v("les pas aveugles sont coupés, comme à 116", r["pas_voyants"] == 8 * 8,
          f"{r['pas_voyants']}")
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
