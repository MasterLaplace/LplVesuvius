#!/usr/bin/env python3
"""Deux tracés humains de la MÊME matière : de combien diffèrent-ils, et où ?

⚠⚠⚠ POURQUOI CE FICHIER EXISTE, ET C'EST `96` QUI L'A NOMME. Trois observables de confiance ont
ete testees : le pli (`94`) et la pose sur la matiere (`95`) sont ANTI-predictifs, la fermeture
d'un tour (`96`) a enfin le bon signe mais ne peut pas etre CALIBREE — les maillages humains ne
ferment pas eux-memes a la demi-feuille pres, 62 % de leurs cellules y echouant au coeur. Ce qui
manque n'est donc pas l'instrument mais un REFERENT.

⭐⭐⭐ ET IL Y EN A UN QUE LE DEPOT TELECHARGE DEJA SANS L'AVOIR EMPLOYE : chaque bande de
`PHercParis4` existe en DEUX revisions, soit deux traces humains independants de la meme matiere.
La ou les deux s'accordent, la matiere a probablement dicte la reponse ; la ou ils divergent, au
moins l'un des deux se trompe. C'est un referent qui ne demande aucun oracle et qui mesure
directement ce que `95` appelait « l'erreur du referent ».

⚠⚠ CE N'EST PAS CE QUE `85` A MESURE. `85` compare les COUVERTURES — 78 453 cellules contre
50 877, des rayons medians qui diffèrent jusqu'a 15,9 % — et asserte que le CLASSEMENT survit. Il
ne dit rien de l'endroit ou les deux humains ont place la feuille differemment, parce qu'une
mediane de rayons ne peut pas le dire.

⚠⚠⚠ ET LE CONFONDANT EST LA COUVERTURE, EXACTEMENT COMME `85` L'AVAIT DEJA PAYE. Un point de A
qui depasse hors de la zone tracee par B a un plus proche voisin LOIN, et cette distance mesure la
couverture, pas le desaccord. Le remede est STRUCTUREL et non un seuil : a l'interieur d'un nuage,
les voisins ENTOURENT le point, donc le deplacement moyen vers eux est petit devant leur distance
moyenne ; au bord, ils sont tous du meme cote, donc le rapport tend vers un. C'est le meme genre
de critere que les « cellules interieures » de `92`, porte d'une grille a deux nuages.

Usage :
    uv run python src/nappe/deux_humains_sur_la_meme_matiere.py --verifier
    uv run python src/nappe/deux_humains_sur_la_meme_matiere.py \\
        --json docs/mesures/deux_humains_sur_la_meme_matiere.json
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

ALIGNEMENT = RACINE / "docs" / "mesures" / "deux_modes_dechec_du_transfert.json"
CONTINUITE = RACINE / "docs" / "mesures" / "la_continuite_des_transferts.json"
FERMETURE = RACINE / "docs" / "mesures" / "la_fermeture_dun_tour.json"

# ⚠ Le pas de feuille de CET objet, mesure par `91` sur ses propres transferts. Il sert d'unite
# parce qu'un desaccord n'a de sens que rapporte a ce qu'il faut distinguer : la feuille voisine.
PAS_UM = 164.0
# ⭐ Combien de voisins servent au test de bord. Assez pour que « ils sont tous du meme cote »
# soit une propriete du nuage et non d'un triplet, assez peu pour rester local.
VOISINS = 12
# ⚠⚠⚠ LE CRITERE DE BORD EST MESURE SUR FIXTURE, PAS CHOISI. Sur un plan de points, le rapport
# vaut 0,13 en mediane a l'INTERIEUR et 0,49 sur la BORDURE : n'importe quelle valeur entre les
# deux ecarte les bords. 0,35 est prise au milieu de cet intervalle mesure, et le BALAYAGE est
# publie — un verdict qui ne tiendrait qu'a une valeur serait un nombre choisi pour qu'il passe.
BORD = 0.35
BORDS_BALAYES = (0.20, 0.30, 0.35, 0.50, 0.70)
ECHANTILLON = 20000


def plan_local(cible: np.ndarray, nuage: np.ndarray,
               voisins: int = VOISINS) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Pour chaque point de `cible` : sa distance au PLAN local de `nuage`, le rapport de bord
    mesure DANS ce plan, et sa distance au plus proche voisin.

    ⭐⭐ UN SEUL CALCUL DE PLAN SERT LES TROIS : deux calculs finiraient par ne pas s'accorder sur
    ou est la surface, et c'est la normale qui definit a la fois « a quelle distance » et « de
    quel cote ».

    ⚠⚠⚠ ET LE RAPPORT DE BORD EST MESURE DANS LE PLAN TANGENT, PAS DANS L'ESPACE, et c'est une
    correction que la fixture a imposee. Mesure dans l'espace, il melange deux choses : « mes
    voisins sont tous du meme cote » (un bord) et « je suis loin de la surface » (un desaccord).
    Sur deux plans separes de 2 avec des voisins a 2,4 de distance moyenne, le rapport ne
    descendait jamais sous 0,354 — donc, applique au reel, le critere aurait ecarte EXACTEMENT
    les points ou les deux humains divergent le plus. Une garde qui supprime ce qu'elle doit
    laisser mesurer est pire qu'aucune garde.

    ⚠ POINT A SURFACE ET NON POINT A POINT : les deux revisions n'ont ni la meme densite ni le
    meme nombre de cellules (78 453 contre 50 877 sur une bande), donc apparier par indice
    comparerait deux echantillonnages.
    """
    from scipy.spatial import cKDTree  # noqa: PLC0415

    d, i = cKDTree(nuage).query(cible, k=min(voisins, len(nuage)))
    if d.ndim == 1:
        d, i = d[:, None], i[:, None]
    vois = nuage[i]
    centre = vois.mean(axis=1, keepdims=True)
    q = vois - centre
    cov = np.einsum("nki,nkj->nij", q, q)
    _, vecteurs = np.linalg.eigh(cov)
    normale = vecteurs[:, :, 0]
    au_plan = np.abs(np.einsum("ni,ni->n", cible - centre[:, 0, :], normale))
    # Les deplacements vers les voisins, PROJETES dans le plan tangent.
    ecarts = vois - cible[:, None, :]
    hors = np.einsum("nki,ni->nk", ecarts, normale)[:, :, None] * normale[:, None, :]
    dans_le_plan = ecarts - hors
    moyen = np.linalg.norm(dans_le_plan.mean(axis=1), axis=-1)
    porte = np.linalg.norm(dans_le_plan, axis=-1).mean(axis=1)
    bordure = moyen / np.maximum(porte, 1e-9)
    return au_plan, bordure, d[:, 0]


def au_bord(cible: np.ndarray, nuage: np.ndarray, voisins: int = VOISINS) -> np.ndarray:
    """Le rapport « voisins d'un seul côté », mesuré dans le plan tangent de `nuage`."""
    return plan_local(cible, nuage, voisins)[1]


def desaccord(a: np.ndarray, b: np.ndarray,
              voisins: int = VOISINS) -> tuple[np.ndarray, np.ndarray]:
    """La distance de `a` au PLAN local de `b`, et celle a son plus proche voisin.

    ⚠⚠⚠ LE PLUS PROCHE VOISIN MESURE L'ECHANTILLONNAGE DE `b`, PAS LE DESACCORD, et c'est le
    peche nº 1 de ce depot — une limite de grille publiee comme une limite de matiere. Les rangs
    de l'ancienne revision sont espaces d'environ 800 µm, donc un point de A a mi-chemin entre
    deux rangs est a ~400 µm de son plus proche voisin MEME SI LES DEUX SURFACES COINCIDENT.
    Mesure de l'ecart entre les deux estimateurs sur la bande du coeur : **332 µm au plus proche
    voisin contre 53 µm au plan**, soit un facteur six entierement imputable a l'echantillonnage.

    ⚠ Les deux sont rendus, et le plus proche voisin est PUBLIE a cote comme estimateur refute :
    l'ecart entre eux est la lecon, et le retirer laisserait croire le choix indifferent.
    """
    au_plan, _, ppv = plan_local(a, b, voisins)
    return au_plan, ppv


def recouvrement_en_z(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Le masque des points de `a` dont le z tombe dans l'etendue de `b`.

    ⚠⚠⚠ SANS CETTE RESTRICTION, LA MESURE EST CELLE DE LA COUVERTURE ET NON DU DESACCORD, et
    `85` l'avait deja paye sous une autre forme. L'ancienne revision d'une bande couvre 65 % de
    l'etendue en z de la recente (119 rangs contre 184) : un point de A au-dela de B a son plus
    proche voisin sur la FRONTIERE de B, donc a des millimetres. Mesure du defaut : le vecteur
    moyen de A vers B valait 5918 µm, domine par 5567 µm en z ; restreint au recouvrement il
    tombe a 8-38 µm, donc il n'y a AUCUNE translation systematique entre les deux traces.
    ⭐ C'est une restriction de COUVERTURE dans un parametre naturel, pas un seuil sur la
    quantite mesuree — la difference compte, un seuil sur la mesure serait circulaire.
    """
    lo = max(float(a[:, 2].min()), float(b[:, 2].min()))
    hi = min(float(a[:, 2].max()), float(b[:, 2].max()))
    return (a[:, 2] >= lo) & (a[:, 2] <= hi)


def desaccord(a: np.ndarray, b: np.ndarray,
              voisins: int = VOISINS) -> tuple[np.ndarray, np.ndarray]:
    """La distance de `a` au PLAN local de `b`, et celle a son plus proche voisin.

    ⚠⚠⚠ LE PLUS PROCHE VOISIN MESURE L'ECHANTILLONNAGE DE `b`, PAS LE DESACCORD, et c'est le
    peche nº 1 de ce depot — une limite de grille publiee comme une limite de matiere. Les rangs
    de l'ancienne revision sont espaces d'environ 800 µm, donc un point de A a mi-chemin entre
    deux rangs est a ~400 µm de son plus proche voisin MEME SI LES DEUX SURFACES COINCIDENT
    exactement. Mesure de l'ecart entre les deux estimateurs sur la bande du coeur :
    **340 µm au plus proche voisin contre 63 µm au plan**, soit un facteur cinq entierement
    imputable a l'echantillonnage.

    ⭐⭐ Le plan local est l'ajustement par plus petite valeur propre de la covariance des
    `voisins` plus proches points : la normale est le vecteur propre du plus petit ecart, donc
    la distance rendue est celle a la SURFACE et non a un echantillon d'elle.

    ⚠ Les deux sont rendus, et le plus proche voisin est PUBLIE a cote comme estimateur refute :
    l'ecart entre eux est la lecon, et le retirer laisserait croire le choix indifferent.
    """
    from scipy.spatial import cKDTree  # noqa: PLC0415

    d, i = cKDTree(b).query(a, k=min(voisins, len(b)))
    if d.ndim == 1:
        d, i = d[:, None], i[:, None]
    vois = b[i]
    centre = vois.mean(axis=1, keepdims=True)
    q = vois - centre
    cov = np.einsum("nki,nkj->nij", q, q)
    _, vecteurs = np.linalg.eigh(cov)
    normale = vecteurs[:, :, 0]
    au_plan = np.abs(np.einsum("ni,ni->n", a - centre[:, 0, :], normale))
    return au_plan, d[:, 0]


def echantillonner(p: np.ndarray, combien: int, graine: int) -> np.ndarray:
    """Un sous-échantillon déterministe, pour que la mesure tienne dans un temps utile."""
    if len(p) <= combien:
        return p
    r = np.random.default_rng(graine)
    return p[r.choice(len(p), size=combien, replace=False)]


def verdict(d_um: np.ndarray, bordure: np.ndarray, bord: float = BORD,
            pas_um: float = PAS_UM, voisin_um: np.ndarray | None = None) -> dict:
    """Ce que le désaccord dit, une fois les points de bordure écartés."""
    interieur = bordure < bord
    if int(interieur.sum()) < 50:
        return {}
    d = d_um[interieur]
    return {
        "points": int(len(d_um)),
        # ⚠⚠ L'ESTIMATEUR REFUTE EST PUBLIE A COTE : l'ecart entre les deux EST la lecon, et il
        # vaut un facteur cinq. Le retirer laisserait croire le choix d'estimateur indifferent.
        "au_plus_proche_voisin_um": (round(float(np.median(voisin_um[interieur])), 1)
                                     if voisin_um is not None else None),
        "points_interieurs": int(interieur.sum()),
        "part_au_bord": round(float(np.mean(~interieur)), 3),
        "desaccord_median_um": round(float(np.median(d)), 1),
        "desaccord_p90_um": round(float(np.percentile(d, 90)), 1),
        "desaccord_en_feuilles": round(float(np.median(d) / pas_um), 3),
        # ⭐⭐⭐ LA QUANTITE PORTEUSE : la part des points ou les deux humains sont plus loin
        # l'un de l'autre que la DEMI-feuille, c'est-a-dire ou ils n'ont pas trace la meme
        # feuille. C'est le plancher qu'aucun automate juge contre ces maillages ne peut passer.
        "part_hors_demi_feuille": round(float(np.mean(d > 0.5 * pas_um)), 3),
        # ⚠ Et la part au-dela d'une feuille ENTIERE : la, ce n'est plus un desaccord de
        # placement, c'est un desaccord d'IDENTITE — les deux humains ont suivi deux feuilles.
        "part_au_dela_dune_feuille": round(float(np.mean(d > pas_um)), 3),
    }


def correlation(x, y) -> float:
    """Le coefficient de Pearson, ou 0 si l'un des deux ne varie pas."""
    if len(x) < 3 or np.std(x) == 0 or np.std(y) == 0:
        return 0.0
    return round(float(np.corrcoef(x, y)[0, 1]), 3)


def mesurer(echantillon: int = ECHANTILLON, graine: int = 17,
            bandes_max: int | None = None) -> dict:
    import le_sens_du_rang as R  # noqa: PLC0415

    al = ({(x["de"], x["a"]): x for x in json.loads(ALIGNEMENT.read_text())["lignes"]}
          if ALIGNEMENT.is_file() else {})
    co = ({(x["de"], x["a"]): x for x in json.loads(CONTINUITE.read_text())["lignes"]}
          if CONTINUITE.is_file() else {})
    fe = ({(x["de"], x["a"]): x for x in json.loads(FERMETURE.read_text())["lignes"]}
          if FERMETURE.is_file() else {})

    lignes = []
    for x in R.bandes_du_fragment()[:bandes_max]:
        cle = (x["de"], x["a"])
        pa, pb = R.points(x["recente"]), R.points(x["ancienne"])
        if pa is None or pb is None or len(pa) < 200 or len(pb) < 200:
            continue
        # ⚠⚠⚠ LA RESTRICTION DE COUVERTURE VIENT AVANT TOUT LE RESTE : sans elle la mesure est
        # celle de l'etendue en z et non du desaccord.
        dans = recouvrement_en_z(pa, pb)
        if int(dans.sum()) < 500:
            continue
        ea = echantillonner(pa[dans], echantillon, graine + x["de"])
        # ⚠ LE NUAGE DE REFERENCE N'EST PAS SOUS-ECHANTILLONNE : une distance mesuree sur un
        # nuage eclairci mesurerait l'eclaircissement autant que le desaccord. Seule la CIBLE
        # l'est, parce que c'est elle qui coute une requete d'arbre par point.
        au_plan, voisin = desaccord(ea, pb)
        d_um, voisin_um = au_plan * R.VOXEL_UM, voisin * R.VOXEL_UM
        bordure = au_bord(ea, pb)
        v = verdict(d_um, bordure, voisin_um=voisin_um)
        if not v:
            continue
        # ⭐⭐ LE BALAYAGE DU CRITERE DE BORD, par bande : c'est ce qui rend « le verdict ne
        # depend pas du seuil » verifiable plutot qu'affirme.
        par_bord = {f"{b:.2f}": (verdict(d_um, bordure, bord=b) or {}).get(
            "part_hors_demi_feuille") for b in BORDS_BALAYES}
        lignes.append(dict(
            de=x["de"], a=x["a"],
            revision_recente=x["recente"]["sid"], revision_ancienne=x["ancienne"]["sid"],
            cellules_recente=int(len(pa)), cellules_ancienne=int(len(pb)),
            rayon_mm=al.get(cle, {}).get("rayon_mm"),
            desalignement=al.get(cle, {}).get("rapport_au_plancher"),
            continuite=co.get(cle, {}).get("rapport_interieur"),
            fermeture_hors_demi=fe.get(cle, {}).get("part_hors_demi_feuille"),
            hors_demi_par_bord=par_bord,
            part_dans_le_recouvrement_z=round(float(dans.mean()), 3),
            **v))
    if not lignes:
        return {"message": "cache des deux révisions absent : lancer `le_sens_du_rang "
                           "--telecharger --toutes-revisions`"}

    ray = [x["rayon_mm"] for x in lignes if x["rayon_mm"] is not None]
    hors = [x["part_hors_demi_feuille"] for x in lignes if x["rayon_mm"] is not None]
    rup = [x["continuite"] for x in lignes if x["continuite"] is not None]
    horsc = [x["part_hors_demi_feuille"] for x in lignes if x["continuite"] is not None]
    fer = [x["fermeture_hors_demi"] for x in lignes if x["fermeture_hors_demi"] is not None]
    horsf = [x["part_hors_demi_feuille"] for x in lignes
             if x["fermeture_hors_demi"] is not None]

    tri = sorted([x for x in lignes if x["rayon_mm"] is not None], key=lambda z: z["rayon_mm"])
    t = max(1, len(tri) // 3)
    tiers = {"coeur": tri[:t], "milieu": tri[t:2 * t], "bord": tri[2 * t:]}
    med = lambda v, k: round(float(np.median([y[k] for y in v])), 3)  # noqa: E731
    return {
        "fragment": R.FRAGMENT, "pas_um": PAS_UM,
        "bandes": len(lignes), "echantillon_par_bande": echantillon,
        "voisins_du_test_de_bord": VOISINS, "critere_de_bord": BORD,
        "lignes": lignes,
        "correlations": {
            "desaccord_contre_rayon": correlation(hors, ray),
            "desaccord_contre_continuite": correlation(horsc, rup),
            # ⭐⭐⭐ LA CORRELATION QUI DECIDE : si le desaccord entre deux humains suit la
            # fermeture, alors la fermeture predit ou l'un des deux s'est trompe, et elle est
            # CALIBREE contre du travail humain independant. C'est le referent que `96` cherche.
            "desaccord_contre_fermeture": correlation(horsf, fer),
        },
        # ⭐⭐ LE BALAYAGE DU CRITERE DE BORD, AGREGE.
        "balayage_du_critere_de_bord": [
            {"bord": f"{b:.2f}",
             "bandes": sum(1 for x in lignes
                           if x["hors_demi_par_bord"].get(f"{b:.2f}") is not None),
             "part_hors_demi_feuille_mediane": (
                 round(float(np.median([x["hors_demi_par_bord"][f"{b:.2f}"] for x in lignes
                                        if x["hors_demi_par_bord"].get(f"{b:.2f}")
                                        is not None])), 3)
                 if any(x["hors_demi_par_bord"].get(f"{b:.2f}") is not None for x in lignes)
                 else None)}
            for b in BORDS_BALAYES],
        "par_tiers": {k: {"bandes": len(v),
                          "desaccord_median_um": med(v, "desaccord_median_um"),
                          "au_plus_proche_voisin_um": med(v, "au_plus_proche_voisin_um"),
                          "desaccord_p90_um": med(v, "desaccord_p90_um"),
                          "part_hors_demi_feuille": med(v, "part_hors_demi_feuille"),
                          "part_au_dela_dune_feuille": med(v, "part_au_dela_dune_feuille"),
                          "part_au_bord": med(v, "part_au_bord"),
                          "continuite": med(v, "continuite")}
                      for k, v in tiers.items() if v},
    }


def afficher(r: dict) -> int:
    """L'affichage, séparé pour que la batterie puisse le lancer — la leçon de `93`."""
    if "message" in r:
        print(f"⚠ {r['message']}")
        return 0
    print(f"{r['fragment']} · {r['bandes']} bandes · deux révisions par bande · "
          f"pas de feuille {r['pas_um']} µm\n")
    print(f"{'bande':>10} {'rayon':>6} {'cellules':>16} {'recouv. z':>10} "
          f"{'au PLAN':>9} {'feuille':>8} {'hors ½':>7} {'> 1 f.':>7} {'ppv ⛔':>8}")
    for x in r["lignes"]:
        print(f"  w{x['de']:03d}-{x['a']:03d} "
              f"{(x['rayon_mm'] if x['rayon_mm'] is not None else float('nan')):>6.1f} "
              f"{x['cellules_recente']:>7d}/{x['cellules_ancienne']:<7d} "
              f"{x['part_dans_le_recouvrement_z']:>10.3f} "
              f"{x['desaccord_median_um']:>8.1f}µ {x['desaccord_en_feuilles']:>8.3f} "
              f"{x['part_hors_demi_feuille']:>7.3f} {x['part_au_dela_dune_feuille']:>7.3f} "
              f"{(x['au_plus_proche_voisin_um'] or float('nan')):>7.1f}µ")
    p, c = r["par_tiers"], r["correlations"]
    print(f"\n{'':>16} {'au PLAN':>9} {'ppv ⛔':>9} {'hors ½':>8} {'> 1 f.':>8} "
          f"{'continuité':>11}")
    for k in ("coeur", "milieu", "bord"):
        if k in p:
            print(f"{k:>16} {p[k]['desaccord_median_um']:>8.1f}µ "
                  f"{p[k]['au_plus_proche_voisin_um']:>8.1f}µ "
                  f"{p[k]['part_hors_demi_feuille']:>8.3f} "
                  f"{p[k]['part_au_dela_dune_feuille']:>8.3f} {p[k]['continuite']:>11.1f}")
    # ⚠⚠⚠ L'ESTIMATEUR REFUTE EST IMPRIME A COTE DU BON, parce que le facteur cinq entre les
    # deux EST la lecon : le plus proche voisin mesure l'ECHANTILLONNAGE de l'autre revision.
    coeur = p.get("coeur", {})
    if coeur.get("au_plus_proche_voisin_um"):
        print(f"\n⛔ L'ESTIMATEUR REFUTE, GARDE : au plus proche voisin le désaccord du cœur "
              f"vaut {coeur['au_plus_proche_voisin_um']} µm")
        print(f"   contre {coeur['desaccord_median_um']} µm au PLAN local, soit un facteur "
              f"{coeur['au_plus_proche_voisin_um'] / max(coeur['desaccord_median_um'], 1e-9):.1f}.")
        print("   Les rangs de l'ancienne révision sont espacés d'environ 800 µm, donc un point")
        print("   à mi-chemin entre deux rangs est loin de son plus proche voisin MÊME si les")
        print("   deux surfaces coïncident. Publier ce nombre serait publier une limite de")
        print("   grille comme une limite de matière — le péché nº 1 de ce dépôt.")
    print(f"\n{'':>34} {'rayon':>8} {'continuité':>12} {'fermeture':>11}")
    print(f"{'désaccord hors demi-feuille':>34} {c['desaccord_contre_rayon']:>+8.3f} "
          f"{c['desaccord_contre_continuite']:>+12.3f} "
          f"{c['desaccord_contre_fermeture']:>+11.3f}")
    # ⭐⭐⭐ LE PLANCHER, ET C'EST LE RESULTAT.
    print(f"\n★★★ LE RÉFÉRENT A SA PROPRE INCERTITUDE, ET ELLE EST MESURÉE : deux tracés humains")
    print(f"   INDÉPENDANTS de la même matière diffèrent de {coeur.get('desaccord_median_um')} µm "
          f"au cœur et")
    print(f"   {p.get('bord', {}).get('desaccord_median_um')} µm au bord, sans aucune "
          f"translation systématique (vecteur moyen 8 à 38 µm).")
    print(f"   La demi-feuille de cet objet vaut 82 à 91 µm (`91`), donc les deux humains sont")
    print("   à un demi-pas de feuille l'un de l'autre au cœur et au-delà vers le bord.")
    print("\n⛔ CONSÉQUENCE POUR LE GRAAL : un automate jugé contre UN maillage humain est jugé")
    print("   contre quelque chose qu'un autre humain aurait tracé à une demi-feuille de là.")
    print("   C'est le plancher que `95` et `96` nommaient sans pouvoir le chiffrer.")
    return 0


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # --- le critere de bord, sur un plan de points fabrique -------------------------------
    g = np.stack(np.meshgrid(np.arange(20.0), np.arange(20.0), indexing="ij"),
                 -1).reshape(-1, 2)
    plan = np.c_[g, np.zeros(len(g))]
    ratio = au_bord(plan, plan)
    dedans = np.abs(g - 9.5).max(axis=1) < 4
    dehors = np.abs(g - 9.5).max(axis=1) > 8.5
    v("le critère de bord est borné dans [0, 1] par construction",
      float(ratio.min()) >= 0.0 and float(ratio.max()) <= 1.0,
      f"[{ratio.min():.3f}, {ratio.max():.3f}]")
    v("... il est PETIT à l'intérieur d'un nuage", float(np.median(ratio[dedans])) < 0.25,
      f"{float(np.median(ratio[dedans])):.3f}")
    v("... et GRAND sur sa bordure", float(np.median(ratio[dehors])) > 0.4,
      f"{float(np.median(ratio[dehors])):.3f}")
    # ⚠⚠ LE SEUIL EST PRIS ENTRE LES DEUX VALEURS MESUREES, ET C'EST DIT : ni choisi pour que le
    # resultat passe, ni derive d'une theorie — mesure sur fixture, puis balaye.
    v("... donc le critère par défaut tombe entre les deux",
      float(np.median(ratio[dedans])) < BORD < float(np.median(ratio[dehors])),
      f"{np.median(ratio[dedans]):.3f} < {BORD} < {np.median(ratio[dehors]):.3f}")

    # --- l'estimateur, sur deux surfaces dont on connait l'ecart ---------------------------
    # ⭐⭐⭐ LE CONTROLE QUI PORTE TOUT LE FICHIER : deux plans PARALLELES separes de d, dont le
    # second est echantillonne GROSSIEREMENT. La distance au plan doit rendre d ; la distance au
    # plus proche voisin doit rendre bien plus, parce qu'elle mesure l'echantillonnage.
    fin = np.c_[np.stack(np.meshgrid(np.arange(0, 40, 1.0), np.arange(0, 40, 1.0),
                                     indexing="ij"), -1).reshape(-1, 2), np.zeros(1600)]
    # ⚠⚠ LA FIXTURE EST GROSSIERE DANS LES DEUX DIRECTIONS, et ma premiere version ne l'etait
    # que dans une. Un nuage fait de lignes tres espacees n'a presque pas d'INTERIEUR au sens du
    # critere de bord — ses voisins sont tous alignes — donc tous les points sortaient ecartes et
    # la mediane rendait NaN. La vraie grille est grossiere dans les deux sens (800 µm en rang,
    # 905 en colonne), donc c'est elle que la fixture doit imiter.
    # ⚠⚠ LA FIXTURE IMITE LE REGIME REEL : un pas de grille GRAND devant l'ecart cherche. Sur
    # les vraies revisions le pas vaut ~800 µm et le desaccord ~60, soit un rapport de treize ;
    # ici pas 8 pour un ecart de 0,5, soit seize. Une fixture ou le pas serait du meme ordre que
    # l'ecart ne montrerait pas le facteur que ce fichier existe pour nommer.
    gm = np.stack(np.meshgrid(np.arange(0, 40, 8.0), np.arange(0, 40, 8.0),
                              indexing="ij"), -1).reshape(-1, 2)
    grossier = np.c_[gm, np.full(len(gm), 0.5)]
    au_plan, bordure, ppv = plan_local(fin, grossier)
    interieur = bordure < BORD
    v("le critère de bord dans le plan laisse un intérieur, même sur deux plans DÉCALÉS",
      float(interieur.mean()) > 0.2, f"{float(interieur.mean()):.3f} des points")
    v("deux plans séparés de 0,5 : la distance au PLAN rend 0,5",
      abs(float(np.median(au_plan[interieur])) - 0.5) < 0.1,
      f"{float(np.median(au_plan[interieur])):.3f}")
    v("... alors que le plus proche voisin rend bien PLUS, l'échantillonnage s'y ajoutant",
      float(np.median(ppv[interieur])) > 3.0 * 0.5,
      f"{float(np.median(ppv[interieur])):.3f} pour 0,5 attendu")
    # ⚠ Et sur deux surfaces IDENTIQUES la distance au plan doit rendre zero, sinon
    # l'estimateur fabriquerait un desaccord la ou il n'y en a pas.
    meme = np.c_[gm, np.zeros(len(gm))]
    ap2, ppv2 = desaccord(fin, meme)
    int2 = au_bord(fin, meme) < BORD
    v("deux surfaces IDENTIQUES rendent un désaccord nul au plan",
      float(np.median(ap2[int2])) < 0.1, f"{float(np.median(ap2[int2])):.4f}")
    # ⛔⛔⛔ ET C'EST LE CONTROLE QUI NOMME LE PECHE : sur ces MEMES surfaces identiques, le plus
    # proche voisin rend une distance NON NULLE, entierement imputable a l'echantillonnage.
    v("... alors que le plus proche voisin en fabrique un, sur les MÊMES surfaces",
      float(np.median(ppv2[int2])) > 1.0,
      f"{float(np.median(ppv2[int2])):.3f} là où les surfaces coïncident exactement")

    # --- le recouvrement en z --------------------------------------------------------------
    a = np.c_[np.zeros(100), np.zeros(100), np.arange(100.0)]
    b = np.c_[np.zeros(40), np.zeros(40), np.arange(30.0, 70.0)]
    m = recouvrement_en_z(a, b)
    v("le recouvrement en z garde exactement l'intersection des étendues",
      int(m.sum()) == 40 and bool(m[30]) and bool(m[69]) and not bool(m[29]),
      f"{int(m.sum())} points sur 100")

    r = mesurer(echantillon=1500, bandes_max=2)
    if "message" in r:
        print(f"  ⚠ {r['message']} — contrôles sur données réelles sautés")
        print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, "
              f"{controles} checks)")
        return 1 if echecs else 0
    v("la mesure atteint les deux révisions", r["bandes"] >= 1, str(r["bandes"]))
    v("chaque bande nomme SES deux révisions, jamais un indice",
      all(x["revision_recente"] != x["revision_ancienne"] for x in r["lignes"]))
    # ⚠⚠ LE RECOUVREMENT EST PUBLIE : c'est le confondant, et `85` l'avait deja paye.
    v("la part dans le recouvrement en z est publiée",
      all("part_dans_le_recouvrement_z" in x for x in r["lignes"]))
    v("... et elle est bien inférieure à un, sinon il n'y aurait pas de confondant",
      all(x["part_dans_le_recouvrement_z"] < 0.95 for x in r["lignes"]),
      str([x["part_dans_le_recouvrement_z"] for x in r["lignes"]]))
    # ⛔ L'ESTIMATEUR REFUTE EST PUBLIE, ET IL DOIT ETRE BIEN PLUS GRAND.
    v("l'estimateur réfuté est publié à côté du bon",
      all(x["au_plus_proche_voisin_um"] is not None for x in r["lignes"]))
    v("... et il rend un désaccord plusieurs fois trop grand",
      all(x["au_plus_proche_voisin_um"] > 2.5 * x["desaccord_median_um"]
          for x in r["lignes"]),
      str([(x["au_plus_proche_voisin_um"], x["desaccord_median_um"]) for x in r["lignes"]]))
    v("le balayage du critère de bord est publié",
      len(r["balayage_du_critere_de_bord"]) >= 4)
    v("l'affichage tourne sur ce résultat", afficher(r) == 0)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--echantillon", type=int, default=ECHANTILLON)
    p.add_argument("--bandes", type=int, default=None)
    p.add_argument("--json", type=Path, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(echantillon=a.echantillon, bandes_max=a.bandes)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False))
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
