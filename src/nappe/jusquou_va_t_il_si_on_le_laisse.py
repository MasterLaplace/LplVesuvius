#!/usr/bin/env python3
"""Jusqu'ou le marcheur va-t-il si on le laisse ? — la portee n'a jamais ete mesuree.

⚠⚠⚠ POURQUOI CE FICHIER, ET LE CONSTAT QUI L'IMPOSE. `107` publie « la matiere porte 1,0 pas
confirme » et le lit comme une portee. Mesure sur ses propres etapes : **56 marches sur 56 ont
atteint le plafond de six pas, zero sortie du volume**. Le marcheur ne s'arrete QUE sur une sortie
— une non-confirmation ne l'interrompt pas, `109` l'a montre et le code le dit. Donc **rien n'a
jamais arrete une marche**, et ce qui a ete publie comme une portee est le compte de pas
consecutifs confirmes, c'est-a-dire une lecture du critere.

⭐⭐⭐ LA PORTEE EST DONC ENTIEREMENT CENSUREE, ET LA SEULE FACON DE LA MESURER EST DE LEVER LE
PLAFOND. Cette tranche refait la marche depuis LES MEMES departs que `107` — la graine et les
cellules sont les siennes — avec un plafond de vingt pas au lieu de six, soit environ quatre
millimetres et demi, l'ordre de grandeur auquel la chaine de `44` tient.

⭐⭐ ET ELLE GARDE TOUT CE QUE LES TRANCHES PRECEDENTES ONT PERDU : le depart (que `107` n'avait pas
ecrit), chaque etape, ET le profil brut de la polyligne (que `110` n'avait pas garde). Deux
tranches ont repaye du reseau pour relire les memes voxels ; celle-ci ne le fera pas faire une
troisieme fois.

⚠⚠ CE QU'ELLE NE PEUT PAS DIRE D'AVANCE : si la matiere s'arrete avant vingt pas, le marcheur ne
le signalera pas en s'arretant — il continuera dans le vide. C'est le REGISTRE et le taux de
confirmation en fonction de la PROFONDEUR qui le diront, et ils sont mesures ici.

Usage :
    uv run python src/nappe/jusquou_va_t_il_si_on_le_laisse.py --verifier
    uv run python src/nappe/jusquou_va_t_il_si_on_le_laisse.py --pas 20 \\
        --json docs/mesures/jusquou_va_t_il_si_on_le_laisse.json
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

CHEMIN_DE_107 = RACINE / "docs" / "mesures" / "le_marcheur_avec_le_bon_pas.json"
# ⚠⚠ VINGT PAS PLUTOT QUE SIX, ET LE CHIFFRE EST DERIVE : vingt pas font environ 4,6 mm a l'avance
# mesuree, c'est-a-dire l'ordre de grandeur auquel `44` mesure que la chaine tient (5,76 mm). Aller
# plus loin couterait proportionnellement sans repondre a une question de plus.
PAS_MAX = 20
SELECTEUR = "deux_roles"
DEMI = 20


def ce_qui_a_arrete_les_marches(brut: dict) -> dict:
    """Qu'est-ce qui a termine chaque marche de `107` ? — le constat qui impose cette tranche.

    ⭐⭐⭐ ELLE EXISTE PARCE QUE LA REPONSE EST « RIEN ». Le marcheur ne s'interrompt que sur une
    sortie du volume ; une non-confirmation ne l'arrete pas. Si toutes les marches atteignent le
    plafond, la portee publiee n'est pas une portee mais un budget, et la distinction change ce
    que « la matiere porte deux pas » veut dire.
    """
    plafond = int(brut.get("pas_max") or 0)
    pas, sorties, longueurs = [], 0, []
    for ligne in brut.get("lignes", []):
        for cel in ligne.get("detail", []):
            for sel in ("calibre", "deux_roles"):
                m = cel.get(sel)
                if not m:
                    continue
                e = [x for x in m.get("etapes", []) if "avance_um" in x]
                pas.append(len(e))
                longueurs.append(sum(float(x["avance_um"]) for x in e))
                if m.get("sortie"):
                    sorties += 1
    if not pas:
        return {"decidable": False, "pourquoi": "aucune marche lisible"}
    au_plafond = sum(1 for p in pas if p >= plafond)
    return {"decidable": True, "marches": len(pas), "plafond": plafond,
            "sorties_du_volume": sorties, "marches_au_plafond": au_plafond,
            "part_au_plafond": round(au_plafond / len(pas), 3),
            "longueur_mediane_um": round(float(np.median(longueurs)), 1),
            # ⭐⭐⭐ LE VERDICT : la portee est-elle mesuree, ou seulement bornee par le budget ?
            "rien_na_arrete_une_seule_marche": bool(sorties == 0 and au_plafond == len(pas)),
            "donc_la_portee_est_entierement_censuree": bool(au_plafond == len(pas))}


def profondeur_de_la_confirmation(marches: list[list[dict]]) -> list[dict]:
    """Le taux de confirmation en fonction de la PROFONDEUR du pas.

    ⭐⭐⭐ C'EST LA QUESTION QUE LE PLAFOND DE SIX EMPECHAIT DE POSER. Si le marcheur s'egare, son
    taux de confirmation doit BAISSER avec la profondeur ; s'il tient, il doit rester plat. A six
    pas `107` ne voyait rien ; a vingt, une decroissance se verrait.

    ⚠ Le denominateur est le nombre de marches ENCORE EN COURSE a ce pas, pas le nombre total :
    une marche sortie du volume au pas huit ne dit rien du pas neuf, et la compter au denominateur
    ferait baisser le taux pour une raison qui n'est pas la matiere.
    """
    if not marches:
        return []
    profond = max(len(m) for m in marches)
    out = []
    for k in range(1, profond + 1):
        presents = [m[k - 1] for m in marches if len(m) >= k and "avance_um" in m[k - 1]]
        if not presents:
            continue
        out.append({"pas": k, "marches": len(presents),
                    "confirmes": sum(1 for x in presents if x.get("confirme")),
                    "taux": round(sum(1 for x in presents if x.get("confirme"))
                                  / len(presents), 3)})
    return out


def le_taux_baisse_avec_la_profondeur(profil: list[dict], tiers: int = 3) -> dict:
    """Le taux de confirmation decroit-il quand on s'enfonce, ou reste-t-il plat ?

    ⚠⚠ LE PARTAGE EST DECLARE AVANT DE VOIR LES CHIFFRES — en tiers de la profondeur — et le test
    est exact sous marges fixees. Choisir la coupure apres coup serait regler un seuil sur ce qui
    passe, ce que ce depot recense comme sa faute numero un.
    """
    lisibles = [x for x in profil if x["marches"] >= 3]
    if len(lisibles) < 2 * tiers:
        return {"decidable": False, "pourquoi": "profondeur insuffisante"}
    tot = sum(x["marches"] for x in lisibles)
    if tot < 20:
        return {"decidable": False, "pourquoi": "moins de vingt pas en tout"}
    n = len(lisibles)
    tot_a = lisibles[: n // tiers]
    tot_b = lisibles[-(n // tiers):]
    a_oui = sum(x["confirmes"] for x in tot_a)
    a_non = sum(x["marches"] - x["confirmes"] for x in tot_a)
    b_oui = sum(x["confirmes"] for x in tot_b)
    b_non = sum(x["marches"] - x["confirmes"] for x in tot_b)
    # ⚠ Le test exact vit dans `107`, qui l en avait besoin pour le risque par pas. L ecrire une
    # seconde fois serait deux implementations d une meme probabilite, libres de diverger.
    from le_marcheur_avec_le_bon_pas import _fisher  # noqa: PLC0415

    p = _fisher(a_oui, a_non, b_oui, b_non)
    ta = a_oui / max(a_oui + a_non, 1)
    tb = b_oui / max(b_oui + b_non, 1)
    return {"decidable": True, "pas_precoces": len(tot_a), "pas_tardifs": len(tot_b),
            "taux_precoce": round(ta, 3), "taux_tardif": round(tb, 3),
            "ecart": round(tb - ta, 3), "p_sous_un_taux_constant": round(p, 4),
            # ⭐⭐⭐ LE VERDICT, ET IL PEUT DIRE « PLAT » : c'est ce qui en fait un test.
            "le_taux_baisse": bool(tb < ta and p < 0.05),
            "le_taux_monte": bool(tb > ta and p < 0.05)}


def reprise_refusee(reprise: dict, attendu: dict) -> str | None:
    """Le brouillon a-t-il ete marche avec les MEMES parametres ? Sinon, pourquoi.

    ⭐⭐⭐⭐ SEPAREE DU CHOIX DES BANDES PARCE QU'ELLE NE DEPEND DE RIEN. Savoir quelles bandes
    garder demande la liste des bandes demandees, donc le cache des departs ; savoir si le
    brouillon est compatible ne demande que le brouillon. Les fondre obligeait le refus a
    attendre une lecture qu'il allait rendre inutile — et rendait le refus inexercable partout
    ou ce cache manque, c'est-a-dire exactement la ou on a besoin qu'il marche.

    ⚠ Un champ ABSENT du brouillon n'est pas un desaccord : un brouillon d'une version anterieure
    n'a pas menti sur ce parametre, il n'en a rien dit.
    """
    for champ, valeur in attendu.items():
        if champ in reprise and reprise[champ] != valeur:
            return (f"reprise refusee : `{champ}` vaut {reprise[champ]!r} dans le brouillon "
                    f"et {valeur!r} ici")
    return None


def bandes_a_reprendre(reprise: dict, attendu: dict, cles: set) -> dict:
    """Quelles bandes d'un brouillon peuvent etre gardees, ou POURQUOI aucune.

    ⭐⭐⭐⭐ ELLE EST PURE POUR POUVOIR ETRE SONDEE. La reprise vit dans `mesurer`, qui a besoin
    du volume distant : une regle de reprise qui ne serait exercable qu'en lisant le reseau ne
    serait exercee par personne, et c'est exactement le genre de code qui se casse le jour ou on
    en a besoin — c'est-a-dire apres une panne.

    ⚠⚠ LE REFUS EST TOTAL ET IL NOMME LE CHAMP. Un brouillon marche avec d'autres parametres
    n'est pas une reprise, c'est une deuxieme course : melanger dans un seul fichier deux bandes a
    `pas_max` 20 et six a 112 rendrait un JSON dont aucune ligne ne dit laquelle est laquelle.
    Garder les bandes compatibles et jeter les autres serait pire encore, parce que le fichier
    aurait alors l'air complet.

    ⚠ Une bande du brouillon qui n'est PAS demandee cette fois-ci est simplement ignoree : le
    brouillon peut venir d'une course plus large, et la reprise ne doit pas la faire grandir.
    """
    refus = reprise_refusee(reprise, attendu)
    if refus is not None:
        return {"message": refus}
    gardees, vues = [], []
    for ligne in reprise.get("lignes", []):
        cle = (int(ligne["de"]), int(ligne["a"]))
        if cle not in cles or cle in vues:
            continue
        vues.append(cle)
        gardees.append(ligne)
    return {"lignes": gardees, "cles": vues,
            "lectures": int(reprise.get("lectures_de_profil", 0))}


def mesurer(pas_max: int = PAS_MAX, bandes_max: int | None = None, demi: int = DEMI,
            fils: int = 32, selecteur: str = SELECTEUR,
            brouillon: Path | None = None,
            fenetre_locale: bool = False, arret_sur_vide: bool = False,
            reprise: dict | None = None) -> dict:
    """La marche profonde, depuis LES MEMES departs que `107`, plafond leve.

    ⭐⭐⭐ LES DEPARTS SONT CEUX DE `107`, PAS DE NOUVEAUX : la graine et les cellules sont les
    siennes, donc la comparaison est appariee par la cellule et le seul changement est la laisse.
    Tirer d'autres cellules aurait melange deux differences en une.

    ⚠⚠ ET TOUT EST GARDE : le depart, chaque etape, ET le profil brut de la polyligne. `107` a
    perdu son depart et `110` ses echantillons ; les deux ont coute une relecture du reseau.

    ⚠ `brouillon` ecrit les lectures AVANT le verdict — la garde que `110` a payee vingt minutes
    pour apprendre.

    ⭐⭐⭐⭐ `reprise` REPREND UN BROUILLON AU LIEU DE TOUT REMARCHER, et ce n'est pas une
    commodite : le 12 septembre une mise a jour de l'hote a redemarre la machine au milieu d'une
    course de dix heures, et deux bandes ecrites n'ont servi qu'a etre relues. Le brouillon
    existait deja pour survivre a une casse ; il lui manquait de pouvoir etre REPRIS.

    ⚠⚠ UNE REPRISE DONT LES PARAMETRES DIFFERENT EST REFUSEE, jamais avertie. Melanger dans un
    seul fichier deux bandes marchees a `pas_max` 20 et six a 112 rendrait un JSON dont aucune
    ligne ne dit laquelle est laquelle, et toute lecture ulterieure serait fausse sans avoir
    l'air de l'etre. Le refus NOMME le champ qui differe.

    ⚠ Ce qui autorise la reprise a rendre le meme fichier qu'une course d'un seul tenant est que
    la marche est DETERMINISTE : le volume est en lecture seule et les barres viennent de nuls a
    graine fixe. Une bande reprise est donc exactement celle qu'on aurait remarchee.
    """
    import combien_dinterstices_traverses as C  # noqa: PLC0415
    import la_normale_nest_pas_le_rayon as N  # noqa: PLC0415
    import le_pas_que_la_matiere_montre as M  # noqa: PLC0415
    from combien_de_pas_la_matiere_porte import (combien_de_pas_confirmes,  # noqa: PLC0415
                                                 marcher)
    from la_direction_que_la_matiere_montre import nul_du_tenseur  # noqa: PLC0415
    from la_normale_nest_pas_le_rayon import avancement, maintenant  # noqa: PLC0415
    from le_compte_suit_il_le_pas import departs_de_107  # noqa: PLC0415
    from voxel_distant import BUCKET, VolumeZarr  # noqa: PLC0415

    # ⚠⚠ LE REFUS DE REPRISE EST TRANCHE EN PREMIER, avant le cache des departs et avant la
    # connexion au volume : il ne depend que du brouillon. Le mettre plus bas le rendait
    # inexercable sans reseau ni cache, c'est-a-dire inexerce.
    attendu = {"fragment": C.OBJET, "volume_fin": C.VOLUME_FIN, "pas_max": int(pas_max),
               "selecteur": selecteur, "demi_cube_voxels": int(demi),
               "fenetre_locale": bool(fenetre_locale),
               "arret_sur_vide": bool(arret_sur_vide)}
    if reprise is not None:
        refus = reprise_refusee(reprise, attendu)
        if refus is not None:
            return {"message": refus}

    brut107 = json.loads(CHEMIN_DE_107.read_text())
    dep = departs_de_107(bandes_max)
    if "message" in dep:
        return dep

    garde = (None if reprise is None
             else bandes_a_reprendre(reprise, attendu, set(dep["par_bande"])))

    try:
        vol = VolumeZarr(f"{BUCKET}/{C.ZARR_FIN}")
    except RuntimeError as e:
        return {"message": f"volume fin injoignable : {e}"}

    longueurs = M.candidats_de_pas(C.PAS_UM)
    mu, sd = M.nul_par_candidat(longueurs)
    barre = max(x["p99"] for x in M.nul_du_balayage_calibre(longueurs, mu, sd).values())
    barre_moities = nul_du_tenseur(demi=demi)["accord_des_moities_p1_deg"]
    barre_interstice = max(x["p99"] for x in C.accord_du_bruit_pur().values())

    rayons = {(int(x["de"]), int(x["a"])): x.get("rayon_mm")
              for x in brut107.get("lignes", [])}
    t0 = maintenant()
    lignes, marches, lectures = [], [], 0
    cles = [k for k in dep["par_bande"]]
    deja: set[tuple[int, int]] = set()
    lectures_reprises = 0
    if garde is not None:
        lignes = list(garde["lignes"])
        deja = set(garde["cles"])
        lectures_reprises = garde["lectures"]
        for ligne in lignes:
            for cel in ligne.get("detail", []):
                marches.append([e for e in cel.get("etapes", []) if "avance_um" in e])
        print(f"reprise : {len(deja)} bande(s) gardee(s) du brouillon, "
              f"{len(cles) - len(deja)} a marcher")
    for i, cle in enumerate(cles):
        if cle in deja:
            continue
        d = dep["par_bande"][cle]
        detail = []
        for j in range(len(d["departs"])):
            e = marcher(vol, d["departs"][j], d["radial"][j], longueurs, mu, sd, barre,
                        barre_moities, barre_interstice, C.VOXEL_FIN_UM, pas_max, demi,
                        interroge_la_matiere=True, fils=fils,
                        selecteur=selecteur, barre_du_selecteur=barre,
                        fenetre_locale=fenetre_locale, arret_sur_vide=arret_sur_vide)
            pas = [x for x in e if "avance_um" in x]
            cel = {"depart_zyx": [round(float(t), 3) for t in d["departs"][j]],
                   "radial_zyx": [round(float(t), 6) for t in d["radial"][j]],
                   "etapes": e, "pas_parcourus": len(pas),
                   "pas_confirmes": combien_de_pas_confirmes(e),
                   "sortie": bool(e and e[-1].get("fin") == "sortie du volume"),
                   # ⚠⚠ TROIS motifs d'arret depuis `122`, et les confondre rendrait la portee
                   # illisible : un bord de champ, un volume qui ne repond plus, et un budget
                   # epuise ne se reparent pas pareil. `113` n'en connaissait que deux, et le
                   # second n'etait jamais atteint.
                   "plus_rien_a_lire": bool(e and e[-1].get("fin") == "plus rien a lire"),
                   "au_plafond": bool(len(pas) >= pas_max),
                   "longueur_um": round(sum(float(x["avance_um"]) for x in pas), 1)}
            # ⭐⭐⭐ LE PROFIL BRUT DE LA POLYLIGNE, GARDE. Une lecture de plus par marche, et toute
            # relecture future devient gratuite.
            if len(pas) >= 2:
                n = C.ECHANTILLONS * len(pas)
                pts, p = [], np.asarray(d["departs"][j], dtype=np.float64).copy()
                for x in pas:
                    dd = np.asarray(x["direction"], dtype=np.float64)
                    av = float(x["avance_um"]) / C.VOXEL_FIN_UM
                    tt = np.linspace(0.0, 1.0, C.ECHANTILLONS, endpoint=False)
                    pts.append(p[None, :] + dd[None, :] * (av * tt)[:, None])
                    p = p + dd * av
                pts.append(p[None, :])
                zyx = np.rint(np.concatenate(pts)).astype(np.int64)
                if vol.dans_le_volume(zyx).all():
                    v = vol.lire(zyx, fils=fils)
                    lectures += 1
                    if np.isfinite(v).all():
                        cel["profil"] = [round(float(t), 2) for t in v]
                        cel["avance_moyenne_um"] = round(
                            float(np.mean([float(x["avance_um"]) for x in pas])), 2)
            detail.append(cel)
            marches.append(pas)
        lignes.append({"de": cle[0], "a": cle[1], "rayon_mm": rayons.get(cle),
                       "detail": detail})
        # ⚠⚠ L'AVANCEMENT COMPTE LES BANDES MARCHEES, PAS TOUTES, ET C'EST LA REPRISE QUI
        # L'IMPOSE. `avancement` estime la fin en supposant que ce qui reste coute comme ce qui
        # est fait ; les bandes reprises n'ont rien coute A CETTE COURSE, donc les compter
        # divisait le temps ecoule par un nombre trop grand. Apres une reprise de deux bandes sur
        # huit, il annoncait « ~1 min restantes » pour cinq bandes d'une heure chacune. Un chiffre
        # faux de deux ordres de grandeur sert moins que pas de chiffre, parce qu'on le croit.
        avancement(i + 1 - len(deja), len(cles) - len(deja), "bandes marchees", t0)
        # ⚠⚠⚠ LE BROUILLON EST ECRIT A CHAQUE BANDE, PAS A LA FIN. Une course de six heures qui
        # casse a la vingt-septieme bande perdrait tout ; `110` a paye vingt minutes pour
        # apprendre a ecrire avant le verdict, et ecrire une seule fois a la fin ne suffit pas
        # quand la course dure. Chaque bande rend l'etat relisible par `--reagreger`.
        if brouillon is not None:
            brouillon.parent.mkdir(parents=True, exist_ok=True)
            brouillon.write_text(json.dumps(
                {"fragment": C.OBJET, "volume_fin": C.VOLUME_FIN,
                 "pas_nominal_um": C.PAS_UM, "pas_max": int(pas_max),
                 "selecteur": selecteur, "demi_cube_voxels": demi,
                 "fenetre_locale": bool(fenetre_locale),
                 "arret_sur_vide": bool(arret_sur_vide),
                 "barre_du_balayage": round(float(barre), 3),
                 "barre_de_linterstice": round(float(barre_interstice), 4),
                 "barre_daccord_des_moities_deg": barre_moities,
                 "lectures_de_profil": lectures + lectures_reprises,
                 # ⚠ `secondes` ne compte QUE cette course : additionner le temps d'une course
                 # interrompue donnerait une duree que personne n'a passee d'un seul tenant.
                 "secondes": round(maintenant() - t0, 1),
                 "bandes_reprises": len(deja),
                 "bandes": len(lignes), "lignes": lignes, "course_incomplete": True},
                indent=2, ensure_ascii=False))

    lu = {"fragment": C.OBJET, "volume_fin": C.VOLUME_FIN, "pas_nominal_um": C.PAS_UM,
          "pas_max": int(pas_max), "selecteur": selecteur, "demi_cube_voxels": demi,
          "fenetre_locale": bool(fenetre_locale), "arret_sur_vide": bool(arret_sur_vide),
          "barre_du_balayage": round(float(barre), 3),
          "barre_de_linterstice": round(float(barre_interstice), 4),
          "barre_daccord_des_moities_deg": barre_moities,
          "lectures_de_profil": lectures + lectures_reprises,
          "secondes": round(maintenant() - t0, 1), "bandes_reprises": len(deja),
          "bandes": len(lignes), "lignes": lignes,
          "ce_qui_a_arrete_les_marches_de_107": ce_qui_a_arrete_les_marches(brut107)}
    if brouillon is not None:
        brouillon.parent.mkdir(parents=True, exist_ok=True)
        brouillon.write_text(json.dumps(lu, indent=2, ensure_ascii=False))
        print(f"lectures écrites avant le verdict : {brouillon}")
    return agreger(lu)


def le_taux_depend_il_de_la_marche(par_marche: list[dict]) -> dict:
    """Le taux de confirmation varie-t-il D'UNE MARCHE A L'AUTRE plus que le hasard ne l'admet ?

    ⭐⭐⭐ POURQUOI CETTE QUESTION EXISTE, ET D'OU ELLE VIENT. Elle n'a pas ete pensee : elle a
    ete VUE. La grille de `figure_jusquou.py` dessine une ligne par marche et une case par pas,
    et les dernieres lignes y sont visiblement plus vides que les premieres — ce que le taux
    global (0,52) et le taux par profondeur (plat) cachent tous les deux, parce qu'ils moyennent
    justement sur l'axe ou l'ecart se trouve. C'est « regarder avant de mesurer » qui paie.

    ⚠⚠ Et c'est une question DIFFERENTE de celle de la profondeur. « Le taux baisse-t-il quand
    on avance » demande si une marche se degrade ; « le taux depend-il de la marche » demande si
    certaines marches sont mauvaises DES LE DEPART. Les deux peuvent etre vraies ou fausses
    independamment, et elles n'ont pas le meme remede : la premiere appellerait une correction en
    cours de route, la seconde un choix de depart.

    Le test est celui d'une binomiale unique : sous « toutes les marches tirent au meme taux »,
    la variance des comptes vaut `n p (1-p)`. On la compare a la variance observee (indice de
    dispersion), et le p vient d'un khi-deux a `k-1` degres.

    ⚠ Le lien avec le RAYON est teste a part (`le_taux_suit_il_le_rayon`). Ma premiere version
    le declarait « descriptif, jamais un test » au motif qu'un ordre n'est pas une correlation —
    c'etait trop prudent : chaque marche porte SON rayon, mesure, donc le rang se teste. Ce qui
    reste vrai est qu'il ne faut pas lire le demi-partage ci-dessous comme ce test.
    """
    k = len(par_marche)
    if k < 3:
        return {"decidable": False, "pourquoi": f"{k} marche(s), il en faut au moins trois"}
    n = par_marche[0]["pas"]
    if any(x["pas"] != n for x in par_marche):
        return {"decidable": False, "pourquoi": "les marches n'ont pas toutes le meme nombre de pas"}
    comptes = np.array([x["confirmes"] for x in par_marche], dtype=float)
    p = float(comptes.sum() / (k * n))
    attendue = n * p * (1.0 - p)
    if attendue <= 0:
        return {"decidable": False, "pourquoi": "taux degenere (0 ou 1), aucune dispersion possible"}
    observee = float(comptes.var(ddof=1))
    khi2 = float(((comptes - n * p) ** 2).sum() / attendue)
    from scipy import stats
    pv = float(stats.chi2.sf(khi2, k - 1))
    moitie = k // 2
    return {
        "decidable": True, "marches": k, "pas_par_marche": n,
        "taux_moyen": round(p, 4),
        "taux_min": round(float(comptes.min() / n), 4),
        "taux_max": round(float(comptes.max() / n), 4),
        "variance_observee": round(observee, 4),
        "variance_sous_un_taux_unique": round(attendue, 4),
        "indice_de_dispersion": round(observee / attendue, 3),
        "khi2": round(khi2, 2), "p_sous_un_taux_unique": round(pv, 4),
        "les_marches_ne_tirent_pas_au_meme_taux": bool(pv < 0.05),
        # ⚠ Descriptif : le test du rayon est `le_taux_suit_il_le_rayon`, pas ce partage.
        "taux_premiere_moitie": round(float(comptes[:moitie].mean() / n), 4),
        "taux_seconde_moitie": round(float(comptes[moitie:].mean() / n), 4)}


def le_taux_suit_il_le_rayon(par_marche: list[dict]) -> dict:
    """Le taux de confirmation suit-il le RAYON de la bande ou la marche est partie ?

    ⭐⭐⭐ C'est la question que la dispersion ouvre et ne repond pas. `le_taux_depend_il_de_la_
    marche` etablit que les marches ne tirent pas au meme taux ; il ne dit pas ce qui les
    separe. Ici chaque marche porte le rayon de sa bande, donc la question a une reponse.

    ⚠⚠ Spearman et non Pearson, et c'est deliberé : on demande si le taux DECROIT avec le
    rayon, pas s'il decroit lineairement. Une chute brusque a un rayon donne est une reponse
    parfaitement bonne a la premiere question et rendrait un mauvais coefficient a la seconde.

    ⚠ Une correlation n'est pas une cause. Le rayon est aussi ce qui fait varier l'epaisseur
    lue, la courbure et la qualite du scan — ce test dit OU le marcheur cesse de confirmer,
    jamais POURQUOI.
    """
    ray = [x.get("rayon_mm") for x in par_marche]
    if len(par_marche) < 4 or any(v is None for v in ray):
        return {"decidable": False,
                "pourquoi": "il faut quatre marches portant chacune son rayon"}
    from scipy import stats
    taux = [x["confirmes"] / x["pas"] for x in par_marche]
    rho, pv = stats.spearmanr(ray, taux)
    return {"decidable": True, "marches": len(par_marche),
            "rayon_min_mm": round(float(min(ray)), 2), "rayon_max_mm": round(float(max(ray)), 2),
            "rho_de_spearman": round(float(rho), 4), "p": round(float(pv), 6),
            "le_taux_decroit_avec_le_rayon": bool(rho < 0 and pv < 0.05)}


def agreger(r: dict) -> dict:
    """Le verdict, DERIVE des etapes gardees — le partage que `107` et `110` imposent."""
    pas_max = int(r.get("pas_max") or 0)
    r_lignes = list(r.get("lignes", []))
    marches, confirmes, longueurs, sorties, plafond = [], [], [], 0, 0
    for ligne in r_lignes:
        for cel in ligne.get("detail", []):
            e = [x for x in cel.get("etapes", []) if "avance_um" in x]
            if not e:
                continue
            marches.append(e)
            confirmes.append(int(cel.get("pas_confirmes") or 0))
            longueurs.append(float(cel.get("longueur_um") or 0.0))
            sorties += 1 if cel.get("sortie") else 0
            plafond += 1 if cel.get("au_plafond") else 0
    r = dict(r)
    if not marches:
        r["resume"] = {"decidable": False, "pourquoi": "aucune marche lisible"}
        return r
    parcourus = [len(m) for m in marches]
    profil = profondeur_de_la_confirmation(marches)
    r["profondeur_de_la_confirmation"] = profil
    r["le_taux_baisse_avec_la_profondeur"] = le_taux_baisse_avec_la_profondeur(profil)
    # ⚠ Le rayon voyage AVEC la marche et n'est pas retrouve par l'indice : les deux
    # coincident aujourd'hui parce qu'il y a une marche par bande, et le jour ou une bande en
    # portera deux, l'indice designerait la mauvaise.
    rayons = [ligne.get("rayon_mm") for ligne in r_lignes for _ in ligne.get("detail", [])
              if _.get("etapes")]
    par_marche = [{"marche": i, "pas": len(m),
                   "confirmes": sum(1 for x in m if x.get("confirme")),
                   "rayon_mm": rayons[i] if i < len(rayons) else None}
                  for i, m in enumerate(marches)]
    r["par_marche"] = par_marche
    r["le_taux_depend_il_de_la_marche"] = le_taux_depend_il_de_la_marche(par_marche)
    r["le_taux_suit_il_le_rayon"] = le_taux_suit_il_le_rayon(par_marche)
    r["resume"] = {
        "decidable": True, "marches": len(marches), "plafond": pas_max,
        "pas_parcourus_median": float(np.median(parcourus)),
        "pas_parcourus_min": int(min(parcourus)), "pas_parcourus_max": int(max(parcourus)),
        "sorties_du_volume": sorties, "marches_au_plafond": plafond,
        "part_au_plafond": round(plafond / len(marches), 3),
        "longueur_mediane_um": round(float(np.median(longueurs)), 1),
        "longueur_max_um": round(float(max(longueurs)), 1),
        "pas_confirmes_median": float(np.median(confirmes)),
        "pas_confirmes_max": int(max(confirmes)),
        "taux_de_confirmation_global": round(
            float(np.mean([1.0 if x.get("confirme") else 0.0 for m in marches for x in m])), 4),
        # ⭐⭐⭐ LE VERDICT QUI COMPTE : quelque chose a-t-il ENFIN arrete une marche ?
        "quelque_chose_a_arrete_des_marches": bool(plafond < len(marches)),
        "la_portee_est_encore_censuree": bool(plafond == len(marches))}
    return r


def afficher(r: dict) -> None:
    if "message" in r:
        print(f"⚠ {r['message']}")
        return
    a = r.get("ce_qui_a_arrete_les_marches_de_107", {})
    if a.get("decidable"):
        print(f"\nCE QUI AVAIT ARRÊTÉ LES MARCHES DE `107` : RIEN")
        print(f"   {a['marches_au_plafond']}/{a['marches']} au plafond de {a['plafond']} pas · "
              f"{a['sorties_du_volume']} sortie(s) du volume · "
              f"longueur médiane {a['longueur_mediane_um']} µm")
        print(f"   ★ la portée y était entièrement CENSURÉE : "
              f"{a['donc_la_portee_est_entierement_censuree']}")
    s = r.get("resume", {})
    if not s.get("decidable"):
        print(f"⚠ {s.get('pourquoi')}")
        return
    print(f"\n{r.get('fragment')} · {s['marches']} marches · plafond {s['plafond']} pas · "
          f"sélecteur {r.get('selecteur')} · {r.get('secondes')} s\n")
    print(f"★★★ QUELQUE CHOSE A-T-IL ARRÊTÉ DES MARCHES ? "
          f"{'OUI' if s['quelque_chose_a_arrete_des_marches'] else 'NON'}")
    print(f"   {s['marches_au_plafond']}/{s['marches']} au plafond "
          f"({s['part_au_plafond']:.1%}) · {s['sorties_du_volume']} sortie(s)")
    print(f"   pas parcourus : médiane {s['pas_parcourus_median']}, de "
          f"{s['pas_parcourus_min']} à {s['pas_parcourus_max']}")
    print(f"   longueur : médiane {s['longueur_mediane_um']} µm, max {s['longueur_max_um']}")
    print(f"   pas confirmés CONSÉCUTIFS : médiane {s['pas_confirmes_median']}, max "
          f"{s['pas_confirmes_max']} · taux global {s['taux_de_confirmation_global']}")
    p = r.get("profondeur_de_la_confirmation") or []
    if p:
        print(f"\nLE TAUX DE CONFIRMATION PAR PROFONDEUR")
        for x in p:
            print(f"   pas {x['pas']:>3} · {x['marches']:>3} marches · "
                  f"{x['confirmes']:>3} confirmés · {x['taux']:.3f}")
    t = r.get("le_taux_baisse_avec_la_profondeur", {})
    if t.get("decidable"):
        print(f"\n★★★ LE TAUX BAISSE-T-IL AVEC LA PROFONDEUR ? "
              f"{'OUI' if t['le_taux_baisse'] else ('IL MONTE' if t['le_taux_monte'] else 'NON')}")
        print(f"   précoce {t['taux_precoce']} sur {t['pas_precoces']} pas · tardif "
              f"{t['taux_tardif']} sur {t['pas_tardifs']} · écart {t['ecart']:+.3f} · "
              f"p = {t['p_sous_un_taux_constant']}")


def _marche(confirmes) -> list[dict]:
    """Une marche fabriquee : une etape par booleen de confirmation."""
    return [{"pas": i + 1, "avance_um": 230.0, "confirme": bool(c),
             "direction": [1.0, 0.0, 0.0]} for i, c in enumerate(confirmes)]


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # === CE QUI A ARRETE LES MARCHES ==========================================================
    # ⭐⭐⭐ LE CONSTAT QUI IMPOSE LA TRANCHE, et il doit pouvoir dire NON : un corpus ou des marches
    # s'arretent avant le plafond n'est PAS entierement censure.
    tout = {"pas_max": 6, "lignes": [{"detail": [{"calibre": {
        "etapes": _marche([True] * 6), "sortie": False}}]} for _ in range(5)]}
    a = ce_qui_a_arrete_les_marches(tout)
    v("un corpus dont toutes les marches touchent le plafond est déclaré CENSURÉ",
      a["rien_na_arrete_une_seule_marche"] is True and a["part_au_plafond"] == 1.0)
    court = json.loads(json.dumps(tout))
    court["lignes"][0]["detail"][0]["calibre"]["etapes"] = _marche([True] * 3)
    court["lignes"][0]["detail"][0]["calibre"]["sortie"] = True
    b = ce_qui_a_arrete_les_marches(court)
    v("... et un corpus où une marche s'arrête avant ne l'est PAS",
      b["rien_na_arrete_une_seule_marche"] is False and b["sorties_du_volume"] == 1,
      f"{b['marches_au_plafond']}/{b['marches']} au plafond")
    v("le constat se refuse sur un corpus vide",
      ce_qui_a_arrete_les_marches({"pas_max": 6, "lignes": []})["decidable"] is False)
    if CHEMIN_DE_107.is_file():
        reel = ce_qui_a_arrete_les_marches(json.loads(CHEMIN_DE_107.read_text()))
        # ⭐⭐⭐ SUR LES DONNEES REELLES DE `107` : rien n'a arrete une seule marche.
        v("sur `107`, rien n'a arrêté une seule marche",
          reel["rien_na_arrete_une_seule_marche"] is True,
          f"{reel['marches_au_plafond']}/{reel['marches']} au plafond, "
          f"{reel['sorties_du_volume']} sortie(s)")

    # === LA PROFONDEUR DE LA CONFIRMATION =====================================================
    # ⚠⚠ LE DENOMINATEUR EST LE NOMBRE DE MARCHES ENCORE EN COURSE : une marche sortie au pas
    # trois ne dit rien du pas quatre, et la compter ferait baisser le taux pour une raison qui
    # n'est pas la matiere.
    p = profondeur_de_la_confirmation([_marche([True] * 5), _marche([True] * 2)])
    v("une marche plus courte quitte le dénominateur au-delà de sa longueur",
      [x["marches"] for x in p] == [2, 2, 1, 1, 1], str([x["marches"] for x in p]))
    v("... et le taux est calculé sur les présents",
      [x["taux"] for x in p] == [1.0] * 5)
    p = profondeur_de_la_confirmation([_marche([True, False, True]),
                                       _marche([False, False, True])])
    v("... et il compte les confirmations, pas les pas",
      [x["confirmes"] for x in p] == [1, 0, 2], str([x["confirmes"] for x in p]))
    v("la profondeur se refuse sans marche", profondeur_de_la_confirmation([]) == [])

    # === LE TAUX BAISSE-T-IL ? ================================================================
    # ⭐⭐⭐ LA GARDE CENTRALE, ET ELLE DOIT TRANCHER DANS LES TROIS SENS : baisse, monte, ou plat.
    # Un verdict qui ne saurait dire « plat » serait un oui deguise.
    plat = [{"pas": k, "marches": 40, "confirmes": 28, "taux": 0.7} for k in range(1, 13)]
    r = le_taux_baisse_avec_la_profondeur(plat)
    v("un taux constant sur de gros effectifs n'est PAS annoncé comme une baisse",
      r["le_taux_baisse"] is False and r["le_taux_monte"] is False,
      f"p = {r['p_sous_un_taux_constant']}")
    baisse = ([{"pas": k, "marches": 40, "confirmes": 36, "taux": 0.9} for k in range(1, 5)]
              + [{"pas": k, "marches": 40, "confirmes": 28, "taux": 0.7}
                 for k in range(5, 9)]
              + [{"pas": k, "marches": 40, "confirmes": 12, "taux": 0.3}
                 for k in range(9, 13)])
    r = le_taux_baisse_avec_la_profondeur(baisse)
    v("... et une vraie baisse l'est",
      r["le_taux_baisse"] is True,
      f"{r['taux_precoce']} → {r['taux_tardif']}, p = {r['p_sous_un_taux_constant']}")
    r = le_taux_baisse_avec_la_profondeur(list(reversed(baisse)))
    v("... et une MONTÉE est annoncée comme telle, pas comme une baisse",
      r["le_taux_monte"] is True and r["le_taux_baisse"] is False)
    # ⚠ Les pas dont l'effectif est trop petit sont ecartes : un pas a deux marches ne decide rien.
    maigre = [{"pas": k, "marches": 2, "confirmes": 2, "taux": 1.0} for k in range(1, 13)]
    v("les pas dont l'effectif est trop petit sont écartés",
      le_taux_baisse_avec_la_profondeur(maigre)["decidable"] is False)
    v("... et une profondeur insuffisante aussi",
      le_taux_baisse_avec_la_profondeur(plat[:4])["decidable"] is False)

    # === LA REPRISE ===========================================================================
    # ⭐⭐⭐⭐ ELLE EXISTE PARCE QU'UNE PANNE L'A EXIGEE : le 12 septembre une mise a jour de
    # l'hote a redemarre la machine au milieu d'une course de dix heures. Le brouillon survivait
    # deja ; ce qui manquait etait de pouvoir le REPRENDRE. La regle est pure, donc elle est
    # exercee ici sans toucher au reseau.
    attendu_ = {"fragment": "PHercParis4", "volume_fin": "v", "pas_max": 112,
                "selecteur": "deux_roles", "demi_cube_voxels": 20,
                "fenetre_locale": False, "arret_sur_vide": True}
    brouillon_ = {**attendu_, "lectures_de_profil": 2,
                  "lignes": [{"de": 10, "a": 27, "rayon_mm": 4.07, "detail": []},
                             {"de": 28, "a": 37, "rayon_mm": 6.32, "detail": []}]}
    cles_ = {(10, 27), (28, 37), (38, 45)}
    g_ = bandes_a_reprendre(brouillon_, attendu_, cles_)
    v("la reprise garde les bandes deja marchees", g_.get("cles") == [(10, 27), (28, 37)],
      f"{g_.get('cles')}")
    v("... et elle rend leurs lignes, pas seulement leurs cles", len(g_["lignes"]) == 2)
    v("... et elle reporte les lectures deja payees", g_["lectures"] == 2)
    # ⚠ Une bande du brouillon qui n'est plus demandee ne doit pas faire grandir la course.
    g2_ = bandes_a_reprendre(brouillon_, attendu_, {(10, 27)})
    v("une bande non demandee est ignoree", g2_["cles"] == [(10, 27)], f"{g2_['cles']}")
    # ⭐⭐⭐⭐ LE REFUS, ET IL DOIT NOMMER LE CHAMP : sans lui, deux bandes marchees a vingt pas
    # et six a cent douze finiraient dans un seul fichier dont aucune ligne ne dit laquelle est
    # laquelle.
    for champ_, mauvais_ in (("pas_max", 20), ("selecteur", "autre"), ("demi_cube_voxels", 12),
                             ("fenetre_locale", True), ("arret_sur_vide", False),
                             ("fragment", "PHerc0500P2")):
        r_ = bandes_a_reprendre({**brouillon_, champ_: mauvais_}, attendu_, cles_)
        v(f"⭐ une reprise dont `{champ_}` differe est REFUSEE", "message" in r_)
        v(f"... et le refus nomme `{champ_}`", champ_ in r_.get("message", ""),
          r_.get("message", ""))
    # ⚠ Sonde : un brouillon SANS le champ ne doit pas etre refuse pour autant — un brouillon
    # d'une version anterieure n'a pas menti, il n'a rien dit.
    sans_ = {k: v_ for k, v_ in brouillon_.items() if k != "arret_sur_vide"}
    v("un brouillon qui ne DIT PAS un parametre n'est pas refuse",
      "message" not in bandes_a_reprendre(sans_, attendu_, cles_))
    # ⚠ Sonde : deux fois la meme bande dans un brouillon ne doit pas la garder deux fois.
    double_ = {**brouillon_, "lignes": brouillon_["lignes"] + [brouillon_["lignes"][0]]}
    v("une bande ecrite deux fois n'est gardee qu'une",
      len(bandes_a_reprendre(double_, attendu_, cles_)["lignes"]) == 2)

    # ⭐⭐⭐⭐ ET LE REFUS EST EXERCE DE BOUT EN BOUT, SANS RESEAU : il est tranche avant la
    # connexion au volume, donc `mesurer` rend son message sans rien lire. Sans ce controle, la
    # seule facon de savoir si le refus marche serait de lancer une course de dix heures.
    faux_brouillon = {"fragment": "PAS_CE_FRAGMENT", "lignes": [],
                      "lectures_de_profil": 0}
    v("le refus ne depend QUE du brouillon",
      reprise_refusee(faux_brouillon, {"fragment": "PHercParis4"}) is not None
      and reprise_refusee({"lignes": []}, {"fragment": "PHercParis4"}) is None)
    hors_ligne = mesurer(pas_max=112, bandes_max=1, reprise=faux_brouillon)
    v("⭐ un refus de reprise est rendu SANS toucher au volume",
      "message" in hors_ligne and "fragment" in hors_ligne["message"],
      f"{hors_ligne.get('message')}")

    # === L'AGREGATION =========================================================================
    # ⚠⚠ ELLE DOIT TOURNER SUR UN BROUILLON SEUL, sinon `--reagreger` ne servirait a rien.
    brouillon = {"pas_max": 20, "lignes": [{"de": 1, "a": 2, "rayon_mm": 4.0, "detail": [
        {"etapes": _marche([True] * 20), "pas_parcourus": 20, "pas_confirmes": 20,
         "sortie": False, "au_plafond": True, "longueur_um": 4600.0},
        {"etapes": _marche([True] * 5), "pas_parcourus": 5, "pas_confirmes": 5,
         "sortie": True, "au_plafond": False, "longueur_um": 1150.0}]}]}
    ag = agreger(brouillon)
    v("l'agrégation tourne sur un brouillon seul", ag["resume"]["marches"] == 2)
    # ⭐⭐⭐ ET LE VERDICT DOIT VOIR QU'UNE MARCHE S'EST ARRETEE : c'est toute la question.
    v("... et elle voit qu'une marche s'est arrêtée avant le plafond",
      ag["resume"]["quelque_chose_a_arrete_des_marches"] is True
      and ag["resume"]["la_portee_est_encore_censuree"] is False,
      f"{ag['resume']['marches_au_plafond']}/{ag['resume']['marches']}")
    tout_plafond = {"pas_max": 20, "lignes": [{"detail": [
        {"etapes": _marche([True] * 20), "pas_parcourus": 20, "pas_confirmes": 20,
         "sortie": False, "au_plafond": True, "longueur_um": 4600.0}]}]}
    v("... et que la portée reste censurée quand tout touche le plafond",
      agreger(tout_plafond)["resume"]["la_portee_est_encore_censuree"] is True)
    v("... et elle rend le taux de confirmation global",
      abs(ag["resume"]["taux_de_confirmation_global"] - 1.0) < 1e-9)

    # === LE PLAFOND EST DERIVE, PAS CHOISI ====================================================
    # ⚠ Vingt pas font environ 4,6 mm a l'avance mesuree, l'ordre de grandeur auquel `44` mesure
    # que la chaine tient. Le chiffre est dans le module, donc verifiable.
    v("le plafond vaut vingt pas, soit l'ordre de grandeur où `44` mesure que la chaîne tient",
      PAS_MAX == 20 and 4.0 < PAS_MAX * 230.0 / 1000.0 < 5.0,
      f"{PAS_MAX} pas = {PAS_MAX * 230.0 / 1000.0:.1f} mm")
    v("... et le sélecteur est celui que `105` a corrigé", SELECTEUR == "deux_roles")

    # ⭐⭐ LES DEUX AGRÉGATS QUE LA FIGURE A FAIT NAÎTRE. Ils ne se testent pas sur la vraie
    # course — elle coûte cinq heures — mais sur des marches fabriquées dont on connaît la
    # réponse, et chacun est sondé en remettant le défaut qu'il doit voir.
    egal = [{"marche": i, "pas": 20, "confirmes": 10, "rayon_mm": 4.0 + i} for i in range(10)]
    d = le_taux_depend_il_de_la_marche(egal)
    v("dix marches au même compte ne dispersent pas", d["decidable"] and d["indice_de_dispersion"] < 0.5,
      f"indice {d.get('indice_de_dispersion')}")
    v("... donc le taux unique n'est pas rejeté", not d["les_marches_ne_tirent_pas_au_meme_taux"])
    # ⚠⚠ LA sonde : des marches franchement séparées DOIVENT rejeter le taux unique. Sans elle,
    # un test qui répondrait « pas de dispersion » à tout passerait le contrôle du dessus.
    coupe = ([{"marche": i, "pas": 20, "confirmes": 18, "rayon_mm": 4.0 + i} for i in range(5)]
             + [{"marche": 5 + i, "pas": 20, "confirmes": 2, "rayon_mm": 9.0 + i} for i in range(5)])
    d2 = le_taux_depend_il_de_la_marche(coupe)
    v("deux populations séparées rejettent le taux unique",
      d2["les_marches_ne_tirent_pas_au_meme_taux"], f"p = {d2.get('p_sous_un_taux_unique')}")
    v("... et l'indice de dispersion le dit", d2["indice_de_dispersion"] > 3,
      f"indice {d2.get('indice_de_dispersion')}")
    v("moins de trois marches est indécidable, jamais « pas de dispersion »",
      not le_taux_depend_il_de_la_marche(egal[:2])["decidable"])

    ry = le_taux_suit_il_le_rayon(coupe)
    v("un taux qui chute avec le rayon est vu", ry["le_taux_decroit_avec_le_rayon"],
      f"rho {ry.get('rho_de_spearman')}, p {ry.get('p')}")
    monte = [{"marche": i, "pas": 20, "confirmes": 2 * i, "rayon_mm": 4.0 + i} for i in range(10)]
    v("... et un taux qui MONTE n'est pas lu comme une chute",
      not le_taux_suit_il_le_rayon(monte)["le_taux_decroit_avec_le_rayon"])
    v("une marche sans rayon rend indécidable plutôt que de deviner",
      not le_taux_suit_il_le_rayon(
          [{"marche": i, "pas": 20, "confirmes": i, "rayon_mm": None} for i in range(5)])["decidable"])

    print(f"\n{'ALL PASS' if echecs == 0 else 'ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 0 if echecs == 0 else 1


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--pas", type=int, default=PAS_MAX)
    p.add_argument("--bandes", type=int, default=None)
    p.add_argument("--demi", type=int, default=DEMI)
    p.add_argument("--fils", type=int, default=32)
    p.add_argument("--selecteur", default=SELECTEUR)
    # ⭐⭐ Les deux options de `122`, et elles DEFAUTENT a l'ancien comportement : une re-course
    # qui changerait le marcheur sans le dire rendrait des chiffres incomparables a ceux de `113`.
    p.add_argument("--fenetre-locale", action="store_true",
                   help="la fenetre de pas suit l'espacement local, a largeur constante (`121`)")
    p.add_argument("--arret-sur-vide", action="store_true",
                   help="la marche s'arrete au premier pas aveugle (`116`)")
    p.add_argument("--reagreger", action="store_true")
    p.add_argument("--reprendre", action="store_true",
                   help="reprend les bandes deja ecrites dans le --json au lieu de les remarcher")
    p.add_argument("--json", type=Path, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if a.reagreger:
        if a.json is None or not a.json.is_file():
            print("⚠ --reagreger demande un --json existant")
            return 1
        r = agreger(json.loads(a.json.read_text()))
        afficher(r)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False))
        print(f"\nréagrégé : {a.json}")
        return 0
    reprise = None
    if a.reprendre:
        if a.json is None or not a.json.is_file():
            print("⚠ --reprendre demande un --json existant")
            return 1
        reprise = json.loads(a.json.read_text())
    r = mesurer(pas_max=a.pas, bandes_max=a.bandes, demi=a.demi, fils=a.fils,
                selecteur=a.selecteur, brouillon=a.json, reprise=reprise,
                fenetre_locale=a.fenetre_locale, arret_sur_vide=a.arret_sur_vide)
    afficher(r)
    # ⚠⚠⚠ UN REFUS N'ECRIT RIEN, ET C'EST UNE SONDE QUI L'A TROUVE. Ma premiere version
    # affichait « reprise refusee » puis ecrasait le brouillon avec le message de refus : la
    # fonction ecrite pour proteger le fichier le DETRUISAIT, et il n'en reste alors aucune trace
    # puisque le seul exemplaire etait celui-la. Tout retour qui porte `message` est un echec,
    # donc il ne touche pas au disque et il sort en code non nul.
    if "message" in r:
        return 1
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False))
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
