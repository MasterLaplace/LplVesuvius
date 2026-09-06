#!/usr/bin/env python3
"""Le critère du raccrochage : ce qu'on cherche est écarté, ce qui reste est COMMENT on choisit

⚠⚠⚠ POURQUOI CE FICHIER EXISTE, ET IL RÉPARE UN DÉFAUT DE MÉTHODE. `le_gabarit_lu_ailleurs` a
fermé trois portes sur la lecture : ce n'est ni la **forme** cherchée (seize variantes, la
meilleure vaut 0,9 µm), ni **où** on l'apprend, ni l'**amplitude** de ce qu'elle choisit. Il
reste le **critère** — comment, la forme et la fenêtre étant fixées, on désigne un décalage.

⚠⚠ ET LES DEUX TRANCHES PRÉCÉDENTES N'ÉVALUAIENT PAS CE QUI TOURNE. Le raccrochage déployé, dans
`le_raccrochage_a_la_matiere`, passe ses décalages par `accorder_les_voisins` — la médiane du
voisinage 3×3 de grille — et **aucune des deux mesures ne l'appelait**. Elles jugeaient donc un
raccrochage plus grossier que celui qui produit les nombres publiés, ce qui est exactement le
défaut que ce dépôt a nommé : une batterie verte sur un module dont le seul chemin non testé est
celui qui produit le nombre publié.

⭐⭐ CE FICHIER TRAVAILLE DONC SUR LA GRILLE, PAS SUR UN NUAGE. Un voisinage se prend dans la
grille de la spire — deux cellules voisines dans la grille sont voisines sur la feuille, alors
que deux points proches dans le volume peuvent appartenir à deux spires. Échantillonner au hasard
détruit cette adjacence, et c'est pour ça que les tranches précédentes ne pouvaient pas exercer
l'accord.

⚠⚠ LE TÉMOIN DE L'ACCORD EST L'ACCORD APPLIQUÉ AU BRUIT. Une médiane de voisinage améliore
n'importe quoi, y compris un décalage tiré d'un gabarit mélangé : son gain doit donc être lu net
de ce que le lissage rend tout seul, sans quoi on créditerait la lecture d'un adoucissement.

Usage :
    uv run python src/nappe/le_critere_du_raccrochage.py --verifier
    uv run python src/nappe/le_critere_du_raccrochage.py \\
        --json docs/mesures/le_critere_du_raccrochage.json
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
for _d in ("commun", "nappe", "encre"):
    sys.path.insert(0, str(RACINE / "src" / _d))

# ⚠ Un seul lecteur de corpus pour tous les dérouleurs, et ses deux fixtures hors ligne.
from le_corpus_des_spires import corpus_fabrique, corpus_publie, volume_fabrique  # noqa: E402
from le_raccrochage_choisit_il_bien import decalage_de_loracle  # noqa: E402

# ⚠⚠ Un seul instrument de comparaison pour toute la famille : la dispersion entre pas y vaut
# quatre fois l'écart entre méthodes, donc seule une différence prise SUR LE MÊME PAS décide.
from lecart_apparie import ecart_apparie, tranche  # noqa: E402

# ⚠⚠⚠ L'ORDRE COMPTE ET IL EST LU : chaque critère « accordé » suit celui dont il est l'accord,
# et chaque témoin suit ce dont il est le témoin. Un tableau publié dans un autre ordre se
# lirait comme une liste de méthodes indépendantes alors que c'est un arbre de variantes.
CRITERES = (
    "ne_rien_faire",
    "maximum",
    "correlation",
    "correlation_accordee",
    "correlation_centree",
    "correlation_accordee_centree",
    "melange",
    "melange_accorde",
)
# ⛔ Ce qui regarde la cible : une borne, jamais un contendant.
BORNE = "oracle"
# ⚠ Les deux témoins, nommés ici pour que le verdict ne puisse pas les compter comme des
# méthodes disponibles — un témoin qui gagnerait un classement serait un classement cassé.
TEMOINS = ("melange", "melange_accorde")


def est_accorde(nom: str) -> bool:
    """Ce critère passe-t-il par la médiane du voisinage de grille ?"""
    return "accorde" in nom


def sans_accord(nom: str) -> str:
    """Le critère dont celui-ci est l'accord — lui-même s'il n'en est pas un.

    ⚠ C'est ce qui permet de mesurer ce que l'accord AJOUTE, plutôt que de comparer un accordé
    à une méthode qui n'a rien à voir avec lui.
    """
    return nom.replace("_accordee", "").replace("_accorde", "") if est_accorde(nom) else nom


def decalages_du_critere(nom: str, corr: np.ndarray, corr_melange: np.ndarray,
                         centres: np.ndarray, lignes: np.ndarray,
                         t_fenetre: np.ndarray) -> np.ndarray:
    """Le décalage que ce critère choisit pour chaque cellule, dans la fenêtre commune.

    ⚠⚠ TOUS LES CRITÈRES CHOISISSENT DANS LA MÊME FENÊTRE, et c'est ce qui rend la comparaison
    honnête : `maximum` est cherché sur la tranche de la ligne qui couvre exactement les centres
    que la corrélation peut atteindre. Le laisser balayer la ligne entière lui donnerait une
    demi-largeur de gabarit de plus de chaque côté, et son avance mesurerait cette fenêtre.

    ⚠⚠⚠ ET LA LIGNE EST TRANCHÉE AVANT D'ÊTRE CHERCHÉE, pas seulement ses décalages. La
    première version passait la ligne ENTIÈRE avec les décalages de la seule fenêtre : `sommet`
    prenait donc l'argmax sur 92 colonnes et indexait un tableau de 62. Sur le vrai volume ça
    lève ; sur la fixture, dont le maximum tombe toujours dans les premières colonnes, **ça
    passait**. Le commentaire disait « cherché sur la tranche » pendant que le code cherchait
    partout — et seule une ligne dont le maximum est HORS fenêtre peut distinguer les deux.

    ⚠ L'accord de voisinage n'est PAS fait ici : il a besoin de la grille, que cette fonction ne
    voit pas. Elle rend le choix par cellule ; `mesurer` le repose sur la grille et l'accorde.
    """
    from le_raccrochage_a_la_matiere import decalage_retenu, sommet  # noqa: PLC0415

    base = sans_accord(nom)
    if base == "ne_rien_faire":
        return np.zeros(len(lignes))
    if base == "maximum":
        reste = lignes.shape[1] - len(t_fenetre)
        if reste < 0 or reste % 2 != 0:
            raise ValueError(f"fenêtre de {len(t_fenetre)} non centrable dans une ligne de "
                             f"{lignes.shape[1]}")
        k = reste // 2
        return sommet(lignes[:, k:k + len(t_fenetre)], t_fenetre, sens=+1)
    if base == "melange":
        return decalage_retenu(corr_melange, centres)
    t = decalage_retenu(corr, centres)
    if base == "correlation_centree":
        # ⚠ Le remède qui a survécu à l'appariement dans `le_raccrochage_choisit_il_bien` :
        # la lecture par cellule intacte, le déplacement d'ensemble retiré.
        return t - float(np.median(t))
    return t


def poser_sur_la_grille(valeurs: np.ndarray, ou: np.ndarray,
                        forme: tuple[int, int]) -> np.ndarray:
    """Reposer des valeurs par cellule sur la grille de la spire, le reste en NaN.

    ⚠⚠ C'EST LA MOITIÉ QUI MANQUAIT AUX DEUX TRANCHES PRÉCÉDENTES. Un voisinage se prend dans
    la GRILLE ; un nuage de points échantillonné au hasard n'en a plus. Sans ce retour à la
    grille, `accorder_les_voisins` est inappelable et le raccrochage évalué reste plus grossier
    que celui qui tourne.
    """
    out = np.full(forme, np.nan)
    out[ou] = valeurs
    return out


def parcourir_les_pas(graine: int = 42, minimum: int = 30, cache_actif: bool = True,
                      cote: float | None = None, fenetre_grille: int | None = None,
                      corpus: dict | None = None, volume=None):
    """Un contexte par pas de spire : la grille, les lignes lues, la corrélation et la cible.

    ⚠⚠⚠ POURQUOI CE PARCOURS EST EXTRAIT. Ce que la lecture d'un pas coûte — deux traversées du
    volume, une pour le gabarit et une pour les lignes — est le même quel que soit ce qu'on
    balaye ensuite : des critères, des largeurs de lissage, autre chose demain. Le recopier
    ferait deux descriptions d'une même lecture, donc deux mesures qui pourraient cesser de
    marcher sur la même matière — ce qui est exactement le défaut que `le_corpus_des_spires`
    existe pour avoir supprimé un cran plus haut.

    ⚠⚠ LE CONTEXTE PORTE LA GRILLE, ET C'EST TOUT SON INTÉRÊT. Un voisinage se prend dans la
    grille de la spire ; un nuage échantillonné au hasard n'en a plus. Les deux tranches qui
    ont précédé ce fichier ne pouvaient pas exercer l'accord de voisinage pour cette seule
    raison.
    """
    from le_pas_normal_atteint_la_spire import distance_a, normales  # noqa: PLC0415
    from le_raccrochage_a_la_matiere import (  # noqa: PLC0415
        BOITE_CENTRE, BOITE_COTE, CacheDisque, Volume, ZARR, accorde_aux_spires,
        accorder_les_voisins, correler, le_long, profil_autour, url_du_volume,
    )
    from scipy.spatial import cKDTree  # noqa: PLC0415

    c = corpus_publie() if corpus is None else corpus
    voxel_um = float(c["voxel_um"])
    ecart_um = float(c["ecart_um"])
    pas_vx = ecart_um / voxel_um
    demi_vx = pas_vx / 2.0
    demi_gab = max(1, int(round(demi_vx / 2.0)))
    if volume is None and not accorde_aux_spires():
        raise RuntimeError(f"le volume {ZARR} n'est pas celui des spires ({c['volume']})")
    if volume is None:
        import tracecheck as tc  # noqa: PLC0415

        url = url_du_volume()
        vol = Volume(url, tc.array_meta(url, 0, 120), CacheDisque(actif=cache_actif))
    else:
        vol = volume

    cote = BOITE_COTE if cote is None else float(cote)
    centre = np.array(BOITE_CENTRE)
    lo, hi = centre - cote / 2, centre + cote / 2
    rng = np.random.default_rng(graine)
    t_gab = np.arange(-demi_gab, demi_gab + 1e-9, 1.0)
    t_ligne = np.arange(-(demi_vx + demi_gab), demi_vx + demi_gab + 1e-9, 1.0)
    fin = len(t_ligne) - demi_gab
    t_fenetre = t_ligne[demi_gab:fin]

    grilles, nuages = {}, {}
    for rang, (a, ok) in sorted(c["grilles"].items()):
        dans = ok & ((a >= lo) & (a <= hi)).all(axis=-1)
        if int(dans.sum()) < minimum:
            continue
        grilles[rang] = (a, dans)
        nuages[rang] = a[ok]

    reglage = dict(volume=c["volume"], voxel_um=voxel_um, ecart_um=ecart_um, pas_vx=pas_vx,
                   demi_gab=int(demi_gab), cote=cote, fenetre_grille=fenetre_grille,
                   boite=dict(centre=list(BOITE_CENTRE), cote_voxels=cote), vol=vol,
                   ecartees=0)
    yield reglage
    for r in sorted(grilles):
        if r + 1 not in nuages:
            continue
        a0, dans = grilles[r]
        n0, bon = normales(a0, dans)
        garde = bon & dans
        if fenetre_grille is not None:
            # ⚠ Une fenêtre de grille est CONTIGUË, jamais un tirage : un sous-échantillon
            # aléatoire n'a plus de voisins, donc l'accord de voisinage ne pourrait pas tourner
            # dessus — ce qui est exactement ce que ces mesures existent pour exercer.
            u, v_ = np.argwhere(garde).mean(axis=0).round().astype(int)
            demi_f = fenetre_grille // 2
            fen = np.zeros_like(garde)
            fen[max(0, u - demi_f):u + demi_f + 1, max(0, v_ - demi_f):v_ + demi_f + 1] = True
            garde = garde & fen
        if int(garde.sum()) < minimum:
            reglage["ecartees"] += 1
            continue
        p_, d_ = a0[garde], n0[garde]
        cible = nuages[r + 1]
        sortant = float(np.median(distance_a(p_ + d_ * pas_vx, cible, voxel_um)))
        rentrant = float(np.median(distance_a(p_ - d_ * pas_vx, cible, voxel_um)))
        sens = 1.0 if sortant <= rentrant else -1.0

        vg, okg = le_long(p_, d_, t_gab, vol)
        if int(okg.sum()) < minimum:
            reglage["ecartees"] += 1
            continue
        gab = profil_autour(vg[okg])
        gab_oriente = gab if sens > 0 else gab[::-1]
        prevu, dd = p_ + d_ * (sens * pas_vx), d_ * sens
        v2, okv = le_long(prevu, dd, t_ligne, vol)
        if int(okv.sum()) < minimum:
            reglage["ecartees"] += 1
            continue

        lisible = poser_sur_la_grille(okv.astype(float), garde, garde.shape) == 1.0
        _, assez = accorder_les_voisins(np.zeros_like(lisible, dtype=float), lisible)
        if int(assez.sum()) < minimum:
            reglage["ecartees"] += 1
            continue

        P, D, L = prevu[okv], dd[okv], v2[okv]
        corr, centres = correler(L, gab_oriente, t_ligne)
        corr_m, _ = correler(L, rng.permuted(gab_oriente), t_ligne)
        arbre = cKDTree(cible)

        def erreur(t_plat, pris, _P=P, _D=D, _arbre=arbre):
            """L'erreur médiane sur les cellules retenues, et les distances par cellule."""
            q = _P[pris] + t_plat[pris][:, None] * _D[pris]
            e = _arbre.query(q, k=1)[0] * voxel_um
            return float(np.median(e)), e

        yield dict(de=r, vers=r + 1, P=P, D=D, L=L, cible=cible, arbre=arbre,
                   corr=corr, corr_melange=corr_m, centres=centres, t_fenetre=t_fenetre,
                   lisible=lisible, assez=assez, erreur=erreur,
                   ou_lisible=np.argwhere(lisible), garde_dans_lisible=assez[lisible])


def mesurer(graine: int = 42, minimum: int = 30, cache_actif: bool = True,
            cote: float | None = None, fenetre_grille: int | None = None,
            corpus: dict | None = None, volume=None) -> dict:
    """Ce que chaque critère choisit, et ce que chacun coûte à la marche."""
    from le_raccrochage_a_la_matiere import accorder_les_voisins  # noqa: PLC0415

    pas = parcourir_les_pas(graine, minimum, cache_actif, cote, fenetre_grille, corpus, volume)
    reglage = next(pas)
    lignes: list[dict] = []
    for ctx in pas:
        entree = dict(de=ctx["de"], vers=ctx["vers"],
                      cellules_lisibles=int(ctx["lisible"].sum()),
                      cellules=int(ctx["assez"].sum()),
                      fenetre_vx=[round(float(ctx["centres"].min()), 2),
                                  round(float(ctx["centres"].max()), 2)],
                      bits_de_supervision=1)
        pris = ctx["garde_dans_lisible"]
        choix: dict[str, np.ndarray] = {}
        for nom in CRITERES:
            brut = decalages_du_critere(sans_accord(nom), ctx["corr"], ctx["corr_melange"],
                                        ctx["centres"], ctx["L"], ctx["t_fenetre"])
            if not est_accorde(nom):
                choix[nom] = brut
                continue
            grille_t = poser_sur_la_grille(brut, ctx["lisible"], ctx["lisible"].shape)
            accorde, _ = accorder_les_voisins(grille_t, ctx["lisible"])
            # ⚠ Une cellule non retenue par l'accord garde son choix brut : elle est de toute
            # façon hors de la population jugée, et laisser un NaN ferait lever la marche.
            valeurs = accorde[ctx["ou_lisible"][:, 0], ctx["ou_lisible"][:, 1]]
            choix[nom] = np.where(np.isnan(valeurs), brut, valeurs)
        for nom in CRITERES:
            med, _ = ctx["erreur"](choix[nom], pris)
            entree[f"erreur_{nom}_um"] = round(med, 1)
            entree[f"decalage_median_{nom}_vx"] = round(float(np.median(choix[nom][pris])), 2)
            if est_accorde(nom):
                # ⚠⚠⚠ COMBIEN DE CELLULES L'ACCORD DÉPLACE RÉELLEMENT. Sans ce compte, un
                # accord devenu inopérant rendrait un écart de zéro micromètre qui se lirait
                # comme « le lissage n'apporte rien » alors qu'il veut dire « le lissage n'a
                # pas eu lieu ». Les deux ont la même tête dans un tableau de résultats.
                ecart = np.abs(choix[nom] - choix[sans_accord(nom)])[pris]
                entree[f"cellules_deplacees_{nom}"] = int((ecart > 1e-9).sum())
        t_oracle, _ = decalage_de_loracle(ctx["P"], ctx["D"], ctx["centres"], ctx["cible"],
                                          reglage["voxel_um"])
        med_o, _ = ctx["erreur"](t_oracle, pris)
        entree[f"erreur_{BORNE}_um"] = round(med_o, 1)
        lignes.append(entree)

    if not lignes:
        raise RuntimeError("aucun pas ne rend un voisinage de grille dans la boîte")

    vol = reglage["vol"]
    r = dict(
        fragment="PHerc0500P2", volume=reglage["volume"], voxel_um=reglage["voxel_um"],
        boite=reglage["boite"],
        pas_nominal_um=reglage["ecart_um"], demi_epaisseur_um=round(reglage["ecart_um"] / 2, 2),
        demi_largeur_gabarit_vx=reglage["demi_gab"], fenetre_grille=fenetre_grille,
        criteres=list(CRITERES), borne=BORNE, temoins=list(TEMOINS),
        paires=len(lignes), paires_ecartees=int(reglage["ecartees"]),
        cellules=int(sum(e["cellules"] for e in lignes)),
        cellules_lisibles=int(sum(e["cellules_lisibles"] for e in lignes)),
        lignes=lignes,
        cout=vol.cache.cout() | dict(voxels_absents=vol.absents, reprises_reseau=vol.reprises))

    def par_pas(nom: str) -> list[float]:
        return [e[f"erreur_{nom}_um"] for e in lignes]

    resume = []
    for nom in CRITERES + (BORNE,):
        resume.append(dict(
            critere=nom, accorde=est_accorde(nom), temoin=nom in TEMOINS,
            borne=nom == BORNE, deploye=nom == "correlation_accordee",
            erreur_mediane_um=round(float(np.median(par_pas(nom))), 1),
            contre_ne_rien_faire=ecart_apparie(par_pas(nom), par_pas("ne_rien_faire")),
            # ⚠⚠ CE QUE L'ACCORD AJOUTE, mesuré contre le critère dont il EST l'accord — jamais
            # contre une autre méthode. Un accordé comparé à autre chose que sa propre version
            # brute mêlerait le lissage et le changement de critère.
            contre_sa_version_brute=(ecart_apparie(par_pas(nom), par_pas(sans_accord(nom)))
                                     if est_accorde(nom) else None)))
    r["resume"] = resume

    def trouver(nom: str) -> dict:
        return next(x for x in resume if x["critere"] == nom)

    dispo = [x for x in resume if not x["temoin"] and not x["borne"]
             and x["critere"] != "ne_rien_faire"]
    r["meilleur_critere"] = min(
        dispo, key=lambda x: x["contre_ne_rien_faire"]["ecart_median_um"])
    # ⭐⭐⭐ LA QUESTION QUE CE FICHIER POSE : le chemin RÉELLEMENT DÉPLOYÉ — corrélation puis
    # accord de voisinage — bat-il le fait de ne pas bouger ? Les deux tranches précédentes ne
    # l'avaient jamais demandé, parce qu'elles n'accordaient pas.
    r["le_chemin_deploye_bat_ne_rien_faire"] = tranche(
        trouver("correlation_accordee")["contre_ne_rien_faire"])
    r["un_critere_bat_ne_rien_faire"] = tranche(
        r["meilleur_critere"]["contre_ne_rien_faire"])
    # ⚠⚠⚠ ET LE TÉMOIN DE L'ACCORD : une médiane de voisinage améliore N'IMPORTE QUOI, y compris
    # un décalage tiré d'un gabarit mélangé. Publier le gain de l'accord sans celui-ci
    # créditerait la lecture d'un simple adoucissement.
    r["laccord_ameliore_la_correlation"] = tranche(
        trouver("correlation_accordee")["contre_sa_version_brute"])
    r["laccord_ameliore_aussi_le_bruit"] = tranche(
        trouver("melange_accorde")["contre_sa_version_brute"])
    r["gain_de_laccord_um"] = trouver(
        "correlation_accordee")["contre_sa_version_brute"]["ecart_median_um"]
    r["gain_de_laccord_sur_le_bruit_um"] = trouver(
        "melange_accorde")["contre_sa_version_brute"]["ecart_median_um"]
    r["erreur_oracle_mediane_um"] = trouver(BORNE)["erreur_mediane_um"]
    r["erreur_ne_rien_faire_mediane_um"] = trouver("ne_rien_faire")["erreur_mediane_um"]
    return r


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # --- l'arbre des critères ---
    v("chaque critère accordé a une version brute dans la liste",
      all(sans_accord(n) in CRITERES for n in CRITERES if est_accorde(n)),
      str([n for n in CRITERES if est_accorde(n)]))
    v("... et un critère brut n'est pas son propre accord",
      all(not est_accorde(sans_accord(n)) for n in CRITERES))
    v("... le chemin réellement déployé est dans la liste",
      "correlation_accordee" in CRITERES and est_accorde("correlation_accordee"))
    # ⚠⚠ UN TÉMOIN N'EST PAS UNE MÉTHODE : s'il pouvait gagner le classement, le classement
    # serait cassé. Les deux témoins ont chacun leur accordé, pour que le lissage soit mesuré
    # sur le bruit comme sur la lecture.
    v("les deux témoins sont nommés, et l'un est l'accord de l'autre",
      set(TEMOINS) <= set(CRITERES) and sans_accord("melange_accorde") == "melange")

    # ⚠⚠⚠ LE CONTRÔLE QUI MANQUAIT, ET QUI DISCRIMINE. Une ligne dont le maximum GLOBAL est
    # hors de la fenêtre : `maximum` doit rendre le meilleur point DE LA FENÊTRE, jamais le
    # maximum global. La première version rendait un indice hors bornes sur le vrai volume et
    # passait sur la fixture, dont le maximum tombe toujours du bon côté.
    ligne = np.zeros((1, 9))
    ligne[0, 0] = 100.0   # le maximum global, hors fenêtre
    ligne[0, 5] = 10.0    # le meilleur point DANS la fenêtre
    fen = np.arange(-2.0, 2.1, 1.0)   # 5 décalages, centrés dans une ligne de 9
    pris = decalages_du_critere("maximum", np.zeros((1, 1)), np.zeros((1, 1)),
                                np.zeros(1), ligne, fen)
    v("`maximum` cherche DANS la fenêtre, jamais sur la ligne entière",
      float(fen[0]) <= float(pris[0]) <= float(fen[-1]) and abs(float(pris[0]) - 1.0) < 1.0,
      f"{float(pris[0]):.2f} pour une fenêtre {[fen[0], fen[-1]]}")
    mal = None
    try:
        decalages_du_critere("maximum", np.zeros((1, 1)), np.zeros((1, 1)), np.zeros(1),
                             np.zeros((1, 8)), fen)
    except ValueError as exc:
        mal = str(exc)
    v("... et une fenêtre non centrable est REFUSÉE, pas décalée en silence",
      mal is not None, str(mal))

    # --- la pose sur la grille ---
    ou = np.array([[True, False], [False, True]])
    g = poser_sur_la_grille(np.array([7.0, 9.0]), ou, (2, 2))
    v("les valeurs reviennent à leur place dans la grille",
      g[0, 0] == 7.0 and g[1, 1] == 9.0 and np.isnan(g[0, 1]) and np.isnan(g[1, 0]),
      str(g.tolist()))

    # --- l'accord de voisinage, sur une grille fabriquée ---
    from le_raccrochage_a_la_matiere import accorder_les_voisins  # noqa: PLC0415

    t = np.full((5, 5), 2.0)
    t[2, 2] = 40.0
    ok = np.ones((5, 5), dtype=bool)
    acc, assez = accorder_les_voisins(t, ok)
    # ⚠⚠⚠ C'EST L'ÉNONCÉ SUR LA MATIÈRE QUE CE FICHIER EXERCE : une feuille est lisse à
    # l'échelle de trois cellules, donc un isolé qui se raccroche à quarante voxels de ses huit
    # voisins ne peut pas avoir raison. La médiane le ramène ; une moyenne se laisserait tirer.
    v("l'accord de voisinage ramène un isolé sur la majorité de ses voisins",
      acc[2, 2] == 2.0, f"{acc[2, 2]} au lieu de 40.0")
    v("... et il écarte les cellules dont le voisinage ne fait pas majorité",
      not assez[0, 0] and assez[2, 2], f"coin {assez[0, 0]}, centre {assez[2, 2]}")

    # ⚠⚠⚠ LE CHEMIN QUI PRODUIT LE NOMBRE PUBLIÉ, HORS LIGNE, avec ses DEUX matières.
    from le_corpus_des_spires import geometrie_fabriquee  # noqa: PLC0415

    g0 = geometrie_fabriquee()
    fab = mesurer(minimum=20, corpus=corpus_fabrique(), volume=volume_fabrique(g0))
    v("la mesure tourne de bout en bout sur des matières fabriquées, sans rien lire",
      fab["paires"] > 0 and len(fab["resume"]) == len(CRITERES) + 1,
      f"{fab['paires']} pas, {len(fab['resume'])} critères")
    # ⚠⚠⚠ UNE SEULE POPULATION, ET C'EST L'ACCORD QUI LA FIXE : juger les bruts sur toutes les
    # cellules et les accordés sur ce qui reste comparerait deux populations.
    v("... tous les critères sont jugés sur les cellules que l'ACCORD retient",
      all(0 < e["cellules"] <= e["cellules_lisibles"] for e in fab["lignes"]),
      str([(e["cellules"], e["cellules_lisibles"]) for e in fab["lignes"]]))
    # ⚠⚠ TOUS CHOISISSENT DANS LA MÊME FENÊTRE : `maximum` compris, sinon son avance mesurerait
    # une demi-largeur de gabarit de plus de chaque côté.
    hors = [(e["de"], n, e[f"decalage_median_{n}_vx"]) for e in fab["lignes"] for n in CRITERES
            if not (e["fenetre_vx"][0] - 1 <= e[f"decalage_median_{n}_vx"]
                    <= e["fenetre_vx"][1] + 1)]
    v("... et tous choisissent dans la MÊME fenêtre, `maximum` compris", not hors, str(hors[:3]))
    # ⚠⚠ L'ORACLE EST UNE BORNE : sa tolérance est DÉRIVÉE — un déplacement d'un voxel ne change
    # une distance que d'un voxel, et c'est tout ce qu'un affinage parabolique peut acheter.
    marge = fab["voxel_um"]
    bat = [(e["de"], n) for e in fab["lignes"] for n in CRITERES
           if e[f"erreur_{BORNE}_um"] > e[f"erreur_{n}_um"] + marge]
    v("... l'oracle n'est battu par aucun critère de plus d'un voxel", not bat, str(bat[:3]))
    # ⚠⚠⚠ CE QUE L'ACCORD AJOUTE EST MESURÉ CONTRE SA PROPRE VERSION BRUTE, jamais contre une
    # autre méthode : sinon le lissage et le changement de critère seraient mêlés.
    v("... l'accord est jugé contre le critère dont il EST l'accord",
      all(x["contre_sa_version_brute"] is not None for x in fab["resume"] if x["accorde"])
      and all(x["contre_sa_version_brute"] is None for x in fab["resume"]
              if not x["accorde"]))
    # ⚠⚠⚠ ET LE TÉMOIN DU LISSAGE : l'accord appliqué au BRUIT. Sans lui, un adoucissement
    # passerait pour une meilleure lecture.
    # ⚠⚠⚠ ET LE CONTRÔLE QUI EMPÊCHE LA TRANCHE ENTIÈRE D'ÊTRE VIDE : l'accord doit DÉPLACER
    # des cellules. Un accord inopérant rendrait « +0,0 µm » — indiscernable, dans un tableau,
    # d'un lissage qui n'apporte rien.
    deplacees = {n: sum(e[f"cellules_deplacees_{n}"] for e in fab["lignes"])
                 for n in CRITERES if est_accorde(n)}
    v("... l'accord DÉPLACE réellement des cellules, sinon la tranche mesurerait le vide",
      all(x > 0 for x in deplacees.values()), str(deplacees))
    v("... et le lissage est aussi mesuré sur le BRUIT, pas seulement sur la lecture",
      isinstance(fab["laccord_ameliore_aussi_le_bruit"], bool)
      and fab["gain_de_laccord_sur_le_bruit_um"] is not None,
      f"lecture {fab['gain_de_laccord_um']:+.1f} µm · bruit "
      f"{fab['gain_de_laccord_sur_le_bruit_um']:+.1f} µm")
    v("... un témoin ne peut pas gagner le classement",
      not fab["meilleur_critere"]["temoin"] and not fab["meilleur_critere"]["borne"],
      fab["meilleur_critere"]["critere"])
    # ⚠⚠ LES VERDICTS PASSENT PAR L'INSTRUMENT PARTAGÉ, jamais par une conjonction recopiée.
    v("... et les verdicts passent par l'écart apparié, avec son intervalle",
      all(x["contre_ne_rien_faire"]["intervalle_um"] is not None for x in fab["resume"])
      and fab["le_chemin_deploye_bat_ne_rien_faire"]
      == tranche(next(x for x in fab["resume"]
                      if x["critere"] == "correlation_accordee")["contre_ne_rien_faire"]))
    v("le résultat est sérialisable tel quel, sans type qui traîne",
      isinstance(json.dumps(fab), str))
    tampon, souci = io.StringIO(), None
    try:
        with contextlib.redirect_stdout(tampon):
            afficher(fab)
    except Exception as exc:  # noqa: BLE001
        souci = f"{type(exc).__name__}: {exc}"
    v("l'affichage tourne sur ce résultat et va jusqu'à son verdict",
      souci is None and "DÉPLOYÉ" in tampon.getvalue(),
      souci or f"{len(tampon.getvalue().splitlines())} lignes")
    # ⚠ Une fenêtre de grille CONTIGUË garde les voisins ; c'est ce qui permet de borner le coût
    # sans rendre l'accord inapplicable.
    etroit = mesurer(minimum=20, fenetre_grille=7, corpus=corpus_fabrique(),
                     volume=volume_fabrique(g0))
    v("une fenêtre de grille contiguë borne le coût sans casser le voisinage",
      etroit["paires"] > 0 and etroit["cellules"] < fab["cellules"],
      f"{etroit['cellules']} contre {fab['cellules']} cellules")
    hors_boite = None
    try:
        mesurer(minimum=20, corpus=corpus_fabrique(decalage_vx=5000.0),
                volume=volume_fabrique(geometrie_fabriquee(decalage_vx=5000.0)))
    except RuntimeError as exc:
        hors_boite = str(exc)
    v("un objet entier posé hors de la boîte est REFUSÉ, pas rendu vide",
      hors_boite is not None, str(hors_boite))

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def afficher(r: dict) -> None:
    """Le compte rendu lisible d'un balayage de critères."""
    print(f"pas nominal {r['pas_nominal_um']} µm · demi-largeur de gabarit "
          f"{r['demi_largeur_gabarit_vx']} vx · {r['paires']} pas "
          f"({r['paires_ecartees']} écartés) · {r['cellules']} cellules retenues sur "
          f"{r['cellules_lisibles']} lisibles\n")
    print(f"{'critère':>30} {'erreur':>8} {'contre ne rien faire':>36} "
          f"{'contre sa version brute':>36}")
    print("-" * 116)

    def lisible(e: dict | None) -> str:
        if e is None or e["ecart_median_um"] is None:
            return "—"
        return (f"{e['ecart_median_um']:+6.1f} µm · {e['pas_ameliores']}/{e['pas']} · "
                f"{str(e['intervalle_um']):>14} · "
                f"{'TRANCHE' if tranche(e) else '—'}")

    for x in r["resume"]:
        marque = (" ⭐" if x["deploye"] else (" ⛔" if x["borne"] else
                                             ("  ~" if x["temoin"] else "")))
        print(f"{x['critere']:>30} {x['erreur_mediane_um']:>7.1f}µ "
              f"{lisible(x['contre_ne_rien_faire']):>36} "
              f"{lisible(x['contre_sa_version_brute']):>36}{marque}")
    print(f"\nne rien faire {r['erreur_ne_rien_faire_mediane_um']} µm · ⛔ oracle "
          f"{r['erreur_oracle_mediane_um']} µm")
    print(f"→ ⭐⭐ le chemin RÉELLEMENT DÉPLOYÉ (corrélation puis accord) bat-il ne rien faire ? "
          f"{'OUI' if r['le_chemin_deploye_bat_ne_rien_faire'] else 'NON'}")
    print(f"→ un critère quelconque y arrive-t-il ? "
          f"{'OUI' if r['un_critere_bat_ne_rien_faire'] else 'NON'} "
          f"(le meilleur : {r['meilleur_critere']['critere']})")
    bouge = {x["critere"]: sum(e.get(f"cellules_deplacees_{x['critere']}", 0)
                               for e in r["lignes"])
             for x in r["resume"] if x["accorde"]}
    print(f"cellules que l'accord DÉPLACE : "
          + " · ".join(f"{n} {c}/{r['cellules']}" for n, c in bouge.items()))
    print(f"→ ⚠ l'accord de voisinage améliore la corrélation : "
          f"{'OUI' if r['laccord_ameliore_la_correlation'] else 'NON'} "
          f"({r['gain_de_laccord_um']:+.1f} µm) — et il améliore AUSSI le bruit : "
          f"{'OUI' if r['laccord_ameliore_aussi_le_bruit'] else 'NON'} "
          f"({r['gain_de_laccord_sur_le_bruit_um']:+.1f} µm)")
    print(f"coût : {r['cout']['blocs_telecharges']} blocs, {r['cout']['mebioctets']} Mio")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--cote", type=float, default=None)
    p.add_argument("--fenetre-grille", type=int, default=None,
                   dest="fenetre_grille",
                   help="borne le coût par une fenêtre CONTIGUË de la grille")
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(cote=a.cote, fenetre_grille=a.fenetre_grille)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
