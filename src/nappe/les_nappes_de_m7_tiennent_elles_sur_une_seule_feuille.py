"""Les nappes de m7 qui suivent leur feuille sur PHerc0358 tiennent-elles d'une seule pièce, sans passer d'une feuille à la voisine ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LES PIÈCES DES NAPPES NE SOIENT COMPTÉES. Ce qui était vu avant d'écrire : tout ce que `301`
publie, dont la part des paires de voisins déchirées de chaque nappe (0,0017 à 0,0577 pour les cinq qui suivent leur feuille).

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P101`. `301` établit que cinq nappes tirées de `m7` sur PHerc0358 suivent leur
feuille, et leurs spires suivantes aussi. Mais l'alignement ne voit pas le rang : une nappe posée pour moitié sur une feuille et
pour moitié sur la voisine est alignée partout. Là où le vote passe d'une feuille à l'autre, deux voisins de la grille s'écartent
d'un pas entier le long de la normale : c'est une déchirure. Une nappe se coupe donc en pièces le long de ses déchirures, et une
pièce sans déchirure ne change de feuille nulle part, sauf là où deux feuilles se touchent.

⚠⚠ Réserve ajoutée le 2026-09-29, après le premier compte des pièces : la phrase précédente est fausse pour une coupure ouverte.
Une coupure qui s'arrête dans la nappe ne sépare rien, et la nappe passe d'une feuille à la voisine en tournant autour de son bout.
D'où le relevé des boucles (`les_boucles_qui_ne_ferment_pas`), ajouté après ce compte et avant d'en voir le résultat, qui ne
décide rien.

## Ce qui est fait

- **Les nappes** sont celles de `301` qui suivent leur feuille, et leurs deux spires suivantes, retirées de `m7` à l'identique :
  la même graine, le même plan, le même vote. Elles doivent redonner, point pour point, les surfaces que `301` a rangées ; sinon
  la mesure est indécidable.
- **Les pièces** : deux points voisins de la grille (quatre voisins) sont dans la même pièce si leurs décalages le long de la
  normale (celui de la nappe au plan, celui de la spire à la nappe) diffèrent d'au plus un demi-pas, 10 voxels. Les pièces sont les
  composantes connexes de ce graphe.
- **Le juge** est celui de `301`, sans rien y changer (Z ≥ 3 contre huit rampes), porté sur la plus grande pièce de chaque
  surface.

## Les issues, par surface

- **d'une seule pièce** si sa plus grande pièce tient au moins 90 % de ses points valides, **en plusieurs pièces** sinon ;
- et la plus grande pièce suit sa feuille ou non, par le juge.

## L'issue de la tranche

**Sur k des cinq nappes, la nappe et ses deux spires suivantes tiennent d'une seule pièce qui suit sa feuille**, avec k de 0 à 5 ;
indécidable si une nappe retirée ne redonne pas celle de `301`, ou si une lecture échoue.

## Rapporté à côté, qui ne décide rien

Le nombre de pièces d'au moins 5 % des points ; la dispersion du pas des spires suivantes dans leur plus grande pièce (médiane et
écart interquartile) ; la part des points appuyés sur `m7` dans la plus grande pièce.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : qu'une pièce sans déchirure reste sur une seule feuille là où deux feuilles se touchent sans
écart, ni que la spire suivante soit la voisine plutôt qu'une plus lointaine si `m7` a manqué une feuille entre elles.

Usage :
    uv run python src/nappe/les_nappes_de_m7_tiennent_elles_sur_une_seule_feuille.py --verifier
    uv run python src/nappe/les_nappes_de_m7_tiennent_elles_sur_une_seule_feuille.py --preparer
    uv run python src/nappe/les_nappes_de_m7_tiennent_elles_sur_une_seule_feuille.py --lire 12
    uv run python src/nappe/les_nappes_de_m7_tiennent_elles_sur_une_seule_feuille.py \\
        --json docs/mesures/les_nappes_de_m7_tiennent_elles_sur_une_seule_feuille.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))
sys.path.insert(0, str(RACINE / "src" / "tracecheck"))

import la_matiere_dit_elle_si_la_surface_est_sur_sa_feuille as m298  # noqa: E402
import lalignement_des_profils_dit_il_si_une_premiere_surface_suit_sa_feuille as m299  # noqa: E402
import une_nappe_tiree_de_m7_suit_elle_sa_feuille as m300  # noqa: E402
import les_nappes_de_m7_suivent_elles_leur_feuille_sur_des_graines_neuves as m301  # noqa: E402

LE_DOSSIER = RACINE / "data" / "nappes_dune_seule_piece"
LES_SURFACES_PREPAREES = LE_DOSSIER / "surfaces"
LE_PLAN = LE_DOSSIER / "plan.json"
CE_QUE_301_A_PUBLIE = RACINE / "docs" / "mesures" / "les_nappes_de_m7_suivent_elles_leur_feuille_sur_des_graines_neuves.json"
LA_PART_DUNE_SEULE_PIECE = 0.90
LA_PART_DUNE_PIECE_COMPTEE = 0.05


# ── Les pièces ─────────────────────────────────────────────────────────────────────────────────────────────────────

def les_pieces(decalage: np.ndarray, valide: np.ndarray, demi: float) -> np.ndarray:
    """Les composantes connexes de la grille : deux voisins (quatre voisins) sont liés s'ils sont valides tous deux et que leurs
    décalages diffèrent d'au plus `demi`. Rend une étiquette par point, −1 hors des points valides."""
    h, w = valide.shape
    parent = np.arange(h * w)

    def racine(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def unir(a, b):
        ra, rb = racine(a), racine(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)

    d = np.where(valide, decalage, np.nan)
    with np.errstate(invalid="ignore"):
        horiz = valide[:, 1:] & valide[:, :-1] & (np.abs(d[:, 1:] - d[:, :-1]) <= demi)
        vert = valide[1:, :] & valide[:-1, :] & (np.abs(d[1:, :] - d[:-1, :]) <= demi)
    for i, j in zip(*np.nonzero(horiz)):
        unir(i * w + j, i * w + j + 1)
    for i, j in zip(*np.nonzero(vert)):
        unir(i * w + j, (i + 1) * w + j)
    out = np.array([racine(k) for k in range(h * w)]).reshape(h, w)
    return np.where(valide, out, -1)


def les_boucles_qui_ne_ferment_pas(decalage: np.ndarray, valide: np.ndarray, pas: float) -> dict:
    """Rapporté, qui ne décide rien, et ajouté après le premier compte des pièces : autour de chaque carré de quatre points
    voisins, la somme des sauts de décalage arrondis au pas. Une surface qui reste sur une seule feuille ferme toutes ses boucles
    (somme nulle) ; une coupure ouverte, qui laisse passer d'une feuille à la voisine autour de son bout, laisse un carré où la
    somme vaut ±1. C'est ce que les pièces ne voient pas : une coupure ouverte ne sépare rien."""
    d = np.where(valide, decalage, np.nan)
    a, b_, c, e = d[:-1, :-1], d[:-1, 1:], d[1:, 1:], d[1:, :-1]
    ok = np.isfinite(a) & np.isfinite(b_) & np.isfinite(c) & np.isfinite(e)
    with np.errstate(invalid="ignore"):
        tour = (np.rint((b_ - a) / pas) + np.rint((c - b_) / pas) + np.rint((e - c) / pas) + np.rint((a - e) / pas))
    ouvertes = ok & (tour != 0)
    with np.errstate(invalid="ignore"):
        sauts = np.concatenate([np.abs(d[:, 1:] - d[:, :-1]).ravel(), np.abs(d[1:, :] - d[:-1, :]).ravel()])
    sauts = sauts[np.isfinite(sauts)]
    grands = sauts[sauts > pas / 2.0]
    return {"les_carres": int(ok.sum()), "ceux_qui_ne_ferment_pas": int(ouvertes.sum()),
            "la_part": round(float(ouvertes.sum() / ok.sum()), 5) if ok.any() else None,
            "les_sauts_de_plus_dun_demi_pas": int(len(grands)),
            "leur_mediane_voxels": round(float(np.median(grands)), 2) if len(grands) else None,
            "leur_part_sous_trois_quarts_de_pas": round(float((grands < 0.75 * pas).mean()), 4) if len(grands) else None}


def le_decompte(etiquettes: np.ndarray) -> dict:
    """La part de la plus grande pièce et le nombre de pièces d'au moins 5 % des points valides."""
    e = etiquettes[etiquettes >= 0]
    if len(e) == 0:
        return {"la_plus_grande": None, "les_pieces_comptees": 0, "les_points": 0}
    _, n = np.unique(e, return_counts=True)
    return {"la_plus_grande": round(float(n.max() / len(e)), 4),
            "les_pieces_comptees": int((n >= LA_PART_DUNE_PIECE_COMPTEE * len(e)).sum()), "les_points": int(len(e))}


def la_plus_grande_piece(etiquettes: np.ndarray) -> np.ndarray:
    e = etiquettes[etiquettes >= 0]
    if len(e) == 0:
        return np.zeros(etiquettes.shape, dtype=bool)
    u, n = np.unique(e, return_counts=True)
    return etiquettes == u[int(np.argmax(n))]


def la_surface(decompte: dict, z: float | None, n: int) -> dict:
    une = decompte["la_plus_grande"] is not None and decompte["la_plus_grande"] >= LA_PART_DUNE_SEULE_PIECE
    return {"dune_seule_piece": bool(une), "la_plus_grande_suit": m300.la_piece(z, n) == "suit sa feuille"}


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("les_nappes_se_redonnent"):
        return {"decidable": False, "lissue": "indécidable : une nappe retirée ne redonne pas celle de 301"}
    k = 0
    for n in d["les_nappes"]:
        if all(n["les_surfaces"][s]["dune_seule_piece"] and n["les_surfaces"][s]["la_plus_grande_suit"]
               for s in ("nappe", "plus", "moins")):
            k += 1
    return {"decidable": True, "k": k, "n": len(d["les_nappes"]),
            "lissue": f"sur {k} des {len(d['les_nappes'])} nappes, la nappe et ses deux spires suivantes tiennent d'une seule "
                      "pièce qui suit sa feuille"}


# ── Les étapes ─────────────────────────────────────────────────────────────────────────────────────────────────────

def les_nappes_qui_suivent() -> list[dict]:
    d = json.loads(CE_QUE_301_A_PUBLIE.read_text())
    return [g for g in d["le_rouleau"]["les_graines"] if g["la_nappe"] == "suit sa feuille"]


def retirer() -> tuple[dict, bool]:
    """Les nappes qui suivent, retirées de `m7`, avec leurs décalages ; et si elles redonnent celles de `301`."""
    from le_transfert_retrouve_t_il_la_spire_voisine import lecteur_du_depot

    from zarr_depth import array_meta

    url = f"{m298.BUCKET}/{m299.LA_PREDICTION_0358}"
    pred = array_meta(url, 0, 120.0)
    lire_, stats = lecteur_du_depot(pred, m300.LE_CACHE_M7, "m7_L0", m299.LA_PREDICTION_0358, 0)
    graines = {tuple((g["x"], g["y"], g["z"])): g for g in m301.les_graines_neuves()}
    z301 = np.load(m301.LES_NAPPES)
    out, identiques = {}, True
    for g in les_nappes_qui_suivent():
        src = graines[tuple(g["la_graine"])]
        nz, ny, nx = src["normale_zyx"]
        r = m300.tirer_une_nappe(tuple(g["la_graine"]), (nx, ny, nz), (pred, lire_))
        rang = g["le_rang"]
        for nom, (pts, ok) in (("nappe", (r["la_nappe"], r["valide"])),
                               ("plus", (r["les_sauts"]["plus"]["la_spire"], r["les_sauts"]["plus"]["valide"])),
                               ("moins", (r["les_sauts"]["moins"]["la_spire"], r["les_sauts"]["moins"]["valide"]))):
            a, aok = z301[f"g{rang}_{nom}"], z301[f"g{rang}_{nom}_ok"]
            identiques &= bool(np.array_equal(aok, ok) and np.array_equal(np.where(ok[..., None], a, 0.0),
                                                                             np.where(ok[..., None], pts, 0.0)))
        out[rang] = r
    return {"les_nappes": out, "les_pannes": list(stats["pannes"])}, identiques


def preparer() -> dict:
    from la_spire_voisine_est_elle_a_un_pas import les_normales

    t0 = time.monotonic()
    r, identiques = retirer()
    demi = m300.LE_PAS_0358 / 2.0
    plan = {"les_nappes_se_redonnent": identiques, "les_pannes": r["les_pannes"], "les_nappes": [], "les_surfaces": {}}
    surfaces = {}
    for rang, x in r["les_nappes"].items():
        entree = {"le_rang": rang, "les_surfaces": {}}
        for nom, pts, ok, dec, appui in (
                ("nappe", x["la_nappe"], x["valide"], x["le_decalage"], x["appui"]),
                ("plus", x["les_sauts"]["plus"]["la_spire"], x["les_sauts"]["plus"]["valide"],
                 x["les_sauts"]["plus"]["le_pas"], x["les_sauts"]["plus"]["appui"]),
                ("moins", x["les_sauts"]["moins"]["la_spire"], x["les_sauts"]["moins"]["valide"],
                 x["les_sauts"]["moins"]["le_pas"], x["les_sauts"]["moins"]["appui"])):
            et = les_pieces(dec, ok, demi)
            grande = la_plus_grande_piece(et)
            dc = le_decompte(et)
            pas_g = np.abs(dec[grande & appui]) if nom != "nappe" else np.zeros(0)
            dc["les_boucles"] = les_boucles_qui_ne_ferment_pas(dec, ok, m300.LE_PAS_0358)
            entree["les_surfaces"][nom] = dict(dc, la_part_appuyee_de_la_plus_grande=round(float(appui[grande].mean()), 4)
                                               if grande.any() else None,
                                               le_pas_median=round(float(np.median(pas_g)), 2) if len(pas_g) else None,
                                               lecart_interquartile_du_pas=round(float(np.subtract(*np.percentile(
                                                   pas_g, [75, 25]))), 2) if len(pas_g) else None)
            nn, nok = les_normales(pts, grande)
            for nom_s, (p, m, nr) in m300.la_famille(f"g{rang}_{nom}", pts, grande, nn, nok, m300.LE_PAS_0358,
                                                     m300.LE_PAS_DU_PLAN).items():
                surfaces[nom_s] = [{"la_piece": [rang, nom], "points": p[m], "normales": nr[m]}]
        plan["les_nappes"].append(entree)
    v = m298.LES_VOLUMES["PHerc0358"]
    vol = m298.LesMorceaux("PHerc0358", v["url"], v["niveau"])
    T = m298.la_demi_fenetre("PHerc0358")
    tous = set()
    LES_SURFACES_PREPAREES.mkdir(parents=True, exist_ok=True)
    for nom, morceaux in surfaces.items():
        f = LES_SURFACES_PREPAREES / f"PHerc0358__{nom}.npz"
        pts = np.concatenate([m["points"] for m in morceaux])
        nrm = np.concatenate([m["normales"] for m in morceaux])
        np.savez_compressed(f, points=pts, normales=nrm, groupe=np.zeros(len(pts), dtype=int), juge=np.full(len(pts), np.nan),
                            groupes=np.array([json.dumps(morceaux[0]["la_piece"])]))
        if len(pts):
            coords = m298.les_coordonnees(pts, nrm, v["facteur"], T)
            tous |= m298.les_morceaux_complets(coords[m298.dans_le_volume(coords, vol.forme)], vol.taille)
        plan["les_surfaces"][nom] = {"le_fichier": str(f.relative_to(RACINE)), "les_points": len(pts)}
    cles = sorted(tous)
    (LE_DOSSIER / "morceaux.json").write_text(json.dumps(cles))
    plan["les_morceaux"] = {"combien": len(cles)}
    plan["les_secondes"] = round(time.monotonic() - t0, 1)
    LE_PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=1))
    return plan


def lire(ouvriers: int = 8) -> dict:
    v = m298.LES_VOLUMES["PHerc0358"]
    vol = m298.LesMorceaux("PHerc0358", v["url"], v["niveau"])
    cles = [tuple(c) for c in json.loads((LE_DOSSIER / "morceaux.json").read_text())]
    comptes = {"deja": 0, "tire": 0, "absent": 0}
    with ThreadPoolExecutor(ouvriers) as ex:
        for r in ex.map(lambda c: vol.tirer(*c), cles):
            comptes[r] += 1
    return dict(comptes, combien=len(cles))


def mesurer() -> dict:
    t0 = time.monotonic()
    plan = json.loads(LE_PLAN.read_text())
    v = m298.LES_VOLUMES["PHerc0358"]
    vol = m298.LesMorceaux("PHerc0358", v["url"], v["niveau"])
    T = m298.la_demi_fenetre("PHerc0358")
    res = {nom: m299.juger(vol, RACINE / info["le_fichier"], v["facteur"], T) for nom, info in plan["les_surfaces"].items()}
    nappes = []
    for n in plan["les_nappes"]:
        e = {"le_rang": n["le_rang"], "les_surfaces": {}}
        for s in ("nappe", "plus", "moins"):
            base = f"g{n['le_rang']}_{s}"
            a = res[base][0]
            tem = [res[f"{base}__{r}_{ph:g}"][0]["lalignement"] for r in m298.LES_PENTES for ph in m300.LES_PHASES]
            z = m300.le_z(a["lalignement"], tem)
            e["les_surfaces"][s] = dict(n["les_surfaces"][s], le_z_de_la_plus_grande=z,
                                        lalignement_de_la_plus_grande=a["lalignement"],
                                        les_points_juges=a["les_points_juges"],
                                        **la_surface(n["les_surfaces"][s], z, a["les_points_juges"]))
        nappes.append(e)
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"la_part_dune_seule_piece": LA_PART_DUNE_SEULE_PIECE,
                            "la_part_dune_piece_comptee": LA_PART_DUNE_PIECE_COMPTEE,
                            "le_demi_pas_voxels": m300.LE_PAS_0358 / 2.0, "le_z_minimum": m300.LE_Z_MINIMUM},
         "les_nappes_se_redonnent": plan["les_nappes_se_redonnent"], "les_pannes": plan["les_pannes"],
         "les_nappes": nappes, "les_morceaux": plan["les_morceaux"]}
    d["le_verdict"] = le_verdict(d)
    d["les_secondes"] = round(time.monotonic() - t0, 1)
    return d


# ── La batterie ────────────────────────────────────────────────────────────────────────────────────────────────────

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

    ok = np.ones((6, 8), dtype=bool)
    plat = np.zeros((6, 8))
    v("★★★ une nappe sans déchirure est d'une seule pièce", le_decompte(les_pieces(plat, ok, 10.0))["la_plus_grande"] == 1.0)
    marche = plat.copy()
    marche[:, 5:] = 20.0
    et = les_pieces(marche, ok, 10.0)
    dc = le_decompte(et)
    v("★★★★ une marche d'une feuille coupe la nappe en deux pièces", dc["la_plus_grande"] == round(30 / 48, 4)
      and dc["les_pieces_comptees"] == 2, str(dc))
    pente = np.tile(np.arange(8) * 4.0, (6, 1))
    v("★★★★ une pente douce, dont chaque pas reste sous le demi-pas, ne déchire pas",
      le_decompte(les_pieces(pente, ok, 10.0))["la_plus_grande"] == 1.0)
    trou = ok.copy()
    trou[:, 3] = False
    v("★★★ une colonne invalide coupe aussi, et ses points ne comptent pas",
      le_decompte(les_pieces(plat, trou, 10.0)) == {"la_plus_grande": round(24 / 42, 4), "les_pieces_comptees": 2,
                                                    "les_points": 42})
    diag = plat.copy()
    diag[0, 0] = 50.0
    v("★★★ un point isolé par une déchirure est sa propre pièce, et ne compte pas sous 5 %",
      le_decompte(les_pieces(diag, ok, 10.0))["les_pieces_comptees"] == 1)
    v("★★★ la plus grande pièce est celle qui a le plus de points", la_plus_grande_piece(et)[:, :5].all()
      and not la_plus_grande_piece(et)[:, 5:].any())
    v("★★★ une surface : d'une seule pièce à 90 %, et suit si Z ≥ 3 sur au moins 100 points",
      la_surface({"la_plus_grande": 0.9}, 3.0, 100) == {"dune_seule_piece": True, "la_plus_grande_suit": True}
      and la_surface({"la_plus_grande": 0.8999}, 9.0, 500)["dune_seule_piece"] is False
      and la_surface({"la_plus_grande": 1.0}, 2.9, 500)["la_plus_grande_suit"] is False)
    s_ = {"dune_seule_piece": True, "la_plus_grande_suit": True}
    base = {"les_nappes_se_redonnent": True, "les_nappes": [
        {"les_surfaces": {"nappe": s_, "plus": s_, "moins": s_}},
        {"les_surfaces": {"nappe": s_, "plus": dict(s_, dune_seule_piece=False), "moins": s_}}]}
    vd = le_verdict(base)
    v("★★★★ l'issue : une nappe ne compte que si elle et ses deux spires tiennent d'une seule pièce qui suit",
      vd["k"] == 1 and vd["lissue"].startswith("sur 1 des 2 nappes"), str(vd))
    v("★★★★ l'issue : indécidable si une nappe retirée ne redonne pas celle de 301",
      not le_verdict(dict(base, les_nappes_se_redonnent=False))["decidable"])
    v("★★★ l'issue : indécidable si une lecture a échoué", not le_verdict(dict(base, les_pannes=["x"]))["decidable"])

    v("★★★ une nappe plate ou en marche fermée ferme toutes ses boucles",
      les_boucles_qui_ne_ferment_pas(plat, ok, 20.0)["ceux_qui_ne_ferment_pas"] == 0
      and les_boucles_qui_ne_ferment_pas(marche, ok, 20.0)["ceux_qui_ne_ferment_pas"] == 0)
    vis = np.zeros((6, 8))
    for i in range(6):
        for j in range(8):
            vis[i, j] = 20.0 * ((np.degrees(np.arctan2(i - 2.5, j - 3.5)) % 360.0) / 360.0)
    bl = les_boucles_qui_ne_ferment_pas(vis, ok, 20.0)
    v("★★★★ une vis, qui passe d'une feuille à la voisine en tournant autour d'un point, laisse une boucle ouverte",
      bl["ceux_qui_ne_ferment_pas"] == 1, str(bl))
    v("★★★ et cette même vis reste d'une seule pièce : les pièces ne la voient pas",
      le_decompte(les_pieces(vis, ok, 10.0))["la_plus_grande"] == 1.0)
    for e in echecs:
        print(f"  ÉCHEC {e}")
    print(f"{Path(__file__).name}   {'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--preparer", action="store_true")
    p.add_argument("--lire", type=int, default=None, metavar="OUVRIERS")
    p.add_argument("--json", type=Path, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if a.preparer:
        print(json.dumps(preparer(), ensure_ascii=False, indent=1))
        return 0
    if a.lire is not None:
        print(json.dumps(lire(a.lire), ensure_ascii=False, indent=1))
        return 0
    d = mesurer()
    texte = json.dumps(d, ensure_ascii=False, indent=1)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(texte + "\n")
    print(texte)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
