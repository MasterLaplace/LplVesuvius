"""Sur PHercParis4, graines 4 à 8, le décalage d'un tour dont la chaîne qui regrandit hérite est-il déjà dans sa nappe de départ, ou naît-il dans une croissance, et à quel saut ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UNE SEULE SURFACE DE LA CHAÎNE NE SOIT LUE POINT PAR POINT CONTRE SON PROPRE TOUR. Ce qui était vu avant
d'écrire : tout ce que `296` à `362` publient, dont `R4-F548` (sous les croissances à cheval, 4 % seulement des pieds des points hors du
tour attendu sont sur le tour de départ : la surface de départ était déjà hors de son tour, et le décalage grandit de saut en saut) et
`R4-F543` (la chaîne mixte, sans croissance, ne passe à cheval qu'une fois sur 30). ⚠ `340` publie, pour chaque nappe de départ, la part
des sommets de chaque tour publié à un quart de pas d'elle ; sur la graine 6, 17 % des sommets du tour `5753_-1` le sont, ce qui laisse
attendre qu'une partie de la nappe y soit déjà.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P160`. Chaque saut de la chaîne qui regrandit est juste là où elle est ; un juge local ne
voit donc pas le décalage. Savoir où il naît dit où un juge doit regarder : dans la nappe, avant la première croissance, ou dans une
croissance.

## Ce qui est fait

- **Les deux chaînes** : la chaîne mixte de `357` et la chaîne qui regrandit de `358`, rejouées par la fonction de `357`.
- **Chaque surface de la chaîne, point par point** : la nappe de départ, puis la surface gardée à chaque saut ; au plus
  `m326.LE_MAXIMUM_DE_POINTS` de ses points posés à normale connue, pris comme le compte de `345` les prend, et les tours publiés où la
  pose de `347` les met.
- **Son propre tour** : pour la nappe, le tour qu'elle retrouve seule ; pour la surface du saut h, ce tour décalé de h dans le sens du
  côté. Un point est **hors de son tour** s'il est posé sur un tour et pas sur le sien.
- **La naissance** : sur un côté, la première surface, nappe comprise, qui a au moins 50 points hors de son tour, le seuil de `349`.
- **Les côtés jugés** : ceux des graines 4 à 8 dont la nappe retrouve un seul tour.
- **Le contrôle** : la chaîne mixte et la chaîne qui regrandit rejouées redonnent ce que `357` et `358` publient, saut par saut.
- **La règle** : parmi les côtés jugés où le décalage naît, si plus de la moitié le portent dès la nappe, **il est déjà dans la nappe de
  départ** ; si plus de la moitié le font naître dans une croissance, **il naît dans une croissance** ; sinon, **l'un et l'autre**.
  Indécidable sous 3 côtés où il naît.

## Les issues

L'issue de la tranche : **sur a côtés jugés, le décalage naît sur b ; dans la nappe sur c, dans une croissance sur d**, puis ce que dit la
règle.

## Rapporté à côté, qui ne décide rien

Les points hors de leur tour, surface par surface, sous les deux chaînes ; le saut où il naît quand c'est dans une croissance.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : pourquoi la nappe ou la croissance passe sur le tour voisin, ni un juge qui le verrait sans tracé.

Usage :
    uv run python src/nappe/ou_nait_le_decalage_que_la_chaine_qui_regrandit_herite.py --verifier
    uv run python src/nappe/ou_nait_le_decalage_que_la_chaine_qui_regrandit_herite.py \\
        --json docs/mesures/ou_nait_le_decalage_que_la_chaine_qui_regrandit_herite.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))
sys.path.insert(0, str(RACINE / "src" / "tracecheck"))

import la_nappe_de_m7_retrouve_t_elle_le_trace_humain_de_paris4 as m321  # noqa: E402
import le_critere_sans_referent_separe_t_il_les_sauts_justes_des_faux as m344  # noqa: E402
import les_feuilles_de_m7_franchies_separent_elles_les_sauts_justes_des_faux as m345  # noqa: E402
import les_points_poses_sur_le_tour_de_trop_franchissent_ils_autre_chose_quune_feuille as m347  # noqa: E402
import la_chaine_mixte_tient_elle_ses_sauts_justes_sur_paris4 as m357  # noqa: E402
import regrandir_la_spire_tenue_rend_il_de_la_surface_sans_passer_a_cheval as m358  # noqa: E402
import le_critere_sur_la_seule_croissance_separe_t_il_les_croissances_a_cheval as m359  # noqa: E402
import les_points_hors_du_tour_attendu_sont_ils_a_lecart_de_leur_spire as m361  # noqa: E402

LE_SEUIL = 50
LE_MINIMUM = 3
LES_CLES_357 = m358.LES_CLES_REJOUEES


def les_points_poses(surface: dict, poser=None) -> dict:
    """Les points d'une surface pris comme le compte de `345` les prend, au plus `m326.LE_MAXIMUM_DE_POINTS` à normale connue, et les
    tours publiés où chacun est posé ; rendu en comptes par ensemble de tours."""
    from la_spire_voisine_est_elle_a_un_pas import les_normales

    if surface is None or not surface["valide"].any():
        return {}
    nn, nok = les_normales(surface["la_nappe"], surface["valide"])
    m = surface["valide"] & nok
    q, nq = surface["la_nappe"][m], nn[m]
    if len(q) > m345.m326.LE_MAXIMUM_DE_POINTS:
        k = np.linspace(0, len(q) - 1, m345.m326.LE_MAXIMUM_DE_POINTS).round().astype(int)
        q, nq = q[k], nq[k]
    poser = poser or (lambda pts, n_: m347.les_poses(pts * m321.LE_FACTEUR, n_, m361.les_tours()))
    return dict(sorted(Counter(",".join(str(t) for t in sorted(w)) for w in poser(q, nq)).items()))


def les_surfaces_lues(k: dict, lire_valeurs, poser=None) -> dict:
    """Sous chaque saut : les points posés de la surface de départ et de la surface gardée."""
    return {"le_depart": les_points_poses(k.get("le_depart"), poser), "la_gardee": les_points_poses(k.get("la_relance"), poser)}


def hors_de_son_tour(poses: dict, tour: int) -> int:
    """Les points posés sur un tour et pas sur `tour`."""
    return sum(n for cle, n in poses.items() if cle and tour not in {int(t) for t in cle.split(",")})


def la_suite(cote: dict, sens: int) -> dict | None:
    """Sur un côté dont la nappe retrouve un seul tour : les points hors de leur tour de la nappe puis de chaque surface gardée, et l'indice
    de la première qui en a `LE_SEUIL`, 0 pour la nappe ; None si la nappe ne retrouve pas un seul tour."""
    sauts = cote["les_sauts"]
    if not sauts or sauts[0].get("le_tour_de_depart") is None or not sauts[0].get("en_plus"):
        return None
    w0 = sauts[0]["le_tour_de_depart"]
    suite = [hors_de_son_tour(sauts[0]["en_plus"]["le_depart"], w0)]
    for h, s in enumerate(sauts, 1):
        if not s.get("en_plus") or not s["en_plus"]["la_gardee"]:
            break
        suite.append(hors_de_son_tour(s["en_plus"]["la_gardee"], w0 + h * sens))
    naissance = next((i for i, n in enumerate(suite) if n >= LE_SEUIL), None)
    return {"le_tour_de_la_nappe": w0, "hors_de_son_tour": suite, "la_naissance": naissance}


def le_bilan(cotes: list[dict]) -> dict:
    lus = []
    for c in cotes:
        if c["le_rang"] not in m344.LES_GRAINES_PROPRES:
            continue
        s = la_suite(c, m344.LE_SENS[c["le_cote"]])
        if s is not None:
            lus.append({"le_rang": c["le_rang"], "le_cote": c["le_cote"], **s})
    nes = [x for x in lus if x["la_naissance"] is not None]
    return {"les_cotes_juges": len(lus), "ou_il_nait": len(nes), "dans_la_nappe": sum(x["la_naissance"] == 0 for x in nes),
            "dans_une_croissance": sum(x["la_naissance"] > 0 for x in nes), "le_detail": lus}


def redonne(cotes: list[dict], publies: list[dict]) -> bool:
    cle = lambda c: (c["le_rang"], c["le_cote"])  # noqa: E731
    garde = lambda c: [{k: s.get(k) for k in LES_CLES_357} for s in c["les_sauts"]]  # noqa: E731
    pub = {cle(c): garde(c) for c in publies}
    return bool(pub) and pub == {cle(c): garde(c) for c in cotes}


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("redonne_357") or not d.get("redonne_358"):
        return {"decidable": False, "lissue": "indécidable : les chaînes rejouées ne redonnent pas ce que 357 et 358 publient"}
    b = d["les_bilans"]["la_chaine_qui_regrandit"]
    if b["ou_il_nait"] < LE_MINIMUM:
        return {"decidable": False, "lissue": f"indécidable : le décalage naît sur {b['ou_il_nait']} côtés"}
    tete = (f"sur {b['les_cotes_juges']} côtés jugés, le décalage naît sur {b['ou_il_nait']} ; dans la nappe sur {b['dans_la_nappe']}, "
            f"dans une croissance sur {b['dans_une_croissance']}")
    suite = ("il est déjà dans la nappe de départ" if 2 * b["dans_la_nappe"] > b["ou_il_nait"]
             else "il naît dans une croissance" if 2 * b["dans_une_croissance"] > b["ou_il_nait"] else "l'un et l'autre")
    return {"decidable": True, "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    t0 = time.monotonic()
    mixte = m357.la_chaine_jugee(en_plus=les_surfaces_lues)
    regrandie = m357.la_chaine_jugee(chainer=m358.la_chaine_qui_regrandit, en_plus=les_surfaces_lues)
    d = {"la_question": __doc__.splitlines()[0], "les_constantes": {"le_seuil": LE_SEUIL, "le_minimum": LE_MINIMUM},
         "les_pannes": mixte["les_pannes"] + regrandie["les_pannes"],
         "la_lecture_de_m7": {"la_chaine_mixte": mixte["la_lecture_de_m7"], "la_chaine_qui_regrandit": regrandie["la_lecture_de_m7"]},
         "redonne_357": redonne(mixte["les_cotes"], json.loads(m358.CE_QUE_357_A_PUBLIE.read_text())["les_cotes"]),
         "redonne_358": redonne(regrandie["les_cotes"], json.loads(m359.CE_QUE_358_A_PUBLIE.read_text())["les_cotes"]["la_chaine_qui_regrandit"]),
         "les_cotes": {"la_chaine_mixte": mixte["les_cotes"], "la_chaine_qui_regrandit": regrandie["les_cotes"]}}
    d["les_bilans"] = {k: le_bilan(v) for k, v in d["les_cotes"].items()}
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

    n = 40
    g = np.zeros((n, n, 3))
    g[..., 0], g[..., 1] = np.meshgrid(np.arange(n) * 5.0, np.arange(n) * 5.0)
    surf = {"la_nappe": g, "valide": np.ones((n, n), dtype=bool)}
    vus = []

    def poser(pts, nn):
        vus.append(len(pts))
        return [[0] if i < 1000 else [-1] if i < 1150 else [] for i in range(len(pts))]
    p = les_points_poses(surf, poser)
    v("★★★★ les points d'une surface : ceux à normale connue, au plus le maximum du compte, par ensemble de tours",
      vus == [m345.m326.LE_MAXIMUM_DE_POINTS] and p == {"": 50, "-1": 150, "0": 1000} and 38 * 38 > m345.m326.LE_MAXIMUM_DE_POINTS,
      str((vus, p)))
    petit = {"la_nappe": g[:20, :20], "valide": np.ones((20, 20), dtype=bool)}
    vus[:] = []
    les_points_poses(petit, poser)
    v("★★★ seuls les points à normale connue : l'intérieur d'une petite surface", vus == [18 * 18], str(vus))
    vus2, avant, avant_t = [], m347.les_poses, dict(m361._LES_TOURS)
    m347.les_poses = lambda pts, nn, tours: vus2.append((float(pts[1, 0]), dict(tours))) or [[] for _ in pts]
    m361._LES_TOURS.clear()
    m361._LES_TOURS.update({"sonde": "les tours publiés"})
    try:
        les_points_poses(surf)
    finally:
        m347.les_poses = avant
        m361._LES_TOURS.clear()
        m361._LES_TOURS.update(avant_t)
    v("★★★ sans pose donnée, celle de 347 au niveau 0", len(vus2) == 1 and vus2[0][1] == {"sonde": "les tours publiés"}
      and vus2[0][0] > 0 and vus2[0][0] % m321.LE_FACTEUR == 0, str(vus2))
    v("★★★ une surface vide ou absente : rien", les_points_poses(None, poser) == {}
      and les_points_poses({"la_nappe": g, "valide": np.zeros((n, n), dtype=bool)}, poser) == {})
    v("★★★★ hors de son tour : posé sur un tour, et pas sur le sien", hors_de_son_tour({"": 9, "0": 10, "-1": 7, "-1,0": 4, "1": 2}, 0) == 9)

    def cote(poses_depart, gardees, w0=0, rang=5, nom="moins"):
        sauts = [{"le_tour_de_depart": w0 if h == 1 else None, "en_plus": {"le_depart": poses_depart if h == 1 else {}, "la_gardee": gd}}
                 for h, gd in enumerate(gardees, 1)]
        return {"le_rang": rang, "le_cote": nom, "les_sauts": sauts}
    s = la_suite(cote({"0": 900, "-1": 60}, [{"-1": 900, "-2": 10}, {"-2": 900, "-1": 70}]), -1)
    v("★★★★ la suite : la nappe contre son tour, chaque surface contre son tour décalé dans le sens du côté ; la naissance à la nappe",
      s == {"le_tour_de_la_nappe": 0, "hors_de_son_tour": [60, 10, 70], "la_naissance": 0}, str(s))
    s2 = la_suite(cote({"0": 900, "-1": 20}, [{"-1": 900, "-2": 10}, {"-2": 900, "-1": 70}]), -1)
    v("★★★★ la naissance dans une croissance, au saut où 50 points sont hors de leur tour", s2["la_naissance"] == 2, str(s2))
    s3 = la_suite(cote({"1": 900, "2": 20}, [{"2": 900}], w0=1, nom="plus"), 1)
    v("★★★ sens plus : le tour de la surface monte", s3["hors_de_son_tour"] == [20, 0] and s3["la_naissance"] is None, str(s3))
    v("★★★ une nappe qui ne retrouve pas un seul tour : pas de suite", la_suite(cote({}, [{}], w0=None), -1) is None)
    s4 = la_suite(cote({"0": 900}, [{"-1": 900}, {}, {"-3": 900, "-2": 80}]), -1)
    v("★★★ la suite s'arrête à la première surface vide", s4["hors_de_son_tour"] == [0, 0], str(s4))
    b = le_bilan([cote({"0": 900, "-1": 60}, [{"-1": 900}]), cote({"0": 900}, [{"-1": 900}, {"-2": 900, "-1": 90}], rang=6),
                  cote({"0": 900}, [{"-1": 900}], rang=7), cote({"0": 900, "-1": 99}, [{"-1": 900}], rang=2),
                  cote({}, [{}], w0=None, rang=8)])
    v("★★★★ le bilan : les côtés des graines 4 à 8 dont la nappe est lue ; où le décalage naît",
      (b["les_cotes_juges"], b["ou_il_nait"], b["dans_la_nappe"], b["dans_une_croissance"]) == (3, 2, 1, 1), str(b))

    def d_(nappe, crois, n_=5, rej=(True, True)):
        return {"les_pannes": [], "redonne_357": rej[0], "redonne_358": rej[1],
                "les_bilans": {"la_chaine_qui_regrandit": {"les_cotes_juges": n_, "ou_il_nait": nappe + crois, "dans_la_nappe": nappe,
                                                            "dans_une_croissance": crois}}}
    v("★★★★ la règle : la nappe, une croissance, l'un et l'autre", le_verdict(d_(3, 1))["lissue"].endswith("dans la nappe de départ")
      and le_verdict(d_(1, 3))["lissue"].endswith("dans une croissance") and le_verdict(d_(2, 2))["lissue"].endswith("l'un et l'autre"))
    v("★★★ sous 3 côtés où il naît, des chaînes qui ne redonnent pas 357 et 358 : indécidable",
      not le_verdict(d_(1, 1))["decidable"] and le_verdict(d_(2, 1))["decidable"]
      and not le_verdict(d_(3, 1, rej=(False, True)))["decidable"] and not le_verdict(d_(3, 1, rej=(True, False)))["decidable"])
    c = [{"le_rang": 4, "le_cote": "moins", "les_sauts": [{"le_saut": 1, "la_justesse": "juste", "depuis": "la spire", "tenu": True,
                                                          "a_cheval": False, "restes": 0, "au_dela": 0, "les_points_poses": 900}]}]
    autre = json.loads(json.dumps(c))
    autre[0]["les_sauts"][0]["restes"] = 3
    v("★★★★ redonne : saut par saut", redonne(c, c) and not redonne(autre, c) and not redonne(c, []))

    for e_ in echecs:
        print(f"  ÉCHEC {e_}")
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
