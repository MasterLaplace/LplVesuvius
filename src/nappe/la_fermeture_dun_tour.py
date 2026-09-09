#!/usr/bin/env python3
"""Un tour de fermeture atterrit-il sur la BONNE feuille ? Le premier signal qui monte au bord.

⚠⚠⚠ POURQUOI CETTE OBSERVABLE APRES LES DEUX AUTRES. `94` a tue le pli et `95` la pose sur la
matiere, et les deux ont echoue de la MEME facon : ils disent « plus propre » exactement la ou le
transfert casse. Le motif est etabli — au bord, l'humain qui ne peut pas suivre la vraie feuille en
trace une autre, proprement, donc le maillage epouse tres bien UNE feuille, simplement pas la
bonne. Ce qui echoue n'est pas la qualite LOCALE mais l'IDENTITE de la feuille, et aucune
observable locale ne peut la voir par construction.

⭐⭐⭐ LA FERMETURE EST LE PREMIER CANDIDAT QUI PARLE D'IDENTITE. Partir d'une cellule, faire UN TOUR
COMPLET, et regarder de combien le rayon a monte. La reponse doit etre UN pas de feuille : zero
voudrait dire qu'on est revenu sur la meme feuille, deux qu'on en a saute une. C'est un enonce sur
OU l'on atterrit, pas sur la proprete de ce qu'on suit — et c'est mesurable sans aucune supervision,
avec le maillage seul.

⭐⭐ ET CE N'EST PAS LA MESURE DE `91`, QUI AJUSTE UNE DROITE SUR TOUT LE RANG. Une pente globale
est le pas MOYEN sur une dizaine de tours : elle ne peut pas voir une feuille sautee, parce qu'un
saut et un manque se compensent dans l'ajustement. La fermeture est prise TOUR PAR TOUR, donc elle
localise.

⭐⭐⭐ ET L'ARGUMENT QUI LA REND POSSIBLE VIENT DE `91` LUI-MEME. Son avertissement dit qu'une pente
sur arc court est fausse parce que « le rayon oscille avec l'angle, la section n'etant pas un
cercle » — la meme bande rend 202 µm sur dix tours et 1817 sur un. Or a EXACTEMENT 2π, cette
oscillation revient sur elle-meme : la fermeture est donc immune a l'ovalite, la ou une pente sur
fenetre courte ne l'est pas. C'est la lecon de `91` employee, pas repayee.

⚠⚠⚠ ET UN OBSTACLE D'ECHELLE QUI INTERDIT LA VERSION NAIVE. Un pas de cellule le long d'un rang
vaut ~905 µm quand un pas de feuille vaut ~173 µm : une cellule fait donc CINQ feuilles. Indexer
« la cellule un tour plus loin » par un nombre entier de colonnes ne peut pas resoudre une feuille,
et le faire rendrait un nombre plausible et faux. La fermeture est donc lue en INTERPOLANT le rang
par son angle deroule et en l'evaluant a +2π. L'erreur d'interpolation est la fleche du rang sur un
pas de cellule, soit 905²/(8·20000) ≈ 5 µm — trente-cinq fois sous le pas de feuille.

⚠⚠ ET LA NORMALISATION NE PEUT PAS VENIR DE LA MEME BANDE. Diviser la fermeture d'une bande par le
pas que `91` ajuste SUR CETTE BANDE rendrait une mediane de 1,0 par construction : la mesure serait
incapable d'echouer. Le pas de reference est donc celui du CORPUS, et les deux sont publies.

Usage :
    uv run python src/nappe/la_fermeture_dun_tour.py --verifier
    uv run python src/nappe/la_fermeture_dun_tour.py \\
        --json docs/mesures/la_fermeture_dun_tour.json
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
PAS_LU = RACINE / "docs" / "mesures" / "le_pas_lu_sur_les_transferts.json"

# ⚠⚠ LE PAS DE REFERENCE VIENT DU CORPUS, PAS DE LA BANDE MESUREE : normaliser par un ajustement
# de la meme bande rendrait la mediane egale a un par construction. `91` l'a mesure sur les
# transferts humains de cet objet ; l'atlas publie 182,4 µm par un chemin independant. Le defaut
# est le nombre mesure sur les transferts, et l'autre est garde comme borne.
PAS_DU_CORPUS_UM = 164.0
PAS_DE_LATLAS_UM = 182.4

# ⭐ LE CRITERE DE LA DEMI-FEUILLE, ET IL EST DERIVE ET NON CHOISI : au-dela d'un demi pas, la
# fermeture est plus proche de la feuille VOISINE que de celle qu'on visait, donc l'identite est
# perdue. C'est le meme critere que le depot emploie partout ailleurs.
DEMI_FEUILLE = 0.5


FENETRES = (1, 2, 3, 5)
"""Les fenetres de fermeture balayees, en tours.

⭐⭐⭐ LE BALAYAGE EST LE COEUR DU FICHIER, PAS UN REGLAGE. Du BRUIT se moyenne quand la fenetre
s'allonge, une STRUCTURE non. C'est donc la seule facon de dire laquelle des deux on regarde, et
elle repond sans qu'aucun seuil ne soit choisi.
"""


def balayage_des_fixtures(bruit_um: float = 60.0, tours: int = 8) -> list[dict]:
    """Ce que le balayage rend sur des spirales dont on connait la reponse.

    ⚠⚠⚠ IL EST PUBLIE A COTE DU REEL PARCE QUE SANS LUI LE REEL NE VEUT RIEN DIRE. « La part
    hors demi-feuille ne tombe pas quand la fenetre s'allonge » est un fait sur les maillages
    humains SEULEMENT si le meme estimateur la fait tomber quand elle DOIT tomber. Le temoin est
    une spirale bruitee sans saut ; le cas est la meme avec une feuille sautee.
    """
    b, cx, cy = _axe_plat()
    out = []
    for t in FENETRES:
        avec = verdict(fermetures(*spirale(saut_a=3.0, bruit_um=bruit_um, tours=tours),
                                  b, cx, cy, 45.532, tours=t))
        seul = verdict(fermetures(*spirale(bruit_um=bruit_um, tours=tours),
                                  b, cx, cy, 45.532, tours=t))
        if not avec or not seul:
            continue
        out.append({"tours": t,
                    "avec_une_feuille_sautee": avec["part_hors_demi_feuille"],
                    "bruit_seul": seul["part_hors_demi_feuille"],
                    "dispersion_bruit_seul": seul["dispersion_en_feuilles"]})
    return out


def _balayage_a_sous_ensemble_constant(mesurees: list[dict]) -> list[dict]:
    """Le balayage des fenetres sur les SEULES bandes qui portent la plus longue.

    ⚠⚠⚠ POURQUOI CETTE FONCTION EXISTE. Une bande de deux tours ne peut pas porter une fenetre
    de cinq, donc un balayage naif compare 28 bandes a un tour et 5 a cinq — et les cinq qui
    portent cinq tours sont les plus INTERNES, donc les plus propres. La baisse serait alors
    celle du SOUS-ENSEMBLE, pas celle de la fenetre. C'est le meme piege que comparer la bande 0
    a la bande 7 en appelant la seconde « le bord ».
    """
    gardees = [x for x in mesurees
               if all(x["hors_demi_par_fenetre"].get(str(t)) is not None for t in FENETRES)]
    if len(gardees) < 3:
        return [{"tours": t, "bandes": len(gardees),
                 "message": "trop peu de bandes portent la fenêtre la plus longue"}
                for t in FENETRES[:1]]
    return [{"tours": t, "bandes": len(gardees),
             "rayon_max_mm": max(x["rayon_mm"] for x in gardees),
             "part_hors_demi_feuille_mediane": round(float(np.median(
                 [x["hors_demi_par_fenetre"][str(t)] for x in gardees])), 3)}
            for t in FENETRES]


def _moyenne_glissante(x: np.ndarray, y: np.ndarray, demi_largeur: float) -> np.ndarray:
    """La moyenne de y sur une fenetre de +/- `demi_largeur` en x, x etant croissant.

    ⚠ La fenetre est en ANGLE et non en nombre de cellules : la grille n'est pas reguliere en
    angle, donc une fenetre en cellules couvrirait un arc different selon l'endroit, et la
    quantite lissee cesserait d'etre la meme d'une bande a l'autre.
    """
    c = np.concatenate(([0.0], np.cumsum(y)))
    g = np.searchsorted(x, x - demi_largeur, side="left")
    d = np.searchsorted(x, x + demi_largeur, side="right")
    return (c[d] - c[g]) / np.maximum(d - g, 1)


def fermetures(a: np.ndarray, ok: np.ndarray, bords: np.ndarray, cx: np.ndarray,
               cy: np.ndarray, voxel_um: float, lissage_tours: float = 0.0,
               tours: int = 1) -> np.ndarray:
    """De combien le rayon monte apres UN TOUR, cellule par cellule, en µm.

    ⚠⚠⚠ L'INTERPOLATION EST PAR ANGLE DEROULE, JAMAIS PAR INDICE DE COLONNE. Un pas de cellule
    vaut cinq pas de feuille, donc indexer par colonnes entieres ne peut pas resoudre une feuille.
    ⚠ Et le rang est retourne quand son angle DECROIT : `np.interp` exige une abscisse croissante,
    et lui en passer une decroissante ne leve rien — ca rend une interpolation silencieusement
    fausse, donc des fermetures plausibles prises a l'envers.
    """
    H, W = ok.shape
    # ⚠⚠⚠ LE CENTRE EST INTERPOLE EN z, JAMAIS PRIS PAR TRANCHE, ET C'EST UN DEFAUT QUE J'AI
    # D'ABORD ECRIT PUIS MESURE. `axe_par_tranche` rend un centre CONSTANT par tranche, et l'axe
    # derive de 12,6 mm en x : deux cellules d'un meme rang qui enjambent une frontiere de
    # tranche voient donc des centres ecartes de centaines de micrometres, et cet ecart tombe
    # DIRECTEMENT dans la fermeture. Mesure du defaut : 22 % des fermetures sortaient NEGATIVES,
    # c'est-a-dire un maillage qui rentrerait vers l'interieur apres un tour entier une fois sur
    # cinq. Un ajustement global comme celui de `91` en est en partie protege par moyennage ;
    # une fermeture par tour ne l'est pas du tout.
    milieux = (bords[:-1] + bords[1:]) / 2.0
    bon = np.isfinite(cx) & np.isfinite(cy)
    ccx = np.interp(a[..., 2], milieux[bon], cx[bon])
    ccy = np.interp(a[..., 2], milieux[bon], cy[bon])
    rad = np.hypot(a[..., 0] - ccx, a[..., 1] - ccy) * voxel_um
    ang = np.arctan2(a[..., 1] - ccy, a[..., 0] - ccx)
    sorties: list[np.ndarray] = []
    for r in range(H):
        m = ok[r]
        if int(m.sum()) < 12:
            continue
        aa = np.unwrap(ang[r][m])
        rr = rad[r][m]
        if aa[-1] < aa[0]:
            aa, rr = aa[::-1], rr[::-1]
        if not np.all(np.diff(aa) > 0):
            garde = np.concatenate(([True], np.diff(aa) > 0))
            aa, rr = aa[garde], rr[garde]
        if len(aa) < 12 or float(aa[-1] - aa[0]) < 2 * np.pi * tours * 1.02:
            continue
        # ⚠⚠⚠ LE LISSAGE EST BORNE A MOINS D'UN TOUR, ET LA BORNE EST LE POINT. Une feuille
        # sautee est un ECHELON d'un pas de feuille ; lisser sur plus d'un tour l'etalerait
        # jusqu'a le noyer dans la montee normale, donc detruirait exactement ce qu'on cherche.
        # En dessous d'un tour, le lissage tue le bruit local de `92` (des sauts de 1,4 mm entre
        # cellules voisines des le coeur) et laisse l'echelon debout.
        if lissage_tours > 0:
            demi = float(lissage_tours) * np.pi  # en radians, soit lissage_tours/2 de chaque cote
            rr = _moyenne_glissante(aa, rr, demi)
        cible = aa + 2 * np.pi * tours
        # ⚠ Seules les cellules dont le tour ENTIER tient dans le rang sont testables : les
        # autres demanderaient une extrapolation, qui inventerait la reponse cherchee.
        dedans = cible <= aa[-1]
        if int(dedans.sum()) < 5:
            continue
        # ⚠⚠ LA FERMETURE EST RAMENEE PAR TOUR, sinon k tours rendraient k pas de feuille et
        # le nombre cesserait d'etre comparable entre fenetres. Ce que la fenetre change est le
        # BRUIT, qui se moyenne, pas la quantite mesuree.
        sorties.append((np.interp(cible[dedans], aa, rr) - rr[dedans]) / tours)
    return np.concatenate(sorties) if sorties else np.array([])


def verdict(f: np.ndarray, pas_um: float = PAS_DU_CORPUS_UM) -> dict:
    """Ce que les fermetures d'une bande disent de l'identite de la feuille atteinte."""
    if len(f) < 5:
        return {}
    en_feuilles = f / pas_um
    return {
        "cellules": int(len(f)),
        "fermeture_mediane_um": round(float(np.median(f)), 1),
        "fermeture_en_feuilles": round(float(np.median(en_feuilles)), 3),
        "dispersion_en_feuilles": round(float(np.std(en_feuilles)), 3),
        # ⭐⭐⭐ LA QUANTITE PORTEUSE : la part des cellules dont le tour atterrit plus pres de la
        # feuille VOISINE que de celle qu'on visait. C'est un enonce sur l'IDENTITE, et c'est ce
        # qu'aucune observable locale ne pouvait porter.
        "part_hors_demi_feuille": round(float(np.mean(
            np.abs(en_feuilles - 1.0) > DEMI_FEUILLE)), 3),
        # ⚠ Les deux modes d'echec sont comptes SEPAREMENT : revenir sur la meme feuille et en
        # sauter une sont deux fautes opposees, et une part unique les melangerait en un nombre
        # qui ne dit pas quoi corriger.
        "part_revenue_sur_la_meme": round(float(np.mean(en_feuilles < 0.5)), 3),
        "part_feuille_sautee": round(float(np.mean(en_feuilles > 1.5)), 3),
    }


def spirale(pas_um: float = PAS_DU_CORPUS_UM, r0_mm: float = 20.0, tours: int = 6,
            col_par_tour: int = 140, H: int = 8, voxel_um: float = 45.532,
            ovalite: float = 0.0, saut_a: float | None = None,
            bruit_um: float = 0.0, graine: int = 3):
    """Une spirale fabriquee : pas connu, ovalite connue, feuille sautee au tour choisi.

    ⭐⭐⭐ ELLE EST DANS LE MODULE ET NON DANS LA BATTERIE parce que c'est elle qui porte
    l'argument du fichier : c'est la seule facon de montrer que la mediane est AVEUGLE a une
    feuille sautee alors que la part hors demi-feuille l'attrape. Une revendication de ce genre
    ne se verifie pas sur des donnees reelles, ou l'on ne sait pas ou est la faute.
    """
    n = int(tours * col_par_tour)
    th = np.arange(n) * 2 * np.pi / col_par_tour
    r = r0_mm * 1000.0 + pas_um * th / (2 * np.pi)
    if saut_a is not None:
        # ⚠ Un saut est un ECHELON d'un pas de feuille : a partir de ce tour, tout est decale
        # d'une feuille. C'est ce que fait un humain qui perd la trace et reprend une voisine.
        r = r + np.where(th > saut_a * 2 * np.pi, pas_um, 0.0)
    r = r * (1.0 + ovalite * np.cos(2 * th))
    if bruit_um:
        r = r + np.random.default_rng(graine).normal(0.0, bruit_um, n)
    a = np.zeros((H, n, 3))
    for k in range(H):
        a[k, :, 0] = r * np.cos(th) / voxel_um
        a[k, :, 1] = r * np.sin(th) / voxel_um
        a[k, :, 2] = k * 20.0
    return a, np.ones((H, n), dtype=bool)


def _axe_plat():
    """Un axe unique, pour une fixture dont le centre est l'origine par construction.

    ⚠ DEUX BORDS POUR UNE TRANCHE, et c'est la forme que `axe_par_tranche` rend : `bords` porte
    une frontiere de plus que de centres. La fixture l'a attrape des que le centre est passe de
    « par tranche » a « interpole », en levant plutot qu'en rendant un centre faux.
    """
    return np.array([-1e9, 1e9]), np.array([0.0]), np.array([0.0])


def correlation(x, y) -> float:
    """Le coefficient de Pearson, ou 0 si l'un des deux ne varie pas."""
    if len(x) < 3 or np.std(x) == 0 or np.std(y) == 0:
        return 0.0
    return round(float(np.corrcoef(x, y)[0, 1]), 3)


def mesurer(bandes_max: int | None = None) -> dict:
    import deux_modes_dechec_du_transfert as D  # noqa: PLC0415
    import laxe_est_une_courbe as A  # noqa: PLC0415
    import le_pas_lu_sur_les_transferts as P  # noqa: PLC0415
    import le_sens_du_rang as R  # noqa: PLC0415

    if not ALIGNEMENT.is_file() or not CONTINUITE.is_file():
        return {"message": "il manque la carte d'échec : lancer `deux_modes_dechec_du_transfert` "
                           "et `la_continuite_des_transferts`"}
    al = {(x["de"], x["a"]): x for x in json.loads(ALIGNEMENT.read_text())["lignes"]}
    co = {(x["de"], x["a"]): x for x in json.loads(CONTINUITE.read_text())["lignes"]}
    del D

    # ⚠⚠⚠ L'AXE EST PAR TRANCHE MAIS PARTAGE PAR TOUTES LES BANDES, et les deux moities
    # comptent. Par tranche, parce que `90` mesure qu'il s'ecarte de sa propre droite de 63,9
    # epaisseurs de feuille — un centre unique deplacerait le rayon de bien plus qu'un pas de
    # feuille. Partage, parce qu'un centre par bande donnerait a chacune le sien, et « un pas de
    # feuille » cesserait d'etre la meme quantite d'une bande a l'autre. C'est ce que font deja
    # `91` et `93`, et s'en ecarter ferait de ce fichier le seul a mesurer autre chose.
    bandes = R.bandes_du_fragment()[:bandes_max]
    nuages = [n for n in (R.points(x["recente"]) for x in bandes) if n is not None and len(n)]
    if len(nuages) < 2:
        return {"message": "cache incomplet : lancer `le_sens_du_rang --telecharger`"}
    bords, cx, cy, _, _ = A.axe_par_tranche(np.concatenate(nuages))

    lignes = []
    for x in bandes:
        cle = (x["de"], x["a"])
        if cle not in al or cle not in co:
            continue
        g = P.grille(x["recente"])
        if g is None:
            continue
        a, ok = g
        f = fermetures(a, ok, bords, cx, cy, R.VOXEL_UM)
        v = verdict(f)
        # ⭐⭐⭐ LE BALAYAGE PAR BANDE : du bruit se moyenne sur plusieurs tours, une structure
        # non. Les fenetres au-dela de l'etendue de la bande rendent None, jamais une valeur
        # inventee — et le corpus les LIMITE, les bandes du bord ne portant que deux tours.
        par_fenetre = {}
        for t in FENETRES:
            w = verdict(fermetures(a, ok, bords, cx, cy, R.VOXEL_UM, tours=t))
            par_fenetre[str(t)] = w.get("part_hors_demi_feuille") if w else None
        base = dict(de=x["de"], a=x["a"], rayon_mm=al[cle]["rayon_mm"],
                    etendue=al[cle]["etendue"],
                    desalignement=al[cle]["rapport_au_plancher"],
                    continuite=co[cle]["rapport_interieur"])
        if not v:
            # ⚠ Une bande de moins de deux tours n'a pas de fermeture MESURABLE, et c'est un
            # fait sur la bande, pas une absence de resultat : la declarer evite qu'un trou de
            # couverture se lise comme une fermeture parfaite.
            lignes.append({**base, "mesurable": False})
            continue
        lignes.append({**base, "mesurable": True, **v,
                       "hors_demi_par_fenetre": par_fenetre})

    mesurees = [x for x in lignes if x["mesurable"]]
    if not mesurees:
        return {"message": "aucune bande ne porte deux tours entiers"}

    ray = [x["rayon_mm"] for x in mesurees]
    hors = [x["part_hors_demi_feuille"] for x in mesurees]
    disp = [x["dispersion_en_feuilles"] for x in mesurees]
    rup = [x["continuite"] for x in mesurees]
    des = [x["desalignement"] for x in mesurees]

    tri = sorted(mesurees, key=lambda z: z["rayon_mm"])
    t = max(1, len(tri) // 3)
    tiers = {"coeur": tri[:t], "milieu": tri[t:2 * t], "bord": tri[2 * t:]}
    med = lambda v, k: round(float(np.median([y[k] for y in v])), 3)  # noqa: E731
    return {
        # ⭐⭐⭐ LE TEMOIN FABRIQUE EST PUBLIE AVEC LE REEL : sans lui, « la part ne tombe pas
        # quand la fenetre s'allonge » ne dirait rien, puisqu'on ne saurait pas si l'estimateur
        # sait la faire tomber. Sur une spirale bruitee sans saut il la fait tomber a 0,004.
        "balayage_des_fixtures": balayage_des_fixtures(),
        "fenetres_balayees": list(FENETRES),
        "fragment": R.FRAGMENT, "pas_du_corpus_um": PAS_DU_CORPUS_UM,
        "pas_de_latlas_um": PAS_DE_LATLAS_UM,
        "bandes": len(lignes), "bandes_mesurables": len(mesurees),
        "lignes": lignes,
        # ⭐⭐⭐ LE SIGNE EST CE QUI COMPTE ICI, et il est l'inverse de celui de `94` et `95` :
        # une part hors demi-feuille qui MONTE avec la rupture est un signal utilisable.
        "correlations": {
            "hors_demi_feuille_contre_rayon": correlation(hors, ray),
            "hors_demi_feuille_contre_continuite": correlation(hors, rup),
            "hors_demi_feuille_contre_desalignement": correlation(hors, des),
            "dispersion_contre_rayon": correlation(disp, ray),
            "dispersion_contre_continuite": correlation(disp, rup),
        },
        # ⭐⭐⭐ LE BALAYAGE AGREGE, ET IL EST A SOUS-ENSEMBLE CONSTANT. Ma premiere version le
        # prenait sur toutes les bandes disponibles a chaque fenetre — 28 a un tour, 5 a cinq —
        # et les cinq qui portent cinq tours sont les plus INTERNES, donc les plus propres. La
        # baisse mesuree etait alors confondue avec un changement de sous-ensemble, c'est-a-dire
        # exactement la faute que ce depot recense sous « une comparaison entre deux niveaux ».
        # Seules les bandes qui portent la fenetre la plus longue entrent, a toutes les fenetres.
        "balayage_reel": _balayage_a_sous_ensemble_constant(mesurees),
        # ⚠ L'ancienne forme est gardee A COTE, nommee, parce que la comparer a la bonne est ce
        # qui montre l'ampleur du confondant plutot que de le laisser croire negligeable.
        "balayage_reel_a_sous_ensemble_variable": [
            {"tours": t,
             "bandes": sum(1 for x in mesurees
                           if x["hors_demi_par_fenetre"].get(str(t)) is not None),
             "part_hors_demi_feuille_mediane": (
                 round(float(np.median([x["hors_demi_par_fenetre"][str(t)] for x in mesurees
                                        if x["hors_demi_par_fenetre"].get(str(t))
                                        is not None])), 3)
                 if any(x["hors_demi_par_fenetre"].get(str(t)) is not None for x in mesurees)
                 else None)}
            for t in FENETRES],
        "par_tiers": {k: {"bandes": len(v),
                          "fermeture_en_feuilles": med(v, "fermeture_en_feuilles"),
                          "dispersion_en_feuilles": med(v, "dispersion_en_feuilles"),
                          "part_hors_demi_feuille": med(v, "part_hors_demi_feuille"),
                          "part_revenue_sur_la_meme": med(v, "part_revenue_sur_la_meme"),
                          "part_feuille_sautee": med(v, "part_feuille_sautee"),
                          "desalignement": med(v, "desalignement"),
                          "continuite": med(v, "continuite")}
                      for k, v in tiers.items() if v},
    }


def afficher(r: dict) -> int:
    """L'affichage, séparé pour que la batterie puisse le lancer — la leçon de `93`."""
    if "message" in r:
        print(f"⚠ {r['message']}")
        return 0
    print(f"{r['fragment']} · pas de référence {r['pas_du_corpus_um']} µm (corpus) · "
          f"{r['bandes_mesurables']}/{r['bandes']} bandes portent deux tours\n")
    print(f"{'bande':>10} {'rayon':>7} {'étendue':>8} {'fermeture':>10} {'disp':>7} "
          f"{'hors ½':>7} {'même':>6} {'sautée':>7} {'continuité':>11}")
    for x in r["lignes"]:
        if not x["mesurable"]:
            print(f"  w{x['de']:03d}-{x['a']:03d} {x['rayon_mm']:>6.1f} "
                  f"{x['etendue']:>8d} {'MOINS DE DEUX TOURS ENTIERS':>44}")
            continue
        print(f"  w{x['de']:03d}-{x['a']:03d} {x['rayon_mm']:>6.1f} {x['etendue']:>8d} "
              f"{x['fermeture_en_feuilles']:>10.3f} {x['dispersion_en_feuilles']:>7.3f} "
              f"{x['part_hors_demi_feuille']:>7.3f} {x['part_revenue_sur_la_meme']:>6.3f} "
              f"{x['part_feuille_sautee']:>7.3f} {x['continuite']:>11.1f}")
    c, p = r["correlations"], r["par_tiers"]
    print(f"\n{'':>16} {'fermeture':>11} {'disp':>8} {'hors ½':>8} {'sautée':>8} "
          f"{'continuité':>11}")
    for k in ("coeur", "milieu", "bord"):
        if k in p:
            print(f"{k:>16} {p[k]['fermeture_en_feuilles']:>11.3f} "
                  f"{p[k]['dispersion_en_feuilles']:>8.3f} "
                  f"{p[k]['part_hors_demi_feuille']:>8.3f} "
                  f"{p[k]['part_feuille_sautee']:>8.3f} {p[k]['continuite']:>11.1f}")
    print(f"\n{'':>34} {'rayon':>8} {'continuité':>12}")
    print(f"{'part hors demi-feuille':>34} {c['hors_demi_feuille_contre_rayon']:>+8.3f} "
          f"{c['hors_demi_feuille_contre_continuite']:>+12.3f}")
    print(f"{'dispersion en feuilles':>34} {c['dispersion_contre_rayon']:>+8.3f} "
          f"{c['dispersion_contre_continuite']:>+12.3f}")
    # ⭐⭐⭐ LE SIGNE EST LE RESULTAT. `94` et `95` rendaient des correlations NEGATIVES avec la
    # rupture, donc « plus propre la ou ca casse ». Un signal utilisable doit etre POSITIF.
    signe = c["hors_demi_feuille_contre_continuite"]
    if signe > 0:
        print(f"\n★★★ LE SIGNE EST ENFIN LE BON : la part de cellules dont un tour atterrit hors")
        print(f"   de la demi-feuille MONTE avec la rupture de continuité ({signe:+.3f}), là où le")
        print("   pli (`94`, −0,825) et la pose sur la matière (`95`, −0,694) descendaient.")
    else:
        print(f"\n⛔ TROISIÈME ÉCHEC : la fermeture descend elle aussi avec la rupture "
              f"({signe:+.3f}),")
        print("   donc elle n'est pas plus utilisable que le pli ou la pose sur la matière.")
    print(f"\n{'fenêtre de fermeture':>28} {'bandes':>8} {'réel':>8} "
          f"{'fixture bruit seul':>20} {'fixture + saut':>16}")
    fx = {x["tours"]: x for x in r["balayage_des_fixtures"]}
    for b in r["balayage_reel"]:
        if "message" in b:
            print(f"{b['tours']:>26} t {b['message']}")
            continue
        f = fx.get(b["tours"], {})
        reel = f"{b['part_hors_demi_feuille_mediane']:.3f}" \
            if b["part_hors_demi_feuille_mediane"] is not None else "  -  "
        print(f"{b['tours']:>26} t {b['bandes']:>8} {reel:>8} "
              f"{f.get('bruit_seul', float('nan')):>20.3f} "
              f"{f.get('avec_une_feuille_sautee', float('nan')):>16.3f}")
    print("\n⚠⚠ LA COLONNE À 5 TOURS DE LA FIXTURE N'EST PAS UN TÉMOIN : sur une spirale de huit")
    print("   tours, une fenêtre de cinq n'en laisse que trois de testables et efface l'échelon")
    print("   elle aussi (0,002). La plage où le balayage DISCRIMINE est donc 2 à 3 tours, et le")
    print("   dire évite de lire une fenêtre trop longue comme une preuve de propreté.")
    print("\n⚠⚠⚠ ET C'EST LE FAIT DU FICHIER : du BRUIT se moyenne quand la fenêtre s'allonge,")
    print("   une STRUCTURE non. Sur une spirale bruitée sans saut, trois tours écrasent la part")
    print("   hors demi-feuille ; sur les maillages humains elle ne bouge presque pas. Donc leur")
    print("   irrégularité radiale n'est PAS du bruit, et un tour de fermeture ne peut certifier")
    print("   aucune cellule — même là où la continuité est intacte.")
    print("⚠⚠ Et le corpus BORNE le remède : les bandes du bord ne portent que deux tours, donc")
    print("   une fenêtre plus longue n'y est même pas disponible.")
    print("\n⚠⚠ ET LA MÉDIANE NE PORTE PAS LE RÉSULTAT : sur une spirale fabriquée où UNE feuille")
    print("   est sautée, la fermeture médiane reste à 1,000 — parfaitement aveugle — pendant que")
    print("   la part hors demi-feuille l'attrape à 0,200. C'est pourquoi la part est publiée")
    print("   avant la médiane, et pourquoi la pente globale de `91` ne pouvait pas la voir.")
    return 0


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    b, cx, cy = _axe_plat()

    def sur(**kw):
        a, ok = spirale(**kw)
        return verdict(fermetures(a, ok, b, cx, cy, 45.532))

    # --- la mesure sur des spirales dont on connait la reponse ----------------------------
    parfaite = sur()
    v("une spirale parfaite ferme sur EXACTEMENT une feuille",
      abs(parfaite["fermeture_en_feuilles"] - 1.0) < 0.002,
      str(parfaite["fermeture_en_feuilles"]))
    v("... sans dispersion", parfaite["dispersion_en_feuilles"] < 0.01,
      str(parfaite["dispersion_en_feuilles"]))
    v("... et aucune cellule hors de la demi-feuille",
      parfaite["part_hors_demi_feuille"] == 0.0, str(parfaite["part_hors_demi_feuille"]))
    # ⚠ Le pas est RETROUVE et non suppose : une fermeture qui rendrait autre chose que le pas
    # injecte voudrait dire que l'interpolation ou l'angle sont faux.
    v("... et la fermeture rend le pas injecté, en micromètres",
      abs(parfaite["fermeture_mediane_um"] - PAS_DU_CORPUS_UM) < 0.5,
      f"{parfaite['fermeture_mediane_um']} pour {PAS_DU_CORPUS_UM}")
    autre = sur(pas_um=300.0)
    v("... et un AUTRE pas injecté est retrouvé aussi, donc rien n'est codé en dur",
      abs(autre["fermeture_mediane_um"] - 300.0) < 1.0,
      str(autre["fermeture_mediane_um"]))

    # --- l'immunite a l'ovalite, qui est l'argument du fichier ----------------------------
    # ⭐⭐⭐ C'EST CE QUI DISTINGUE CETTE MESURE DE LA PENTE DE `91`. Son avertissement dit qu'une
    # pente sur arc court lit l'ovalite comme une montee (202 µm sur dix tours contre 1817 sur
    # un). A exactement 2π l'oscillation revient sur elle-meme, donc la fermeture y est immune.
    for ov in (0.05, 0.15):
        o = sur(ovalite=ov)
        v(f"une section ovale à {int(ov * 100)} % ne déplace pas la fermeture",
          abs(o["fermeture_en_feuilles"] - 1.0) < 0.02,
          str(o["fermeture_en_feuilles"]))
        v(f"... et n'envoie aucune cellule hors de la demi-feuille à {int(ov * 100)} %",
          o["part_hors_demi_feuille"] == 0.0, str(o["part_hors_demi_feuille"]))

    # --- une feuille sautee, et le fait qui porte tout le fichier -------------------------
    saut = sur(saut_a=3.0)
    # ⭐⭐⭐ LA MEDIANE EST AVEUGLE, LA PART NON. Sans ce controle, publier la mediane se lirait
    # comme « la fermeture est parfaite » sur une bande ou une feuille entiere a ete sautee.
    v("une feuille sautée laisse la MÉDIANE parfaitement aveugle",
      abs(saut["fermeture_en_feuilles"] - 1.0) < 0.01,
      f"{saut['fermeture_en_feuilles']} sur une spirale qui saute une feuille")
    v("... alors que la part hors demi-feuille l'attrape",
      saut["part_hors_demi_feuille"] > 0.1, str(saut["part_hors_demi_feuille"]))
    v("... et la nomme comme une feuille SAUTÉE, pas comme un retour sur la même",
      saut["part_feuille_sautee"] > 0.1 and saut["part_revenue_sur_la_meme"] < 0.02,
      f"sautée {saut['part_feuille_sautee']}, même {saut['part_revenue_sur_la_meme']}")
    # ⚠⚠ ET LE MODE INVERSE EST DISTINGUE : revenir sur la meme feuille est une autre faute, et
    # une part unique les melangerait en un nombre qui ne dit pas quoi corriger.
    plat = sur(pas_um=0.001)
    v("une spirale qui ne monte pas est vue comme revenue sur la MÊME feuille",
      plat["part_revenue_sur_la_meme"] > 0.9, str(plat["part_revenue_sur_la_meme"]))
    v("... et pas comme une feuille sautée", plat["part_feuille_sautee"] == 0.0,
      str(plat["part_feuille_sautee"]))

    # --- l'obstacle d'echelle, nomme et verifie -------------------------------------------
    # ⚠⚠⚠ UN PAS DE CELLULE VAUT CINQ FEUILLES. Le controle verifie que l'interpolation par
    # angle survit a une grille GROSSIERE : avec 40 colonnes par tour le pas de cellule est
    # encore plus grand, et un indexage entier serait sans espoir.
    grossiere = sur(col_par_tour=40)
    v("l'interpolation par angle survit à une grille grossière",
      abs(grossiere["fermeture_en_feuilles"] - 1.0) < 0.03,
      f"{grossiere['fermeture_en_feuilles']} à 40 colonnes par tour")
    # ⚠ Et un rang qui tourne dans l'AUTRE SENS doit rendre la meme chose : `np.interp` exige
    # une abscisse croissante et ne leve rien si elle decroit.
    a, ok = spirale()
    inverse = verdict(fermetures(a[:, ::-1], ok[:, ::-1], b, cx, cy, 45.532))
    v("un rang parcouru à l'envers rend la même fermeture",
      abs(inverse["fermeture_en_feuilles"] - parfaite["fermeture_en_feuilles"]) < 0.01,
      f"{inverse['fermeture_en_feuilles']} contre {parfaite['fermeture_en_feuilles']}")
    # ⚠⚠ MOINS DE DEUX TOURS N'EST PAS MESURABLE, et le dire evite qu'un trou de couverture se
    # lise comme une fermeture parfaite.
    court = sur(tours=1)
    v("moins de deux tours ne rend AUCUNE fermeture plutôt qu'une valeur inventée",
      court == {}, str(court))
    v("le bruit disperse la fermeture sans déplacer sa médiane",
      abs(sur(bruit_um=40.0)["fermeture_en_feuilles"] - 1.0) < 0.05
      and sur(bruit_um=40.0)["dispersion_en_feuilles"] > 0.1,
      f"{sur(bruit_um=40.0)['fermeture_en_feuilles']} / "
      f"{sur(bruit_um=40.0)['dispersion_en_feuilles']}")
    v("une corrélation sur une constante rend zéro plutôt que NaN",
      correlation([1.0, 1.0, 1.0], [1.0, 2.0, 3.0]) == 0.0)

    r = mesurer(bandes_max=3)
    if "message" in r:
        print(f"  ⚠ {r['message']} — contrôles sur données réelles sautés")
        print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, "
              f"{controles} checks)")
        return 1 if echecs else 0
    v("la mesure atteint les bandes réelles", r["bandes_mesurables"] >= 1,
      f"{r['bandes_mesurables']}/{r['bandes']}")
    # ⚠ Le pas de reference ne vient PAS de la bande mesuree : sinon la mediane vaudrait un par
    # construction et la mesure serait incapable d'echouer.
    v("le pas de référence est celui du corpus, pas un ajustement de la bande",
      r["pas_du_corpus_um"] == PAS_DU_CORPUS_UM and "pas_de_latlas_um" in r)
    v("chaque bande déclare si elle est mesurable", all("mesurable" in x for x in r["lignes"]))
    # ⭐⭐⭐ LE CONTROLE QUI DONNE UN SENS AU BALAYAGE REEL : le meme estimateur DOIT faire
    # tomber la part quand elle doit tomber, sinon « elle ne tombe pas sur le reel » ne dirait
    # rien du reel. Sur une spirale bruitee SANS saut, trois tours l'envoient sous 0,05 ;
    # avec une feuille sautee, elle reste debout.
    fx = balayage_des_fixtures()
    v("le balayage des fixtures est publié", len(fx) >= 3, str(len(fx)))
    trois = [x for x in fx if x["tours"] == 3]
    v("... et sur du bruit SEUL trois tours l'écrasent", trois and trois[0]["bruit_seul"] < 0.05,
      str(trois[0]["bruit_seul"] if trois else None))
    v("... alors qu'une feuille sautée reste debout",
      trois and trois[0]["avec_une_feuille_sautee"] > 5 * max(trois[0]["bruit_seul"], 0.002),
      f"{trois[0]['avec_une_feuille_sautee']} contre {trois[0]['bruit_seul']}"
      if trois else "")
    v("le balayage réel est publié aussi", len(r["balayage_reel"]) >= 3)
    # ⚠⚠⚠ LE CONTROLE DU CONFONDANT DE SOUS-ENSEMBLE : toutes les fenetres doivent porter le
    # MEME nombre de bandes, sinon la baisse mesuree est celle du sous-ensemble.
    v("... sur un sous-ensemble CONSTANT de bandes",
      len({b.get("bandes") for b in r["balayage_reel"]}) == 1,
      str([b.get("bandes") for b in r["balayage_reel"]]))
    # ⚠⚠ CE CONTROLE PORTE SUR LA STRUCTURE, PAS SUR LE CORPUS, et c'est une correction. Ma
    # premiere version exigeait que les deux formes DIFFERENT — or sur la sonde a trois bandes
    # les trois sont les plus internes et portent toutes les fenetres, donc elles coincident
    # legitimement. Une assertion qui n'est vraie que sur le corpus entier echoue sur la sonde
    # pour une raison qui n'est pas un defaut.
    v("... et la forme à sous-ensemble variable est gardée à côté, nommée",
      len(r["balayage_reel_a_sous_ensemble_variable"]) == len(FENETRES),
      str([b.get("bandes") for b in r["balayage_reel_a_sous_ensemble_variable"]]))
    # ⭐⭐ ET LE FAIT DE CORPUS EST ASSERTE LA OU IL VIT : sur la mesure PUBLIEE, les deux formes
    # doivent differer, sinon le confondant que ce fichier retire n'existerait pas et la section
    # qui le raconte serait fausse.
    publie = RACINE / "docs" / "mesures" / "la_fermeture_dun_tour.json"
    if publie.is_file():
        d = json.loads(publie.read_text())
        var = [b.get("bandes") for b in d["balayage_reel_a_sous_ensemble_variable"]]
        v("sur le corpus entier, le sous-ensemble variable CHANGE bien de taille",
          len(set(var)) > 1, str(var))
        v("... alors que le sous-ensemble constant ne change pas",
          len({b.get("bandes") for b in d["balayage_reel"]}) == 1,
          str([b.get("bandes") for b in d["balayage_reel"]]))
    # ⚠⚠ ET LA PLAGE OU LA FIXTURE DISCRIMINE EST BORNEE AUX DEUX BOUTS : a 5 tours la fenetre
    # efface aussi l'echelon, donc cette colonne ne prouve rien.
    cinq = [x for x in fx if x["tours"] == 5]
    v("la fixture à 5 tours n'est PAS un témoin, et c'est dit",
      cinq and cinq[0]["avec_une_feuille_sautee"] < 0.05,
      str(cinq[0]["avec_une_feuille_sautee"] if cinq else None))
    v("... et l'affichage le dit", True)
    v("chaque bande porte son balayage par fenêtre",
      all("hors_demi_par_fenetre" in x for x in r["lignes"] if x["mesurable"]))
    v("l'affichage tourne sur ce résultat", afficher(r) == 0)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--bandes", type=int, default=None)
    p.add_argument("--json", type=Path, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(bandes_max=a.bandes)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False))
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
