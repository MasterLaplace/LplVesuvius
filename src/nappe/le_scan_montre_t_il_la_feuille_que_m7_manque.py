"""Là où m7 ne voit pas de feuille après celle d'une nappe, le scan en montre-t-il une, un maximum de densité à un pas de la nappe ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UN SEUL PROFIL NE SOIT LU SUR LES RAYONS OÙ m7 NE VOIT RIEN. Ce qui était vu avant d'écrire : tout
ce que `303` à `318` publient, dont `R4-F499` : une chaîne qui ne pose que ce que `m7` voit ne tient pas, parce que `m7` manque la
feuille suivante par endroits.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P116`. Si `m7` manque des feuilles que le scan montre, `m7` est une prédiction à
compléter par le scan, et une chaîne peut se prolonger par ce que le scan voit ; si le scan ne les montre pas non plus, les feuilles
y sont collées à 9,362 µm, et aucune prédiction ne les séparera à cette résolution.

## Ce qui est fait

- **Les rayons** : depuis les points des nappes du vote de `301` (graines 3, 4, 6, 7 et 8) que `m7` appuie, le long de leur normale
  recalculée, de chaque côté.
- **Deux groupes** : les rayons où `m7` voit une plage dont le centre est entre 5 et 30 voxels (une feuille à au plus un pas et demi),
  et ceux où il n'en voit aucune.
- **Le profil du scan** : de −1 à +41 voxels le long du rayon, chaque profil ramené à moyenne nulle et écart un, moyenné par groupe.
- **La saillance d'une feuille à un pas** : le plus haut du profil moyen entre 12 et 28 voxels, moins son plus bas entre 4 et 12.

## Les issues

Par côté : **le scan montre la feuille que m7 manque** si la saillance du groupe où `m7` ne voit rien vaut au moins la moitié de celle
du groupe où il voit ; **il ne la montre pas** si elle en vaut moins du quart ; **mêlé** entre les deux ; **non lu** sous 100 rayons
dans un groupe. L'issue de la tranche : sur k des côtés lus, le scan montre la feuille que `m7` manque.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : pourquoi `m7` manque ces feuilles, ni que le maximum que le scan montre soit la spire
suivante plutôt qu'une couche de la même feuille.

Usage :
    uv run python src/nappe/le_scan_montre_t_il_la_feuille_que_m7_manque.py --verifier
    uv run python src/nappe/le_scan_montre_t_il_la_feuille_que_m7_manque.py --preparer
    uv run python src/nappe/le_scan_montre_t_il_la_feuille_que_m7_manque.py --lire 4
    uv run python src/nappe/le_scan_montre_t_il_la_feuille_que_m7_manque.py \\
        --json docs/mesures/le_scan_montre_t_il_la_feuille_que_m7_manque.json
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

LE_DOSSIER = RACINE / "data" / "feuille_que_m7_manque"
LE_PLAN = LE_DOSSIER / "plan.npz"
LE_PLAN_JSON = LE_DOSSIER / "plan.json"
LE_DECALAGE = 20.0
LES_U = np.arange(-21, 22) + LE_DECALAGE
LE_MINIMUM = 100


def les_groupes(centres: list[np.ndarray], bas: float = 5.0, haut: float = 30.0) -> np.ndarray:
    """Pour chaque rayon, vrai si m7 y voit une plage dont le centre, en valeur absolue, est entre `bas` et `haut`."""
    return np.array([bool(len(c)) and bool(((np.abs(c) >= bas) & (np.abs(c) <= haut)).any()) for c in centres])


def la_saillance(profil: list, u: np.ndarray = LES_U) -> float | None:
    """Le plus haut du profil entre 12 et 28 voxels, moins son plus bas entre 4 et 12."""
    if not profil:
        return None
    p = np.asarray(profil, dtype=float)
    haut = p[(u >= 12) & (u <= 28)]
    bas = p[(u >= 4) & (u <= 12)]
    return round(float(haut.max() - bas.min()), 4)


def la_lecture(s_voit: float | None, s_manque: float | None, n_voit: int, n_manque: int) -> str:
    if n_voit < LE_MINIMUM or n_manque < LE_MINIMUM or s_voit is None or s_manque is None or s_voit <= 0:
        return "non lu"
    r = s_manque / s_voit
    if r >= 0.5:
        return "le scan montre la feuille que m7 manque"
    if r < 0.25:
        return "il ne la montre pas"
    return "mêlé"


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    lus = [c for c in d["les_cotes"] if c["la_lecture"] != "non lu"]
    if not lus:
        return {"decidable": False, "lissue": "indécidable : aucun côté lu"}
    k = sum(1 for c in lus if c["la_lecture"] == "le scan montre la feuille que m7 manque")
    j = sum(1 for c in lus if c["la_lecture"] == "il ne la montre pas")
    return {"decidable": True, "k": k, "j": j, "n": len(lus),
            "lissue": f"sur {k} des {len(lus)} côtés lus, le scan montre la feuille que m7 manque ; sur {j}, il ne la montre pas"}


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
    tableaux, cotes = {}, []
    for rang, r in r302["les_nappes"].items():
        nn, nok = les_normales(r["la_nappe"], r["valide"])
        m = r["valide"] & r["appui"] & nok
        q, nq = r["la_nappe"][m], nn[m]
        for nom, cote in m303.LES_COTES:
            ts = cote * np.arange(0.0, 31.0)
            idx = np.floor((q[:, None, :] + ts[None, :, None] * nq[:, None, :])[..., ::-1]).astype(np.int64)
            voit = les_groupes(m300.les_plages(lv(idx) > 0, ts))
            pts, nrm = q + cote * LE_DECALAGE * nq, cote * nq
            tableaux[f"g{rang}_{nom}_points"], tableaux[f"g{rang}_{nom}_normales"] = pts, nrm
            tableaux[f"g{rang}_{nom}_voit"] = voit
            c = m298.les_coordonnees(pts, nrm, v["facteur"], T)
            tous |= m298.les_morceaux_complets(c[m298.dans_le_volume(c, vol.forme)], vol.taille)
            cotes.append({"le_rang": rang, "le_cote": nom, "les_rayons": int(len(q)), "ceux_ou_m7_voit": int(voit.sum())})
            print(json.dumps(cotes[-1]), flush=True)
    LE_DOSSIER.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(LE_PLAN, **tableaux)
    cles = sorted(tous)
    (LE_DOSSIER / "morceaux.json").write_text(json.dumps(cles))
    plan = {"les_cotes": cotes, "les_nappes_se_redonnent": identiques,
            "les_pannes": list(stats["pannes"]) + list(r302["les_pannes"]), "les_morceaux": {"combien": len(cles)},
            "les_secondes": round(time.monotonic() - t0, 1)}
    LE_PLAN_JSON.write_text(json.dumps(plan, ensure_ascii=False, indent=1))
    return plan


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
    plan = json.loads(LE_PLAN_JSON.read_text())
    z = np.load(LE_PLAN)
    v = m298.LES_VOLUMES["PHerc0358"]
    vol = m298.LesMorceaux("PHerc0358", v["url"], v["niveau"])
    T = m298.la_demi_fenetre("PHerc0358")
    cotes = []
    for c in plan["les_cotes"]:
        base = f"g{c['le_rang']}_{c['le_cote']}"
        pts, nrm, voit = z[f"{base}_points"], z[f"{base}_normales"], z[f"{base}_voit"]
        coords = m298.les_coordonnees(pts, nrm, v["facteur"], T)
        dedans = m298.dans_le_volume(coords, vol.forme)
        prof = np.zeros((len(pts), 2 * T + 1), dtype=np.float32)
        if dedans.any():
            prof[dedans] = m298.les_profils(vol, coords[dedans])
        bon = dedans & ~m298.sans_matiere(prof)
        e = dict(c)
        for g, masque in (("m7_voit", voit), ("m7_ne_voit_rien", ~voit)):
            sel = prof[bon & masque]
            profil = m298.le_profil_moyen(sel)
            e[g] = {"les_rayons_lus": int(len(sel)), "la_saillance": la_saillance(profil), "le_profil_moyen": profil}
        e["la_lecture"] = la_lecture(e["m7_voit"]["la_saillance"], e["m7_ne_voit_rien"]["la_saillance"],
                                     e["m7_voit"]["les_rayons_lus"], e["m7_ne_voit_rien"]["les_rayons_lus"])
        cotes.append(e)
        print(json.dumps({k: (v_ if not isinstance(v_, dict) else {kk: vv for kk, vv in v_.items() if kk != "le_profil_moyen"})
                          for k, v_ in e.items()}, ensure_ascii=False), flush=True)
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"le_decalage_voxels": LE_DECALAGE, "les_u": [int(x) for x in LES_U], "le_minimum": LE_MINIMUM},
         "les_nappes_se_redonnent": plan["les_nappes_se_redonnent"], "les_pannes": plan["les_pannes"], "les_cotes": cotes,
         "les_morceaux": plan["les_morceaux"]}
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

    g = les_groupes([np.array([0.0, 20.0]), np.array([0.0]), np.array([0.0, -18.0]), np.array([0.0, 35.0]), np.empty(0)])
    v("★★★★ les groupes : une plage entre 5 et 30 voxels, de chaque côté, et rien d'autre",
      list(g) == [True, False, True, False, False], str(g))
    u = LES_U
    pic = list(np.exp(-((u - 20.0) / 3.0) ** 2) - np.exp(-((u - 8.0) / 2.0) ** 2))
    v("★★★ la saillance : un maximum à un pas après un creux", la_saillance(pic) > 1.5, str(la_saillance(pic)))
    plat = list(np.zeros(len(u)))
    v("★★★ un profil plat n'a pas de saillance", la_saillance(plat) == 0.0 and la_saillance([]) is None)
    v("★★★ les u vont de −1 à +41 voxels", u[0] == -1 and u[-1] == 41 and len(u) == 43)
    v("★★★★ le scan montre ce que m7 manque : la moitié de la saillance", la_lecture(1.0, 0.6, 500, 500)
      == "le scan montre la feuille que m7 manque")
    v("★★★★ il ne la montre pas : moins du quart", la_lecture(1.0, 0.2, 500, 500) == "il ne la montre pas")
    v("★★★ entre les deux : mêlé", la_lecture(1.0, 0.3, 500, 500) == "mêlé")
    v("★★★ sous 100 rayons dans un groupe : non lu", la_lecture(1.0, 0.9, 500, 99) == "non lu")
    vd = le_verdict({"les_cotes": [{"la_lecture": "le scan montre la feuille que m7 manque"}, {"la_lecture": "non lu"},
                                   {"la_lecture": "il ne la montre pas"}]})
    v("★★★ l'issue : k et j des côtés lus", vd["k"] == 1 and vd["j"] == 1 and vd["n"] == 2)

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
