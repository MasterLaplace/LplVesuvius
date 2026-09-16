"""Le vrillage paie-t-il le coin qui manque ? — ce que `169` a laissé ouvert.

⭐⭐⭐⭐ POURQUOI CE FICHIER. `169` mesure que les deux causes du depot tirent en SENS OPPOSES :
l'ECRASEMENT penche azimutalement et suit parfaitement, le FROISSEMENT penche axialement et ne suit
pas. Le vrai rouleau demande un penchant AXIAL ET SUIVI, et aucun melange des deux ne le donne. Le
VRILLAGE — un enroulement de travers, ou la feuille derive le long de l'axe en s'enroulant — donne
ce coin-la : sa normale sort du plan du tour d'une quantite CONSTANTE au lieu d'osciller.

⚠⚠ MAIS UNE CAUSE QUI DONNE UNE GRANDEUR EN DEPLACE D'AUTRES, et c'est toute la question. `R4-F87`
calibre la fixture sur TROIS grandeurs du rouleau — le rapport chemin sur etendue, le penchant, la
coherence. Un vrillage assez grand pour renverser la direction peut casser ce que cette calibration
a construit. La tranche ne demande donc pas « peut-on le fabriquer » — on peut — mais « est-ce que
ca coute plus que ca ne rapporte ».

⚠⚠⚠ LA METHODE EST CELLE DE `134` : on calibre sur une grandeur SANS REGARDER celle qu'on demande.
Le vrillage est pose par bissection sur la PART AXIALE du rouleau, puis seulement on lit ce que les
trois autres sont devenues.

⚠⚠ ET LA DISTANCE EST LA PIRE DES TROIS ECARTS, JAMAIS LEUR MOYENNE — la forme de `R4-F87`. Une
moyenne pardonnerait a une matiere qui reproduit deux grandeurs et rate la troisieme.

⚠ UN SEUL INSTRUMENT DES DEUX COTES. Le rapport, le penchant et la coherence sont relus ici par
`penchant()`, celui de `R4-F79`, sur la matiere avec et sans vrillage. Les comparer aux nombres que
`R4-F87` publie melangerait deux instruments ; ce qui est compare ici est la distance au ROULEAU,
mesuree deux fois par le meme appareil.

Usage :
    uv run python src/nappe/le_vrillage_paie_t_il_le_coin_qui_manque.py --verifier
    uv run python src/nappe/le_vrillage_paie_t_il_le_coin_qui_manque.py \\
        --json docs/mesures/le_vrillage_paie_t_il_le_coin_qui_manque.json
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))

from la_pince_tient_elle_la_feuille import (LONGUEUR_DONDE_UM, _PAS,  # noqa: E402
                                            _VOXEL)
from le_chemin_penche_t_il_ou_serpente_t_il import (_barres,  # noqa: E402
                                                    _marcher_et_pencher)

LA_COURSE_DU_ROULEAU = RACINE / "docs" / "mesures" / "le_chemin_penche_t_il_ou_serpente_t_il.json"
LA_CALIBRATION = RACINE / "docs" / "mesures" / "lecrasement_explique_t_il_lobliquite.json"
RAYON_MM = 10.0
DEPARTS = 10
CAP = 0.75
PAS_MAX = 40
CENTRE_YX_VX = (6000.0, 6000.0)
FORME = (4000, 16000, 16000)
# La matiere que `R4-F87` calibre, et sur laquelle la chaine `161`-`168` tourne.
ECRASEMENT, AMPLITUDE_UM = 0.2782, 100.0
# ⚠ L'echelle balayee est LARGE et ses bornes sont dites : en dessous de 0,05 le froissement, treize
# fois plus grand, couvre tout ; au-dela de 1,0 la feuille derive d'un pas par pas et cesse d'etre
# un enroulement reconnaissable.
ECHELLE = (0.0, 0.05, 0.15, 0.3, 0.45, 0.6, 0.8, 1.0)


def ce_que_le_rouleau_a_rendu(course: Path = LA_COURSE_DU_ROULEAU,
                              calibration: Path = LA_CALIBRATION) -> dict | None:
    """Les quatre grandeurs du VRAI rouleau, relues et jamais recalculees.

    ⚠⚠ Elles viennent de DEUX mesures stockees : la course de `R4-F79` porte les parts axiale et
    azimutale AVEC CAP, la calibration de `R4-F87` porte le rapport, le penchant et la coherence.
    Les recalculer ici en ferait une seconde reponse a une question deja tranchee.
    """
    if not course.is_file() or not calibration.is_file():
        return None
    c = json.loads(course.read_text(encoding="utf-8"))
    k = json.loads(calibration.read_text(encoding="utf-8"))
    avec = next((x for x in (c.get("par_course") or [])
                 if float(x.get("memoire_du_cap", -1.0)) == CAP), None)
    if avec is None:
        return None
    f = avec.get("la_forme_du_penchant") or {}
    j = k.get("juger") or {}
    besoin = {"axial": f.get("axial_absolu_median"), "azimutal": f.get("azimutal_absolu_median"),
              "glissement_axial_um": f.get("glissement_axial_median_um"),
              "rapport": j.get("rapport_du_rouleau"),
              "penchant_deg": j.get("penchant_du_rouleau_deg"),
              "coherence": j.get("coherence_du_rouleau")}
    if any(v is None for v in besoin.values()):
        return None
    return {"sources": [course.name, calibration.name], "memoire_du_cap": CAP,
            **{cle: float(v) for cle, v in besoin.items()}}


def _matiere_vrillee(vrillage: float, rayon_mm: float = RAYON_MM):
    from combien_de_pas_la_matiere_porte import (  # noqa: PLC0415
        VolumeFabriqueEnSpiraleVrillee)

    return VolumeFabriqueEnSpiraleVrillee(
        _PAS(), vrillage=float(vrillage), r0_um=rayon_mm * 1000.0 - 0.25 * _PAS(),
        centre_yx_vx=CENTRE_YX_VX, forme=FORME, ecrasement=ECRASEMENT,
        amplitude_um=AMPLITUDE_UM, longueur_donde_um=LONGUEUR_DONDE_UM)


def _un_depart(vol, k: int, departs: int, rayon_mm: float):
    """Le depart numero `k`, ASSIS sur une feuille et oriente le long de la normale.

    ⚠⚠⚠ L'ASSISE EST UNE RECHERCHE DE RACINE BORNEE, et `169` a paye ce qu'un simple decalage
    coute : sur une section ECRASEE la phase n'est pas lineaire le long du rayon, et un depart
    tombe entre deux feuilles fait mesurer a l'instrument sa propre erreur de mise en place.
    """
    a = 2.0 * np.pi * k / int(departs)
    radial = np.array([0.0, np.sin(a), np.cos(a)])
    r_vx = rayon_mm * 1000.0 / _VOXEL()
    p0 = np.array([2000.0, CENTRE_YX_VX[0] + r_vx * np.sin(a),
                   CENTRE_YX_VX[1] + r_vx * np.cos(a)])
    depart = p0.copy()
    cible = round(float(vol.phase(p0.reshape(1, 3))[0]))
    for _ in range(24):
        ph = float(vol.phase(depart.reshape(1, 3))[0])
        if abs(ph - cible) < _VOXEL() / _PAS():
            break
        depart = depart + radial * ((cible - ph) * vol.pas_um / _VOXEL())
    n0 = np.asarray(vol.normale_locale(depart)).reshape(3)
    axe = np.array([depart[0], CENTRE_YX_VX[0], CENTRE_YX_VX[1]])
    ph2 = float(vol.phase(depart.reshape(1, 3))[0])
    return depart, n0, axe, round(abs(ph2 - round(ph2)), 6)


def les_quatre_grandeurs(vrillage: float, barres, departs: int = DEPARTS,
                         rayon_mm: float = RAYON_MM, pas_max: int = PAS_MAX) -> dict:
    """Ce qu'une matiere vrillee rend, sur les quatre grandeurs qui comptent.

    ⚠ Le RAPPORT est le chemin parcouru divise par l'etendue radiale traversee — la grandeur que
    `136` mesure a 1,186 sur le rouleau, et qu'aucune cause seule n'expliquait.
    """
    vol = _matiere_vrillee(vrillage, rayon_mm)
    axs, azs, cohs, gls, angs, raps, assises = [], [], [], [], [], [], []
    for k in range(int(departs)):
        depart, n0, axe, assise = _un_depart(vol, k, departs, rayon_mm)
        assises.append(assise)
        p = _marcher_et_pencher(vol, depart, n0, axe, barres, pas_max, CAP)
        if not p.get("decidable"):
            continue
        etendue = float(p.get("etendue_cylindrique_um") or 0.0)
        if etendue <= 0.0:
            continue
        axs.append(float(p["axial_absolu_median"]))
        azs.append(float(p["azimutal_absolu_median"]))
        cohs.append(float(p["coherence_tangentielle"]))
        gls.append(float(p["glissement_axial_median_um"]))
        angs.append(float(p["angle_median_deg"]))
        raps.append(float(p["chemin_um"]) / etendue)
    if not axs:
        return {"vrillage": float(vrillage), "decidable": False,
                "raison": "aucune marche décidable", "departs": int(departs)}
    def med(xs, n=3):
        return round(float(statistics.median(xs)), n)
    return {"vrillage": float(vrillage), "decidable": True, "departs": int(departs),
            "decidables": len(axs), "axial": med(axs), "azimutal": med(azs),
            "coherence": med(cohs), "glissement_axial_um": med(gls, 1),
            "penchant_deg": med(angs, 2), "rapport": med(raps, 4),
            # ⚠⚠ UN COMPTE, pas une moyenne : combien de marches penchent reellement axialement.
            "marches_axiales": int(sum(1 for a, z in zip(axs, azs) if a > z)),
            "pire_assise_en_feuilles": round(max(assises), 6) if assises else None}


def distance_au_rouleau(m: dict, rouleau: dict) -> dict | None:
    """La PIRE des trois écarts relatifs au rouleau, jamais leur moyenne.

    ⚠⚠ C'est la forme de `R4-F87`, et elle existe pour une raison : une moyenne pardonnerait à une
    matière qui reproduit deux grandeurs et rate la troisième. La distance publiée est donc celle
    de la grandeur la plus mal reproduite, et son NOM est publié avec elle.
    """
    if not m.get("decidable"):
        return None
    ecarts = {}
    for cle in ("rapport", "penchant_deg", "coherence"):
        cible = float(rouleau[cle])
        ecarts[cle] = round(abs(float(m[cle]) - cible) / abs(cible), 4)
    pire = max(ecarts, key=lambda k: ecarts[k])
    return {"par_grandeur": ecarts, "la_pire": pire, "distance": ecarts[pire]}


def _bracket(echelle: list[dict], cible: float) -> tuple[float, float] | None:
    """Les deux barreaux de l'échelle qui ENCADRENT la cible, lus et non supposés.

    ⚠⚠⚠ LA PART AXIALE N'EST PAS MONOTONE EN LE VRILLAGE, et c'est mesuré : tant que le
    froissement domine — il vaut treize fois un vrillage de cinq centièmes — elle monte et descend.
    Une bissection posée sur un intervalle supposé monotone rendrait donc un nombre sans le dire.
    Le bracket est LU sur l'échelle balayée, et s'il n'existe pas, la tranche le DIT.
    """
    dec = [x for x in echelle if x.get("decidable")]
    for a, b in zip(dec, dec[1:]):
        if (a["axial"] - cible) * (b["axial"] - cible) <= 0.0:
            return float(a["vrillage"]), float(b["vrillage"])
    return None


def poser_le_vrillage(echelle: list[dict], cible: float, barres, tours: int = 8,
                      departs: int = DEPARTS) -> dict:
    """Le vrillage qui donne au fixture la part axiale du ROULEAU, par bissection.

    ⚠⚠ ON CALIBRE SUR UNE GRANDEUR SANS REGARDER CELLE QU'ON DEMANDE — la méthode de `134`. Ce qui
    est posé ici est la part AXIALE ; ce qu'on lira ensuite est la cohérence, le rapport et le
    penchant, dont rien n'a été fait pour qu'ils tombent juste.
    """
    br = _bracket(echelle, cible)
    if br is None:
        return {"decidable": False,
                "raison": f"la part axiale du rouleau ({cible}) n'est pas encadrée par l'échelle"}
    lo, hi = br
    # ⚠ Le signe de la borne BASSE est mesure UNE fois : le remesurer a chaque tour paierait huit
    # grilles pour une information qui ne change pas, et une bissection qui coute huit fois son
    # prix finit par ne pas etre lancee.
    m_lo = next((x for x in echelle if float(x["vrillage"]) == lo), None)
    if m_lo is None or not m_lo.get("decidable"):
        return {"decidable": False, "raison": f"la borne basse {lo} n'est pas mesurée"}
    signe_lo = 1.0 if (m_lo["axial"] - cible) > 0.0 else -1.0
    for _ in range(int(tours)):
        mid = 0.5 * (lo + hi)
        m = les_quatre_grandeurs(mid, barres, departs=departs)
        if not m.get("decidable"):
            return {"decidable": False, "raison": f"indécidable à vrillage {mid}"}
        if (m["axial"] - cible) * signe_lo <= 0.0:
            hi = mid
        else:
            lo = mid
    pose = 0.5 * (lo + hi)
    return {"decidable": True, "vrillage": round(pose, 5), "bracket": [lo, hi],
            "cible_axiale": float(cible), "tours": int(tours),
            **{f"pose_{k}": v for k, v in les_quatre_grandeurs(pose, barres,
                                                               departs=departs).items()}}


def lenquete(echelle=ECHELLE, departs: int = DEPARTS, rouleau: dict | None = None) -> dict:
    barres = _barres()
    balayage = [les_quatre_grandeurs(v, barres, departs=departs) for v in echelle]
    # ⚠⚠ LE CONTROLE VIDE : sur la spirale NUE, sans ecrasement ni froissement ni vrillage, il n'y a
    # pas de penchant du tout. Une part axiale non nulle y mesurerait le MARCHEUR.
    from combien_de_pas_la_matiere_porte import (  # noqa: PLC0415
        VolumeFabriqueEnSpiraleVrillee)
    nue = VolumeFabriqueEnSpiraleVrillee(
        _PAS(), vrillage=0.0, r0_um=RAYON_MM * 1000.0 - 0.25 * _PAS(),
        centre_yx_vx=CENTRE_YX_VX, forme=FORME, ecrasement=0.0, amplitude_um=0.0,
        longueur_donde_um=LONGUEUR_DONDE_UM)
    gl_nue, ax_nue = [], []
    for k in range(int(departs)):
        depart, n0, axe, _a = _un_depart(nue, k, departs, RAYON_MM)
        p = _marcher_et_pencher(nue, depart, n0, axe, barres, PAS_MAX, CAP)
        if p.get("decidable"):
            gl_nue.append(float(p["glissement_axial_median_um"]))
            ax_nue.append(float(p["axial_absolu_median"]))
    controle = {"nom": "spirale nue", "decidables": len(gl_nue),
                "glissement_axial_median_um": (round(float(statistics.median(gl_nue)), 1)
                                               if gl_nue else None),
                "axial_median": (round(float(statistics.median(ax_nue)), 3) if ax_nue else None)}
    controle["il_ne_penche_pas"] = bool(
        gl_nue and controle["glissement_axial_median_um"] == 0.0
        and controle["axial_median"] == 0.0)
    pose = (poser_le_vrillage(balayage, float(rouleau["axial"]), barres, departs=departs)
            if rouleau else {"decidable": False, "raison": "le rouleau est absent"})
    return {"decidable": bool(balayage), "echelle": [float(v) for v in echelle],
            "balayage": balayage, "le_controle_de_la_spirale_nue": controle,
            "la_pose": pose, "departs": int(departs), "rayon_mm": RAYON_MM,
            "memoire_du_cap": CAP, "pas_max": PAS_MAX,
            "matiere": {"ecrasement": ECRASEMENT, "amplitude_um": AMPLITUDE_UM}}


def juger(d: dict, rouleau: dict | None) -> dict:
    if not d.get("decidable"):
        return {"decidable": False, "raison": "aucune matière mesurée"}
    # ⚠⚠⚠ SANS LE ROULEAU IL N'Y A PAS DE COMPARAISON, et conclure sur la seule fixture serait une
    # affirmation sur une matiere deguisee en comparaison entre deux.
    if rouleau is None:
        return {"decidable": False, "raison": "les mesures du rouleau sont absentes"}
    sans = next((x for x in d["balayage"] if float(x["vrillage"]) == 0.0), None)
    pose = d.get("la_pose") or {}
    avec = ({k[5:]: v for k, v in pose.items() if k.startswith("pose_")}
            if pose.get("decidable") else None)
    d_sans = distance_au_rouleau(sans, rouleau) if sans else None
    d_avec = distance_au_rouleau(avec, rouleau) if avec else None
    # ⭐⭐⭐⭐ LE VERDICT EST JOINT, ET IL A DEUX MOITIES QUI ECHOUENT DIFFEREMMENT : le vrillage doit
    # RENVERSER le sens — la fixture doit penser axialement comme le rouleau — ET ne pas ELOIGNER
    # la matiere des trois grandeurs que `R4-F87` calibre. Une cause qui donne le sens en cassant
    # le reste n'est pas une explication, c'est un parametre de plus.
    gagne_le_cote = bool(avec and avec["axial"] > avec["azimutal"])
    perd_le_cote = bool(sans and sans["axial"] > sans["azimutal"])
    pas_plus_loin = bool(d_sans and d_avec and d_avec["distance"] <= d_sans["distance"])
    return {"decidable": True, "le_rouleau": rouleau,
            "sans_vrillage": sans, "avec_vrillage": avec,
            "distance_sans_vrillage": d_sans, "distance_avec_vrillage": d_avec,
            "le_controle_de_la_spirale_nue": d["le_controle_de_la_spirale_nue"],
            "la_pose": pose,
            "il_donne_le_cote": bool(gagne_le_cote and not perd_le_cote),
            "il_neloigne_pas_des_trois": pas_plus_loin,
            "il_paie_ce_quil_donne": bool(gagne_le_cote and not perd_le_cote and pas_plus_loin)}


def mesurer(echelle=ECHELLE, departs: int = DEPARTS, course: Path = LA_COURSE_DU_ROULEAU,
            calibration: Path = LA_CALIBRATION) -> dict:
    r = ce_que_le_rouleau_a_rendu(course, calibration)
    d = lenquete(echelle, departs, r)
    return {"enquete": d, "juger": juger(d, r)}


def reagreger(r: dict, course: Path = LA_COURSE_DU_ROULEAU,
              calibration: Path = LA_CALIBRATION) -> dict:
    r["juger"] = juger(r["enquete"], ce_que_le_rouleau_a_rendu(course, calibration))
    return r


def afficher(r: dict) -> None:
    if "message" in r:
        print(f"⚠ {r['message']}")
        return
    j, d = r["juger"], r["enquete"]
    if not j.get("decidable"):
        print(f"⚠ {j.get('raison', 'indécidable')}")
        return
    c = j["le_controle_de_la_spirale_nue"]
    marque = "★" if c["il_ne_penche_pas"] else "✗"
    print(f"{marque} contrôle — la spirale NUE ne penche pas : part axiale {c['axial_median']}, "
          f"glissement {c['glissement_axial_median_um']} µm sur {c['decidables']} marches")
    ro = j["le_rouleau"]
    print(f"\n   le rouleau, avec cap : axial {ro['axial']} · azimutal {ro['azimutal']} · "
          f"rapport {ro['rapport']} · penchant {ro['penchant_deg']}° · cohérence {ro['coherence']}")
    print(f"\n   — le balayage du vrillage —  (matière écrasée {d['matiere']['ecrasement']}, "
          f"froissée {d['matiere']['amplitude_um']} µm)")
    print(f"   {'vrillage':>9} | {'axial':>6} | {'azimut':>7} | {'penche':>13} | {'cohér.':>7} | "
          f"{'rapport':>8} | {'penchant':>9} | {'ax/az':>6}")
    for m in d["balayage"]:
        if not m.get("decidable"):
            print(f"   {m['vrillage']:>9} | {'(indécidable)':>30}")
            continue
        print(f"   {m['vrillage']:>9} | {m['axial']:>6.3f} | {m['azimutal']:>7.3f} | "
              f"{'AXIALEMENT' if m['axial'] > m['azimutal'] else 'azimutalement':>13} | "
              f"{m['coherence']:>7.3f} | {m['rapport']:>8.4f} | {m['penchant_deg']:>8.2f}° | "
              f"{m['marches_axiales']:>3}/{m['decidables']}")
    p = j["la_pose"]
    print(f"\n   — la pose —")
    if not p.get("decidable"):
        print(f"      ✗ {p.get('raison')}")
    else:
        print(f"      vrillage {p['vrillage']} posé par bissection sur la part axiale "
              f"{p['cible_axiale']}, bracket {p['bracket']}")
    for nom, m, dd in (("sans vrillage", j["sans_vrillage"], j["distance_sans_vrillage"]),
                       ("avec vrillage", j["avec_vrillage"], j["distance_avec_vrillage"])):
        if not m or not dd:
            continue
        print(f"      {nom:>14} : rapport {m['rapport']} · penchant {m['penchant_deg']}° · "
              f"cohérence {m['coherence']} — pire écart {dd['distance']} sur « {dd['la_pire']} »")
    print("\n★★★★ le vrillage paie-t-il ce qu'il donne ?")
    print(f"      il donne le CÔTÉ            : {'OUI' if j['il_donne_le_cote'] else 'non'}")
    print(f"      il n'éloigne pas des TROIS  : "
          f"{'OUI' if j['il_neloigne_pas_des_trois'] else 'non'}")
    print(f"      donc il PAIE                : {'OUI' if j['il_paie_ce_quil_donne'] else 'non'}")


def _m(vrillage, axial, azimutal, rapport, penchant, coherence, dec=True, n=4) -> dict:
    return {"vrillage": float(vrillage), "decidable": bool(dec), "departs": n, "decidables": n,
            "axial": axial, "azimutal": azimutal, "coherence": coherence,
            "glissement_axial_um": 30.0, "penchant_deg": penchant, "rapport": rapport,
            "marches_axiales": int(n if axial > azimutal else 0),
            "pire_assise_en_feuilles": 0.001}


def verifier() -> int:
    import contextlib  # noqa: PLC0415
    import io  # noqa: PLC0415

    echecs = controles = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    ro = {"axial": 0.334, "azimutal": 0.193, "glissement_axial_um": 43.2,
          "rapport": 1.186, "penchant_deg": 25.48, "coherence": 0.925, "memoire_du_cap": 0.75}

    print("— la distance est la PIRE des trois —")
    proche = distance_au_rouleau(_m(0.0, 0.2, 0.3, 1.18, 25.4, 0.92), ro)
    v("⭐⭐⭐ elle nomme la grandeur la plus mal reproduite",
      proche["la_pire"] in proche["par_grandeur"]
      and proche["distance"] == max(proche["par_grandeur"].values()))
    # ⚠⚠ DEUX GRANDEURS PARFAITES ET UNE RATEE NE FONT PAS UNE MOYENNE ACCEPTABLE.
    bancal = distance_au_rouleau(_m(0.0, 0.2, 0.3, 1.186, 25.48, 0.40), ro)
    moyenne = sum(bancal["par_grandeur"].values()) / 3.0
    v("⭐⭐⭐⭐ deux grandeurs justes et une ratée donnent une GRANDE distance, pas une moyenne",
      bancal["distance"] > 0.5 and bancal["distance"] > moyenne * 2.0,
      f"pire {bancal['distance']} sur « {bancal['la_pire']} », moyenne {moyenne:.4f}")
    v("⚠ une mesure indécidable n'a pas de distance",
      distance_au_rouleau({"decidable": False}, ro) is None)

    print("\n— le bracket est LU sur l'échelle, jamais supposé —")
    monte = [_m(0.0, 0.20, 0.30, 1.1, 24.0, 0.94), _m(0.5, 0.30, 0.28, 1.1, 24.0, 0.96),
             _m(1.0, 0.50, 0.26, 1.1, 24.0, 0.98)]
    v("⭐⭐⭐⭐ il trouve les deux barreaux qui ENCADRENT la cible",
      _bracket(monte, 0.334) == (0.5, 1.0), str(_bracket(monte, 0.334)))
    # ⚠⚠⚠ LA PART AXIALE N'EST PAS MONOTONE TANT QUE LE FROISSEMENT DOMINE : un bracket suppose
    # rendrait un nombre sans le dire.
    creux = [_m(0.0, 0.20, 0.30, 1.1, 24.0, 0.94), _m(0.1, 0.15, 0.29, 1.1, 24.0, 0.94),
             _m(0.2, 0.18, 0.29, 1.1, 24.0, 0.95)]
    v("⭐⭐⭐⭐ ... et il REFUSE quand la cible n'est encadrée par aucun couple",
      _bracket(creux, 0.334) is None,
      "la part axiale n'est pas monotone tant que le froissement domine")
    v("⚠ une échelle indécidable ne fabrique pas de bracket",
      _bracket([_m(0.0, 0, 0, 0, 0, 0, dec=False)], 0.334) is None)

    print("\n— le verdict a DEUX moitiés qui échouent différemment —")
    sans = _m(0.0, 0.20, 0.30, 1.10, 24.0, 0.94)
    d_ = {"decidable": True, "echelle": [0.0], "balayage": [sans],
          "le_controle_de_la_spirale_nue": {"nom": "spirale nue", "decidables": 2,
                                            "glissement_axial_median_um": 0.0,
                                            "axial_median": 0.0, "il_ne_penche_pas": True},
          "la_pose": {"decidable": True, "vrillage": 0.5, "bracket": [0.3, 0.6],
                      "cible_axiale": 0.334, "tours": 8,
                      **{f"pose_{k}": v_ for k, v_
                         in _m(0.5, 0.34, 0.20, 1.12, 25.0, 0.93).items()}},
          "departs": 4, "rayon_mm": 10.0, "memoire_du_cap": 0.75, "pas_max": 40,
          "matiere": {"ecrasement": 0.2782, "amplitude_um": 100.0}}
    j = juger(d_, ro)
    v("⭐⭐⭐⭐ il paie quand il donne le côté ET n'éloigne pas des trois",
      j["il_donne_le_cote"] is True and j["il_neloigne_pas_des_trois"] is True
      and j["il_paie_ce_quil_donne"] is True)
    loin = json.loads(json.dumps(d_))
    loin["la_pose"]["pose_coherence"] = 0.30
    v("⭐⭐⭐⭐ ... et il cesse de payer s'il ÉLOIGNE des trois, même en donnant le côté",
      juger(loin, ro)["il_donne_le_cote"] is True
      and juger(loin, ro)["il_paie_ce_quil_donne"] is False,
      "une cause qui donne le sens en cassant le reste est un paramètre de plus")
    rien = json.loads(json.dumps(d_))
    rien["la_pose"]["pose_axial"], rien["la_pose"]["pose_azimutal"] = 0.15, 0.35
    v("⭐⭐⭐⭐ ... et il ne paie pas s'il ne donne PAS le côté",
      juger(rien, ro)["il_donne_le_cote"] is False
      and juger(rien, ro)["il_paie_ce_quil_donne"] is False)
    # ⚠⚠ ET IL NE GAGNE RIEN SI LA MATIERE PENCHAIT DEJA AXIALEMENT SANS LUI.
    deja = json.loads(json.dumps(d_))
    deja["balayage"][0]["axial"], deja["balayage"][0]["azimutal"] = 0.40, 0.20
    v("⭐⭐⭐ ... et il ne gagne rien si la matière penchait DÉJÀ axialement sans lui",
      juger(deja, ro)["il_donne_le_cote"] is False,
      "sinon il serait crédité de ce que la matière faisait toute seule")
    v("⚠⚠⚠ sans les mesures du rouleau, le jugement REFUSE de conclure",
      juger(d_, None)["decidable"] is False)

    print("\n— sur données réelles —")
    barres = _barres()
    vraie = ce_que_le_rouleau_a_rendu()
    v("⚠⚠ les quatre grandeurs du rouleau sont RELUES, jamais recalculées",
      vraie is not None and vraie["axial"] == 0.334 and vraie["rapport"] == 1.186
      and vraie["coherence"] == 0.925, str(vraie))
    m0 = les_quatre_grandeurs(0.0, barres, departs=2, pas_max=12)
    v("⭐⭐⭐⭐ à vrillage nul la matière calibrée marche réellement",
      m0["decidable"] and m0["decidables"] > 0 and m0["rapport"] > 1.0,
      f"{m0['decidables']} marches, rapport {m0['rapport']}, axial {m0['axial']} contre "
      f"{m0['azimutal']}")
    # ⚠⚠⚠ L'ASSISE EST VERIFIEE SUR DONNEES REELLES, et sa borne est DERIVEE du voxel : `169` a
    # publie deux verdicts faux faute de ce controle.
    v("⭐⭐⭐⭐ ... et le marcheur y part SUR une feuille",
      m0["pire_assise_en_feuilles"] < _VOXEL() / _PAS(),
      f"{m0['pire_assise_en_feuilles']} contre {round(_VOXEL() / _PAS(), 6)} qu'un voxel exprime")
    m1 = les_quatre_grandeurs(1.0, barres, departs=2, pas_max=12)
    v("⭐⭐⭐⭐ ... et un vrillage franc DÉPLACE réellement la part axiale",
      m1["decidable"] and m1["axial"] > m0["axial"],
      f"{m0['axial']} sans vrillage contre {m1['axial']} à un vrillage de 1,0")
    tampon = io.StringIO()
    with contextlib.redirect_stdout(tampon):
        afficher({"juger": j, "enquete": d_})
    sortie = tampon.getvalue()
    v("⚠ `afficher` rend le contrôle, le balayage, la pose et les deux moitiés du verdict",
      "contrôle" in sortie and "balayage" in sortie and "la pose" in sortie
      and "il donne le CÔTÉ" in sortie, f"{len(sortie)} caractères")
    tampon = io.StringIO()
    with contextlib.redirect_stdout(tampon):
        afficher({"message": "rien à montrer"})
    v("⚠ un message est dit, jamais dessiné", "⚠" in tampon.getvalue())

    print(f"\n{'ALL PASS' if echecs == 0 else '⛔ ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--json", type=Path, default=None)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--reagreger", type=Path, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = (reagreger(json.loads(a.reagreger.read_text())) if a.reagreger is not None
         else mesurer())
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
