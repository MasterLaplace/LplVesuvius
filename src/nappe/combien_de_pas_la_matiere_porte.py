#!/usr/bin/env python3
"""Combien de pas la MATIERE porte-t-elle ? — la question du graal, posee sans aucun maillage.

⚠⚠⚠ POURQUOI CE FICHIER, ET C'EST LE GRAAL EN UNE PHRASE. `99` rend le PAS que la matiere
montre, `101` rend la DIRECTION. Les deux ensemble sont exactement ce qu'un automate doit savoir
pour franchir une feuille : *avance de p(matiere) le long de n(matiere)*. Mais derouler n'est pas
faire UN pas, c'est les ENCHAINER — et la question qui decide est *au bout de combien de pas la
matiere cesse-t-elle de confirmer*. Le prix tolere huit heures d'humain la ou l'etat de l'art en
depense 775 sur la correction du transfert de spire a spire ; ce fichier mesure jusqu'ou on va
sans lui.

⭐⭐⭐ ET IL N'Y A AUCUN REFERENT HUMAIN DANS LA BOUCLE. La direction vient du tenseur de structure
(`101`), le pas vient du balayage calibre (`99`), et la verification vient du critere de `98` —
brillant-sombre-brillant sur exactement un interstice. Les quatre candidats de `94` a `97` ont
tous ete fermes parce qu'ils se calibraient contre un maillage dont `97` a mesure qu'il n'a pas
de valeur unique. Ici le maillage ne sert qu'a dire OU COMMENCER.

⚠⚠ LES DEUX SEULS BITS DE SUPERVISION SONT DECLARES. (1) La cellule de DEPART vient du maillage :
un automate reel la recevrait d'une graine, et `77` a mesure que les graines publiees existent.
(2) Le SENS — vers l'exterieur du rouleau — est fixe UNE FOIS au premier pas, parce que le signe
d'un vecteur propre est arbitraire ; le choisir a chaque pas en regardant la cible reviendrait a
souffler la route au marcheur. C'est la regle que `derouler_par_le_pas_normal` a etablie, reprise
telle quelle.

⭐⭐⭐ LE LECTEUR EST UN SEAM, ET C'EST LA DECISION QUI REND LA FIXTURE UTILE. Le marcheur ne
connait qu'un objet qui sait `lire(points)` et `dans_le_volume(points)`. Le MEME marcheur tourne
donc sur un volume FABRIQUE dont on connait la reponse et sur le vrai volume fin. Sans ce seam, la
fixture testerait un autre code que la mesure — et une fixture qui n'exerce pas le chemin reel ne
prouve rien.

⚠⚠ « SORTI DU VOLUME » ET « PERDU LA FEUILLE » SONT DEUX FINS DIFFERENTES, et les confondre
ferait passer un bord de champ pour un echec de la matiere. Elles sont comptees a part.

⭐⭐ LE TEMOIN EST L'AUTOMATE NAIF : avancer du pas NOMINAL le long du RAYON, ce que ferait un
derouleur qui n'interroge pas la matiere. `100` a mesure que le rayon est a 34° de la nappe et
`99` que le pas nominal se trompe de 15 a 24 %, donc le temoin doit degrader — et s'il ne
degradait pas, la mesure ne dirait rien de la matiere.

Usage :
    uv run python src/nappe/combien_de_pas_la_matiere_porte.py --verifier
    uv run python src/nappe/combien_de_pas_la_matiere_porte.py \\
        --json docs/mesures/combien_de_pas_la_matiere_porte.json
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

ALIGNEMENT = RACINE / "docs" / "mesures" / "deux_modes_dechec_du_transfert.json"
CONTINUITE = RACINE / "docs" / "mesures" / "la_continuite_des_transferts.json"

# ⚠ Le nombre de pas n'est pas choisi pour que le resultat passe : c'est ce que le budget de
# lecture permet. Chaque pas coute un cube (41³ voxels, ~1681 plages recollees) plus un segment
# emboite (146 points), donc huit pas par cellule est le plus loin qu'on aille en une heure de
# reseau. Un rouleau entier en demande 31 spires ; ce fichier mesure la PENTE, pas le total.
PAS_MAX = 8
CELLULES_PAR_BANDE = 6
DEMI = 20


class VolumeFabrique:
    """Un volume ANALYTIQUE : une pile de feuilles planes d'obliquite et de pas CONNUS.

    ⭐⭐⭐ ELLE PORTE L'ARGUMENT DU FICHIER, donc elle est dans le module et pas dans la batterie.
    Sur des donnees reelles on ne sait pas ou est la reponse : un marcheur qui survit dix pas
    pourrait suivre la matiere ou tourner en rond dans le bruit. Ici l'empilement est connu, donc
    le marcheur peut ECHOUER — et le temoin naif DOIT echouer des que l'obliquite n'est pas nulle.

    ⚠ Elle expose exactement l'interface du vrai lecteur (`lire`, `dans_le_volume`), ce qui est ce
    qui fait tourner le MEME marcheur sur les deux.
    """

    def __init__(self, pas_um: float, obliquite_deg: float = 0.0, voxel_um: float = 2.4,
                 bruit: float = 0.0, graine: int = 3, forme=(4000, 4000, 4000)) -> None:
        self.pas_um = float(pas_um)
        self.obliquite_deg = float(obliquite_deg)
        self.voxel_um = float(voxel_um)
        self.bruit = float(bruit)
        self.forme = tuple(int(x) for x in forme)
        self._r = np.random.default_rng(graine)
        th = np.deg2rad(obliquite_deg)
        # ⚠ La normale de l'empilement fait `obliquite` avec l'axe x, DANS le plan (y, x) : c'est
        # l'obliquite planaire, celle que `100` a mesuree et celle qu'un rayon confondrait avec
        # une distance inter-feuilles trop grande.
        self.normale = np.array([0.0, np.sin(th), np.cos(th)])
        self.lectures = 0

    def dans_le_volume(self, p: np.ndarray) -> np.ndarray:
        p = np.asarray(p).reshape(-1, 3)
        return np.all((p >= 0) & (p < np.asarray(self.forme)), axis=1)

    def lire(self, points: np.ndarray, fils: int = 1) -> np.ndarray:
        del fils
        p = np.asarray(points, dtype=np.float64).reshape(-1, 3)
        self.lectures += len(p)
        proj = (p @ self.normale) * self.voxel_um
        v = 100.0 + 40.0 * np.cos(2 * np.pi * proj / self.pas_um)
        if self.bruit:
            v = v + self._r.normal(0.0, self.bruit, len(v))
        return v


def direction_de_la_matiere(lecteur, centre_fin: np.ndarray, demi: int = DEMI,
                            fils: int = 32) -> tuple[np.ndarray | None, float, float]:
    """La direction locale de l'empilement, lue dans un cube autour du point — et sa garde.

    Rend (direction en (z, y, x), desaccord des deux moities en degres, planarite). La direction
    est None quand le cube sort du volume ou qu'une lecture manque : « on ne sait pas » et « la
    matiere n'a pas d'orientation » sont deux etats differents.
    """
    from la_direction_que_la_matiere_montre import (accord_des_moities,  # noqa: PLC0415
                                                     bloc, planarite,
                                                     tenseur_de_structure)

    pts = bloc(centre_fin, demi)
    if not lecteur.dans_le_volume(pts).all():
        return None, float("nan"), float("nan")
    brut = lecteur.lire(pts, fils=fils)
    if not np.isfinite(brut).all():
        return None, float("nan"), float("nan")
    n = 2 * demi + 1
    cube = brut.reshape(n, n, n)
    desaccord, direction = accord_des_moities(cube)
    _, valeurs = tenseur_de_structure(cube)
    return direction, desaccord, planarite(valeurs)


def pas_que_la_matiere_dicte(lecteur, p_fin: np.ndarray, direction_fin: np.ndarray,
                             longueurs: np.ndarray, mu: np.ndarray, sd: np.ndarray,
                             voxel_fin_um: float, fils: int = 32,
                             selecteur: str = "calibre", barre: float | None = None) -> dict:
    """La longueur que la matiere accorde le mieux le long de cette direction, et son score.

    ⭐⭐ LE BALAYAGE EST CELUI DE `99`, IMPORTE ET NON RECOPIE — meme fenetre, meme nul par
    candidat, meme rejet des butees. Seule la DIRECTION change ici, ce qui est la seule facon que
    la comparaison entre le marcheur et le naif porte sur la direction et sur rien d'autre.

    ⚠⚠⚠ `selecteur` EXISTE PARCE QUE `105` A TROUVE CELUI DE PRODUCTION BIAISE HAUT — il lit un
    cran trop haut, soit +18,4 % sur le vrai volume. Le defaut vaut `"calibre"`, donc AUCUN chiffre
    deja publie ne bouge ; `"deux_roles"` prend le selecteur corrige, ou le calibre GARDE et le brut
    CHOISIT parmi les admis. Un second `pas_que_la_matiere_dicte` aurait ete deux implementations
    d'un meme pas, libres de ne pas s'accorder — la duplication que ce depot paie en boucle.
    """
    import le_pas_que_la_matiere_montre as M  # noqa: PLC0415

    n_long = M.ECHANTILLONS * M.SUR_ECHANTILLONNAGE
    pas_vx = float(longueurs[-1]) / voxel_fin_um
    t = np.linspace(0.0, 1.0, n_long)
    seg = p_fin[None, :] + direction_fin[None, :] * (pas_vx * t)[:, None]
    zyx = np.rint(seg).astype(np.int64)
    if not lecteur.dans_le_volume(zyx).all():
        return {"sortie": True}
    v = lecteur.lire(zyx, fils=fils)
    if not np.isfinite(v).all():
        return {"sortie": True}
    profs = M.profils_emboites(v.reshape(1, n_long), longueurs)
    if selecteur == "calibre":
        lu, sc, k, sur = M.pas_montre_calibre(profs, longueurs, mu, sd)
    else:
        from le_balayage_rend_il_le_pas_injecte import choisir  # noqa: PLC0415
        if barre is None:
            raise ValueError("le sélecteur corrigé demande la barre du nul calibré")
        lu, sc, k, sur = choisir(profs, longueurs, mu, sd, selecteur, barre)
    return {"sortie": False, "pas_um": float(lu[0]), "score": float(sc[0]),
            "indice": int(k[0]),
            "en_butee": bool(M.touche_un_bord(k, len(longueurs))[0]),
            "part_sur_la_feuille": bool(sur[0])}


def traverse_un_interstice(lecteur, p_fin: np.ndarray, direction_fin: np.ndarray,
                           avance_um: float, voxel_fin_um: float,
                           fils: int = 32) -> dict:
    """Le pas qui vient d'etre decide traverse-t-il EXACTEMENT UN interstice ?

    ⭐⭐⭐ C'EST LA VERIFICATION, ET ELLE A REMPLACE LE BALAYAGE POUR UNE RAISON MESUREE. Ma
    premiere version verifiait avec le BALAYAGE de `99`, qui cherche la meilleure periode le long
    de la direction donnee. Sur un empilement oblique de 35°, la periode le long du RAYON vaut
    pas / cos(35°) = 211 µm — dans la fenetre de recherche — donc le balayage la trouve et
    CONFIRME. L'automate naif passait ainsi les huit pas : mesure, 8 sur 8 la ou il devait
    echouer.

    ⛔⛔ C'ETAIT UNE VERIFICATION INCAPABLE D'ECHOUER, le peche nº 1 de ce depot, et sous sa forme
    la plus sournoise : elle testait « la matiere est-elle feuilletee ici » — ce qui est vrai
    partout — et non « le pas a-t-il franchi UNE feuille », qui est la seule question.

    ⭐⭐ LA BONNE VERIFICATION EST A GABARIT FIXE, sur le segment REELLEMENT parcouru : le profil
    sur `avance_um` doit valoir brillant-sombre-brillant, c'est-a-dire exactement un interstice au
    sens de `98`. Un pas trop court n'en traverse pas un entier, un pas trop long en traverse
    deux, et aucun des deux ne peut se faire passer pour l'autre parce que rien n'est cherche.

    ⚠ Les DEUX roles sont donc separes, et ils doivent l'etre : `99` DECIDE de combien avancer,
    `98` VERIFIE ce que l'avance a traverse. Les confondre est ce qui rendait la mesure muette.
    """
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    pas_vx = float(avance_um) / voxel_fin_um
    t = np.linspace(0.0, 1.0, C.ECHANTILLONS)
    seg = p_fin[None, :] + direction_fin[None, :] * (pas_vx * t)[:, None]
    zyx = np.rint(seg).astype(np.int64)
    if not lecteur.dans_le_volume(zyx).all():
        return {"sortie": True}
    v = lecteur.lire(zyx, fils=fils)
    if not np.isfinite(v).all():
        return {"sortie": True}
    combien, sur, score, marge = C.accord(v.reshape(1, -1))
    # ⭐⭐⭐ ET LA FRACTION CONTINUE, AJOUTEE PAR `104` : la famille de gabarits de `98` est
    # {1, 2, 3}, donc `combien` ne descend JAMAIS sous un et le compteur est AVEUGLE A UN RETARD —
    # un segment ne franchissant que 0,82 feuille rend « 1 interstice » au score 0,781. La famille
    # CONTINUE rend la fraction, donc elle peut valoir moins de un, et elle s'accumule en registre.
    # ⚠ Elle ne remplace PAS `accord` pour la garde : chaque famille porte la barre de sa forme.
    frac, sc_c, butee = C.feuilles_franchies(v.reshape(1, -1))
    return {"sortie": False, "interstices": int(combien[0]),
            "part_sur_la_feuille": bool(sur[0]),
            "accord": float(score[0]), "marge": float(marge[0]),
            "feuilles_franchies": (float(frac[0]) if np.isfinite(frac[0]) else None),
            "score_continu": (float(sc_c[0]) if np.isfinite(sc_c[0]) else None),
            "fraction_en_butee": bool(butee[0])}


def marcher(lecteur, depart_fin: np.ndarray, direction0: np.ndarray, longueurs: np.ndarray,
            mu: np.ndarray, sd: np.ndarray, barre: float, barre_moities: float,
            barre_interstice: float, voxel_fin_um: float, pas_max: int = PAS_MAX,
            demi: int = DEMI, interroge_la_matiere: bool = True,
            pas_impose_um: float | None = None, direction_imposee=None,
            fils: int = 32, selecteur: str = "calibre",
            barre_du_selecteur: float | None = None,
            fenetre_locale: bool = False, arret_sur_vide: bool = False) -> list[dict]:
    """Enchainer les pas, et rendre a CHAQUE pas si la matiere confirme encore.

    ⭐⭐⭐ C'EST LE MARCHEUR, ET IL N'A BESOIN D'AUCUN MAILLAGE. `interroge_la_matiere` a False
    donne le TEMOIN NAIF : direction imposee, pas impose, et la meme verification. Le temoin
    partage donc tout sauf ce qu'on teste.

    ⚠⚠ LE SENS EST FIXE UNE FOIS. Le signe d'un vecteur propre est arbitraire, donc a chaque pas
    la direction lue est retournee pour CONTINUER dans le sens du pas precedent. Le choisir en
    regardant la cible reviendrait a souffler la route.

    ⭐⭐⭐⭐ `fenetre_locale` FAIT SUIVRE A LA FENETRE L'ESPACEMENT MESURE, ET C'EST LE DESSIN QUE
    `121` A RENDU GRATUIT. `117` mesure que 63 pas voyants sur 382 sont refuses parce que l'optimum
    tombe au bord de la fenetre, `118` que les deux bouts sont de VRAIS pas (80,7 et 380,2 µm) et
    que la variation n'est pas radiale — donc qu'il faut une mesure locale. `121` mesure que
    RECENTRER la fenetre laisse le nul par candidat inchange a 2,6e-16 pres, parce qu'il ne depend
    que des RAPPORTS des longueurs a la plus longue. La fenetre peut donc suivre l'espacement sans
    qu'on recalibre quoi que ce soit.

    ⚠⚠ ET LA LARGEUR NE BOUGE PAS, C'EST LA CONDITION. `121` mesure qu'ELARGIR deplace le nul de
    1,2 sigma pour [0,3 ; 3,0], alors que le score calibre vaut `(score - mu)/sd` : garder la barre
    publiee sur une fenetre elargie remettrait le biais vers les courts que `nul_par_candidat`
    existe pour tuer. La fenetre recue est donc VERIFIEE etre celle de la calibration, et un
    refus vaut mieux qu'une barre fausse.

    ⚠ L'espacement suivi est celui du pas PRECEDENT, deduit comme `118` le fait — `avance /
    feuilles franchies` — et seulement quand la fraction n'est pas elle-meme en butee, parce qu'un
    rapport de deux bornes n'est une mesure de rien. Le premier pas garde donc la fenetre nominale.

    ⭐⭐ `arret_sur_vide` ARRETE LA MARCHE AU PREMIER PAS AVEUGLE. `116` mesure que la cecite est
    ABSORBANTE — aucune des 11 marches qui cessent de lire ne relit, la ou un tirage au hasard en
    ferait relire sept — donc s'arreter ne coute rien. Le defaut reste FAUX pour que rien de deja
    publie ne bouge : en faire le defaut changerait ce que toute marche mesure, ce qui est la
    question de `R4-P20` et pas une retouche.

    ⚠ « plus rien a lire » est un troisieme motif d'arret, distinct de « sortie du volume » : un
    bord de champ et un volume qui ne repond plus ne se reparent pas pareil.
    """
    p = np.asarray(depart_fin, dtype=np.float64).copy()
    sens = np.asarray(direction0, dtype=np.float64).copy()
    sens = sens / max(np.linalg.norm(sens), 1e-12)
    etapes = []
    parcouru = 0.0
    # ⚠⚠ LA GARDE DE `121`, et elle refuse plutot que de recalibrer en douce : la fenetre recue
    # doit etre EXACTEMENT celle sur laquelle `mu` et `sd` ont ete tires, sinon la barre ne lui
    # appartient pas. Recentrer est licite (meme rapports), changer la largeur ne l'est pas.
    nominal_um = None
    if fenetre_locale:
        import le_pas_que_la_matiere_montre as _M  # noqa: PLC0415

        nominal_um = float(longueurs[-1]) / _M.FACTEUR_HAUT
        if not np.allclose(_M.candidats_de_pas(nominal_um), longueurs, rtol=1e-9, atol=1e-9):
            raise ValueError(
                "fenetre_locale exige la fenetre de la calibration : la fenetre recue n'est pas "
                f"candidats_de_pas({nominal_um:.3f}), donc `mu`/`sd` ne lui appartiennent pas")
    espacement_um = None
    for k in range(1, pas_max + 1):
        if interroge_la_matiere:
            d, desaccord, pl = direction_de_la_matiere(lecteur, p, demi, fils)
            if d is None:
                etapes.append({"pas": k, "fin": "sortie du volume"})
                break
            # ⚠ Retourner pour CONTINUER, jamais pour viser : le seul bit de supervision est le
            # sens initial, et il a ete fixe hors de cette boucle.
            if float(d @ sens) < 0.0:
                d = -d
            # ⚠⚠⚠ LA PLANARITE EST CONSULTEE, ET C'EST LA REPARATION DE `R4-P23`. Le drapeau
            # ne lisait que le desaccord des deux moities — or deux moities de RIEN ne peuvent
            # pas etre en desaccord : sur un cube constant l'angle vaut exactement 0,00°, donc il
            # passe n'importe quelle barre. `115` a compte le resultat : 178 pas aveugles sur 178
            # declares `oriente`, c'est-a-dire la confiance maximale exactement la ou le marcheur
            # ne lit rien.
            #
            # ⚠⚠ LA GARDE EXISTAIT DEJA, ECRITE ET TESTEE, ET PERSONNE NE L'APPELAIT.
            # `planarite` documente que « le cas degenere doit etre DETECTE, pas repondu » et rend
            # exactement 0,0 sur un tenseur nul ; sa batterie asserte meme que « sa direction
            # reste finie, donc SEULE LA PLANARITE PEUT L'ECARTER ». C'etait un contrat avec un
            # consommateur qui n'a jamais existe.
            #
            # ⚠⚠ ET C'EST UN TEST DE DEGENERESCENCE, JAMAIS UN SEUIL. `accord_des_moities` mesure
            # qu'a sigma 15 pour 40 d'amplitude la direction est bonne a 2,50° pendant que la
            # planarite vaut 0,344, c'est-a-dire AU niveau du bruit pur : fermer sur une barre de
            # planarite supprimerait ce que la garde doit laisser passer. Seul l'exactement nul
            # est refuse, et il ne peut venir que d'un tenseur nul.
            rien_lu = not (np.isfinite(pl) and pl > 0.0)
            oriente = bool(np.isfinite(desaccord) and desaccord < barre_moities and not rien_lu)
            if rien_lu and arret_sur_vide:
                etapes.append({"pas": k, "fin": "plus rien a lire"})
                break
        else:
            d = np.asarray(direction_imposee, dtype=np.float64)
            d = d / max(np.linalg.norm(d), 1e-12)
            if float(d @ sens) < 0.0:
                d = -d
            # ⚠ Le temoin naif n'interroge pas la matiere, donc il n'a rien a declarer aveugle :
            # `rien_lu` y est faux par construction et non par mesure, et le dire evite de lire
            # plus tard un temoin comme une marche voyante.
            desaccord, pl, oriente, rien_lu = float("nan"), float("nan"), True, False
        # ⭐⭐ DEUX ROLES SEPARES : `99` DECIDE de combien avancer, `98` VERIFIE ce que l'avance
        # a traverse. Le temoin naif ne demande pas au premier — il avance du pas nominal — mais
        # il subit exactement le meme second.
        echelle = 1.0
        if pas_impose_um is not None:
            avance_um = float(pas_impose_um)
            r = {"sortie": False, "pas_um": avance_um, "score": float("nan"),
                 "en_butee": False}
        else:
            # ⚠⚠ `selecteur` DEFAUTE A `"calibre"`, donc aucune marche deja publiee ne bouge ;
            # `"deux_roles"` prend le selecteur que `105` a corrige. Un second `marcher` aurait ete
            # deux implementations d'une meme marche, libres de ne pas s'accorder.
            # ⭐⭐⭐ La fenetre suit l'espacement du pas precedent, a largeur constante. `mu` et
            # `sd` sont reutilises TELS QUELS, et c'est `121` qui l'autorise.
            if fenetre_locale and espacement_um is not None and nominal_um:
                echelle = float(espacement_um) / nominal_um
            lg = longueurs if echelle == 1.0 else longueurs * echelle
            r = pas_que_la_matiere_dicte(lecteur, p, d, lg, mu, sd, voxel_fin_um, fils,
                                         selecteur=selecteur, barre=barre_du_selecteur)
            if r.get("sortie"):
                etapes.append({"pas": k, "fin": "sortie du volume"})
                break
            avance_um = r["pas_um"]
        w = traverse_un_interstice(lecteur, p, d, avance_um, voxel_fin_um, fils)
        if w.get("sortie"):
            etapes.append({"pas": k, "fin": "sortie du volume"})
            break
        # ⭐⭐⭐ « LA MATIERE CONFIRME » DEMANDE TROIS CONDITIONS, et chacune ecarte une facon
        # differente de se tromper : le profil doit valoir EXACTEMENT UN interstice (sinon le pas
        # a saute une feuille ou n'en a pas franchi), l'accord doit depasser la barre du bruit pur
        # (sinon la matiere n'a rien dit), et la recherche ne doit pas etre en butee de fenetre
        # (sinon on lit « au moins ceci » comme « ceci »).
        confirme = bool(w["interstices"] == 1
                        and w["accord"] > barre_interstice
                        and not r["en_butee"])
        etapes.append({
            "pas": k,
            "oriente": oriente,
            # ⚠⚠ Le fait est ECRIT plutot que deduit. `115` reconnait un pas aveugle a une
            # conjonction de grandeurs exactement nulles, ce qui marche sur les courses deja
            # gardees ; ce champ le dit a la source, donc une analyse future n'a plus a le
            # deviner — et le jour ou la reparation change ces deux grandeurs, la signature
            # deduite cesserait de matcher en silence.
            "rien_lu": rien_lu,
            "desaccord_des_moities_deg": (round(desaccord, 2)
                                          if np.isfinite(desaccord) else None),
            "planarite": round(pl, 3) if np.isfinite(pl) else None,
            "pas_um": round(float(r["pas_um"]), 1),
            "score_du_balayage": (round(float(r["score"]), 3)
                                  if np.isfinite(r["score"]) else None),
            "interstices_traverses": w["interstices"],
            "accord_de_linterstice": round(w["accord"], 3),
            # ⚠ La fraction CONTINUE voyage avec le compte entier, jamais a sa place : l'un garde
            # (« la matiere a-t-elle repondu »), l'autre mesure (« de combien »).
            "feuilles_franchies": (round(w["feuilles_franchies"], 3)
                                   if w.get("feuilles_franchies") is not None else None),
            "fraction_en_butee": w.get("fraction_en_butee"),
            "en_butee": r["en_butee"], "confirme": confirme,
            "avance_um": round(avance_um, 1),
            # ⚠⚠ LA DIRECTION EST GARDEE, et sans elle le trajet n'est pas reconstructible : `107`
            # doit relire la POLYLIGNE reellement parcourue pour compter les feuilles franchies sur
            # l'ensemble, ce qui est la seule forme NON tautologique du registre. Une droite entre
            # les deux bouts couperait au travers et compterait autre chose.
            "direction": [round(float(x), 6) for x in d],
            "parcouru_um": round(parcouru + avance_um, 1),
            # ⚠ L'echelle de la fenetre est ECRITE a chaque pas, meme quand elle vaut un : sans
            # elle, une re-course a fenetre locale serait indistinguable d'une course nominale
            # dans son propre registre, et l'experience ne pourrait pas etre auditee.
            "echelle_de_la_fenetre": round(float(echelle), 4),
        })
        # ⚠⚠ L'espacement suivi vient de `118` — `avance / feuilles franchies` — et il est REFUSE
        # quand la fraction est elle-meme en butee : un rapport de deux bornes n'est une mesure de
        # rien. Le refus garde l'espacement PRECEDENT plutot que d'en inventer un, donc la fenetre
        # ne saute pas sur un pas injugeable.
        if fenetre_locale:
            f_ = w.get("feuilles_franchies")
            if f_ and not w.get("fraction_en_butee") and np.isfinite(f_) and f_ > 0.0:
                espacement_um = float(avance_um) / float(f_)
        p = p + d * (avance_um / voxel_fin_um)
        parcouru += avance_um
        sens = d
    return etapes


def combien_de_pas_confirmes(etapes: list[dict]) -> int:
    """Combien de pas CONSECUTIFS la matiere a confirmes depuis le depart.

    ⚠⚠ CONSECUTIFS, ET C'EST LE CHIFFRE QUI COMPTE POUR LE GRAAL. Un marcheur qui confirme les
    pas 1, 2 puis 5 a perdu la feuille au pas 3 : tout ce qu'il ecrit ensuite est faux, meme si
    la matiere se remet a repondre plus loin. Compter le TOTAL des pas confirmes surestimerait
    donc exactement ce que l'automate sait faire.
    """
    n = 0
    for e in etapes:
        if e.get("fin") or not e.get("confirme"):
            break
        n += 1
    return n


class VolumeFabriqueAPasVariable(VolumeFabrique):
    """Une pile dont le pas VARIE le long de la normale, avec une phase exacte.

    ⭐⭐⭐ ELLE EXISTE POUR LA FENETRE LOCALE, ET ELLE EST LE SEUL MOYEN DE LA TESTER. Sur une pile
    a pas constant, une fenetre qui suit l'espacement et une fenetre fixe rendent la meme chose :
    le controle serait vert sans rien exercer. Il faut une pile dont l'espacement change SOUS le
    marcheur pour que la fenetre fixe se retrouve en butee et que la locale suive.

    ⚠⚠ LA PHASE EST L'INTEGRALE DE `1/pas`, PAS `proj/pas`. Avec un pas qui varie lineairement,
    `cos(2*pi*proj/pas(proj))` ne rend PAS une pile de pas local `pas(proj)` — elle rend une pile
    dont l'espacement est faux partout sauf a l'origine. L'integrale de `dx/(p0 + k x)` vaut
    `ln(1 + k x / p0)/k`, et c'est elle qui donne une pile dont le pas local est exactement celui
    qu'on demande. La fixture doit etre juste avant que le controle veuille dire quelque chose.
    """

    def __init__(self, pas_depart_um: float, pas_par_um: float, proj0_um: float = 0.0,
                 **kw) -> None:
        super().__init__(pas_depart_um, **kw)
        self.pas_par_um = float(pas_par_um)
        """La variation du pas par micrometre parcouru le long de la normale."""
        self.proj0_um = float(proj0_um)
        """⚠⚠ L'ABSCISSE OU LE PAS VAUT `pas_depart_um`, ET L'OUBLIER REND LA FIXTURE ABSURDE.
        La projection d'un point du volume vaut plusieurs milliers de micrometres — un depart a
        (2000, 2000, 2000) voxels en fait 4800 — donc une pente de 0,05 µm/µm referencee au COIN
        du volume rend un pas NEGATIF la ou le marcheur part. Ma premiere version le faisait, et
        la marche choisissait le plus long candidat a tous les pas sur une pile qui n'avait plus
        de sens. Le chirp a besoin d'une origine, et la seule qui en ait une est le depart."""

    def pas_local_um(self, proj_um: float) -> float:
        """Le pas de la pile a cette abscisse le long de la normale — la reponse connue."""
        return self.pas_um + self.pas_par_um * (float(proj_um) - self.proj0_um)

    def recale(self, depart_vx: np.ndarray) -> np.ndarray:
        """Le depart, glisse sur la feuille la plus proche — en PHASE, pas en `proj / pas`.

        ⚠⚠ Sur une pile a pas variable la phase n'est PAS `proj / pas` : c'est l'integrale de
        `1/pas`. Recaler sur des multiples du pas de depart laisse donc le marcheur entre deux
        feuilles des que la pile s'ecarte de son pas initial, et le controle mesurerait sa propre
        erreur de mise en place — le defaut que `controle_fabrique` documente deja.
        """
        pr = float(np.asarray(depart_vx, dtype=np.float64) @ self.normale) * self.voxel_um
        k = self.pas_par_um
        u = pr - self.proj0_um
        phase = u / self.pas_um if abs(k) < 1e-12 else np.log(
            max(1.0 + k * u / self.pas_um, 1e-9)) / k
        cible = float(np.round(phase))
        v = cible * self.pas_um if abs(k) < 1e-12 else (np.exp(cible * k) - 1.0) * self.pas_um / k
        return np.asarray(depart_vx, dtype=np.float64) + self.normale * (
            (self.proj0_um + v - pr) / self.voxel_um)

    def lire(self, points: np.ndarray, fils: int = 1) -> np.ndarray:
        del fils
        q = np.asarray(points, dtype=np.float64).reshape(-1, 3)
        self.lectures += len(q)
        u = (q @ self.normale) * self.voxel_um - self.proj0_um
        k = self.pas_par_um
        if abs(k) < 1e-12:
            phase = u / self.pas_um
        else:
            # ⚠ `maximum` : sous un pas nul la pile n'a plus de sens, et un log de negatif
            # rendrait un NaN que le marcheur lirait comme une lecture manquante.
            phase = np.log(np.maximum(1.0 + k * u / self.pas_um, 1e-9)) / k
        v = 100.0 + 40.0 * np.cos(2 * np.pi * phase)
        if self.bruit:
            v = v + self._r.normal(0.0, self.bruit, len(v))
        return v


def plafond_pour_traverser(rayon_min_mm: float, rayon_max_mm: float,
                           espacement_um: float) -> int:
    """Combien de pas il faut pour traverser toute l'etendue radiale d'une campagne.

    ⭐⭐⭐ LE PLAFOND D'UNE RE-COURSE EST DERIVE, PAS CHOISI. `113` a leve le plafond de six a
    vingt et 28 marches sur 28 l'ont touche : un plafond qui se choisit est un budget, et il se
    republie en portee. Celui-ci sort de la geometrie — l'etendue a traverser divisee par
    l'espacement d'une feuille — donc il dit combien de transferts le graal demande reellement.

    ⚠ C'est un ORDRE DE GRANDEUR et il le dit : l'espacement varie d'un facteur cinq (`118`), donc
    le compte exact depend du chemin. Le publier comme une valeur exacte serait lire une moyenne
    sur l'axe ou la difference vit.
    """
    if espacement_um <= 0.0:
        raise ValueError("l'espacement doit etre positif")
    etendue_um = (float(rayon_max_mm) - float(rayon_min_mm)) * 1000.0
    if etendue_um <= 0.0:
        raise ValueError("le rayon maximal doit depasser le minimal")
    return int(np.ceil(etendue_um / float(espacement_um)))


def demonstration_fenetre_locale(pas_par_um: float = -0.04, pas_max: int = 26,
                                 demi: int = DEMI) -> dict:
    """Les deux fenetres, sur une pile dont on CONNAIT le pas a chaque profondeur.

    ⭐⭐⭐⭐ ELLE EST DANS LE MODULE ET PAS DANS LA BATTERIE, pour la meme raison que
    `controle_fabrique` : un lecteur doit voir a cote du resultat que la fenetre fixe se met en
    butee la ou la locale ne le fait pas, sinon « recentrer recupere des pas » se lit comme une
    promesse. Ici la reponse est connue a chaque profondeur, donc les deux fenetres peuvent
    ECHOUER.

    ⚠⚠ C'est une demonstration ANALYTIQUE, pas une re-course : elle ne touche aucun volume et ne
    dit rien du vrai rouleau. Ce qu'elle etablit est que le mecanisme fait ce que `R4-P24`
    attend de lui quand l'espacement varie, ce qui est la condition pour que la re-course vaille
    ses heures de lecture.
    """
    import combien_dinterstices_traverses as C  # noqa: PLC0415
    import le_pas_que_la_matiere_montre as M  # noqa: PLC0415

    longueurs = M.candidats_de_pas(C.PAS_UM)
    mu, sd = M.nul_par_candidat(longueurs, tirages=300)
    barre = max(x["p99"] for x in M.nul_du_balayage_calibre(longueurs, mu, sd,
                                                            tirages=150).values())
    from la_direction_que_la_matiere_montre import nul_du_tenseur  # noqa: PLC0415

    nul = nul_du_tenseur(tirages=40, demi=demi)
    x_hat = np.array([0.0, 0.0, 1.0])
    depart = np.array([2000.0, 2000.0, 2000.0])
    proj0 = float(depart @ x_hat) * C.VOXEL_FIN_UM
    pile = VolumeFabriqueAPasVariable(C.PAS_UM, pas_par_um, proj0_um=proj0)
    dep = pile.recale(depart)
    out = {"pas_nominal_um": C.PAS_UM, "pas_par_um": float(pas_par_um), "pas_max": pas_max,
           "fenetre": [M.FACTEUR_BAS, M.FACTEUR_HAUT],
           "bout_court_um": round(M.FACTEUR_BAS * C.PAS_UM, 1),
           "bout_long_um": round(M.FACTEUR_HAUT * C.PAS_UM, 1), "marches": {}}
    for nom, locale in (("fenetre_fixe", False), ("fenetre_locale", True)):
        es = [e for e in marcher(pile, dep, x_hat, longueurs, mu, sd, barre,
                                 nul["accord_des_moities_p1_deg"],
                                 max(x["p99"] for x in C.accord_du_bruit_pur(tirages=200).values()),
                                 C.VOXEL_FIN_UM, pas_max=pas_max, demi=demi,
                                 fenetre_locale=locale) if "confirme" in e]
        out["marches"][nom] = {
            "pas": len(es),
            "en_butee": sum(1 for e in es if e["en_butee"]),
            "confirmes": sum(1 for e in es if e["confirme"]),
            "pas_um_min": round(min(e["pas_um"] for e in es), 1) if es else None,
            "echelle_min": round(min(e["echelle_de_la_fenetre"] for e in es), 3) if es else None,
            "parcouru_um": round(es[-1]["parcouru_um"], 1) if es else 0.0,
            "pas_local_final_um": (round(pile.pas_local_um(proj0 + es[-1]["parcouru_um"]), 1)
                                   if es else None)}
    f, l = out["marches"]["fenetre_fixe"], out["marches"]["fenetre_locale"]
    out["la_fenetre_locale_retire_la_butee"] = bool(f["en_butee"] > 0 and l["en_butee"] == 0)
    out["la_fenetre_locale_confirme_plus"] = bool(l["confirmes"] > f["confirmes"])
    out["la_fenetre_locale_descend_sous_le_bout_court"] = bool(
        l["pas_um_min"] is not None and l["pas_um_min"] < out["bout_court_um"])
    return out


def controle_fabrique(longueurs, mu, sd, barre: float, barre_moities: float,
                      barre_interstice: float, pas_max: int = PAS_MAX,
                      demi: int = DEMI, obliquites=(0.0, 35.0)) -> dict:
    """Ce que le marcheur ET le temoin rendent sur des empilements dont on CONNAIT la reponse.

    ⭐⭐⭐ IL EST PUBLIE PLUTOT QU'ASSERTE DANS LA BATTERIE, et la difference compte : un controle
    qui ne vit que dans un `--verifier` n'apparait pas a cote du resultat qu'il rend lisible. Le
    lecteur d'un document doit voir, sur la meme page, que le temoin REUSSIT quand il a raison et
    ECHOUE quand la matiere est oblique — sinon « le naif fait zero » se lit comme un homme de
    paille.

    ⚠ Le depart est recale sur la famille de plans a chaque obliquite : une cellule qui tombe
    entre deux feuilles ne correspond a AUCUNE polarite du gabarit, et le controle mesurerait
    alors sa propre erreur de mise en place — le defaut que la fixture de `100` a paye.
    """
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    x_hat = np.array([0.0, 0.0, 1.0])
    out = {"pas_max": pas_max, "empilements": []}
    for th in obliquites:
        vf = VolumeFabrique(C.PAS_UM, obliquite_deg=float(th))
        dep = np.array([2000.0, 2000.0, 2000.0])
        proj = float(dep @ vf.normale) * C.VOXEL_FIN_UM
        dep = dep + vf.normale * ((round(proj / C.PAS_UM) * C.PAS_UM - proj) / C.VOXEL_FIN_UM)
        mat = marcher(vf, dep, x_hat, longueurs, mu, sd, barre, barre_moities,
                      barre_interstice, C.VOXEL_FIN_UM, pas_max=pas_max, demi=demi)
        naif = marcher(vf, dep, x_hat, longueurs, mu, sd, barre, barre_moities,
                       barre_interstice, C.VOXEL_FIN_UM, pas_max=pas_max, demi=demi,
                       interroge_la_matiere=False, pas_impose_um=C.PAS_UM,
                       direction_imposee=x_hat)
        out["empilements"].append({
            "obliquite_deg": float(th),
            "pas_confirmes_matiere": combien_de_pas_confirmes(mat),
            "pas_confirmes_naif": combien_de_pas_confirmes(naif),
            "pas_lu_median_um": _mediane([e.get("pas_um") for e in mat]),
        })
    # ⭐⭐ LE VERDICT DU CONTROLE, CALCULE : le temoin doit REUSSIR a obliquite nulle — sinon il
    # est casse et son echec ailleurs ne prouve rien — et ECHOUER des qu'elle ne l'est plus.
    droit = next((e for e in out["empilements"] if e["obliquite_deg"] == 0.0), None)
    oblique = next((e for e in out["empilements"] if e["obliquite_deg"] > 0.0), None)
    if droit and oblique:
        out["le_temoin_nest_pas_un_homme_de_paille"] = bool(
            droit["pas_confirmes_naif"] >= pas_max)
        out["lobliquite_seule_fait_echouer_le_temoin"] = bool(
            oblique["pas_confirmes_naif"] < oblique["pas_confirmes_matiere"])
    return out


def _mediane(v) -> float | None:
    v = np.asarray([x for x in v if x is not None and np.isfinite(x)], dtype=np.float64)
    return round(float(np.median(v)), 2) if len(v) else None


def correlation(x, y) -> float:
    """Le coefficient de Pearson, ou 0 si l'un des deux ne varie pas."""
    if len(x) < 3 or np.std(x) == 0 or np.std(y) == 0:
        return 0.0
    return round(float(np.corrcoef(x, y)[0, 1]), 3)


def mesurer(cellules: int = CELLULES_PAR_BANDE, pas_max: int = PAS_MAX, demi: int = DEMI,
            graine: int = 137, bandes_max: int | None = None, fils: int = 32) -> dict:
    """Le marcheur et son temoin naif, sur le vrai volume, bande par bande."""
    import combien_dinterstices_traverses as C  # noqa: PLC0415
    import la_normale_nest_pas_le_rayon as N  # noqa: PLC0415
    from la_normale_nest_pas_le_rayon import avancement  # noqa: PLC0415
    import laxe_est_une_courbe as A  # noqa: PLC0415
    import le_pas_lu_sur_les_transferts as P  # noqa: PLC0415
    import le_pas_que_la_matiere_montre as M  # noqa: PLC0415
    import le_sens_du_rang as R  # noqa: PLC0415
    from la_direction_que_la_matiere_montre import nul_du_tenseur  # noqa: PLC0415
    from transformations_de_volume import (appliquer, appliquer_direction,  # noqa: PLC0415
                                           matrice)
    from voxel_distant import BUCKET, VolumeZarr  # noqa: PLC0415

    m = matrice(C.OBJET, C.VOLUME_DU_MAILLAGE, C.VOLUME_FIN)
    if m is None:
        return {"message": "transformation vers le volume fin absente des métadonnées"}
    try:
        vol = VolumeZarr(f"{BUCKET}/{C.ZARR_FIN}")
    except RuntimeError as e:
        return {"message": f"volume fin injoignable : {e}"}

    al = ({(x["de"], x["a"]): x for x in json.loads(ALIGNEMENT.read_text())["lignes"]}
          if ALIGNEMENT.is_file() else {})
    co = ({(x["de"], x["a"]): x for x in json.loads(CONTINUITE.read_text())["lignes"]}
          if CONTINUITE.is_file() else {})
    longueurs = M.candidats_de_pas(C.PAS_UM)
    mu, sd = M.nul_par_candidat(longueurs)
    barre = max(v["p99"] for v in M.nul_du_balayage_calibre(longueurs, mu, sd).values())
    nul = nul_du_tenseur(demi=demi)
    barre_moities = nul["accord_des_moities_p1_deg"]
    # ⚠ La barre de l'interstice vient du modele nul FABRIQUE de `98` — le p99 du bruit blanc —
    # et non d'un reglage. C'est ce qui rend « la matiere a repondu » verifiable.
    nul_interstice = C.accord_du_bruit_pur()
    barre_interstice = max(v["p99"] for v in nul_interstice.values())

    bandes = R.bandes_du_fragment()[:bandes_max]
    nuages = [n for n in (R.points(x["recente"]) for x in bandes) if n is not None and len(n)]
    if len(nuages) < 2 and len(bandes) >= 2:
        return {"message": "cache incomplet : lancer `le_sens_du_rang --telecharger`"}
    if len(nuages) < 2:
        return {"message": f"l'axe demande au moins deux bandes ; {len(bandes)} demandée(s)"}
    bords, cx, cy, _, _ = A.axe_par_tranche(np.concatenate(nuages))

    depart = time.time()
    lignes = []
    for x in bandes:
        g = P.grille(x["recente"])
        if g is None:
            continue
        a, ok = g
        ind = C.echantillonner(ok, cellules, graine + x["de"])
        if len(ind) < 3:
            continue
        p0 = a[ind[:, 0], ind[:, 1]]
        c0 = N.centre_interpole(p0[:, 2], bords, cx, cy)
        rad = N.direction_radiale(p0, c0)
        rad_fin = appliquer_direction(m, rad)
        departs = appliquer(m, p0)

        marches, temoins = [], []
        for j in range(len(departs)):
            # ⚠ Le sens initial est le RAYON SORTANT, transporte : c'est le bit de supervision
            # declare, et il est le MEME pour le marcheur et pour le temoin.
            sens0 = rad_fin[j]
            marches.append(marcher(vol, departs[j], sens0, longueurs, mu, sd, barre,
                                   barre_moities, barre_interstice, C.VOXEL_FIN_UM,
                                   pas_max, demi, interroge_la_matiere=True, fils=fils))
            # ⭐⭐ LE TEMOIN NAIF : pas NOMINAL, direction RADIALE, MEME verification.
            temoins.append(marcher(vol, departs[j], sens0, longueurs, mu, sd, barre,
                                   barre_moities, barre_interstice, C.VOXEL_FIN_UM,
                                   pas_max, demi, interroge_la_matiere=False,
                                   pas_impose_um=C.PAS_UM, direction_imposee=sens0,
                                   fils=fils))
        d = {"de": x["de"], "a": x["a"],
             "rayon_mm": al.get((x["de"], x["a"]), {}).get("rayon_mm"),
             "continuite": co.get((x["de"], x["a"]), {}).get("rapport_interieur"),
             "cellules": len(departs)}
        for nom, jeu in (("matiere", marches), ("naif", temoins)):
            confirmes = [combien_de_pas_confirmes(e) for e in jeu]
            sorties = sum(1 for e in jeu if e and e[-1].get("fin") == "sortie du volume")
            d[f"pas_confirmes_median_{nom}"] = _mediane(confirmes)
            d[f"pas_confirmes_max_{nom}"] = int(max(confirmes)) if confirmes else 0
            d[f"sorties_du_volume_{nom}"] = int(sorties)
            porte = [e[c - 1]["parcouru_um"] for e, c in zip(jeu, confirmes) if c >= 1]
            d[f"distance_portee_um_{nom}"] = _mediane(porte)
            # ⚠⚠ LE SOUS-ENSEMBLE EST COMPTE A COTE DE SA MEDIANE. La distance portee ne se
            # calcule que sur les cellules qui ont porte AU MOINS un pas, donc une bande peut
            # afficher une mediane de zero pas ET une distance non nulle — deux populations
            # differentes sur la meme ligne. `99` a paye exactement ca en comparant une
            # population filtree a une population brute.
            d[f"cellules_qui_ont_porte_{nom}"] = int(sum(1 for c in confirmes if c >= 1))
            # ⚠⚠⚠ ET LA CENSURE EST COMPTEE : une cellule qui atteint le plafond de pas dit
            # « AU MOINS ceci », pas « ceci ». La publier comme une portee ferait passer une
            # limite de BUDGET pour une limite de MATIERE.
            d[f"cellules_au_plafond_{nom}"] = int(sum(1 for c in confirmes if c >= pas_max))
        d["pas_montre_median_um"] = _mediane(
            [s["pas_um"] for e in marches for s in e if "pas_um" in s])
        d["desaccord_median_deg"] = _mediane(
            [s.get("desaccord_des_moities_deg") for e in marches for s in e])
        lignes.append(d)
        avancement(len(lignes), len(bandes), "bandes", depart)

    out = {"fragment": C.OBJET, "volume_fin": C.VOLUME_FIN,
           "voxel_fin_um": C.VOXEL_FIN_UM, "pas_nominal_um": C.PAS_UM,
           "pas_max": pas_max, "demi_cube_voxels": demi,
           "cote_du_cube_um": round((2 * demi + 1) * C.VOXEL_FIN_UM, 1),
           "cellules_par_bande": cellules,
           "barre_du_balayage": round(float(barre), 3),
           "barre_de_linterstice": round(float(barre_interstice), 4),
           "barre_daccord_des_moities_deg": barre_moities,
           "bandes": len(lignes), "lignes": lignes,
           "controle_fabrique": controle_fabrique(longueurs, mu, sd, barre, barre_moities,
                                                  barre_interstice, pas_max, demi)}
    return agreger(out)


def agreger(r: dict) -> dict:
    """Le verdict, DERIVE des lignes par bande — meme partage que `100` et `101`."""
    lues = [x for x in r["lignes"] if x.get("pas_confirmes_median_matiere") is not None]
    if not lues:
        return r
    mat = [x["pas_confirmes_median_matiere"] for x in lues]
    naif = [x["pas_confirmes_median_naif"] for x in lues
            if x.get("pas_confirmes_median_naif") is not None]
    porte = [x["distance_portee_um_matiere"] for x in lues
             if x.get("distance_portee_um_matiere") is not None]
    ray = [x["rayon_mm"] for x in lues if x.get("rayon_mm") is not None]
    matr = [x["pas_confirmes_median_matiere"] for x in lues if x.get("rayon_mm") is not None]
    rup = [x["continuite"] for x in lues if x.get("continuite") is not None]
    matc = [x["pas_confirmes_median_matiere"] for x in lues
            if x.get("continuite") is not None]
    # ⚠⚠⚠ LA CENSURE SE PUBLIE AVANT LE RESULTAT QU'ELLE BORNE. Une bande dont une cellule
    # atteint le plafond dit « au moins N pas » ; annoncer sa mediane sans dire qu'elle est
    # tronquee ferait passer une limite de BUDGET DE LECTURE pour une limite de MATIERE — le
    # peche que `99` a enregistre sous le nom de butee.
    plafond = r.get("pas_max")
    censurees = sum(1 for x in lues
                    if x.get("pas_confirmes_max_matiere", 0) >= (plafond or 10 ** 9))
    censurees_naif = sum(1 for x in lues
                         if x.get("pas_confirmes_max_naif", 0) >= (plafond or 10 ** 9))
    r["resume"] = {
        "bandes_lues": len(lues),
        "plafond_de_pas": plafond,
        "bandes_dont_une_cellule_atteint_le_plafond": censurees,
        "bandes_dont_une_cellule_atteint_le_plafond_naif": censurees_naif,
        "part_de_bandes_censurees": round(censurees / max(len(lues), 1), 3),
        "la_portee_est_censuree": bool(censurees > 0),
        "pas_confirmes_median_matiere": round(float(np.median(mat)), 2),
        "pas_confirmes_max_matiere": int(max(x["pas_confirmes_max_matiere"] for x in lues)),
        "pas_confirmes_median_naif": (round(float(np.median(naif)), 2) if naif else None),
        "distance_portee_mediane_um": (round(float(np.median(porte)), 1) if porte else None),
        "pas_confirmes_contre_rayon": correlation(matr, ray),
    }
    # ⚠⚠⚠ LE VERDICT NE S'EMET PAS SANS DONNEE DE TEMOIN. `bool(naif and ...)` rendrait FALSE
    # quand la liste est vide, c'est-a-dire « la matiere ne porte pas plus loin » alors que la
    # verite est « le temoin n'a pas tourne » — le meme faux zero que `101` a paye sur une
    # correlation, et il est plus grave ici parce qu'il porte le verdict du fichier.
    if naif:
        r["resume"].update({
            # ⭐⭐⭐ LE VERDICT, CALCULE ET NON REDIGE : interroger la matiere porte-t-il PLUS
            # LOIN qu'un pas nominal le long du rayon ? Si non, l'instrument de `99` et `101` ne
            # sert a rien pour derouler, et il faut le dire.
            "interroger_la_matiere_porte_plus_loin": bool(
                np.median(mat) > np.median(naif)),
            "avantage_en_pas": round(float(np.median(mat)) - float(np.median(naif)), 2),
        })
    else:
        r["resume"]["temoin_naif_a_tourne"] = False
    if len(rup) >= 3:
        r["resume"]["pas_confirmes_contre_continuite"] = correlation(matc, rup)
    else:
        r["resume"]["continuite_jointe"] = False
    return r


def afficher(r: dict) -> int:
    """L'affichage, séparé pour que la batterie puisse le lancer — la leçon de `93`."""
    from la_normale_nest_pas_le_rayon import nombre_ou_absent  # noqa: PLC0415

    if "message" in r:
        print(f"⚠ {r['message']}")
        return 0
    print(f"{r['fragment']} · {r['bandes']} bandes · {r['cellules_par_bande']} cellules · "
          f"jusqu'à {r['pas_max']} pas · cube de {r['cote_du_cube_um']} µm\n")
    print(f"barre du balayage {r['barre_du_balayage']} (écarts-types du nul) · barre de "
          f"l'interstice {r.get('barre_de_linterstice')} (p99 du bruit pur) · les deux moitiés "
          f"du cube\ndoivent s'accorder sous {r['barre_daccord_des_moities_deg']}°\n")
    print(f"{'bande':>10} {'rayon':>6} {'pas MATIÈRE':>12} {'pas NAÏF':>9} "
          f"{'porté µm':>9} {'pas lu µm':>10} {'désacc.':>8} {'sorties':>8}")
    print(f"{'':>10} {'':>6} {'(★ = au plafond, donc « au moins »)':>50}")
    for x in r["lignes"]:
        if x.get("pas_confirmes_median_matiere") is None:
            continue
        marque = "★" if x.get("pas_confirmes_max_matiere", 0) >= r.get("pas_max", 10 ** 9) \
            else " "
        print(f"  w{x['de']:03d}-{x['a']:03d} {nombre_ou_absent(x['rayon_mm']):>6.1f} "
              f"{x['pas_confirmes_median_matiere']:>11.1f}{marque} "
              f"{nombre_ou_absent(x['pas_confirmes_median_naif']):>9.1f} "
              f"{nombre_ou_absent(x['distance_portee_um_matiere']):>9.0f} "
              f"{nombre_ou_absent(x['pas_montre_median_um']):>10.1f} "
              f"{nombre_ou_absent(x['desaccord_median_deg']):>7.1f}° "
              f"{x['sorties_du_volume_matiere']:>8d}")
    s = r.get("resume")
    if not s:
        print("\n⚠ aucune bande marchée")
        return 0
    print(f"\n{'':>30} {'MATIÈRE':>10} {'NAÏF':>10}")
    print(f"{'pas confirmés, médiane':>30} {s['pas_confirmes_median_matiere']:>10.2f} "
          f"{nombre_ou_absent(s['pas_confirmes_median_naif']):>10.2f}")
    if s.get("temoin_naif_a_tourne") is False:
        print("\n⚠ le témoin naïf n'a pas tourné : aucun verdict n'est émis plutôt qu'un "
              "verdict rendu sans comparaison")
        return 0
    if s["interroger_la_matiere_porte_plus_loin"]:
        print(f"\n★★★ INTERROGER LA MATIÈRE PORTE PLUS LOIN QU'UN PAS NOMINAL RADIAL : "
              f"{s['pas_confirmes_median_matiere']:.2f} pas")
        print(f"   contre {s['pas_confirmes_median_naif']:.2f}, soit "
              f"{s['avantage_en_pas']:+.2f} pas d'avantage. Le pas de `99` et la direction")
        print("   de `101` sont donc utilisables ENCHAÎNÉS, pas seulement un par un.")
    else:
        print(f"\n⛔⛔ INTERROGER LA MATIÈRE NE PORTE PAS PLUS LOIN : "
              f"{s['pas_confirmes_median_matiere']:.2f} pas contre")
        print(f"   {nombre_ou_absent(s['pas_confirmes_median_naif']):.2f} pour l'automate naïf. "
              f"Le pas et la direction de la matière ne suffisent")
        print("   donc pas à enchaîner, et il faut le dire plutôt que de publier le cas isolé.")
    cf = r.get("controle_fabrique", {})
    if cf.get("empilements"):
        print(f"\n{'empilement fabriqué':>26} {'MATIÈRE':>10} {'NAÏF':>10}")
        for e in cf["empilements"]:
            print(f"{('obliquité ' + format(e['obliquite_deg'], '.0f') + '°'):>26} "
                  f"{e['pas_confirmes_matiere']:>10d} {e['pas_confirmes_naif']:>10d}")
        if cf.get("le_temoin_nest_pas_un_homme_de_paille"):
            print("   ★★ le témoin RÉUSSIT quand le pas nominal et le rayon sont justes, donc")
            print("      son échec ailleurs vient de l'obliquité et non d'un témoin cassé.")
    if s.get("la_portee_est_censuree"):
        print(f"\n⚠⚠⚠ MAIS LA PORTÉE EST CENSURÉE, ET ÇA SE DIT AVANT LE RÉSULTAT : "
              f"{s['bandes_dont_une_cellule_atteint_le_plafond']} bandes sur "
              f"{s['bandes_lues']}")
        print(f"   ont au moins une cellule qui atteint le plafond de {s['plafond_de_pas']} pas, "
              f"soit {100 * s['part_de_bandes_censurees']:.0f} %. « {s['pas_confirmes_median_matiere']:.2f} pas »")
        print("   est donc une BORNE INFÉRIEURE, pas une valeur : le plafond est un budget de")
        print("   lecture, et le publier comme une limite de matière serait la butée de `99`.")
    if s.get("distance_portee_mediane_um") is not None:
        print(f"\n⚠ distance médiane portée avant de perdre la feuille : "
              f"{s['distance_portee_mediane_um']:.0f} µm, soit "
              f"{s['distance_portee_mediane_um'] / r['pas_nominal_um']:.1f} feuilles nominales.")
        print("   ⚠ Elle est calculée sur les seules cellules qui ont porté AU MOINS un pas,")
        print("   donc une bande peut afficher zéro pas médian et une distance non nulle : ce")
        print("   sont deux populations, et les lire côte à côte sans le dire les confondrait.")
    print(f"\n⚠ « sorti du volume » et « perdu la feuille » sont comptés à part : un bord de "
          f"champ n'est pas un échec de la matière.")
    return 0


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    import combien_dinterstices_traverses as C  # noqa: PLC0415
    import le_pas_que_la_matiere_montre as M  # noqa: PLC0415
    from la_direction_que_la_matiere_montre import nul_du_tenseur  # noqa: PLC0415

    longueurs = M.candidats_de_pas(C.PAS_UM)
    mu, sd = M.nul_par_candidat(longueurs, tirages=300)
    barre = max(x["p99"] for x in M.nul_du_balayage_calibre(longueurs, mu, sd,
                                                            tirages=150).values())
    nul = nul_du_tenseur(tirages=40, demi=DEMI)
    barre_moities = nul["accord_des_moities_p1_deg"]
    barre_interstice = max(x["p99"] for x in C.accord_du_bruit_pur(tirages=200).values())

    # --- le compte de pas CONSECUTIFS, et non le total ------------------------------------
    # ⚠⚠ SANS CETTE DISTINCTION LA MESURE SURESTIME L'AUTOMATE : un marcheur qui perd la feuille
    # au pas 3 ecrit du faux ensuite, meme si la matiere repond de nouveau au pas 5.
    faux = [{"pas": 1, "confirme": True}, {"pas": 2, "confirme": True},
            {"pas": 3, "confirme": False}, {"pas": 4, "confirme": True},
            {"pas": 5, "confirme": True}]
    v("les pas confirmés sont comptés CONSÉCUTIFS, pas en total",
      combien_de_pas_confirmes(faux) == 2, f"{combien_de_pas_confirmes(faux)} pour 4 au total")
    v("... et une sortie du volume arrête le compte",
      combien_de_pas_confirmes([{"pas": 1, "confirme": True},
                                {"pas": 2, "fin": "sortie du volume"}]) == 1)
    v("... et un marcheur qui échoue au premier pas rend zéro",
      combien_de_pas_confirmes([{"pas": 1, "confirme": False}]) == 0)

    # --- le volume fabrique, et il expose l'interface du VRAI lecteur ---------------------
    vf = VolumeFabrique(C.PAS_UM, obliquite_deg=0.0)
    depart = np.array([2000.0, 2000.0, 2000.0])
    v("le volume fabriqué répond `dans_le_volume` comme le vrai lecteur",
      bool(vf.dans_le_volume(depart[None, :])[0])
      and not bool(vf.dans_le_volume(np.array([[0.0, 0.0, 9999.0]]))[0]))
    # ⚠ Le depart doit tomber SUR une feuille, sinon aucune polarite du gabarit ne correspond —
    # c'est le defaut que la fixture de `100` a paye et il vaut ici aussi.
    pas_vx = C.PAS_UM / C.VOXEL_FIN_UM
    depart[2] = round(2000.0 / pas_vx) * pas_vx
    x_hat = np.array([0.0, 0.0, 1.0])

    # === LE MARCHEUR DOIT SURVIVRE SUR UN EMPILEMENT PARFAIT ==============================
    etapes = marcher(vf, depart, x_hat, longueurs, mu, sd, barre, barre_moities,
                     barre_interstice, C.VOXEL_FIN_UM, pas_max=PAS_MAX, demi=DEMI)
    n = combien_de_pas_confirmes(etapes)
    v(f"sur un empilement PARFAIT, le marcheur confirme les {PAS_MAX} pas",
      n == PAS_MAX, f"{n} pas · pas lus {[e.get('pas_um') for e in etapes[:3]]}")
    # ⭐⭐ LE PAS LU OSCILLE D'UN CRAN AUTOUR DU VRAI, ET C'EST AUTO-CORRECTEUR : apres une
    # avance d'un cran trop longue, le segment suivant demarre un cran au-dela de la feuille,
    # donc le meilleur accord est un cran trop COURT et ramene sur la feuille. La quantite juste
    # est donc la MOYENNE sur la marche, pas chaque pas — et elle doit valoir le pas injecte.
    lus = [e["pas_um"] for e in etapes if "pas_um" in e]
    cran = float(longueurs[1] - longueurs[0])
    v("... et chaque pas lu est à un cran du pas injecté",
      all(abs(x - C.PAS_UM) <= cran + 0.1 for x in lus), str(lus))
    v("... et leur MOYENNE vaut le pas injecté, l'oscillation étant auto-correctrice",
      abs(float(np.mean(lus)) - C.PAS_UM) < 0.5 * cran,
      f"{float(np.mean(lus)):.2f} µm pour {C.PAS_UM} injectés")
    # ⭐ Et la distance parcourue doit valoir le nombre de pas fois le pas : un marcheur qui
    # confirme sans avancer confirmerait la meme feuille huit fois.
    v("... et il a réellement AVANCÉ de huit feuilles",
      abs(etapes[-1]["parcouru_um"] - PAS_MAX * C.PAS_UM) < 2.0 * C.PAS_UM,
      f"{etapes[-1]['parcouru_um']:.0f} µm pour {PAS_MAX * C.PAS_UM:.0f} attendus")

    # === LE TEMOIN NAIF DOIT ECHOUER DES QUE L'EMPILEMENT EST OBLIQUE =====================
    # ⭐⭐⭐ C'EST LE CONTROLE QUI DONNE UN SENS AU RESULTAT. Si le naif reussissait aussi bien,
    # interroger la matiere ne servirait a rien — et sur un empilement oblique il ne peut PAS
    # reussir, parce que le pas radial vaut pas / cos(theta) et non pas.
    theta = 35.0
    vo = VolumeFabrique(C.PAS_UM, obliquite_deg=theta)
    dep_o = depart.copy()
    # ⚠ Le depart est recale sur la famille de plans obliques, meme raison que ci-dessus.
    proj = float(dep_o @ vo.normale) * C.VOXEL_FIN_UM
    dep_o = dep_o + vo.normale * ((round(proj / C.PAS_UM) * C.PAS_UM - proj)
                                  / C.VOXEL_FIN_UM)
    mat_o = marcher(vo, dep_o, x_hat, longueurs, mu, sd, barre, barre_moities,
                    barre_interstice, C.VOXEL_FIN_UM, pas_max=PAS_MAX, demi=DEMI)
    naif_o = marcher(vo, dep_o, x_hat, longueurs, mu, sd, barre, barre_moities,
                     barre_interstice, C.VOXEL_FIN_UM, pas_max=PAS_MAX, demi=DEMI,
                     interroge_la_matiere=False, pas_impose_um=C.PAS_UM,
                     direction_imposee=x_hat)
    nm, nn = combien_de_pas_confirmes(mat_o), combien_de_pas_confirmes(naif_o)
    v(f"sur un empilement OBLIQUE à {theta:.0f}°, le marcheur suit la matière",
      nm >= PAS_MAX - 1, f"{nm} pas sur {PAS_MAX}")
    v("... et l'automate NAÏF y perd la feuille, donc le contrôle discrimine",
      nn < nm, f"naïf {nn} contre matière {nm}")
    # ⚠ Et la direction que le marcheur suit doit etre celle de l'empilement, pas le rayon.
    from la_direction_que_la_matiere_montre import angle_entre  # noqa: PLC0415
    d_lue, _, _ = direction_de_la_matiere(vo, dep_o, DEMI)
    v(f"... parce qu'il lit bien la normale de l'empilement ({theta:.0f}° du rayon)",
      abs(angle_entre(d_lue, vo.normale)) < 3.0
      and abs(angle_entre(d_lue, x_hat) - theta) < 3.0,
      f"{angle_entre(d_lue, vo.normale):.2f}° de la normale, "
      f"{angle_entre(d_lue, x_hat):.2f}° du rayon")

    # ⭐⭐⭐ ET LE TEMOIN N'EST PAS UN HOMME DE PAILLE : sur un empilement DROIT, ou le pas
    # nominal ET la direction radiale sont JUSTES, le naif doit REUSSIR. Sans ce controle, son
    # echec sur l'oblique pourrait venir d'un temoin casse plutot que de l'obliquite.
    naif_droit = marcher(vf, depart, x_hat, longueurs, mu, sd, barre, barre_moities,
                         barre_interstice, C.VOXEL_FIN_UM, pas_max=PAS_MAX, demi=DEMI,
                         interroge_la_matiere=False, pas_impose_um=C.PAS_UM,
                         direction_imposee=x_hat)
    v("sur un empilement DROIT, le témoin naïf réussit — ce n'est pas un homme de paille",
      combien_de_pas_confirmes(naif_droit) == PAS_MAX,
      f"{combien_de_pas_confirmes(naif_droit)} pas sur {PAS_MAX}")

    # === ET LE BRUIT NE DOIT PAS FABRIQUER UNE REUSSITE ===================================
    # ⚠⚠ UN VOLUME SANS EMPILEMENT DU TOUT : le marcheur ne doit RIEN confirmer, sinon la
    # mesure serait satisfaite par du bruit.
    class _Bruit:
        def __init__(self, forme=(4000, 4000, 4000), graine=11):
            self.forme = forme
            self._r = np.random.default_rng(graine)

        def dans_le_volume(self, p):
            p = np.asarray(p).reshape(-1, 3)
            return np.all((p >= 0) & (p < np.asarray(self.forme)), axis=1)

        def lire(self, points, fils=1):
            del fils
            return self._r.normal(100.0, 10.0, len(np.asarray(points).reshape(-1, 3)))

    b = marcher(_Bruit(), depart, x_hat, longueurs, mu, sd, barre, barre_moities,
                barre_interstice, C.VOXEL_FIN_UM, pas_max=PAS_MAX, demi=DEMI)
    v("sur du BRUIT PUR, le marcheur ne confirme rien",
      combien_de_pas_confirmes(b) == 0, f"{combien_de_pas_confirmes(b)} pas")

    # === LE VIDE, ET LA REPARATION DE `R4-P23` ===========================================
    # ⚠⚠⚠ Deux moities de RIEN ne peuvent pas etre en desaccord. Sur un cube constant l'angle
    # vaut exactement 0,00°, donc il passe n'importe quelle barre : le drapeau qui ne lisait que
    # ce desaccord declarait `oriente` exactement la ou le marcheur ne lit rien (`115`, 178 sur
    # 178). La garde etait ecrite dans `planarite` et n'avait aucun appelant.
    from la_direction_que_la_matiere_montre import (accord_des_moities as _accord,  # noqa: PLC0415
                                                    planarite as _plan,
                                                    tenseur_de_structure as _tens)
    _cube_vide = np.full((2 * DEMI + 1,) * 3, 137.0)
    _des, _ = _accord(_cube_vide)
    v("un cube constant rend un desaccord EXACTEMENT nul", _des == 0.0, f"{_des}")
    v("... donc il passait n'importe quelle barre", _des < barre_moities)
    v("... et c'est la planarite qui le detecte", _plan(_tens(_cube_vide)[1]) == 0.0)

    class _Vide:
        """Un volume lu, DANS ses bornes, et constant : ni sortie ni lecture manquante."""

        def __init__(self, forme=(4000, 4000, 4000), valeur=137.0):
            self.forme = forme
            self.valeur = valeur

        def dans_le_volume(self, p):
            p = np.asarray(p).reshape(-1, 3)
            return np.all((p >= 0) & (p < np.asarray(self.forme)), axis=1)

        def lire(self, points, fils=1):
            del fils
            return np.full(len(np.asarray(points).reshape(-1, 3)), self.valeur)

    vide = marcher(_Vide(), depart, x_hat, longueurs, mu, sd, barre, barre_moities,
                   barre_interstice, C.VOXEL_FIN_UM, pas_max=4, demi=DEMI)
    pas_vides = [e for e in vide if "confirme" in e]
    v("le vide n'est ni une sortie ni une lecture manquante", len(pas_vides) == 4,
      f"{len(pas_vides)} pas")
    v("⭐ chaque pas y est declare `rien_lu`", all(e["rien_lu"] for e in pas_vides))
    v("⭐ et AUCUN n'est declare `oriente`", not any(e["oriente"] for e in pas_vides))
    v("... ni confirme", not any(e["confirme"] for e in pas_vides))
    # ⚠⚠ LA SONDE SYMETRIQUE, et c'est elle qui compte : la garde ne doit pas supprimer ce
    # qu'elle doit laisser passer. Sur du BRUIT la planarite vaut le niveau du bruit pur, pas
    # zero — fermer sur une barre de planarite aurait ecarte des lectures reelles.
    pas_bruit = [e for e in b if "confirme" in e]
    v("sonde : sur du bruit, aucun pas n'est declare `rien_lu`",
      pas_bruit and not any(e["rien_lu"] for e in pas_bruit),
      f"{sum(1 for e in pas_bruit if e['rien_lu'])}/{len(pas_bruit)}")
    v("... parce que la planarite du bruit n'est pas nulle",
      _plan(_tens(np.random.default_rng(3).normal(100.0, 10.0,
                                                  (2 * DEMI + 1,) * 3))[1]) > 0.0)
    # ⚠⚠ ET LE CONTRASTE EST EPINGLE, PAS RACONTE. `120` publie un tableau vide/bruit ; un chiffre
    # publie dont le calcul n'est pas dans l'arbre est une anecdote, donc les deux valeurs du bruit
    # sont assertees ici avec LEUR graine et LEUR forme. Elles bougeront si l'estimateur change,
    # ce qui est exactement ce qu'une epingle doit faire.
    _b41 = np.random.default_rng(0).normal(size=(41, 41, 41))
    v("un cube de bruit (graine 0, 41³) rend un desaccord franc",
      round(_accord(_b41)[0], 2) == 27.63, f"{round(_accord(_b41)[0], 2)}")
    v("... et une planarite au niveau du bruit pur",
      round(_plan(_tens(_b41)[1]), 3) == 0.337, f"{round(_plan(_tens(_b41)[1]), 3)}")

    # === LA RE-COURSE : FENETRE LOCALE, PLAFOND DERIVE, ARRET SUR VIDE ===================
    # ⚠⚠ Tout ce bloc est HORS LIGNE : des piles analytiques dont on connait la reponse.

    # ⭐⭐ Le plafond est DERIVE de la geometrie, pas choisi.
    v("le plafond derive de l'etendue radiale et de l'espacement",
      plafond_pour_traverser(4.07, 23.8, 177.0) == 112,
      f"{plafond_pour_traverser(4.07, 23.8, 177.0)}")
    v("... et il grandit quand l'espacement retrecit",
      plafond_pour_traverser(4.07, 23.8, 88.5) > plafond_pour_traverser(4.07, 23.8, 177.0))
    for mauvais in ((4.07, 23.8, 0.0), (23.8, 4.07, 177.0)):
        try:
            plafond_pour_traverser(*mauvais)
            v(f"sonde : {mauvais} est refuse", False)
        except ValueError:
            v(f"sonde : {mauvais} est refuse", True)

    # ⭐⭐⭐ La pile a pas variable est JUSTE : son pas local est bien celui qu'elle annonce, ET
    # son origine est celle du depart. ⚠ Sans ces controles, le test de la fenetre locale
    # mesurerait l'erreur de sa propre fixture — ce qu'il a fait a ma premiere version, ou le
    # chirp etait reference au COIN du volume et rendait un pas negatif au depart du marcheur.
    depart_vx = np.array([2000.0, 2000.0, 2000.0])
    proj0 = float(depart_vx @ np.array([0.0, 0.0, 1.0])) * C.VOXEL_FIN_UM
    pv = VolumeFabriqueAPasVariable(173.0, -0.04, proj0_um=proj0)
    v("un chirp NUL rend exactement la pile constante",
      float(np.max(np.abs(VolumeFabrique(173.0).lire(np.array([[2000.0, 2000.0, 2000.0 + i]
                                                               for i in range(64)]))
                          - VolumeFabriqueAPasVariable(173.0, 0.0).lire(
                              np.array([[2000.0, 2000.0, 2000.0 + i] for i in range(64)]))))) < 1e-9)
    v("le pas local au depart est celui qui est declare", pv.pas_local_um(proj0) == 173.0,
      f"{pv.pas_local_um(proj0)}")
    for x in (0.0, 500.0, 1500.0):
        h = 1e-3
        ph = (lambda u: np.log(max(1.0 + pv.pas_par_um * u / pv.pas_um, 1e-9)) / pv.pas_par_um)
        pente = (ph(x + h) - ph(x)) / h
        v(f"la pile a pas variable a le pas annonce a {x:.0f} µm du depart",
          abs(1.0 / pente - pv.pas_local_um(proj0 + x)) < 0.05,
          f"{1.0 / pente:.3f} contre {pv.pas_local_um(proj0 + x):.3f}")
    # ⚠⚠ Le recalage se fait sur la PHASE : sur une feuille la valeur lue est le maximum de la
    # pile. Une cellule entre deux feuilles ne correspond a aucune polarite du gabarit, et le
    # controle mesurerait sa mise en place au lieu du marcheur.
    dep_v = pv.recale(depart_vx)
    v("le recalage pose le depart SUR une feuille",
      abs(float(pv.lire(dep_v.reshape(1, 3))[0]) - 140.0) < 1.0,
      f"{float(pv.lire(dep_v.reshape(1, 3))[0]):.2f}")

    # ⭐⭐⭐⭐ LE CONTROLE DE NON-CHANGEMENT : sur une pile a pas CONSTANT, la fenetre locale ne
    # doit rien deplacer. Elle ne peut pas etre bit-a-bit identique — l'espacement deduit vaut
    # `avance / feuilles franchies` et la fraction porte son propre bruit — donc ce qui est
    # asserte est qu'elle reste sous UN CRAN de la fenetre, et le cran est celui du balayage
    # (0,05 du nominal), pas une tolerance choisie.
    cran = (M.FACTEUR_HAUT - M.FACTEUR_BAS) / (M.CANDIDATS - 1)
    pc = VolumeFabrique(C.PAS_UM)
    dep_c = np.array([2000.0, 2000.0, 2000.0])
    proj_c = float(dep_c @ pc.normale) * C.VOXEL_FIN_UM
    dep_c = dep_c + pc.normale * ((round(proj_c / C.PAS_UM) * C.PAS_UM - proj_c) / C.VOXEL_FIN_UM)
    fixe = marcher(pc, dep_c, x_hat, longueurs, mu, sd, barre, barre_moities, barre_interstice,
                   C.VOXEL_FIN_UM, pas_max=8, demi=DEMI)
    local = marcher(pc, dep_c, x_hat, longueurs, mu, sd, barre, barre_moities, barre_interstice,
                    C.VOXEL_FIN_UM, pas_max=8, demi=DEMI, fenetre_locale=True)
    ech = [e["echelle_de_la_fenetre"] for e in local if "confirme" in e]
    # ⚠⚠ CE QUI EST ASSERTE EST QUE LA FENETRE CONTIENT ENCORE LA VERITE, pas que l'echelle ne
    # bouge pas — et c'est une correction de ma premiere version, qui exigeait « sous un cran » et
    # a echoue a 0,094. La raison est reelle : le marcheur ALTERNE entre deux candidats de part et
    # d'autre du pas vrai (181,7 puis 164,3 sur une pile a 173), donc l'espacement deduit alterne
    # avec lui. Une fenetre qui suit alterne aussi, et ce n'est pas un defaut tant qu'elle
    # continue de contenir le pas vrai.
    v("a pas constant, la fenetre contient encore le pas vrai a chaque pas",
      ech and all(M.FACTEUR_BAS * x <= 1.0 <= M.FACTEUR_HAUT * x for x in ech),
      f"echelles {min(ech):.3f} a {max(ech):.3f}")
    # ⚠ La MEDIANE, elle, doit rester sous un cran : elle est insensible a l'alternance et
    # attraperait une derive systematique, qui serait un vrai defaut.
    v("... et son echelle mediane reste sous un cran",
      ech and abs(float(np.median(ech)) - 1.0) < cran,
      f"{float(np.median(ech)):.4f} contre un cran de {cran:.4f}")
    v("... le premier pas garde la fenetre nominale", ech and ech[0] == 1.0)
    v("... et les deux marches vont aussi loin",
      len([e for e in fixe if "confirme" in e]) == len([e for e in local if "confirme" in e]))

    # ⭐⭐⭐⭐ LE PAYOFF : sur une pile dont le pas passe SOUS le bout court de la fenetre, la
    # fenetre fixe se met en butee et la locale suit. C'est la revendication de `R4-P24`, et sans
    # cette fixture elle ne serait qu'une intention.
    f_v = [e for e in marcher(pv, dep_v, x_hat, longueurs, mu, sd, barre, barre_moities,
                              barre_interstice, C.VOXEL_FIN_UM, pas_max=26, demi=DEMI)
           if "confirme" in e]
    l_v = [e for e in marcher(pv, dep_v, x_hat, longueurs, mu, sd, barre, barre_moities,
                              barre_interstice, C.VOXEL_FIN_UM, pas_max=26, demi=DEMI,
                              fenetre_locale=True) if "confirme" in e]
    butee_fixe = sum(1 for e in f_v if e["en_butee"])
    butee_locale = sum(1 for e in l_v if e["en_butee"])
    v("sur une pile qui retrecit, la fenetre FIXE se met en butee", butee_fixe > 0,
      f"{butee_fixe}/{len(f_v)}")
    v("... et la fenetre LOCALE, non", butee_locale == 0,
      f"{butee_locale} contre {butee_fixe}")
    v("... donc elle confirme plus de pas",
      sum(1 for e in l_v if e["confirme"]) > sum(1 for e in f_v if e["confirme"]),
      f"{sum(1 for e in l_v if e['confirme'])} contre {sum(1 for e in f_v if e['confirme'])}")
    # ⚠ Et elle descend sous le BOUT COURT de la fenetre fixe, ce qui est la revendication : la
    # fenetre globale ne peut pas exprimer ce pas-la, la locale si.
    v("... parce qu'elle a suivi le pas sous le bout court de la fenetre fixe",
      l_v and min(e["pas_um"] for e in l_v) < M.FACTEUR_BAS * C.PAS_UM,
      f"{min(e['pas_um'] for e in l_v):.1f} contre {M.FACTEUR_BAS * C.PAS_UM:.1f}")

    # ⭐⭐ La demonstration publiee doit dire ce que la batterie vient de verifier, sinon le
    # document et le controle parleraient de deux choses.
    demo = demonstration_fenetre_locale()
    v("la demonstration retire la butee", demo["la_fenetre_locale_retire_la_butee"],
      f"{demo['marches']['fenetre_fixe']['en_butee']} → "
      f"{demo['marches']['fenetre_locale']['en_butee']}")
    v("... et confirme plus de pas", demo["la_fenetre_locale_confirme_plus"])
    v("... et descend sous le bout court",
      demo["la_fenetre_locale_descend_sous_le_bout_court"],
      f"{demo['marches']['fenetre_locale']['pas_um_min']} contre {demo['bout_court_um']}")

    # ⚠⚠ LA GARDE DE `121` : une fenetre qui n'est pas celle de la calibration est REFUSEE.
    try:
        marcher(pc, dep_c, x_hat, M.candidats_de_pas(C.PAS_UM, bas=0.3, haut=3.0), mu, sd, barre,
                barre_moities, barre_interstice, C.VOXEL_FIN_UM, pas_max=2, demi=DEMI,
                fenetre_locale=True)
        v("sonde : une fenetre elargie est refusee par fenetre_locale", False)
    except ValueError:
        v("sonde : une fenetre elargie est refusee par fenetre_locale", True)
    v("... alors qu'elle passe sans fenetre_locale",
      len(marcher(pc, dep_c, x_hat, M.candidats_de_pas(C.PAS_UM, bas=0.3, haut=3.0), mu, sd,
                  barre, barre_moities, barre_interstice, C.VOXEL_FIN_UM, pas_max=2,
                  demi=DEMI)) == 2)

    # ⭐⭐ L'ARRET SUR VIDE, et sa symetrique.
    stop = marcher(_Vide(), depart, x_hat, longueurs, mu, sd, barre, barre_moities,
                   barre_interstice, C.VOXEL_FIN_UM, pas_max=6, demi=DEMI, arret_sur_vide=True)
    v("l'arret sur vide stoppe au premier pas aveugle", len(stop) == 1, f"{len(stop)}")
    v("... et le motif est distinct d'une sortie de volume",
      stop[0].get("fin") == "plus rien a lire", f"{stop[0]}")
    v("sonde : sans l'option, la marche continue dans le vide",
      len([e for e in marcher(_Vide(), depart, x_hat, longueurs, mu, sd, barre, barre_moities,
                              barre_interstice, C.VOXEL_FIN_UM, pas_max=6, demi=DEMI)
           if "confirme" in e]) == 6)
    v("... et sur une pile qui repond, l'option ne change rien",
      len([e for e in marcher(pc, dep_c, x_hat, longueurs, mu, sd, barre, barre_moities,
                              barre_interstice, C.VOXEL_FIN_UM, pas_max=4, demi=DEMI,
                              arret_sur_vide=True) if "confirme" in e]) == 4)

    # === LES DONNEES REELLES ==============================================================
    # ⚠ Au moins quatre cellules : la mesure saute une bande qui en garde moins de trois, donc
    # un contrôle à deux cellules rendait « 0 bande », ce qui ressemble à une panne.
    r = mesurer(cellules=4, pas_max=2, demi=8, bandes_max=2)
    if "message" in r:
        print(f"  ⚠ {r['message']} — contrôles sur données réelles sautés")
        print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, "
              f"{controles} checks)")
        return 1 if echecs else 0
    v("la mesure atteint le volume fin", r["bandes"] >= 1, f"{r['bandes']} bandes")
    v("le verdict qui compare la matière au naïf est rendu",
      "resume" in r and "interroger_la_matiere_porte_plus_loin" in r["resume"])
    v("« sorti du volume » est compté à part de « perdu la feuille »",
      all("sorties_du_volume_matiere" in x for x in r["lignes"]))
    # ⚠⚠⚠ LA CENSURE DOIT ETRE PUBLIEE, ET LE VERDICT DOIT SAVOIR LA DETECTER. Sur un plafond
    # volontairement bas (2 pas), une bande qui l'atteint doit etre COMPTEE : sans ce controle,
    # une limite de budget de lecture se publierait comme une limite de matiere.
    v("la censure par le plafond est comptée et publiée",
      "la_portee_est_censuree" in r["resume"]
      and "bandes_dont_une_cellule_atteint_le_plafond" in r["resume"])
    v("... et le sous-ensemble qui a porté est compté à côté de sa distance",
      all("cellules_qui_ont_porte_matiere" in x for x in r["lignes"]))
    # ⭐ Et le compteur doit pouvoir dire NON : un jeu fabrique dont aucune cellule n'atteint le
    # plafond doit rendre « pas censure », sinon le drapeau serait toujours vrai.
    faux = {"pas_max": 6, "lignes": [
        {"de": 1, "a": 2, "rayon_mm": 5.0, "continuite": 1.0,
         "pas_confirmes_median_matiere": 2.0, "pas_confirmes_max_matiere": 3,
         "pas_confirmes_median_naif": 0.0, "pas_confirmes_max_naif": 1,
         "distance_portee_um_matiere": 400.0},
        {"de": 3, "a": 4, "rayon_mm": 9.0, "continuite": 2.0,
         "pas_confirmes_median_matiere": 1.0, "pas_confirmes_max_matiere": 2,
         "pas_confirmes_median_naif": 0.0, "pas_confirmes_max_naif": 0,
         "distance_portee_um_matiere": 200.0},
        {"de": 5, "a": 6, "rayon_mm": 14.0, "continuite": 5.0,
         "pas_confirmes_median_matiere": 3.0, "pas_confirmes_max_matiere": 4,
         "pas_confirmes_median_naif": 1.0, "pas_confirmes_max_naif": 2,
         "distance_portee_um_matiere": 600.0}]}
    v("... et un jeu SANS cellule au plafond est déclaré NON censuré",
      not agreger(faux)["resume"]["la_portee_est_censuree"])
    faux["lignes"][0]["pas_confirmes_max_matiere"] = 6
    v("... alors qu'une seule cellule au plafond suffit à le déclarer",
      agreger(faux)["resume"]["la_portee_est_censuree"]
      and agreger(faux)["resume"]["bandes_dont_une_cellule_atteint_le_plafond"] == 1)
    v("l'affichage tourne sur ce résultat", afficher(r) == 0)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--cellules", type=int, default=CELLULES_PAR_BANDE)
    p.add_argument("--pas", type=int, default=PAS_MAX)
    p.add_argument("--demi", type=int, default=DEMI)
    p.add_argument("--bandes", type=int, default=None)
    p.add_argument("--reagreger", action="store_true")
    # ⚠ La demonstration de la fenetre locale est ANALYTIQUE : elle ne touche aucun volume, donc
    # elle a son propre drapeau plutot que de s'inviter dans une mesure qui, elle, lit le reseau.
    p.add_argument("--demonstration", action="store_true",
                   help="la fenetre fixe contre la fenetre locale, sur une pile a pas connu")
    p.add_argument("--json", type=Path, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if a.demonstration:
        r = demonstration_fenetre_locale()
        f_, l_ = r["marches"]["fenetre_fixe"], r["marches"]["fenetre_locale"]
        print(f"pile a pas variable ({r['pas_par_um']} µm/µm) · fenêtre "
              f"[{r['bout_court_um']} ; {r['bout_long_um']}] µm")
        for nom, m in r["marches"].items():
            print(f"  {nom:<14} {m['pas']:>2} pas · {m['en_butee']:>2} en butée · "
                  f"{m['confirmes']:>2} confirmés · pas min {m['pas_um_min']} µm · "
                  f"échelle min {m['echelle_min']}")
        print(f"  ⭐ la fenêtre locale retire la butée : "
              f"{r['la_fenetre_locale_retire_la_butee']} ({f_['en_butee']} → {l_['en_butee']})")
        if a.json:
            a.json.write_text(json.dumps(r, indent=1, ensure_ascii=False), encoding="utf-8")
            print(f"\nécrit : {a.json}")
        return 0
    if a.reagreger:
        if a.json is None or not a.json.is_file():
            print("⚠ --reagreger demande un --json existant")
            return 1
        r = json.loads(a.json.read_text())
        # ⚠ Le controle fabrique est ANALYTIQUE : il ne touche pas au reseau, donc le
        # recalculer coute quelques secondes et evite qu'une image ecrite avant qu'il n'existe
        # reste sans lui. Les lignes par bande, elles, ne sont jamais retouchees.
        if "controle_fabrique" not in r:
            import combien_dinterstices_traverses as C  # noqa: PLC0415
            import le_pas_que_la_matiere_montre as M  # noqa: PLC0415
            from la_direction_que_la_matiere_montre import (  # noqa: PLC0415
                nul_du_tenseur)

            lo = M.candidats_de_pas(C.PAS_UM)
            mu_, sd_ = M.nul_par_candidat(lo)
            ba = max(x["p99"] for x in M.nul_du_balayage_calibre(lo, mu_, sd_).values())
            bm = nul_du_tenseur(demi=r.get("demi_cube_voxels", DEMI))[
                "accord_des_moities_p1_deg"]
            bi = max(x["p99"] for x in C.accord_du_bruit_pur().values())
            r["controle_fabrique"] = controle_fabrique(
                lo, mu_, sd_, ba, bm, bi, r.get("pas_max", PAS_MAX),
                r.get("demi_cube_voxels", DEMI))
        r = agreger(r)
        afficher(r)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False))
        print(f"\nréagrégé : {a.json}")
        return 0
    r = mesurer(cellules=a.cellules, pas_max=a.pas, demi=a.demi, bandes_max=a.bandes)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False))
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
