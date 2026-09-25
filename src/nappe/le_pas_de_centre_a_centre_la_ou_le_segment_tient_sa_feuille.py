"""Là où le segment tient sa feuille, le pas de centre à centre marche-t-il calme, et que dit-il de la spire produite ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LE BLOC NE SOIT CHOISI ET AVANT QU'UN SEUL PAS N'Y SOIT LU. Ce qui était vu avant
d'écrire : tout ce que `257` et `258` publient.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P94`. Sur le bloc de `257`, le segment passe entre deux feuilles, et la marche du
segment lui-même, lue de centre à centre, s'y étend sur 126 voxels : `258` ne sait pas dire si c'est le segment qui dérive
ou le pas. Un bloc où le segment tient sa feuille le dit.

## Le bloc, sans choix

Parmi les blocs de 16 × 16 chunks de `257` (dans l'empreinte, la surface produite définie partout), ceux où `m7` voit le
segment lui-même, à moins de douze voxels le long de sa normale, en au moins **0,95** des points de la maille ; parmi eux,
celui qui porte le plus de ratés jugés (les deux juges de `247` d'accord). ⚠ C'est la prédiction qui dit que le segment
tient sa feuille ; le scan le vérifie ensuite, par la couche la plus claire de chaque chunk de la pile (`257`).

## Ce qui se lit

Le segment réduit et la spire produite, rendus comme dans `257`. Sur chacun, le pas de centre à centre de `258` et le pas à la
couture de `224`, puis la marche du bloc. La rampe numérique de `258` (24 voxels, la même matière décalée) sur le segment.

## Les issues, exclusives, dans cet ordre

- le scan dit que le segment ne tient pas sa feuille ici non plus (moins de la moitié des chunks à moins d'un quart de pas du
  milieu) : la règle n'a pas trouvé de bloc propre ;
- la rampe numérique n'est pas retrouvée à un demi au moins de centre à centre : pas d'instrument ;
- la marche du segment, de centre à centre, s'étend sur plus d'un pas : le pas est trop bruité pour marcher un bloc ;
- sinon, la différence des marches de la spire produite et du segment sépare, ou non, mieux que le témoin les paires que le
  juge sépare.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : une boucle, un autre côté, `ps256`, ni ce que vaut le bloc au-delà de lui-même.

Usage :
    uv run python src/nappe/le_pas_de_centre_a_centre_la_ou_le_segment_tient_sa_feuille.py --verifier
    uv run python src/nappe/le_pas_de_centre_a_centre_la_ou_le_segment_tient_sa_feuille.py \\
        --json docs/mesures/le_pas_de_centre_a_centre_la_ou_le_segment_tient_sa_feuille.json
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

from la_spire_produite_se_lit_elle_dans_le_treillis import (LA_MAILLE, LA_PREDICTION, LE_BLOC,  # noqa: E402
                                                            LE_COTE, LE_COTE_DU_CHUNK, LE_DOSSIER, LES_JUGES,
                                                            ecrire_tifxyz, la_feuille_dans_la_pile,
                                                            la_coupe, la_fenetre_de_maille, la_marche_du_bloc,
                                                            la_rangee_de_coupe,
                                                            la_part_retrouvee, laccord_des_paires, le_cadre,
                                                            le_maillage_produit, le_maillage_reduit, le_meta,
                                                            lerreur_aux_chunks, lerreur_jugee, les_pas_du_bloc,
                                                            lire_la_pile, rendre, servir)
from la_spire_voisine_est_elle_a_un_pas import (LE_CACHE, LE_SEGMENT, PAS_EN_VOXELS, lire_tifxyz,  # noqa: E402
                                                les_normales, telecharger)
from le_pas_de_centre_a_centre_voit_il_la_rampe import (LA_RAMPE_NUMERIQUE, LE_SEUIL_DE_LA_RAMPE,  # noqa: E402
                                                        la_pile_decalee, les_pas_de_centre)
from le_transfert_retrouve_t_il_la_spire_voisine import (LES_PREDICTIONS, le_facteur,  # noqa: E402
                                                         lecteur_du_depot, les_echantillons, lire_les_valeurs)
from ou_le_maillage_quitte_t_il_son_feuillet import le_segment_declare, un_chunk  # noqa: E402
from zarr_depth import BUCKET, array_meta  # noqa: E402

LA_PART_OU_M7_VOIT_LE_SEGMENT = 0.95
LE_TREILLIS = (396, 285)   # la grille de chunks du volume publié de `20230702185753`, que `257` publie


def la_carte_ou_la_prediction_voit_le_segment(ref, valide, lire, pred, facteur, maille: int = LA_MAILLE) -> np.ndarray:
    """Sur la maille : 1 là où la prédiction voit le segment à moins de douze voxels le long de sa normale, 0 là où elle
    ne le voit pas, NaN là où la maille n'a pas de normale — le contrôle du repère de `247`, point par point."""
    n, ok = les_normales(ref, valide)
    grille = np.zeros_like(ok)
    grille[::maille, ::maille] = True
    ii, jj = np.nonzero(ok & grille)
    _, idx = les_echantillons(ref[ii, jj], n[ii, jj], 0, facteur)
    vu = lire_les_valeurs(idx, pred, lire) > 0
    out = np.full(ok[::maille, ::maille].shape, np.nan)
    out[ii // maille, jj // maille] = vu.any(axis=1).astype(float)
    return out


def le_bloc_propre(tau: np.ndarray, erreur: np.ndarray, voit: np.ndarray, empreinte: np.ndarray, gy: int, gx: int,
                   cote: int = LE_BLOC, seuil: float = LA_PART_OU_M7_VOIT_LE_SEGMENT, pas_de_grille: int = 20) -> dict:
    """Le bloc de la règle : ceux de `257`, où la prédiction voit le segment en `seuil` au moins des points ; parmi eux,
    le plus de ratés jugés, égalités départagées par la rangée puis la colonne."""
    cands, propres = [], 0
    for by in range(0, gy - cote + 1, cote):
        for bx in range(0, gx - cote + 1, cote):
            e0 = empreinte[by * LE_COTE_DU_CHUNK // pas_de_grille:(by + cote) * LE_COTE_DU_CHUNK // pas_de_grille,
                           bx * LE_COTE_DU_CHUNK // pas_de_grille:(bx + cote) * LE_COTE_DU_CHUNK // pas_de_grille]
            sr, sc = la_fenetre_de_maille(by, bx, cote, pas_de_grille=pas_de_grille)
            if e0.size == 0 or not e0.all() or sr.stop > tau.shape[0] or sc.stop > tau.shape[1] \
                    or not np.isfinite(tau[sr, sc]).all():
                continue
            vv = voit[sr, sc]
            vv = vv[np.isfinite(vv)]
            if vv.size == 0 or vv.mean() < seuil:
                continue
            propres += 1
            e = erreur[sr, sc]
            note = np.isfinite(e)
            cands.append((-int((np.abs(e[note]) >= PAS_EN_VOXELS / 2).sum()), by, bx, int(note.sum()),
                          round(float(vv.mean()), 4)))
    if not cands:
        return {"decidable": False, "la_raison": "aucun bloc où la prédiction voit le segment"}
    cands.sort()
    m, by, bx, n, part = cands[0]
    return {"decidable": True, "la_rangee": by, "la_colonne": bx, "le_cote": cote, "les_rates": -m,
            "les_points_notes": n, "la_part_ou_m7_voit_le_segment": part, "les_blocs_propres": propres}


def lire_le_bloc(nom: str, tifxyz: Path, by: int, bx: int) -> tuple[np.ndarray | None, dict]:
    sortie = LE_DOSSIER / nom / f"bloc_{by}_{bx}"
    r = rendre(tifxyz, sortie, le_cadre(by, bx, LE_BLOC))
    return (lire_la_pile(sortie) if r["rendue"] else None), r


def les_deux_marches(pile: np.ndarray, by: int, bx: int) -> dict:
    """La marche de centre à centre et celle à la couture, sur une pile locale."""
    ouvrir = servir(pile, by, bx)
    c = les_pas_de_centre(ouvrir, by, bx, LE_BLOC)
    mc = la_marche_du_bloc(c["h"], c["v"], by, bx, LE_BLOC)
    lu = les_pas_du_bloc(by, bx, LE_BLOC, ouvrir, le_meta((109, LE_TREILLIS[0] * 128, LE_TREILLIS[1] * 128)),
                         {"cle": "rendu local", "segment": LE_SEGMENT})
    mk = (la_marche_du_bloc(lu["le_long"], lu["en_travers"], by, bx, LE_BLOC) if lu.get("decidable")
          else {"la_profondeur": np.full((LE_BLOC, LE_BLOC), np.nan), "les_coutures": 0})
    return {"de_centre_a_centre": mc, "a_la_couture": mk, "les_chunks_lus": c["les_chunks_lus"]}


def la_pile_publiee(by: int, bx: int, cote: int = LE_BLOC) -> np.ndarray | None:
    """La pile PUBLIÉE du bloc, chunk par chunk : le segment plein, et non réduit à la maille de la chaîne."""
    vol = le_segment_declare()
    url = f"{BUCKET}/{vol['cle']}"
    meta = array_meta(url, 0, 120.0)
    out = np.zeros((109, cote * LE_COTE_DU_CHUNK, cote * LE_COTE_DU_CHUNK), dtype=np.uint8)
    for i in range(cote):
        for j in range(cote):
            b, _ = un_chunk(url, meta, by + i, bx + j, 120.0, None)
            if b is None:
                return None
            out[:, i * LE_COTE_DU_CHUNK:(i + 1) * LE_COTE_DU_CHUNK, j * LE_COTE_DU_CHUNK:(j + 1) * LE_COTE_DU_CHUNK] = b
    return out


def la_feuille(pile: np.ndarray) -> dict:
    f = la_feuille_dans_la_pile(pile)
    fv = f[np.isfinite(f)]
    return {"les_chunks": int(fv.size), "lecart_median_voxels": round(float(np.median(np.abs(fv))), 4),
            "la_part_a_moins_dun_quart_de_pas": round(float((np.abs(fv) <= PAS_EN_VOXELS / 4).mean()), 4)}


def letendue(a: np.ndarray):
    return round(float(np.nanmax(a) - np.nanmin(a)), 4) if np.isfinite(a).any() else None


def resume(m: dict) -> dict:
    return {"les_coutures": m.get("les_coutures"), "le_residu_rms": m.get("le_residu_rms"),
            "letendue_voxels": letendue(m["la_profondeur"])}


def mesurer(cache: Path = LE_CACHE) -> dict:
    debut = time.monotonic()
    d = telecharger(LE_SEGMENT, cache)
    if isinstance(d, str):
        return {"decidable": False, "la_raison": d}
    ref, valide, esp = lire_tifxyz(d)
    chemin, niveau = LES_PREDICTIONS[LA_PREDICTION]
    facteur, pred = le_facteur(chemin, niveau)
    lire, stats = lecteur_du_depot(pred, cache, LA_PREDICTION, chemin, niveau)
    voit = la_carte_ou_la_prediction_voit_le_segment(ref, valide, lire, pred, facteur)
    tau = np.load(cache / f"transfert_suivante_{LE_SEGMENT}_{LA_PREDICTION}_{LE_COTE}.npy")
    err = lerreur_jugee(tau, [np.load(cache / f"verite_{LE_SEGMENT}_{j}_{LE_COTE}.npy") for j in LES_JUGES])
    out = {"le_segment": LE_SEGMENT, "la_part_ou_m7_voit_le_segment_sur_toute_la_maille":
           round(float(np.nanmean(voit)), 4), "la_lecture_de_m7": {"chunks_lus": stats["lus"], "pannes": len(stats["pannes"])}}
    bloc = le_bloc_propre(tau, err, voit, valide, *LE_TREILLIS)
    out["le_bloc"] = bloc
    if not bloc["decidable"]:
        return {**out, "decidable": False}
    by, bx = bloc["la_rangee"], bloc["la_colonne"]
    scale = 1.0 / (esp * LA_MAILLE)
    pr, vr = le_maillage_reduit(ref, valide)
    pp, vp = le_maillage_produit(ref, valide, tau)
    t_r = ecrire_tifxyz(LE_DOSSIER / "le_segment_reduit" / "maillage", pr, vr, scale, "le_segment_reduit")
    t_p = ecrire_tifxyz(LE_DOSSIER / "la_spire_produite" / "maillage", pp, vp, scale, "la_spire_produite")
    piles, rendus = {}, {}
    for nom, t in (("le_segment_reduit", t_r), ("la_spire_produite", t_p)):
        piles[nom], rendus[nom] = lire_le_bloc(nom, t, by, bx)
        if piles[nom] is None:
            return {**out, "les_rendus": rendus, "decidable": False}
    out["les_rendus"] = rendus
    out["la_feuille_dans_la_pile_du_segment"] = la_feuille(piles["le_segment_reduit"])
    marches = {nom: les_deux_marches(p, by, bx) for nom, p in piles.items()}
    decalee, pose = la_pile_decalee(piles["le_segment_reduit"], LA_RAMPE_NUMERIQUE)
    md = les_deux_marches(decalee, by, bx)
    s = marches["le_segment_reduit"]
    out["la_rampe_numerique"] = {
        "de_centre_a_centre": la_part_retrouvee(md["de_centre_a_centre"]["la_profondeur"],
                                                s["de_centre_a_centre"]["la_profondeur"], pose),
        "a_la_couture": la_part_retrouvee(md["a_la_couture"]["la_profondeur"], s["a_la_couture"]["la_profondeur"], pose)}
    # ⚠⚠ AJOUTÉ APRÈS LA PREMIÈRE MESURE : le scan disait le segment réduit hors de sa feuille là où `m7` le voit sur elle.
    # La pile publiée, rendue sur le segment PLEIN, dit si c'est la maille de la chaîne qui perd la feuille.
    pub = la_pile_publiee(by, bx)
    if pub is not None:
        mpub = les_deux_marches(pub, by, bx)
        dpub, pose_pub = la_pile_decalee(pub, LA_RAMPE_NUMERIQUE)
        mdp = les_deux_marches(dpub, by, bx)
        out["la_pile_publiee"] = {
            "la_feuille_dans_la_pile": la_feuille(pub),
            "de_centre_a_centre": resume(mpub["de_centre_a_centre"]), "a_la_couture": resume(mpub["a_la_couture"]),
            "la_rampe_numerique": {
                "de_centre_a_centre": la_part_retrouvee(mdp["de_centre_a_centre"]["la_profondeur"],
                                                        mpub["de_centre_a_centre"]["la_profondeur"], pose_pub),
                "a_la_couture": la_part_retrouvee(mdp["a_la_couture"]["la_profondeur"],
                                                  mpub["a_la_couture"]["la_profondeur"], pose_pub)}}
    e = lerreur_aux_chunks(err, by, bx, LE_BLOC)
    ic = la_rangee_de_coupe(e)
    yc = ic * LE_COTE_DU_CHUNK + LE_COTE_DU_CHUNK // 2
    out["les_coupes"] = {"la_rangee_du_bloc": ic, "la_publiee": None if pub is None else la_coupe(pub, yc),
                         **{nom: la_coupe(pl, yc) for nom, pl in piles.items()}}
    out["lerreur_aux_chunks"] = {"les_chunks_notes": int(np.isfinite(e).sum()),
                                 "les_chunks_rates": int((np.abs(e[np.isfinite(e)]) >= PAS_EN_VOXELS / 2).sum())}
    out["les_marches"], cartes = {}, {"lerreur": e}
    for sens in ("de_centre_a_centre", "a_la_couture"):
        ms, mp = s[sens]["la_profondeur"], marches["la_spire_produite"][sens]["la_profondeur"]
        diff = mp - ms
        out["les_marches"][sens] = {"le_segment": resume(s[sens]), "la_spire_produite": resume(marches["la_spire_produite"][sens]),
                                    "la_difference": {"letendue_voxels": letendue(diff),
                                                      "laccord_des_paires": laccord_des_paires(diff, e),
                                                      "contre_lerreur_jugee": la_part_retrouvee(mp, ms, e)}}
        cartes[f"le_segment_{sens}"], cartes[f"la_difference_{sens}"] = ms, diff
    out["le_temoin_plat"] = laccord_des_paires(np.zeros_like(e), e)
    out["les_cartes"] = {k: [[None if not np.isfinite(x) else round(float(x), 2) for x in r] for r in c]
                         for k, c in cartes.items()}
    out["les_secondes"] = round(time.monotonic() - debut, 1)
    out["decidable"] = True
    return out


def le_verdict(r: dict) -> dict:
    if not r.get("decidable"):
        return {"lissue": "indécidable"}
    f = r["la_feuille_dans_la_pile_du_segment"]
    if f["la_part_a_moins_dun_quart_de_pas"] < 0.5:
        return {"lissue": "le scan dit que le segment ne tient pas sa feuille ici non plus : la règle n'a pas trouvé de "
                          "bloc propre"}
    z = r["la_rampe_numerique"]["de_centre_a_centre"]
    if not z.get("decidable") or z["la_pente"] < LE_SEUIL_DE_LA_RAMPE:
        return {"lissue": "la rampe numérique n'est pas retrouvée de centre à centre : pas d'instrument"}
    m = r["les_marches"]["de_centre_a_centre"]
    if (m["le_segment"]["letendue_voxels"] or 0.0) > PAS_EN_VOXELS:
        return {"lissue": "la marche du segment, de centre à centre, s'étend sur plus d'un pas : le pas est trop bruité "
                          "pour marcher un bloc"}
    a = m["la_difference"]["laccord_des_paires"]
    sep = a.get("la_part_que_la_marche_separe_parmi_celles_que_le_juge_separe") or 0.0
    reu = a.get("la_part_que_la_marche_reunit_parmi_celles_que_le_juge_reunit") or 0.0
    if sep <= 0.5 or sep + reu <= 1.0:
        return {"lissue": "le pas marche calme, et la différence ne sépare pas mieux que le témoin les paires que le juge "
                          "sépare", "separe": sep, "reunit": reu}
    return {"lissue": "le pas marche calme, et la différence sépare : le treillis, lu de centre à centre, juge la spire "
                      "produite", "separe": sep, "reunit": reu}


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

    # Le bloc : trois candidats, un où la prédiction ne voit pas assez le segment et qui porte le plus de ratés.
    tau = np.zeros((60, 40))
    err = np.zeros((60, 40))
    voit = np.ones((60, 40))
    emp = np.ones((600, 400), dtype=bool)
    err[0:10, 0:10] = 72.0      # le bloc (0, 0) : le plus raté, mais la prédiction n'y voit pas le segment
    voit[0:14, 0:14] = 0.0
    err[12:18, 20:26] = 72.0    # le bloc (16, 16) : moins raté, propre
    b = le_bloc_propre(tau, err, voit, emp, 70, 45, cote=16)
    v("★★★★ le bloc est le plus raté parmi ceux où la prédiction voit le segment",
      lambda: b["decidable"] and (b["la_rangee"], b["la_colonne"]) == (16, 16) and b["la_part_ou_m7_voit_le_segment"] >= 0.95,
      str(b))
    voit2 = voit.copy()
    voit2[12:15, 20:26] = 0.0
    b2 = le_bloc_propre(tau, err, voit2, emp, 70, 45, cote=16)
    v("★★★ sous le seuil de 0,95, un bloc n'est plus propre", lambda: (b2["la_rangee"], b2["la_colonne"]) != (16, 16), str(b2))
    v("★★★ aucun bloc propre : indécidable, par sa raison",
      lambda: not le_bloc_propre(tau, err, np.zeros_like(voit), emp, 70, 45, cote=16)["decidable"])
    base = {"decidable": True, "la_feuille_dans_la_pile_du_segment": {"la_part_a_moins_dun_quart_de_pas": 0.8},
            "la_rampe_numerique": {"de_centre_a_centre": {"decidable": True, "la_pente": 1.0}},
            "les_marches": {"de_centre_a_centre": {"le_segment": {"letendue_voxels": 40.0},
                                                   "la_difference": {"laccord_des_paires": {
                                                       "la_part_que_la_marche_separe_parmi_celles_que_le_juge_separe": 0.9,
                                                       "la_part_que_la_marche_reunit_parmi_celles_que_le_juge_reunit": 0.9}}}}}
    v("★★★★ le verdict suit l'ordre déclaré : sépare", lambda: "sépare :" in le_verdict(base)["lissue"])
    b3 = json.loads(json.dumps(base))
    b3["la_feuille_dans_la_pile_du_segment"]["la_part_a_moins_dun_quart_de_pas"] = 0.3
    v("★★★★ un segment que le scan dit hors de sa feuille arrête tout", lambda: "bloc propre" in le_verdict(b3)["lissue"])
    b4 = json.loads(json.dumps(base))
    b4["les_marches"]["de_centre_a_centre"]["le_segment"]["letendue_voxels"] = 90.0
    v("★★★★ une marche du segment plus longue qu'un pas dit le pas trop bruité", lambda: "trop bruité" in le_verdict(b4)["lissue"])
    b5 = json.loads(json.dumps(base))
    b5["la_rampe_numerique"]["de_centre_a_centre"]["la_pente"] = 0.2
    v("★★★ une rampe numérique manquée dit : pas d'instrument", lambda: "pas d'instrument" in le_verdict(b5)["lissue"])
    v("★★★ l'étendue ignore les chunks sans profondeur", lambda: letendue(np.array([[1.0, np.nan], [4.0, -2.0]])) == 6.0)

    for x in echecs:
        print(f"  ÉCHEC {x}")
    print(f"{Path(__file__).name}   {'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer()
    r["le_verdict"] = le_verdict(r)
    texte = json.dumps(r, indent=1, ensure_ascii=False)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(texte + "\n")
    print(json.dumps({k: r.get(k) for k in ("le_bloc", "le_verdict")}, ensure_ascii=False))
    return 0 if r.get("decidable") else 2


if __name__ == "__main__":
    raise SystemExit(main())
