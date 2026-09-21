"""La marche construite sur la MOYENNE des rangées du treillis traverse-t-elle vraiment ?

⭐⭐⭐⭐ POURQUOI CE FICHIER, ET C'EST `208` QUI LE FORCE. `207` a nommé le plafond d'une rangée
seule : même avec un lecteur PARFAIT, la dérive seule donne **34,8806 voxels** sur les 244 coutures
d'une rangée, contre un demi-feuillet de **36**. Une rangée se traverse de justesse et rien de plus
long ne se traverse. `208` a mesuré qu'une fermeture de boucle existe — deux rangées voisines du
treillis partagent une dérive de **1,5129 voxels** pendant que chacune garde un bruit propre de
**1,9387** et **1,899** — et il en a tiré une excursion de **23,5352 voxels**, sous le demi-feuillet.

⚠⚠⚠ MAIS CE NOMBRE EST UNE PROJECTION, ET UNE BORNE OPTIMISTE. Il suppose que moyenner les rangées
retire TOUT le bruit propre ; trois lectures n'en retirent qu'une part en racine de trois. La
prédiction honnête se pose donc avant la mesure et elle a deux bornes, pas une :
l'OPTIMISTE est la dérive partagée seule, la RÉALISTE est la racine de la somme de son carré et du
carré du bruit propre divisé par trois. La dispersion MESURÉE du pas moyenné dira où elle tombe, et
c'est exactement ce qui rend cette tranche falsifiable.

⚠⚠ LE PIÈGE EST ÉCRIT D'AVANCE, ET C'EST CELUI DE `207` : les rangées du treillis n'ont PAS les
mêmes trous — `208` a lu **255**, **251** et **254 chunks** — donc les coutures COMMUNES aux trois
sont moins nombreuses, et le plus long tronçon commun est plus court que celui d'une rangée seule.
Une marche qui traverse un tronçon plus court n'a pas traversé davantage, donc la longueur est
publiée À CÔTÉ de l'excursion et jamais après.

⭐⭐⭐⭐ ET LE CONTRÔLE EST GRATUIT, PARCE QU'IL EST APPARIÉ : la rangée médiane SEULE, restreinte aux
MÊMES coutures, donne une seconde marche de même longueur. Le rapport des deux excursions est donc
un gain mesuré à longueur égale, sans qu'aucune correction n'entre. ⚠ Il reste bruité — l'excursion
d'une seule réalisation est très variable, `207` l'a payé — donc ce qui décide est la DISPERSION du
pas, moyennée sur toutes les coutures, et l'excursion répond à « traverse-t-elle », pas à « de
combien ».

Usage :
    uv run python src/nappe/la_moyenne_des_rangees_traverse_t_elle.py --verifier
    uv run python src/nappe/la_moyenne_des_rangees_traverse_t_elle.py \\
        --json docs/mesures/la_moyenne_des_rangees_traverse_t_elle.json
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

from combien_de_rangees_faut_il_pour_lire_le_pas import la_ligne  # noqa: E402
from la_derive_saccumule_t_elle import (contre_les_signes,  # noqa: E402
                                        les_troncons)
from la_recette_posee_sur_le_rouleau import DELAI, PERMUTATIONS  # noqa: E402
from le_cumul_recale_traverse_t_il_la_rangee import (la_dispersion_de_204,  # noqa: E402
                                                     le_cumul, lexcursion,
                                                     lexcursion_predite)
from ou_le_maillage_quitte_t_il_son_feuillet import (le_segment_declare,  # noqa: E402
                                                     les_pannes_de_reseau)
from ouvrir_les_quinze import _rng  # noqa: E402
from que_montrent_ces_deux_vues import (DEMI_PAS_EN_VOXELS,  # noqa: E402
                                        PAS_EN_VOXELS)
from une_rangee_voisine_lit_elle_le_meme_pas import (les_pas_dune_rangee,  # noqa: E402
                                                     les_rangees_du_treillis)
from zarr_depth import BUCKET, array_meta  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
CE_QUE_LA_VOISINE_A_RENDU = MESURES / "une_rangee_voisine_lit_elle_le_meme_pas.json"
CE_QUE_LE_CUMUL_A_RENDU = MESURES / "le_cumul_recale_traverse_t_il_la_rangee.json"
GRAINE = 20261018
LES_RANGEES = 16

LA_QUESTION_DECLAREE = ("la marche construite sur la moyenne des rangées du treillis traverse-t-elle "
                        "son tronçon sans jamais s'éloigner d'un demi-feuillet de son départ ?")
LES_EPREUVES_DECLAREES = ("les pas moyennés des rangées du treillis s'additionnent-ils, ou se "
                          "compensent-ils",)
GARANTIE = 1.0 / (PERMUTATIONS + 1)
GARANTIE_PAR_EPREUVE = GARANTIE / len(LES_EPREUVES_DECLAREES)


def ce_que_la_voisine_a_rendu(chemin: Path = CE_QUE_LA_VOISINE_A_RENDU) -> dict:
    """La dérive partagée et le bruit propre, tels que `208` les a publiés — relus, jamais refaits.

    ⚠⚠⚠ LES DEUX PIECES DE LA PREDICTION VIENNENT DE LEUR PRODUCTEUR. `208` a separe le pas en une
    part que deux rangees voisines PARTAGENT et une part PROPRE a chacune ; cette tranche ne refait
    pas cette separation, elle en tire une consequence. Retaper les nombres ici en ferait une
    seconde definition, et deux definitions finissent par ne pas s'accorder.
    """
    if not Path(chemin).is_file():
        return {"decidable": False, "raison": "la mesure de `208` est absente"}
    d = json.loads(Path(chemin).read_text(encoding="utf-8"))
    v = d.get("le_verdict") or {}
    if not v.get("decidable") or v.get("la_derive_partagee_en_voxels") is None:
        return {"decidable": False, "raison": "`208` ne publie pas de dérive partagée"}
    return {"decidable": True,
            "la_derive_partagee_en_voxels": v.get("la_derive_partagee_en_voxels"),
            "le_bruit_de_la_mediane_en_voxels": v.get("le_bruit_de_la_mediane_en_voxels"),
            "le_bruit_de_la_voisine_en_voxels": v.get("le_bruit_de_la_voisine_en_voxels"),
            "les_coutures_communes_a_deux": v.get("les_coutures_communes"),
            "la_rangee_mediane": v.get("la_rangee_mediane")}


def ce_que_le_cumul_a_rendu(chemin: Path = CE_QUE_LE_CUMUL_A_RENDU) -> dict:
    """Ce que `207` a mesuré sur UNE rangée — la marche à laquelle celle-ci se compare.

    ⚠⚠ SA LONGUEUR EST LUE AUSSI, ET C'EST ELLE QUI COMPTE : comparer deux excursions sans comparer
    leurs longueurs dirait qu'une marche plus courte traverse mieux.
    """
    if not Path(chemin).is_file():
        return {"decidable": False, "raison": "la mesure de `207` est absente"}
    d = json.loads(Path(chemin).read_text(encoding="utf-8"))
    v = d.get("le_verdict") or {}
    if not v.get("decidable") or v.get("lexcursion_en_voxels") is None:
        return {"decidable": False, "raison": "`207` ne publie pas d'excursion"}
    return {"decidable": True,
            "lexcursion_en_voxels": v.get("lexcursion_en_voxels"),
            "lexcursion_en_plis": v.get("lexcursion_en_plis"),
            "les_pas_du_cumul": d.get("les_pas_du_cumul"),
            "les_coutures_de_tous_les_troncons": d.get("les_coutures_de_tous_les_troncons")}


def la_dispersion_predite(partagee, propre, combien: int) -> dict:
    """Ce que moyenner `k` rangées laisse — posé avant la mesure, et avec ses DEUX bornes.

    ⭐⭐⭐⭐ LES DEUX BORNES SONT LA RAISON D'ETRE DE CETTE TRANCHE. `208` a projete la borne
    OPTIMISTE : moyenner retire tout le bruit propre et laisse la derive partagee. Mais `k` lectures
    d'un bruit propre n'en retirent qu'une part en racine de `k`, donc la borne REALISTE vaut la
    racine du carre de la derive partagee plus le carre du bruit propre divise par `k`. La mesure
    tombera entre les deux, ou en dehors, et c'est ce qui la rend refutable.

    ⚠⚠ LE MODELE SUPPOSE QUE LES TROIS RANGEES PORTENT LE MEME BRUIT PROPRE, ce que `208` n'a pas
    mesure — il n'a decompose que des PAIRES. Le bruit de la mediane est donc pris comme
    representatif, et le dire est le seul comportement honnete : une moyenne de bruits inegaux
    retire un peu moins que cette formule.
    """
    if partagee is None or propre is None or int(combien) < 1:
        return {"decidable": False,
                "raison": "la dérive partagée, le bruit propre ou le nombre de rangées manque"}
    p, b, k = float(partagee), float(propre), int(combien)
    realiste = float(np.sqrt(p * p + (b * b) / float(k)))
    seule = float(np.sqrt(p * p + b * b))
    return {"decidable": True, "les_rangees_moyennees": k,
            "la_derive_partagee_en_voxels": round(p, 4),
            "le_bruit_propre_en_voxels": round(b, 4),
            "la_borne_optimiste_en_voxels": round(p, 4),
            "la_borne_realiste_en_voxels": round(realiste, 4),
            "ce_quune_rangee_seule_porte_en_voxels": round(seule, 4),
            "ce_que_la_moyenne_retire_au_mieux": round(seule - p, 4),
            "ce_que_trois_lectures_retirent": round(seule - realiste, 4)}


def les_coutures_communes_aux_rangees(pas_par_rangee: dict) -> list[int]:
    """Les colonnes où TOUTES les rangées ont lu un pas — l'intersection, jamais l'union.

    ⚠⚠⚠ UNE COUTURE QU'UNE SEULE RANGEE N'A PAS LUE N'EST PAS MOYENNABLE : y prendre la moyenne des
    deux autres melangerait deux quantites de dispersions differentes dans une meme marche, donc le
    cumul cesserait d'etre l'accumulation d'un seul objet. L'union serait plus longue et fausse.
    """
    if not pas_par_rangee:
        return []
    commun = None
    for pas in pas_par_rangee.values():
        cles = set(int(c) for c in pas)
        commun = cles if commun is None else (commun & cles)
    return sorted(commun or [])


def le_pas_moyenne(pas_par_rangee: dict, coutures) -> list[float]:
    """Le pas moyen des rangées, couture par couture, INDEXÉ PAR COLONNE.

    ⚠⚠⚠ L'INDEX EST LA COLONNE ET JAMAIS LE RANG. Deux rangees du treillis n'ont pas les memes
    trous, donc leurs listes de pas n'ont ni la meme longueur ni le meme alignement : moyenner par
    RANG joindrait des coutures qui ne sont pas au meme endroit du rouleau. C'est le defaut que
    `201` a paye et que `202` a repare, et il se repaie ici des qu'on cesse d'y penser.
    """
    out = []
    for c in coutures:
        vals = [float(pas[int(c)]) for pas in pas_par_rangee.values() if int(c) in pas]
        out.append(float(np.mean(vals)) if vals else float("nan"))
    return out


def ce_que_la_moyenne_a_retire(pas_par_rangee: dict, coutures, predite: dict) -> dict:
    """La dispersion MESURÉE du pas moyenné, contre les deux bornes posées d'avance.

    ⭐⭐⭐⭐ C'EST LE NOMBRE QUI DECIDE, ET NON L'EXCURSION. Une dispersion est une moyenne sur toutes
    les coutures, donc elle est stable ; une excursion est une seule realisation, donc elle varie
    beaucoup — `207` l'a paye en voyant son etalon refuser une epreuve batie dessus. L'excursion
    repond a « traverse-t-elle », la dispersion repond a « de combien la moyenne a-t-elle aide ».

    ⚠ La dispersion de CHAQUE rangee est publiee a cote : deux rangees qui ne liraient qu'une valeur
    constante auraient une moyenne de dispersion nulle sans que rien n'ait ete retire.
    """
    cs = [int(c) for c in coutures]
    if len(cs) < 3:
        return {"decidable": False, "raison": "moins de trois coutures communes"}
    moy = np.asarray(le_pas_moyenne(pas_par_rangee, cs), dtype=float)
    if not np.all(np.isfinite(moy)):
        return {"decidable": False, "raison": "une couture commune n'est lue par aucune rangée"}
    par_rangee = {int(r): round(float(np.std([float(p[c]) for c in cs])), 4)
                  for r, p in pas_par_rangee.items()}
    mesuree = float(np.std(moy))
    opt = predite.get("la_borne_optimiste_en_voxels")
    rea = predite.get("la_borne_realiste_en_voxels")
    # ⚠⚠⚠ L'ERREUR D'ECHANTILLONNAGE EST PUBLIEE, ET ELLE EST DERIVEE : l'ecart-type d'un
    # ecart-type estime sur `n` tirages vaut lui-meme divise par la racine de deux fois `n`. Sans
    # elle, une mesure qui depasse une borne de deux pour cent se lit comme un modele refute, alors
    # que l'ecart peut valoir une demi-erreur. Et c'est la meme quantite qui borne les sondes.
    erreur = mesuree / float(np.sqrt(2.0 * len(cs)))
    ecart = ((mesuree - float(rea)) / erreur) if (rea and erreur > 0.0) else None
    return {"decidable": True, "les_coutures": len(cs),
            "les_rangees_moyennees": len(pas_par_rangee),
            "la_dispersion_de_chaque_rangee_en_voxels": par_rangee,
            "la_dispersion_mediane_dune_rangee_en_voxels": round(
                float(np.median(list(par_rangee.values()))), 4),
            "la_dispersion_du_pas_moyenne_en_voxels": round(mesuree, 4),
            "la_borne_optimiste_en_voxels": opt,
            "la_borne_realiste_en_voxels": rea,
            "le_rapport_a_la_borne_optimiste": (round(mesuree / float(opt), 4)
                                                if opt else None),
            "le_rapport_a_la_borne_realiste": (round(mesuree / float(rea), 4)
                                               if rea else None),
            "lerreur_dechantillonnage_en_voxels": round(erreur, 4),
            "lecart_a_la_borne_realiste_en_erreurs": (None if ecart is None
                                                      else round(float(ecart), 4)),
            "elle_saccorde_a_la_borne_realiste": (None if ecart is None
                                                  else bool(abs(float(ecart)) <= 3.0)),
            "elle_tombe_entre_les_deux_bornes": (
                bool(float(opt) <= mesuree <= float(rea)) if opt and rea else None),
            "la_projection_de_208_est_atteinte": (bool(mesuree <= float(opt))
                                                  if opt else None)}


def la_marche_du_plus_long_troncon(pas_par_rangee: dict, coutures, colonnes,
                                   rangee_seule: int) -> dict:
    """La marche moyennée et la marche d'UNE rangée NOMMÉE, sur LES MÊMES coutures.

    ⚠⚠⚠ LA RANGEE DU CONTROLE EST UN ARGUMENT, ET ELLE L'EST PARCE QU'UNE PREMIERE VERSION LA
    DEDUISAIT D'UN `sorted(...)[0]` — ce qui rend la plus PETITE clef, donc la voisine `197`, et
    non la mediane `198` que le document nommait. La marche de controle etait celle d'une voisine
    publiee sous le nom de la rangee seule : un nombre juste sous un mauvais nom, le peche capital
    de cette chaine. C'est le recoupement avec `207` qui l'a livre — ses cent cinq pas differaient
    tous, sur ce qui devait etre la meme rangee et le meme troncon.

    ⭐⭐⭐⭐ L'APPARIEMENT EST CE QUI REND LE GAIN MESURABLE : les deux marches partent du meme
    endroit, franchissent les memes coutures et s'arretent au meme endroit, donc leur rapport ne
    contient aucune correction de longueur. Comparer l'excursion moyennee a celle que `207` a
    publiee sur une AUTRE liste de coutures aurait melange le gain et la difference de longueur.

    ⚠⚠ ET LE TRONCON EST LE PLUS LONG SUITE DE COUTURES CONTIGUES, pas la liste entiere : deux
    coutures separees par un trou n'ont pas de chunk commun, donc accumuler de l'une a l'autre
    inventerait un pas que personne n'a lu. `les_troncons` est celle de `199`, importee.
    """
    cs = sorted(int(c) for c in coutures)
    if len(cs) < 2:
        return {"decidable": False, "raison": "moins de deux coutures communes"}
    troncons = les_troncons(set(cs), list(colonnes))
    if not troncons:
        return {"decidable": False, "raison": "aucune suite de deux coutures contiguës"}
    le_plus_long = max(troncons, key=len)
    mediane = int(rangee_seule)
    if mediane not in pas_par_rangee:
        return {"decidable": False,
                "raison": f"la rangée {mediane} n'est pas parmi celles qui sont moyennées"}
    moyennes = le_pas_moyenne(pas_par_rangee, le_plus_long)
    seuls = [float(pas_par_rangee[mediane][int(c)]) for c in le_plus_long]
    return {"decidable": True,
            "les_troncons": [[int(t[0]), int(t[-1]), len(t)] for t in troncons],
            "le_plus_long_troncon": [int(le_plus_long[0]), int(le_plus_long[-1]),
                                     len(le_plus_long)],
            "les_coutures_du_troncon": len(le_plus_long),
            "les_coutures_communes_en_tout": len(cs),
            "la_rangee_seule": int(mediane),
            "les_pas_moyennes_en_voxels": [round(float(x), 4) for x in moyennes],
            "les_pas_dune_rangee_seule_en_voxels": [round(float(x), 4) for x in seuls],
            "le_cumul_moyenne_en_voxels": [round(float(x), 4)
                                           for x in le_cumul(moyennes)],
            "le_cumul_dune_rangee_seule_en_voxels": [round(float(x), 4)
                                                     for x in le_cumul(seuls)],
            "lexcursion_moyennee": lexcursion(le_cumul(moyennes)),
            "lexcursion_dune_rangee_seule": lexcursion(le_cumul(seuls))}


def juger(marche: dict, retire: dict, epreuve: dict, prediction: dict,
          par_207: dict, demi: float = DEMI_PAS_EN_VOXELS) -> dict:
    """La marche moyennée traverse-t-elle, et de combien la moyenne a-t-elle aidé ?

    ⚠⚠ LA LONGUEUR EST PUBLIEE AVANT L'EXCURSION, exactement comme la porte l'exigeait : une marche
    qui traverse un troncon plus court n'a pas traverse davantage, et un verdict qui donnerait
    l'excursion seule laisserait croire le contraire.

    ⚠ Tout se lit par `.get()` et la presence est testee avant la valeur : une batterie qui meurt
    avant son verdict ne dit rien, et c'est une panne que cette chaine a payee cinq fois.
    """
    if not marche.get("decidable") or not epreuve.get("decidable"):
        return {"decidable": False, "raison": "la marche ou l'épreuve manque"}
    moy = marche.get("lexcursion_moyennee") or {}
    seule = marche.get("lexcursion_dune_rangee_seule") or {}
    if not moy.get("decidable") or not seule.get("decidable"):
        return {"decidable": False, "raison": "une des deux excursions est indécidable"}
    ec = float(moy["lexcursion_en_voxels"])
    es = float(seule["lexcursion_en_voxels"])
    att = (prediction or {}).get("lecart_attendu_en_voxels")
    n207 = (par_207 or {}).get("les_pas_du_cumul")
    return {"decidable": True,
            "les_coutures_du_troncon": marche.get("les_coutures_du_troncon"),
            "les_coutures_communes_en_tout": marche.get("les_coutures_communes_en_tout"),
            "les_coutures_de_207": n207,
            "les_coutures_de_toute_la_rangee_de_207": (par_207 or {}).get(
                "les_coutures_de_tous_les_troncons"),
            "le_rapport_des_longueurs_a_207": (
                round(float(marche["les_coutures_du_troncon"]) / float(n207), 4)
                if n207 else None),
            "lexcursion_moyennee_en_voxels": moy["lexcursion_en_voxels"],
            "lexcursion_moyennee_en_plis": moy["lexcursion_en_plis"],
            "lexcursion_moyennee_en_demi_plis": round(ec / float(demi), 4),
            "lexcursion_dune_rangee_seule_en_voxels": seule["lexcursion_en_voxels"],
            "le_gain_mesure_sur_lexcursion": (round(es / ec, 4) if ec > 0 else None),
            "le_demi_pli_en_voxels": int(demi),
            "elle_traverse_sous_le_demi_pli": bool(ec < float(demi)),
            "la_rangee_seule_traverse_sous_le_demi_pli": bool(es < float(demi)),
            "lecart_attendu_en_voxels": att,
            "le_rapport_observe_sur_attendu": (round(ec / float(att), 4) if att else None),
            "la_dispersion_du_pas_moyenne_en_voxels": (retire or {}).get(
                "la_dispersion_du_pas_moyenne_en_voxels"),
            "la_borne_optimiste_en_voxels": (retire or {}).get("la_borne_optimiste_en_voxels"),
            "la_borne_realiste_en_voxels": (retire or {}).get("la_borne_realiste_en_voxels"),
            "lerreur_dechantillonnage_en_voxels": (retire or {}).get(
                "lerreur_dechantillonnage_en_voxels"),
            "lecart_a_la_borne_realiste_en_erreurs": (retire or {}).get(
                "lecart_a_la_borne_realiste_en_erreurs"),
            "elle_saccorde_a_la_borne_realiste": (retire or {}).get(
                "elle_saccorde_a_la_borne_realiste"),
            "elle_tombe_entre_les_deux_bornes": (retire or {}).get(
                "elle_tombe_entre_les_deux_bornes"),
            "la_projection_de_208_est_atteinte": (retire or {}).get(
                "la_projection_de_208_est_atteinte"),
            "ca_saccumule": bool(epreuve.get("ca_saccumule")),
            "les_tirages_au_moins_aussi_loin": epreuve.get("les_tirages_au_moins_aussi_loin"),
            "combien_de_marches_au_hasard": epreuve.get("combien_de_marches_au_hasard"),
            "lexcursion_de_207_en_voxels": (par_207 or {}).get("lexcursion_en_voxels")}


def les_replicats_du_refus(garantie: float = GARANTIE_PAR_EPREUVE) -> dict:
    """Combien de réplicats la face négative exige pour DÉCIDER, et non seulement pour exister.

    ⚠⚠⚠ `202` A POSE LE PLANCHER — `int(2/garantie)` replicats, soit quarante, de sorte que deux
    faux soient ATTENDUS et que la face ne soit pas vide. Mais quarante ne DECIDENT pas : une
    epreuve au niveau EXACT de la garantie depasse l'acceptation dans une fraction que la loi
    binomiale donne exactement, et `210` est tombe dessus — six faux sur quarante alors que le
    niveau vrai mesure 0,06 sur quatre cents.

    ⚠⚠ LE COMPTE PUBLIE MET TROIS ERREURS D'ECHANTILLONNAGE DANS LA MARGE QUE LA REGLE LAISSE.
    L'erreur d'un taux `g` sur `m` tirages vaut la racine de `g(1-g)/m`, la marge vaut `g`, donc
    `m` vaut neuf fois `(1-g)/g`. Aucun reglage n'entre la-dedans : le nombre se derive de la
    garantie, exactement comme le plancher de `202` s'en derivait.
    """
    import math  # noqa: PLC0415
    g = float(garantie)
    plancher = int(2.0 / g)
    decisif = int(math.ceil(9.0 * (1.0 - g) / g))
    admis = int(math.floor(2.0 * g * plancher))
    rate = 1.0 - sum(math.comb(plancher, k) * (g ** k) * ((1.0 - g) ** (plancher - k))
                     for k in range(admis + 1))
    return {"decidable": True, "la_garantie": round(g, 7),
            "le_plancher_de_202": int(plancher),
            "les_faux_admis_au_plancher": int(admis),
            "la_chance_de_rater_au_plancher": round(float(rate), 4),
            "le_compte_decisif": int(decisif),
            "lerreur_au_compte_decisif": round(
                float((g * (1.0 - g) / decisif) ** 0.5), 4)}


def des_rangees_fabriquees(coutures: int, combien: int, derive: float, propre: float,
                           biais: float, graine: int) -> dict:
    """`combien` rangées dont le pas partage une dérive et garde un bruit propre.

    ⭐⭐⭐⭐ LE BIAIS EST DANS LA PART PARTAGEE, ET C'EST CE QUI REND LA FIXTURE JUSTE : un biais que
    seule une rangee porterait serait divise par trois en moyennant, donc la face positive
    mesurerait la moyenne et non l'epreuve. Une composante systematique de la SURFACE est vue par
    toutes les rangees, et c'est la seule chose que le tirage de signes peut voir.

    ⚠ La derive et le bruit poses sont les memes sur les deux faces : elles ne different que par la
    presence du biais.
    """
    r = _rng(int(graine))
    commune = float(biais) + r.normal(0.0, float(derive), size=int(coutures))
    out = {}
    for k in range(int(combien)):
        propre_k = r.normal(0.0, float(propre), size=int(coutures))
        out[int(k)] = {int(c): float(commune[c] + propre_k[c]) for c in range(int(coutures))}
    return out


def sur_letalon(coutures: int = 240, combien: int = 3, derive: float = 1.5129,
                propre: float = 1.9387, biais: float | None = None,
                graine: int = GRAINE, replicats: int = 12,
                tirages: int = PERMUTATIONS, lecteur=None) -> dict:
    """L'épreuve voit-elle un biais de surface À TRAVERS la moyenne, et se tait-elle sinon ?

    ⚠⚠⚠ L'ETALON EXERCE TOUTE LA CHAINE ET PAS SEULEMENT L'EPREUVE : il fabrique les rangees, prend
    leurs coutures communes, MOYENNE, puis tire les signes. Un etalon pose directement sur un pas
    moyenne ne dirait rien de la moyenne, et c'est elle qui est neuve dans cette tranche.

    ⚠⚠ LES DEUX FACES SUR REPLICATS, ET LA FACE NEGATIVE EN A DAVANTAGE — la lecon de `202`.
    ⚠⚠ LE BIAIS N'EST PAS CHOISI ICI : c'est celui que l'etalon de `199` a pose, relu chez son
    producteur par `207`. Reprendre l'epreuve de `199` sans reprendre sa matiere de calibration
    ferait dire a « l'etalon separe » deux choses differentes selon la tranche.
    """
    if biais is None:
        from peut_on_deplier_la_phase import \
            ce_que_la_marche_a_rendu  # noqa: PLC0415
        lu = (lecteur or ce_que_la_marche_a_rendu)()
        biais = (lu or {}).get("le_biais_de_letalon_en_voxels")
    if biais is None:
        return {"decidable": False, "raison": "`199` ne publie pas le biais de son étalon"}
    vus, nets, dispersions = 0, [], []
    for i in range(int(replicats)):
        rangees = des_rangees_fabriquees(coutures, combien, derive, propre, biais,
                                         int(graine) + 1000 * i)
        communes = les_coutures_communes_aux_rangees(rangees)
        moy = le_pas_moyenne(rangees, communes)
        ep = contre_les_signes(moy, tirages, int(graine) + i)
        vus += int(bool(ep.get("ca_saccumule")))
        if ep.get("decidable"):
            nets.append(float(ep["le_deplacement_net_en_voxels"]))
        dispersions.append(float(np.std(moy)))
    combien_de_refus = les_replicats_du_refus(GARANTIE_PAR_EPREUVE)
    replicats_du_refus = int(combien_de_refus["le_compte_decisif"])
    faux, sans = 0, []
    for i in range(replicats_du_refus):
        rangees = des_rangees_fabriquees(coutures, combien, derive, propre, 0.0,
                                         int(graine) + 500000 + 1000 * i)
        communes = les_coutures_communes_aux_rangees(rangees)
        moy = le_pas_moyenne(rangees, communes)
        ep = contre_les_signes(moy, tirages, int(graine) + 77 + i)
        faux += int(bool(ep.get("ca_saccumule")))
        if ep.get("decidable"):
            sans.append(float(ep["le_deplacement_net_en_voxels"]))
    return {"decidable": True,
            "les_coutures_par_replicat": int(coutures),
            "les_rangees_moyennees": int(combien),
            "la_derive_posee_en_voxels": float(derive),
            "le_bruit_propre_pose_en_voxels": float(propre),
            "le_biais_pose_en_voxels": float(biais),
            "replicats": int(replicats), "les_vus": int(vus),
            "la_part_trouvee": round(float(vus) / float(replicats), 4),
            "la_dispersion_mediane_du_pas_moyenne_en_voxels": (
                round(float(np.median(dispersions)), 4) if dispersions else None),
            "le_net_median_sur_la_face_positive_en_voxels": (
                round(float(np.median(nets)), 4) if nets else None),
            "les_replicats_du_refus": int(replicats_du_refus), "les_faux": int(faux),
            "le_plancher_de_202": combien_de_refus["le_plancher_de_202"],
            "la_chance_de_rater_au_plancher": combien_de_refus["la_chance_de_rater_au_plancher"],
            "le_taux_de_faux": round(float(faux) / float(replicats_du_refus), 4),
            "le_net_median_sur_la_face_negative_en_voxels": (
                round(float(np.median(sans)), 4) if sans else None),
            "la_garantie": round(float(GARANTIE_PAR_EPREUVE), 4),
            "letalon_separe": bool(vus >= replicats
                                   and faux / float(replicats_du_refus)
                                   <= float(GARANTIE_PAR_EPREUVE) * 2.0 + 1e-12)}


def mesurer(delai: float = DELAI, graine: int = GRAINE, replicats: int = 12,
            colonnes: int | None = None, ouvrir=None, meta=None,
            combien: int = LES_RANGEES) -> dict:
    """Les trois rangées lues, leurs pas moyennés couture par couture, la marche et son contrôle."""
    v = le_segment_declare()
    if v is None:
        return {"decidable": False, "raison": "aucun volume recensé"}
    if meta is None:
        try:
            meta = array_meta(f"{BUCKET}/{v['cle']}", 0, delai)
        except Exception as e:  # noqa: BLE001
            return {"decidable": False, "raison": f"le volume ne répond pas : {type(e).__name__}"}
    _, hy, hx = meta["chunks"]
    _, rows, cols = meta["shape"]
    gy, gx = -(-rows // hy), -(-cols // hx)
    echelle = les_rangees_du_treillis(gy)
    if not echelle.get("decidable"):
        return {"decidable": False, "raison": echelle.get("raison")}
    lignes, pas_par_rangee = {}, {}
    for r_ in echelle["les_rangees"]:
        lg = la_ligne(v, delai, colonnes, ouvrir, meta, combien, int(r_))
        if not lg.get("decidable"):
            return {"decidable": False,
                    "raison": f"la rangée {r_} est vide : {lg.get('raison')}"}
        pannes = les_pannes_de_reseau(lg.get("refuses"))
        if pannes:
            return {"decidable": False,
                    "raison": f"{pannes} chunks perdus par le réseau sur la rangée {r_} — une "
                              f"rangée dont le fil est tombé n'est pas comparable"}
        lignes[int(r_)] = {k: x for k, x in lg.items()
                           if k not in ("droits", "gauches", "les_colonnes")}
        pas_par_rangee[int(r_)] = les_pas_dune_rangee(lg["droits"], lg["gauches"],
                                                      lg["les_rangees_lues"])
    les_colonnes = list(range(gx if colonnes is None else min(int(colonnes), gx)))
    communes = les_coutures_communes_aux_rangees(pas_par_rangee)
    par_208 = ce_que_la_voisine_a_rendu()
    par_207 = ce_que_le_cumul_a_rendu()
    par_204 = la_dispersion_de_204()
    predite = la_dispersion_predite(par_208.get("la_derive_partagee_en_voxels"),
                                    par_208.get("le_bruit_de_la_mediane_en_voxels"),
                                    len(pas_par_rangee))
    retire = ce_que_la_moyenne_a_retire(pas_par_rangee, communes, predite)
    marche = la_marche_du_plus_long_troncon(pas_par_rangee, communes, les_colonnes,
                                            int(echelle["la_mediane"]))
    pas_moyennes = marche.get("les_pas_moyennes_en_voxels") or []
    epreuve = contre_les_signes(pas_moyennes, PERMUTATIONS, graine)
    n = marche.get("les_coutures_du_troncon") or 0
    prediction = lexcursion_predite(
        retire.get("la_dispersion_du_pas_moyenne_en_voxels"), int(n)) if n else {
        "decidable": False, "raison": "aucun tronçon"}
    # ⭐⭐⭐⭐ LES TROIS PREDICTIONS A LA MEME LONGUEUR, PARCE QU'UNE SEULE NE DIRAIT RIEN. La borne
    # optimiste est ce que `208` projetait, la realiste ce que trois lectures peuvent retirer, et
    # celle d'une rangee seule ce que `207` a mesure ; les publier a la longueur du TRONCON COMMUN
    # les rend comparables entre elles, ce qu'elles ne sont pas a des longueurs differentes.
    a_la_meme_longueur = {
        "loptimiste_de_208": lexcursion_predite(
            predite.get("la_borne_optimiste_en_voxels"), int(n)) if n else None,
        "la_realiste_a_trois_lectures": lexcursion_predite(
            predite.get("la_borne_realiste_en_voxels"), int(n)) if n else None,
        "une_rangee_seule": lexcursion_predite(
            par_204.get("la_dispersion_en_voxels"), int(n)) if n else None,
        "le_plancher_de_la_matiere": lexcursion_predite(
            par_204.get("la_derive_en_voxels"), int(n)) if n else None}
    # ⚠⚠⚠ ET LA MEME PREDICTION A TOUTES LES COUTURES COMMUNES, PARCE QUE LE TRONCON N'EST PAS
    # LA RANGEE. C'est la discipline que `207` a posee et la raison qu'il en donne : publier la
    # seule prediction du troncon laisserait croire que le verdict porte sur la rangee entiere —
    # un nombre juste sous un mauvais nom. Les trois lignes se comparent au demi-feuillet, qui
    # n'est pas un seuil choisi mais la distance a laquelle la surface saute au feuillet voisin.
    a_toutes_les_coutures = {
        "la_moyenne_mesuree": lexcursion_predite(
            retire.get("la_dispersion_du_pas_moyenne_en_voxels"), len(communes)),
        "une_rangee_seule": lexcursion_predite(
            par_204.get("la_dispersion_en_voxels"), len(communes)),
        "le_plancher_de_la_matiere": lexcursion_predite(
            par_204.get("la_derive_en_voxels"), len(communes))} if communes else {}
    return {
        "graine": int(graine), "tirages": int(PERMUTATIONS),
        "la_question_declaree": LA_QUESTION_DECLAREE,
        "les_epreuves_declarees": list(LES_EPREUVES_DECLAREES),
        "la_garantie_par_epreuve": round(float(GARANTIE_PAR_EPREUVE), 7),
        "le_pas_dun_pli_en_voxels": round(float(PAS_EN_VOXELS), 4),
        "le_demi_pli_en_voxels": int(DEMI_PAS_EN_VOXELS),
        "les_rangees_du_treillis": echelle,
        "ce_que_208_a_rendu": par_208,
        "ce_que_207_a_rendu": par_207,
        "ce_que_204_a_rendu": par_204,
        "la_dispersion_predite": predite,
        "les_lignes": lignes,
        "les_pas_par_rangee": {str(k): len(x) for k, x in pas_par_rangee.items()},
        "les_coutures_communes": len(communes),
        "ce_que_la_moyenne_a_retire": retire,
        "la_marche": marche,
        "lepreuve": epreuve,
        "la_prediction": prediction,
        "les_predictions_a_la_meme_longueur": a_la_meme_longueur,
        "les_predictions_a_toutes_les_coutures": a_toutes_les_coutures,
        "le_verdict": juger(marche, retire, epreuve, prediction, par_207),
        "letalon": sur_letalon(
            max(3, int(n)), len(pas_par_rangee),
            par_208.get("la_derive_partagee_en_voxels") or 1.5129,
            par_208.get("le_bruit_de_la_mediane_en_voxels") or 1.9387,
            None, graine, replicats),
    }


def afficher(r: dict) -> None:
    if not r.get("decidable", True) and "raison" in r:
        print(f"INDÉCIDABLE : {r['raison']}")
        return
    ec = r.get("les_rangees_du_treillis") or {}
    lignes = r.get("les_lignes") or {}
    une = lignes.get(ec.get("la_mediane")) or next(iter(lignes.values()), {})
    print(f"LA MOYENNE DES RANGÉES TRAVERSE-T-ELLE   segment {une.get('segment')} · "
          f"rangées {ec.get('les_rangees')} · {une.get('colonnes_demandees')} colonnes "
          f"demandées · {len(une.get('les_rangees_lues') or [])} rangées de coupe")
    print("  LES PAS PAR RANGÉE " + " · ".join(
        f"{k}→{x}" for k, x in (r.get("les_pas_par_rangee") or {}).items())
        + f" · communes {r.get('les_coutures_communes')}")
    p = r.get("la_dispersion_predite") or {}
    if p.get("decidable"):
        print(f"  LA PRÉDICTION     une rangée porte "
              f"{p['ce_quune_rangee_seule_porte_en_voxels']} · optimiste "
              f"{p['la_borne_optimiste_en_voxels']} · réaliste à "
              f"{p['les_rangees_moyennees']} lectures {p['la_borne_realiste_en_voxels']}")
    q = r.get("ce_que_la_moyenne_a_retire") or {}
    if q.get("decidable"):
        print(f"  CE QU'ELLE RETIRE dispersion mesurée du pas moyenné "
              f"{q['la_dispersion_du_pas_moyenne_en_voxels']} sur {q['les_coutures']} "
              f"coutures · rangée médiane "
              f"{q['la_dispersion_mediane_dune_rangee_en_voxels']}")
        print(f"                    rapport à l'optimiste "
              f"{q['le_rapport_a_la_borne_optimiste']} · à la réaliste "
              f"{q['le_rapport_a_la_borne_realiste']} · entre les deux "
              f"{q['elle_tombe_entre_les_deux_bornes']}")
    m = r.get("la_marche") or {}
    if m.get("decidable"):
        print(f"  LE TRONÇON        {len(m.get('les_troncons') or [])} tronçons · le plus long "
              f"{m['le_plus_long_troncon']} · {m['les_coutures_du_troncon']} coutures sur "
              f"{m['les_coutures_communes_en_tout']} communes")
        mo = m.get("lexcursion_moyennee") or {}
        se = m.get("lexcursion_dune_rangee_seule") or {}
        print(f"  L'EXCURSION       moyennée {mo.get('lexcursion_en_voxels')} voxels = "
              f"{mo.get('lexcursion_en_plis')} pli · rangée seule "
              f"{se.get('lexcursion_en_voxels')} voxels")
    a = r.get("les_predictions_a_la_meme_longueur") or {}
    for nom, x in a.items():
        if isinstance(x, dict) and x.get("decidable"):
            print(f"  À {nom:<28} {x['la_dispersion_de_204_en_voxels']} × racine de "
                  f"{x['les_coutures']} = {x['lecart_attendu_en_voxels']} voxels · sous le "
                  f"demi-pli {x['il_tient_sous_le_demi_pli']}")
    ep = r.get("lepreuve") or {}
    if ep.get("decidable"):
        print(f"  L'ÉPREUVE         déplacement net {ep['le_deplacement_net_en_voxels']} contre "
              f"{ep['le_deplacement_du_nul_median_en_voxels']} au nul · "
              f"{ep['les_tirages_au_moins_aussi_loin']}/{ep['tirages']} · "
              f"{ep['combien_de_marches_au_hasard']} marche au hasard · ça s'accumule "
              f"{ep['ca_saccumule']}")
    ve = r.get("le_verdict") or {}
    if ve.get("decidable"):
        print(f"  LE VERDICT        {ve['les_coutures_du_troncon']} coutures contre "
              f"{ve['les_coutures_de_207']} à `207` (rapport "
              f"{ve['le_rapport_des_longueurs_a_207']}) · excursion "
              f"{ve['lexcursion_moyennee_en_voxels']} voxels = "
              f"{ve['lexcursion_moyennee_en_demi_plis']} demi-pli")
        print(f"                    traverse {ve['elle_traverse_sous_le_demi_pli']} · la rangée "
              f"seule sur les MÊMES coutures {ve['lexcursion_dune_rangee_seule_en_voxels']} "
              f"(gain {ve['le_gain_mesure_sur_lexcursion']}) · `207` en donnait "
              f"{ve['lexcursion_de_207_en_voxels']}")
        print(f"                    la projection de `208` est atteinte "
              f"{ve['la_projection_de_208_est_atteinte']} · entre les deux bornes "
              f"{ve['elle_tombe_entre_les_deux_bornes']}")
    et = r.get("letalon") or {}
    if et.get("decidable"):
        print(f"  L'ÉTALON          sépare {et['letalon_separe']} · trouve "
              f"{et['la_part_trouvee']} des {et['replicats']} réplicats (net "
              f"{et['le_net_median_sur_la_face_positive_en_voxels']}) · {et['les_faux']} "
              f"faux sur {et['les_replicats_du_refus']} = {et['le_taux_de_faux']} pour "
              f"{et['la_garantie']} garantis")


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

    # ⚠⚠⚠ L'INTERSECTION, JAMAIS L'UNION : une couture qu'une rangee n'a pas lue n'est pas
    # moyennable. Un bris qui prend l'union rend une liste PLUS LONGUE, donc une sonde qui ne
    # verifierait que « il y a des coutures » resterait verte.
    trois = {198: {0: 1.0, 1: 2.0, 2: 3.0, 5: 9.0},
             197: {0: 2.0, 1: 4.0, 2: 6.0, 7: 9.0},
             199: {0: 3.0, 2: 9.0, 3: 1.0}}
    comm = les_coutures_communes_aux_rangees(trois)
    v("★★★★ les coutures communes sont l'INTERSECTION des trois rangées",
      comm == [0, 2], str(comm))
    v("★★★ trois rangées sans aucune colonne partagée ne rendent aucune couture",
      les_coutures_communes_aux_rangees({1: {0: 1.0}, 2: {5: 1.0}}) == [])
    v("★★★ aucune rangée ne rend aucune couture",
      les_coutures_communes_aux_rangees({}) == [])

    # ⚠⚠⚠ LE PAS MOYENNE EST INDEXE PAR COLONNE : un bris qui moyennerait par RANG prendrait, a
    # la couture 2, la DEUXIEME valeur de chaque liste — soit 2,0 / 4,0 / 9,0 au lieu de
    # 3,0 / 6,0 / 9,0. La fixture est batie pour que les deux lectures DIFFERENT.
    moy = le_pas_moyenne(trois, [0, 2])
    v("★★★★ le pas moyenné est la moyenne des rangées À LA MÊME COLONNE",
      abs(moy[0] - 2.0) < 1e-12 and abs(moy[1] - 6.0) < 1e-12, str(moy))
    par_rang = [float(np.mean([list(p.values())[i] for p in trois.values()]))
                for i in range(2)]
    v("★★★★ moyenner par RANG donnerait autre chose, et la sonde le montre",
      abs(par_rang[1] - moy[1]) > 1e-9, f"{par_rang} contre {moy}")
    v("★★★ une seule rangée moyennée rend cette rangée telle quelle",
      abs(le_pas_moyenne({198: trois[198]}, [1])[0] - 2.0) < 1e-12)

    # ⭐⭐⭐⭐ LES DEUX BORNES, ET C'EST TOUTE LA TRANCHE.
    pr = la_dispersion_predite(1.5129, 1.9387, 3)
    attendu = float(np.sqrt(1.5129 ** 2 + (1.9387 ** 2) / 3.0))
    v("★★★★ la borne optimiste est la dérive partagée SEULE — la projection de `208`",
      pr["decidable"] and abs(pr["la_borne_optimiste_en_voxels"] - 1.5129) < 1e-9)
    v("★★★★ la borne réaliste divise le carré du bruit propre par le nombre de LECTURES",
      abs(pr["la_borne_realiste_en_voxels"] - round(attendu, 4)) < 1e-9,
      f"{pr.get('la_borne_realiste_en_voxels')} contre {round(attendu, 4)}")
    v("★★★★ la réaliste est STRICTEMENT au-dessus de l'optimiste dès qu'un bruit propre existe",
      pr["la_borne_realiste_en_voxels"] > pr["la_borne_optimiste_en_voxels"])
    v("★★★★ à UNE seule lecture, la réaliste vaut ce qu'une rangée seule porte",
      abs(la_dispersion_predite(1.5129, 1.9387, 1)["la_borne_realiste_en_voxels"]
          - pr["ce_quune_rangee_seule_porte_en_voxels"]) < 1e-9)
    v("★★★ moyenner davantage de rangées resserre la borne réaliste",
      la_dispersion_predite(1.5129, 1.9387, 9)["la_borne_realiste_en_voxels"]
      < pr["la_borne_realiste_en_voxels"])
    v("★★★ sans bruit propre, les deux bornes se confondent",
      abs(la_dispersion_predite(1.5129, 0.0, 3)["la_borne_realiste_en_voxels"]
          - 1.5129) < 1e-9)
    v("★★★ une dérive partagée absente ne rend AUCUNE prédiction",
      not la_dispersion_predite(None, 1.9387, 3)["decidable"])
    v("★★★ un bruit propre absent ne rend AUCUNE prédiction",
      not la_dispersion_predite(1.5129, None, 3)["decidable"])
    v("★★★ zéro rangée moyennée ne rend AUCUNE prédiction",
      not la_dispersion_predite(1.5129, 1.9387, 0)["decidable"])

    # ⭐⭐⭐⭐ LA MESURE TOMBE ENTRE LES DEUX BORNES SUR UNE MATIERE BATIE EXACTEMENT AINSI, et
    # l'encadrement est STRUCTUREL : un bris qui rendrait une seule rangee au lieu de la moyenne
    # sortirait AU-DESSUS de la realiste, un bris qui retirerait tout le bruit sortirait SOUS
    # l'optimiste. Asserter « il y a une dispersion » aurait ete satisfait par les deux.
    fab = des_rangees_fabriquees(4000, 3, 1.5129, 1.9387, 0.0, 4242)
    cf = les_coutures_communes_aux_rangees(fab)
    qr = ce_que_la_moyenne_a_retire(fab, cf, pr)
    mes = float(qr["la_dispersion_du_pas_moyenne_en_voxels"])
    # ⚠⚠⚠ LA TOLERANCE EST DERIVEE, JAMAIS CHOISIE : l'ecart-type d'un ecart-type estime sur `n`
    # tirages vaut lui-meme divise par la racine de deux fois `n`. Ma premiere sonde exigeait une
    # inegalite STRICTE contre la borne realiste — 1,8841 contre 1,8819, soit un dixieme de cette
    # erreur-la — donc elle ne passait que par chance et aurait rougi au prochain grain.
    erreur = float(qr["la_borne_realiste_en_voxels"]) / float(np.sqrt(2.0 * qr["les_coutures"]))
    v("★★★★ la dispersion mesurée s'accorde à la borne RÉALISTE à trois erreurs près",
      qr["decidable"]
      and abs(mes - float(qr["la_borne_realiste_en_voxels"])) < 3.0 * erreur,
      f"{mes} contre {qr.get('la_borne_realiste_en_voxels')} ± {round(erreur, 4)}")
    v("★★★★ et elle est très AU-DESSUS de la borne optimiste — la projection de `208` NE tient pas",
      mes - float(qr["la_borne_optimiste_en_voxels"]) > 3.0 * erreur,
      f"{mes} contre {qr.get('la_borne_optimiste_en_voxels')} ± {round(erreur, 4)}")
    v("★★★★ et très SOUS ce qu'une rangée seule porte — moyenner retire bel et bien quelque chose",
      float(qr["la_dispersion_mediane_dune_rangee_en_voxels"]) - mes > 3.0 * erreur,
      f"{mes} contre {qr.get('la_dispersion_mediane_dune_rangee_en_voxels')}")
    v("★★★ la dispersion de CHAQUE rangée est publiée à côté",
      len(qr["la_dispersion_de_chaque_rangee_en_voxels"]) == 3)
    # ⚠⚠ LA SONDE PORTE SUR UNE IDENTITE ENTRE DEUX NOMBRES PUBLIES, jamais sur une seconde
    # ecriture de la formule : recopier le calcul du producteur en ferait une SECONDE DEFINITION,
    # libre de deriver avec lui. L'erreur d'un ecart-type vaut cet ecart-type divise par la racine
    # de DEUX fois le compte, donc le produit des deux doit rendre la dispersion. Un bris qui
    # oublie le facteur deux laisse le rapport a racine de deux.
    # ⚠⚠ LA TOLERANCE VIENT DE L'ARRONDI PUBLIE, ET DE NULLE PART AILLEURS : le producteur rend
    # quatre decimales, donc chaque nombre porte jusqu'a un demi dix-millieme, et multiplier par
    # la racine de deux mille coutures propage cet arrondi. Ma premiere version exigeait un
    # milliemé et a rougi sur du code juste — pour la bonne raison, mais pas la bonne sonde.
    arrondi = 5e-5
    v("★★★★ l'erreur d'échantillonnage porte bien le facteur DEUX du compte de coutures",
      abs(float(qr["lerreur_dechantillonnage_en_voxels"])
          * float(np.sqrt(2.0 * qr["les_coutures"]))
          - float(qr["la_dispersion_du_pas_moyenne_en_voxels"]))
      < arrondi * float(np.sqrt(2.0 * qr["les_coutures"])) + arrondi,
      f"{qr.get('lerreur_dechantillonnage_en_voxels')} × racine de 2×"
      f"{qr.get('les_coutures')} pour {qr.get('la_dispersion_du_pas_moyenne_en_voxels')}")
    v("★★★★ l'écart à la borne réaliste est compté EN ERREURS, pas en voxels",
      abs(float(qr["lecart_a_la_borne_realiste_en_erreurs"])
          * float(qr["lerreur_dechantillonnage_en_voxels"])
          - (float(qr["la_dispersion_du_pas_moyenne_en_voxels"])
             - float(qr["la_borne_realiste_en_voxels"])))
      < arrondi * (2.0 + abs(float(qr["lecart_a_la_borne_realiste_en_erreurs"]))))
    v("★★★ et l'accord à trois erreurs près est publié comme tel",
      qr["elle_saccorde_a_la_borne_realiste"]
      is bool(abs(float(qr["lecart_a_la_borne_realiste_en_erreurs"])) <= 3.0))
    v("★★★ moins de trois coutures communes ne rendent AUCUNE mesure",
      not ce_que_la_moyenne_a_retire(trois, [0], pr)["decidable"])

    # ⚠⚠ LE TRONCON EST CELUI DE `199`, IMPORTE : un trou coupe la marche, il ne se recolle pas.
    pas4 = {198: {}, 197: {}, 199: {}}
    for r_ in pas4:
        for c in (0, 1, 2, 3, 7, 8):
            pas4[r_][c] = float(c) + (0.1 * r_)
    ma = la_marche_du_plus_long_troncon(pas4, les_coutures_communes_aux_rangees(pas4),
                                        list(range(12)), 198)
    # ⚠⚠⚠ LA RANGEE DU CONTROLE EST CELLE QU'ON NOMME, ET LA FIXTURE EST BATIE POUR QUE LE TRI
    # DONNE UNE AUTRE REPONSE : les trois rangees portent des valeurs DIFFERENTES, et la mediane
    # declaree `198` n'est pas la plus petite clef. Une premiere version prenait `sorted(...)[0]`,
    # donc la voisine `197`, et publiait sa marche sous le nom de la rangee seule — c'est le
    # recoupement avec `207` qui l'a dit, pas une relecture.
    nommees = {198: {c: float(c) for c in range(6)},
               197: {c: -float(c) for c in range(6)},
               199: {c: 10.0 * float(c) for c in range(6)}}
    for demandee, attendu in ((198, [0.0, 1.0, 2.0]), (197, [0.0, -1.0, -2.0]),
                              (199, [0.0, 10.0, 20.0])):
        mn = la_marche_du_plus_long_troncon(
            nommees, les_coutures_communes_aux_rangees(nommees), list(range(8)), demandee)
        v(f"★★★★ le contrôle marche bien sur la rangée {demandee} qu'on lui NOMME",
          mn["decidable"] and mn["la_rangee_seule"] == demandee
          and mn["les_pas_dune_rangee_seule_en_voxels"][:3] == attendu,
          f"{mn.get('la_rangee_seule')} · {mn.get('les_pas_dune_rangee_seule_en_voxels')[:3]}")
    v("★★★ une rangée de contrôle absente des moyennées est REFUSÉE",
      not la_marche_du_plus_long_troncon(
          nommees, les_coutures_communes_aux_rangees(nommees), list(range(8)), 42)["decidable"])
    v("★★★★ un trou dans les coutures communes coupe la marche en deux tronçons",
      ma["decidable"] and len(ma["les_troncons"]) == 2, str(ma.get("les_troncons")))
    v("★★★★ la marche porte le PLUS LONG tronçon, pas la liste entière",
      ma["les_coutures_du_troncon"] == 4
      and ma["les_coutures_communes_en_tout"] == 6,
      f"{ma.get('les_coutures_du_troncon')} sur {ma.get('les_coutures_communes_en_tout')}")
    v("★★★★ les deux marches ont EXACTEMENT le même nombre de pas — le contrôle est apparié",
      len(ma["les_pas_moyennes_en_voxels"]) == len(ma["les_pas_dune_rangee_seule_en_voxels"]),
      f"{len(ma['les_pas_moyennes_en_voxels'])} contre "
      f"{len(ma['les_pas_dune_rangee_seule_en_voxels'])}")
    v("★★★ la marche publie sa trace, pas seulement son amplitude",
      len(ma["le_cumul_moyenne_en_voxels"]) == ma["les_coutures_du_troncon"] + 1)
    v("★★★ moins de deux coutures communes ne rendent AUCUNE marche",
      not la_marche_du_plus_long_troncon(pas4, [3], list(range(12)), 198)["decidable"])
    v("★★★ des coutures communes toutes isolées ne rendent AUCUNE marche",
      not la_marche_du_plus_long_troncon(pas4, [0, 2, 7], list(range(12)), 198)["decidable"])

    # ⚠⚠⚠ L'ORDRE DES PAS EST CELUI DES COLONNES : un bris qui trierait les pas rendrait la MEME
    # dispersion et une AUTRE excursion, donc la sonde porte sur l'excursion.
    croissants = [1.0, 1.0, 1.0, -1.0, -1.0, -1.0]
    alternes = [1.0, -1.0, 1.0, -1.0, 1.0, -1.0]
    v("★★★★ l'excursion dépend de l'ORDRE des pas, pas seulement de leurs tailles",
      abs(lexcursion(le_cumul(croissants))["lexcursion_en_voxels"]
          - lexcursion(le_cumul(alternes))["lexcursion_en_voxels"]) > 1e-9)
    # ⚠⚠⚠ ET LA SONDE TRAVERSE LE CHEMIN QUE LE VERDICT SUIT, SUR UNE MATIERE QUI ZIGZAGUE. Une
    # premiere version comparait deux listes ecrites a la main sans jamais passer par la marche,
    # et la fixture `pas4` a des pas MONOTONES — donc les trier ne changeait rien. Le bris « les
    # pas sont tries » restait vert des deux cotes.
    valeurs = [3.0, -5.0, 8.0, -2.0, 6.0]
    zig = {r_: {c: x for c, x in enumerate(valeurs)} for r_ in (198, 197, 199)}
    mz = la_marche_du_plus_long_troncon(zig, les_coutures_communes_aux_rangees(zig),
                                        list(range(8)), 198)
    v("★★★★ la marche publie ses pas DANS L'ORDRE DES COLONNES, jamais triés",
      mz["decidable"] and mz["les_pas_moyennes_en_voxels"] == valeurs,
      str(mz.get("les_pas_moyennes_en_voxels")))
    v("★★★★ et son excursion diffère de celle des MÊMES pas triés",
      abs(float(mz["lexcursion_moyennee"]["lexcursion_en_voxels"])
          - float(lexcursion(le_cumul(sorted(valeurs)))["lexcursion_en_voxels"])) > 1e-9,
      f"{mz['lexcursion_moyennee']['lexcursion_en_voxels']} contre "
      f"{lexcursion(le_cumul(sorted(valeurs)))['lexcursion_en_voxels']}")

    # ⭐ LE VERDICT, ET IL SURVIT A CE QUI MANQUE.
    ep_ = contre_les_signes(ma["les_pas_moyennes_en_voxels"], PERMUTATIONS, GRAINE)
    ve = juger(ma, qr, ep_, lexcursion_predite(1.0, 4), {"les_pas_du_cumul": 105,
                                                         "lexcursion_en_voxels": 28.0625})
    v("★★★★ le verdict publie la LONGUEUR du tronçon à côté de l'excursion",
      ve["decidable"] and ve["les_coutures_du_troncon"] == 4
      and ve["lexcursion_moyennee_en_voxels"] is not None)
    v("★★★★ il publie le rapport des longueurs à `207`, sinon une marche plus courte "
      "passerait pour meilleure",
      abs(ve["le_rapport_des_longueurs_a_207"] - round(4.0 / 105.0, 4)) < 1e-9,
      str(ve.get("le_rapport_des_longueurs_a_207")))
    v("★★★★ il publie l'excursion de la rangée SEULE sur les mêmes coutures",
      ve["lexcursion_dune_rangee_seule_en_voxels"] is not None
      and ve["le_gain_mesure_sur_lexcursion"] is not None)
    v("★★★ une marche indécidable ne rend AUCUN verdict",
      not juger({"decidable": False}, qr, ep_, {}, {})["decidable"])
    v("★★★ une épreuve indécidable ne rend AUCUN verdict",
      not juger(ma, qr, {"decidable": False}, {}, {})["decidable"])
    try:
        sans_207 = juger(ma, qr, ep_, {}, {})
        ok_207 = (sans_207.get("decidable") is True
                  and sans_207.get("les_coutures_de_207") is None)
        detail_207 = str(sans_207.get("les_coutures_de_207"))
    except Exception as exc_:  # noqa: BLE001
        ok_207, detail_207 = False, f"{type(exc_).__name__}"
    v("★★★★ un verdict privé de ce que `207` a publié ne MEURT pas, il le dit",
      ok_207, detail_207)
    try:
        sans_retire = juger(ma, None, ep_, {}, {})
        ok_retire = sans_retire.get("decidable") is True
        detail_retire = ""
    except Exception as exc_:  # noqa: BLE001
        ok_retire, detail_retire = False, f"{type(exc_).__name__}"
    v("★★★★ un verdict privé de ce que la moyenne a retiré ne MEURT pas non plus",
      ok_retire, detail_retire)

    # ⚠⚠ LES LECTEURS DES PRODUCTEURS REFUSENT PLUTOT QUE DE DEVINER.
    v("★★★ sans la mesure de `208`, le lecteur se refuse",
      not ce_que_la_voisine_a_rendu(Path("/absent.json"))["decidable"])
    v("★★★ sans la mesure de `207`, le lecteur se refuse",
      not ce_que_le_cumul_a_rendu(Path("/absent.json"))["decidable"])
    lu208 = ce_que_la_voisine_a_rendu()
    if lu208.get("decidable"):
        v("★★★★ la dérive partagée est LUE chez `208`, jamais retapée ici",
          lu208["la_derive_partagee_en_voxels"] is not None
          and lu208["le_bruit_de_la_mediane_en_voxels"] is not None)

    # ⭐⭐⭐⭐ L'ETALON EXERCE TOUTE LA CHAINE : fabriquer, moyenner, tirer les signes.
    et = sur_letalon(240, 3, 1.5129, 1.9387, None, GRAINE, replicats=3,
                     tirages=PERMUTATIONS)
    v("★★★★ l'étalon voit un biais de surface À TRAVERS la moyenne",
      et["la_part_trouvee"] >= 0.99, str(et.get("la_part_trouvee")))
    # ⚠⚠⚠ LE COMPTE DE LA FACE NEGATIVE EST DERIVE, ET IL DEPASSE LE PLANCHER DE `202`. Ce
    # plancher fait qu'elle EXISTE ; il ne la fait pas DECIDER — `210` a rendu six faux sur
    # quarante pour un niveau vrai mesure a 0,06, et la loi binomiale dit exactement a quelle
    # frequence ca arrive. La sonde asserte le calcul, pas le chiffre qui en sort.
    rf = les_replicats_du_refus(GARANTIE_PAR_EPREUVE)
    v("★★★ le plancher de `202` est celui qu'il a toujours été, et il est publié",
      rf["le_plancher_de_202"] == int(2.0 / GARANTIE_PAR_EPREUVE))
    v("★★★★ le compte décisif met TROIS erreurs d'échantillonnage dans la marge",
      abs(rf["lerreur_au_compte_decisif"]
          - round((GARANTIE_PAR_EPREUVE / 3.0), 4)) < 5e-4,
      f"{rf.get('lerreur_au_compte_decisif')} pour {round(GARANTIE_PAR_EPREUVE / 3.0, 4)}")
    v("★★★★ et il est STRICTEMENT au-dessus du plancher de `202`",
      rf["le_compte_decisif"] > rf["le_plancher_de_202"],
      f"{rf.get('le_compte_decisif')} contre {rf.get('le_plancher_de_202')}")
    v("★★★★ la chance de rater AU PLANCHER est calculée exactement, et elle n'est pas nulle",
      0.0 < rf["la_chance_de_rater_au_plancher"] < 0.5,
      str(rf.get("la_chance_de_rater_au_plancher")))
    # ⚠⚠⚠ LES FAUX ADMIS SONT LE PLUS GRAND COMPTE QUE L'ACCEPTATION TOLERE, et c'est une
    # identite entre deux nombres publies : le compte admis tient sous deux fois la garantie, le
    # suivant n'y tient pas. Une sonde qui se contentait de « la chance est entre zero et un demi »
    # restait verte pour un seuil deux fois trop large.
    admis, plancher = rf["les_faux_admis_au_plancher"], rf["le_plancher_de_202"]
    v("★★★★ les faux admis au plancher sont le PLUS GRAND compte sous deux fois la garantie",
      admis / float(plancher) <= 2.0 * GARANTIE_PAR_EPREUVE + 1e-12
      and (admis + 1) / float(plancher) > 2.0 * GARANTIE_PAR_EPREUVE,
      f"{admis} sur {plancher} pour {2.0 * GARANTIE_PAR_EPREUVE}")
    v("★★★★ et la chance de rater y est PLUS GRANDE qu'au compte décisif",
      rf["la_chance_de_rater_au_plancher"]
      > les_replicats_du_refus(GARANTIE_PAR_EPREUVE * 2.0)["la_chance_de_rater_au_plancher"],
      str(rf.get("la_chance_de_rater_au_plancher")))
    v("★★★ une garantie plus serrée exige davantage de réplicats",
      les_replicats_du_refus(0.01)["le_compte_decisif"] > rf["le_compte_decisif"])
    v("★★★★ l'étalon utilise le compte DÉCISIF, jamais le plancher",
      et["les_replicats_du_refus"] == rf["le_compte_decisif"]
      and et["le_plancher_de_202"] == rf["le_plancher_de_202"],
      f"{et.get('les_replicats_du_refus')} pour {rf.get('le_compte_decisif')}")
    v("★★★★ sans biais, le taux de faux tient la garantie",
      et["le_taux_de_faux"] <= GARANTIE_PAR_EPREUVE * 2.0 + 1e-12,
      f"{et.get('les_faux')} faux sur {et.get('les_replicats_du_refus')}")
    v("★★★ l'étalon sépare ses deux faces, et il le DIT", et["letalon_separe"] is True)
    v("★★★★ le déplacement net est publié sur les DEUX faces, et la biaisée va PLUS LOIN",
      et["le_net_median_sur_la_face_positive_en_voxels"]
      > et["le_net_median_sur_la_face_negative_en_voxels"],
      f"{et.get('le_net_median_sur_la_face_positive_en_voxels')} contre "
      f"{et.get('le_net_median_sur_la_face_negative_en_voxels')}")
    # ⚠⚠⚠ LE BIAIS N'EST PAS PASSE ICI, ET C'EST TOUT L'INTERET : une premiere version le donnait
    # explicitement a `None` en cinquieme position, donc le DEFAUT du parametre n'etait exerce par
    # rien et un bris qui y ecrivait « 2.0 » restait vert. C'est le defaut de `208`, un cran plus
    # bas dans la meme fonction.
    v("★★★★ le biais N'EST PAS choisi ici : privé du lecteur de `199`, l'étalon se REFUSE",
      not sur_letalon(24, replicats=1, tirages=3,
                      lecteur=lambda: {"decidable": False})["decidable"])
    # ⚠⚠ L'ETALON EST APPELE SANS ARGUMENT ICI, SINON SES DEFAUTS NE SONT EXERCES PAR RIEN : le
    # defaut de `208` etait ce bris-la, et il est reste vert tant que chaque sonde passait tout.
    par_defaut = sur_letalon(24, replicats=1, tirages=3)
    v("★★★★ la dérive et le bruit PAR DÉFAUT de l'étalon sont ceux que `208` a publiés",
      par_defaut["la_derive_posee_en_voxels"]
      == lu208.get("la_derive_partagee_en_voxels")
      and par_defaut["le_bruit_propre_pose_en_voxels"]
      == lu208.get("le_bruit_de_la_mediane_en_voxels"),
      f"{par_defaut.get('la_derive_posee_en_voxels')} · "
      f"{par_defaut.get('le_bruit_propre_pose_en_voxels')}")
    v("★★★★ l'étalon moyenne bien TROIS rangées par défaut",
      par_defaut["les_rangees_moyennees"] == 3)

    # ⚠⚠ LA FIXTURE MET LE BIAIS DANS LA PART PARTAGEE : un biais propre a une rangee serait
    # divise par trois en moyennant, donc la face positive mesurerait la moyenne et non l'epreuve.
    avec = des_rangees_fabriquees(2000, 3, 1.0, 2.0, 5.0, 77)
    sans = des_rangees_fabriquees(2000, 3, 1.0, 2.0, 0.0, 77)
    m_avec = float(np.mean(le_pas_moyenne(avec, les_coutures_communes_aux_rangees(avec))))
    m_sans = float(np.mean(le_pas_moyenne(sans, les_coutures_communes_aux_rangees(sans))))
    v("★★★★ le biais posé SURVIT à la moyenne des trois rangées",
      abs(m_avec - m_sans - 5.0) < 0.3, f"{round(m_avec, 4)} contre {round(m_sans, 4)}")
    v("★★★★ chaque rangée fabriquée garde un bruit PROPRE, sinon la moyenne ne retirerait rien",
      float(np.std([avec[0][c] - avec[1][c] for c in range(2000)])) > 1.0)

    # ⚠⚠ LA MESURE COMPLETE SUR UN FAUX DEPOT, POUR QUE LE CHEMIN ENTIER SOIT EXERCE.
    meta = {"chunks": [109, 12, 12], "shape": [109, 36, 40]}
    bloc = _rng(31).normal(0.5, 0.2, size=(109, 12, 12)).astype(np.float32)

    def _depot(cy, cx):
        """Un dépôt qui REFUSE une rangée hors du treillis — comme le vrai le ferait."""
        return ((bloc, None) if 0 <= int(cy) < 3 else (None, "absent du dépôt"))

    out = mesurer(0.0, GRAINE, 1, 4, _depot, meta, 4)
    v("★★★★ la mesure complète traverse les trois rangées du treillis",
      len(out.get("les_pas_par_rangee") or {}) == 3, str(out.get("raison")))
    v("★★★ elle publie les coutures communes et la question déclarée",
      out.get("les_coutures_communes") is not None
      and out.get("la_question_declaree") == LA_QUESTION_DECLAREE)
    v("★★★ elle publie les prédictions à la MÊME longueur, pour qu'elles soient comparables",
      set(out.get("les_predictions_a_la_meme_longueur") or {})
      == {"loptimiste_de_208", "la_realiste_a_trois_lectures", "une_rangee_seule",
          "le_plancher_de_la_matiere"})
    # ⚠⚠⚠ ET A TOUTES LES COUTURES, SINON LE VERDICT SE LIRAIT COMME PORTANT SUR LA RANGEE.
    v("★★★★ elle publie aussi les prédictions à TOUTES les coutures communes",
      set(out.get("les_predictions_a_toutes_les_coutures") or {})
      == {"la_moyenne_mesuree", "une_rangee_seule", "le_plancher_de_la_matiere"},
      str(set(out.get("les_predictions_a_toutes_les_coutures") or {})))
    tt = (out.get("les_predictions_a_toutes_les_coutures") or {}).get("une_rangee_seule") or {}
    v("★★★★ et elles portent sur PLUS de coutures que le tronçon, jamais moins",
      tt.get("les_coutures", 0) >= (out.get("la_marche") or {}).get("les_coutures_du_troncon", 0),
      f"{tt.get('les_coutures')} contre "
      f"{(out.get('la_marche') or {}).get('les_coutures_du_troncon')}")

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
    ap.add_argument("--graine", type=int, default=GRAINE)
    ap.add_argument("--replicats", type=int, default=12)
    a = ap.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(DELAI, a.graine, a.replicats, a.colonnes)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
