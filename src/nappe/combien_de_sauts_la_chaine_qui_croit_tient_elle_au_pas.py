"""Combien de sauts la chaîne qui croît tient-elle au pas, sur PHerc0358 depuis les cinq côtés dont le premier saut pose au pas, et sur PHercParis4 depuis les quatorze ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UNE CHAÎNE QUI CROÎT NE SOIT TIRÉE AU-DELÀ DU PREMIER SAUT DEPUIS CES CÔTÉS. Ce qui était vu avant
d'écrire : tout ce que `296` à `327` publient, dont `R4-F508` (le premier saut pose au pas sur 5 côtés de PHerc0358, graine 6 côté moins,
7 et 8 des deux côtés, et sur 14 de PHercParis4), `R4-F512`, et les quatre sauts que `306` publie depuis la graine 6 de PHerc0358 : côté
moins, 79,24 %, 69,87 %, 58,44 % puis 0,66 % du plan, à 18, 20,5, 13,5 et 15,75 voxels.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P126`. La nappe et le saut qui croissent sont validés sur PHercParis4 contre un tracé
humain, sur un saut. Le nombre de sauts que la chaîne tient au pas sur PHerc0358 est ce qu'un rouleau sans tracé peut produire avec ces
seules méthodes ; le même compte sur PHercParis4 dit si c'est une limite de PHerc0358 ou de la chaîne.

## Ce qui est fait

- **Les côtés** : ceux dont le premier saut pose au pas dans `324`, sur chaque rouleau.
- **La chaîne** : depuis la nappe qui croît de `305`, huit sauts qui croissent de `306`, chacun parti de la spire du précédent, sans en
  changer une règle, au pas de chaque rouleau.
- **Un saut tient** s'il pose au pas (la règle de `324` : au moins 10 % du plan, pas médian entre un demi-pas et un pas et demi) et que
  sa spire n'est pas posée dans un bloc de `m7` (la règle de `326`).

## Les issues

Par côté, **la chaîne tient h sauts** : le dernier saut h tel que les sauts 1 à h tiennent tous. L'issue de la tranche : **sur
PHerc0358, la chaîne tient h sauts en médiane sur les 5 côtés, et sur PHercParis4, h' sur les 14** ; et, déclaré avant : **elle produit
plusieurs spires sur PHerc0358** si au moins la moitié de ses côtés tiennent au moins deux sauts.

## Rapporté à côté, qui ne décide rien

Pour chaque saut : la part du plan posée, le pas médian en pas du rouleau, la longueur de la plage de `m7` sous la spire.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : que ces spires soient consécutives ou sur la bonne feuille, au-delà du premier saut de PHercParis4.

Usage :
    uv run python src/nappe/combien_de_sauts_la_chaine_qui_croit_tient_elle_au_pas.py --verifier
    uv run python src/nappe/combien_de_sauts_la_chaine_qui_croit_tient_elle_au_pas.py \\
        --json docs/mesures/combien_de_sauts_la_chaine_qui_croit_tient_elle_au_pas.json
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

import lalignement_des_profils_dit_il_si_une_premiere_surface_suit_sa_feuille as m299  # noqa: E402
import une_nappe_tiree_de_m7_suit_elle_sa_feuille as m300  # noqa: E402
import les_nappes_de_m7_suivent_elles_leur_feuille_sur_des_graines_neuves as m301  # noqa: E402
import une_nappe_qui_refuse_de_changer_de_feuille_suit_elle_encore_sa_feuille as m305  # noqa: E402
import la_chaine_dune_seule_feuille_suit_elle_sa_feuille_sur_quatre_spires as m306  # noqa: E402
import la_nappe_de_m7_retrouve_t_elle_le_trace_humain_de_paris4 as m321  # noqa: E402
import la_nappe_qui_croit_tient_elle_le_trace_humain_de_paris4 as m322  # noqa: E402
import le_saut_qui_croit_pose_t_il_au_pas_sur_les_deux_rouleaux as m324  # noqa: E402
import la_nappe_plate_est_elle_posee_dans_un_bloc_de_m7 as m326  # noqa: E402

LES_SAUTS = 8
CE_QUE_324_A_PUBLIE = RACINE / "docs" / "mesures" / "le_saut_qui_croit_pose_t_il_au_pas_sur_les_deux_rouleaux.json"


def un_saut(s: dict, lire_valeurs, pas: float) -> dict:
    """Ce qu'un saut pose, et s'il tient : au pas, et sa spire hors d'un bloc de `m7`."""
    e = m324.le_saut(s["le_pas"], s["valide"], pas)
    if s["valide"].any():
        plage = m326.lire_les_plages({"la_nappe": s["la_spire"], "valide": s["valide"]}, lire_valeurs, pas)
    else:
        plage = {"la_longueur_mediane_en_pas": None, "la_lecture": "non lue"}
    e["la_plage_en_pas"] = plage["la_longueur_mediane_en_pas"]
    e["tient"] = bool(e["pose_au_pas"] and plage["la_lecture"] != "dans un bloc")
    return e


def combien(sauts: list[dict]) -> int:
    h = 0
    for s in sauts:
        if not s["tient"]:
            break
        h += 1
    return h


def la_chaine(nappe: dict, cote: float, lire_valeurs, pas: float, tolerance: float, sauts: int = LES_SAUTS) -> list[dict]:
    """Jusqu'à `sauts` sauts qui croissent, chacun parti de la spire du précédent ; la chaîne s'arrête au premier saut qui ne pose rien."""
    surf, ok = nappe["la_nappe"], nappe["valide"]
    out = []
    for _ in range(sauts):
        s = m306.le_saut_croissant(surf, ok, cote, lire_valeurs, tolerance=tolerance)
        out.append(un_saut(s, lire_valeurs, pas))
        if not s["valide"].any():
            break
        surf, ok = s["la_spire"], s["valide"]
    return out


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    c0, c4 = d["les_cotes"]["PHerc0358"], d["les_cotes"]["PHercParis4"]
    if not c0 or not c4:
        return {"decidable": False, "lissue": "indécidable : aucun côté à suivre"}
    if not all(c["les_sauts"] and c["les_sauts"][0]["pose_au_pas"] for c in c0 + c4):
        return {"decidable": False, "lissue": "indécidable : un premier saut ne redonne pas 324"}
    h0 = [c["tient"] for c in c0]
    h4 = [c["tient"] for c in c4]
    m0, m4 = float(np.median(h0)), float(np.median(h4))
    plusieurs = 2 * sum(1 for x in h0 if x >= 2) >= len(h0)
    f_ = lambda x: f"{x:g}".replace(".", ",") + (" saut" if x <= 1 else " sauts")  # noqa: E731
    return {"decidable": True, "h0": h0, "h4": h4, "plusieurs": plusieurs,
            "lissue": f"sur PHerc0358, la chaîne qui croît tient {f_(m0)} en médiane sur les {len(h0)} côtés, et sur PHercParis4, "
                      f"{f_(m4)} sur les {len(h4)} ; " + ("elle produit plusieurs spires sur PHerc0358" if plusieurs
                                                         else "elle ne produit pas plusieurs spires sur PHerc0358")}


def mesurer() -> dict:
    import le_tour_produit_porte_t_il_le_texte_du_segment as j296
    from le_transfert_retrouve_t_il_la_spire_voisine import lecteur_du_depot, lire_les_valeurs
    from la_spire_voisine_est_elle_a_un_pas import les_normales, lire_tifxyz

    from zarr_depth import BUCKET, array_meta

    t0 = time.monotonic()
    d324 = json.loads(CE_QUE_324_A_PUBLIE.read_text())
    a_suivre = {r: {(c["le_rang"], c["le_cote"]) for c in d324["les_cotes"][r] if c["le_saut"]["pose_au_pas"]}
                for r in ("PHerc0358", "PHercParis4")}
    cotes = {"PHerc0358": [], "PHercParis4": []}
    lecture = {}
    pred = array_meta(f"{BUCKET}/{m299.LA_PREDICTION_0358}", 0, 120.0)
    lire_, stats = lecteur_du_depot(pred, m300.LE_CACHE_M7, "m7_L0", m299.LA_PREDICTION_0358, 0)
    lv = lambda idx: lire_les_valeurs(idx, pred, lire_)  # noqa: E731
    d301 = {tuple(g["la_graine"]): g["le_rang"]
            for g in json.loads(m305.CE_QUE_301_A_PUBLIE.read_text())["le_rouleau"]["les_graines"]}
    for g in m301.les_graines_neuves():
        cle = (g["x"], g["y"], g["z"])
        rang = d301[cle]
        if not any((rang, c) in a_suivre["PHerc0358"] for c, _ in m306.LES_COTES):
            continue
        nz, ny, nx = g["normale_zyx"]
        r = m305.la_nappe_croissante(cle, (nx, ny, nz), lv)
        for c, cote in m306.LES_COTES:
            if (rang, c) not in a_suivre["PHerc0358"]:
                continue
            sauts = la_chaine(r, cote, lv, m300.LE_PAS_0358, m305.LA_TOLERANCE)
            e = {"le_rang": rang, "le_cote": c, "les_sauts": sauts, "tient": combien(sauts)}
            cotes["PHerc0358"].append(e)
            print("PHerc0358", json.dumps({k: v for k, v in e.items() if k != "les_sauts"}, ensure_ascii=False),
                  [(s["la_part_du_plan"], s["le_pas_median_en_pas"], s["la_plage_en_pas"]) for s in sauts], flush=True)
    pannes = list(stats["pannes"])
    lecture["PHerc0358"] = {k: v for k, v in stats.items() if k != "pannes"}

    seg, sok, _ = lire_tifxyz(j296.LE_DOSSIER / j296.LES_SURFACES[0] / "maillage")
    sn, snok = les_normales(seg, sok)
    pred = array_meta(f"{BUCKET}/{m321.LA_PREDICTION}", 0, 120.0)
    lire4, stats4 = lecteur_du_depot(pred, m321.LE_CACHE, "m7_L2", m321.LA_PREDICTION, 0)
    lv4 = lambda idx: m300.lire_m7(idx, (pred, lire4))  # noqa: E731
    for rang, (i, j) in enumerate(m321.les_graines(seg, sok, snok), 1):
        if not any((rang, c) in a_suivre["PHercParis4"] for c, _ in m306.LES_COTES):
            continue
        r = m322.la_nappe_de_paris4(seg[i, j] / m321.LE_FACTEUR, sn[i, j], lv4)
        for c, cote in m306.LES_COTES:
            if (rang, c) not in a_suivre["PHercParis4"]:
                continue
            with m321.le_rouleau_de_paris4():
                sauts = la_chaine(r, cote, lv4, m321.LE_PAS_L2, m322.LA_TOLERANCE_L2)
            e = {"le_rang": rang, "le_cote": c, "les_sauts": sauts, "tient": combien(sauts)}
            cotes["PHercParis4"].append(e)
            print("PHercParis4", json.dumps({k: v for k, v in e.items() if k != "les_sauts"}, ensure_ascii=False),
                  [(s["la_part_du_plan"], s["le_pas_median_en_pas"], s["la_plage_en_pas"]) for s in sauts], flush=True)
    pannes += list(stats4["pannes"])
    lecture["PHercParis4"] = {k: v for k, v in stats4.items() if k != "pannes"}
    d = {"la_question": __doc__.splitlines()[0], "les_constantes": {"les_sauts": LES_SAUTS},
         "les_pannes": pannes, "la_lecture_de_m7": lecture, "les_cotes": cotes}
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

    # Une nappe plane de 9 × 9 points au pas 10, et des feuilles de m7 minces à 20 voxels l'une de l'autre : la chaîne tient chaque saut.
    grille = np.zeros((9, 9, 3))
    for a in range(9):
        for b in range(9):
            grille[a, b] = (100.0 + 10.0 * b, 100.0 + 10.0 * a, 100.0)
    nappe = {"la_nappe": grille, "valide": np.ones((9, 9), dtype=bool)}
    feuilles = lambda idx: (idx[..., 0] - 100) % 20 == 0  # noqa: E731
    ch = la_chaine(nappe, 1.0, feuilles, 20.0, 5.0, sauts=3)
    v("★★★★ des feuilles minces tous les 20 voxels : trois sauts tenus", len(ch) == 3 and combien(ch) == 3, str(ch))
    bloc = lambda idx: (idx[..., 0] == 100) | ((idx[..., 0] >= 110) & (idx[..., 0] <= 130))  # noqa: E731
    ch = la_chaine(nappe, 1.0, bloc, 20.0, 5.0, sauts=3)
    v("★★★★ une spire posée au pas mais dans un bloc de 21 voxels ne tient pas", ch[0]["pose_au_pas"] and combien(ch) == 0
      and ch[0]["la_plage_en_pas"] >= 1.0, str(ch[:1]))
    loin = lambda idx: (idx[..., 0] == 100) | (idx[..., 0] == 145)  # noqa: E731
    ch = la_chaine(nappe, 1.0, loin, 20.0, 5.0, sauts=3)
    v("★★★ une feuille à 45 voxels pour un pas de 20 : le saut ne tient pas", combien(ch) == 0 and not ch[0]["pose_au_pas"])
    rien = lambda idx: idx[..., 0] == 100  # noqa: E731
    ch = la_chaine(nappe, 1.0, rien, 20.0, 5.0, sauts=3)
    v("★★★ la chaîne s'arrête au premier saut qui ne pose rien", len(ch) == 1 and ch[0]["la_part_du_plan"] == 0.0, str(ch))
    s = [{"tient": True}, {"tient": False}, {"tient": True}]
    v("★★★ on compte les sauts tenus d'affilée, depuis le premier", combien(s) == 1)
    c = lambda h: {"tient": h, "les_sauts": [{"pose_au_pas": True}]}  # noqa: E731
    vd = le_verdict({"les_pannes": [], "les_cotes": {"PHerc0358": [c(2), c(3), c(0), c(1)], "PHercParis4": [c(1)]}})
    v("★★★★ deux côtés sur quatre à deux sauts au moins : plusieurs spires", vd["plusieurs"], str(vd))
    vd = le_verdict({"les_pannes": [], "les_cotes": {"PHerc0358": [c(2), c(1), c(0), c(1)], "PHercParis4": [c(1)]}})
    v("★★★★ un seul sur quatre : pas plusieurs", not vd["plusieurs"])
    v("★★★ un premier saut qui ne pose plus au pas : indécidable",
      not le_verdict({"les_pannes": [], "les_cotes": {"PHerc0358": [{"tient": 0, "les_sauts": [{"pose_au_pas": False}]}],
                                                      "PHercParis4": [c(1)]}})["decidable"])

    for e in echecs:
        print(f"  ÉCHEC {e}")
    print(f"{Path(__file__).name}   {'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    d = mesurer()
    texte = json.dumps(d, ensure_ascii=False, indent=1)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(texte + "\n")
    print(json.dumps(d["le_verdict"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
