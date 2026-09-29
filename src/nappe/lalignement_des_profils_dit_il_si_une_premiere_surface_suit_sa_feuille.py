"""L'alignement des profils dit-il, au pas du prix, si une première surface suit sa feuille ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LES BLOCS D'ÉTALONNAGE NE SOIENT LUS ET AVANT QUE LES SURFACES JUGÉES SUR PHerc0358 NE
SOIENT POUSSÉES. Ce qui était vu avant d'écrire : tout ce que `298` publie, dont les amplitudes réunies du profil moyen sur les
six blocs de `296` (tracé 0,74, rampes 0,1 et 0,13, décalé 0,73) et le profil plat de la surface de `24`. C'est pourquoi
l'étalonnage se fait ici sur six autres blocs, et le rouleau sur des surfaces neuves.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P98`. `298` a montré que la note au point ne sépare pas : un tracé humain est posé
sur la face de sa feuille, où le rang du scan vaut à peu près 1/2. Mais le profil moyen du tracé se cale sur l'empilement, et
ceux des rampes plantées restent plats. Ce juge-là, l'alignement, doit être déclaré avant d'être mesuré, étalonné là où la
réponse est connue, puis porté sur une première surface qu'on n'a pas vue.

## Le juge : l'alignement d'une pièce contre ses propres traversées

Pour chaque point, le profil du scan brut le long de sa normale, ±200 µm, ramené à moyenne nulle et écart un, comme `298`.
L'alignement d'une pièce est l'amplitude (le plus haut moins le plus bas) de la moyenne de ses profils : des profils calés sur
les feuilles s'additionnent, des profils au hasard s'annulent. ⭐ Il n'a pas de valeur au hasard qui vaille partout : il dépend
du nombre de points et de la matière. Il est donc rapporté à celui des deux rampes de `298` plantées dans les propres points de
la pièce (pentes 1/4 et 1, amplitude deux pas), qui traversent l'empilement dans la même matière, avec le même nombre de
points. Le rapport R = alignement de la pièce / le plus grand des deux alignements de ses rampes vaut à peu près 1 pour une pièce
qui traverse déjà l'empilement, et d'autant plus que la pièce suit une feuille.

Une pièce **suit sa feuille** si R ≥ 2 ; **ne la suit pas** sinon ; **non jugée** si elle a moins de 100 points qui voient de la
matière. Le seuil 2 est posé avant de lire : l'alignement doit valoir le double de la meilleure des deux traversées plantées.

## L'étalonnage, sur PHercParis4 au niveau 2 (9,6 µm), sur six blocs neufs

Les six blocs : parmi les 340 candidats de `257`, triés, ceux de rang ⌊k(N − 1)/7⌉ pour k = 1 à 6, hors des six de `296`. Une
règle de position, aveugle à ce que les blocs contiennent. Chaque bloc est une pièce.

- surfaces qui suivent leur feuille : le segment réduit, et le premier saut de la chaîne de `248` (la spire produite de `275`) ;
- surfaces qui traversent : les deux rampes plantées dans le segment, jugées chacune contre ses propres rampes ;
- rapporté, qui ne décide rien : le segment décalé d'un demi-pas, que l'alignement ne doit pas voir.

Le juge sépare au pas du prix si, sur chacun des six blocs, le segment et le premier saut ont R ≥ 2, et les deux rampes R < 2.

## Le rouleau, et des surfaces qu'on n'a pas vues

PHerc0358, par la règle de `298`, qui y a une première surface. Les surfaces jugées sont neuves : les quatre premières graines
que `trouver_graine.py` rend sur la prédiction `m7` publiée (planarité, niveau 2, `--chunks 24`, à mi-hauteur, ses défauts), dans son
ordre, chacune poussée par `vc_grow_seg_from_seed` avec les paramètres de `24` (`seed.json`), puis jugée par pièces de 16 × 16
mailles au niveau 0 (9,362 µm), suréchantillonnées deux fois. Aucune n'a été vue avant d'être jugée. Leurs auto-intersections
(`vc_tifxyz_selfcross`) et leur part hors de la matière sont rapportées à côté.

## Les issues, exclusives

- l'étalonnage ne sépare pas : **au pas du prix, l'alignement des profils ne sépare pas une feuille d'une traversée**, et le
  rouleau n'est pas jugé ;
- sinon, pour chaque surface neuve, la part de ses points jugés qui sont dans des pièces qui suivent leur feuille ; et l'issue de
  la tranche : **la première surface qui suit sa feuille sur la moitié au moins de ses points jugés**, ou **aucune des quatre ne
  suit sa feuille sur la moitié de ses points jugés** ;
- indécidable si la chaîne de `297` ne se redonne pas, si aucune graine ne pousse de surface, ou si aucune pièce n'est jugée.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : sur quelle feuille la surface est posée, ni si elle passe d'une feuille à la voisine sans
se croiser : l'alignement d'une pièce ne voit pas un saut qui garde la phase, et une pièce assez grande pour contenir un saut en
voit la moyenne. Ni que la surface soit le recto, ni qu'elle se déroule ; ni ce que vaut un tirage du traceur plutôt qu'un autre
(`R3-F05`) : chaque graine est poussée une fois.

Usage :
    uv run python src/nappe/lalignement_des_profils_dit_il_si_une_premiere_surface_suit_sa_feuille.py --verifier
    uv run python src/nappe/lalignement_des_profils_dit_il_si_une_premiere_surface_suit_sa_feuille.py --graines
    uv run python src/nappe/lalignement_des_profils_dit_il_si_une_premiere_surface_suit_sa_feuille.py --pousser
    uv run python src/nappe/lalignement_des_profils_dit_il_si_une_premiere_surface_suit_sa_feuille.py --preparer
    uv run python src/nappe/lalignement_des_profils_dit_il_si_une_premiere_surface_suit_sa_feuille.py --lire 8
    uv run python src/nappe/lalignement_des_profils_dit_il_si_une_premiere_surface_suit_sa_feuille.py \\
        --json docs/mesures/lalignement_des_profils_dit_il_si_une_premiere_surface_suit_sa_feuille.json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "tracecheck"))

import la_matiere_dit_elle_si_la_surface_est_sur_sa_feuille as m298  # noqa: E402

LE_DOSSIER = RACINE / "data" / "alignement_au_pas_du_prix"
LES_SURFACES_PREPAREES = LE_DOSSIER / "surfaces"
LES_TRACES = LE_DOSSIER / "traces"
LES_GRAINES = LE_DOSSIER / "graines.json"
LE_PLAN = LE_DOSSIER / "plan.json"
LA_PREDICTION_0358 = ("PHerc0358/representations/predictions/surfaces/"
                      "20250821151737-surface-20260413222639-surface-m7-L0-th0.2.zarr")
LES_PARAMETRES_DE_24 = RACINE / "data" / "artefacts" / "PHerc0358" / "seed.json"
LA_GRAINE_DE_24 = (1544, 1544, 7768)
LES_GRAINES_POUSSEES = 4
LE_RAPPORT_MINIMUM = 2.0
LES_BLOCS = 6


# ── Le juge ────────────────────────────────────────────────────────────────────────────────────────────────────────

def lalignement(profils: np.ndarray) -> float | None:
    """L'amplitude du profil moyen, chaque profil ramené à moyenne nulle et écart un ; None sans profil."""
    if len(profils) == 0:
        return None
    return m298.le_relief(m298.le_profil_moyen(profils))["lamplitude"]


def le_rapport(a: float | None, a_douce: float | None, a_raide: float | None) -> float | None:
    """L'alignement d'une pièce rapporté au plus grand de ceux de ses deux rampes."""
    if a is None or a_douce is None or a_raide is None:
        return None
    temoin = max(a_douce, a_raide)
    return round(a / temoin, 3) if temoin > 0 else None


def la_piece(r: float | None, n: int, seuil: float = LE_RAPPORT_MINIMUM) -> str:
    if r is None or n < m298.LE_MINIMUM_DE_POINTS_PAR_PIECE:
        return "non jugée"
    return "suit sa feuille" if r >= seuil else "ne la suit pas"


def letalonnage_separe(blocs: list[dict]) -> dict:
    """Le juge sépare si, sur chaque bloc, le segment et le premier saut ont R ≥ 2 et les deux rampes R < 2."""
    raisons = []
    for b in blocs:
        for nom in ("le_segment", "saut_1"):
            if b[nom] is None or not b[nom] >= LE_RAPPORT_MINIMUM:
                raisons.append(f"bloc {b['le_bloc']} : le {nom} n'a pas R ≥ 2 ({b[nom]})")
        for nom in ("rampe_douce", "rampe_raide"):
            if b[nom] is None or not b[nom] < LE_RAPPORT_MINIMUM:
                raisons.append(f"bloc {b['le_bloc']} : la {nom} a R ≥ 2 ({b[nom]})")
    return {"separe": not raisons and len(blocs) == LES_BLOCS, "les_raisons": raisons}


def la_part_qui_suit(pieces: list[dict]) -> tuple[float | None, int]:
    """La part des points jugés qui sont dans des pièces qui suivent leur feuille, et le nombre de points jugés."""
    total = sum(p["les_points_juges"] for p in pieces if p["la_piece"] != "non jugée")
    suit = sum(p["les_points_juges"] for p in pieces if p["la_piece"] == "suit sa feuille")
    return (round(suit / total, 4) if total else None), int(total)


def le_verdict(d: dict) -> dict:
    if not d.get("la_chaine_de_297_se_redonne"):
        return {"decidable": False, "lissue": "indécidable : la chaîne de 297 ne se redonne pas"}
    if not d["letalonnage"]["le_verdict"]["separe"]:
        return {"decidable": True, "separe": False,
                "lissue": "au pas du prix, l'alignement des profils ne sépare pas une feuille d'une traversée"}
    surfaces = d["le_rouleau"]["les_surfaces"]
    if not surfaces:
        return {"decidable": False, "separe": True, "lissue": "indécidable : aucune graine n'a poussé de surface"}
    jugees = [s for s in surfaces if s["les_points_juges_en_pieces"] > 0]
    if not jugees:
        return {"decidable": False, "separe": True, "lissue": "indécidable : aucune pièce n'est jugée"}
    for s in surfaces:
        if s["la_part_qui_suit"] is not None and s["la_part_qui_suit"] >= 0.5:
            return {"decidable": True, "separe": True, "la_surface": s["la_graine"],
                    "lissue": f"la surface de la graine {s['le_rang']} suit sa feuille sur {s['la_part_qui_suit']} de ses "
                              "points jugés"}
    return {"decidable": True, "separe": True,
            "lissue": "aucune des surfaces neuves ne suit sa feuille sur la moitié de ses points jugés"}


# ── Les blocs, les graines, les traces ─────────────────────────────────────────────────────────────────────────────

def les_blocs_neufs(candidats: list, deja: list, combien: int = LES_BLOCS) -> list[tuple]:
    """Parmi les candidats triés, hors de `deja`, ceux de rang arrondi k(N − 1)/(combien + 1), k = 1 à `combien`."""
    reste = sorted(tuple(c) for c in candidats if tuple(c) not in {tuple(x) for x in deja})
    n = len(reste)
    rangs = [int(np.floor(k * (n - 1) / (combien + 1) + 0.5)) for k in range(1, combien + 1)]
    return [reste[r] for r in rangs]


def les_graines_retenues(graines: list[dict], combien: int = LES_GRAINES_POUSSEES, loin: float = 64.0) -> list[dict]:
    """Les premières graines, dans l'ordre rendu, en écartant celle de `24` si elle revient."""
    out = []
    for g in graines:
        if max(abs(g["x"] - LA_GRAINE_DE_24[0]), abs(g["y"] - LA_GRAINE_DE_24[1]),
               abs(g["z"] - LA_GRAINE_DE_24[2])) <= loin:
            continue
        out.append(g)
        if len(out) == combien:
            break
    return out


def trouver_les_graines() -> dict:
    LE_DOSSIER.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, str(RACINE / "src" / "commun" / "trouver_graine.py"), LA_PREDICTION_0358, "--level", "2",
           "--chunks", "24", "--candidats", "8", "--voxel-um", "9.362", "--out", str(LES_GRAINES)]
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=RACINE)
    return {"le_code": p.returncode, "la_sortie": p.stdout[-4000:], "les_erreurs": p.stderr[-2000:]}


def lire_les_graines() -> list[dict]:
    d = json.loads(LES_GRAINES.read_text())
    return d["candidats"] if isinstance(d, dict) else d


def pousser() -> dict:
    """Chaque graine retenue poussée une fois, avec les paramètres de `24` ; puis ses auto-intersections."""
    graines = les_graines_retenues(lire_les_graines())
    url = f"{m298.BUCKET}/{LA_PREDICTION_0358}"
    out = []
    for rang, g in enumerate(graines, 1):
        dossier = LES_TRACES / f"graine_{rang}"
        dossier.mkdir(parents=True, exist_ok=True)
        existantes = sorted(dossier.glob("auto_grown_*"))
        t0 = time.monotonic()
        if not existantes:
            p = subprocess.run(["vc_grow_seg_from_seed", "-v", url, "-t", str(dossier), "-p", str(LES_PARAMETRES_DE_24),
                                "-s", str(g["x"]), str(g["y"]), str(g["z"])], capture_output=True, text=True)
            (dossier / "pousser.log").write_text(p.stdout[-20000:] + "\n--- stderr ---\n" + p.stderr[-20000:])
            existantes = sorted(dossier.glob("auto_grown_*"))
        e = {"le_rang": rang, "la_graine": [g["x"], g["y"], g["z"]], "les_secondes": round(time.monotonic() - t0, 1),
             "la_surface": str(existantes[-1].relative_to(RACINE)) if existantes else None}
        if existantes:
            sc = dossier / "selfcross.json"
            if not sc.exists():
                subprocess.run(["vc_tifxyz_selfcross", "--surface", str(existantes[-1]), "-o", str(sc)],
                               capture_output=True, text=True)
            try:
                s = json.loads(sc.read_text())
                e["les_contacts_transverses"] = int(sum(c.get("transverse", 0) for c in s.get("census", [])))
            except (OSError, ValueError):
                e["les_contacts_transverses"] = None
            meta = json.loads((existantes[-1] / "meta.json").read_text())
            e["laire_cm2"] = round(float(meta.get("area_cm2", 0.0)), 3)
        out.append(e)
        print(json.dumps(e, ensure_ascii=False), flush=True)
    (LE_DOSSIER / "traces.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    return {"les_traces": out}


# ── Préparer, lire, mesurer ────────────────────────────────────────────────────────────────────────────────────────

def les_rampes_de(points, valide, normales, n_ok, demi, pas, pas_de_grille) -> dict:
    """Les deux rampes plantées dans une surface, et son décalé, chacun avec ses normales recalculées."""
    from la_spire_voisine_est_elle_a_un_pas import les_normales

    out = {}
    for nom, (dp, dok) in m298.les_defauts(points, valide, normales, n_ok, demi, pas, pas_de_grille).items():
        nn, nok = les_normales(dp, dok)
        out[nom] = (dp, dok & nok, nn)
    return out


def la_famille(nom: str, points, valide, normales, n_ok, demi, pas, pas_de_grille, avec_decale: bool) -> dict:
    """Une surface jugée et ses témoins : `nom`, `nom__rampe_douce`, `nom__rampe_raide`, et son décalé si demandé."""
    fam = {nom: (points, valide & n_ok, normales)}
    for d, v in les_rampes_de(points, valide, normales, n_ok, demi, pas, pas_de_grille).items():
        if d in m298.LES_PENTES or avec_decale:
            fam[f"{nom}__{d}"] = v
    return fam


def les_surfaces_de_paris4() -> tuple[dict, list]:
    import le_tour_produit_porte_t_il_le_texte_du_segment as j296
    from la_procedure_sans_juge_tient_elle_sur_le_segment_entier import le_segment
    from la_spire_voisine_est_elle_a_un_pas import LE_CACHE, les_normales, lire_tifxyz
    from que_montrent_ces_deux_vues import DEMI_PAS_EN_VOXELS, PAS_EN_VOXELS

    k = m298.LE_SURECHANTILLONNAGE["PHercParis4"]
    deja = json.loads(j296.LE_PLAN.read_text())["les_blocs_de_la_partie_b"]
    _, _, _, candidats = le_segment(LE_CACHE)
    blocs = les_blocs_neufs(sorted(candidats), deja)
    grilles = {"le_segment": lire_tifxyz(j296.LE_DOSSIER / j296.LES_SURFACES[0] / "maillage"),
               "saut_1": lire_tifxyz(j296.LE_DOSSIER / j296.LES_SURFACES[1] / "maillage")}
    esp = grilles["le_segment"][2]
    out: dict = {}
    for b in blocs:
        lignes, colonnes = j296.les_mailles_dune_bande(*b, 1, esp)
        for n, (pts, ok, _) in grilles.items():
            L, C = lignes[lignes < ok.shape[0]], colonnes[colonnes < ok.shape[1]]
            sp, sok = m298.surechantillonner(pts[np.ix_(L, C)], ok[np.ix_(L, C)], k)
            nn, nok = les_normales(sp, sok)
            fam = la_famille(n, sp, sok, nn, nok, float(DEMI_PAS_EN_VOXELS), float(PAS_EN_VOXELS), esp / k,
                             avec_decale=(n == "le_segment"))
            if n == "le_segment":
                for r in m298.LES_PENTES:
                    rp, rok, rn = fam[f"le_segment__{r}"]
                    fam.update(la_famille(r, rp, rok, rn, np.ones_like(rok), float(DEMI_PAS_EN_VOXELS),
                                          float(PAS_EN_VOXELS), esp / k, avec_decale=False))
                dp, dok, dn = fam.pop("le_segment__decale_dun_demi_pas")
                fam.update(la_famille("decale_dun_demi_pas", dp, dok, dn, np.ones_like(dok), float(DEMI_PAS_EN_VOXELS),
                                      float(PAS_EN_VOXELS), esp / k, avec_decale=False))
            for nom, (p, m, nr) in fam.items():
                out.setdefault(nom, []).append({"le_bloc": list(b), "points": p[m], "normales": nr[m], "juge": None})
    return out, [list(b) for b in blocs]


def les_surfaces_de_0358(traces: list[dict]) -> dict:
    from la_spire_voisine_est_elle_a_un_pas import les_normales, lire_tifxyz

    k = m298.LE_SURECHANTILLONNAGE["PHerc0358"]
    pas = (float(json.loads(m298.LE_PAS_DE_0358.read_text())["seuils"]["0.5"]["median_um"])
           / m298.LES_VOLUMES["PHerc0358"]["le_voxel_um"])
    P = m298.LA_PIECE_EN_MAILLES * k
    out: dict = {}
    for t in traces:
        if not t.get("la_surface"):
            continue
        pts, ok, esp = lire_tifxyz(RACINE / t["la_surface"])
        sp, sok = m298.surechantillonner(pts, ok, k)
        nn, nok = les_normales(sp, sok)
        fam = la_famille(f"graine_{t['le_rang']}", sp, sok, nn, nok, pas / 2.0, pas, esp / k, avec_decale=True)
        for nom, (p, m, nr) in fam.items():
            out[nom] = []
            for i0 in range(0, m.shape[0], P):
                for j0 in range(0, m.shape[1], P):
                    mm = m[i0:i0 + P, j0:j0 + P]
                    if mm.any():
                        out[nom].append({"la_piece": [i0 // k, j0 // k], "points": p[i0:i0 + P, j0:j0 + P][mm],
                                         "normales": nr[i0:i0 + P, j0:j0 + P][mm], "juge": None})
    return out


def ranger(nom: str, morceaux: list[dict], cle: str) -> Path:
    LES_SURFACES_PREPAREES.mkdir(parents=True, exist_ok=True)
    f = LES_SURFACES_PREPAREES / f"{nom}.npz"
    vide = np.zeros((0, 3))
    np.savez_compressed(f, points=np.concatenate([m["points"] for m in morceaux]) if morceaux else vide,
                        normales=np.concatenate([m["normales"] for m in morceaux]) if morceaux else vide,
                        groupe=np.concatenate([np.full(len(m["points"]), i) for i, m in enumerate(morceaux)])
                        if morceaux else np.zeros(0, dtype=int),
                        juge=np.full(sum(len(m["points"]) for m in morceaux), np.nan),
                        groupes=np.array([json.dumps(m[cle]) for m in morceaux]))
    return f


def preparer() -> dict:
    t0 = time.monotonic()
    plan297 = json.loads(m298.CE_QUE_297_A_PREPARE.read_text())
    se_redonne = bool((plan297.get("la_chaine_redonne_248") or {}).get("tous")
                      and plan297.get("le_premier_saut_est_la_spire_produite"))
    paris, blocs = les_surfaces_de_paris4()
    traces = json.loads((LE_DOSSIER / "traces.json").read_text())
    prix = les_surfaces_de_0358(traces)
    plan = {"la_chaine_de_297_se_redonne": se_redonne, "les_blocs": blocs, "les_traces": traces, "les_surfaces": {},
            "les_morceaux": {}}
    for volume, surfaces, cle in (("PHercParis4", paris, "le_bloc"), ("PHerc0358", prix, "la_piece")):
        v = m298.LES_VOLUMES[volume]
        vol = m298.LesMorceaux(volume, v["url"], v["niveau"])
        T = m298.la_demi_fenetre(volume)
        tous = set()
        for nom, morceaux in surfaces.items():
            f = ranger(f"{volume}__{nom}", morceaux, cle)
            n = sum(len(m["points"]) for m in morceaux)
            if n:
                pts = np.concatenate([m["points"] for m in morceaux])
                nrm = np.concatenate([m["normales"] for m in morceaux])
                coords = m298.les_coordonnees(pts, nrm, v["facteur"], T)
                tous |= m298.les_morceaux_complets(coords[m298.dans_le_volume(coords, vol.forme)], vol.taille)
            plan["les_surfaces"][f"{volume}__{nom}"] = {"le_fichier": str(f.relative_to(RACINE)), "les_points": n,
                                                          "les_groupes": len(morceaux)}
        cles = sorted(tous)
        (LE_DOSSIER / f"morceaux_{volume}.json").write_text(json.dumps(cles))
        plan["les_morceaux"][volume] = {"combien": len(cles), "les_octets": int(len(cles) * np.prod(vol.taille))}
    plan["les_secondes"] = round(time.monotonic() - t0, 1)
    LE_PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=1))
    return plan


def lire(ouvriers: int = 8) -> dict:
    """Les morceaux sont rangés au même endroit que ceux de `298` : ce qui y est déjà n'est pas retiré."""
    out = {}
    for volume, v in m298.LES_VOLUMES.items():
        t0 = time.monotonic()
        cles = [tuple(c) for c in json.loads((LE_DOSSIER / f"morceaux_{volume}.json").read_text())]
        vol = m298.LesMorceaux(volume, v["url"], v["niveau"])
        comptes = {"deja": 0, "tire": 0, "absent": 0}
        with ThreadPoolExecutor(ouvriers) as ex:
            for r in ex.map(lambda c: vol.tirer(*c), cles):
                comptes[r] += 1
        out[volume] = dict(comptes, combien=len(cles), les_secondes=round(time.monotonic() - t0, 1))
        print(json.dumps({volume: out[volume]}), flush=True)
    return out


def juger(vol, fichier: Path, facteur: float, T: int) -> list[dict]:
    """Par groupe (bloc ou pièce) : l'alignement, les points jugés, sans matière, hors du volume."""
    z = np.load(fichier)
    pts, nrm, groupe = z["points"], z["normales"], z["groupe"]
    groupes = [json.loads(g) for g in z["groupes"]]
    out = []
    if len(pts) == 0:
        return out
    coords = m298.les_coordonnees(pts, nrm, facteur, T)
    dedans = m298.dans_le_volume(coords, vol.forme)
    profils = np.zeros((len(pts), 2 * T + 1), dtype=np.float32)
    if dedans.any():
        profils[dedans] = m298.les_profils(vol, coords[dedans])
    vide = m298.sans_matiere(profils) & dedans
    juge = dedans & ~vide
    for i, g in enumerate(groupes):
        m = groupe == i
        out.append({"le_groupe": g, "lalignement": lalignement(profils[m & juge]), "les_points_juges": int((m & juge).sum()),
                    "sans_matiere": int((m & vide).sum()), "hors_du_volume": int((m & ~dedans).sum())})
    return out


def la_table(res: dict, nom: str) -> list[dict]:
    """Par groupe, le rapport R d'une surface à ses deux rampes."""
    a, d_, r_ = res[nom], res[f"{nom}__rampe_douce"], res[f"{nom}__rampe_raide"]
    out = []
    for g in a:
        gd = next((x for x in d_ if x["le_groupe"] == g["le_groupe"]), None)
        gr = next((x for x in r_ if x["le_groupe"] == g["le_groupe"]), None)
        R = le_rapport(g["lalignement"], gd and gd["lalignement"], gr and gr["lalignement"])
        out.append(dict(g, lalignement_rampe_douce=gd and gd["lalignement"], lalignement_rampe_raide=gr and gr["lalignement"],
                        le_rapport=R, la_piece=la_piece(R, g["les_points_juges"])))
    return out


def les_releves(d: dict) -> dict:
    """Ce qui se lit de la mesure sans rien décider : l'alignement lui-même, sans le rapport, sur l'étalonnage et sur les
    pièces jugées de chaque surface neuve, à côté de celui de leurs rampes."""
    def med(xs):
        xs = [x for x in xs if x is not None]
        return round(float(np.median(xs)), 3) if xs else None

    out = {"letalonnage": {}, "le_rouleau": []}
    for nom, t in d["letalonnage"]["les_tables"].items():
        a = [g["lalignement"] for g in t if g["lalignement"] is not None]
        r = [x for g in t for x in (g["lalignement_rampe_douce"], g["lalignement_rampe_raide"]) if x is not None]
        out["letalonnage"][nom] = {"lalignement_min": min(a) if a else None, "lalignement_max": max(a) if a else None,
                                   "celui_des_rampes_min": min(r) if r else None,
                                   "celui_des_rampes_max": max(r) if r else None}
    for s in d["le_rouleau"]["les_surfaces"]:
        jug = [p for p in s["le_detail"] if p["la_piece"] != "non jugée"]
        out["le_rouleau"].append({"le_rang": s["le_rang"], "les_pieces_jugees": len(jug),
                                  "le_rapport_median": med([p["le_rapport"] for p in jug]),
                                  "lalignement_median": med([p["lalignement"] for p in jug]),
                                  "celui_de_la_rampe_douce": med([p["lalignement_rampe_douce"] for p in jug]),
                                  "celui_de_la_rampe_raide": med([p["lalignement_rampe_raide"] for p in jug]),
                                  "la_part_sans_matiere": round(s["sans_matiere"] / s["les_points"], 4)
                                  if s["les_points"] else None})
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
                res[cle.split("__", 1)[1] if volume == "PHercParis4" else "0358:" + cle.split("__", 1)[1]] = \
                    juger(vol, RACINE / info["le_fichier"], v["facteur"], T)
                print(f"{cle} ({time.monotonic() - t0:.0f} s)", flush=True)
    paris = {k: v for k, v in res.items() if not k.startswith("0358:")}
    tables = {n: la_table(paris, n) for n in ("le_segment", "saut_1", "rampe_douce", "rampe_raide", "decale_dun_demi_pas")}
    blocs = []
    for i, b in enumerate(plan["les_blocs"]):
        blocs.append({"le_bloc": b, **{n: tables[n][i]["le_rapport"] for n in tables},
                      "lalignement": {n: tables[n][i]["lalignement"] for n in tables},
                      "les_points_juges": {n: tables[n][i]["les_points_juges"] for n in tables}})
    e = {"les_blocs": blocs, "le_verdict": letalonnage_separe(blocs), "les_tables": tables}
    prix = {k.split(":", 1)[1]: v for k, v in res.items() if k.startswith("0358:")}
    surfaces = []
    for t in plan["les_traces"]:
        nom = f"graine_{t['le_rang']}"
        if nom not in prix:
            continue
        pieces = la_table(prix, nom)
        part, n = la_part_qui_suit(pieces)
        total = sum(p["les_points_juges"] + p["sans_matiere"] + p["hors_du_volume"] for p in prix[nom])
        surfaces.append({"le_rang": t["le_rang"], "la_graine": t["la_graine"], "laire_cm2": t.get("laire_cm2"),
                         "les_contacts_transverses": t.get("les_contacts_transverses"), "la_part_qui_suit": part,
                         "les_points_juges_en_pieces": n, "les_points": int(total),
                         "sans_matiere": int(sum(p["sans_matiere"] for p in prix[nom])),
                         "les_pieces": {v: sum(1 for p in pieces if p["la_piece"] == v)
                                        for v in ("suit sa feuille", "ne la suit pas", "non jugée")},
                         "le_detail": pieces})
    d = {"la_question": __doc__.splitlines()[0], "la_chaine_de_297_se_redonne": plan["la_chaine_de_297_se_redonne"],
         "les_constantes": {"le_rapport_minimum": LE_RAPPORT_MINIMUM, "les_graines_poussees": LES_GRAINES_POUSSEES,
                            "la_fenetre_um": m298.LA_FENETRE_UM, "la_piece_en_mailles": m298.LA_PIECE_EN_MAILLES,
                            "les_pentes": m298.LES_PENTES},
         "letalonnage": e, "le_rouleau": {"les_surfaces": surfaces, "les_traces": plan["les_traces"]},
         "les_morceaux": plan["les_morceaux"]}
    d["le_verdict"] = le_verdict(d)
    d["les_releves"] = les_releves(d)
    d["les_secondes"] = round(time.monotonic() - t0, 1)
    return d


# ── La batterie ────────────────────────────────────────────────────────────────────────────────────────────────────

def verifier() -> int:
    import tempfile

    from la_spire_voisine_est_elle_a_un_pas import les_normales

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

    tmp = Path(tempfile.mkdtemp())
    pas, taille = 18.0, 16

    def profils_de(volume, pts, nrm, nom):
        meta = {"shape": list(volume.shape), "chunks": [taille] * 3, "fill_value": 0, "compressor": None}
        vol = m298.LesMorceaux(nom, None, 0, meta=meta, source=m298._source_de(volume, taille), dossier=tmp)
        coords = m298.les_coordonnees(pts, nrm, 1.0, 21)
        dedans = m298.dans_le_volume(coords, vol.forme)
        for c in m298.les_morceaux_complets(coords[dedans], vol.taille):
            vol.tirer(*c)
        pr = m298.les_profils(vol, coords[dedans])
        return pr[~m298.sans_matiere(pr)]

    def plan_z(z, n=48, espace=2.0):
        g = np.zeros((n, n, 3))
        for i in range(n):
            for j in range(n):
                g[i, j] = (40.0 + j * espace, 40.0 + i * espace, z)
        return g

    V = m298._feuillets((200, 150, 150), pas, 0, 3.0, bruit=6.0)
    G = plan_z(5 * pas + 4.0)                          # sur le flanc de sa feuille, comme un tracé humain
    OK = np.ones(G.shape[:2], dtype=bool)
    N, NOK = les_normales(G, OK)
    fam = la_famille("s", G, OK, N, NOK, pas / 2, pas, 2.0, avec_decale=True)
    al = {n: lalignement(profils_de(V, p[m], nr[m], f"v_{n}")) for n, (p, m, nr) in fam.items()}
    R = le_rapport(al["s"], al["s__rampe_douce"], al["s__rampe_raide"])
    v("★★★★ une surface posée sur le flanc de sa feuille est alignée : R ≥ 2", lambda: R >= 2.0, f"{R} {al}")
    v("★★★ son décalé d'un demi-pas reste aligné : le juge ne voit pas un décalage",
      lambda: al["s__decale_dun_demi_pas"] > 0.5 * al["s"], str(al))
    rp, rm, rn = fam["s__rampe_douce"]
    fr_ = la_famille("r", rp, rm, rn, np.ones_like(rm), pas / 2, pas, 2.0, avec_decale=False)
    alr = {n: lalignement(profils_de(V, p[m], nr[m], f"w_{n}")) for n, (p, m, nr) in fr_.items()}
    Rr = le_rapport(alr["r"], alr["r__rampe_douce"], alr["r__rampe_raide"])
    v("★★★★ une rampe, jugée contre ses propres rampes, n'est pas alignée : R < 2", lambda: Rr < 2.0, f"{Rr} {alr}")
    rng = np.random.default_rng(5)
    ph = rng.uniform(0, 1, 3000)
    t = np.arange(-21, 22)
    hasard = np.cos(2 * np.pi * (t[None, :] / pas + ph[:, None])).astype(np.float32)
    cale = np.cos(2 * np.pi * (t[None, :] / pas + 0.1)).astype(np.float32) + 0.05 * hasard
    v("★★★ l'alignement : des profils calés s'additionnent, des profils au hasard s'annulent",
      lalignement(cale) > 1.5 and lalignement(hasard) < 0.2, f"{lalignement(cale)} {lalignement(hasard)}")
    v("★★ sans profil, pas d'alignement", lalignement(np.zeros((0, 43))) is None)
    v("★★★ le rapport prend la plus alignée des deux rampes", le_rapport(0.8, 0.1, 0.4) == 2.0
      and le_rapport(0.8, 0.0, 0.0) is None and le_rapport(None, 0.1, 0.1) is None)
    v("★★★ une pièce : suit si R ≥ 2, ne suit pas sinon, non jugée sous 100 points",
      la_piece(2.0, 500) == "suit sa feuille" and la_piece(1.99, 500) == "ne la suit pas"
      and la_piece(5.0, 99) == "non jugée" and la_piece(None, 500) == "non jugée")
    bl = {"le_bloc": [1, 1], "le_segment": 4.0, "saut_1": 3.0, "rampe_douce": 1.1, "rampe_raide": 0.9}
    v("★★★★ l'étalonnage sépare quand les six blocs ordonnent", letalonnage_separe([bl] * 6)["separe"])
    for casse, nom in ((dict(bl, saut_1=1.9), "le premier saut sous 2"), (dict(bl, rampe_raide=2.0), "une rampe à 2"),
                       (dict(bl, le_segment=None), "une note absente")):
        v(f"★★★★ l'étalonnage ne sépare pas si un seul bloc a {nom}", not letalonnage_separe([bl] * 5 + [casse])["separe"])
    v("★★★ l'étalonnage ne sépare pas sur moins de six blocs", not letalonnage_separe([bl] * 5)["separe"])
    pcs = [{"la_piece": "suit sa feuille", "les_points_juges": 300}, {"la_piece": "ne la suit pas", "les_points_juges": 100},
           {"la_piece": "non jugée", "les_points_juges": 40}]
    v("★★★★ la part qui suit, sans les pièces non jugées", la_part_qui_suit(pcs) == (0.75, 400))
    base = {"la_chaine_de_297_se_redonne": True, "letalonnage": {"le_verdict": {"separe": True}},
            "le_rouleau": {"les_surfaces": [
                {"le_rang": 1, "la_graine": [1, 2, 3], "la_part_qui_suit": 0.3, "les_points_juges_en_pieces": 500},
                {"le_rang": 2, "la_graine": [4, 5, 6], "la_part_qui_suit": 0.6, "les_points_juges_en_pieces": 500}]}}
    vd = le_verdict(base)
    v("★★★★ l'issue : la première surface qui suit sa feuille sur la moitié de ses points",
      vd["decidable"] and vd.get("la_surface") == [4, 5, 6] and "graine 2" in vd["lissue"], str(vd))
    b1 = json.loads(json.dumps(base))
    b1["le_rouleau"]["les_surfaces"][0]["la_part_qui_suit"] = 0.5
    v("★★★ l'issue : la première dans l'ordre des graines, à égalité de seuil comprise",
      le_verdict(b1).get("la_surface") == [1, 2, 3], str(le_verdict(b1)))
    b2 = json.loads(json.dumps(base))
    b2["le_rouleau"]["les_surfaces"][1]["la_part_qui_suit"] = 0.49
    v("★★★★ l'issue : aucune ne suit sur la moitié", le_verdict(b2)["lissue"].startswith("aucune"))
    b3 = json.loads(json.dumps(base))
    b3["letalonnage"]["le_verdict"]["separe"] = False
    v("★★★★ l'issue : un étalonnage qui ne sépare pas ne juge pas le rouleau",
      le_verdict(b3)["separe"] is False and "ne sépare pas" in le_verdict(b3)["lissue"])
    b4 = json.loads(json.dumps(base))
    b4["le_rouleau"]["les_surfaces"] = []
    v("★★★ l'issue : indécidable sans surface poussée", not le_verdict(b4)["decidable"])
    b5 = json.loads(json.dumps(base))
    for s in b5["le_rouleau"]["les_surfaces"]:
        s["les_points_juges_en_pieces"] = 0
    v("★★★ l'issue : indécidable sans pièce jugée", not le_verdict(b5)["decidable"])
    v("★★★ l'issue : indécidable si la chaîne ne se redonne pas",
      not le_verdict(dict(base, la_chaine_de_297_se_redonne=False))["decidable"])
    cand = [(r, c) for r in range(0, 100, 10) for c in range(0, 50, 10)]
    sans = les_blocs_neufs(cand, [])
    nb = les_blocs_neufs(cand, sans[:3])
    v("★★★ les blocs neufs : six, dans l'ordre, étalés sur les candidats, hors des blocs déjà vus",
      len(nb) == 6 and nb == sorted(nb) and not set(nb) & set(sans[:3]) and nb[0] != nb[-1]
      and sans == les_blocs_neufs(list(reversed(cand)), []), f"{sans} {nb}")
    echelle = np.random.default_rng(7).uniform(0.2, 30.0, len(cale)).astype(np.float32)
    v("★★★ l'alignement ne dépend ni de la luminosité ni du contraste de chaque point",
      abs(lalignement(cale * echelle[:, None] + 40.0 * echelle[:, None]) - lalignement(cale)) < 0.02,
      f"{lalignement(cale * echelle[:, None] + 40.0 * echelle[:, None])} {lalignement(cale)}")
    fausse = {"letalonnage": {"les_tables": {"le_segment": [
        {"lalignement": 0.8, "lalignement_rampe_douce": 0.2, "lalignement_rampe_raide": 0.1},
        {"lalignement": 0.6, "lalignement_rampe_douce": None, "lalignement_rampe_raide": 0.3}]}},
        "le_rouleau": {"les_surfaces": [{"le_rang": 1, "sans_matiere": 50, "les_points": 200, "le_detail": [
            {"la_piece": "ne la suit pas", "le_rapport": 0.9, "lalignement": 0.2, "lalignement_rampe_douce": 0.2,
             "lalignement_rampe_raide": 0.3},
            {"la_piece": "non jugée", "le_rapport": 9.0, "lalignement": 9.0, "lalignement_rampe_douce": 1.0,
             "lalignement_rampe_raide": 1.0},
            {"la_piece": "suit sa feuille", "le_rapport": 3.0, "lalignement": 0.6, "lalignement_rampe_douce": 0.2,
             "lalignement_rampe_raide": 0.1}]}]}}
    rl = les_releves(fausse)
    v("★★★ les relevés : sans les pièces non jugées, les rampes à part, les extrêmes de l'étalonnage",
      rl["le_rouleau"][0]["lalignement_median"] == 0.4 and rl["le_rouleau"][0]["les_pieces_jugees"] == 2
      and rl["le_rouleau"][0]["la_part_sans_matiere"] == 0.25
      and rl["letalonnage"]["le_segment"] == {"lalignement_min": 0.6, "lalignement_max": 0.8, "celui_des_rampes_min": 0.1,
                                              "celui_des_rampes_max": 0.3}, str(rl))
    gr = [{"x": 1544, "y": 1544, "z": 7768}, {"x": 10, "y": 10, "z": 10}, {"x": 20, "y": 20, "z": 20},
          {"x": 1550, "y": 1540, "z": 7770}, {"x": 30, "y": 30, "z": 30}, {"x": 40, "y": 40, "z": 40},
          {"x": 50, "y": 50, "z": 50}]
    v("★★★ les graines : les quatre premières dans l'ordre rendu, sans celle de 24",
      [g["x"] for g in les_graines_retenues(gr)] == [10, 20, 30, 40])

    for e in echecs:
        print(f"  ÉCHEC {e}")
    print(f"{Path(__file__).name}   {'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--graines", action="store_true", help="les graines de trouver_graine, sur la prédiction publiée")
    p.add_argument("--pousser", action="store_true", help="les surfaces neuves, une par graine retenue")
    p.add_argument("--preparer", action="store_true")
    p.add_argument("--lire", type=int, default=None, metavar="OUVRIERS")
    p.add_argument("--json", type=Path, default=None)
    p.add_argument("--releves", type=Path, default=None, metavar="MESURE",
                   help="recalcule les relevés d'une mesure déjà faite, sans rien relire du scan")
    a = p.parse_args()
    if a.releves is not None:
        d = json.loads(a.releves.read_text())
        d["les_releves"] = les_releves(d)
        a.releves.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n")
        print(json.dumps(d["les_releves"], ensure_ascii=False, indent=1))
        return 0
    if a.verifier:
        return verifier()
    if a.graines:
        print(json.dumps(trouver_les_graines(), ensure_ascii=False, indent=1))
        return 0
    if a.pousser:
        print(json.dumps(pousser(), ensure_ascii=False, indent=1))
        return 0
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
