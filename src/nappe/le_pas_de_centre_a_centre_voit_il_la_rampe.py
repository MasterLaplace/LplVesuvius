"""Un pas lu d'un centre de chunk à l'autre voit-il la dérive qu'un pas lu à la couture ne voit pas ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UN SEUL PAS DE CENTRE À CENTRE NE SOIT LU. Ce qui était vu avant d'écrire : tout ce que
`257` publie, c'est-à-dire les trois piles rendues sur le bloc, la rampe posée, et le fait que la marche des coutures n'en
retrouve que 0,1396.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P94`. Le pas de `199` se lit sur les seize colonnes de part et d'autre d'une
couture, exprès, pour ne voir que ce qui saute à la couture. Une surface qui glisse d'une spire à l'autre en douceur, comme
celle que produit la chaîne, ne saute nulle part. Un pas lu sur le chunk ENTIER de part et d'autre voit la différence de
profondeur entre les centres de deux chunks voisins, donc toute dérive, lente ou non.

## Le pas

Le même estimateur que `224` (`le_pas_de_k_rangees`, seize rangées de coupe, la même plage d'un demi-feuillet), sur les
mêmes chunks passés au même filtre, mais chaque profil est la moyenne du chunk ENTIER le long de la coupe, et non de ses seize
colonnes de bord. Puis la marche du bloc de `257`, par moindres carrés.

## Ce qui se mesure, sur les piles de `257`

1. LE CONTRÔLE POSITIF : la pente de la marche de la rampe, moins celle du segment réduit, contre l'écart posé. ⭐ Déclaré :
   elle voit la rampe si cette pente atteint un demi.
2. LE SEGMENT : l'étendue de sa marche sur le bloc.
3. LA SPIRE PRODUITE : la marche de la spire produite moins celle du segment, qui retire ce que le segment fait de lui-même,
   contre l'erreur que le juge donne au transfert ; l'accord des paires de `257`, avec le témoin plat.

## Les issues, exclusives

- le pas de centre à centre ne voit pas la rampe : il n'y a pas encore d'instrument ;
- il la voit, et la différence des marches ne sépare pas mieux que le témoin les paires que le juge sépare : sur ce bloc,
  la spire produite ne dérive pas là où le juge la dit ratée, ou le juge se trompe ;
- il la voit, et elle sépare : le treillis, lu de centre à centre, juge une spire que la chaîne a produite.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : un autre bloc, une boucle, ni si le pas de centre à centre garde le bruit assez bas
pour marcher cent coutures. ⚠ Le bloc est celui de `257`, où le segment passe entre deux feuilles.

Usage :
    uv run python src/nappe/le_pas_de_centre_a_centre_voit_il_la_rampe.py --verifier
    uv run python src/nappe/le_pas_de_centre_a_centre_voit_il_la_rampe.py \\
        --json docs/mesures/le_pas_de_centre_a_centre_voit_il_la_rampe.json
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

from combien_de_rangees_faut_il_pour_lire_le_pas import (LES_RANGEES, le_pas_de_k_rangees,  # noqa: E402
                                                         les_rangees_a_lire, un_chunk_retenu)
from la_spire_produite_se_lit_elle_dans_le_treillis import (LA_RAMPE_EN_CHUNKS, LE_BLOC, LE_COTE_DU_CHUNK,  # noqa: E402
                                                            LE_DOSSIER, LE_DOSSIER_DE_LA_RAMPE, laccord_des_paires,
                                                            la_marche_du_bloc, la_part_retrouvee, le_meta,
                                                            les_pas_du_bloc, lire_la_pile, servir)
from la_spire_voisine_est_elle_a_un_pas import LE_SEGMENT  # noqa: E402

CE_QUE_257_A_PUBLIE = RACINE / "docs" / "mesures" / "la_spire_produite_se_lit_elle_dans_le_treillis.json"
LES_PILES = {"le_segment_reduit": "le_segment_reduit", "la_spire_produite": "la_spire_produite",
             "la_rampe_posee": LE_DOSSIER_DE_LA_RAMPE}
LE_SEUIL_DE_LA_RAMPE = 0.5
LA_RAMPE_NUMERIQUE = 24.0   # voxels : un tiers de pas, pour ne pousser hors de la pile qu'un quart de ses couches


def les_profils_entiers(b: np.ndarray, coupes) -> tuple[dict, dict]:
    """Les profils d'un chunk moyennés sur le chunk ENTIER : le long de chaque rangée de coupe (pour les pas le long des
    rangées), et le long de chaque colonne de coupe (pour les pas entre rangées)."""
    b = np.asarray(b, dtype=float)
    par_rangee = {int(r): b[:, int(r), :].mean(axis=1) for r in coupes}
    par_colonne = {int(c): b[:, :, int(c)].mean(axis=1) for c in coupes}
    return par_rangee, par_colonne


def les_pas_de_centre(ouvrir, by: int, bx: int, cote: int, combien: int = LES_RANGEES) -> dict:
    """Les pas de centre à centre de toutes les coutures du bloc, au format de `257` : `h[r][c]` et `v[r][c]`."""
    coupes = les_rangees_a_lire(LE_COTE_DU_CHUNK, combien)
    prof, refus = {}, {}
    for r in range(by, by + cote):
        for c in range(bx, bx + cote):
            b, pourquoi, _ = un_chunk_retenu(ouvrir, r, c)
            if b is None:
                refus[pourquoi] = refus.get(pourquoi, 0) + 1
                continue
            prof[(r, c)] = les_profils_entiers(b, coupes)
    h, v = {}, {}
    for (r, c), (pr, pc) in prof.items():
        if (r, c + 1) in prof:
            x = le_pas_de_k_rangees(pr, prof[(r, c + 1)][0], coupes)
            if x.get("decidable"):
                h.setdefault(r, {})[c] = (float(x["le_pas_en_voxels"]), float(x["le_desaccord_en_voxels"]),
                                          int(x["les_rangees"]))
        if (r + 1, c) in prof:
            x = le_pas_de_k_rangees(pc, prof[(r + 1, c)][1], coupes)
            if x.get("decidable"):
                v.setdefault(r, {})[c] = (float(x["le_pas_en_voxels"]), float(x["le_desaccord_en_voxels"]),
                                          int(x["les_rangees"]))
    return {"h": h, "v": v, "les_chunks_lus": len(prof), "les_refus": refus}


def la_pile_decalee(pile: np.ndarray, hauteur: float, largeur: int = LA_RAMPE_EN_CHUNKS,
                    chunk: int = LE_COTE_DU_CHUNK) -> tuple[np.ndarray, np.ndarray]:
    """La rampe NUMÉRIQUE : la même pile, chaque rangée de pixels décalée en profondeur de la rampe, entière, en
    prolongeant le bord. La matière ne change pas, seule sa profondeur ; rend aussi la rampe au centre de chaque chunk."""
    cote = pile.shape[1] // chunk
    yy = np.arange(pile.shape[1], dtype=float)
    y0 = (cote // 2 - largeur // 2) * chunk
    s = np.round(np.clip((yy - y0) / float(largeur * chunk), 0.0, 1.0) * float(hauteur)).astype(int)
    z = np.arange(pile.shape[0])
    out = np.empty_like(pile)
    for y in range(pile.shape[1]):
        out[:, y, :] = pile[np.clip(z - s[y], 0, pile.shape[0] - 1), y, :]
    centres = np.clip((np.arange(cote) * chunk + chunk / 2.0 - y0) / float(largeur * chunk), 0.0, 1.0) * float(hauteur)
    return out, np.broadcast_to(centres[:, None], (cote, cote)).copy()


def la_grille(liste) -> np.ndarray:
    return np.array([[np.nan if x is None else float(x) for x in r] for r in liste])


def en_liste(a: np.ndarray) -> list:
    return [[None if not np.isfinite(x) else round(float(x), 2) for x in r] for r in a]


def mesurer() -> dict:
    d = json.loads(CE_QUE_257_A_PUBLIE.read_text())
    by, bx = d["le_bloc"]["la_rangee"], d["le_bloc"]["la_colonne"]
    erreur, rampe = la_grille(d["les_cartes"]["lerreur"]), la_grille(d["les_cartes"]["la_rampe"])
    out = {"le_bloc": {"la_rangee": by, "la_colonne": bx, "le_cote": LE_BLOC}, "les_piles": {}}
    marches = {}
    for nom, dossier in LES_PILES.items():
        chemin = LE_DOSSIER / dossier / f"bloc_{by}_{bx}"
        if not chemin.is_dir():
            return {**out, "decidable": False, "la_raison": f"la pile {nom} de 257 n'est pas sur le disque : {chemin}"}
        lu = les_pas_de_centre(servir(lire_la_pile(chemin), by, bx), by, bx, LE_BLOC)
        m = la_marche_du_bloc(lu["h"], lu["v"], by, bx, LE_BLOC)
        prof = m.pop("la_profondeur")
        marches[nom] = prof
        des = [abs(x[1]) for s in (lu["h"], lu["v"]) for t in s.values() for x in t.values()]
        out["les_piles"][nom] = {"les_chunks_lus": lu["les_chunks_lus"], "les_refus": lu["les_refus"], "la_marche": m,
                                 "letendue_de_la_marche_voxels": (round(float(np.nanmax(prof) - np.nanmin(prof)), 4)
                                                                  if np.isfinite(prof).any() else None),
                                 "le_desaccord_median_voxels": round(float(np.median(des)), 4) if des else None}
    out["ce_que_la_marche_retrouve_de_la_rampe"] = la_part_retrouvee(marches["la_rampe_posee"],
                                                                      marches["le_segment_reduit"], rampe)
    # ⚠⚠ AJOUTÉ APRÈS LA PREMIÈRE MESURE : la rampe rendue pousse la surface sur d'AUTRES feuilles, dont la géométrie n'est
    # pas celle du segment ; la rampe numérique décale la même matière, donc sa réponse est connue au voxel près.
    reduite = lire_la_pile(LE_DOSSIER / "le_segment_reduit" / f"bloc_{by}_{bx}")
    decalee, pose = la_pile_decalee(reduite, LA_RAMPE_NUMERIQUE)
    lu = les_pas_de_centre(servir(decalee, by, bx), by, bx, LE_BLOC)
    m = la_marche_du_bloc(lu["h"], lu["v"], by, bx, LE_BLOC)
    num = {"la_hauteur_voxels": LA_RAMPE_NUMERIQUE,
           "de_centre_a_centre": la_part_retrouvee(m["la_profondeur"], marches["le_segment_reduit"], pose)}
    meta, vol = le_meta((109, 50600, 36400)), {"cle": "rendu local", "segment": LE_SEGMENT}
    temoin = les_pas_du_bloc(by, bx, LE_BLOC, servir(reduite, by, bx), meta, vol)
    couture = les_pas_du_bloc(by, bx, LE_BLOC, servir(decalee, by, bx), meta, vol)
    if temoin.get("decidable") and couture.get("decidable"):
        mt = la_marche_du_bloc(temoin["le_long"], temoin["en_travers"], by, bx, LE_BLOC)["la_profondeur"]
        mc = la_marche_du_bloc(couture["le_long"], couture["en_travers"], by, bx, LE_BLOC)["la_profondeur"]
        num["a_la_couture"] = la_part_retrouvee(mc, mt, pose)
    out["la_rampe_numerique"] = num
    out["ce_que_la_marche_des_coutures_en_retrouvait"] = d["ce_que_la_marche_retrouve_de_la_rampe"]
    diff = marches["la_spire_produite"] - marches["le_segment_reduit"]
    out["la_difference_des_marches"] = {"laccord_des_paires": laccord_des_paires(diff, erreur),
                                        "letendue_voxels": (round(float(np.nanmax(diff) - np.nanmin(diff)), 4)
                                                            if np.isfinite(diff).any() else None)}
    out["le_temoin_plat"] = laccord_des_paires(np.zeros_like(erreur), erreur)
    dc = la_grille(d["les_cartes"]["la_spire_produite"]) - la_grille(d["les_cartes"]["le_segment_reduit"])
    out["la_difference_des_marches_des_coutures"] = {"laccord_des_paires": laccord_des_paires(dc, erreur),
                                                     "letendue_voxels": round(float(np.nanmax(dc) - np.nanmin(dc)), 4)}
    # ⚠ Ajouté après la première mesure, pour décrire et non pour juger : la pente de la différence contre l'erreur.
    out["la_difference_des_marches"]["contre_lerreur_jugee"] = la_part_retrouvee(marches["la_spire_produite"],
                                                                                marches["le_segment_reduit"], erreur)
    out["les_cartes"] = {"lerreur": en_liste(erreur), "la_rampe": en_liste(rampe),
                         **{k: en_liste(v) for k, v in marches.items()}, "la_difference": en_liste(diff),
                         "la_difference_des_coutures": en_liste(dc),
                         "le_segment_reduit_des_coutures": d["les_cartes"]["le_segment_reduit"]}
    out["decidable"] = True
    return out


def le_verdict(r: dict) -> dict:
    z = r.get("ce_que_la_marche_retrouve_de_la_rampe") or {}
    if not r.get("decidable") or not z.get("decidable") or z["la_pente"] < LE_SEUIL_DE_LA_RAMPE:
        return {"lissue": "le pas de centre à centre ne voit pas la rampe : il n'y a pas encore d'instrument"}
    a = (r.get("la_difference_des_marches") or {}).get("laccord_des_paires") or {}
    sep = a.get("la_part_que_la_marche_separe_parmi_celles_que_le_juge_separe") or 0.0
    reu = a.get("la_part_que_la_marche_reunit_parmi_celles_que_le_juge_reunit") or 0.0
    if sep <= 0.5 or sep + reu <= 1.0:
        return {"lissue": "il voit la rampe, et la différence des marches ne sépare pas mieux que le témoin : sur ce bloc, "
                          "la spire produite ne dérive pas là où le juge la dit ratée, ou le juge se trompe",
                "separe": sep, "reunit": reu}
    return {"lissue": "il voit la rampe, et elle sépare : le treillis, lu de centre à centre, juge une spire que la chaîne "
                      "a produite", "separe": sep, "reunit": reu}


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

    # Une pile fabriquée : des feuilles tous les 72 couches, un pas ; la surface dérive de 3 couches par chunk le long
    # des rangées, PROGRESSIVEMENT à l'intérieur de chaque chunk, sans aucun saut à la couture.
    rng = np.random.default_rng(1)
    couches, cote = 109, 4
    y = np.arange(couches)[:, None, None]
    xs = np.arange(cote * LE_COTE_DU_CHUNK)[None, None, :]
    derive = 3.0 * xs / LE_COTE_DU_CHUNK
    pile = 100.0 + 80.0 * np.cos(2 * np.pi * (y - derive) / 72.0) + rng.normal(0, 4, (couches, cote * LE_COTE_DU_CHUNK, 1))
    pile = np.clip(np.broadcast_to(pile, (couches, cote * LE_COTE_DU_CHUNK, cote * LE_COTE_DU_CHUNK)), 1, 255)
    pile = pile.astype(np.uint8)
    lu = les_pas_de_centre(servir(pile, 10, 20), 10, 20, cote)
    hs = [x[0] for s in lu["h"].values() for x in s.values()]
    vs = [x[0] for s in lu["v"].values() for x in s.values()]
    v("★★★★ le pas de centre à centre lit la dérive d'un chunk entier, sans saut à la couture",
      lambda: len(hs) == 12 and all(abs(abs(x) - 3.0) < 0.6 for x in hs), str(hs[:4]))
    v("★★★★ et rien entre rangées, où la surface ne dérive pas", lambda: len(vs) == 12 and all(abs(x) < 0.6 for x in vs),
      str(vs[:4]))
    from combien_de_rangees_faut_il_pour_lire_le_pas import les_bords_droit_et_gauche
    co = les_rangees_a_lire(LE_COTE_DU_CHUNK)
    dr, _ = les_bords_droit_et_gauche(pile[:, :128, :128], co, 16)
    _, ga = les_bords_droit_et_gauche(pile[:, :128, 128:256], co, 16)
    couture = le_pas_de_k_rangees(dr, ga, co)
    v("★★★★ sur la même pile, le pas à la couture de `199` n'en voit qu'un huitième : il ne voit que ce qui saute",
      lambda: abs(couture["le_pas_en_voxels"]) < 1.0, str(couture.get("le_pas_en_voxels")))
    m = la_marche_du_bloc(lu["h"], lu["v"], 10, 20, cote)
    v("★★★ la marche en tire une pente d'un chunk à l'autre", lambda: abs(abs(np.nanmean(np.diff(m["la_profondeur"], axis=1))) - 3.0) < 0.6)
    pr, pc = les_profils_entiers(pile[:, :128, :128], [8, 24])
    v("★★★ un profil entier est la moyenne de toute la coupe",
      lambda: np.allclose(pr[8], pile[:, 8, :128].astype(float).mean(axis=1)) and np.allclose(pc[24], pile[:, :128, 24].astype(float).mean(axis=1)))
    vide = np.zeros_like(pile)
    lu0 = les_pas_de_centre(servir(vide, 10, 20), 10, 20, cote)
    v("★★★ un chunk vide est refusé par le filtre du dépôt, et compté", lambda: lu0["les_chunks_lus"] == 0 and lu0["les_refus"].get("vide") == 16)
    v("★★★★ le verdict refuse un pas qui ne voit pas la rampe",
      lambda: "ne voit pas" in le_verdict({"decidable": True, "ce_que_la_marche_retrouve_de_la_rampe": {"decidable": True, "la_pente": 0.2}})["lissue"])
    plat = laccord_des_paires(np.zeros((4, 4)), np.where(np.arange(16).reshape(4, 4) % 4 >= 2, 72.0, 0.0))
    v("★★★ le verdict retient le témoin : une différence plate ne sépare pas",
      lambda: "ne sépare pas" in le_verdict({"decidable": True, "ce_que_la_marche_retrouve_de_la_rampe": {"decidable": True, "la_pente": 0.9},
                                             "la_difference_des_marches": {"laccord_des_paires": plat}})["lissue"])

    pd, pose = la_pile_decalee(pile[:, :512, :512], 24.0)
    v("★★★★ la rampe numérique décale la même matière, de la rampe arrondie, et rend la rampe au centre des chunks",
      lambda: np.array_equal(pd[:, 10, :], pile[:, 10, :512]) and np.array_equal(pd[40:, 500, :], pile[17:86, 500, :512])
      and np.allclose(pose[:, 0], [3.0, 9.0, 15.0, 21.0]) and (pose[:, 0] == pose[:, 3]).all(), str(pose[:, 0]))

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
    print(json.dumps({k: r.get(k) for k in ("ce_que_la_marche_retrouve_de_la_rampe", "le_verdict")}, ensure_ascii=False))
    return 0 if r.get("decidable") else 2


if __name__ == "__main__":
    raise SystemExit(main())
