#!/usr/bin/env python3
"""Deux ancres valent-elles mieux qu'une ? — encadrer une spire par les deux côtés.

⚠⚠⚠ POURQUOI CE FICHIER EXISTE. Cinq soupçons ont été testés et écartés sur la mécanique du pas —
la fenêtre, les décalages, le gabarit, les normales, la longueur — et tous portaient sur **la même
marche** : une qui part d'une seule spire et n'a que sa propre reconstruction pour se juger. Ce
fichier change la structure du problème plutôt qu'un réglage : la spire `m` est reconstruite depuis
`m − j` **et** depuis `m + j`, donc par les deux côtés.

⭐⭐ ET LÀ, POUR LA PREMIÈRE FOIS, DEUX RECONSTRUCTIONS SE RENCONTRENT. Des spires concentriques ne
se croisent jamais, donc « plusieurs départs » ne veut rien dire tant qu'on marche tous dans le même
sens ; encadrer, si. Leur **désaccord** est alors une mesure de confiance qui ne demande **aucune
cible** — c'est la seule de tout le chantier, et elle se valide en la confrontant à l'erreur vraie.

⚠⚠ CE QUE ÇA MESURE ET CE QUE ÇA NE MESURE PAS. Un vrai dérouleur n'a qu'une ancre : encadrer
suppose de connaître les deux bouts. Ce n'est donc pas une méthode, c'est une **borne** — elle dit
ce qu'on gagnerait si l'on avait deux ancres au lieu d'une, donc si l'effort doit aller vers une
meilleure propagation ou vers **plus d'ancres**. Le corpus en publie treize.

⚠⚠ LA COMBINAISON DOIT BATTRE LES DEUX BRANCHES, pas la plus mauvaise. Battre la plus mauvaise est
gratuit : « prendre la meilleure des deux » y suffirait, et savoir laquelle est la meilleure demande
la réponse. C'est le verdict rendu.

⚠ Les triplets sont **symétriques** (`m − j`, `m`, `m + j`) : deux branches qui marchent un nombre
de tours différent ne se comparent pas, et leur combinaison mesurerait surtout laquelle a le moins
marché.

⚠ Aucune lecture du volume ici : le pas aveugle est le meilleur dérouleur mesuré, et il ne lit rien.
Cette tranche ne coûte donc pas un bloc.

Usage :
    uv run python src/nappe/derouler_des_deux_bords.py --verifier
    uv run python src/nappe/derouler_des_deux_bords.py \\
        --json docs/mesures/derouler_des_deux_bords.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
for _d in ("commun", "nappe", "encre"):
    sys.path.insert(0, str(RACINE / "src" / _d))

WRAPS = RACINE / "docs" / "mesures" / "les_wraps_publies.json"


def marcher(a: np.ndarray, ok: np.ndarray, tours: int, pas_vx: float,
            sens: float) -> tuple[np.ndarray, np.ndarray]:
    """La grille avancée de `tours` pas aveugles le long de ses propres normales.

    ⚠ C'est exactement le pas du dérouleur publié — `un_pas` y est importé, pas recopié : deux
    implémentations d'un même geste finiraient par ne pas s'accorder, et la comparaison des deux
    branches porterait sur leur désaccord d'implémentation.
    """
    from derouler_par_le_pas_normal import un_pas  # noqa: PLC0415

    for _ in range(tours):
        a, ok = un_pas(a, ok, pas_vx, sens)
        if not ok.any():
            break
    return a, ok


def combiner(gauche: np.ndarray, droite: np.ndarray) -> np.ndarray:
    """Le nuage à mi-chemin des deux branches, point par point du plus proche voisin.

    ⚠⚠ LES DEUX BRANCHES N'ONT PAS LA MÊME GRILLE — elles viennent de deux spires publiées, donc
    de deux paramétrages. Les moyenner cellule à cellule apparierait des points qui n'ont rien à
    voir. L'appariement se fait donc dans l'ESPACE, par plus proche voisin, ce qui est la seule
    correspondance que deux surfaces reconstruites partagent.

    ⚠ Le résultat a la taille de `gauche` : la combinaison est **orientée**, et l'appelant qui
    veut la symétrie doit la demander dans les deux sens. Prétendre le contraire cacherait que
    deux nuages de tailles différentes ne se moyennent pas en un nuage canonique.
    """
    from scipy.spatial import cKDTree  # noqa: PLC0415

    if gauche.size == 0 or droite.size == 0:
        return gauche
    proche = droite[cKDTree(droite).query(gauche, k=1)[1]]
    return 0.5 * (gauche + proche)


def desaccord(gauche: np.ndarray, droite: np.ndarray, voxel_um: float) -> np.ndarray:
    """La distance de chaque point d'une branche à l'autre branche, en micromètres.

    ⚠⚠⚠ C'EST LA SEULE MESURE DE CONFIANCE DU CHANTIER QUI NE DEMANDE PAS LA RÉPONSE. Tout le
    reste — erreur, part perdue, groupement — se calcule contre une spire publiée. Celle-ci se
    calcule entre deux reconstructions, donc un dérouleur pourrait s'en servir en marchant. Reste
    à savoir si elle prédit quelque chose, ce que cette mesure confronte.
    """
    from le_pas_normal_atteint_la_spire import distance_a  # noqa: PLC0415

    return distance_a(gauche, droite, voxel_um)


def ecart_signe(branche: np.ndarray, cible: np.ndarray, direction: np.ndarray,
                voxel_um: float) -> float:
    """De combien la branche DÉPASSE sa cible, le long de sa direction de marche, en µm.

    ⚠⚠⚠ POURQUOI LE SIGNE, ET PAS SEULEMENT LA DISTANCE. Une distance est toujours positive,
    donc deux branches qui se trompent en sens contraires ont exactement le même profil d'erreur
    qu'une qui se trompe deux fois dans le même sens. Le signe sépare les deux, et c'est lui qui
    dit si l'encadrement gagne parce qu'il **annule un biais** ou parce que moyenner deux choses
    bruitées aide toujours un peu. Ce sont deux mécanismes différents et ils ne promettent pas
    la même chose ailleurs.

    ⚠ La projection se fait sur la direction de marche de la branche, pas sur la normale de la
    cible : ce qu'on veut savoir est si elle est allée trop loin, et « trop loin » se compte le
    long du chemin parcouru.
    """
    from scipy.spatial import cKDTree  # noqa: PLC0415

    if branche.size == 0 or cible.size == 0:
        return 0.0
    proche = cible[cKDTree(cible).query(branche, k=1)[1]]
    u = direction / max(1e-12, float(np.linalg.norm(direction)))
    return float(np.median((branche - proche) @ u)) * voxel_um


def triplets(rangs: list[int], j: int) -> list[tuple[int, int, int]]:
    """Les triplets SYMÉTRIQUES `(m − j, m, m + j)` dont les trois spires sont disponibles."""
    presents = set(rangs)
    return [(m - j, m, m + j) for m in sorted(presents)
            if (m - j) in presents and (m + j) in presents]


def mesurer(cote: float | None = None, minimum: int = 30,
            sauts: tuple[int, ...] = (1, 2, 3)) -> dict:
    """Encadrer chaque spire par ses deux voisines à distance `j`, et juger les trois nuages."""
    from le_pas_normal_atteint_la_spire import distance_a, essayer_le_pas, grille, normales  # noqa: PLC0415, E501
    from le_raccrochage_a_la_matiere import BOITE_CENTRE, BOITE_COTE  # noqa: PLC0415
    from les_wraps_publies import VOLUME, VOXEL_UM, wraps_du_fragment  # noqa: PLC0415

    if not WRAPS.is_file():
        raise RuntimeError(f"mesure absente : {WRAPS}")
    ecart_um = float(json.loads(WRAPS.read_text())["resume"]["1"]["mediane_um"])
    pas_vx = ecart_um / VOXEL_UM

    cote = BOITE_COTE if cote is None else float(cote)
    centre = np.array(BOITE_CENTRE)
    lo, hi = centre - cote / 2, centre + cote / 2

    grilles, nuages = {}, {}
    for w in wraps_du_fragment():
        g = grille(w, VOLUME, VOXEL_UM)
        if g is None:
            continue
        a, ok = g
        dans = ok & ((a >= lo) & (a <= hi)).all(axis=-1)
        if int(dans.sum()) < minimum:
            continue
        idx = np.argwhere(dans)
        sous = (slice(int(idx[:, 0].min()), int(idx[:, 0].max()) + 1),
                slice(int(idx[:, 1].min()), int(idx[:, 1].max()) + 1))
        grilles[w["rang"]] = (a[sous].copy(), dans[sous].copy())
        nuages[w["rang"]] = a[ok]

    lignes = []
    for j in sauts:
        for bas, milieu, haut in triplets(sorted(grilles), j):
            cible = nuages[milieu]
            branches, directions = {}, {}
            for depart, cle in ((bas, "montante"), (haut, "descendante")):
                a0, ok0 = grilles[depart]
                n0, bon0 = normales(a0, ok0)
                if not bon0.any():
                    break
                # ⚠⚠ UN BIT DE SUPERVISION PAR BRANCHE, DÉCLARÉ : le signe de la normale vient du
                # paramétrage de la grille, pas de la matière, donc il est fixé au premier pas en
                # regardant la cible — et une seule fois. Les branches en ont donc deux à elles
                # deux, contre un pour une marche simple, et c'est le prix de l'encadrement.
                e = essayer_le_pas(a0[bon0], n0[bon0], cible, pas_vx, VOXEL_UM)
                sens = 1.0 if e["retenu"] == "+" else -1.0
                av, okv = marcher(a0, ok0, j, pas_vx, sens)
                if int(okv.sum()) < minimum:
                    break
                branches[cle] = av[okv]
                # ⚠ La direction de marche de la branche est la normale MOYENNE de sa
                # surface de départ, orientée par le sens retenu : c'est la seule direction que
                # les deux branches partagent au signe près, donc la seule sur laquelle leurs
                # écarts se comparent.
                directions[cle] = sens * n0[bon0].mean(axis=0)
            if len(branches) != 2:
                continue
            g_, d_ = branches["montante"], branches["descendante"]
            # ⚠ La direction de marche retenue pour la projection est celle de la branche
            # MONTANTE : les deux branches vont en sens contraires, donc les projeter chacune
            # sur la sienne rendrait deux nombres positifs et cacherait justement l'opposition
            # qu'on cherche à mesurer.
            axe = directions["montante"]
            s_g = ecart_signe(g_, cible, axe, VOXEL_UM)
            s_d = ecart_signe(d_, cible, axe, VOXEL_UM)
            mid_g = combiner(g_, d_)
            mid_d = combiner(d_, g_)
            e_g = float(np.median(distance_a(g_, cible, VOXEL_UM)))
            e_d = float(np.median(distance_a(d_, cible, VOXEL_UM)))
            e_m = float(np.median(np.concatenate([
                distance_a(mid_g, cible, VOXEL_UM), distance_a(mid_d, cible, VOXEL_UM)])))
            des = float(np.median(desaccord(g_, d_, VOXEL_UM)))
            lignes.append(dict(
                saut=j, depuis_bas=bas, cible=milieu, depuis_haut=haut,
                points_montante=int(len(g_)), points_descendante=int(len(d_)),
                erreur_montante_um=round(e_g, 1), erreur_descendante_um=round(e_d, 1),
                erreur_encadree_um=round(e_m, 1),
                erreur_de_la_meilleure_um=round(min(e_g, e_d), 1),
                desaccord_um=round(des, 1),
                ecart_signe_montante_um=round(s_g, 1),
                ecart_signe_descendante_um=round(s_d, 1),
                signes_opposes=bool(s_g * s_d < 0),
                bits_de_supervision=2))

    if not lignes:
        raise RuntimeError("aucun triplet mesurable dans la boîte")

    def med(cle):
        return round(float(np.median([e[cle] for e in lignes])), 1)

    r = dict(
        fragment="PHerc0500P2", volume=VOLUME, voxel_um=VOXEL_UM,
        boite=dict(centre=list(BOITE_CENTRE), cote_voxels=cote),
        ecart_lu_um=ecart_um, demi_epaisseur_um=round(ecart_um / 2, 2),
        sauts=list(sauts), triplets=len(lignes), lignes=lignes,
        erreur_montante_mediane_um=med("erreur_montante_um"),
        erreur_descendante_mediane_um=med("erreur_descendante_um"),
        erreur_encadree_mediane_um=med("erreur_encadree_um"),
        erreur_de_la_meilleure_mediane_um=med("erreur_de_la_meilleure_um"),
        desaccord_median_um=med("desaccord_um"),
    )
    # ⚠⚠⚠ LE VERDICT EST QUE L'ENCADREMENT BATTE LES DEUX BRANCHES, TRIPLET PAR TRIPLET. Battre
    # leur médiane serait plus facile et ne voudrait rien dire : « prendre la meilleure des deux »
    # y suffirait, et savoir laquelle est la meilleure demande la réponse.
    # ⚠⚠⚠ LE MÉCANISME : les deux branches se trompent-elles en sens CONTRAIRES ? Si oui,
    # l'encadrement annule un biais, et c'est une propriété de la marche qu'on peut espérer
    # ailleurs. Si non, il ne fait que moyenner du bruit, ce qui gagne √2 au mieux et ne promet
    # rien. Les deux mécanismes rendent la même médiane et ne disent pas la même chose.
    r["triplets_aux_signes_opposes"] = sum(1 for e in lignes if e["signes_opposes"])
    r["lencadrement_annule_un_biais"] = bool(
        r["triplets_aux_signes_opposes"] > 0.75 * len(lignes))
    r["ecart_signe_montant_median_um"] = med("ecart_signe_montante_um")
    r["ecart_signe_descendant_median_um"] = med("ecart_signe_descendante_um")
    r["triplets_ou_lencadrement_bat_les_deux"] = sum(
        1 for e in lignes
        if e["erreur_encadree_um"] < min(e["erreur_montante_um"], e["erreur_descendante_um"]))
    r["lencadrement_bat_les_deux"] = bool(
        r["erreur_encadree_mediane_um"] < r["erreur_de_la_meilleure_mediane_um"])
    # ⚠⚠ ET LE DÉSACCORD DOIT PRÉDIRE L'ERREUR pour valoir comme signal de confiance : sans cela
    # c'est un nombre qu'on peut calculer et dont on ne peut rien faire. La corrélation de rang
    # est préférée à celle de Pearson — on demande un ORDRE, pas une droite.
    if len(lignes) > 2:
        from scipy.stats import spearmanr  # noqa: PLC0415

        rho, pval = spearmanr([e["desaccord_um"] for e in lignes],
                              [e["erreur_encadree_um"] for e in lignes])
        r["desaccord_contre_erreur"] = dict(rho=round(float(rho), 3), p=round(float(pval), 4),
                                            n=len(lignes))
        r["le_desaccord_predit_lerreur"] = bool(rho > 0 and pval < 0.05)
    r["sous_la_demi_feuille"] = {
        cle: bool(r[cle] < ecart_um / 2) for cle in
        ("erreur_montante_mediane_um", "erreur_descendante_mediane_um",
         "erreur_encadree_mediane_um")}
    return r


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # --- les triplets ---
    v("un triplet est symétrique et ses trois spires sont là",
      triplets([4, 5, 6, 7], 1) == [(4, 5, 6), (5, 6, 7)], str(triplets([4, 5, 6, 7], 1)))
    v("... et un trou en retire ceux qui le traversent",
      triplets([4, 5, 7, 8], 1) == [], str(triplets([4, 5, 7, 8], 1)))
    v("un saut plus grand donne d'autres triplets",
      triplets([4, 5, 6, 7, 8], 2) == [(4, 6, 8)], str(triplets([4, 5, 6, 7, 8], 2)))

    # --- la marche, sur un plan dont on connaît la cible ---
    uu, vv = np.meshgrid(np.arange(14.0), np.arange(14.0), indexing="ij")
    plan = np.stack([uu * 3 + 100, vv * 3 + 100, np.full(uu.shape, 50.0)], axis=-1)
    ok = np.ones(plan.shape[:2], dtype=bool)
    av, okv = marcher(plan, ok, 2, 10.0, 1.0)
    v("deux pas de dix avancent de vingt", abs(float(np.median(av[okv][:, 2])) - 70.0) < 1e-9,
      str(float(np.median(av[okv][:, 2]))))
    # ⚠ Le masque fond d'une cellule par tour : le compte est rendu, pas caché.
    v("... et la grille perd une cellule de bord par tour",
      int(okv.sum()) == 10 * 10, str(int(okv.sum())))

    # --- la combinaison ---
    g = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]])
    d = np.array([[0.0, 0.0, 10.0], [1.0, 0.0, 10.0]])
    v("la combinaison tombe à mi-chemin",
      bool(np.allclose(combiner(g, d)[:, 2], 5.0)), str(combiner(g, d)))
    v("... et combiner un nuage avec lui-même ne le déplace pas",
      bool(np.allclose(combiner(g, g), g)))
    # ⚠⚠ L'APPARIEMENT EST SPATIAL, PAS PAR INDICE : deux grilles différentes n'ont pas les mêmes
    # cellules, et un appariement par indice moyennerait des points sans rapport.
    d_melange = d[::-1].copy()
    v("l'appariement se fait par plus proche voisin, pas par indice",
      bool(np.allclose(combiner(g, d_melange), combiner(g, d))))
    v("un nuage vide laisse l'autre en place", bool(np.allclose(combiner(g, np.zeros((0, 3))), g)))
    # ⚠ La combinaison est ORIENTÉE : deux nuages de tailles différentes n'ont pas de milieu
    # canonique, et prétendre le contraire cacherait l'asymétrie.
    v("la combinaison a la taille de son premier argument",
      combiner(g, np.vstack([d, d]))
      .shape[0] == 2 and combiner(np.vstack([g, g]), d).shape[0] == 4)

    # --- le désaccord ---
    ds = desaccord(g, d, 2.0)
    v("le désaccord vaut la distance entre les deux branches",
      bool(np.allclose(ds, 20.0)), str(ds))
    v("... et il est nul entre une branche et elle-même",
      bool(np.allclose(desaccord(g, g, 2.0), 0.0)))
    # ⚠⚠⚠ LE TÉMOIN QUI COMPTE : une combinaison ne doit PAS être meilleure par construction.
    # Deux branches du MÊME côté de la cible ont un milieu qui reste du même côté, donc pas
    # meilleur que la plus proche — sans ce contrôle, « l'encadrement gagne » serait une
    # propriété de la moyenne et pas de l'encadrement.
    cible = np.array([[0.0, 0.0, 100.0], [1.0, 0.0, 100.0]])
    from le_pas_normal_atteint_la_spire import distance_a  # noqa: PLC0415
    meme_cote_a = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]])
    meme_cote_b = np.array([[0.0, 0.0, 20.0], [1.0, 0.0, 20.0]])
    mid = combiner(meme_cote_a, meme_cote_b)
    v("deux branches du même côté : leur milieu ne bat pas la plus proche",
      float(np.median(distance_a(mid, cible, 1.0)))
      >= float(np.median(distance_a(meme_cote_b, cible, 1.0))),
      f"{float(np.median(distance_a(mid, cible, 1.0)))} contre "
      f"{float(np.median(distance_a(meme_cote_b, cible, 1.0)))}")
    # ⚠ … alors que deux branches qui l'ENCADRENT doivent, elles, faire mieux que les deux.
    enc_a = np.array([[0.0, 0.0, 60.0], [1.0, 0.0, 60.0]])
    enc_b = np.array([[0.0, 0.0, 150.0], [1.0, 0.0, 150.0]])
    mid2 = combiner(enc_a, enc_b)
    v("... et deux branches qui encadrent font mieux que les deux",
      float(np.median(distance_a(mid2, cible, 1.0)))
      < min(float(np.median(distance_a(enc_a, cible, 1.0))),
            float(np.median(distance_a(enc_b, cible, 1.0)))),
      str(float(np.median(distance_a(mid2, cible, 1.0)))))

    # --- l'écart SIGNÉ ---
    axe = np.array([0.0, 0.0, 1.0])
    v("une branche qui dépasse rend un écart positif",
      ecart_signe(enc_b, cible, axe, 1.0) > 0, str(ecart_signe(enc_b, cible, axe, 1.0)))
    v("... et une branche qui n'est pas allée assez loin, un écart négatif",
      ecart_signe(enc_a, cible, axe, 1.0) < 0, str(ecart_signe(enc_a, cible, axe, 1.0)))
    # ⚠⚠⚠ C'EST CE SIGNE QUI SÉPARE LES DEUX MÉCANISMES : deux branches du MÊME côté rendent le
    # même signe, donc leur moyenne ne peut pas annuler de biais — et c'est exactement le cas
    # où le contrôle plus haut montre que l'encadrement ne gagne pas.
    v("deux branches du même côté rendent le même signe",
      ecart_signe(meme_cote_a, cible, axe, 1.0)
      * ecart_signe(meme_cote_b, cible, axe, 1.0) > 0)
    v("... et deux branches qui encadrent, des signes opposés",
      ecart_signe(enc_a, cible, axe, 1.0) * ecart_signe(enc_b, cible, axe, 1.0) < 0)
    v("l'écart signé est nul contre soi-même",
      abs(ecart_signe(cible, cible, axe, 1.0)) < 1e-9)
    v("... et une cible vide ne rend pas d'écart",
      ecart_signe(enc_a, np.zeros((0, 3)), axe, 1.0) == 0.0)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--cote", type=float, default=None)
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(cote=a.cote)
    print(f"écart inter-feuilles {r['ecart_lu_um']} µm · demi-épaisseur "
          f"{r['demi_epaisseur_um']} µm · {r['triplets']} triplets\n")
    print(f"{'saut':>5} {'triplet':>12} {'montante':>10} {'descend.':>10} {'ENCADRÉE':>10} "
          f"{'désaccord':>11}")
    print("-" * 64)
    for e in r["lignes"]:
        trio = f"{e['depuis_bas']}→{e['cible']}←{e['depuis_haut']}"
        print(f"{e['saut']:>5} {trio:>12} "
              f"{e['erreur_montante_um']:>9.0f}µ {e['erreur_descendante_um']:>9.0f}µ "
              f"{e['erreur_encadree_um']:>9.0f}µ {e['desaccord_um']:>10.0f}µ")
    print(f"\nmédianes : montante {r['erreur_montante_mediane_um']} µm · descendante "
          f"{r['erreur_descendante_mediane_um']} µm · encadrée "
          f"{r['erreur_encadree_mediane_um']} µm")
    print(f"la meilleure des deux branches : {r['erreur_de_la_meilleure_mediane_um']} µm "
          "(elle demande de savoir laquelle)")
    print(f"désaccord entre branches : {r['desaccord_median_um']} µm")
    print(f"écart SIGNÉ le long de la marche montante : montante "
          f"{r['ecart_signe_montant_median_um']:+.1f} µm · descendante "
          f"{r['ecart_signe_descendant_median_um']:+.1f} µm → signes opposés sur "
          f"{r['triplets_aux_signes_opposes']} triplets sur {r['triplets']}, donc "
          f"{'un BIAIS annulé' if r['lencadrement_annule_un_biais'] else 'du bruit moyenné'}")
    if "desaccord_contre_erreur" in r:
        d = r["desaccord_contre_erreur"]
        print(f"le désaccord prédit-il l'erreur ? rho {d['rho']} (p {d['p']}, n {d['n']}) → "
              f"{'OUI' if r['le_desaccord_predit_lerreur'] else 'NON'}")
    print(f"\n→ l'encadrement bat les DEUX branches : "
          f"{'OUI' if r['lencadrement_bat_les_deux'] else 'NON'} "
          f"({r['triplets_ou_lencadrement_bat_les_deux']} triplets sur {r['triplets']})")
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
