"""Une chaîne qui croît, relancée à chaque saut en une nappe entière sur la feuille que le saut a atteinte, descend-elle plus loin les tours publiés de PHercParis4, et tient-elle plus de sauts sur PHerc0358 ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UNE SEULE CHAÎNE RELANCÉE NE SOIT TIRÉE. Ce qui était vu avant d'écrire : tout ce que `296` à `330`
publient, dont `R4-F516` (sans relance, la chaîne descend six tours publiés en médiane sur PHercParis4, et s'arrête quand sa spire
rétrécit à quelques pour cent du plan) et `R4-F513` (sur PHerc0358, elle tient un saut au pas en médiane, sa spire tombant sous 10 % du
plan).

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P128`. Le saut qui croît pose sa spire sur la grille de la surface d'où il part, et un point
qui ne l'a pas suivie est perdu pour tous les sauts d'après : la spire ne peut que rétrécir. Une nappe qui croît, lancée sur la feuille que
le saut a atteinte, repart d'un plan entier.

## Ce qui est fait

- **Les graines, la nappe et le saut** : ceux de `330` sur PHercParis4, et ceux de `328` sur PHerc0358 (ses cinq côtés), sans rien y
  changer.
- **La relance** : après chaque saut, le point posé de la spire le plus proche du barycentre de ses points posés, avec sa normale, devient
  la graine d'une nappe qui croît de `305` (au pas de chaque rouleau) ; le saut suivant part de cette nappe. Une spire sans point posé à
  normale connue arrête la chaîne.
- **Ce qui est jugé** : sur PHercParis4, la descente de `330` sur la suite des surfaces relancées, contre les tours `5753_0` à `5753_-7` ;
  sur PHerc0358, la tenue de `328` (le saut pose au pas, et la nappe relancée n'est pas dans un bloc).

## Les issues

L'issue de la tranche : **relancée, la chaîne descend h' tours publiés en médiane sur PHercParis4, contre 6 sans relance, et tient h0'
sauts en médiane sur PHerc0358, contre 1** ; et, déclaré avant : **la relance prolonge la chaîne** si h0' > 1 et h' ≥ 6 ; **elle la
dégrade** si h' < 6 ; **elle ne change rien** sinon.

## Rapporté à côté, qui ne décide rien

La part du plan posée par chaque spire et par chaque nappe relancée.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : sur quelle feuille tombe une nappe relancée de PHerc0358.

Usage :
    uv run python src/nappe/une_chaine_relancee_a_chaque_tour_descend_elle_plus_loin.py --verifier
    uv run python src/nappe/une_chaine_relancee_a_chaque_tour_descend_elle_plus_loin.py \\
        --json docs/mesures/une_chaine_relancee_a_chaque_tour_descend_elle_plus_loin.json
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
import le_saut_qui_croit_pose_t_il_au_pas_sur_les_deux_rouleaux as m324  # noqa: E402
import la_nappe_plate_est_elle_posee_dans_un_bloc_de_m7 as m326  # noqa: E402
import combien_de_sauts_la_chaine_qui_croit_tient_elle_au_pas as m328  # noqa: E402
import la_chaine_qui_croit_tombe_t_elle_sur_les_tours_publies as m329  # noqa: E402
import jusqua_quel_tour_publie_la_chaine_qui_croit_descend_elle as m330  # noqa: E402

LES_SAUTS = 8


def la_graine_de_la_relance(spire: np.ndarray, valide: np.ndarray):
    """Le point posé de la spire, à normale connue, le plus proche du barycentre de ses points posés, et sa normale ; None s'il n'y en a
    pas."""
    from la_spire_voisine_est_elle_a_un_pas import les_normales

    nn, nok = les_normales(spire, valide)
    m = valide & nok
    if not m.any():
        return None
    pts = spire[m]
    k = int(np.argmin(np.linalg.norm(pts - pts.mean(axis=0), axis=1)))
    return pts[k], nn[m][k]


def la_chaine_relancee(nappe: dict, cote: float, relancer, sauter, sauts: int = LES_SAUTS, avec_la_spire: bool = False) -> list[dict]:
    """Jusqu'à `sauts` sauts, chacun parti de la nappe relancée sur la spire du précédent ; `sauter(surface, valide)` rend le saut,
    `relancer(point, normale)` la nappe. Avec `avec_la_spire`, écrit pour `333`, `relancer(point, normale, spire, valide)` reçoit
    aussi la spire entière et ses points posés."""
    surf, ok = nappe["la_nappe"], nappe["valide"]
    out = []
    for _ in range(sauts):
        s = sauter(surf, ok)
        g = la_graine_de_la_relance(s["la_spire"], s["valide"]) if s["valide"].any() else None
        if g is None:
            out.append({"le_saut": s, "la_relance": None})
            break
        r = relancer(*g, s["la_spire"], s["valide"]) if avec_la_spire else relancer(*g)
        out.append({"le_saut": s, "la_relance": r})
        if not r["valide"].any():
            break
        surf, ok = r["la_nappe"], r["valide"]
    return out


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    p4 = [g["la_descente"] for g in d["les_graines"]["PHercParis4"] if g["le_tour_touche"]]
    p0 = [c["tient"] for c in d["les_cotes"]["PHerc0358"]]
    if not p4 or not p0:
        return {"decidable": False, "lissue": "indécidable : rien à comparer"}
    h, h0 = float(np.median(p4)), float(np.median(p0))
    f_ = lambda x, un, plusieurs: f"{x:g}".replace(".", ",") + (f" {un}" if x <= 1 else f" {plusieurs}")  # noqa: E731
    tete = (f"relancée, la chaîne descend {f_(h, 'tour publié', 'tours publiés')} en médiane sur PHercParis4, contre 6 sans relance, et "
            f"tient {f_(h0, 'saut', 'sauts')} en médiane sur PHerc0358, contre 1")
    if h < 6:
        suite = "elle la dégrade"
    elif h0 > 1:
        suite = "la relance prolonge la chaîne"
    else:
        suite = "elle ne change rien"
    return {"decidable": True, "h": h, "h0": h0, "lissue": f"{tete} ; {suite}"}


def mesurer(relancer4=None, relancer0=None, avec_la_spire: bool = False, lire_la_spire: bool = False,
            rouleaux: tuple = ("PHercParis4", "PHerc0358"), observer=None) -> dict:
    """La mesure de `331`. Avec `relancer4(lire_valeurs)` et `relancer0(lire_valeurs)`, écrits pour `333`, les relances de
    PHercParis4 et de PHerc0358 sont fabriquées par l'appelant, et reçoivent la spire si `avec_la_spire`. Avec `lire_la_spire`, écrit
    pour `334`, PHercParis4 rapporte aussi ce que les tours publiés disent de la nappe de départ, de chaque spire, et de la part de
    chaque nappe relancée que la croissance a posée hors de ses semis ; PHerc0358 n'est mesuré que s'il est dans `rouleaux`. Avec
    `observer(rang, cote, h, k)`, écrit pour `336`, chaque saut `h` d'un côté de PHercParis4 est montré à l'appelant, et ce qu'il rend
    est ajouté à son relevé."""
    import le_tour_produit_porte_t_il_le_texte_du_segment as j296
    from le_transfert_retrouve_t_il_la_spire_voisine import lecteur_du_depot, lire_les_valeurs
    from la_spire_voisine_est_elle_a_un_pas import les_normales, lire_tifxyz

    from zarr_depth import BUCKET, array_meta

    t0 = time.monotonic()
    tours = {r: m329.lire_un_tour(r, m330.LES_TOURS) for r in m330.LES_TOURS}
    seg, sok, _ = lire_tifxyz(j296.LE_DOSSIER / j296.LES_SURFACES[0] / "maillage")
    sn, snok = les_normales(seg, sok)
    pred = array_meta(f"{BUCKET}/{m321.LA_PREDICTION}", 0, 120.0)
    lire4, stats4 = lecteur_du_depot(pred, m321.LE_CACHE, "m7_L2", m321.LA_PREDICTION, 0)
    lv4 = lambda idx: m300.lire_m7(idx, (pred, lire4))  # noqa: E731
    graines = {"PHercParis4": []}
    for rang, (i, j) in enumerate(m321.les_graines(seg, sok, snok), 1):
        r = m322.la_nappe_de_paris4(seg[i, j] / m321.LE_FACTEUR, sn[i, j], lv4)
        lect_nappe = m329.les_lectures(r["la_nappe"][r["valide"]] * m321.LE_FACTEUR, tours)
        e = {"le_rang": rang, "les_cotes": {}}
        for nom, cote in m306.LES_COTES:
            def sauter(s_, o_, cote=cote):
                with m321.le_rouleau_de_paris4():
                    return m306.le_saut_croissant(s_, o_, cote, lv4, tolerance=m322.LA_TOLERANCE_L2)
            rel4 = (lambda p_, n_: m322.la_nappe_de_paris4(p_, n_, lv4)) if relancer4 is None else relancer4(lv4)
            chaine = la_chaine_relancee(r, cote, rel4, sauter, avec_la_spire=avec_la_spire)
            surfaces = [{t: x["la_lecture"] for t, x in lect_nappe.items()}]
            detail = []
            for h, k in enumerate(chaine, 1):
                rl = k["la_relance"]
                vus = dict(observer(rang, nom, h, k) or {}) if observer is not None else {}
                if lire_la_spire:
                    sp = m329.les_lectures(k["le_saut"]["la_spire"][k["le_saut"]["valide"]] * m321.LE_FACTEUR, tours)
                    vus["les_tours_de_la_spire"] = {str(t): x["la_lecture"] for t, x in sp.items()}
                    if rl is not None and "les_semes" in rl:
                        cr = m329.les_lectures(rl["la_nappe"][rl["valide"] & ~rl["les_semes"]] * m321.LE_FACTEUR, tours)
                        vus["les_tours_de_la_croissance"] = {str(t): x["la_lecture"] for t, x in cr.items()}
                if rl is None:
                    surfaces.append({t: "non lue" for t in tours})
                    detail.append({"la_part_de_la_spire": round(float(k["le_saut"]["valide"].mean()), 4), "la_part_relancee": None,
                                   **vus})
                    continue
                lect = m329.les_lectures(rl["la_nappe"][rl["valide"]] * m321.LE_FACTEUR, tours)
                surfaces.append({t: x["la_lecture"] for t, x in lect.items()})
                detail.append({"la_part_de_la_spire": round(float(k["le_saut"]["valide"].mean()), 4),
                               "la_part_relancee": round(float(rl["valide"].mean()), 4),
                               "les_tours": {str(t): x["la_lecture"] for t, x in lect.items()},
                               **({"les_semis": rl["les_semis"]} if "les_semis" in rl else {}), **vus})
            e["les_cotes"][nom] = dict({"les_surfaces": detail}, **m330.la_descente(surfaces))
            if lire_la_spire:
                e["les_cotes"][nom]["les_tours_de_la_nappe"] = {str(t): x for t, x in surfaces[0].items()}
        e["la_descente"] = max(c["la_descente"] for c in e["les_cotes"].values())
        e["le_tour_touche"] = any(c["le_tour_de_depart"] is not None for c in e["les_cotes"].values())
        graines["PHercParis4"].append(e)
        print("PHercParis4", json.dumps({"le_rang": rang, "la_descente": e["la_descente"],
                                          "par_cote": {c: (v["le_tour_de_depart"], v["la_descente"], v["larret"])
                                                       for c, v in e["les_cotes"].items()}}, ensure_ascii=False), flush=True)
    pannes = list(stats4["pannes"])

    cotes0 = []
    if "PHerc0358" not in rouleaux:
        d = {"la_question": __doc__.splitlines()[0], "les_constantes": {"les_sauts": LES_SAUTS}, "les_pannes": pannes,
             "la_lecture_de_m7": {"PHercParis4": {k: v for k, v in stats4.items() if k != "pannes"}},
             "les_graines": graines, "les_cotes": {"PHerc0358": cotes0}}
        d["le_verdict"] = le_verdict(d)
        d["les_secondes"] = round(time.monotonic() - t0, 1)
        return d
    d324 = json.loads(m328.CE_QUE_324_A_PUBLIE.read_text())
    a_suivre = {(c["le_rang"], c["le_cote"]) for c in d324["les_cotes"]["PHerc0358"] if c["le_saut"]["pose_au_pas"]}
    pred0 = array_meta(f"{BUCKET}/{m299.LA_PREDICTION_0358}", 0, 120.0)
    lire0, stats0 = lecteur_du_depot(pred0, m300.LE_CACHE_M7, "m7_L0", m299.LA_PREDICTION_0358, 0)
    lv0 = lambda idx: lire_les_valeurs(idx, pred0, lire0)  # noqa: E731
    d301 = {tuple(g["la_graine"]): g["le_rang"]
            for g in json.loads(m305.CE_QUE_301_A_PUBLIE.read_text())["le_rouleau"]["les_graines"]}
    for g in m301.les_graines_neuves():
        cle = (g["x"], g["y"], g["z"])
        rang = d301[cle]
        if not any((rang, c) in a_suivre for c, _ in m306.LES_COTES):
            continue
        nz, ny, nx = g["normale_zyx"]
        r = m305.la_nappe_croissante(cle, (nx, ny, nz), lv0)
        for nom, cote in m306.LES_COTES:
            if (rang, nom) not in a_suivre:
                continue
            rel0 = ((lambda p_, n_: m305.la_nappe_croissante(tuple(p_), tuple(n_), lv0)) if relancer0 is None
                    else relancer0(lv0))
            chaine = la_chaine_relancee(r, cote, rel0, lambda s_, o_, cote=cote: m306.le_saut_croissant(s_, o_, cote, lv0),
                                        avec_la_spire=avec_la_spire)
            sauts = []
            for k in chaine:
                e_ = m324.le_saut(k["le_saut"]["le_pas"], k["le_saut"]["valide"], m300.LE_PAS_0358)
                rl = k["la_relance"]
                if rl is None or not rl["valide"].any():
                    e_.update({"la_part_relancee": None, "la_plage_en_pas": None, "tient": False})
                else:
                    plage = m326.lire_les_plages(rl, lv0, m300.LE_PAS_0358)
                    e_.update({"la_part_relancee": round(float(rl["valide"].mean()), 4),
                               "la_plage_en_pas": plage["la_longueur_mediane_en_pas"],
                               "tient": bool(e_["pose_au_pas"] and plage["la_lecture"] != "dans un bloc"),
                               **({"les_semis": rl["les_semis"]} if "les_semis" in rl else {})})
                sauts.append(e_)
            e = {"le_rang": rang, "le_cote": nom, "les_sauts": sauts, "tient": m328.combien(sauts)}
            cotes0.append(e)
            print("PHerc0358", json.dumps({"le_rang": rang, "le_cote": nom, "tient": e["tient"]}, ensure_ascii=False),
                  [(s["la_part_du_plan"], s["le_pas_median_en_pas"], s["la_part_relancee"]) for s in sauts], flush=True)
    pannes += list(stats0["pannes"])
    d = {"la_question": __doc__.splitlines()[0], "les_constantes": {"les_sauts": LES_SAUTS},
         "les_pannes": pannes, "la_lecture_de_m7": {"PHercParis4": {k: v for k, v in stats4.items() if k != "pannes"},
                                                    "PHerc0358": {k: v for k, v in stats0.items() if k != "pannes"}},
         "les_graines": graines, "les_cotes": {"PHerc0358": cotes0}}
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

    grille = np.zeros((9, 9, 3))
    for a in range(9):
        for b in range(9):
            grille[a, b] = (100.0 + 10.0 * b, 100.0 + 10.0 * a, 120.0)
    valide = np.zeros((9, 9), dtype=bool)
    valide[1:7, 1:4] = True
    g = la_graine_de_la_relance(grille, valide)
    v("★★★★ la graine de la relance : le point posé à normale connue le plus proche du barycentre, pas le premier", g is not None
      and np.allclose(g[0], (120.0, 130.0, 120.0)) and abs(abs(g[1][2]) - 1.0) < 1e-9, str(g))
    v("★★★ une spire sans point à normale connue n'a pas de relance",
      la_graine_de_la_relance(grille, np.eye(9, dtype=bool)) is None)
    feuilles = lambda idx: (idx[..., 0] - 100) % 20 == 0  # noqa: E731
    nappe = {"la_nappe": grille - np.array([0.0, 0.0, 20.0]), "valide": np.ones((9, 9), dtype=bool)}
    appels = []

    def relancer(p_, n_):
        appels.append(tuple(np.round(p_, 1)))
        r = m305.la_nappe_croissante(tuple(p_), tuple(n_), feuilles)
        return r

    departs = []

    def sauter(s_, o_):
        departs.append(s_)
        return m306.le_saut_croissant(s_, o_, 1.0, feuilles)

    ch = la_chaine_relancee(nappe, 1.0, relancer, sauter, sauts=3)
    v("★★★★ chaque saut part de la nappe relancée, pas de la spire", len(departs) == 3
      and np.array_equal(departs[1], ch[0]["la_relance"]["la_nappe"]) and not np.array_equal(departs[1], ch[0]["le_saut"]["la_spire"]))
    v("★★★★ trois sauts, chacun relancé en une nappe entière sur la feuille suivante", len(ch) == 3 and len(appels) == 3
      and all(k["la_relance"]["valide"].mean() > 0.9 for k in ch) and [a[2] for a in appels] == [120.0, 140.0, 160.0], str(appels))
    vide = lambda idx: idx[..., 0] == 80  # noqa: E731
    ch = la_chaine_relancee(nappe, 1.0, relancer, lambda s_, o_: m306.le_saut_croissant(s_, o_, 1.0, vide), sauts=3)
    v("★★★ un saut qui ne pose rien arrête la chaîne, sans relance", len(ch) == 1 and ch[0]["la_relance"] is None)
    g_ = lambda h, t: {"la_descente": h, "le_tour_touche": t}  # noqa: E731
    c_ = lambda h: {"tient": h}  # noqa: E731
    base = {"les_pannes": []}
    vd = le_verdict(dict(base, les_graines={"PHercParis4": [g_(6, True), g_(7, True)]}, les_cotes={"PHerc0358": [c_(2), c_(3)]}))
    v("★★★★ h' ≥ 6 et h0' > 1 : la relance prolonge", vd["lissue"].endswith("la relance prolonge la chaîne"), vd["lissue"])
    vd = le_verdict(dict(base, les_graines={"PHercParis4": [g_(5, True), g_(5, True)]}, les_cotes={"PHerc0358": [c_(4)]}))
    v("★★★★ h' < 6 : elle la dégrade, quoi que fasse PHerc0358", vd["lissue"].endswith("elle la dégrade"))
    vd = le_verdict(dict(base, les_graines={"PHercParis4": [g_(6, True)]}, les_cotes={"PHerc0358": [c_(1), c_(1)]}))
    v("★★★ h0' = 1 : elle ne change rien", vd["lissue"].endswith("elle ne change rien"))
    v("★★★ les graines qui ne touchent pas de tour ne comptent pas", le_verdict(dict(
        base, les_graines={"PHercParis4": [g_(6, True), g_(0, False)]}, les_cotes={"PHerc0358": [c_(2)]}))["h"] == 6.0)

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
