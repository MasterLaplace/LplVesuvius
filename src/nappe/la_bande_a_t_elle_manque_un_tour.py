"""Là où la bande saute plus d'un pas et demi, est-ce elle qui a manqué un tour, ou la chaîne qui s'arrête sur une
fausse feuille ?

⭐⭐⭐⭐ LA QUESTION DE `248` (`R4-P93`). Au premier saut, la chaîne tombe trop près de la couche de la bande sur 1516 et
1611 points avec `m7`, et près des trois quarts de ces chutes sont là où la bande elle-même saute plus d'un pas et demi
entre le segment et sa couche suivante. Deux lectures s'opposent : la bande n'a pas tracé un tour et le juge compte le
suivant, ou l'écart réel est grand et la prédiction voit une feuille qui n'existe pas. Elles disent deux choses
différentes de ce que la chaîne perd par saut.

⭐⭐⭐⭐ LE JUGE EST LE SCAN LUI-MÊME, lu brut au niveau 2 (9,6 µm), là où la chaîne est tombée. Le scan ne dépend ni de
la bande ni de la prédiction que la chaîne a lue : s'il montre de la matière à cette profondeur, la chaîne y a trouvé
une vraie feuille et c'est la bande qui a manqué un tour.

⚠⚠⚠ LE CRITÈRE EST ÉTALONNÉ, PAS CHOISI. « De la matière » veut dire : une intensité, rapportée à celle de la feuille du
segment sur le même rayon, au-dessus d'un seuil fixé par deux groupes témoins dont on connaît la réponse. Là où la
chaîne et la bande s'accordent, il y a une feuille à leur profondeur commune (le témoin feuille), et un interstice à
mi-chemin entre le segment et elle (le témoin interstice). Le seuil est celui qui sépare le mieux les deux (Youden) ; sa
sensibilité et son taux de fausses alertes sont mesurés sur eux, et la part de vraies feuilles parmi les chutes en est
déduite par le mélange des deux taux.

⚠⚠ LES CHOIX SONT DÉCLARÉS AVANT LA MESURE : la moyenne sur 3 × 3 rayons voisins espacés d'un voxel brut, la fenêtre de
huit voxels de part et d'autre de la profondeur, le seuil de Youden, un témoin sur k points d'accord pour en garder
environ trois mille par côté, et les deux prédictions de `248`.

Usage :
    uv run python src/nappe/la_bande_a_t_elle_manque_un_tour.py --verifier
    uv run python src/nappe/la_bande_a_t_elle_manque_un_tour.py --json docs/mesures/la_bande_a_t_elle_manque_un_tour.json
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

from la_spire_voisine_est_elle_a_un_pas import (DEMI_PAS_EN_VOXELS, LE_CACHE, PAS_EN_VOXELS,  # noqa: E402
                                                les_normales, lire_tifxyz, telecharger)
from le_transfert_enchaine_tient_il_les_spires import (LA_BANDE, LA_TRANCHE, LES_SAUTS,  # noqa: E402
                                                       les_couches_ordonnees)
from le_transfert_retrouve_t_il_la_spire_voisine import (DELAI, LA_MAILLE, LE_VOLUME,  # noqa: E402
                                                         LES_PREDICTIONS, le_facteur, lecteur_du_depot,
                                                         lire_les_valeurs)

LE_NIVEAU_BRUT = 2
LA_FENETRE_BRUTE = 8.0          # voxels du maillage, de part et d'autre de la profondeur lue
LE_SAUT_DE_LA_BANDE = PAS_EN_VOXELS + DEMI_PAS_EN_VOXELS
LES_TEMOINS_PAR_COTE = 3000
LE_DERRIERE = 12.0              # le rayon commence un peu derrière le segment, pour lire sa feuille entière


def les_offsets(n: np.ndarray, facteur: int) -> np.ndarray:
    """Les 3 × 3 décalages latéraux de chaque rayon, espacés d'un voxel brut, dans le plan normal à n."""
    a = np.where(np.abs(n[:, :1]) < 0.9, np.array([[1.0, 0.0, 0.0]]), np.array([[0.0, 1.0, 0.0]]))
    e1 = np.cross(n, a)
    e1 /= np.linalg.norm(e1, axis=1, keepdims=True)
    e2 = np.cross(n, e1)
    k = np.array([-1.0, 0.0, 1.0]) * facteur
    return np.stack([i * e1 + j * e2 for i in k for j in k], axis=1)        # (points, 9, xyz)


def le_profil_brut(p: np.ndarray, n: np.ndarray, t: np.ndarray, facteur: int, meta: dict, lire) -> np.ndarray:
    """L'intensité brute le long du rayon de chaque point, moyennée sur ses 3 × 3 rayons voisins."""
    off = les_offsets(n, facteur)
    pos = p[:, None, None, :] + off[:, None, :, :] + t[None, :, None, None] * n[:, None, None, :]
    idx = np.floor(pos[..., ::-1] / facteur).astype(np.int64).reshape(len(p), -1, 3)
    val = lire_les_valeurs(idx, meta, lire).astype(np.float64).reshape(len(p), len(t), off.shape[1])
    return val.mean(axis=2)


def la_moyenne_autour(profil: np.ndarray, t: np.ndarray, centre: np.ndarray,
                      demi: float = LA_FENETRE_BRUTE) -> np.ndarray:
    """La moyenne du profil de chaque point dans la fenêtre de ± `demi` voxels autour de `centre`."""
    dedans = np.abs(t[None, :] - centre[:, None]) <= demi
    with np.errstate(invalid="ignore"):
        return np.where(dedans.any(axis=1), (profil * dedans).sum(axis=1) / dedans.sum(axis=1), np.nan)


def le_seuil(feuille: np.ndarray, interstice: np.ndarray) -> dict:
    """Le seuil qui sépare le mieux deux témoins (Youden), sa sensibilité, ses fausses alertes, et l'aire sous la
    courbe ROC. Une valeur au-dessus du seuil est lue comme de la matière."""
    f, g = feuille[np.isfinite(feuille)], interstice[np.isfinite(interstice)]
    cand = np.unique(np.concatenate([f, g]))
    tpr = np.array([(f >= c).mean() for c in cand])
    fpr = np.array([(g >= c).mean() for c in cand])
    k = int(np.argmax(tpr - fpr))
    rang = np.argsort(np.argsort(np.concatenate([f, g]), kind="stable"), kind="stable") + 1.0
    auc = (rang[:len(f)].sum() - len(f) * (len(f) + 1) / 2.0) / (len(f) * len(g))
    return {"le_seuil": float(cand[k]), "la_sensibilite": float(tpr[k]), "les_fausses_alertes": float(fpr[k]),
            "laire_sous_la_courbe": float(auc)}


def la_part_de_vraies_feuilles(part_observee: float, sensibilite: float, fausses_alertes: float) -> float | None:
    """La part de vraies feuilles qui rend compte d'une part observée au-dessus du seuil, par le mélange des deux taux
    des témoins, bornée à [0, 1]. Indécidable si le seuil ne sépare rien."""
    if sensibilite - fausses_alertes <= 0:
        return None
    return float(min(1.0, max(0.0, (part_observee - fausses_alertes) / (sensibilite - fausses_alertes))))


def les_groupes(tau: np.ndarray, t_b: np.ndarray, cote: float) -> dict:
    """Les points d'accord, les chutes trop près là où la bande saute, et les chutes trop près là où elle ne saute pas."""
    note = np.isfinite(t_b) & np.isfinite(tau)
    with np.errstate(invalid="ignore"):
        err = cote * (tau - t_b)
        accord = note & (np.abs(err) < DEMI_PAS_EN_VOXELS)
        pres = note & (err <= -DEMI_PAS_EN_VOXELS)
        saute = np.abs(t_b) > LE_SAUT_DE_LA_BANDE
    return {"accord": accord, "trop_pres_la_ou_la_bande_saute": pres & saute,
            "trop_pres_la_ou_elle_ne_saute_pas": pres & ~saute}


def un_sur_k(masque: np.ndarray, combien: int) -> np.ndarray:
    """Un point sur k parmi ceux du masque, dans l'ordre de la maille, pour en garder environ `combien`."""
    ou = np.flatnonzero(masque)
    k = max(1, int(np.ceil(len(ou) / combien)))
    garde = np.zeros_like(masque)
    garde[ou[::k]] = True
    return garde


def _q(x: np.ndarray) -> dict:
    x = x[np.isfinite(x)]
    if not len(x):
        return {"combien": 0}
    return {"combien": int(len(x)), "q25": round(float(np.percentile(x, 25)), 4),
            "mediane": round(float(np.median(x)), 4), "q75": round(float(np.percentile(x, 75)), 4)}


LA_PORTEE_ALIGNEE = 44         # voxels de part et d'autre de la profondeur où les profils sont alignés
LE_CREUX = (28.0, 44.0)        # un demi-pas, à la fenêtre près : là où un interstice borde une feuille
LES_TIRAGES = 200


def le_profil_aligne(profil: np.ndarray, t: np.ndarray, centre: np.ndarray, soi: np.ndarray,
                     portee: int = LA_PORTEE_ALIGNEE) -> np.ndarray:
    """Le profil de chaque rayon, rapporté à la feuille du segment, lu à ± `portee` voxels de `centre`, dans le sens
    du rayon. Hors du rayon, NaN."""
    pas = t[1] - t[0]
    i0 = np.rint((centre - t[0]) / pas).astype(np.int64)
    d = np.arange(-portee, portee + 1)
    ii = i0[:, None] + d[None, :]
    dedans = (ii >= 0) & (ii < len(t)) & np.isfinite(centre)[:, None]
    val = np.take_along_axis(profil, np.clip(ii, 0, len(t) - 1), axis=1)
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(dedans, val / soi[:, None], np.nan)


def le_contraste(aligne: np.ndarray, demi: float = LA_FENETRE_BRUTE, creux=LE_CREUX) -> float:
    """Le pic sur le creux du profil médian aligné : la moyenne à ± `demi` du centre, sur celle à un demi-pas de part
    et d'autre. Une feuille au centre donne plus de un, un interstice moins de un."""
    d = np.arange(aligne.shape[1]) - aligne.shape[1] // 2
    with np.errstate(invalid="ignore"):
        med = np.nanmedian(aligne, axis=0)
    pic = np.nanmean(med[np.abs(d) <= demi])
    bord = np.nanmean(med[(np.abs(d) >= creux[0]) & (np.abs(d) <= creux[1])])
    return float(pic / bord)


def le_contraste_et_son_intervalle(aligne: np.ndarray, tirages: int = LES_TIRAGES, graine: int = 0) -> dict:
    """Le contraste du profil médian, et son intervalle de 5 à 95 % par tirage des rayons avec remise."""
    rng = np.random.default_rng(graine)
    c = [le_contraste(aligne[rng.integers(0, len(aligne), len(aligne))]) for _ in range(tirages)]
    with np.errstate(invalid="ignore"):
        med = np.nanmedian(aligne, axis=0)
    return {"le_contraste": round(le_contraste(aligne), 4), "q05": round(float(np.percentile(c, 5)), 4),
            "q95": round(float(np.percentile(c, 95)), 4), "les_rayons": int(len(aligne)),
            "lamplitude": round(float(np.nanmax(med) - np.nanmin(med)), 4),
            "le_profil_median": [round(float(x), 4) for x in med]}


def juger_un_cote(profil: np.ndarray, t: np.ndarray, tau: np.ndarray, t_b: np.ndarray, groupes: dict,
                  temoins: np.ndarray) -> dict:
    """Le seuil étalonné sur les témoins, puis ce que le scan montre là où la chaîne et la bande sont tombées."""
    soi = la_moyenne_autour(profil, t, np.zeros(len(tau)))

    def s(centre):
        with np.errstate(invalid="ignore", divide="ignore"):
            return la_moyenne_autour(profil, t, centre) / soi

    ref = {"la_feuille": s(t_b)[temoins], "linterstice": s(t_b / 2.0)[temoins]}
    seuil = le_seuil(ref["la_feuille"], ref["linterstice"])
    out = {"les_temoins": int(temoins.sum()),
           "lintensite_du_segment": _q(soi[temoins]),
           "le_temoin_feuille": _q(ref["la_feuille"]), "le_temoin_interstice": _q(ref["linterstice"]),
           "le_seuil": {k: round(v, 4) for k, v in seuil.items()}, "les_chutes": {}}
    # ⚠⚠ LE PROFIL MÉDIAN DES TÉMOINS DONT LA COUCHE EST À UN PAS, à six voxels près : ajouté après la mesure, pour voir
    # ce que le scan montre le long de la normale là où la réponse est connue. Il ne change ni le seuil ni les groupes.
    a_un_pas = temoins & (np.abs(np.abs(t_b) - PAS_EN_VOXELS) <= 6.0)
    if a_un_pas.any():
        with np.errstate(invalid="ignore", divide="ignore"):
            rel = profil[a_un_pas] / soi[a_un_pas, None]
        out["le_profil_des_temoins_a_un_pas"] = {
            "combien": int(a_un_pas.sum()), "t": [round(float(x), 1) for x in np.abs(t)],
            **{nom: [round(float(x), 4) for x in np.nanpercentile(rel, q, axis=0)]
               for nom, q in (("q25", 25), ("mediane", 50), ("q75", 75))}}
    # ⚠⚠⚠ LE JUGE EN MOYENNE, AJOUTÉ APRÈS QUE LE JUGE POINT PAR POINT A ÉCHOUÉ SON ÉTALONNAGE. Un rayon seul est trop
    # bruité, mais la médiane de mille rayons alignés sur la même profondeur montre la feuille. Même étalonnage : les
    # points d'accord alignés là où la chaîne est tombée (une feuille connue), et à mi-chemin entre le segment et elle
    # (un interstice connu). Les chutes sont alignées là où la chaîne est tombée.
    out["le_juge_en_moyenne"] = {
        "le_temoin_feuille": le_contraste_et_son_intervalle(le_profil_aligne(profil, t, tau, soi)[temoins]),
        "le_temoin_interstice": le_contraste_et_son_intervalle(le_profil_aligne(profil, t, tau / 2.0, soi)[temoins])}
    for nom in ("trop_pres_la_ou_la_bande_saute", "trop_pres_la_ou_elle_ne_saute_pas"):
        g = groupes[nom]
        if g.any():
            out["le_juge_en_moyenne"][nom] = le_contraste_et_son_intervalle(le_profil_aligne(profil, t, tau, soi)[g])
    # ⚠ ET LA COUCHE QUE LA BANDE A TRACÉE, alignée sur la bande elle-même, contre les points d'accord alignés de même :
    # une face de feuille et non le centre d'une plage de la prédiction, donc un témoin à part.
    g = groupes["trop_pres_la_ou_la_bande_saute"]
    if g.any():
        out["le_juge_en_moyenne"]["le_temoin_feuille_sur_la_bande"] = le_contraste_et_son_intervalle(
            le_profil_aligne(profil, t, t_b, soi)[temoins])
        out["le_juge_en_moyenne"]["la_couche_de_la_bande_la_ou_elle_saute"] = le_contraste_et_son_intervalle(
            le_profil_aligne(profil, t, t_b, soi)[g])
    for nom in ("trop_pres_la_ou_la_bande_saute", "trop_pres_la_ou_elle_ne_saute_pas"):
        g = groupes[nom]
        if not g.any():
            out["les_chutes"][nom] = {"combien": 0}
            continue
        ou = {"ou_la_chaine_est_tombee": s(tau)[g], "ou_la_bande_a_sa_couche": s(t_b)[g],
              "entre_les_deux": s((tau + t_b) / 2.0)[g]}
        r = {"combien": int(g.sum()),
             "la_profondeur_de_la_chaine_en_pas": _q(np.abs(tau[g]) / PAS_EN_VOXELS),
             "la_profondeur_de_la_bande_en_pas": _q(np.abs(t_b[g]) / PAS_EN_VOXELS)}
        for k, v in ou.items():
            part = float((v[np.isfinite(v)] >= seuil["le_seuil"]).mean()) if np.isfinite(v).any() else None
            vraies = None if part is None else la_part_de_vraies_feuilles(part, seuil["la_sensibilite"],
                                                                           seuil["les_fausses_alertes"])
            r[k] = {"le_rapport": _q(v), "la_part_au_dessus_du_seuil": None if part is None else round(part, 4),
                    "la_part_de_vraies_feuilles": None if vraies is None else round(vraies, 4)}
        out["les_chutes"][nom] = r
    return out


def mesurer(cache: Path = LE_CACHE, maille: int = LA_MAILLE, delai: float = DELAI) -> dict:
    debut = time.monotonic()
    d = telecharger(LA_BANDE, cache, delai)
    if isinstance(d, str):
        return {"decidable": False, "la_raison": d}
    ref, valide, esp = lire_tifxyz(d)
    h = ref.shape[0]
    a, b = int(h * LA_TRANCHE[0]), int(h * LA_TRANCHE[1])
    ref, valide = ref[a:b], valide[a:b]
    couches = les_couches_ordonnees(ref, valide, esp, maille, LES_SAUTS)["les_cartes"]
    normales, ok = les_normales(ref, valide)
    grille = np.zeros_like(ok)
    grille[::maille, ::maille] = True
    ii, jj = np.nonzero(ok & grille)
    p, n = ref[ii, jj], normales[ii, jj]
    gi, gj = ii // maille, jj // maille
    facteur, meta = le_facteur(LE_VOLUME, LE_NIVEAU_BRUT, delai)
    lire, stats = lecteur_du_depot(meta, cache, "brut", LE_VOLUME, LE_NIVEAU_BRUT, delai)
    out = {"la_bande": LA_BANDE, "les_rangees": list(LA_TRANCHE), "les_points": int(len(p)),
           "le_volume": LE_VOLUME, "le_niveau": LE_NIVEAU_BRUT, "le_facteur": facteur,
           "la_fenetre_voxels": LA_FENETRE_BRUTE, "le_saut_de_la_bande_voxels": round(LE_SAUT_DE_LA_BANDE, 4),
           "les_predictions": {}}
    t_max = float(np.ceil(LES_SAUTS * PAS_EN_VOXELS))
    for cote_, nom, cote in (("plus", "du_cote_plus", 1.0), ("moins", "du_cote_moins", -1.0)):
        t_b = couches[cote_][gi, gj, 0]
        t = cote * np.arange(-LE_DERRIERE, t_max + 1.0)
        groupes, taus = {}, {}
        for nom_p in LES_PREDICTIONS:
            f = cache / f"transfert_suivante_{LA_BANDE}_{nom_p}_{nom}.npy"
            if not f.exists():
                return {"decidable": False, "la_raison": f"le premier saut de 247 manque : {f.name}"}
            taus[nom_p] = np.load(f)[gi, gj]
            groupes[nom_p] = les_groupes(taus[nom_p], t_b, cote)
        temoins = {k: un_sur_k(g["accord"], LES_TEMOINS_PAR_COTE) for k, g in groupes.items()}
        a_lire = np.zeros(len(p), dtype=bool)
        for k, g in groupes.items():
            a_lire |= temoins[k] | g["trop_pres_la_ou_la_bande_saute"] | g["trop_pres_la_ou_elle_ne_saute_pas"]
        profil = np.full((len(p), len(t)), np.nan)
        profil[a_lire] = le_profil_brut(p[a_lire], n[a_lire], t, facteur, meta, lire)
        for nom_p in LES_PREDICTIONS:
            out["les_predictions"].setdefault(nom_p, {})[nom] = juger_un_cote(profil, t, taus[nom_p], t_b,
                                                                              groupes[nom_p], temoins[nom_p])
        out.setdefault("les_rayons_lus", {})[nom] = int(a_lire.sum())
    out["la_lecture"] = {"chunks_lus": stats["lus"], "chunks_absents": stats["absents"],
                         "mo_lus": round(stats["octets"] / 1e6, 1), "les_pannes": stats["pannes"][:20],
                         "combien_de_pannes": len(stats["pannes"])}
    out["les_secondes"] = round(time.monotonic() - debut, 1)
    out["decidable"] = not stats["pannes"]
    return out


def afficher(r: dict) -> None:
    if "les_points" not in r:
        print(f"indécidable : {r.get('la_raison')}")
        return
    print(f"{r['la_bande']} {r['les_rangees']} : {r['les_points']} points, rayons lus {r['les_rayons_lus']}, "
          f"{r['la_lecture']['chunks_lus']} chunks, {r['la_lecture']['combien_de_pannes']} pannes, {r['les_secondes']} s")
    for nom_p, rp in r["les_predictions"].items():
        for nom, j in rp.items():
            print(f"— {nom_p} {nom} : {j['les_temoins']} témoins, segment {j['lintensite_du_segment']}")
            print(f"    témoin feuille {j['le_temoin_feuille']}   témoin interstice {j['le_temoin_interstice']}")
            print(f"    seuil {j['le_seuil']}")
            pr_ = j.get("le_profil_des_temoins_a_un_pas")
            if pr_:
                print(f"    profil médian des {pr_['combien']} témoins à un pas (t : rapport) : " + "  ".join(
                    f"{pr_['t'][k]:.0f}:{pr_['mediane'][k]:.3f}" for k in range(0, len(pr_['t']), 12)))
            for k_, c_ in j["le_juge_en_moyenne"].items():
                print(f"    en moyenne {k_:40s} {c_['le_contraste']} [{c_['q05']}, {c_['q95']}] sur {c_['les_rayons']}, "
                      f"amplitude {c_['lamplitude']}   "
                      + " ".join(f"{x:.2f}" for x in c_["le_profil_median"][::8]))
            for g, c in j["les_chutes"].items():
                if not c.get("combien"):
                    continue
                print(f"    {g} ({c['combien']}) : chaîne à {c['la_profondeur_de_la_chaine_en_pas']['mediane']} pas, "
                      f"bande à {c['la_profondeur_de_la_bande_en_pas']['mediane']} pas")
                for k in ("ou_la_chaine_est_tombee", "ou_la_bande_a_sa_couche", "entre_les_deux"):
                    print(f"      {k:26s} rapport médian {c[k]['le_rapport'].get('mediane')}   au-dessus du seuil "
                          f"{c[k]['la_part_au_dessus_du_seuil']}   part de vraies feuilles {c[k]['la_part_de_vraies_feuilles']}")


# ---------------------------------------------------------------------------------------------------
def verifier() -> int:
    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        if not ok:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    # ⭐⭐⭐⭐ LE SEUIL : deux témoins bien séparés donnent une aire de un et un seuil entre eux ; deux témoins confondus,
    # une aire d'un demi, et la part de vraies feuilles devient indécidable.
    rng = np.random.default_rng(7)
    f = rng.normal(1.0, 0.05, 500)
    g = rng.normal(0.4, 0.05, 500)
    s = le_seuil(f, g)
    v("★★★★ deux témoins séparés : aire de un", s["laire_sous_la_courbe"] > 0.999, str(s))
    v("★★★★ et le seuil tombe entre eux", 0.5 < s["le_seuil"] < 0.9, str(s))
    confondus = le_seuil(rng.normal(0.7, 0.1, 2000), rng.normal(0.7, 0.1, 2000))
    v("★★★ deux témoins confondus : aire d'un demi", abs(confondus["laire_sous_la_courbe"] - 0.5) < 0.05, str(confondus))
    v("★★★★ un seuil qui ne sépare rien ne déduit aucune part", la_part_de_vraies_feuilles(0.6, 0.5, 0.5) is None)
    # ⭐⭐⭐⭐ LE MÉLANGE : une part observée à mi-chemin des deux taux veut dire une moitié de vraies feuilles.
    v("★★★★ à mi-chemin des deux taux, la moitié sont de vraies feuilles",
      abs(la_part_de_vraies_feuilles(0.5, 0.9, 0.1) - 0.5) < 1e-9)
    v("★★★ au taux des fausses alertes, aucune", la_part_de_vraies_feuilles(0.1, 0.9, 0.1) == 0.0)
    v("★★★ au-delà de la sensibilité, bornée à un", la_part_de_vraies_feuilles(0.95, 0.9, 0.1) == 1.0)
    # ⚠⚠ L'AIRE EST CELLE DE LA FEUILLE AU-DESSUS DE L'INTERSTICE, pas l'inverse.
    v("★★★★ des témoins inversés rendent une aire nulle", le_seuil(g, f)["laire_sous_la_courbe"] < 0.001)

    # ⭐⭐⭐ LES GROUPES : un point d'accord, une chute trop près où la bande saute, une où elle ne saute pas, un trop loin.
    t_b = np.array([72.0, 150.0, 100.0, 72.0, np.nan])
    tau = np.array([75.0, 72.0, 60.0, 150.0, 72.0])
    gr = les_groupes(tau, t_b, 1.0)
    v("★★★★ l'accord, la chute où la bande saute, celle où elle ne saute pas",
      gr["accord"].tolist() == [True, False, False, False, False]
      and gr["trop_pres_la_ou_la_bande_saute"].tolist() == [False, True, False, False, False]
      and gr["trop_pres_la_ou_elle_ne_saute_pas"].tolist() == [False, False, True, False, False], str(gr))
    grm = les_groupes(-tau, -t_b, -1.0)
    v("★★★ de l'autre côté, les mêmes groupes", all(np.array_equal(gr[k], grm[k]) for k in gr))
    v("★★★ un sur k garde environ le nombre voulu, dans l'ordre", un_sur_k(np.ones(10, bool), 3).tolist()
      == [True, False, False, False, True, False, False, False, True, False])

    # ⭐⭐⭐⭐ LE PROFIL BRUT, sur un scan fabriqué : trois feuilles en z, lues à travers le vrai chemin des chunks. Un
    # rayon qui traverse une feuille la voit, un rayon dans l'interstice ne voit rien, et la moyenne 3 × 3 ne déplace
    # pas une feuille plane.
    fa = 4
    meta = {"shape": [128, 32, 32], "chunks": [16, 16, 16], "fill_value": 0}
    vol = np.full(meta["shape"], 40, np.uint8)
    z0 = 20
    for z in (z0, z0 + 18, z0 + 36):
        vol[z - 2:z + 3, :, :] = 200

    def lire(c):
        a0 = np.asarray(c) * 16
        return vol[a0[0]:a0[0] + 16, a0[1]:a0[1] + 16, a0[2]:a0[2] + 16]

    p = np.array([[60.0, 60.0, z0 * fa + 2.0]])
    nn = np.array([[0.0, 0.0, 1.0]])
    t = np.arange(-12.0, 181.0)
    prof = le_profil_brut(p, nn, t, fa, meta, lire)
    v("★★★★ le profil voit la feuille du segment à t = 0", prof[0, t == 0][0] == 200.0, str(prof[0, t == 0]))
    v("★★★★ et l'interstice à mi-chemin", prof[0, t == 36][0] == 40.0, str(prof[0, t == 36]))
    v("★★★★ et la feuille suivante à un pas", prof[0, t == 72][0] == 200.0)
    moy = la_moyenne_autour(prof, t, np.array([72.0]))
    v("★★★ la fenêtre autour d'une feuille reste de la feuille", moy[0] > 150.0, str(moy))
    v("★★★ la fenêtre autour de l'interstice reste de l'interstice", la_moyenne_autour(prof, t, np.array([36.0]))[0] < 60.0)
    v("★★ une fenêtre hors du rayon ne rend rien", np.isnan(la_moyenne_autour(prof, t, np.array([1000.0]))[0]))
    # ⚠⚠⚠ LE CAS QUI COMPTE : une bande qui saute un tour. Le scan a une feuille à un pas, la bande n'a tracé que celle à
    # deux pas, la chaîne est tombée à un pas. Le rapport à la chaîne est celui d'une feuille, celui entre les deux
    # d'un interstice.
    soi = la_moyenne_autour(prof, t, np.array([0.0]))
    chaine = la_moyenne_autour(prof, t, np.array([72.0])) / soi
    entre = la_moyenne_autour(prof, t, np.array([108.0])) / soi
    v("★★★★ là où la bande a sauté un tour, le scan montre une feuille où la chaîne est tombée", chaine[0] > 0.75)
    v("★★★★ et un interstice entre la chaîne et la bande", entre[0] < 0.35, str(entre))
    incl = np.array([[1.0, 1.0, 1.0]]) / np.sqrt(3.0)
    off = les_offsets(incl, fa)
    normes = np.sort(np.linalg.norm(off[0], axis=1))
    v("★★★ les neuf rayons sont dans le plan normal, même pour une normale inclinée",
      np.abs(off[0] @ incl[0]).max() < 1e-9, str(off[0] @ incl[0]))
    v("★★★ et à un voxel brut, ou √2 en diagonale", np.allclose(normes, [0] + [fa] * 4 + [fa * np.sqrt(2)] * 4),
      str(normes))
    # ⭐⭐⭐⭐ LE JUGE D'UN CÔTÉ, sur des profils fabriqués : des témoins qui séparent, une chute sur une vraie feuille et
    # une chute sur rien. La part de vraies feuilles vaut la moitié.
    N = 402
    tt = np.arange(-12.0, 301.0)
    prof2 = np.full((N, len(tt)), 40.0)
    prof2[:, np.abs(tt) <= 10] = 200.0
    prof2[:400, np.abs(tt - 72) <= 10] = 200.0
    prof2[400, np.abs(tt - 72) <= 10] = 200.0         # la vraie feuille, que la bande n'a pas tracée
    prof2[400:, np.abs(tt - 144) <= 10] = 200.0       # la couche de la bande, à deux pas
    tb2 = np.r_[np.full(400, 72.0), 144.0, 144.0]
    tau2 = np.r_[np.full(400, 72.0), 72.0, 72.0]
    gr2 = les_groupes(tau2, tb2, 1.0)
    j = juger_un_cote(prof2, tt, tau2, tb2, gr2, gr2["accord"])
    c = j["les_chutes"]["trop_pres_la_ou_la_bande_saute"]
    v("★★★★ deux chutes où la bande saute, dont une sur une vraie feuille", c["combien"] == 2
      and c["ou_la_chaine_est_tombee"]["la_part_au_dessus_du_seuil"] == 0.5, str(c))
    v("★★★★ et la part de vraies feuilles en est la moitié", c["ou_la_chaine_est_tombee"]["la_part_de_vraies_feuilles"] == 0.5)
    v("★★★ la couche de la bande est une feuille pour les deux", c["ou_la_bande_a_sa_couche"]["la_part_au_dessus_du_seuil"] == 1.0)

    # ⚠⚠⚠ L'ÉCLAIRAGE D'UN RAYON NE DOIT PAS DÉCIDER : la moitié des témoins lus six fois plus sombres. Rapportée à la
    # feuille du segment sur le même rayon, la feuille reste une feuille et l'interstice un interstice.
    sombre = prof2.copy()
    sombre[:200] *= 0.15
    js = juger_un_cote(sombre, tt, tau2, tb2, gr2, gr2["accord"])
    v("★★★★ rapportée à la feuille du segment, l'intensité sépare encore parfaitement les témoins",
      js["le_seuil"]["laire_sous_la_courbe"] == 1.0, str(js["le_seuil"]))

    # ⭐⭐⭐⭐ LE JUGE EN MOYENNE : cent rayons bruités, une feuille à un pas. Aligné sur la feuille, le contraste dépasse
    # un ; aligné à mi-chemin, il est sous un ; et un tirage fixé rend le même intervalle.
    rng2 = np.random.default_rng(3)
    tt3 = np.arange(-12.0, 301.0)
    base = np.full(len(tt3), 40.0)
    base[np.abs(tt3) <= 10] = 200.0
    base[np.abs(tt3 - 72) <= 10] = 200.0
    bruit = base[None, :] + rng2.normal(0.0, 60.0, (100, len(tt3)))
    soi3 = la_moyenne_autour(bruit, tt3, np.zeros(100))
    feuille = le_contraste(le_profil_aligne(bruit, tt3, np.full(100, 72.0), soi3))
    creux = le_contraste(le_profil_aligne(bruit, tt3, np.full(100, 36.0), soi3))
    v("★★★★ en moyenne, aligné sur une feuille, le contraste dépasse un", feuille > 1.5, str(feuille))
    v("★★★★ et aligné sur l'interstice, il est sous un", creux < 0.7, str(creux))
    i1 = le_contraste_et_son_intervalle(le_profil_aligne(bruit, tt3, np.full(100, 72.0), soi3))
    v("★★★ l'intervalle encadre le contraste, et il est reproductible", i1["q05"] <= i1["le_contraste"] <= i1["q95"]
      and i1 == le_contraste_et_son_intervalle(le_profil_aligne(bruit, tt3, np.full(100, 72.0), soi3)))
    v("★★★ l'alignement lit dans le sens du rayon, de l'autre côté aussi",
      abs(le_contraste(le_profil_aligne(bruit, -tt3, np.full(100, -72.0), soi3)) - feuille) < 1e-9)
    plat = np.full((50, len(tt3)), 90.0)
    ip = le_contraste_et_son_intervalle(le_profil_aligne(plat, tt3, np.full(50, 72.0), np.full(50, 100.0)))
    v("★★★ un profil plat a un contraste de un et une amplitude nulle", ip["le_contraste"] == 1.0 and ip["lamplitude"] == 0.0,
      str({k: ip[k] for k in ("le_contraste", "lamplitude")}))
    v("★★★ une feuille bruitée a une amplitude", i1["lamplitude"] > 0.3, str(i1["lamplitude"]))
    v("★★ un centre hors du rayon ne rend rien", np.isnan(le_profil_aligne(bruit, tt3, np.full(100, 5000.0), soi3)).all())

    for e_ in echecs:
        print(f"  ÉCHEC {e_}")
    print(f"{Path(__file__).name}   "
          f"{'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} ({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path, default=None)
    p.add_argument("--delai", type=float, default=DELAI)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(LE_CACHE, LA_MAILLE, a.delai)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=1))
        print(f"\nécrit : {a.json}")
    return 0 if r.get("decidable") else 2


if __name__ == "__main__":
    raise SystemExit(main())
