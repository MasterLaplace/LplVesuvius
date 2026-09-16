"""La fixture penche-t-elle du même côté que le rouleau ? — ce que `R4-F87` n'a pas calibré.

⭐⭐⭐⭐ POURQUOI CE FICHIER, ET IL BORNE HUIT TRANCHES. `R4-F87` établit que la fixture approche le
rouleau à **5,5 %** sur trois grandeurs : le **rapport** des axes, le **penchant** et la
**cohérence**. La direction de ce penchant n'en fait pas partie. Or `R4-F79` mesure sur le VRAI
rouleau que le penchant est plus **axial** qu'azimutal — **0,334** contre **0,193** — et que le
marcheur glisse de **43,2 µm** le long de la longueur du rouleau à chaque pas. Toute la chaîne
`161`–`168` tourne sur la fixture ; si celle-ci penchait dans l'autre sens, ces huit tranches
mesureraient une matière qui n'a pas le défaut du rouleau.

⚠⚠ LE MÊME INSTRUMENT ET LE MÊME MARCHEUR, DEUX MATIÈRES. La décomposition est `penchant()`, celle
qui a produit `R4-F79`, et le marcheur est `marcher`, celui de `100` — jamais `suivre`. Employer un
autre marcheur comparerait deux instruments en croyant comparer deux matières.

⚠⚠⚠ LES CHIFFRES DU VRAI ROULEAU SONT LUS, JAMAIS RECALCULÉS. Ils sont publiés (`R4-F79`) et leur
course coûte des heures ; ce module les relit dans la mesure stockée et REFUSE de conclure si elle
est absente. Les recalculer ici en ferait une seconde réponse à une question déjà tranchée.

⚠⚠ DEUX QUESTIONS, DEUX ÉNONCÉS EXACTS, ET AUCUN SEUIL :
  • **le côté** — la part axiale dépasse-t-elle la part azimutale ? C'est le mot pour mot de
    `R4-F79`, et il se compte sur les cases, jamais sur une moyenne ;
  • **le suivi** — la cohérence, c'est-à-dire le déplacement tangentiel NET divisé par le chemin
    tangentiel PARCOURU. Un chemin qui penche toujours du même côté rend un ; un chemin qui oblique
    alternativement rend zéro. Deux matières de même penchant peuvent rendre l'une et l'autre.

⚠ CONTRÔLE OBLIGATOIRE ET VIDE : sur la spirale nue il n'y a PAS de penchant — la normale y est
presque le rayon — donc la comparaison des deux parts n'y veut rien dire. La dire, jamais rendre un
verdict.

Usage :
    uv run python src/nappe/la_fixture_penche_t_elle_du_meme_cote.py --verifier
    uv run python src/nappe/la_fixture_penche_t_elle_du_meme_cote.py \\
        --json docs/mesures/la_fixture_penche_t_elle_du_meme_cote.json
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

from la_pince_tient_elle_la_feuille import LONGUEUR_DONDE_UM, MATIERES, _nom  # noqa: E402
from le_chemin_penche_t_il_ou_serpente_t_il import (_barres,  # noqa: E402
                                                    _marcher_et_pencher)

LA_COURSE_DU_ROULEAU = RACINE / "docs" / "mesures" / "le_chemin_penche_t_il_ou_serpente_t_il.json"
RAYONS_MM = (6.0, 10.0, 14.0)
CAPS = (0.0, 0.75)
PAS_MAX = 40
CENTRE_YX_VX = (6000.0, 6000.0)
FORME = (4000, 16000, 16000)
LA_SPIRALE_NUE = (0.0, 0.0)


def ce_que_le_rouleau_a_rendu(chemin: Path = LA_COURSE_DU_ROULEAU) -> dict | None:
    """Les quatre grandeurs du VRAI rouleau, relues et jamais recalculées.

    ⚠⚠ Rend `None` si la mesure est absente, et l'appelant doit alors REFUSER de conclure : une
    comparaison dont un côté manque n'est pas une comparaison à moitié faite, c'est une affirmation
    sur une seule matière déguisée en comparaison.
    """
    if not chemin.is_file():
        return None
    d = json.loads(chemin.read_text(encoding="utf-8"))
    courses = d.get("par_course") or []
    if not courses:
        return None
    f = (courses[0] or {}).get("la_forme_du_penchant") or {}
    besoin = ("axial_absolu_median", "azimutal_absolu_median",
              "glissement_axial_median_um", "coherence_mediane")
    if any(f.get(k) is None for k in besoin):
        return None
    return {"source": chemin.name, "nom": str(courses[0].get("nom", "le rouleau")),
            **{k: float(f[k]) for k in besoin}}


def le_cote_dune_marche(p: dict) -> dict | None:
    """Une marche, et de quel côté elle penche — sans moyenner quoi que ce soit."""
    if not p.get("decidable"):
        return None
    a = p.get("axial_absolu_median")
    z = p.get("azimutal_absolu_median")
    if a is None or z is None:
        return None
    return {"pas": int(p["pas"]), "axial": float(a), "azimutal": float(z),
            "glissement_axial_um": float(p.get("glissement_axial_median_um") or 0.0),
            "coherence": float(p.get("coherence_tangentielle") or 0.0),
            # ⚠⚠ UN ECART EXACTEMENT NUL N'EST NI L'UN NI L'AUTRE : l'enonce du depot depuis `161`.
            "penche_axialement": bool(a > z), "penche_azimutalement": bool(a < z),
            "les_deux_parts_sont_egales": bool(a == z)}


def _resume(cas: list[dict | None]) -> dict:
    dec = [c for c in cas if c is not None]
    if not dec:
        return {"decidable": False, "raison": "aucune marche décidable", "marches": len(cas)}
    return {"decidable": True, "marches": len(cas), "decidables": len(dec),
            "penchent_axialement": int(sum(1 for c in dec if c["penche_axialement"])),
            "penchent_azimutalement": int(sum(1 for c in dec if c["penche_azimutalement"])),
            "parts_egales": int(sum(1 for c in dec if c["les_deux_parts_sont_egales"])),
            **{f"{k}_median": round(float(statistics.median([c[k] for c in dec])), 3)
               for k in ("axial", "azimutal", "coherence")},
            "glissement_axial_median_um": round(
                float(statistics.median([c["glissement_axial_um"] for c in dec])), 1)}


def lenquete(matieres=MATIERES, rayons_mm=RAYONS_MM, caps=CAPS,
             pas_max: int = PAS_MAX) -> dict:
    from combien_de_pas_la_matiere_porte import (  # noqa: PLC0415
        VolumeFabriqueEnSpiraleFroissee)

    barres = _barres()
    C = barres[-1]
    cases = []
    for ecr, amp in matieres:
        for r_mm in rayons_mm:
            # ⚠ Le depart est recale sur une phase ENTIERE : sur l'axe +y l'angle vaut pi/2, donc
            # la phase y vaut -1/4 et le rayon de reference est decale d'un quart de pas. Une
            # cellule qui tombe entre deux feuilles ne correspond a aucune polarite du gabarit, et
            # l'instrument mesurerait alors sa propre erreur de mise en place.
            vol = VolumeFabriqueEnSpiraleFroissee(
                C.PAS_UM, r0_um=r_mm * 1000.0 - 0.25 * C.PAS_UM, centre_yx_vx=CENTRE_YX_VX,
                forme=FORME, ecrasement=float(ecr), amplitude_um=float(amp),
                longueur_donde_um=LONGUEUR_DONDE_UM)
            r_vx = r_mm * 1000.0 / C.VOXEL_FIN_UM
            depart = np.array([2000.0, CENTRE_YX_VX[0] + r_vx, CENTRE_YX_VX[1]])
            radial = np.array([0.0, 1.0, 0.0])
            axe = depart - radial * r_vx
            for cap in caps:
                p = _marcher_et_pencher(vol, depart, radial, axe, barres, pas_max, float(cap))
                cases.append({"nom": _nom(ecr, amp), "ecrasement": float(ecr),
                              "amplitude_um": float(amp), "rayon_mm": float(r_mm),
                              "memoire_du_cap": float(cap),
                              "marche": le_cote_dune_marche(p)})
    return {"decidable": bool(cases), "cases": cases,
            "rayons_mm": [float(r) for r in rayons_mm], "caps": [float(c) for c in caps],
            "pas_max": int(pas_max)}


def _cumuler(cs: list[dict], nom: str) -> dict:
    out = {"nom": nom, "cases": len(cs), **_resume([c["marche"] for c in cs])}
    # ⭐⭐⭐⭐ L'ENONCE EST CELUI DE `R4-F79`, MOT POUR MOT, ET IL SE COMPTE SUR LES CASES. Une
    # matiere penche axialement quand AUCUNE de ses marches decidables ne penche dans l'autre
    # sens — la forme jointe du depot. Une moyenne pardonnerait a une matiere qui penche d'un
    # cote la moitie du temps.
    out["elle_penche_axialement"] = bool(
        out.get("decidable") and out.get("penchent_axialement", 0) > 0
        and out.get("penchent_azimutalement", 0) == 0)
    return out


def par_matiere(d: dict) -> list[dict]:
    return [_cumuler([c for c in d["cases"] if c["nom"] == nom], nom)
            for nom in dict.fromkeys(c["nom"] for c in d["cases"])]


def _croiser(d: dict, cle: str) -> list[dict]:
    return [_cumuler([c for c in d["cases"] if c[cle] == v], f"{cle} {v}")
            for v in dict.fromkeys(c[cle] for c in d["cases"])]


def juger(d: dict, rouleau: dict | None) -> dict:
    if not d.get("decidable"):
        return {"decidable": False, "raison": "aucune case mesurée"}
    # ⚠⚠⚠ SANS LE ROULEAU IL N'Y A PAS DE COMPARAISON. Conclure sur la seule fixture serait une
    # affirmation sur une matiere deguisee en comparaison entre deux.
    if rouleau is None:
        return {"decidable": False,
                "raison": f"la course du rouleau est absente : {LA_COURSE_DU_ROULEAU.name}"}
    mat = par_matiere(d)
    nue = next((m for m in mat if m["nom"] == _nom(*LA_SPIRALE_NUE)), None)
    # ⚠⚠ LE CONTROLE EST UNE ABSENCE DE PENCHANT : sur la spirale nue la normale est presque le
    # rayon, donc les DEUX parts sont quasi nulles et leur comparaison ne veut rien dire. Ce qui
    # est exige n'est pas un sens mais l'ABSENCE de glissement.
    controle = {"nom": nue["nom"] if nue else None,
                "axial_median": nue["axial_median"] if nue else None,
                "azimutal_median": nue["azimutal_median"] if nue else None,
                "glissement_axial_median_um": (nue["glissement_axial_median_um"]
                                               if nue else None),
                "decidables": nue["decidables"] if nue else None}
    controle["il_ne_penche_pas"] = bool(
        nue is not None and nue["decidables"] > 0
        and controle["glissement_axial_median_um"] == 0.0)
    # ⭐⭐⭐⭐ LA MATIERE DU ROULEAU EST CELLE QUE `R4-F87` A CALIBREE : c'est la seule dont la
    # comparaison au vrai rouleau ait un sens, et c'est celle sur laquelle `161`-`168` tournent.
    la_calibree = next((m for m in mat if m["nom"] == _nom(*MATIERES[-1])), None)
    comparaison = None
    if la_calibree and la_calibree.get("decidable"):
        comparaison = {
            "nom": la_calibree["nom"], "le_rouleau": rouleau,
            "le_cote_saccorde": bool(la_calibree["elle_penche_axialement"]
                                     and rouleau["axial_absolu_median"]
                                     > rouleau["azimutal_absolu_median"]),
            # ⚠⚠ CHAQUE GRANDEUR PORTE SES DEUX COTES SOUS LEURS PROPRES NOMS. Une premiere
            # version affichait le chiffre du ROULEAU sous l'etiquette « fixture » : un nombre
            # juste sous un mauvais nom est pire qu'un nombre absent.
            "part_axiale": {"la_fixture": la_calibree["axial_median"],
                            "le_rouleau": rouleau["axial_absolu_median"]},
            "part_azimutale": {"la_fixture": la_calibree["azimutal_median"],
                               "le_rouleau": rouleau["azimutal_absolu_median"]},
            "glissement_axial_um": {"la_fixture": la_calibree["glissement_axial_median_um"],
                                    "le_rouleau": rouleau["glissement_axial_median_um"]},
            "coherence": {"la_fixture": la_calibree["coherence_median"],
                          "le_rouleau": rouleau["coherence_mediane"]}}
        # ⚠⚠ « LE MEME COTE » ET « LE MEME SUIVI » SONT DEUX ENONCES, et les melanger ferait
        # passer une matiere qui glisse autant mais pas toujours du meme cote pour une matiere
        # qui reproduit le rouleau.
        comparaison["le_suivi_saccorde"] = bool(
            la_calibree["coherence_median"] >= rouleau["coherence_mediane"])
    return {"decidable": True, "par_matiere": mat,
            "par_rayon": _croiser(d, "rayon_mm"), "par_cap": _croiser(d, "memoire_du_cap"),
            "tout": _cumuler(d["cases"], "tout"),
            "le_controle_de_la_spirale_nue": controle,
            "la_comparaison_au_rouleau": comparaison,
            "matieres_qui_penchent_axialement": [str(m["nom"]) for m in mat
                                                 if m["elle_penche_axialement"]]}


def mesurer(matieres=MATIERES, rayons_mm=RAYONS_MM, caps=CAPS, pas_max: int = PAS_MAX,
            course: Path = LA_COURSE_DU_ROULEAU) -> dict:
    d = lenquete(matieres, rayons_mm, caps, pas_max)
    return {"enquete": d, "juger": juger(d, ce_que_le_rouleau_a_rendu(course))}


def reagreger(r: dict, course: Path = LA_COURSE_DU_ROULEAU) -> dict:
    r["juger"] = juger(r["enquete"], ce_que_le_rouleau_a_rendu(course))
    return r


def _court(nom: str) -> str:
    return (nom.replace("spirale ", "").replace("écrasée et froissée", "écr+fro")
            .replace("froissée", "fro").replace("écrasée", "écr"))


def afficher(r: dict) -> None:
    if "message" in r:
        print(f"⚠ {r['message']}")
        return
    j = r["juger"]
    if not j.get("decidable"):
        print(f"⚠ {j.get('raison', 'indécidable')}")
        return
    c = j["le_controle_de_la_spirale_nue"]
    marque = "★" if c["il_ne_penche_pas"] else "✗"
    print(f"{marque} contrôle — sur la spirale NUE il n'y a PAS de penchant : glissement axial "
          f"{c['glissement_axial_median_um']} µm, parts {c['axial_median']} et "
          f"{c['azimutal_median']} sur {c['decidables']} marches")
    for titre, groupes in (("par matière", j["par_matiere"]), ("par rayon", j["par_rayon"]),
                           ("par cap", j["par_cap"])):
        print(f"\n   — {titre} —")
        print(f"   {'':>22} | {'marches':>7} | {'axial':>7} | {'azimutal':>8} | "
              f"{'gliss. µm':>9} | {'cohér.':>7} | {'axial/azim/=':>13}")
        for g in groupes:
            if not g.get("decidable"):
                print(f"   {_court(g['nom']):>22} | {'—':>7} | {'(rien de décidable)':>40}")
                continue
            tient = "★" if g["elle_penche_axialement"] else " "
            print(f" {tient} {_court(g['nom']):>22} | {g['decidables']:>7} | "
                  f"{g['axial_median']:>7.3f} | {g['azimutal_median']:>8.3f} | "
                  f"{g['glissement_axial_median_um']:>9.1f} | {g['coherence_median']:>7.3f} | "
                  f"{g['penchent_axialement']:>4}/{g['penchent_azimutalement']:>4}/"
                  f"{g['parts_egales']:>3}")
    cp = j["la_comparaison_au_rouleau"]
    print("\n★★★★ la fixture calibrée penche-t-elle du même CÔTÉ que le vrai rouleau ?")
    if cp is None:
        print("      — la comparaison est indécidable")
        return
    r_ = cp["le_rouleau"]
    pa, pz = cp["part_axiale"], cp["part_azimutale"]
    print(f"      le côté  : {'OUI' if cp['le_cote_saccorde'] else 'non'} — "
          f"fixture {pa['la_fixture']} axial contre {pz['la_fixture']} azimutal ; "
          f"rouleau {pa['le_rouleau']} contre {pz['le_rouleau']} ({r_['source']})")
    g_ = cp["glissement_axial_um"]
    print(f"      le glissement axial : {g_['la_fixture']} µm contre {g_['le_rouleau']} µm")
    k_ = cp["coherence"]
    print(f"      le suivi : {'OUI' if cp['le_suivi_saccorde'] else 'non'} — cohérence "
          f"{k_['la_fixture']} contre {k_['le_rouleau']} sur le rouleau")


def _marche(axial: float, azimutal: float, gliss: float = 10.0, coh: float = 0.5,
            pas: int = 20) -> dict:
    return le_cote_dune_marche({"decidable": True, "pas": pas,
                                "axial_absolu_median": axial,
                                "azimutal_absolu_median": azimutal,
                                "glissement_axial_median_um": gliss,
                                "coherence_tangentielle": coh})


def _case(nom: str, m: dict | None, rayon: float = 10.0, cap: float = 0.0) -> dict:
    return {"nom": nom, "ecrasement": 0.0, "amplitude_um": 0.0, "rayon_mm": rayon,
            "memoire_du_cap": cap, "marche": m}


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

    print("— une marche, et de quel côté elle penche —")
    v("⭐⭐⭐ une marche plus axiale qu'azimutale est comptée comme telle",
      _marche(0.334, 0.193)["penche_axialement"] is True
      and _marche(0.334, 0.193)["penche_azimutalement"] is False)
    v("⭐⭐⭐⭐ ... et l'inverse est compté aussi, il n'est pas écarté",
      _marche(0.193, 0.334)["penche_azimutalement"] is True
      and _marche(0.193, 0.334)["penche_axialement"] is False)
    # ⚠⚠ UN ECART EXACTEMENT NUL N'EST NI L'UN NI L'AUTRE, l'enonce du depot depuis `161`.
    e = _marche(0.25, 0.25)
    v("⚠⚠ deux parts exactement égales sont comptées à part, jamais avec l'un des deux",
      e["les_deux_parts_sont_egales"] is True and e["penche_axialement"] is False
      and e["penche_azimutalement"] is False)
    v("⚠ une marche indécidable n'est pas un cas",
      le_cote_dune_marche({"decidable": False}) is None
      and le_cote_dune_marche({"decidable": True, "pas": 3}) is None)

    print("\n— l'énoncé se compte sur les cases —")
    tous = _cumuler([_case("m", _marche(0.3, 0.1)), _case("m", _marche(0.2, 0.15))], "m")
    v("⭐⭐⭐⭐ une matière penche axialement quand AUCUNE marche ne penche dans l'autre sens",
      tous["elle_penche_axialement"] is True)
    melange = _cumuler([_case("m", _marche(0.3, 0.1)), _case("m", _marche(0.1, 0.3))], "m")
    v("⭐⭐⭐⭐ ... et elle cesse dès qu'UNE SEULE penche dans l'autre",
      melange["elle_penche_axialement"] is False,
      "une sur deux suffit, c'est un compte et non une moyenne")
    v("⭐⭐⭐ ... et une matière dont rien n'est décidable ne le gagne pas",
      _cumuler([_case("m", None)], "m")["elle_penche_axialement"] is False,
      "rien à comparer n'est pas un penchant")

    print("\n— la comparaison EXIGE les deux côtés —")
    d_ = {"decidable": True, "rayons_mm": [10.0], "caps": [0.0], "pas_max": 20,
          "cases": [_case(_nom(*LA_SPIRALE_NUE), _marche(0.0, 0.002, gliss=0.0, coh=1.0)),
                    _case(_nom(*MATIERES[-1]), _marche(0.19, 0.148, gliss=43.7, coh=0.548))]}
    v("⚠⚠⚠ sans la course du rouleau, le jugement REFUSE de conclure",
      juger(d_, None)["decidable"] is False,
      "une comparaison dont un côté manque n'est pas une comparaison à moitié faite")
    faux_rouleau = {"source": "x", "nom": "y", "axial_absolu_median": 0.334,
                    "azimutal_absolu_median": 0.193, "glissement_axial_median_um": 43.2,
                    "coherence_mediane": 0.925}
    j = juger(d_, faux_rouleau)
    cp = j["la_comparaison_au_rouleau"]
    v("⭐⭐⭐⭐ le CÔTÉ et le SUIVI sont deux énoncés, jamais mêlés",
      cp["le_cote_saccorde"] is True and cp["le_suivi_saccorde"] is False,
      "une matière qui glisse autant sans glisser du même côté n'est pas la même matière")
    hautement = juger(d_, {**faux_rouleau, "coherence_mediane": 0.4})
    v("⭐⭐⭐ ... et le suivi s'accorde quand la cohérence y est",
      hautement["la_comparaison_au_rouleau"]["le_suivi_saccorde"] is True)
    # ⚠⚠⚠ UN NOMBRE JUSTE SOUS UN MAUVAIS NOM EST PIRE QU'UN NOMBRE ABSENT, et la batterie
    # passait des DEUX cotes avant ce controle : `afficher` imprimait la part du ROULEAU sous
    # l'etiquette « fixture ». Ce qui l'attrape n'est pas de relire le code, c'est de changer la
    # valeur de la FIXTURE et d'exiger que la sortie change.
    autre = juger({**d_, "cases": [d_["cases"][0],
                                   _case(_nom(*MATIERES[-1]),
                                         _marche(0.717, 0.148, gliss=43.7, coh=0.548))]},
                  faux_rouleau)
    t1, t2 = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(t1):
        afficher({"juger": j, "enquete": d_})
    with contextlib.redirect_stdout(t2):
        afficher({"juger": autre, "enquete": d_})
    v("⭐⭐⭐⭐ la part de la FIXTURE est celle qui est écrite sous son nom",
      "0.717" in t2.getvalue() and "0.717" not in t1.getvalue()
      and autre["la_comparaison_au_rouleau"]["part_axiale"]["la_fixture"] == 0.717,
      "un nombre juste sous un mauvais nom est pire qu'un nombre absent")
    v("⚠ les chiffres du rouleau sont RELUS, jamais recalculés",
      cp["le_rouleau"]["glissement_axial_median_um"] == 43.2
      and cp["glissement_axial_um"]["le_rouleau"] == 43.2)
    v("⚠⚠ une course absente rend None, elle ne rend pas des zéros",
      ce_que_le_rouleau_a_rendu(RACINE / "docs" / "mesures" / "_absente_169.json") is None)

    print("\n— le contrôle est une ABSENCE de penchant —")
    v("⭐⭐⭐⭐ le contrôle tient quand la spirale nue ne glisse pas",
      j["le_controle_de_la_spirale_nue"]["il_ne_penche_pas"] is True)
    glisse = juger({**d_, "cases": [_case(_nom(*LA_SPIRALE_NUE),
                                          _marche(0.3, 0.1, gliss=12.0)),
                                    d_["cases"][1]]}, faux_rouleau)
    v("⭐⭐⭐⭐ ... et il TOMBE dès que la spirale nue glisse",
      glisse["le_controle_de_la_spirale_nue"]["il_ne_penche_pas"] is False,
      "un glissement sur une matière sans penchant mesurerait le marcheur")

    print("\n— `mesurer`, `reagreger`, `afficher` —")
    petite = mesurer(matieres=(LA_SPIRALE_NUE, MATIERES[-1]), rayons_mm=(10.0,), caps=(0.75,),
                     pas_max=12)
    jp = petite["juger"]
    v("⭐⭐⭐⭐ sur la spirale NUE la mesure réelle ne trouve AUCUN glissement",
      jp["le_controle_de_la_spirale_nue"]["il_ne_penche_pas"] is True,
      f"{jp['le_controle_de_la_spirale_nue']}")
    # ⚠⚠⚠ ET SUR LA MATIERE CALIBREE LES DEUX PARTS DOIVENT EXISTER REELLEMENT. Sans ce controle
    # la batterie ne verifierait jamais sur donnees reelles que le marcheur avance.
    cal = next(m for m in jp["par_matiere"] if m["nom"] == _nom(*MATIERES[-1]))
    v("⭐⭐⭐⭐ sur la matière calibrée, le marcheur avance et les deux parts existent",
      cal["decidable"] and cal["decidables"] > 0 and cal["glissement_axial_median_um"] > 0.0,
      f"{cal['decidables']} marches, {cal['axial_median']} axial contre "
      f"{cal['azimutal_median']} azimutal, {cal['glissement_axial_median_um']} µm")
    avant = json.loads(json.dumps(petite["enquete"]))
    r2 = reagreger(json.loads(json.dumps(petite)))
    v("⭐⭐⭐ `reagreger` ne touche PAS un seul nombre mesuré", r2["enquete"] == avant)
    tampon = io.StringIO()
    with contextlib.redirect_stdout(tampon):
        afficher({"juger": j, "enquete": d_})
    sortie = tampon.getvalue()
    v("⚠ `afficher` rend le contrôle, les tableaux et les deux énoncés",
      "contrôle" in sortie and "par matière" in sortie and "le côté" in sortie
      and "le suivi" in sortie, f"{len(sortie)} caractères")
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
