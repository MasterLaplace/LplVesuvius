"""Un saut qui croît parti de la distance médiane que sa nappe voit, et qui refuse de partir d'un bloc de m7, pose-t-il au pas plus souvent sur PHerc0358, sans tomber moins souvent sur le tour suivant de PHercParis4 ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UN SEUL SAUT PARTI DE LA MÉDIANE NE SOIT TIRÉ. Ce qui était vu avant d'écrire : tout ce que `296` à
`326` publient, dont `R4-F506` (sur PHercParis4, le saut qui croît de `306` tombe sur le tour suivant du segment sur 4 graines sur 8),
`R4-F508` (il pose au pas sur 5 côtés sur 16 de PHerc0358), `R4-F509` (son départ, pris d'un seul point, s'écarte de la médiane et
déplace le saut, sur la graine 4 de PHerc0358 et la graine 8 côté moins de PHercParis4) et `R4-F511` (trois nappes de PHerc0358 sont
posées dans un bloc de `m7`).

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P125`. Les deux corrections se lisent sans référent : partir de la distance que la nappe
voit le plus souvent plutôt que de ce qu'un point a vu, et refuser de partir d'un bloc. PHercParis4 dit si elles gardent ce qui tombait
juste ; PHerc0358, si elles posent au pas plus souvent.

## Ce qui est fait

- **Les graines et la nappe** : celles de `325`, sans rien y changer.
- **Le refus des blocs** : la règle de `326` ; une nappe posée dans un bloc de `m7` n'a pas de saut.
- **Le saut parti de la médiane** : le saut qui croît de `306` dont le départ est le point le plus proche du centre dont la feuille
  suivante est à au plus un quart de pas de la médiane de celles que tous les points de la nappe voient ; le reste sans changement.
- **Le témoin** : le saut de `306`, tel quel, dans la même mesure, sans refus des blocs.
- **Ce qui est jugé** : sur PHercParis4, si l'une des deux spires retrouve le tour suivant du segment (la règle de `323`) ; sur
  PHerc0358, si chaque côté pose au pas (la règle de `324`).

## Les issues

L'issue de la tranche : **le saut parti de la médiane tombe sur le tour suivant de PHercParis4 sur k graines, contre k0 pour le témoin,
et pose au pas sur m côtés de PHerc0358, contre m0** ; et, déclaré avant : **il pose au pas plus souvent sans tomber moins souvent** si
k ≥ k0 et m > m0 ; **il tombe moins souvent** si k < k0 ; **il ne change rien** sinon. Indécidable si une lecture échoue, si une nappe de
PHerc0358 ne redonne pas `305`, ou si le témoin ne redonne pas `323` et `324`.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : sur quelle feuille tombent les spires posées au pas de PHerc0358.

Usage :
    uv run python src/nappe/un_saut_parti_de_la_mediane_tombe_t_il_plus_souvent_au_pas.py --verifier
    uv run python src/nappe/un_saut_parti_de_la_mediane_tombe_t_il_plus_souvent_au_pas.py \\
        --json docs/mesures/un_saut_parti_de_la_mediane_tombe_t_il_plus_souvent_au_pas.json
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

import lalignement_des_profils_dit_il_si_une_premiere_surface_suit_sa_feuille as m299  # noqa: E402
import une_nappe_tiree_de_m7_suit_elle_sa_feuille as m300  # noqa: E402
import les_nappes_de_m7_suivent_elles_leur_feuille_sur_des_graines_neuves as m301  # noqa: E402
import une_nappe_qui_refuse_de_changer_de_feuille_suit_elle_encore_sa_feuille as m305  # noqa: E402
import la_chaine_dune_seule_feuille_suit_elle_sa_feuille_sur_quatre_spires as m306  # noqa: E402
import la_nappe_de_m7_retrouve_t_elle_le_trace_humain_de_paris4 as m321  # noqa: E402
import la_nappe_qui_croit_tient_elle_le_trace_humain_de_paris4 as m322  # noqa: E402
import la_spire_qui_croit_tombe_t_elle_sur_le_tour_suivant_du_segment as m323  # noqa: E402
import le_saut_qui_croit_pose_t_il_au_pas_sur_les_deux_rouleaux as m324  # noqa: E402
import la_nappe_plate_est_elle_posee_dans_un_bloc_de_m7 as m326  # noqa: E402

LES_SAUTS = (("le_temoin", False), ("parti_de_la_mediane", True))


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("les_nappes_de_0358_se_redonnent"):
        return {"decidable": False, "lissue": "indécidable : une nappe de PHerc0358 ne redonne pas celle de 305"}
    c = d["les_comptes"]
    if not d.get("le_temoin_redonne"):
        return {"decidable": False, "lissue": f"indécidable : le témoin ne redonne pas 323 et 324 ({c})"}
    k, k0, m, m0 = c["k"], c["k0"], c["m"], c["m0"]
    tete = (f"le saut parti de la médiane tombe sur le tour suivant de PHercParis4 sur {k} graines, contre {k0} pour le témoin, et pose "
            f"au pas sur {m} côtés de PHerc0358, contre {m0}")
    if k < k0:
        suite = "il tombe moins souvent"
    elif m > m0:
        suite = "il pose au pas plus souvent sans tomber moins souvent"
    else:
        suite = "il ne change rien"
    return {"decidable": True, "k": k, "k0": k0, "m": m, "m0": m0, "lissue": f"{tete} ; {suite}"}


def les_comptes(d: dict) -> dict:
    p4, p0 = d["les_graines"]["PHercParis4"], d["les_graines"]["PHerc0358"]
    tombe = lambda g, s: g["les_sauts"][s]["la_lecture"] == "tombe sur le tour suivant"  # noqa: E731
    au_pas = lambda g, s: sum(1 for c in ("plus", "moins") if g["les_sauts"][s]["les_cotes"][c]["pose_au_pas"])  # noqa: E731
    return {"k": sum(1 for g in p4 if tombe(g, "parti_de_la_mediane")), "k0": sum(1 for g in p4 if tombe(g, "le_temoin")),
            "m": sum(au_pas(g, "parti_de_la_mediane") for g in p0), "m0": sum(au_pas(g, "le_temoin") for g in p0)}


def les_deux_sauts(nappe: dict, lire_valeurs, pas: float, tolerance: float, refusee: bool) -> dict:
    """Le témoin et le saut parti de la médiane, de chaque côté ; le second n'est pas tiré d'une nappe refusée."""
    out = {}
    for nom, median in LES_SAUTS:
        cotes = {}
        for c, cote in m306.LES_COTES:
            if median and refusee:
                cotes[c] = None
                continue
            cotes[c] = m306.le_saut_croissant(nappe["la_nappe"], nappe["valide"], cote, lire_valeurs, tolerance=tolerance,
                                              au_median=median)
        out[nom] = cotes
    return out


def resumer(sauts: dict, pas: float) -> dict:
    vide = {"la_part_du_plan": 0.0, "le_pas_median_en_pas": None, "pose_au_pas": False}
    return {c: (vide if s is None else m324.le_saut(s["le_pas"], s["valide"], pas)) for c, s in sauts.items()}


def mesurer() -> dict:
    import le_tour_produit_porte_t_il_le_texte_du_segment as j296
    from le_transfert_retrouve_t_il_la_spire_voisine import lecteur_du_depot, lire_les_valeurs
    from la_spire_voisine_est_elle_a_un_pas import les_normales, lire_tifxyz

    from zarr_depth import BUCKET, array_meta

    t0 = time.monotonic()
    graines = {"PHerc0358": [], "PHercParis4": []}
    lecture = {}
    publie = {g["le_rang"]: g["les_points_poses"] for g in json.loads(m324.CE_QUE_305_A_PUBLIE.read_text())["les_graines"]}
    pred = array_meta(f"{BUCKET}/{m299.LA_PREDICTION_0358}", 0, 120.0)
    lire_, stats = lecteur_du_depot(pred, m300.LE_CACHE_M7, "m7_L0", m299.LA_PREDICTION_0358, 0)
    lv = lambda idx: lire_les_valeurs(idx, pred, lire_)  # noqa: E731
    d301 = {tuple(g["la_graine"]): g["le_rang"]
            for g in json.loads(m305.CE_QUE_301_A_PUBLIE.read_text())["le_rouleau"]["les_graines"]}
    se_redonnent = True
    for g in m301.les_graines_neuves():
        cle = (g["x"], g["y"], g["z"])
        rang = d301[cle]
        nz, ny, nx = g["normale_zyx"]
        r = m305.la_nappe_croissante(cle, (nx, ny, nz), lv)
        se_redonnent &= int(r["valide"].sum()) == publie.get(rang)
        plage = m326.lire_les_plages(r, lv, m300.LE_PAS_0358)
        refusee = plage["la_lecture"] == "dans un bloc"
        sauts = les_deux_sauts(r, lv, m300.LE_PAS_0358, m305.LA_TOLERANCE, refusee)
        e = {"le_rang": rang, "refusee": refusee, "la_plage_en_pas": plage["la_longueur_mediane_en_pas"],
             "les_sauts": {nom: {"les_cotes": resumer(sauts[nom], m300.LE_PAS_0358)} for nom, _ in LES_SAUTS}}
        graines["PHerc0358"].append(e)
        print("PHerc0358", json.dumps(e, ensure_ascii=False), flush=True)
    pannes = list(stats["pannes"])
    lecture["PHerc0358"] = {k: v for k, v in stats.items() if k != "pannes"}

    seg, sok, _ = lire_tifxyz(j296.LE_DOSSIER / j296.LES_SURFACES[0] / "maillage")
    sn, snok = les_normales(seg, sok)
    ok = sok & snok
    pred = array_meta(f"{BUCKET}/{m321.LA_PREDICTION}", 0, 120.0)
    lire4, stats4 = lecteur_du_depot(pred, m321.LE_CACHE, "m7_L2", m321.LA_PREDICTION, 0)
    lv4 = lambda idx: m300.lire_m7(idx, (pred, lire4))  # noqa: E731
    for rang, (i, j) in enumerate(m321.les_graines(seg, sok, snok), 1):
        paires, _ = m323.le_tour_suivant(seg, ok, ok & m321.la_fenetre(ok.shape, i, j))
        tour, tour_n = seg[paires[:, 0], paires[:, 1]], sn[paires[:, 0], paires[:, 1]]
        r = m322.la_nappe_de_paris4(seg[i, j] / m321.LE_FACTEUR, sn[i, j], lv4)
        with m321.le_rouleau_de_paris4():
            plage = m326.lire_les_plages(r, lv4, m321.LE_PAS_L2)
            refusee = plage["la_lecture"] == "dans un bloc"
            sauts = les_deux_sauts(r, lv4, m321.LE_PAS_L2, m322.LA_TOLERANCE_L2, refusee)
        e = {"le_rang": rang, "refusee": refusee, "la_plage_en_pas": plage["la_longueur_mediane_en_pas"], "les_sauts": {}}
        for nom, _ in LES_SAUTS:
            lectures = {"la_nappe": "non lue"}
            spires = {}
            for c in ("plus", "moins"):
                s = sauts[nom][c]
                if s is None:
                    spires[c] = {"les_sommets_en_face": 0, "la_lecture": "non lue"}
                else:
                    t = m321.les_ecarts(tour, tour_n, s["la_spire"][s["valide"]] * m321.LE_FACTEUR)
                    spires[c] = m321.la_coincidence(t)
                lectures[f"la_spire_{c}"] = spires[c]["la_lecture"]
            e["les_sauts"][nom] = {"les_cotes": resumer(sauts[nom], m321.LE_PAS_L2), "les_spires": spires,
                                   "la_lecture": m323.la_lecture_de_la_graine(lectures)}
        graines["PHercParis4"].append(e)
        print("PHercParis4", json.dumps(e, ensure_ascii=False), flush=True)
    pannes += list(stats4["pannes"])
    lecture["PHercParis4"] = {k: v for k, v in stats4.items() if k != "pannes"}
    d = {"la_question": __doc__.splitlines()[0], "les_pannes": pannes, "la_lecture_de_m7": lecture,
         "les_nappes_de_0358_se_redonnent": bool(se_redonnent), "les_graines": graines}
    d["les_comptes"] = les_comptes(d)
    d["le_temoin_redonne"] = d["les_comptes"]["k0"] == 4 and d["les_comptes"]["m0"] == 5
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

    # Une nappe plane de 9 × 9 points au pas 10, et deux feuilles de m7 au-dessus : à 20 voxels partout, et à 57 sous le seul point
    # le plus proche du centre qui en voie une. Le départ de 306 prend 57 ; celui de la médiane, 20, et pose les 48 points qui ont une
    # normale (les 49 de l'intérieur de la grille, moins le centre, qui ne voit que 57).
    grille = np.zeros((9, 9, 3))
    for a in range(9):
        for b in range(9):
            grille[a, b] = (100.0 + 10.0 * b, 100.0 + 10.0 * a, 100.0)
    nappe = {"la_nappe": grille, "valide": np.ones((9, 9), dtype=bool)}

    def m7(idx):
        z, y, x = idx[..., 0], idx[..., 1], idx[..., 2]
        pres = (z == 100) | (z == 120)
        loin = (z == 157) & (x == 140) & (y == 140)
        trou = (z == 120) & (x == 140) & (y == 140)
        return (pres & ~trou) | loin

    s306 = m306.le_saut_croissant(grille, nappe["valide"], 1.0, m7)
    smed = m306.le_saut_croissant(grille, nappe["valide"], 1.0, m7, au_median=True)
    v("★★★★ le départ de 306 prend la feuille qu'un seul point voit, à 57 voxels", s306["le_depart"] == [4, 4]
      and abs(float(np.nanmedian(s306["le_pas"][s306["valide"]])) - 57.0) < 1.0, str(s306["le_depart"]))
    v("★★★★ le départ de la médiane prend celle que tous voient, à 20 voxels", smed["le_depart"] != [4, 4]
      and abs(float(np.nanmedian(smed["le_pas"][smed["valide"]])) - 20.0) < 1.0 and int(smed["valide"].sum()) == 48,
      f"{smed['le_depart']} {int(smed['valide'].sum())}")
    deux = resumer(les_deux_sauts(nappe, m7, 20.0, 5.0, refusee=False)["parti_de_la_mediane"], 20.0)
    v("★★★★ les deux sauts : celui de la médiane pose au pas là où le témoin pose loin", deux["plus"]["pose_au_pas"]
      and deux["plus"]["le_pas_median_en_pas"] == 1.0, str(deux["plus"]))
    sauts = les_deux_sauts(nappe, m7, 20.0, 5.0, refusee=True)
    v("★★★ une nappe refusée n'a pas de saut parti de la médiane, mais garde son témoin",
      sauts["parti_de_la_mediane"]["plus"] is None and sauts["le_temoin"]["plus"] is not None)
    v("★★★ un saut refusé ne pose rien", resumer({"plus": None}, 20.0)["plus"]["pose_au_pas"] is False)
    g = lambda t_, m_, a_, b_: {"les_sauts": {"le_temoin": {"la_lecture": t_, "les_cotes": {"plus": {"pose_au_pas": a_},  # noqa: E731
                                                                                             "moins": {"pose_au_pas": False}}},
                                              "parti_de_la_mediane": {"la_lecture": m_, "les_cotes": {"plus": {"pose_au_pas": b_},
                                                                                                       "moins": {"pose_au_pas": b_}}}}}
    d = {"les_graines": {"PHercParis4": [g("tombe sur le tour suivant", "tombe sur le tour suivant", False, False)],
                         "PHerc0358": [g("non lue", "non lue", True, True)]}}
    c = les_comptes(d)
    v("★★★ les comptes : k, k0, m, m0", c == {"k": 1, "k0": 1, "m": 2, "m0": 1}, str(c))
    base = {"les_pannes": [], "les_nappes_de_0358_se_redonnent": True, "le_temoin_redonne": True}
    v("★★★★ k ≥ k0 et m > m0 : il pose au pas plus souvent",
      le_verdict(dict(base, les_comptes={"k": 4, "k0": 4, "m": 6, "m0": 5}))["lissue"].endswith("sans tomber moins souvent"))
    v("★★★★ k < k0 : il tombe moins souvent, quoi que fasse m",
      le_verdict(dict(base, les_comptes={"k": 3, "k0": 4, "m": 9, "m0": 5}))["lissue"].endswith("il tombe moins souvent"))
    v("★★★ m = m0 : il ne change rien",
      le_verdict(dict(base, les_comptes={"k": 5, "k0": 4, "m": 5, "m0": 5}))["lissue"].endswith("il ne change rien"))
    v("★★★ un témoin qui ne redonne pas 323 et 324 : indécidable",
      not le_verdict(dict(base, le_temoin_redonne=False, les_comptes={"k": 5, "k0": 3, "m": 5, "m0": 5}))["decidable"])

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
