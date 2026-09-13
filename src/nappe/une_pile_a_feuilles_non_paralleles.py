#!/usr/bin/env python3
"""Une pile a feuilles non paralleles fait-elle virer le marcheur comme le vrai rouleau ?

⭐⭐⭐⭐ POURQUOI CE FICHIER EXISTE. `132` a elimine les deux causes qu'on aurait supposees au
virage de 14° par pas du vrai rouleau : ni l'enroulement (0,0103°/pas sur une spirale ideale) ni le
bruit d'intensite (rectitude 0,9994 sur la pile plane bruitee). Il a nomme l'hypothese restante —
des feuilles NON PARALLELES — et dit que la fixture manquait. `133` a couru le cap sur le vrai
rouleau et mesure qu'il redresse ; ce qu'il ne peut pas dire, c'est POURQUOI le marcheur virait,
parce que sur le vrai volume la normale vraie est inconnue. Ici elle est connue.

⭐⭐⭐⭐ LA FIXTURE EST CALIBREE SUR UNE GRANDEUR QUE LE VRAI ROULEAU MESURE DEJA, ET QUI N'EST PAS
LA DERIVE. Chaque pas d'une course garde `desaccord_des_moities_deg` — l'angle entre les directions
lues sur les deux moities disjointes du cube (`100`). Sur la pile plane et sur la spirale il est
presque nul ; sur le rouleau il ne l'est pas. La pile froissee (`VolumeFabriqueOndulee`) recoit
l'amplitude qui reproduit la MEDIANE reelle de ce desaccord, par bissection, sans jamais regarder
la rectitude ni le virage du marcheur. Puis on demande si le marcheur y vire comme sur le rouleau.
Regler la fixture sur la dérive qu'elle doit reproduire serait la faute numero un du depot.

⚠⚠ LA LONGUEUR D'ONDE N'EST PAS CALIBRABLE PAR LA MEME CIBLE, donc elle est BALAYEE a trois
valeurs DERIVEES du cube de lecture — une, deux et quatre fois son cote — et le verdict est rendu
pour chacune. Si la reponse depend de la longueur d'onde, le document doit le dire plutot que
choisir celle qui arrange.

⚠ Le controle est la pile plane de `124`, `127` et `128`, meme bruit : son desaccord doit rester
loin de la cible, sinon la calibration n'aurait rien a faire et le verdict serait vide.

Usage :
    uv run python src/nappe/une_pile_a_feuilles_non_paralleles.py --verifier
    uv run python src/nappe/une_pile_a_feuilles_non_paralleles.py \\
        --json docs/mesures/une_pile_a_feuilles_non_paralleles.json
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
COURSE_A_CAP = RACINE / "docs" / "mesures" / "la_course_a_cap.json"
DEMI = 20
GRAINES = (3, 11, 29)
MEMOIRES = (0.0, 0.75)
PAS = 112
BRUIT = 8.0
OBLIQUITE = 35.0
CUBES_DE_CALIBRATION = 40
TOLERANCE_DEG = 0.25


def cote_du_cube_um(demi: int = DEMI) -> float:
    """Le cote du cube de lecture en micrometres — l'echelle dont les longueurs d'onde derivent."""
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    return (2 * demi + 1) * C.VOXEL_FIN_UM


def longueurs_donde_um(demi: int = DEMI) -> list[float]:
    """Une, deux et quatre fois le cote du cube : derivees, pas choisies."""
    c = cote_du_cube_um(demi)
    return [round(c, 1), round(2 * c, 1), round(4 * c, 1)]


def _quantiles(valeurs) -> dict:
    a = np.asarray([x for x in valeurs if x is not None and np.isfinite(x)], dtype=float)
    if len(a) == 0:
        return {"n": 0}
    return {"n": int(len(a)), "mediane": round(float(np.median(a)), 2),
            "p25": round(float(np.percentile(a, 25)), 2),
            "p75": round(float(np.percentile(a, 75)), 2),
            "p90": round(float(np.percentile(a, 90)), 2)}


def le_desaccord_reel(course_p: Path = COURSE) -> dict:
    """La distribution du desaccord des deux moities sur les pas VOYANTS d'une vraie course.

    ⚠ Les pas aveugles sont ecartes : un cube qui ne lit rien rend un desaccord de 0,00° exactement
    (`115`), qui tirerait la distribution vers un accord que la matiere n'a pas donne.
    """
    from ce_qui_porte_le_taux import est_aveugle  # noqa: PLC0415

    d = json.loads(course_p.read_text(encoding="utf-8"))
    vals, virages = [], []
    for ligne in d.get("lignes", []):
        for cel in ligne.get("detail", []):
            etapes = [e for e in cel.get("etapes", []) if "confirme" in e]
            n = next((i for i, e in enumerate(etapes) if est_aveugle(e)), len(etapes))
            voyants = etapes[:n]
            vals.extend(e.get("desaccord_des_moities_deg") for e in voyants)
            dirs = np.asarray([e["direction"] for e in voyants], dtype=float)
            if len(dirs) >= 2:
                v_ = [float(np.degrees(np.arccos(np.clip(float(a @ b), -1.0, 1.0))))
                      for a, b in zip(dirs, dirs[1:])]
                virages.append(float(np.median(v_)))
    q = _quantiles(vals)
    q["source"] = course_p.name
    q["memoire_du_cap"] = d.get("memoire_du_cap", 0.0)
    # ⚠ Le virage est publie PAR MARCHE puis resume, jamais melange en un seul sac : deux marches
    # de longueurs tres differentes pesent alors pareil, comme dans `le_marcheur_derive_t_il`.
    q["virage_par_pas"] = _quantiles(virages)
    # ⚠ La persistance reelle est celle que `132` mesure, appelee et non recopiee : deux cosinus
    # calcules a deux endroits seraient libres de ne pas s'accorder sur ce qu'est un virage.
    from un_cap_a_memoire import le_virage_reel_persiste_t_il  # noqa: PLC0415

    pers = le_virage_reel_persiste_t_il(course_p)
    q["cos_virages_median"] = pers.get("cos_median") if pers.get("decidable") else None
    return q


def desaccord_de_la_pile(pile, cubes: int = CUBES_DE_CALIBRATION, demi: int = DEMI,
                         graine: int = 1) -> dict:
    """La distribution du desaccord des moities sur des cubes tires au hasard dans la pile.

    ⚠ Les centres sont tires UNIFORMEMENT dans l'interieur, avec la marge du cube : c'est la seule
    facon que la distribution ne depende pas d'un chemin particulier — un marcheur, lui, ne
    visite que la ou il va.
    """
    from combien_de_pas_la_matiere_porte import direction_de_la_matiere  # noqa: PLC0415

    r = np.random.default_rng(graine)
    forme = np.asarray(pile.forme, dtype=float)
    vals = []
    for _ in range(int(cubes)):
        c = r.uniform(demi + 2, forme - demi - 2)
        _, des, _ = direction_de_la_matiere(pile, c, demi, 1)
        vals.append(des)
    return _quantiles(vals)


VARIANTES = ("en_phase", "par_feuille")
"""Les deux froissements : le meme sur toutes les feuilles, ou un par feuille.

⭐⭐⭐⭐ La premiere mesure n'a tourne qu'en phase, et la pile calibree n'a PAS fait virer le
marcheur (3,1° a 5,6° par pas pour 13,6° reels). Une raison se lisait dans la fixture : un
marcheur qui suit la normale MOYENNE garde sa position dans le plan des feuilles, donc un
froissement partage par toutes les feuilles est pour lui une inclinaison constante. ⚠ Elle n'est
vraie que du marcheur ideal — le reel suit la normale LOCALE et glisse des que l'inclinaison est
forte (27° par pas a 20 µm d'amplitude, mesure) — donc elle ne decide de rien : c'est la seconde
variante, calibree de la meme facon, qui repond. Elle est une matiere qui distingue ses feuilles
(`R4-P26`)."""


def _pile(amplitude_um: float, longueur_donde_um: float, graine: int, forme=(4000, 4000, 4000),
          par_feuille: bool = False):
    from combien_de_pas_la_matiere_porte import VolumeFabriqueOndulee  # noqa: PLC0415
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    return VolumeFabriqueOndulee(C.PAS_UM, amplitude_um=amplitude_um,
                                 longueur_donde_um=longueur_donde_um, obliquite_deg=OBLIQUITE,
                                 bruit=BRUIT, graine=graine, forme=forme, par_feuille=par_feuille)


def calibrer_lamplitude(longueur_donde_um: float, cible_deg: float, graine: int = 3,
                        cubes: int = CUBES_DE_CALIBRATION, demi: int = DEMI,
                        tolerance_deg: float = TOLERANCE_DEG, iterations: int = 14,
                        par_feuille: bool = False) -> dict:
    """L'amplitude de froissement qui rend la MEDIANE reelle du desaccord, par bissection.

    ⭐⭐⭐ C'EST UNE CALIBRATION SUR UNE CIBLE MESUREE, PAS UN REGLAGE : la cible vient du vrai
    rouleau et la fixture n'est jamais regardee sur ce qu'on lui demandera ensuite. La borne haute
    de la recherche est l'amplitude qui incline la feuille a 60°, au-dela de quoi une pile n'est
    plus une pile.

    ⚠ Une cible qu'aucune amplitude n'atteint est DITE (`atteint` faux) : la bissection rend alors
    l'amplitude la plus proche, et le verdict qui en decoule est marque comme tel.
    """
    a_max = float(longueur_donde_um) * np.tan(np.radians(60.0)) / (2.0 * np.pi)
    bas, haut = 0.0, a_max
    def des(a):
        return desaccord_de_la_pile(_pile(a, longueur_donde_um, graine, par_feuille=par_feuille),
                                    cubes, demi)["mediane"]

    des_haut, des_bas = des(haut), des(bas)
    historique = [{"amplitude_um": round(bas, 3), "mediane_deg": des_bas},
                  {"amplitude_um": round(haut, 3), "mediane_deg": des_haut}]
    if des_haut < cible_deg:
        return {"decidable": True, "atteint": False, "amplitude_um": round(haut, 3),
                "mediane_deg": des_haut, "cible_deg": cible_deg,
                "pourquoi": "meme l'inclinaison maximale ne rend pas la cible",
                "historique": historique}
    milieu, des_m = haut, des_haut
    for _ in range(int(iterations)):
        milieu = 0.5 * (bas + haut)
        des_m = des(milieu)
        historique.append({"amplitude_um": round(milieu, 3), "mediane_deg": des_m})
        if abs(des_m - cible_deg) <= tolerance_deg:
            break
        if des_m < cible_deg:
            bas = milieu
        else:
            haut = milieu
    pile = _pile(milieu, longueur_donde_um, graine, par_feuille=par_feuille)
    return {"decidable": True, "atteint": bool(abs(des_m - cible_deg) <= tolerance_deg),
            "par_feuille": bool(par_feuille),
            "amplitude_um": round(milieu, 3), "mediane_deg": des_m, "cible_deg": cible_deg,
            "inclinaison_max_deg": round(pile.inclinaison_max_deg(), 2),
            "iterations": len(historique) - 2, "historique": historique}


def le_marcheur_sur_la_pile(amplitude_um: float, longueur_donde_um: float,
                            graines=GRAINES, memoires=MEMOIRES, pas: int = PAS,
                            demi: int = DEMI, par_feuille: bool = False) -> dict:
    """Le marcheur, lache sur la pile froissee calibree : vire-t-il, et la memoire l'aide-t-elle ?

    ⭐⭐⭐ L'ERREUR EST MESUREE CONTRE LA NORMALE VRAIE, ce que seule une fixture permet, et le
    desaccord RENCONTRE est publie a cote : c'est le controle que la calibration tient la ou le
    marcheur passe, et pas seulement sur des cubes tires au hasard.

    ⚠ Apparie graine par graine, comme `132` : la meme pile est marchee a chaque memoire.
    """
    from combien_de_pas_la_matiere_porte import marcher  # noqa: PLC0415
    import combien_dinterstices_traverses as C  # noqa: PLC0415
    from le_marcheur_reste_t_il_verrouille import _outils  # noqa: PLC0415

    o = _outils(demi)
    cote = int(4000 + pas * C.PAS_UM / C.VOXEL_FIN_UM * 1.5)
    out = {"amplitude_um": amplitude_um, "longueur_donde_um": longueur_donde_um,
           "par_feuille": bool(par_feuille), "pas": pas, "graines": list(graines),
           "par_memoire": []}
    for lam in memoires:
        lots = []
        for g in graines:
            pile = _pile(amplitude_um, longueur_donde_um, g, forme=(cote, cote, cote),
                         par_feuille=par_feuille)
            dep = np.array([2000.0, 2000.0, 2000.0])
            n0 = pile.normale_locale(dep.reshape(1, 3))[0]
            e = marcher(pile, dep, n0, o["longueurs"], o["mu"], o["sd"], o["barre"],
                        o["barre_moities"], o["barre_interstice"], C.VOXEL_FIN_UM,
                        pas_max=pas, demi=demi, memoire_du_cap=lam)
            lus = [x for x in e if "confirme" in x]
            if len(lus) < 2:
                continue
            D = np.asarray([x["direction"] for x in lus], dtype=float)
            A = np.asarray([x["avance_um"] for x in lus], dtype=float)
            p = dep.copy()
            erreurs = []
            for x in lus:
                vrai = pile.normale_locale(p.reshape(1, 3))[0]
                dd = np.asarray(x["direction"], dtype=float)
                erreurs.append(float(np.degrees(np.arccos(np.clip(abs(float(dd @ vrai)), -1, 1)))))
                p = p + dd * (float(x["avance_um"]) / C.VOXEL_FIN_UM)
            virages = [float(np.degrees(np.arccos(np.clip(float(a @ b), -1.0, 1.0))))
                       for a, b in zip(D, D[1:])]
            # ⭐⭐⭐ LA PERSISTANCE DU VIRAGE, comme `132` la mesure sur le rouleau : le cosinus entre
            # deux virages consecutifs pris comme VECTEURS. Un virage qui alterne (cos < 0) se
            # compense et laisse la marche droite ; un virage qui persiste la fait deriver. C'est
            # ce qui separe « tourner autant que le rouleau » de « deriver comme lui ».
            vecs = []
            for a, b in zip(D, D[1:]):
                perp = b - a * float(a @ b)
                n_ = float(np.linalg.norm(perp))
                vecs.append(perp / n_ if n_ > 1e-12 else None)
            cos_ = [float(u @ w) for u, w in zip(vecs, vecs[1:]) if u is not None and w is not None]
            net = float(np.linalg.norm((D * A[:, None]).sum(axis=0)))
            lots.append({"graine": g, "pas": len(lus),
                         "rectitude": round(net / max(1e-9, float(A.sum())), 4),
                         "virage_median_deg": round(float(np.median(virages)), 2),
                         "cos_virages_median": (round(float(np.median(cos_)), 4) if cos_ else None),
                         "erreur_a_la_normale_vraie_deg": round(float(np.median(erreurs)), 3),
                         "desaccord_rencontre_median_deg": round(float(np.median(
                             [x["desaccord_des_moities_deg"] for x in lus
                              if x.get("desaccord_des_moities_deg") is not None])), 2),
                         "taux": round(sum(1 for x in lus if x["confirme"]) / len(lus), 4)})
        if not lots:
            continue
        med = lambda k: round(float(np.median([x[k] for x in lots])), 4)  # noqa: E731
        out["par_memoire"].append({
            "memoire": lam, "lots": len(lots), "detail": lots,
            "rectitude_mediane": med("rectitude"),
            "virage_median_deg": round(med("virage_median_deg"), 2),
            "cos_virages_median": (round(float(np.median([x["cos_virages_median"] for x in lots
                                                          if x["cos_virages_median"] is not None])), 4)
                                   if any(x["cos_virages_median"] is not None for x in lots) else None),
            "erreur_mediane_deg": round(med("erreur_a_la_normale_vraie_deg"), 3),
            "desaccord_rencontre_median_deg": round(med("desaccord_rencontre_median_deg"), 2),
            "taux_median": med("taux")})
    base = next((x for x in out["par_memoire"] if x["memoire"] == 0.0), None)
    if base:
        for x in out["par_memoire"]:
            if x["memoire"] == 0.0:
                continue
            x["gain_en_virage_deg"] = round(base["virage_median_deg"] - x["virage_median_deg"], 2)
            x["gain_en_erreur_deg"] = round(base["erreur_mediane_deg"] - x["erreur_mediane_deg"], 3)
            x["cout_en_taux"] = round(base["taux_median"] - x["taux_median"], 4)
    return out


def juger(reel: dict, pile: dict, controle: dict) -> dict:
    """La pile calibree fait-elle virer le marcheur DANS LA FOURCHETTE du vrai rouleau ?

    ⭐⭐⭐ LA FOURCHETTE EST MESUREE, PAS CHOISIE : c'est l'intervalle p25-p75 des virages medians
    par marche de la vraie course. Un virage de la pile qui y tombe reproduit le rouleau ; au-dessous,
    la pile est trop sage ; au-dessus, trop folle. Le controle — la pile plane — doit tomber
    au-dessous, sinon le verdict ne distingue rien.
    """
    v_reel = reel.get("virage_par_pas", {})
    base = next((x for x in pile.get("par_memoire", []) if x["memoire"] == 0.0), None)
    if base is None or v_reel.get("n", 0) < 3:
        return {"decidable": False, "pourquoi": "pas de marche a memoire nulle, ou trop peu de "
                                                 "marches reelles"}
    v = base["virage_median_deg"]
    bas, haut = v_reel["p25"], v_reel["p75"]
    return {"decidable": True, "virage_de_la_pile_deg": v,
            "fourchette_reelle_deg": [bas, haut], "virage_reel_median_deg": v_reel["mediane"],
            "virage_du_controle_deg": controle.get("virage_median_deg"),
            "la_pile_vire_comme_le_rouleau": bool(bas <= v <= haut),
            "la_pile_vire_moins": bool(v < bas), "la_pile_vire_plus": bool(v > haut),
            "le_controle_vire_moins": bool(controle.get("virage_median_deg") is not None
                                           and controle["virage_median_deg"] < bas)}


def mesurer(course_p: Path = COURSE, graines=GRAINES, pas: int = PAS, demi: int = DEMI,
            longueurs=None, cubes: int = CUBES_DE_CALIBRATION) -> dict:
    from la_normale_nest_pas_le_rayon import avancement, maintenant  # noqa: PLC0415
    from combien_de_pas_la_matiere_porte import VolumeFabrique  # noqa: PLC0415
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    t0 = maintenant()
    reel = le_desaccord_reel(course_p)
    reel_cap = le_desaccord_reel(COURSE_A_CAP) if COURSE_A_CAP.is_file() else None
    plane = VolumeFabrique(C.PAS_UM, obliquite_deg=OBLIQUITE, bruit=BRUIT, graine=GRAINES[0])
    controle_desaccord = desaccord_de_la_pile(plane, cubes, demi)
    # ⚠ Le controle marche AUSSI : un desaccord nul qui ferait quand meme virer le marcheur
    # rendrait la calibration hors sujet, et il faut pouvoir le voir.
    controle_marche = le_marcheur_sur_la_pile(0.0, longueurs_donde_um(demi)[0], graines,
                                              (0.0,), pas, demi)["par_memoire"][0]
    out = {"source": course_p.name, "desaccord_reel": reel, "desaccord_reel_a_cap": reel_cap,
           "controle_pile_plane": {"desaccord": controle_desaccord, "marche": controle_marche},
           "cote_du_cube_um": round(cote_du_cube_um(demi), 1), "bruit": BRUIT,
           "obliquite_deg": OBLIQUITE, "graines": list(graines), "pas": pas,
           "par_longueur_donde": []}
    lds = longueurs or longueurs_donde_um(demi)
    etapes = [(v_, ld) for v_ in VARIANTES for ld in lds]
    for i, (variante, ld) in enumerate(etapes):
        pf = variante == "par_feuille"
        cal = calibrer_lamplitude(ld, reel["mediane"], GRAINES[0], cubes, demi, par_feuille=pf)
        marche = le_marcheur_sur_la_pile(cal["amplitude_um"], ld, graines, MEMOIRES, pas, demi,
                                         par_feuille=pf)
        out["par_longueur_donde"].append({
            "variante": variante, "longueur_donde_um": ld, "calibration": cal, "marche": marche,
            "verdict": juger(reel, marche, controle_marche)})
        avancement(i + 1, len(etapes), "piles", t0)
    # ⭐⭐⭐⭐ Le verdict de la tranche, par variante : une seule longueur d'onde qui reproduit le
    # rouleau suffit a dire que la variante PEUT le faire ; aucune, qu'elle ne le peut pas.
    out["par_variante"] = {
        v_: {"une_longueur_donde_vire_comme_le_rouleau": any(
                 x["verdict"].get("la_pile_vire_comme_le_rouleau") for x in out["par_longueur_donde"]
                 if x["variante"] == v_),
             "toutes_virent_moins": all(
                 x["verdict"].get("la_pile_vire_moins") for x in out["par_longueur_donde"]
                 if x["variante"] == v_),
             "virages_deg": [x["verdict"].get("virage_de_la_pile_deg")
                             for x in out["par_longueur_donde"] if x["variante"] == v_]}
        for v_ in VARIANTES}
    out["secondes"] = round(maintenant() - t0, 1)
    return out


def afficher(r: dict) -> None:
    d = r["desaccord_reel"]
    print(f"désaccord des moitiés RÉEL ({d['source']}) : médiane {d['mediane']}° "
          f"[{d['p25']} ; {d['p75']}], p90 {d['p90']} sur {d['n']} pas voyants · "
          f"virage réel médian {d['virage_par_pas']['mediane']}° "
          f"[{d['virage_par_pas']['p25']} ; {d['virage_par_pas']['p75']}]")
    c = r["controle_pile_plane"]
    print(f"contrôle, pile plane : désaccord médian {c['desaccord']['mediane']}° · "
          f"virage {c['marche']['virage_median_deg']}° · rectitude {c['marche']['rectitude_mediane']}")
    for x in r["par_longueur_donde"]:
        cal, v = x["calibration"], x["verdict"]
        print(f"\n[{x.get('variante', 'en_phase')}] λ = {x['longueur_donde_um']} µm · amplitude calibrée {cal['amplitude_um']} µm "
              f"(inclinaison max {cal.get('inclinaison_max_deg')}°) · désaccord obtenu "
              f"{cal['mediane_deg']}° pour {cal['cible_deg']}° · atteint {cal['atteint']}")
        for m in x["marche"]["par_memoire"]:
            print(f"   mémoire {m['memoire']:.2f} · virage {m['virage_median_deg']}° (cos {m.get('cos_virages_median')}) · rectitude "
                  f"{m['rectitude_mediane']} · erreur à la normale vraie {m['erreur_mediane_deg']}° · "
                  f"désaccord rencontré {m['desaccord_rencontre_median_deg']}° · taux {m['taux_median']}"
                  + (f" · coût en taux {m['cout_en_taux']}" if "cout_en_taux" in m else ""))
        if v.get("decidable"):
            print(f"   ★ la pile vire comme le rouleau : {v['la_pile_vire_comme_le_rouleau']} "
                  f"({v['virage_de_la_pile_deg']}° pour [{v['fourchette_reelle_deg'][0]} ; "
                  f"{v['fourchette_reelle_deg'][1]}]) · moins {v['la_pile_vire_moins']} · plus "
                  f"{v['la_pile_vire_plus']} · le contrôle vire moins {v['le_controle_vire_moins']}")
    for v_, x in r.get("par_variante", {}).items():
        print(f"\n★★★ {v_} : une longueur d'onde vire comme le rouleau : "
              f"{x['une_longueur_donde_vire_comme_le_rouleau']} · toutes virent moins : "
              f"{x['toutes_virent_moins']} · virages {x['virages_deg']}")
    print(f"\n{r.get('secondes')} s")


def verifier() -> int:
    echecs = controles = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    lds = longueurs_donde_um()
    v("les longueurs d'onde sont une, deux et quatre fois le côté du cube",
      len(lds) == 3 and abs(lds[1] - 2 * lds[0]) < 0.2 and abs(lds[2] - 4 * lds[0]) < 0.2,
      f"{lds}")
    v("... et le côté du cube est celui du marcheur", abs(cote_du_cube_um() - 41 * 2.4) < 1e-9)

    # ⭐⭐⭐ LE DESACCORD CROIT AVEC L'AMPLITUDE, sinon la bissection n'a pas de sens.
    plane_q = desaccord_de_la_pile(_pile(0.0, lds[1], 3), cubes=12)
    d0 = plane_q["mediane"]
    d1 = desaccord_de_la_pile(_pile(10.0, lds[1], 3), cubes=12)["mediane"]
    d2 = desaccord_de_la_pile(_pile(30.0, lds[1], 3), cubes=12)["mediane"]
    v("le désaccord des moitiés croît avec l'amplitude du froissement", d0 < d1 < d2,
      f"{d0} < {d1} < {d2}")

    # ⭐⭐⭐⭐ LA CALIBRATION ATTEINT UNE CIBLE ATTEIGNABLE, et refuse d'affirmer une cible hors
    # de portee : une bissection qui rendrait toujours « atteint » serait un reglage deguise.
    cal = calibrer_lamplitude(lds[1], cible_deg=d1, cubes=12, iterations=10, tolerance_deg=0.5)
    v("la bissection retrouve une cible atteignable", cal["atteint"]
      and abs(cal["mediane_deg"] - d1) <= 0.5, f"{cal['amplitude_um']} µm → {cal['mediane_deg']}°")
    v("... près de l'amplitude qui l'a produite", abs(cal["amplitude_um"] - 10.0) < 4.0,
      f"{cal['amplitude_um']} µm pour 10")
    hors = calibrer_lamplitude(lds[1], cible_deg=89.0, cubes=6, iterations=3)
    v("sonde : une cible inatteignable est DITE inatteignable", hors["atteint"] is False
      and "pourquoi" in hors)

    # ⭐⭐⭐ LE DESACCORD REEL EST LU SUR LES PAS VOYANTS, et sa fixture fabriquée le prouve.
    import tempfile  # noqa: PLC0415
    with tempfile.TemporaryDirectory() as dtmp:
        j = Path(dtmp) / "c.json"
        def etape(k, des, aveugle=False):
            return {"pas": k, "confirme": True, "oriente": True, "rien_lu": aveugle,
                    "desaccord_des_moities_deg": 0.0 if aveugle else des, "planarite": 0.0 if aveugle else 0.4,
                    "score_du_balayage": 0.0 if aveugle else 1.0, "accord_de_linterstice": 0.0 if aveugle else 0.9,
                    "direction": [0.0, np.sin(0.1 * k), np.cos(0.1 * k)], "avance_um": 173.0,
                    "parcouru_um": 173.0 * k}
        j.write_text(json.dumps({"memoire_du_cap": 0.0, "lignes": [
            {"de": 0, "a": 1, "detail": [{"etapes": [etape(1, 5.0), etape(2, 7.0), etape(3, 9.0),
                                                     etape(4, 0.0, aveugle=True), etape(5, 40.0)]}]},
            {"de": 2, "a": 3, "detail": [{"etapes": [etape(1, 11.0), etape(2, 13.0), etape(3, 15.0)]}]},
            {"de": 4, "a": 5, "detail": [{"etapes": [etape(1, 1.0), etape(2, 3.0)]}]}]}))
        d = le_desaccord_reel(j)
        v("le désaccord réel ne compte que les pas voyants", d["n"] == 8, f"{d['n']} pas")
        v("... et le pas qui suit un aveugle est écarté avec lui", d["p90"] < 20.0, f"p90 {d['p90']}")
        v("... et le virage est publié par marche", d["virage_par_pas"]["n"] == 3)
    if COURSE.is_file():
        dr = le_desaccord_reel(COURSE)
        # ⚠ Un enonce DISTRIBUTIONNEL, pas un facteur choisi : la mediane reelle doit depasser ce
        # que la pile plane rend neuf fois sur dix, sinon la calibration n'aurait rien a faire.
        v("sur la vraie course, la médiane réelle dépasse le p90 de la pile plane",
          dr["mediane"] > plane_q["p90"], f"réel {dr['mediane']}° contre p90 plane {plane_q['p90']}°")

    # ⚠ Le juge distingue trois issues et le controle : il n'est pas une tautologie.
    reel_f = {"virage_par_pas": {"n": 10, "mediane": 14.0, "p25": 10.0, "p75": 20.0}}
    def pile_f(virage):
        return {"par_memoire": [{"memoire": 0.0, "virage_median_deg": virage}]}
    v("un virage dans la fourchette réelle est « comme le rouleau »",
      juger(reel_f, pile_f(14.0), {"virage_median_deg": 2.0})["la_pile_vire_comme_le_rouleau"])
    v("... au-dessous, « vire moins »", juger(reel_f, pile_f(3.0), {"virage_median_deg": 2.0})["la_pile_vire_moins"])
    v("... au-dessus, « vire plus »", juger(reel_f, pile_f(30.0), {"virage_median_deg": 2.0})["la_pile_vire_plus"])
    v("... et un contrôle qui vire autant que le rouleau est vu",
      not juger(reel_f, pile_f(14.0), {"virage_median_deg": 15.0})["le_controle_vire_moins"])

    # ⚠⚠ LES DEUX VARIANTES SONT DEUX MATIERES, ASSERTE SANS PREJUGER DU SENS : ma premiere version
    # exigeait que le marcheur vire DAVANTAGE par feuille, au nom d'un raisonnement sur le
    # marcheur ideal — et la mesure a rendu l'inverse a cette amplitude (9,2° contre 29,71°). Un
    # controle qui encode une conclusion attendue est un controle qui refuse la mesure ; celui-ci
    # ne demande que ce qui est sur : les deux piles ne rendent pas la meme marche.
    en_phase = le_marcheur_sur_la_pile(20.0, lds[1], graines=(3,), memoires=(0.0,), pas=12)
    par_feuille = le_marcheur_sur_la_pile(20.0, lds[1], graines=(3,), memoires=(0.0,), pas=12,
                                          par_feuille=True)
    v("à amplitude égale, les deux froissements ne rendent pas la même marche",
      par_feuille["par_memoire"][0]["virage_median_deg"] != en_phase["par_memoire"][0]["virage_median_deg"],
      f"par feuille {par_feuille['par_memoire'][0]['virage_median_deg']}° contre en phase "
      f"{en_phase['par_memoire'][0]['virage_median_deg']}°")
    v("... et la variante est écrite dans le résultat",
      par_feuille["par_feuille"] is True and en_phase["par_feuille"] is False)
    v("... et la calibration porte la variante",
      calibrer_lamplitude(lds[1], cible_deg=d1, cubes=6, iterations=2, par_feuille=True)["par_feuille"] is True)

    # ⭐ Une marche courte sur la pile froissée tourne et rend ses champs.
    m = le_marcheur_sur_la_pile(10.0, lds[1], graines=(3,), memoires=(0.0, 0.75), pas=6)
    v("le marcheur tourne sur la pile froissée aux deux mémoires", len(m["par_memoire"]) == 2
      and all(x["lots"] == 1 for x in m["par_memoire"]))
    v("... et la mémoire publie son gain et son coût",
      all(k in m["par_memoire"][1] for k in ("gain_en_virage_deg", "gain_en_erreur_deg", "cout_en_taux")))
    v("... et le désaccord rencontré est publié",
      m["par_memoire"][0]["desaccord_rencontre_median_deg"] is not None)
    v("... et la persistance du virage aussi, bornée à [-1, 1]",
      m["par_memoire"][0]["cos_virages_median"] is not None
      and -1.0 <= m["par_memoire"][0]["cos_virages_median"] <= 1.0)

    # ⚠ Le chemin qui produit le nombre publié est ATTEINT, en petit : une graine, six pas, six
    # cubes, une longueur d'onde. Une batterie qui teste les briques sans jamais assembler la
    # mesure ne peut pas échouer là où ça compte (`le_chemin_du_nombre_publie`).
    if COURSE.is_file():
        import contextlib, io  # noqa: PLC0415
        r = mesurer(graines=(3,), pas=6, cubes=6, longueurs=[lds[1]])
        v("la mesure assemblée rend une pile par variante",
          [x["variante"] for x in r["par_longueur_donde"]] == list(VARIANTES))
        v("... et un verdict par variante", set(r["par_variante"]) == set(VARIANTES))
        tampon = io.StringIO()
        with contextlib.redirect_stdout(tampon):
            afficher(r)
        v("... et l'affichage tourne dessus", "★★★ en_phase" in tampon.getvalue())

    print(f"\n{'ALL PASS' if echecs == 0 else 'ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--course", type=Path, default=COURSE)
    p.add_argument("--pas", type=int, default=PAS)
    p.add_argument("--cubes", type=int, default=CUBES_DE_CALIBRATION)
    p.add_argument("--json", type=Path, default=None)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(a.course, pas=a.pas, cubes=a.cubes)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False))
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
