"""Là où deux tours publiés voisins se recouvrent, autour des graines 1 à 3, la matière du scan de PHercParis4 montre-t-elle une bande de papyrus deux fois plus épaisse que là où ils sont séparés, deux feuilles collées, ou simple, un tour posé sur la feuille de son voisin ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UN SEUL PROFIL DU SCAN NE SOIT LU SOUS UN RECOUVREMENT. Ce qui était vu avant d'écrire : tout ce que
`296` à `342` publient, dont `R4-F527` (autour des graines 1 à 3, deux tours publiés voisins sont à un quart de pas l'un de l'autre sur
27 à 46 % des sommets du premier qui ont le second en face) et `R4-F528` (`m7` n'y voit qu'une plage de 3 voxels du niveau 2, comme
ailleurs, mais toutes ses plages ont ici 2 à 4 voxels, et il ne montre pas qu'il distinguerait deux feuilles collées d'une seule) ; le
volume de PHercParis4 au niveau 2, 9,6 µm, que `298` a lu, et dont 2835 morceaux sont déjà rangés.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P139`. Le scan porte l'épaisseur réelle du papyrus, que `m7` ne porte pas. Deux feuilles
écrasées l'une contre l'autre y font une bande claire deux fois plus épaisse qu'une feuille, ou deux bandes à moins d'un demi-pas ; un tour
publié posé sur la feuille de son voisin n'y laisse qu'une bande simple.

## Ce qui est fait

- **Les paires et les sommets** : ceux de `342`, sans rien y changer : pour les 18 paires qui se recouvrent autour des graines 1 à 3, 600
  sommets recouverts et 600 séparés du premier tour.
- **Le profil** : le scan au niveau 2, en trilinéaire comme `298`, le long de la normale de chaque sommet, sur un pas de chaque côté, au
  quart de voxel.
- **La bande** : le maximum du profil à au plus un quart de pas du sommet ; le fond, le minimum sur le pas de chaque côté ; la largeur,
  d'un seul tenant autour du maximum, où le profil dépasse la moitié entre le fond et le maximum, en voxels du niveau 2.
- **La règle** : pour chaque paire où les deux groupes ont au moins 50 profils mesurés, le rapport de la largeur médiane des recouverts à
  celle des séparés ; la médiane de ce rapport sur les paires dit **deux feuilles collées** si elle est d'au moins 1,5, **un tour posé sur
  la feuille de son voisin** si elle est d'au plus 1,2, **le scan ne tranche pas** sinon.

## Les issues

L'issue de la tranche : **sous les n paires qui se recouvrent, la bande du scan là où les tours se recouvrent a en médiane r fois la
largeur de celle d'où ils sont séparés** ; puis l'une des trois lectures déclarées.

## Rapporté à côté, qui ne décide rien

La répartition des largeurs dans chaque groupe, et le nombre médian de maxima au-dessus de la moitié à moins d'un demi-pas du sommet.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : lequel des deux tours est mal posé, s'il y en a un ; ni ce que le scan montrerait à 2,4 µm, le
niveau 0, plutôt qu'au niveau 2.

Usage :
    uv run python src/nappe/sous_le_recouvrement_le_scan_montre_t_il_deux_feuilles.py --verifier
    uv run python src/nappe/sous_le_recouvrement_le_scan_montre_t_il_deux_feuilles.py --preparer
    uv run python src/nappe/sous_le_recouvrement_le_scan_montre_t_il_deux_feuilles.py --lire 4
    uv run python src/nappe/sous_le_recouvrement_le_scan_montre_t_il_deux_feuilles.py \\
        --json docs/mesures/sous_le_recouvrement_le_scan_montre_t_il_deux_feuilles.json
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
import la_nappe_de_m7_retrouve_t_elle_le_trace_humain_de_paris4 as m321  # noqa: E402
import la_chaine_qui_croit_tombe_t_elle_sur_les_tours_publies as m329  # noqa: E402
import jusqua_quel_tour_publie_la_chaine_qui_croit_descend_elle as m330  # noqa: E402
import deux_tours_publies_voisins_se_distinguent_ils_a_un_quart_de_pas as m337  # noqa: E402
import sous_le_recouvrement_m7_voit_il_deux_feuilles_collees as m342  # noqa: E402

LE_DOSSIER = RACINE / "data" / "matiere_sous_le_recouvrement"
LE_PLAN = LE_DOSSIER / "plan.json"
LE_PAS_DU_PROFIL = 0.25            # voxels du niveau 2
LE_MINIMUM = 50
LE_COLLE, LE_SIMPLE = 1.5, 1.2


def les_positions(t_max: float = m321.LE_PAS_L2, pas: float = LE_PAS_DU_PROFIL) -> np.ndarray:
    return np.arange(-t_max, t_max + pas / 2.0, pas)


def les_coordonnees(points_l0: np.ndarray, normales: np.ndarray, t: np.ndarray) -> np.ndarray:
    """(n, len(t), 3) : les positions du profil, au niveau 2, dans l'ordre (z, y, x) du volume."""
    c = points_l0[:, None, :] / m321.LE_FACTEUR + t[None, :, None] * normales[:, None, :]
    return c[..., ::-1]


def la_bande(profil: np.ndarray, t: np.ndarray) -> dict | None:
    """La largeur, en voxels du niveau 2, de la bande claire la plus forte à au plus un quart de pas du sommet, à mi-hauteur entre le fond
    et son maximum ; et le nombre de maxima au-dessus de cette mi-hauteur à moins d'un demi-pas."""
    pres = np.flatnonzero(np.abs(t) <= m321.LE_PAS_L2 / 4.0)
    k = pres[int(np.argmax(profil[pres]))]
    haut, fond = float(profil[k]), float(profil.min())
    if haut - fond <= 0.0:
        return None
    moitie = (haut + fond) / 2.0
    dessus = profil >= moitie
    a = k
    while a > 0 and dessus[a - 1]:
        a -= 1
    b = k
    while b < len(profil) - 1 and dessus[b + 1]:
        b += 1
    if a == 0 or b == len(profil) - 1:
        return None
    demi = np.abs(t) <= m321.LE_PAS_L2 / 2.0
    p = profil
    maxima = np.flatnonzero((p[1:-1] >= p[:-2]) & (p[1:-1] > p[2:]) & (p[1:-1] >= moitie) & demi[1:-1]) + 1
    return {"la_largeur": float((b - a + 1) * (t[1] - t[0])), "les_maxima": int(len(maxima))}


def les_bandes(profils: np.ndarray, t: np.ndarray) -> dict:
    ls, ms = [], []
    for p in profils:
        r = la_bande(p, t)
        if r is not None:
            ls.append(r["la_largeur"])
            ms.append(r["les_maxima"])
    return {"les_largeurs": np.array(ls), "les_maxima": np.array(ms, dtype=int), "les_profils": int(len(profils))}


def le_rapport(recouverts: dict, separes: dict) -> float | None:
    if len(recouverts["les_largeurs"]) < LE_MINIMUM or len(separes["les_largeurs"]) < LE_MINIMUM:
        return None
    return round(float(np.median(recouverts["les_largeurs"]) / np.median(separes["les_largeurs"])), 3)


def le_verdict(d: dict) -> dict:
    if d.get("les_absents"):
        return {"decidable": False, "lissue": f"indécidable : {d['les_absents']} morceaux du scan ne sont pas rangés"}
    rs = [p["le_rapport"] for p in d["les_paires"] if p["le_rapport"] is not None]
    if not rs:
        return {"decidable": False, "lissue": "indécidable : aucune paire mesurable"}
    r = round(float(np.median(rs)), 2)
    tete = (f"sous les {len(rs)} paires qui se recouvrent, la bande du scan là où les tours se recouvrent a en médiane {r:g} fois la "
            f"largeur de celle d'où ils sont séparés").replace(".", ",")
    suite = ("deux feuilles collées" if r >= LE_COLLE else "un tour posé sur la feuille de son voisin" if r <= LE_SIMPLE
             else "le scan ne tranche pas")
    return {"decidable": True, "n": len(rs), "r": r, "lissue": f"{tete} ; {suite}"}


def resumer(b: dict) -> dict:
    lo = b["les_largeurs"]
    return {"les_profils": b["les_profils"], "mesures": int(len(lo)),
            "la_largeur_mediane_l2": round(float(np.median(lo)), 3) if len(lo) else None,
            "le_quartile_bas": round(float(np.percentile(lo, 25)), 3) if len(lo) else None,
            "le_quartile_haut": round(float(np.percentile(lo, 75)), 3) if len(lo) else None,
            "le_nombre_median_de_maxima": float(np.median(b["les_maxima"])) if len(lo) else None,
            "les_largeurs_comptees": {f"{x:g}": int(c) for x, c in zip(*np.unique(lo, return_counts=True))}}


def les_groupes() -> list[dict]:
    """Les paires qui se recouvrent autour des graines 1 à 3 et leurs deux groupes de sommets, comme `342`."""
    import le_tour_produit_porte_t_il_le_texte_du_segment as j296
    from la_spire_voisine_est_elle_a_un_pas import les_normales, lire_tifxyz

    d341 = json.loads(m342.CE_QUE_341_A_PUBLIE.read_text())
    a_lire = {(g["le_rang"], tuple(p["les_tours"])) for g in d341["les_graines"] if g["le_rang"] in m342.LES_GRAINES_DU_PROBLEME
              for p in g["les_paires"] if p["se_recouvrent"]}
    seg, sok, _ = lire_tifxyz(j296.LE_DOSSIER / j296.LES_SURFACES[0] / "maillage")
    sn, snok = les_normales(seg, sok)
    tours = {r: m329.lire_un_tour(r, m330.LES_TOURS) for r in m330.LES_TOURS}
    out = []
    for rang, (i, j) in enumerate(m321.les_graines(seg, sok, snok), 1):
        for ka, kb in m337.LES_PAIRES:
            if (rang, (ka, kb)) in a_lire:
                out.append({"le_rang": rang, "les_tours": [ka, kb], "les_groupes": m342.les_deux_groupes(tours[ka], tours[kb], seg[i, j])})
    return out


def le_volume() -> m298.LesMorceaux:
    v = m298.LES_VOLUMES["PHercParis4"]
    return m298.LesMorceaux("PHercParis4", v["url"], v["niveau"])


def preparer() -> dict:
    vol = le_volume()
    t = les_positions()
    tous = set()
    for p in les_groupes():
        for pts, nn in p["les_groupes"].values():
            if len(pts):
                tous |= m298.les_morceaux_complets(les_coordonnees(pts, nn, t), vol.taille)
    cles = sorted(tous)
    manquants = [c for c in cles if not vol.connu(*c)]
    LE_DOSSIER.mkdir(parents=True, exist_ok=True)
    LE_PLAN.write_text(json.dumps({"les_morceaux": [list(c) for c in cles], "les_manquants": [list(c) for c in manquants]}))
    return {"les_morceaux": len(cles), "les_manquants": len(manquants), "les_mo_a_tirer": round(len(manquants) * np.prod(vol.taille) / 1e6, 1)}


def lire(ouvriers: int = 4) -> dict:
    vol = le_volume()
    cles = [tuple(c) for c in json.loads(LE_PLAN.read_text())["les_manquants"]]
    comptes = {"deja": 0, "tire": 0, "absent": 0}
    with ThreadPoolExecutor(ouvriers) as ex:
        for r in ex.map(lambda c: vol.tirer(*c), cles):
            comptes[r] += 1
    return dict(comptes, combien=len(cles))


def mesurer() -> dict:
    t0 = time.monotonic()
    vol = le_volume()
    t = les_positions()
    plan = json.loads(LE_PLAN.read_text())
    absents = sum(1 for c in plan["les_morceaux"] if not vol.connu(*c))
    paires = []
    for p in les_groupes():
        bs = {}
        for nom, (pts, nn) in p["les_groupes"].items():
            bs[nom] = les_bandes(m298.les_profils(vol, les_coordonnees(pts, nn, t)), t) if len(pts) and not absents else \
                {"les_largeurs": np.zeros(0), "les_maxima": np.zeros(0, dtype=int), "les_profils": int(len(pts))}
        e = {"le_rang": p["le_rang"], "les_tours": p["les_tours"], "les_recouverts": resumer(bs["recouverts"]),
             "les_separes": resumer(bs["separes"]), "le_rapport": le_rapport(bs["recouverts"], bs["separes"])}
        paires.append(e)
        print(json.dumps({k: v for k, v in e.items() if k in ("le_rang", "les_tours", "le_rapport")}
                         | {"rec": e["les_recouverts"]["la_largeur_mediane_l2"], "sep": e["les_separes"]["la_largeur_mediane_l2"]},
                         ensure_ascii=False), flush=True)
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"le_pas_du_profil_l2": LE_PAS_DU_PROFIL, "le_minimum": LE_MINIMUM, "le_colle": LE_COLLE, "le_simple": LE_SIMPLE},
         "les_morceaux": len(plan["les_morceaux"]), "les_absents": absents, "les_lus_sur_disque": vol.lus_sur_disque, "les_paires": paires}
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

    t = les_positions()
    creneau = lambda c, w: np.where(np.abs(t - c) <= w / 2.0, 200.0, 50.0)  # noqa: E731
    b = la_bande(creneau(0.0, 5.0), t)
    v("★★★★★ une bande claire de 5 voxels a 5 voxels de large, à mi-hauteur", b is not None and abs(b["la_largeur"] - 5.25) < 0.3
      and b["les_maxima"] <= 1, str(b))
    b = la_bande(creneau(0.0, 10.0), t)
    v("★★★★ deux fois plus épaisse, deux fois plus large", b is not None and abs(b["la_largeur"] - 10.25) < 0.3, str(b))
    b = la_bande(creneau(8.0, 4.0), t)
    v("★★★★ une bande à plus d'un quart de pas du sommet n'est pas la sienne : le sommet est dans le fond",
      b is None or b["la_largeur"] < 1.0, str(b))
    cloche = 100.0 + 100.0 * np.exp(-0.5 * (t / 2.0) ** 2)
    b = la_bande(cloche, t)
    v("★★★★ la mi-hauteur se prend au-dessus du fond : une cloche d'écart-type 2 a 4,7 voxels de large", b is not None
      and abs(b["la_largeur"] - 4.71) < 0.3, str(b))
    deux = np.maximum(np.exp(-0.5 * ((t + 3.0) / 1.2) ** 2), np.exp(-0.5 * ((t - 3.0) / 1.2) ** 2)) * 150.0 + 50.0
    b = la_bande(deux, t)
    v("★★★ deux bandes séparées à moins d'un demi-pas : deux maxima", b is not None and b["les_maxima"] == 2, str(b))
    v("★★★ un profil plat n'a pas de bande", la_bande(np.full(len(t), 80.0), t) is None)
    v("★★★ une bande qui touche le bord du profil n'est pas mesurée", la_bande(np.where(t < 1.0, 200.0, 50.0), t) is None)

    pts = np.array([[4000.0, 4000.0, 4000.0]])
    c = les_coordonnees(pts, np.array([[0.0, 0.0, 1.0]]), np.array([-1.0, 0.0, 1.0]))
    v("★★★★ les coordonnées du profil : au niveau 2, en (z, y, x), le long de la normale",
      np.allclose(c[0], [[999.0, 1000.0, 1000.0], [1000.0, 1000.0, 1000.0], [1001.0, 1000.0, 1000.0]]), str(c))

    g_ = lambda w, n=60: {"les_largeurs": np.full(n, w), "les_maxima": np.ones(n, dtype=int)}  # noqa: E731
    v("★★★★ le rapport des largeurs médianes, et rien sous 50 profils mesurés",
      le_rapport(g_(10.0), g_(5.0)) == 2.0 and le_rapport(g_(10.0, 49), g_(5.0)) is None)
    p_ = lambda r: {"le_rapport": r}  # noqa: E731
    vd = le_verdict({"les_absents": 0, "les_paires": [p_(2.0), p_(1.6), p_(1.0), p_(None)]})
    v("★★★★ médiane 1,6 : deux feuilles collées ; une paire non mesurable ne compte pas", vd["lissue"].endswith("deux feuilles collées")
      and vd["n"] == 3, vd["lissue"])
    vd = le_verdict({"les_absents": 0, "les_paires": [p_(1.0), p_(1.1)]})
    v("★★★★ médiane 1,05 : un tour posé sur la feuille de son voisin",
      vd["lissue"].endswith("un tour posé sur la feuille de son voisin"))
    vd = le_verdict({"les_absents": 0, "les_paires": [p_(1.35)]})
    v("★★★ entre les deux : le scan ne tranche pas", vd["lissue"].endswith("le scan ne tranche pas"))
    v("★★★★ des morceaux du scan manquants rendent la tranche indécidable",
      not le_verdict({"les_absents": 3, "les_paires": [p_(2.0)]})["decidable"])

    for e_ in echecs:
        print(f"  ÉCHEC {e_}")
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
        print(json.dumps(preparer(), ensure_ascii=False))
        return 0
    if a.lire is not None:
        print(json.dumps(lire(a.lire), ensure_ascii=False))
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
