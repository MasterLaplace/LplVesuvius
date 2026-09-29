"""Les points d'une spire de la chaîne que m7 n'appuie pas sont-ils au cœur d'une feuille, au pas donné de 20 voxels et pas à 16 ni à 24 ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LE PLUS DENSE NE SOIT LU À PART SUR LES POINTS NON APPUYÉS. Ce qui était vu avant d'écrire : tout
ce que `303` à `316` publient, dont `R4-F497` : le pas de la chaîne suit le pas donné au vote, et le plus dense moyenné sur toute la
spire reste à 0 à 2 voxels quel que soit ce pas.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P114`. Une spire mêle deux sortes de points : ceux que le vote pose sur une plage de
`m7`, et ceux qu'il pose à la médiane de ses voisins ou au pas donné. `316` montre que les premiers dominent le profil moyen. Lus à
part, les seconds disent ce que `315` affirmait sans pouvoir le mesurer : si un point posé au pas de 20 voxels tombe au cœur d'une
feuille, c'est que l'empilement est régulier à ce pas ; s'il y tombe aussi à 16 et à 24, le juge ne voit rien.

## Ce qui est fait

- **Les chaînes** : celles de `316`, graines 4 et 7, deux côtés chacune, seize sauts, aux pas donnés de 16, 20 et 24 voxels.
- **Deux groupes par spire** : les points appuyés sur `m7`, et les autres.
- **La lecture** : pour chaque groupe, le profil moyen du juge de `301`, son plus dense, et son amplitude.
- **Au cœur** : le plus dense médian des sauts 9 à 16 à au plus 5 voxels de la spire, et une amplitude médiane d'au moins 0,5, sans
  quoi le profil n'a pas de maximum à lire.

## Les issues

Par côté, sur les points non appuyés : **l'empilement est régulier au pas de 20** s'ils sont au cœur au pas de 20 et hors du cœur à
16 et à 24 ; **le juge ne voit rien** s'ils sont au cœur aux trois pas ; **hors du cœur même à 20** s'ils ne le sont pas au pas de
20 ; **mêlé** sinon. L'issue de la tranche : sur k des quatre côtés, l'empilement est régulier au pas de 20.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : que les spires soient consécutives.

Usage :
    uv run python src/nappe/les_points_que_m7_nappuie_pas_sont_ils_au_coeur_dune_feuille.py --verifier
    uv run python src/nappe/les_points_que_m7_nappuie_pas_sont_ils_au_coeur_dune_feuille.py --preparer
    uv run python src/nappe/les_points_que_m7_nappuie_pas_sont_ils_au_coeur_dune_feuille.py --lire 4
    uv run python src/nappe/les_points_que_m7_nappuie_pas_sont_ils_au_coeur_dune_feuille.py \\
        --json docs/mesures/les_points_que_m7_nappuie_pas_sont_ils_au_coeur_dune_feuille.json
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
import le_pas_de_la_chaine_vient_il_de_m7_ou_du_pas_par_defaut as m316  # noqa: E402

LE_DOSSIER = RACINE / "data" / "points_non_appuyes"
LES_SURFACES_PREPAREES = LE_DOSSIER / "surfaces"
LE_PLAN = LE_DOSSIER / "plan.json"
LAMPLITUDE_MINIMALE = 0.5
LES_GROUPES = ("appuyes", "non_appuyes")


def au_coeur(plus_denses: list, amplitudes: list, quart: int) -> bool | None:
    """Au cœur si le plus dense médian des sauts 9 à 16 est à au plus `quart` et l'amplitude médiane d'au moins 0,5."""
    xs = [x for x in plus_denses[8:16] if x is not None]
    am = [x for x in amplitudes[8:16] if x is not None]
    if not xs or not am:
        return None
    return abs(float(np.median(xs))) <= quart and float(np.median(am)) >= LAMPLITUDE_MINIMALE


def la_lecture(c16: bool | None, c20: bool | None, c24: bool | None) -> str:
    if None in (c16, c20, c24):
        return "non lue"
    if c20 and not c16 and not c24:
        return "l'empilement est régulier au pas de 20"
    if c20 and c16 and c24:
        return "le juge ne voit rien"
    if not c20:
        return "hors du cœur même à 20"
    return "mêlé"


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    lus = [c for c in d["les_cotes"] if c["la_lecture"] != "non lue"]
    if not lus:
        return {"decidable": False, "lissue": "indécidable : aucun côté lu"}
    k = sum(1 for c in lus if c["la_lecture"] == "l'empilement est régulier au pas de 20")
    return {"decidable": True, "k": k, "n": len(lus),
            "lissue": f"sur {k} des {len(lus)} côtés, les points que m7 n'appuie pas disent l'empilement régulier au pas de 20"}


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
    for rang in m316.LES_GRAINES:
        r = r302["les_nappes"][rang]
        for nom, cote in m303.LES_COTES:
            e = {"le_rang": rang, "le_cote": nom, "les_pas": {}}
            for pas in m316.LES_PAS:
                with m316.le_pas_donne(pas):
                    chaine = m303.enchainer(r["la_nappe"], r["valide"], cote, lv, sauts=m316.LES_SAUTS)
                e["les_pas"][f"{pas:g}"] = []
                for h, s in enumerate(chaine, 1):
                    sn, snok = les_normales(s["la_spire"], s["valide"])
                    mm = s["valide"] & snok
                    pts, nrm, ap = s["la_spire"][mm], sn[mm], s["appui"][mm]
                    cle = f"g{rang}_{nom}_{pas:g}_{h}"
                    f = LES_SURFACES_PREPAREES / f"PHerc0358__{cle}.npz"
                    np.savez_compressed(f, points=pts, normales=nrm, groupe=np.where(ap, 0, 1).astype(int),
                                        juge=np.full(len(pts), np.nan), groupes=np.array([json.dumps(g) for g in LES_GROUPES]))
                    if len(pts):
                        c = m298.les_coordonnees(pts, nrm, v["facteur"], T)
                        tous |= m298.les_morceaux_complets(c[m298.dans_le_volume(c, vol.forme)], vol.taille)
                    plan["les_surfaces"][cle] = {"le_fichier": str(f.relative_to(RACINE)), "les_points": len(pts),
                                                 "les_appuyes": int(ap.sum())}
                    e["les_pas"][f"{pas:g}"].append({"le_saut": h, "les_appuyes": int(ap.sum()), "les_points": len(pts)})
            plan["les_cotes"].append(e)
            print(json.dumps({"le_rang": rang, "le_cote": nom}), flush=True)
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
        e = {"le_rang": c["le_rang"], "le_cote": c["le_cote"], "les_pas": {}, "au_coeur": {}}
        for pas, sauts in c["les_pas"].items():
            lus = []
            for s in sauts:
                info = plan["les_surfaces"][f"g{c['le_rang']}_{c['le_cote']}_{pas}_{s['le_saut']}"]
                r = {json.dumps(x["le_groupe"]).strip('"'): x for x in m299.juger(vol, RACINE / info["le_fichier"],
                                                                                 v["facteur"], T)}
                ligne = dict(s)
                for g in LES_GROUPES:
                    x = r.get(g)
                    rel = m298.le_relief(x["le_profil_moyen"]) if x else m298.le_relief([])
                    ligne[g] = {"le_plus_dense": m309.le_plus_dense(x["le_profil_moyen"]) if x else None,
                                "lamplitude": rel["lamplitude"], "les_points_juges": x["les_points_juges"] if x else 0}
                lus.append(ligne)
            e["les_pas"][pas] = lus
            e["au_coeur"][pas] = {g: au_coeur([x[g]["le_plus_dense"] for x in lus], [x[g]["lamplitude"] for x in lus], quart)
                                  for g in LES_GROUPES}
        a = {p: e["au_coeur"][p]["non_appuyes"] for p in ("16", "20", "24")}
        e["la_lecture"] = la_lecture(a["16"], a["20"], a["24"])
        cotes.append(e)
        print(json.dumps({"le_rang": e["le_rang"], "le_cote": e["le_cote"], "au_coeur": e["au_coeur"],
                          "lecture": e["la_lecture"]}, ensure_ascii=False), flush=True)
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"les_pas": list(m316.LES_PAS), "le_quart_de_pas_voxels": quart,
                            "lamplitude_minimale": LAMPLITUDE_MINIMALE},
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

    v("★★★★ au cœur : plus dense médian des sauts 9 à 16 à au plus un quart de pas, et une amplitude",
      au_coeur([20] * 8 + [0, 1, -1, 2, 0, 0, 1, -2], [0.1] * 8 + [0.9] * 8, 5) is True)
    v("★★★★ un profil plat n'est pas au cœur, même avec un plus dense à 0",
      au_coeur([0] * 16, [0.2] * 16, 5) is False)
    v("★★★ un plus dense à 8 voxels n'est pas au cœur", au_coeur([8] * 16, [1.0] * 16, 5) is False)
    v("★★★ sans lecture, rien", au_coeur([None] * 16, [None] * 16, 5) is None)
    v("★★★★ au cœur à 20 seulement : l'empilement est régulier au pas de 20",
      la_lecture(False, True, False) == "l'empilement est régulier au pas de 20")
    v("★★★★ au cœur aux trois pas : le juge ne voit rien", la_lecture(True, True, True) == "le juge ne voit rien")
    v("★★★ pas au cœur à 20", la_lecture(True, False, True) == "hors du cœur même à 20")
    v("★★★ au cœur à 20 et à un seul autre : mêlé", la_lecture(True, True, False) == "mêlé"
      and la_lecture(False, True, True) == "mêlé")
    v("★★★ une lecture manquante : non lue", la_lecture(None, True, False) == "non lue")
    vd = le_verdict({"les_cotes": [{"la_lecture": "l'empilement est régulier au pas de 20"}, {"la_lecture": "mêlé"}]})
    v("★★★ l'issue : k des côtés lus", vd["k"] == 1 and vd["n"] == 2)

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
