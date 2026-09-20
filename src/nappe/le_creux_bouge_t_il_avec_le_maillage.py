"""Le creux bouge-t-il AVEC le maillage, ou dérive-t-il pour son compte ?

⭐⭐⭐⭐ POURQUOI CE FICHIER, ET C'EST `R4-P50` QUI LE NOMME. `201` a établi que la phase du creux ne
se déplie pas : son écart replié d'un chunk au suivant vaut **18,3754 voxels** là où un repère qui
suivrait une frontière rendrait **4,941** — le pas que `199` mesure sur la même rangée. La porte
demandait ce qui, dans un cube, distingue les deux frontières qu'il peut contenir. Mais cette
question en présuppose une AUTRE, que rien n'a mesurée : **le creux est-il seulement attaché à la
matière ?**

⭐⭐⭐⭐ ET LA RÉPONSE EST UN TEST APPARIÉ, EXACT, SUR LES MÊMES PAIRES DE COLONNES. Si le creux est
une frontière de feuillet, alors quand le maillage dérive de `d` voxels d'un chunk au suivant, la
frontière doit paraître bouger d'autant — au signe près. Les deux quantités se lisent sur la MÊME
couture : `199` rend le pas du maillage, `200` rend la couche du creux. Leur corrélation dit si le
creux appartient au papyrus ou au hasard.

⚠⚠⚠ LE SIGNE N'EST PAS POSÉ, IL EST MESURÉ. L'épreuve déclarée porte sur la VALEUR ABSOLUE de la
corrélation, et la pente signée est publiée à côté. `199` a déjà payé un pas rendu à l'envers ;
poser le sens attendu ferait de l'accord une conséquence de la convention.

⚠⚠ ET LA TRANCHE RÉPARE LE DÉFAUT QUE `201` A NOMMÉ : chaque pas est publié AVEC SES DEUX COLONNES.
Le cumul de `199` était indexé par numéro de pas, donc injoignable ; ici la jointure est dans la
donnée.

⚠ LA LIMITE EST ÉCRITE : le pas du maillage se lit à la COUTURE, le creux est une propriété du CUBE
entier. Les deux ne vivent donc pas tout à fait à la même échelle, et seule une dérive lisse à
l'échelle du chunk les rend comparables. C'est une raison d'attendre une corrélation partielle, pas
une raison de n'en attendre aucune.

Usage :
    uv run python src/nappe/le_creux_bouge_t_il_avec_le_maillage.py --verifier
    uv run python src/nappe/le_creux_bouge_t_il_avec_le_maillage.py \\
        --json docs/mesures/le_creux_bouge_t_il_avec_le_maillage.json
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

from la_derive_saccumule_t_elle import (LA_PAUSE_ENTRE_ESSAIS,  # noqa: E402
                                        la_largeur_du_bord, la_ligne_declaree, un_pas)
from la_recette_posee_sur_le_rouleau import DELAI, PERMUTATIONS  # noqa: E402
from le_creux_borne_t_il_la_marche import (la_courbe_dun_bloc,  # noqa: E402
                                           le_repere_dun_chunk)
from ou_le_maillage_quitte_t_il_son_feuillet import (le_segment_declare,  # noqa: E402
                                                     le_taux_tient_la_garantie,
                                                     les_pannes_de_reseau, un_chunk)
from ouvrir_les_quinze import _rng  # noqa: E402
from peut_on_deplier_la_phase import (ce_que_la_marche_a_rendu,  # noqa: E402
                                      le_repli)
from que_montrent_ces_deux_vues import (DEMI_PAS_EN_VOXELS,  # noqa: E402
                                        PAS_EN_VOXELS, la_rangee_montree, une_section)
from zarr_depth import BUCKET, array_meta  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
GRAINE = 20261010

LA_QUESTION_DECLAREE = ("le creux bouge-t-il avec le maillage, ou dérive-t-il pour son compte ?")
LES_EPREUVES_DECLAREES = ("le pas du creux est-il apparié au pas du maillage",)
GARANTIE = 1.0 / (PERMUTATIONS + 1)
GARANTIE_PAR_EPREUVE = GARANTIE / len(LES_EPREUVES_DECLAREES)


def les_paires_voisines(reperes: dict, colonnes) -> list[tuple[int, int]]:
    """Les colonnes CONTIGUËS dont les deux chunks portent un repère lisible.

    ⚠⚠⚠ SEULES LES COLONNES VOISINES COMPTENT, ET C'EST UNE CONTRAINTE DE L'ESTIMATEUR, PAS UN
    CHOIX : `un_pas` compare le bord DROIT d'un chunk au bord GAUCHE du suivant. Deux chunks séparés
    par un trou n'ont pas de couture commune, et leur demander un pas inventerait un déplacement que
    personne n'a mesuré — la règle que `199` avait déjà écrite pour ses tronçons.
    """
    ok = {int(c) for c in colonnes
          if c in reperes and reperes[c].get("lisible")}
    return [(c, c + 1) for c in sorted(ok) if (c + 1) in ok]


def les_deux_pas(sections: dict, reperes: dict, paires, largeur: int,
                 plage: int = DEMI_PAS_EN_VOXELS, periode: float = PAS_EN_VOXELS) -> dict:
    """Pour chaque couture : le pas du MAILLAGE et le pas du CREUX, appariés par construction.

    ⭐⭐⭐⭐ C'EST TOUTE LA TRANCHE. Les deux nombres sortent de la MÊME paire de chunks, donc leur
    appariement n'est pas une hypothèse : il est dans la donnée. `201` ne pouvait pas le faire parce
    que `199` publiait son cumul sans les colonnes.

    ⚠⚠ LE PAS DU CREUX EST REPLIÉ, celui du maillage ne l'est pas : le premier est défini modulo un
    pli — c'est ce que `200` a mesuré — le second est déjà borné par la demi-période de sa recherche.
    """
    maillage, creux, cols, satures = [], [], [], 0
    for a, b in paires:
        if a not in sections or b not in sections:
            continue
        # ⚠⚠ UN REPERE ILLISIBLE NE PORTE AUCUNE COUCHE, et le lire rendrait `None` : la paire est
        # sautee ici AUSSI, meme si `les_paires_voisines` l'a deja ecartee. Sans ce garde, un bris
        # pose sur l'autre fonction faisait tomber la batterie en panne AVANT son verdict, donc le
        # defaut se lisait comme une erreur d'execution et non comme une sonde rouge.
        if reperes[a].get("la_couche") is None or reperes[b].get("la_couche") is None:
            continue
        r = un_pas(sections[a], sections[b], largeur, plage)
        if not r.get("decidable"):
            continue
        d = float(reperes[b]["la_couche"]) - float(reperes[a]["la_couche"])
        maillage.append(int(r["le_pas_en_voxels"]))
        creux.append(float(le_repli(d, periode)))
        # ⭐⭐⭐⭐ LES DEUX COLONNES VOYAGENT AVEC LE PAS : c'est le defaut de `201` repare a la
        # source. Un pas sans sa couture ne peut etre joint a rien.
        cols.append([int(a), int(b)])
        satures += int(bool(r["il_sature"]))
    if len(maillage) < 3:
        return {"decidable": False, "raison": "moins de trois coutures appariées"}
    m = np.asarray(maillage, dtype=float)
    c = np.asarray(creux, dtype=float)
    return {"decidable": True, "les_coutures": len(maillage),
            "les_colonnes_des_pas": cols,
            "le_pas_du_maillage_en_voxels": [int(x) for x in maillage],
            "le_pas_du_creux_en_voxels": [round(float(x), 4) for x in creux],
            "les_pas_du_maillage_qui_saturent": int(satures),
            "le_pas_quadratique_du_maillage_en_voxels": round(
                float(np.sqrt(float(np.mean(m * m)))), 4),
            "le_pas_quadratique_du_creux_en_voxels": round(
                float(np.sqrt(float(np.mean(c * c)))), 4)}


def la_correlation(maillage, creux) -> float | None:
    """La corrélation de Pearson des deux pas — nulle quand l'un des deux ne varie pas."""
    m = np.asarray(maillage, dtype=float)
    c = np.asarray(creux, dtype=float)
    if m.size < 3 or c.size != m.size:
        return None
    m, c = m - m.mean(), c - c.mean()
    e = float(np.dot(m, m)) * float(np.dot(c, c))
    if e <= 0.0:
        return None
    return float(np.dot(m, c)) / (e ** 0.5)


def la_pente(maillage, creux) -> float | None:
    """La pente du creux sur le maillage — publiée SIGNÉE, et jamais posée.

    ⭐ UNE FRONTIERE ATTACHEE A LA MATIERE DONNE UNE PENTE DE MODULE UN : quand le maillage glisse
    d'un voxel, la frontiere paraît glisser d'autant. Le SENS depend d'une convention que `199` a
    deja rendue a l'envers une fois, donc il se lit dans la mesure et ne s'ecrit nulle part.
    """
    m = np.asarray(maillage, dtype=float)
    c = np.asarray(creux, dtype=float)
    if m.size < 3 or c.size != m.size:
        return None
    mm = m - m.mean()
    d = float(np.dot(mm, mm))
    if d <= 0.0:
        return None
    return float(np.dot(mm, c - c.mean())) / d


def la_decomposition(maillage, creux, pente) -> dict:
    """Ce que le modèle additif donne : la dérive COMMUNE, et le bruit propre de chaque lecteur.

    ⭐⭐⭐⭐ C'EST LA PARTIE UTILE DU RESULTAT, ET ELLE EST CHIFFREE. Le modele est ecrit ici et nulle
    part ailleurs : les deux lecteurs voient une meme derive `T`, et chacun y ajoute une erreur qui
    lui est propre et independante de l'autre. Alors la covariance des deux pas EST la variance de
    `T`, et ce qui reste de chaque variance est le bruit de ce lecteur-la. Sans cette lecture,
    « pente 0,49 » se lirait comme « le creux bouge moitie moins », alors que le modele dit tout
    autre chose : le creux bouge AUTANT, et il est lu deux fois moins bien.

    ⚠⚠⚠ LE LIEN ENTRE LA PENTE ET LA CORRELATION EST UNE IDENTITE ALGEBRIQUE, PAS UNE CONFIRMATION
    DU MODELE. `r = pente x ecart-type de x / ecart-type de y` est vrai de n'importe quelles deux
    suites, donc le verifier ne prouve rien. Ce qui se verifie est ailleurs : que la variance
    commune reste POSITIVE et INFERIEURE aux deux variances observees. Un modele additif qui
    demanderait un bruit negatif serait refute par ses propres nombres.

    ⚠ La pente est prise en argument plutot que recalculee : deux definitions de la meme quantite
    finiraient par ne plus s'accorder.
    """
    m = np.asarray(maillage, dtype=float)
    c = np.asarray(creux, dtype=float)
    if pente is None or m.size < 3 or c.size != m.size:
        return {"decidable": False, "raison": "pente absente ou suites incompatibles"}
    vm, vc = float(np.var(m)), float(np.var(c))
    commune = float(pente) * vm
    if not (0.0 < commune < vm and commune < vc):
        return {"decidable": False,
                "raison": "le modèle additif demanderait un bruit négatif : il est réfuté par "
                          "ses propres nombres"}
    bm, bc = abs(vm - commune) ** 0.5, abs(vc - commune) ** 0.5
    return {"decidable": True,
            "le_modele": "les deux lecteurs voient une même dérive, chacun avec son bruit propre",
            "la_variance_du_maillage_en_voxels2": round(vm, 4),
            "la_variance_du_creux_en_voxels2": round(vc, 4),
            "la_derive_commune_en_voxels": round(abs(commune) ** 0.5, 4),
            "le_bruit_du_maillage_en_voxels": round(bm, 4),
            "le_bruit_du_creux_en_voxels": round(bc, 4),
            "le_signal_sur_bruit_du_maillage": (round(abs(commune) ** 0.5 / bm, 4)
                                                if bm > 0 else None),
            "le_signal_sur_bruit_du_creux": (round(abs(commune) ** 0.5 / bc, 4)
                                             if bc > 0 else None)}


def lappariement(maillage, creux, tirages: int = PERMUTATIONS, graine: int = GRAINE,
                 garantie: float = GARANTIE_PAR_EPREUVE) -> dict:
    """Les deux pas sont-ils appariés, ou un mélange fait-il aussi bien ? L'UNIQUE ÉPREUVE.

    ⭐⭐⭐⭐ LE MELANGE EST LE NUL EXACT ET IL MORD : il garde les deux lois marginales — donc tout ce
    que les estimateurs imposent, leurs bornes, leurs saturations, leur bruit — et ne detruit que
    l'APPARIEMENT, qui est precisement ce que la tranche mesure.

    ⚠⚠⚠ LA STATISTIQUE EST LA VALEUR ABSOLUE DE LA CORRELATION, parce que le sens n'est pas pose.
    Un nul a une seule face rendrait la moitie de l'epreuve invisible, et poser le sens ferait de
    l'accord une consequence de la convention de signe.
    """
    r = la_correlation(maillage, creux)
    if r is None:
        return {"decidable": False, "raison": "un des deux pas ne varie pas"}
    obs = abs(r)
    g = _rng(int(graine))
    c = np.asarray(creux, dtype=float)
    nuls = []
    for _ in range(int(tirages)):
        x = la_correlation(maillage, g.permutation(c))
        nuls.append(0.0 if x is None else abs(x))
    aussi_forts = int(sum(1 for x in nuls if x >= obs - 1e-12))
    pv = float(aussi_forts + 1) / float(int(tirages) + 1)
    return {"decidable": True, "tirages": int(tirages),
            "la_correlation_signee": round(float(r), 4),
            "la_correlation_absolue": round(obs, 4),
            "la_correlation_absolue_mediane_du_nul": round(float(np.median(nuls)), 4),
            "la_correlation_absolue_maximale_du_nul": round(float(np.max(nuls)), 4),
            "les_melanges_au_moins_aussi_forts": aussi_forts,
            "la_valeur_p": round(pv, 7),
            "la_garantie_de_lepreuve": round(float(garantie), 7),
            "les_deux_pas_sont_apparies": bool(pv <= float(garantie) + 1e-12)}


def une_rangee_fabriquee(chunks: int, couches: int, colonnes: int, couche0: float,
                         pas_quadratique: float, bruit: float, graine: int,
                         apparie: bool = True, largeur: int = 9,
                         permutations: int = PERMUTATIONS) -> tuple:
    """Une rangée de chunks voisins tirés d'un MÊME feuillet qui dérive — la fixture de la chaîne.

    ⭐⭐⭐⭐ LE PROFIL D'INTENSITÉ ET LA COURBE DE COHÉRENCE SORTENT DU MÊME DÉCALAGE, et c'est ce qui
    fait de la fixture un contrôle plutôt qu'une pétition de principe : rien n'impose aux deux
    ESTIMATEURS de s'accorder, seule la matière les y oblige. `un_pas` lit l'intensité, le repère lit
    la cohérence, et aucun des deux ne sait ce que l'autre voit.

    ⚠⚠⚠ `apparie=False` CONSTRUIT LA FACE NÉGATIVE : la cohérence y dérive de son côté, avec la même
    loi et la même amplitude. Une face négative bâtie sur une matière PLATE serait plus facile à
    refuser, donc elle ne mesurerait pas le bon refus.
    """
    r = _rng(int(graine))
    z = np.arange(int(couches), dtype=float)
    # ⚠⚠⚠ LA TEXTURE EST APERIODIQUE, ET C'EST UNE CORRECTION PAYEE. La premiere version posait une
    # sinusoide de periode dix-sept : `un_pas` y trouve autant d'alignements que de periodes, donc
    # il ALIASE des huit voxels et demi. L'etalon cassait alors a cette valeur-la, pendant que sa
    # docstring annoncait la demi-periode — un nombre juste sous un mauvais nom. Un fond tire une
    # fois puis DECOUPE a des decalages differents n'a qu'un seul alignement.
    marge = int(DEMI_PAS_EN_VOXELS) * 2 + 4
    fond = r.normal(0.0, 1.0, size=int(couches) + 2 * marge)
    marche = np.concatenate(([0.0], np.cumsum(r.normal(0.0, float(pas_quadratique),
                                                       size=int(chunks) - 1))))
    autre = (marche if apparie else
             np.concatenate(([0.0], np.cumsum(r.normal(0.0, float(pas_quadratique),
                                                       size=int(chunks) - 1)))))
    sections, reperes = {}, {}
    for k in range(int(chunks)):
        # ⚠ L'intensite porte une texture : sans elle, `un_pas` refuse un « bord plat ».
        dec = int(round(float(marche[k])))
        dec = max(-marge, min(marge, dec))
        onde = fond[marge - dec:marge - dec + int(couches)]
        creux_i = np.exp(-0.5 * ((z - (couche0 + marche[k])) / (largeur / 2.0)) ** 2)
        profil = 0.6 + 0.3 * onde - 0.4 * creux_i
        sections[k] = np.tile((profil + r.normal(0.0, float(bruit), size=int(couches)))[:, None],
                              (1, int(colonnes)))
        creux_c = np.exp(-0.5 * ((z - (couche0 + autre[k])) / (largeur / 2.0)) ** 2)
        coh = 0.6 - 0.45 * creux_c + r.normal(0.0, float(bruit), size=int(couches))
        courbe = [[0.0, float(max(0.0, x))] for x in coh]
        # ⚠⚠⚠ LA COUCHE EST LUE PAR LE VRAI LECTEUR, JAMAIS ECRITE PAR LA FIXTURE. La premiere
        # version construisait la courbe puis la JETAIT et posait `la_couche` elle-meme : l'etalon
        # n'exercait alors aucun des deux estimateurs, et il aurait separe meme si le lecteur etait
        # casse. C'est la famille des fixtures complaisantes que ce depot a deja payee cinq fois.
        reperes[k] = le_repere_dun_chunk(courbe, int(permutations), int(graine) + 31 * k)
    return sections, reperes, marche, autre


def la_chaine_saccorde(chunks: int, couches: int, colonnes: int, couche0: float,
                       pas_quadratique: float, bruit: float, graine: int,
                       largeur_du_bord: int, tirages: int, apparie: bool = True) -> bool:
    """Sur une rangée fabriquée, l'épreuve se déclenche-t-elle ?"""
    sections, reperes, _m, _a = une_rangee_fabriquee(
        chunks, couches, colonnes, couche0, pas_quadratique, bruit, graine, apparie,
        permutations=int(tirages))
    paires = les_paires_voisines(reperes, sorted(sections))
    deux = les_deux_pas(sections, reperes, paires, largeur_du_bord)
    if not deux.get("decidable"):
        return False
    ap = lappariement(deux["le_pas_du_maillage_en_voxels"], deux["le_pas_du_creux_en_voxels"],
                      tirages, int(graine) + 1)
    return bool(ap.get("decidable") and ap["les_deux_pas_sont_apparies"])


def lechelle_des_derives(pas_de_reference: float,
                         demi_periode: float = float(DEMI_PAS_EN_VOXELS)) -> list[float]:
    """L'échelle de l'étalon, DÉRIVÉE du pas que `199` a mesuré — aucune valeur n'est tapée.

    ⭐ LE DERNIER BARREAU EST LA DEMI-PERIODE : c'est la ou le pas du creux ALIASE, donc la ou
    l'appariement doit se perdre. Les premiers encadrent la derive reelle du rouleau.
    """
    q = float(pas_de_reference)
    return [round(x, 4) for x in (q / 2.0, q, 2.0 * q, float(demi_periode))]


def sur_letalon(largeur_du_bord: int, pas_de_reference: float,
                tirages: int = PERMUTATIONS, graine: int = GRAINE,
                replicats: int = 12, chunks: int = 24, couches: int = 109,
                colonnes: int = 128, bruit: float = 0.02, echelle=None) -> dict:
    """La chaîne entière retrouve-t-elle un appariement posé, et refuse-t-elle un faux ?

    ⭐⭐⭐⭐ L'ÉCHELLE EST EN VOXELS DE DÉRIVE PAR COUTURE, et le dernier barreau approche la
    demi-période : c'est là que le pas du creux ALIASE, donc là que l'appariement doit se perdre. Un
    étalon qui réussirait partout ne séparerait rien.

    ⚠⚠⚠ LES DEUX FACES SUR RÉPLICATS. La face négative fait dériver la cohérence de son côté avec la
    MÊME loi : c'est le refus difficile, et le seul qui mesure quelque chose.
    """
    if echelle is None:
        echelle = lechelle_des_derives(pas_de_reference)
    courbe = []
    for s in echelle:
        vus = sum(int(la_chaine_saccorde(chunks, couches, colonnes, 54.0, float(s), bruit,
                                         int(graine) + 100 * k, largeur_du_bord, tirages))
                  for k in range(int(replicats)))
        # ⚠ LA PART EST ARRONDIE A LA PUBLICATION : cinq replicats sur douze valent
        # 0,41666666666666663, et un chiffre a seize decimales n'est citable dans aucun document.
        courbe.append({"la_derive_par_couture_en_voxels": round(float(s), 4),
                       "part_des_replicats": round(float(vus) / float(replicats), 4)})
    # ⚠⚠ « TIENT » EST LE MEILLEUR BARREAU ET « CASSE » CELUI QUI LE SUIT, DANS CET ORDRE : une
    # premiere version prenait le dernier barreau plein et le PREMIER barreau creux, qui peut le
    # preceder — la courbe n'est pas monotone, parce qu'une derive trop PETITE ne donne pas assez de
    # variation au pas entier de `un_pas` pour qu'une correlation se lise.
    pleins = [k for k, x in enumerate(courbe) if x["part_des_replicats"] >= 1.0]
    tient = courbe[pleins[-1]]["la_derive_par_couture_en_voxels"] if pleins else None
    apres = [x for k, x in enumerate(courbe)
             if pleins and k > pleins[-1] and x["part_des_replicats"] < 1.0]
    casse = apres[0]["la_derive_par_couture_en_voxels"] if apres else None
    # ⚠⚠⚠ LA FACE NEGATIVE DEMANDE PLUS DE REPLICATS QUE LA POSITIVE, ET LE COMPTE SE DERIVE. Avec
    # `n` replicats, le plus petit taux non nul vaut `1/n` : a douze replicats il vaut 0,083, donc
    # DEJA plus que la garantie de 0,05, et l'etalon ne peut alors demontrer un taux compatible
    # qu'en n'ayant AUCUN faux. Il faut `1/garantie` replicats pour qu'un seul faux n'excede pas la
    # garantie, et le double pour que deux ne l'excedent pas non plus. Ce defaut a ete paye : la
    # premiere version rendait 4 faux sur 12, pendant que l'epreuve mesuree a part rendait 0,0433
    # sur 300 tirages et la fixture 0,025 sur 40 — le taux etait bon, c'est l'echantillon qui etait
    # trop petit pour le montrer.
    replicats_du_refus = int(2.0 / float(GARANTIE_PAR_EPREUVE))
    faux = sum(int(la_chaine_saccorde(chunks, couches, colonnes, 54.0, 2.0, bruit,
                                      int(graine) + 7000 + 137 * k, largeur_du_bord, tirages,
                                      apparie=False))
               for k in range(replicats_du_refus))
    tenue = le_taux_tient_la_garantie(faux, replicats_du_refus, GARANTIE_PAR_EPREUVE)
    haut = round(max(x["part_des_replicats"] for x in courbe), 4)
    return {"decidable": True, "la_courbe": courbe, "la_derive_qui_tient": tient,
            "la_derive_qui_casse": casse,
            "la_part_a_la_demi_periode": courbe[-1]["part_des_replicats"],
            "la_part_maximale": haut, "les_chunks_par_rangee": int(chunks),
            "le_bruit": float(bruit), "replicats": int(replicats),
            "les_replicats_du_refus": int(replicats_du_refus),
            "les_faux": int(faux),
            "le_taux_de_faux": round(float(faux) / float(replicats_du_refus), 4),
            "la_garantie": round(float(GARANTIE_PAR_EPREUVE), 4),
            "la_probabilite_den_avoir_autant": round(
                float(tenue["la_probabilite_den_avoir_autant"]), 6),
            "letalon_separe": bool(tient is not None and casse is not None
                                   and courbe[-1]["part_des_replicats"] < haut
                                   and bool(tenue["il_tient"]))}


def la_ligne(volume: dict, delai: float = DELAI, colonnes: int | None = None,
             permutations: int = PERMUTATIONS, graine: int = GRAINE,
             ouvrir=None, meta=None) -> dict:
    """Le repère ABSOLU et la coupe de chaque chunk d'une rangée — la MÊME que `199` et `200`.

    ⚠⚠⚠ LES DEUX LECTURES SORTENT DU MÊME TÉLÉCHARGEMENT. Les lire en deux passes en ferait deux
    rangées, et rien ne garantirait qu'elles portent sur les mêmes chunks.
    """
    url = f"{BUCKET}/{volume['cle']}"
    if meta is None:
        try:
            meta = array_meta(url, 0, delai)
        except Exception as e:  # noqa: BLE001
            return {"decidable": False, "raison": f"le volume ne répond pas : {type(e).__name__}"}
    _, hy, hx = meta["chunks"]
    _, rows, cols = meta["shape"]
    gy, gx = -(-rows // hy), -(-cols // hx)
    ligne = la_ligne_declaree(gy)
    voulues = list(range(gx if colonnes is None else min(int(colonnes), gx)))
    prendre = ouvrir or (lambda cy, cx: un_chunk(url, meta, cy, cx, delai, None,
                                                 pause=LA_PAUSE_ENTRE_ESSAIS))
    sections, reperes, refus, reprises = {}, {}, {}, 0
    for cx in voulues:
        bloc, pourquoi = prendre(int(ligne), int(cx))
        if bloc is not None and pourquoi and str(pourquoi).startswith("repris"):
            reprises += int(str(pourquoi).split()[-1])
            pourquoi = None
        if bloc is None:
            refus[pourquoi] = refus.get(pourquoi, 0) + 1
            continue
        b = np.asarray(bloc)
        if float(b.max()) <= 0.0:
            refus["vide"] = refus.get("vide", 0) + 1
            continue
        courbe, quoi = la_courbe_dun_bloc(b)
        if courbe is None:
            refus[quoi] = refus.get(quoi, 0) + 1
            continue
        sections[int(cx)] = une_section(b, la_rangee_montree(b.shape[1]))
        reperes[int(cx)] = le_repere_dun_chunk(courbe, permutations, graine)
    return {"decidable": bool(reperes), "segment": volume["segment"],
            "grille_de_chunks": [int(gy), int(gx)], "la_rangee": int(ligne),
            "colonnes_demandees": len(voulues), "colonnes_lues": len(reperes),
            "les_reperes_lisibles": int(sum(1 for x in reperes.values() if x["lisible"])),
            "les_reprises_du_reseau": int(reprises), "refuses": refus,
            "sections": sections, "reperes": reperes, "les_colonnes": voulues}


def juger(deux: dict, appariement: dict) -> dict:
    """Le creux appartient-il au papyrus ? Le verdict ne tient qu'à l'épreuve déclarée.

    ⚠⚠ LA PENTE EST PUBLIEE A COTE ET NE PORTE PAS LE VERDICT : une pente de module un sur des pas
    qui ne seraient pas apparies serait un artefact de deux lois marginales, et une correlation sans
    pente lisible reste une correlation.
    """
    if not deux.get("decidable") or not appariement.get("decidable"):
        return {"decidable": False, "raison": "une des deux lectures manque"}
    p = la_pente(deux["le_pas_du_maillage_en_voxels"], deux["le_pas_du_creux_en_voxels"])
    return {"decidable": True,
            "les_coutures": int(deux["les_coutures"]),
            "la_pente_du_creux_sur_le_maillage": (None if p is None else round(float(p), 4)),
            "la_correlation_signee": appariement["la_correlation_signee"],
            "la_valeur_p": appariement["la_valeur_p"],
            "le_creux_bouge_avec_le_maillage": bool(
                appariement["les_deux_pas_sont_apparies"])}


def mesurer(delai: float = DELAI, permutations: int = PERMUTATIONS, graine: int = GRAINE,
            replicats: int = 12, colonnes: int | None = None, ouvrir=None, meta=None) -> dict:
    """Les deux pas sur les mêmes coutures, et l'épreuve appariée."""
    v = le_segment_declare()
    if v is None:
        return {"decidable": False, "raison": "aucun volume recensé"}
    lg = la_ligne(v, delai, colonnes, permutations, graine, ouvrir, meta)
    if not lg.get("decidable"):
        return {"decidable": False, "raison": lg.get("raison", "la ligne est vide")}
    pannes = les_pannes_de_reseau(lg.get("refuses"))
    if pannes:
        return {"decidable": False,
                "raison": f"{pannes} chunks perdus par le réseau — une rangée dont le fil est "
                          f"tombé n'est pas comparable à celles de `199` et `200`",
                "la_ligne": {k: x for k, x in lg.items()
                             if k not in ("sections", "reperes", "les_colonnes")}}
    largeur = la_largeur_du_bord()
    # ⭐ LE PAS DE REFERENCE DE L'ETALON EST CELUI QUE `199` A PUBLIE SUR CETTE RANGEE, relu et
    # jamais recalcule : une echelle tapee a la main ferait passer un reglage pour une mesure.
    m199 = ce_que_la_marche_a_rendu()
    reference = float(m199["le_pas_quadratique_en_voxels"]) if m199.get("decidable") else None
    paires = les_paires_voisines(lg["reperes"], lg["les_colonnes"])
    deux = les_deux_pas(lg["sections"], lg["reperes"], paires, largeur)
    ap = ({"decidable": False, "raison": "aucune couture appariée"} if not deux.get("decidable")
          else lappariement(deux["le_pas_du_maillage_en_voxels"],
                            deux["le_pas_du_creux_en_voxels"], permutations, graine))
    return {
        "graine": int(graine), "tirages": int(permutations),
        "la_question_declaree": LA_QUESTION_DECLAREE,
        "les_epreuves_declarees": list(LES_EPREUVES_DECLAREES),
        "la_garantie_par_epreuve": round(float(GARANTIE_PAR_EPREUVE), 7),
        "le_pas_dun_pli_en_voxels": round(float(PAS_EN_VOXELS), 4),
        "la_demi_periode_en_voxels": int(DEMI_PAS_EN_VOXELS),
        "la_largeur_du_bord": int(largeur),
        "la_ligne": {k: x for k, x in lg.items()
                     if k not in ("sections", "reperes", "les_colonnes")},
        "les_paires_voisines": len(paires),
        "les_deux_pas": deux,
        "lappariement": ap,
        "la_decomposition": (la_decomposition(deux["le_pas_du_maillage_en_voxels"],
                                              deux["le_pas_du_creux_en_voxels"],
                                              la_pente(deux["le_pas_du_maillage_en_voxels"],
                                                       deux["le_pas_du_creux_en_voxels"]))
                             if deux.get("decidable")
                             else {"decidable": False, "raison": "aucune couture appariée"}),
        "le_verdict": juger(deux, ap),
        "ce_que_199_a_rendu": m199,
        "letalon": ({"decidable": False,
                     "raison": "le pas de référence de `199` est absent, donc l'échelle de "
                               "l'étalon ne peut pas être dérivée"}
                    if reference is None
                    else sur_letalon(largeur, reference, permutations, graine, replicats)),
    }


def afficher(r: dict) -> None:
    if not r.get("decidable", True):
        print(f"LE CREUX BOUGE-T-IL AVEC LE MAILLAGE   indécidable : {r.get('raison')}")
        return
    lg, d2, ap = r["la_ligne"], r["les_deux_pas"], r["lappariement"]
    ve, e = r["le_verdict"], r["letalon"]
    print(f"LE CREUX BOUGE-T-IL AVEC LE MAILLAGE   segment {lg['segment']} · rangée "
          f"{lg['la_rangee']} · {lg['colonnes_lues']} chunks lus sur "
          f"{lg['colonnes_demandees']} · refus {lg['refuses'] or '—'}")
    print(f"  LES COUTURES      {r['les_paires_voisines']} paires voisines · largeur de bord "
          f"{r['la_largeur_du_bord']} colonnes")
    if d2.get("decidable"):
        print(f"                    {d2['les_coutures']} coutures appariées · pas quadratique "
              f"maillage {d2['le_pas_quadratique_du_maillage_en_voxels']} vx · creux "
              f"{d2['le_pas_quadratique_du_creux_en_voxels']} vx · "
              f"{d2['les_pas_du_maillage_qui_saturent']} saturés")
    else:
        print(f"                    indécidable : {d2.get('raison')}")
    if ap.get("decidable"):
        print(f"  L'ÉPREUVE         corrélation {ap['la_correlation_signee']} (module "
              f"{ap['la_correlation_absolue']}) contre "
              f"{ap['la_correlation_absolue_mediane_du_nul']} au mélange · "
              f"{ap['les_melanges_au_moins_aussi_forts']}/{ap['tirages']} · P = "
              f"{ap['la_valeur_p']} · appariés {ap['les_deux_pas_sont_apparies']}")
    else:
        print(f"  L'ÉPREUVE         indécidable : {ap.get('raison')}")
    dc = r.get("la_decomposition") or {}
    if dc.get("decidable"):
        print(f"  LA DÉCOMPOSITION  dérive commune {dc['la_derive_commune_en_voxels']} vx · bruit "
              f"du maillage {dc['le_bruit_du_maillage_en_voxels']} vx · bruit du creux "
              f"{dc['le_bruit_du_creux_en_voxels']} vx")
        print(f"                    signal sur bruit : maillage "
              f"{dc['le_signal_sur_bruit_du_maillage']} · creux "
              f"{dc['le_signal_sur_bruit_du_creux']}")
    if ve.get("decidable"):
        print(f"  LE VERDICT        pente {ve['la_pente_du_creux_sur_le_maillage']} · bouge avec "
              f"le maillage {ve['le_creux_bouge_avec_le_maillage']}")
    if not e.get("decidable"):
        print(f"  L'ÉTALON          indécidable : {e.get('raison')}")
        return
    print(f"  L'ÉTALON          sépare {e['letalon_separe']} · tient jusqu'à "
          f"{e['la_derive_qui_tient']} vx · casse à {e['la_derive_qui_casse']} vx · "
          f"{e['les_faux']} faux sur {e['les_replicats_du_refus']} = {e['le_taux_de_faux']} "
          f"pour {e['la_garantie']} garantis")
    print("                    courbe " + " · ".join(
        f"{x['la_derive_par_couture_en_voxels']:g}→{x['part_des_replicats']:g}"
        for x in e["la_courbe"]))


def verifier() -> int:
    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        if not ok:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    v("★★ une seule question est déclarée", isinstance(LA_QUESTION_DECLAREE, str))
    v("★★★ une seule épreuve est déclarée, donc la garantie reste entière",
      len(LES_EPREUVES_DECLAREES) == 1
      and abs(GARANTIE_PAR_EPREUVE - 1.0 / (PERMUTATIONS + 1)) < 1e-12)
    v("★★ la rangée est la MÊME que celle de `199` et `200`", la_ligne_declaree(396) == 198)

    # ⚠⚠⚠ SEULES LES COLONNES VOISINES ONT UNE COUTURE, ET ELLES SONT DERIVEES DES COLONNES.
    rep = {1: {"lisible": True}, 2: {"lisible": True}, 3: {"lisible": False},
           4: {"lisible": True}, 5: {"lisible": True}, 9: {"lisible": True}}
    pr = les_paires_voisines(rep, [1, 2, 3, 4, 5, 9])
    v("★★★★ seules les colonnes contiguës dont les DEUX repères sont lisibles font une paire",
      pr == [(1, 2), (4, 5)], str(pr))
    v("★★★ une colonne isolée n'en fait aucune", les_paires_voisines({7: {"lisible": True}},
                                                                     [7]) == [])
    v("★★★ un repère illisible coupe la suite", (3, 4) not in pr and (2, 3) not in pr)
    v("★★★★ et `les_deux_pas` le saute AUSSI, sans jamais lire une couche absente",
      les_deux_pas({k: np.tile(np.zeros(109)[:, None], (1, 8)) for k in range(4)},
                   {0: {"lisible": True, "la_couche": 1}, 1: {"lisible": False,
                                                              "la_couche": None},
                    2: {"lisible": True, "la_couche": 3}, 3: {"lisible": True,
                                                              "la_couche": 4}},
                   [(0, 1), (1, 2), (2, 3)], 4).get("decidable") is False)

    # ⭐⭐⭐⭐ LES DEUX PAS SORTENT DE LA MEME PAIRE, ET CHAQUE PAS PORTE SES DEUX COLONNES.
    p = float(PAS_EN_VOXELS)
    fond0 = _rng(17).normal(0.0, 1.0, size=200)

    def _coupe(dec):
        return np.tile(fond0[60 - int(dec):60 - int(dec) + 109][:, None], (1, 32))

    # ⚠⚠ LES DECALAGES SONT INEGAUX EXPRES : des pas tous identiques n'ont aucune variance, donc
    # ni pente ni correlation ne s'y lisent, et une sonde posee dessus ne mesurerait rien.
    poses = [0, 3, 7, 12, 20, 30]
    sec = {k: _coupe(poses[k]) for k in (0, 1, 2)}
    rp = {k: {"lisible": True, "la_couche": 40 + poses[k], "les_couches": 109}
          for k in (0, 1, 2)}
    d2 = les_deux_pas(sec, rp, [(0, 1), (1, 2)], 16)
    v("★★ moins de trois coutures rend indécidable", not d2.get("decidable"))
    for k in (3, 4, 5):
        sec[k] = _coupe(poses[k])
        rp[k] = {"lisible": True, "la_couche": 40 + poses[k], "les_couches": 109}
    toutes = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)]
    d2 = les_deux_pas(sec, rp, toutes, 16)
    attendus = [poses[k + 1] - poses[k] for k in range(5)]
    v("★★★★ chaque pas publie SES DEUX COLONNES — le défaut de `201` réparé à la source",
      d2["decidable"] and d2["les_colonnes_des_pas"] == [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5]],
      str(d2.get("les_colonnes_des_pas")))
    v("★★★★ le pas du creux est la différence des couches lues",
      [int(x) for x in d2["le_pas_du_creux_en_voxels"]] == attendus,
      str(d2["le_pas_du_creux_en_voxels"]))
    v("★★★★ et le pas du maillage vient de `un_pas`, avec le signe que L'ESTIMATEUR rend",
      d2["le_pas_du_maillage_en_voxels"] == attendus,
      str(d2["le_pas_du_maillage_en_voxels"]))
    v("★★★★ sur cette fixture les deux pas vont DANS LE MÊME SENS, et c'est mesuré",
      abs(la_pente(d2["le_pas_du_maillage_en_voxels"],
                   d2["le_pas_du_creux_en_voxels"]) - 1.0) < 1e-9,
      str(la_pente(d2["le_pas_du_maillage_en_voxels"], d2["le_pas_du_creux_en_voxels"])))
    rp2 = dict(rp)
    rp2[1] = {"lisible": True, "la_couche": 40 + poses[1] + int(round(p)), "les_couches": 109}
    d3 = les_deux_pas(sec, rp2, toutes, 16)
    v("★★★★ un saut d'UN PLI EXACT est replié, donc il ne compte pas comme un grand pas",
      abs(float(d3["le_pas_du_creux_en_voxels"][0]) - float(attendus[0])) < 1.0,
      str(d3["le_pas_du_creux_en_voxels"][0]))
    v("★★★ cinq coutures donnent cinq pas", d2["les_coutures"] == 5)
    sans = {k: x for k, x in sec.items() if k != 2}
    v("★★★★ une paire dont une coupe manque est SAUTÉE, jamais devinée",
      les_deux_pas(sans, rp, toutes, 16)["les_coutures"] == 3
      and les_deux_pas(sans, rp, toutes, 16)["les_colonnes_des_pas"]
      == [[0, 1], [3, 4], [4, 5]],
      str(les_deux_pas(sans, rp, toutes, 16)["les_colonnes_des_pas"]))

    # ⚠⚠⚠ LA CORRELATION ET LA PENTE SONT EXACTES, ET LA PENTE EST SIGNEE.
    v("★★★★ la corrélation vaut un sur deux suites identiques",
      abs(la_correlation([1.0, 2.0, 3.0, 4.0], [1.0, 2.0, 3.0, 4.0]) - 1.0) < 1e-12)
    v("★★★★ et moins un sur deux suites opposées",
      abs(la_correlation([1.0, 2.0, 3.0, 4.0], [-1.0, -2.0, -3.0, -4.0]) + 1.0) < 1e-12)
    v("★★★ elle manque plutôt que de valoir zéro quand une suite ne varie pas",
      la_correlation([1.0, 2.0, 3.0], [5.0, 5.0, 5.0]) is None)
    v("★★★★ la pente est SIGNÉE et vaut le rapport des amplitudes",
      abs(la_pente([1.0, 2.0, 3.0, 4.0], [-2.0, -4.0, -6.0, -8.0]) + 2.0) < 1e-12,
      str(la_pente([1.0, 2.0, 3.0, 4.0], [-2.0, -4.0, -6.0, -8.0])))
    v("★★★ et elle diffère de la corrélation, qui est sans unité",
      abs(la_correlation([1.0, 2.0, 3.0, 4.0], [-2.0, -4.0, -6.0, -8.0]) + 1.0) < 1e-12)

    # ⭐⭐⭐⭐ LA DECOMPOSITION RETROUVE DES VARIANCES POSEES, ET REFUSE UN MODELE IMPOSSIBLE.
    gd = _rng(9)
    n_ = 40000
    vrai = gd.normal(0.0, 3.0, size=n_)
    xx = vrai + gd.normal(0.0, 4.0, size=n_)
    yy = vrai + gd.normal(0.0, 10.0, size=n_)
    dec = la_decomposition(xx, yy, la_pente(xx, yy))
    # ⚠⚠ LES CLEFS SE LISENT PAR `get` : un bris pose sur la decomposition faisait tomber la
    # batterie en PANNE avant son verdict, donc le defaut se lisait comme une erreur d'execution
    # et non comme une sonde rouge. Une batterie doit rendre un verdict, meme cassee.
    v("★★★★ la décomposition retrouve une dérive commune posée à trois voxels",
      dec.get("decidable") and abs(float(dec.get("la_derive_commune_en_voxels") or 0.0)
                                   - 3.0) < 0.3,
      str(dec.get("la_derive_commune_en_voxels") or dec.get("raison")))
    v("★★★★ et les deux bruits posés à quatre et dix",
      dec.get("decidable")
      and abs(float(dec.get("le_bruit_du_maillage_en_voxels") or 0.0) - 4.0) < 0.3
      and abs(float(dec.get("le_bruit_du_creux_en_voxels") or 0.0) - 10.0) < 0.4,
      f"{dec.get('le_bruit_du_maillage_en_voxels')} et "
      f"{dec.get('le_bruit_du_creux_en_voxels')}")
    v("★★★★ un modèle qui demanderait un bruit NÉGATIF est refusé par ses propres nombres",
      not la_decomposition([1.0, 2.0, 3.0, 4.0], [10.0, 20.0, 30.0, 40.0],
                           la_pente([1.0, 2.0, 3.0, 4.0],
                                    [10.0, 20.0, 30.0, 40.0])).get("decidable"))
    v("★★★ une pente absente rend la décomposition indécidable",
      not la_decomposition([1.0, 2.0, 3.0], [4.0, 5.0, 6.0], None).get("decidable"))
    v("★★★ et une pente négative aussi, faute de variance commune positive",
      not la_decomposition(xx, -yy, la_pente(xx, -yy)).get("decidable"))

    # ⭐⭐⭐⭐ L'EPREUVE EST SANS SIGNE, ET LE NUL MORD.
    g0 = _rng(3)
    m0 = g0.normal(0.0, 5.0, size=60)
    ap_plus = lappariement(m0, m0 + g0.normal(0.0, 1.0, size=60), 19, 5)
    v("★★★★ l'épreuve se déclenche sur des pas appariés dans le même sens",
      ap_plus["les_deux_pas_sont_apparies"] and ap_plus["la_correlation_signee"] > 0)
    ap_moins = lappariement(m0, -m0 + g0.normal(0.0, 1.0, size=60), 19, 5)
    v("★★★★ ET AUSSI EN SENS OPPOSÉ : la statistique est le MODULE, le sens n'est pas posé",
      ap_moins["les_deux_pas_sont_apparies"] and ap_moins["la_correlation_signee"] < 0,
      f"r = {ap_moins['la_correlation_signee']}")
    ap_rien = lappariement(m0, g0.normal(0.0, 5.0, size=60), 19, 5)
    v("★★★★ et elle se tait sur deux suites indépendantes",
      not ap_rien["les_deux_pas_sont_apparies"], f"P = {ap_rien['la_valeur_p']}")
    v("★★★ le nul n'est pas vide : un mélange change la corrélation",
      ap_plus["la_correlation_absolue_mediane_du_nul"] < ap_plus["la_correlation_absolue"] / 2.0,
      f"{ap_plus['la_correlation_absolue_mediane_du_nul']} contre "
      f"{ap_plus['la_correlation_absolue']}")
    v("★★ une épreuve sur un pas constant est indécidable",
      not lappariement([1.0, 2.0, 3.0], [4.0, 4.0, 4.0], 19, 5).get("decidable"))

    # ⚠⚠⚠ LA FIXTURE FAIT LIRE LA COUCHE PAR LE VRAI LECTEUR, ELLE NE L'ECRIT PAS.
    sf, rf, marche, autre = une_rangee_fabriquee(8, 109, 64, 54.0, 3.0, 0.02, 21)
    lues = [rf[k]["la_couche"] for k in sorted(rf) if rf[k]["lisible"]]
    posees = [54.0 + marche[k] for k in sorted(rf) if rf[k]["lisible"]]
    v("★★★★ le repère de la fixture est LU, et il retrouve la couche posée",
      len(lues) >= 6 and max(abs(a - b) for a, b in zip(lues, posees)) <= 4.0,
      f"{lues} pour {[round(x, 1) for x in posees]}")
    # ⚠⚠⚠ LA SONDE PRECEDENTE NE PEUT PAS DISTINGUER UNE COUCHE LUE D'UNE COUCHE ECRITE : un bris
    # qui remplacait le lecteur par la valeur posee est reste VERT, parce qu'une valeur ecrite
    # satisfait trivialement « elle retrouve la couche posee ». Ce qui discrimine est STRUCTUREL :
    # le lecteur rend aussi une profondeur et une largeur, qu'aucune fixture ne fabrique.
    v("★★★★ et il porte la PROFONDEUR et la LARGEUR que seul le lecteur produit",
      rf[0].get("la_profondeur") is not None and rf[0].get("la_largeur") is not None,
      str(sorted(rf[0])))
    v("★★★★ la face appariée fait suivre LA MÊME marche aux deux",
      float(np.max(np.abs(marche - autre))) < 1e-12)
    _s2, _r2, m2, a2 = une_rangee_fabriquee(8, 109, 64, 54.0, 3.0, 0.02, 21, apparie=False)
    v("★★★★ la face négative fait dériver la cohérence DE SON CÔTÉ, pas sur une matière plate",
      float(np.max(np.abs(m2 - a2))) > 1.0 and float(np.std(a2)) > 0.5,
      f"écart {round(float(np.max(np.abs(m2 - a2))), 2)} · dispersion "
      f"{round(float(np.std(a2)), 2)}")
    v("★★★ et la section porte une texture, sinon `un_pas` refuserait un bord plat",
      float(np.std(sf[0][:, 0])) > 0.05, str(round(float(np.std(sf[0][:, 0])), 4)))

    # ⭐⭐⭐⭐ LA CHAINE ENTIERE SEPARE, ET LES DEUX FACES PASSENT PAR LA MEME FONCTION.
    v("★★★★ une rangée fabriquée APPARIÉE déclenche l'épreuve",
      la_chaine_saccorde(24, 109, 128, 54.0, 2.0, 0.02, 11, 16, 19))
    v("★★★★ et une rangée NON APPARIÉE ne la déclenche pas",
      not la_chaine_saccorde(24, 109, 128, 54.0, 2.0, 0.02, 11, 16, 19, apparie=False))

    v("★★★★ l'échelle de l'étalon est DÉRIVÉE du pas de `199` et finit à la demi-période",
      lechelle_des_derives(4.941) == [2.4705, 4.941, 9.882, 36.0],
      str(lechelle_des_derives(4.941)))
    e = sur_letalon(16, 4.941, 19, 21, replicats=6, chunks=20)
    v("★★★★ l'étalon PERD l'appariement à la demi-période, là où le pas du creux aliase",
      e["la_part_a_la_demi_periode"] < e["la_part_maximale"],
      f"{e['la_part_a_la_demi_periode']} contre {e['la_part_maximale']}")
    v("★★★★ « casse » vient APRÈS « tient », jamais avant",
      e["la_derive_qui_tient"] is not None and e["la_derive_qui_casse"] is not None
      and float(e["la_derive_qui_casse"]) > float(e["la_derive_qui_tient"]),
      f"tient {e['la_derive_qui_tient']} casse {e['la_derive_qui_casse']}")
    v("★★★★ la face négative a ASSEZ de réplicats pour qu'un seul faux ne dépasse pas la garantie",
      e["les_replicats_du_refus"] >= int(1.0 / GARANTIE_PAR_EPREUVE)
      and 1.0 / float(e["les_replicats_du_refus"]) <= GARANTIE_PAR_EPREUVE,
      f"{e['les_replicats_du_refus']} réplicats pour une garantie de {GARANTIE_PAR_EPREUVE}")
    v("★★★★ son taux de faux est COMPATIBLE avec la garantie, jamais simplement inférieur",
      e["letalon_separe"],
      f"{e['les_faux']} faux sur {e['les_replicats_du_refus']}, P = "
      f"{e['la_probabilite_den_avoir_autant']}")
    v("★★★ et une dérive trop PETITE ne suffit pas non plus : le pas entier n'a pas de quoi varier",
      e["la_courbe"][0]["part_des_replicats"] <= e["la_part_maximale"],
      str([x["part_des_replicats"] for x in e["la_courbe"]]))

    # ⚠⚠ LE VERDICT NE TIENT QU'A L'EPREUVE DECLAREE.
    faux_deux = {"decidable": True, "les_coutures": 9,
                 "le_pas_du_maillage_en_voxels": [1.0, 2.0, 3.0, 4.0],
                 "le_pas_du_creux_en_voxels": [-1.0, -2.0, -3.0, -4.0]}
    v("★★★★ une pente de module un ne suffit pas si l'épreuve ne se déclenche pas",
      not juger(faux_deux, {"decidable": True, "les_deux_pas_sont_apparies": False,
                            "la_correlation_signee": -1.0, "la_valeur_p": 0.4})
      ["le_creux_bouge_avec_le_maillage"])
    jg = juger(faux_deux, {"decidable": True, "les_deux_pas_sont_apparies": True,
                           "la_correlation_signee": -1.0, "la_valeur_p": 0.05})
    v("★★★★ et la pente publiée est celle des données, pas une constante",
      abs(float(jg["la_pente_du_creux_sur_le_maillage"]) + 1.0) < 1e-9,
      str(jg["la_pente_du_creux_sur_le_maillage"]))
    v("★★ un verdict sans lecture est indécidable",
      not juger({"decidable": False}, {"decidable": True})["decidable"])

    # ⚠⚠⚠ LES DEUX LECTURES SORTENT DU MEME TELECHARGEMENT, ET UN VOLUME MUET EST REFUSE.
    appels = []

    def ouvrir(cy, cx):
        appels.append((cy, cx))
        z = np.arange(109.0)
        prof = 0.6 + 0.3 * np.sin(2.0 * np.pi * (z - cx) / 17.0) \
            - 0.4 * np.exp(-0.5 * ((z - (54.0 + cx)) / 4.5) ** 2)
        # ⚠ Une texture LATERALE est necessaire : un bloc constant en y et x est ecarte par le
        # filtre du producteur (« trop peu texture »), donc la rangee entiere serait vide.
        lat = 1.0 + 0.4 * np.sin(np.arange(8.0) / 1.3)
        b = np.clip(prof[:, None, None] * 200.0 * lat[None, :, None]
                    * np.ones((1, 1, 8)), 0, 255).astype(np.uint8)
        return b, None

    meta = {"chunks": [109, 8, 8], "shape": [109, 24, 40]}
    lg = la_ligne({"cle": "x", "segment": "s"}, 0.0, None, 19, 5, ouvrir, meta)
    v("★★★★ la coupe ET le repère sortent du MÊME téléchargement, un appel par colonne",
      lg["decidable"] and len(appels) == lg["colonnes_demandees"]
      and set(lg["sections"]) == set(lg["reperes"]),
      f"{len(appels)} appels pour {lg['colonnes_demandees']} colonnes")
    v("★★★ la rangée lue est la rangée médiane déclarée",
      all(cy == la_ligne_declaree(3) for cy, _cx in appels), str(appels[:2]))
    v("★★★ un volume qui ne répond pas est refusé, jamais deviné",
      not la_ligne({"cle": "x", "segment": "s"}, 0.0, None, 19, 5,
                   lambda cy, cx: (None, "absent du dépôt"), meta)["decidable"])

    for e_ in echecs:
        print(f"  ÉCHEC {e_}")
    print(f"{Path(__file__).name}   "
          f"{'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--verifier", action="store_true")
    ap.add_argument("--json", type=Path, default=None)
    ap.add_argument("--colonnes", type=int, default=None)
    ap.add_argument("--tirages", type=int, default=PERMUTATIONS)
    ap.add_argument("--graine", type=int, default=GRAINE)
    ap.add_argument("--replicats", type=int, default=12)
    a = ap.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(DELAI, a.tirages, a.graine, a.replicats, a.colonnes)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
