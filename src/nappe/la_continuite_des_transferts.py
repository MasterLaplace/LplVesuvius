#!/usr/bin/env python3
"""Les transferts que l'humain a reussis sont-ils CONTINUS ? Oui au coeur, non au bord.

⚠⚠⚠ POURQUOI CETTE QUESTION EST CELLE DU GOULOT. `91` etablit que les 28 bandes de
`PHercParis4` sont des transferts de spire a spire deja faits a la main, et que leur etendue
declaree EST leur nombre de tours. Reste a savoir ce que l'humain a REELLEMENT produit : une
nappe continue qui derive de feuille en feuille, ou une couture de morceaux ?

⭐⭐⭐ MESURE, ET ELLE COUPE LE CORPUS EN DEUX SANS SEUIL CHOISI. Le plus grand saut entre deux
cellules VOISINES d'une meme ligne de grille, rapporte au pas d'echantillonnage, vaut **1,1 a
2,6** sur les onze bandes les plus internes et monte **jusqu'a 41** sur les plus externes. La
progression est reguliere : 1,2 · 2,1 · 3,9 · 6,7 · 8,8 · 22 · 41. **La verite de terrain se
degrade progressivement vers l'exterieur.**

⭐⭐ CE QUE CA DIT DU REMPLACANT DE L'HUMAIN, et c'est une borne sur ce qu'on peut lui demander :
la ou le rouleau est intact, un humain trace **continument** ; la ou il ne l'est pas, **meme un
humain** rend une surface discontinue. Un automate ne peut donc pas etre juge sur les bandes
externes comme sur les internes — et l'etendue qui tombe de 18 a 2 spires (`84`) n'est pas
seulement la circonference qui croit, c'est aussi la continuite qui casse.

⚠⚠ UNE PREMIERE LECTURE, FAUSSE, EST GARDEE ICI. J'ai d'abord vu les sauts sur les lignes 3, 4 et
181 d'une grille de 198 et conclu « effilochage du bord du maillage ». Le test structurel les
GARDE : une cellule est dite interieure quand ses **quatre** voisines de grille sont valides, ce
qui ne depend d'aucune marge choisie, et les sauts de trente millimetres y survivent. Ils sont
donc dans de la matiere reellement maillee.

⚠⚠⚠ ET UNE SECONDE LECTURE, REFUTEE PAR LE TEST DIRECT. Les sauts correlent fortement avec le
gonflement de pente que `91` n'expliquait pas — **r = 0,796**, et 0,870 en log-log ; les bandes a
saut inferieur a cinq millimetres rendent 173 µm de pente mediane, les autres 393. J'ai failli
publier la cause. Mais **retirer les lignes qui contiennent un saut change la pente de moins de
1 %** (941,1 → 932,5 · 1160,0 → 1143,0). Les deux grandeurs croissent vers l'exterieur, et
**aucune ne cause l'autre** : c'est un confondant, pas un mecanisme.

⚠ Donc la cause du gonflement de `91` reste NON TROUVEE, avec desormais **trois** candidats
refutes : section ovale (elle degonfle), centre decale (dix fois trop faible), sauts (moins de
1 % d'effet). Le controle de fenetre de `91` tient toujours sans elle.

Usage :
    uv run python src/nappe/la_continuite_des_transferts.py --verifier
    uv run python src/nappe/la_continuite_des_transferts.py \\
        --json docs/mesures/la_continuite_des_transferts.json
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
sys.path.insert(0, str(RACINE / "src" / "depot"))

# ⚠ Au-dela de cette distance, un pas entre cellules voisines n'est plus un pas d'echantillonnage
# mais une rupture. Le seuil est DERIVE : le pas median vaut ~910 µm sur les 28 bandes, donc cinq
# millimetres valent cinq fois et demie le pas — bien au-dela de toute dispersion normale, et bien
# en deca des trente millimetres observes. Il ne sert qu'a COMPTER les ruptures ; le verdict, lui,
# porte sur le rapport au pas median, qui n'a aucun seuil.
RUPTURE_UM = 5000.0


def cellules_interieures(ok: np.ndarray) -> np.ndarray:
    """Les cellules dont les QUATRE voisines de grille sont valides.

    ⭐⭐ C'EST UNE DEFINITION STRUCTURELLE, PAS UNE MARGE CHOISIE. Ma premiere lecture attribuait
    les sauts a l'effilochage du bord, sur la foi de leurs indices de ligne ; il fallait un test
    qui ne depende d'aucune distance au bord. Une cellule entouree de quatre voisines valides est
    dans de la matiere maillee, ou qu'elle soit dans la grille.
    """
    out = np.zeros_like(ok)
    out[1:-1, 1:-1] = (ok[1:-1, 1:-1] & ok[:-2, 1:-1] & ok[2:, 1:-1]
                       & ok[1:-1, :-2] & ok[1:-1, 2:])
    return out


def sauts(a: np.ndarray, ok: np.ndarray, voxel_um: float) -> dict:
    """Les distances entre cellules voisines d'une meme ligne, toutes puis interieures.

    ⚠ Le RAPPORT au pas median est le verdict, parce qu'il n'a pas d'unite a choisir : une
    surface continue echantillonnee regulierement rend un rapport proche de un, quelle que soit
    la finesse du maillage.
    """
    pas = np.linalg.norm(a[:, 1:] - a[:, :-1], axis=-1) * voxel_um
    tous = ok[:, 1:] & ok[:, :-1]
    it = cellules_interieures(ok)
    dedans = it[:, 1:] & it[:, :-1]
    if not dedans.any():
        return {}
    dt, dd = pas[tous], pas[dedans]
    return {
        "pas_median_um": round(float(np.median(dd)), 0),
        "saut_max_toutes_um": round(float(dt.max()), 0),
        "saut_max_interieur_um": round(float(dd.max()), 0),
        # ⭐ LE VERDICT, sans unite a choisir.
        "rapport_interieur": round(float(dd.max() / np.median(dd)), 1),
        "ruptures_interieures": int((dd > RUPTURE_UM).sum()),
        "part_des_paires": round(float((dd > RUPTURE_UM).mean()), 6),
        "part_interieure": round(float(dedans.sum() / max(1, tous.sum())), 3),
    }


def pente_sans_les_sauts(a: np.ndarray, ok: np.ndarray, bords: np.ndarray, cx: np.ndarray,
                         cy: np.ndarray, voxel_um: float) -> dict:
    """La pente de `91`, calculee avec puis SANS les lignes qui contiennent une rupture.

    ⚠⚠⚠ C'EST LE TEST QUI REFUTE LA CAUSE QUE LA CORRELATION SUGGERAIT. Une correlation de 0,80
    entre deux grandeurs qui croissent toutes deux vers l'exterieur ne dit rien du mecanisme ;
    retirer la cause supposee et regarder si l'effet bouge, si.
    """
    H, W = ok.shape
    i = np.clip(np.searchsorted(bords, a[..., 2], side="right") - 1, 0, cx.size - 1)
    rad = np.hypot(a[..., 0] - cx[i], a[..., 1] - cy[i]) * voxel_um / 1000.0
    ang = np.arctan2(a[..., 1] - cy[i], a[..., 0] - cx[i])
    pas = np.linalg.norm(a[:, 1:] - a[:, :-1], axis=-1) * voxel_um
    toutes: list[float] = []
    propres: list[float] = []
    for r in range(H):
        m = ok[r]
        if int(m.sum()) < 0.8 * W:
            continue
        idx = np.flatnonzero(m)
        aa = np.unwrap(ang[r][m])
        if float(aa.max() - aa.min()) < 0.5 * 2 * np.pi:
            continue
        p = abs(float(np.polyfit(aa, rad[r][m], 1)[0])) * 2 * np.pi * 1000.0
        toutes.append(p)
        v = np.diff(idx) == 1
        rompue = bool((pas[r][idx[:-1]][v] > RUPTURE_UM).any()) if v.any() else False
        if not rompue:
            propres.append(p)
    if not toutes:
        return {}
    return {
        "pente_toutes_lignes_um": round(float(np.median(toutes)), 1),
        "pente_sans_les_sauts_um": round(float(np.median(propres)), 1) if propres else None,
        "lignes": len(toutes), "lignes_sans_saut": len(propres),
    }


def mesurer() -> dict:
    import laxe_est_une_courbe as A  # noqa: PLC0415
    import le_pas_lu_sur_les_transferts as P  # noqa: PLC0415
    import le_sens_du_rang as R  # noqa: PLC0415

    bandes = R.bandes_du_fragment()
    nuages = []
    for x in bandes:
        n = R.points(x["recente"])
        if n is not None and len(n):
            nuages.append(n)
    if len(nuages) < 3:
        return {"message": "cache incomplet : lancer `le_sens_du_rang --telecharger`"}
    tout = np.concatenate(nuages)
    bords, cx, cy, _, _ = A.axe_par_tranche(tout)

    lignes = []
    for x in bandes:
        g = P.grille(x["recente"])
        if g is None:
            continue
        a, ok = g
        s = sauts(a, ok, R.VOXEL_UM)
        if not s:
            continue
        p = pente_sans_les_sauts(a, ok, bords, cx, cy, R.VOXEL_UM)
        lignes.append({"de": x["de"], "a": x["a"], "etendue": x["etendue"], **s, **p})

    rap = [x["rapport_interieur"] for x in lignes]
    n = len(lignes) // 3
    # ⭐ Le corpus se lit en TIERS plutot qu'avec un seuil : les bandes sont deja ordonnees du
    # coeur vers le bord, donc les tiers sont une decoupe de la matiere et non un choix.
    tiers = {"coeur": rap[:n], "milieu": rap[n:2 * n], "bord": rap[2 * n:]}
    avec = [x for x in lignes if x["pente_sans_les_sauts_um"] is not None
            and x["ruptures_interieures"] > 0]
    ecarts = [abs(x["pente_toutes_lignes_um"] - x["pente_sans_les_sauts_um"])
              / max(1e-9, x["pente_toutes_lignes_um"]) for x in avec]
    corr = float(np.corrcoef([x["rapport_interieur"] for x in lignes],
                             [x["pente_toutes_lignes_um"] for x in lignes])[0, 1])
    return {
        "fragment": R.FRAGMENT, "voxel_um": R.VOXEL_UM, "rupture_um": RUPTURE_UM,
        "bandes": len(lignes), "lignes": lignes,
        # ⭐⭐⭐ LA DEGRADATION VERS L'EXTERIEUR, en tiers du corpus.
        "degradation": {k: {"bandes": len(v), "rapport_median": round(float(np.median(v)), 1),
                            "rapport_max": round(float(max(v)), 1)}
                        for k, v in tiers.items() if v},
        "la_continuite_se_degrade_vers_le_bord": bool(
            np.median(tiers["bord"]) > 5 * np.median(tiers["coeur"])),
        # ⚠⚠⚠ LE CONFONDANT, ET SON REFUS.
        "correlation_saut_pente": round(corr, 3),
        "retirer_les_sauts_change_la_pente_de": {
            "bandes_testees": len(avec),
            "ecart_relatif_median": round(float(np.median(ecarts)), 4) if ecarts else None,
            "ecart_relatif_max": round(float(max(ecarts)), 4) if ecarts else None,
        },
        "les_sauts_expliquent_la_pente": bool(ecarts and max(ecarts) > 0.10),
    }


def verifier() -> int:
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  FAIL {nom} — {detail}")

    # --- la mecanique, sur une grille fabriquee ----------------------------------------------
    ok = np.ones((7, 7), dtype=bool)
    it = cellules_interieures(ok)
    v("les bords ne sont jamais intérieurs", not it[0].any() and not it[:, 0].any())
    v("... et le cœur l'est", it[3, 3])
    # ⚠⚠ UN TROU AU MILIEU DESQUALIFIE SES VOISINES, ce qui est le sens de « quatre voisines
    # valides » — et c'est ce qui rend la definition structurelle plutot qu'une marge.
    ok2 = ok.copy()
    ok2[3, 3] = False
    it2 = cellules_interieures(ok2)
    v("un trou désqualifie ses quatre voisines",
      not it2[2, 3] and not it2[4, 3] and not it2[3, 2] and not it2[3, 4])
    v("... sans désqualifier une cellule éloignée", it2[1, 1] if ok2[1, 1] else True)

    # ⚠ Une surface REGULIERE rend un rapport proche de un ; une surface avec une rupture rend
    # un grand rapport. Les deux sont fabriquees, donc la reponse est connue.
    lisse = np.zeros((7, 7, 3))
    for r in range(7):
        lisse[r, :, 0] = np.arange(7) * 20.0
        lisse[r, :, 1] = r * 20.0
    s = sauts(lisse, ok, 45.532)
    v("une surface régulière rend un rapport proche de un",
      abs(s["rapport_interieur"] - 1.0) < 0.01, str(s))
    v("... et ne compte aucune rupture", s["ruptures_interieures"] == 0, str(s))
    rompue = lisse.copy()
    rompue[3, 4:, 0] += 400.0   # ~18 mm a 45,532 µm
    s2 = sauts(rompue, ok, 45.532)
    v("une rupture est vue, et le rapport explose", s2["rapport_interieur"] > 10, str(s2))
    v("... et elle est comptée", s2["ruptures_interieures"] >= 1, str(s2))
    # ⚠⚠ ET LE SEUIL DE COMPTAGE NE DECIDE PAS DU VERDICT : le rapport, lui, n'a pas de seuil.
    v("le verdict ne dépend pas du seuil de comptage",
      sauts(lisse, ok, 45.532)["rapport_interieur"]
      < sauts(rompue, ok, 45.532)["rapport_interieur"] / 5)

    r = mesurer()
    if "message" in r:
        print(f"  ⚠ {r['message']} — contrôles sur données réelles sautés")
        print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, "
              f"{controles} checks)")
        return 1 if echecs else 0

    d = r["degradation"]
    # ⭐⭐⭐ LE FAIT : la continuite se degrade vers l'exterieur.
    v("la continuité se dégrade du cœur vers le bord",
      r["la_continuite_se_degrade_vers_le_bord"], str(d))
    v("... et les trois tiers sont ordonnés",
      d["coeur"]["rapport_median"] < d["milieu"]["rapport_median"]
      < d["bord"]["rapport_median"], str(d))
    # ⚠⚠ LES SAUTS SURVIVENT AU TEST STRUCTUREL : ce ne sont pas des bords effiloches.
    pires = max(x["saut_max_interieur_um"] for x in r["lignes"])
    v("les plus gros sauts survivent au test des cellules intérieures",
      pires > 20000, f"{pires} µm")
    v("... et ils restent rares", max(x["part_des_paires"] for x in r["lignes"]) < 0.01,
      str(max(x["part_des_paires"] for x in r["lignes"])))
    # ⚠⚠⚠ LE CONFONDANT EST NOMME, ET REFUSE PAR LE TEST DIRECT.
    v("la corrélation saut/pente est forte", r["correlation_saut_pente"] > 0.7,
      str(r["correlation_saut_pente"]))
    e = r["retirer_les_sauts_change_la_pente_de"]
    v("... et pourtant retirer les sauts ne change presque rien",
      e["ecart_relatif_max"] < 0.05, str(e))
    v("... donc les sauts n'expliquent PAS la pente",
      not r["les_sauts_expliquent_la_pente"],
      "une corrélation de 0,8 entre deux grandeurs qui croissent ensemble n'est pas un mécanisme")

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    a = p.parse_args()
    if a.verifier:
        return verifier()

    r = mesurer()
    if "message" in r:
        print(f"⚠ {r['message']}")
        return 1
    print(f"{r['fragment']} · {r['bandes']} bandes · une rupture est un pas de plus de "
          f"{r['rupture_um'] / 1000:.0f} mm entre cellules voisines\n")
    print(f"{'bande':>10} {'ét.':>4} {'pas médian':>11} {'saut intérieur':>15} "
          f"{'rapport':>8} {'ruptures':>9}")
    for x in r["lignes"]:
        print(f"  w{x['de']:03d}-{x['a']:03d} {x['etendue']:>4} {x['pas_median_um']:>10.0f} µm "
              f"{x['saut_max_interieur_um'] / 1000:>12.1f} mm {x['rapport_interieur']:>8.1f} "
              f"{x['ruptures_interieures']:>9}")
    d = r["degradation"]
    print(f"\n⭐⭐⭐ LA CONTINUITÉ SE DÉGRADE VERS LE BORD — rapport médian par tiers :")
    for k in ("coeur", "milieu", "bord"):
        if k in d:
            print(f"     {k:>7} : {d[k]['rapport_median']:>6.1f}  (max {d[k]['rapport_max']:.1f}, "
                  f"{d[k]['bandes']} bandes)")
    print("   ⭐ là où le rouleau est intact, un humain trace continûment ; là où il ne l'est")
    print("     pas, MÊME UN HUMAIN rend une surface discontinue.")
    e = r["retirer_les_sauts_change_la_pente_de"]
    print(f"\n⚠⚠⚠ ET LE CONFONDANT, REFUSÉ — corrélation saut/pente r = "
          f"{r['correlation_saut_pente']}, ce qui suggérait la cause du gonflement de `91`.")
    print(f"   mais retirer les lignes qui contiennent un saut change la pente de "
          f"{e['ecart_relatif_median']:.1%} en médiane, {e['ecart_relatif_max']:.1%} au pire,")
    print(f"   sur {e['bandes_testees']} bandes. Les deux grandeurs croissent vers l'extérieur ;")
    print("   aucune ne cause l'autre. ⚠ La cause de `91` reste NON TROUVÉE — troisième candidat")
    print("   réfuté, après la section ovale et le centre décalé.")
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False) + "\n")
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
