"""Une bande de bord plus large lit-elle mieux le pas — et que devient la portée ?

⭐⭐⭐⭐ POURQUOI CE FICHIER, ET C'EST `R4-P51` QUI LE NOMME. `202` a mesuré que le pas du maillage
porte **3,4585 voxels** de dérive vraie pour **3,5189 voxels** de bruit d'estimateur : `199` mesure
donc sa propre erreur autant que le mouvement du feuillet. La largeur de bande qu'il emploie —
**16 colonnes** — vient d'une règle de `198` qui n'a jamais été vérifiée sur la matière : une bande
de `w` colonnes serpente de `w·m/128`, et on prend la plus grande puissance de deux qui garde cela
sous un voxel. Cette tranche met la règle à l'épreuve.

⭐⭐⭐⭐ ET LE BRUIT SE MESURE SANS SECOND LECTEUR. La bande se coupe en deux moitiés disjointes :
celle qui touche la couture, et celle qui est plus loin. Les deux voient la MÊME dérive, donc leur
désaccord est du bruit d'estimateur. C'est un pied bien plus ferme que le modèle croisé de `202`,
qui suppose deux erreurs indépendantes entre deux instruments différents — ici il n'y a qu'un
instrument, appliqué deux fois.

⭐ ET LES DEUX ROUTES DOIVENT DONNER LE MÊME NOMBRE. La dérive estimée par les demi-bandes se compare
à celle que `202` a publiée par l'accord avec le creux. Ce sont deux méthodes sans rien de commun, et
leur accord — ou leur désaccord — est une prédiction falsifiable, pas une identité.

⚠⚠⚠ LE PRIX DE CHERCHER EST SÉPARÉ DE CELUI DE CONFIRMER, comme `192` l'a imposé. Les coutures sont
coupées en deux par leur PARITÉ : les impaires servent à tracer la courbe et à nommer une largeur,
les paires à l'éprouver. Nommer une largeur sur la même matière qui la confirme trouverait toujours
quelque chose.

⚠⚠ LA MOITIÉ PROCHE ET LA MOITIÉ LOIN NE REGARDENT PAS TOUT À FAIT LE MÊME ENDROIT, donc leur
désaccord contient le bruit PLUS la variation réelle de la dérive sur la largeur de la bande. C'est
donc une BORNE SUPÉRIEURE du bruit, et c'est le bon sens de l'erreur : un bruit surestimé ne peut pas
faire croire à une précision qu'on n'a pas.

⚠ La portée est rendue par `combien_de_chunks_avant`, la fonction de `199` elle-même, jamais
réécrite. Et elle est publiée comme une SECONDE LECTURE, à côté de celle de `199` et non à sa place :
`199` publie la portée de SON pas, cette tranche celle de la dérive.

Usage :
    uv run python src/nappe/une_bande_plus_large_lit_elle_mieux.py --verifier
    uv run python src/nappe/une_bande_plus_large_lit_elle_mieux.py \\
        --json docs/mesures/une_bande_plus_large_lit_elle_mieux.json
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
                                        combien_de_chunks_avant, la_largeur_du_bord,
                                        la_ligne_declaree, un_pas)
from la_recette_posee_sur_le_rouleau import DELAI, PERMUTATIONS  # noqa: E402
from le_creux_borne_t_il_la_marche import la_courbe_dun_bloc  # noqa: E402
from ou_le_maillage_quitte_t_il_son_feuillet import (le_segment_declare,  # noqa: E402
                                                     les_pannes_de_reseau, un_chunk)
from ouvrir_les_quinze import _rng  # noqa: E402
from peut_on_deplier_la_phase import ce_que_la_marche_a_rendu  # noqa: E402
from regarder_dans_la_profondeur import (la_loi_appariee,  # noqa: E402
                                         le_seuil_apparie)
from que_montrent_ces_deux_vues import (DEMI_PAS_EN_VOXELS,  # noqa: E402
                                        PAS_EN_VOXELS, la_rangee_montree, une_section)
from zarr_depth import BUCKET, array_meta  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
CE_QUE_LAPPARIEMENT_A_RENDU = MESURES / "le_creux_bouge_t_il_avec_le_maillage.json"
GRAINE = 20261011

LA_QUESTION_DECLAREE = ("une bande de bord plus large lit-elle le pas avec moins de bruit, "
                        "et que devient alors la portée du feuillet ?")
LES_EPREUVES_DECLAREES = ("la largeur nommée sur les coutures impaires fait-elle mieux, "
                          "sur les coutures paires, que celle de `198`",)
GARANTIE = 1.0 / (PERMUTATIONS + 1)
GARANTIE_PAR_EPREUVE = GARANTIE / len(LES_EPREUVES_DECLAREES)


def les_largeurs_a_essayer(cote: int = 128) -> list[int]:
    """Les largeurs candidates : les puissances de deux qu'une coupe en DEUX MOITIÉS admet.

    ⚠⚠ LE PLAFOND EST LA MOITIÉ DU CÔTÉ, et il se dérive : une bande large de plus de la moitié du
    chunk ferait se recouvrir les deux bords d'un même chunk, et l'estimateur comparerait une
    colonne à elle-même. Le plancher est deux, parce qu'une bande d'une seule colonne ne se coupe
    pas en deux.
    """
    out, w = [], 2
    while w <= int(cote) // 2:
        out.append(int(w))
        w *= 2
    return out


def le_serpentement_de_la_bande(gauche: np.ndarray, droite: np.ndarray, largeur: int,
                                plage: int = DEMI_PAS_EN_VOXELS) -> dict:
    """De combien la bande SERPENTE sur sa largeur — la quantité dont `198` tire sa règle.

    ⚠⚠⚠ CE N'EST PAS UN BRUIT D'ESTIMATEUR, ET LE CONFONDRE AVEC UN A ETE UNE ERREUR PAYEE. La
    moitie PROCHE lit la couture entre deux colonnes voisines ; la moitie LOIN lit deux bandes
    situees a `w` colonnes l'une de l'autre. Leur desaccord contient donc, par construction, la
    variation REELLE de la profondeur sur `w` colonnes — c'est-a-dire le serpentement — et il croit
    avec `w` meme quand l'estimateur est parfait. La premiere version de cette tranche l'appelait
    « bruit » et en tirait une courbe monotone qui ne mesurait que sa propre definition.

    ⭐ SOUS SON VRAI NOM, IL SERT : c'est exactement la quantite que la regle de `198` borne a un
    voxel, et `198` l'a publiee sur un treillis. La comparer a ce qu'elle vaut sur une rangee est un
    controle croise que rien n'avait fait.
    """
    g, d = np.asarray(gauche, dtype=float), np.asarray(droite, dtype=float)
    w = int(largeur)
    if w < 2 or g.ndim != 2 or d.ndim != 2:
        return {"decidable": False, "raison": "largeur trop petite ou coupes incompatibles"}
    h = w // 2
    if g.shape[1] < w or d.shape[1] < w:
        return {"decidable": False, "raison": "la coupe est plus étroite que la bande"}
    proche = un_pas(g[:, -h:], d[:, :h], h, plage)
    loin = un_pas(g[:, -w:-h], d[:, h:w], h, plage)
    if not (proche.get("decidable") and loin.get("decidable")):
        return {"decidable": False, "raison": "une des deux lectures a refusé"}
    return {"decidable": True, "la_largeur": w,
            "le_pas_proche_en_voxels": int(proche["le_pas_en_voxels"]),
            "le_pas_loin_en_voxels": int(loin["le_pas_en_voxels"]),
            "le_serpentement_en_voxels": int(proche["le_pas_en_voxels"])
            - int(loin["le_pas_en_voxels"])}


def les_deux_rangees(haute_g: np.ndarray, haute_d: np.ndarray, basse_g: np.ndarray,
                     basse_d: np.ndarray, largeur: int,
                     plage: int = DEMI_PAS_EN_VOXELS) -> dict:
    """Le pas lu sur DEUX RANGÉES du même chunk — le bruit de l'estimateur, à largeur fixée.

    ⭐⭐⭐⭐ LES DEUX LECTURES PORTENT SUR LES MÊMES COLONNES ET LA MÊME COUTURE. Ce qui change est la
    rangee de la coupe, donc la matiere que l'estimateur regarde — et rien d'autre. Leur desaccord
    ne peut pas croitre avec la largeur de la bande par construction, ce qui est precisement ce
    qu'il faut pour COMPARER des largeurs entre elles.

    ⚠⚠ IL RESTE UNE BORNE SUPERIEURE : deux rangees d'un meme chunk ne derivent pas exactement
    pareil — `198` a mesure ce serpentement — donc le desaccord porte le bruit PLUS cette
    difference reelle. Mais cette difference ne depend PAS de la largeur, donc elle decale la
    courbe sans la pencher, et la comparaison entre largeurs tient.

    ⚠ Les deux rangees sont prises au QUART et aux TROIS QUARTS de la hauteur du chunk : assez
    ecartees pour que leurs textures soient independantes, et symetriques pour qu'aucune ne soit
    privilegiee.
    """
    w = int(largeur)
    if w < 1:
        return {"decidable": False, "raison": "largeur nulle"}
    haut = un_pas(haute_g, haute_d, w, plage)
    bas = un_pas(basse_g, basse_d, w, plage)
    if not (haut.get("decidable") and bas.get("decidable")):
        return {"decidable": False, "raison": "une des deux rangées a refusé"}
    return {"decidable": True, "la_largeur": w,
            "le_pas_haut_en_voxels": int(haut["le_pas_en_voxels"]),
            "le_pas_bas_en_voxels": int(bas["le_pas_en_voxels"]),
            "le_desaccord_en_voxels": int(haut["le_pas_en_voxels"])
            - int(bas["le_pas_en_voxels"])}


def la_derive_et_le_bruit(proches, loins) -> dict:
    """La dérive vraie et le bruit d'une demi-bande, tirés de l'accord des deux moitiés.

    ⭐⭐⭐⭐ L'ARITHMETIQUE EST EXACTE ET SANS REGLAGE. Si les deux moities rendent `T + e1` et
    `T + e2` avec des erreurs de meme variance, alors la variance de leur DIFFERENCE vaut deux fois
    celle d'une erreur, et celle de leur MOYENNE vaut la variance de `T` plus la moitie de celle
    d'une erreur. Les deux equations se resolvent : `var(T) = var(moyenne) - var(difference)/4`.

    ⚠⚠⚠ ET LE MODELE SE REFUTE PAR SES PROPRES NOMBRES : si la difference est si grande que `var(T)`
    sort negative, il n'y a pas de derive a extraire et la fonction REFUSE plutot que de rendre une
    racine de nombre negatif.
    """
    a = np.asarray(proches, dtype=float)
    b = np.asarray(loins, dtype=float)
    if a.size < 3 or b.size != a.size:
        return {"decidable": False, "raison": "moins de trois coutures"}
    diff = a - b
    moyenne = (a + b) / 2.0
    vd, vm = float(np.var(diff)), float(np.var(moyenne))
    vt = vm - vd / 4.0
    if vt <= 0.0:
        return {"decidable": False,
                "raison": "les deux moitiés se désaccordent plus qu'elles ne s'accordent : "
                          "aucune dérive à extraire"}
    return {"decidable": True, "les_coutures": int(a.size),
            "la_variance_du_desaccord_en_voxels2": round(vd, 4),
            "le_desaccord_quadratique_en_voxels": round(vd ** 0.5, 4),
            "le_desaccord_median_en_voxels": round(float(np.median(np.abs(diff))), 4),
            "la_derive_en_voxels": round(vt ** 0.5, 4),
            "le_bruit_dune_demi_bande_en_voxels": round((vd / 2.0) ** 0.5, 4),
            "le_signal_sur_bruit": round(vt ** 0.5 / max(1e-9, (vd / 2.0) ** 0.5), 4)}


def les_coutures_dune_parite(paires, impaires: bool) -> list:
    """Une couture sur deux — le partage entre CHERCHER et CONFIRMER.

    ⚠⚠⚠ LA PARITE EST CHOISIE PARCE QU'ELLE NE REGARDE RIEN. Couper la rangee en deux moities
    contigues donnerait deux morceaux de rouleau differents, et une largeur nommee sur l'un pourrait
    echouer sur l'autre pour une raison de matiere et non de methode. Une couture sur deux melange
    les deux moities partout.
    """
    return [p for k, p in enumerate(paires) if (k % 2 == 1) == bool(impaires)]


def lerreur_dune_bande(bruit, serpentement) -> float:
    """L'erreur d'une bande : son aléa et son biais, composés EN QUADRATURE.

    ⭐ LA COMPOSITION N'EST PAS UN CHOIX : deux sources d'erreur independantes ajoutent leurs
    VARIANCES, pas leurs amplitudes. C'est la meme arithmetique que la decomposition de `202` et
    celle des demi-bandes, et l'employer ici garde une seule regle dans toute la chaine.
    """
    return float((float(bruit) ** 2 + float(serpentement) ** 2) ** 0.5)


def les_deux_courbes(lectures: dict, serpentements: dict, largeurs, coutures) -> dict:
    """Le bruit et le serpentement, largeur par largeur — et l'erreur qu'ils composent.

    ⭐⭐⭐⭐ LES DEUX VONT EN SENS CONTRAIRE, ET C'EST TOUT L'ARGUMENT DE `198`. Elargir la bande
    moyenne plus de colonnes, donc diminue l'ALEA ; mais elle moyenne alors des profondeurs qui
    different, donc augmente le BIAIS. La largeur utile est celle ou les deux se croisent, et `198`
    la fixait par une regle a un voxel sans jamais mesurer les deux termes.
    """
    barreaux = []
    for w in largeurs:
        hauts, bas, serp = [], [], []
        for p in coutures:
            lu = lectures.get((w, p))
            if lu is not None and lu.get("decidable"):
                hauts.append(lu["le_pas_haut_en_voxels"])
                bas.append(lu["le_pas_bas_en_voxels"])
            sp = serpentements.get((w, p))
            if sp is not None and sp.get("decidable"):
                serp.append(sp["le_serpentement_en_voxels"])
        if len(hauts) < 3 or len(serp) < 3:
            continue
        d = np.asarray(hauts, dtype=float) - np.asarray(bas, dtype=float)
        s = np.asarray(serp, dtype=float)
        # ⚠⚠ L'ALEA D'UNE SEULE LECTURE EST CELUI DU DESACCORD DIVISE PAR RACINE DE DEUX : le
        # desaccord porte les erreurs des DEUX rangees, et elles s'ajoutent en variance.
        alea = float(np.sqrt(float(np.mean(d * d)))) / (2.0 ** 0.5)
        biais = float(np.sqrt(float(np.mean(s * s))))
        moyenne = (np.asarray(hauts, dtype=float) + np.asarray(bas, dtype=float)) / 2.0
        # ⚠⚠⚠ LA DYNAMIQUE EST PUBLIEE A COTE DE L'ERREUR, ET C'EST UN DEFAUT REEL QUI L'IMPOSE :
        # une bande de deux colonnes lit deux voisines presque identiques, donc elle rend
        # TOUJOURS le meme pas. Son alea est minuscule et son serpentement aussi — elle gagne le
        # critere de l'erreur composee en ne mesurant RIEN. Un critere qui recompense un
        # instrument mort est un critere satisfait par la panne qu'il devait attraper.
        barreaux.append({"la_largeur": int(w), "les_coutures": len(hauts),
                         "la_dispersion_du_pas_en_voxels": round(float(np.std(moyenne)), 4),
                         "le_desaccord_des_rangees_en_voxels": round(
                             float(np.sqrt(float(np.mean(d * d)))), 4),
                         "lalea_en_voxels": round(alea, 4),
                         "le_serpentement_en_voxels": round(biais, 4),
                         "lerreur_en_voxels": round(lerreur_dune_bande(alea, biais), 4)})
    if not barreaux:
        return {"decidable": False, "raison": "aucune largeur lisible"}
    meilleure = min(barreaux, key=lambda x: (x["lerreur_en_voxels"], x["la_largeur"]))
    return {"decidable": True, "les_barreaux": barreaux,
            "la_largeur_nommee": int(meilleure["la_largeur"]),
            "son_erreur_en_voxels": meilleure["lerreur_en_voxels"],
            "lalea_a_la_largeur_nommee_en_voxels": meilleure["lalea_en_voxels"],
            "le_serpentement_a_la_largeur_nommee_en_voxels":
                meilleure["le_serpentement_en_voxels"]}


def lerreur_dune_couture(lectures: dict, serpentements: dict, w: int, p) -> float | None:
    """L'erreur d'UNE couture à UNE largeur — la quantité que l'épreuve appariée compare."""
    lu, sp = lectures.get((int(w), p)), serpentements.get((int(w), p))
    if lu is None or sp is None or not lu.get("decidable") or not sp.get("decidable"):
        return None
    return lerreur_dune_bande(abs(int(lu["le_desaccord_en_voxels"])) / (2.0 ** 0.5),
                              abs(int(sp["le_serpentement_en_voxels"])))


def confirmer(lectures: dict, serpentements: dict, coutures, largeur_nommee: int,
              largeur_de_198: int, garantie: float = GARANTIE_PAR_EPREUVE) -> dict:
    """La largeur nommée fait-elle mieux, sur des coutures qu'elle n'a jamais vues ? L'ÉPREUVE.

    ⭐⭐⭐⭐ LE TEST EST APPARIE ET EXACT : chaque couture est lue aux DEUX largeurs, donc le nul est
    celui d'un tirage a pile ou face sur les seules coutures qui tranchent. Une couture ou les deux
    largeurs se trompent d'autant ne designe personne, et elle est ecartee comme une egalite l'est
    d'un test des signes.

    ⚠⚠⚠ ET SI LA RECHERCHE NOMME LA LARGEUR DE `198`, L'EPREUVE EST VIDE — et c'est une REPONSE, pas
    une panne : aucune largeur ne fait mieux, donc la regle de `198` tient sur la matiere.
    """
    if int(largeur_nommee) == int(largeur_de_198):
        return {"decidable": False,
                "raison": "la recherche nomme la largeur de `198` : rien à confirmer, et c'est "
                          "la réponse",
                "la_largeur_nommee": int(largeur_nommee),
                "la_largeur_de_198": int(largeur_de_198)}
    informatives, justes, vues = 0, 0, 0
    for p in coutures:
        ea = lerreur_dune_couture(lectures, serpentements, largeur_nommee, p)
        eb = lerreur_dune_couture(lectures, serpentements, largeur_de_198, p)
        if ea is None or eb is None:
            continue
        vues += 1
        if abs(ea - eb) < 1e-9:
            continue
        informatives += 1
        justes += int(ea < eb)
    pv = la_loi_appariee(informatives, justes)
    return {"decidable": bool(informatives > 0),
            "la_largeur_nommee": int(largeur_nommee), "la_largeur_de_198": int(largeur_de_198),
            "les_coutures_vues": int(vues), "les_coutures_informatives": int(informatives),
            "les_coutures_ou_la_nommee_gagne": int(justes),
            "le_seuil_apparie": le_seuil_apparie(informatives, garantie).get("le_seuil"),
            "la_valeur_p": round(float(pv), 7),
            "la_garantie_de_lepreuve": round(float(garantie), 7),
            "la_nommee_fait_mieux": bool(pv <= float(garantie) + 1e-12)}


def ce_que_lappariement_a_rendu(chemin: Path = CE_QUE_LAPPARIEMENT_A_RENDU) -> dict:
    """La dérive que `202` a publiée par l'accord avec le creux — relue, jamais recalculée.

    ⚠⚠⚠ C'EST LE CONTROLE CROISE DE LA TRANCHE : deux methodes sans rien de commun — un second
    lecteur d'un cote, deux moities d'un meme lecteur de l'autre — doivent rendre la meme derive.
    """
    if not Path(chemin).is_file():
        return {"decidable": False, "raison": "la mesure de `202` est absente"}
    d = json.loads(Path(chemin).read_text(encoding="utf-8"))
    dc = d.get("la_decomposition") or {}
    if not dc.get("decidable"):
        return {"decidable": False, "raison": "la décomposition de `202` est indécidable"}
    return {"decidable": True,
            "la_derive_en_voxels": dc.get("la_derive_commune_en_voxels"),
            "le_bruit_du_maillage_en_voxels": dc.get("le_bruit_du_maillage_en_voxels"),
            "la_largeur_du_bord": d.get("la_largeur_du_bord"),
            "la_rangee": (d.get("la_ligne") or {}).get("la_rangee")}


def la_portee(derive: float, reference: dict, alea: float | None = None) -> dict:
    """Après combien de chunks un demi-pli est perdu, à cette dérive — la SECONDE LECTURE.

    ⚠⚠⚠ ELLE NE REMPLACE PAS CELLE DE `199`, ELLE SE MET A COTE. `199` publie la portee de SON pas
    quadratique, qui est ce que son estimateur rend ; cette tranche publie celle de la DERIVE, dont
    le bruit d'estimateur a ete retire. Ce sont deux quantites differentes sous deux noms differents,
    et ecraser l'une par l'autre ferait disparaitre ce que `199` a reellement mesure.

    ⚠ La fonction est celle de `199`, importee et jamais reecrite : une seconde definition de la
    portee finirait par ne plus s'accorder avec la premiere.
    """
    if derive is None or float(derive) <= 0.0:
        return {"decidable": False, "raison": "aucune dérive à projeter"}
    # ⚠⚠⚠ UNE DERIVE PLUS PETITE QUE LE BRUIT QUI LA MESURE NE SE PROJETTE PAS, et le critere est
    # DERIVE : projeter une marche au hasard dont le pas est sous le seuil de detection rend une
    # portee arbitrairement grande — la premiere version a rendu **19 metres** sur un rouleau large
    # de cent vingt et un millimetres. Le refus est la reponse, pas une panne.
    if alea is not None and float(derive) <= float(alea):
        return {"decidable": False,
                "raison": f"la dérive ({round(float(derive), 4)} voxel) ne dépasse pas l'aléa qui "
                          f"la mesure ({round(float(alea), 4)}) : rien à projeter"}
    par_la_derive = combien_de_chunks_avant(float(derive), float(DEMI_PAS_EN_VOXELS))
    ref = reference.get("le_pas_quadratique_en_voxels")
    par_le_pas = (combien_de_chunks_avant(float(ref), float(DEMI_PAS_EN_VOXELS))
                  if ref else {"decidable": False, "raison": "le pas de `199` est absent"})
    return {"decidable": bool(par_la_derive.get("decidable")),
            "la_derive_en_voxels": round(float(derive), 4),
            "par_la_derive": par_la_derive,
            "le_pas_quadratique_de_199_en_voxels": ref,
            "par_le_pas_de_199": par_le_pas,
            "le_rapport_des_portees": (
                round(float(par_la_derive["les_chunks"]) / float(par_le_pas["les_chunks"]), 4)
                if par_la_derive.get("decidable") and par_le_pas.get("decidable")
                and par_le_pas["les_chunks"] else None)}


def une_rangee_a_bande(chunks: int, couches: int, colonnes: int,
                       serpentement_par_colonne: float, bruit_par_colonne: float,
                       graine: int, rangees: int = 2) -> dict:
    """Une rangée dont la profondeur est une MARCHE CONTINUE le long des colonnes du rouleau.

    ⭐⭐⭐⭐ LA CONTINUITE A TRAVERS LA COUTURE EST TOUTE LA FIXTURE. La colonne la plus a droite d'un
    chunk et la plus a gauche du suivant sont VOISINES dans le volume, donc leurs profondeurs sont
    presque egales. Une premiere version posait un serpentement qui repartait de zero a chaque
    chunk : elle fabriquait une dent de scie, donc un saut d'un pli entier a chaque couture, et
    l'estimateur lisait **-27 voxels** la ou la verite valait **-1,7**.

    ⭐ LES DEUX EFFETS QUE LA TRANCHE OPPOSE SORTENT DU MEME OBJET, et un seul parametre les separe.
    Le BRUIT par colonne pousse a elargir la bande, puisqu'on en moyenne davantage. Le SERPENTEMENT
    par colonne pousse a la retrecir, puisqu'une bande large moyenne des profondeurs qui different.

    ⚠⚠ LES RANGEES PARTAGENT LA PROFONDEUR ET NON LE BRUIT, et c'est ce qui fait de leur desaccord
    une mesure d'ALEA : elles voient la meme surface, donc le serpentement les biaise de la meme
    facon et ne peut pas se lire dans leur difference.
    """
    r = _rng(int(graine))
    marge = int(DEMI_PAS_EN_VOXELS) * 2 + 4
    fond = r.normal(0.0, 1.0, size=int(couches) + 2 * marge)
    n = int(chunks) * int(colonnes)
    prof = np.cumsum(r.normal(0.0, float(serpentement_par_colonne), size=n))
    prof = prof - float(np.mean(prof))
    par_rangee = []
    for _ in range(int(rangees)):
        sections = {}
        for k in range(int(chunks)):
            cols = []
            for c in range(int(colonnes)):
                j = int(round(float(prof[k * int(colonnes) + c])))
                j = max(-marge, min(marge, j))
                cols.append(fond[marge - j:marge - j + int(couches)]
                            + r.normal(0.0, float(bruit_par_colonne), size=int(couches)))
            sections[k] = np.stack(cols, axis=1)
        par_rangee.append(sections)
    return {"les_rangees": par_rangee, "les_profondeurs": prof,
            "la_derive_par_couture_en_voxels": round(
                float(serpentement_par_colonne) * (float(colonnes) ** 0.5), 4)}


def la_part_qui_ameliore(chunks: int, couches: int, colonnes: int,
                         serpentement_par_colonne: float, bruit_par_colonne: float,
                         graine: int, replicats: int, largeurs) -> dict:
    """La part des réplicats où la LARGE bande a une erreur composée plus petite que l'ÉTROITE.

    ⚠⚠ LES EGALITES COMPTENT COMME DES ECHECS, ET C'EST LE BON SENS DE L'ERREUR : sur une matiere
    si facile que les deux largeurs lisent juste, elargir n'apporte RIEN, et le dire « mieux »
    ferait passer une absence d'effet pour un gain.
    """
    etroite, large = int(min(largeurs)), int(max(largeurs))
    mieux = 0
    for k in range(int(replicats)):
        f = une_rangee_a_bande(chunks, couches, colonnes, serpentement_par_colonne,
                               bruit_par_colonne, int(graine) + 101 * k)
        if len(f["les_rangees"]) < 2:
            # ⚠⚠ UNE FIXTURE QUI NE REND QU'UNE RANGEE NE PEUT MESURER AUCUN ALEA, et le dire ici
            # garde a la batterie un VERDICT : un bris pose sur la fixture la faisait tomber en
            # panne avant qu'elle ne rende le sien.
            continue
        haute, basse = f["les_rangees"][0], f["les_rangees"][1]
        e = {}
        for w in (etroite, large):
            al, se = [], []
            for a in range(int(chunks) - 1):
                x = les_deux_rangees(haute[a], haute[a + 1], basse[a], basse[a + 1], w)
                y = le_serpentement_de_la_bande(haute[a], haute[a + 1], w)
                if x.get("decidable"):
                    al.append(x["le_desaccord_en_voxels"])
                if y.get("decidable"):
                    se.append(y["le_serpentement_en_voxels"])
            if al and se:
                e[w] = lerreur_dune_bande(
                    float(np.sqrt(np.mean(np.asarray(al, float) ** 2))) / (2.0 ** 0.5),
                    float(np.sqrt(np.mean(np.asarray(se, float) ** 2))))
        if etroite in e and large in e:
            mieux += int(e[large] < e[etroite])
    return {"les_replicats": int(replicats), "les_mieux": int(mieux),
            "la_part": round(float(mieux) / float(replicats), 4)}


def sur_letalon(largeurs, graine: int = GRAINE, replicats: int = 12, chunks: int = 24,
                couches: int = 109, colonnes: int = 128) -> dict:
    """L'instrument sait-il dire que large est MIEUX, et aussi que large est PIRE ?

    ⭐⭐⭐⭐ LES DEUX FACES SONT LES DEUX REGIMES DE LA REGLE DE `198`, ET RIEN N'Y EST TAPE. Cette
    regle prend la plus grande puissance de deux dont le serpentement d'une bande reste sous UN
    voxel. Un serpentement par colonne de `s` fait serpenter une bande de `w` colonnes de
    `s·racine(w)`, donc a `s = 0,02` meme la bande la plus large reste sous un cinquieme de voxel —
    la regle dit LARGE — et a `s = 1` la plus etroite depasse deja un voxel et demi — la regle dit
    ETROIT. L'instrument doit dire la meme chose qu'elle dans les deux cas.

    ⚠⚠⚠ LES DEUX FACES SUR REPLICATS, ET ELLES SONT SYMETRIQUES : un instrument qui rendrait toujours
    « large est mieux » separerait la premiere face sans rien mesurer.
    """
    calme, agite = 0.02, 1.0
    sans = la_part_qui_ameliore(chunks, couches, colonnes, calme, 3.0,
                                graine, replicats, largeurs)
    avec = la_part_qui_ameliore(chunks, couches, colonnes, agite, 0.2,
                                graine + 5000, replicats, largeurs)
    return {"decidable": True,
            "la_largeur_etroite": int(min(largeurs)), "la_largeur_large": int(max(largeurs)),
            "le_serpentement_calme_par_colonne": float(calme),
            "le_serpentement_agite_par_colonne": float(agite),
            "le_serpentement_dune_bande_calme_en_voxels": round(
                calme * (float(max(largeurs)) ** 0.5), 4),
            "le_serpentement_dune_bande_agitee_en_voxels": round(
                agite * (float(min(largeurs)) ** 0.5), 4),
            "quand_la_regle_dit_large": sans, "quand_la_regle_dit_etroit": avec,
            "letalon_separe": bool(sans["la_part"] >= 1.0 and avec["la_part"] <= 0.0)}


def les_rangees_declarees(cote: int) -> tuple[int, int]:
    """Les deux rangées de coupe : au QUART et aux TROIS QUARTS de la hauteur du chunk.

    ⚠ Elles sont derivees et symetriques : assez ecartees pour que leurs textures soient
    independantes, et aucune n'est privilegiee. Les prendre adjacentes ferait deux lectures de la
    MEME matiere, donc un desaccord qui sous-estimerait l'alea.
    """
    return int(cote) // 4, (3 * int(cote)) // 4


def la_ligne(volume: dict, delai: float = DELAI, colonnes: int | None = None,
             ouvrir=None, meta=None) -> dict:
    """Deux coupes de chaque chunk d'une rangée — la MÊME rangée que `199`, `200` et `202`.

    ⚠ Le filtre du producteur est celui de `200` : un chunk trop peu texturé n'entre pas, sinon la
    rangée ne serait plus comparable à celles des tranches qui la précèdent.
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
    hautes, basses, refus, reprises = {}, {}, {}, 0
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
        ra, rb = les_rangees_declarees(b.shape[1])
        hautes[int(cx)] = une_section(b, ra)
        basses[int(cx)] = une_section(b, rb)
    return {"decidable": bool(hautes), "segment": volume["segment"],
            "grille_de_chunks": [int(gy), int(gx)], "la_rangee": int(ligne),
            "le_cote_du_chunk": int(hx),
            "les_rangees_de_coupe": list(les_rangees_declarees(int(hx))),
            "colonnes_demandees": len(voulues), "colonnes_lues": len(hautes),
            "les_reprises_du_reseau": int(reprises), "refuses": refus,
            "hautes": hautes, "basses": basses, "les_colonnes": voulues}


def juger(courbe: dict, epreuve: dict, croise: dict, portee: dict) -> dict:
    """La règle de `198` tient-elle ? Le verdict ne tient qu'à l'épreuve déclarée.

    ⚠⚠ ET LE CONTROLE CROISE EST PUBLIE A COTE SANS PORTER LE VERDICT : que deux methodes rendent la
    meme derive est une propriete du MONDE, pas de l'epreuve.
    """
    if not courbe.get("decidable"):
        return {"decidable": False, "raison": "aucune courbe"}
    nommee = int(courbe["la_largeur_nommee"])
    l198 = epreuve.get("la_largeur_de_198")
    # ⭐⭐⭐⭐ LA PREMISSE DE `198` SE VERIFIE SANS AUCUN CRITERE DE SELECTION : sa regle prend la plus
    # grande puissance de deux dont le serpentement reste sous UN voxel. Le serpentement a cette
    # largeur est mesure ici, et il suffit de le lire. C'est le seul verdict de la tranche qui ne
    # depende pas de la facon dont une largeur est nommee.
    s198 = next((x["le_serpentement_en_voxels"] for x in courbe.get("les_barreaux") or []
                 if x["la_largeur"] == l198), None)
    return {"decidable": True,
            "la_largeur_nommee": nommee,
            "le_serpentement_a_la_largeur_de_198_en_voxels": s198,
            "la_premisse_de_198_tient": (None if s198 is None else bool(float(s198) < 1.0)),
            "de_combien_la_premisse_est_depassee": (
                None if s198 is None else round(float(s198), 4)),
            "la_largeur_de_198": epreuve.get("la_largeur_de_198"),
            "la_nommee_fait_mieux": bool(epreuve.get("la_nommee_fait_mieux")),
            "la_regle_de_198_tient": bool(
                nommee == epreuve.get("la_largeur_de_198")
                or not epreuve.get("la_nommee_fait_mieux")),
            "lalea_a_la_largeur_nommee_en_voxels": courbe.get(
                "lalea_a_la_largeur_nommee_en_voxels"),
            "le_serpentement_a_la_largeur_nommee_en_voxels": courbe.get(
                "le_serpentement_a_la_largeur_nommee_en_voxels"),
            "la_derive_par_les_rangees_en_voxels": courbe.get("la_derive_a_la_largeur_nommee"),
            "la_derive_par_le_creux_en_voxels": croise.get("la_derive_en_voxels"),
            "le_rapport_des_deux_derives": courbe.get("le_rapport_des_deux_derives"),
            "la_portee_par_la_derive_en_chunks": (
                (portee.get("par_la_derive") or {}).get("les_chunks")),
            "la_portee_de_199_en_chunks": (
                (portee.get("par_le_pas_de_199") or {}).get("les_chunks"))}


def mesurer(delai: float = DELAI, graine: int = GRAINE, replicats: int = 12,
            colonnes: int | None = None, ouvrir=None, meta=None) -> dict:
    """Les deux courbes, l'épreuve sur les coutures réservées, et la portée."""
    v = le_segment_declare()
    if v is None:
        return {"decidable": False, "raison": "aucun volume recensé"}
    lg = la_ligne(v, delai, colonnes, ouvrir, meta)
    if not lg.get("decidable"):
        return {"decidable": False, "raison": lg.get("raison", "la ligne est vide")}
    pannes = les_pannes_de_reseau(lg.get("refuses"))
    if pannes:
        return {"decidable": False,
                "raison": f"{pannes} chunks perdus par le réseau — une rangée dont le fil est "
                          f"tombé n'est pas comparable à celles de `199` à `202`",
                "la_ligne": {k: x for k, x in lg.items()
                             if k not in ("hautes", "basses", "les_colonnes")}}
    hautes, basses = lg["hautes"], lg["basses"]
    voisines = [(c, c + 1) for c in sorted(hautes) if (c + 1) in hautes]
    largeurs = les_largeurs_a_essayer(int(lg["le_cote_du_chunk"]))
    l198 = int(la_largeur_du_bord())
    lectures, serpentements = {}, {}
    for w in largeurs:
        for p in voisines:
            lectures[(w, p)] = les_deux_rangees(hautes[p[0]], hautes[p[1]],
                                                basses[p[0]], basses[p[1]], w)
            serpentements[(w, p)] = le_serpentement_de_la_bande(hautes[p[0]], hautes[p[1]], w)
    croise = ce_que_lappariement_a_rendu()
    chercher = les_coutures_dune_parite(voisines, True)
    a_confirmer = les_coutures_dune_parite(voisines, False)
    recherche = les_deux_courbes(lectures, serpentements, largeurs, chercher)
    entiere = les_deux_courbes(lectures, serpentements, largeurs, voisines)
    # ⭐⭐⭐⭐ LA DERIVE PAR LES DEUX RANGEES SE COMPARE A CELLE QUE `202` A TIREE DU CREUX : deux
    # methodes sans rien de commun, donc leur accord est une prediction falsifiable.
    def _derive(w):
        h_ = [lectures[(w, p)]["le_pas_haut_en_voxels"] for p in voisines
              if lectures[(w, p)].get("decidable")]
        b_ = [lectures[(w, p)]["le_pas_bas_en_voxels"] for p in voisines
              if lectures[(w, p)].get("decidable")]
        return la_derive_et_le_bruit(h_, b_)

    nommee = int(recherche["la_largeur_nommee"]) if recherche.get("decidable") else l198
    # ⭐⭐⭐⭐ LA DERIVE SE LIT A LA LARGEUR QUE LA TRANCHE CONCLUT, PAS A CELLE DONT ELLE DOUTE. Elle
    # est publiee aux DEUX, et le refus a l'une est lui-meme un resultat : si les deux rangees se
    # desaccordent plus que leur moyenne ne varie, il n'y a aucune derive a extraire a cette
    # largeur-la, et c'est ce que le modele dit de lui-meme.
    db = _derive(nommee)
    db198 = _derive(l198)
    entiere["la_derive_a_la_largeur_nommee"] = db.get("la_derive_en_voxels")
    entiere["la_derive_a_la_largeur_de_198"] = db198.get("la_derive_en_voxels")
    entiere["le_refus_a_la_largeur_de_198"] = db198.get("raison")
    entiere["la_derive_de_202_en_voxels"] = croise.get("la_derive_en_voxels")
    entiere["le_rapport_des_deux_derives"] = (
        round(float(db["la_derive_en_voxels"]) / float(croise["la_derive_en_voxels"]), 4)
        if db.get("decidable") and croise.get("la_derive_en_voxels") else None)
    epreuve = (confirmer(lectures, serpentements, a_confirmer,
                         int(recherche["la_largeur_nommee"]), l198)
               if recherche.get("decidable")
               else {"decidable": False, "raison": "aucune largeur nommée"})
    m199 = ce_que_la_marche_a_rendu()
    alea_nommee = next((x["lalea_en_voxels"] for x in entiere["les_barreaux"]
                        if x["la_largeur"] == nommee), None)
    portee = la_portee(entiere.get("la_derive_a_la_largeur_nommee"), m199, alea_nommee)
    return {
        "graine": int(graine), "tirages": int(PERMUTATIONS),
        "la_question_declaree": LA_QUESTION_DECLAREE,
        "les_epreuves_declarees": list(LES_EPREUVES_DECLAREES),
        "la_garantie_par_epreuve": round(float(GARANTIE_PAR_EPREUVE), 7),
        "le_pas_dun_pli_en_voxels": round(float(PAS_EN_VOXELS), 4),
        "la_demi_periode_en_voxels": int(DEMI_PAS_EN_VOXELS),
        "la_largeur_de_198": l198,
        "les_largeurs_essayees": largeurs,
        "la_ligne": {k: x for k, x in lg.items()
                     if k not in ("hautes", "basses", "les_colonnes")},
        "les_coutures_voisines": len(voisines),
        "les_coutures_pour_chercher": len(chercher),
        "les_coutures_pour_confirmer": len(a_confirmer),
        "ce_que_199_a_rendu": m199,
        "ce_que_202_a_rendu": croise,
        "la_derive_par_les_deux_rangees": db,
        "la_derive_a_la_largeur_de_198": db198,
        "la_recherche": recherche,
        "la_courbe_entiere": entiere,
        "lepreuve": epreuve,
        "la_portee": portee,
        "le_verdict": juger(entiere, epreuve, croise, portee),
        "letalon": sur_letalon(largeurs, graine, replicats),
    }


def afficher(r: dict) -> None:
    if not r.get("decidable", True):
        print(f"UNE BANDE PLUS LARGE LIT-ELLE MIEUX   indécidable : {r.get('raison')}")
        return
    lg, re_, en = r["la_ligne"], r["la_recherche"], r["la_courbe_entiere"]
    ep, po, ve, e = r["lepreuve"], r["la_portee"], r["le_verdict"], r["letalon"]
    print(f"UNE BANDE PLUS LARGE LIT-ELLE MIEUX   segment {lg['segment']} · rangée "
          f"{lg['la_rangee']} · {lg['colonnes_lues']} chunks lus sur "
          f"{lg['colonnes_demandees']} · coupes aux rangées {lg['les_rangees_de_coupe']}")
    print(f"  LES COUTURES      {r['les_coutures_voisines']} voisines · "
          f"{r['les_coutures_pour_chercher']} pour chercher · "
          f"{r['les_coutures_pour_confirmer']} pour confirmer · largeur de `198` "
          f"{r['la_largeur_de_198']}")
    if en.get("decidable"):
        print("  L'ALÉA            " + " · ".join(
            f"{x['la_largeur']}→{x['lalea_en_voxels']}" for x in en["les_barreaux"]))
        print("  LE SERPENTEMENT   " + " · ".join(
            f"{x['la_largeur']}→{x['le_serpentement_en_voxels']}" for x in en["les_barreaux"]))
        print("  L'ERREUR          " + " · ".join(
            f"{x['la_largeur']}→{x['lerreur_en_voxels']}" for x in en["les_barreaux"]))
        print(f"  LA DÉRIVE         {en.get('la_derive_a_la_largeur_nommee')} vx à la largeur "
              f"nommée contre {en.get('la_derive_de_202_en_voxels')} par le creux (`202`) · "
              f"rapport {en.get('le_rapport_des_deux_derives')}")
        print(f"                    à la largeur de `198` : "
              f"{en.get('la_derive_a_la_largeur_de_198') or en.get('le_refus_a_la_largeur_de_198')}")
    if re_.get("decidable"):
        print(f"  LA RECHERCHE      nomme la largeur {re_['la_largeur_nommee']} "
              f"(erreur {re_['son_erreur_en_voxels']} vx)")
    if ep.get("decidable"):
        print(f"  L'ÉPREUVE         {ep['les_coutures_ou_la_nommee_gagne']} gains sur "
              f"{ep['les_coutures_informatives']} informatives (seuil {ep['le_seuil_apparie']}) · "
              f"P = {ep['la_valeur_p']} · mieux {ep['la_nommee_fait_mieux']}")
    else:
        print(f"  L'ÉPREUVE         {ep.get('raison')}")
    if po.get("decidable"):
        print(f"  LA PORTÉE         un demi-pli en {po['par_la_derive']['les_chunks']} chunks "
              f"= {po['par_la_derive']['la_largeur_en_mm']} mm, à la dérive "
              f"{po['la_derive_en_voxels']} vx · `199` en donnait "
              f"{po['par_le_pas_de_199']['les_chunks']}")
    if ve.get("decidable"):
        print(f"  LE VERDICT        la PRÉMISSE de `198` — un serpentement sous un voxel — tient "
              f"{ve['la_premisse_de_198_tient']} : il vaut "
              f"{ve['de_combien_la_premisse_est_depassee']} voxels à sa largeur")
        print(f"                    sa RÈGLE tient {ve['la_regle_de_198_tient']} · dérive "
              f"{ve.get('la_derive_par_les_rangees_en_voxels')} contre "
              f"{ve.get('la_derive_par_le_creux_en_voxels')} par le creux")
    print(f"  L'ÉTALON          sépare {e['letalon_separe']} · quand la règle dit LARGE, large "
          f"gagne {e['quand_la_regle_dit_large']['la_part']} · quand elle dit ÉTROIT, large gagne "
          f"{e['quand_la_regle_dit_etroit']['la_part']}")


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
    v("★★ la rangée est la MÊME que celle de `199` à `202`", la_ligne_declaree(396) == 198)

    # ⚠⚠ LES LARGEURS ET LES RANGEES SONT DERIVEES DU CHUNK, PAS TAPEES.
    v("★★★★ les largeurs sont les puissances de deux jusqu'à la MOITIÉ du côté",
      les_largeurs_a_essayer(128) == [2, 4, 8, 16, 32, 64], str(les_largeurs_a_essayer(128)))
    v("★★★ un chunk plus petit en offre moins", les_largeurs_a_essayer(32) == [2, 4, 8, 16])
    v("★★★ et la largeur de `198` est parmi elles", 16 in les_largeurs_a_essayer(128))
    v("★★★★ les deux rangées sont au quart et aux trois quarts, donc symétriques et écartées",
      les_rangees_declarees(128) == (32, 96)
      and les_rangees_declarees(128)[1] - les_rangees_declarees(128)[0] == 64,
      str(les_rangees_declarees(128)))

    fond = _rng(3).normal(0.0, 1.0, size=200)

    def _plate(dec, n=128):
        return np.stack([fond[60 - int(dec):60 - int(dec) + 109] for _ in range(n)], axis=1)

    def _mixte(dec_proche, dec_loin, w):
        h, cols = w // 2, []
        for c in range(128):
            d = dec_proche if c >= 128 - h else (dec_loin if c >= 128 - w else 0)
            cols.append(fond[60 - int(d):60 - int(d) + 109])
        return np.stack(cols, axis=1)

    # ⭐⭐⭐⭐ LE SERPENTEMENT MESURE LA VARIATION SUR LA LARGEUR, ET IL PORTE CE NOM.
    sp = le_serpentement_de_la_bande(_plate(0), _plate(5), 32)
    v("★★★★ une bande qui ne serpente pas rend un serpentement nul",
      sp["decidable"] and sp["le_serpentement_en_voxels"] == 0
      and sp["le_pas_proche_en_voxels"] == 5, str(sp))
    sp2 = le_serpentement_de_la_bande(_mixte(0, 7, 32), _plate(5), 32)
    v("★★★★ et une bande dont la moitié loin porte autre chose le rend non nul : les deux moitiés "
      "sont bien DISJOINTES",
      sp2["decidable"] and sp2["le_serpentement_en_voxels"] != 0,
      f"proche {sp2.get('le_pas_proche_en_voxels')} loin {sp2.get('le_pas_loin_en_voxels')}")
    v("★★ une largeur de un ne se coupe pas en deux",
      not le_serpentement_de_la_bande(_plate(0), _plate(5), 1).get("decidable"))

    # ⭐⭐⭐⭐ LE DESACCORD DES DEUX RANGEES MESURE L'ALEA, ET IL PORTE CE NOM.
    dr = les_deux_rangees(_plate(0), _plate(5), _plate(0), _plate(5), 16)
    v("★★★★ deux rangées qui voient la même chose rendent un désaccord nul",
      dr["decidable"] and dr["le_desaccord_en_voxels"] == 0, str(dr))
    dr2 = les_deux_rangees(_plate(0), _plate(5), _plate(0), _plate(9), 16)
    v("★★★★ et deux rangées qui lisent des pas différents le rendent",
      dr2["le_desaccord_en_voxels"] == 5 - 9, str(dr2["le_desaccord_en_voxels"]))
    v("★★★★ le désaccord des rangées NE DÉPEND PAS de la largeur quand la matière est plate — "
      "c'est ce qui rend les largeurs comparables",
      {les_deux_rangees(_plate(0), _plate(5), _plate(0), _plate(9), w)["le_desaccord_en_voxels"]
       for w in (2, 8, 32, 64)} == {-4})

    def _rampe(pente):
        """Une coupe dont la profondeur monte en RAMPE en s'éloignant de la couture.

        ⚠ La rampe est bornée aux soixante-quatre colonnes de la bande la plus large : au-delà,
        le décalage sortirait du fond tiré et la coupe ne serait plus lisible.
        """
        cols = []
        for c in range(128):
            j = int(round(float(pente) * min(64.0, float(127 - c))))
            cols.append(fond[60 - j:60 - j + 109])
        return np.stack(cols, axis=1)

    large = le_serpentement_de_la_bande(_rampe(0.5), _plate(0), 64)["le_serpentement_en_voxels"]
    etroit = le_serpentement_de_la_bande(_rampe(0.5), _plate(0), 4)["le_serpentement_en_voxels"]
    v("★★★★ alors que le serpentement, lui, CROÎT avec la largeur sur une bande en rampe",
      abs(large) > 4 * max(1, abs(etroit)), f"large {large} contre étroit {etroit}")

    # ⭐ L'ERREUR COMPOSE LES DEUX EN QUADRATURE, PAS EN SOMME.
    v("★★★★ l'erreur compose l'aléa et le serpentement en QUADRATURE",
      abs(lerreur_dune_bande(3.0, 4.0) - 5.0) < 1e-9, str(lerreur_dune_bande(3.0, 4.0)))
    v("★★★ donc elle n'est pas leur somme", abs(lerreur_dune_bande(3.0, 4.0) - 7.0) > 1.0)

    # ⭐⭐⭐⭐ LA DERIVE ET LE BRUIT SE RETROUVENT SUR DES VARIANCES POSEES.
    gr = _rng(7)
    n_ = 60000
    vrai = gr.normal(0.0, 4.0, size=n_)
    db = la_derive_et_le_bruit(vrai + gr.normal(0.0, 3.0, size=n_),
                               vrai + gr.normal(0.0, 3.0, size=n_))
    v("★★★★ la dérive posée à quatre voxels est retrouvée",
      db.get("decidable") and abs(float(db["la_derive_en_voxels"]) - 4.0) < 0.2,
      str(db.get("la_derive_en_voxels")))
    v("★★★★ et le bruit d'une rangée posé à trois",
      abs(float(db["le_bruit_dune_demi_bande_en_voxels"]) - 3.0) < 0.2,
      str(db.get("le_bruit_dune_demi_bande_en_voxels")))
    v("★★★★ deux lectures qui ne s'accordent pas du tout ne laissent AUCUNE dérive à extraire",
      not la_derive_et_le_bruit(gr.normal(0.0, 5.0, size=4000),
                                gr.normal(0.0, 5.0, size=4000)).get("decidable"))

    # ⚠⚠⚠ CHERCHER ET CONFIRMER SONT DISJOINTS, ET ENTRELACES.
    paires = [(c, c + 1) for c in range(10)]
    ch, co = les_coutures_dune_parite(paires, True), les_coutures_dune_parite(paires, False)
    v("★★★★ les deux moitiés sont disjointes et couvrent tout",
      set(ch) | set(co) == set(paires) and not (set(ch) & set(co)))
    v("★★★★ et elles sont ENTRELACÉES, pas deux morceaux contigus de rouleau",
      ch[:3] == [(1, 2), (3, 4), (5, 6)] and co[:3] == [(0, 1), (2, 3), (4, 5)]
      and len(ch) + len(co) == len(paires), f"{ch[:3]} · {co[:3]}")

    # ⭐⭐⭐⭐ LA COURBE NOMME PAR L'ERREUR COMPOSEE, ET TRANCHE LES EGALITES PAR LA PLUS PETITE.
    lect, serp = {}, {}
    for w, al, se in ((2, 12, 0), (4, 6, 1), (8, 3, 2), (16, 3, 2), (32, 1, 9)):
        for k, p in enumerate(paires):
            s = 1 if k % 2 else -1
            lect[(w, p)] = {"decidable": True, "la_largeur": w,
                            "le_pas_haut_en_voxels": al * s, "le_pas_bas_en_voxels": 0,
                            "le_desaccord_en_voxels": al * s}
            serp[(w, p)] = {"decidable": True, "la_largeur": w,
                            "le_pas_proche_en_voxels": se * s, "le_pas_loin_en_voxels": 0,
                            "le_serpentement_en_voxels": se * s}
    cb = les_deux_courbes(lect, serp, [2, 4, 8, 16, 32], paires)
    v("★★★★ la courbe nomme la largeur à la plus petite erreur COMPOSÉE",
      cb["decidable"] and cb["la_largeur_nommee"] == 8, str(cb.get("la_largeur_nommee")))
    v("★★★★ et une égalité se tranche par la PLUS PETITE largeur",
      cb["la_largeur_nommee"] == 8 and any(x["la_largeur"] == 16 for x in cb["les_barreaux"]))
    v("★★★★ l'aléa publié est celui d'UNE lecture, donc le désaccord divisé par racine de deux",
      abs(cb["les_barreaux"][0]["lalea_en_voxels"] - round(12.0 / (2.0 ** 0.5), 4)) < 1e-4,
      str(cb["les_barreaux"][0]))

    # ⚠⚠⚠ L'EPREUVE EST APPARIEE, ELLE ECARTE LES EGALITES, ET ELLE SE TAIT QUAND IL N'Y A RIEN.
    ep = confirmer(lect, serp, paires, 8, 16)
    v("★★★★ deux largeurs d'erreur identique ne désignent aucune couture informative",
      ep["les_coutures_informatives"] == 0 and ep["les_coutures_vues"] == 10,
      f"{ep['les_coutures_informatives']} sur {ep['les_coutures_vues']}")
    ep2 = confirmer(lect, serp, paires, 8, 2)
    v("★★★★ une largeur meilleure partout gagne toutes les informatives et déclenche",
      ep2["decidable"] and ep2["les_coutures_ou_la_nommee_gagne"] == 10
      and ep2["la_nommee_fait_mieux"],
      f"{ep2['les_coutures_ou_la_nommee_gagne']}/{ep2['les_coutures_informatives']} "
      f"P = {ep2['la_valeur_p']}")
    ep3 = confirmer(lect, serp, paires, 2, 8)
    v("★★★★ et la largeur PIRE ne déclenche pas, même avec autant d'informatives",
      not ep3["la_nommee_fait_mieux"] and ep3["les_coutures_ou_la_nommee_gagne"] == 0,
      f"{ep3['les_coutures_ou_la_nommee_gagne']} · P = {ep3['la_valeur_p']}")
    # ⚠⚠ LA SONDE LIT LA RAISON, PAS SEULEMENT LE REFUS : sans le garde, comparer une largeur a
    # elle-meme rend AUSSI « indecidable », mais parce que toutes les coutures sont a egalite.
    # Deux refus pour deux raisons differentes doivent se distinguer, sinon le bris passe.
    vide = confirmer(lect, serp, paires, 16, 16)
    v("★★★★ si la recherche nomme la largeur de `198`, l'épreuve est VIDE — et c'est la réponse",
      not vide.get("decidable") and "réponse" in str(vide.get("raison")), str(vide.get("raison")))

    # ⚠⚠⚠ LA PORTEE EST CELLE DE `199`, ET ELLE NE REMPLACE PAS LA SIENNE.
    po = la_portee(3.4585, {"le_pas_quadratique_en_voxels": 4.941})
    v("★★★★ la portée par la dérive vient de la fonction de `199`",
      po["decidable"] and po["par_la_derive"]["les_chunks"]
      == combien_de_chunks_avant(3.4585, float(DEMI_PAS_EN_VOXELS))["les_chunks"],
      str(po["par_la_derive"]))
    v("★★★★ et la portée du PAS de `199` est publiée À CÔTÉ, jamais écrasée",
      abs(po["par_le_pas_de_199"]["les_chunks"] - 53.09) < 0.5, str(po["par_le_pas_de_199"]))
    v("★★★★ une dérive plus petite porte PLUS LOIN, et le rapport le dit",
      po["le_rapport_des_portees"] > 1.0, str(po["le_rapport_des_portees"]))
    v("★★ une dérive nulle ne se projette pas",
      not la_portee(0.0, {"le_pas_quadratique_en_voxels": 4.941}).get("decidable"))
    # ⚠⚠⚠ ET UNE DERIVE PLUS PETITE QUE SON PROPRE ALEA NON PLUS : sans ce refus, un estimateur qui
    # ne mesure rien rend une portee de dix-neuf metres sur un rouleau large de cent vingt et un
    # millimetres. Le defaut a ete paye, la mesure l'a rendu.
    v("★★★★ une dérive plus petite que l'aléa qui la mesure est REFUSÉE, jamais projetée",
      not la_portee(0.1436, {"le_pas_quadratique_en_voxels": 4.941}, 0.2362).get("decidable"))
    v("★★★★ et la même dérive se projette quand l'aléa est plus petit qu'elle",
      la_portee(0.1436, {"le_pas_quadratique_en_voxels": 4.941}, 0.05).get("decidable"))
    v("★★★ sans aléa donné, la portée ne refuse rien — le garde ne s'invente pas de nombre",
      la_portee(0.1436, {"le_pas_quadratique_en_voxels": 4.941}).get("decidable"))

    # ⭐⭐⭐⭐ LA PREMISSE DE `198` SE LIT SANS AUCUN CRITERE DE SELECTION.
    courbe_198 = {"decidable": True, "la_largeur_nommee": 2,
                  "les_barreaux": [{"la_largeur": 16, "le_serpentement_en_voxels": 10.97},
                                   {"la_largeur": 2, "le_serpentement_en_voxels": 0.45}]}
    jg = juger(courbe_198, {"la_largeur_de_198": 16}, {}, {})
    v("★★★★ un serpentement de onze voxels à la largeur de `198` REFUTE sa prémisse",
      jg["la_premisse_de_198_tient"] is False
      and abs(float(jg["de_combien_la_premisse_est_depassee"]) - 10.97) < 1e-9,
      str(jg["de_combien_la_premisse_est_depassee"]))
    courbe_ok = {"decidable": True, "la_largeur_nommee": 16,
                 "les_barreaux": [{"la_largeur": 16, "le_serpentement_en_voxels": 0.4}]}
    v("★★★★ et un serpentement sous un voxel la tient",
      juger(courbe_ok, {"la_largeur_de_198": 16}, {}, {})["la_premisse_de_198_tient"] is True)
    v("★★★ une largeur absente de la courbe rend la prémisse indécidable, jamais fausse",
      juger(courbe_ok, {"la_largeur_de_198": 8}, {}, {})["la_premisse_de_198_tient"] is None)

    # ⚠⚠⚠ CHAQUE BARREAU PUBLIE LA DYNAMIQUE DU PAS, sinon un estimateur MORT gagne le critere.
    v("★★★★ chaque barreau porte la dispersion du pas qu'il lit",
      all("la_dispersion_du_pas_en_voxels" in x for x in cb["les_barreaux"]),
      str(cb["les_barreaux"][0]))
    v("★★★★ et elle vaut zéro quand l'estimateur rend toujours le même pas",
      abs(les_deux_courbes(
          {(4, p): {"decidable": True, "le_pas_haut_en_voxels": 0,
                    "le_pas_bas_en_voxels": 0, "le_desaccord_en_voxels": 0} for p in paires},
          {(4, p): {"decidable": True, "le_serpentement_en_voxels": 0} for p in paires},
          [4], paires)["les_barreaux"][0]["la_dispersion_du_pas_en_voxels"]) < 1e-9)
    v("★★★ `202` absent est refusé, jamais deviné",
      not ce_que_lappariement_a_rendu(MESURES / "absent.json")["decidable"])

    # ⭐⭐⭐⭐ L'ETALON SAIT DIRE LES DEUX SENS.
    e = sur_letalon([2, 4, 8, 16, 32, 64], 11, replicats=6, chunks=20)
    v("★★★★ quand la règle de `198` dit LARGE, l'instrument le dit aussi, sur tous les réplicats",
      e["quand_la_regle_dit_large"]["la_part"] >= 1.0, str(e["quand_la_regle_dit_large"]))
    v("★★★★ et quand elle dit ÉTROIT, l'instrument ne dit JAMAIS large",
      e["quand_la_regle_dit_etroit"]["la_part"] <= 0.0, str(e["quand_la_regle_dit_etroit"]))
    v("★★★★ les deux régimes sont DÉRIVÉS de la règle, pas posés",
      e["le_serpentement_dune_bande_calme_en_voxels"] < 1.0
      and e["le_serpentement_dune_bande_agitee_en_voxels"] > 1.0,
      f"{e['le_serpentement_dune_bande_calme_en_voxels']} contre "
      f"{e['le_serpentement_dune_bande_agitee_en_voxels']}")
    v("★★★ l'étalon sépare", e["letalon_separe"])
    facile = la_part_qui_ameliore(20, 109, 128, 0.001, 0.01, 31, 6, [2, 64])
    v("★★★★ sur une matière que les DEUX largeurs lisent parfaitement, élargir n'apporte rien",
      facile["la_part"] <= 0.0, str(facile))

    # ⚠⚠⚠ LA FIXTURE EST CONTINUE A TRAVERS LA COUTURE, ET SES RANGEES PARTAGENT LA PROFONDEUR.
    fx = une_rangee_a_bande(6, 109, 32, 0.3, 0.2, 5)
    pr = fx["les_profondeurs"]
    sauts = [abs(float(pr[k * 32 + 31] - pr[(k + 1) * 32])) for k in range(5)]
    v("★★★★ la profondeur est CONTINUE d'un chunk au suivant — pas de dent de scie à la couture",
      max(sauts) < 2.0, f"saut maximal {round(max(sauts), 3)} voxel")
    v("★★★ et la dérive par couture SUIT du serpentement, elle n'est pas posée à côté",
      abs(fx["la_derive_par_couture_en_voxels"] - round(0.3 * (32 ** 0.5), 4)) < 1e-9,
      str(fx["la_derive_par_couture_en_voxels"]))
    v("★★★★ la fixture rend bien DEUX rangées, et elles DIFFÈRENT — sinon leur désaccord serait "
      "nul par construction et ne mesurerait aucun aléa",
      len(fx["les_rangees"]) == 2
      and float(np.max(np.abs(fx["les_rangees"][0][0]
                              - fx["les_rangees"][-1][0]))) > 0.0,
      f"{len(fx['les_rangees'])} rangée(s)")

    # ⚠⚠ LE VERDICT NE TIENT QU'A L'EPREUVE DECLAREE.
    v("★★★★ la règle de `198` tient quand la recherche la nomme elle-même",
      juger({"decidable": True, "la_largeur_nommee": 16},
            {"la_largeur_de_198": 16}, {}, {})["la_regle_de_198_tient"])
    v("★★★★ et elle tombe quand une autre largeur fait mieux sur des coutures réservées",
      not juger({"decidable": True, "la_largeur_nommee": 32},
                {"la_largeur_de_198": 16, "la_nommee_fait_mieux": True}, {},
                {})["la_regle_de_198_tient"])
    v("★★★ mais une largeur nommée qui NE confirme PAS ne la fait pas tomber",
      juger({"decidable": True, "la_largeur_nommee": 32},
            {"la_largeur_de_198": 16, "la_nommee_fait_mieux": False}, {},
            {})["la_regle_de_198_tient"])

    meta = {"chunks": [109, 8, 8], "shape": [109, 24, 40]}
    v("★★★ un volume qui ne répond pas est refusé, jamais deviné",
      not la_ligne({"cle": "x", "segment": "s"}, 0.0, None,
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
