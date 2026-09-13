#!/usr/bin/env python3
"""Ou la matiere cesse-t-elle de se lire ? — ce qu'il y a a l'endroit ou une marche s'arrete.

⭐⭐⭐⭐ POURQUOI CE FICHIER EXISTE. `131` a mesure que ce qui arrete onze marches sur seize n'est
pas le plafond mais « plus rien a lire », et l'a lu comme *le volume qui cesse de repondre*
(`R4-F62`) ; `133` a mesure que le cap y arrive plus tot encore (quatorze sur seize), et a deplace la
question du graal vers « pourquoi la matiere cesse de se lire ». Personne n'etait alle REGARDER
l'endroit de l'arret. Or `rien_lu` a une definition exacte : le cube de lecture est CONSTANT, donc
entierement au remplissage du volume masque — et un volume masque est au remplissage la ou il n'y a
pas de rouleau.

⭐⭐⭐ LA QUESTION EST DONC GEOMETRIQUE, ET ELLE SE MESURE : l'arret est-il A LA SURFACE EXTERIEURE
du rouleau — c'est-a-dire la marche a-t-elle traverse tout ce qu'il y avait a traverser — ou dans
un vide interieur, avec de la matiere plus loin ? Deux mesures repondent, et elles ne partagent
aucune hypothese : (1) y a-t-il de la matiere AU-DELA de l'arret, le long de la derniere
direction, sur seize pas ; (2) a quel rayon est la surface exterieure sur le rayon meme de l'arret,
lue en lancant un rayon depuis l'axe de la bande a travers le point d'arret jusqu'au bord du champ.

⚠⚠ CE QUE CA CHANGE SI LA REPONSE EST « LA SURFACE » : une marche arretee par « plus rien a lire »
n'a pas ete arretee, elle est ARRIVEE. La portee mesuree par `130`, `131` et `133` serait alors
celle d'un marcheur qui traverse le rouleau de part en part, et le taux de confirmation le long de
cette traversee serait la seule chose qui reste a juger.

⚠ L'axe de la bande est celui que `107` a pose : le depart moins le radial fois le rayon. C'est un
POINT par bande, pas la courbe de `90` — assez pour un rayon a un pas pres, pas pour une carte.

Usage :
    uv run python src/nappe/ou_la_matiere_cesse_de_se_lire.py --verifier
    uv run python src/nappe/ou_la_matiere_cesse_de_se_lire.py \\
        --json docs/mesures/ou_la_matiere_cesse_de_se_lire.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))

COURSES = (RACINE / "docs" / "mesures" / "la_course_a_cap.json",
           RACINE / "docs" / "mesures" / "la_re_course_large.json")
PAS_AU_DELA = 16
ECHANTILLON_UM = 50.0
DEMI_SONDE = 2


def arrets(course: dict, trace: list[dict] | None, voxel_um: float, pas_um: float) -> list[dict]:
    """Chaque marche de la course : ou elle s'est arretee, dans quelle direction, a quel rayon.

    ⚠ La position vient de la TRACE quand elle existe (positions exactes de `marcher`), sinon elle
    est reconstruite depuis les etapes — a l'arrondi pres de `avance_um` et `direction`, que
    `le_marcheur_derive_t_il` borne a quelques micrometres sur cent pas : assez pour poser un cube.
    """
    derniers = {}
    if trace:
        for l in trace:
            if l.get("quoi") == "pas":
                derniers[int(l["marche"])] = np.asarray(l["position_zyx"], dtype=float)
    out, i = [], 0
    for ligne in course.get("lignes", []):
        for cel in ligne.get("detail", []):
            m = i
            i += 1
            etapes = [e for e in cel.get("etapes", []) if "avance_um" in e]
            if not etapes:
                continue
            dep = np.asarray(cel["depart_zyx"], dtype=float)
            rad = np.asarray(cel["radial_zyx"], dtype=float)
            r0 = float(ligne.get("rayon_mm"))
            axe = dep - rad * (r0 * 1000.0 / voxel_um)
            if m in derniers:
                p = derniers[m]
            else:
                p = dep.copy()
                for e in etapes:
                    p = p + np.asarray(e["direction"], dtype=float) * (float(e["avance_um"]) / voxel_um)
            fin = ("sortie du volume" if cel.get("sortie") else
                   "plus rien a lire" if cel.get("plus_rien_a_lire") else
                   "plafond" if cel.get("au_plafond") else "arret")
            out.append({"marche": m, "bande": [int(ligne["de"]), int(ligne["a"])], "rayon_mm": r0,
                        "fin": fin, "pas": len(etapes), "axe_zyx": [float(x) for x in axe],
                        "position_zyx": [float(x) for x in p],
                        "direction": [float(x) for x in etapes[-1]["direction"]],
                        "rayon_arret_mm": round(float(np.linalg.norm(p - axe)) * voxel_um / 1000.0, 2)})
    return out


def au_dela(lecteur, position, direction, pas_um: float, voxel_um: float, demi: int = 20,
            pas_max: int = PAS_AU_DELA, fils: int = 64) -> dict:
    """Y a-t-il de la matiere AU-DELA de l'arret, le long de la derniere direction ?

    ⚠ Un cube par pas, jusqu'a seize pas (2,8 mm) : la part de voxels au remplissage est publiee
    a chaque pas, et « la matiere reprend » est le premier cube qui n'est pas entierement au
    remplissage. Un vide interieur d'un rouleau fait quelques centaines de micrometres ; seize pas
    de remplissage ne sont plus un vide, c'est l'exterieur.
    """
    from la_direction_que_la_matiere_montre import bloc  # noqa: PLC0415

    p = np.asarray(position, dtype=float)
    d = np.asarray(direction, dtype=float)
    d = d / max(float(np.linalg.norm(d)), 1e-12)
    parts, reprise = [], None
    for k in range(0, pas_max + 1):
        q = p + d * (k * pas_um / voxel_um)
        pts = bloc(q, demi)
        if not lecteur.dans_le_volume(pts).all():
            parts.append(None)
            continue
        v = lecteur.lire(pts, fils=fils)
        part = float(np.mean(v == lecteur.remplissage))
        parts.append(round(part, 3))
        if k > 0 and reprise is None and part < 1.0:
            reprise = k
    return {"part_au_remplissage_par_pas": parts, "la_matiere_reprend_au_pas": reprise,
            "rien_sur_seize_pas": bool(reprise is None and all(x == 1.0 for x in parts if x is not None))}


def rayon_exterieur(lecteur, axe, position, voxel_um: float, jusqua_mm: float = 45.0,
                    echantillon_um: float = ECHANTILLON_UM, demi_sonde: int = DEMI_SONDE,
                    fils: int = 64) -> dict:
    """La surface exterieure du rouleau sur le rayon meme de l'arret.

    Un rayon est lance depuis l'axe de la bande a travers le point d'arret, echantillonne tous les
    `echantillon_um` par une petite sonde cubique ; la surface exterieure est le DERNIER echantillon
    qui porte de la matiere avant le bord du champ ou `jusqua_mm`. ⚠ « Dernier » et non « premier
    vide » : un vide interieur ne doit pas passer pour la surface, et le remplissage exterieur, lui,
    persiste jusqu'au bord.
    """
    from la_direction_que_la_matiere_montre import bloc  # noqa: PLC0415

    a = np.asarray(axe, dtype=float)
    p = np.asarray(position, dtype=float)
    u = p - a
    u = u / max(float(np.linalg.norm(u)), 1e-12)
    rayons_um = np.arange(echantillon_um, jusqua_mm * 1000.0 + echantillon_um, echantillon_um)
    pts, garde = [], []
    for r in rayons_um:
        q = a + u * (r / voxel_um)
        b = bloc(q, demi_sonde)
        if not lecteur.dans_le_volume(b).all():
            break
        pts.append(b)
        garde.append(r)
    if not pts:
        return {"decidable": False, "pourquoi": "le rayon sort du champ des le premier echantillon"}
    v = lecteur.lire(np.concatenate(pts), fils=fils)
    n = (2 * demi_sonde + 1) ** 3
    matiere = np.array([np.any(v[i * n:(i + 1) * n] != lecteur.remplissage) for i in range(len(pts))])
    if not matiere.any():
        return {"decidable": False, "pourquoi": "aucune matiere sur le rayon"}
    dernier = int(np.max(np.nonzero(matiere)[0]))
    # ⚠ Un dernier echantillon AU BORD du champ n'est pas une surface : c'est le scan qui finit.
    borne = bool(dernier >= len(pts) - 1)
    return {"decidable": True, "rayon_exterieur_mm": round(float(garde[dernier]) / 1000.0, 2),
            "echantillons": len(pts), "echantillon_um": echantillon_um,
            "coupe_par_le_bord_du_champ": borne}


def juger(arret: dict, dela: dict, ext: dict, pas_um: float) -> dict:
    """L'arret est-il a la surface exterieure, dans un vide, ou ailleurs ?

    ⚠ La tolerance est UN PAS (`pas_um`) : un marcheur qui s'arrete a moins d'un pas de la surface
    mesuree sur son propre rayon s'est arrete PARCE QU'il n'y avait plus de rouleau devant lui. Ce
    n'est pas un seuil regle — c'est la resolution de la marche elle-meme.
    """
    if not ext.get("decidable"):
        return {"decidable": False, "pourquoi": ext.get("pourquoi")}
    ecart = round(arret["rayon_arret_mm"] - ext["rayon_exterieur_mm"], 2)
    a_la_surface = bool(abs(ecart) <= pas_um / 1000.0 and dela["rien_sur_seize_pas"])
    au_dela_de_la_surface = bool(ecart > pas_um / 1000.0 and dela["rien_sur_seize_pas"])
    return {"decidable": True, "ecart_a_la_surface_mm": ecart,
            "a_la_surface": a_la_surface, "au_dela_de_la_surface": au_dela_de_la_surface,
            "dans_un_vide_interieur": bool(dela["la_matiere_reprend_au_pas"] is not None),
            "sorti_du_rouleau": bool(a_la_surface or au_dela_de_la_surface)}


def mesurer(courses=COURSES, demi: int = 20, fils: int = 64) -> dict:
    import combien_dinterstices_traverses as C  # noqa: PLC0415
    from la_normale_nest_pas_le_rayon import avancement, maintenant  # noqa: PLC0415
    from voxel_distant import BUCKET, VolumeZarr  # noqa: PLC0415

    try:
        vol = VolumeZarr(f"{BUCKET}/{C.ZARR_FIN}")
    except RuntimeError as e:
        return {"message": f"volume fin injoignable : {e}"}
    t0 = maintenant()
    out = {"fragment": C.OBJET, "volume_fin": C.VOLUME_FIN, "remplissage": vol.remplissage,
           "pas_um": C.PAS_UM, "pas_au_dela": PAS_AU_DELA, "par_course": []}
    for cp in courses:
        cp = Path(cp)
        if not cp.is_file():
            continue
        course = json.loads(cp.read_text(encoding="utf-8"))
        tp = cp.with_suffix(".jsonl")
        trace = ([json.loads(l) for l in tp.read_text(encoding="utf-8").splitlines() if l.strip()]
                 if tp.is_file() else None)
        lignes = []
        liste = arrets(course, trace, C.VOXEL_FIN_UM, C.PAS_UM)
        for i, a in enumerate(liste):
            dela = au_dela(vol, a["position_zyx"], a["direction"], C.PAS_UM, C.VOXEL_FIN_UM, demi,
                           fils=fils)
            ext = rayon_exterieur(vol, a["axe_zyx"], a["position_zyx"], C.VOXEL_FIN_UM, fils=fils)
            lignes.append({**a, "au_dela": dela, "surface": ext, "verdict": juger(a, dela, ext, C.PAS_UM)})
            avancement(i + 1, len(liste), f"arrets de {cp.name}", t0)
        rien = [x for x in lignes if x["fin"] == "plus rien a lire"]
        dec = [x for x in rien if x["verdict"].get("decidable")]
        out["par_course"].append({
            "source": cp.name, "memoire_du_cap": course.get("memoire_du_cap", 0.0),
            "trace_utilisee": trace is not None, "marches": len(lignes), "arrets": lignes,
            "resume": {
                "plus_rien_a_lire": len(rien), "decidables": len(dec),
                "sortis_du_rouleau": sum(1 for x in dec if x["verdict"]["sorti_du_rouleau"]),
                "a_la_surface": sum(1 for x in dec if x["verdict"]["a_la_surface"]),
                "au_dela_de_la_surface": sum(1 for x in dec if x["verdict"]["au_dela_de_la_surface"]),
                "dans_un_vide_interieur": sum(1 for x in dec if x["verdict"]["dans_un_vide_interieur"]),
                "rien_sur_seize_pas": sum(1 for x in rien if x["au_dela"]["rien_sur_seize_pas"]),
                "ecart_a_la_surface_median_mm": (round(float(np.median(
                    [x["verdict"]["ecart_a_la_surface_mm"] for x in dec])), 2) if dec else None),
                "rayon_exterieur_median_mm": (round(float(np.median(
                    [x["surface"]["rayon_exterieur_mm"] for x in dec])), 2) if dec else None),
                "rayon_arret_median_mm": (round(float(np.median(
                    [x["rayon_arret_mm"] for x in rien])), 2) if rien else None)}})
    out["secondes"] = round(maintenant() - t0, 1)
    return out


def afficher(r: dict) -> None:
    if "message" in r:
        print(f"⚠ {r['message']}")
        return
    for c in r["par_course"]:
        s = c["resume"]
        print(f"\n{c['source']} (λ = {c['memoire_du_cap']}) · {c['marches']} marches · "
              f"{s['plus_rien_a_lire']} arrêts « plus rien à lire »")
        for x in c["arrets"]:
            v, e = x["verdict"], x["surface"]
            print(f"   r0 {x['rayon_mm']:>5.2f} → arrêt {x['rayon_arret_mm']:>5.2f} mm après {x['pas']:>3} pas · "
                  f"{x['fin']:<16} · surface {e.get('rayon_exterieur_mm', '?'):>5} mm · écart "
                  f"{v.get('ecart_a_la_surface_mm', '?'):>5} · matière au-delà : "
                  f"{'non sur 16 pas' if x['au_dela']['rien_sur_seize_pas'] else 'reprend au pas ' + str(x['au_dela']['la_matiere_reprend_au_pas'])}"
                  + (" · ★ SORTI DU ROULEAU" if v.get("sorti_du_rouleau") else ""))
        print(f"   ★★★ {s['sortis_du_rouleau']}/{s['decidables']} arrêts sortis du rouleau "
              f"({s['a_la_surface']} à la surface, {s['au_dela_de_la_surface']} au-delà) · "
              f"{s['dans_un_vide_interieur']} dans un vide intérieur · rayon extérieur médian "
              f"{s['rayon_exterieur_median_mm']} mm · écart médian {s['ecart_a_la_surface_median_mm']} mm")
    print(f"\n{r['secondes']} s")


class _Rouleau:
    """Un rouleau fabrique : de la matiere jusqu'au rayon R autour d'un axe, remplissage au-dela,
    avec en option une coquille de vide entre deux rayons — pour que la batterie ait une reponse."""

    def __init__(self, axe, R_mm, voxel_um=2.4, vide_mm=None, forme=(6000, 6000, 6000)):
        self.axe = np.asarray(axe, dtype=float)
        self.R = R_mm * 1000.0 / voxel_um
        self.vide = None if vide_mm is None else tuple(v * 1000.0 / voxel_um for v in vide_mm)
        self.forme = forme
        self.remplissage = 0

    def dans_le_volume(self, p):
        p = np.asarray(p).reshape(-1, 3)
        return np.all((p >= 0) & (p < np.asarray(self.forme)), axis=1)

    def lire(self, pts, fils=1):
        q = np.asarray(pts, dtype=float).reshape(-1, 3)
        r = np.linalg.norm(q - self.axe, axis=1)
        v = np.where(r <= self.R, 120.0, 0.0)
        if self.vide is not None:
            v = np.where((r > self.vide[0]) & (r < self.vide[1]), 0.0, v)
        return v


def verifier() -> int:
    echecs = controles = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    vox, pas = 2.4, 173.0
    axe = np.array([3000.0, 3000.0, 3000.0])
    rou = _Rouleau(axe, R_mm=6.0, voxel_um=vox)
    u = np.array([0.0, 0.0, 1.0])
    # un arret POSE a la surface : le cube y est entierement au remplissage ? Non — a la surface
    # meme le cube est a moitie plein ; l'arret d'un marcheur est un pas AU-DELA, la ou le cube
    # est vide. On pose l'arret a 6,1 mm, un cube au-dela de la surface.
    p_surface = axe + u * (6.1 * 1000.0 / vox)
    ext = rayon_exterieur(rou, axe, p_surface, vox)
    v("la surface exterieure est retrouvee a un echantillon pres", ext["decidable"]
      and abs(ext["rayon_exterieur_mm"] - 6.0) <= ECHANTILLON_UM / 1000.0 + 1e-9,
      f"{ext.get('rayon_exterieur_mm')} mm pour 6,0")
    v("... et elle n'est pas coupee par le bord du champ", not ext["coupe_par_le_bord_du_champ"])
    dela = au_dela(rou, p_surface, u, pas, vox)
    v("au-dela de la surface il n'y a rien sur seize pas", dela["rien_sur_seize_pas"])
    a = {"rayon_arret_mm": 6.1}
    j = juger(a, dela, ext, pas)
    v("un arret a un pas de la surface est SORTI DU ROULEAU", j["sorti_du_rouleau"] and j["a_la_surface"],
      f"ecart {j['ecart_a_la_surface_mm']} mm")
    # un arret dans un VIDE INTERIEUR : coquille vide de 3,0 a 3,4 mm, matiere jusqu'a 6
    creux = _Rouleau(axe, R_mm=6.0, voxel_um=vox, vide_mm=(3.0, 3.4))
    p_vide = axe + u * (3.2 * 1000.0 / vox)
    dela2 = au_dela(creux, p_vide, u, pas, vox)
    v("dans un vide interieur la matiere REPREND", dela2["la_matiere_reprend_au_pas"] is not None
      and not dela2["rien_sur_seize_pas"], f"reprend au pas {dela2['la_matiere_reprend_au_pas']}")
    ext2 = rayon_exterieur(creux, axe, p_vide, vox)
    v("... et la surface exterieure reste celle du rouleau, pas celle du vide",
      abs(ext2["rayon_exterieur_mm"] - 6.0) <= ECHANTILLON_UM / 1000.0 + 1e-9,
      f"{ext2['rayon_exterieur_mm']} mm")
    j2 = juger({"rayon_arret_mm": 3.2}, dela2, ext2, pas)
    v("... donc l'arret est juge DANS UN VIDE, pas sorti", j2["dans_un_vide_interieur"]
      and not j2["sorti_du_rouleau"], f"ecart {j2['ecart_a_la_surface_mm']} mm")
    # sonde : un rouleau qui remplit tout le champ n'a pas de surface — c'est le bord qui coupe
    plein = _Rouleau(axe, R_mm=50.0, voxel_um=vox)
    ext3 = rayon_exterieur(plein, axe, p_surface, vox)
    v("sonde : une matiere qui va jusqu'au bord du champ est dite COUPEE par le bord",
      ext3["decidable"] and ext3["coupe_par_le_bord_du_champ"])
    # sonde : aucune matiere sur le rayon → indecidable, jamais une surface a zero
    ext4 = rayon_exterieur(_Rouleau(axe, R_mm=0.001, voxel_um=vox), axe, p_surface, vox)
    v("sonde : un rayon sans matiere est indecidable", not ext4["decidable"])
    # les arrets d'une course fabriquee : position depuis la trace, sinon reconstruite
    course = {"lignes": [{"de": 1, "a": 2, "rayon_mm": 4.0, "detail": [{
        "depart_zyx": [100.0, 100.0, 100.0], "radial_zyx": [0.0, 0.0, 1.0],
        "etapes": [{"direction": [0.0, 0.0, 1.0], "avance_um": 240.0} for _ in range(3)],
        "plus_rien_a_lire": True, "sortie": False, "au_plafond": False}]}]}
    sans = arrets(course, None, vox, pas)
    v("sans trace, la position est reconstruite depuis les etapes",
      np.allclose(sans[0]["position_zyx"], [100.0, 100.0, 400.0]) and sans[0]["fin"] == "plus rien a lire")
    v("... et le rayon d'arret vaut le rayon initial plus le chemin",
      abs(sans[0]["rayon_arret_mm"] - (4.0 + 0.72)) < 0.01, f"{sans[0]['rayon_arret_mm']}")
    avec = arrets(course, [{"quoi": "pas", "marche": 0, "position_zyx": [100.0, 100.0, 401.0]}], vox, pas)
    v("avec trace, la position est celle de la trace", avec[0]["position_zyx"][2] == 401.0)

    # ⚠ Le chemin qui produit le nombre publié est ATTEINT, sur le VOLUME FABRIQUÉ : `mesurer`
    # lit le réseau, donc il n'est pas appelé ici — mais l'assemblage qu'il fait, lui, l'est, sur
    # un rouleau dont la surface est connue. Une batterie qui teste les briques sans jamais les
    # assembler ne peut pas échouer là où ça compte.
    import contextlib, io  # noqa: PLC0415
    course_f = {"memoire_du_cap": 0.75, "lignes": [{"de": 1, "a": 2, "rayon_mm": 3.0, "detail": [{
        "depart_zyx": list(axe + u * (3.0 * 1000.0 / vox)), "radial_zyx": [0.0, 0.0, 1.0],
        "etapes": [{"direction": [0.0, 0.0, 1.0], "avance_um": pas} for _ in range(18)],
        "plus_rien_a_lire": True, "sortie": False, "au_plafond": False}]}]}
    liste = arrets(course_f, None, vox, pas)
    a0 = liste[0]
    dela0 = au_dela(rou, a0["position_zyx"], a0["direction"], pas, vox)
    ext0 = rayon_exterieur(rou, a0["axe_zyx"], a0["position_zyx"], vox)
    j0 = juger(a0, dela0, ext0, pas)
    v("l'assemblage juge une marche qui a traversé un rouleau fabriqué",
      j0["decidable"] and j0["sorti_du_rouleau"],
      f"arrêt {a0['rayon_arret_mm']} mm, surface {ext0.get('rayon_exterieur_mm')} mm")
    faux = {"fragment": "F", "pas_um": pas, "pas_au_dela": PAS_AU_DELA, "secondes": 1.0,
            "par_course": [{"source": "f.json", "memoire_du_cap": 0.75, "trace_utilisee": False,
                            "marches": 1, "arrets": [{**a0, "au_dela": dela0, "surface": ext0,
                                                      "verdict": j0}],
                            "resume": {"plus_rien_a_lire": 1, "decidables": 1, "sortis_du_rouleau": 1,
                                       "a_la_surface": int(j0["a_la_surface"]),
                                       "au_dela_de_la_surface": int(j0["au_dela_de_la_surface"]),
                                       "dans_un_vide_interieur": 0, "rien_sur_seize_pas": 1,
                                       "ecart_a_la_surface_median_mm": j0["ecart_a_la_surface_mm"],
                                       "rayon_exterieur_median_mm": ext0["rayon_exterieur_mm"],
                                       "rayon_arret_median_mm": a0["rayon_arret_mm"]}}]}
    tampon = io.StringIO()
    with contextlib.redirect_stdout(tampon):
        afficher(faux)
    v("... et l'affichage tourne dessus", "SORTI DU ROULEAU" in tampon.getvalue())
    tampon = io.StringIO()
    with contextlib.redirect_stdout(tampon):
        afficher({"message": "volume injoignable"})
    v("... et un volume injoignable est dit, jamais dessiné", "⚠" in tampon.getvalue())

    print(f"\n{'ALL PASS' if echecs == 0 else 'ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path, default=None)
    p.add_argument("--fils", type=int, default=64)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(fils=a.fils)
    afficher(r)
    if "message" in r:
        return 1
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False))
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
