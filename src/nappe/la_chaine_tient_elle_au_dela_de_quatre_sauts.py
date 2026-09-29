"""La chaîne de m7 de 303 tient-elle au-delà de quatre sauts, au cœur d'une feuille et d'une surface de m7 à la suivante ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UN SEUL SAUT AU-DELÀ DU QUATRIÈME NE SOIT TIRÉ. Ce qui était vu avant d'écrire : tout ce que
`303` à `314` publient, dont `R4-F491` (les 32 spires de huit côtés sur dix sont à au plus 2 voxels du plus dense du scan) et
`R4-F494` (la chaîne passe d'une surface de `m7` à la suivante sur 71 à 100 % des rayons, et la part qui en saute une grandit de
saut en saut sur les graines 4, 7 et 8).

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST UN PAS VERS `R4-P103`. Une chaîne qui fait un tour du rouleau trancherait la question des
spires consécutives ; elle demande des centaines de sauts. Avant d'en demander autant, il faut savoir combien de sauts la chaîne
tient, et ce qui la fait lâcher.

## Ce qui est fait

- **La chaîne** : celle de `303`, prolongée à seize sauts de chaque côté, sur les cinq graines de `301` qui suivent l'empilement,
  chaque saut parti de la surface que le précédent a posée, exactement comme `303`.
- **Au cœur d'une feuille** : le plus dense du profil moyen du scan à au plus 5 voxels de la spire (`310`).
- **D'une surface de `m7` à la suivante** : au moins la moitié des rayons appuyés sans plage de `m7` intermédiaire (`313`).
- **Un saut tient** s'il est l'un et l'autre, et qu'au moins 100 points en sont jugés.

## Les issues

Par côté, le dernier saut h tel que les sauts 1 à h tiennent tous. **L'issue de la tranche** : la chaîne tient jusqu'au saut H sur
au moins la moitié des dix côtés, H le plus grand pour lequel c'est vrai.

## Rapporté à côté, qui ne décide rien

Pour chaque saut : le décalage du plus dense, la part des rayons sans plage intermédiaire, la part appuyée sur `m7`, le pas médian,
et la part des points sans matière.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : que les spires soient consécutives, ni ce que vaut la chaîne loin de ses six millimètres de
large.

Usage :
    uv run python src/nappe/la_chaine_tient_elle_au_dela_de_quatre_sauts.py --verifier
    uv run python src/nappe/la_chaine_tient_elle_au_dela_de_quatre_sauts.py --preparer
    uv run python src/nappe/la_chaine_tient_elle_au_dela_de_quatre_sauts.py --lire 4
    uv run python src/nappe/la_chaine_tient_elle_au_dela_de_quatre_sauts.py \\
        --json docs/mesures/la_chaine_tient_elle_au_dela_de_quatre_sauts.json
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
import les_nappes_de_m7_tiennent_elles_sur_une_seule_feuille as m302  # noqa: E402
import la_chaine_tiree_de_m7_suit_elle_sa_feuille_au_dela_du_premier_saut as m303  # noqa: E402
import le_plus_dense_dit_il_si_une_surface_est_sur_sa_feuille as m309  # noqa: E402
import la_chaine_saute_t_elle_des_surfaces_de_m7 as m313  # noqa: E402

LE_DOSSIER = RACINE / "data" / "chaine_longue"
LES_SURFACES_PREPAREES = LE_DOSSIER / "surfaces"
LE_PLAN = LE_DOSSIER / "plan.json"
LES_SAUTS = 16


def tient(s: dict, quart: int) -> bool:
    return (s["le_plus_dense"] is not None and abs(s["le_plus_dense"]) <= quart and s["les_points_juges"] >= 100
            and s["aucune"] is not None and s["aucune"] >= 0.5)


def le_dernier_qui_tient(sauts: list[dict], quart: int) -> int:
    h = 0
    for s in sauts:
        if not tient(s, quart):
            break
        h += 1
    return h


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    derniers = [c["le_dernier_saut_qui_tient"] for c in d["les_cotes"]]
    if not derniers:
        return {"decidable": False, "lissue": "indécidable : aucun côté"}
    n = len(derniers)
    H = max((h for h in range(1, LES_SAUTS + 1) if sum(1 for x in derniers if x >= h) * 2 >= n), default=0)
    return {"decidable": True, "H": H, "les_derniers": derniers,
            "lissue": (f"la chaîne tient jusqu'au saut {H} sur au moins la moitié des {n} côtés" if H else
                       f"la chaîne ne tient pas dès le premier saut sur plus de la moitié des {n} côtés")}


def preparer() -> dict:
    from le_transfert_retrouve_t_il_la_spire_voisine import lecteur_du_depot, lire_les_valeurs
    from la_spire_voisine_est_elle_a_un_pas import les_normales

    from zarr_depth import array_meta

    t0 = time.monotonic()
    pred = array_meta(f"{m298.BUCKET}/{m299.LA_PREDICTION_0358}", 0, 120.0)
    lire_, stats = lecteur_du_depot(pred, m300.LE_CACHE_M7, "m7_L0", m299.LA_PREDICTION_0358, 0)
    lv = lambda idx: lire_les_valeurs(idx, pred, lire_)  # noqa: E731
    r302, identiques = m302.retirer()
    v = m298.LES_VOLUMES["PHerc0358"]
    vol = m298.LesMorceaux("PHerc0358", v["url"], v["niveau"])
    T = m298.la_demi_fenetre("PHerc0358")
    tous = set()
    plan = {"les_cotes": [], "les_surfaces": {}}
    LES_SURFACES_PREPAREES.mkdir(parents=True, exist_ok=True)
    for rang, r in r302["les_nappes"].items():
        for nom, cote in m303.LES_COTES:
            surf, ok = r["la_nappe"], r["valide"]
            e = {"le_rang": rang, "le_cote": nom, "les_sauts": []}
            for h, s in enumerate(m303.enchainer(r["la_nappe"], r["valide"], cote, lv, sauts=LES_SAUTS), 1):
                nn, nok = les_normales(surf, ok)
                m = (s["appui"] & s["valide"] & nok & np.isfinite(s["le_pas"])).ravel()
                q, nq, pas_ = surf.reshape(-1, 3)[m], nn.reshape(-1, 3)[m], s["le_pas"].ravel()[m]
                n = np.zeros(0, dtype=int)
                if len(q):
                    L = int(np.ceil(np.abs(pas_).max())) + 1
                    ts = cote * np.arange(0.0, float(L))
                    idx = np.floor((q[:, None, :] + ts[None, :, None] * nq[:, None, :])[..., ::-1]).astype(np.int64)
                    vu = (lv(idx) > 0) & (np.abs(ts)[None, :] <= np.abs(pas_)[:, None] + m313.LA_MARGE)
                    n = m313.les_intermediaires(m300.les_plages(vu, ts), pas_)
                a = np.abs(s["le_pas"][s["valide"] & s["appui"]])
                lu = m313.le_saut(n)
                e["les_sauts"].append({"le_saut": h, "aucune": lu["aucune"], "une": lu["une"], "les_rayons": lu["les_rayons"],
                                       "la_part_appuyee": round(float(s["appui"].mean()), 4),
                                       "le_pas_median_voxels": round(float(np.median(a)), 2) if len(a) else None})
                sn, snok = les_normales(s["la_spire"], s["valide"])
                mm = s["valide"] & snok
                pts, nrm = s["la_spire"][mm], sn[mm]
                f = LES_SURFACES_PREPAREES / f"PHerc0358__g{rang}_{nom}_{h}.npz"
                np.savez_compressed(f, points=pts, normales=nrm, groupe=np.zeros(len(pts), dtype=int),
                                    juge=np.full(len(pts), np.nan), groupes=np.array([json.dumps([rang, nom, h])]))
                if len(pts):
                    c = m298.les_coordonnees(pts, nrm, v["facteur"], T)
                    tous |= m298.les_morceaux_complets(c[m298.dans_le_volume(c, vol.forme)], vol.taille)
                plan["les_surfaces"][f"g{rang}_{nom}_{h}"] = {"le_fichier": str(f.relative_to(RACINE)), "les_points": len(pts)}
                surf, ok = s["la_spire"], s["valide"]
            plan["les_cotes"].append(e)
            print(json.dumps({"le_rang": rang, "le_cote": nom, "aucune": [x["aucune"] for x in e["les_sauts"]]}), flush=True)
    cles = sorted(tous)
    (LE_DOSSIER / "morceaux.json").write_text(json.dumps(cles))
    plan.update(les_nappes_se_redonnent=identiques, les_pannes=list(stats["pannes"]) + list(r302["les_pannes"]),
                les_morceaux={"combien": len(cles)}, les_secondes=round(time.monotonic() - t0, 1))
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
    quart = m309.le_quart_de_pas("PHerc0358")
    cotes = []
    for c in plan["les_cotes"]:
        e = dict(c, les_sauts=[])
        for s in c["les_sauts"]:
            info = plan["les_surfaces"][f"g{c['le_rang']}_{c['le_cote']}_{s['le_saut']}"]
            r = m299.juger(vol, RACINE / info["le_fichier"], v["facteur"], T)
            pd = m309.le_plus_dense(r[0]["le_profil_moyen"]) if r else None
            e["les_sauts"].append(dict(s, le_plus_dense=pd, les_points_juges=r[0]["les_points_juges"] if r else 0,
                                       sans_matiere=r[0]["sans_matiere"] if r else 0))
        e["le_dernier_saut_qui_tient"] = le_dernier_qui_tient(e["les_sauts"], quart)
        cotes.append(e)
        print(json.dumps({"le_rang": e["le_rang"], "le_cote": e["le_cote"], "h": e["le_dernier_saut_qui_tient"]}), flush=True)
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"les_sauts": LES_SAUTS, "le_quart_de_pas_voxels": quart, "la_marge_voxels": m313.LA_MARGE},
         "les_nappes_se_redonnent": plan["les_nappes_se_redonnent"], "les_pannes": plan["les_pannes"],
         "les_cotes": cotes, "les_morceaux": plan["les_morceaux"]}
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

    bon = {"le_plus_dense": -2, "les_points_juges": 3000, "aucune": 0.8}
    v("★★★★ un saut tient au cœur, d'une surface à la suivante, avec assez de points", tient(bon, 5))
    v("★★★★ hors du cœur, il ne tient pas", not tient(dict(bon, le_plus_dense=7), 5))
    v("★★★★ s'il saute des surfaces de m7, il ne tient pas", not tient(dict(bon, aucune=0.4), 5))
    v("★★★ sous 100 points jugés, il ne tient pas", not tient(dict(bon, les_points_juges=99), 5))
    v("★★★ sans plus dense, il ne tient pas", not tient(dict(bon, le_plus_dense=None), 5))
    v("★★★ la borne du quart de pas est incluse", tient(dict(bon, le_plus_dense=-5), 5))
    v("★★★ le dernier qui tient s'arrête au premier qui lâche",
      le_dernier_qui_tient([bon, dict(bon, aucune=0.1), bon], 5) == 1 and le_dernier_qui_tient([bon] * 3, 5) == 3)
    vd = le_verdict({"les_cotes": [{"le_dernier_saut_qui_tient": x} for x in (16, 10, 3, 12, 0, 9)]})
    v("★★★ l'issue : le plus grand saut tenu sur au moins la moitié des côtés", vd["H"] == 10, str(vd))
    v("★★★ indécidable sans côté ou si une lecture échoue", not le_verdict({"les_cotes": []})["decidable"]
      and not le_verdict({"les_pannes": ["x"], "les_cotes": []})["decidable"])

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
