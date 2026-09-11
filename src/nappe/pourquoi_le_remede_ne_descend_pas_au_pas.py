#!/usr/bin/env python3
"""Pourquoi le remede de `111` ne descend pas au PAS — et ou il redevient possible.

⚠⚠⚠ POURQUOI CE FICHIER. `111` a repare l'estimateur du TRAJET en bornant sa bande par des
longueurs d'onde physiques, et la comptabilite d'enroulement marche partout. Mais la PORTEE du
marcheur — un pas confirme, six cents micrometres — n'a pas bouge, et elle depend d'un autre
instrument : le critere de `98` applique au segment d'UN pas. La question qui suit est donc
immediate : le meme remede repare-t-il aussi le critere par pas ?

⛔⛔⛔ NON, ET CE N'EST PAS UN MANQUE D'EFFORT : c'est la RESOLUTION de la fenetre. Un segment d'un
pas fait une periode, donc sa base de Fourier a pour plus basse frequence non nulle EXACTEMENT le
signal. Une derive de longueur d'onde superieure a `lambda_max` n'y est pas REPRESENTABLE : elle ne
se distingue pas d'un decalage constant plus le signal lui-meme. Il n'y a donc rien a retirer, et
la contamination qu'elle cause est irreductible.

⚠⚠⚠ ET J'AI ECHOUE DEUX FOIS AVANT DE LE COMPRENDRE, CHAQUE FOIS SUR LA BASE ET NON SUR LA
MATIERE. Un detrendage POLYNOMIAL de degre deux absorbe **96 %** du gabarit a un pas : ce n'est pas
un sous-espace de basse frequence, c'est un sous-espace qui contient le signal. Et une grille
harmonique non orthogonale est si mal conditionnee qu'une decomposition en rend un espace plus
grand que le sien. La seule base honnete est celle de Fourier SUR LA FENETRE, exactement
orthonormee, ou il n'y a rien a choisir.

⭐⭐⭐ ET LE REMEDE REDEVIENT POSSIBLE DES DEUX PAS. `f_lo = L / lambda_max` vaut 0,66 a un pas et
1,33 a deux : le premier mode a retirer apparait exactement quand la fenetre depasse
`lambda_max`. C'est une consequence de conception, pas une opinion — confirmer sur une fenetre de
plusieurs pas a quelque chose a nettoyer, confirmer pas a pas n'a rien.

Usage :
    uv run python src/nappe/pourquoi_le_remede_ne_descend_pas_au_pas.py --verifier
    uv run python src/nappe/pourquoi_le_remede_ne_descend_pas_au_pas.py \\
        --json docs/mesures/pourquoi_le_remede_ne_descend_pas_au_pas.json
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

PROFILS = RACINE / "docs" / "mesures" / "une_bande_qui_ne_bouge_pas_avec_la_fenetre.json"
SELECTEURS = ("calibre", "deux_roles")
FENETRES = (1, 2, 3, 4, 6)
TIRAGES_DU_NUL = 3000
GRAINE = 112


def modes_sous_le_signal(longueur_um: float, pas_dans_la_fenetre: int,
                         lambda_max_um: float) -> dict:
    """Quels modes de Fourier de la fenetre sont SOUS le signal, donc retirables ?

    ⭐⭐⭐ C'EST TOUTE LA TRANCHE EN UNE FONCTION, ET ELLE N'A AUCUN PARAMETRE A REGLER. La base de
    Fourier d'une fenetre est exactement orthonormee et ses modes sont les entiers `j` = nombre de
    periodes sur la fenetre. « Longueur d'onde superieure a `lambda_max` » se lit donc
    `j < f_lo = L / lambda_max`, et le signal d'un marcheur qui franchit une feuille par pas est le
    mode `j = k`, ou `k` est le nombre de pas.

    ⚠⚠⚠ ET LES DEUX NE SE RENCONTRENT JAMAIS : `f_lo = k * avance / lambda_max` et l'avance est
    bornee par `lambda_max`, donc `f_lo < k` toujours. Retirer les modes bas est exactement
    orthogonal au signal, a TOUTE longueur — ce qui rend le remede de `111` exact, et non
    approche.

    ⛔⛔ MAIS A UN PAS LA LISTE EST VIDE. `f_lo` vaut alors moins de un, donc aucun mode non nul
    n'est sous le signal : le premier mode de la fenetre EST le signal. Une derive plus longue que
    la fenetre n'y est pas representable, donc elle n'est pas retirable — et sa contamination est
    irreductible.
    """
    if lambda_max_um <= 0.0 or longueur_um <= 0.0 or pas_dans_la_fenetre < 1:
        raise ValueError("une fenetre a une longueur et un compte de pas strictement positifs")
    f_lo = longueur_um / lambda_max_um
    a_retirer = [j for j in range(1, int(np.floor(f_lo)) + 1)]
    return {"longueur_um": round(float(longueur_um), 1),
            "pas": int(pas_dans_la_fenetre),
            "f_lo": round(float(f_lo), 4),
            "modes_a_retirer": a_retirer,
            "mode_du_signal": int(pas_dans_la_fenetre),
            # ⚠ Le controle qui doit TOUJOURS tenir : le signal n'est jamais dans ce qu'on retire.
            "le_signal_est_hors_de_ce_quon_retire": bool(
                pas_dans_la_fenetre not in a_retirer),
            "il_y_a_quelque_chose_a_retirer": bool(a_retirer)}


def retirer_les_modes_bas(v: np.ndarray, modes) -> np.ndarray:
    """Retire du profil les modes de Fourier listes, par projection orthogonale.

    ⚠ Les modes de la fenetre sont orthogonaux entre eux ET au signal, donc les retirer un par un
    est exact : il n'y a ni ordre ni conditionnement a surveiller, contrairement a une grille de
    frequences non entieres.
    """
    n = v.size
    t = np.linspace(0.0, 1.0, n)
    z = np.asarray(v, dtype=np.float64).copy()
    for j in modes:
        for base in (np.cos(2.0 * np.pi * j * t), np.sin(2.0 * np.pi * j * t)):
            b = base - base.mean()
            d = float(b @ b)
            if d > 1e-12:
                z = z - (float(z @ b) / d) * b
    return z


def lorthogonalite_est_elle_exacte(lambda_max_um: float, avance_um: float,
                                   fenetres=FENETRES,
                                   echantillons_par_pas: int = 73) -> dict:
    """L'orthogonalite des modes bas au signal est-elle EXACTE, et sur quelle grille ?

    ⚠⚠⚠ ELLE EXISTE PARCE QUE J'AI ECRIT « EXACTEMENT ORTHOGONAL » ET QUE LA BATTERIE M'A REPRIS.
    Une base de Fourier est exactement orthogonale sur la grille DFT — `n` points, extremite
    EXCLUE. Or les profils que `111` a gardes font `73k + 1` points, extremite INCLUSE : le
    premier et le dernier echantillon d'une fenetre sont a la meme phase, donc la grille n'est
    plus celle ou l'orthogonalite est exacte.

    ⭐ LA MESURE DIT DE COMBIEN : zero a la precision machine sur la grille DFT, et au pire
    **1,3 %** sur la grille a extremite incluse, decroissant comme `1/n`. C'est soixante-dix fois
    moins que ce qu'un polynome de degre deux absorbe a un pas, donc la conclusion tient — mais
    « exact » etait faux et le chiffre remplace le mot.
    """
    lignes = []
    for k in fenetres:
        n = k * echantillons_par_pas + 1
        f_lo = k * avance_um / lambda_max_um
        modes = [j for j in range(1, int(np.floor(f_lo)) + 1)]
        pires = {"incluse": 0.0, "dft": 0.0}
        for nom, u, t in (("incluse", np.linspace(0.0, 1.0, n),
                           np.linspace(0.0, float(k), n)),
                          ("dft", np.arange(n - 1) / (n - 1),
                           np.arange(n - 1) / (n - 1) * k)):
            g = np.cos(2.0 * np.pi * t)
            g = g - g.mean()
            nz = np.linalg.norm(g)
            if nz < 1e-12:
                continue
            g = g / nz
            for j in modes:
                for base in (np.cos(2.0 * np.pi * j * u), np.sin(2.0 * np.pi * j * u)):
                    b = base - base.mean()
                    nb = np.linalg.norm(b)
                    if nb > 1e-12:
                        pires[nom] = max(pires[nom], abs(float(g @ (b / nb))))
        lignes.append({"pas": k, "modes": modes,
                       "recouvrement_grille_incluse": float(f"{pires['incluse']:.3e}"),
                       "recouvrement_grille_dft": float(f"{pires['dft']:.3e}")})
    avec = [x for x in lignes if x["modes"]]
    return {"par_fenetre": lignes,
            "pire_sur_la_grille_incluse": max(
                (x["recouvrement_grille_incluse"] for x in avec), default=0.0),
            "pire_sur_la_grille_dft": max(
                (x["recouvrement_grille_dft"] for x in avec), default=0.0),
            # ⭐⭐ LES DEUX VERDICTS, ET C'EST LEUR ECART QUI EST LE RESULTAT.
            "exacte_sur_la_grille_dft": bool(
                max((x["recouvrement_grille_dft"] for x in avec), default=0.0) < 1e-12),
            "approchee_sur_la_grille_incluse": bool(
                0.0 < max((x["recouvrement_grille_incluse"] for x in avec), default=0.0) < 0.02),
            "et_elle_decroit_avec_la_fenetre": bool(
                len(avec) > 1
                and avec[-1]["recouvrement_grille_incluse"]
                < avec[0]["recouvrement_grille_incluse"])}


def part_absorbee(colonnes: np.ndarray, gabarit: np.ndarray,
                  tolerance: float = 1e-6) -> dict:
    """Quelle part du gabarit un sous-espace absorbe-t-il — PAR SVD, jamais par QR.

    ⚠⚠⚠ ELLE EXISTE PARCE QUE MA PREMIERE VERSION UTILISAIT `qr`, ET C'EST FAUX SUR UNE BASE MAL
    CONDITIONNEE : `qr` rend des colonnes orthonormees dont l'espace DEPASSE celui de la matrice
    quand celle-ci est quasi-degeneree, donc elle absorbait 100 % de tout, a toute longueur. La
    decomposition en valeurs singulieres avec une tolerance DECLAREE rend le rang reel.

    ⚠ La tolerance est relative a la plus grande valeur singuliere et vaut un millionieme : plus
    serre, on garde des directions numeriquement vides ; plus lache, on jette du signal reel.
    """
    u, s, _ = np.linalg.svd(np.asarray(colonnes, dtype=np.float64), full_matrices=False)
    if s.size == 0:
        return {"part": 0.0, "rang": 0, "colonnes": 0}
    rang = int((s > tolerance * max(float(s[0]), 1e-300)).sum())
    g = np.asarray(gabarit, dtype=np.float64)
    return {"part": round(float(np.linalg.norm(u[:, :rang].T @ g)), 4),
            "rang": rang, "colonnes": int(np.asarray(colonnes).shape[1])}


def gabarit_de_la_fenetre(pas: int, echantillons_par_pas: int) -> np.ndarray:
    """Le profil attendu d'une fenetre de `pas` pas qui franchit une feuille par pas."""
    n = pas * echantillons_par_pas + 1
    t = np.linspace(0.0, float(pas), n)
    g = np.cos(2.0 * np.pi * t)
    g = g - g.mean()
    return g / np.linalg.norm(g)


def pourquoi_les_autres_bases_echouent(lambda_max_um: float, avance_um: float,
                                       fenetres=FENETRES,
                                       echantillons_par_pas: int = 73) -> dict:
    """Les deux bases que j'ai essayees avant, et ce qu'elles absorbent du signal.

    ⭐⭐ ELLES SONT PUBLIEES PLUTOT QUE TUES, parce que leur echec est ce qui designe la bonne
    base. Un detrendage POLYNOMIAL n'est pas un sous-espace de basse frequence : au degre deux il
    absorbe presque tout le gabarit d'UN pas, donc il repare la contamination en detruisant ce
    qu'il devait garder. Et une grille harmonique a frequences NON ENTIERES n'est pas orthogonale
    sur la fenetre, donc elle mord sur le signal et son conditionnement rend le calcul fragile.
    """
    out = {"polynomial": [], "harmonique_non_entiere": []}
    for k in fenetres:
        n = k * echantillons_par_pas + 1
        u = np.linspace(0.0, 1.0, n)
        g = gabarit_de_la_fenetre(k, echantillons_par_pas)
        ligne = {"pas": k}
        for deg in (1, 2, 3):
            ligne[f"degre_{deg}"] = part_absorbee(
                np.vander(u, deg + 1, increasing=True), g)["part"]
        out["polynomial"].append(ligne)
        f_lo = k * avance_um / lambda_max_um
        cols = [np.ones(n)]
        for f in np.arange(0.1, f_lo + 1e-9, 0.1):
            cols += [np.cos(2.0 * np.pi * f * u), np.sin(2.0 * np.pi * f * u)]
        a = part_absorbee(np.column_stack(cols), g)
        out["harmonique_non_entiere"].append({"pas": k, "f_lo": round(float(f_lo), 3), **a})
    # ⭐ ET LA BONNE BASE, POUR COMPARAISON : les modes ENTIERS de la fenetre absorbent ZERO.
    out["fourier_de_la_fenetre"] = []
    for k in fenetres:
        n = k * echantillons_par_pas + 1
        u = np.linspace(0.0, 1.0, n)
        g = gabarit_de_la_fenetre(k, echantillons_par_pas)
        m = modes_sous_le_signal(k * avance_um, k, lambda_max_um)
        cols = [np.ones(n)]
        for j in m["modes_a_retirer"]:
            cols += [np.cos(2.0 * np.pi * j * u), np.sin(2.0 * np.pi * j * u)]
        out["fourier_de_la_fenetre"].append(
            {"pas": k, "modes": m["modes_a_retirer"],
             **part_absorbee(np.column_stack(cols), g)})
    poly = out["polynomial"][0]
    return {**out,
            # ⭐⭐⭐ LES TROIS VERDICTS, chacun capable de dire non.
            "le_polynome_de_degre_deux_detruit_le_gabarit_a_un_pas": bool(
                poly["degre_2"] > 0.5),
            "la_grille_non_entiere_mord_sur_le_signal": bool(
                max(x["part"] for x in out["harmonique_non_entiere"]) > 0.5),
            # ⚠⚠ « ORTHOGONALE » EST MESUREE SUR LA GRILLE REELLEMENT UTILISEE, celle a extremite
            # incluse, ou elle vaut au pire quelques centiemes et non zero. Le seuil est deux
            # pour cent : dix fois plus que la pire valeur mesuree, et cinquante fois moins que
            # ce que la pire des deux autres bases absorbe.
            "la_base_de_fourier_est_quasi_orthogonale_au_signal": bool(
                max(x["part"] for x in out["fourier_de_la_fenetre"]) < 0.02),
            "part_absorbee_par_fourier": round(
                max(x["part"] for x in out["fourier_de_la_fenetre"]), 4)}


def la_contamination_est_irreductible(avance_um: float, lambda_max_um: float,
                                      echantillons_par_pas: int = 73,
                                      derives=(0.2, 0.3, 0.5, 0.66, 1.0),
                                      amplitude: float = 1.5,
                                      graine: int = GRAINE) -> dict:
    """A UN pas, retirer les modes bas ne change rien — parce qu'il n'y en a aucun.

    ⭐⭐⭐ C'EST LA DEMONSTRATION, ET ELLE SE LIT SANS MODELE : sur un segment d'un pas, l'accord
    chute quand une derive s'ajoute, et il vaut EXACTEMENT LE MEME apres retrait des modes sous le
    signal. Non pas parce que le retrait est mal fait, mais parce que la liste des modes est vide.

    ⚠ Les derives sont donnees en periodes PAR FENETRE, donc `f = 0,3` veut dire une longueur
    d'onde de trois fois et un tiers la fenetre. Toutes celles listees sont sous un, donc toutes
    sont plus longues que la fenetre.
    """
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    n = echantillons_par_pas
    t = np.linspace(0.0, 1.0, n)
    rng = np.random.default_rng(graine)
    m = modes_sous_le_signal(avance_um, 1, lambda_max_um)
    lignes = []
    for f in derives:
        v = (100.0 + 40.0 * np.cos(2.0 * np.pi * t)
             + 40.0 * amplitude * np.cos(2.0 * np.pi * f * t + 0.4)
             + rng.normal(0.0, 5.0, n))
        a_brut = float(C.accord(v.reshape(1, -1))[2][0])
        a_net = float(C.accord(
            retirer_les_modes_bas(v, m["modes_a_retirer"]).reshape(1, -1))[2][0])
        lignes.append({"derive_en_periodes_par_fenetre": f,
                       "longueur_donde_um": round(avance_um / f, 1),
                       "accord_brut": round(a_brut, 4),
                       "accord_apres_retrait": round(a_net, 4),
                       "gain": round(a_net - a_brut, 4)})
    propre = float(C.accord((100.0 + 40.0 * np.cos(2.0 * np.pi * t)).reshape(1, -1))[2][0])
    return {"avance_um": avance_um, "modes_a_retirer": m["modes_a_retirer"],
            "accord_sans_derive": round(propre, 4), "par_derive": lignes,
            "contamination_max": round(propre - min(x["accord_brut"] for x in lignes), 4),
            # ⭐⭐⭐ LE VERDICT : le retrait ne rend RIEN, et la raison est que la liste est vide.
            "le_retrait_ne_change_rien": bool(
                all(abs(x["gain"]) < 1e-9 for x in lignes)),
            "parce_que_la_liste_est_vide": not m["il_y_a_quelque_chose_a_retirer"]}


def a_partir_de_quelle_fenetre(avance_um: float, lambda_max_um: float,
                               fenetres=FENETRES) -> dict:
    """A partir de combien de pas y a-t-il quelque chose a retirer ?

    ⭐⭐⭐ C'EST LA CONSEQUENCE DE CONCEPTION, et elle tombe d'une inegalite plutot que d'un essai :
    le premier mode retirable apparait quand `L >= lambda_max`, c'est-a-dire des que la fenetre
    depasse le plus grand espacement de feuille plausible. Confirmer sur une fenetre de plusieurs
    pas a donc quelque chose a nettoyer ; confirmer pas a pas n'a rien.
    """
    lignes = [modes_sous_le_signal(k * avance_um, k, lambda_max_um) for k in fenetres]
    premier = next((x["pas"] for x in lignes if x["il_y_a_quelque_chose_a_retirer"]), None)
    return {"par_fenetre": lignes, "premiere_fenetre_nettoyable": premier,
            "seuil_en_micrometres": round(float(lambda_max_um), 1),
            "seuil_en_pas": round(float(lambda_max_um) / float(avance_um), 3),
            # ⚠ Le signal doit rester hors de ce qu'on retire a TOUTE longueur, sinon le remede
            # mangerait ce qu'il doit garder.
            "le_signal_reste_toujours_hors_du_retrait": bool(
                all(x["le_signal_est_hors_de_ce_quon_retire"] for x in lignes))}


def famille_de_la_fenetre(pas: int, echantillons: int):
    """La famille de gabarits d'une fenetre de `pas` pas — la generalisation fidele de `98`.

    ⚠⚠ `98` teste 1, 2 ou 3 interstices sur un segment d'UN pas : le pas peut en traverser un,
    deux ou trois. Sur une fenetre de `k` pas, les memes trois hypotheses deviennent `k`, `2k` et
    `3k`. Prendre `k-1, k, k+1` serait une autre famille, celle d'un pas qui derive un peu, et ce
    n'est PAS ce que `98` teste — la substituer changerait la question sans le dire.
    """
    n = pas * echantillons + 1
    t = np.linspace(0.0, float(pas), n)
    out = []
    for m in (1, 2, 3):
        g = np.cos(2.0 * np.pi * m * t)
        g = g - g.mean()
        g = g / np.linalg.norm(g)
        out.append((m * pas, g))
        out.append((m * pas, -g))
    return out


def accord_sur_la_fenetre(v: np.ndarray, famille) -> tuple[float, int]:
    """Le meilleur accord de la famille, et le compte d'interstices qu'il designe."""
    z = np.asarray(v, dtype=np.float64)
    z = z - z.mean()
    n = float(np.linalg.norm(z))
    if n < 1e-12:
        return 0.0, 0
    z = z / n
    best = (-2.0, 0)
    for combien, g in famille:
        s = float(z @ g)
        if s > best[0]:
            best = (s, combien)
    return best


def barre_de_la_fenetre(pas: int, modes, echantillons: int,
                        tirages: int = TIRAGES_DU_NUL, graine: int = GRAINE) -> dict:
    """Ce que la famille de la fenetre rend sur du bruit pur, AVANT et APRES retrait des modes.

    ⭐⭐⭐ ELLE EXISTE PARCE QUE RETIRER DES MODES CHANGE LA FAMILLE, donc sa barre. Reprendre celle
    de `98` apres avoir retire trois modes serait donner a une forme la barre d'une autre — la
    faute que ce depot a deja recensee. Et le sens du changement est publie : retirer des
    directions LAISSE MOINS DE PLACE au bruit, donc la barre devrait monter.
    """
    rng = np.random.default_rng(graine + pas)
    fam = famille_de_la_fenetre(pas, echantillons)
    n = pas * echantillons + 1
    brut, net = [], []
    for _ in range(tirages):
        v = rng.normal(100.0, 20.0, n)
        brut.append(accord_sur_la_fenetre(v, fam)[0])
        net.append(accord_sur_la_fenetre(retirer_les_modes_bas(v, modes), fam)[0])
    return {"pas": pas, "tirages": int(tirages),
            "barre_brute": round(float(np.percentile(brut, 99)), 4),
            "barre_apres_retrait": round(float(np.percentile(net, 99)), 4),
            "la_barre_monte_apres_retrait": bool(
                np.percentile(net, 99) > np.percentile(brut, 99))}


def sur_les_segments_reels(chemin: Path, lambda_max_um: float, fenetres=FENETRES,
                           echantillons: int = 73, tirages: int = TIRAGES_DU_NUL,
                           graine: int = GRAINE) -> dict:
    """Le retrait des modes bas change-t-il la confirmation, fenetre par fenetre ?

    ⭐⭐⭐ ZERO LECTURE : `111` a garde les profils bruts, donc chaque fenetre de `k` pas est un
    sous-ensemble d'un profil deja paye. C'est exactement ce que garder les profils achete.

    ⚠⚠ Les fenetres d'une meme marche se RECOUVRENT — la fenetre qui part du pas 1 et celle qui
    part du pas 2 partagent `k-1` pas — donc leurs accords sont correles. Ce qui est rendu decrit
    la population de fenetres, pas un echantillon independant, et le dire vaut mieux que de
    laisser croire a `n` mesures.
    """
    brut = json.loads(Path(chemin).read_text())
    lignes = []
    for k in fenetres:
        fam = famille_de_la_fenetre(k, echantillons)
        a_brut, a_net, avances = [], [], []
        modes_vus = None
        for ligne in brut.get("lignes", []):
            for cel in ligne.get("detail", []):
                for sel in SELECTEURS:
                    m = cel.get(sel)
                    if not isinstance(m, dict) or not m.get("decidable"):
                        continue
                    v = np.asarray(m["profil"], dtype=np.float64)
                    av = float(m["avance_moyenne_um"])
                    for i in range(0, int(m["pas"]) - k + 1):
                        seg = v[i * echantillons: (i + k) * echantillons + 1]
                        if seg.size < k * echantillons + 1:
                            continue
                        md = modes_sous_le_signal(k * av, k, lambda_max_um)
                        modes_vus = md["modes_a_retirer"]
                        a_brut.append(accord_sur_la_fenetre(seg, fam)[0])
                        a_net.append(accord_sur_la_fenetre(
                            retirer_les_modes_bas(seg, md["modes_a_retirer"]), fam)[0])
                        avances.append(av)
        if not a_brut:
            continue
        b = barre_de_la_fenetre(k, modes_vus or [], echantillons, tirages, graine)
        ab, an = np.asarray(a_brut), np.asarray(a_net)
        lignes.append({
            "pas": k, "fenetres": len(a_brut), "modes_retires": modes_vus or [],
            "avance_mediane_um": round(float(np.median(avances)), 1),
            "accord_median_brut": round(float(np.median(ab)), 4),
            "accord_median_apres_retrait": round(float(np.median(an)), 4),
            "gain_median": round(float(np.median(an - ab)), 4),
            "barre_brute": b["barre_brute"], "barre_apres_retrait": b["barre_apres_retrait"],
            "part_au_dessus_brut": round(float(np.mean(ab > b["barre_brute"])), 3),
            "part_au_dessus_apres_retrait": round(
                float(np.mean(an > b["barre_apres_retrait"])), 3)})
    if not lignes:
        return {"decidable": False, "pourquoi": "aucun profil lisible"}
    un = lignes[0]
    return {"decidable": True, "par_fenetre": lignes,
            "source": str(Path(chemin).relative_to(RACINE)),
            # ⭐⭐⭐ LE VERDICT A UN PAS : rien ne bouge, parce qu'il n'y a rien a retirer.
            "a_un_pas_le_retrait_ne_change_rien": bool(
                un["pas"] == 1 and abs(un["gain_median"]) < 1e-9),
            "gain_median_au_plus_long": lignes[-1]["gain_median"],
            # ⚠ Et sur les fenetres ou il y a quelque chose a retirer, le gain est-il reel ?
            "le_retrait_aide_sur_les_fenetres_longues": bool(
                any(x["modes_retires"] and x["part_au_dessus_apres_retrait"]
                    > x["part_au_dessus_brut"] for x in lignes)),
            "les_fenetres_se_recouvrent":
                "les fenetres d'une meme marche partagent k-1 pas, donc leurs accords sont "
                "correles : ceci decrit une population de fenetres, pas n mesures independantes"}


def mesurer(chemin: Path = PROFILS, tirages: int = TIRAGES_DU_NUL,
            graine: int = GRAINE) -> dict:
    """La tranche entiere, sur les profils que `111` a gardes. Zero lecture distante."""
    import combien_dinterstices_traverses as C  # noqa: PLC0415
    import le_pas_que_la_matiere_montre as M  # noqa: PLC0415

    cands = M.candidats_de_pas(C.PAS_UM)
    lmax = float(np.max(cands))
    brut = json.loads(Path(chemin).read_text()) if Path(chemin).is_file() else {}
    avances = [float(m["avance_moyenne_um"])
               for ligne in brut.get("lignes", [])
               for cel in ligne.get("detail", [])
               for sel in SELECTEURS
               for m in [cel.get(sel)]
               if isinstance(m, dict) and m.get("decidable")]
    av = float(np.median(avances)) if avances else 230.0
    r = {"fragment": brut.get("fragment"), "lambda_max_um": lmax,
         "avance_mediane_um": round(av, 1), "echantillons_par_pas": C.ECHANTILLONS,
         "a_partir_de_quelle_fenetre": a_partir_de_quelle_fenetre(av, lmax),
         "pourquoi_les_autres_bases_echouent": pourquoi_les_autres_bases_echouent(
             lmax, av, echantillons_par_pas=C.ECHANTILLONS),
         "lorthogonalite_est_elle_exacte": lorthogonalite_est_elle_exacte(
             lmax, av, echantillons_par_pas=C.ECHANTILLONS),
         "la_contamination_est_irreductible": la_contamination_est_irreductible(
             av, lmax, echantillons_par_pas=C.ECHANTILLONS)}
    if brut:
        r["sur_les_segments_reels"] = sur_les_segments_reels(
            chemin, lmax, echantillons=C.ECHANTILLONS, tirages=tirages, graine=graine)
    return r


def afficher(r: dict) -> None:
    print(f"\n{r.get('fragment')} · λmax {r.get('lambda_max_um')} µm · avance médiane "
          f"{r.get('avance_mediane_um')} µm\n")
    a = r.get("a_partir_de_quelle_fenetre", {})
    print("QUELS MODES SONT SOUS LE SIGNAL, FENÊTRE PAR FENÊTRE ?")
    print(f"   {'pas':>4} {'L (µm)':>8} {'f_lo':>6} {'à retirer':>16} {'signal':>7} {'ortho':>6}")
    for x in a.get("par_fenetre", []):
        print(f"   {x['pas']:>4} {x['longueur_um']:>8.0f} {x['f_lo']:>6.2f} "
              f"{str(x['modes_a_retirer']) if x['modes_a_retirer'] else '— (rien)':>16} "
              f"{x['mode_du_signal']:>7} "
              f"{'oui' if x['le_signal_est_hors_de_ce_quon_retire'] else 'NON':>6}")
    print(f"   ★★★ première fenêtre nettoyable : {a.get('premiere_fenetre_nettoyable')} pas "
          f"(seuil {a.get('seuil_en_micrometres')} µm = {a.get('seuil_en_pas')} pas)")
    c = r.get("la_contamination_est_irreductible", {})
    print(f"\n★★★ À UN PAS, LE RETRAIT NE CHANGE RIEN — "
          f"{'CONFIRMÉ' if c.get('le_retrait_ne_change_rien') else 'INFIRMÉ'}, "
          f"parce que la liste des modes est vide : {c.get('parce_que_la_liste_est_vide')}")
    print(f"   accord sans dérive {c.get('accord_sans_derive')}")
    for x in c.get("par_derive", []):
        print(f"   dérive f={x['derive_en_periodes_par_fenetre']:<5} "
              f"(λ={x['longueur_donde_um']:>7.1f} µm) : brut {x['accord_brut']:.4f} · "
              f"après retrait {x['accord_apres_retrait']:.4f} · gain {x['gain']:+.4f}")
    print(f"   ⚠ contamination maximale mesurée : {c.get('contamination_max')}")
    b = r.get("pourquoi_les_autres_bases_echouent", {})
    print(f"\n⚠⚠⚠ CE QUE LES AUTRES BASES ABSORBENT DU SIGNAL (part du gabarit)")
    print(f"   {'pas':>4} {'poly d1':>8} {'poly d2':>8} {'poly d3':>8} "
          f"{'harm. non entière':>18} {'FOURIER':>9}")
    for p_, h, f in zip(b.get("polynomial", []), b.get("harmonique_non_entiere", []),
                        b.get("fourier_de_la_fenetre", [])):
        print(f"   {p_['pas']:>4} {p_['degre_1']:>8.4f} {p_['degre_2']:>8.4f} "
              f"{p_['degre_3']:>8.4f} {h['part']:>18.4f} {f['part']:>9.4f}")
    print(f"   ★ le polynôme de degré deux détruit le gabarit à un pas : "
          f"{b.get('le_polynome_de_degre_deux_detruit_le_gabarit_a_un_pas')}")
    print(f"   ★ la grille non entière mord sur le signal : "
          f"{b.get('la_grille_non_entiere_mord_sur_le_signal')}")
    print(f"   ★★ la base de Fourier est QUASI orthogonale au signal : "
          f"{b.get('la_base_de_fourier_est_quasi_orthogonale_au_signal')} "
          f"(absorbe au plus {b.get('part_absorbee_par_fourier')})")
    o = r.get("lorthogonalite_est_elle_exacte", {})
    if o:
        print(f"   ⚠⚠⚠ et « EXACTEMENT orthogonal » était faux sur la grille employée : "
              f"{o.get('pire_sur_la_grille_incluse')} au pire à extrémité INCLUSE, "
              f"{o.get('pire_sur_la_grille_dft')} sur la grille DFT")
        print(f"       exacte sur la grille DFT : {o.get('exacte_sur_la_grille_dft')} · "
              f"et le résidu décroît avec la fenêtre : "
              f"{o.get('et_elle_decroit_avec_la_fenetre')}")
    s = r.get("sur_les_segments_reels", {})
    if s.get("decidable"):
        print(f"\nSUR LES SEGMENTS RÉELS (profils gardés par `111`, zéro lecture)")
        print(f"   {'pas':>4} {'fenêtres':>9} {'retirés':>10} {'brut':>8} {'net':>8} "
              f"{'gain':>8} {'>barre brut':>12} {'>barre net':>11}")
        for x in s["par_fenetre"]:
            print(f"   {x['pas']:>4} {x['fenetres']:>9} "
                  f"{str(x['modes_retires']) if x['modes_retires'] else '—':>10} "
                  f"{x['accord_median_brut']:>8.4f} {x['accord_median_apres_retrait']:>8.4f} "
                  f"{x['gain_median']:>+8.4f} {x['part_au_dessus_brut']:>12.3f} "
                  f"{x['part_au_dessus_apres_retrait']:>11.3f}")
        print(f"   ★★★ à un pas, le retrait ne change rien : "
              f"{s.get('a_un_pas_le_retrait_ne_change_rien')}")
        print(f"   ★ le retrait aide sur les fenêtres longues : "
              f"{s.get('le_retrait_aide_sur_les_fenetres_longues')}")
        print(f"   ⚠ {s.get('les_fenetres_se_recouvrent')}")


def verifier() -> int:
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    N = C.ECHANTILLONS
    AV, LMAX = 230.0, 346.0

    # === LES MODES SOUS LE SIGNAL =============================================================
    # ⭐⭐⭐ LE FAIT STRUCTUREL : a un pas la liste est VIDE, et elle cesse de l'etre des que la
    # fenetre depasse la plus grande longueur d'onde plausible.
    un = modes_sous_le_signal(AV, 1, LMAX)
    v("à un pas, aucun mode n'est sous le signal",
      un["modes_a_retirer"] == [] and un["il_y_a_quelque_chose_a_retirer"] is False,
      f"f_lo = {un['f_lo']}")
    deux = modes_sous_le_signal(2 * AV, 2, LMAX)
    v("... et à deux pas il y en a un",
      deux["modes_a_retirer"] == [1], f"f_lo = {deux['f_lo']}")
    six = modes_sous_le_signal(6 * AV, 6, LMAX)
    v("... et à six pas il y en a trois", six["modes_a_retirer"] == [1, 2, 3])
    # ⚠⚠⚠ LE CONTROLE QUI DOIT TOUJOURS TENIR : le signal n'est JAMAIS dans ce qu'on retire.
    # C'est ce qui rend le remede de `111` exact plutot qu'approche.
    v("le signal n'est jamais dans ce qu'on retire, à aucune longueur",
      all(modes_sous_le_signal(k * AV, k, LMAX)["le_signal_est_hors_de_ce_quon_retire"]
          for k in range(1, 25)))
    # ⚠ Et la raison est une inegalite, pas une observation : `f_lo = k*avance/lambda_max` et
    # l'avance est bornee par lambda_max, donc `f_lo < k` toujours.
    v("... et c'est parce que l'avance est bornée par λmax",
      all(modes_sous_le_signal(k * AV, k, LMAX)["f_lo"] < k for k in range(1, 25)))
    for mauvais in ((AV, 1, 0.0), (0.0, 1, LMAX), (AV, 0, LMAX)):
        try:
            modes_sous_le_signal(*mauvais)
            ok = False
        except ValueError:
            ok = True
        v(f"une fenêtre absurde est refusée {mauvais}", ok)

    # === LE RETRAIT EST EXACT =================================================================
    t = np.linspace(0.0, 1.0, 6 * N + 1)
    sig = np.cos(2.0 * np.pi * 6.0 * t)
    # ⭐⭐ Retirer les modes 1 à 3 laisse le mode 6 INTACT, a la precision machine.
    net = retirer_les_modes_bas(100.0 + 40.0 * sig, [1, 2, 3])
    z = net - net.mean()
    s = sig - sig.mean()
    # ⚠⚠⚠ LA TOLERANCE EST CELLE DE LA GRILLE, PAS DE LA MACHINE. J'avais asserte 1e-9 et la
    # batterie m'a repris a 3e-5 : la grille des profils inclut son extremite, donc les modes ne
    # sont exactement orthogonaux que sur la grille DFT. `lorthogonalite_est_elle_exacte` mesure
    # l'ecart des deux, et la tolerance ici en decoule.
    v("retirer les modes bas laisse le signal intact, à la tolérance de la grille",
      abs(float(z @ s) / (np.linalg.norm(z) * np.linalg.norm(s)) - 1.0) < 1e-3,
      f"corrélation {float(z @ s) / (np.linalg.norm(z) * np.linalg.norm(s)):.9f}")
    # ⚠ Et il retire BIEN ce qu'il vise : un mode 2 injecté doit disparaître.
    sale = 100.0 + 40.0 * sig + 80.0 * np.cos(2.0 * np.pi * 2.0 * t)
    reste = retirer_les_modes_bas(sale, [1, 2, 3])
    m2 = np.cos(2.0 * np.pi * 2.0 * t)
    m2 = m2 - m2.mean()
    v("... et retire bien le mode visé",
      abs(float((reste - reste.mean()) @ m2)) / (np.linalg.norm(reste - reste.mean())
                                                 * np.linalg.norm(m2)) < 1e-3)

    # === POURQUOI LES AUTRES BASES ECHOUENT ===================================================
    # ⭐⭐⭐ LES DEUX ECHECS SONT MESURES, PAS RACONTES, et c'est leur echec qui designe la bonne
    # base. Sans eux, « la base de Fourier » serait un choix parmi d'autres.
    b = pourquoi_les_autres_bases_echouent(LMAX, AV, echantillons_par_pas=N)
    v("un polynôme de degré deux détruit le gabarit à un pas",
      b["le_polynome_de_degre_deux_detruit_le_gabarit_a_un_pas"] is True,
      f"absorbe {b['polynomial'][0]['degre_2']}")
    v("... alors qu'un polynôme de degré UN n'en absorbe rien, à aucune longueur",
      all(abs(x["degre_1"]) < 1e-9 for x in b["polynomial"]))
    # ⚠ Et le degre deux devient inoffensif quand la fenetre s'allonge : ce n'est pas le polynome
    # qui est mauvais, c'est la fenetre d'un pas qui est trop courte.
    v("... et le degré deux devient inoffensif quand la fenêtre s'allonge",
      b["polynomial"][-1]["degre_2"] < 0.1 < b["polynomial"][0]["degre_2"],
      f"{b['polynomial'][0]['degre_2']} à un pas contre {b['polynomial'][-1]['degre_2']}")
    v("une grille harmonique NON ENTIÈRE mord sur le signal",
      b["la_grille_non_entiere_mord_sur_le_signal"] is True,
      f"absorbe jusqu'à {max(x['part'] for x in b['harmonique_non_entiere'])}")
    v("... là où la base de Fourier de la fenêtre en absorbe moins de deux pour cent",
      b["la_base_de_fourier_est_quasi_orthogonale_au_signal"] is True,
      f"absorbe au plus {b['part_absorbee_par_fourier']}")
    # ⭐⭐⭐ ET LA RAISON DE CE QUI RESTE EST MESUREE, PAS SUPPOSEE : exacte sur la grille DFT,
    # approchee sur celle a extremite incluse que `98` et `111` emploient.
    o = lorthogonalite_est_elle_exacte(LMAX, AV, echantillons_par_pas=N)
    v("l'orthogonalité est EXACTE sur la grille DFT",
      o["exacte_sur_la_grille_dft"] is True, f"{o['pire_sur_la_grille_dft']}")
    v("... et seulement APPROCHÉE sur la grille à extrémité incluse",
      o["approchee_sur_la_grille_incluse"] is True, f"{o['pire_sur_la_grille_incluse']}")
    v("... et le résidu décroît quand la fenêtre s'allonge",
      o["et_elle_decroit_avec_la_fenetre"] is True)
    # ⚠⚠ LA PART ABSORBEE SE CALCULE PAR SVD, JAMAIS PAR QR : ma premiere version utilisait `qr`,
    # qui sur une base quasi-degeneree rend un espace PLUS GRAND que celui de la matrice, donc
    # elle absorbait tout, partout. La garde le verifie sur une matrice volontairement degeneree.
    n = 50
    u = np.linspace(0.0, 1.0, n)
    deg = np.column_stack([u, u, u + 1e-14])
    g = np.cos(2.0 * np.pi * 3.0 * u)
    g = g - g.mean()
    g = g / np.linalg.norm(g)
    p = part_absorbee(deg, g)
    v("la part absorbée par SVD voit le rang réel d'une base dégénérée",
      p["rang"] == 1 and p["colonnes"] == 3, f"rang {p['rang']} pour {p['colonnes']} colonnes")

    # === LA CONTAMINATION IRREDUCTIBLE ========================================================
    # ⭐⭐⭐ LE RESULTAT DE LA TRANCHE : a un pas, le retrait ne rend RIEN, et la raison est que la
    # liste est vide — pas que le retrait est mal fait.
    c = la_contamination_est_irreductible(AV, LMAX, echantillons_par_pas=N)
    v("à un pas, le retrait ne change rien du tout",
      c["le_retrait_ne_change_rien"] is True and c["parce_que_la_liste_est_vide"] is True)
    v("... et la contamination par une dérive est réelle, donc il y aurait de quoi réparer",
      c["contamination_max"] > 0.2, f"{c['contamination_max']}")
    # ⚠⚠ ET LA MEME DERIVE, SUR UNE FENETRE DE SIX PAS, EST RETIRABLE : c'est l'asymetrie, et sans
    # elle la tranche dirait seulement « ca ne marche pas » sans dire ou ca marche.
    t6 = np.linspace(0.0, 6.0, 6 * N + 1)
    u6 = np.linspace(0.0, 1.0, 6 * N + 1)
    fam6 = famille_de_la_fenetre(6, N)
    sale6 = (100.0 + 40.0 * np.cos(2.0 * np.pi * t6)
             + 60.0 * np.cos(2.0 * np.pi * 2.0 * u6 + 0.4))
    a0 = accord_sur_la_fenetre(sale6, fam6)[0]
    a1 = accord_sur_la_fenetre(
        retirer_les_modes_bas(sale6, modes_sous_le_signal(6 * AV, 6, LMAX)["modes_a_retirer"]),
        fam6)[0]
    v("la MÊME dérive, sur six pas, est retirable et l'accord remonte",
      a1 > a0 + 0.1, f"{a0:.4f} → {a1:.4f}")

    # === LA FAMILLE DE LA FENETRE =============================================================
    # ⚠⚠ ELLE GENERALISE `98` FIDELEMENT : un pas peut traverser 1, 2 ou 3 interstices, donc une
    # fenetre de k pas en traverse k, 2k ou 3k. Une famille `k-1, k, k+1` serait une AUTRE
    # question — celle d'un pas qui derive — et la substituer changerait le sujet sans le dire.
    fam = famille_de_la_fenetre(3, N)
    v("la famille d'une fenêtre de trois pas teste 3, 6 et 9 interstices",
      sorted({c for c, _g in fam}) == [3, 6, 9])
    v("... et les deux polarités, comme `98`", len(fam) == 6)
    t3 = np.linspace(0.0, 3.0, 3 * N + 1)
    v("... et elle reconnaît une fenêtre qui franchit exactement trois feuilles",
      accord_sur_la_fenetre(100.0 + 40.0 * np.cos(2.0 * np.pi * t3), fam)[1] == 3)
    v("... et six quand elle en franchit six",
      accord_sur_la_fenetre(100.0 + 40.0 * np.cos(2.0 * np.pi * 2.0 * t3), fam)[1] == 6)

    # === LA BARRE APRES RETRAIT ===============================================================
    # ⚠⚠ RETIRER DES MODES CHANGE LA FAMILLE, DONC SA BARRE. Reprendre celle de `98` serait donner
    # a une forme la barre d'une autre.
    ba = barre_de_la_fenetre(6, [1, 2, 3], N, tirages=400)
    v("la barre après retrait est calculée à part de la barre brute",
      abs(ba["barre_apres_retrait"] - ba["barre_brute"]) > 1e-6,
      f"{ba['barre_brute']} contre {ba['barre_apres_retrait']}")
    v("... et elle MONTE, parce qu'il reste moins de place au bruit",
      ba["la_barre_monte_apres_retrait"] is True,
      f"{ba['barre_brute']} → {ba['barre_apres_retrait']}")

    # === LA PREMIERE FENETRE NETTOYABLE =======================================================
    a = a_partir_de_quelle_fenetre(AV, LMAX)
    v("la première fenêtre nettoyable est celle qui dépasse λmax",
      a["premiere_fenetre_nettoyable"] == 2, str(a["premiere_fenetre_nettoyable"]))
    v("... et le seuil est λmax lui-même, en micromètres",
      abs(a["seuil_en_micrometres"] - LMAX) < 1e-9)
    v("... et le signal reste hors du retrait à toute longueur",
      a["le_signal_reste_toujours_hors_du_retrait"] is True)

    # === LES PROFILS DE `111` =================================================================
    if PROFILS.is_file():
        brut = json.loads(PROFILS.read_text())
        n_prof = sum(1 for ligne in brut.get("lignes", [])
                     for cel in ligne.get("detail", []) for sel in SELECTEURS
                     for m in [cel.get(sel)]
                     if isinstance(m, dict) and m.get("decidable"))
        v("les profils gardés par `111` sont lisibles", n_prof >= 24, f"{n_prof} profils")
        # ⚠⚠⚠ LE CONTROLE SE LISAIT LUI-MEME : ma premiere version cherchait la chaine
        # « voxel_distant » dans le fichier, et le controle CONTIENT cette chaine, donc il
        # echouait toujours. C'est le piege de `pkill -f` qui matche sa propre ligne de commande,
        # en costume neuf. L'arbre syntaxique ne voit que les IMPORTS, pas les litteraux.
        import ast  # noqa: PLC0415
        arbre = ast.parse(Path(__file__).read_text())
        importes = set()
        for n_ in ast.walk(arbre):
            if isinstance(n_, ast.Import):
                importes.update(a.name for a in n_.names)
            elif isinstance(n_, ast.ImportFrom) and n_.module:
                importes.add(n_.module)
        v("... et cette tranche n'importe RIEN qui lise le volume distant",
          not any("voxel" in x or "zarr" in x for x in importes),
          str(sorted(importes)))
    else:
        v("les profils de `111` sont présents", False, str(PROFILS))

    print(f"\n{'ALL PASS' if echecs == 0 else 'ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 0 if echecs == 0 else 1


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--source", type=Path, default=PROFILS)
    p.add_argument("--tirages", type=int, default=TIRAGES_DU_NUL)
    p.add_argument("--graine", type=int, default=GRAINE)
    p.add_argument("--json", type=Path, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(chemin=a.source, tirages=a.tirages, graine=a.graine)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False))
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
