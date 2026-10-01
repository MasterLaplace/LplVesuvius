"""Sur PHerc1203, le tour suivant que le transfert produit depuis une surface poussée sans humain tombe-t-il sur une autre surface poussée sans humain, là où celle-ci passe à un tour ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UNE SEULE SURFACE DE PHERC1203 NE SOIT TÉLÉCHARGÉE, ET AVANT QUE `m7` N'Y SOIT LU. Ce qui était vu
avant d'écrire : tout ce que `247` à `410` publient, dont `R4-F412` (sur le segment `20230702185753` de PHercParis4, le transfert retombe
sur la bonne spire pour 0,9214 et 0,9163 des points) et `R4-F482` (sur PHerc0358, le saut suivant de `300`) ; et, du dépôt public, la
liste des 22 segments `auto_grown_*` de PHerc1203 et leurs `meta.json` : l'aire (2,9 à 16,1 cm²), la boîte englobante, la source
(`vc_grow_seg_from_seed`), l'échelle de grille (0,05, une maille de 20 voxels) et les tailles des fichiers. Aucune surface, aucune
valeur de `m7` de PHerc1203.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P218` ET #13. Le Grand Prix 2027 paie le premier rouleau éligible entièrement déroulé et
lisible, avec au plus 8 heures d'intervention humaine. Le transfert d'un tour au suivant est la pièce qui multiplie une surface en un
rouleau, et il n'a jamais tourné sur un rouleau éligible depuis une surface que personne n'a posée. PHerc1203 publie 22 surfaces poussées
par un programme : elles sont le départ, et elles sont aussi le juge. Là où une autre de ces surfaces passe à un tour de celle d'où part
le transfert, le tour produit doit tomber dessus. Leur croissance n'est pas le transfert, même si les deux lisent une prédiction de
surface.

## Ce qui est fait

- **Les surfaces** : les 22 segments publiés sous `PHerc1203/segments/raw/`, leur version de tête (`x.tif`, `y.tif`, `z.tif`), en
  voxels du scan `20250820131727` à 9,362 µm. Un sommet vaut −1 hors de la surface.
- **Le contrôle** : la part des points intérieurs d'une surface où `m7` (la prédiction `L0` de ce scan) s'allume à moins de 3 voxels le
  long de sa normale. Une surface n'entre dans la mesure, ni comme départ ni comme juge, que si cette part vaut au moins 0,5.
- **Le transfert** : `le_saut_suivant` de `300`, la règle de `248` — de chaque point, le long de sa normale, la première feuille de
  `m7` au-delà de la sienne, sur trois pas, puis le vote de `247` —, des deux côtés de chaque surface. Le pas est celui de `300`,
  20 voxels, soit 187,24 µm : PHerc1203 a le voxel de PHerc0358, et 187 µm est le pas médian de la collection (`R6-F12`).
- **Le juge** : de chaque point, le long de la même normale et du même côté, le premier passage d'une AUTRE surface retenue, entre
  un demi-pas et trois pas. Un passage est un changement de signe de la distance au plan tangent du sommet le plus proche de cette
  surface, ce sommet restant à moins d'une maille sur le côté. Le point est **jugé** si ce passage tombe entre un demi-pas et un pas
  et demi. Le tour produit y est **juste** si son écart diffère de celui du passage d'au plus un quart de pas, 5 voxels.
- **Le témoin**, celui de `247`, qui prédit sans rien lire : le décalage fixe d'un pas, jugé sur les mêmes points.

## La règle

Sur tous les points jugés, des deux côtés de toutes les surfaces retenues :

- **oui** si la part juste du transfert vaut au moins 0,8 et dépasse celle du témoin d'au moins 0,05 ;
- **non** si elle est sous 0,5, ou sous celle du témoin ;
- **en partie** sinon ;
- **indécidable** si moins de 2 surfaces passent le contrôle, si moins de 1000 points sont jugés, ou si une lecture de `m7` échoue.

L'issue : **la part juste du transfert, celle du témoin, sur combien de points et de surfaces, et la règle.**

## Rapporté à côté, qui ne décide rien

- le contrôle et les parts justes surface par surface, et sur combien de surfaces le transfert bat le témoin ;
- là où le passage est entre un pas et demi et trois pas : où le tour produit s'arrête, sur la surface, avant elle ou au-delà ;
- les distances de passage, en pas ; la part des points du tour produit appuyés sur une feuille de `m7`, ses déchirures ;
- les téléchargements.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : que la surface rencontrée soit le tour voisin — une feuille qu'aucune surface ne couvre peut
s'intercaler, et c'est pourquoi seul un passage à moins d'un pas et demi décide ; que les surfaces automatiques soient justes, le
contrôle ne dit que `m7` les voit ; rien de l'encre ; rien de ce que vaut le transfert sur tout le rouleau.

Usage :
    uv run python src/nappe/le_transfert_tombe_t_il_sur_les_surfaces_automatiques_de_pherc1203.py --verifier
    uv run python src/nappe/le_transfert_tombe_t_il_sur_les_surfaces_automatiques_de_pherc1203.py --preparer
    uv run python src/nappe/le_transfert_tombe_t_il_sur_les_surfaces_automatiques_de_pherc1203.py --transferer
    uv run python src/nappe/le_transfert_tombe_t_il_sur_les_surfaces_automatiques_de_pherc1203.py \\
        --json docs/mesures/le_transfert_tombe_t_il_sur_les_surfaces_automatiques_de_pherc1203.json
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

import une_nappe_tiree_de_m7_suit_elle_sa_feuille as m300  # noqa: E402

LE_DOSSIER = RACINE / "data" / "chaine_pherc1203"
LES_SURFACES = LE_DOSSIER / "surfaces"
LES_TRANSFERTS = LE_DOSSIER / "transferts"
LE_CACHE_M7 = LE_DOSSIER / "m7"
LE_PLAN = LE_DOSSIER / "plan.json"
LE_ROULEAU = "PHerc1203"
LE_SCAN = "20250820131727"
LES_SEGMENTS = f"{LE_ROULEAU}/segments/raw/"
LA_PREDICTION = (f"{LE_ROULEAU}/representations/predictions/surfaces/"
                 f"{LE_SCAN}-surface-20260413222639-surface-m7-L0-th0.2.zarr")
LES_FICHIERS = ("meta.json", "x.tif", "y.tif", "z.tif")
LE_HORS_SURFACE = -1.0

LE_PAS = m300.LE_PAS_0358
LE_QUART = LE_PAS / 4.0
LA_BANDE = (0.5, 1.5)
LA_PORTEE = 3.0
LE_CONTROLE = m300.LE_CONTROLE
LE_MINIMUM_DU_CONTROLE = 0.5
LE_SEUIL_OUI, LA_MARGE, LE_SEUIL_NON = 0.8, 0.05, 0.5
LE_MINIMUM_DE_POINTS, LE_MINIMUM_DE_SURFACES = 1000, 2
LES_COTES = {"plus": 1.0, "moins": -1.0}
LE_PAQUET = 8192
LES_CLASSES_DE_PAS = (0.5, 1.0, 1.5, 2.0, 2.5, 3.0)
LE_MORCEAU_MOYEN_MO = 0.32


# ── Les surfaces ───────────────────────────────────────────────────────────────────────────────────────────────────

def lire_la_surface(dossier: Path) -> tuple[np.ndarray, np.ndarray, float]:
    """Les sommets (h, w, 3) en (x, y, z), le masque des sommets valides, et la maille en voxels, d'une surface tifxyz."""
    import tifffile

    xyz = np.stack([tifffile.imread(dossier / f"{a}.tif").astype(np.float64) for a in "xyz"], -1)
    meta = json.loads((dossier / "meta.json").read_text())
    valide = np.all(np.isfinite(xyz), axis=-1) & np.all(xyz != LE_HORS_SURFACE, axis=-1)
    return np.where(valide[..., None], xyz, 0.0), valide, 1.0 / float(meta["scale"][0])


def les_normales(points: np.ndarray, valide: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    from la_spire_voisine_est_elle_a_un_pas import les_normales as n

    return n(points, valide)


def les_rayons(p: np.ndarray, n: np.ndarray, t: np.ndarray) -> np.ndarray:
    """Les indices (…, len(t), 3) en (z, y, x) des points p + t·n."""
    return np.floor((p[:, None, :] + t[None, :, None] * n[:, None, :])[..., ::-1]).astype(np.int64)


def le_controle(p: np.ndarray, n: np.ndarray, lire_valeurs) -> float | None:
    """La part des points où `m7` s'allume à moins de `LE_CONTROLE` voxels le long de la normale."""
    if not len(p):
        return None
    t = np.arange(-np.floor(LE_CONTROLE), np.floor(LE_CONTROLE) + 1.0)
    return round(float((lire_valeurs(les_rayons(p, n, t)) > 0).any(axis=1).mean()), 4)


def les_morceaux(p: np.ndarray, n: np.ndarray, taille, pas: float = 10.0) -> set:
    """Les morceaux de `m7` que lisent le contrôle et le transfert des deux côtés, à `pas` voxels près le long du rayon."""
    t = np.arange(-LA_PORTEE * LE_PAS, LA_PORTEE * LE_PAS + pas, pas)
    cles = les_rayons(p, n, t).reshape(-1, 3) // np.asarray(taille)
    return set(map(tuple, np.unique(cles, axis=0).tolist()))


# ── Le juge ────────────────────────────────────────────────────────────────────────────────────────────────────────

class LesAutres:
    """Les sommets intérieurs des surfaces retenues, leurs normales et leur surface d'origine, pour chercher un passage."""

    def __init__(self, surfaces: dict):
        from scipy.spatial import cKDTree

        p, n, k, self.noms, self.mailles = [], [], [], sorted(surfaces), []
        for i, nom in enumerate(self.noms):
            s = surfaces[nom]
            p.append(s["p"])
            n.append(s["n"])
            k.append(np.full(len(s["p"]), i))
            self.mailles.append(s["maille"])
        self.p, self.n, self.k = np.concatenate(p), np.concatenate(n), np.concatenate(k)
        self.maille = max(self.mailles)
        self.arbre = cKDTree(self.p)

    def sauf(self, nom: str) -> "LesAutres":
        """Les mêmes, sans la surface `nom`."""
        garder = self.k != self.noms.index(nom)
        autre = object.__new__(LesAutres)
        from scipy.spatial import cKDTree

        autre.noms, autre.mailles, autre.maille = self.noms, self.mailles, self.maille
        autre.p, autre.n, autre.k = self.p[garder], self.n[garder], self.k[garder]
        autre.arbre = cKDTree(autre.p)
        return autre


def les_passages(p: np.ndarray, n: np.ndarray, cote: float, autres: LesAutres) -> tuple[np.ndarray, np.ndarray]:
    """Le long de cote·n, depuis chaque point, l'écart du premier passage d'une autre surface entre un demi-pas et `LA_PORTEE` pas, et
    son indice ; NaN et −1 sans passage. Un passage : la distance au plan tangent du sommet le plus proche change de signe entre deux
    pas d'un voxel, le sommet restant de la même surface et à moins d'une maille sur le côté."""
    t = np.arange(np.ceil(LE_PAS / 2.0), LA_PORTEE * LE_PAS + 1.0)
    out_t, out_k = np.full(len(p), np.nan), np.full(len(p), -1)
    for a in range(0, len(p), LE_PAQUET):
        r = p[a:a + LE_PAQUET, None, :] + (cote * t)[None, :, None] * n[a:a + LE_PAQUET, None, :]
        _, j = autres.arbre.query(r.reshape(-1, 3), workers=2)
        j = j.reshape(r.shape[:2])
        v = r - autres.p[j]
        nq = autres.n[j]
        h = np.einsum("ijk,ijk->ij", v, nq)
        cote_ok = np.linalg.norm(v - h[..., None] * nq, axis=-1) <= autres.maille
        k = autres.k[j]
        signe = np.sign(h)
        change = (signe[:, :-1] != signe[:, 1:]) & (k[:, :-1] == k[:, 1:]) & cote_ok[:, :-1] & cote_ok[:, 1:]
        ligne = np.flatnonzero(change.any(axis=1))
        if not len(ligne):
            continue
        c = change[ligne].argmax(axis=1)
        h0, h1 = h[ligne, c], h[ligne, c + 1]
        frac = np.where(h0 != h1, h0 / np.where(h0 != h1, h0 - h1, 1.0), 0.0)
        out_t[a + ligne] = t[c] + frac * (t[c + 1] - t[c])
        out_k[a + ligne] = k[ligne, c]
    return out_t, out_k


def juger(ecart: np.ndarray, passage: np.ndarray) -> dict:
    """Les comptes d'un côté d'une surface : les points jugés (passage dans la bande), justes du transfert et du témoin, et, au-delà de
    la bande, où le tour produit s'arrête."""
    e = np.abs(ecart)
    juge = np.isfinite(passage) & (passage >= LA_BANDE[0] * LE_PAS) & (passage <= LA_BANDE[1] * LE_PAS)
    loin = np.isfinite(passage) & (passage > LA_BANDE[1] * LE_PAS)
    ok_e = np.isfinite(e)
    juste_t = juge & ok_e & (np.abs(e - passage) <= LE_QUART)
    juste_w = juge & (np.abs(LE_PAS - passage) <= LE_QUART)
    sur = loin & ok_e & (np.abs(e - passage) <= LE_QUART)
    avant = loin & ok_e & (e < passage - LE_QUART)
    return {"les_jugés": int(juge.sum()), "justes_transfert": int(juste_t.sum()), "justes_temoin": int(juste_w.sum()),
            "au_dela": {"les_points": int(loin.sum()), "sur": int(sur.sum()), "avant": int(avant.sum()),
                        "apres": int((loin & ~sur & ~avant).sum())},
            "les_passages_en_pas": np.histogram(passage[np.isfinite(passage)] / LE_PAS, bins=LES_CLASSES_DE_PAS)[0].tolist()}


def la_part(a: int, b: int) -> float | None:
    return round(a / b, 4) if b else None


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture de m7 a échoué ({d['les_pannes'][0]})"}
    s = d["la_somme"]
    if d["les_surfaces_retenues"] < LE_MINIMUM_DE_SURFACES:
        return {"decidable": False, "lissue": f"indécidable : {d['les_surfaces_retenues']} surface(s) passent le contrôle"}
    if s["les_jugés"] < LE_MINIMUM_DE_POINTS:
        return {"decidable": False, "lissue": f"indécidable : {s['les_jugés']} points jugés"}
    pt, pw = s["la_part_du_transfert"], s["la_part_du_temoin"]
    suite = "oui" if pt >= LE_SEUIL_OUI and pt >= pw + LA_MARGE else "non" if pt < LE_SEUIL_NON or pt < pw else "en partie"
    f = lambda x: f"{x:g}".replace(".", ",")  # noqa: E731
    return {"decidable": True, "la_suite": suite,
            "lissue": f"transfert {f(pt)}, témoin {f(pw)}, sur {s['les_jugés']} points de {s['les_surfaces_jugées']} surfaces ; {suite}"}


# ── Préparer, transférer, mesurer ──────────────────────────────────────────────────────────────────────────────────

def les_noms() -> list[str]:
    import tracecheck as tc

    return sorted(p.rstrip("/").rsplit("/", 1)[-1] for p in tc.list_prefix(LES_SEGMENTS, 60.0) if "auto_grown_" in p)


def le_lecteur():
    from le_transfert_retrouve_t_il_la_spire_voisine import lecteur_du_depot
    from zarr_depth import BUCKET, array_meta

    pred = array_meta(f"{BUCKET}/{LA_PREDICTION}", 0, 120.0)
    lire, stats = lecteur_du_depot(pred, LE_CACHE_M7, "m7_L0", LA_PREDICTION, 0)
    return pred, lire, stats, (lambda idx: m300.lire_m7(idx, (pred, lire)))


def preparer() -> dict:
    """Les surfaces tirées du dépôt s'il en manque, et le compte des morceaux de `m7` qu'il faudra : rien de `m7` n'est lu."""
    import tracecheck as tc
    from zarr_depth import BUCKET, array_meta

    noms, octets, morceaux, surfaces = les_noms(), 0, set(), []
    taille = tuple(array_meta(f"{BUCKET}/{LA_PREDICTION}", 0, 120.0)["chunks"])
    for nom in noms:
        d = LES_SURFACES / nom
        d.mkdir(parents=True, exist_ok=True)
        for f in LES_FICHIERS:
            if not (d / f).exists():
                brut, raison = tc.get_with_reason(f"{BUCKET}/{LES_SEGMENTS}{nom}/{f}", 120.0)
                if brut is None:
                    raise RuntimeError(f"{nom}/{f} : {raison}")
                (d / f).write_bytes(brut)
                octets += len(brut)
        p, valide, maille = lire_la_surface(d)
        n, ok = les_normales(p, valide)
        morceaux |= les_morceaux(p[ok], n[ok], taille)
        meta = json.loads((d / "meta.json").read_text())
        surfaces.append({"le_nom": nom, "laire_cm2": round(float(meta["area_cm2"]), 3), "la_grille": list(valide.shape),
                         "la_maille_voxels": maille, "les_sommets_valides": int(valide.sum()), "les_points_interieurs": int(ok.sum())})
    deja = sum((LE_CACHE_M7 / "m7_L0" / f"0_{z}_{y}_{x}.blosc").exists() for z, y, x in morceaux)
    plan = {"les_surfaces": surfaces, "les_octets_des_surfaces_tirés": octets, "les_morceaux_de_m7": len(morceaux),
            "deja_sur_le_disque": deja, "la_taille_des_morceaux": list(taille),
            "lestimation_du_telechargement_mo": round((len(morceaux) - deja) * LE_MORCEAU_MOYEN_MO, 1)}
    LE_DOSSIER.mkdir(parents=True, exist_ok=True)
    LE_PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=1) + "\n")
    return plan


def transferer() -> int:
    """Le contrôle et le transfert des deux côtés de chaque surface, rangés sur disque ; une surface déjà faite est sautée."""
    pred, lire, stats, lire_valeurs = le_lecteur()
    LES_TRANSFERTS.mkdir(parents=True, exist_ok=True)
    for nom in json.loads(LE_PLAN.read_text())["les_surfaces"]:
        nom = nom["le_nom"]
        sortie = LES_TRANSFERTS / f"{nom}.npz"
        if sortie.exists():
            continue
        t0 = time.monotonic()
        p, valide, maille = lire_la_surface(LES_SURFACES / nom)
        n, ok = les_normales(p, valide)
        ligne = {"le_nom": nom, "le_controle": le_controle(p[ok], n[ok], lire_valeurs)}
        tableaux = {}
        if ligne["le_controle"] is not None and ligne["le_controle"] >= LE_MINIMUM_DU_CONTROLE:
            for cote, signe in LES_COTES.items():
                s = m300.le_saut_suivant(p, valide, signe, lire_valeurs)
                tableaux[f"{cote}_pas"], tableaux[f"{cote}_appui"], tableaux[f"{cote}_valide"] = s["le_pas"], s["appui"], s["valide"]
                ligne[cote] = {"la_part_appuyee": round(float(s["appui"][ok].mean()), 4), "les_tours": s["les_tours"],
                               "les_dechirures": m300.les_dechirures(s["le_pas"], s["valide"], LE_PAS / 2.0)}
        ligne["les_secondes"] = round(time.monotonic() - t0, 1)
        ligne["les_pannes"] = stats["pannes"][:5]
        np.savez_compressed(sortie, **tableaux)
        with (LE_DOSSIER / "transferts.out").open("a") as o:
            o.write(json.dumps(ligne, ensure_ascii=False) + "\n")
        print(json.dumps(ligne, ensure_ascii=False), flush=True)
    print(json.dumps({"la_lecture_de_m7": {k: (v if k != "pannes" else v[:20]) for k, v in stats.items()}}), flush=True)
    return 1 if stats["pannes"] else 0


def mesurer() -> dict:
    """Le juge, sur les transferts rangés : rien n'est relu du dépôt."""
    t0 = time.monotonic()
    plan = json.loads(LE_PLAN.read_text())
    lignes = {}
    for l in (LE_DOSSIER / "transferts.out").read_text().splitlines():
        x = json.loads(l)
        lignes[x["le_nom"]] = x
    pannes = [p for x in lignes.values() for p in x.get("les_pannes", [])]
    retenues, geo = [], {}
    for s in plan["les_surfaces"]:
        nom = s["le_nom"]
        if nom not in lignes:
            pannes.append(f"{nom} : pas de transfert")
            continue
        if lignes[nom]["le_controle"] is not None and lignes[nom]["le_controle"] >= LE_MINIMUM_DU_CONTROLE:
            p, valide, maille = lire_la_surface(LES_SURFACES / nom)
            n, ok = les_normales(p, valide)
            geo[nom] = {"p": p[ok], "n": n[ok], "ok": ok, "maille": maille}
            retenues.append(nom)
    par_surface, somme, histo = [], {"les_jugés": 0, "justes_transfert": 0, "justes_temoin": 0}, np.zeros(len(LES_CLASSES_DE_PAS) - 1, int)
    loin = {"les_points": 0, "sur": 0, "avant": 0, "apres": 0}
    tous = LesAutres(geo) if len(geo) >= 2 else None
    for s in plan["les_surfaces"]:
        nom = s["le_nom"]
        e = {"le_nom": nom, "laire_cm2": s["laire_cm2"], "le_controle": lignes.get(nom, {}).get("le_controle"), "retenue": nom in geo}
        if nom in geo and tous is not None:
            autres, g = tous.sauf(nom), geo[nom]
            tr = np.load(LES_TRANSFERTS / f"{nom}.npz")
            for cote, signe in LES_COTES.items():
                ecart = np.where(tr[f"{cote}_valide"], tr[f"{cote}_pas"], np.nan)[g["ok"]]
                passage, _ = les_passages(g["p"], g["n"], signe, autres)
                j = juger(ecart, passage)
                for k in somme:
                    somme[k] += j[k]
                for k in loin:
                    loin[k] += j["au_dela"][k]
                histo += np.asarray(j["les_passages_en_pas"])
                e[cote] = {**j, "la_part_du_transfert": la_part(j["justes_transfert"], j["les_jugés"]),
                           "la_part_du_temoin": la_part(j["justes_temoin"], j["les_jugés"]), **lignes[nom].get(cote, {})}
        par_surface.append(e)
    jugees = [e for e in par_surface if e["retenue"] and sum(e[c]["les_jugés"] for c in LES_COTES if c in e) > 0]
    bat = sum(1 for e in jugees if sum(e[c]["justes_transfert"] for c in LES_COTES) > sum(e[c]["justes_temoin"] for c in LES_COTES))
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"le_pas_voxels": LE_PAS, "le_quart_voxels": LE_QUART, "la_bande_en_pas": list(LA_BANDE),
                            "la_portee_en_pas": LA_PORTEE, "le_controle_voxels": LE_CONTROLE,
                            "le_minimum_du_controle": LE_MINIMUM_DU_CONTROLE, "le_seuil_oui": LE_SEUIL_OUI, "la_marge": LA_MARGE,
                            "le_seuil_non": LE_SEUIL_NON, "la_prediction": LA_PREDICTION},
         "le_plan": {k: v for k, v in plan.items() if k != "les_surfaces"},
         "les_surfaces_retenues": len(retenues), "les_pannes": pannes[:20],
         "la_somme": {**somme, "les_surfaces_jugées": len(jugees),
                      "la_part_du_transfert": la_part(somme["justes_transfert"], somme["les_jugés"]),
                      "la_part_du_temoin": la_part(somme["justes_temoin"], somme["les_jugés"])},
         "au_dela_de_la_bande": {**loin, **{f"la_part_{k}": la_part(loin[k], loin["les_points"]) for k in ("sur", "avant", "apres")}},
         "les_passages_en_pas": {"les_bornes": list(LES_CLASSES_DE_PAS), "les_comptes": histo.tolist()},
         "les_surfaces_ou_le_transfert_bat_le_temoin": f"{bat} sur {len(jugees)}",
         "par_surface": par_surface}
    d["le_verdict"] = le_verdict(d)
    d["les_secondes"] = round(time.monotonic() - t0, 1)
    return d


# ── La batterie ────────────────────────────────────────────────────────────────────────────────────────────────────

def un_plan(z: float, cote: int = 12, maille: float = 20.0, decale: tuple = (0.0, 0.0)) -> tuple[np.ndarray, np.ndarray]:
    """Un plan horizontal de cote × cote sommets à la hauteur z, de normale de grille +z."""
    i, j = np.meshgrid(np.arange(cote), np.arange(cote), indexing="ij")
    p = np.stack([j * maille + 1000.0 + decale[0], i * maille + 1000.0 + decale[1], np.full(i.shape, z)], -1).astype(float)
    return p, np.ones(i.shape, bool)


def verifier() -> int:
    import tempfile

    import tifffile

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

    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        x = np.array([[1.0, 2.0], [-1.0, 4.0]], np.float32)
        tifffile.imwrite(d / "x.tif", x)
        tifffile.imwrite(d / "y.tif", x + 10)
        tifffile.imwrite(d / "z.tif", np.where(x == -1, -1, x + 100).astype(np.float32))
        (d / "meta.json").write_text(json.dumps({"scale": [0.05, 0.05]}))
        p, valide, maille = lire_la_surface(d)
        v("★★★ tifxyz : x, y, z dans cet ordre, −1 hors de la surface, la maille de l'échelle",
          valide.tolist() == [[True, True], [False, True]] and p[0, 1].tolist() == [2.0, 12.0, 102.0] and maille == 20.0
          and p[1, 0].tolist() == [0.0, 0.0, 0.0], f"{valide.tolist()} {p[0, 1]} {maille}")

    a, va = un_plan(500.0)
    na, oka = les_normales(a, va)
    v("★★ la normale de grille d'un plan de la batterie pointe vers +z", np.allclose(na[oka], [0, 0, 1]) and oka.sum() == 100,
      str(na[oka][:1]))

    def autres_de(*zs, decale=(0.0, 0.0)):
        g = {}
        for k, z in enumerate(zs):
            p, vv = un_plan(z, decale=decale)
            n, ok = les_normales(p, vv)
            g[f"b{k}"] = {"p": p[ok], "n": n[ok], "maille": 20.0}
        return LesAutres(g)

    pa, nna = a[oka], na[oka]
    t, k = les_passages(pa, nna, 1.0, autres_de(527.0))
    v("★★★ le passage d'une surface à 27 voxels est lu à 27, du bon côté", np.allclose(t, 27.0) and (k == 0).all(), str(t[:3]))
    t2, _ = les_passages(pa, nna, -1.0, autres_de(527.0))
    v("★★★ de l'autre côté, la même surface n'est pas rencontrée", np.isnan(t2).all(), str(t2[:3]))
    t3, k3 = les_passages(pa, nna, 1.0, autres_de(545.0, 525.0))
    v("★★★ le PREMIER passage : 25 avant 45", np.allclose(t3, 25.0) and (k3 == 1).all(), str(t3[:3]))
    t4, _ = les_passages(pa, nna, 1.0, autres_de(505.0))
    v("★★ un passage sous un demi-pas (la même feuille) ne compte pas", np.isnan(t4).all(), str(t4[:3]))
    t5, _ = les_passages(pa, nna, 1.0, autres_de(527.0, decale=(400.0, 0.0)))
    v("★★★ une surface qui n'est pas en face ne passe pas, même à la bonne hauteur", np.isnan(t5).all(), str(t5[:3]))
    t6, _ = les_passages(pa, nna, 1.0, autres_de(527.3))
    v("★★ le passage est interpolé entre deux pas d'un voxel", np.allclose(t6, 27.3, atol=1e-6), str(t6[:3]))
    t7, _ = les_passages(pa, nna, 1.0, autres_de(575.0))
    v("★★ au-delà de trois pas, rien", np.isnan(t7).all(), str(t7[:3]))
    g = {}
    for nom_, z_, dec_ in (("b0", 505.0, (0.0, 0.0)), ("b1", 535.0, (10.0, 10.0))):
        p_, vv_ = un_plan(z_, decale=dec_)
        n_, ok_ = les_normales(p_, vv_)
        g[nom_] = {"p": p_[ok_], "n": -n_[ok_], "maille": 20.0}
    t8, k8 = les_passages(pa, nna, 1.0, LesAutres(g))
    v("★★★ le sommet le plus proche qui passe d'une surface à l'autre n'est pas un passage : seul celui de 35 compte",
      np.allclose(t8, 35.0) and (k8 == 1).all(), str(t8[:3]))

    j = juger(np.array([20.0, 26.0, 20.0, 35.0, 20.0, np.nan, 50.0, 35.0]),
              np.array([20.0, 26.0, 26.0, 35.0, 35.0, 20.0, 35.0, np.nan]))
    v("★★★ juger : jugés dans la bande seulement, le transfert juste à un quart de pas, le témoin à un pas",
      j["les_jugés"] == 4 and j["justes_transfert"] == 2 and j["justes_temoin"] == 2, str(j))
    v("★★★ juger : au-delà de la bande, sur, avant, après", j["au_dela"] == {"les_points": 3, "sur": 1, "avant": 1, "apres": 1},
      str(j["au_dela"]))
    v("★★ juger : un écart négatif (côté moins) compte par sa valeur absolue",
      juger(np.array([-24.0]), np.array([24.0]))["justes_transfert"] == 1)
    v("★★ juger : un tour produit absent n'est jamais juste, le témoin l'est",
      juger(np.array([np.nan]), np.array([20.0]))["justes_transfert"] == 0 and juger(np.array([np.nan]), np.array([20.0]))["justes_temoin"] == 1)
    v("★★ juger : le témoin rate à 6 voxels du pas, pas à 5",
      juger(np.array([26.0, 25.0]), np.array([26.0, 25.0]))["justes_temoin"] == 1)

    def vd(pt, pw, n=5000, s=3, pannes=()):
        return le_verdict({"les_pannes": list(pannes), "les_surfaces_retenues": s,
                           "la_somme": {"les_jugés": n, "la_part_du_transfert": pt, "la_part_du_temoin": pw, "les_surfaces_jugées": s}})

    v("★★★ la règle : oui", vd(0.85, 0.7)["la_suite"] == "oui")
    v("★★★ la règle : à 0,8 tout juste, oui", vd(0.8, 0.75)["la_suite"] == "oui")
    v("★★★ la règle : la marge sur le témoin manque, en partie", vd(0.85, 0.82)["la_suite"] == "en partie")
    v("★★★ la règle : sous 0,5, non", vd(0.45, 0.3)["la_suite"] == "non")
    v("★★★ la règle : sous le témoin, non", vd(0.6, 0.65)["la_suite"] == "non")
    v("★★ la règle : en partie entre 0,5 et 0,8", vd(0.7, 0.5)["la_suite"] == "en partie")
    v("★★ la règle : indécidable sous 1000 points", not vd(0.9, 0.1, n=999)["decidable"])
    v("★★ la règle : indécidable sous 2 surfaces", not vd(0.9, 0.1, s=1)["decidable"])
    v("★★ la règle : indécidable si m7 n'a pas été lu", not vd(0.9, 0.1, pannes=["x"])["decidable"])

    feuilles = (500, 527, 554)

    def m7_de(idx):
        z = idx[..., 0]
        return np.isin(z, [f + dz for f in feuilles for dz in (-1, 0, 1)]).astype(np.uint8) * 255

    v("★★★ le contrôle : sur sa feuille, 1 ; décalé de 8 voxels, 0",
      le_controle(pa, nna, m7_de) == 1.0 and le_controle(pa + [0, 0, 8.0], nna, m7_de) == 0.0)
    s = m300.le_saut_suivant(a, va, 1.0, m7_de)
    ec = np.where(s["valide"], s["le_pas"], np.nan)[oka]
    v("★★★ le transfert de 300 trouve la feuille à 27 voxels, côté plus, et le passage aussi : juste, le témoin non",
      np.allclose(ec, 27.0) and juger(ec, les_passages(pa, nna, 1.0, autres_de(527.0))[0])["justes_transfert"] == 100
      and juger(ec, les_passages(pa, nna, 1.0, autres_de(527.0))[0])["justes_temoin"] == 0, str(ec[:3]))
    sm = m300.le_saut_suivant(a, va, -1.0, m7_de)
    v("★★ côté moins, sans feuille, le transfert garde le pas par défaut, négatif",
      np.allclose(np.where(sm["valide"], sm["le_pas"], np.nan)[oka], -LE_PAS), str(sm["le_pas"][oka.nonzero()][:3]))
    m = les_morceaux(pa, nna, (192, 192, 192))
    v("★★ les morceaux : un plan à z=500, ±60 voxels, x et y de 1020 à 1200, tient dans quatre morceaux de la couche 2",
      m == {(2, 5, 5), (2, 5, 6), (2, 6, 5), (2, 6, 6)}, str(sorted(m)))
    v("★★ les morceaux : à z=380, les couches 1 et 2", {c[0] for c in les_morceaux(pa - [0, 0, 120.0], nna, (192, 192, 192))} == {1, 2})

    for e in echecs:
        print(f"  ÉCHEC {e}")
    print(f"{Path(__file__).name}   {'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--preparer", action="store_true", help="les surfaces, et le compte des morceaux de m7, sans lire m7")
    p.add_argument("--transferer", action="store_true", help="le contrôle et le transfert de chaque surface")
    p.add_argument("--json", type=Path, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if a.preparer:
        print(json.dumps(preparer(), ensure_ascii=False, indent=1))
        return 0
    if a.transferer:
        return transferer()
    d = mesurer()
    texte = json.dumps(d, ensure_ascii=False, indent=1)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(texte + "\n")
    print(texte)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
