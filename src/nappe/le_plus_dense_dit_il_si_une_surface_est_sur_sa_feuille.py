"""Le plus dense du profil moyen, à moins d'un quart de pas d'une surface, dit-il si elle est posée sur sa feuille ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE CE JUGE NE SOIT MESURÉ SUR UN SEUL BLOC NEUF. Ce qui était vu avant d'écrire : tout ce que `298`
à `308` publient, dont la courbe de `308`, lue sur les vingt-quatre blocs de l'étalonnage de `301` : le profil moyen du tracé humain
de PHercParis4 est le plus dense à +3 voxels et le plus creux à −5, et les nappes de `m7` des graines 3, 6 et 7 de PHerc0358 à −2, 0
et +1. La forme du juge vient de là ; c'est pourquoi il est étalonné sur des blocs que rien n'a encore regardés.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P109`. Le contraste de `308` demande si la surface est le plus dense de sa feuille ;
la main humaine la pose sur la face, à un quart de pas de ce plus dense, et le contraste échoue sur elle. Demander où est le plus
dense par rapport à la surface garde la face et refuse l'entre-deux : décalée d'un demi-pas, une surface a son plus dense à plus
d'un quart de pas d'elle.

## Ce qui est fait

- **L'étalonnage, PHercParis4** : vingt-quatre blocs neufs du segment, hors de ceux de `296`, `299`, `300` et `301`, choisis par la
  règle de rangs de `299` ; le tracé humain de chaque bloc, et le même décalé le long de ses normales de −1, −0,5, −0,25, +0,25,
  +0,5 et +1 pas.
- **Le profil moyen** : celui du juge de `301`, chaque profil du scan brut ramené à moyenne nulle et écart un, sur ±200 µm, moyenné
  par bloc.
- **Le juge** : une surface est **posée sur sa feuille** si le plus dense de son profil moyen est à au plus un quart de pas d'elle,
  5 voxels sur les deux volumes (173 µm et 187,24 µm divisés par quatre, au voxel de 9,6 et 9,362 µm, arrondis).
- **Rapporté, PHerc0358** : les nappes et spires suivantes de `301` telles qu'elles sont rangées, et les nappes croissantes de
  `305` qui suivent l'empilement.

## L'issue

**Le juge du plus dense sépare la feuille de l'entre-deux** si, sur les blocs neufs, le tracé est posé sur sa feuille pour au moins
90 % des blocs, et décalé d'un demi-pas, des deux côtés réunis, pour au plus 5 % des 48 comparaisons, sans aucun profil absent ;
sinon **il ne la sépare pas**. Indécidable si une lecture échoue.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : quelle face de sa feuille une surface suit, ni si deux feuilles collées se lisent comme une.

Usage :
    uv run python src/nappe/le_plus_dense_dit_il_si_une_surface_est_sur_sa_feuille.py --verifier
    uv run python src/nappe/le_plus_dense_dit_il_si_une_surface_est_sur_sa_feuille.py --preparer
    uv run python src/nappe/le_plus_dense_dit_il_si_une_surface_est_sur_sa_feuille.py --lire 4
    uv run python src/nappe/le_plus_dense_dit_il_si_une_surface_est_sur_sa_feuille.py \\
        --json docs/mesures/le_plus_dense_dit_il_si_une_surface_est_sur_sa_feuille.json
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
import le_juge_voit_il_lentre_deux_feuilles as m307  # noqa: E402
import un_juge_de_position_separe_t_il_la_feuille_de_lentre_deux as m308  # noqa: E402

LE_DOSSIER = RACINE / "data" / "juge_du_plus_dense"
LES_SURFACES_PREPAREES = LE_DOSSIER / "surfaces"
LE_PLAN = LE_DOSSIER / "plan.json"
LES_DECALAGES = (-1.0, -0.5, -0.25, 0.0, 0.25, 0.5, 1.0)
LES_BLOCS = 24
MESURES = RACINE / "docs" / "mesures"


def le_quart_de_pas(volume: str) -> int:
    """Le quart du pas du rouleau, en voxels du niveau jugé, arrondi."""
    return int(round(m308.LES_PAS_UM[volume] / 4.0 / m298.LES_VOLUMES[volume]["le_voxel_um"]))


def le_plus_dense(profil: list) -> int | None:
    """Le décalage, en voxels le long de la normale, où le profil moyen est le plus haut ; le premier à égalité ; None sans
    profil."""
    if not profil:
        return None
    p = np.asarray(profil, dtype=float)
    return int(np.argmax(p)) - len(p) // 2


def posee(profil: list, quart: int) -> bool | None:
    d = le_plus_dense(profil)
    return None if d is None else abs(d) <= quart


def la_part(xs: list) -> float | None:
    """La part des vrais ; un absent compte comme faux."""
    if not xs:
        return None
    return round(sum(1 for x in xs if x) / len(xs), 4)


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    blocs = d["paris4"]["les_blocs"]
    if not blocs:
        return {"decidable": False, "lissue": "indécidable : aucun bloc"}
    k0 = sum(1 for b in blocs if b["posee"]["p0"])
    kd = sum(1 for b in blocs for k in ("m0_5", "p0_5") if b["posee"][k])
    absents = sum(1 for b in blocs for k in ("p0", "m0_5", "p0_5") if b["posee"][k] is None)
    sur, entre = la_part([b["posee"]["p0"] for b in blocs]), la_part([b["posee"][k] for b in blocs for k in ("m0_5", "p0_5")])
    separe = absents == 0 and sur >= m307.LE_TAUX_SUR_LA_FEUILLE and entre <= m307.LE_TAUX_ENTRE_DEUX
    n = 2 * len(blocs)
    return {"decidable": True, "separe": separe, "la_part_posee_a_sa_place": sur, "la_part_posee_au_demi_pas": entre,
            "les_absents": absents,
            "lissue": (f"le juge du plus dense sépare la feuille de l'entre-deux : le tracé est posé sur sa feuille dans {k0} des "
                       f"{len(blocs)} blocs neufs, décalé d'un demi-pas dans {kd} des {n} comparaisons" if separe else
                       f"le juge du plus dense ne sépare pas la feuille de l'entre-deux : le tracé est posé sur sa feuille dans "
                       f"{k0} des {len(blocs)} blocs neufs, décalé d'un demi-pas dans {kd} des {n} comparaisons")}


# ── Les étapes ─────────────────────────────────────────────────────────────────────────────────────────────────────

def les_blocs_deja_vus() -> list:
    import le_tour_produit_porte_t_il_le_texte_du_segment as j296

    deja = list(json.loads(j296.LE_PLAN.read_text())["les_blocs_de_la_partie_b"])
    for nom in ("lalignement_des_profils_dit_il_si_une_premiere_surface_suit_sa_feuille.json",
                "une_nappe_tiree_de_m7_suit_elle_sa_feuille.json",
                "les_nappes_de_m7_suivent_elles_leur_feuille_sur_des_graines_neuves.json"):
        deja += json.loads((MESURES / nom).read_text())["letalonnage"]["les_blocs"]
    return [tuple(b["le_bloc"] if isinstance(b, dict) else b) for b in deja]


def les_surfaces_de_paris4() -> tuple[dict, list]:
    import le_tour_produit_porte_t_il_le_texte_du_segment as j296
    from la_procedure_sans_juge_tient_elle_sur_le_segment_entier import le_segment
    from la_spire_voisine_est_elle_a_un_pas import LE_CACHE, les_normales, lire_tifxyz
    from que_montrent_ces_deux_vues import PAS_EN_VOXELS

    k = m298.LE_SURECHANTILLONNAGE["PHercParis4"]
    _, _, _, candidats = le_segment(LE_CACHE)
    blocs = m299.les_blocs_neufs(sorted(candidats), les_blocs_deja_vus(), combien=LES_BLOCS)
    pts0, ok0, esp = lire_tifxyz(j296.LE_DOSSIER / j296.LES_SURFACES[0] / "maillage")
    out: dict = {}
    for b in blocs:
        lignes, colonnes = j296.les_mailles_dune_bande(*b, 1, esp)
        L, C = lignes[lignes < ok0.shape[0]], colonnes[colonnes < ok0.shape[1]]
        sp, sok = m298.surechantillonner(pts0[np.ix_(L, C)], ok0[np.ix_(L, C)], k)
        nn, nok = les_normales(sp, sok)
        m = sok & nok
        for d in LES_DECALAGES:
            dp = m307.decaler(sp, nn, d, float(PAS_EN_VOXELS))
            out.setdefault(m307.le_nom(d), []).append({"le_bloc": list(b), "points": dp[m], "normales": nn[m]})
    return out, [list(b) for b in blocs]


def les_surfaces_de_0358() -> dict:
    from la_spire_voisine_est_elle_a_un_pas import les_normales

    out: dict = {}
    z = np.load(m301.LES_NAPPES)
    for r in sorted({int(k[1:].split("_")[0]) for k in z.files}):
        for s in ("nappe", "plus", "moins"):
            pts, ok = z[f"g{r}_{s}"], z[f"g{r}_{s}_ok"]
            nn, nok = les_normales(pts, ok)
            m = ok & nok
            out[f"vote_g{r}_{s}"] = [{"la_piece": ["301", r, s], "points": pts[m], "normales": nn[m]}]
    plan307 = json.loads(m307.LE_PLAN.read_text())
    for cle, info in plan307["les_surfaces"].items():
        if cle.startswith("PHerc0358__g") and cle.endswith("_p0"):
            r = int(cle.split("__g")[1].split("_")[0])
            f = np.load(RACINE / info["le_fichier"])
            out[f"croissante_g{r}"] = [{"la_piece": ["305", r, "nappe"], "points": f["points"], "normales": f["normales"]}]
    return out


def preparer() -> dict:
    t0 = time.monotonic()
    paris, blocs = les_surfaces_de_paris4()
    prix = les_surfaces_de_0358()
    plan = {"les_blocs": blocs, "les_surfaces": {}, "les_morceaux": {}}
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
    qp, qq = le_quart_de_pas("PHercParis4"), le_quart_de_pas("PHerc0358")
    noms = [m307.le_nom(x) for x in LES_DECALAGES]
    blocs = []
    for i, b in enumerate(plan["les_blocs"]):
        prof = {k: res[f"PHercParis4__{k}"][i]["le_profil_moyen"] for k in noms}
        blocs.append({"le_bloc": b, "le_plus_dense": {k: le_plus_dense(prof[k]) for k in noms},
                      "posee": {k: posee(prof[k], qp) for k in noms},
                      "les_points_juges": res["PHercParis4__p0"][i]["les_points_juges"]})
    courbe = [{"le_decalage_en_pas": x, "la_part_posee": la_part([b["posee"][m307.le_nom(x)] for b in blocs])}
              for x in LES_DECALAGES]
    places = [b["le_plus_dense"]["p0"] for b in blocs if b["le_plus_dense"]["p0"] is not None]
    la_place = ({"le_min": int(min(places)), "la_mediane": float(np.median(places)), "le_max": int(max(places)),
                 "du_cote_negatif": sum(1 for x in places if x < 0)} if places else None)
    surfaces = []
    for cle in sorted(k for k in res if k.startswith("PHerc0358__")):
        if not res[cle]:
            surfaces.append({"la_surface": cle.split("__")[1], "le_plus_dense": None, "posee": None, "les_points_juges": 0})
            continue
        a = res[cle][0]
        surfaces.append({"la_surface": cle.split("__")[1], "le_plus_dense": le_plus_dense(a["le_profil_moyen"]),
                         "posee": posee(a["le_profil_moyen"], qq), "les_points_juges": a["les_points_juges"],
                         "sans_matiere": a["sans_matiere"]})
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"les_quarts_de_pas_voxels": {"PHercParis4": qp, "PHerc0358": qq},
                            "les_decalages_en_pas": list(LES_DECALAGES), "les_blocs": LES_BLOCS},
         "les_pannes": [], "paris4": {"les_blocs": blocs, "la_courbe": courbe, "la_place_du_plus_dense_du_trace": la_place}, "phercs0358": {"les_surfaces": surfaces},
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

    v("★★★ le quart de pas : 5 voxels sur les deux volumes", le_quart_de_pas("PHercParis4") == 5
      and le_quart_de_pas("PHerc0358") == 5)
    u = np.arange(-21, 22)
    face = list(np.exp(-((u - 3) / 3.0) ** 2))
    v("★★★★ le plus dense : son décalage, signé, par rapport à la surface", le_plus_dense(face) == 3
      and le_plus_dense(list(np.exp(-((u + 7) / 3.0) ** 2))) == -7 and le_plus_dense([]) is None)
    v("★★★★ posée sur la face de sa feuille, à 3 voxels du plus dense", posee(face, 5) is True)
    decale = list(np.exp(-((u - 3 + 9) / 3.0) ** 2))
    v("★★★★ décalée d'un demi-pas, le plus dense est à plus d'un quart de pas", posee(decale, 5) is False)
    v("★★★ le quart de pas est une borne incluse", posee(list(np.exp(-((u - 5) / 3.0) ** 2)), 5) is True
      and posee(list(np.exp(-((u + 6) / 3.0) ** 2)), 5) is False)
    v("★★★★ un absent compte comme non posé", la_part([True, None, False, True]) == 0.5 and la_part([]) is None)

    def blocs_(a, b):
        return [{"posee": {"p0": a[i], "m0_5": b[2 * i], "p0_5": b[2 * i + 1]}} for i in range(len(a))]

    ok_ = le_verdict({"paris4": {"les_blocs": blocs_([True] * 20, [False] * 40)}})
    v("★★★★ sépare : posé partout à sa place, nulle part au demi-pas", ok_["separe"] and "dans 20 des 20" in ok_["lissue"])
    ko = le_verdict({"paris4": {"les_blocs": blocs_([True] * 20, [False] * 37 + [True] * 3)}})
    v("★★★★ ne sépare pas : trois demi-pas posés sur quarante dépassent 5 %", not ko["separe"]
      and "dans 3 des 40" in ko["lissue"])
    v("★★★★ les deux côtés du demi-pas comptent",
      not le_verdict({"paris4": {"les_blocs": [{"posee": {"p0": True, "m0_5": False, "p0_5": True}}] * 20}})["separe"])
    v("★★★ un absent empêche la séparation",
      not le_verdict({"paris4": {"les_blocs": blocs_([True] * 20, [False] * 39 + [None])}})["separe"])
    v("★★★ indécidable sans bloc ou si une lecture échoue", not le_verdict({"paris4": {"les_blocs": []}})["decidable"]
      and not le_verdict({"les_pannes": ["x"]})["decidable"])
    deja = les_blocs_deja_vus()
    v("★★★★ les blocs déjà vus comptent ceux de 296, 299, 300 et 301", len(deja) >= 3 * m299.LES_BLOCS
      and all(tuple(b["le_bloc"]) in set(deja) for b in json.loads(
          (MESURES / "les_nappes_de_m7_suivent_elles_leur_feuille_sur_des_graines_neuves.json").read_text())[
          "letalonnage"]["les_blocs"]), str(len(deja)))

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
