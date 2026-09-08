#!/usr/bin/env python3
"""Ou les spires voisines sont-elles PARALLELES ? Au milieu — pas au bord, et pas mesurable au coeur.

⚠⚠⚠ POURQUOI CETTE QUESTION EST LA DERNIERE AVANT DE CONSTRUIRE. Un marcheur transfere en
avancant d'un pas le long de la NORMALE a la feuille. Ce pas n'atterrit sur la spire voisine que
si les deux spires sont PARALLELES : a un desalignement de trente degres, un pas de 182 µm tombe
a 91 µm de cote, soit la moitie du pas lui-meme. Savoir ou les spires sont paralleles, c'est
savoir ou un pas geometrique suffit — et ou il faut autre chose.

⭐⭐⭐ MESURE, SUR LES TRANSFERTS QUE L'HUMAIN A REUSSIS, ET LA REPONSE EST UN U. L'angle entre la
normale d'une cellule et celle de la cellule situee UN TOUR plus loin vaut 42,4° sur la bande la
plus interne, tombe a **7,7°** au milieu (w073-076), puis remonte a **36,7°** au bord. Ce n'est
donc ni « pire au coeur » ni « pire au bord » : c'est **minimal au milieu**.

⚠⚠⚠ ET LA BANDE LA PLUS INTERNE N'EST PAS DESALIGNEE, ELLE EST NON RESOLUE. Sa grille ne porte
que **27 colonnes par tour**, donc la normale y est moyennee sur **13,3° d'arc par cellule** —
plus que son propre desaccord entre cellules adjacentes (11,6°). Quand la rotation d'une seule
cellule depasse la variation locale de la surface, l'estimateur mesure l'echantillonnage et non la
matiere. Le critere d'exclusion est DERIVE de cette comparaison, et non choisi.

⭐⭐ CE QUE CA DIT DU REMPLACANT DE L'HUMAIN : **les deux modes d'echec sont au BORD**, et non aux
deux bouts comme je l'ai d'abord ecrit. Au bord, `92` mesure une surface **brisee** (31 fois le
pas d'echantillonnage) et ce fichier mesure des spires **desalignees** (jusqu'a 5,2 fois le
desaccord entre cellules adjacentes). Au milieu, les deux sont propres. Un automate a donc un
probleme localise, pas un probleme uniforme.

⚠⚠⚠ ET UNE ERREUR A MOI, GARDEE ICI PARCE QU'ELLE A INVERSE LA CONCLUSION. Mon exploration
comparait la bande 0 a la bande 7 en appelant la seconde « le bord » — alors que les deux sont
dans le tiers interieur. J'en avais tire « desaligne au coeur, parallele au bord », soit
exactement l'inverse. Un tiers se compte sur le corpus entier, pas sur les premieres lignes d'un
tableau.

⚠⚠ ET LE « PLANCHER » N'EST PAS UN PLANCHER DE BRUIT. Le desaccord entre cellules ADJACENTES est
domine par la rotation de la normale d'une cellule a l'autre — 13,3° au coeur, 1,8° au bord — et
non par la rugosite : une spirale PARFAITE echantillonnee a 60 colonnes par tour rend 6,0°, ce qui
est exactement sa rotation par cellule. Il sert donc de repere LOCAL a la meme resolution, ce qui
est utile, mais l'appeler « bruit » serait faux.

⭐ LE CONTROLE QUI VALIDE LA METHODE EST DANS LA MESURE. Une normale de spirale TOURNE avec
l'angle : a un quart de tour elle doit maximalement diverger, a un tour entier elle doit REVENIR.
Mesure : **62 a 66° a un quart de tour** contre 7,7 a 42° a un tour. Si le tour entier ne revenait
pas sous le quart de tour, la mesure ne suivrait pas la spire et ne dirait rien du transfert.

Usage :
    uv run python src/nappe/deux_modes_dechec_du_transfert.py --verifier
    uv run python src/nappe/deux_modes_dechec_du_transfert.py \\
        --json docs/mesures/deux_modes_dechec_du_transfert.json
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

# ⚠ Une bande doit couvrir assez de tours pour qu'un decalage d'un tour tienne dans sa grille, et
# assez de colonnes par tour pour qu'un quart de tour soit plus d'une cellule. Huit colonnes par
# tour est le plancher : en dessous, « un quart de tour » vaut deux cellules et le controle de
# rotation ne veut plus rien dire.
COLONNES_PAR_TOUR_MINIMUM = 8


def normales(a: np.ndarray, ok: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """La normale de chaque cellule, depuis les deux tangentes de la grille.

    ⚠ Les differences CENTREES et non decalees : une difference avant introduit un demi-pas de
    biais dans la direction de la tangente, donc un demi-pas dans la normale, et c'est
    exactement l'ordre de grandeur qu'on cherche a mesurer.
    """
    du = np.zeros_like(a)
    dv = np.zeros_like(a)
    du[:, 1:-1] = a[:, 2:] - a[:, :-2]
    dv[1:-1] = a[2:] - a[:-2]
    n = np.cross(du, dv)
    ln = np.linalg.norm(n, axis=-1)
    bon = ok & (ln > 1e-6)
    return np.where(bon[..., None], n / np.where(ln[..., None] == 0, 1, ln[..., None]), 0), bon


def desaccord(n: np.ndarray, bon: np.ndarray, decalage: int) -> float | None:
    """L'angle median entre la normale d'une cellule et celle de la cellule `decalage` plus loin.

    ⚠⚠ LA VALEUR ABSOLUE DU PRODUIT SCALAIRE : une normale n'a pas d'orientation, donc deux
    normales opposees decrivent la meme feuille. Sans le repli, une feuille dont le maillage
    change d'orientation rendrait 180° la ou il n'y a aucun desalignement.
    """
    if decalage < 1 or decalage >= n.shape[1]:
        return None
    v = bon[:, :-decalage] & bon[:, decalage:]
    if not v.any():
        return None
    d = np.abs(np.einsum("...i,...i->...", n[:, :-decalage], n[:, decalage:]))[v]
    return float(np.median(np.degrees(np.arccos(np.clip(d, 0.0, 1.0)))))


def colonnes_par_tour(a: np.ndarray, ok: np.ndarray, bords: np.ndarray, cx: np.ndarray,
                      cy: np.ndarray) -> int | None:
    """Combien de colonnes de grille font un tour complet ?

    ⭐ Lu sur la ligne la mieux remplie, par l'angle DEROULE : c'est ce qui permet de nommer « la
    cellule un tour plus loin » sans supposer que la grille est reguliere en angle.
    """
    i = np.clip(np.searchsorted(bords, a[..., 2], side="right") - 1, 0, cx.size - 1)
    ang = np.arctan2(a[..., 1] - cy[i], a[..., 0] - cx[i])
    r = int(np.argmax(ok.sum(axis=1)))
    m = ok[r]
    if int(m.sum()) < 10:
        return None
    aa = np.unwrap(ang[r][m])
    tours = float(aa.max() - aa.min()) / (2 * np.pi)
    if tours < 0.9:
        return None
    return int(round(int(m.sum()) / tours))


def spirale_parfaite(rayon_mm: float, col_par_tour: int, tours: int = 6,
                     pas_mm: float = 0.2, pas_cellule_mm: float = 0.905) -> tuple:
    """Une spirale sans rugosite, echantillonnee comme la vraie — le repere qui NE suffit PAS.

    ⚠⚠ ELLE EST GARDEE PARCE QU'ELLE A INDUIT EN ERREUR. Comparee a elle, la mesure reelle
    semblait quatorze a dix-neuf fois trop grande PARTOUT, ce qui aurait fait publier un
    desalignement uniforme. Une spirale parfaite n'a aucune rugosite : elle mesure ce que
    l'echantillonnage seul produit, pas ce a quoi une vraie surface doit etre comparee.
    """
    W = col_par_tour * tours
    H = 30
    th = np.linspace(0.0, tours * 2 * np.pi, W)
    rr = rayon_mm + pas_mm * th / (2 * np.pi)
    a = np.zeros((H, W, 3))
    for k in range(H):
        a[k, :, 0] = rr * np.cos(th)
        a[k, :, 1] = rr * np.sin(th)
        a[k, :, 2] = k * pas_cellule_mm
    return a, np.ones((H, W), dtype=bool)


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
        ct = colonnes_par_tour(a, ok, bords, cx, cy)
        if ct is None or ct < COLONNES_PAR_TOUR_MINIMUM or ct >= ok.shape[1]:
            continue
        n, bon = normales(a, ok)
        plancher = desaccord(n, bon, 1)
        quart = desaccord(n, bon, max(2, ct // 4))
        tour = desaccord(n, bon, ct)
        if plancher is None or tour is None or quart is None:
            continue
        # ⚠ Le repere « spirale parfaite », garde parce qu'il induit en erreur : il dit ce que
        # l'echantillonnage seul produit, jamais ce a quoi une vraie surface se compare.
        i = np.clip(np.searchsorted(bords, a[..., 2], side="right") - 1, 0, cx.size - 1)
        rayon = float(np.median(np.hypot(a[..., 0] - cx[i], a[..., 1] - cy[i])[ok])
                      * R.VOXEL_UM / 1000.0)
        fa, fo = spirale_parfaite(rayon, ct)
        fn, fb = normales(fa, fo)
        parfaite = desaccord(fn, fb, ct)
        lignes.append({
            "de": x["de"], "a": x["a"], "etendue": x["etendue"],
            "rayon_mm": round(rayon, 2), "colonnes_par_tour": ct,
            # ⚠⚠ CE N'EST PAS UN PLANCHER DE BRUIT : il est domine par la rotation de la
            # normale d'une cellule a l'autre. Il sert de repere LOCAL a la meme resolution.
            "adjacent_deg": round(plancher, 1),
            "rotation_par_cellule_deg": round(360.0 / ct, 1),
            # ⭐⭐⭐ LE CRITERE D'EXCLUSION, DERIVE : quand la rotation d'une seule cellule
            # depasse le desaccord entre cellules adjacentes, l'estimateur mesure
            # l'echantillonnage et non la matiere. Aucun seuil choisi.
            "resolue": bool(360.0 / ct < plancher),
            "quart_de_tour_deg": round(quart, 1),
            "un_tour_deg": round(tour, 1),
            "spirale_parfaite_deg": round(parfaite, 1) if parfaite is not None else None,
            # ⭐⭐⭐ LE VERDICT : le desalignement rapporte au bruit de la surface ELLE-MEME.
            "rapport_au_plancher": round(tour / max(plancher, 1e-9), 2),
        })
    if not lignes:
        return {"message": "aucune bande exploitable"}

    n = len(lignes) // 3
    tiers = {"coeur": lignes[:n], "milieu": lignes[n:2 * n], "bord": lignes[2 * n:]}
    return {
        "fragment": R.FRAGMENT, "voxel_um": R.VOXEL_UM,
        "bandes": len(lignes), "lignes": lignes,
        "par_tiers": {k: {"bandes": len(v),
                          "adjacent_median_deg": round(
                              float(np.median([y["adjacent_deg"] for y in v])), 1),
                          "non_resolues": sum(1 for y in v if not y["resolue"]),
                          "un_tour_median_deg": round(
                              float(np.median([y["un_tour_deg"] for y in v])), 1),
                          "rapport_median": round(
                              float(np.median([y["rapport_au_plancher"] for y in v])), 2)}
                      for k, v in tiers.items() if v},
        # ⭐ LE CONTROLE QUI VALIDE LA METHODE : une normale de spirale doit REVENIR apres un tour.
        "la_normale_revient_apres_un_tour": bool(
            all(x["un_tour_deg"] < x["quart_de_tour_deg"] for x in lignes)),
        # ⭐⭐⭐ LE U : le minimum du desalignement, et les deux bouts qui remontent.
        "le_minimum": min(
            (x for x in lignes if x["resolue"]), key=lambda y: y["un_tour_deg"], default=None),
        "aux_deux_bouts": {
            "premiere_resolue": next((x for x in lignes if x["resolue"]), None),
            "derniere": lignes[-1],
        },
        "bandes_non_resolues": [f"w{x['de']:03d}-{x['a']:03d}"
                                for x in lignes if not x["resolue"]],
        "quart_de_tour_median_deg": round(
            float(np.median([x["quart_de_tour_deg"] for x in lignes])), 1),
        # ⚠⚠ LE REPERE TROMPEUR, PUBLIE A COTE pour que l'erreur soit lisible.
        "spirale_parfaite_median_deg": round(
            float(np.median([x["spirale_parfaite_deg"] for x in lignes
                             if x["spirale_parfaite_deg"] is not None])), 1),
    }


def verifier() -> int:
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  FAIL {nom} — {detail}")

    # --- la mecanique, sur une spirale dont on connait la reponse ----------------------------
    a, ok = spirale_parfaite(10.0, 60)
    n, bon = normales(a, ok)
    # ⭐⭐⭐ LE DESACCORD ENTRE CELLULES ADJACENTES EST LA ROTATION, PAS DU BRUIT. Une spirale
    # PARFAITE a 60 colonnes par tour rend 6,0°, ce qui est exactement 360/60. C'est ce que ma
    # premiere version assertait a l'envers — « presque constantes », donc sous 2° — et ce qui
    # m'a fait appeler « plancher de bruit » une quantite purement geometrique.
    v("le désaccord entre cellules adjacentes EST la rotation par cellule",
      abs(desaccord(n, bon, 1) - 360.0 / 60) < 0.2,
      f"{desaccord(n, bon, 1):.2f}° pour {360.0 / 60:.2f}° attendu")
    # ⭐⭐ LE CONTROLE DE ROTATION : a un quart de tour la normale a tourne, a un tour elle revient.
    q, t = desaccord(n, bon, 15), desaccord(n, bon, 60)
    v("... elle diverge maximalement à un quart de tour", q > 60.0, f"{q}°")
    v("... et REVIENT après un tour entier", t < 5.0, f"{t}° contre {q}° au quart")
    # ⚠⚠ LA VALEUR ABSOLUE : une normale n'a pas d'orientation. Sans le repli, une feuille dont
    # le maillage s'inverse rendrait 180° la ou il n'y a aucun desalignement.
    inv = n.copy()
    inv[:, ::2] *= -1.0
    v("une normale retournée ne compte pas comme un désalignement",
      abs(desaccord(inv, bon, 2) - desaccord(n, bon, 2)) < 1e-6,
      f"{desaccord(inv, bon, 2)} contre {desaccord(n, bon, 2)}")
    # ⚠ Un decalage hors grille ne leve pas, il rend None.
    v("un décalage plus grand que la grille rend None", desaccord(n, bon, 10000) is None)
    v("... et un décalage nul aussi", desaccord(n, bon, 0) is None)
    # ⚠⚠⚠ ET UNE SURFACE RUGUEUSE MONTE SON PLANCHER : c'est ce que la spirale parfaite ne dit
    # pas, et c'est pour ca qu'elle ne suffit pas comme repere.
    # ⚠⚠ LA RUGOSITE S'AJOUTE A LA ROTATION SANS LA REMPLACER, et c'est pour ca que le
    # desaccord adjacent ne peut pas etre lu comme un bruit : a cette resolution il est domine
    # par la geometrie. Une rugosite dix fois plus forte le montre.
    rug = a + np.random.default_rng(7).normal(0.0, 0.4, a.shape)
    rn, rb = normales(rug, ok)
    v("une surface très rugueuse dépasse la rotation par cellule",
      desaccord(rn, rb, 1) > 2 * desaccord(n, bon, 1),
      f"{desaccord(rn, rb, 1):.1f}° contre {desaccord(n, bon, 1):.1f}°")
    v("... alors qu'une rugosité faible y reste noyée",
      abs(desaccord(*normales(a + np.random.default_rng(7).normal(0.0, 0.02, a.shape), ok), 1)
          - desaccord(n, bon, 1)) < 1.0,
      "à cette résolution, la géométrie domine")

    r = mesurer()
    if "message" in r:
        print(f"  ⚠ {r['message']} — contrôles sur données réelles sautés")
        print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, "
              f"{controles} checks)")
        return 1 if echecs else 0

    # --- les donnees reelles ------------------------------------------------------------------
    # ⭐ LE CONTROLE DE METHODE, SUR LES VRAIES BANDES : sans le retour apres un tour, la mesure
    # ne suivrait pas la spire et ne dirait rien du transfert.
    v("sur les vraies bandes aussi, la normale revient après un tour",
      r["la_normale_revient_apres_un_tour"],
      f"quart de tour {r['quart_de_tour_median_deg']}°")
    p = r["par_tiers"]
    # ⚠⚠⚠ LE CRITERE D'EXCLUSION EST DERIVE ET IL MORD : les bandes les plus internes n'ont pas
    # assez de colonnes par tour pour que leur normale soit resolue.
    v("les bandes non résolues sont nommées, et ce sont les plus internes",
      r["bandes_non_resolues"] and all("w0" in x for x in r["bandes_non_resolues"]),
      str(r["bandes_non_resolues"]))
    v("... et le tiers extérieur, lui, est entièrement résolu",
      p["bord"]["non_resolues"] == 0, str(p["bord"]))
    # ⭐⭐⭐ LE U : minimal au milieu, remontant au bord.
    mini = r["le_minimum"]
    der = r["aux_deux_bouts"]["derniere"]
    v("le désalignement est MINIMAL à mi-rayon", 8.0 < mini["rayon_mm"] < 18.0,
      f"minimum à {mini['rayon_mm']} mm : {mini['un_tour_deg']}°")
    v("... et les spires y sont quasi parallèles", mini["rapport_au_plancher"] < 1.5,
      f"×{mini['rapport_au_plancher']}")
    v("... alors qu'au bord elles ne le sont plus", der["rapport_au_plancher"] > 3.0,
      f"×{der['rapport_au_plancher']} à {der['rayon_mm']} mm")
    # ⭐⭐ LE TIERS EXTERIEUR PORTE LE DESALIGNEMENT, et c'est l'inverse de ce que j'avais
    # d'abord ecrit en comparant deux bandes du meme tiers.
    v("le tiers extérieur est le plus désaligné",
      p["bord"]["rapport_median"] > p["milieu"]["rapport_median"]
      and p["bord"]["rapport_median"] > 3.0, str(p))
    # ⭐ LE CONTROLE DE METHODE : la normale revient apres un tour.
    v("sur les vraies bandes aussi, la normale revient après un tour",
      r["la_normale_revient_apres_un_tour"],
      f"quart de tour {r['quart_de_tour_median_deg']}°")
    # ⚠⚠ LE REPERE TROMPEUR EST PUBLIE : compare a lui, tout semblait desaligne partout.
    v("la spirale parfaite rend un angle bien plus petit que le désaccord réel",
      r["spirale_parfaite_median_deg"] < p["bord"]["adjacent_median_deg"],
      f"{r['spirale_parfaite_median_deg']}° contre {p['bord']['adjacent_median_deg']}°")

    # ⚠⚠⚠ LA BATTERIE EXERCE SON PROPRE AFFICHAGE. Sans ce controle, `--verifier` est reste vert
    # a dix-sept controles pendant que `main()` plantait sur une clef renommee : une batterie qui
    # ne lance jamais le chemin que l'utilisateur emprunte ne garde pas ce qu'il voit.
    import contextlib  # noqa: PLC0415
    import io as _io  # noqa: PLC0415

    sortie = _io.StringIO()
    try:
        with contextlib.redirect_stdout(sortie):
            code = main_affichage(r)
        v("l'affichage tourne sur ce résultat", code == 0)
        texte = sortie.getvalue()
        v("... et il nomme les trois tiers",
          all(k in texte for k in ("cœur", "milieu", "bord")), texte[:120])
        v("... et il dit où est le minimum",
          f"{r['le_minimum']['rayon_mm']:.1f}" in texte or
          str(r["le_minimum"]["un_tour_deg"]) in texte)
    except Exception as err:  # noqa: BLE001
        v("l'affichage tourne sur ce résultat", False, f"{type(err).__name__}: {err}")

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
    code = main_affichage(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False) + "\n")
        print(f"\nécrit : {a.json}")
    return code


def main_affichage(r: dict) -> int:
    """L'affichage, SEPARE pour que la batterie puisse le lancer.

    ⚠⚠ Un affichage qui ne vit que dans `main()` n'est jamais exerce par `--verifier`, donc une
    clef renommee y survit jusqu'a ce qu'un humain lance la commande. C'est arrive ici.
    """
    print(f"{r['fragment']} · {r['bandes']} bandes · angle entre la normale d'une cellule et "
          "celle d'un tour plus loin\n")
    print(f"{'bande':>10} {'rayon':>7} {'col/tour':>9} {'adjacent':>9} {'1/4 tour':>9} "
          f"{'UN TOUR':>8} {'rapport':>8}")
    for x in r["lignes"]:
        print(f"  w{x['de']:03d}-{x['a']:03d} {x['rayon_mm']:>6.1f} {x['colonnes_par_tour']:>9} "
              f"{x['adjacent_deg']:>8.1f}° {x['quart_de_tour_deg']:>8.1f}° "
              f"{x['un_tour_deg']:>7.1f}° {x['rapport_au_plancher']:>8.2f}")
    p_ = r["par_tiers"]
    print(f"\n⭐ LE CONTRÔLE DE MÉTHODE — la normale diverge à un quart de tour "
          f"({r['quart_de_tour_median_deg']}°) et REVIENT après un tour entier.")
    print("   sans ce retour, la mesure ne suivrait pas la spire et ne dirait rien du transfert.")
    # ⚠ « bruit » serait faux : le désaccord entre cellules adjacentes est dominé par la
    # ROTATION de la normale d'une cellule à l'autre, pas par la rugosité.
    print(f"\n⭐⭐⭐ LE DÉSALIGNEMENT, rapporté au désaccord entre cellules ADJACENTES :")
    # ⚠ Le libellé est du FRANÇAIS, la clef est un identifiant : les confondre fait imprimer
    # « coeur » dans une sortie destinée à un humain, et fait échouer un contrôle qui cherche
    # le mot juste.
    for k, mot in (("coeur", "cœur"), ("milieu", "milieu"), ("bord", "bord")):
        if k in p_:
            print(f"     {mot:>7} : {p_[k]['un_tour_median_deg']:>5.1f}° contre "
                  f"{p_[k]['adjacent_median_deg']:>4.1f}° entre cellules adjacentes  →  "
                  f"×{p_[k]['rapport_median']}")
    # ⚠⚠ Ce titre disait « AUX DEUX BOUTS » juste au-dessus d'une ligne qui dit le contraire :
    # un titre qui contredit son propre corps est pire qu'un titre absent.
    print(f"\n⭐⭐ LE DÉSALIGNEMENT EST MINIMAL À MI-RAYON :")
    mini, der = r["le_minimum"], r["aux_deux_bouts"]["derniere"]
    print(f"   à MI-RAYON ({mini['rayon_mm']:.1f} mm) les spires sont quasi PARALLÈLES : "
          f"{mini['un_tour_deg']}° contre {mini['adjacent_deg']}° → ×{mini['rapport_au_plancher']}")
    print(f"   au BORD ({der['rayon_mm']:.1f} mm) elles ne le sont plus : {der['un_tour_deg']}° "
          f"→ ×{der['rapport_au_plancher']}")
    print(f"   ⭐ et `92` mesure que la surface y est AUSSI brisée (×31) — les deux modes")
    print("     d'échec sont donc au BORD, pas aux deux bouts.")
    if r["bandes_non_resolues"]:
        print(f"   ⚠ {len(r['bandes_non_resolues'])} bande(s) NON RÉSOLUE(S) à cette "
              f"résolution : {', '.join(r['bandes_non_resolues'])} — leur normale est moyennée")
        print("     sur plus d'arc que leur propre variation locale.")
    print(f"\n⚠⚠ le repère TROMPEUR, gardé : une spirale parfaite échantillonnée pareil rend "
          f"{r['spirale_parfaite_median_deg']}°,")
    print("   donc comparée à elle la mesure semblait 14 à 19 fois trop grande PARTOUT. une")
    print("   spirale parfaite n'a aucune rugosité : le bon repère est la surface elle-même.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
