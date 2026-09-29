"""La nappe de m7, tirée sur PHercParis4 comme sur PHerc0358, au même pas de 9,6 µm, retrouve-t-elle le tracé humain, et ses spires suivantes les feuilles voisines ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UNE SEULE NAPPE DE m7 NE SOIT TIRÉE SUR PHercParis4. Ce qui était vu avant d'écrire : tout ce que
`296` à `320` publient, dont toute la série `300` à `320` sur PHerc0358, faite sans référent, et `R4-F490` : le tracé humain de
PHercParis4 est posé sur la face de sa feuille, de −16 à +12 voxels de 9,6 µm de son plus dense selon le bloc.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P118`. PHercParis4 publie la même prédiction, `m7`, au niveau 2 du volume, 9,6 µm, la
résolution de PHerc0358, et il a un tracé humain. La méthode de `300` y peut être jugée contre une réponse connue : si la nappe de `m7`
tombe sur le tracé humain, et sa spire suivante à un pas de lui, ce que la série a mesuré sans référent sur PHerc0358 a un appui.

## Ce qui est fait

- **Les graines** : huit sommets du segment humain réduit de `296` (le même que toute la série sur PHercParis4), pris sur une grille
  régulière de ses sommets valides, avec la normale du segment ; ramenés au niveau 2 (divisés par 4).
- **La nappe** : exactement celle de `300` (un plan de 65 × 65 points au pas de 10 voxels du niveau 2, le vote de `247` sur les plages de
  `m7`, ses spires suivantes de chaque côté), avec le pas du rouleau de PHercParis4, 18,02 voxels au niveau 2, à la place de celui de
  PHerc0358.
- **La comparaison** : les sommets du segment dans l'emprise du plan de la nappe (8 sommets de part et d'autre de la graine sur la
  grille du segment, soit la demi-largeur du plan, 320 voxels du niveau 2 ou 1280 de 2,4 µm, divisée par l'espacement de 160) ; pour
  chacun en face d'un point de la nappe (à au plus 40 voxels de 2,4 µm de côté), l'écart signé le long de la normale du segment, en
  voxels de 2,4 µm ; sur les seuls points de la nappe appuyés sur `m7`. Borner les sommets à l'emprise du plan, et non à la distance
  de la nappe, empêche qu'une autre partie du segment, loin en travers, compte comme en face.
- **Le pas** : celui de `300` est remplacé, le temps de la mesure, par 18,02 voxels, et la demi-portée de la recherche par un pas et
  demi de ce pas, comme dans `300`.

## Les issues

Par graine, **la nappe retrouve le tracé** si au moins 50 sommets lui font face, que l'écart médian est à au plus un quart de pas (18
voxels de 2,4 µm) et qu'au moins la moitié des sommets en face sont à un quart de pas ; **elle ne le retrouve pas** sinon ; **non lue**
sous 50 sommets en face. L'issue de la tranche : **sur k des huit graines, la nappe de m7 retrouve le tracé humain.**

## Rapporté à côté, qui ne décide rien

Pour chaque spire suivante, de chaque côté : l'écart médian au segment, en pas du rouleau, et la part des sommets en face à moins
d'un quart de pas du pas entier.

⚠ Ajouté après la première mesure, le 2026-09-29, sans toucher à la règle : par anneau de sommets autour de la graine (0 à 2, 3 à 5,
6 à 8), la part des sommets en face sur la feuille du tracé, la part à un pas entier, et l'écart du plan de `300` lui-même au segment ;
et l'histogramme des écarts. La première mesure rendait la nappe sur la feuille du tracé près de sa graine et loin de lui ailleurs.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : que la méthode vaille sur PHerc0358 aussi bien que sur PHercParis4, dont le scan et la feuille
diffèrent.

Usage :
    uv run python src/nappe/la_nappe_de_m7_retrouve_t_elle_le_trace_humain_de_paris4.py --verifier
    uv run python src/nappe/la_nappe_de_m7_retrouve_t_elle_le_trace_humain_de_paris4.py \\
        --json docs/mesures/la_nappe_de_m7_retrouve_t_elle_le_trace_humain_de_paris4.json
"""
from __future__ import annotations

import argparse
import contextlib
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
import le_pas_de_la_chaine_vient_il_de_m7_ou_du_pas_par_defaut as m316  # noqa: E402

LA_PREDICTION = ("PHercParis4/representations/predictions/surfaces/"
                 "20260411134726-surface-20260413222639-surface-m7-L2-th0.2.zarr")
LE_CACHE = RACINE / "data" / "nappe_paris4" / "m7"
LE_FACTEUR = 4.0
LE_PAS_L0 = 173.0 / 2.4                  # 72,08 voxels de 2,4 µm
LE_PAS_L2 = LE_PAS_L0 / LE_FACTEUR        # 18,02 voxels de 9,6 µm
LE_QUART = LE_PAS_L0 / 4.0                # 18,02 voxels de 2,4 µm
LE_LATERAL = 40.0
LES_GRAINES = 8
LE_MINIMUM = 50
LA_FENETRE = 8                            # sommets du segment, de part et d'autre de la graine
LES_ANNEAUX = ((0, 2), (3, 5), (6, 8))    # rapporté : distance à la graine, en sommets du segment
LES_BORNES = np.arange(-162.0, 163.0, 18.0)


def les_graines(points: np.ndarray, valide: np.ndarray, n_ok: np.ndarray, combien: int = LES_GRAINES) -> list[tuple[int, int]]:
    """Des sommets valides à normale connue, sur une grille régulière des rangées et colonnes, pris dans l'ordre et à distance du bord
    du segment (au moins 8 sommets)."""
    h, w = valide.shape
    ok = valide & n_ok
    interieur = np.zeros_like(ok)
    interieur[8:-8, 8:-8] = True
    ok &= interieur
    for d in range(3, 12):
        rs, cs = np.linspace(8, h - 9, d).round().astype(int), np.linspace(8, w - 9, d).round().astype(int)
        cand = [(int(r), int(c)) for r in rs for c in cs if ok[r, c]]
        if len(cand) >= combien:
            pas = len(cand) / combien
            return [cand[int(k * pas)] for k in range(combien)]
    return []


@contextlib.contextmanager
def le_rouleau_de_paris4():
    """Le pas de `300` et sa demi-portée, remplacés par ceux de PHercParis4 le temps d'un bloc, et rendus ensuite."""
    avant = m300.LA_DEMI_PORTEE
    m300.LA_DEMI_PORTEE = 1.5 * LE_PAS_L2
    try:
        with m316.le_pas_donne(LE_PAS_L2):
            yield
    finally:
        m300.LA_DEMI_PORTEE = avant


def la_fenetre(forme: tuple[int, int], i: int, j: int, demi: int = LA_FENETRE) -> np.ndarray:
    """Le masque des sommets du segment à au plus `demi` rangées et colonnes de la graine."""
    m = np.zeros(forme, dtype=bool)
    m[max(0, i - demi):i + demi + 1, max(0, j - demi):j + demi + 1] = True
    return m


def les_ecarts(ref: np.ndarray, ref_n: np.ndarray, nuage: np.ndarray, lateral: float = LE_LATERAL) -> np.ndarray:
    """L'écart signé, le long de la normale de chaque sommet du segment, au point du nuage le plus proche ; NaN pour un sommet
    qui n'est pas en face (écart latéral au-delà de `lateral`)."""
    from scipy.spatial import cKDTree

    if not len(ref) or not len(nuage):
        return np.full(len(ref), np.nan)
    _, idx = cKDTree(nuage).query(ref)
    delta = nuage[idx] - ref
    t = np.einsum("ij,ij->i", delta, ref_n)
    lat = np.linalg.norm(delta - t[:, None] * ref_n, axis=-1)
    return np.where(lat <= lateral, t, np.nan)


def par_anneau(t: np.ndarray, anneau: np.ndarray, plan: np.ndarray) -> list[dict]:
    """Rapporté, ne décide rien : par anneau de sommets autour de la graine, la part des sommets en face à un quart de pas du
    tracé, à un quart de pas d'un pas entier, et l'écart médian du plan de `300` lui-même au segment."""
    out = []
    for k, (a, b) in enumerate(LES_ANNEAUX):
        m = (anneau >= a) & (anneau <= b)
        x = t[m & np.isfinite(t)]
        pl = np.abs(plan[m & np.isfinite(plan)])
        e = {"lanneau": [a, b], "les_sommets_en_face": int(len(x)),
             "lecart_median_du_plan_voxels": round(float(np.median(pl)), 2) if len(pl) else None}
        if len(x):
            e["la_part_sur_la_feuille_du_trace"] = round(float((np.abs(x) <= LE_QUART).mean()), 4)
            e["la_part_a_un_pas"] = round(float((np.abs(np.abs(x) - LE_PAS_L0) <= LE_QUART).mean()), 4)
        out.append(e)
    return out


def lhistogramme(t: np.ndarray) -> list[int]:
    """Rapporté : les écarts des sommets en face, par tranches de 18 voxels de 2,4 µm, de −162 à +162."""
    h, _ = np.histogram(t[np.isfinite(t)], bins=LES_BORNES)
    return [int(x) for x in h]


def la_coincidence(t: np.ndarray, cible: float = 0.0) -> dict:
    """Ce que les écarts disent d'une surface censée être à `cible` voxels du segment."""
    t = t[np.isfinite(t)]
    if len(t) < LE_MINIMUM:
        return {"les_sommets_en_face": int(len(t)), "la_lecture": "non lue"}
    a = np.abs(np.abs(t) - cible) if cible else np.abs(t)
    med = float(np.median(t))
    part = float((a <= LE_QUART).mean())
    ok = (abs(abs(med) - cible) <= LE_QUART) and part >= 0.5
    return {"les_sommets_en_face": int(len(t)), "lecart_median_voxels": round(med, 2),
            "lecart_median_en_pas": round(med / LE_PAS_L0, 3), "la_part_a_un_quart_de_pas": round(part, 4),
            "la_lecture": "retrouve" if ok else "ne retrouve pas"}


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    lues = [g for g in d["les_graines"] if g["la_nappe"]["la_lecture"] != "non lue"]
    if not lues:
        return {"decidable": False, "lissue": "indécidable : aucune graine lue"}
    k = sum(1 for g in lues if g["la_nappe"]["la_lecture"] == "retrouve")
    return {"decidable": True, "k": k, "n": len(lues),
            "lissue": f"sur {k} des {len(lues)} graines, la nappe de m7 retrouve le tracé humain de PHercParis4"}


def mesurer() -> dict:
    import le_tour_produit_porte_t_il_le_texte_du_segment as j296
    from le_transfert_retrouve_t_il_la_spire_voisine import lecteur_du_depot
    from la_spire_voisine_est_elle_a_un_pas import les_normales, lire_tifxyz

    from zarr_depth import BUCKET, array_meta

    t0 = time.monotonic()
    seg, sok, esp = lire_tifxyz(j296.LE_DOSSIER / j296.LES_SURFACES[0] / "maillage")
    sn, snok = les_normales(seg, sok)
    pred = array_meta(f"{BUCKET}/{LA_PREDICTION}", 0, 120.0)
    lire_, stats = lecteur_du_depot(pred, LE_CACHE, "m7_L2", LA_PREDICTION, 0)
    graines = []
    for rang, (i, j) in enumerate(les_graines(seg, sok, snok), 1):
        g0 = seg[i, j] / LE_FACTEUR
        f = sok & snok & la_fenetre(sok.shape, i, j)
        ref, ref_n = seg[f], sn[f]
        ii, jj = np.nonzero(f)
        anneau = np.maximum(np.abs(ii - i), np.abs(jj - j))
        plan, _ = m300.le_plan(tuple(g0), tuple(sn[i, j]))
        t_plan = les_ecarts(ref, ref_n, plan.reshape(-1, 3) * LE_FACTEUR)
        with le_rouleau_de_paris4():
            r = m300.tirer_une_nappe(tuple(g0), tuple(sn[i, j]), (pred, lire_))
        e = {"le_rang": rang, "le_sommet": [i, j], "la_graine_l2": [round(float(x), 2) for x in g0],
             "les_sommets_de_la_fenetre": int(f.sum()), "la_part_appuyee": round(float(r["appui"].mean()), 4)}
        pts = r["la_nappe"][r["valide"] & r["appui"]] * LE_FACTEUR
        t = les_ecarts(ref, ref_n, pts)
        e["la_nappe"] = dict(la_coincidence(t), par_anneau=par_anneau(t, anneau, t_plan), lhistogramme=lhistogramme(t))
        for nom in ("plus", "moins"):
            s = r["les_sauts"][nom]
            sp = s["la_spire"][s["valide"] & s["appui"]] * LE_FACTEUR
            ts = les_ecarts(ref, ref_n, sp)
            e[f"la_spire_{nom}"] = dict(la_coincidence(ts, cible=LE_PAS_L0), la_part_appuyee=round(float(s["appui"].mean()), 4),
                                        lhistogramme=lhistogramme(ts))
        graines.append(e)
        print(json.dumps(e, ensure_ascii=False), flush=True)
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"la_prediction": LA_PREDICTION, "le_pas_l0_voxels": round(LE_PAS_L0, 3),
                            "le_pas_l2_voxels": round(LE_PAS_L2, 3), "le_quart_de_pas_l0_voxels": round(LE_QUART, 3),
                            "le_lateral_l0_voxels": LE_LATERAL, "le_minimum": LE_MINIMUM, "la_fenetre_sommets": LA_FENETRE,
                            "lespacement_du_segment": esp},
         "les_pannes": list(stats["pannes"]), "la_lecture_de_m7": {k: v for k, v in stats.items() if k != "pannes"},
         "les_graines": graines}
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

    v("★★★ le pas de PHercParis4 : 72,08 voxels de 2,4 µm, 18,02 au niveau 2", round(LE_PAS_L0, 2) == 72.08
      and round(LE_PAS_L2, 2) == 18.02)
    k = np.arange(-20, 21) * 20.0
    ref = np.stack(np.meshgrid(k, k, indexing="ij"), -1).reshape(-1, 2)
    ref = np.concatenate([ref, np.zeros((len(ref), 1))], axis=1)
    n = np.tile([0.0, 0.0, 1.0], (len(ref), 1))
    t = les_ecarts(ref, n, ref + np.array([0.0, 0.0, 10.0]))
    v("★★★★ l'écart signé : un nuage décalé de 10 le long de la normale", len(t) == len(ref) and np.allclose(t, 10.0))
    t = les_ecarts(ref, n, ref[:10] + np.array([0.0, 0.0, 10.0]))
    v("★★★★ seuls les sommets en face comptent", 10 <= int(np.isfinite(t).sum()) < len(ref))
    v("★★★ un sommet qui n'est pas en face ne compte pas dans la lecture",
      la_coincidence(np.concatenate([np.full(60, 0.0), np.full(60, np.nan)]))["les_sommets_en_face"] == 60)
    an = np.array([0, 2, 4, 4, 7, 8])
    pa = par_anneau(np.array([0.0, 5.0, 72.0, np.nan, -70.0, 40.0]), an, np.array([0.0, 1.0, 30.0, 30.0, 100.0, 120.0]))
    v("★★★ par anneau : sur la feuille près de la graine, à un pas plus loin, bornes comprises",
      pa[0]["les_sommets_en_face"] == 2 and pa[0]["la_part_sur_la_feuille_du_trace"] == 1.0
      and pa[1]["la_part_a_un_pas"] == 1.0 and pa[1]["les_sommets_en_face"] == 1 and pa[2]["la_part_a_un_pas"] == 0.5
      and pa[2]["lecart_median_du_plan_voxels"] == 110.0, str(pa))
    v("★★ l'histogramme ignore les sommets qui ne sont pas en face", sum(lhistogramme(np.array([0.0, np.nan, 100.0]))) == 2)
    c = la_coincidence(np.full(100, 12.0))
    v("★★★★ à 12 voxels, la nappe retrouve le tracé", c["la_lecture"] == "retrouve")
    v("★★★★ à un demi-pas, elle ne le retrouve pas", la_coincidence(np.full(100, 36.0))["la_lecture"] == "ne retrouve pas")
    v("★★★ une médiane juste mais six sommets sur dix loin : ne retrouve pas",
      la_coincidence(np.concatenate([np.full(30, -40.0), np.full(40, 0.0), np.full(30, 40.0)]))["la_lecture"]
      == "ne retrouve pas")
    v("★★★★ une spire à un pas du tracé, de chaque signe", la_coincidence(np.full(100, -70.0), cible=LE_PAS_L0)["la_lecture"]
      == "retrouve" and la_coincidence(np.full(100, 75.0), cible=LE_PAS_L0)["la_lecture"] == "retrouve")
    v("★★★ la moitié à 10, la moitié à 30 : la médiane, 20, dépasse le quart de pas",
      la_coincidence(np.concatenate([np.full(50, 10.0), np.full(50, 30.0)]))["la_lecture"] == "ne retrouve pas")
    v("★★★ sous 50 sommets en face : non lue", la_coincidence(np.full(49, 0.0))["la_lecture"] == "non lue")
    ok = np.ones((40, 30), dtype=bool)
    gs = les_graines(np.zeros((40, 30, 3)), ok, ok)
    v("★★★ huit graines, loin du bord, distinctes", len(gs) == 8 and len(set(gs)) == 8
      and all(8 <= i < 32 and 8 <= j < 22 for i, j in gs), str(gs))
    f = la_fenetre((40, 30), 10, 12)
    v("★★★ la fenêtre : 17 × 17 sommets autour de la graine, rognée au bord", int(f.sum()) == 17 * 17
      and int(la_fenetre((40, 30), 2, 12).sum()) == 11 * 17)
    v("★★★ la fenêtre couvre la demi-largeur du plan de 300", LA_FENETRE == round((m300.LE_COTE_DU_PLAN // 2)
      * m300.LE_PAS_DU_PLAN * LE_FACTEUR / 160.0))
    pas0, portee0 = m300.LE_PAS_0358, m300.LA_DEMI_PORTEE
    with le_rouleau_de_paris4():
        dedans = (m300.LE_PAS_0358, m300.LA_DEMI_PORTEE)
    v("★★★★ le pas et la demi-portée de PHercParis4 le temps du bloc, rendus ensuite",
      dedans == (LE_PAS_L2, 1.5 * LE_PAS_L2) and (m300.LE_PAS_0358, m300.LA_DEMI_PORTEE) == (pas0, portee0))
    vd = le_verdict({"les_graines": [{"la_nappe": {"la_lecture": "retrouve"}}, {"la_nappe": {"la_lecture": "non lue"}},
                                     {"la_nappe": {"la_lecture": "ne retrouve pas"}}]})
    v("★★★ l'issue : k des graines lues", vd["k"] == 1 and vd["n"] == 2)

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
