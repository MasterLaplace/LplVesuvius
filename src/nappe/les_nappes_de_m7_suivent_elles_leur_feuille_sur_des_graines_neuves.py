"""Déclaré par taux et sur vingt-quatre blocs, le juge sépare-t-il, et les nappes de m7 tirées de graines neuves suivent-elles leur feuille ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LES VINGT-QUATRE BLOCS D'ÉTALONNAGE NE SOIENT LUS ET AVANT QUE LES GRAINES NEUVES NE SOIENT
CHERCHÉES. Ce qui était vu avant d'écrire : tout ce que `298` à `300` publient, dont les Z de `300` sur six blocs (le tracé humain
de 8,294 à 23,476, les rampes jusqu'à 2,224, le premier saut à 2,842 sur un bloc) et ses quatre nappes, dont deux se calent.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P100`. `300` a manqué sa règle tout-ou-rien d'une comparaison sur vingt-quatre, sur
une surface qui n'est pas un référent. Un juge n'est jamais parfait : il se déclare par ses taux, sur assez de blocs pour que
ceux-ci veuillent dire quelque chose, et contre le seul référent qu'on ait, le tracé humain. Puis il se porte sur des nappes
qu'on n'a pas vues.

## Le juge, inchangé

Celui de `300` : l'alignement d'une pièce contre huit rampes plantées dans ses propres points, Z ≥ 3.

## L'étalonnage, par taux

Sur PHercParis4 au niveau 2, vingt-quatre blocs parmi les candidats de `257`, hors des dix-huit déjà lus, de rang ⌊k(N − 1)/25⌉
pour k = 1 à 24. Le juge sépare si le tracé humain a Z ≥ 3 sur au moins 90 % des blocs, et si les deux rampes plantées dans le
tracé, jugées chacune contre ses huit rampes, ont Z ≥ 3 sur au plus 5 % de leurs quarante-huit comparaisons. Le premier saut de
la chaîne est rapporté à côté : il n'est pas un référent.

## Les graines neuves

`trouver_graine.py` sur la prédiction `m7` de PHerc0358, avec ses défauts sauf la hauteur : au quart et aux trois quarts de la
hauteur du rouleau (`--z-fraction 0.25` et `0.75`). Toutes les graines rendues, dans leur ordre, jusqu'à quatre par hauteur, en
écartant celles de `299`. Chacune donne sa nappe et ses deux spires suivantes, exactement comme `300`.

## Les issues, exclusives

- l'étalonnage ne sépare pas : **même par taux, l'alignement contre huit traversées ne sépare pas au pas du prix** ;
- sinon : **sur k des n graines neuves, la nappe tirée de m7 suit sa feuille, et sur j d'entre elles une spire suivante
  aussi** ;
- indécidable si une lecture échoue ou si aucune graine n'est rendue.

## Rapporté à côté, qui ne décide rien

Le premier saut sur les vingt-quatre blocs ; l'appui sur `m7`, les déchirures et le pas médian appuyé de chaque nappe et de
chaque spire ; la part sans matière.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : sur quelle feuille une nappe est posée, qu'elle ne passe pas d'une feuille à la voisine, que
la spire suivante soit la voisine ; ni ce que vaut une nappe de 6 mm pour un rouleau entier.

Usage :
    uv run python src/nappe/les_nappes_de_m7_suivent_elles_leur_feuille_sur_des_graines_neuves.py --verifier
    uv run python src/nappe/les_nappes_de_m7_suivent_elles_leur_feuille_sur_des_graines_neuves.py --graines
    uv run python src/nappe/les_nappes_de_m7_suivent_elles_leur_feuille_sur_des_graines_neuves.py --tirer
    uv run python src/nappe/les_nappes_de_m7_suivent_elles_leur_feuille_sur_des_graines_neuves.py --preparer
    uv run python src/nappe/les_nappes_de_m7_suivent_elles_leur_feuille_sur_des_graines_neuves.py --lire 12
    uv run python src/nappe/les_nappes_de_m7_suivent_elles_leur_feuille_sur_des_graines_neuves.py \\
        --json docs/mesures/les_nappes_de_m7_suivent_elles_leur_feuille_sur_des_graines_neuves.json
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
sys.path.insert(0, str(RACINE / "src" / "commun"))
sys.path.insert(0, str(RACINE / "src" / "tracecheck"))

import la_matiere_dit_elle_si_la_surface_est_sur_sa_feuille as m298  # noqa: E402
import lalignement_des_profils_dit_il_si_une_premiere_surface_suit_sa_feuille as m299  # noqa: E402
import une_nappe_tiree_de_m7_suit_elle_sa_feuille as m300  # noqa: E402

LE_DOSSIER = RACINE / "data" / "nappes_de_m7_neuves"
LES_SURFACES_PREPAREES = LE_DOSSIER / "surfaces"
LE_PLAN = LE_DOSSIER / "plan.json"
LES_NAPPES = LE_DOSSIER / "nappes.npz"
LES_NAPPES_JSON = LE_DOSSIER / "nappes.json"
CE_QUE_300_A_PUBLIE = RACINE / "docs" / "mesures" / "une_nappe_tiree_de_m7_suit_elle_sa_feuille.json"
LES_BLOCS = 24
LES_HAUTEURS = (0.25, 0.75)
LES_GRAINES_PAR_HAUTEUR = 4
LE_TAUX_DU_TRACE = 0.90
LE_TAUX_DES_RAMPES = 0.05


# ── Les issues ─────────────────────────────────────────────────────────────────────────────────────────────────────

def letalonnage_par_taux(blocs: list[dict]) -> dict:
    """Le juge sépare si le tracé passe Z ≥ 3 sur au moins 90 % des blocs et les rampes sur au plus 5 % des comparaisons."""
    trace = [b["le_segment"] for b in blocs]
    rampes = [b[n] for b in blocs for n in ("rampe_douce", "rampe_raide")]
    t_ok = sum(1 for z in trace if z is not None and z >= m300.LE_Z_MINIMUM)
    r_ok = sum(1 for z in rampes if z is not None and z >= m300.LE_Z_MINIMUM)
    absents = sum(1 for z in trace + rampes if z is None)
    taux_t = round(t_ok / len(trace), 4) if trace else None
    taux_r = round(r_ok / len(rampes), 4) if rampes else None
    separe = (len(blocs) == LES_BLOCS and absents == 0 and taux_t is not None and taux_t >= LE_TAUX_DU_TRACE
              and taux_r is not None and taux_r <= LE_TAUX_DES_RAMPES)
    return {"separe": separe, "le_taux_du_trace": taux_t, "le_taux_des_rampes": taux_r, "les_absents": absents,
            "les_blocs": len(blocs)}


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d["letalonnage"]["le_verdict"]["separe"]:
        return {"decidable": True, "separe": False,
                "lissue": "même par taux, l'alignement contre huit traversées ne sépare pas au pas du prix"}
    graines = d["le_rouleau"]["les_graines"]
    if not graines:
        return {"decidable": False, "separe": True, "lissue": "indécidable : aucune graine n'est rendue"}
    k = sum(1 for g in graines if g["la_nappe"] == "suit sa feuille")
    j = sum(1 for g in graines if g["la_nappe"] == "suit sa feuille"
            and any(g["les_sauts"][c] == "suit sa feuille" for c in ("plus", "moins")))
    return {"decidable": True, "separe": True, "k": k, "j": j, "n": len(graines),
            "lissue": f"sur {k} des {len(graines)} graines neuves, la nappe tirée de m7 suit sa feuille, et sur {j} d'entre "
                      "elles une spire suivante aussi"}


# ── Les étapes ─────────────────────────────────────────────────────────────────────────────────────────────────────

def chercher_les_graines() -> dict:
    LE_DOSSIER.mkdir(parents=True, exist_ok=True)
    out = {}
    for h in LES_HAUTEURS:
        f = LE_DOSSIER / f"graines_{h:g}.json"
        cmd = [sys.executable, str(RACINE / "src" / "commun" / "trouver_graine.py"), m299.LA_PREDICTION_0358, "--level", "2",
               "--chunks", "24", "--candidats", "8", "--voxel-um", "9.362", "--z-fraction", str(h), "--out", str(f)]
        p = subprocess.run(cmd, capture_output=True, text=True, cwd=RACINE)
        out[str(h)] = {"le_code": p.returncode, "la_sortie": p.stdout[-3000:], "les_erreurs": p.stderr[-1000:]}
    return out


def les_graines_neuves() -> list[dict]:
    """Jusqu'à quatre graines par hauteur, dans leur ordre, sans celles de `299`."""
    vues = {(g["x"], g["y"], g["z"]) for g in json.loads(m299.LES_GRAINES.read_text())["candidats"]}
    out = []
    for h in LES_HAUTEURS:
        f = LE_DOSSIER / f"graines_{h:g}.json"
        if not f.exists():
            continue
        prises = 0
        for g in json.loads(f.read_text())["candidats"]:
            if (g["x"], g["y"], g["z"]) in vues:
                continue
            out.append(dict(g, la_hauteur=h))
            prises += 1
            if prises == LES_GRAINES_PAR_HAUTEUR:
                break
    return out


def tirer() -> dict:
    from le_transfert_retrouve_t_il_la_spire_voisine import lecteur_du_depot

    from zarr_depth import array_meta

    graines = les_graines_neuves()
    url = f"{m298.BUCKET}/{m299.LA_PREDICTION_0358}"
    pred = array_meta(url, 0, 120.0)
    lire_, stats = lecteur_du_depot(pred, m300.LE_CACHE_M7, "m7_L0", m299.LA_PREDICTION_0358, 0)
    tableaux, resume = {}, []
    for rang, g in enumerate(graines, 1):
        t0 = time.monotonic()
        nz, ny, nx = g["normale_zyx"]
        r = m300.tirer_une_nappe((g["x"], g["y"], g["z"]), (nx, ny, nz), (pred, lire_))
        tableaux[f"g{rang}_nappe"], tableaux[f"g{rang}_nappe_ok"] = r["la_nappe"], r["valide"]
        e = {"le_rang": rang, "la_hauteur": g["la_hauteur"], "la_graine": [g["x"], g["y"], g["z"]],
             "la_part_appuyee": round(float(r["appui"].mean()), 4),
             "les_dechirures": m300.les_dechirures(r["le_decalage"], r["valide"], m300.LE_PAS_0358 / 2.0), "les_sauts": {}}
        for c, s in r["les_sauts"].items():
            tableaux[f"g{rang}_{c}"], tableaux[f"g{rang}_{c}_ok"] = s["la_spire"], s["valide"]
            pas_ = s["le_pas"][s["valide"] & s["appui"]]
            e["les_sauts"][c] = {"la_part_appuyee": round(float(s["appui"].mean()), 4),
                                 "le_pas_median_des_appuyes_voxels": round(float(np.median(np.abs(pas_))), 2)
                                 if len(pas_) else None,
                                 "les_dechirures": m300.les_dechirures(s["le_pas"], s["valide"], m300.LE_PAS_0358 / 2.0)}
        e["les_secondes"] = round(time.monotonic() - t0, 1)
        resume.append(e)
        print(json.dumps(e, ensure_ascii=False), flush=True)
    LE_DOSSIER.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(LES_NAPPES, **tableaux)
    d = {"les_nappes": resume, "la_lecture_de_m7": {k: (v if k != "pannes" else v[:20]) for k, v in stats.items()}}
    LES_NAPPES_JSON.write_text(json.dumps(d, ensure_ascii=False, indent=1))
    return d


def les_surfaces_de_paris4() -> tuple[dict, list]:
    import le_tour_produit_porte_t_il_le_texte_du_segment as j296
    from la_procedure_sans_juge_tient_elle_sur_le_segment_entier import le_segment
    from la_spire_voisine_est_elle_a_un_pas import LE_CACHE, les_normales, lire_tifxyz
    from que_montrent_ces_deux_vues import DEMI_PAS_EN_VOXELS, PAS_EN_VOXELS

    k = m298.LE_SURECHANTILLONNAGE["PHercParis4"]
    deja = (json.loads(j296.LE_PLAN.read_text())["les_blocs_de_la_partie_b"]
            + json.loads(m300.CE_QUE_299_A_PUBLIE.read_text())["letalonnage"]["les_blocs"]
            + json.loads(CE_QUE_300_A_PUBLIE.read_text())["letalonnage"]["les_blocs"])
    deja = [b["le_bloc"] if isinstance(b, dict) else b for b in deja]
    _, _, _, candidats = le_segment(LE_CACHE)
    blocs = m299.les_blocs_neufs(sorted(candidats), deja, combien=LES_BLOCS)
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
            fam = m300.la_famille(n, sp, sok, nn, nok, float(PAS_EN_VOXELS), esp / k)
            if n == "le_segment":
                for dn, (dp, dok) in m298.les_defauts(sp, sok, nn, nok, float(DEMI_PAS_EN_VOXELS), float(PAS_EN_VOXELS),
                                                      esp / k).items():
                    if dn in m298.LES_PENTES:
                        rn, rok = les_normales(dp, dok)
                        fam.update(m300.la_famille(dn, dp, dok, rn, rok, float(PAS_EN_VOXELS), esp / k))
            for nom, (p, m, nr) in fam.items():
                out.setdefault(nom, []).append({"le_bloc": list(b), "points": p[m], "normales": nr[m]})
    return out, [list(b) for b in blocs]


def les_surfaces_de_0358() -> dict:
    from la_spire_voisine_est_elle_a_un_pas import les_normales

    z = np.load(LES_NAPPES)
    out: dict = {}
    rangs = sorted({int(k[1:].split("_")[0]) for k in z.files})
    for r in rangs:
        for s in ("nappe", "plus", "moins"):
            pts, ok = z[f"g{r}_{s}"], z[f"g{r}_{s}_ok"]
            nn, nok = les_normales(pts, ok)
            for nom, (p, m, nr) in m300.la_famille(f"g{r}_{s}", pts, ok, nn, nok, m300.LE_PAS_0358,
                                                   m300.LE_PAS_DU_PLAN).items():
                out[nom] = [{"la_piece": [r, s], "points": p[m], "normales": nr[m]}]
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
        plan["les_morceaux"][volume] = {"combien": len(cles), "les_octets": int(len(cles) * np.prod(vol.taille))}
    plan["les_secondes"] = round(time.monotonic() - t0, 1)
    LE_PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=1))
    return plan


def lire(ouvriers: int = 8) -> dict:
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
    (LE_DOSSIER / "lire.json").write_text(json.dumps(out, indent=1))
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
    blocs = []
    for i, b in enumerate(plan["les_blocs"]):
        ligne = {"le_bloc": b, "lalignement": {}}
        for nom in ("le_segment", "saut_1", "rampe_douce", "rampe_raide"):
            base = f"PHercParis4__{nom}"
            a = res[base][i]["lalignement"]
            tem = [res[f"{base}__{r}_{ph:g}"][i]["lalignement"] for r in m298.LES_PENTES for ph in m300.LES_PHASES]
            ligne[nom] = m300.le_z(a, tem)
            ligne["lalignement"][nom] = a
        blocs.append(ligne)
    sauts1 = [b["saut_1"] for b in blocs]
    e = {"les_blocs": blocs, "le_verdict": letalonnage_par_taux(blocs),
         "le_premier_saut_rapporte": {"au_moins_3": sum(1 for z in sauts1 if z is not None and z >= m300.LE_Z_MINIMUM),
                                      "sur": len(sauts1)}}
    nappes = json.loads(LES_NAPPES_JSON.read_text())
    graines = []
    for g in nappes["les_nappes"]:
        r = g["le_rang"]
        e_ = {"le_rang": r, "la_hauteur": g["la_hauteur"], "la_graine": g["la_graine"],
              "la_part_appuyee": g["la_part_appuyee"], "les_dechirures": g["les_dechirures"], "les_sauts": {},
              "le_detail": {}}
        for s in ("nappe", "plus", "moins"):
            cle = f"PHerc0358__g{r}_{s}"
            a = res[cle][0]
            tem = [res[f"{cle}__{rr}_{ph:g}"][0]["lalignement"] for rr in m298.LES_PENTES for ph in m300.LES_PHASES]
            z = m300.le_z(a["lalignement"], tem)
            e_["le_detail"][s] = {"le_z": z, "lalignement": a["lalignement"],
                                  "la_moyenne_des_temoins": round(float(np.mean([x for x in tem if x is not None])), 3)
                                  if any(x is not None for x in tem) else None,
                                  "les_points_juges": a["les_points_juges"], "sans_matiere": a["sans_matiere"],
                                  "la_piece": m300.la_piece(z, a["les_points_juges"])}
        e_["la_nappe"] = e_["le_detail"]["nappe"]["la_piece"]
        for c in ("plus", "moins"):
            e_["les_sauts"][c] = e_["le_detail"][c]["la_piece"]
            e_["le_detail"][c].update(g["les_sauts"][c])
        graines.append(e_)
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"les_blocs": LES_BLOCS, "les_hauteurs": LES_HAUTEURS,
                            "les_graines_par_hauteur": LES_GRAINES_PAR_HAUTEUR, "le_taux_du_trace": LE_TAUX_DU_TRACE,
                            "le_taux_des_rampes": LE_TAUX_DES_RAMPES, "le_z_minimum": m300.LE_Z_MINIMUM},
         "letalonnage": e, "le_rouleau": {"les_graines": graines}, "la_lecture_de_m7": nappes["la_lecture_de_m7"],
         "les_morceaux": plan["les_morceaux"], "les_pannes": list(nappes["la_lecture_de_m7"].get("pannes", []))}
    d["le_verdict"] = le_verdict(d)
    d["les_secondes"] = round(time.monotonic() - t0, 1)
    return d


# ── La batterie ────────────────────────────────────────────────────────────────────────────────────────────────────

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

    bon = {"le_segment": 9.0, "saut_1": 1.0, "rampe_douce": 0.5, "rampe_raide": -0.5}
    blocs = [dict(bon, le_bloc=[i, i]) for i in range(24)]
    v("★★★★ par taux : un tracé qui passe partout et des rampes qui ne passent jamais séparent, même si le premier saut rate",
      letalonnage_par_taux(blocs)["separe"])
    b2 = [dict(b) for b in blocs]
    for b in b2[:2]:
        b["le_segment"] = 2.0
    v("★★★★ par taux : deux blocs sur vingt-quatre sous 3 pour le tracé, c'est encore 91,7 %", letalonnage_par_taux(b2)["separe"]
      and letalonnage_par_taux(b2)["le_taux_du_trace"] == round(22 / 24, 4))
    b3 = [dict(b) for b in blocs]
    for b in b3[:3]:
        b["le_segment"] = 2.0
    v("★★★★ par taux : trois blocs sous 3 pour le tracé, 87,5 %, ne séparent pas", not letalonnage_par_taux(b3)["separe"])
    b4 = [dict(b) for b in blocs]
    b4[0]["rampe_douce"], b4[1]["rampe_raide"] = 3.5, 4.0
    v("★★★★ par taux : deux rampes sur quarante-huit à 3 ou plus, 4,2 %, séparent encore", letalonnage_par_taux(b4)["separe"])
    b5 = [dict(b) for b in b4]
    b5[2]["rampe_douce"] = 3.0
    v("★★★★ par taux : trois rampes sur quarante-huit, 6,25 %, ne séparent pas", not letalonnage_par_taux(b5)["separe"])
    b7 = [dict(b) for b in blocs]
    for b in b7[:3]:
        b["rampe_raide"] = 5.0
    v("★★★★ par taux : les deux rampes comptent, trois rampes à 45° au-dessus de 3 ne séparent pas",
      not letalonnage_par_taux(b7)["separe"] and letalonnage_par_taux(b7)["le_taux_des_rampes"] == round(3 / 48, 4))
    v("★★★ par taux : moins de vingt-quatre blocs, ou un Z absent, ne séparent pas",
      not letalonnage_par_taux(blocs[:23])["separe"]
      and not letalonnage_par_taux([dict(blocs[0], le_segment=None)] + blocs[1:])["separe"])
    base = {"letalonnage": {"le_verdict": {"separe": True}}, "le_rouleau": {"les_graines": [
        {"la_nappe": "suit sa feuille", "les_sauts": {"plus": "suit sa feuille", "moins": "ne la suit pas"}},
        {"la_nappe": "ne la suit pas", "les_sauts": {"plus": "suit sa feuille", "moins": "suit sa feuille"}}]}}
    vd = le_verdict(base)
    v("★★★★ l'issue : k nappes qui suivent sur n graines, j avec une spire suivante",
      vd["k"] == 1 and vd["j"] == 1 and vd["n"] == 2 and vd["lissue"].startswith("sur 1 des 2 graines neuves"), str(vd))
    v("★★★ l'issue : indécidable sans graine", not le_verdict({"letalonnage": {"le_verdict": {"separe": True}},
                                                               "le_rouleau": {"les_graines": []}})["decidable"])
    b6 = json.loads(json.dumps(base))
    b6["letalonnage"]["le_verdict"]["separe"] = False
    v("★★★★ l'issue : un étalonnage qui ne sépare pas ne juge rien", le_verdict(b6)["separe"] is False)
    import tempfile
    vieux_dossier = LE_DOSSIER
    tmp = Path(tempfile.mkdtemp())
    try:
        globals()["LE_DOSSIER"] = tmp
        (tmp / "graines_0.25.json").write_text(json.dumps({"candidats": [
            {"x": 1, "y": 1, "z": 1}, {"x": 2, "y": 2, "z": 2}, {"x": 3, "y": 3, "z": 3}, {"x": 4, "y": 4, "z": 4},
            {"x": 5, "y": 5, "z": 5}]}))
        (tmp / "graines_0.75.json").write_text(json.dumps({"candidats": [{"x": 4936, "y": 2576, "z": 7852},
                                                                          {"x": 9, "y": 9, "z": 9}]}))
        gn = les_graines_neuves()
    finally:
        globals()["LE_DOSSIER"] = vieux_dossier
    v("★★★ les graines neuves : quatre au plus par hauteur, dans l'ordre, sans celles de 299",
      [g["x"] for g in gn] == [1, 2, 3, 4, 9] and gn[-1]["la_hauteur"] == 0.75, str([g["x"] for g in gn]))

    for e in echecs:
        print(f"  ÉCHEC {e}")
    print(f"{Path(__file__).name}   {'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--graines", action="store_true")
    p.add_argument("--tirer", action="store_true")
    p.add_argument("--preparer", action="store_true")
    p.add_argument("--lire", type=int, default=None, metavar="OUVRIERS")
    p.add_argument("--json", type=Path, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if a.graines:
        print(json.dumps(chercher_les_graines(), ensure_ascii=False, indent=1))
        return 0
    if a.tirer:
        print(json.dumps(tirer(), ensure_ascii=False, indent=1))
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
