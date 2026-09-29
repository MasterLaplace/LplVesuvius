"""Le pas de la chaîne de m7 vient-il de m7 et du scan, ou du pas par défaut que le vote lui donne ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UNE SEULE CHAÎNE NE SOIT TIRÉE AVEC UN AUTRE PAS PAR DÉFAUT. Ce qui était vu avant d'écrire : tout
ce que `303` à `315` publient, dont `R4-F496` : prolongée à seize sauts, la chaîne tient sur six côtés sur dix, mais `m7` n'appuie
plus que 15 à 16 % des points au seizième saut, et le pas médian converge sur 20 à 21 voxels, le pas par défaut du vote.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE. Si le vote pose ce que `m7` ne voit pas au pas qu'on lui donne, la chaîne peut avancer de 20 voxels
parce qu'on le lui a dit, et « au plus dense du scan à 20 voxels » ne serait qu'un empilement régulier retrouvé par un paramètre. Le
seul moyen de le savoir est de lui donner un autre pas et de regarder si elle le suit.

## Ce qui est fait

- **Les côtés** : les quatre qui tiennent seize sauts sur les graines 4 et 7 (`315`), depuis les nappes de `301` retirées de `m7`.
- **Trois pas par défaut** : 16, 20 et 24 voxels, donnés au saut de `300` à la place du pas du rouleau, partout où il s'en sert (la
  portée du rayon, le départ d'un point qui ne voit rien, le demi-pas du vote) ; rien d'autre ne change.
- **La lecture, à chaque saut** : le pas médian de tous les points valides, appuyés ou non, et le plus dense du profil moyen du scan.

## Les issues

Par côté et par pas donné, le pas médian des sauts 9 à 16. **Le pas vient de m7 et du scan** si, à 16 et à 24 voxels, il reste à
au plus 2 voxels de celui obtenu à 20 ; **il suit le pas donné** s'il s'en écarte de plus de la moitié de l'écart, 2 voxels, vers le
pas donné ; **mêlé** sinon. L'issue de la tranche : sur k des quatre côtés, le pas vient de `m7` et du scan.

## Rapporté à côté, qui ne décide rien

À chaque saut et chaque pas donné, le plus dense du profil moyen, et la part des points appuyés sur `m7`.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : que les spires soient consécutives.

Usage :
    uv run python src/nappe/le_pas_de_la_chaine_vient_il_de_m7_ou_du_pas_par_defaut.py --verifier
    uv run python src/nappe/le_pas_de_la_chaine_vient_il_de_m7_ou_du_pas_par_defaut.py --preparer
    uv run python src/nappe/le_pas_de_la_chaine_vient_il_de_m7_ou_du_pas_par_defaut.py --lire 4
    uv run python src/nappe/le_pas_de_la_chaine_vient_il_de_m7_ou_du_pas_par_defaut.py \\
        --json docs/mesures/le_pas_de_la_chaine_vient_il_de_m7_ou_du_pas_par_defaut.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
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

LE_DOSSIER = RACINE / "data" / "pas_par_defaut"
LES_SURFACES_PREPAREES = LE_DOSSIER / "surfaces"
LE_PLAN = LE_DOSSIER / "plan.json"
LES_PAS = (16.0, 20.0, 24.0)
LES_GRAINES = (4, 7)
LES_SAUTS = 16
LA_TOLERANCE = 2.0


@contextmanager
def le_pas_donne(pas: float):
    """Le pas par défaut du saut de `300`, remplacé le temps d'un bloc et rendu ensuite, quoi qu'il arrive."""
    avant = m300.LE_PAS_0358
    m300.LE_PAS_0358 = pas
    try:
        yield
    finally:
        m300.LE_PAS_0358 = avant


def le_pas_tardif(pas_par_saut: list) -> float | None:
    """Le pas médian des sauts 9 à 16."""
    xs = [x for x in pas_par_saut[8:16] if x is not None]
    return round(float(np.median(xs)), 2) if xs else None


def la_lecture(p16: float | None, p20: float | None, p24: float | None) -> str:
    if None in (p16, p20, p24):
        return "non lue"
    if abs(p16 - p20) <= LA_TOLERANCE and abs(p24 - p20) <= LA_TOLERANCE:
        return "le pas vient de m7 et du scan"
    if p16 < p20 - LA_TOLERANCE and p24 > p20 + LA_TOLERANCE:
        return "il suit le pas donné"
    return "mêlé"


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    lus = [c for c in d["les_cotes"] if c["la_lecture"] != "non lue"]
    if not lus:
        return {"decidable": False, "lissue": "indécidable : aucun côté lu"}
    k = sum(1 for c in lus if c["la_lecture"] == "le pas vient de m7 et du scan")
    j = sum(1 for c in lus if c["la_lecture"] == "il suit le pas donné")
    return {"decidable": True, "k": k, "j": j, "n": len(lus),
            "lissue": f"sur {k} des {len(lus)} côtés, le pas de la chaîne vient de m7 et du scan ; sur {j}, il suit le pas donné"}


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
    for rang in LES_GRAINES:
        r = r302["les_nappes"][rang]
        for nom, cote in m303.LES_COTES:
            e = {"le_rang": rang, "le_cote": nom, "les_pas": {}}
            for pas in LES_PAS:
                with le_pas_donne(pas):
                    chaine = m303.enchainer(r["la_nappe"], r["valide"], cote, lv, sauts=LES_SAUTS)
                sauts = []
                for h, s in enumerate(chaine, 1):
                    a = np.abs(s["le_pas"][s["valide"] & np.isfinite(s["le_pas"])])
                    sauts.append({"le_saut": h, "le_pas_median_voxels": round(float(np.median(a)), 2) if len(a) else None,
                                  "la_part_appuyee": round(float(s["appui"].mean()), 4)})
                    sn, snok = les_normales(s["la_spire"], s["valide"])
                    mm = s["valide"] & snok
                    pts, nrm = s["la_spire"][mm], sn[mm]
                    cle = f"g{rang}_{nom}_{pas:g}_{h}"
                    f = LES_SURFACES_PREPAREES / f"PHerc0358__{cle}.npz"
                    np.savez_compressed(f, points=pts, normales=nrm, groupe=np.zeros(len(pts), dtype=int),
                                        juge=np.full(len(pts), np.nan), groupes=np.array([json.dumps([rang, nom, pas, h])]))
                    if len(pts):
                        c = m298.les_coordonnees(pts, nrm, v["facteur"], T)
                        tous |= m298.les_morceaux_complets(c[m298.dans_le_volume(c, vol.forme)], vol.taille)
                    plan["les_surfaces"][cle] = {"le_fichier": str(f.relative_to(RACINE)), "les_points": len(pts)}
                e["les_pas"][f"{pas:g}"] = sauts
            plan["les_cotes"].append(e)
            print(json.dumps({"le_rang": rang, "le_cote": nom,
                              "pas": {k: [x["le_pas_median_voxels"] for x in v_] for k, v_ in e["les_pas"].items()}}), flush=True)
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
    cotes = []
    for c in plan["les_cotes"]:
        e = {"le_rang": c["le_rang"], "le_cote": c["le_cote"], "les_pas": {}}
        for pas, sauts in c["les_pas"].items():
            lus = []
            for s in sauts:
                info = plan["les_surfaces"][f"g{c['le_rang']}_{c['le_cote']}_{pas}_{s['le_saut']}"]
                r = m299.juger(vol, RACINE / info["le_fichier"], v["facteur"], T)
                lus.append(dict(s, le_plus_dense=m309.le_plus_dense(r[0]["le_profil_moyen"]) if r else None))
            e["les_pas"][pas] = lus
        tard = {pas: le_pas_tardif([x["le_pas_median_voxels"] for x in lus]) for pas, lus in e["les_pas"].items()}
        e["le_pas_tardif"] = tard
        e["la_lecture"] = la_lecture(tard.get("16"), tard.get("20"), tard.get("24"))
        cotes.append(e)
        print(json.dumps({"le_rang": e["le_rang"], "le_cote": e["le_cote"], "tard": tard, "lecture": e["la_lecture"]},
                         ensure_ascii=False), flush=True)
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"les_pas": list(LES_PAS), "les_graines": list(LES_GRAINES), "les_sauts": LES_SAUTS,
                            "la_tolerance_voxels": LA_TOLERANCE},
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

    avant = m300.LE_PAS_0358
    with le_pas_donne(16.0):
        dedans = m300.LE_PAS_0358
    v("★★★★ le pas donné remplace celui du saut dans le bloc, et est rendu après", dedans == 16.0 and m300.LE_PAS_0358 == avant)
    try:
        with le_pas_donne(24.0):
            raise RuntimeError("x")
    except RuntimeError:
        pass
    v("★★★ le pas est rendu même quand le bloc lève", m300.LE_PAS_0358 == avant)
    v("★★★ le pas tardif : la médiane des sauts 9 à 16", le_pas_tardif([100.0] * 8 + [20.0, 21.0, 19.0, 20.0, 20.0, 22.0, 20.0,
                                                                                      20.0]) == 20.0)
    v("★★★★ un pas qui ne bouge pas avec le pas donné vient de m7 et du scan",
      la_lecture(19.5, 20.0, 21.5) == "le pas vient de m7 et du scan")
    v("★★★★ un pas qui suit le pas donné", la_lecture(16.0, 20.0, 24.0) == "il suit le pas donné")
    v("★★★ un pas qui ne suit qu'un côté : mêlé", la_lecture(16.0, 20.0, 21.0) == "mêlé")
    v("★★★ la tolérance de 2 voxels est incluse", la_lecture(18.0, 20.0, 22.0) == "le pas vient de m7 et du scan")
    v("★★★ sans un des trois pas : non lue", la_lecture(None, 20.0, 24.0) == "non lue")
    vd = le_verdict({"les_cotes": [{"la_lecture": "le pas vient de m7 et du scan"}, {"la_lecture": "il suit le pas donné"},
                                   {"la_lecture": "non lue"}]})
    v("★★★ l'issue : k et j sur les côtés lus", vd["k"] == 1 and vd["j"] == 1 and vd["n"] == 2)

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
