"""Sur PHercParis4, graines 4 à 8, sous les croissances à cheval, le pied de chaque point hors du tour attendu, à l'écart de sa spire, sur la surface de départ est-il posé sur le tour de départ, ou déjà sur un autre ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UN SEUL PIED NE SOIT LU SOUS LA CHAÎNE QUI REGRANDIT. Ce qui était vu avant d'écrire : tout ce que
`296` à `361` publient, dont `R4-F547` (sous 10 des 12 croissances à cheval, les points hors du tour attendu sont à l'écart de leur spire,
où sont 93 % des points de l'attendu : la surface et les tours publiés se contredisent là), `R4-F534` (sous la surface bornée de la graine
8, les pieds des points posés sur le tour de trop sont sur le tour d'avant : la surface de départ était déjà à cheval) et `R4-F536` (le
cheval naît à un saut et s'hérite aux suivants).

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P159`. Un point à l'écart d'une spire de la surface de départ, que la pose met sur le tour
de départ, contredit le tour publié ou la surface de départ. Son pied, le point de la surface de départ en face de lui, tranche : posé sur
le tour de départ, il met deux points à une spire l'un de l'autre sur le même tour publié, et c'est ce tour qui se contredit ; posé sur un
autre tour, c'est la surface de départ qui était déjà hors du sien, et le cheval s'hérite.

## Ce qui est fait

- **La chaîne qui regrandit** : celle de `358`, rejouée par la fonction de `357`, comme dans `361`.
- **Chaque point** : son écart au départ rapporté à celui de sa spire et les tours où il est posé, comme dans `361` ; **son pied**, le
  point de la surface de départ le plus proche, avec sa normale, et les tours publiés où ce pied est posé à un quart de pas, par les
  fonctions de `348`. Un pied sans normale n'est pas posé.
- **La question** : sous les croissances à cheval jugées de `361`, les points hors du tour attendu à l'écart de leur spire, et parmi leurs
  pieds posés sur un tour, la part posée sur le tour de départ.
- **Le contrôle** : sous les mêmes croissances, parmi les pieds posés des points posés sur le tour attendu à l'écart de leur spire, plus de
  la moitié sont posés sur le tour de départ ; sinon la mesure ne voit pas la surface de départ sur son tour, et la tranche est
  indécidable. Et la chaîne rejouée redonne `358`.
- **La règle** : au moins 50 pieds posés sous la question, sinon indécidable. Si les trois quarts au moins sont posés sur le tour de départ,
  **c'est le tour publié qui se contredit** ; si un quart au plus, **c'est la surface de départ qui était déjà hors de son tour** ; sinon,
  **l'un et l'autre**.

## Les issues

L'issue de la tranche : **sous les croissances à cheval, p % des pieds posés des points hors du tour attendu à l'écart de leur spire sont
sur le tour de départ**, puis ce que dit la règle.

## Rapporté à côté, qui ne décide rien

Les tours sur lesquels les autres pieds sont posés ; la même lecture pour les seuls points semés et pour ceux de la croissance.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : si un tour publié qui se contredit est faux, ou si c'est `m7` et la chaîne qui se trompent
ensemble ; seul le scan le dirait.

Usage :
    uv run python src/nappe/le_pied_des_points_hors_du_tour_attendu_est_il_sur_le_tour_de_depart.py --verifier
    uv run python src/nappe/le_pied_des_points_hors_du_tour_attendu_est_il_sur_le_tour_de_depart.py \\
        --json docs/mesures/le_pied_des_points_hors_du_tour_attendu_est_il_sur_le_tour_de_depart.json
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
import les_points_poses_sur_le_tour_de_trop_franchissent_ils_autre_chose_quune_feuille as m347  # noqa: E402
import la_surface_de_depart_est_elle_sur_son_tour_sous_la_surface_bornee as m348  # noqa: E402
import une_chaine_qui_garde_la_spire_tenue_va_t_elle_plus_loin_sur_pherc0358 as m356  # noqa: E402
import la_chaine_mixte_tient_elle_ses_sauts_justes_sur_paris4 as m357  # noqa: E402
import regrandir_la_spire_tenue_rend_il_de_la_surface_sans_passer_a_cheval as m358  # noqa: E402
import le_critere_sur_la_seule_croissance_separe_t_il_les_croissances_a_cheval as m359  # noqa: E402
import les_points_hors_du_tour_attendu_sont_ils_a_lecart_de_leur_spire as m361  # noqa: E402

LE_MINIMUM_DE_PIEDS = 50
SANS_PIED = "?"


def les_pieds_lus(k: dict, lire_valeurs, comptes=m359.les_comptes4, poser=None, poser_les_pieds=None,
                  trouver_les_pieds=None) -> dict | None:
    """Sous un saut qui garde une surface regrandie, chaque point pris par le compte de `345`, par sa zone, ses tours, sa partie, et les
    tours où son pied sur la surface de départ est posé ; rendu en comptes. None sous un autre saut."""
    rl = k.get("la_relance")
    if k.get("depuis") != m356.DEPUIS_LA_CROISSANCE or rl is None or "les_semes" not in rl:
        return None
    r = comptes(k["le_depart"], rl, lire_valeurs)
    if r is None:
        return {"lecart_de_la_spire": None, "les_comptes": {}}
    poser = poser or (lambda pts, nn: m347.les_poses(pts * m321.LE_FACTEUR, nn, m361.les_tours()))
    poser_les_pieds = poser_les_pieds or (lambda p, n, ok: m348.les_poses_des_pieds(p * m321.LE_FACTEUR, n, ok, m361.les_tours())[1])
    poses = poser(r["les_points"], r["les_normales"])
    pieds, npieds, ok = (trouver_les_pieds or m348.les_pieds)(r["les_points"], k["le_depart"])
    poses_pieds = poser_les_pieds(pieds, npieds, ok)
    semes = rl["les_semes"].ravel()[r["les_mailles"]]
    e = np.where(np.asarray(r["en_face"], dtype=bool), np.asarray(r["les_ecarts"], dtype=float), np.nan)
    spire = e[semes & np.isfinite(e)]
    es = float(np.median(spire)) if len(spire) else None
    n = Counter()
    for ecart, tours, seme, tp, bon in zip(e, poses, semes, poses_pieds, ok):
        zone = m361.INCONNU if es is None or es == 0 else m361.la_zone(ecart / es)
        pied = ",".join(str(t) for t in sorted(tp)) if bon else SANS_PIED
        n[f"{','.join(str(t) for t in sorted(tours))}|{zone}|{'semis' if seme else 'croissance'}|{pied}"] += 1
    return {"lecart_de_la_spire": None if es is None else round(es, 3), "les_comptes": dict(sorted(n.items()))}


def les_pieds_de(saut: dict, sens: int, partie: str | None = None) -> dict | None:
    """Sous un saut dont le tour de départ est lu : pour les points à l'écart de leur spire posés hors du tour attendu, puis sur l'attendu,
    les tours où leurs pieds sont posés ; seulement ceux de `partie` si elle est donnée."""
    w0 = saut.get("le_tour_de_depart")
    if w0 is None or not saut.get("en_plus"):
        return None
    wa, wd = w0 + sens, w0 + 2 * sens
    out = {"hors": Counter(), "attendu": Counter()}
    for cle, n in saut["en_plus"]["les_comptes"].items():
        tours, zone, part, pied = cle.split("|")
        w = {int(t) for t in tours.split(",") if t}
        if zone != m361.SPIRE or (partie is not None and part != partie):
            continue
        groupe = "attendu" if wa in w else "hors" if (w0 in w or wd in w) else None
        if groupe is not None:
            out[groupe][pied] += n
    return {g: dict(c) for g, c in out.items()}


def la_part_sur_le_depart(c: dict, w0: int) -> tuple[int, int]:
    """Des pieds : combien sont posés sur le tour de départ, combien sont posés sur un tour."""
    sur, poses = 0, 0
    for pied, n in c.items():
        if pied in (SANS_PIED, ""):
            continue
        poses += n
        sur += n if w0 in {int(t) for t in pied.split(",")} else 0
    return sur, poses


def le_bilan(cotes: list[dict]) -> dict:
    hors, attendu, ailleurs, jugees = [0, 0], [0, 0], Counter(), 0
    for s, sens in m361.les_croissances_a_cheval(cotes):
        lu = m361.la_lecture(s, sens)
        if lu is None or m361.le_cote_de(lu)[3] < m361.LE_MINIMUM_DE_POINTS:
            continue
        p = les_pieds_de(s, sens)
        w0 = s["le_tour_de_depart"]
        jugees += 1
        for acc, g in ((hors, "hors"), (attendu, "attendu")):
            sur, poses = la_part_sur_le_depart(p[g], w0)
            acc[0] += sur
            acc[1] += poses
        for pied, n in p["hors"].items():
            if pied not in (SANS_PIED, "") and w0 not in {int(t) for t in pied.split(",")}:
                ailleurs[str(sorted(int(t) - w0 for t in pied.split(",")))] += n
    return {"les_jugees": jugees, "hors": {"sur_le_depart": hors[0], "poses": hors[1]},
            "attendu": {"sur_le_depart": attendu[0], "poses": attendu[1]},
            "le_controle": bool(attendu[1]) and 2 * attendu[0] > attendu[1], "ailleurs_par_ecart_de_tour": dict(ailleurs)}


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("redonne_358"):
        return {"decidable": False, "lissue": "indécidable : la chaîne rejouée ne redonne pas ce que 358 publie"}
    b = d["le_bilan"]
    if not b["le_controle"]:
        return {"decidable": False, "lissue": "indécidable : sous l'attendu, les pieds ne sont pas sur le tour de départ"}
    h = b["hors"]
    if h["poses"] < LE_MINIMUM_DE_PIEDS:
        return {"decidable": False, "lissue": f"indécidable : {h['poses']} pieds posés"}
    p = h["sur_le_depart"] / h["poses"]
    tete = (f"sous les croissances à cheval, {round(100 * p)} % des {h['poses']} pieds posés des points hors du tour attendu à l'écart "
            f"de leur spire sont sur le tour de départ")
    suite = ("c'est le tour publié qui se contredit" if 4 * h["sur_le_depart"] >= 3 * h["poses"]
             else "c'est la surface de départ qui était déjà hors de son tour" if 4 * h["sur_le_depart"] <= h["poses"]
             else "l'un et l'autre")
    return {"decidable": True, "p": round(p, 4), "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    t0 = time.monotonic()
    r = m357.la_chaine_jugee(chainer=m358.la_chaine_qui_regrandit, en_plus=les_pieds_lus)
    d = {"la_question": __doc__.splitlines()[0], "les_constantes": {"le_minimum_de_pieds": LE_MINIMUM_DE_PIEDS},
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

    n = 10
    valide = np.ones((n, n), dtype=bool)
    semes = np.zeros((n, n), dtype=bool)
    semes[:4] = True
    dep = np.zeros((n, n, 3))
    dep[..., 0], dep[..., 1] = np.meshgrid(np.arange(n) * 5.0, np.arange(n) * 5.0)
    k = {"depuis": m356.DEPUIS_LA_CROISSANCE, "le_depart": {"la_nappe": dep, "valide": valide},
         "la_relance": {"la_nappe": dep + np.array([0.0, 0.0, 10.0]), "valide": valide, "les_semes": semes}}

    def comptes(dep_, arr, lv):
        pts = arr["la_nappe"].reshape(-1, 3)
        return {"les_points": pts, "les_normales": np.tile([0.0, 0.0, 1.0], (100, 1)), "les_mailles": np.arange(100),
                "en_face": np.ones(100, dtype=bool), "les_ecarts": [10.0] * 60 + [1.0] * 40}
    vus = []

    def poser(pts, nn):
        return [[-1] if i < 30 else [0] for i in range(len(pts))]

    def poser_les_pieds(p, nn, ok):
        vus.append((len(p), int(ok.sum())))
        return [[0] if i < 50 else [1] for i in range(len(p))]
    tous = lambda q, dep_: (q - np.array([0.0, 0.0, 10.0]), np.tile([0.0, 0.0, 1.0], (len(q), 1)), np.ones(len(q), dtype=bool))  # noqa: E731
    lu = les_pieds_lus(k, "m7", comptes, poser, poser_les_pieds, tous)
    v("★★★★ chaque point, par sa zone, ses tours, sa partie et les tours de son pied sur la surface de départ",
      lu["les_comptes"] == {"-1|à l'écart de la spire|semis|0": 30, "0|à l'écart de la spire|semis|0": 10,
                            "0|à l'écart de la spire|croissance|0": 10, "0|à l'écart de la spire|croissance|1": 10,
                            "0|près du départ|croissance|1": 40} and vus and vus[0][0] == 100, str((lu, vus)))
    un_sur_deux = lambda q, dep_: (np.zeros((len(q), 3)), np.zeros((len(q), 3)), np.arange(len(q)) % 2 == 0)  # noqa: E731
    sans = les_pieds_lus(k, "m7", comptes, poser, lambda p, nn, ok: [[0]] * len(p), un_sur_deux)
    v("★★★ un pied sans normale n'est pas posé", sum(n_ for c, n_ in sans["les_comptes"].items() if c.endswith("|?")) == 50, str(sans))
    reels = []
    avant = m348.les_pieds
    m348.les_pieds = lambda q, dep_: reels.append((len(q), dep_ is k["le_depart"])) or avant(q, dep_)
    try:
        les_pieds_lus(k, "m7", comptes, poser, poser_les_pieds)
    finally:
        m348.les_pieds = avant
    v("★★★ sans pieds donnés, ceux de 348 sur la surface de départ", reels == [(100, True)], str(reels))
    v("★★★ sous une spire gardée ou une relance, rien",
      les_pieds_lus(dict(k, depuis=m356.DEPUIS_LA_SPIRE), "m7", comptes, poser, poser_les_pieds) is None)
    s = {"le_tour_de_depart": 0, "en_plus": lu}
    p = les_pieds_de(s, -1)
    v("★★★★ les pieds des points à l'écart de la spire, posés hors de l'attendu puis sur l'attendu ; les autres zones ne comptent pas",
      p == {"hors": {"0": 20, "1": 10}, "attendu": {"0": 30}}, str(p))
    v("★★★ seulement une partie", les_pieds_de(s, -1, "semis") == {"hors": {"0": 10}, "attendu": {"0": 30}})
    v("★★★★ la part sur le tour de départ : parmi les pieds posés, sans les pieds sans normale ni les pieds posés nulle part",
      lambda: la_part_sur_le_depart({"0": 20, "1": 10, "?": 7, "": 5, "0,1": 4}, 0) == (24, 34))

    def saut(en_plus, cheval=True, rang=5):
        return {"le_rang": rang, "le_cote": "moins", "les_sauts": [{"la_justesse": "juste", "depuis": m356.DEPUIS_LA_CROISSANCE,
                                                                     "a_cheval": cheval, "le_tour_de_depart": -3, "en_plus": en_plus}]}
    ep = {"lecart_de_la_spire": 10.0, "les_comptes": {"-3|à l'écart de la spire|croissance|-3": 40, "-3|à l'écart de la spire|semis|-2": 20,
                                                       "-5|à l'écart de la spire|croissance|-2": 7, "-3|à l'écart de la spire|semis|?": 9,
                                                       "-3|à l'écart de la spire|semis|": 3,
                                                       "-4|à l'écart de la spire|croissance|-3": 90, "-4|à l'écart de la spire|semis|-2": 10}}
    bil = {}
    v("★★★★ le bilan : les croissances à cheval jugées de 361 seulement, l'au-delà compris, sans les pieds sans normale ni posés nulle "
      "part, et les autres pieds rangés par leur écart au tour de départ",
      lambda: bil.update(le_bilan([saut(ep), saut(ep, cheval=False), saut(ep, rang=2)])) or (
          bil["les_jugees"] == 1 and bil["hors"] == {"sur_le_depart": 40, "poses": 67}
          and bil["attendu"] == {"sur_le_depart": 90, "poses": 100} and bil["le_controle"]
          and bil["ailleurs_par_ecart_de_tour"] == {"[1]": 27}), str(bil))
    vus_p, avant_p, avant_t = [], m348.les_poses_des_pieds, dict(m361._LES_TOURS)
    m348.les_poses_des_pieds = lambda p_, n_, ok_, tours: vus_p.append((float(p_[0, 0]), dict(tours))) or (
        [["lus"]] * len(p_), [["posés"]] * len(p_))
    m361._LES_TOURS.clear()
    m361._LES_TOURS.update({"sonde": "les tours publiés"})
    try:
        un = les_pieds_lus(k, "m7", comptes, poser, None,
                           lambda q, dep_: (np.ones((len(q), 3)), np.ones((len(q), 3)), np.ones(len(q), dtype=bool)))
    finally:
        m348.les_poses_des_pieds = avant_p
        m361._LES_TOURS.clear()
        m361._LES_TOURS.update(avant_t)
    v("★★★★ sans pose donnée, les pieds sont posés par 348 au niveau 0, et c'est la pose, pas la lecture, qui est gardée",
      vus_p == [(m321.LE_FACTEUR, {"sonde": "les tours publiés"})] and all(c.endswith("|posés") for c in un["les_comptes"]),
      str((vus_p, un)))

    def d_(sur, poses, ok=True, rej=True):
        return {"les_pannes": [], "redonne_358": rej, "le_bilan": {"hors": {"sur_le_depart": sur, "poses": poses}, "le_controle": ok}}
    v("★★★★ la règle : les trois quarts, un quart, entre les deux",
      le_verdict(d_(75, 100))["lissue"].endswith("le tour publié qui se contredit")
      and le_verdict(d_(25, 100))["lissue"].endswith("déjà hors de son tour")
      and le_verdict(d_(50, 100))["lissue"].endswith("l'un et l'autre") and le_verdict(d_(74, 100))["lissue"].endswith("l'un et l'autre")
      and le_verdict(d_(26, 100))["lissue"].endswith("l'un et l'autre"))
    v("★★★ moins de 50 pieds, un contrôle tombé, une chaîne qui ne redonne pas 358 : indécidable",
      not le_verdict(d_(40, 49))["decidable"] and le_verdict(d_(40, 50))["decidable"]
      and not le_verdict(d_(75, 100, ok=False))["decidable"] and not le_verdict(d_(75, 100, rej=False))["decidable"])

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
