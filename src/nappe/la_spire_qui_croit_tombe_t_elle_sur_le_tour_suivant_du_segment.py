"""La spire suivante de la nappe qui croît, tirée sur PHercParis4 par le saut qui croît de 306, tombe-t-elle sur le segment là où il repasse un tour plus loin ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UNE SEULE SPIRE QUI CROÎT NE SOIT TIRÉE SUR PHercParis4. Ce qui était vu avant d'écrire : tout ce
que `296` à `322` publient, dont `R4-F504` (la nappe qui croît de `305` tient la feuille du tracé humain jusqu'au bord sur 5 graines sur
8) et `R4-F505` (sur la graine 4, elle part à −46,84 voxels du tracé). ⚠ Et une exploration de la seule géométrie du segment, hors de
ce dépôt et sans lire `m7` : pour les sommets du segment autour des huit graines, le vis-à-vis de `296` (le sommet du segment le plus
proche en 3D à plus de 30 mailles sur la surface) est à 47 à 146 voxels de 2,4 µm, un tour plus loin ; et autour de la graine 4, il
est à −36 à −54 voxels le long de la normale, là où la nappe qui croît s'est posée. La lecture de la nappe elle-même contre ce tour est
donc en partie connue pour la graine 4 ; celle des spires ne l'est pour aucune graine.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P121`. Le segment fait plus d'un tour : en face de ses sommets, un tour plus loin, passe un
autre de ses propres sommets. Là, la spire suivante d'une nappe posée sur le tracé a une réponse connue. C'est la chaîne, et plus
seulement la première surface, jugée contre un tracé humain.

## Ce qui est fait

- **Les graines et la nappe** : les huit graines de `321` et la nappe qui croît de `322`, sans rien y changer.
- **Les spires** : de chaque côté, le saut qui croît de `306`, sans en changer une règle, au pas de PHercParis4 (sa tolérance d'un
  quart de pas, 4,51 voxels du niveau 2, et trois pas de recherche) : le départ prend la première feuille de `m7` après la sienne, puis
  la croissance de `305` ; aucun point n'est posé sans `m7`.
- **Le tour suivant** : pour chaque sommet du segment dans la fenêtre de `321` autour de la graine, son vis-à-vis par la règle de `296`,
  sans rien y changer ; l'ensemble de ces vis-à-vis, avec leurs normales, est le tour suivant.
- **La comparaison** : celle de `321`, sur les sommets du tour suivant : l'écart signé de chacun à la surface comparée, le long de sa
  normale, en face à au plus 40 voxels de côté.

## Les issues

Par graine et par surface (la nappe, la spire plus, la spire moins), **elle retrouve le tour suivant** si au moins 50 de ses sommets lui
font face, que l'écart médian est à au plus un quart de pas et qu'au moins la moitié des sommets en face sont à un quart de pas ; **elle
ne le retrouve pas** sinon ; **non lue** sous 50 sommets en face. Par graine, **la chaîne tombe sur le tour suivant** si l'une des deux
spires le retrouve. L'issue de la tranche : **sur k des huit graines, la spire suivante de la nappe qui croît tombe sur le tour suivant
du segment.**

## Rapporté à côté, qui ne décide rien

La distance médiane d'un sommet à son vis-à-vis ; la part posée de chaque spire ; la lecture de la nappe elle-même contre le tour
suivant, qui ne devrait pas le retrouver là où elle retrouve le tracé : si elle le retrouvait aussi, la comparaison ne séparerait pas
deux tours.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : ce que vaut la chaîne au-delà d'un saut, ni sur PHerc0358.

Usage :
    uv run python src/nappe/la_spire_qui_croit_tombe_t_elle_sur_le_tour_suivant_du_segment.py --verifier
    uv run python src/nappe/la_spire_qui_croit_tombe_t_elle_sur_le_tour_suivant_du_segment.py \\
        --json docs/mesures/la_spire_qui_croit_tombe_t_elle_sur_le_tour_suivant_du_segment.json
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
import la_chaine_dune_seule_feuille_suit_elle_sa_feuille_sur_quatre_spires as m306  # noqa: E402
import la_nappe_de_m7_retrouve_t_elle_le_trace_humain_de_paris4 as m321  # noqa: E402
import la_nappe_qui_croit_tient_elle_le_trace_humain_de_paris4 as m322  # noqa: E402

LES_SURFACES = ("la_nappe", "la_spire_plus", "la_spire_moins")


def le_tour_suivant(seg: np.ndarray, ok: np.ndarray, fenetre: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Les indices (rangée, colonne) des vis-à-vis de `296` des sommets de la fenêtre, sans doublon, dans l'ordre de la grille ; et
    la distance en 3D de chaque sommet de la fenêtre à son vis-à-vis."""
    import le_tour_produit_porte_t_il_le_texte_du_segment as j296

    fi, fj = np.nonzero(fenetre)
    if not len(fi):
        return np.zeros((0, 2), dtype=int), np.zeros(0)
    lignes = np.arange(fi.min(), fi.max() + 1)
    colonnes = np.arange(fj.min(), fj.max() + 1)
    masque = np.zeros_like(ok)
    masque[fenetre] = True
    fl, fc, ecart = j296.les_vis_a_vis(seg, ok, seg, masque, lignes, colonnes)
    connu = np.isfinite(fl)
    paires = np.unique(np.stack([fl[connu], fc[connu]], -1).astype(int), axis=0)
    return paires, ecart[connu]


def la_lecture_de_la_graine(lectures: dict) -> str:
    """La chaîne tombe sur le tour suivant si l'une des deux spires le retrouve ; non lue si aucune des deux n'est lue."""
    spires = [lectures[s] for s in ("la_spire_plus", "la_spire_moins")]
    if "retrouve" in spires:
        return "tombe sur le tour suivant"
    return "non lue" if all(x == "non lue" for x in spires) else "ne tombe pas sur le tour suivant"


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    gs = d["les_graines"]
    if not gs:
        return {"decidable": False, "lissue": "indécidable : aucune graine"}
    k = sum(1 for g in gs if g["la_lecture"] == "tombe sur le tour suivant")
    return {"decidable": True, "k": k, "n": len(gs),
            "lissue": f"sur {k} des {len(gs)} graines, la spire suivante de la nappe qui croît tombe sur le tour suivant du segment"}


def mesurer() -> dict:
    import le_tour_produit_porte_t_il_le_texte_du_segment as j296
    from le_transfert_retrouve_t_il_la_spire_voisine import lecteur_du_depot
    from la_spire_voisine_est_elle_a_un_pas import les_normales, lire_tifxyz

    from zarr_depth import BUCKET, array_meta

    t0 = time.monotonic()
    seg, sok, esp = lire_tifxyz(j296.LE_DOSSIER / j296.LES_SURFACES[0] / "maillage")
    sn, snok = les_normales(seg, sok)
    ok = sok & snok
    pred = array_meta(f"{BUCKET}/{m321.LA_PREDICTION}", 0, 120.0)
    lire_, stats = lecteur_du_depot(pred, m321.LE_CACHE, "m7_L2", m321.LA_PREDICTION, 0)
    lv = lambda idx: m300.lire_m7(idx, (pred, lire_))  # noqa: E731
    graines = []
    for rang, (i, j) in enumerate(m321.les_graines(seg, sok, snok), 1):
        g0 = seg[i, j] / m321.LE_FACTEUR
        paires, dist = le_tour_suivant(seg, ok, ok & m321.la_fenetre(ok.shape, i, j))
        tour, tour_n = seg[paires[:, 0], paires[:, 1]], sn[paires[:, 0], paires[:, 1]]
        nappe = m322.la_nappe_de_paris4(g0, sn[i, j], lv)
        surfaces = {"la_nappe": (nappe["la_nappe"], nappe["valide"])}
        parts = {}
        with m321.le_rouleau_de_paris4():
            for nom, cote in (("la_spire_plus", 1.0), ("la_spire_moins", -1.0)):
                s = m306.le_saut_croissant(nappe["la_nappe"], nappe["valide"], cote, lv, tolerance=m322.LA_TOLERANCE_L2)
                surfaces[nom] = (s["la_spire"], s["valide"])
                parts[nom] = round(float(s["valide"].mean()), 4)
        e = {"le_rang": rang, "le_sommet": [i, j], "les_sommets_du_tour_suivant": int(len(paires)),
             "la_distance_mediane_au_vis_a_vis_voxels": round(float(np.median(dist)), 2) if len(dist) else None,
             "les_parts_posees": parts}
        lectures = {}
        for nom in LES_SURFACES:
            pts, val = surfaces[nom]
            t = m321.les_ecarts(tour, tour_n, pts[val] * m321.LE_FACTEUR)
            e[nom] = dict(m321.la_coincidence(t), lhistogramme=m321.lhistogramme(t))
            lectures[nom] = e[nom]["la_lecture"]
        e["la_lecture"] = la_lecture_de_la_graine(lectures)
        graines.append(e)
        print(json.dumps(e, ensure_ascii=False), flush=True)
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"la_tolerance_l2_voxels": round(m322.LA_TOLERANCE_L2, 3),
                            "le_quart_de_pas_l0_voxels": round(m321.LE_QUART, 3), "lespacement_du_segment": esp},
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

    # Un segment synthétique de deux tours : deux bandes planes de 40 × 50 sommets espacés de 160 voxels, comme le segment réduit,
    # à 70 voxels l'une de l'autre en z ; la seconde tourne dans l'autre sens sur la grille, comme un tour d'enroulement.
    h, w = 100, 40
    seg = np.zeros((h, w, 3))
    for a in range(h):
        for b in range(w):
            if a < 50:
                seg[a, b] = (b * 160.0, a * 160.0, 0.0)
            else:
                seg[a, b] = (b * 160.0, (99 - a) * 160.0, 70.0)
    ok = np.ones((h, w), dtype=bool)
    fen = np.zeros_like(ok)
    fen[20:30, 15:25] = True
    paires, dist = le_tour_suivant(seg, ok, fen)
    v("★★★★ le tour suivant : les vis-à-vis de la fenêtre sont sur la seconde bande, à 70 voxels",
      len(paires) > 0 and (paires[:, 0] >= 50).all() and np.allclose(dist, 70.0), f"{len(paires)} {dist[:3]}")
    seg3 = seg.copy()
    seg3[..., :2] *= 50.0 / 160.0
    paires3, dist3 = le_tour_suivant(seg3, ok, fen)
    v("★★★★ un voisin de la même feuille, plus proche que le tour suivant, n'est pas un vis-à-vis",
      len(paires3) > 0 and (paires3[:, 0] >= 50).all() and np.allclose(dist3, 70.0), f"{len(paires3)} {dist3[:3]}")
    seg2 = seg.copy()
    seg2[50:, :, 1] *= 2.0
    paires2, _ = le_tour_suivant(seg2, ok, fen)
    v("★★★ sans doublon, quand deux sommets de la fenêtre ont le même vis-à-vis",
      0 < len(paires2) < int(fen.sum()) and len(paires2) == len({tuple(p) for p in paires2}), str(len(paires2)))
    v("★★★ une fenêtre vide n'a pas de tour suivant", len(le_tour_suivant(seg, ok, np.zeros_like(ok))[0]) == 0)
    v("★★★★ la chaîne tombe sur le tour suivant si l'une des deux spires le retrouve",
      la_lecture_de_la_graine({"la_nappe": "ne retrouve pas", "la_spire_plus": "ne retrouve pas",
                               "la_spire_moins": "retrouve"}) == "tombe sur le tour suivant")
    v("★★★★ la nappe seule ne suffit pas",
      la_lecture_de_la_graine({"la_nappe": "retrouve", "la_spire_plus": "ne retrouve pas",
                               "la_spire_moins": "non lue"}) == "ne tombe pas sur le tour suivant")
    v("★★★ deux spires non lues : non lue",
      la_lecture_de_la_graine({"la_nappe": "retrouve", "la_spire_plus": "non lue", "la_spire_moins": "non lue"}) == "non lue")
    vd = le_verdict({"les_pannes": [], "les_graines": [{"la_lecture": "tombe sur le tour suivant"}, {"la_lecture": "non lue"}]})
    v("★★★ l'issue : k des huit graines", vd["k"] == 1 and vd["n"] == 2)
    v("★★★ une panne de lecture rend la tranche indécidable",
      not le_verdict({"les_pannes": ["x"], "les_graines": [{"la_lecture": "non lue"}]})["decidable"])

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
