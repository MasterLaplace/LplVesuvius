#!/usr/bin/env python3
"""Combien de virage la matière demande-t-elle, et un cap à mémoire coûte-t-il quelque chose ?

⚠⚠⚠ POURQUOI CE FICHIER. `130` mesure que ce qui manque au marcheur est un **cap**, et `131` que
la fréquence de son recul ne se tranchera pas par plus de lecture. En cherchant où brancher un cap,
un fait du code est apparu : **`sens` ne choisit que le SIGNE**. La direction d'un pas est
entièrement celle du tenseur local, donc le marcheur n'avait aucun gouvernail — il n'existait aucun
mécanisme par lequel un cap aurait pu agir. `marcher` en reçoit un ici (`memoire_du_cap`), et une
mémoire nulle rend exactement le marcheur d'avant.

⭐⭐⭐⭐ **ET LA PREMIÈRE MESURE RENVERSE LA PRÉMISSE QUI A FAIT CONSTRUIRE LA SPIRALE.** J'avais
écrit qu'une pile enroulée ferait payer un cap rigide, puisque sa normale tourne. Elle tourne avec
l'ANGLE — or un marcheur qui traverse des feuilles avance **radialement**, donc à angle presque
constant. Sur une traversée radiale complète la normale vraie tourne de **quelques dixièmes de
degré**, pendant que le marcheur, lui, vire de plusieurs degrés par pas.

⚠⚠ **ET AUCUNE FIXTURE DU DÉPÔT NE REPRODUIT LA DÉRIVE DU VRAI ROULEAU.** Sur la pile plane
bruitée qui porte `124`, `127` et `128`, le marcheur rend une rectitude de **0,999** sur cent douze
pas. Le bruit d'intensité ne fait pas dériver : ce qui dérive est une matière dont les feuilles ne
sont pas parallèles, et c'est ce qu'aucune pile fabriquée n'a.

⚠ Aucune lecture distante : les fixtures sont analytiques et la course réelle est celle que `131`
a gardée.

  uv run python src/nappe/un_cap_a_memoire.py --verifier
  uv run python src/nappe/un_cap_a_memoire.py --json docs/mesures/un_cap_a_memoire.json
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
COURSE = RACINE / "docs" / "mesures" / "la_re_course_large.json"

MEMOIRES = (0.0, 0.25, 0.5, 0.75)
"""Les forces de cap comparées. 0 est le marcheur d'avant, donc la base.

⚠ Quatre valeurs et non un balayage : la question est de savoir SI une mémoire change quelque
chose et ce qu'elle coûte, pas de trouver la meilleure. Chercher la meilleure sur le corpus qui
sert à juger serait régler un seuil sur ce qui passe."""

GRAINES = (3, 11, 29, 53)
PAS = 112
RAYON_DEPART_UM = 8000.0


def _outils(demi: int = 20):
    from le_marcheur_reste_t_il_verrouille import _outils as o  # noqa: PLC0415

    return o(demi)


def _spirale(graine: int, bruit: float = 8.0):
    from combien_de_pas_la_matiere_porte import VolumeFabriqueEnSpirale  # noqa: PLC0415
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    # ⚠⚠ Le volume doit contenir le rayon d'ARRIVEE, pas seulement celui du depart : une
    # traversee complete part a 8 mm et finit vers 27, soit plus de onze mille voxels du centre.
    # Une forme trop petite ne rend pas une marche courte, elle rend ZERO pas.
    return VolumeFabriqueEnSpirale(C.PAS_UM, r0_um=4000.0, centre_yx_vx=(2000.0, 2000.0),
                                   bruit=bruit, graine=graine, forme=(20000, 20000, 20000))


def _depart_sur_la_spirale(sp, rayon_um: float = RAYON_DEPART_UM) -> np.ndarray:
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    return np.array([2000.0, 2000.0, 2000.0 + rayon_um / C.VOXEL_FIN_UM])


def combien_de_virage_la_matiere_demande(graine: int = 3, pas: int = PAS,
                                         demi: int = 20) -> dict:
    """Sur une pile enroulée, de combien la VRAIE normale tourne-t-elle sous une marche ?

    ⭐⭐⭐⭐ C'EST LA QUESTION QUE SEULE UNE FIXTURE PEUT RÉPONDRE, et elle borne tout le reste :
    si la matière ne demande presque aucun virage, alors un cap qui se souvient ne combat rien et
    sa seule fonction est d'enlever du bruit. Sur le vrai volume la vérité n'existe nulle part,
    donc la question n'y a pas de réponse.

    ⚠⚠ ET ELLE CORRIGE LA PRÉMISSE QUI A FAIT CONSTRUIRE LA SPIRALE. Sa normale tourne avec
    l'ANGLE, pas avec le rayon ; or un marcheur qui traverse des feuilles avance radialement, donc
    à angle presque constant. Une pile enroulée ne fait donc PAS payer un cap rigide, et c'est un
    fait de géométrie et non un choix de paramètre.
    """
    from combien_de_pas_la_matiere_porte import marcher  # noqa: PLC0415
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    o = _outils(demi)
    sp = _spirale(graine)
    dep = _depart_sur_la_spirale(sp)
    n0 = sp.normale_locale(dep.reshape(1, 3))[0]
    e = marcher(sp, dep, n0, o["longueurs"], o["mu"], o["sd"], o["barre"], o["barre_moities"],
                o["barre_interstice"], C.VOXEL_FIN_UM, pas_max=pas, demi=demi)
    lus = [x for x in e if "confirme" in x]
    if len(lus) < 3:
        return {"decidable": False, "pourquoi": f"{len(lus)} pas marchés"}
    p = dep.copy()
    rayons, angles, normales, directions = [], [], [], []
    for x in lus:
        rho, th = sp.cylindriques(p.reshape(1, 3))
        rayons.append(float(rho[0]))
        angles.append(float(th[0]))
        normales.append(sp.normale_locale(p.reshape(1, 3))[0])
        directions.append(np.asarray(x["direction"], dtype=np.float64))
        p = p + directions[-1] * (float(x["avance_um"]) / C.VOXEL_FIN_UM)
    rho, th = sp.cylindriques(p.reshape(1, 3))
    rayons.append(float(rho[0]))
    angles.append(float(th[0]))

    def _angle(a, b):
        return float(np.degrees(np.arccos(np.clip(abs(float(a @ b)), -1.0, 1.0))))

    vrais = [_angle(normales[i], normales[i + 1]) for i in range(len(normales) - 1)]
    siens = [_angle(directions[i], directions[i + 1]) for i in range(len(directions) - 1)]
    return {"decidable": True, "graine": graine, "pas": len(lus),
            "rayon_depart_um": round(rayons[0], 1), "rayon_arrivee_um": round(rayons[-1], 1),
            "angle_parcouru_deg": round(float(np.degrees(abs(angles[-1] - angles[0]))), 4),
            "virage_vrai_total_deg": round(_angle(normales[0], normales[-1]), 4),
            "virage_vrai_median_deg": round(float(np.median(vrais)), 4),
            "virage_vrai_max_deg": round(float(max(vrais)), 4),
            "virage_du_marcheur_median_deg": round(float(np.median(siens)), 2),
            "virage_du_marcheur_max_deg": round(float(max(siens)), 2),
            "facteur": round(float(np.median(siens)) / max(1e-9, float(np.median(vrais))), 1),
            # ⭐⭐⭐⭐ Le verdict : le marcheur tourne-t-il bien plus que la matière ne demande ?
            "le_marcheur_tourne_plus_que_la_matiere": bool(
                float(np.median(siens)) > 10.0 * float(np.median(vrais)))}


def le_virage_reel_persiste_t_il(course_p: Path = COURSE, minimum_de_pas: int = 20) -> dict:
    """Sur la VRAIE matière, le virage d'un pas au suivant persiste-t-il, ou alterne-t-il ?

    ⭐⭐⭐⭐ C'EST CE QUI DÉCIDE SI UNE MÉMOIRE PEUT AIDER. Un virage qui **persiste** est une
    matière qui courbe, et un cap qui se souvient la combattrait ; un virage qui **alterne** est du
    bruit, et c'est exactement ce qu'une moyenne enlève. Les deux rendent le même virage médian,
    donc le virage seul ne dit pas lequel on a.

    ⚠⚠ Le virage est pris comme un VECTEUR et non comme un angle : deux virages de même amplitude
    dans des directions opposées ont le même angle, et c'est précisément la différence qu'il faut
    voir. La composante du pas suivant perpendiculaire au pas courant est ce vecteur.

    ⚠ L'unité décisive est la MARCHE : les virages d'une marche partagent sa matière, donc les
    compter comme indépendants gonflerait n d'un facteur vingt.
    """
    from le_marcheur_derive_t_il import marches  # noqa: PLC0415

    d = json.loads(Path(course_p).read_text(encoding="utf-8"))
    pm = [m for m in marches(d) if m["pas_voyants"] >= minimum_de_pas]
    if len(pm) < 3:
        return {"decidable": False, "pourquoi": f"{len(pm)} marches d'au moins "
                                                f"{minimum_de_pas} pas"}
    par_marche = []
    for m in pm:
        D = [np.asarray(x, dtype=np.float64) for x in m["directions"]]
        virages = []
        for i in range(len(D) - 1):
            a, b = D[i], D[i + 1]
            perp = b - float(b @ a) * a
            n = float(np.linalg.norm(perp))
            virages.append(perp / n if n > 1e-12 else None)
        cos = [float(virages[i] @ virages[i + 1]) for i in range(len(virages) - 1)
               if virages[i] is not None and virages[i + 1] is not None]
        if cos:
            par_marche.append({"rayon_mm": m["rayon_mm"], "pas": m["pas_voyants"],
                               "cos_moyen": round(float(np.mean(cos)), 4)})
    if len(par_marche) < 3:
        return {"decidable": False, "pourquoi": "moins de trois marches exploitables"}
    vals = np.array([x["cos_moyen"] for x in par_marche])
    from scipy.stats import wilcoxon  # noqa: PLC0415

    p = float(wilcoxon(vals).pvalue)
    return {"decidable": True, "source": Path(course_p).name, "marches": len(par_marche),
            "par_marche": par_marche,
            "cos_median": round(float(np.median(vals)), 4),
            "cos_min": round(float(vals.min()), 4), "cos_max": round(float(vals.max()), 4),
            "marches_negatives": int((vals < 0).sum()),
            "p_contre_zero": round(p, 6),
            # ⭐⭐⭐⭐ Les deux verdicts, et ils ne sont pas complémentaires : une série qui ne
            # tranche pas rend faux aux deux, et c'est la réponse honnête.
            "le_virage_persiste": bool(float(np.median(vals)) > 0.0 and p < 0.01),
            "le_virage_alterne": bool(float(np.median(vals)) < 0.0 and p < 0.01)}


def ce_que_la_memoire_change(memoires=MEMOIRES, graines=GRAINES, pas: int = PAS,
                             demi: int = 20) -> dict:
    """Sur la spirale, une mémoire réduit-elle l'erreur à la vérité — et que coûte-t-elle ?

    ⭐⭐⭐ L'ERREUR EST MESURÉE CONTRE LA NORMALE VRAIE, ce que seule une fixture permet. Sur le
    vrai volume on ne peut comparer le marcheur qu'à lui-même, donc « il va plus droit » n'y veut
    dire que « il change moins d'avis ».

    ⚠⚠ LE TEST EST APPARIÉ GRAINE PAR GRAINE : la même réalisation de bruit est marchée à chaque
    mémoire. Comparer des graines différentes mesurerait surtout laquelle est tombée sur un tirage
    clément.

    ⚠ Le taux de confirmation est rendu à côté : une mémoire qui réduirait l'erreur en cessant de
    confirmer aurait déplacé le problème, pas résolu.
    """
    from combien_de_pas_la_matiere_porte import marcher  # noqa: PLC0415
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    o = _outils(demi)
    out = {"pas": pas, "graines": list(graines), "memoires": list(memoires), "par_memoire": []}
    for lam in memoires:
        lots = []
        for g in graines:
            sp = _spirale(g)
            dep = _depart_sur_la_spirale(sp)
            n0 = sp.normale_locale(dep.reshape(1, 3))[0]
            e = marcher(sp, dep, n0, o["longueurs"], o["mu"], o["sd"], o["barre"],
                        o["barre_moities"], o["barre_interstice"], C.VOXEL_FIN_UM,
                        pas_max=pas, demi=demi, memoire_du_cap=lam)
            lus = [x for x in e if "confirme" in x]
            if not lus:
                continue
            p = dep.copy()
            erreurs = []
            for x in lus:
                vrai = sp.normale_locale(p.reshape(1, 3))[0]
                dd = np.asarray(x["direction"], dtype=np.float64)
                erreurs.append(float(np.degrees(np.arccos(
                    np.clip(abs(float(dd @ vrai)), -1.0, 1.0)))))
                p = p + dd * (float(x["avance_um"]) / C.VOXEL_FIN_UM)
            lots.append({"graine": g, "pas": len(lus),
                         "erreur_mediane_deg": round(float(np.median(erreurs)), 3),
                         "erreur_max_deg": round(float(max(erreurs)), 3),
                         "taux": round(sum(1 for x in lus if x["confirme"]) / len(lus), 4)})
        if not lots:
            continue
        out["par_memoire"].append({
            "memoire": lam, "lots": len(lots),
            "erreur_mediane_deg": round(float(np.median(
                [x["erreur_mediane_deg"] for x in lots])), 3),
            "erreur_max_deg": round(float(np.median([x["erreur_max_deg"] for x in lots])), 3),
            "taux_median": round(float(np.median([x["taux"] for x in lots])), 4),
            "detail": lots})
    base = next((x for x in out["par_memoire"] if x["memoire"] == 0.0), None)
    if base:
        for x in out["par_memoire"]:
            if x["memoire"] == 0.0:
                continue
            x["gain_en_erreur_deg"] = round(base["erreur_mediane_deg"]
                                            - x["erreur_mediane_deg"], 3)
            x["cout_en_taux"] = round(base["taux_median"] - x["taux_median"], 4)
            # ⭐⭐⭐ Le verdict : moins d'erreur ET pas de taux sacrifié.
            x["la_memoire_aide"] = bool(x["erreur_mediane_deg"] < base["erreur_mediane_deg"]
                                        and x["taux_median"] >= base["taux_median"] - 0.05)
    return out


def la_pile_plane_derive_t_elle(graines=GRAINES, pas: int = PAS, demi: int = 20,
                                obliquite_deg: float = 35.0, bruit: float = 8.0) -> dict:
    """La fixture qui porte `124`, `127` et `128` reproduit-elle seulement la dérive ?

    ⭐⭐⭐⭐ C'EST LE CONTRÔLE QUI DÉCIDE DE CE QU'ON PEUT VALIDER ANALYTIQUEMENT. Si le marcheur
    va parfaitement droit sur la pile fabriquée, alors une proposition de cap n'y a **rien à
    réparer** : elle y paraîtrait inutile ou inoffensive selon le hasard, et dans les deux cas la
    mesure ne dirait rien du vrai rouleau.

    ⚠ Le bruit est celui des tranches qui s'en servent, pas un bruit choisi pour faire dériver :
    changer le bruit pour obtenir la dérive rendrait la fixture d'accord avec la conclusion.
    """
    from combien_de_pas_la_matiere_porte import VolumeFabrique, marcher  # noqa: PLC0415
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    o = _outils(demi)
    x_hat = np.array([0.0, 0.0, 1.0])
    lots = []
    for g in graines:
        cote = int(4000 + pas * C.PAS_UM / C.VOXEL_FIN_UM * 1.5)
        pile = VolumeFabrique(C.PAS_UM, obliquite_deg=obliquite_deg, bruit=bruit, graine=g,
                              forme=(cote, cote, cote))
        base = np.array([2000.0, 2000.0, 2000.0])
        proj = float(base @ pile.normale) * C.VOXEL_FIN_UM
        base = base + pile.normale * ((round(proj / C.PAS_UM) * C.PAS_UM - proj)
                                      / C.VOXEL_FIN_UM)
        e = marcher(pile, base, x_hat, o["longueurs"], o["mu"], o["sd"], o["barre"],
                    o["barre_moities"], o["barre_interstice"], C.VOXEL_FIN_UM,
                    pas_max=pas, demi=demi)
        lus = [x for x in e if "confirme" in x]
        if not lus:
            continue
        D = np.array([x["direction"] for x in lus], dtype=float)
        A = np.array([x["avance_um"] for x in lus], dtype=float)
        net = float(np.linalg.norm((D * A[:, None]).sum(axis=0)))
        virages = [float(np.degrees(np.arccos(np.clip(abs(float(D[i] @ D[i + 1])), -1.0, 1.0))))
                   for i in range(len(D) - 1)]
        lots.append({"graine": g, "pas": len(lus), "chemin_um": round(float(A.sum()), 1),
                     "net_um": round(net, 1),
                     "rectitude": round(net / max(1e-9, float(A.sum())), 4),
                     "virage_median_deg": round(float(np.median(virages)), 2),
                     "taux": round(sum(1 for x in lus if x["confirme"]) / len(lus), 4)})
    if not lots:
        return {"decidable": False, "pourquoi": "aucune marche"}
    rec = float(np.median([x["rectitude"] for x in lots]))
    return {"decidable": True, "obliquite_deg": obliquite_deg, "bruit": bruit,
            "pas": pas, "lots": len(lots), "detail": lots,
            "rectitude_mediane": round(rec, 4),
            "virage_median_deg": round(float(np.median(
                [x["virage_median_deg"] for x in lots])), 2),
            "taux_median": round(float(np.median([x["taux"] for x in lots])), 4),
            # ⭐⭐⭐⭐ Le verdict : la fixture a-t-elle seulement de quoi montrer une dérive ?
            "la_pile_plane_derive": bool(rec < 0.95)}


def mesurer(pas: int = PAS, graines=GRAINES, course_p: Path = COURSE) -> dict:
    """Tout, analytique — sauf la course réelle, qui est déjà gardée."""
    return {"combien_de_virage_la_matiere_demande": combien_de_virage_la_matiere_demande(
                pas=pas),
            "le_virage_reel_persiste_t_il": le_virage_reel_persiste_t_il(course_p),
            "ce_que_la_memoire_change": ce_que_la_memoire_change(graines=graines, pas=pas),
            "la_pile_plane_derive_t_elle": la_pile_plane_derive_t_elle(graines=graines,
                                                                      pas=pas)}


def afficher(r: dict) -> None:
    v = r["combien_de_virage_la_matiere_demande"]
    if v.get("decidable"):
        print(f"COMBIEN DE VIRAGE LA MATIÈRE DEMANDE — spirale, {v['pas']} pas")
        print(f"   rayon {v['rayon_depart_um']} → {v['rayon_arrivee_um']} µm, "
              f"angle parcouru {v['angle_parcouru_deg']}°")
        print(f"   virage VRAI : {v['virage_vrai_total_deg']}° en tout, "
              f"{v['virage_vrai_median_deg']}° par pas (max {v['virage_vrai_max_deg']})")
        print(f"   virage du MARCHEUR : {v['virage_du_marcheur_median_deg']}° par pas "
              f"(max {v['virage_du_marcheur_max_deg']})")
        print(f"   ⭐ facteur {v['facteur']}× · il tourne plus que la matière ne demande : "
              f"{v['le_marcheur_tourne_plus_que_la_matiere']}")
    a = r["le_virage_reel_persiste_t_il"]
    if a.get("decidable"):
        print(f"\nLE VIRAGE RÉEL PERSISTE-T-IL — {a['source']}, {a['marches']} marches")
        print(f"   cos entre virages consécutifs : médiane {a['cos_median']} "
              f"[{a['cos_min']} ; {a['cos_max']}] · {a['marches_negatives']}/{a['marches']} "
              f"négatives · p {a['p_contre_zero']}")
        print(f"   ⭐ persiste : {a['le_virage_persiste']} · ALTERNE : {a['le_virage_alterne']}")
    m = r["ce_que_la_memoire_change"]
    print(f"\nCE QUE LA MÉMOIRE CHANGE — spirale, {len(m['graines'])} graines, {m['pas']} pas")
    print("   mémoire   erreur médiane   erreur max   taux   gain   coût")
    for x in m["par_memoire"]:
        print(f"   {x['memoire']:>7.2f}   {x['erreur_mediane_deg']:>14.3f}° "
              f"{x['erreur_max_deg']:>11.3f}°   {x['taux_median']:.3f}"
              f"   {x.get('gain_en_erreur_deg', '')!s:>5}   {x.get('cout_en_taux', '')!s:>6}")
    p = r["la_pile_plane_derive_t_elle"]
    if p.get("decidable"):
        print(f"\n⚠⚠ LA PILE PLANE DÉRIVE-T-ELLE — obliquité {p['obliquite_deg']}°, "
              f"bruit {p['bruit']}, {p['pas']} pas")
        print(f"   rectitude médiane {p['rectitude_mediane']} · virage "
              f"{p['virage_median_deg']}°/pas · taux {p['taux_median']}")
        print(f"   ⭐ elle dérive : {p['la_pile_plane_derive']}")


def verifier() -> int:
    """La batterie, hors ligne, sur peu de pas — et cinq sondes."""
    echecs = controles = 0

    def v(nom, obtenu, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not obtenu:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f" — {detail}" if detail else ""))

    from combien_de_pas_la_matiere_porte import VolumeFabrique, marcher  # noqa: PLC0415
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    o = _outils(20)
    x_hat = np.array([0.0, 0.0, 1.0])
    pile = VolumeFabrique(C.PAS_UM, obliquite_deg=35.0, bruit=8.0, graine=3,
                          forme=(9000, 9000, 9000))
    base = np.array([2000.0, 2000.0, 2000.0])

    def course(lam, pas=8):
        return [x for x in marcher(pile, base, x_hat, o["longueurs"], o["mu"], o["sd"],
                                   o["barre"], o["barre_moities"], o["barre_interstice"],
                                   C.VOXEL_FIN_UM, pas_max=pas, demi=20,
                                   memoire_du_cap=lam) if "confirme" in x]

    # ⭐⭐⭐⭐ LE CONTRÔLE QUI PROTÈGE TOUT LE DÉPÔT : une mémoire NULLE doit rendre exactement le
    # marcheur d'avant, sinon ce paramètre déplacerait chaque mesure déjà publiée.
    sans = course(0.0)
    avant = [round(float(x["avance_um"]), 6) for x in sans]
    dirs = [[round(float(t), 9) for t in x["direction"]] for x in sans]
    encore = course(0.0)
    v("une mémoire NULLE est reproductible",
      [round(float(x["avance_um"]), 6) for x in encore] == avant)
    v("... et ses directions sont identiques",
      [[round(float(t), 9) for t in x["direction"]] for x in encore] == dirs)
    v("... et la marche avance", len(sans) >= 6, f"{len(sans)} pas")
    # ⚠ Sonde : une mémoire non nulle DOIT changer quelque chose, sinon le paramètre serait inerte
    # et tout ce qui suit mesurerait deux fois la même marche.
    avec = course(0.75)
    v("⭐ une mémoire non nulle change les directions",
      [[round(float(t), 9) for t in x["direction"]] for x in avec] != dirs)

    # ⭐⭐⭐ LE VIRAGE VECTORIEL : deux virages de même amplitude et de sens opposés ont le même
    # ANGLE, et c'est la différence qu'il faut voir. Sur des directions fabriquées qui alternent,
    # le cosinus doit être négatif ; sur des directions qui tournent toujours du même côté, positif.
    def faux_course(dirs_):
        return {"lignes": [{"rayon_mm": 4.0, "detail": [{"etapes": [
            {"confirme": True, "direction": list(d), "avance_um": 100.0,
             "parcouru_um": 100.0 * (i + 1), "desaccord_des_moities_deg": 1.0,
             "planarite": 0.9} for i, d in enumerate(dirs_)]}]}]}

    def tourne(n, pas_deg, alterne):
        out, a = [], 0.0
        for i in range(n):
            a += np.radians(pas_deg) * ((-1.0) ** i if alterne else 1.0)
            out.append([0.0, np.sin(a), np.cos(a)])
        return out

    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as dtmp:
        j = Path(dtmp) / "c.json"
        for nom, alterne, attendu in (("qui ALTERNE", True, "alterne"),
                                      ("qui PERSISTE", False, "persiste")):
            # ⚠⚠ DIX MARCHES ET NON SIX, parce qu'un Wilcoxon a six paires ne peut PAS descendre
            # sous 0,01 : son p plancher vaut 2/2^6 = 0,031. Une fixture a six marches rendait
            # donc un controle IMPOSSIBLE A PASSER, quel que soit le signal — et il echouait en
            # affichant un cosinus de −0,9945, c'est-a-dire un signal parfait.
            c = faux_course(tourne(30, 6.0, alterne))
            c["lignes"] = [c["lignes"][0] for _ in range(10)]
            j.write_text(json.dumps(c), encoding="utf-8")
            r = le_virage_reel_persiste_t_il(j)
            v(f"⭐ un virage {nom} est vu comme tel",
              r.get(f"le_virage_{attendu}") is True, f"cos {r.get('cos_median')}")
            v(f"... et pas comme l'autre",
              r.get("le_virage_persiste" if attendu == "alterne"
                    else "le_virage_alterne") is False)
        # ⚠ Sonde : moins de trois marches rend INDECIDABLE, jamais « pas de persistance ».
        c = faux_course(tourne(30, 6.0, True))
        j.write_text(json.dumps(c), encoding="utf-8")
        v("moins de trois marches rend indécidable",
          le_virage_reel_persiste_t_il(j).get("decidable") is False)

    # ⚠⚠ La pile plane : le verdict doit pouvoir rendre VRAI, sinon « elle ne dérive pas » serait
    # vrai par construction. Une pile au bruit énorme doit, elle, dériver.
    d_propre = la_pile_plane_derive_t_elle(graines=(3,), pas=10)
    v("la pile plane est mesurée", d_propre.get("decidable"))
    v("⭐ et le marcheur y va droit", not d_propre["la_pile_plane_derive"],
      f"rectitude {d_propre['rectitude_mediane']}")
    d_sale = la_pile_plane_derive_t_elle(graines=(3,), pas=10, bruit=60.0)
    v("⭐ sonde : une pile au bruit ÉNORME, elle, dérive",
      d_sale["la_pile_plane_derive"], f"rectitude {d_sale['rectitude_mediane']}")

    # ⭐⭐ La spirale : la matière demande-t-elle peu de virage, et le marcheur en fait-il plus ?
    w = combien_de_virage_la_matiere_demande(pas=12)
    v("le virage demandé par la matière est mesuré", w.get("decidable"), f"{w.get('pourquoi')}")
    v("⭐ la matière enroulée demande très peu de virage",
      w["virage_vrai_median_deg"] < 0.2, f"{w['virage_vrai_median_deg']}°")
    v("⭐ ... et le marcheur en fait bien plus",
      w["le_marcheur_tourne_plus_que_la_matiere"], f"facteur {w['facteur']}")
    v("... et la marche est bien restée presque au même angle",
      w["angle_parcouru_deg"] < 2.0, f"{w['angle_parcouru_deg']}°")

    m = ce_que_la_memoire_change(memoires=(0.0, 0.5), graines=(3,), pas=10)
    v("la mémoire est comparée à la base", len(m["par_memoire"]) == 2)
    v("... et la base est bien la mémoire nulle", m["par_memoire"][0]["memoire"] == 0.0)
    v("... et le gain est rendu à côté du coût",
      "gain_en_erreur_deg" in m["par_memoire"][1]
      and "cout_en_taux" in m["par_memoire"][1])

    print(f"\n{'ALL PASS' if echecs == 0 else 'ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path)
    p.add_argument("--pas", type=int, default=PAS)
    p.add_argument("--course", type=Path, default=COURSE)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(pas=a.pas, course_p=a.course)
    afficher(r)
    if a.json:
        a.json.write_text(json.dumps(r, indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
