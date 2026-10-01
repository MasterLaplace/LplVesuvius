"""Sur PHercParis4, graines 4 à 6, m7 compte-t-il une feuille entre les tours −6 et −7 publiés, là où arrive un saut parti du tour −6 ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UNE SEULE FEUILLE NE SOIT COMPTÉE ENTRE DEUX TOURS PUBLIÉS. Ce qui était vu avant d'écrire : tout ce
que `296` à `406` publient, dont **`R4-F592`** (`406` : sur les graines 4 à 6, 10 sauts d'une feuille partent du tour −6 et sont sur lui
au même endroit ; 9 d'entre eux mesurent 1,49 à 1,61 pas quand le tour −7 est à 0,43 à 0,56 pas), **`R4-F522`** (le tour −7 est plus
loin des plages de `m7` que le tour −6) et **`R4-F527`**, **`R4-F529`** (autour des graines 1 à 3, un tour publié est posé sur la feuille
de son voisin). `m7` n'a jamais été compté entre deux tours publiés : `345` à `406` comptent entre deux surfaces d'une chaîne.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P204`. Sur les graines 4 à 6, `m7` dit qu'un saut ne passe qu'une feuille alors qu'il va
trois fois plus loin que le tour −7. Les deux ne peuvent pas avoir raison ensemble. Si `m7` compte une feuille entre les tours −6 et −7
publiés, là où le saut arrive, le tour −7 est bien la feuille suivante, et c'est le compte du saut qui se trompe. S'il n'en compte aucune,
le tour −7 est posé sur la feuille du tour −6.

## Ce qui est fait

- **Les chaînes** : les deux familles de `403` à `406`, relancées sur les seize côtés. Le contrôle : les tours retrouvés redonnent ceux de
  `403`, et la lecture du départ de `406` redonne la sienne, saut par saut.
- **Le témoin** : les sauts d'une feuille que `403` juge justes, du tour k au tour k − 1. **La cible** : les sauts d'une feuille partis
  du tour −6, sur les graines 4 à 6, dont le départ est sur le tour −6 au même endroit (`406`).
- **Le compte** : les deux tours publiés k et k − 1, ramenés au niveau 2 et pris dans la boîte englobante de la surface d'arrivée du
  saut, élargie de la marge de `329`, la boîte où `404` à `406` prennent leurs sommets en face ; les feuilles de `m7` passées de l'un à l'autre, point par point, comme `345` compte un saut, et le nombre de feuilles que porte le
  plus de points, s'ils sont au moins 50 (`383`).
- **La règle** : le témoin vaut si au moins 5 de ses comptes sont lus et qu'au moins 80 % d'entre eux disent une feuille. S'il vaut : au
  moins 80 % des comptes de la cible à une feuille, **oui** ; moins de 50 %, **non** ; sinon, **en partie**. Indécidable si le témoin ne
  vaut pas, sous 5 comptes de la cible lus, si une lecture de `m7` échoue ou si le contrôle échoue.

## Les issues

L'issue de la tranche : **entre les tours −6 et −7, graines 4 à 6 : k comptes sur n à une feuille ; témoin : w sur t**, puis ce que dit la
règle. Si c'est non, ce que disent les autres comptes.

## Rapporté à côté, qui ne décide rien

Les comptes point par point de chaque saut lu ; ceux des sauts d'une feuille partis du tour −6 sur les autres graines.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : si c'est oui, pourquoi `m7` compte une seule feuille sur un saut qui en passe trois écarts de tour ;
rien sur PHerc0358.

Usage :
    uv run python src/nappe/m7_compte_t_il_une_feuille_entre_les_tours_moins_six_et_moins_sept_sur_paris4.py --verifier
    uv run python src/nappe/m7_compte_t_il_une_feuille_entre_les_tours_moins_six_et_moins_sept_sur_paris4.py \\
        --json docs/mesures/m7_compte_t_il_une_feuille_entre_les_tours_moins_six_et_moins_sept_sur_paris4.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))
sys.path.insert(0, str(RACINE / "src" / "tracecheck"))

import la_nappe_de_m7_retrouve_t_elle_le_trace_humain_de_paris4 as m321  # noqa: E402
import la_chaine_qui_croit_tombe_t_elle_sur_les_tours_publies as m329  # noqa: E402
import jusqua_quel_tour_publie_la_chaine_qui_croit_descend_elle as m330  # noqa: E402
import les_feuilles_de_m7_franchies_separent_elles_les_sauts_justes_des_faux as m345  # noqa: E402
import quelles_surfaces_laccord_de_trois_chaines_valide_t_il_sur_pherc0358 as m374  # noqa: E402
import une_surface_validee_par_trois_chaines_est_elle_sur_le_bon_tour_de_paris4 as m379  # noqa: E402
import les_feuilles_de_m7_disent_elles_que_le_premier_saut_de_la_suivie_de_la_graine_4_en_franchit_deux as m383  # noqa: E402
import laccord_aux_comptes_de_m7_valide_t_il_des_surfaces_sur_le_bon_tour_de_paris4 as m385  # noqa: E402
import un_saut_de_deux_feuilles_parti_du_tour_moins_six_finit_il_au_dela_du_suivant_sur_paris4 as m404  # noqa: E402
import la_lecture_de_404_donne_t_elle_un_tour_aux_sauts_justes_dune_feuille_sur_paris4 as m405  # noqa: E402
import le_depart_dun_saut_parti_du_tour_moins_six_est_il_sur_ce_tour_sur_paris4 as m406  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_403_A_PUBLIE = m404.CE_QUE_403_A_PUBLIE
CE_QUE_406_A_PUBLIE = LES_MESURES / "le_depart_dun_saut_parti_du_tour_moins_six_est_il_sur_ce_tour_sur_paris4.json"
LES_CHAINES = m374.LES_CHAINES
LES_FAMILLES = m404.LES_FAMILLES
LES_GRAINES_DE_LA_CIBLE = (4, 5, 6)
LA_PART, LA_MOITIE = 0.8, 0.5
LE_MINIMUM = 5


def la_grille(rang: int) -> dict:
    """Un tour publié comme une surface de chaîne : sa grille de sommets ramenée au niveau 2, et les sommets valides."""
    from la_spire_voisine_est_elle_a_un_pas import lire_tifxyz

    p, ok, _ = lire_tifxyz(m329.le_dossier_du_tour(rang, m330.LES_TOURS))
    return {"la_nappe": p / m321.LE_FACTEUR, "valide": ok}


def dans_la_boite(grille: dict, arrivee_l2: np.ndarray) -> dict:
    """Le tour réduit aux sommets dans la boîte englobante de la surface d'arrivée, élargie de la marge de `329`, au niveau 2 : la même
    boîte où `404` à `406` prennent les sommets en face."""
    marge = m329.LA_MARGE / m321.LE_FACTEUR
    lo, hi = arrivee_l2.min(axis=0) - marge, arrivee_l2.max(axis=0) + marge
    m = grille["valide"] & ((grille["la_nappe"] >= lo) & (grille["la_nappe"] <= hi)).all(axis=-1)
    return {"la_nappe": grille["la_nappe"], "valide": m}


def le_compte_entre_les_tours(grilles: dict, depart: int, suivant: int, arrivee_l2: np.ndarray, lire_valeurs) -> dict:
    """Les feuilles de `m7` passées du tour `depart` au tour `suivant`, point par point sur le tour suivant, dans la boîte de l'arrivée."""
    a, b = dans_la_boite(grilles[depart], arrivee_l2), dans_la_boite(grilles[suivant], arrivee_l2)
    if not a["valide"].any() or not b["valide"].any():
        return {"les_points": 0, "les_mesures": 0, "les_comptes": {}, "le_nombre_de_feuilles": None}
    f = m345.le_resume(m345.les_comptes_point_par_point(a, b, lire_valeurs, m385.LE_PAS))
    return {**f, "le_nombre_de_feuilles": m383.le_nombre_de_feuilles(f["les_comptes"])}


def les_lus(sauts: list[dict]) -> list[dict]:
    return [x for x in sauts if x["entre_les_tours"]["le_nombre_de_feuilles"] is not None]


def la_cible(sauts: list[dict]) -> list[dict]:
    return [x for x in sauts if x["le_nombre_de_feuilles"] == 1 and x["le_rang"] in LES_GRAINES_DE_LA_CIBLE
            and x["au_depart"]["lue"] and x["au_depart"]["sur_son_tour"]]


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("le_controle"):
        return {"decidable": False, "lissue": "indécidable : les chaînes relancées ne redonnent pas 403 et 406"}
    temoin, cible = les_lus(d["les_sauts_justes"]), les_lus(la_cible(d["les_sauts_de_moins_six"]))
    un = lambda xs: sum(x["entre_les_tours"]["le_nombre_de_feuilles"] == 1 for x in xs)  # noqa: E731
    w, k = un(temoin), un(cible)
    tete = f"entre les tours −6 et −7, graines 4 à 6 : {k} comptes sur {len(cible)} à une feuille ; témoin : {w} sur {len(temoin)}"
    if len(temoin) < LE_MINIMUM or w < LA_PART * len(temoin):
        return {"decidable": False, "lissue": f"{tete} ; indécidable, le témoin ne vaut pas"}
    if len(cible) < LE_MINIMUM:
        return {"decidable": False, "lissue": f"{tete} ; indécidable, moins de {LE_MINIMUM} comptes de la cible lus"}
    if k >= LA_PART * len(cible):
        return {"decidable": True, "lissue": f"{tete} ; oui"}
    autres = sorted({x["entre_les_tours"]["le_nombre_de_feuilles"] for x in cible} - {1})
    suite = "non" if k < LA_MOITIE * len(cible) else "en partie"
    return {"decidable": True, "lissue": f"{tete} ; {suite}, les autres comptes à " + ", ".join(str(a) for a in autres)}


def mesurer() -> dict:
    t0 = time.monotonic()
    tours = {r: m329.lire_un_tour(r, m330.LES_TOURS) for r in m330.LES_TOURS}
    grilles = {r: la_grille(r) for r in m330.LES_TOURS}
    d403 = json.loads(CE_QUE_403_A_PUBLIE.read_text())
    d406 = json.loads(CE_QUE_406_A_PUBLIE.read_text())
    lus406 = {(c["le_rang"], c["le_cote"], f, s["la_chaine"], s["le_saut"]): s["au_depart"]
              for c in d406["les_cotes"] for f in LES_FAMILLES for s in c[f]}
    vus406 = set()
    cotes = [{"le_rang": c["le_rang"], "le_cote": c["le_cote"], **{f: [] for f in LES_FAMILLES}} for c in d403["les_cotes"]]
    controle, pannes = True, []
    for f, enchainer in LES_FAMILLES.items():
        d331, trois_, cotes_d331, lv = m404.une_famille(enchainer)
        pannes += list(d331["les_pannes"])
        controle &= len(cotes_d331) == len(trois_) == len(d403["les_cotes"])
        for (rang, cote), trois, c403, c_out in zip(cotes_d331, trois_, d403["les_cotes"], cotes):
            controle &= (rang, cote) == (c403["le_rang"], c403["le_cote"])
            for x in LES_CHAINES:
                surfaces = [trois["les_nappes"][x]] + list(trois["les_relances"][x])
                retrouves = [m379.les_retrouves(s, tours) for s in surfaces]
                controle &= retrouves == c403[f][x]["les_tours"]
                for s403 in c403[f][x]["les_sauts"]:
                    h = s403["le_saut"]
                    depart = retrouves[h - 1]
                    juste = s403["dit"] == "juste" and s403["le_nombre_de_feuilles"] == 1 and s403["les_tours"] == 1
                    de_moins_six = depart == [m404.LE_DEPART] and s403["le_nombre_de_feuilles"] in m404.LES_FEUILLES
                    if not (juste or de_moins_six):
                        continue
                    k = depart[0]
                    avant, apres = m379.les_points_lus(surfaces[h - 1]), m379.les_points_lus(surfaces[h])
                    au_depart = m406.la_lecture(avant, apres, tours, k, k - 1)
                    cle = (rang, cote, f, x, h)
                    vus406.add(cle)
                    controle &= lus406.get(cle) == au_depart
                    arrivee_l2 = surfaces[h]["la_nappe"][surfaces[h]["valide"]]
                    c_out[f].append({"la_chaine": x, "le_saut": h, "le_nombre_de_feuilles": s403["le_nombre_de_feuilles"],
                                     "les_comptes": s403["les_comptes"], "le_depart": k, "juste": juste, "de_moins_six": de_moins_six,
                                     "au_depart": au_depart,
                                     "entre_les_tours": le_compte_entre_les_tours(grilles, k, k - 1, arrivee_l2, lv)})
            print(json.dumps({"la_famille": f, "le_rang": rang, "le_cote": cote, "controle": bool(controle),
                              "lus": len(c_out[f])}, ensure_ascii=False), flush=True)
    controle &= vus406 == set(lus406)
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"les_graines_de_la_cible": list(LES_GRAINES_DE_LA_CIBLE), "la_part": LA_PART, "la_moitie": LA_MOITIE,
                            "le_minimum": LE_MINIMUM, "le_minimum_de_mesures": m383.LE_MINIMUM_DE_MESURES,
                            "le_pas_l2": round(m385.LE_PAS, 3)},
         "les_pannes": pannes, "le_controle": bool(controle), "les_cotes": cotes,
         "les_sauts_justes": m405.les_sauts(cotes, "juste"), "les_sauts_de_moins_six": m405.les_sauts(cotes, "de_moins_six")}
    d["le_verdict"] = le_verdict(d)
    d["les_secondes"] = round(time.monotonic() - t0, 1)
    return d


def verifier() -> int:
    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        try:
            res = ok() if callable(ok) else ok
        except Exception as exc:  # noqa: BLE001
            echecs.append(f"{nom} — LEVÉE {type(exc).__name__}: {exc}")
            return
        if not res:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    n = 30
    ii, jj = np.meshgrid(np.arange(n, dtype=float), np.arange(n, dtype=float), indexing="ij")
    plan = lambda z: {"la_nappe": np.stack([ii * 2.0 + 20.0, jj * 2.0 + 20.0, np.full_like(ii, z)], -1),  # noqa: E731
                      "valide": np.ones((n, n), bool)}
    vol = np.zeros((120, 120, 120), bool)
    for z in (40, 58, 76):
        vol[z - 1:z + 2] = True
    lire = lambda idx: vol[tuple(np.clip(idx, 0, 119).reshape(-1, 3).T)].reshape(idx.shape[:-1])  # noqa: E731
    grilles = {-2: plan(40.0), -3: plan(58.0), -4: plan(40.5)}
    arrivee = plan(58.0)["la_nappe"].reshape(-1, 3)
    un = le_compte_entre_les_tours(grilles, -2, -3, arrivee, lire)
    zero = le_compte_entre_les_tours(grilles, -2, -4, arrivee, lire)
    v("★★★★ deux tours sur deux feuilles voisines de m7 en comptent une ; deux tours sur la même feuille, aucune",
      un["le_nombre_de_feuilles"] == 1 and zero["le_nombre_de_feuilles"] == 0, f"{un} {zero}")
    loin = np.array([[300.0, 300.0, 58.0], [310.0, 310.0, 58.0]])
    v("★★★★ hors de la boîte de l'arrivée, rien n'est compté",
      le_compte_entre_les_tours(grilles, -2, -3, loin, lire)["le_nombre_de_feuilles"] is None)
    petite = arrivee[(arrivee[:, 0] < 30.0) & (arrivee[:, 1] < 30.0)]
    bord = 28.0 + m329.LA_MARGE / m321.LE_FACTEUR
    v("★★★★ la boîte est celle de l'arrivée, élargie de la marge de 329, et rien au-delà",
      dans_la_boite(grilles[-3], petite)["valide"].sum() == ((ii * 2 + 20 <= bord) & (jj * 2 + 20 <= bord)).sum())

    lu = lambda n_, rang=4, sur=True, f=1: {"le_rang": rang, "le_nombre_de_feuilles": f,  # noqa: E731
                                           "au_depart": {"lue": True, "sur_son_tour": sur},
                                           "entre_les_tours": {"le_nombre_de_feuilles": n_}}
    v("★★★★ la cible : une feuille, graines 4 à 6, départ sur le tour −6",
      len(la_cible([lu(1), lu(1, rang=8), lu(1, sur=False), lu(1, f=2), lu(1, rang=6)])) == 2)

    def d_(temoin, cible, ok=True):
        return {"le_controle": ok, "les_pannes": [], "les_sauts_justes": [lu(c) for c in temoin],
                "les_sauts_de_moins_six": [lu(c) for c in cible]}
    t5 = [1, 1, 1, 1, 2]
    v("★★★★ la règle : 80 % à une feuille, oui ; moins de 50 %, non ; sinon, en partie, avec les autres comptes",
      le_verdict(d_(t5, [1] * 5))["lissue"].endswith("; oui")
      and le_verdict(d_(t5, [1, 1, 0, 0, 0]))["lissue"].endswith("; non, les autres comptes à 0")
      and le_verdict(d_(t5, [1, 1, 1, 0, 2]))["lissue"].endswith("; en partie, les autres comptes à 0, 2"))
    v("★★★★ l'issue dit les deux comptes",
      le_verdict(d_(t5, [1, 1, 1, 0, 2]))["lissue"]
      == "entre les tours −6 et −7, graines 4 à 6 : 3 comptes sur 5 à une feuille ; témoin : 4 sur 5 ; en partie, les autres comptes à 0, 2")
    v("★★★★ le témoin ne vaut pas sous 80 % ou sous 5 comptes ; un compte non lu ne compte pas",
      not le_verdict(d_([1, 1, 1, 2, 2], [1] * 5))["decidable"] and not le_verdict(d_([1] * 4, [1] * 5))["decidable"]
      and not le_verdict(d_([1] * 4 + [None], [1] * 5))["decidable"])
    v("★★★ indécidable sous 5 comptes de la cible, ou sans contrôle",
      not le_verdict(d_(t5, [1] * 4))["decidable"] and not le_verdict(d_(t5, [1] * 5, ok=False))["decidable"])

    for e in echecs:
        print(f"  ÉCHEC {e}")
    print(f"{Path(__file__).name}   {'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    d = mesurer()
    texte = json.dumps(d, ensure_ascii=False, indent=1)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(texte + "\n")
    print(json.dumps(d["le_verdict"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
