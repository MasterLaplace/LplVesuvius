"""Une relance qui fait croître la nappe depuis la spire entière, chaque point posé gardant sa feuille, garde-t-elle la justesse de la chaîne sans relance en lui rendant sa surface ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UNE SEULE NAPPE NE SOIT RELANCÉE DEPUIS UNE SPIRE. Ce qui était vu avant d'écrire : tout ce que
`296` à `332` publient, dont `R4-F516` (sans relance, la chaîne descend six tours publiés en médiane sur PHercParis4 et ne se trompe de
tour qu'une fois) et `R4-F517` (relancée en une nappe qui croît depuis le point central de la spire, elle garde sa surface mais descend
5,5 tours en médiane et se trompe quatre fois ; sur PHerc0358 elle tient 2 sauts en médiane contre 1).

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P129`. La relance de `331` fait croître une nappe neuve depuis un seul point de la spire :
tout le reste du plan est reposé par la croissance, qui peut passer d'une feuille à la voisine là où la spire avait une lacune, et
atteindre de l'autre côté une région que la spire avait posée sur la bonne feuille. Une relance qui sème chaque point posé de la spire
sur sa propre feuille, et ne fait croître que ce qui manque, ne peut plus y repasser.

## Ce qui est fait

- **Les graines, la nappe, le saut, le plan de la relance** : ceux de `331`, sans rien y changer. Le plan est centré sur le point posé de
  la spire le plus proche du barycentre, perpendiculaire à sa normale, et `m7` est lu le long de sa normale comme `305` le lit.
- **Les semis** : chaque point posé de la spire tombe dans une maille du plan ; celui qui tombe le plus près de son centre y est gardé.
  La maille prend la feuille de `m7` la plus proche du décalage de ce point, à au plus un quart de pas ; au-delà, elle n'est pas semée.
- **La croissance** : celle de `305`, partie de toutes les mailles semées à la fois, dans l'ordre de la grille. Aucune maille semée n'est
  reposée, et aucun point n'est posé sans être appuyé sur `m7`.
- **Ce qui est jugé** : comme `331`, la descente de `330` sur les tours `5753_0` à `5753_-7` pour PHercParis4, et la tenue de `328` pour
  PHerc0358.

## Les issues

L'issue de la tranche : **relancée depuis sa spire, la chaîne descend h tours publiés en médiane sur PHercParis4 et se trompe f fois,
contre 6 et 1 sans relance, et tient h0 sauts en médiane sur PHerc0358, contre 1** ; et, déclaré avant : **elle garde la justesse et rend
la surface** si h ≥ 6, f ≤ 1 et h0 > 1 ; **elle perd la justesse** si h < 6 ou f > 1 ; **elle garde la justesse sans rendre la surface**
sinon. f compte les côtés dont la descente s'arrête sur un saut faux, sur toutes les graines.

## Rapporté à côté, qui ne décide rien

La part du plan posée par chaque nappe relancée, et combien de ses mailles sont semées depuis la spire.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : sur quelle feuille tombe une nappe relancée de PHerc0358 ; ni si une relance qui ne pose que
la spire, sans croître au-delà, ferait mieux.

Usage :
    uv run python src/nappe/la_relance_partie_de_la_spire_entiere_garde_t_elle_la_justesse.py --verifier
    uv run python src/nappe/la_relance_partie_de_la_spire_entiere_garde_t_elle_la_justesse.py \\
        --json docs/mesures/la_relance_partie_de_la_spire_entiere_garde_t_elle_la_justesse.json
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

import une_nappe_tiree_de_m7_suit_elle_sa_feuille as m300  # noqa: E402
import une_nappe_qui_refuse_de_changer_de_feuille_suit_elle_encore_sa_feuille as m305  # noqa: E402
import la_chaine_dune_seule_feuille_suit_elle_sa_feuille_sur_quatre_spires as m306  # noqa: E402
import la_nappe_de_m7_retrouve_t_elle_le_trace_humain_de_paris4 as m321  # noqa: E402
import la_nappe_qui_croit_tient_elle_le_trace_humain_de_paris4 as m322  # noqa: E402
import une_chaine_relancee_a_chaque_tour_descend_elle_plus_loin as m331  # noqa: E402

LA_DESCENTE_SANS_RELANCE = 6.0
LES_SAUTS_FAUX_SANS_RELANCE = 1
LA_TENUE_SANS_RELANCE = 1.0


def les_cibles(spire: np.ndarray, valide: np.ndarray, grille: np.ndarray, n: np.ndarray,
               pas: float = m300.LE_PAS_DU_PLAN) -> np.ndarray:
    """Pour chaque maille du plan `grille`, le décalage le long de `n` du point posé de la spire qui y tombe le plus près de son centre ;
    NaN là où aucun n'y tombe. À égalité, le premier dans l'ordre de la spire."""
    forme = grille.shape[:2]
    cible = np.full(forme, np.nan)
    pts = spire[valide]
    if not len(pts):
        return cible
    lignes = (grille[1, 0] - grille[0, 0]) / pas
    colonnes = (grille[0, 1] - grille[0, 0]) / pas
    d = pts - grille[0, 0]
    a, b, h = d @ lignes / pas, d @ colonnes / pas, d @ n
    ia, ib = np.rint(a).astype(np.int64), np.rint(b).astype(np.int64)
    dans = (ia >= 0) & (ia < forme[0]) & (ib >= 0) & (ib < forme[1])
    if not dans.any():
        return cible
    k = np.flatnonzero(dans)
    ecart = (a[k] - ia[k]) ** 2 + (b[k] - ib[k]) ** 2
    ordre = k[np.lexsort((np.arange(len(k)), ecart))]
    _, premiers = np.unique(ia[ordre] * forme[1] + ib[ordre], return_index=True)
    gardes = ordre[premiers]
    cible[ia[gardes], ib[gardes]] = h[gardes]
    return cible


def la_nappe_de_la_spire(spire: np.ndarray, valide: np.ndarray, graine_xyz, normale_xyz, lire_valeurs,
                         tolerance: float = m305.LA_TOLERANCE) -> dict:
    """Le plan de la relance de `331`, les feuilles de `m7` de chacun de ses points ; chaque maille où tombe un point posé de la spire
    prend la feuille la plus proche de son décalage, à au plus `tolerance` ; puis la croissance de `305` depuis toutes ces mailles."""
    grille, n = m300.le_plan(graine_xyz, normale_xyz)
    forme = grille.shape[:2]
    p = grille.reshape(-1, 3)
    t = np.arange(-np.floor(m300.LA_DEMI_PORTEE), np.floor(m300.LA_DEMI_PORTEE) + 1.0)
    idx = np.floor((p[:, None, :] + t[None, :, None] * n[None, None, :])[..., ::-1]).astype(np.int64)
    centres = m300.les_plages(lire_valeurs(idx) > 0, t)
    cible = les_cibles(spire, valide, grille, n).ravel()
    dec = np.full(forme, np.nan)
    pose = np.zeros(forme, dtype=bool)
    for k in np.flatnonzero(np.isfinite(cible)):
        c = centres[k]
        if not len(c):
            continue
        m = int(np.argmin(np.abs(c - cible[k])))
        if abs(c[m] - cible[k]) <= tolerance:
            dec.flat[k], pose.flat[k] = c[m], True
    semes = pose.copy()
    dec, pose = m305.etendre(centres, forme, dec, pose, tolerance)
    nappe = (p + np.nan_to_num(dec.ravel())[:, None] * n[None, :]).reshape(forme + (3,))
    return {"la_nappe": nappe, "valide": pose, "le_decalage": dec, "les_semis": int(semes.sum()), "les_semes": semes,
            "les_mailles_touchees": int(np.isfinite(cible).sum())}


def la_nappe_de_la_spire_de_paris4(spire, valide, graine_l2, normale, lire_valeurs) -> dict:
    """La relance depuis la spire, au pas de PHercParis4 : sa tolérance et la demi-portée de son plan."""
    with m321.le_rouleau_de_paris4():
        return la_nappe_de_la_spire(spire, valide, graine_l2, normale, lire_valeurs, tolerance=m322.LA_TOLERANCE_L2)


def les_sauts_faux(graines: list[dict]) -> int:
    return sum(1 for g in graines for c in g["les_cotes"].values() if c["larret"] == "un saut faux")


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    gs = d["les_graines"]["PHercParis4"]
    p4 = [g["la_descente"] for g in gs if g["le_tour_touche"]]
    p0 = [c["tient"] for c in d["les_cotes"]["PHerc0358"]]
    if not p4 or not p0:
        return {"decidable": False, "lissue": "indécidable : rien à comparer"}
    h, h0, f = float(np.median(p4)), float(np.median(p0)), les_sauts_faux(gs)
    f_ = lambda x, un, plusieurs: f"{x:g}".replace(".", ",") + (f" {un}" if x <= 1 else f" {plusieurs}")  # noqa: E731
    tete = (f"relancée depuis sa spire, la chaîne descend {f_(h, 'tour publié', 'tours publiés')} en médiane sur PHercParis4 et se "
            f"trompe {f} fois, contre 6 et 1 sans relance, et tient {f_(h0, 'saut', 'sauts')} en médiane sur PHerc0358, contre 1")
    if h < LA_DESCENTE_SANS_RELANCE or f > LES_SAUTS_FAUX_SANS_RELANCE:
        suite = "elle perd la justesse"
    elif h0 > LA_TENUE_SANS_RELANCE:
        suite = "elle garde la justesse et rend la surface"
    else:
        suite = "elle garde la justesse sans rendre la surface"
    return {"decidable": True, "h": h, "h0": h0, "f": f, "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    t0 = time.monotonic()
    d = m331.mesurer(
        relancer4=lambda lv: (lambda p_, n_, s_, o_: la_nappe_de_la_spire_de_paris4(s_, o_, p_, n_, lv)),
        relancer0=lambda lv: (lambda p_, n_, s_, o_: la_nappe_de_la_spire(s_, o_, tuple(p_), tuple(n_), lv)),
        avec_la_spire=True)
    d["la_question"] = __doc__.splitlines()[0]
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

    haut = np.array([0.0, 0.0, 1.0])
    grille, n = m300.le_plan((500.0, 300.0, 120.0), haut)
    spire = grille + 7.0 * n
    valide = np.zeros(grille.shape[:2], dtype=bool)
    valide[10:20, 30:40] = True
    c = les_cibles(spire, valide, grille, n)
    v("★★★★ chaque point posé de la spire donne son décalage à sa maille, et aucune autre maille n'en reçoit",
      np.array_equal(np.isfinite(c), valide) and np.allclose(c[valide], 7.0))
    col = (grille[0, 1] - grille[0, 0]) / m300.LE_PAS_DU_PLAN
    deux = np.stack([grille[5, 5] + 1.0 * col + 7.0 * n, grille[5, 5] - 4.0 * col + 9.0 * n, grille[5, 5] + 900.0 * col])
    c = les_cibles(deux, np.ones(3, dtype=bool), grille, n)
    v("★★★★ deux points dans une maille : celui le plus près de son centre, pas le premier ; un point hors du plan n'y tombe pas",
      np.isfinite(c).sum() == 1 and c[5, 5] == 7.0, str(c[np.isfinite(c)]))
    deux = np.stack([grille[5, 5] - 4.0 * col + 9.0 * n, grille[5, 5] + 1.0 * col + 7.0 * n])
    v("★★★ le même, dans l'autre ordre", les_cibles(deux, np.ones(2, dtype=bool), grille, n)[5, 5] == 7.0)

    def deux_feuilles(idx):
        """S1 en z = 132 sauf dans la bande 540 ≤ x < 560, S2 en z = 136 à partir de x = 540 : S2 fait le pont par-dessus la lacune de
        S1, à 4 voxels d'elle."""
        z, x = idx[..., 0], idx[..., 2]
        s1 = (np.abs(z - 132) <= 1) & ((x < 540) | (x >= 560))
        s2 = (np.abs(z - 136) <= 1) & (x >= 540)
        return (s1 | s2).astype(float)

    graine = (500.0, 300.0, 132.0)
    g2, _ = m300.le_plan(graine, haut)
    sp = g2.copy()
    ok = (g2[..., 0] < 540) | (g2[..., 0] >= 560)
    loin = g2[..., 0] >= 560
    seul = m305.la_nappe_croissante(graine, haut, deux_feuilles)
    toute = la_nappe_de_la_spire(sp, ok, graine, haut, deux_feuilles)
    part = lambda r: float((r["valide"] & loin & (np.abs(r["le_decalage"]) < 0.5)).sum() / loin.sum())  # noqa: E731
    v("★★★★★ au-delà de la lacune, la nappe semée depuis la spire reste sur S1, là où la nappe partie d'un seul point passe sur S2",
      part(toute) > 0.99 and part(seul) < 0.01, f"{part(toute)} {part(seul)}")
    v("★★★★ la lacune est reposée par la croissance, sur S2, qui y est seule", toute["valide"][~ok].all()
      and np.allclose(toute["le_decalage"][~ok], 4.0))
    v("★★★ toutes les mailles de la spire sont semées", toute["les_semis"] == int(ok.sum()) == toute["les_mailles_touchees"]
      and np.array_equal(toute["les_semes"], ok))
    v("★★★ les semis rendus sont ceux d'avant la croissance, pas les points posés après",
      not np.array_equal(toute["les_semes"], toute["valide"]))
    valide = np.zeros(g2.shape[:2], dtype=bool)
    valide[30:35, 30:35] = True
    petite = la_nappe_de_la_spire(sp, valide & ok, graine, haut, deux_feuilles)
    v("★★★★ une petite spire est prolongée par la croissance : la nappe pose bien plus que ce qu'elle sème",
      petite["les_semis"] == 25 and petite["valide"].sum() > 1000, str(petite["valide"].sum()))
    haute = la_nappe_de_la_spire(sp, ok, (500.0, 300.0, 124.0), haut,
                                 lambda idx: ((np.abs(idx[..., 0] - 120) <= 1) | (np.abs(idx[..., 0] - 132) <= 1)).astype(float))
    v("★★★★★ chaque maille prend la feuille la plus proche de son point de la spire, pas celle la plus proche du plan",
      haute["les_semis"] == int(ok.sum()) and np.allclose(haute["le_decalage"][haute["valide"]], 8.0),
      str(haute["les_semis"]))
    loin_de_tout = la_nappe_de_la_spire(sp + np.array([0.0, 0.0, 10.0]), ok, graine, haut,
                                        lambda idx: ((idx[..., 0] - 132) % 20 == 0).astype(float))
    v("★★★★ une spire qui ne tombe sur aucune feuille à un quart de pas ne sème rien, et rien n'est posé",
      loin_de_tout["les_semis"] == 0 and not loin_de_tout["valide"].any())
    v("★★★ la tolérance est celle qu'on lui donne", la_nappe_de_la_spire(
        sp + np.array([0.0, 0.0, 10.0]), ok, graine, haut, lambda idx: ((idx[..., 0] - 132) % 20 == 0).astype(float),
        tolerance=10.0)["les_semis"] > 0)

    recus = []
    feuilles_tous_les_20 = lambda idx: ((idx[..., 0] - 100) % 20 == 0).astype(float)  # noqa: E731

    def relancer(p_, n_, s_, o_):
        recus.append((s_, o_))
        return la_nappe_de_la_spire(s_, o_, tuple(p_), tuple(n_), feuilles_tous_les_20)

    plan0, _ = m300.le_plan((500.0, 300.0, 100.0), haut)
    ch = m331.la_chaine_relancee({"la_nappe": plan0, "valide": np.ones(plan0.shape[:2], dtype=bool)}, 1.0, relancer,
                                 lambda s_, o_: m306.le_saut_croissant(s_, o_, 1.0, feuilles_tous_les_20),
                                 sauts=2, avec_la_spire=True)
    v("★★★★ la relance reçoit la spire du saut et ses points posés", len(recus) == 2
      and np.array_equal(recus[0][0], ch[0]["le_saut"]["la_spire"]) and np.array_equal(recus[0][1], ch[0]["le_saut"]["valide"]))
    v("★★★ la chaîne relancée depuis la spire monte d'une feuille à chaque saut", len(ch) == 2 and np.allclose(
        ch[1]["la_relance"]["la_nappe"][ch[1]["la_relance"]["valide"]][:, 2], 140.0), str(len(ch)))

    g_ = lambda h, t, arrets=("un tour manqué",): {"la_descente": h, "le_tour_touche": t,  # noqa: E731
                                                   "les_cotes": {f"c{i}": {"larret": a} for i, a in enumerate(arrets)}}
    c_ = lambda h: {"tient": h}  # noqa: E731
    base = {"les_pannes": []}
    vd = le_verdict(dict(base, les_graines={"PHercParis4": [g_(6, True), g_(7, True, ("un saut faux", "aucun tour touché"))]},
                         les_cotes={"PHerc0358": [c_(2), c_(3)]}))
    v("★★★★ h ≥ 6, un saut faux, h0 > 1 : elle garde la justesse et rend la surface",
      vd["lissue"].endswith("elle garde la justesse et rend la surface") and vd["f"] == 1, vd["lissue"])
    vd = le_verdict(dict(base, les_graines={"PHercParis4": [g_(6, True, ("un saut faux",)), g_(7, True, ("un saut faux",))]},
                         les_cotes={"PHerc0358": [c_(4)]}))
    v("★★★★ deux sauts faux : elle perd la justesse, même à h ≥ 6", vd["lissue"].endswith("elle perd la justesse"), vd["lissue"])
    vd = le_verdict(dict(base, les_graines={"PHercParis4": [g_(5, True), g_(5, True)]}, les_cotes={"PHerc0358": [c_(4)]}))
    v("★★★★ h < 6 : elle perd la justesse", vd["lissue"].endswith("elle perd la justesse"))
    vd = le_verdict(dict(base, les_graines={"PHercParis4": [g_(6, True)]}, les_cotes={"PHerc0358": [c_(1), c_(1)]}))
    v("★★★ h0 = 1 : elle garde la justesse sans rendre la surface",
      vd["lissue"].endswith("elle garde la justesse sans rendre la surface"))
    v("★★★ les graines qui ne touchent pas de tour ne comptent pas dans h", le_verdict(dict(
        base, les_graines={"PHercParis4": [g_(6, True), g_(0, False)]}, les_cotes={"PHerc0358": [c_(2)]}))["h"] == 6.0)
    v("★★★ indécidable si une lecture échoue", not le_verdict({"les_pannes": ["x"]})["decidable"])

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
