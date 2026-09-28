"""Une marche qui s'étend au nord et au sud rend-elle à la bande `w028-037` le gain que la procédure y perd ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UNE SEULE PILE DE CETTE TRANCHE NE SOIT RENDUE. Ce qui était vu avant d'écrire : tout ce que
`248` et `257` à `294` publient. Sur la bande, la procédure n'améliore pas le premier saut (`281`), et chaque bloc de sa tranche
n'a de voisins qu'à l'est et à l'ouest. Sur le segment `20230702185753`, ne lui laisser que ces deux voisins fait tomber son gain
de 122 à 5 (`291`), et des voisins plus lointains sur la seule rangée le font tomber à −307 (`294`). Ce qui manque à la bande
serait une marche qui s'étende dans les deux directions.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P95`. La tranche de `248` ne fait que 37 chunks de haut : une seule rangée de blocs y
est candidate. Une tranche plus haute donne à une rangée de blocs des voisins au nord et au sud. Le quadrillage des chunks ne se
réaligne pas sur celui de `281`, donc tout est rendu à neuf. Par décision de l'auteur, l'expérience est réduite : trois rangées de
blocs, sur 30 colonnes de blocs au milieu de la bande.

## Ce qui est fait, déclaré avant tout rendu

- La tranche va des rangées 0,40 à 0,60 de la bande, au lieu de 0,45 à 0,55. La chaîne, les normales et les couches sont celles de
  `248`, calculées sur cette tranche ; son premier saut est la surface corrigée, la bande réduite est la référence.
- Les blocs rendus sont les blocs candidats des rangées de blocs 16, 32 et 48, sur les 30 colonnes de blocs du milieu de la bande.
  Les blocs décidés sont ceux de la rangée 32 ; les deux autres rangées ne servent que de voisins.
- La décision est celle de `275`, avec tous les voisins candidats. Sur les mêmes blocs, elle est refaite avec les seuls voisins est
  et ouest, comme la tranche de `281` les lui laissait : c'est la comparaison qui compte.
- Le juge est la première couche de la bande, et il ne sert qu'à noter. Le test est celui de `290`.

⚠ Les contrôles rendent la mesure décidable : la chaîne, refaite deux fois, rend deux fois le même premier saut ; la règle du
treillis redonne celui de `257` ; le bloc de la rangée 32 qui porte le plus de points notés est rendu à distance sur les deux
surfaces, puis depuis le miroir, et les deux piles doivent être identiques voxel pour voxel ; il ne manque aucune pile, et la
lecture ne connaît aucune panne.

## Les issues, exclusives, sur les blocs de la rangée 32 qui ont leurs quatre voisins

- le gain net sur les points est positif, et le test du signe passe sous 0,05 sur les points : une marche dans les deux
  directions rend à la bande un gain qui se distingue du hasard ;
- sinon : elle ne le lui rend pas.

⚠ Rapporté à côté : les mêmes blocs avec les seuls voisins est et ouest ; le test par blocs ; les blocs de la rangée 32 qui n'ont
pas leurs quatre voisins.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : la bande entière ; le deuxième saut ; les autres colonnes.

Usage :
    uv run python src/nappe/une_marche_dans_les_deux_directions_rend_elle_son_gain_a_la_bande.py --verifier
    uv run python src/nappe/une_marche_dans_les_deux_directions_rend_elle_son_gain_a_la_bande.py --preparer
    uv run python src/nappe/une_marche_dans_les_deux_directions_rend_elle_son_gain_a_la_bande.py --controler 2
    uv run python src/nappe/une_marche_dans_les_deux_directions_rend_elle_son_gain_a_la_bande.py --etalonner A1
    uv run python src/nappe/une_marche_dans_les_deux_directions_rend_elle_son_gain_a_la_bande.py --rendre 2
    uv run python src/nappe/une_marche_dans_les_deux_directions_rend_elle_son_gain_a_la_bande.py --pas 3
    uv run python src/nappe/une_marche_dans_les_deux_directions_rend_elle_son_gain_a_la_bande.py \\
        --json docs/mesures/une_marche_dans_les_deux_directions_rend_elle_son_gain_a_la_bande.json
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

from la_procedure_sans_juge_corrige_t_elle_le_deuxieme_saut import les_blocs_notes  # noqa: E402
from la_procedure_sans_juge_tient_elle_sur_la_bande import (CE_QUE_257_A_PUBLIE, LE_CACHE, LE_SIGNE,  # noqa: E402
                                                            LE_SUFFIXE, LES_SURFACES_DE_LA_BANDE, la_bande,
                                                            le_treillis_de)
from la_procedure_sans_juge_tient_elle_sur_le_segment_entier import (CE_QUE_261_A_PUBLIE, calculer_les_pas,  # noqa: E402
                                                                     la_reunion, le_controle_du_miroir,
                                                                     les_besoins, les_rendus_sur_le_disque,
                                                                     les_tables, les_voxels_differents,
                                                                     tout_rendre, un_bloc)
from le_miroir_du_volume import LE_MIROIR, remplir  # noqa: E402
from la_procedure_tient_elle_sur_le_segment_avec_ses_seuls_voisins_est_et_ouest import (  # noqa: E402
    le_test, les_voisins_est_ouest)
from la_spire_produite_se_lit_elle_dans_le_treillis import (LA_MAILLE, LE_BLOC, LE_DOSSIER,  # noqa: E402
                                                            ecrire_tifxyz, la_pile_est_complete, le_cadre,
                                                            le_maillage_produit, le_maillage_reduit,
                                                            les_blocs_candidats, rendre)
from la_spire_voisine_est_elle_a_un_pas import LE_SEGMENT, lire_tifxyz, telecharger  # noqa: E402
from le_transfert_enchaine_tient_il_les_spires import LES_SAUTS, enchainer  # noqa: E402
from le_voisinage_dit_il_quel_niveau_est_le_bon import les_voisins  # noqa: E402

LA_TRANCHE_HAUTE = (0.40, 0.60)
LES_RANGEES_DE_BLOCS = (16, 32, 48)
LA_RANGEE_DECIDEE = 32
LES_COLONNES = 30
LES_SURFACES_HAUTES = ("la_bande_haute_reduite", "la_spire_produite_de_la_bande_haute")   # la référence, la produite
LE_PREMIER_SAUT_HAUT = LE_CACHE / f"premier_saut_de_la_bande_haute_{LE_SUFFIXE}.npy"
LA_COUCHE_HAUTE = LE_CACHE / f"couche_un_de_la_bande_haute_{LE_SUFFIXE}.npy"
LE_PLAN = LE_DOSSIER / "la_bande_haute_plan.json"
LE_CONTROLE = LE_DOSSIER / "la_bande_haute_controle.json"
LE_ETALONNAGE = LE_DOSSIER / "la_bande_haute_etalon"
LE_RENDU = LE_DOSSIER / "la_bande_haute_rendu.json"   # et, de surveiller_lunite.sh, un `*_cgroup.json` par lancement


def les_colonnes_du_milieu(colonnes: list[int], combien: int = LES_COLONNES) -> list[int]:
    """Les `combien` colonnes de blocs du milieu, prises dans l'ordre, sans choisir sur ce qu'elles contiennent."""
    colonnes = sorted(colonnes)
    debut = max(0, (len(colonnes) - combien) // 2)
    return colonnes[debut:debut + combien]


def les_blocs_a_rendre(candidats: set, rangees=LES_RANGEES_DE_BLOCS, combien: int = LES_COLONNES) -> set:
    """Les blocs candidats des rangées choisies, sur les colonnes du milieu de la rangée décidée."""
    colonnes = set(les_colonnes_du_milieu([bx for by, bx in candidats if by == LA_RANGEE_DECIDEE], combien))
    return {(by, bx) for by, bx in candidats if by in rangees and bx in colonnes}


def les_blocs_decides(a_rendre: set) -> list[tuple[int, int]]:
    return sorted(b for b in a_rendre if b[0] == LA_RANGEE_DECIDEE)


def la_taille_mediane_dune_pile(surfaces=LES_SURFACES_DE_LA_BANDE) -> int | None:
    """La taille médiane, en octets, d'une pile complète de la bande déjà rendue par `281`, mesurée sur le disque."""
    tailles = sorted(sum(f.stat().st_size for f in d.glob("*.tif")) for s in surfaces
                     for d in (LE_DOSSIER / s).glob("bloc_*") if d.is_dir() and la_pile_est_complete(d))
    return tailles[len(tailles) // 2] if tailles else None


def a_quatre_voisins(by: int, bx: int, a_rendre: set) -> bool:
    return len(les_voisins(by, bx, a_rendre)) == 4


def le_verdict(r: dict) -> dict:
    if not r.get("decidable"):
        return {"lissue": "indécidable : la chaîne n'est pas stable, le treillis ne redonne pas 257, le miroir ne redonne pas "
                          "les piles rendues à distance, il manque une pile, ou la lecture est tombée en panne"}
    p = r["les_blocs_a_quatre_voisins"]["avec_tous_leurs_voisins"]["le_test"]["sur_les_points"]
    if p["le_gain_net"] > 0 and p["sous_le_seuil"]:
        return {"lissue": "une marche dans les deux directions rend à la bande un gain qui se distingue du hasard"}
    return {"lissue": "une marche dans les deux directions ne rend pas à la bande un gain qui se distingue du hasard"}


# ── LES ÉTAPES ─────────────────────────────────────────────────────────────────────────────────────────────────────

def preparer(cache: Path = LE_CACHE) -> dict:
    """La chaîne de `248` sur la tranche haute, les deux surfaces à rendre, le juge, les blocs et ce que le rendu coûtera."""
    b = la_bande(cache, rangees=LA_TRANCHE_HAUTE)
    if isinstance(b, str):
        return {"decidable": False, "la_raison": b}
    p, n, gi, gj, grille = b["p"], b["n"], b["gi"], b["gj"], b["sur_la_grille"]
    tau0 = grille(np.einsum("ij,ij->i", enchainer(p, n, LE_SIGNE, 1, b["lire_rayon"], grille, gi, gj, True)[0]["q"] - p, n))
    tau0_bis = grille(np.einsum("ij,ij->i", enchainer(p, n, LE_SIGNE, 1, b["lire_rayon"], grille, gi, gj, True)[0]["q"] - p,
                                n))
    couche = grille(b["verite"][0])
    pas_de_grille = int(round(b["esp"]))
    gy, gx = le_treillis_de(b["valide"].shape, pas_de_grille)
    ref5753, _, esp5753 = lire_tifxyz(telecharger(LE_SEGMENT, cache))
    treillis_257 = json.loads(CE_QUE_257_A_PUBLIE.read_text())["le_treillis"]
    candidats = set(les_blocs_candidats(tau0, b["valide"], gy, gx, pas_de_grille=pas_de_grille))
    a_rendre = les_blocs_a_rendre(candidats)
    decides = les_blocs_decides(a_rendre)
    notes = les_blocs_notes(tau0 - couche, set(decides))
    scale = 1.0 / (b["esp"] * LA_MAILLE)
    pr, vr = le_maillage_reduit(b["ref"], b["valide"])
    pp, vp = le_maillage_produit(b["ref"], b["valide"], tau0)
    ecrire_tifxyz(LE_DOSSIER / LES_SURFACES_HAUTES[0] / "maillage", pr, vr, scale, LES_SURFACES_HAUTES[0])
    ecrire_tifxyz(LE_DOSSIER / LES_SURFACES_HAUTES[1] / "maillage", pp, vp, scale, LES_SURFACES_HAUTES[1])
    np.save(LE_PREMIER_SAUT_HAUT, tau0)
    np.save(LA_COUCHE_HAUTE, couche)
    taches = [(s, by, bx) for (by, bx) in sorted(a_rendre) for s in LES_SURFACES_HAUTES]
    besoins = les_besoins(taches)
    par_rangee = {str(r): len(set().union(*[besoins[t] for t in taches if t[1] == r])) for r in LES_RANGEES_DE_BLOCS
                  if any(t[1] == r for t in taches)}
    pile = la_taille_mediane_dune_pile()
    controle = max(notes, key=lambda k: (notes[k], k)) if notes else None
    plan = {"la_tranche": list(LA_TRANCHE_HAUTE), "la_chaine_est_stable": bool(np.array_equal(tau0, tau0_bis, equal_nan=True)),
            "le_treillis": {"la_bande": [gy, gx], "le_pas_de_grille_voxels": pas_de_grille,
                            "la_grille_de_la_tranche": list(b["valide"].shape),
                            "le_segment_20230702185753": list(le_treillis_de(ref5753.shape[:2], int(round(esp5753)))),
                            "celui_de_257": treillis_257},
            "les_rangees_candidates": sorted({by for by, _ in candidats}),
            "les_blocs_a_rendre": sorted(f"{by}_{bx}" for by, bx in a_rendre),
            "les_blocs_decides": [f"{by}_{bx}" for by, bx in decides],
            "les_blocs_a_quatre_voisins": [f"{by}_{bx}" for by, bx in decides if a_quatre_voisins(by, bx, a_rendre)],
            "les_points_notes_par_bloc_decide": {f"{k[0]}_{k[1]}": v for k, v in sorted(notes.items())},
            "le_bloc_du_controle": None if controle is None else f"{controle[0]}_{controle[1]}",
            "le_cout": {"les_piles": len(taches), "la_pile_mediane_de_281_octets": pile,
                        "le_disque_go": None if pile is None else round(len(taches) * pile / 1e9, 1),
                        "les_chunks_par_rangee": par_rangee, "les_chunks": sum(par_rangee.values())},
            "la_lecture": {"combien_de_pannes": len(b["stats"]["pannes"])}}
    plan["le_treillis"]["reproduit"] = plan["le_treillis"]["le_segment_20230702185753"] == treillis_257
    LE_PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=1))
    return plan


def lire_le_plan() -> dict:
    d = json.loads(LE_PLAN.read_text())
    bloc = lambda s: tuple(int(x) for x in s.split("_"))  # noqa: E731
    return {"a_rendre": {bloc(k) for k in d["les_blocs_a_rendre"]}, "decides": [bloc(k) for k in d["les_blocs_decides"]],
            "quatre": [bloc(k) for k in d["les_blocs_a_quatre_voisins"]],
            "controle": bloc(d["le_bloc_du_controle"]) if d["le_bloc_du_controle"] else None, "brut": d}


def le_telechargement_projete(rempli: dict, chunks: int) -> dict:
    """Ce que le rendu de toutes les rangées téléchargera, au poids par chunk que le contrôle vient de mesurer."""
    lus = rempli["telecharges"] - rempli["absents_de_la_source"]
    par_chunk = rempli["les_octets"] / lus if lus else None
    return {"les_octets_par_chunk": None if par_chunk is None else round(par_chunk),
            "le_debit_mo_s": rempli.get("le_debit_mo_s"),
            "les_go": None if par_chunk is None else round(chunks * par_chunk / 1e9, 1)}


def controler(ouvriers: int = 2) -> dict:
    """Les piles du bloc de contrôle, rendues à distance puis depuis le miroir, comparées voxel pour voxel."""
    plan = lire_le_plan()
    by, bx = plan["controle"]
    taches = [(s, by, bx) for s in LES_SURFACES_HAUTES]

    def a_distance(t_):
        s, y, x = t_
        return t_, rendre(LE_DOSSIER / s / "maillage", LE_DOSSIER / s / f"bloc_{y}_{x}", le_cadre(y, x, LE_BLOC))

    with ThreadPoolExecutor(max_workers=int(ouvriers)) as pool:
        distance = dict(pool.map(a_distance, taches))
    r = {"a_distance": {f"{s}_{y}_{x}": v for (s, y, x), v in distance.items()}}
    r["le_miroir"] = le_controle_du_miroir(min(int(ouvriers), 3), tuple(taches))
    r["identiques"] = bool(r["le_miroir"]["identiques"])
    r["le_telechargement_projete"] = le_telechargement_projete(r["le_miroir"]["le_remplissage"],
                                                               plan["brut"]["le_cout"]["les_chunks"])
    LE_CONTROLE.write_text(json.dumps(r, ensure_ascii=False, indent=1))
    return r


def etalonner(etiquette: str, ouvriers: int = 2) -> dict:
    """Les deux piles du bloc de contrôle, rendues ensemble depuis le miroir sous les bornes de l'unité qui lance l'étape,
    et comparées voxel pour voxel aux piles rendues à distance : un réglage qui change un voxel n'est pas un réglage.

    ⚠ Le miroir est déjà chaud du contrôle : chaque essai lit le même disque, et seules les bornes changent d'un essai à
    l'autre. `surveiller_lunite.sh` relève, à côté, ce que les bornes coûtent.
    """
    import shutil

    plan = lire_le_plan()
    by, bx = plan["controle"]
    taches = [(s, by, bx) for s in LES_SURFACES_HAUTES]
    dossier = LE_ETALONNAGE / etiquette
    if dossier.exists():
        return {"etiquette": etiquette, "refuse": f"{dossier} existe déjà : un essai ne reprend pas un essai"}
    rempli = remplir(set().union(*les_besoins(taches).values()))
    debut = time.monotonic()

    def un(t_):
        s, y, x = t_
        r = rendre(LE_DOSSIER / s / "maillage", dossier / s, le_cadre(y, x, LE_BLOC), miroir=LE_MIROIR)
        diff = les_voxels_differents(LE_DOSSIER / s / f"bloc_{y}_{x}", dossier / s) if r["rendue"] else None
        return f"{s}_{y}_{x}", {"rendue": r["rendue"], "les_secondes": r.get("les_secondes"), "les_voxels_differents": diff}

    with ThreadPoolExecutor(max_workers=int(ouvriers)) as pool:
        piles = dict(pool.map(un, taches))
    out = {"etiquette": etiquette, "les_ouvriers": int(ouvriers), "les_secondes": round(time.monotonic() - debut, 1),
           "les_piles": piles, "le_remplissage": rempli,
           "identiques": all(p_["les_voxels_differents"] == 0 for p_ in piles.values())}
    shutil.rmtree(dossier)
    (LE_ETALONNAGE / f"{etiquette}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    return out


def lire_letalonnage() -> list[dict]:
    """Les essais d'étalonnage, chacun avec ce que ses bornes lui ont coûté, dans l'ordre de leurs étiquettes."""
    out = []
    for f in sorted(LE_ETALONNAGE.glob("*.json")):
        if f.stem.endswith("_cgroup"):
            continue
        e = json.loads(f.read_text())
        cg = LE_ETALONNAGE / f"{f.stem}_cgroup.json"
        e["le_cgroup"] = json.loads(cg.read_text()) if cg.is_file() else None
        out.append(e)
    return out


def mesurer(pas_ouvriers: int = 3) -> dict:
    debut = time.monotonic()
    plan = lire_le_plan()
    brut, a_rendre = plan["brut"], plan["a_rendre"]
    controle = json.loads(LE_CONTROLE.read_text()) if LE_CONTROLE.is_file() else {"identiques": False}
    glissade = float(json.loads(CE_QUE_261_A_PUBLIE.read_text())["le_signe"]["lecart_retrouve_voxels"])
    tau0 = np.load(LE_PREMIER_SAUT_HAUT)
    err = tau0 - np.load(LA_COUCHE_HAUTE)
    out = {"le_plan": {k: brut[k] for k in ("la_tranche", "la_chaine_est_stable", "le_treillis", "les_rangees_candidates",
                                              "les_blocs_a_quatre_voisins",
                                              "le_bloc_du_controle", "le_cout", "la_lecture")},
           "les_blocs_rendus": len(a_rendre), "les_blocs_decides": len(plan["decides"]),
           "le_controle_du_miroir": {"identiques": controle["identiques"],
                                     "les_piles": {k: x.get("les_voxels_differents") for k, x in
                                                   controle.get("le_miroir", {}).get("les_piles", {}).items()}}}
    out["le_cout_du_rendu"] = {"letalonnage": lire_letalonnage(),
                               "le_rendu": json.loads(LE_RENDU.read_text()) if LE_RENDU.is_file() else None,
                               "ses_bornes": [json.loads(f.read_text()) for f in
                                              sorted(LE_DOSSIER.glob(f"{LE_RENDU.stem}*_cgroup.json"))]}
    out["les_pas"] = calculer_les_pas(a_rendre, pas_ouvriers, True, LES_SURFACES_HAUTES)
    rendus = les_rendus_sur_le_disque(a_rendre, LES_SURFACES_HAUTES)
    out["les_piles_manquantes"] = sorted(f"{s}_{by}_{bx}" for (s, by, bx), ok in rendus.items() if not ok)
    tables = les_tables(a_rendre, rendus, LES_SURFACES_HAUTES)
    tous = [un_bloc(by, bx, a_rendre, tables, rendus, tau0, err, glissade, LES_SURFACES_HAUTES)[0]
            for by, bx in plan["decides"]]
    eo = [un_bloc(by, bx, a_rendre, tables, rendus, tau0, err, glissade, LES_SURFACES_HAUTES,
                  les_voisins_de=les_voisins_est_ouest)[0] for by, bx in plan["decides"]]
    quatre = set(plan["quatre"])
    garde = lambda blocs, dedans: [b_ for b_ in blocs if ((b_["la_rangee"], b_["la_colonne"]) in quatre) == dedans]  # noqa: E731
    for nom, dedans in (("les_blocs_a_quatre_voisins", True), ("les_autres_blocs_decides", False)):
        r_t, r_e = la_reunion(garde(tous, dedans)), la_reunion(garde(eo, dedans))
        out[nom] = {"avec_tous_leurs_voisins": {"les_reunis": r_t, "le_test": le_test(r_t)},
                    "avec_les_seuls_voisins_est_et_ouest": {"les_reunis": r_e, "le_test": le_test(r_e)}}
    out["les_blocs"], out["les_blocs_avec_les_seuls_voisins_est_et_ouest"] = tous, eo
    out["les_non_decides"] = {f"{b_['la_rangee']}_{b_['la_colonne']}": b_["la_raison"] for b_ in tous if not b_["decidable"]}
    out["decidable"] = (bool(brut["la_chaine_est_stable"]) and bool(brut["le_treillis"]["reproduit"])
                        and bool(controle["identiques"]) and not out["les_piles_manquantes"]
                        and not brut["la_lecture"]["combien_de_pannes"])
    out["le_verdict"] = le_verdict(out)
    out["les_secondes"] = round(time.monotonic() - debut, 1)
    return out


# ── LES PILES ÉCRITES JUSTE AVANT LA CHUTE ─────────────────────────────────────────────────────────────────────────

def lexces_de_zeros(couches: list[np.ndarray]) -> dict:
    """Ce qu'une couche a de zéros EN TROP sur la médiane des couches de sa pile.

    ⚠ Les couches d'une pile partagent l'empreinte de sa surface, donc leurs zéros hors du maillage sont presque les
    mêmes : une page perdue au moment d'une chute se lit comme une couche qui a soudain plus de zéros que ses sœurs,
    sans erreur de lecture.
    """
    z = np.array([int((c == 0).sum()) for c in couches])
    med = float(np.median(z))
    n = int(couches[0].size)
    return {"les_couches": len(couches), "les_voxels_par_couche": n, "les_octets_par_voxel": int(couches[0].itemsize),
            "la_mediane_des_zeros": med,
            "lexces_maximal_pour_mille": round(1000 * float(z.max() - med) / n, 3),
            "les_couches_toutes_nulles": int(sum(1 for c in couches if not c.any()))}


def les_zeros_des_piles(noms: list[str]) -> dict:
    """`lexces_de_zeros` sur les deux surfaces de chaque bloc nommé (`bloc_16_704`)."""
    import tifffile

    out = {}
    for s in LES_SURFACES_HAUTES:
        for nom in noms:
            d = LE_DOSSIER / s / nom
            out[f"{s}/{nom}"] = lexces_de_zeros([tifffile.imread(f) for f in sorted(d.glob("*.tif"))])
    return out


# ── LA BATTERIE ────────────────────────────────────────────────────────────────────────────────────────────────────

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

    cols = [16 * k for k in range(10)]
    v("★★★★ les colonnes du milieu sont prises dans l'ordre, au milieu", les_colonnes_du_milieu(cols, 4) == [48, 64, 80, 96])
    v("★★★ moins de colonnes qu'il n'en faut : toutes", les_colonnes_du_milieu(cols[:3], 4) == [0, 16, 32])
    c = {(r, x) for r in (0, 16, 32, 48, 64) for x in cols}
    a = les_blocs_a_rendre(c, combien=4)
    v("★★★★ les blocs rendus sont ceux des rangées 16, 32 et 48 sur les colonnes du milieu de la rangée 32",
      a == {(r, x) for r in (16, 32, 48) for x in (48, 64, 80, 96)}, str(sorted(a))[:120])
    v("★★★ seuls ceux de la rangée 32 sont décidés", les_blocs_decides(a) == [(32, x) for x in (48, 64, 80, 96)])
    v("★★★★ un bloc décidé a quatre voisins s'il en a au nord, au sud, à l'est et à l'ouest parmi les rendus",
      a_quatre_voisins(32, 64, a) and not a_quatre_voisins(32, 48, a) and not a_quatre_voisins(32, 96, a))
    r_ = lambda g, s: {"decidable": True, "les_blocs_a_quatre_voisins": {"avec_tous_leurs_voisins": {"le_test": {  # noqa: E731
        "sur_les_points": {"le_gain_net": g, "sous_le_seuil": s}}}}}
    v("★★★★ les issues : un gain positif sous le seuil, sinon non, indécidable sans contrôle",
      "ne rend pas" not in le_verdict(r_(5, True))["lissue"] and "ne rend pas" in le_verdict(r_(-5, True))["lissue"]
      and "ne rend pas" in le_verdict(r_(5, False))["lissue"] and "indécidable" in le_verdict({"decidable": False})["lissue"])
    v("★★ la tranche haute contient celle de 248", LA_TRANCHE_HAUTE[0] < 0.45 and LA_TRANCHE_HAUTE[1] > 0.55)
    pr = le_telechargement_projete({"telecharges": 12, "absents_de_la_source": 2, "les_octets": 50_000}, 1000)
    v("★★★ le poids d'un chunk ne compte pas les chunks absents de la source", pr["les_octets_par_chunk"] == 5000
      and pr["les_go"] == 0.0, str(pr))
    sain = [np.ones((4, 4), dtype=np.uint8) for _ in range(5)]
    for c in sain:
        c[0, :] = 0
    v("★★★ des couches aux mêmes zéros n'ont aucun excès", lexces_de_zeros(sain)["lexces_maximal_pour_mille"] == 0.0)
    troue = [c.copy() for c in sain]
    troue[2][1:3, :] = 0
    v("★★★★ une couche à moitié effacée se voit en excès, sans être toute nulle",
      lexces_de_zeros(troue)["lexces_maximal_pour_mille"] == 500.0 and lexces_de_zeros(troue)["les_couches_toutes_nulles"] == 0)
    v("★★ une couche toute nulle est comptée", lexces_de_zeros(sain[:4] + [np.zeros((4, 4), np.uint8)])[
        "les_couches_toutes_nulles"] == 1)
    v("★★ sans chunk téléchargé, pas de projection", le_telechargement_projete(
        {"telecharges": 0, "absents_de_la_source": 0, "les_octets": 0}, 1000)["les_go"] is None)

    for x in echecs:
        print(f"  ÉCHEC {x}")
    print(f"{Path(__file__).name}   {'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--preparer", action="store_true")
    p.add_argument("--controler", type=int, default=None, metavar="OUVRIERS")
    p.add_argument("--etalonner", default=None, metavar="ETIQUETTE")
    p.add_argument("--ouvriers", type=int, default=2)
    p.add_argument("--rendre", type=int, default=None, metavar="OUVRIERS")
    p.add_argument("--pas", type=int, default=None, metavar="OUVRIERS")
    p.add_argument("--json", type=Path, default=None)
    p.add_argument("--zeros", nargs="+", default=None, metavar="BLOC", help="les zéros en trop des piles nommées")
    a = p.parse_args()
    if a.zeros:
        print(json.dumps(les_zeros_des_piles(a.zeros), ensure_ascii=False, indent=1))
        return 0
    if a.verifier:
        return verifier()
    if a.preparer:
        plan = preparer()
        print(json.dumps({k: (len(x) if isinstance(x, (list, dict)) and k.startswith("les_blocs") else x)
                          for k, x in plan.items()}, ensure_ascii=False, indent=1))
        return 0 if plan.get("la_chaine_est_stable") and plan["le_treillis"]["reproduit"] else 2
    if a.controler is not None:
        r = controler(a.controler)
        print(json.dumps({"identiques": r["identiques"], "les_piles": r["le_miroir"]["les_piles"]}, ensure_ascii=False))
        return 0 if r["identiques"] else 2
    if a.etalonner is not None:
        if not (LE_CONTROLE.is_file() and json.loads(LE_CONTROLE.read_text())["identiques"]):
            print("le miroir n'est pas contrôlé sur ces surfaces : --controler d'abord")
            return 2
        LE_ETALONNAGE.mkdir(parents=True, exist_ok=True)
        r = etalonner(a.etalonner, a.ouvriers)
        print(json.dumps(r, ensure_ascii=False))
        return 0 if r.get("identiques") else 2
    if a.rendre is not None:
        if not (LE_CONTROLE.is_file() and json.loads(LE_CONTROLE.read_text())["identiques"]):
            print("le miroir n'est pas contrôlé sur ces surfaces : --controler d'abord")
            return 2
        r = tout_rendre(lire_le_plan()["a_rendre"], a.rendre, LES_SURFACES_HAUTES)
        LE_RENDU.write_text(json.dumps(r, ensure_ascii=False, indent=1))
        print(json.dumps(r, ensure_ascii=False))
        return 0 if not r["echouees"] else 2
    if a.pas is not None:
        print(json.dumps(calculer_les_pas(lire_le_plan()["a_rendre"], a.pas, True, LES_SURFACES_HAUTES), ensure_ascii=False))
        return 0
    r = mesurer()
    print(json.dumps({k: r[k] for k in r if k != "les_blocs"}, ensure_ascii=False, indent=1))
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=1))
        print(f"\nécrit : {a.json}")
    return 0 if r.get("decidable") else 2


if __name__ == "__main__":
    raise SystemExit(main())
