"""Le juge sans référent de 301 note-t-il une surface décalée d'un demi-pas comme hors de sa feuille, et d'un pas entier comme sur une feuille ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UNE SEULE SURFACE DÉCALÉE NE SOIT JUGÉE. Ce qui était vu avant d'écrire : tout ce que `298` à
`306` publient, dont le constat de `306` : les spires − de la graine 3 de PHerc0358, appuyées sur `m7` sur 1 à 4 % de leurs points
seulement, presque entièrement la surface précédente décalée de 20 voxels, sont notées sur leur feuille à Z 26,325.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P107`. Le juge de `301` a été étalonné contre des rampes, qui traversent
l'empilement ; il n'a jamais été confronté à une surface parallèle à sa feuille mais posée entre deux feuilles. Si un empilement
régulier suffit à le satisfaire à un pas de n'importe quelle feuille, il le satisfait peut-être aussi à un demi-pas, et « suit sa
feuille » voudrait dire « est parallèle à l'empilement ».

## Ce qui est fait

- **PHercParis4, où la réponse est connue** : les vingt-quatre blocs de l'étalonnage de `301`, le tracé humain de chaque bloc,
  décalé le long de ses normales de −1 à +1 pas par quarts de pas (neuf décalages, le pas du segment). Le décalage nul doit redonner
  le Z de `301` bloc pour bloc.
- **PHerc0358, rapporté** : les nappes croissantes de `305` qui suivent leur feuille (graines 3, 6 et 7), retirées de `m7` à
  l'identique, aux mêmes neuf décalages, au pas du rouleau (20 voxels).
- **Le juge** : celui de `301`, sans rien y changer : pour chaque surface décalée, huit rampes plantées dans ses propres points,
  Z ≥ 3.

## L'issue

**Le juge sépare la feuille de l'entre-deux** si, sur PHercParis4, le tracé non décalé passe sur au moins 90 % des blocs et le tracé
décalé d'un demi-pas, des deux côtés réunis, sur au plus 5 % des 48 comparaisons, sans aucun Z absent, la règle de l'étalonnage
de `301` ; sinon **il ne la sépare pas**, avec la part. Indécidable si une lecture échoue ou si le décalage nul ne redonne pas `301`.

## Rapporté à côté, qui ne décide rien

La part des blocs à Z ≥ 3 à chaque décalage, dont ±1 pas, la feuille voisine ; et le Z de chaque nappe de PHerc0358 à chaque
décalage.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : ce que vaut le juge sur un empilement irrégulier, ni sur quelle feuille une surface qui passe
se trouve.

Usage :
    uv run python src/nappe/le_juge_voit_il_lentre_deux_feuilles.py --verifier
    uv run python src/nappe/le_juge_voit_il_lentre_deux_feuilles.py --preparer
    uv run python src/nappe/le_juge_voit_il_lentre_deux_feuilles.py --lire 4
    uv run python src/nappe/le_juge_voit_il_lentre_deux_feuilles.py --json docs/mesures/le_juge_voit_il_lentre_deux_feuilles.json
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
import une_nappe_qui_refuse_de_changer_de_feuille_suit_elle_encore_sa_feuille as m305  # noqa: E402

LE_DOSSIER = RACINE / "data" / "juge_et_entre_deux"
LES_SURFACES_PREPAREES = LE_DOSSIER / "surfaces"
LE_PLAN = LE_DOSSIER / "plan.json"
CE_QUE_305_A_PUBLIE = m305.RACINE / "docs" / "mesures" / "une_nappe_qui_refuse_de_changer_de_feuille_suit_elle_encore_sa_feuille.json"
LES_DECALAGES = (-1.0, -0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75, 1.0)   # en pas
LE_TAUX_SUR_LA_FEUILLE = m301.LE_TAUX_DU_TRACE
LE_TAUX_ENTRE_DEUX = m301.LE_TAUX_DES_RAMPES


def le_nom(d: float) -> str:
    """Le nom d'un décalage, sans point ni signe moins, pour un nom de fichier."""
    return ("m" if d < 0 else "p") + f"{abs(d):g}".replace(".", "_")


def decaler(points: np.ndarray, normales: np.ndarray, d: float, pas: float) -> np.ndarray:
    return points + (d * pas) * normales


def le_taux(zs: list) -> float | None:
    """La part des Z au moins égaux à 3 ; un Z absent compte comme un échec, pas comme une abstention."""
    if not zs:
        return None
    return round(sum(1 for z in zs if z is not None and z >= m300.LE_Z_MINIMUM) / len(zs), 4)


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("le_decalage_nul_redonne_301"):
        return {"decidable": False, "lissue": "indécidable : le décalage nul ne redonne pas le Z de 301"}
    blocs = d["paris4"]["les_blocs"]
    sur = le_taux([b["les_z"]["p0"] for b in blocs])
    entre = le_taux([b["les_z"][k] for b in blocs for k in ("m0_5", "p0_5")])
    n = 2 * len(blocs)
    passes = sum(1 for b in blocs for k in ("m0_5", "p0_5") if b["les_z"][k] is not None
                 and b["les_z"][k] >= m300.LE_Z_MINIMUM)
    absents = sum(1 for b in blocs for k in ("p0", "m0_5", "p0_5") if b["les_z"][k] is None)
    separe = (absents == 0 and sur is not None and entre is not None and sur >= LE_TAUX_SUR_LA_FEUILLE
              and entre <= LE_TAUX_ENTRE_DEUX)
    return {"decidable": True, "separe": separe, "le_taux_sur_la_feuille": sur, "le_taux_entre_deux": entre,
            "les_absents": absents,
            "lissue": ("le juge note la surface décalée d'un demi-pas hors de sa feuille : il sépare la feuille de l'entre-deux"
                       if separe else f"le juge note la surface décalée d'un demi-pas sur sa feuille dans {passes} des {n} "
                                      "comparaisons : il ne sépare pas la feuille de l'entre-deux")}


# ── Les étapes ─────────────────────────────────────────────────────────────────────────────────────────────────────

def les_familles_de_paris4() -> tuple[dict, list]:
    import le_tour_produit_porte_t_il_le_texte_du_segment as j296
    from la_spire_voisine_est_elle_a_un_pas import les_normales, lire_tifxyz
    from que_montrent_ces_deux_vues import PAS_EN_VOXELS

    k = m298.LE_SURECHANTILLONNAGE["PHercParis4"]
    d301 = json.loads(m301.RACINE.joinpath("docs", "mesures",
                                           "les_nappes_de_m7_suivent_elles_leur_feuille_sur_des_graines_neuves.json").read_text())
    blocs = [b["le_bloc"] for b in d301["letalonnage"]["les_blocs"]]
    pts0, ok0, esp = lire_tifxyz(j296.LE_DOSSIER / j296.LES_SURFACES[0] / "maillage")
    out: dict = {}
    for b in blocs:
        lignes, colonnes = j296.les_mailles_dune_bande(*b, 1, esp)
        L, C = lignes[lignes < ok0.shape[0]], colonnes[colonnes < ok0.shape[1]]
        sp, sok = m298.surechantillonner(pts0[np.ix_(L, C)], ok0[np.ix_(L, C)], k)
        nn, nok = les_normales(sp, sok)
        for d in LES_DECALAGES:
            dp = decaler(sp, nn, d, float(PAS_EN_VOXELS))
            for nom, (p, m, nr) in m300.la_famille(le_nom(d), dp, sok, nn, nok, float(PAS_EN_VOXELS), esp / k).items():
                out.setdefault(nom, []).append({"le_bloc": list(b), "points": p[m], "normales": nr[m]})
    return out, [list(b) for b in blocs]


def les_familles_de_0358() -> tuple[dict, bool, list]:
    from le_transfert_retrouve_t_il_la_spire_voisine import lecteur_du_depot, lire_les_valeurs
    from la_spire_voisine_est_elle_a_un_pas import les_normales

    from zarr_depth import array_meta

    url = f"{m298.BUCKET}/{m299.LA_PREDICTION_0358}"
    pred = array_meta(url, 0, 120.0)
    lire_, stats = lecteur_du_depot(pred, m300.LE_CACHE_M7, "m7_L0", m299.LA_PREDICTION_0358, 0)
    lv = lambda idx: lire_les_valeurs(idx, pred, lire_)  # noqa: E731
    graines = {tuple((g["x"], g["y"], g["z"])): g for g in m301.les_graines_neuves()}
    d305 = json.loads(CE_QUE_305_A_PUBLIE.read_text())
    out, identiques = {}, True
    for g in d305["les_graines"]:
        if g["la_nappe"] != "suit sa feuille":
            continue
        src = graines[tuple(g["la_graine"])]
        nz, ny, nx = src["normale_zyx"]
        r = m305.la_nappe_croissante(tuple(g["la_graine"]), (nx, ny, nz), lv)
        identiques &= m305.la_carte(r["le_decalage"], r["valide"]) == g["la_carte"]
        nn, nok = les_normales(r["la_nappe"], r["valide"])
        for d in LES_DECALAGES:
            dp = decaler(r["la_nappe"], nn, d, m300.LE_PAS_0358)
            for nom, (p, m, nr) in m300.la_famille(f"g{g['le_rang']}_{le_nom(d)}", dp, r["valide"], nn, nok, m300.LE_PAS_0358,
                                                   m300.LE_PAS_DU_PLAN).items():
                out[nom] = [{"la_piece": [g["le_rang"], d], "points": p[m], "normales": nr[m]}]
    return out, bool(identiques), list(stats["pannes"])


def preparer() -> dict:
    t0 = time.monotonic()
    paris, blocs = les_familles_de_paris4()
    prix, identiques, pannes = les_familles_de_0358()
    plan = {"les_blocs": blocs, "les_nappes_se_redonnent": identiques, "les_pannes": pannes, "les_surfaces": {},
            "les_morceaux": {}}
    LES_SURFACES_PREPAREES.mkdir(parents=True, exist_ok=True)
    for volume, surfaces, cle in (("PHercParis4", paris, "le_bloc"), ("PHerc0358", prix, "la_piece")):
        v = m298.LES_VOLUMES[volume]
        vol = m298.LesMorceaux(volume, v["url"], v["niveau"])
        T = m298.la_demi_fenetre(volume)
        tous = set()
        for nom, morceaux in surfaces.items():
            f = LES_SURFACES_PREPAREES / f"{volume}__{nom}.npz"
            pts = np.concatenate([m["points"] for m in morceaux])
            nrm = np.concatenate([m["normales"] for m in morceaux])
            np.savez_compressed(f, points=pts, normales=nrm,
                                groupe=np.concatenate([np.full(len(m["points"]), i) for i, m in enumerate(morceaux)]),
                                juge=np.full(len(pts), np.nan), groupes=np.array([json.dumps(m[cle]) for m in morceaux]))
            if len(pts):
                coords = m298.les_coordonnees(pts, nrm, v["facteur"], T)
                tous |= m298.les_morceaux_complets(coords[m298.dans_le_volume(coords, vol.forme)], vol.taille)
            plan["les_surfaces"][f"{volume}__{nom}"] = {"le_fichier": str(f.relative_to(RACINE)), "les_points": len(pts)}
        cles = sorted(tous)
        (LE_DOSSIER / f"morceaux_{volume}.json").write_text(json.dumps(cles))
        plan["les_morceaux"][volume] = {"combien": len(cles)}
    plan["les_secondes"] = round(time.monotonic() - t0, 1)
    LE_PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=1))
    return {k: v_ for k, v_ in plan.items() if k != "les_surfaces"}


def lire(ouvriers: int = 4) -> dict:
    out = {}
    for volume, v in m298.LES_VOLUMES.items():
        cles = [tuple(c) for c in json.loads((LE_DOSSIER / f"morceaux_{volume}.json").read_text())]
        vol = m298.LesMorceaux(volume, v["url"], v["niveau"])
        comptes = {"deja": 0, "tire": 0, "absent": 0}
        with ThreadPoolExecutor(ouvriers) as ex:
            for r in ex.map(lambda c: vol.tirer(*c), cles):
                comptes[r] += 1
        out[volume] = dict(comptes, combien=len(cles))
    return out


def le_z_du_groupe(res: dict, base: str, i: int) -> float | None:
    if not res.get(base) or len(res[base]) <= i:
        return None
    a = res[base][i]["lalignement"]
    tem = [(res.get(f"{base}__{r}_{ph:g}") or [{}] * (i + 1))[i].get("lalignement") for r in m298.LES_PENTES
           for ph in m300.LES_PHASES]
    return m300.le_z(a, tem)


def mesurer() -> dict:
    t0 = time.monotonic()
    plan = json.loads(LE_PLAN.read_text())
    res: dict = {}
    for volume, v in m298.LES_VOLUMES.items():
        vol = m298.LesMorceaux(volume, v["url"], v["niveau"])
        T = m298.la_demi_fenetre(volume)
        for cle, info in plan["les_surfaces"].items():
            if cle.startswith(volume + "__"):
                res[cle] = m299.juger(vol, RACINE / info["le_fichier"], v["facteur"], T)
        print(f"{volume} ({time.monotonic() - t0:.0f} s)", flush=True)
    d301 = {tuple(b["le_bloc"]): b for b in json.loads(m301.RACINE.joinpath(
        "docs", "mesures", "les_nappes_de_m7_suivent_elles_leur_feuille_sur_des_graines_neuves.json").read_text())[
        "letalonnage"]["les_blocs"]}
    blocs, redonne = [], True
    for i, b in enumerate(plan["les_blocs"]):
        zs = {le_nom(dd): le_z_du_groupe(res, f"PHercParis4__{le_nom(dd)}", i) for dd in LES_DECALAGES}
        redonne &= zs["p0"] == d301[tuple(b)]["le_segment"]
        blocs.append({"le_bloc": b, "les_z": zs, "le_z_de_301": d301[tuple(b)]["le_segment"]})
    courbe = [{"le_decalage_en_pas": dd, "le_taux": le_taux([x["les_z"][le_nom(dd)] for x in blocs])} for dd in LES_DECALAGES]
    rangs = sorted({int(k.split("__g")[1].split("_")[0]) for k in plan["les_surfaces"] if k.startswith("PHerc0358__g")})
    nappes = [{"le_rang": r, "les_z": {le_nom(dd): le_z_du_groupe(res, f"PHerc0358__g{r}_{le_nom(dd)}", 0)
                                       for dd in LES_DECALAGES}} for r in rangs]
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"les_decalages_en_pas": list(LES_DECALAGES), "le_taux_sur_la_feuille": LE_TAUX_SUR_LA_FEUILLE,
                            "le_taux_entre_deux": LE_TAUX_ENTRE_DEUX, "le_z_minimum": m300.LE_Z_MINIMUM},
         "le_decalage_nul_redonne_301": bool(redonne), "les_nappes_se_redonnent": plan["les_nappes_se_redonnent"],
         "les_pannes": plan["les_pannes"], "paris4": {"les_blocs": blocs, "la_courbe": courbe},
         "phercs0358": {"les_nappes": nappes}, "les_morceaux": plan["les_morceaux"]}
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

    v("★★★ un nom par décalage, distinct, sans point ni signe moins",
      [le_nom(d) for d in LES_DECALAGES] == ["m1", "m0_75", "m0_5", "m0_25", "p0", "p0_25", "p0_5", "p0_75", "p1"])
    p = np.zeros((2, 2, 3))
    n = np.zeros((2, 2, 3))
    n[..., 2] = 1.0
    v("★★★ décaler : le long de la normale, en fractions de pas", np.allclose(decaler(p, n, -0.5, 20.0)[..., 2], -10.0))
    v("★★★★ le taux : un Z absent compte comme un échec", le_taux([3.0, None, 2.9, 10.0]) == 0.5 and le_taux([]) is None)

    def blocs_(sur, entre):
        return [{"les_z": {"p0": sur[i], "m0_5": entre[2 * i], "p0_5": entre[2 * i + 1]}} for i in range(len(sur))]

    ok_ = le_verdict({"le_decalage_nul_redonne_301": True, "paris4": {"les_blocs": blocs_([5.0] * 20, [1.0] * 40)}})
    v("★★★★ sépare : le tracé passe partout et le demi-pas nulle part", ok_["separe"] and ok_["lissue"].startswith("le juge note"))
    ko = le_verdict({"le_decalage_nul_redonne_301": True,
                     "paris4": {"les_blocs": blocs_([5.0] * 20, [1.0] * 37 + [4.0] * 3)}})
    v("★★★★ ne sépare pas : trois demi-pas sur quarante au-dessus de 3 dépassent 5 %",
      not ko["separe"] and "dans 3 des 40 comparaisons" in ko["lissue"], ko["lissue"])
    un_cote = le_verdict({"le_decalage_nul_redonne_301": True,
                          "paris4": {"les_blocs": [{"les_z": {"p0": 5.0, "m0_5": 1.0, "p0_5": 4.0}} for _ in range(20)]}})
    v("★★★★ les deux côtés du demi-pas comptent", not un_cote["separe"])
    v("★★★ un Z absent empêche la séparation, comme dans l'étalonnage de 301",
      not le_verdict({"le_decalage_nul_redonne_301": True,
                      "paris4": {"les_blocs": blocs_([5.0] * 20, [1.0] * 39 + [None])}})["separe"])
    v("★★★ sans tracé qui passe, pas de séparation",
      not le_verdict({"le_decalage_nul_redonne_301": True,
                      "paris4": {"les_blocs": blocs_([5.0] * 17 + [1.0] * 3, [1.0] * 40)}})["separe"])
    v("★★★ indécidable si le décalage nul ne redonne pas 301, ou si une lecture échoue",
      not le_verdict({"le_decalage_nul_redonne_301": False, "paris4": {"les_blocs": []}})["decidable"]
      and not le_verdict({"les_pannes": ["x"]})["decidable"])
    res = {"s": [{"lalignement": 1.0}], **{f"s__{r}_{ph:g}": [{"lalignement": 0.1 * (1 + k % 3)}]
                                          for k, (r, ph) in enumerate((r, ph) for r in m298.LES_PENTES
                                                                      for ph in m300.LES_PHASES)}}
    z = le_z_du_groupe(res, "s", 0)
    v("★★★ le Z d'un groupe : contre ses huit rampes", z is not None and z > 3.0, str(z))
    res.pop("s__rampe_raide_1")
    v("★★★ une rampe sans point rend un Z absent, pas une levée", le_z_du_groupe(res, "s", 0) is None)

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
