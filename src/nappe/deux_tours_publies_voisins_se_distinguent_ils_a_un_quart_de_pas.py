"""Là où la chaîne les descend, à quel écart les tours publiés consécutifs 5753_0 à 5753_-7 sont-ils l'un de l'autre, et la lecture « retrouve » à un quart du pas nominal peut-elle attribuer une même surface à deux tours voisins ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LA MOINDRE SURFACE À MI-CHEMIN DE DEUX TOURS NE SOIT LUE. Ce qui était vu avant d'écrire : tout ce que
`296` à `336` publient, dont `R4-F522` (dans les boîtes des septièmes surfaces de la chaîne bornée, `5753_-6` est à 0,45 à 0,59 pas nominal
de `5753_-5`) ; et, dans les lectures de `333` et `334`, des surfaces qui retrouvent deux tours à la fois.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P133`. La lecture de `321` dit qu'une surface retrouve un tour si l'écart médian de ses
sommets en face est d'au plus un quart du pas nominal (18,02 voxels de 2,4 µm) et que la moitié au moins y sont. Si deux tours voisins sont à
moins d'un demi-pas nominal l'un de l'autre, une surface posée entre les deux est à un quart de pas de chacun, et la lecture la donne aux
deux. La descente de `330`, que `331` à `336` reprennent, compte un saut juste dès que la surface retrouve le tour attendu, même avec un
autre : si deux tours voisins peuvent être retrouvés ensemble, une descente peut être comptée juste sans l'être.

## Ce qui est fait

- **Les boîtes** : autour de chacune des huit graines de `321`, un cube de 1280 voxels de 2,4 µm de demi-côté, la demi-largeur du plan
  des nappes ; c'est là que la chaîne descend.
- **Les paires** : pour chaque graine et chaque paire de tours consécutifs, de `5753_0` et `5753_-1` à `5753_-6` et `5753_-7`, les sommets
  du premier dans la boîte, au plus 20 000 pris régulièrement, et leur écart au second le long de leur normale, par la comparaison de `321`.
- **La surface à mi-chemin** : chaque sommet du premier tour qui a le second en face, déplacé de la moitié de son écart le long de sa
  normale. Elle est lue contre les deux tours par la lecture de `329`, telle quelle.
- **La règle** : deux tours voisins sont **confondus** autour d'une graine si leur surface à mi-chemin les retrouve tous les deux. Une paire
  dont le premier tour a moins de 50 sommets en face du second n'est pas mesurée.

## Les issues

L'issue de la tranche : **sur les N paires de tours voisins mesurées autour des huit graines, une surface à mi-chemin retrouve les deux tours
m fois** ; et, déclaré avant : **la lecture sépare toujours deux tours voisins** si m = 0 ; **elle peut attribuer une même surface à deux
tours voisins** sinon.

## Rapporté à côté, qui ne décide rien

L'écart médian de chaque paire, en pas nominaux, et la part de ses sommets à moins d'un demi-pas nominal ; et, dans la descente de la chaîne
bornée telle que `336` l'a relevée, combien des surfaces comptées justes retrouvent aussi un autre tour.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : si les tours publiés sont à la bonne place ; ni ce que vaudrait une lecture plus stricte.

Usage :
    uv run python src/nappe/deux_tours_publies_voisins_se_distinguent_ils_a_un_quart_de_pas.py --verifier
    uv run python src/nappe/deux_tours_publies_voisins_se_distinguent_ils_a_un_quart_de_pas.py \\
        --json docs/mesures/deux_tours_publies_voisins_se_distinguent_ils_a_un_quart_de_pas.json
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

import la_nappe_de_m7_retrouve_t_elle_le_trace_humain_de_paris4 as m321  # noqa: E402
import la_chaine_qui_croit_tombe_t_elle_sur_les_tours_publies as m329  # noqa: E402
import jusqua_quel_tour_publie_la_chaine_qui_croit_descend_elle as m330  # noqa: E402

CE_QUE_336_A_PUBLIE = RACINE / "docs" / "mesures" / "pourquoi_aucune_chaine_ne_retrouve_t_elle_le_septieme_tour.json"
LA_DEMI_BOITE = 1280.0             # voxels de 2,4 µm : 32 mailles de 10 voxels du niveau 2
LE_MAXIMUM = 20000
LES_PAIRES = tuple((k, k - 1) for k in range(0, -7, -1))


def dans_la_boite(tour: dict, centre: np.ndarray, demi: float = LA_DEMI_BOITE, maximum: int = LE_MAXIMUM):
    """Les sommets du tour et leurs normales dans le cube de demi-côté `demi` autour de `centre`, au plus `maximum` pris régulièrement."""
    m = (np.abs(tour["points"] - centre) <= demi).all(axis=1)
    p, n = tour["points"][m], tour["normales"][m]
    if len(p) > maximum:
        k = np.linspace(0, len(p) - 1, maximum).round().astype(int)
        p, n = p[k], n[k]
    return p, n


def la_surface_a_mi_chemin(a: np.ndarray, an: np.ndarray, b: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Les sommets de `a` qui ont `b` en face, déplacés de la moitié de leur écart à `b` le long de leur normale ; et ces écarts."""
    t = m321.les_ecarts(a, an, b)
    m = np.isfinite(t)
    return a[m] + (t[m] / 2.0)[:, None] * an[m], t[m]


def sont_confondus(a_mi_chemin: dict) -> bool:
    """Deux tours sont confondus si la surface à mi-chemin les retrouve tous les deux."""
    return len(a_mi_chemin) == 2 and all(x == "retrouve" for x in a_mi_chemin.values())


def la_paire(ka: int, kb: int, ta: dict, tb: dict, centre: np.ndarray) -> dict:
    a, an = dans_la_boite(ta, centre)
    b, _ = dans_la_boite(tb, centre, maximum=10 ** 9)
    mi, t = la_surface_a_mi_chemin(a, an, b) if len(a) and len(b) else (np.zeros((0, 3)), np.zeros(0))
    e = {"les_tours": [ka, kb], "les_sommets_en_face": int(len(t))}
    if len(t) < m321.LE_MINIMUM:
        return dict(e, mesuree=False)
    lect = m329.les_lectures(mi, {ka: ta, kb: tb})
    e.update(mesuree=True, lecart_median_en_pas=round(float(np.median(np.abs(t))) / m321.LE_PAS_L0, 3),
             la_part_sous_un_demi_pas=round(float((np.abs(t) <= 2.0 * m321.LE_QUART).mean()), 4),
             a_mi_chemin={str(ka): lect[ka]["la_lecture"], str(kb): lect[kb]["la_lecture"]})
    e["confondus"] = sont_confondus(e["a_mi_chemin"])
    return e


def les_descentes_a_deux_tours(graines: list[dict]) -> list[dict]:
    """Pour chaque graine, côté moins, les surfaces que la descente de `330` compte justes, et combien d'entre elles retrouvent aussi un
    autre tour."""
    out = []
    for g in graines:
        c = g["les_cotes"]["moins"]
        surfaces = [{int(t): x for t, x in c["les_tours_de_la_nappe"].items()}]
        surfaces += [{int(t): x for t, x in s["les_tours"].items()} if "les_tours" in s else {} for s in c["les_surfaces"]]
        k0 = next((k for k, s in enumerate(surfaces) if m329.le_tour_de_la_nappe(s) is not None), None)
        if k0 is None:
            out.append({"le_rang": g["le_rang"], "comptees": 0, "a_deux_tours": 0})
            continue
        comptees = surfaces[k0 + 1:k0 + 1 + c["la_descente"]]
        deux = sum(1 for s in comptees if sum(1 for x in s.values() if x == "retrouve") >= 2)
        out.append({"le_rang": g["le_rang"], "comptees": len(comptees), "a_deux_tours": deux})
    return out


def le_verdict(d: dict) -> dict:
    ps = [p for g in d["les_graines"] for p in g["les_paires"] if p["mesuree"]]
    if not ps:
        return {"decidable": False, "lissue": "indécidable : aucune paire de tours voisins mesurée"}
    m = sum(1 for p in ps if p["confondus"])
    tete = (f"sur les {len(ps)} paires de tours voisins mesurées autour des {len(d['les_graines'])} graines, une surface à mi-chemin "
            f"retrouve les deux tours {m} fois")
    suite = "la lecture sépare toujours deux tours voisins" if m == 0 else "elle peut attribuer une même surface à deux tours voisins"
    return {"decidable": True, "N": len(ps), "m": m, "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    import le_tour_produit_porte_t_il_le_texte_du_segment as j296
    from la_spire_voisine_est_elle_a_un_pas import les_normales, lire_tifxyz

    t0 = time.monotonic()
    seg, sok, _ = lire_tifxyz(j296.LE_DOSSIER / j296.LES_SURFACES[0] / "maillage")
    sn, snok = les_normales(seg, sok)
    tours = {r: m329.lire_un_tour(r, m330.LES_TOURS) for r in m330.LES_TOURS}
    graines = []
    for rang, (i, j) in enumerate(m321.les_graines(seg, sok, snok), 1):
        centre = seg[i, j]
        ps = [la_paire(ka, kb, tours[ka], tours[kb], centre) for ka, kb in LES_PAIRES]
        graines.append({"le_rang": rang, "le_centre": [round(float(x), 1) for x in centre], "les_paires": ps})
        print(rang, [(p["les_tours"], p.get("lecart_median_en_pas"), p.get("confondus")) for p in ps], flush=True)
    d336 = json.loads(CE_QUE_336_A_PUBLIE.read_text())
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"la_demi_boite_voxels": LA_DEMI_BOITE, "le_maximum": LE_MAXIMUM, "le_quart_voxels": round(m321.LE_QUART, 3)},
         "les_graines": graines, "les_descentes_de_336": les_descentes_a_deux_tours(d336["les_graines"]["PHercParis4"])}
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

    k = np.arange(-300.0, 301.0, 20.0)
    xy = np.stack(np.meshgrid(k, k, indexing="ij"), axis=-1).reshape(-1, 2)

    def plan(z, signe=1.0):
        pts = np.concatenate([xy + 1000.0, np.full((len(xy), 1), z)], axis=1)
        return {"points": pts, "normales": np.tile([0.0, 0.0, signe], (len(pts), 1))}

    centre = np.array([1000.0, 1000.0, 400.0])
    pas = m321.LE_PAS_L0
    e = la_paire(0, -1, plan(400.0), plan(400.0 + 0.4 * pas), centre)
    v("★★★★★ à 0,4 pas nominal, la surface à mi-chemin est à 0,2 pas de chacun : les deux tours sont confondus",
      e["mesuree"] and e["confondus"] and e["lecart_median_en_pas"] == 0.4, str(e))
    e = la_paire(0, -1, plan(400.0), plan(400.0 + 0.7 * pas), centre)
    v("★★★★★ à 0,7 pas nominal, à 0,35 de chacun : ils ne sont pas confondus", e["mesuree"] and not e["confondus"]
      and e["a_mi_chemin"] == {"0": "ne retrouve pas", "-1": "ne retrouve pas"}, str(e))
    e = la_paire(0, -1, plan(400.0, -1.0), plan(400.0 + 0.4 * pas), centre)
    v("★★★★ le sens des normales ne change pas la surface à mi-chemin", e.get("confondus") is True, str(e))
    mi, t = la_surface_a_mi_chemin(plan(400.0)["points"], plan(400.0)["normales"], plan(440.0)["points"])
    v("★★★ la surface à mi-chemin est au milieu", np.allclose(mi[:, 2], 420.0) and np.allclose(t, 40.0))
    loin = {"points": plan(400.0)["points"] + np.array([5000.0, 0.0, 0.0]), "normales": plan(400.0)["normales"]}
    v("★★★★ un tour hors de la boîte n'est pas mesuré", not la_paire(0, -1, loin, plan(430.0), centre)["mesuree"])
    coin = {"points": plan(430.0)["points"][480:481], "normales": plan(430.0)["normales"][480:481]}
    e = la_paire(0, -1, plan(400.0), coin, centre)
    v("★★★★ moins de 50 sommets en face : la paire n'est pas mesurée", 0 < e["les_sommets_en_face"] < 50 and not e["mesuree"], str(e))
    v("★★★ la boîte garde au plus le maximum, pris régulièrement",
      len(dans_la_boite(plan(400.0), centre, maximum=100)[0]) == 100 and len(dans_la_boite(plan(400.0), centre)[0]) == len(xy))

    t_ = lambda *r: {str(x): ("retrouve" if x in r else "ne retrouve pas") for x in range(0, -8, -1)}  # noqa: E731
    cote = {"la_descente": 3, "les_tours_de_la_nappe": t_(),
            "les_surfaces": [{"les_tours": t_(0)}, {"les_tours": t_(-1)}, {"les_tours": t_(-2)}, {"les_tours": t_(-3, -4)},
                             {"les_tours": t_(-3, -4)}]}
    ds = les_descentes_a_deux_tours([{"le_rang": 4, "les_cotes": {"moins": cote}}])
    v("★★★★ confondus seulement si les deux tours sont retrouvés", sont_confondus({"0": "retrouve", "-1": "retrouve"})
      and not sont_confondus({"0": "retrouve", "-1": "ne retrouve pas"}) and not sont_confondus({"0": "retrouve"}))
    v("★★★★★ seules les surfaces que la descente compte sont lues, ni celle d'avant ni celle d'après",
      ds == [{"le_rang": 4, "comptees": 3, "a_deux_tours": 1}], str(ds))

    p_ = lambda c, m=True: {"mesuree": m, "confondus": c}  # noqa: E731
    vd = le_verdict({"les_graines": [{"les_paires": [p_(False), p_(False), p_(True, False)]}]})
    v("★★★★ aucune paire mesurée confondue : la lecture sépare toujours ; une paire non mesurée ne compte pas",
      vd["lissue"].endswith("la lecture sépare toujours deux tours voisins") and vd["N"] == 2)
    vd = le_verdict({"les_graines": [{"les_paires": [p_(False), p_(True)]}]})
    v("★★★★ une seule confondue suffit", vd["lissue"].endswith("elle peut attribuer une même surface à deux tours voisins"))
    v("★★★ sans paire mesurée, indécidable", not le_verdict({"les_graines": [{"les_paires": [p_(True, False)]}]})["decidable"])

    for e_ in echecs:
        print(f"  ÉCHEC {e_}")
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
