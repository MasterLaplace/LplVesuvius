"""Sur PHercParis4, graines 4 à 8, sous les croissances à cheval, les points que les tours publiés posent hors du tour attendu sont-ils là où leur tour publié les met, ou à l'écart de leur spire ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UN SEUL POINT NE SOIT LU À LA FOIS PAR SON ÉCART ET PAR SON TOUR. Ce qui était vu avant d'écrire : tout
ce que `296` à `360` publient, dont `R4-F546` (l'écart des points de la croissance au départ, rapporté à celui de sa spire, ne sépare pas
les croissances à cheval des saines), `R4-F545` (le compte des feuilles de `m7` non plus), et `R4-F529` (autour des graines 1 à 3, un
tour publié est posé sur la feuille de son voisin : c'est le référent qui s'y trompe).

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P158`. Deux juges sans référent ne voient pas le cheval que les tours publiés disent. Ou
bien le cheval est réel et les deux juges sont aveugles, ou bien ce sont les tours publiés qui placent mal ces points. Un point posé sur le
tour de départ qui en est vraiment revenu doit être près de la surface de départ ; un point posé au-delà doit en être deux fois plus loin
que sa spire. S'ils sont au contraire à l'écart de leur spire, c'est le tour publié qui se trompe là.

## Ce qui est fait

- **La chaîne qui regrandit** : celle de `358`, rejouée par la fonction de `357`, qui gagne pour cela le tour de départ de chaque saut.
- **Chaque point, par son écart et par son tour** : sous chaque saut qui garde une surface regrandie, le compte de `345` de toute la
  surface rend l'écart signé de chaque point au départ ; la pose de `347` rend les tours publiés sur lesquels il est posé, à un quart de pas.
  L'écart est rapporté à celui de la spire, la médiane des écarts de ses points semés, comme dans `360` : un rapport x sous ½ est **près du
  départ**, de ½ à 1,5 **à l'écart de la spire**, au-dessus de 1,5 **au-delà**, négatif **de l'autre côté**.
- **Les points hors du tour attendu** : ceux de `349`, posés sur le tour de départ et pas sur l'attendu, ou au-delà et pas sur l'attendu.
  Un tel point est **d'accord avec son tour** s'il est près du départ, resté, ou au-delà, parti au-delà ; **à l'écart de sa spire** sinon
  s'il y est.
- **Les croissances jugées** : les croissances à cheval des graines 4 à 8, justes, qui ont au moins 10 points hors du tour attendu lus
  par leur écart ; chacune va du côté où va la majorité de ces points, ou d'aucun.
- **Le contrôle** : sous ces croissances, les points posés sur le tour attendu sont, pour plus de la moitié, à l'écart de leur spire ;
  sinon l'écart ne lit pas les tours là où ils sont d'accord, et la tranche est indécidable. Et la chaîne rejouée redonne `358`.
- **La règle** : si plus de la moitié des croissances jugées ont leurs points hors du tour attendu à l'écart de leur spire, **ce sont les
  tours publiés qui les placent mal** ; si plus de la moitié les ont d'accord avec leur tour, **la croissance est vraiment à cheval** ;
  sinon, **ni l'un ni l'autre**. Indécidable sous 5 croissances jugées.

## Les issues

L'issue de la tranche : **sous a des n croissances à cheval jugées, les points hors du tour attendu sont à l'écart de leur spire, et
d'accord avec leur tour sous b**, puis ce que dit la règle.

## Rapporté à côté, qui ne décide rien

Les mêmes lectures sur les points semés et sur les points de la croissance, séparément ; et sous les croissances saines.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : où est la vraie feuille. Que l'écart et le tour publié se contredisent dit que l'un des deux se
trompe ; seul le scan, comme dans `343`, peut dire lequel.

Usage :
    uv run python src/nappe/les_points_hors_du_tour_attendu_sont_ils_a_lecart_de_leur_spire.py --verifier
    uv run python src/nappe/les_points_hors_du_tour_attendu_sont_ils_a_lecart_de_leur_spire.py \\
        --json docs/mesures/les_points_hors_du_tour_attendu_sont_ils_a_lecart_de_leur_spire.json
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
import la_chaine_qui_croit_tombe_t_elle_sur_les_tours_publies as m329  # noqa: E402
import jusqua_quel_tour_publie_la_chaine_qui_croit_descend_elle as m330  # noqa: E402
import le_critere_sans_referent_separe_t_il_les_sauts_justes_des_faux as m344  # noqa: E402
import les_points_poses_sur_le_tour_de_trop_franchissent_ils_autre_chose_quune_feuille as m347  # noqa: E402
import une_chaine_qui_garde_la_spire_tenue_va_t_elle_plus_loin_sur_pherc0358 as m356  # noqa: E402
import la_chaine_mixte_tient_elle_ses_sauts_justes_sur_paris4 as m357  # noqa: E402
import regrandir_la_spire_tenue_rend_il_de_la_surface_sans_passer_a_cheval as m358  # noqa: E402
import le_critere_sur_la_seule_croissance_separe_t_il_les_croissances_a_cheval as m359  # noqa: E402

LE_MINIMUM_DE_POINTS = 10
LE_MINIMUM = 5
PRES, SPIRE, DELA, AUTRE, INCONNU = "près du départ", "à l'écart de la spire", "au-delà", "de l'autre côté", "inconnu"
_LES_TOURS: dict = {}


def la_zone(x: float) -> str:
    """Où est un point, par le rapport de son écart au départ à celui de sa spire."""
    if not np.isfinite(x):
        return INCONNU
    if x < -0.5:
        return AUTRE
    if abs(x) < 0.5:
        return PRES
    return SPIRE if x <= 1.5 else DELA


def les_tours() -> dict:
    if not _LES_TOURS:
        _LES_TOURS.update({r: m329.lire_un_tour(r, m330.LES_TOURS) for r in m330.LES_TOURS})
    return _LES_TOURS


def les_points_lus(k: dict, lire_valeurs, comptes=m359.les_comptes4, poser=None) -> dict | None:
    """Sous un saut qui garde une surface regrandie, chaque point pris par le compte de `345`, lu par son écart rapporté à celui de sa
    spire et par les tours publiés où il est posé ; rendu en comptes par (tours, zone, partie). None sous un autre saut."""
    rl = k.get("la_relance")
    if k.get("depuis") != m356.DEPUIS_LA_CROISSANCE or rl is None or "les_semes" not in rl:
        return None
    r = comptes(k["le_depart"], rl, lire_valeurs)
    if r is None:
        return {"lecart_de_la_spire": None, "les_comptes": {}}
    poser = poser or (lambda pts, nn: m347.les_poses(pts * m321.LE_FACTEUR, nn, les_tours()))
    poses = poser(r["les_points"], r["les_normales"])
    semes = rl["les_semes"].ravel()[r["les_mailles"]]
    e = np.where(np.asarray(r["en_face"], dtype=bool), np.asarray(r["les_ecarts"], dtype=float), np.nan)
    spire = e[semes & np.isfinite(e)]
    es = float(np.median(spire)) if len(spire) else None
    n = Counter()
    for ecart, tours, seme in zip(e, poses, semes):
        zone = INCONNU if es is None or es == 0 else la_zone(ecart / es)
        n[f"{','.join(str(t) for t in sorted(tours))}|{zone}|{'semis' if seme else 'croissance'}"] += 1
    return {"lecart_de_la_spire": None if es is None else round(es, 3), "les_comptes": dict(sorted(n.items()))}


def la_lecture(saut: dict, sens: int, partie: str | None = None) -> dict | None:
    """Sous un saut dont le tour de départ est lu : ses points posés sur le tour attendu, restés sur le tour de départ, partis au-delà,
    par zone ; seulement ceux de `partie` si elle est donnée. None sans tour de départ ou sans lecture."""
    w0 = saut.get("le_tour_de_depart")
    if w0 is None or not saut.get("en_plus"):
        return None
    wa, wd = w0 + sens, w0 + 2 * sens
    out = {g: Counter() for g in ("attendu", "restes", "au_dela")}
    for cle, n in saut["en_plus"]["les_comptes"].items():
        tours, zone, part = cle.split("|")
        w = {int(t) for t in tours.split(",") if t}
        if partie is not None and part != partie:
            continue
        if wa in w:
            out["attendu"][zone] += n
        elif w0 in w:
            out["restes"][zone] += n
        elif wd in w:
            out["au_dela"][zone] += n
    return {g: dict(c) for g, c in out.items()}


def le_cote_de(lu: dict) -> tuple[str | None, int, int, int]:
    """Des points hors du tour attendu lus par leur écart : combien sont d'accord avec leur tour, combien à l'écart de leur spire, combien
    lus ; et le côté de la majorité, ou None."""
    accord = lu["restes"].get(PRES, 0) + lu["au_dela"].get(DELA, 0)
    spire = lu["restes"].get(SPIRE, 0) + lu["au_dela"].get(SPIRE, 0)
    lus = sum(n for g in ("restes", "au_dela") for z, n in lu[g].items() if z != INCONNU)
    cote = "la spire" if 2 * spire > lus else "le tour" if 2 * accord > lus else None
    return cote, accord, spire, lus


def les_croissances_a_cheval(cotes: list[dict], a_cheval: bool = True) -> list[tuple[dict, int]]:
    return [(s, m344.LE_SENS[c["le_cote"]]) for c in cotes if c["le_rang"] in m344.LES_GRAINES_PROPRES for s in c["les_sauts"]
            if s["la_justesse"] == "juste" and s["depuis"] == m356.DEPUIS_LA_CROISSANCE and bool(s["a_cheval"]) == a_cheval
            and s.get("en_plus")]


def le_bilan(cotes: list[dict]) -> dict:
    jugees, attendu = [], Counter()
    for s, sens in les_croissances_a_cheval(cotes):
        lu = la_lecture(s, sens)
        if lu is None:
            continue
        cote, accord, spire, lus = le_cote_de(lu)
        attendu.update(lu["attendu"])
        if lus >= LE_MINIMUM_DE_POINTS:
            jugees.append({"le_cote_de": cote, "daccord": accord, "a_lecart": spire, "lus": lus})
    lus_attendu = sum(n for z, n in attendu.items() if z != INCONNU)
    return {"les_jugees": len(jugees), "a_lecart_de_la_spire": sum(j["le_cote_de"] == "la spire" for j in jugees),
            "daccord_avec_le_tour": sum(j["le_cote_de"] == "le tour" for j in jugees), "le_detail": jugees,
            "lattendu": dict(attendu), "le_controle": bool(lus_attendu) and 2 * attendu.get(SPIRE, 0) > lus_attendu}


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("redonne_358"):
        return {"decidable": False, "lissue": "indécidable : la chaîne rejouée ne redonne pas ce que 358 publie"}
    b = d["le_bilan"]
    if not b["le_controle"]:
        return {"decidable": False, "lissue": "indécidable : sur le tour attendu, les points ne sont pas à l'écart de leur spire"}
    if b["les_jugees"] < LE_MINIMUM:
        return {"decidable": False, "lissue": f"indécidable : {b['les_jugees']} croissances jugées"}
    tete = (f"sous {b['a_lecart_de_la_spire']} des {b['les_jugees']} croissances à cheval jugées, les points hors du tour attendu sont à "
            f"l'écart de leur spire, et d'accord avec leur tour sous {b['daccord_avec_le_tour']}")
    if 2 * b["a_lecart_de_la_spire"] > b["les_jugees"]:
        suite = "ce sont les tours publiés qui les placent mal"
    elif 2 * b["daccord_avec_le_tour"] > b["les_jugees"]:
        suite = "la croissance est vraiment à cheval"
    else:
        suite = "ni l'un ni l'autre"
    return {"decidable": True, "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    t0 = time.monotonic()
    r = m357.la_chaine_jugee(chainer=m358.la_chaine_qui_regrandit, en_plus=les_points_lus)
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"le_minimum_de_points": LE_MINIMUM_DE_POINTS, "le_minimum": LE_MINIMUM},
         "les_pannes": r["les_pannes"], "la_lecture_de_m7": r["la_lecture_de_m7"], "le_controle": r["le_controle"],
         "redonne_358": m359.redonne_358(r["les_cotes"], json.loads(m359.CE_QUE_358_A_PUBLIE.read_text())), "les_cotes": r["les_cotes"]}
    d["le_bilan"] = le_bilan(r["les_cotes"])
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

    v("★★★★ les zones : près du départ, à l'écart de la spire, au-delà, de l'autre côté, inconnu",
      [la_zone(x) for x in (0.0, 0.49, 0.5, 1.0, 1.5, 1.51, -0.6, -0.4, float("nan"))]
      == [PRES, PRES, SPIRE, SPIRE, SPIRE, DELA, AUTRE, PRES, INCONNU])
    n = 10
    valide = np.ones((n, n), dtype=bool)
    semes = np.zeros((n, n), dtype=bool)
    semes[:4] = True
    k = {"depuis": m356.DEPUIS_LA_CROISSANCE, "le_depart": {}, "la_relance": {"la_nappe": np.zeros((n, n, 3)), "valide": valide,
                                                                              "les_semes": semes}}

    def comptes(dep, arr, lv):
        e = [10.0] * 40 + [10.0] * 20 + [1.0] * 20 + [20.0] * 10 + [float("nan")] * 10
        return {"les_points": np.zeros((100, 3)), "les_normales": np.zeros((100, 3)), "les_mailles": np.arange(100),
                "en_face": np.array([i != 45 for i in range(100)]), "les_ecarts": e}

    def poser(pts, nn):
        return [[0, -1] if i < 40 else [-1] if i < 60 else [0] if i < 80 else [-2] if i < 90 else [] for i in range(100)]
    lu = les_points_lus(k, "m7", comptes, poser)
    v("★★★★ chaque point, par son écart rapporté à celui de la spire et par ses tours ; un point sans le départ en face est inconnu",
      lu["lecart_de_la_spire"] == 10.0 and lu["les_comptes"] == {"-1,0|à l'écart de la spire|semis": 40,
                                                                  "-1|à l'écart de la spire|croissance": 19,
                                                                  "-1|inconnu|croissance": 1, "0|près du départ|croissance": 20,
                                                                  "-2|au-delà|croissance": 10, "|inconnu|croissance": 10},
      str(lu))
    def comptes_biais(dep, arr, lv):
        e = [10.0] * 40 + [1.0] * 60
        return {"les_points": np.zeros((100, 3)), "les_normales": np.zeros((100, 3)), "les_mailles": np.arange(100),
                "en_face": np.ones(100, dtype=bool), "les_ecarts": e}
    v("★★★★ l'écart de la spire se lit sur ses seuls points semés", les_points_lus(k, "m7", comptes_biais, poser)["lecart_de_la_spire"] == 10.0)
    vus, avant = [], (m347.les_poses, dict(_LES_TOURS))
    m347.les_poses = lambda pts, nn, tours: vus.append((float(pts[0, 0]), dict(tours))) or [[] for _ in pts]
    _LES_TOURS.clear()
    _LES_TOURS.update({"sonde": "les tours publiés"})
    try:
        def comptes_un(dep, arr, lv):
            r_ = comptes(dep, arr, lv)
            r_["les_points"] = np.ones((100, 3))
            return r_
        les_points_lus(k, "m7", comptes_un)
    finally:
        m347.les_poses = avant[0]
        _LES_TOURS.clear()
        _LES_TOURS.update(avant[1])
    v("★★★★ les points sont posés sur les tours publiés au niveau 0, leur pas multiplié par le facteur de niveau",
      vus == [(m321.LE_FACTEUR, {"sonde": "les tours publiés"})], str(vus))
    v("★★★ sous une spire gardée ou une relance, rien",
      les_points_lus(dict(k, depuis=m356.DEPUIS_LA_SPIRE), "m7", comptes, poser) is None)
    s = {"le_tour_de_depart": 0, "en_plus": lu}
    l = la_lecture(s, -1)
    v("★★★★ la lecture : posé sur l'attendu, resté sur le départ sans l'attendu, parti au-delà sans l'attendu",
      l == {"attendu": {SPIRE: 59, INCONNU: 1}, "restes": {PRES: 20}, "au_dela": {DELA: 10}}, str(l))
    v("★★★ sens plus : l'attendu est au-dessus du départ", la_lecture({"le_tour_de_depart": -2, "en_plus": lu}, 1)["attendu"]
      == {SPIRE: 59, INCONNU: 1} and la_lecture({"le_tour_de_depart": -2, "en_plus": lu}, 1)["restes"] == {DELA: 10})
    v("★★★ la lecture d'une seule partie", la_lecture(s, -1, "semis") == {"attendu": {SPIRE: 40}, "restes": {}, "au_dela": {}})
    v("★★★ sans tour de départ, pas de lecture", la_lecture({"le_tour_de_depart": None, "en_plus": lu}, -1) is None)
    v("★★★★ d'accord avec son tour : resté près du départ, ou parti au-delà", le_cote_de(la_lecture(s, -1)) == ("le tour", 30, 0, 30))
    a_lecart = {"attendu": {SPIRE: 50}, "restes": {SPIRE: 40, PRES: 5}, "au_dela": {SPIRE: 10, DELA: 5, INCONNU: 7}}
    v("★★★★ à l'écart de sa spire : la majorité des points lus hors de l'attendu y sont ; les inconnus ne comptent pas",
      le_cote_de(a_lecart) == ("la spire", 10, 50, 60))
    v("★★★ sans majorité, moitié comprise : ni l'un ni l'autre", le_cote_de({"restes": {SPIRE: 5, PRES: 5}, "au_dela": {AUTRE: 2}})[0] is None
      and le_cote_de({"restes": {SPIRE: 5, PRES: 5}, "au_dela": {}})[0] is None)

    def saut(lu_, cheval=True, rang=5):
        return {"le_rang": rang, "le_cote": "moins", "les_sauts": [{"la_justesse": "juste", "depuis": m356.DEPUIS_LA_CROISSANCE,
                                                                     "a_cheval": cheval, "le_tour_de_depart": 0, "en_plus": lu_}]}
    ecart = {"lecart_de_la_spire": 10.0, "les_comptes": {"-1|à l'écart de la spire|croissance": 60, "0|à l'écart de la spire|croissance": 30,
                                                          "0|près du départ|croissance": 5}}
    peu = {"lecart_de_la_spire": 10.0, "les_comptes": {"-1|à l'écart de la spire|croissance": 60, "0|près du départ|croissance": 9}}
    b = le_bilan([saut(ecart), saut(lu), saut(peu), saut(ecart, cheval=False), saut(ecart, rang=2)])
    v("★★★★ le bilan : les croissances à cheval des graines 4 à 8, justes, à 10 points lus hors de l'attendu",
      (b["les_jugees"], b["a_lecart_de_la_spire"], b["daccord_avec_le_tour"]) == (2, 1, 1), str(b))
    v("★★★★ le contrôle : sur l'attendu, les points sont à l'écart de leur spire pour plus de la moitié",
      b["le_controle"] and not le_bilan([saut({"lecart_de_la_spire": 10.0, "les_comptes": {"-1|près du départ|croissance": 60,
                                                                                         "-1|à l'écart de la spire|croissance": 60}})])["le_controle"])

    def d_(a, t, n_=10, ok=True, rej=True):
        return {"les_pannes": [], "redonne_358": rej, "le_bilan": {"les_jugees": n_, "a_lecart_de_la_spire": a, "daccord_avec_le_tour": t,
                                                                   "le_controle": ok}}
    v("★★★★ la règle : la spire, le tour, ni l'un ni l'autre",
      le_verdict(d_(6, 2))["lissue"].endswith("les placent mal") and le_verdict(d_(2, 6))["lissue"].endswith("vraiment à cheval")
      and le_verdict(d_(5, 5))["lissue"].endswith("ni l'un ni l'autre"))
    v("★★★ un contrôle tombé, moins de 5 croissances, une chaîne qui ne redonne pas 358 : indécidable",
      not le_verdict(d_(6, 2, ok=False))["decidable"] and not le_verdict(d_(4, 0, n_=4))["decidable"]
      and not le_verdict(d_(6, 2, rej=False))["decidable"] and le_verdict(d_(3, 0, n_=5))["decidable"])

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
