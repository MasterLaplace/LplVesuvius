"""Sur PHerc0358, la chaîne tirée de m7 suit-elle sa feuille au-delà du premier saut ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UN SEUL SAUT AU-DELÀ DU PREMIER NE SOIT TIRÉ. Ce qui était vu avant d'écrire : tout ce que
`301` et `302` publient, dont les cinq nappes qui suivent leur feuille et leurs premiers sauts, qui la suivent aussi.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE. Dérouler demande des dizaines de sauts. Sur le segment de PHercParis4, la chaîne de `248`
enchaîne quatre sauts, chacun parti de la surface que le précédent a produite, et `297` suit son texte jusqu'au deuxième. Sur un
rouleau sans tracé, il n'y a ni segment ni texte : il y a le juge de `301`, sans référent, étalonné par taux. Cette tranche
enchaîne la même chaîne depuis les nappes de `m7` et demande au juge jusqu'où elle suit sa feuille.

## Ce qui est fait

- **Les départs** : les cinq nappes de `301` qui suivent leur feuille (graines 3, 4, 6, 7 et 8), retirées de `m7` à l'identique.
- **La chaîne** : de chaque côté, quatre sauts, chacun parti de la surface que le précédent a produite, le long de sa normale
  recalculée, jusqu'à la première feuille de `m7` après la sienne, avec le vote de `247`, exactement comme le premier saut de
  `300`. Le premier saut doit redonner celui de `301` point pour point.
- **Le juge** : celui de `301`, sans rien y changer, Z ≥ 3 contre huit rampes ; son étalonnage par taux est celui de `301`.

## Les issues, par côté

Le dernier saut h tel que les sauts 1 à h suivent tous leur feuille ; 0 si le premier ne la suit pas.

## L'issue de la tranche

**La chaîne suit sa feuille jusqu'au saut H sur au moins la moitié des dix côtés**, H le plus grand saut pour lequel c'est vrai ;
indécidable si une lecture échoue ou si un premier saut ne redonne pas celui de `301`.

## Rapporté à côté, qui ne décide rien

Pour chaque saut : la part des points appuyés sur `m7`, la part sans matière, le pas médian des points appuyés, les boucles qui ne
ferment pas (le relevé de `302`).

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : sur quelle feuille chaque saut tombe, ni qu'il n'ait pas sauté deux feuilles à la fois là où
`m7` en manque une ; un saut qui suit sa feuille peut être la feuille d'après la voisine. Ni ce que vaut une chaîne de 6 mm.

Usage :
    uv run python src/nappe/la_chaine_tiree_de_m7_suit_elle_sa_feuille_au_dela_du_premier_saut.py --verifier
    uv run python src/nappe/la_chaine_tiree_de_m7_suit_elle_sa_feuille_au_dela_du_premier_saut.py --preparer
    uv run python src/nappe/la_chaine_tiree_de_m7_suit_elle_sa_feuille_au_dela_du_premier_saut.py --lire 12
    uv run python src/nappe/la_chaine_tiree_de_m7_suit_elle_sa_feuille_au_dela_du_premier_saut.py \\
        --json docs/mesures/la_chaine_tiree_de_m7_suit_elle_sa_feuille_au_dela_du_premier_saut.json
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

LE_DOSSIER = RACINE / "data" / "chaine_de_m7"
LES_SURFACES_PREPAREES = LE_DOSSIER / "surfaces"
LE_PLAN = LE_DOSSIER / "plan.json"
LES_SAUTS = 4
LES_COTES = (("plus", 1.0), ("moins", -1.0))


def le_dernier_qui_suit(verdicts: list[str]) -> int:
    """Le dernier saut h tel que les sauts 1 à h suivent tous leur feuille."""
    h = 0
    for v in verdicts:
        if v != "suit sa feuille":
            break
        h += 1
    return h


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("les_premiers_sauts_se_redonnent"):
        return {"decidable": False, "lissue": "indécidable : un premier saut ne redonne pas celui de 301"}
    derniers = [c["le_dernier_saut_qui_suit"] for c in d["les_cotes"]]
    if not derniers:
        return {"decidable": False, "lissue": "indécidable : aucun côté"}
    H = max((h for h in range(1, LES_SAUTS + 1) if sum(1 for x in derniers if x >= h) * 2 >= len(derniers)), default=0)
    return {"decidable": True, "H": H, "les_derniers": derniers,
            "lissue": (f"la chaîne suit sa feuille jusqu'au saut {H} sur au moins la moitié des {len(derniers)} côtés" if H
                       else f"la chaîne ne suit pas sa feuille dès le premier saut sur plus de la moitié des {len(derniers)} "
                            "côtés")}


def enchainer(nappe: np.ndarray, valide: np.ndarray, cote: float, lire_valeurs, sauts: int = LES_SAUTS) -> list[dict]:
    """Les sauts successifs, chacun parti de la surface produite par le précédent."""
    surf, ok = nappe, valide
    out = []
    for _ in range(sauts):
        s = m300.le_saut_suivant(surf, ok, cote, lire_valeurs)
        out.append(s)
        surf, ok = s["la_spire"], s["valide"]
    return out


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
    z301 = np.load(m301.LES_NAPPES)
    identiques = True
    plan = {"les_cotes": [], "les_surfaces": {}}
    surfaces = {}
    for g in m302.les_nappes_qui_suivent():
        src = graines[tuple(g["la_graine"])]
        nz, ny, nx = src["normale_zyx"]
        r = m300.tirer_une_nappe(tuple(g["la_graine"]), (nx, ny, nz), (pred, lire_))
        rang = g["le_rang"]
        for nom, cote in LES_COTES:
            chaine = enchainer(r["la_nappe"], r["valide"], cote, lv)
            a, aok = z301[f"g{rang}_{nom}"], z301[f"g{rang}_{nom}_ok"]
            s1 = chaine[0]
            identiques &= bool(np.array_equal(aok, s1["valide"]) and np.array_equal(
                np.where(aok[..., None], a, 0.0), np.where(s1["valide"][..., None], s1["la_spire"], 0.0)))
            cote_ = {"le_rang": rang, "le_cote": nom, "les_sauts": []}
            for h, s in enumerate(chaine, 1):
                pas_ = np.abs(s["le_pas"][s["valide"] & s["appui"]])
                cote_["les_sauts"].append({
                    "le_saut": h, "la_part_appuyee": round(float(s["appui"].mean()), 4),
                    "le_pas_median_des_appuyes_voxels": round(float(np.median(pas_)), 2) if len(pas_) else None,
                    "les_boucles": m302.les_boucles_qui_ne_ferment_pas(s["le_pas"], s["valide"], m300.LE_PAS_0358)})
                nn, nok = les_normales(s["la_spire"], s["valide"])
                for n_, (p, m, nr) in m300.la_famille(f"g{rang}_{nom}_{h}", s["la_spire"], s["valide"], nn, nok,
                                                      m300.LE_PAS_0358, m300.LE_PAS_DU_PLAN).items():
                    surfaces[n_] = [{"la_piece": [rang, nom, h], "points": p[m], "normales": nr[m]}]
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
    plan.update(les_premiers_sauts_se_redonnent=identiques, les_pannes=list(stats["pannes"]),
                les_morceaux={"combien": len(cles)}, la_lecture_de_m7={k: v_ for k, v_ in stats.items() if k != "pannes"},
                les_secondes=round(time.monotonic() - t0, 1))
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
    cotes = []
    for c in plan["les_cotes"]:
        e = dict(c, les_sauts=[])
        verdicts = []
        for s in c["les_sauts"]:
            base = f"g{c['le_rang']}_{c['le_cote']}_{s['le_saut']}"
            a = res[base][0]
            tem = [res[f"{base}__{r}_{ph:g}"][0]["lalignement"] for r in m298.LES_PENTES for ph in m300.LES_PHASES]
            z = m300.le_z(a["lalignement"], tem)
            piece = m300.la_piece(z, a["les_points_juges"])
            verdicts.append(piece)
            e["les_sauts"].append(dict(s, le_z=z, lalignement=a["lalignement"], les_points_juges=a["les_points_juges"],
                                       sans_matiere=a["sans_matiere"], la_piece=piece))
        e["le_dernier_saut_qui_suit"] = le_dernier_qui_suit(verdicts)
        cotes.append(e)
    d = {"la_question": __doc__.splitlines()[0], "les_constantes": {"les_sauts": LES_SAUTS, "le_z_minimum": m300.LE_Z_MINIMUM},
         "les_premiers_sauts_se_redonnent": plan["les_premiers_sauts_se_redonnent"], "les_pannes": plan["les_pannes"],
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

    S, N = "suit sa feuille", "ne la suit pas"
    v("★★★ le dernier saut qui suit : la suite ininterrompue depuis le premier",
      le_dernier_qui_suit([S, S, N, S]) == 2 and le_dernier_qui_suit([N, S, S, S]) == 0 and le_dernier_qui_suit([S] * 4) == 4
      and le_dernier_qui_suit([S, "non jugée", S, S]) == 1)
    base = {"les_premiers_sauts_se_redonnent": True, "les_cotes": [{"le_dernier_saut_qui_suit": x}
                                                                    for x in (4, 3, 3, 2, 1, 1, 0, 0, 2, 3)]}
    vd = le_verdict(base)
    v("★★★★ l'issue : le plus grand saut atteint sur au moins la moitié des côtés", vd["H"] == 2 and "saut 2" in vd["lissue"],
      str(vd))
    b2 = dict(base, les_cotes=[{"le_dernier_saut_qui_suit": x} for x in (0, 0, 0, 0, 0, 0, 1, 1, 1, 1)])
    v("★★★ l'issue : moins de la moitié des côtés au premier saut, H = 0", le_verdict(b2)["H"] == 0
      and "dès le premier saut" in le_verdict(b2)["lissue"])
    v("★★★★ l'issue : indécidable si un premier saut ne redonne pas celui de 301",
      not le_verdict(dict(base, les_premiers_sauts_se_redonnent=False))["decidable"])
    v("★★★ l'issue : indécidable si une lecture a échoué", not le_verdict(dict(base, les_pannes=["x"]))["decidable"])

    M = np.zeros((140, 60, 60), dtype=np.uint8)
    for zz in range(10, 140, 20):
        M[zz:zz + 2] = 255

    def lv(idx):
        dedans = np.all((idx >= 0) & (idx < np.array(M.shape)), axis=-1)
        out = np.zeros(idx.shape[:-1], dtype=np.uint8)
        out[dedans] = M[idx[dedans][:, 0], idx[dedans][:, 1], idx[dedans][:, 2]]
        return out

    g = np.zeros((9, 9, 3))
    for i in range(9):
        for j in range(9):
            g[i, j] = (10.0 + 4 * j, 10.0 + 4 * i, 50.5)
    ch = enchainer(g, np.ones((9, 9), bool), 1.0, lv)
    zs = [float(np.median(c["la_spire"][..., 2][c["valide"]])) for c in ch]
    v("★★★★ la chaîne avance d'une feuille par saut, chacun parti du précédent", np.allclose(zs, [70.5, 90.5, 110.5, 130.5],
                                                                                            atol=0.6), str(zs))

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
