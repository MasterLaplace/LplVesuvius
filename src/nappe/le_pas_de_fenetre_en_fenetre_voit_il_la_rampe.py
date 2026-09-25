"""Des pas courts, enchaînés de fenêtre en fenêtre à travers le chunk, voient-ils la dérive partout ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UN SEUL PAS DE FENÊTRE EN FENÊTRE NE SOIT LU. Ce qui était vu avant d'écrire : tout ce que
`257`, `258` et `259` publient.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P94`. Le pas à la couture est stable mais ne voit qu'un huitième d'une dérive :
ses deux fenêtres de seize colonnes sont à seize colonnes l'une de l'autre, sur un chunk de cent vingt-huit (`257`). Le pas de
centre à centre voit toute la dérive sur un bloc et presque rien sur un autre, où les feuilles ondulent (`258`, `259`).
Entre les deux : la même fenêtre de seize colonnes que la couture, mais comparée à sa voisine à chaque fenêtre du chunk, et
les huit pas d'un centre de chunk au suivant additionnés. Chaque pas est aussi court que celui de la couture, donc suit une
feuille qui ondule ; leur somme voit toute la dérive.

## Le pas

⚠⚠ Il est FIN, et c'est le seul écart à l'estimateur de `199` : un pas de fenêtre en fenêtre vaut une fraction de voxel quand
la dérive est lente, et huit pas arrondis au voxel près additionnent huit arrondis, souvent zéro. Le sommet de la corrélation,
la même que celle de `199`, est affiné par la parabole qui passe par ses trois points ; arrondi, il rend le pas de `199`.
Pour chaque rangée de coupe de `224`, la somme des huit pas de la fenêtre centrale d'un chunk à celle du suivant ; puis la
moyenne sur les seize rangées, comme `224` moyenne ses estimations.

## Ce qui se mesure

1. LA RAMPE NUMÉRIQUE de `258` (24 voxels, la même matière décalée), sur les trois piles déjà lues : le segment réduit du bloc
   de `257`, le segment réduit du bloc de `259`, et la pile publiée du bloc de `259`. ⭐ Déclaré : il voit la rampe s'il en
   retrouve au moins un demi sur les TROIS.
2. LE BRUIT : l'étendue de la marche du segment lui-même, et le résidu des moindres carrés, sur les deux blocs.
3. LA SPIRE PRODUITE : la différence de sa marche et de celle du segment contre l'erreur jugée, sur les deux blocs.

## Les issues, exclusives

- il ne voit pas la rampe sur l'une des trois piles au moins : pas d'instrument ;
- il la voit, et sur aucun des deux blocs la différence ne sépare mieux que le témoin : il ne juge pas la spire produite ;
- il la voit, et elle sépare sur un bloc au moins : il juge la spire produite là.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : une boucle, un autre côté, `ps256`, ni comment le bruit s'accumule sur cent coutures.

Usage :
    uv run python src/nappe/le_pas_de_fenetre_en_fenetre_voit_il_la_rampe.py --verifier
    uv run python src/nappe/le_pas_de_fenetre_en_fenetre_voit_il_la_rampe.py \\
        --json docs/mesures/le_pas_de_fenetre_en_fenetre_voit_il_la_rampe.json
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

from combien_de_rangees_faut_il_pour_lire_le_pas import (LES_RANGEES, le_pas_dune_rangee,  # noqa: E402
                                                         les_rangees_a_lire, un_chunk_retenu)
from la_spire_produite_se_lit_elle_dans_le_treillis import (LE_BLOC, LE_COTE_DU_CHUNK, LE_DOSSIER,  # noqa: E402
                                                            laccord_des_paires, la_marche_du_bloc,
                                                            la_part_retrouvee, lire_la_pile, servir)
from la_spire_voisine_est_elle_a_un_pas import DEMI_PAS_EN_VOXELS  # noqa: E402
from le_pas_de_centre_a_centre_la_ou_le_segment_tient_sa_feuille import la_pile_publiee  # noqa: E402
from le_pas_de_centre_a_centre_voit_il_la_rampe import LA_RAMPE_NUMERIQUE, la_pile_decalee  # noqa: E402

LA_FENETRE = 16   # la largeur de bord de `199`, dérivée et publiée
LE_SEUIL_DE_LA_RAMPE = 0.5
LES_MESURES = RACINE / "docs" / "mesures"
LES_BLOCS = {"le_bloc_de_257": ("la_spire_produite_se_lit_elle_dans_le_treillis.json", "les_cartes", "lerreur"),
             "le_bloc_de_259": ("le_pas_de_centre_a_centre_la_ou_le_segment_tient_sa_feuille.json", "les_cartes", "lerreur")}


def le_pas_fin(a: np.ndarray, b: np.ndarray, plage: int = DEMI_PAS_EN_VOXELS) -> float | None:
    """Le décalage qui aligne `b` sur `a`, au signe de `199`, affiné par la parabole du sommet de la corrélation.

    ⚠ La corrélation est EXACTEMENT celle de `199` (normalisée par l'énergie des deux fenêtres) : seul le sommet est affiné.
    """
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    a, b = a - a.mean(), b - b.mean()
    if float(np.dot(a, a)) <= 0.0 or float(np.dot(b, b)) <= 0.0:
        return None
    p = int(min(int(plage), (len(a) - 1) // 2))
    if p < 1:
        return None
    sc = []
    for k in range(-p, p + 1):
        aa = a[max(0, k):len(a) + min(0, k)]
        bb = b[max(0, -k):len(b) + min(0, -k)]
        e = float(np.dot(aa, aa)) * float(np.dot(bb, bb))
        sc.append(float(np.dot(aa, bb)) / (e ** 0.5) if e > 0.0 else -1.0)
    i = int(np.argmax(sc))
    d = 0.0
    if 0 < i < len(sc) - 1:
        y0, y1, y2 = sc[i - 1], sc[i], sc[i + 1]
        den = y0 - 2.0 * y1 + y2
        if den < 0.0:
            d = 0.5 * (y0 - y2) / den
    return -((i + d) - p)


def les_fenetres(section: np.ndarray, largeur: int = LA_FENETRE) -> np.ndarray:
    """Les profils de chaque fenêtre de `largeur` colonnes d'une coupe (couche, colonne) : (couche, fenêtre)."""
    n = section.shape[1] // largeur
    return np.asarray(section[:, :n * largeur], dtype=float).reshape(section.shape[0], n, largeur).mean(axis=2)


def la_somme_des_pas(fa: np.ndarray, fb: np.ndarray) -> float | None:
    """La somme des pas de fenêtre en fenêtre, de la fenêtre centrale de `fa` à celle de `fb`, en passant la couture."""
    f = np.concatenate([fa, fb], axis=1)
    n = fa.shape[1]
    de, a = n // 2, n + n // 2
    total = 0.0
    for j in range(de, a):
        x = le_pas_fin(f[:, j], f[:, j + 1])
        if x is None:
            return None
        total += x
    return total


def les_pas_de_fenetre(ouvrir, by: int, bx: int, cote: int, combien: int = LES_RANGEES) -> dict:
    """Les pas de fenêtre en fenêtre de toutes les coutures du bloc, au format de `257` : `h[r][c]` et `v[r][c]`."""
    coupes = les_rangees_a_lire(LE_COTE_DU_CHUNK, combien)
    fen, refus = {}, {}
    for r in range(by, by + cote):
        for c in range(bx, bx + cote):
            b, pourquoi, _ = un_chunk_retenu(ouvrir, r, c)
            if b is None:
                refus[pourquoi] = refus.get(pourquoi, 0) + 1
                continue
            b = np.asarray(b, dtype=float)
            fen[(r, c)] = ({int(k): les_fenetres(b[:, int(k), :]) for k in coupes},
                           {int(k): les_fenetres(b[:, :, int(k)]) for k in coupes})
    h, v = {}, {}
    for (r, c), (fr, fc) in fen.items():
        for sens, voisin, mien, d in (("h", (r, c + 1), fr, h), ("v", (r + 1, c), fc, v)):
            if voisin not in fen:
                continue
            autre = fen[voisin][0 if sens == "h" else 1]
            lus = [la_somme_des_pas(mien[k], autre[k]) for k in coupes]
            lus = [x for x in lus if x is not None]
            if len(lus) < 2:
                continue
            d.setdefault(r, {})[c] = (float(np.mean(lus)), float(np.mean(lus[0::2]) - np.mean(lus[1::2])), len(lus))
    return {"h": h, "v": v, "les_chunks_lus": len(fen), "les_refus": refus}


def la_grille(liste) -> np.ndarray:
    return np.array([[np.nan if x is None else float(x) for x in r] for r in liste])


def la_marche(pile: np.ndarray, by: int, bx: int) -> dict:
    lu = les_pas_de_fenetre(servir(pile, by, bx), by, bx, LE_BLOC)
    m = la_marche_du_bloc(lu["h"], lu["v"], by, bx, LE_BLOC)
    return {**m, "les_chunks_lus": lu["les_chunks_lus"]}


def letendue(a):
    return round(float(np.nanmax(a) - np.nanmin(a)), 4) if np.isfinite(a).any() else None


def la_pile_publiee_en_cache(by: int, bx: int) -> np.ndarray | None:
    """La pile publiée d'un bloc, gardée sur le disque de travail après la première lecture."""
    f = LE_DOSSIER / "la_publiee" / f"bloc_{by}_{bx}.npy"
    if f.exists():
        return np.load(f)
    p = la_pile_publiee(by, bx)
    if p is not None:
        f.parent.mkdir(parents=True, exist_ok=True)
        np.save(f, p)
    return p


def mesurer() -> dict:
    out = {"la_fenetre_en_colonnes": LA_FENETRE, "les_blocs": {}, "la_rampe_numerique": {}}
    for nom, (fichier, cle, carte) in LES_BLOCS.items():
        d = json.loads((LES_MESURES / fichier).read_text())
        by, bx = d["le_bloc"]["la_rangee"], d["le_bloc"]["la_colonne"]
        erreur = la_grille(d[cle][carte])
        piles = {n: lire_la_pile(LE_DOSSIER / n / f"bloc_{by}_{bx}") for n in ("le_segment_reduit", "la_spire_produite")}
        ms, mp = la_marche(piles["le_segment_reduit"], by, bx), la_marche(piles["la_spire_produite"], by, bx)
        ps, pp = ms.pop("la_profondeur"), mp.pop("la_profondeur")
        diff = pp - ps
        decalee, pose = la_pile_decalee(piles["le_segment_reduit"], LA_RAMPE_NUMERIQUE)
        md = la_marche(decalee, by, bx)
        out["la_rampe_numerique"][f"{nom}_segment_reduit"] = la_part_retrouvee(md.pop("la_profondeur"), ps, pose)
        out["les_blocs"][nom] = {"la_rangee": by, "la_colonne": bx,
                                 "le_segment": {**ms, "letendue_voxels": letendue(ps)},
                                 "la_spire_produite": {**mp, "letendue_voxels": letendue(pp)},
                                 "la_difference": {"letendue_voxels": letendue(diff),
                                                   "laccord_des_paires": laccord_des_paires(diff, erreur),
                                                   "contre_lerreur_jugee": la_part_retrouvee(pp, ps, erreur)},
                                 "le_temoin_plat": laccord_des_paires(np.zeros_like(erreur), erreur),
                                 "les_cartes": {k: [[None if not np.isfinite(x) else round(float(x), 2) for x in r]
                                                    for r in a] for k, a in (("lerreur", erreur), ("le_segment", ps),
                                                                             ("la_difference", diff))}}
        if nom == "le_bloc_de_259":
            pub = la_pile_publiee_en_cache(by, bx)
            if pub is None:
                return {**out, "decidable": False, "la_raison": "la pile publiée du bloc de 259 ne répond pas"}
            mpub = la_marche(pub, by, bx)
            ppub = mpub.pop("la_profondeur")
            dpub, pose_pub = la_pile_decalee(pub, LA_RAMPE_NUMERIQUE)
            mdp = la_marche(dpub, by, bx)
            out["la_rampe_numerique"][f"{nom}_pile_publiee"] = la_part_retrouvee(mdp.pop("la_profondeur"), ppub, pose_pub)
            out["les_blocs"][nom]["la_pile_publiee"] = {**mpub, "letendue_voxels": letendue(ppub)}
    out["decidable"] = True
    return out


def le_verdict(r: dict) -> dict:
    if not r.get("decidable"):
        return {"lissue": "indécidable"}
    pentes = [z.get("la_pente") for z in r["la_rampe_numerique"].values()]
    if len(pentes) < 3 or any(p is None or p < LE_SEUIL_DE_LA_RAMPE for p in pentes):
        return {"lissue": "il ne voit pas la rampe sur l'une des trois piles au moins : pas d'instrument", "les_pentes": pentes}
    separe = []
    for nom, b in r["les_blocs"].items():
        a = b["la_difference"]["laccord_des_paires"]
        s = a.get("la_part_que_la_marche_separe_parmi_celles_que_le_juge_separe") or 0.0
        u = a.get("la_part_que_la_marche_reunit_parmi_celles_que_le_juge_reunit") or 0.0
        if s > 0.5 and s + u > 1.0:
            separe.append(nom)
    if not separe:
        return {"lissue": "il voit la rampe, et sur aucun des deux blocs la différence ne sépare mieux que le témoin : il ne "
                          "juge pas la spire produite", "les_pentes": pentes}
    return {"lissue": f"il voit la rampe, et elle sépare sur {', '.join(separe)} : il juge la spire produite là",
            "les_pentes": pentes}


def verifier() -> int:
    from la_derive_saccumule_t_elle import un_pas

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

    rng = np.random.default_rng(3)
    ecarts = []
    for _ in range(200):
        a, b = rng.normal(size=109), rng.normal(size=109)
        fin = le_pas_fin(a, b)
        ent = un_pas(a.reshape(-1, 1), b.reshape(-1, 1), 1)["le_pas_en_voxels"]
        ecarts.append(abs(fin - ent))
    v("★★★★ arrondi, le pas fin rend le pas de 199 : même corrélation, seul le sommet est affiné",
      lambda: max(ecarts) <= 0.5 + 1e-9, str(max(ecarts)))
    z = np.arange(109.0)
    prof = lambda s: np.exp(-0.5 * ((z - 54.0 - s) / 6.0) ** 2) + 0.5 * np.exp(-0.5 * ((z - 20.0 - s) / 5.0) ** 2)  # noqa: E731
    v("★★★★ le pas fin retrouve une fraction de voxel, au signe de 199",
      lambda: abs(le_pas_fin(prof(0.0), prof(1.4)) - 1.4) < 0.25 and un_pas(prof(0.0).reshape(-1, 1), prof(3.0).reshape(-1, 1), 1)["le_pas_en_voxels"] == 3,
      str(le_pas_fin(prof(0.0), prof(1.4))))
    # Une pile où la feuille ONDULE de quinze couches sur soixante-quatre colonnes, et dérive de six couches par chunk.
    couches, cote = 109, 4
    y = np.arange(couches)[:, None, None]
    xs = np.arange(cote * LE_COTE_DU_CHUNK)[None, None, :]
    ondule = 15.0 * np.sin(2 * np.pi * xs / 64.0)
    derive = 6.0 * xs / LE_COTE_DU_CHUNK
    bruit = rng.normal(0, 3, (couches, cote * LE_COTE_DU_CHUNK, 1))
    pile = 100 + 80 * np.cos(2 * np.pi * (y - derive - ondule) / 72.0) + bruit
    pile = np.clip(np.broadcast_to(pile, (couches, cote * LE_COTE_DU_CHUNK, cote * LE_COTE_DU_CHUNK)), 1, 255).astype(np.uint8)
    lu = les_pas_de_fenetre(servir(pile, 10, 20), 10, 20, cote)
    hs = [x[0] for s in lu["h"].values() for x in s.values()]
    vs = [x[0] for s in lu["v"].values() for x in s.values()]
    v("★★★★ sur une feuille qui ondule, les pas de fenêtre en fenêtre additionnent la dérive d'un chunk",
      lambda: len(hs) == 12 and abs(abs(np.mean(hs)) - 6.0) < 1.0, f"{np.mean(hs) if hs else None}")
    v("★★★★ et rien entre rangées, où la surface ne dérive pas", lambda: len(vs) == 12 and abs(np.mean(vs)) < 1.0,
      f"{np.mean(vs) if vs else None}")
    from le_pas_de_centre_a_centre_voit_il_la_rampe import les_pas_de_centre
    lc = les_pas_de_centre(servir(pile, 10, 20), 10, 20, cote)
    hc = [x[0] for s in lc["h"].values() for x in s.values()]
    # ⚠ Écrite d'abord pour affirmer que le pas de centre à centre s'y trompe, cette sonde a échoué : une ondulation
    # régulière ne le trompe pas. Elle dit désormais ce qui est vrai, et la cause de `259` n'est pas reproduite ici.
    v("★★★ sur la même pile, les pas de centre à centre de 258 la voient aussi : une ondulation régulière ne les trompe pas",
      lambda: abs(abs(np.mean(hc)) - 6.0) < 1.0, f"{np.mean(hc)}")
    fa = np.zeros((109, 8))
    v("★★★ une fenêtre plate rend le pas indéfini, jamais zéro", lambda: la_somme_des_pas(fa, fa) is None)
    base = {"decidable": True, "la_rampe_numerique": {"a": {"la_pente": 0.9}, "b": {"la_pente": 0.8}, "c": {"la_pente": 0.4}},
            "les_blocs": {}}
    v("★★★★ une seule pile où la rampe n'est pas retrouvée suffit : pas d'instrument",
      lambda: "pas d'instrument" in le_verdict(base)["lissue"])
    base["la_rampe_numerique"]["c"]["la_pente"] = 0.7
    base["les_blocs"] = {"x": {"la_difference": {"laccord_des_paires": {
        "la_part_que_la_marche_separe_parmi_celles_que_le_juge_separe": 0.2,
        "la_part_que_la_marche_reunit_parmi_celles_que_le_juge_reunit": 0.9}}}}
    v("★★★ il voit la rampe, sans séparer : il ne juge pas", lambda: "ne juge pas" in le_verdict(base)["lissue"])

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
    print(json.dumps({k: r.get(k) for k in ("la_rampe_numerique", "le_verdict")}, ensure_ascii=False))
    return 0 if r.get("decidable") else 2


if __name__ == "__main__":
    raise SystemExit(main())
