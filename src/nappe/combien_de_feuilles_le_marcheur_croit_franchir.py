#!/usr/bin/env python3
"""Combien de feuilles le marcheur croit-il franchir, et combien en franchit-il ?

⭐⭐⭐⭐ POURQUOI CE FICHIER EXISTE, ET POURQUOI IL N'AURAIT PAS PU EXISTER AVANT `135`. Le graal
demande de transferer de spire a spire ; un dérouleur qui se trompe de compte se decale d'autant de
spires, et personne n'avait mesure ce compte. Il fallait pour cela savoir OU une marche finit, ce
que `135` a etabli : vingt-quatre arrets sur vingt-cinq sont la surface exterieure du rouleau, donc
une marche traverse de son rayon de depart a son rayon de sortie. L'etendue radiale traversee est
alors connue, l'espacement des feuilles de `PHercParis4` est mesure par DEUX instruments
independants (`R4-F14` : 164 µm par les transferts humains, 182,4 par l'atlas), et le marcheur, lui,
publie `feuilles_franchies` a chaque pas. Les trois se comparent.

⚠⚠ CE QUE LE COMPTE DU MARCHEUR N'EST PAS : une division par le pas nominal. `feuilles_franchies`
ajuste une famille de cosinus au profil d'intensite LU sur le segment et rend la frequence qui
colle ; aucun espacement n'y entre. La comparaison n'est donc pas tautologique.

⭐⭐⭐ ET LA QUESTION A DEUX LECTURES QUE LA MESURE SUR LE ROULEAU NE PEUT PAS SEPARER : un compte
qui depasse l'etendue radiale divisee par l'espacement peut vouloir dire que le marcheur SUR-COMPTE,
ou qu'un chemin oblique traverse reellement plus de feuilles qu'une traversee radiale. Les deux
predisent la meme chose sur le rouleau. Ce qui les separe est une matiere ou le compte vrai est
CONNU — une pile fabriquee, dont la normale est analytique — et c'est le controle du §4 :
`la_fixture_tranche_t_elle`.

⚠ L'espacement voyage en PAIRE et jamais seul : les deux instruments de `R4-F14` different de 11 %,
c'est-a-dire de l'ordre de l'effet cherche. Un verdict qui ne tiendrait que pour l'un des deux
n'est pas un verdict.

Usage :
    uv run python src/nappe/combien_de_feuilles_le_marcheur_croit_franchir.py --verifier
    uv run python src/nappe/combien_de_feuilles_le_marcheur_croit_franchir.py \\
        --json docs/mesures/combien_de_feuilles_le_marcheur_croit_franchir.json
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

CESSE = RACINE / "docs" / "mesures" / "ou_la_matiere_cesse_de_se_lire.json"
# ⚠⚠ LES DEUX ESPACEMENTS DE `R4-F14`, ET ILS VOYAGENT ENSEMBLE. 164 µm vient des transferts
# humains (`91` §3), 182,4 de l'atlas `winding-ruler` (`86` §3). Publier un seul ferait passer le
# desaccord de deux instruments pour une precision qu'aucun des deux n'a.
ESPACEMENTS_UM = (164.0, 182.4)
PAS_MINIMUM = 5
VOXEL_UM = 2.4


def traversees(cesse: dict, racine: Path = RACINE) -> list[dict]:
    """Chaque marche SORTIE DU ROULEAU : ce qu'elle a traverse, et ce qu'elle a compte.

    ⚠⚠ Seules les marches sorties sont retenues, et c'est la condition qui rend le compte
    geometrique definissable : une marche arretee au plafond n'a pas traverse une etendue connue,
    elle s'est arretee quelque part. `135` les distingue.

    ⚠ La marche est coupee a son premier pas aveugle, comme `119` et `133` le font : ce qui suit
    n'a rien lu, donc son compte ne mesure rien.

    ⚠ Le RETOUR RADIAL est mesure et rendu : une marche qui remonte puis redescend en rayon
    refranchit des feuilles, donc son compte DOIT depasser l'etendue nette. Le confondre avec un
    sur-comptage ferait porter au marcheur ce qui est sa trajectoire.
    """
    from ce_qui_porte_le_taux import est_aveugle  # noqa: PLC0415

    out = []
    for c in cesse.get("par_course", []):
        chemin = racine / "docs" / "mesures" / c["source"]
        if not chemin.is_file():
            continue
        course = json.loads(chemin.read_text(encoding="utf-8"))
        cellules, i = {}, 0
        for ligne in course.get("lignes", []):
            for cel in ligne.get("detail", []):
                cellules[i] = (ligne, cel)
                i += 1
        for a in c.get("arrets", []):
            if not a.get("verdict", {}).get("sorti_du_rouleau"):
                continue
            ligne, cel = cellules[a["marche"]]
            etapes = [e for e in cel.get("etapes", []) if "confirme" in e]
            n = next((k for k, e in enumerate(etapes) if est_aveugle(e)), len(etapes))
            voyants = etapes[:n]
            if len(voyants) < PAS_MINIMUM:
                continue
            fr = [e.get("feuilles_franchies") for e in voyants]
            compte = float(sum(x for x in fr if x is not None))
            if compte <= 0.0:
                continue
            axe = np.asarray(a["axe_zyx"], dtype=float)
            p = np.asarray(cel["depart_zyx"], dtype=float)
            rayons = [float(np.linalg.norm(p - axe)) * VOXEL_UM]
            for e in voyants:
                p = p + np.asarray(e["direction"], dtype=float) * (float(e["avance_um"]) / VOXEL_UM)
                rayons.append(float(np.linalg.norm(p - axe)) * VOXEL_UM)
            dr = np.diff(np.asarray(rayons))
            etendue = float(rayons[-1] - rayons[0])
            parcourue = float(np.abs(dr).sum())
            chemin_um = float(sum(float(e["avance_um"]) for e in voyants))
            if etendue <= 0.0 or chemin_um <= 0.0:
                continue
            out.append({
                "course": c["source"], "memoire_du_cap": c.get("memoire_du_cap", 0.0),
                "bande": [int(ligne["de"]), int(ligne["a"])], "rayon_mm": ligne.get("rayon_mm"),
                "pas_voyants": len(voyants),
                "etendue_radiale_um": round(etendue, 1),
                "etendue_radiale_parcourue_um": round(parcourue, 1),
                "retour_radial": round(parcourue / etendue, 3),
                "chemin_um": round(chemin_um, 1),
                "obliquite_du_chemin": round(chemin_um / etendue, 3),
                "feuilles_comptees": round(compte, 2),
                "pas_en_butee": sum(1 for e in voyants if e.get("fraction_en_butee")),
                "fraction_par_pas": round(compte / len(voyants), 4)})
    return out


def lecart_au_compte_geometrique(tr: list[dict], espacements=ESPACEMENTS_UM) -> dict:
    """L'espacement que le compte du marcheur IMPLIQUE, contre celui des deux instruments.

    ⭐⭐⭐⭐ C'EST LA FORME QUI SURVIT A UNE FOURCHETTE, ET MA PREMIERE VERSION NE LA PRENAIT PAS.
    J'avais publie « l'erreur en spires » et un verdict « sur-compte aux DEUX instruments » — or
    un marcheur qui compte PARFAITEMENT a 164 µm sur-compte aussi quand on le juge a 182,4, donc
    ce verdict etait satisfait par un marcheur juste. C'est une sonde de la batterie qui l'a dit.
    La quantite qui ne souffre pas de ce defaut est l'espacement IMPLIQUE — etendue divisee par le
    compte — parce qu'elle se compare a la fourchette entiere : au-dessous de 164 le marcheur
    compte trop de feuilles pour la distance, au-dessus de 182,4 pas assez, entre les deux il est
    compatible avec ce que les instruments savent.

    ⭐⭐⭐ ET IL EN FAUT DEUX, PAS UN : l'espacement implique par le RAYON (l'etendue traversee) et
    celui implique par le CHEMIN (la distance parcourue). Le premier dit si le compte s'accorde a
    une traversee radiale, le second a une traversee le long du chemin reel. Les publier tous les
    deux est ce qui empeche de lire une obliquite comme une erreur de comptage.

    ⚠⚠ LE COMPTE DU MARCHEUR EST UNE BORNE INFERIEURE : une fraction en butee dit « au moins »,
    une fraction refusee n'entre pas dans la somme. L'espacement implique est donc une borne
    SUPERIEURE, et un compte juge « trop grand » l'est d'autant plus surement.

    ⚠ L'erreur en spires reste publiee par espacement, parce que c'est la seule forme qui dise
    combien de spires un humain devrait corriger — mais elle ne porte plus le verdict.
    """
    if len(tr) < 3:
        return {"decidable": False, "pourquoi": f"{len(tr)} traversee(s), il en faut trois"}
    imp_r = np.array([x["etendue_radiale_um"] / x["feuilles_comptees"] for x in tr])
    imp_c = np.array([x["chemin_um"] / x["feuilles_comptees"] for x in tr])
    bas, haut = float(min(espacements)), float(max(espacements))
    med_r, med_c = float(np.median(imp_r)), float(np.median(imp_c))
    out = {"decidable": True, "traversees": len(tr),
           "fourchette_des_instruments_um": [bas, haut],
           "espacement_implique_par_le_rayon_um": round(med_r, 1),
           "espacement_implique_par_le_rayon_min": round(float(imp_r.min()), 1),
           "espacement_implique_par_le_rayon_max": round(float(imp_r.max()), 1),
           "espacement_implique_par_le_chemin_um": round(med_c, 1),
           "espacement_implique_par_le_chemin_min": round(float(imp_c.min()), 1),
           "espacement_implique_par_le_chemin_max": round(float(imp_c.max()), 1),
           "marches_dont_le_chemin_tombe_dans_la_fourchette": int(((imp_c >= bas)
                                                                   & (imp_c <= haut)).sum()),
           "par_espacement": []}
    for esp in espacements:
        err = np.array([x["feuilles_comptees"] - x["etendue_radiale_um"] / esp for x in tr])
        out["par_espacement"].append({
            "espacement_um": esp,
            "erreur_mediane_spires": round(float(np.median(err)), 1),
            "erreur_min_spires": round(float(err.min()), 1),
            "erreur_max_spires": round(float(err.max()), 1),
            "marches_qui_sur_comptent": int((err > 0).sum())})
    # ⭐⭐ Les verdicts portent sur la FOURCHETTE ENTIERE, donc un marcheur juste a l'un des deux
    # instruments ne peut pas etre declare fautif.
    out["le_compte_radial_est_sous_la_fourchette"] = bool(med_r < bas)
    out["le_compte_radial_est_au_dessus"] = bool(med_r > haut)
    out["le_compte_du_chemin_est_dans_la_fourchette"] = bool(bas <= med_c <= haut)
    return out


def le_surcomptage_est_il_lobliquite(tr: list[dict], espacement: float = ESPACEMENTS_UM[0]) -> dict:
    """Le sur-comptage vaut-il l'OBLIQUITE du chemin — le marcheur compte-t-il le long du chemin ?

    ⭐⭐⭐⭐ DEUX TESTS QUI DISENT DES CHOSES DIFFERENTES, ET IL FAUT LES DEUX. Le rang dit que les
    deux grandeurs varient ENSEMBLE ; l'appariement dit qu'elles sont EGALES. Une correlation
    parfaite serait compatible avec un facteur deux constant, et un ecart median nul serait
    compatible avec deux nuages qui se croisent. L'un sans l'autre laisserait la conclusion ouverte.

    ⚠⚠ UNE EGALITE NE SE PROUVE PAS PAR UN p GRAND. Un Wilcoxon qui ne rejette pas l'egalite ne
    l'etablit pas — il dit que l'ecart n'est pas distinguable de zero A CETTE TAILLE. Le verdict
    demande donc AUSSI que l'ecart median soit petit devant l'effet : moins d'un dixieme du
    sur-comptage lui-meme, sinon « indiscernable » ne veut rien dire.
    """
    if len(tr) < 6:
        return {"decidable": False, "pourquoi": f"{len(tr)} traversee(s), il en faut six"}
    from scipy import stats  # noqa: PLC0415

    o = np.array([x["obliquite_du_chemin"] for x in tr])
    s = np.array([x["feuilles_comptees"] / (x["etendue_radiale_um"] / espacement) for x in tr])
    par_chemin = np.array([x["feuilles_comptees"] / (x["chemin_um"] / espacement) for x in tr])
    rho, p_rho = stats.spearmanr(o, s)
    d = s - o
    p_app = float(stats.wilcoxon(d).pvalue) if np.any(d) else None
    ecart = float(np.median(d))
    effet = float(np.median(s)) - 1.0
    return {
        "decidable": True, "traversees": len(tr), "espacement_um": espacement,
        "obliquite_mediane": round(float(np.median(o)), 3),
        "sur_comptage_median": round(float(np.median(s)), 3),
        "ecart_median": round(ecart, 4),
        "rho_de_spearman": round(float(rho), 4), "p_du_rang": round(float(p_rho), 8),
        "p_apparie": None if p_app is None else round(p_app, 4),
        # ⭐ La quantite qui dit tout : une feuille par `espacement` de CHEMIN vaudrait 1,000.
        "feuilles_par_espacement_de_chemin": round(float(np.median(par_chemin)), 4),
        "feuilles_par_espacement_de_chemin_min": round(float(par_chemin.min()), 3),
        "feuilles_par_espacement_de_chemin_max": round(float(par_chemin.max()), 3),
        "les_deux_varient_ensemble": bool(p_rho < 0.01 and rho > 0.5),
        "et_elles_sont_egales": bool(p_app is not None and p_app > 0.05
                                     and abs(ecart) < 0.1 * max(abs(effet), 1e-9)),
        "le_marcheur_compte_le_long_du_chemin": bool(
            p_rho < 0.01 and rho > 0.5 and p_app is not None and p_app > 0.05
            and abs(ecart) < 0.1 * max(abs(effet), 1e-9))}


def le_cap_reduit_il_lerreur(tr: list[dict], espacement: float = ESPACEMENTS_UM[0]) -> dict:
    """Apparie bande par bande : le cap reduit-il l'erreur de comptage ?

    ⚠⚠ APPARIE, comme `133` : les deux courses partent des MEMES departs, donc la difference est
    un effet du cap et de rien d'autre. Comparer deux medianes sur deux lots de tailles
    differentes melangerait l'effet du cap et celui de la selection des marches qui sortent.

    ⚠ La comparaison porte sur la VALEUR ABSOLUE de l'erreur : sur-compter de trois spires et en
    sous-compter de trois sont deux façons egales de se tromper de trois spires.
    """
    par_bande: dict[tuple[int, int], dict] = {}
    for x in tr:
        cle = (x["bande"][0], x["bande"][1])
        lam = "avec" if float(x["memoire_du_cap"]) > 0.0 else "sans"
        par_bande.setdefault(cle, {})[lam] = x
    paires = [(k, v["sans"], v["avec"]) for k, v in sorted(par_bande.items())
              if "sans" in v and "avec" in v]
    if len(paires) < 7:
        return {"decidable": False,
                "pourquoi": f"{len(paires)} paire(s), il en faut sept pour qu'un Wilcoxon tranche"}
    from scipy import stats  # noqa: PLC0415

    def err(x):
        return abs(x["feuilles_comptees"] - x["etendue_radiale_um"] / espacement)

    a = np.array([err(s) for _, s, _ in paires])
    b = np.array([err(c) for _, _, c in paires])
    d = b - a
    p = float(stats.wilcoxon(d).pvalue) if np.any(d) else None
    return {"decidable": True, "paires": len(paires), "espacement_um": espacement,
            "erreur_mediane_sans_cap": round(float(np.median(a)), 1),
            "erreur_mediane_avec_cap": round(float(np.median(b)), 1),
            "marches_ou_le_cap_se_trompe_moins": int((b < a).sum()),
            "p_apparie": None if p is None else round(p, 5),
            "detail": [{"bande": list(k), "rayon_mm": s["rayon_mm"],
                        "erreur_sans_cap": round(float(err(s)), 1),
                        "erreur_avec_cap": round(float(err(c)), 1)} for k, s, c in paires],
            "le_cap_reduit_lerreur": bool(p is not None and p < 0.05
                                          and int((b < a).sum()) > len(paires) / 2)}


def la_fixture_tranche_t_elle(angles=(0.0, 20.0, 35.0, 50.0), pas: int = 20,
                              demi: int = 20, graine: int = 3, bruit: float = 8.0) -> dict:
    """Sur une pile dont la normale est CONNUE, le marcheur compte-t-il le chemin ou l'epaisseur ?

    ⭐⭐⭐⭐ C'EST LE CONTROLE QUI SEPARE LES DEUX LECTURES, ET IL EST GRATUIT. Sur le rouleau,
    « le marcheur sur-compte » et « un chemin oblique traverse plus de feuilles » predisent la
    meme chose. Sur une pile plane d'obliquite connue, l'EPAISSEUR traversee est la projection du
    deplacement sur la normale — un nombre exact. Si le compte suit le chemin, c'est le marcheur ;
    s'il suit l'epaisseur, c'est la geometrie du rouleau.

    ⚠⚠⚠ LA DIRECTION EST IMPOSEE, ET C'EST UNE MESURE QUI ME L'A APPRIS. Ma premiere version
    lancait le marcheur sur un axe fixe en croyant que l'obliquite de la PILE ferait l'angle — or
    `marcher` LIT sa direction dans la matiere a chaque pas, donc il se remet aussitot sur la
    normale et son chemin est perpendiculaire par construction : chemin et epaisseur sortaient
    egaux a 0,1 % pour une pile a 35°, et le controle ne distinguait rien. C'etait une
    verification incapable d'echouer, et seule la mesure l'a dit. La direction est donc imposee a
    un angle CONNU de la normale, ce que `marcher` sait faire depuis le temoin naif de `102`.

    ⚠ Le pas reste celui que la matiere dicte : imposer l'avance ferait du compte une consequence
    du reglage.
    """
    from combien_de_pas_la_matiere_porte import VolumeFabrique, marcher  # noqa: PLC0415
    from le_marcheur_reste_t_il_verrouille import _outils  # noqa: PLC0415
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    o = _outils(demi)
    lots = []
    pile = VolumeFabrique(C.PAS_UM, obliquite_deg=0.0, bruit=bruit, graine=graine)
    n_hat = pile.normale
    # ⚠ Un axe du PLAN des feuilles, pour incliner la direction imposee d'un angle connu.
    t_hat = np.array([1.0, 0.0, 0.0])
    for th in angles:
        a_ = np.radians(float(th))
        d_impose = np.cos(a_) * n_hat + np.sin(a_) * t_hat
        dep = np.array([2000.0, 2000.0, 2000.0])
        # ⚠⚠ `interroge_la_matiere=False` EST CE QUI REND LA DIRECTION IMPOSEE EFFECTIVE — sans
        # lui, `marcher` relit sa direction dans la matiere et `direction_imposee` ne sert qu'a
        # fixer le sens. Ma premiere version l'oubliait, et la fixture rendait chemin et epaisseur
        # egaux a 0,1 % : elle ne pouvait pas trancher. ⚠ Le PAS reste celui que la matiere dicte
        # (`pas_impose_um` absent), donc seule la direction est du temoin.
        e = marcher(pile, dep, d_impose, o["longueurs"], o["mu"], o["sd"], o["barre"],
                    o["barre_moities"], o["barre_interstice"], C.VOXEL_FIN_UM,
                    pas_max=pas, demi=demi, interroge_la_matiere=False,
                    direction_imposee=d_impose)
        voyants = [q for q in e if "confirme" in q]
        if len(voyants) < PAS_MINIMUM:
            continue
        compte = float(sum(q["feuilles_franchies"] for q in voyants
                           if q.get("feuilles_franchies") is not None))
        chemin = float(sum(float(q["avance_um"]) for q in voyants))
        p = dep.copy()
        for q in voyants:
            p = p + np.asarray(q["direction"], dtype=float) * (float(q["avance_um"]) / C.VOXEL_FIN_UM)
        # L'EPAISSEUR vraie : la projection du deplacement sur la normale de la pile.
        epaisseur = abs(float((p - dep) @ pile.normale)) * C.VOXEL_FIN_UM
        if epaisseur <= 0.0:
            continue
        lots.append({"angle_a_la_normale_deg": float(th), "pas": len(voyants),
                     "chemin_um": round(chemin, 1), "epaisseur_um": round(epaisseur, 1),
                     "feuilles_comptees": round(compte, 2),
                     "feuilles_attendues_par_epaisseur": round(epaisseur / C.PAS_UM, 2),
                     "feuilles_attendues_par_chemin": round(chemin / C.PAS_UM, 2),
                     "compte_sur_epaisseur": round(compte / (epaisseur / C.PAS_UM), 3),
                     "compte_sur_chemin": round(compte / (chemin / C.PAS_UM), 3),
                     "pas_en_butee": sum(1 for q in voyants if q.get("fraction_en_butee"))})
    if len(lots) < 2:
        return {"decidable": False, "pourquoi": "moins de deux angles exploitables"}
    # ⚠ Le verdict se lit sur les obliquites OBLIQUES : a zero degre chemin et epaisseur sont
    # egaux par construction, donc ce cas ne distingue rien et sert de temoin.
    obl = [x for x in lots if x["angle_a_la_normale_deg"] > 0.0]
    e_ = float(np.median([x["compte_sur_epaisseur"] for x in obl]))
    c_ = float(np.median([x["compte_sur_chemin"] for x in obl]))
    return {"decidable": True, "lots": lots, "angles_obliques": len(obl),
            "compte_sur_epaisseur_median": round(e_, 3),
            "compte_sur_chemin_median": round(c_, 3),
            # ⭐ Le verdict : lequel des deux vaut un ?
            "le_compte_suit_lepaisseur": bool(abs(e_ - 1.0) < abs(c_ - 1.0)),
            "le_compte_suit_le_chemin": bool(abs(c_ - 1.0) < abs(e_ - 1.0))}


def un_zigzag_compte_t_il_double(angles=(0.0, 20.0, 35.0), pas: int = 20, demi: int = 20,
                                 graine: int = 3, bruit: float = 8.0) -> dict:
    """Un chemin qui ALTERNE recompte-t-il les memes feuilles ? — le mecanisme, teste.

    ⭐⭐⭐⭐ POURQUOI CETTE QUESTION EST LA DERNIERE, ET POURQUOI ELLE EST STRUCTURELLE.
    `feuilles_franchies` ajuste une FREQUENCE au profil : une frequence est positive, donc le
    compte d'un pas l'est toujours. Un marcheur qui avance dans la pile puis recule ne peut donc
    pas DECOMPTER — il additionne les deux. La fixture du §4 le montre juste en ligne droite ;
    celle-ci demande ce qu'il devient quand la direction alterne, ce qui est exactement ce que le
    vrai marcheur fait (`132` : le virage reel ALTERNE, cos -0,2061).

    ⚠⚠ LE ZIGZAG EST SYMETRIQUE AUTOUR DE LA NORMALE, donc l'epaisseur nette traversee est la
    MEME qu'en ligne droite a chemin egal : ce qui change est seulement que la direction alterne.
    Un zigzag qui avancerait moins ferait porter a l'alternance ce qui serait une avance moindre.

    ⚠ La direction est imposee, comme au §4, sinon le marcheur se remet sur la normale et il n'y
    a plus d'alternance a mesurer.
    """
    from combien_de_pas_la_matiere_porte import VolumeFabrique, marcher  # noqa: PLC0415
    from le_marcheur_reste_t_il_verrouille import _outils  # noqa: PLC0415
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    o = _outils(demi)
    pile = VolumeFabrique(C.PAS_UM, obliquite_deg=0.0, bruit=bruit, graine=graine)
    n_hat, t_hat = pile.normale, np.array([1.0, 0.0, 0.0])
    lots = []
    for th in angles:
        a_ = np.radians(float(th))
        for alterne in (False, True):
            dep = np.array([2000.0, 2000.0, 2000.0])
            p, compte, chemin, npas = dep.copy(), 0.0, 0.0, 0
            for k in range(int(pas)):
                s = (-1.0 if (alterne and k % 2) else 1.0)
                d = np.cos(a_) * n_hat + s * np.sin(a_) * t_hat
                e = marcher(pile, p, d, o["longueurs"], o["mu"], o["sd"], o["barre"],
                            o["barre_moities"], o["barre_interstice"], C.VOXEL_FIN_UM,
                            pas_max=1, demi=demi, interroge_la_matiere=False,
                            direction_imposee=d)
                q = [x for x in e if "confirme" in x]
                if not q:
                    break
                x = q[0]
                if x.get("feuilles_franchies") is not None:
                    compte += float(x["feuilles_franchies"])
                chemin += float(x["avance_um"])
                npas += 1
                p = p + d * (float(x["avance_um"]) / C.VOXEL_FIN_UM)
            if npas < 4:
                continue
            epaisseur = abs(float((p - dep) @ n_hat)) * C.VOXEL_FIN_UM
            lots.append({"angle_deg": float(th), "alterne": bool(alterne), "pas": npas,
                         "chemin_um": round(chemin, 1), "epaisseur_um": round(epaisseur, 1),
                         "feuilles_comptees": round(compte, 2),
                         "compte_sur_epaisseur": round(compte / (epaisseur / C.PAS_UM), 3)})
    paires = []
    for th in angles:
        d_ = [x for x in lots if x["angle_deg"] == th]
        droit = next((x for x in d_ if not x["alterne"]), None)
        zig = next((x for x in d_ if x["alterne"]), None)
        if droit and zig:
            paires.append({"angle_deg": th,
                           "droit": droit["compte_sur_epaisseur"],
                           "zigzag": zig["compte_sur_epaisseur"],
                           "ecart": round(zig["compte_sur_epaisseur"]
                                          - droit["compte_sur_epaisseur"], 3)})
    if not paires:
        return {"decidable": False, "pourquoi": "aucune paire droit/zigzag exploitable"}
    # ⚠ A angle NUL le zigzag n'existe pas (les deux directions coincident), donc ce cas est le
    # temoin : son ecart doit valoir zero, sinon la mesure bouge pour une raison qui n'est pas
    # l'alternance.
    obl = [x for x in paires if x["angle_deg"] > 0.0]
    temoin = next((x for x in paires if x["angle_deg"] == 0.0), None)
    return {"decidable": True, "lots": lots, "paires": paires,
            "ecart_median_oblique": (round(float(np.median([x["ecart"] for x in obl])), 3)
                                     if obl else None),
            "temoin_a_angle_nul": None if temoin is None else temoin["ecart"],
            "le_zigzag_sur_compte": bool(obl and float(np.median([x["ecart"] for x in obl])) > 0.02
                                         and (temoin is None or abs(temoin["ecart"]) < 0.02))}


def mesurer(cesse_p: Path = CESSE) -> dict:
    cesse = json.loads(cesse_p.read_text(encoding="utf-8"))
    tr = traversees(cesse)
    avec = [x for x in tr if float(x["memoire_du_cap"]) > 0.0]
    sans = [x for x in tr if float(x["memoire_du_cap"]) == 0.0]
    return {
        "source": cesse_p.name, "espacements_um": list(ESPACEMENTS_UM),
        "traversees": tr,
        "retours_radiaux": {"marches": len(tr),
                            "monotones": sum(1 for x in tr if x["retour_radial"] <= 1.001),
                            "retour_max": (round(max(x["retour_radial"] for x in tr), 3)
                                           if tr else None)},
        "lecart_au_compte_geometrique": lecart_au_compte_geometrique(tr),
        "avec_cap": lecart_au_compte_geometrique(avec),
        "sans_cap": lecart_au_compte_geometrique(sans),
        "le_surcomptage_est_il_lobliquite": le_surcomptage_est_il_lobliquite(tr),
        "le_cap_reduit_il_lerreur": le_cap_reduit_il_lerreur(tr),
        "la_fixture_tranche_t_elle": la_fixture_tranche_t_elle(),
        "un_zigzag_compte_t_il_double": un_zigzag_compte_t_il_double()}


def afficher(r: dict) -> None:
    t = r["traversees"]
    rr = r["retours_radiaux"]
    print(f"{len(t)} traversées complètes ({r['source']}) · {rr['monotones']}/{rr['marches']} "
          f"monotones en rayon (retour max {rr['retour_max']})")
    for x in t:
        print(f"   λ {x['memoire_du_cap']} · r {x['rayon_mm']:>5} mm · {x['pas_voyants']:>3} pas · "
              f"étendue {x['etendue_radiale_um']:>7} µm · chemin {x['chemin_um']:>7} · obliquité "
              f"{x['obliquite_du_chemin']:.3f} · comptées {x['feuilles_comptees']:>6}")
    for nom, cle in (("toutes", "lecart_au_compte_geometrique"), ("avec cap", "avec_cap"),
                     ("sans cap", "sans_cap")):
        g = r[cle]
        if not g.get("decidable"):
            print(f"\n{nom} : ⚠ {g['pourquoi']}")
            continue
        print(f"\n★★★ L'ESPACEMENT QUE LE COMPTE IMPLIQUE ({nom}, {g['traversees']} traversées)")
        print(f"   fourchette des deux instruments : {g['fourchette_des_instruments_um']} µm")
        print(f"   par le RAYON  : {g['espacement_implique_par_le_rayon_um']} µm "
              f"[{g['espacement_implique_par_le_rayon_min']} ; "
              f"{g['espacement_implique_par_le_rayon_max']}] · sous la fourchette : "
              f"{g['le_compte_radial_est_sous_la_fourchette']}")
        print(f"   par le CHEMIN : {g['espacement_implique_par_le_chemin_um']} µm "
              f"[{g['espacement_implique_par_le_chemin_min']} ; "
              f"{g['espacement_implique_par_le_chemin_max']}] · dans la fourchette : "
              f"{g['le_compte_du_chemin_est_dans_la_fourchette']} "
              f"({g['marches_dont_le_chemin_tombe_dans_la_fourchette']}/{g['traversees']} marches)")
        for e in g["par_espacement"]:
            print(f"   erreur à {e['espacement_um']} µm : médiane {e['erreur_mediane_spires']:+} "
                  f"spires [{e['erreur_min_spires']:+} ; {e['erreur_max_spires']:+}] · "
                  f"{e['marches_qui_sur_comptent']}/{g['traversees']} sur-comptent")
    o = r["le_surcomptage_est_il_lobliquite"]
    if o.get("decidable"):
        print(f"\n★★★ LE SUR-COMPTAGE EST-IL L'OBLIQUITÉ DU CHEMIN ? "
              f"{'OUI' if o['le_marcheur_compte_le_long_du_chemin'] else 'NON'}")
        print(f"   obliquité médiane {o['obliquite_mediane']} · sur-comptage {o['sur_comptage_median']} "
              f"· écart {o['ecart_median']:+}")
        print(f"   varient ensemble : rho {o['rho_de_spearman']:+}, p {o['p_du_rang']} · "
              f"égales : p apparié {o['p_apparie']}")
        print(f"   ⭐ feuilles par {o['espacement_um']} µm de CHEMIN : "
              f"{o['feuilles_par_espacement_de_chemin']} "
              f"[{o['feuilles_par_espacement_de_chemin_min']} ; "
              f"{o['feuilles_par_espacement_de_chemin_max']}]")
    c = r["le_cap_reduit_il_lerreur"]
    if c.get("decidable"):
        print(f"\n★★★ LE CAP RÉDUIT-IL L'ERREUR ? {'OUI' if c['le_cap_reduit_lerreur'] else 'NON'}")
        print(f"   {c['marches_ou_le_cap_se_trompe_moins']}/{c['paires']} bandes · médiane "
              f"{c['erreur_mediane_sans_cap']} → {c['erreur_mediane_avec_cap']} spires · p "
              f"{c['p_apparie']}")
    f = r["la_fixture_tranche_t_elle"]
    if f.get("decidable"):
        print(f"\n★★★ LA FIXTURE TRANCHE : le compte suit "
              f"{'L ÉPAISSEUR' if f['le_compte_suit_lepaisseur'] else 'LE CHEMIN'}")
        for x in f["lots"]:
            print(f"   angle {x['angle_a_la_normale_deg']:>4}° · {x['pas']:>2} pas · chemin "
                  f"{x['chemin_um']:>7} · épaisseur {x['epaisseur_um']:>7} · comptées "
                  f"{x['feuilles_comptees']:>6} · /épaisseur {x['compte_sur_epaisseur']} · "
                  f"/chemin {x['compte_sur_chemin']}")
        print(f"   médianes sur les {f['angles_obliques']} angles obliques : "
              f"/épaisseur {f['compte_sur_epaisseur_median']} · /chemin "
              f"{f['compte_sur_chemin_median']}")
    z = r.get("un_zigzag_compte_t_il_double", {})
    if z.get("decidable"):
        print(f"\n★★★ UN CHEMIN QUI ALTERNE RECOMPTE-T-IL ? "
              f"{'OUI' if z['le_zigzag_sur_compte'] else 'NON'}")
        for x in z["paires"]:
            print(f"   angle {x['angle_deg']:>4}° · droit {x['droit']} · zigzag {x['zigzag']} · "
                  f"écart {x['ecart']:+}")
        print(f"   écart médian sur les angles obliques {z['ecart_median_oblique']:+} · "
              f"témoin à angle nul {z['temoin_a_angle_nul']:+}")


def verifier() -> int:
    echecs = controles = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # === LES TRAVERSEES, SUR UNE COURSE FABRIQUEE ===========================================
    import tempfile  # noqa: PLC0415

    def course(nom, lam, marches):
        lignes = []
        for i, (r0, npas, dz, fr) in enumerate(marches):
            e = [{"pas": k + 1, "confirme": True, "oriente": True, "rien_lu": False,
                  "desaccord_des_moities_deg": 3.0, "planarite": 0.4, "score_du_balayage": 1.0,
                  "accord_de_linterstice": 0.9, "direction": [0.0, 0.0, 1.0],
                  "feuilles_franchies": fr, "fraction_en_butee": False,
                  "avance_um": 164.0, "parcouru_um": 164.0 * (k + 1)} for k in range(npas)]
            lignes.append({"de": 10 * i, "a": 10 * i + 9, "rayon_mm": r0, "detail": [{
                "depart_zyx": [0.0, 0.0, r0 * 1000.0 / VOXEL_UM], "radial_zyx": [0.0, 0.0, 1.0],
                "etapes": e, "pas_parcourus": npas, "pas_confirmes": npas,
                "sortie": False, "plus_rien_a_lire": True, "au_plafond": False}]})
        return {"source": nom, "memoire_du_cap": lam, "arrets": [
            {"marche": i, "axe_zyx": [0.0, 0.0, 0.0],
             "verdict": {"decidable": True, "sorti_du_rouleau": True}}
            for i in range(len(marches))], "lignes": lignes}

    with tempfile.TemporaryDirectory() as dtmp:
        r = Path(dtmp) / "docs" / "mesures"
        r.mkdir(parents=True)
        # une marche droite de 20 pas de 164 µm : étendue 3280 µm, 20 feuilles comptées
        a = course("a.json", 0.75, [(5.0, 20, 1.0, 1.0), (7.0, 20, 1.0, 1.0)])
        (r / "a.json").write_text(json.dumps(a))
        cesse = {"par_course": [{"source": "a.json", "memoire_du_cap": 0.75,
                                 "arrets": a["arrets"]}]}
        tr = traversees(cesse, racine=Path(dtmp))
        v("une marche droite rend son étendue et son chemin", len(tr) == 2
          and abs(tr[0]["etendue_radiale_um"] - 3280.0) < 1.0
          and abs(tr[0]["chemin_um"] - 3280.0) < 1.0, f"{tr[0] if tr else None}")
        v("... et son obliquité vaut un", abs(tr[0]["obliquite_du_chemin"] - 1.0) < 0.01)
        v("... et son retour radial aussi", abs(tr[0]["retour_radial"] - 1.0) < 0.01)
        v("... et le compte est la somme des fractions", tr[0]["feuilles_comptees"] == 20.0)

    # === L'ECART AU COMPTE GEOMETRIQUE =======================================================
    def trav(etendue, chemin, compte, lam=0.75, bande=(0, 1), r0=5.0, npas=20, retour=1.0):
        return {"course": "x.json", "memoire_du_cap": lam, "bande": list(bande), "rayon_mm": r0,
                "pas_voyants": npas, "etendue_radiale_um": etendue,
                "etendue_radiale_parcourue_um": etendue * retour, "retour_radial": retour,
                "chemin_um": chemin, "obliquite_du_chemin": round(chemin / etendue, 3),
                "feuilles_comptees": compte, "pas_en_butee": 0,
                "fraction_par_pas": round(compte / npas, 4)}

    # un marcheur PARFAIT à 164 µm : il compte exactement étendue/164
    parfait = [trav(3280.0, 3280.0, 20.0), trav(4920.0, 4920.0, 30.0), trav(1640.0, 1640.0, 10.0)]
    g = lecart_au_compte_geometrique(parfait)
    v("un marcheur parfait à 164 µm implique un espacement de 164",
      g["decidable"] and abs(g["espacement_implique_par_le_rayon_um"] - 164.0) < 0.5,
      f"{g['espacement_implique_par_le_rayon_um']} µm")
    # ⚠⚠⚠ LA SONDE QUI A FAIT REECRIRE CE VERDICT : un marcheur JUSTE à 164 sur-compte de six
    # spires quand on le juge à 182,4 — donc « sur-compte aux deux instruments » était satisfait
    # par un marcheur sans défaut. Le verdict porte désormais sur la FOURCHETTE, et un marcheur
    # juste à l'un des deux n'y est jamais déclaré fautif.
    v("... et il sur-compte quand on le juge à 182,4 µm",
      g["par_espacement"][1]["erreur_mediane_spires"] > 1.0,
      f"{g['par_espacement'][1]['erreur_mediane_spires']:+} spires")
    v("... et pourtant il n'est PAS déclaré sous la fourchette",
      not g["le_compte_radial_est_sous_la_fourchette"])
    gros = [trav(3280.0, 3280.0, 30.0), trav(4920.0, 4920.0, 45.0), trav(1640.0, 1640.0, 15.0)]
    g2 = lecart_au_compte_geometrique(gros)
    v("un marcheur qui compte moitié trop tombe SOUS la fourchette",
      g2["le_compte_radial_est_sous_la_fourchette"],
      f"{g2['espacement_implique_par_le_rayon_um']} µm pour [164 ; 182,4]")
    maigre = [trav(3280.0, 3280.0, 15.0), trav(4920.0, 4920.0, 22.0), trav(1640.0, 1640.0, 7.0)]
    v("... et un marcheur qui compte trop peu est AU-DESSUS",
      lecart_au_compte_geometrique(maigre)["le_compte_radial_est_au_dessus"])
    # ⭐ Un marcheur juste LE LONG DE SON CHEMIN, sur des marches obliques : son espacement radial
    # tombe sous la fourchette alors que celui de son chemin y est. Sans les deux quantités, cette
    # marche serait déclarée fautive.
    obliques = [trav(3280.0, 3280.0 * 1.2, round(3280.0 * 1.2 / 170.0, 2)),
                trav(4920.0, 4920.0 * 1.2, round(4920.0 * 1.2 / 170.0, 2)),
                trav(1640.0, 1640.0 * 1.2, round(1640.0 * 1.2 / 170.0, 2))]
    g3 = lecart_au_compte_geometrique(obliques)
    v("un marcheur juste le long de son chemin : radial sous la fourchette, chemin dedans",
      g3["le_compte_radial_est_sous_la_fourchette"]
      and g3["le_compte_du_chemin_est_dans_la_fourchette"],
      f"rayon {g3['espacement_implique_par_le_rayon_um']} · chemin "
      f"{g3['espacement_implique_par_le_chemin_um']}")
    v("moins de trois traversées est indécidable",
      not lecart_au_compte_geometrique(parfait[:2])["decidable"])

    # === LE SUR-COMPTAGE EST-IL L'OBLIQUITE ? ================================================
    # un marcheur qui compte UNE feuille par 164 µm de CHEMIN : son sur-comptage EST l'obliquité
    rng = np.random.default_rng(5)
    le_chemin = []
    for i in range(12):
        ete = 3000.0 + 300.0 * i
        obl = 1.0 + 0.05 * (i % 5) + float(rng.normal(0, 0.01))
        ch = ete * obl
        le_chemin.append(trav(round(ete, 1), round(ch, 1), round(ch / 164.0, 2)))
    o = le_surcomptage_est_il_lobliquite(le_chemin)
    v("un marcheur qui compte le long du chemin est reconnu",
      o["decidable"] and o["le_marcheur_compte_le_long_du_chemin"],
      f"rho {o['rho_de_spearman']}, p apparié {o['p_apparie']}, écart {o['ecart_median']:+}")
    v("... et sa quantité vaut un", abs(o["feuilles_par_espacement_de_chemin"] - 1.0) < 0.01,
      f"{o['feuilles_par_espacement_de_chemin']}")
    # ⭐⭐ LA SONDE : un marcheur qui compte le long de l'EPAISSEUR ne doit PAS être reconnu.
    lepaisseur = [trav(x["etendue_radiale_um"], x["chemin_um"],
                       round(x["etendue_radiale_um"] / 164.0, 2)) for x in le_chemin]
    o2 = le_surcomptage_est_il_lobliquite(lepaisseur)
    v("sonde : un marcheur qui compte l'épaisseur n'est PAS dit compter le chemin",
      not o2["le_marcheur_compte_le_long_du_chemin"],
      f"sur-comptage {o2['sur_comptage_median']} pour une obliquité de {o2['obliquite_mediane']}")
    # ⚠ Et un marcheur qui compte DEUX fois le chemin : les deux varient ensemble mais ne sont
    # PAS égales — c'est ce que l'appariement attrape et que le rang seul laisserait passer.
    double = [trav(x["etendue_radiale_um"], x["chemin_um"], x["feuilles_comptees"] * 2.0)
              for x in le_chemin]
    o3 = le_surcomptage_est_il_lobliquite(double)
    v("sonde : un facteur deux constant est vu par l'appariement, pas par le rang",
      o3["les_deux_varient_ensemble"] and not o3["et_elles_sont_egales"],
      f"rho {o3['rho_de_spearman']}, p apparié {o3['p_apparie']}")
    v("moins de six traversées est indécidable",
      not le_surcomptage_est_il_lobliquite(le_chemin[:5])["decidable"])

    # === LE CAP =============================================================================
    paires = []
    for i in range(9):
        b = (10 * i, 10 * i + 9)
        paires.append(trav(3280.0, 3280.0 * 1.4, 28.0, lam=0.0, bande=b, r0=4.0 + i))
        paires.append(trav(3280.0, 3280.0 * 1.05, 21.0, lam=0.75, bande=b, r0=4.0 + i))
    cc = le_cap_reduit_il_lerreur(paires)
    v("le cap qui se trompe moins est vu", cc["decidable"] and cc["le_cap_reduit_lerreur"],
      f"{cc['marches_ou_le_cap_se_trompe_moins']}/{cc['paires']}, p {cc['p_apparie']}")
    inverse = [dict(x, memoire_du_cap=0.75 if x["memoire_du_cap"] == 0.0 else 0.0) for x in paires]
    v("sonde : les deux courses inversées ne donnent PAS un cap qui aide",
      not le_cap_reduit_il_lerreur(inverse)["le_cap_reduit_lerreur"])
    v("six paires sont indécidables plutôt qu'un « non »",
      not le_cap_reduit_il_lerreur(paires[:12])["decidable"])

    # === LA FIXTURE QUI TRANCHE ==============================================================
    f = la_fixture_tranche_t_elle(angles=(0.0, 35.0), pas=8)
    v("la fixture rend un lot par angle", f["decidable"] and len(f["lots"]) == 2)
    v("... et à angle nul chemin et épaisseur coïncident",
      abs(f["lots"][0]["chemin_um"] - f["lots"][0]["epaisseur_um"]) < 0.05 * f["lots"][0]["chemin_um"],
      f"{f['lots'][0]['chemin_um']} contre {f['lots'][0]['epaisseur_um']}")
    # ⚠⚠ LE CONTROLE DU CONTROLE : si le chemin n'était pas réellement oblique, les deux
    # quantités coïncideraient et la fixture ne trancherait rien. C'est ce qui est arrivé à ma
    # première version, qui laissait le marcheur lire sa direction.
    v("... et à 35° ils diffèrent, sinon le contrôle ne distinguerait rien",
      f["lots"][1]["chemin_um"] > 1.1 * f["lots"][1]["epaisseur_um"],
      f"{f['lots'][1]['chemin_um']} contre {f['lots'][1]['epaisseur_um']}")
    v("... et l'épaisseur vaut le chemin fois le cosinus de l'angle imposé",
      abs(f["lots"][1]["epaisseur_um"] - f["lots"][1]["chemin_um"] * np.cos(np.radians(35.0)))
      < 0.02 * f["lots"][1]["chemin_um"],
      f"{f['lots'][1]['epaisseur_um']} pour {f['lots'][1]['chemin_um'] * np.cos(np.radians(35.0)):.1f}")
    v("... et le verdict nomme l'un des deux",
      f["le_compte_suit_lepaisseur"] != f["le_compte_suit_le_chemin"],
      f"épaisseur {f['compte_sur_epaisseur_median']} · chemin {f['compte_sur_chemin_median']}")

    # === LE ZIGZAG ===========================================================================
    z = un_zigzag_compte_t_il_double(angles=(0.0, 35.0), pas=10)
    v("le zigzag rend une paire par angle", z["decidable"] and len(z["paires"]) == 2)
    # ⚠⚠ LE TEMOIN : à angle nul les deux chemins sont le MÊME, donc l'écart doit être nul. Sans
    # lui, un écart mesuré pourrait venir de n'importe quoi d'autre que l'alternance.
    v("... et le témoin à angle nul ne bouge pas", abs(z["temoin_a_angle_nul"]) < 0.02,
      f"{z['temoin_a_angle_nul']:+}")
    v("... et le verdict nomme ce qu'il a vu",
      isinstance(z["le_zigzag_sur_compte"], bool),
      f"écart oblique {z['ecart_median_oblique']:+}")

    # ⚠ Le chemin qui produit le nombre publié est ATTEINT, en petit : la mesure assemblée tourne
    # sur les vraies courses si elles sont là, et son affichage avec. Une batterie qui teste les
    # briques sans jamais les assembler ne peut pas échouer là où ça compte.
    if CESSE.is_file():
        import contextlib, io  # noqa: PLC0415
        r = mesurer()
        v("la mesure assemblée rend des traversées", len(r["traversees"]) > 0,
          f"{len(r['traversees'])}")
        v("... et les quatre verdicts",
          all(r[k].get("decidable") for k in ("lecart_au_compte_geometrique",
                                              "le_surcomptage_est_il_lobliquite",
                                              "le_cap_reduit_il_lerreur",
                                              "la_fixture_tranche_t_elle")))
        tampon = io.StringIO()
        with contextlib.redirect_stdout(tampon):
            afficher(r)
        v("... et l'affichage tourne dessus", "LA FIXTURE TRANCHE" in tampon.getvalue())

    print(f"\n{'ALL PASS' if echecs == 0 else 'ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--cesse", type=Path, default=CESSE)
    p.add_argument("--json", type=Path, default=None)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(a.cesse)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False))
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
