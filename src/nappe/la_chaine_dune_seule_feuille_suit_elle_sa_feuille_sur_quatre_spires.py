"""La chaîne partie d'une nappe de m7 d'une seule feuille, dont chaque saut croît sans changer de feuille, suit-elle sa feuille sur quatre spires ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UN SEUL SAUT CROISSANT NE SOIT TIRÉ. Ce qui était vu avant d'écrire : tout ce que `300` à `305`
publient, dont les deux nappes croissantes des graines 3 et 6 de PHerc0358, d'une seule feuille, qui suivent leur feuille.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P105`. La chaîne de `303` suit l'empilement pendant quatre sauts, mais chacun de
ses sauts est un vote, qui passe à la feuille voisine là où les feuilles sont serrées (`304`). Cette tranche fait croître chaque
saut comme `305` fait croître la nappe : depuis un point, sans jamais prendre une feuille à plus d'un quart de pas de celle de
ses voisins déjà posés.

## Ce qui est fait

- **Les départs** : les nappes croissantes de `305` qui suivent leur feuille sans déchirure ni boucle ouverte, retirées de `m7` à
  l'identique (leur carte au demi-voxel doit redonner celle que `305` publie).
- **Le saut croissant** : de chaque point posé de la surface précédente, le long de sa normale recalculée, du côté du saut, les
  feuilles de `m7` sur trois pas. Le départ est le point le plus proche du centre de la grille qui voit une feuille après la
  sienne ; il prend cette feuille-là. Puis la croissance de `305`, sur les feuilles que chaque point voit, à 5 voxels au plus de
  la médiane de ses voisins posés.
- **La chaîne** : de chaque côté, quatre sauts, chacun parti de la surface que le précédent a posée.
- **Le juge** : celui de `301`, sans rien y changer (Z ≥ 3 contre huit rampes, au moins 100 points jugés).

## Les issues, par côté

Un saut **tient** s'il suit sa feuille et n'a aucune boucle ouverte (le relevé de `302`). Par côté : le dernier saut h tel que
les sauts 1 à h tiennent tous ; 0 si le premier ne tient pas.

## L'issue de la tranche

**La chaîne d'une seule feuille tient jusqu'au saut H sur au moins la moitié des côtés**, H le plus grand saut pour lequel c'est
vrai ; indécidable si une lecture échoue, si aucune nappe de `305` ne part, ou si une nappe de départ ne redonne pas celle de `305`.

## Rapporté à côté, qui ne décide rien

Pour chaque saut : la part du plan posée, les déchirures, le pas médian, et la part des points posés dont le pas est à moins
d'un quart de pas du pas du rouleau (20 voxels).

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : que les quatre spires soient consécutives, si `m7` manque une feuille entière sur la zone ;
ni ce que vaut une chaîne de 6 mm sur un rouleau entier.

Usage :
    uv run python src/nappe/la_chaine_dune_seule_feuille_suit_elle_sa_feuille_sur_quatre_spires.py --verifier
    uv run python src/nappe/la_chaine_dune_seule_feuille_suit_elle_sa_feuille_sur_quatre_spires.py --preparer
    uv run python src/nappe/la_chaine_dune_seule_feuille_suit_elle_sa_feuille_sur_quatre_spires.py --lire 4
    uv run python src/nappe/la_chaine_dune_seule_feuille_suit_elle_sa_feuille_sur_quatre_spires.py \\
        --json docs/mesures/la_chaine_dune_seule_feuille_suit_elle_sa_feuille_sur_quatre_spires.json
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
import les_nappes_de_m7_tiennent_elles_sur_une_seule_feuille as m302  # noqa: E402
import une_nappe_qui_refuse_de_changer_de_feuille_suit_elle_encore_sa_feuille as m305  # noqa: E402

LE_DOSSIER = RACINE / "data" / "chaine_dune_seule_feuille"
LES_SURFACES_PREPAREES = LE_DOSSIER / "surfaces"
LE_PLAN = LE_DOSSIER / "plan.json"
CE_QUE_305_A_PUBLIE = RACINE / "docs" / "mesures" / "une_nappe_qui_refuse_de_changer_de_feuille_suit_elle_encore_sa_feuille.json"
LES_SAUTS = 4
LES_COTES = (("plus", 1.0), ("moins", -1.0))


# ── Le saut croissant ──────────────────────────────────────────────────────────────────────────────────────────────

def le_depart(suivante: np.ndarray, forme: tuple) -> tuple[int, int] | None:
    """Le point le plus proche du centre de la grille qui voit une feuille après la sienne ; à égalité, le premier dans
    l'ordre de la grille."""
    h, w = forme
    ok = np.isfinite(suivante.reshape(forme))
    if not ok.any():
        return None
    i, j = np.nonzero(ok)
    d = (i - (h - 1) / 2.0) ** 2 + (j - (w - 1) / 2.0) ** 2
    k = int(np.argmin(d))
    return int(i[k]), int(j[k])


def le_saut_croissant(surface: np.ndarray, valide: np.ndarray, cote: float, lire_valeurs,
                      tolerance: float = m305.LA_TOLERANCE, au_median: bool = False) -> dict:
    """De chaque point posé d'une surface, le long de sa normale recalculée, du côté `cote`, les feuilles de `m7` sur trois
    pas ; le départ prend la première après la sienne, puis la croissance de `305`. Rend aussi, pour `325`, la première feuille
    après la sienne que chaque point voit (NaN s'il n'en voit aucune). Avec `au_median`, écrit pour `327`, le départ est le point
    le plus proche du centre dont la feuille suivante est à au plus `tolerance` de la médiane de celles que tous les points voient."""
    from la_spire_voisine_est_elle_a_un_pas import les_normales

    forme = valide.shape
    nn, nok = les_normales(surface, valide)
    q, nq = surface.reshape(-1, 3), nn.reshape(-1, 3)
    ts = cote * np.arange(0.0, 3.0 * m300.LE_PAS_0358 + 1.0)
    idx = np.floor((q[:, None, :] + ts[None, :, None] * nq[:, None, :])[..., ::-1]).astype(np.int64)
    vu = (lire_valeurs(idx) > 0) & nok.reshape(-1)[:, None]
    suivante = m300.la_feuille_apres_la_sienne(ts, vu)
    pour_le_depart = suivante
    if au_median and np.isfinite(suivante).any():
        med = float(np.median(suivante[np.isfinite(suivante)]))
        with np.errstate(invalid="ignore"):
            pour_le_depart = np.where(np.abs(suivante - med) <= tolerance, suivante, np.nan)
    depart = le_depart(pour_le_depart, forme)
    if depart is None:
        vide = np.zeros(forme, dtype=bool)
        return {"la_spire": surface.copy(), "valide": vide, "le_pas": np.full(forme, np.nan), "le_depart": None,
                "les_suivantes": suivante.reshape(forme)}
    centres = m300.les_plages(vu, ts)
    pas_, pose = m305.croitre(centres, forme, depart, tolerance, demi_portee=tolerance,
                              cible_de_depart=float(suivante[depart[0] * forme[1] + depart[1]]))
    spire = (q + np.nan_to_num(pas_.ravel())[:, None] * nq).reshape(forme + (3,))
    return {"la_spire": spire, "valide": pose, "le_pas": pas_, "le_depart": list(depart), "les_suivantes": suivante.reshape(forme)}


def enchainer(nappe: np.ndarray, valide: np.ndarray, cote: float, lire_valeurs, sauts: int = LES_SAUTS) -> list[dict]:
    surf, ok = nappe, valide
    out = []
    for _ in range(sauts):
        s = le_saut_croissant(surf, ok, cote, lire_valeurs)
        out.append(s)
        surf, ok = s["la_spire"], s["valide"]
    return out


def la_part_au_pas(pas_: np.ndarray, pose: np.ndarray) -> float | None:
    """La part des points posés dont le pas est à moins d'un quart de pas du pas du rouleau."""
    a = np.abs(pas_[pose & np.isfinite(pas_)])
    if not len(a):
        return None
    return round(float((np.abs(a - m300.LE_PAS_0358) <= m305.LA_TOLERANCE).mean()), 4)


def tient(piece: str, boucles_ouvertes: int) -> bool:
    return piece == "suit sa feuille" and boucles_ouvertes == 0


def le_dernier_qui_tient(sauts: list[dict]) -> int:
    h = 0
    for s in sauts:
        if not tient(s["la_piece"], s["les_boucles"]["ceux_qui_ne_ferment_pas"]):
            break
        h += 1
    return h


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("les_departs_se_redonnent"):
        return {"decidable": False, "lissue": "indécidable : une nappe de départ ne redonne pas celle de 305"}
    derniers = [c["le_dernier_saut_qui_tient"] for c in d["les_cotes"]]
    if not derniers:
        return {"decidable": False, "lissue": "indécidable : aucune nappe de 305 ne part"}
    H = max((h for h in range(1, LES_SAUTS + 1) if sum(1 for x in derniers if x >= h) * 2 >= len(derniers)), default=0)
    return {"decidable": True, "H": H, "les_derniers": derniers,
            "lissue": (f"la chaîne d'une seule feuille tient jusqu'au saut {H} sur au moins la moitié des {len(derniers)} côtés"
                       if H else f"la chaîne d'une seule feuille ne tient pas dès le premier saut sur plus de la moitié des "
                                 f"{len(derniers)} côtés")}


# ── Les étapes ─────────────────────────────────────────────────────────────────────────────────────────────────────

def les_departs() -> list[dict]:
    """Les nappes de `305` qui suivent leur feuille sans déchirure ni boucle ouverte."""
    d = json.loads(CE_QUE_305_A_PUBLIE.read_text())
    return [g for g in d["les_graines"] if g["la_nappe"] == "suit sa feuille" and not g["les_dechirures"]
            and not g["les_boucles"]["ceux_qui_ne_ferment_pas"]]


def preparer() -> dict:
    from le_transfert_retrouve_t_il_la_spire_voisine import lecteur_du_depot, lire_les_valeurs
    from la_spire_voisine_est_elle_a_un_pas import les_normales

    from zarr_depth import array_meta

    t0 = time.monotonic()
    url = f"{m298.BUCKET}/{m299.LA_PREDICTION_0358}"
    pred = array_meta(url, 0, 120.0)
    lire_, stats = lecteur_du_depot(pred, m300.LE_CACHE_M7, "m7_L0", m299.LA_PREDICTION_0358, 0)
    lv = lambda idx: lire_les_valeurs(idx, pred, lire_)  # noqa: E731
    graines = {tuple((g["x"], g["y"], g["z"])): g for g in m301.les_graines_neuves()}
    identiques = True
    plan = {"les_cotes": [], "les_surfaces": {}}
    surfaces = {}
    for g in les_departs():
        src = graines[tuple(g["la_graine"])]
        nz, ny, nx = src["normale_zyx"]
        r = m305.la_nappe_croissante(tuple(g["la_graine"]), (nx, ny, nz), lv)
        identiques &= m305.la_carte(r["le_decalage"], r["valide"]) == g["la_carte"]
        rang = g["le_rang"]
        for nom, cote in LES_COTES:
            cote_ = {"le_rang": rang, "le_cote": nom, "les_sauts": []}
            for h, s in enumerate(enchainer(r["la_nappe"], r["valide"], cote, lv), 1):
                pose = s["valide"]
                a = np.abs(s["le_pas"][pose])
                cote_["les_sauts"].append({
                    "le_saut": h, "le_depart": s["le_depart"], "la_part_du_plan": round(float(pose.mean()), 4),
                    "les_dechirures": m300.les_dechirures(s["le_pas"], pose, m300.LE_PAS_0358 / 2.0),
                    "les_boucles": m302.les_boucles_qui_ne_ferment_pas(s["le_pas"], pose, m300.LE_PAS_0358),
                    "le_pas_median_voxels": round(float(np.median(a)), 2) if len(a) else None,
                    "la_part_au_pas": la_part_au_pas(s["le_pas"], pose),
                    "la_carte": m305.la_carte(s["le_pas"], pose)})
                nn, nok = les_normales(s["la_spire"], pose)
                for n_, (p, m, nr) in m300.la_famille(f"g{rang}_{nom}_{h}", s["la_spire"], pose, nn, nok, m300.LE_PAS_0358,
                                                      m300.LE_PAS_DU_PLAN).items():
                    surfaces[n_] = [{"la_piece": [rang, nom, h], "points": p[m], "normales": nr[m]}]
                resume = {k: v for k, v in cote_["les_sauts"][-1].items() if k != "la_carte"}
                print(json.dumps(dict(resume, le_rang=rang, le_cote=nom), ensure_ascii=False), flush=True)
            plan["les_cotes"].append(cote_)
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
    plan.update(les_departs_se_redonnent=bool(identiques), les_pannes=list(stats["pannes"]),
                les_morceaux={"combien": len(cles)}, la_lecture_de_m7={k: v_ for k, v_ in stats.items() if k != "pannes"},
                les_secondes=round(time.monotonic() - t0, 1))
    LE_PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=1))
    return {k: v_ for k, v_ in plan.items() if k not in ("les_cotes", "les_surfaces")}


def lire(ouvriers: int = 4) -> dict:
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
    cotes = []
    for c in plan["les_cotes"]:
        e = dict(c, les_sauts=[])
        for s in c["les_sauts"]:
            base = f"g{c['le_rang']}_{c['le_cote']}_{s['le_saut']}"
            if not res.get(base):
                e["les_sauts"].append(dict(s, le_z=None, lalignement=None, les_points_juges=0, sans_matiere=0,
                                           la_piece="non jugée", tient=False))
                continue
            a = res[base][0]
            tem = [(res[f"{base}__{r}_{ph:g}"] or [{"lalignement": None}])[0]["lalignement"] for r in m298.LES_PENTES
                   for ph in m300.LES_PHASES]
            z = m300.le_z(a["lalignement"], tem)
            piece = m300.la_piece(z, a["les_points_juges"])
            e["les_sauts"].append(dict(s, le_z=z, lalignement=a["lalignement"], les_points_juges=a["les_points_juges"],
                                       sans_matiere=a["sans_matiere"], la_piece=piece,
                                       tient=tient(piece, s["les_boucles"]["ceux_qui_ne_ferment_pas"])))
        e["le_dernier_saut_qui_tient"] = le_dernier_qui_tient(e["les_sauts"])
        cotes.append(e)
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"les_sauts": LES_SAUTS, "la_tolerance_voxels": m305.LA_TOLERANCE, "le_z_minimum": m300.LE_Z_MINIMUM},
         "les_departs_se_redonnent": plan["les_departs_se_redonnent"], "les_pannes": plan["les_pannes"],
         "les_cotes": cotes, "les_morceaux": plan["les_morceaux"], "la_lecture_de_m7": plan["la_lecture_de_m7"]}
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

    n = 9
    k = (np.arange(n) - 4) * 10.0
    plan = np.stack(np.meshgrid(k, k, indexing="ij"), axis=-1)
    surface = np.concatenate([plan[..., 1:2], plan[..., 0:1], np.full((n, n, 1), 100.0)], axis=-1)
    valide = np.ones((n, n), dtype=bool)

    def feuilles(zs, ou=None):
        """Des feuilles de 3 voxels aux hauteurs `zs` au-dessus de z = 100 ; `ou(x, y)` limite une feuille à une région."""
        def lv(idx):
            z, y, x = idx[..., 0] - 100, idx[..., 1], idx[..., 2]
            out = np.zeros(z.shape)
            for f in zs:
                m = np.abs(z - f) <= 1
                if ou is not None and f in ou:
                    m &= ou[f](x, y)
                out[m] = 1.0
            return out
        return lv

    s = le_saut_croissant(surface, valide, 1.0, feuilles([0, 20, 32]))
    interieur = np.zeros((n, n), dtype=bool)
    interieur[1:-1, 1:-1] = True
    v("★★★★ le saut prend la feuille après la sienne, et la garde partout où la normale existe",
      np.array_equal(s["valide"], interieur) and np.allclose(s["le_pas"][interieur], 20.0), str(np.nanmax(s["le_pas"])))
    s = le_saut_croissant(surface, valide, 1.0, feuilles([0, 30]))
    v("★★★★ un point sans normale ne voit rien, même quand son rayon immobile tombe sur la feuille qu'on cherche",
      np.array_equal(s["valide"], interieur) and np.allclose(s["le_pas"][interieur], 30.0))
    s = le_saut_croissant(surface, valide, -1.0, feuilles([0, -20, -32]))
    v("★★★ de l'autre côté, la feuille d'avant", np.allclose(s["le_pas"][interieur], -20.0))
    coupee = feuilles([0, 20, 32], {20: lambda x, y: x < 5})
    s = le_saut_croissant(surface, valide, 1.0, coupee)
    v("★★★★ là où la feuille suivante s'arrête et où une feuille à 12 voxels continue, le saut laisse un trou au lieu d'y passer",
      np.allclose(s["le_pas"][s["valide"]], 20.0) and not s["valide"][:, 5:].any() and s["valide"][1:-1, 1:5].all(),
      str(s["le_pas"]))
    v("★★★ le départ : le point le plus proche du centre qui voit une feuille après la sienne",
      le_depart(np.array([1.0, np.nan, np.nan, np.nan, 2.0, np.nan, np.nan, np.nan, np.nan]), (3, 3)) == (1, 1)
      and le_depart(np.array([np.nan, 1.0, np.nan, np.nan, np.nan, np.nan, 2.0, np.nan, np.nan]), (3, 3)) == (0, 1)
      and le_depart(np.full(9, np.nan), (3, 3)) is None)
    s = le_saut_croissant(surface, valide, 1.0, feuilles([0]))
    v("★★★ sans feuille après la sienne, rien n'est posé", not s["valide"].any() and s["le_depart"] is None)
    ch = enchainer(surface, valide, 1.0, feuilles([0, 20, 40, 60]), sauts=2)
    v("★★★ la chaîne : chaque saut part de la surface que le précédent a posée",
      np.allclose(ch[1]["le_pas"][ch[1]["valide"]], 20.0) and np.allclose(ch[1]["la_spire"][ch[1]["valide"]][:, 2], 140.0)
      and ch[1]["valide"].sum() < ch[0]["valide"].sum())
    v("★★★ la part au pas : à moins d'un quart de pas de 20 voxels",
      la_part_au_pas(np.array([[20.0, -24.0, 26.0, np.nan]]), np.array([[True, True, True, True]])) == round(2 / 3, 4))
    b0 = {"ceux_qui_ne_ferment_pas": 0}
    b1 = {"ceux_qui_ne_ferment_pas": 1}
    sauts = [{"la_piece": "suit sa feuille", "les_boucles": b0}, {"la_piece": "suit sa feuille", "les_boucles": b1},
             {"la_piece": "suit sa feuille", "les_boucles": b0}]
    v("★★★★ un saut tient s'il suit sa feuille ET ferme toutes ses boucles ; le dernier qui tient s'arrête au premier qui lâche",
      le_dernier_qui_tient(sauts) == 1 and le_dernier_qui_tient(sauts[2:]) == 1
      and le_dernier_qui_tient([{"la_piece": "ne la suit pas", "les_boucles": b0}]) == 0)
    vd = le_verdict({"les_departs_se_redonnent": True, "les_cotes": [{"le_dernier_saut_qui_tient": x} for x in (4, 2, 0, 3)]})
    v("★★★ l'issue : le plus grand saut tenu sur au moins la moitié des côtés", vd["H"] == 3, str(vd))
    v("★★★ l'issue : indécidable sans départ, si un départ ne se redonne pas, ou si une lecture échoue",
      not le_verdict({"les_departs_se_redonnent": True, "les_cotes": []})["decidable"]
      and not le_verdict({"les_departs_se_redonnent": False, "les_cotes": [{"le_dernier_saut_qui_tient": 4}]})["decidable"]
      and not le_verdict({"les_pannes": ["x"]})["decidable"])

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
    print(json.dumps(d["le_verdict"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
