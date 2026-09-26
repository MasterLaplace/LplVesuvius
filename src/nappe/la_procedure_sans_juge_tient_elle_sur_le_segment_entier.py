"""La procédure sans juge de `265` tient-elle sur le segment entier ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UN SEUL BLOC NEUF NE SOIT RENDU. Ce qui était vu avant d'écrire : tout ce que `257` à
`274` publient. La procédure de `265` n'a tourné que sur neuf blocs des 340 que `257` admet, deux choisis et sept pris à pas
réguliers par `263` ; réunis, elle y rend 37 ratés justes pour 7 justes ratés, un gain net de 30 (`274`).

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P95`. Ce qui remplace l'humain qui corrige le transfert doit corriger partout où
il passe, pas seulement là où on l'a regardé travailler : `263` a vu une procédure qui corrigeait les deux blocs choisis en
défaire d'autres. Neuf blocs ne disent pas ce que fait la procédure sur le segment. Les 340 le disent, et la spire produite
corrigée sur tout le segment est ce qu'une chaîne transférerait ensuite.

## La procédure, celle de `265`, sans rien y changer

Pour chaque bloc candidat de `257` : ses voisins au nord, au sud, à l'ouest et à l'est, gardés s'ils sont candidats ; la
marche d'un seul tenant sur le bloc et eux, pour la spire produite et pour le segment réduit ; l'ancre, la médiane de leur
différence sur les voisins seuls ; la décision de `264` ; une passe. Le juge ne sert qu'à noter.

⚠ Ce qui change est la façon de calculer, pas la procédure, et deux contrôles le tiennent :
- Un pas de fenêtre en fenêtre ne dépend que des deux chunks de sa couture : il est donc calculé une fois pour le segment,
  bloc par bloc, et la marche d'un voisinage est faite des pas dont les deux chunks sont dans ses blocs, dans l'ordre où `265`
  les prenait. Sur les neuf voisinages publiés, les comptes doivent redevenir les publiés.
- Les piles sont rendues depuis un miroir local des seuls chunks du volume qu'elles lisent (`le_miroir_du_volume`), et non
  plus à distance. Sur huit piles déjà rendues à distance, le rendu depuis le miroir doit être identique voxel pour voxel.
Si l'un des deux échoue, la mesure est indécidable.

## Les issues, exclusives, sur tous les blocs décidés réunis

- les ratés rendus justes sont plus nombreux que les justes rendus ratés : la procédure améliore la spire produite sur le
  segment entier ;
- ils ne le sont pas : elle ne l'améliore pas.

⚠ Rapporté à côté : bloc par bloc, ce que la décision corrige ; combien de blocs montent, descendent ou ne bougent pas ; les
blocs non décidés et pourquoi ; la part des points notés du segment que les blocs candidats couvrent.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : la spire suivante, transférée depuis celle-ci ; un autre côté, une autre prédiction ;
une seconde passe.

Usage :
    uv run python src/nappe/la_procedure_sans_juge_tient_elle_sur_le_segment_entier.py --verifier
    uv run python src/nappe/la_procedure_sans_juge_tient_elle_sur_le_segment_entier.py --les-neuf 5
    uv run python src/nappe/la_procedure_sans_juge_tient_elle_sur_le_segment_entier.py --rendre 4
    uv run python src/nappe/la_procedure_sans_juge_tient_elle_sur_le_segment_entier.py --pas 5
    uv run python src/nappe/la_procedure_sans_juge_tient_elle_sur_le_segment_entier.py \\
        --json docs/mesures/la_procedure_sans_juge_tient_elle_sur_le_segment_entier.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))

from combien_de_rangees_faut_il_pour_lire_le_pas import (LES_RANGEES, les_rangees_a_lire,  # noqa: E402
                                                         un_chunk_retenu)
from la_correction_tient_elle_sur_des_blocs_reguliers import la_part_reunie  # noqa: E402
from la_marche_corrige_t_elle_la_spire_produite import la_carte_aux_points, la_part_juste  # noqa: E402
from la_marche_sait_elle_ou_ne_pas_corriger import (corriger_decide, la_decision, le_bilan,  # noqa: E402
                                                    le_melange)
from la_spire_produite_se_lit_elle_dans_le_treillis import (LA_PREDICTION, LE_BLOC, LE_COTE,  # noqa: E402
                                                            LE_COTE_DU_CHUNK, LE_DOSSIER, LES_JUGES, le_cadre,
                                                            la_marche_du_bloc, la_pile_est_complete,
                                                            les_blocs_candidats, lerreur_jugee, lire_la_pile, rendre)
from la_spire_voisine_est_elle_a_un_pas import LE_CACHE, LE_SEGMENT, lire_tifxyz, telecharger  # noqa: E402
from le_pas_de_fenetre_en_fenetre_voit_il_la_rampe import la_somme_des_pas, les_fenetres  # noqa: E402
from le_miroir_du_volume import LE_MIROIR, les_chunks_dun_cadre, remplir, vider  # noqa: E402
from le_voisinage_dit_il_quel_niveau_est_le_bon import (LES_SURFACES, lancre_du_voisinage,  # noqa: E402
                                                        les_voisins, servir_plusieurs)

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_257_A_PUBLIE = LES_MESURES / "la_spire_produite_se_lit_elle_dans_le_treillis.json"
CE_QUE_261_A_PUBLIE = LES_MESURES / "la_marche_corrige_t_elle_la_spire_produite.json"
CE_QUE_265_A_PUBLIE = LES_MESURES / "le_voisinage_dit_il_quel_niveau_est_le_bon.json"
CE_QUE_270_A_PUBLIE = LES_MESURES / "lancre_du_voisinage_tient_elle_sur_des_blocs_reguliers.json"
LES_PAS = LE_DOSSIER / "les_pas"
LA_SPIRE_CORRIGEE = LE_CACHE / f"transfert_suivante_corrige_265_{LE_SEGMENT}_{LA_PREDICTION}_{LE_COTE}.npy"
LES_COMPTES = ("les_points_corriges", "les_rates_rendus_justes", "les_justes_rendus_rates")


# ── LES PAS, UNE FOIS POUR LE SEGMENT ──────────────────────────────────────────────────────────────────────────────

def les_pas_dun_bloc(ouvrir, by: int, bx: int, est: bool, sud: bool, cote: int = LE_BLOC, combien: int = LES_RANGEES,
                     retenir=un_chunk_retenu) -> dict:
    """Les pas de toutes les coutures qui PARTENT d'un chunk du bloc : celles du dedans, et, si le voisin est rendu, celles
    qui passent à l'est et au sud. Les coutures de l'ouest et du nord partent du voisin, qui les porte.

    ⚠⚠ Les fenêtres et les pas sont ceux de `les_pas_de_fenetre`, expression pour expression : un pas ne dépend que des deux
    chunks de sa couture, et c'est ce qui permet de le calculer une fois. La batterie le vérifie contre `les_pas_de_fenetre`.
    """
    coupes = les_rangees_a_lire(LE_COTE_DU_CHUNK, combien)
    a_lire = [(r, c) for r in range(by, by + cote) for c in range(bx, bx + cote)]
    a_lire += [(r, bx + cote) for r in range(by, by + cote)] if est else []
    a_lire += [(by + cote, c) for c in range(bx, bx + cote)] if sud else []
    fen, refus = {}, {}
    for r, c in a_lire:
        b, pourquoi, _ = retenir(ouvrir, r, c)
        if b is None:
            refus[pourquoi] = refus.get(pourquoi, 0) + 1
            continue
        b = np.asarray(b, dtype=float)
        fen[(r, c)] = ({int(k): les_fenetres(b[:, int(k), :]) for k in coupes},
                       {int(k): les_fenetres(b[:, :, int(k)]) for k in coupes})
    h, v = {}, {}
    for r in range(by, by + cote):
        for c in range(bx, bx + cote):
            if (r, c) not in fen:
                continue
            fr, fc = fen[(r, c)]
            for sens, voisin, mien, d in (("h", (r, c + 1), fr, h), ("v", (r + 1, c), fc, v)):
                if voisin not in fen:
                    continue
                autre = fen[voisin][0 if sens == "h" else 1]
                lus = [la_somme_des_pas(mien[k], autre[k]) for k in coupes]
                lus = [x for x in lus if x is not None]
                if len(lus) < 2:
                    continue
                d[f"{r}_{c}"] = [float(np.mean(lus)), float(np.mean(lus[0::2]) - np.mean(lus[1::2])), len(lus)]
    return {"la_rangee": by, "la_colonne": bx, "est": bool(est), "sud": bool(sud), "h": h, "v": v,
            "les_chunks_retenus": sum(1 for (r, c) in fen if by <= r < by + cote and bx <= c < bx + cote),
            "les_refus": refus}


def la_marche_assemblee(tables: dict, blocs: list[tuple[int, int]], y0: int, x0: int, cote: int,
                        bloc: int = LE_BLOC) -> dict:
    """La marche de `265` sur le carré de côté `cote` en (y0, x0), faite des pas dont les deux chunks sont dans `blocs`.

    ⚠ Les pas sont remis dans l'ordre où `les_pas_de_fenetre` les rangeait, rangée puis colonne : les moindres carrés les
    reçoivent dans le même ordre, donc rendent les mêmes nombres.
    """
    permis = set(blocs)
    dans = lambda r, c: (r // bloc * bloc, c // bloc * bloc) in permis  # noqa: E731
    h, v = {}, {}
    for r in range(y0, y0 + cote):
        for c in range(x0, x0 + cote):
            if not dans(r, c):
                continue
            t = tables[(r // bloc * bloc, c // bloc * bloc)]
            for sens, voisin, d in (("h", (r, c + 1), h), ("v", (r + 1, c), v)):
                x = t[sens].get(f"{r}_{c}")
                if x is not None and dans(*voisin):
                    d.setdefault(r, {})[c] = tuple(x)
    return la_marche_du_bloc(h, v, y0, x0, cote)


def le_fichier_des_pas(surface: str, by: int, bx: int) -> Path:
    return LES_PAS / surface / f"bloc_{by}_{bx}.json"


def la_pile_de_bord(dossier: Path, cote_est: bool) -> np.ndarray:
    """La seule rangée ou colonne de chunks d'une pile voisine que les coutures de l'est ou du sud touchent."""
    p = lire_la_pile(dossier)
    return np.ascontiguousarray(p[:, :, :LE_COTE_DU_CHUNK] if cote_est else p[:, :LE_COTE_DU_CHUNK, :])


def une_table(tache: tuple) -> str:
    """Une tâche du calcul des pas, pour un processus : `(surface, by, bx, est, sud)`."""
    s, by, bx, est, sud = tache
    piles = {(by, bx): lire_la_pile(LE_DOSSIER / s / f"bloc_{by}_{bx}")}
    if est:
        piles[(by, bx + LE_BLOC)] = la_pile_de_bord(LE_DOSSIER / s / f"bloc_{by}_{bx + LE_BLOC}", True)
    if sud:
        piles[(by + LE_BLOC, bx)] = la_pile_de_bord(LE_DOSSIER / s / f"bloc_{by + LE_BLOC}_{bx}", False)
    t = les_pas_dun_bloc(servir_plusieurs(piles), by, bx, est, sud)
    f = le_fichier_des_pas(s, by, bx)
    f.parent.mkdir(parents=True, exist_ok=True)
    tmp = f.with_suffix(".tmp")
    tmp.write_text(json.dumps(t))
    tmp.replace(f)
    return f"{s} ({by}, {bx})"


def les_taches_des_pas(candidats: set, rendus: dict, final: bool, surfaces: tuple = LES_SURFACES) -> list[tuple]:
    """Les tables à faire ou à refaire. Hors du passage final, un bloc attend que ses voisins de l'est et du sud soient
    rendus ; au passage final, un voisin qui ne s'est pas rendu est laissé, et le bloc est fait sans lui.

    ⚠ Une table faite sans son voisin est refaite quand il devient rendu : elle manquerait les coutures qui le relient.
    """
    out = []
    for s in surfaces:
        for by, bx in sorted(candidats):
            if not rendus.get((s, by, bx)):
                continue
            besoin = {"est": (by, bx + LE_BLOC), "sud": (by + LE_BLOC, bx)}
            dispo = {k: (b in candidats and bool(rendus.get((s, *b)))) for k, b in besoin.items()}
            if not final and any(b in candidats and not rendus.get((s, *b)) for b in besoin.values()):
                continue
            f = le_fichier_des_pas(s, by, bx)
            if f.is_file():
                t = json.loads(f.read_text())
                if t["est"] == dispo["est"] and t["sud"] == dispo["sud"]:
                    continue
            out.append((s, by, bx, dispo["est"], dispo["sud"]))
    return out


def les_rendus_sur_le_disque(candidats: set, surfaces: tuple = LES_SURFACES) -> dict:
    return {(s, by, bx): la_pile_est_complete(LE_DOSSIER / s / f"bloc_{by}_{bx}")
            for s in surfaces for by, bx in candidats}


def calculer_les_pas(candidats: set, ouvriers: int, final: bool, surfaces: tuple = LES_SURFACES) -> dict:
    taches = les_taches_des_pas(candidats, les_rendus_sur_le_disque(candidats, surfaces), final, surfaces)
    debut = time.monotonic()
    print(f"les pas : {len(taches)} tables à faire", flush=True)
    with ProcessPoolExecutor(max_workers=int(ouvriers)) as pool:
        for k, nom in enumerate(pool.map(une_table, taches), 1):
            print(f"  table {k}/{len(taches)} : {nom}, {round(time.monotonic() - debut)} s", flush=True)
    return {"les_tables_faites": len(taches), "les_secondes": round(time.monotonic() - debut, 1)}


def les_besoins(taches: list[tuple]) -> dict:
    """Les chunks du volume que chaque rendu `(surface, by, bx)` lit, d'après sa surface."""
    maillages = {s: lire_tifxyz(LE_DOSSIER / s / "maillage") for s in {t[0] for t in taches}}
    return {t: les_chunks_dun_cadre(maillages[t[0]][0], maillages[t[0]][2], le_cadre(t[1], t[2], LE_BLOC)) for t in taches}


LES_PILES_DU_CONTROLE = tuple((s, by, bx) for s in LES_SURFACES for by, bx in ((16, 176), (160, 144), (160, 160), (352, 128)))


def le_controle_du_miroir(ouvriers: int = 3, taches: tuple = LES_PILES_DU_CONTROLE) -> dict:
    """Des piles déjà rendues à distance, rendues à nouveau depuis le miroir, comparées voxel pour voxel.

    ⚠⚠ C'est ce qui autorise le miroir : un chunk que l'estimation oublie se lit comme du vide, sans erreur, et seule cette
    comparaison le verrait. Les piles comparées sont celles des deux blocs choisis et de deux blocs réguliers, sur les deux
    surfaces, fixées ici avant tout rendu depuis le miroir.
    """
    import tifffile

    taches = list(taches)
    rempli = remplir(set().union(*les_besoins(taches).values()))
    temoin = LE_DOSSIER / "le_miroir_controle"

    def un(t):
        s, by, bx = t
        ref, neuf = LE_DOSSIER / s / f"bloc_{by}_{bx}", temoin / f"{s}_{by}_{bx}"
        if not la_pile_est_complete(ref):
            return t, {"comparee": False, "la_raison": "pas de pile rendue à distance"}
        r = rendre(LE_DOSSIER / s / "maillage", neuf, le_cadre(by, bx, LE_BLOC), miroir=LE_MIROIR)
        if not r["rendue"]:
            return t, {"comparee": False, "la_raison": "le rendu depuis le miroir échoue"}
        diff = sum(int((tifffile.imread(x) != tifffile.imread(y)).sum())
                   for x, y in zip(sorted(ref.glob("*.tif")), sorted(neuf.glob("*.tif"))))
        return t, {"comparee": True, "les_voxels_differents": diff, "les_secondes": r.get("les_secondes")}

    with ThreadPoolExecutor(max_workers=int(ouvriers)) as pool:
        res = dict(pool.map(un, taches))
    import shutil
    shutil.rmtree(temoin, ignore_errors=True)
    return {"le_remplissage": rempli, "les_piles": {f"{s}_{by}_{bx}": r for (s, by, bx), r in res.items()},
            "identiques": all(r.get("comparee") and r["les_voxels_differents"] == 0 for r in res.values())}


def tout_rendre(candidats: set, ouvriers: int, surfaces: tuple = LES_SURFACES) -> dict:
    """Les deux surfaces sur tous les blocs candidats, depuis le miroir, rangée de blocs par rangée de blocs ; une pile
    complète n'est pas refaite.

    Le miroir ne garde que les chunks de la rangée en cours et de la suivante, que l'on télécharge pendant que la première
    se rend : tout le segment tiendrait des centaines de gigaoctets.
    """
    a_faire = [(s, by, bx) for (by, bx) in sorted(candidats) for s in surfaces
               if not la_pile_est_complete(LE_DOSSIER / s / f"bloc_{by}_{bx}")]
    besoin = les_besoins(a_faire)
    rangees = sorted({t[1] for t in a_faire})
    de = lambda r: set().union(*[besoin[t] for t in a_faire if t[1] == r]) if r is not None else set()  # noqa: E731
    debut, res, remplis = time.monotonic(), {}, []

    def un(t):
        s, by, bx = t
        r = rendre(LE_DOSSIER / s / "maillage", LE_DOSSIER / s / f"bloc_{by}_{bx}", le_cadre(by, bx, LE_BLOC),
                   miroir=LE_MIROIR)
        print(f"  rendu {s} ({by}, {bx}) : {r['rendue']}, {r.get('les_secondes')} s, "
              f"{round(time.monotonic() - debut)} s depuis le début", flush=True)
        return t, r

    # ⚠ Le téléchargement de la rangée suivante et le vidage courent ensemble sans se gêner : l'un n'écrit que des chunks
    # que l'autre garde.
    with ThreadPoolExecutor(max_workers=1) as avance:
        futur = avance.submit(remplir, de(rangees[0])) if rangees else None
        for i, r in enumerate(rangees):
            remplis.append(futur.result())
            print(f"rangée {r} ({i + 1}/{len(rangees)}) : {remplis[-1]}", flush=True)
            garde = de(rangees[i + 1] if i + 1 < len(rangees) else None)
            futur = avance.submit(remplir, garde)
            with ThreadPoolExecutor(max_workers=int(ouvriers)) as pool:
                res.update(pool.map(un, [t for t in a_faire if t[1] == r]))
            vider(garde)
        if futur is not None:
            futur.result()
    return {"les_piles_a_rendre": len(a_faire), "rendues": sum(1 for r in res.values() if r["rendue"]),
            "echouees": sorted(f"{s}_{by}_{bx}" for (s, by, bx), r in res.items() if not r["rendue"]),
            "les_octets_telecharges": int(sum(x["les_octets"] for x in remplis)),
            "les_secondes": round(time.monotonic() - debut, 1)}


# ── LA DÉCISION, BLOC PAR BLOC ─────────────────────────────────────────────────────────────────────────────────────

def la_decision_du_bloc(tau0: np.ndarray, err: np.ndarray, prod: np.ndarray, red: np.ndarray, by: int, bx: int,
                        glissade: float, lancre=lancre_du_voisinage) -> tuple[dict, np.ndarray, np.ndarray] | None:
    """La décision de `265` sur un voisinage : son bilan, les points corrigés et leur nouvelle valeur. None si aucun voisin
    ne se relie au bloc. `lancre` prend l'ancre sur la différence des marches du voisinage."""
    c = LE_BLOC
    diff = prod - red
    ancre = lancre(diff, by - c, bx - c, by, bx)
    if ancre is None:
        return None
    d_b = diff[c:2 * c, c:2 * c] - ancre
    ecart, dedans = la_carte_aux_points(d_b, by, bx, tau0.shape)
    ecart = np.where(dedans, ecart, np.nan)
    dec = la_decision(ecart, le_melange(d_b, glissade))
    tau1 = corriger_decide(tau0, ecart, dec)
    verite = tau0 - err
    bilan = {"lancre_voxels": round(float(ancre), 4), "avant": la_part_juste(tau0, verite, dedans),
             **le_bilan(tau0, tau1, verite, err, dedans, dec)}
    return bilan, dec & dedans, tau1


def un_bloc(by: int, bx: int, candidats: set, tables: dict, rendus: dict, tau0, err, glissade,
            surfaces: tuple = LES_SURFACES, les_voisins_de=les_voisins,
            lancre=lancre_du_voisinage) -> tuple[dict, tuple]:
    """La décision de `265` sur un bloc ; `surfaces` est (la référence, la surface produite), dans cet ordre,
    `les_voisins_de` choisit les blocs voisins que la marche et l'ancre lisent, et `lancre` prend l'ancre."""
    blocs = [(by, bx)] + les_voisins_de(by, bx, candidats)
    for s in surfaces:
        for vy, vx in blocs:
            if not rendus.get((s, vy, vx)) or (s, vy, vx) not in tables:
                return {"la_rangee": by, "la_colonne": bx, "decidable": False,
                        "la_raison": f"{s} ne se rend pas sur ({vy}, {vx})"}, None
    if len(blocs) == 1:
        return {"la_rangee": by, "la_colonne": bx, "decidable": False, "la_raison": "aucun voisin candidat"}, None
    prof = {s: la_marche_assemblee({b: tables[(s, *b)] for b in blocs}, blocs, by - LE_BLOC, bx - LE_BLOC,
                                   3 * LE_BLOC)["la_profondeur"] for s in surfaces}
    lu = la_decision_du_bloc(tau0, err, prof[surfaces[1]], prof[surfaces[0]], by, bx, glissade, lancre)
    if lu is None:
        return {"la_rangee": by, "la_colonne": bx, "decidable": False, "la_raison": "aucun voisin ne se relie au bloc"}, None
    bilan, corriges, tau1 = lu
    return {"la_rangee": by, "la_colonne": bx, "decidable": True, "les_voisins": len(blocs) - 1, **bilan}, (corriges, tau1)


def la_reunion(blocs: list[dict]) -> dict:
    """Les blocs décidés, réunis : la part avant et après sur tous leurs points notés, et les comptes."""
    ok = {f"{b['la_rangee']}_{b['la_colonne']}": b for b in blocs if b.get("decidable")}
    out = {"les_blocs": len(ok), "avant": la_part_reunie(ok, "avant"), "apres": la_part_reunie(ok, "apres"),
           "les_points_notes": sum(b["avant"]["les_points_notes"] for b in ok.values()),
           **{k: sum(b[k] for b in ok.values()) for k in LES_COMPTES}}
    out["le_gain_net"] = out["les_rates_rendus_justes"] - out["les_justes_rendus_rates"]
    sens = lambda b: (b["apres"]["la_part_sur_la_bonne_spire"] or 0) - (b["avant"]["la_part_sur_la_bonne_spire"] or 0)  # noqa: E731
    out["les_blocs_qui_montent"] = sum(1 for b in ok.values() if sens(b) > 0)
    out["les_blocs_qui_descendent"] = sum(1 for b in ok.values() if sens(b) < 0)
    out["les_blocs_immobiles"] = sum(1 for b in ok.values() if sens(b) == 0)
    return out


def les_neuf_publies() -> dict:
    """Les neuf voisinages que `265` et `270` ont publiés, et leurs comptes."""
    out = {}
    for source in (CE_QUE_265_A_PUBLIE, CE_QUE_270_A_PUBLIE):
        for nom, b in json.loads(source.read_text())["les_blocs"].items():
            out[(b["la_rangee"], b["la_colonne"])] = {"nom": nom, **{k: b["lancre_du_voisinage"]["la_decision"][k]
                                                                    for k in LES_COMPTES}}
    return out


def la_reproduction(blocs: list[dict], publies: dict) -> dict:
    par = {(b["la_rangee"], b["la_colonne"]): b for b in blocs}
    lignes = {}
    for cle, p in publies.items():
        b = par.get(cle, {})
        lu = {k: b.get(k) for k in LES_COMPTES}
        lignes[p["nom"]] = {"publie": {k: p[k] for k in LES_COMPTES}, "refait": lu,
                            "reproduit": bool(b.get("decidable")) and lu == {k: p[k] for k in LES_COMPTES}}
    return {"les_voisinages": lignes, "tous": all(x["reproduit"] for x in lignes.values())}


def le_segment(cache: Path = LE_CACHE) -> tuple:
    """Le transfert de `m7`, l'erreur que les deux juges notent, la glissade de `261` et les blocs candidats de `257`."""
    d257 = json.loads(CE_QUE_257_A_PUBLIE.read_text())
    glissade = float(json.loads(CE_QUE_261_A_PUBLIE.read_text())["le_signe"]["lecart_retrouve_voxels"])
    gy, gx = d257["le_treillis"]
    _, valide, _ = lire_tifxyz(telecharger(LE_SEGMENT, cache))
    tau0 = np.load(cache / f"transfert_suivante_{LE_SEGMENT}_{LA_PREDICTION}_{LE_COTE}.npy")
    err = lerreur_jugee(tau0, [np.load(cache / f"verite_{LE_SEGMENT}_{j}_{LE_COTE}.npy") for j in LES_JUGES])
    return tau0, err, glissade, set(les_blocs_candidats(tau0, valide, gy, gx))


def les_tables(candidats: set, rendus: dict, surfaces: tuple = LES_SURFACES) -> dict:
    tables = {}
    for s in surfaces:
        for by, bx in candidats:
            f = le_fichier_des_pas(s, by, bx)
            if rendus[(s, by, bx)] and f.is_file():
                tables[(s, by, bx)] = json.loads(f.read_text())
    return tables


def reproduire_les_neuf(pas_ouvriers: int, cache: Path = LE_CACHE) -> dict:
    """Avant de rendre le segment : les neuf voisinages publiés, par les tables, sur les piles déjà rendues.

    ⚠ Les tables faites ici sans un voisin de l'est ou du sud pas encore rendu seront refaites quand il le sera.
    """
    tau0, err, glissade, candidats = le_segment(cache)
    calculer_les_pas(candidats, pas_ouvriers, final=True)
    rendus = les_rendus_sur_le_disque(candidats)
    tables = les_tables(candidats, rendus)
    publies = les_neuf_publies()
    blocs = [un_bloc(by, bx, candidats, tables, rendus, tau0, err, glissade)[0] for by, bx in sorted(publies)]
    return la_reproduction(blocs, publies)


def mesurer(cache: Path = LE_CACHE, rendre_ouvriers: int = 4, pas_ouvriers: int = 5) -> dict:
    debut = time.monotonic()
    tau0, err, glissade, candidats = le_segment(cache)
    out = {"la_glissade_voxels": glissade, "les_candidats": len(candidats)}
    out["le_controle_du_miroir"] = le_controle_du_miroir()
    out["les_rendus"] = tout_rendre(candidats, rendre_ouvriers) if out["le_controle_du_miroir"]["identiques"] else None
    out["les_pas"] = calculer_les_pas(candidats, pas_ouvriers, final=True)
    rendus = les_rendus_sur_le_disque(candidats)
    tables = les_tables(candidats, rendus)
    blocs, tau1 = [], tau0.copy()
    for by, bx in sorted(candidats):
        b, corr = un_bloc(by, bx, candidats, tables, rendus, tau0, err, glissade)
        blocs.append(b)
        if corr is not None:
            masque, t = corr
            tau1[masque] = t[masque]
    out["les_blocs"] = blocs
    out["la_reproduction"] = la_reproduction(blocs, les_neuf_publies())
    out["decidable"] = out["la_reproduction"]["tous"] and out["le_controle_du_miroir"]["identiques"]
    out["les_non_decides"] = {f"{b['la_rangee']}_{b['la_colonne']}": b["la_raison"] for b in blocs if not b["decidable"]}
    out["les_reunis"] = la_reunion(blocs)
    note = np.isfinite(err)
    out["la_part_des_points_notes_du_segment_dans_les_blocs"] = (
        round(out["les_reunis"]["les_points_notes"] / int(note.sum()), 4) if note.any() else None)
    out["le_segment_entier"] = {"avant": la_part_juste(tau0, tau0 - err, note), "apres": la_part_juste(tau1, tau0 - err, note)}
    np.save(LA_SPIRE_CORRIGEE, tau1)
    out["la_spire_corrigee"] = LA_SPIRE_CORRIGEE.name
    out["les_secondes"] = round(time.monotonic() - debut, 1)
    return out


def le_verdict(r: dict) -> dict:
    if not r.get("decidable"):
        return {"lissue": "indécidable : le miroir ne redonne pas les piles rendues à distance, ou les neuf voisinages "
                          "publiés ne redonnent pas leurs comptes"}
    if r["les_reunis"]["le_gain_net"] > 0:
        return {"lissue": "la procédure améliore la spire produite sur le segment entier"}
    return {"lissue": "la procédure n'améliore pas la spire produite sur le segment entier"}


# ── LA BATTERIE ────────────────────────────────────────────────────────────────────────────────────────────────────

def _une_pile_de_feuilles(ny: int, nx: int, graine: int = 7) -> np.ndarray:
    """Une pile synthétique de `ny` × `nx` chunks : une feuille dont la profondeur ondule, et du bruit."""
    rng = np.random.default_rng(graine)
    h, w = ny * LE_COTE_DU_CHUNK, nx * LE_COTE_DU_CHUNK
    yy, xx = np.mgrid[0:h, 0:w]
    z0 = 54 + 9 * np.sin(xx / 170.0) + 7 * np.cos(yy / 230.0)
    z = np.arange(109)[:, None, None]
    p = 200 * np.exp(-0.5 * ((z - z0[None]) / 3.0) ** 2) + 20 * np.exp(-0.5 * ((z - z0[None] - 30) / 3.0) ** 2)
    return np.clip(p + rng.normal(0, 6, p.shape), 0, 255).astype(np.uint8)


def _garder_tout(ouvrir, r, c):
    b, pourquoi = ouvrir(r, c)
    return (None, pourquoi, 0) if b is None else (b, None, 0)


def verifier() -> int:
    import le_pas_de_fenetre_en_fenetre_voit_il_la_rampe as lpf
    from le_voisinage_dit_il_quel_niveau_est_le_bon import les_quatre

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

    # Quatre blocs de deux chunks de côté : les pas calculés bloc par bloc, puis assemblés, contre les_pas_de_fenetre.
    cb, combien = 2, 4
    pile = _une_pile_de_feuilles(2 * cb, 2 * cb)
    blocs = [(0, 0), (0, cb), (cb, 0), (cb, cb)]
    decoupe = {b: pile[:, b[0] * LE_COTE_DU_CHUNK:(b[0] + cb) * LE_COTE_DU_CHUNK,
                       b[1] * LE_COTE_DU_CHUNK:(b[1] + cb) * LE_COTE_DU_CHUNK] for b in blocs}
    garde = lpf.un_chunk_retenu
    lpf.un_chunk_retenu = _garder_tout
    try:
        def les_deux(permis):
            ref = lpf.les_pas_de_fenetre(servir_plusieurs({b: decoupe[b] for b in permis}, cote=cb), 0, 0, 2 * cb,
                                         combien=combien)
            # ⚠ Les tables sont faites avec TOUS les blocs rendus, comme sur le segment : c'est l'assemblage seul qui doit
            # écarter les coutures vers un bloc absent du voisinage.
            tables = {b: les_pas_dun_bloc(servir_plusieurs(decoupe, cote=cb), b[0], b[1], (b[0], b[1] + cb) in blocs,
                                          (b[0] + cb, b[1]) in blocs, cote=cb, combien=combien, retenir=_garder_tout)
                      for b in blocs}
            return ref, tables

        def pareil(permis):
            ref, tables = les_deux(permis)
            m_ref = la_marche_du_bloc(ref["h"], ref["v"], 0, 0, 2 * cb)
            m_moi = la_marche_assemblee({b: tables[b] for b in permis}, permis, 0, 0, 2 * cb, bloc=cb)
            a, b = m_ref["la_profondeur"], m_moi["la_profondeur"]
            return (m_ref["les_coutures"] == m_moi["les_coutures"] > 0 and np.array_equal(np.isnan(a), np.isnan(b))
                    and np.array_equal(a[np.isfinite(a)], b[np.isfinite(b)]))

        v("★★★★ les pas faits bloc par bloc et assemblés redonnent la marche de les_pas_de_fenetre, au bit près",
          lambda: pareil(blocs))
        v("★★★★ sans le bloc du coin, ils redonnent encore la marche : aucune couture ne passe vers un bloc absent",
          lambda: pareil([(0, 0), (0, cb), (cb, 0)]))
        def les_colonnes_de_depart(est: bool) -> set[int]:
            t = les_pas_dun_bloc(servir_plusieurs({q: decoupe[q] for q in blocs}, cote=cb), 0, 0, est, False, cote=cb,
                                 combien=combien, retenir=_garder_tout)
            return {int(k.split("_")[1]) for k in t["h"]}

        v("★★★ une table porte la couture de l'est quand son voisin est rendu, et aucune sans lui",
          lambda: cb - 1 in les_colonnes_de_depart(True) and cb - 1 not in les_colonnes_de_depart(False))
    finally:
        lpf.un_chunk_retenu = garde

    # La décision : celle de `les_quatre`, qui est la procédure de `265`.
    rng = np.random.default_rng(3)
    by, bx = 16, 16
    tau0 = rng.normal(0, 3, (40, 40))
    err = np.where(rng.random((40, 40)) < 0.3, 69.0, 0.0) + rng.normal(0, 2, (40, 40))
    red = rng.normal(0, 2, (48, 48))
    prod = red + rng.normal(0, 2, (48, 48))
    prod[16:24, 16:32] += 69.0
    d = la_decision_du_bloc(tau0, err, prod, red, by, bx, 69.458)
    diff = prod - red
    ref = les_quatre(tau0, err, tau0 - err, by, bx, diff[16:32, 16:32], lancre_du_voisinage(diff, 0, 0, by, bx), 69.458)
    v("★★★★ la décision du bloc est celle de 265, compte pour compte",
      lambda: d is not None and all(d[0][k] == ref["la_decision"][k] for k in LES_COMPTES)
      and d[0]["apres"] == ref["la_decision"]["apres"] and d[0]["les_points_corriges"] > 0, str(d and d[0]))
    v("★★★ les points corrigés sont dans le bloc, et seuls eux changent",
      lambda: d is not None and np.array_equal(np.nan_to_num(d[2][~d[1]]), np.nan_to_num(tau0[~d[1]])))

    # La réunion et les issues.
    b1 = {"la_rangee": 0, "la_colonne": 0, "decidable": True, "avant": {"les_points_notes": 10, "la_part_sur_la_bonne_spire": 0.5},
          "apres": {"les_points_notes": 10, "la_part_sur_la_bonne_spire": 0.8}, "les_points_corriges": 4,
          "les_rates_rendus_justes": 3, "les_justes_rendus_rates": 0}
    b2 = {"la_rangee": 0, "la_colonne": 16, "decidable": True, "avant": {"les_points_notes": 30, "la_part_sur_la_bonne_spire": 1.0},
          "apres": {"les_points_notes": 30, "la_part_sur_la_bonne_spire": 0.9}, "les_points_corriges": 3,
          "les_rates_rendus_justes": 0, "les_justes_rendus_rates": 3}
    b3 = {"la_rangee": 16, "la_colonne": 0, "decidable": False, "la_raison": "x"}
    g = la_reunion([b1, b2, b3])
    v("★★★★ la réunion ne prend que les blocs décidés, pèse la part par les points et fait le gain net",
      g["les_blocs"] == 2 and g["le_gain_net"] == 0 and g["avant"] == 0.875 and g["apres"] == 0.875
      and g["les_blocs_qui_montent"] == 1 and g["les_blocs_qui_descendent"] == 1, str(g))
    r_ok = {"decidable": True, "les_reunis": {"le_gain_net": 1}}
    v("★★★★ les issues : améliore si le gain net est positif, sinon non, indécidable si non reproduit",
      "améliore la" in le_verdict(r_ok)["lissue"]
      and "n'améliore pas" in le_verdict({"decidable": True, "les_reunis": {"le_gain_net": 0}})["lissue"]
      and "indécidable" in le_verdict({"decidable": False})["lissue"])
    pub = {(0, 0): {"nom": "a", "les_points_corriges": 4, "les_rates_rendus_justes": 3, "les_justes_rendus_rates": 0}}
    v("★★★ la reproduction exige les comptes publiés, et un bloc non décidé ne reproduit rien",
      la_reproduction([b1], pub)["tous"] and not la_reproduction([b3 | {"la_rangee": 0, "la_colonne": 0}], pub)["tous"])

    for e in echecs:
        print(f"  ÉCHEC {e}")
    print(f"{Path(__file__).name}   {'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--rendre", type=int, metavar="N", help="rendre les deux surfaces sur tous les blocs, N à la fois")
    p.add_argument("--pas", type=int, metavar="N", help="faire les tables des pas déjà possibles, N processus")
    p.add_argument("--les-neuf", type=int, metavar="N",
                   help="refaire les neuf voisinages publiés par les tables, sur les piles déjà rendues, N processus")
    p.add_argument("--json", type=Path)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if a.les_neuf:
        print(json.dumps(reproduire_les_neuf(a.les_neuf), indent=1, ensure_ascii=False))
        return 0
    if a.rendre or a.pas:
        candidats = le_segment()[3]
        if a.rendre:
            c = le_controle_du_miroir()
            print(json.dumps(c, ensure_ascii=False), flush=True)
            if not c["identiques"]:
                return 1
            print(json.dumps(tout_rendre(candidats, a.rendre), ensure_ascii=False))
        if a.pas:
            print(json.dumps(calculer_les_pas(candidats, a.pas, final=False), ensure_ascii=False))
        return 0
    if a.json:
        r = mesurer()
        r["le_verdict"] = le_verdict(r)
        a.json.write_text(json.dumps(r, indent=1, ensure_ascii=False))
        print(json.dumps({"la_reproduction": r["la_reproduction"]["tous"], "les_reunis": r["les_reunis"],
                          "le_verdict": r["le_verdict"]}, indent=1, ensure_ascii=False))
        return 0
    p.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
