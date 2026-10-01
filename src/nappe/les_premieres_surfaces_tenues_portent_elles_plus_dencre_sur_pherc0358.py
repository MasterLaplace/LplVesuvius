"""Sur PHerc0358, les premières surfaces que le critère tient portent-elles plus d'encre, au détecteur de 296, que celles qu'il refuse ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UNE SEULE LECTURE D'ENCRE DE PHERC0358 N'EXISTE. Ce qui était vu avant d'écrire : tout ce que `296`
à `408` publient, dont **`R4-F540`** et la mesure de `354` (les statuts des surfaces des chaînes de PHerc0358 au critère de `352`), et
**`408`** : sur le bloc étalon de PHercParis4 ramené à 9,6 µm par moyenne de bloc, le détecteur de `296` s'accorde encore à 0,869 avec
la carte publiée, contre 0,0554 pour le témoin, mais dans un seul sens des couches (`R4-F594`) ; **`409`** fixe ce sens sur le bloc
étalon, rendu par le rendu de ce fichier depuis le niveau 9,6 µm de PHercParis4 : les couches croissant vers le creux de la feuille, 0,8162
contre 0,1083 pour le témoin, et −0,0777 vers la bosse (`R4-F595`). Aucune lecture d'encre de PHerc0358 n'existe, nulle part.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P151`. PHerc0358 n'a aucun tracé humain. Sur un tel rouleau, l'encre est le seul témoin
indépendant du compte des feuilles de `m7`, qui fonde le critère. Si les surfaces que le critère tient portent plus d'encre propre à
leur feuille que celles qu'il refuse, le critère est confirmé par un juge qui ne lui doit rien.

## Ce qui est fait

- **Les chaînes de PHerc0358**, reconstruites comme `354` les construit (`m331.les_chaines_de_0358`), et leurs sauts jugés par le
  critère de `354`. Le contrôle : chaque saut redonne le statut que `354` publie.
- **Les ensembles**, fixés par la règle avant la lecture : **H**, les surfaces du premier saut que le critère tient ; **R**, les surfaces
  des sauts 1 et 2 qu'il refuse et qui existent ; **N**, la nappe de départ de chaque graine chaînée.
- **Le rendu**, pour chaque surface : sa grille rééchantillonnée à 2,4 µm, et le scan lu en trilinéaire le long de ses normales, les
  couches 23 à 84 d'une pile dont la surface est la couche 54, comme le bloc étalon de `296`, empilées dans le sens que `409` fixe,
  vers le creux : **celui de la nappe de départ de sa graine**, porté à la surface par ses normales (amendé, voir plus bas). Le rendu
  est celui de `409`. **Le jumeau** : la même surface poussée d'un demi-pas, 10 voxels, du côté où croissent ses couches, entre deux
  feuilles.
- **Le détecteur**, celui de `296` et `408`, sur l'iGPU, une lecture par processus.
- **L'encre d'une lecture**, E : la probabilité moyenne, réduite 8 fois comme dans `296`, sur les pixels réduits entièrement couverts
  par la surface. **D = E(surface) − E(jumeau)**, sur les mêmes pixels : l'encre propre à la feuille. Une hallucination uniforme s'y
  annule.
- **Les témoins, qui doivent tenir pour que le verdict compte** : **T1**, `408` dit oui et `409` fixe un sens ; **T2**, sur au moins 2 des nappes de départ
  N, D > 0 : le détecteur distingue la feuille de l'entre-deux sur PHerc0358 même. T2 est lu d'abord ; s'il ne tient pas, H et R ne sont
  pas lus.
- **La règle** : si tous les D de H dépassent tous ceux de R, **oui** ; si aucun D de H ne dépasse la médiane de ceux de R, **non** ;
  sinon, **en partie**. Indécidable si T1 ou T2 ne tient pas, si une lecture manque ou si le contrôle échoue. Sous l'échange de H et R,
  le oui a une probabilité de 1 sur C(|H| + |R|, |H|).

## Les issues

L'issue de la tranche : **D de H : a ; D de R : de b à c ; T2 : k sur n**, puis ce que dit la règle.

## Rapporté à côté, qui ne décide rien

E brut de chaque surface et de son jumeau ; la part des pixels où la probabilité dépasse 0,5 ; le temps de chaque lecture. Le creux de
chaque surface : le rayon d'un cylindre qui donnerait sa courbure, et le cosinus entre son creux et la direction du centre du volume,
un axe grossier, puisque aucun axe de PHerc0358 n'est publié. Ajouté avant toute lecture, après le verdict de `409`.

**L'autre sens, à la question de l'auteur** (ajouté le 2026-10-01 vers 15 h 38, pendant les lectures, avant qu'une seule ne soit finie) :
l'encre elle-même dirait-elle dans quel sens lire ? **Le côté que l'encre choisit**, pour chaque surface, est celui dont la part des
pixels réduits au-dessus de 0,5 est la plus haute, à sa place ; à égalité, aucun. Le même choix est fait sur le bloc étalon de `409`, où
la carte publiée dit le bon sens. Rien de cela n'entre dans le verdict.

⚠⚠⚠ **AMENDÉ le 2026-10-01 vers 16 h, avant qu'une seule valeur d'encre de PHerc0358 ne soit regardée.** La règle écrite d'abord lisait
chaque surface vers son propre creux. La géométrie seule, sans encre, la contredit : les 13 surfaces ont des normales moyennes parallèles
à celles de la nappe de départ de leur graine (produit scalaire de 0,948 à 1), mais 5 d'entre elles se creusent du côté opposé à cette
nappe, dont `H_8_plus_1`. Deux feuilles voisines d'un même rouleau, à un ou deux pas l'une de l'autre, ne se creusent pas vers deux
axes opposés : sur des surfaces de 6 mm, dont la flèche est de 0 à 16 voxels pour des ondulations de 6 à 16, la courbure de chaque
surface ne dit pas de quel côté est l'axe. **La règle amendée**, qui seule décide : chaque surface est lue du côté du creux de la nappe
de départ de sa graine, porté par le signe du produit de leurs normales moyennes ; un produit sous 0,5 en valeur absolue laisse la
surface sans côté, donc indécidable. Les trois nappes de départ se lisent de leur propre côté, comme avant : les deux lectures de `N_6`
faites avant l'amendement sont de ce côté, et gardées. **Chaque surface et son jumeau sont aussi lus de l'autre côté**, après les
lectures qui décident : la règle écrite d'abord, le côté de la graine et le choix de l'encre sont ainsi rapportés tous les trois.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : si les lettres sont lisibles ; ce que vaut le critère au-delà des deux premiers sauts ; une surface
de 6 mm porte au plus quelques lettres, et peut n'en porter aucune.

Usage :
    uv run python src/nappe/les_premieres_surfaces_tenues_portent_elles_plus_dencre_sur_pherc0358.py --verifier
    uv run python src/nappe/les_premieres_surfaces_tenues_portent_elles_plus_dencre_sur_pherc0358.py --preparer
    uv run --project src/xpu --with albumentations --with zarr --with tqdm --with numcodecs --with imagecodecs \\
        python src/nappe/les_premieres_surfaces_tenues_portent_elles_plus_dencre_sur_pherc0358.py --encre
    uv run python src/nappe/les_premieres_surfaces_tenues_portent_elles_plus_dencre_sur_pherc0358.py \\
        --json docs/mesures/les_premieres_surfaces_tenues_portent_elles_plus_dencre_sur_pherc0358.json
"""
from __future__ import annotations

import argparse
import gc
import json
import math
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))
sys.path.insert(0, str(RACINE / "src" / "tracecheck"))

import le_tour_produit_porte_t_il_le_texte_du_segment as m296  # noqa: E402
import une_nappe_tiree_de_m7_suit_elle_sa_feuille as m300  # noqa: E402
import le_rendu_de_pherc0358_lit_il_lencre_de_paris4_et_dans_quel_sens as m409  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_354_A_PUBLIE = LES_MESURES / "le_compte_et_le_seuil_tiennent_ils_une_premiere_surface_sur_pherc0358.json"
CE_QUE_408_A_PUBLIE = LES_MESURES / "le_detecteur_de_296_lit_il_encore_lencre_de_paris4_ramenee_a_9um.json"
CE_QUE_409_A_PUBLIE = LES_MESURES / "le_rendu_de_pherc0358_lit_il_lencre_de_paris4_et_dans_quel_sens.json"
LE_DOSSIER = RACINE / "data" / "encre_pherc0358"
LE_VOXEL_UM, LE_PIXEL_UM = 9.362, 2.4
LA_COUCHE_DE_LA_SURFACE = 54
LE_DEMI_PAS = m300.LE_PAS_0358 / 2.0
LES_SAUTS_DE_R = (1, 2)
LE_MINIMUM_DE_T2 = 2
LE_SEUIL_HAUT = 0.5


def les_ensembles(d354: dict) -> dict:
    """H, R et N tels que la règle les fixe, depuis les statuts que `354` publie : des clés (rang, côté, saut), et les graines pour N."""
    h, r = [], []
    for c in d354["les_cotes"]:
        for s in c["les_sauts"]:
            cle = (c["le_rang"], c["le_cote"], s["le_saut"])
            if s["le_saut"] == 1 and s["tient"]:
                h.append(cle)
            elif s["le_saut"] in LES_SAUTS_DE_R and s["a_une_surface"] and not s["tient"]:
                r.append(cle)
    return {"H": h, "R": r, "N": sorted({c["le_rang"] for c in d354["les_cotes"]})}


def la_grille_fine(nappe: np.ndarray, valide: np.ndarray, pas_du_plan: float = m300.LE_PAS_DU_PLAN,
                   pixel: float = LE_PIXEL_UM / LE_VOXEL_UM) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """La surface rééchantillonnée au pixel du détecteur, par la grille de `409` : positions, normales unitaires et pixels couverts."""
    h, w = nappe.shape[:2]
    k = pas_du_plan / pixel
    ii, jj = np.meshgrid(np.arange(int((h - 1) * k)) / k, np.arange(int((w - 1) * k)) / k, indexing="ij")
    return m409.la_grille_aux_indices(nappe, valide, ii, jj)


LES_COTES = ("plus", "moins")
LE_PRODUIT_MINIMUM = 0.5


def lautre(cote: str) -> str:
    return "moins" if cote == "plus" else "plus"


def les_normales_du_cote(nn: np.ndarray, cote: str) -> np.ndarray:
    """Les normales du rendu : celles de la grille du côté « plus », retournées du côté « moins »."""
    return nn if cote == "plus" else -nn


def le_cote_du_creux(a: float, sens: str) -> str:
    """Le côté de la grille vers lequel croissent les couches : celui où la surface se creuse si `409` fixe le creux, l'autre sinon."""
    creux = "plus" if a > 0 else "moins"
    return creux if sens == "creux" else lautre(creux)


def les_cotes(nappes: dict, sens: str) -> dict:
    """Pour chaque surface, le côté que lit chaque règle. **Par la graine**, qui décide : le côté du creux de la nappe de départ de sa
    graine, porté par le signe du produit de leurs normales moyennes ; None si ce produit est sous 0,5 en valeur absolue. **Par la
    surface**, la règle écrite d'abord, rapportée : le côté de son propre creux."""
    geo = {nom: m409.la_courbure_moyenne(*nv) for nom, nv in nappes.items()}
    out = {}
    for nom, (a, nm, _) in geo.items():
        a0, nm0, _ = geo[f"N_{nom.split('_')[1]}"]
        pr = float(nm @ nm0)
        cote_n = le_cote_du_creux(a0, sens)
        par_la_graine = None if abs(pr) < LE_PRODUIT_MINIMUM else (cote_n if pr > 0 else lautre(cote_n))
        out[nom] = {"par_la_graine": par_la_graine, "par_la_surface": le_cote_du_creux(a, sens),
                    "le_produit_des_normales": round(pr, 4), "le_coefficient": a}
    return out


def les_nappes(plan: dict) -> dict:
    out = {}
    for nom in plan["les_surfaces"]:
        s = np.load(LE_DOSSIER / f"{nom}.npz")
        out[nom] = (s["la_nappe"], s["valide"])
    return out


def le_sens_de_409() -> str:
    return json.loads(CE_QUE_409_A_PUBLIE.read_text())["le_verdict"]["le_sens"]


def le_creux_rapporte(nappe: np.ndarray, valide: np.ndarray, forme: tuple) -> dict:
    """Rapporté à côté, qui ne décide rien : le coefficient a de la courbure de `409`, le rayon d'un cylindre qui le donnerait, 1/(4|a|),
    et le cosinus entre le creux et la direction du centre du volume dans le plan (x, y). Ce centre n'est qu'un axe grossier : aucun axe de
    PHerc0358 n'est publié. `forme` est en (z, y, x)."""
    a, nm, c = m409.la_courbure_moyenne(nappe, valide)
    creux = nm * (1.0 if a > 0 else -1.0)
    vers_laxe = np.array([forme[2] / 2.0, forme[1] / 2.0]) - c[:2]
    cos = float(creux[:2] @ vers_laxe / max(np.linalg.norm(creux[:2]) * np.linalg.norm(vers_laxe), 1e-12))
    return {"le_coefficient": a, "le_rayon_dun_cylindre_en_voxels": round(1.0 / (4.0 * abs(a)), 1) if a else None,
            "la_distance_au_centre_en_voxels": round(float(np.linalg.norm(vers_laxe)), 1), "le_cosinus_vers_le_centre": round(cos, 4)}


def lencre_dune_lecture(proba: np.ndarray, couvert: np.ndarray) -> dict:
    """E : la probabilité réduite 8 fois, moyennée sur les pixels réduits entièrement couverts ; et la part au-dessus de 0,5."""
    r = m296.reduire(proba)
    c = m296.reduire(couvert.astype(np.float32))
    h, w = min(r.shape[0], c.shape[0]), min(r.shape[1], c.shape[1])
    r, c = r[:h, :w], c[:h, :w]
    m = (c >= 1.0 - 1e-9) & np.isfinite(r)
    if not m.any():
        return {"lencre": None, "les_pixels": 0, "la_part_haute": None}
    return {"lencre": round(float(r[m].mean()), 5), "les_pixels": int(m.sum()), "la_part_haute": round(float((r[m] > LE_SEUIL_HAUT).mean()), 5)}


def le_d(lecture: dict, jumeau: dict) -> float | None:
    if lecture["lencre"] is None or jumeau["lencre"] is None:
        return None
    return round(lecture["lencre"] - jumeau["lencre"], 5)


def le_verdict(d: dict) -> dict:
    if not d.get("le_controle"):
        return {"decidable": False, "lissue": "indécidable : les chaînes reconstruites ne redonnent pas les statuts de 354"}
    if not d.get("t1"):
        return {"decidable": False, "lissue": "indécidable : T1 ne tient pas, le détecteur ne lit pas à 9,6 µm (408) ou le sens n'est pas fixé (409)"}
    dn = [x["le_d"] for x in d["les_lectures"]["N"]]
    k = sum(x is not None and x > 0 for x in dn)
    t2 = f"T2 : {k} sur {len(dn)}"
    if k < LE_MINIMUM_DE_T2:
        return {"decidable": False, "lissue": f"{t2} ; indécidable, le détecteur ne sépare pas la feuille de l'entre-deux"}
    dh, dr = [x["le_d"] for x in d["les_lectures"]["H"]], [x["le_d"] for x in d["les_lectures"]["R"]]
    if not dh or not dr or any(x is None for x in dh + dr):
        return {"decidable": False, "lissue": f"{t2} ; indécidable, une lecture de H ou de R manque"}
    f = lambda x: f"{x:g}".replace(".", ",")  # noqa: E731
    tete = f"D de H : {' ; '.join(f(x) for x in dh)} ; D de R : de {f(min(dr))} à {f(max(dr))} ; {t2}"
    med = float(np.median(dr))
    suite = "oui" if min(dh) > max(dr) else "non" if max(dh) <= med else "en partie"
    return {"decidable": True, "lissue": f"{tete} ; {suite}", "la_chance_du_oui": f"1 sur {math.comb(len(dh) + len(dr), len(dh))}"}


def le_nom(genre: str, cle) -> str:
    return f"{genre}_{cle}" if genre == "N" else f"{genre}_{cle[0]}_{cle[1]}_{cle[2]}"


def preparer() -> int:
    """Les chaînes reconstruites, le contrôle des statuts, et chaque surface lue gardée sur le disque ; les morceaux du scan qu'il faut,
    tirés s'ils manquent, et comptés."""
    import le_compte_et_le_seuil_tiennent_ils_une_premiere_surface_sur_pherc0358 as m354
    import la_matiere_dit_elle_si_la_surface_est_sur_sa_feuille as mm
    import une_chaine_relancee_a_chaque_tour_descend_elle_plus_loin as m331

    d354 = json.loads(CE_QUE_354_A_PUBLIE.read_text())
    ens = les_ensembles(d354)
    publie = {(c["le_rang"], c["le_cote"], s["le_saut"]): s["tient"] for c in d354["les_cotes"] for s in c["les_sauts"]}
    chaines, lv0, _ = m331.les_chaines_de_0358()
    LE_DOSSIER.mkdir(parents=True, exist_ok=True)
    controle, surfaces = True, {}
    for c in chaines:
        for h, k in enumerate(c["la_chaine"], 1):
            cle = (c["le_rang"], c["le_cote"], h)
            controle &= publie.get(cle) == m354.le_saut(k, lv0)["tient"]
            if cle in ens["H"] or cle in ens["R"]:
                surfaces[le_nom("H" if cle in ens["H"] else "R", cle)] = k["la_relance"]
            if h == 1 and c["le_rang"] in ens["N"]:
                surfaces.setdefault(le_nom("N", c["le_rang"]), k["le_depart"])
    controle &= len(publie) == sum(len(c["la_chaine"]) for c in chaines)
    vol = mm.LesMorceaux("PHerc0358", mm.LES_VOLUMES["PHerc0358"]["url"], 0)
    tires = {"deja": 0, "tire": 0, "absent": 0}
    marge = float(np.abs(m409.les_decalages_des_couches(LE_PIXEL_UM / LE_VOXEL_UM)).max() + LE_DEMI_PAS + 2)
    for nom, s in surfaces.items():
        np.savez_compressed(LE_DOSSIER / f"{nom}.npz", la_nappe=s["la_nappe"], valide=s["valide"])
        pts = s["la_nappe"][s["valide"]]
        bas = np.floor(pts.min(axis=0) - marge).astype(int)[::-1] // np.asarray(vol.taille)
        haut = np.floor(pts.max(axis=0) + marge).astype(int)[::-1] // np.asarray(vol.taille)
        for cz in range(bas[0], haut[0] + 1):
            for cy in range(bas[1], haut[1] + 1):
                for cx in range(bas[2], haut[2] + 1):
                    tires[vol.tirer(cz, cy, cx)] += 1
    plan = {"le_controle": bool(controle), "les_ensembles": {k: [list(x) if isinstance(x, tuple) else x for x in v] for k, v in ens.items()},
            "les_surfaces": sorted(surfaces), "les_morceaux": tires}
    (LE_DOSSIER / "plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1) + "\n")
    print(json.dumps(plan, ensure_ascii=False), flush=True)
    return 0 if controle else 1


def le_fichier(nom: str, decalage: float, cote: str) -> Path:
    """La lecture d'une surface : à sa place ou en jumeau, les couches croissant du côté « plus » de la grille ou du côté « moins »."""
    return LE_DOSSIER / f"{nom}_{'jumeau' if decalage else 'surface'}_{cote}.npy"


def le_cote_que_lencre_choisit(en_plus: dict, en_moins: dict) -> str | None:
    """Rapporté à côté : le côté dont la part haute est la plus grande ; None à égalité ou si une lecture manque."""
    a, b = en_plus.get("la_part_haute"), en_moins.get("la_part_haute")
    if a is None or b is None or a == b:
        return None
    return "plus" if a > b else "moins"


def lordre_des_lectures(noms: list[str], cotes: dict, t2_tient: bool | None) -> list[tuple[str, str]]:
    """Les lectures (surface, côté), dans l'ordre : les nappes de départ du côté qui décide ; si T2 tient, H et R de ce côté ; puis
    l'autre côté de tout ce qui a été lu. `t2_tient` à None : T2 n'est pas encore lu, seules les nappes viennent."""
    n = [x for x in noms if x.startswith("N_")]
    hr = [x for x in noms if x[:2] in ("H_", "R_")]
    out = [(x, cotes[x]["par_la_graine"]) for x in n]
    if t2_tient is None:
        return out
    lus = n + (hr if t2_tient else [])
    if t2_tient:
        out += [(x, cotes[x]["par_la_graine"]) for x in hr if cotes[x]["par_la_graine"] is not None]
    out += [(x, lautre(cotes[x]["par_la_graine"])) for x in lus if cotes[x]["par_la_graine"] is not None]
    return [(x, c) for x, c in out if c is not None]


def une_lecture(nom: str, decalage: float, cote: str) -> int:
    """Une surface rendue à `decalage` voxels de sa place, lue par le détecteur ; un processus par lecture. ⚠ La grille fine, ses normales
    et le cache des morceaux sont rendus avant de charger le modèle : à 2496², gardés, ils menaient le processus à 3,36 Go de mémoire
    anonyme pendant le chargement, figé sous le plafond de la garde."""
    import la_matiere_dit_elle_si_la_surface_est_sur_sa_feuille as mm
    import le_detecteur_de_296_lit_il_encore_lencre_de_paris4_ramenee_a_9um as m408

    s = np.load(LE_DOSSIER / f"{nom}.npz")
    p, nn, couvert = la_grille_fine(s["la_nappe"], s["valide"])
    nn = les_normales_du_cote(nn, cote)
    vol = mm.LesMorceaux("PHerc0358", mm.LES_VOLUMES["PHerc0358"]["url"], 0)
    t0 = time.monotonic()
    pile = m409.rendre(p, nn, couvert, decalage, LE_PIXEL_UM / LE_VOXEL_UM, lambda c: mm.les_profils(vol, c))
    rendu = round(time.monotonic() - t0, 1)
    sortie = le_fichier(nom, decalage, cote)
    np.save(LE_DOSSIER / f"{nom}_couvert.npy", couvert)
    a_cote = {"le_creux": le_creux_rapporte(s["la_nappe"], s["valide"], vol.forme), "la_couverture": round(float(couvert.mean()), 4)}
    del p, nn, couvert, vol, s
    gc.collect()
    r = m408.lencre(pile, sortie)
    ligne = {"la_surface": nom, "le_decalage": decalage, "le_cote": cote, "rendu_en_secondes": rendu, **r, **a_cote}
    with (LE_DOSSIER / "encre.out").open("a") as o:
        o.write(json.dumps(ligne, ensure_ascii=False) + "\n")
    print(json.dumps(ligne, ensure_ascii=False), flush=True)
    return 0


def encre() -> int:
    """T2 d'abord : les nappes de départ et leurs jumeaux ; H et R seulement si T2 tient. Chaque lecture dans son propre processus."""
    plan = json.loads((LE_DOSSIER / "plan.json").read_text())
    if not plan["le_controle"]:
        print("le contrôle des statuts de 354 échoue : rien n'est lu", flush=True)
        return 1

    cotes = les_cotes(les_nappes(plan), le_sens_de_409())
    (LE_DOSSIER / "cotes.json").write_text(json.dumps(cotes, ensure_ascii=False, indent=1) + "\n")

    def lire(paires):
        for nom, cote in paires:
            for dec in (0.0, LE_DEMI_PAS):
                if le_fichier(nom, dec, cote).exists():
                    continue
                subprocess.run([sys.executable, __file__, "--une-lecture", nom, "--decalage", str(dec), "--cote", cote], check=True)

    lire(lordre_des_lectures(plan["les_surfaces"], cotes, None))
    dn = [le_d(*les_deux(n, cotes[n]["par_la_graine"])) for n in plan["les_surfaces"] if n.startswith("N_")]
    t2 = sum(x is not None and x > 0 for x in dn) >= LE_MINIMUM_DE_T2
    print(json.dumps({"t2": "tient" if t2 else "ne tient pas"}), flush=True)
    lire(lordre_des_lectures(plan["les_surfaces"], cotes, t2))
    return 0


def le_choix_de_lencre(plan: dict, cotes: dict) -> dict:
    """Rapporté à côté : pour chaque surface lue des deux côtés, l'encre de chacun, le côté qu'elle choisit, et s'il est celui de la
    graine ou celui de la surface ; et le même choix sur le bloc étalon de `409`, où la carte publiée dit le bon sens."""
    out = []
    for nom in plan["les_surfaces"]:
        if not all(le_fichier(nom, 0.0, c).exists() for c in LES_COTES):
            continue
        couvert = np.load(LE_DOSSIER / f"{nom}_couvert.npy")
        e = {c: lencre_dune_lecture(np.load(le_fichier(nom, 0.0, c)), couvert) for c in LES_COTES}
        ch = le_cote_que_lencre_choisit(e["plus"], e["moins"])
        out.append({"la_surface": nom, "en_plus": e["plus"], "en_moins": e["moins"], "lencre_choisit": ch,
                    "celui_de_la_graine": ch is not None and ch == cotes[nom]["par_la_graine"],
                    "celui_de_la_surface": ch is not None and ch == cotes[nom]["par_la_surface"]})
    etalon = None
    if all((m409.LE_DOSSIER / f).exists() for f in ("encre_creux.npy", "encre_bosse.npy", "couvert.npy")):
        cv = np.load(m409.LE_DOSSIER / "couvert.npy")
        e = {s_: lencre_dune_lecture(np.load(m409.LE_DOSSIER / f"encre_{s_}.npy"), cv) for s_ in ("creux", "bosse")}
        ch = le_cote_que_lencre_choisit(e["creux"], e["bosse"])
        etalon = {"vers_le_creux": e["creux"], "vers_la_bosse": e["bosse"],
                  "lencre_choisit": None if ch is None else ("le creux" if ch == "plus" else "la bosse")}
    return {"les_surfaces": out, "letalon": etalon, "lues": len(out),
            "celui_de_la_graine": sum(x["celui_de_la_graine"] for x in out),
            "celui_de_la_surface": sum(x["celui_de_la_surface"] for x in out)}


def les_deux(nom: str, cote: str) -> tuple[dict, dict]:
    couvert = np.load(LE_DOSSIER / f"{nom}_couvert.npy")
    return tuple(lencre_dune_lecture(np.load(le_fichier(nom, dec, cote)), couvert) for dec in (0.0, LE_DEMI_PAS))


def les_lectures_par(plan: dict, cotes: dict, regle: str) -> dict:
    """Les D de chaque groupe, chaque surface lue du côté que donne `regle` (« par_la_graine » ou « par_la_surface »)."""
    out = {"H": [], "R": [], "N": []}
    for nom in plan["les_surfaces"]:
        c = cotes[nom][regle]
        if c is None or not all(le_fichier(nom, dec, c).exists() for dec in (0.0, LE_DEMI_PAS)):
            out[nom[0]].append({"la_surface": nom, "le_cote": c, "le_d": None})
            continue
        s, j = les_deux(nom, c)
        out[nom[0]].append({"la_surface": nom, "le_cote": c, "la_lecture": s, "le_jumeau": j, "le_d": le_d(s, j)})
    return out


def mesurer() -> dict:
    plan = json.loads((LE_DOSSIER / "plan.json").read_text())
    d408, d409 = json.loads(CE_QUE_408_A_PUBLIE.read_text()), json.loads(CE_QUE_409_A_PUBLIE.read_text())
    cotes = les_cotes(les_nappes(plan), d409["le_verdict"]["le_sens"])
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"le_voxel_um": LE_VOXEL_UM, "le_pixel_um": LE_PIXEL_UM, "le_demi_pas": LE_DEMI_PAS,
                            "les_sauts_de_r": list(LES_SAUTS_DE_R), "le_minimum_de_t2": LE_MINIMUM_DE_T2, "le_seuil_haut": LE_SEUIL_HAUT},
         "le_plan": plan, "le_controle": plan["le_controle"], "t1": d408["le_verdict"]["lissue"].endswith("; oui") and "le_sens" in d409["le_verdict"],
         "le_sens": d409["le_verdict"].get("le_sens"),
         "les_cotes": cotes,
         "les_lectures": les_lectures_par(plan, cotes, "par_la_graine"),
         "le_choix_de_lencre": le_choix_de_lencre(plan, cotes),
         "les_temps": [json.loads(l) for l in (LE_DOSSIER / "encre.out").read_text().splitlines()] if (LE_DOSSIER / "encre.out").exists() else []}
    d["le_verdict"] = le_verdict(d)
    premiere = {**d, "les_lectures": les_lectures_par(plan, cotes, "par_la_surface")}
    d["la_regle_ecrite_dabord"] = {"les_lectures": premiere["les_lectures"], "le_verdict": le_verdict(premiere)}
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

    s_ = lambda h, t, a=True: {"le_saut": h, "tient": t, "a_une_surface": a}  # noqa: E731
    d354 = {"les_cotes": [{"le_rang": 6, "le_cote": "moins", "les_sauts": [s_(1, True), s_(2, False), s_(3, False)]},
                          {"le_rang": 7, "le_cote": "plus", "les_sauts": [s_(1, False), s_(2, False, False), s_(4, True)]},
                          {"le_rang": 8, "le_cote": "plus", "les_sauts": [s_(1, False), s_(2, True)]}]}
    e = les_ensembles(d354)
    v("★★★★ H est le premier saut tenu, R les sauts 1 et 2 refusés qui ont une surface, N les graines chaînées",
      e == {"H": [(6, "moins", 1)], "R": [(6, "moins", 2), (7, "plus", 1), (8, "plus", 1)], "N": [6, 7, 8]}, str(e))

    ii, jj = np.meshgrid(np.arange(5.0), np.arange(5.0), indexing="ij")
    plan_ = np.stack([jj * 10.0, ii * 10.0, np.full_like(ii, 7.0)], -1)
    ok = np.ones((5, 5), bool)
    p, nn, couvert = la_grille_fine(plan_, ok, pas_du_plan=10.0, pixel=2.5)
    v("★★★★ la grille fine a le pas du détecteur et garde les positions de la surface",
      p.shape[:2] == (16, 16) and np.allclose(p[1, 1], [2.5, 2.5, 7.0]) and np.allclose(p[..., 2], 7.0))
    v("★★★★ les normales fines sont unitaires et celles de la grille", np.allclose(np.linalg.norm(nn[couvert], axis=-1), 1.0)
      and np.allclose(np.abs(nn[couvert][:, 2]), 1.0))
    v("★★★★ un pixel n'est couvert que si ses sommets voisins le sont : le bord, sans normale, ne l'est pas",
      not couvert[0].any() and couvert[5:10, 5:10].all())
    t = m409.les_decalages_des_couches(0.25)
    v("★★★★ la couche 54 est la surface, et les couches vont de 23 à 84", len(t) == 62 and t[54 - 23] == 0.0 and t[0] == -31 * 0.25)
    vu = []
    pile = m409.rendre(p, nn, couvert, 2.0, 0.25, lambda c: (vu.append(c) or c[..., 0] * 10.0), bande=4)
    signe = float(nn[couvert][0, 2])
    v("★★★★ le rendu lit le long de la normale, au décalage demandé, la surface à la couche 54, et zéro hors de la surface",
      pile.shape == (16, 16, 62) and pile[~couvert].max() == 0
      and np.allclose(np.concatenate(vu)[:, 54 - 23, 0], 7.0 + 2.0 * signe), str(np.concatenate(vu)[:3, 54 - 23]))

    ib, jb = np.meshgrid(np.arange(9.0), np.arange(9.0), indexing="ij")
    bol = np.stack([(jb - 4) * 10.0, (ib - 4) * 10.0, ((jb - 4) ** 2 + (ib - 4) ** 2) * 2.0], -1)
    okb = np.ones((9, 9), bool)
    _, nb, cb = la_grille_fine(bol, okb, pas_du_plan=10.0, pixel=5.0)
    cote_bol = le_cote_du_creux(m409.la_courbure_moyenne(bol, okb)[0], "creux")
    v("★★★★ les normales tournées vers le creux d'un bol montent ; de l'autre côté elles descendent",
      (les_normales_du_cote(nb, cote_bol)[cb][:, 2] > 0).all() and (les_normales_du_cote(nb, lautre(cote_bol))[cb][:, 2] < 0).all()
      and le_cote_du_creux(m409.la_courbure_moyenne(bol, okb)[0], "bosse") == lautre(cote_bol))
    ondule = bol * [1, 1, -1] + [0, 0, 20.0]
    retourne = bol[::-1].copy()
    cts = les_cotes({"N_6": (bol, okb), "R_6_moins_2": (ondule, okb), "H_6_moins_1": (retourne, okb)}, "creux")
    v("★★★★ une surface parallèle qui se creuse de l'autre côté garde, par la graine, le côté de la nappe de départ",
      cts["R_6_moins_2"]["par_la_graine"] == cts["N_6"]["par_la_graine"] == cote_bol
      and cts["R_6_moins_2"]["par_la_surface"] == lautre(cote_bol), str(cts))
    v("★★★★ une grille retournée prend, par la graine, le côté opposé de sa grille, le même dans l'espace",
      cts["H_6_moins_1"]["le_produit_des_normales"] < 0 and cts["H_6_moins_1"]["par_la_graine"] == lautre(cote_bol))
    pl = np.stack([(jb - 4) * 10.0, np.zeros_like(jb), (ib - 4) * 10.0], -1)
    v("★★★ une surface perpendiculaire à sa nappe de départ n'a pas de côté",
      les_cotes({"N_6": (bol, okb), "R_6_moins_2": (pl, okb)}, "creux")["R_6_moins_2"]["par_la_graine"] is None)
    th, zz = np.meshgrid(np.linspace(-0.3, 0.3, 13), np.linspace(0.0, 120.0, 13), indexing="ij")
    cyl = np.stack([600.0 + 200.0 * np.cos(th), 500.0 + 200.0 * np.sin(th), zz], -1)
    okc = np.ones(th.shape, bool)
    rc = le_creux_rapporte(cyl, okc, (400, 1000, 1200))
    v("★★★★ sur un cylindre de rayon 200 autour du centre du volume, le creux regarde le centre et le rayon redonne 200 à 10 % près",
      rc["le_cosinus_vers_le_centre"] > 0.99 and abs(rc["le_rayon_dun_cylindre_en_voxels"] - 200.0) < 20.0
      and abs(rc["la_distance_au_centre_en_voxels"] - 200.0) < 10.0, str(rc))
    v("★★★ retourné, le cylindre garde son creux vers le centre",
      le_creux_rapporte(cyl[::-1], okc, (400, 1000, 1200))["le_cosinus_vers_le_centre"] > 0.99)
    pr = np.zeros((64, 64), np.float32)
    pr[:, :32] = 0.8
    cv = np.zeros((64, 64), bool)
    cv[:, :36] = True
    v("★★★★ E ne compte que les pixels réduits entièrement couverts",
      lencre_dune_lecture(pr, cv)["lencre"] == 0.8 and lencre_dune_lecture(pr, cv)["les_pixels"] == 8 * 4)
    v("★★★★ D est l'encre de la surface moins celle du jumeau", le_d({"lencre": 0.3}, {"lencre": 0.1}) == 0.2
      and le_d({"lencre": None}, {"lencre": 0.1}) is None)

    lu = lambda d_: {"le_d": d_}  # noqa: E731
    d_ = lambda h, r, n=(0.1, 0.1, -0.1), t1=True, ok_=True: {"le_controle": ok_, "t1": t1, "les_lectures": {  # noqa: E731
        "H": [lu(x) for x in h], "R": [lu(x) for x in r], "N": [lu(x) for x in n]}}
    r8 = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08]
    v("★★★★ la règle : tous les H au-dessus de tous les R, oui ; aucun au-dessus de la médiane, non ; sinon, en partie",
      le_verdict(d_([0.1, 0.09], r8))["lissue"].endswith("; oui") and le_verdict(d_([0.04, 0.03], r8))["lissue"].endswith("; non")
      and le_verdict(d_([0.1, 0.03], r8))["lissue"].endswith("; en partie")
      and le_verdict(d_([0.1, 0.06], r8))["lissue"].endswith("; en partie"))
    v("★★★★ l'issue dit les D et T2 ; la chance du oui est 1 sur 45 pour 2 contre 8",
      le_verdict(d_([0.1, 0.09], r8))["lissue"] == "D de H : 0,1 ; 0,09 ; D de R : de 0,01 à 0,08 ; T2 : 2 sur 3 ; oui"
      and le_verdict(d_([0.1, 0.09], r8))["la_chance_du_oui"] == "1 sur 45")
    v("★★★★ indécidable si T2 a moins de 2 nappes à D positif, sans T1, sans contrôle, ou si une lecture manque",
      not le_verdict(d_([0.1, 0.09], r8, n=(0.1, -0.1, None)))["decidable"] and not le_verdict(d_([0.1, 0.09], r8, t1=False))["decidable"]
      and not le_verdict(d_([0.1, 0.09], r8, ok_=False))["decidable"] and not le_verdict(d_([0.1, None], r8))["decidable"])

    v("★★★★ chaque lecture porte sa place et son côté dans son nom",
      le_fichier("N_6", 0.0, "moins").name == "N_6_surface_moins.npy" and le_fichier("N_6", LE_DEMI_PAS, "plus").name == "N_6_jumeau_plus.npy")
    v("★★★★ l'encre choisit le côté à la part haute la plus grande, aucun à égalité ou si une lecture manque",
      le_cote_que_lencre_choisit({"la_part_haute": 0.2}, {"la_part_haute": 0.05}) == "plus"
      and le_cote_que_lencre_choisit({"la_part_haute": 0.05}, {"la_part_haute": 0.2}) == "moins"
      and le_cote_que_lencre_choisit({"la_part_haute": 0.1}, {"la_part_haute": 0.1}) is None
      and le_cote_que_lencre_choisit({"la_part_haute": None}, {"la_part_haute": 0.1}) is None)
    noms = ["H_6_moins_1", "N_6", "N_7", "R_7_plus_1"]
    cc = {"H_6_moins_1": {"par_la_graine": "moins"}, "N_6": {"par_la_graine": "moins"}, "N_7": {"par_la_graine": "plus"},
          "R_7_plus_1": {"par_la_graine": None}}
    v("★★★★ l'ordre : les nappes du côté qui décide d'abord ; H et R seulement si T2 tient ; puis l'autre côté de ce qui est lu",
      lordre_des_lectures(noms, cc, None) == [("N_6", "moins"), ("N_7", "plus")]
      and lordre_des_lectures(noms, cc, True) == [("N_6", "moins"), ("N_7", "plus"), ("H_6_moins_1", "moins"),
                                                  ("N_6", "plus"), ("N_7", "moins"), ("H_6_moins_1", "plus")]
      and lordre_des_lectures(noms, cc, False) == [("N_6", "moins"), ("N_7", "plus"), ("N_6", "plus"), ("N_7", "moins")],
      str(lordre_des_lectures(noms, cc, True)))

    for e_ in echecs:
        print(f"  ÉCHEC {e_}")
    print(f"{Path(__file__).name}   {'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--preparer", action="store_true", help="les chaînes, le contrôle, les surfaces et les morceaux du scan")
    p.add_argument("--encre", action="store_true", help="T2, puis H et R si T2 tient, sur l'iGPU")
    p.add_argument("--une-lecture", default=None, help="une surface, dans son propre processus")
    p.add_argument("--decalage", type=float, default=0.0)
    p.add_argument("--cote", choices=LES_COTES, default=None, help="le côté de la grille vers lequel croissent les couches")
    p.add_argument("--json", type=Path, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if a.preparer:
        return preparer()
    if a.une_lecture:
        return une_lecture(a.une_lecture, a.decalage, a.cote)
    if a.encre:
        return encre()
    d = mesurer()
    texte = json.dumps(d, ensure_ascii=False, indent=1)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(texte + "\n")
    print(json.dumps(d["le_verdict"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
