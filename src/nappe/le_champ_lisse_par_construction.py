#!/usr/bin/env python3
"""Un champ de décalages lisse PAR CONSTRUCTION, plutôt qu'un champ bruité lissé après coup

⚠⚠⚠ POURQUOI CE FICHIER EXISTE, ET C'EST LE SEUL CHANTIER QUI RESTE. Deux mesures y convergent.
`loracle_est_il_atteignable` a montré que le champ de décalages qu'une méthode parfaite devrait
produire est **plat** — rugosité 0,0 voxel — pendant que celui du raccrochage est à **56 %** de la
rugosité du **bruit pur**. `la_direction_du_pas` a montré que le champ utile, décalage comme
rotation, est **lisse localement et étendu globalement**. Et `la_lissite_de_la_feuille` a montré
que le lissage **après coup** plafonne : au-delà du 3×3, tout gain supplémentaire est du lissage.

⭐⭐ CE FICHIER ESSAIE L'AUTRE VOIE. Une médiane de voisinage est un **ajustement local par une
constante** ; ce qu'on cherche est un champ dont la lissité est une **propriété de sa forme**, pas
le résultat d'un moyennage. Une surface polynomiale ajustée sur la grille est lisse quoi qu'il
arrive dans les données — elle ne peut pas être bruitée, parce qu'elle n'a pas assez de degrés de
liberté pour l'être.

⚠⚠ ET LE TÉMOIN SUIT CHAQUE AJUSTEMENT. Ajuster une surface à trois paramètres sur du bruit rend
déjà quelque chose de lisse ; ce qui compte est ce que l'ajustement rend de PLUS sur la lecture
que sur son gabarit mélangé. Sans ce témoin, on créditerait la lecture d'un geste qui marche sans
elle — c'est exactement ce que la tranche sur la lissité a dû mesurer.

⚠ Les degrés balayés sont dérivés et non choisis : zéro est le recentrage déjà mesuré, un est le
plan, et au-delà chaque degré ajoute une courbure. Le balayage s'arrête là où le nombre de
paramètres cesse d'être négligeable devant le nombre de cellules — sinon on n'ajuste plus une
surface, on interpole du bruit.

Usage :
    uv run python src/nappe/le_champ_lisse_par_construction.py --verifier
    uv run python src/nappe/le_champ_lisse_par_construction.py --cote 960 \\
        --json docs/mesures/le_champ_lisse_par_construction.json
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

from le_corpus_des_spires import corpus_fabrique, corpus_publie, volume_fabrique  # noqa: E402
from le_critere_du_raccrochage import (  # noqa: E402
    decalages_du_critere, parcourir_les_pas, poser_sur_la_grille,
)
from lecart_apparie import ecart_apparie, tranche  # noqa: E402
from loracle_est_il_atteignable import rugosite  # noqa: E402

DEGRES = (0, 1, 2, 3)
# ⚠ La demi-fenêtre du plan LOCAL : quatre cellules, donc 81 points pour trois paramètres. Plus
# étroit, un plan interpole son propre voisinage et cesse de lisser quoi que ce soit — sur un
# 3×3, neuf points pour trois paramètres, ce qu'on rendrait serait le bruit remis en forme.
DEMI_LOCAL = 4
LECTURES = ("correlation", "melange")


def base_polynomiale(u: np.ndarray, v: np.ndarray, degre: int) -> np.ndarray:
    """Les monômes en (u, v) jusqu'au degré demandé, sur des coordonnées NORMALISÉES.

    ⚠⚠ LA NORMALISATION N'EST PAS COSMÉTIQUE. Sur une grille de plusieurs dizaines de cellules,
    un cube d'indices bruts vaut des dizaines de milliers : la matrice normale devient si mal
    conditionnée que les coefficients rendus n'ont plus de sens, et l'ajustement rend un champ
    qui oscille. Ramener (u, v) dans [-1, 1] est ce qui rend le degré trois utilisable.
    """
    colonnes = []
    for total in range(degre + 1):
        for i in range(total + 1):
            colonnes.append((u ** (total - i)) * (v ** i))
    return np.stack(colonnes, axis=1)


def nombre_de_termes(degre: int) -> int:
    """Combien de paramètres un ajustement de ce degré consomme."""
    return (degre + 1) * (degre + 2) // 2


def ajuster_surface(champ: np.ndarray, valide: np.ndarray,
                    degre: int) -> tuple[np.ndarray, np.ndarray]:
    """Le champ remplacé par la surface polynomiale qui l'approche au mieux, sur toute la grille.

    ⚠⚠⚠ C'EST LA DIFFÉRENCE AVEC UNE MÉDIANE DE VOISINAGE, et elle est de nature. Une médiane
    rend un champ qui PEUT être bruité — elle atténue le bruit, elle ne l'interdit pas. Une
    surface de degré `d` n'a que `(d+1)(d+2)/2` paramètres pour toute la feuille : elle est
    lisse parce qu'elle n'a pas de quoi ne pas l'être.

    ⚠ Elle ne rétrécit AUCUN masque : chaque cellule valide reçoit une valeur, y compris aux
    bords. C'est le second écart avec le voisinage, qui écarte ce qu'il ne peut pas moyenner.
    """
    h, w = champ.shape
    uu, vv = np.meshgrid(np.arange(h), np.arange(w), indexing="ij")
    u = (2.0 * uu / max(1, h - 1) - 1.0)
    v = (2.0 * vv / max(1, w - 1) - 1.0)
    bon = valide & np.isfinite(champ)
    if int(bon.sum()) < nombre_de_termes(degre) + 1:
        return np.full_like(champ, np.nan), np.zeros_like(valide)
    A = base_polynomiale(u[bon], v[bon], degre)
    coef, *_ = np.linalg.lstsq(A, champ[bon], rcond=None)
    plein = base_polynomiale(u.reshape(-1), v.reshape(-1), degre) @ coef
    out = np.full_like(champ, np.nan)
    out[valide] = plein.reshape(h, w)[valide]
    return out, valide.copy()


def ajuster_localement(champ: np.ndarray, valide: np.ndarray,
                       demi: int = DEMI_LOCAL) -> tuple[np.ndarray, np.ndarray]:
    """Un PLAN ajusté sur le voisinage de chaque cellule — la médiane, d'un degré plus haut.

    ⚠⚠ UNE MÉDIANE DE VOISINAGE EST UN AJUSTEMENT LOCAL PAR UNE CONSTANTE. La remplacer par un
    plan est donc le pas suivant exactement, et non une autre idée : là où la médiane suppose
    que le décalage ne varie pas dans la fenêtre, le plan lui laisse une pente. Sur un champ
    qu'on sait **étendu à travers la feuille**, cette pente est précisément ce qui manque.

    ⚠ Le seuil de points est la MAJORITÉ de la fenêtre, dérivé comme celui du voisinage — et il
    est en plus exigé strictement supérieur au nombre de paramètres, sinon le plan interpole.
    """
    h, w = champ.shape
    minimum = max((2 * demi + 1) ** 2 // 2 + 1, nombre_de_termes(1) + 1)
    out = np.full_like(champ, np.nan)
    assez = np.zeros_like(valide)
    bon = valide & np.isfinite(champ)
    for i in range(h):
        i0, i1 = max(0, i - demi), min(h, i + demi + 1)
        for j in range(w):
            if not bon[i, j]:
                continue
            j0, j1 = max(0, j - demi), min(w, j + demi + 1)
            m = bon[i0:i1, j0:j1]
            if int(m.sum()) < minimum:
                continue
            uu, vv = np.nonzero(m)
            A = np.stack([np.ones(len(uu)), uu + i0 - i, vv + j0 - j], axis=1)
            coef, *_ = np.linalg.lstsq(A, champ[i0:i1, j0:j1][m], rcond=None)
            out[i, j] = coef[0]
            assez[i, j] = True
    return out, assez


def ajustements(degres=DEGRES, demi_local: int = DEMI_LOCAL) -> list[tuple[str, str, int]]:
    """Les champs comparés : `(nom, genre, paramètre)`.

    ⚠ L'ordre est lu : le brut, puis le voisinage en service, puis les surfaces par degré
    croissant, puis la composition. Un tableau publié dans un autre ordre se lirait comme une
    liste de méthodes sans rapport, alors que c'est une échelle.
    """
    out = [("brut", "brut", 0), ("median_3", "median", 1)]
    out += [(f"surface_{d}", "surface", int(d)) for d in degres]
    out += [("plan_local", "local", int(demi_local)),
            ("median_puis_surface_1", "compose", 1)]
    return out


def appliquer(nom: str, genre: str, param: int, champ: np.ndarray,
              valide: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Le champ transformé par cet ajustement, et les cellules qu'il retient."""
    from le_raccrochage_a_la_matiere import accorder_les_voisins  # noqa: PLC0415

    if genre == "brut":
        return champ, valide.copy()
    if genre == "median":
        return accorder_les_voisins(champ, valide, demi=param)
    if genre == "surface":
        return ajuster_surface(champ, valide, param)
    if genre == "local":
        return ajuster_localement(champ, valide, param)
    if genre == "compose":
        # ⭐ LA COMPOSITION QUE LE DÉPÔT A DÉJÀ SOUS LA MAIN : le voisinage en service, puis une
        # surface. C'est le seul candidat qui utilise ce qui marche déjà au lieu de le remplacer.
        lisse, garde = accorder_les_voisins(champ, valide, demi=1)
        return ajuster_surface(lisse, garde, param)
    raise ValueError(f"ajustement inconnu : {genre}")


def mesurer(graine: int = 42, minimum: int = 30, cache_actif: bool = True,
            cote: float | None = None, fenetre_grille: int | None = None,
            degres=DEGRES, demi_local: int = DEMI_LOCAL,
            corpus: dict | None = None, volume=None) -> dict:
    """Ce que chaque façon de rendre le champ lisse coûte à la marche."""
    from le_raccrochage_choisit_il_bien import decalage_de_loracle  # noqa: PLC0415

    table = ajustements(degres, demi_local)
    pas = parcourir_les_pas(graine, minimum, cache_actif, cote, fenetre_grille, corpus, volume)
    reglage = next(pas)
    lignes: list[dict] = []
    for ctx in pas:
        brut = {lec: decalages_du_critere(lec, ctx["corr"], ctx["corr_melange"],
                                          ctx["centres"], ctx["L"], ctx["t_fenetre"])
                for lec in LECTURES}
        champs: dict[tuple[str, str], np.ndarray] = {}
        commun = ctx["assez"].copy()
        for lec in LECTURES:
            grille = poser_sur_la_grille(brut[lec], ctx["lisible"], ctx["lisible"].shape)
            for nom, genre, param in table:
                valeurs, garde = appliquer(nom, genre, param, grille, ctx["lisible"])
                champs[(lec, nom)] = valeurs
                # ⚠⚠⚠ UNE SEULE POPULATION POUR TOUT LE TABLEAU. Les surfaces globales ne
                # rétrécissent rien, le voisinage et le plan local si : juger chacun sur ce
                # qu'il lui reste comparerait des populations, et c'est le défaut que cette
                # famille a déjà eu à retirer une fois.
                commun &= garde
        if int(commun.sum()) < minimum:
            reglage["ecartees"] += 1
            continue
        pris = commun[ctx["lisible"]]
        ou = ctx["ou_lisible"]
        entree = dict(de=ctx["de"], vers=ctx["vers"], cellules=int(commun.sum()),
                      cellules_lisibles=int(ctx["lisible"].sum()), bits_de_supervision=1)
        entree["erreur_ne_rien_faire_um"] = round(
            ctx["erreur"](np.zeros(len(ctx["P"])), pris)[0], 1)
        t_oracle, _ = decalage_de_loracle(ctx["P"], ctx["D"], ctx["centres"], ctx["cible"],
                                          reglage["voxel_um"])
        entree["erreur_oracle_um"] = round(ctx["erreur"](t_oracle, pris)[0], 1)
        for lec in LECTURES:
            for nom, _, _ in table:
                grille = champs[(lec, nom)]
                plat = grille[ou[:, 0], ou[:, 1]]
                plat = np.where(np.isfinite(plat), plat, brut[lec])
                entree[f"erreur_{lec}_{nom}_um"] = round(ctx["erreur"](plat, pris)[0], 1)
                if lec == "correlation":
                    entree[f"rugosite_{nom}_vx"] = rugosite(grille, commun)
        lignes.append(entree)

    if not lignes:
        raise RuntimeError("aucun pas ne rend une grille assez peuplée dans la boîte")

    vol = reglage["vol"]
    r = dict(
        fragment="PHerc0500P2", volume=reglage["volume"], voxel_um=reglage["voxel_um"],
        boite=reglage["boite"], pas_nominal_um=reglage["ecart_um"],
        degres=[int(d) for d in degres], demi_local=int(demi_local),
        ajustements=[n for n, _, _ in table], lectures=list(LECTURES),
        paires=len(lignes), paires_ecartees=int(reglage["ecartees"]),
        cellules=int(sum(e["cellules"] for e in lignes)),
        cellules_lisibles=int(sum(e["cellules_lisibles"] for e in lignes)),
        lignes=lignes,
        cout=vol.cache.cout() | dict(voxels_absents=vol.absents, reprises_reseau=vol.reprises))

    def par_pas(cle: str) -> list[float]:
        return [e[cle] for e in lignes]

    resume = []
    for nom, genre, param in table:
        entree = dict(ajustement=nom, genre=genre, parametre=param,
                      deploye=bool(nom == "median_3"),
                      parametres_du_modele=(nombre_de_termes(param)
                                            if genre in ("surface", "compose") else None))
        for lec in LECTURES:
            cle = f"erreur_{lec}_{nom}_um"
            entree[f"erreur_{lec}_um"] = round(float(np.median(par_pas(cle))), 1)
            entree[f"{lec}_contre_ne_rien_faire"] = ecart_apparie(
                par_pas(cle), par_pas("erreur_ne_rien_faire_um"))
            entree[f"{lec}_contre_deploye"] = ecart_apparie(
                par_pas(cle), par_pas(f"erreur_{lec}_median_3_um"))
        a = entree["correlation_contre_deploye"]["ecart_median_um"]
        b = entree["melange_contre_deploye"]["ecart_median_um"]
        # ⭐⭐⭐ CE QUE L'AJUSTEMENT REND DE PLUS SUR LA LECTURE QUE SUR LE BRUIT. Une surface
        # ajustée sur du bruit rend déjà quelque chose de lisse ; sans cette soustraction, on
        # créditerait la lecture d'un geste qui marche sans elle.
        entree["part_hors_lissage_um"] = (None if a is None or b is None else round(a - b, 1))
        entree["rugosite_vx"] = (
            round(float(np.median([e[f"rugosite_{nom}_vx"] for e in lignes
                                   if e[f"rugosite_{nom}_vx"] is not None])), 2)
            if any(e[f"rugosite_{nom}_vx"] is not None for e in lignes) else None)
        resume.append(entree)
    r["resume"] = resume

    def trouver(nom: str) -> dict:
        return next(x for x in resume if x["ajustement"] == nom)

    r["erreur_ne_rien_faire_mediane_um"] = round(
        float(np.median(par_pas("erreur_ne_rien_faire_um"))), 1)
    r["erreur_oracle_mediane_um"] = round(
        float(np.median(par_pas("erreur_oracle_um"))), 1)
    r["etage_deploye"] = trouver("median_3")
    candidats = [x for x in resume if not x["deploye"] and x["ajustement"] != "brut"]
    r["meilleur_ajustement"] = min(
        candidats, key=lambda x: x["correlation_contre_deploye"]["ecart_median_um"])
    # ⭐⭐⭐ LE VERDICT QUE CE FICHIER EXISTE POUR RENDRE : un champ lisse PAR CONSTRUCTION
    # bat-il le voisinage en service ? Et il faut qu'il tranche, pas seulement qu'il devance.
    r["un_champ_construit_bat_le_deploye"] = tranche(
        r["meilleur_ajustement"]["correlation_contre_deploye"])
    # ⚠⚠ ET LA MÊME QUESTION NETTE DU LISSAGE : si le meilleur ajustement gagne autant sur le
    # bruit que sur la lecture, ce qu'il ajoute n'est pas de la lecture.
    r["le_gain_du_meilleur_est_hors_lissage"] = bool(
        r["meilleur_ajustement"]["part_hors_lissage_um"] is not None
        and r["meilleur_ajustement"]["part_hors_lissage_um"] < 0)
    r["rugosites"] = {x["ajustement"]: x["rugosite_vx"] for x in resume}
    return r


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    v("le nombre de termes suit le degré", [nombre_de_termes(d) for d in (0, 1, 2, 3)]
      == [1, 3, 6, 10])
    v("l'échelle part du brut, contient le voisinage en service et finit par la composition",
      [n for n, _, _ in ajustements()][:2] == ["brut", "median_3"]
      and [n for n, _, _ in ajustements()][-1] == "median_puis_surface_1",
      str([n for n, _, _ in ajustements()]))

    # --- l'ajustement de surface ---
    h = w = 21
    uu, vv = np.meshgrid(np.arange(h), np.arange(w), indexing="ij")
    ok = np.ones((h, w), dtype=bool)
    plan = 3.0 + 0.5 * uu - 0.25 * vv
    ajuste, garde = ajuster_surface(plan, ok, 1)
    # ⚠⚠ UN PLAN AJUSTÉ SUR UN PLAN DOIT LE RENDRE EXACTEMENT : sans ça, c'est le
    # conditionnement de la base qui décide, et le degré trois serait inutilisable.
    v("un plan ajusté sur un plan le rend exactement",
      float(np.max(np.abs(ajuste - plan))) < 1e-9,
      f"{float(np.max(np.abs(ajuste - plan))):.2e}")
    cube = plan + 0.001 * (uu - 10) ** 3
    aj3, _ = ajuster_surface(cube, ok, 3)
    v("... et un degré trois rend une cubique exactement, malgré les indices bruts",
      float(np.max(np.abs(aj3 - cube))) < 1e-6,
      f"{float(np.max(np.abs(aj3 - cube))):.2e}")
    # ⚠⚠⚠ LA PROPRIÉTÉ QUI DONNE SON NOM AU FICHIER : une surface est lisse même sur du bruit,
    # parce qu'elle n'a pas assez de paramètres pour ne pas l'être.
    bruyant = np.random.default_rng(5).normal(0.0, 20.0, (h, w))
    aj_bruit, _ = ajuster_surface(bruyant, ok, 1)
    v("un plan ajusté sur du BRUIT reste lisse — il n'a pas de quoi ne pas l'être",
      rugosite(aj_bruit, ok) < rugosite(bruyant, ok) / 20.0,
      f"{rugosite(aj_bruit, ok)} contre {rugosite(bruyant, ok)}")
    v("... et il ne rétrécit AUCUN masque, contrairement au voisinage",
      int(garde.sum()) == int(ok.sum()))
    v("... un champ trop pauvre pour son degré ne rend rien, plutôt qu'un ajustement au hasard",
      int(ajuster_surface(plan, np.zeros((h, w), dtype=bool), 3)[1].sum()) == 0)

    # --- le plan local ---
    loc, assez_loc = ajuster_localement(plan, ok, demi=4)
    interieur = np.zeros((h, w), dtype=bool)
    interieur[6:-6, 6:-6] = True
    v("un plan local ajusté sur un plan le rend exactement, au cœur de la grille",
      float(np.max(np.abs(loc[interieur] - plan[interieur]))) < 1e-9)
    # ⚠ Il rétrécit, lui : c'est ce qui fixe la population commune de toute la mesure.
    v("... mais il RÉTRÉCIT le masque, comme le voisinage",
      int(assez_loc.sum()) < int(ok.sum()),
      f"{int(assez_loc.sum())} sur {int(ok.sum())}")

    # ⚠⚠⚠ LE CHEMIN QUI PRODUIT LE NOMBRE PUBLIÉ, HORS LIGNE, avec ses DEUX matières.
    from le_corpus_des_spires import geometrie_fabriquee  # noqa: PLC0415

    g0 = geometrie_fabriquee()
    fab = mesurer(minimum=20, degres=(0, 1), demi_local=2, corpus=corpus_fabrique(),
                  volume=volume_fabrique(g0))
    v("la mesure tourne de bout en bout sur des matières fabriquées, sans rien lire",
      fab["paires"] > 0 and len(fab["resume"]) == len(ajustements((0, 1), 2)),
      f"{fab['paires']} pas, {len(fab['resume'])} ajustements")
    v("... tous les ajustements sont jugés sur la MÊME population",
      all(0 < e["cellules"] <= e["cellules_lisibles"] for e in fab["lignes"]),
      str([(e["cellules"], e["cellules_lisibles"]) for e in fab["lignes"]]))
    # ⭐⭐ LA PROPRIÉTÉ MESURÉE SUR LA VRAIE MATIÈRE : les surfaces sont plus lisses que le champ
    # brut, et c'est ce qui distingue « lisse par construction » de « lissé ».
    v("... les surfaces ajustées sont plus lisses que le champ brut",
      all(fab["rugosites"][n] <= fab["rugosites"]["brut"] + 1e-9
          for n in fab["ajustements"] if n != "brut"),
      str(fab["rugosites"]))
    v("... le témoin du gabarit mélangé est mesuré pour CHAQUE ajustement",
      all(x["melange_contre_deploye"] is not None and "part_hors_lissage_um" in x
          for x in fab["resume"]))
    v("... l'ajustement en service a un écart nul à lui-même",
      fab["etage_deploye"]["correlation_contre_deploye"]["ecart_median_um"] == 0.0)
    v("... et le meilleur est choisi sur l'écart APPARIÉ au déployé, pas sur l'erreur brute",
      fab["meilleur_ajustement"]["correlation_contre_deploye"]["intervalle_um"] is not None
      and (not fab["un_champ_construit_bat_le_deploye"]
           or tranche(fab["meilleur_ajustement"]["correlation_contre_deploye"])),
      f"{fab['meilleur_ajustement']['ajustement']} · "
      f"{fab['meilleur_ajustement']['correlation_contre_deploye']}")
    v("le résultat est sérialisable tel quel, sans type qui traîne",
      isinstance(json.dumps(fab), str))
    tampon, souci = io.StringIO(), None
    try:
        with contextlib.redirect_stdout(tampon):
            afficher(fab)
    except Exception as exc:  # noqa: BLE001
        souci = f"{type(exc).__name__}: {exc}"
    v("l'affichage tourne sur ce résultat et va jusqu'à son verdict",
      souci is None and "CONSTRUCTION" in tampon.getvalue(),
      souci or f"{len(tampon.getvalue().splitlines())} lignes")
    hors = None
    try:
        mesurer(minimum=20, degres=(1,), demi_local=2,
                corpus=corpus_fabrique(decalage_vx=5000.0),
                volume=volume_fabrique(geometrie_fabriquee(decalage_vx=5000.0)))
    except RuntimeError as exc:
        hors = str(exc)
    v("un objet entier posé hors de la boîte est REFUSÉ, pas rendu vide",
      hors is not None, str(hors))

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def afficher(r: dict) -> None:
    """Le compte rendu lisible d'un balayage d'ajustements."""
    print(f"pas nominal {r['pas_nominal_um']} µm · {r['paires']} pas "
          f"({r['paires_ecartees']} écartés) · {r['cellules']} cellules retenues sur "
          f"{r['cellules_lisibles']} lisibles\n")
    print(f"{'ajustement':>22} {'param.':>7} {'rugosité':>9} {'LECTURE':>9} "
          f"{'contre le déployé':>34} {'BRUIT':>8} {'HORS LISSAGE':>13}")
    print("-" * 112)

    def court(e) -> str:
        if e is None or e["ecart_median_um"] is None:
            return "—"
        return (f"{e['ecart_median_um']:+6.1f} · {e['pas_ameliores']}/{e['pas']} · "
                f"{str(e['intervalle_um']):>14} · {'TRANCHE' if tranche(e) else '—'}")

    def nombre(valeur, chiffres: int = 2) -> str:
        return "—" if valeur is None else f"{valeur:.{chiffres}f}"

    for x in r["resume"]:
        marque = " ⭐" if x["deploye"] else ""
        p = x["parametres_du_modele"]
        part = ("—" if x["part_hors_lissage_um"] is None
                else f"{x['part_hors_lissage_um']:+.1f} µm")
        print(f"{x['ajustement']:>22} {('—' if p is None else str(p)):>7} "
              f"{nombre(x['rugosite_vx']):>9} "
              f"{x['erreur_correlation_um']:>8.1f}µ "
              f"{court(x['correlation_contre_deploye']):>34} "
              f"{x['erreur_melange_um']:>7.1f}µ {part:>13}{marque}")
    print(f"\nne rien faire {r['erreur_ne_rien_faire_mediane_um']} µm · ⛔ oracle "
          f"{r['erreur_oracle_mediane_um']} µm")
    m = r["meilleur_ajustement"]
    print(f"→ ⭐⭐⭐ un champ lisse PAR CONSTRUCTION bat-il le voisinage en service ? "
          f"{'OUI' if r['un_champ_construit_bat_le_deploye'] else 'NON'} "
          f"(le meilleur : {m['ajustement']} · {court(m['correlation_contre_deploye'])})")
    print(f"→ ⚠ et son gain est-il HORS LISSAGE (plus sur la lecture que sur le bruit) ? "
          f"{'OUI' if r['le_gain_du_meilleur_est_hors_lissage'] else 'NON'} "
          f"({m['part_hors_lissage_um']} µm)")
    print(f"coût : {r['cout']['blocs_telecharges']} blocs, {r['cout']['mebioctets']} Mio")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--cote", type=float, default=None)
    p.add_argument("--fenetre-grille", type=int, default=None, dest="fenetre_grille")
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
