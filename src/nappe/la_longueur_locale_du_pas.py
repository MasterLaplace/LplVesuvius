#!/usr/bin/env python3
"""À quelle distance est la feuille SUIVANTE, ici ? — la longueur du pas, lue dans le volume.

⚠⚠⚠ POURQUOI CE FICHIER EXISTE. Quatre soupçons ont été testés et écartés sur la mécanique du
raccrochage — la fenêtre, les décalages, le gabarit, les normales — et toutes ces marches
avancent de la **même** longueur partout : la médiane publiée, 135,5 µm. Or le corpus dit que
l'écart entre spires consécutives va de **60,5 µm** au premier décile à **295,1** au neuvième,
soit un facteur **cinq**. Avancer d'une médiane sur un terrain qui varie d'un facteur cinq n'est
pas une approximation, c'est une erreur systématique par endroit.

⭐⭐ ET CETTE LONGUEUR SE LIT SANS LA CIBLE. La crête suivante le long de la normale **est** la
feuille voisine. Le gabarit lu sur la surface de départ dit à quoi ressemble une feuille ; le
chercher dans une fenêtre qui s'ouvre **vers l'extérieur** dit à quelle distance est la
prochaine. Rien de tout ça ne demande de connaître la spire d'arrivée.

⚠⚠ LA FENÊTRE EST DÉRIVÉE, PAS CHOISIE : de **une demi-longueur nominale à une et demie**. En
deçà, on retrouverait la feuille sur laquelle on se tient ; au-delà, on peut sauter la voisine
et attraper la suivante. C'est la seule bande où « la prochaine crête » veut dire quelque chose.

⚠⚠⚠ ET L'ARBITRE EST DEHORS. La distribution des longueurs lues est confrontée à celle des
écarts entre spires **publiées**, qui n'entre à aucun moment dans la lecture. Si les deux
s'accordent sur leurs déciles, le volume mesure bien ce que la géométrie publie ; si elles
divergent, la lecture mesure autre chose et il faut le dire avant de s'en servir.

⚠ Le témoin est le gabarit **mélangé** : même fenêtre, même recherche, même géométrie, seul le
lien entre la distance et la matière est coupé. Il rend le plancher de bruit d'une distance
tirée dans la fenêtre.

Usage :
    uv run python src/nappe/la_longueur_locale_du_pas.py --verifier
    uv run python src/nappe/la_longueur_locale_du_pas.py \\
        --json docs/mesures/la_longueur_locale_du_pas.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
for _d in ("commun", "nappe", "encre", "tracecheck"):
    sys.path.insert(0, str(RACINE / "src" / _d))

WRAPS = RACINE / "docs" / "mesures" / "les_wraps_publies.json"


def bornes_de_recherche(pas_vx: float) -> tuple[float, float]:
    """La bande où « la prochaine crête » veut dire quelque chose, en voxels.

    ⚠⚠ DÉRIVÉE, PAS CHOISIE. Sous une demi-longueur on retrouve la feuille de départ ; au-delà
    d'une et demie on peut sauter la voisine. Ces deux bornes ne sont pas des réglages : elles
    sont les seules qui rendent la question bien posée.
    """
    return 0.5 * pas_vx, 1.5 * pas_vx


def longueurs_lues(points: np.ndarray, directions: np.ndarray, gabarit: np.ndarray,
                   bas_vx: float, haut_vx: float, volume, demi_gab: int,
                   melanger=None) -> tuple[np.ndarray, np.ndarray, float]:
    """La distance à la crête suivante, pour chaque point, le long de sa direction.

    Rend `(longueurs en voxels, masque des lignes lisibles, force médiane de la corrélation)`.

    ⚠⚠ La ligne est lue AU-DELÀ des bornes, de la largeur du gabarit : une forme centrée sur la
    borne haute a besoin de sa moitié droite pour être reconnue. Chercher sur exactement la
    bande demandée amputerait les candidats des deux bouts, donc rendrait systématiquement des
    longueurs trop centrales.
    """
    from le_raccrochage_a_la_matiere import correler, decalage_retenu, le_long  # noqa: PLC0415

    t = np.arange(bas_vx - demi_gab, haut_vx + demi_gab + 1e-9, 1.0)
    v, ok = le_long(points, directions, t, volume)
    if not ok.any():
        return np.zeros(0), ok, 0.0
    gab = gabarit if melanger is None else melanger.permuted(gabarit)
    corr, centres = correler(v[ok], gab, t)
    dedans = (centres >= bas_vx) & (centres <= haut_vx)
    if not dedans.any():
        return np.zeros(0), np.zeros(len(points), dtype=bool), 0.0
    # ⚠⚠⚠ LA FORCE DE LA CORRÉLATION EST RENDUE, et ce n'est pas décoratif : c'est elle qui
    # permet de CHOISIR le sens. Sans elle l'appelant n'avait que le nombre de lignes lisibles,
    # qui est presque toujours le même des deux côtés — donc son `max` retombait sur le premier
    # sens essayé, et le sens était codé en dur derrière un commentaire qui prétendait le
    # dériver. Payé le 2026-09-06.
    force = float(np.median(corr[:, dedans].max(axis=1)))
    return decalage_retenu(corr[:, dedans], centres[dedans]), ok, force


def deciles(valeurs: np.ndarray) -> dict:
    """Les trois quantiles que le corpus publie pour ses écarts entre spires."""
    if valeurs.size == 0:
        return dict(p10=None, mediane=None, p90=None, n=0)
    return dict(p10=round(float(np.percentile(valeurs, 10)), 1),
                mediane=round(float(np.median(valeurs)), 1),
                p90=round(float(np.percentile(valeurs, 90)), 1),
                n=int(valeurs.size))


def accord_des_distributions(lues: dict, publiees: dict) -> dict:
    """De combien les deux distributions s'écartent, décile par décile.

    ⚠⚠ L'ÉCART EST RENDU EN PART DE LA MÉDIANE PUBLIÉE, pas en micromètres bruts : dire « 40 µm
    d'écart » ne veut rien dire tant qu'on ne sait pas si la grandeur en vaut 60 ou 300. Et les
    trois déciles sont rendus séparément — deux distributions peuvent partager leur médiane et
    n'avoir aucune queue en commun, ce qui est exactement le cas qu'on cherche à trancher.
    """
    out = {}
    for cle in ("p10", "mediane", "p90"):
        a, b = lues.get(cle), publiees.get(cle)
        out[cle] = None if (a is None or b is None or not publiees.get("mediane")) else round(
            (a - b) / publiees["mediane"], 3)
    return out


def _publiees(lu: dict) -> dict:
    """Les écarts entre spires consécutives que le corpus publie, en micromètres.

    ⚠ Ils sont pris sur les paires **consécutives** uniquement (`sauts["1"]`) : les sauts de
    deux ou trois spires mesurent autre chose, et les mélanger gonflerait la queue haute avec
    des distances qui ne sont pas des voisinages.
    """
    p10 = [e["p10_um"] for e in lu["sauts"]["1"]]
    med = [e["mediane_um"] for e in lu["sauts"]["1"]]
    p90 = [e["p90_um"] for e in lu["sauts"]["1"]]
    return dict(p10=round(float(np.median(p10)), 1), mediane=round(float(np.median(med)), 1),
                p90=round(float(np.median(p90)), 1), n=len(med))


def mesurer(echantillon: int = 2000, graine: int = 42, cache_actif: bool = True,
            cote: float | None = None) -> dict:
    """La longueur locale du pas, lue dans le volume, confrontée aux écarts publiés."""
    import tracecheck as tc  # noqa: PLC0415

    from le_pas_normal_atteint_la_spire import distance_a, grille, normales  # noqa: PLC0415
    from le_raccrochage_a_la_matiere import (  # noqa: PLC0415
        BOITE_CENTRE, BOITE_COTE, CacheDisque, Volume, ZARR, accorde_aux_spires, le_long,
        profil_autour, url_du_volume,
    )
    from les_wraps_publies import VOLUME, VOXEL_UM, wraps_du_fragment  # noqa: PLC0415

    if not accorde_aux_spires():
        raise RuntimeError(f"le volume {ZARR} n'est pas celui des spires ({VOLUME})")
    if not WRAPS.is_file():
        raise RuntimeError(f"mesure absente : {WRAPS}")
    lu = json.loads(WRAPS.read_text())
    ecart_um = float(lu["resume"]["1"]["mediane_um"])
    pas_vx = ecart_um / VOXEL_UM
    demi_gab = round(pas_vx / 4.0)
    bas, haut = bornes_de_recherche(pas_vx)

    url = url_du_volume()
    meta = tc.array_meta(url, 0, 120)
    cache = CacheDisque(actif=cache_actif)
    vol = Volume(url, meta, cache)

    cote = BOITE_COTE if cote is None else float(cote)
    centre = np.array(BOITE_CENTRE)
    lo, hi = centre - cote / 2, centre + cote / 2
    rng = np.random.default_rng(graine)
    t_gab = np.arange(-demi_gab, demi_gab + 1e-9, 1.0)

    lignes, toutes, toutes_melangees, ecarts_au_temoin = [], [], [], []
    for w in wraps_du_fragment():
        g = grille(w, VOLUME, VOXEL_UM)
        if g is None:
            continue
        a, ok = g
        n, bon = normales(a, ok)
        dans = bon & ((a >= lo) & (a <= hi)).all(axis=-1)
        if int(dans.sum()) < 30:
            continue
        idx = np.argwhere(dans)
        pris = idx[rng.choice(len(idx), size=min(echantillon, len(idx)), replace=False)]
        p = a[pris[:, 0], pris[:, 1]]
        d = n[pris[:, 0], pris[:, 1]]

        # ⚠⚠⚠ LE SENS EST DÉRIVÉ DE LA MATIÈRE, PAS DE LA CIBLE. La feuille suivante est du
        # côté où la crête suivante existe ; les deux sens sont essayés et celui qui rend la
        # meilleure corrélation gagne. C'est ce qui rend la lecture utilisable par un dérouleur
        # qui n'a pas de spire d'arrivée sous la main.
        vg, okg = le_long(p, d, t_gab, vol)
        if okg.sum() < 30:
            continue
        gab = profil_autour(vg[okg])
        scores = {}
        for sens in (+1.0, -1.0):
            scores[sens] = longueurs_lues(p, d * sens, gab, bas, haut, vol, demi_gab)
        # ⚠⚠ Le sens est celui où la crête suivante RESSEMBLE le plus à une feuille, pas celui
        # où il reste le plus de lignes lisibles : les deux côtés sont presque toujours
        # lisibles autant, donc ce second critère ne choisissait rien.
        sens = max(scores, key=lambda s: scores[s][2])
        lg, okl, force = scores[sens]
        if lg.size == 0:
            continue
        um = lg * VOXEL_UM
        toutes.append(um)
        mel, _, force_mel = longueurs_lues(p, d * sens, gab, bas, haut, vol, demi_gab,
                                           melanger=rng)
        if mel.size == lg.size and mel.size:
            toutes_melangees.append(mel * VOXEL_UM)
            # ⚠⚠⚠ LA COMPARAISON QUI DÉCIDE EST CELLULE PAR CELLULE, PAS DÉCILE PAR DÉCILE.
            # Deux lectures peuvent partager leurs trois quantiles et n'avoir aucun point
            # commun ; et surtout, la médiane d'un tirage UNIFORME dans [0,5 L ; 1,5 L] vaut
            # exactement L, donc une médiane qui tombe sur le nominal ne prouve rien du tout.
            # Si la lecture et son témoin s'accordent cellule à cellule, elles mesurent la même
            # chose — et cette chose est la fenêtre.
            ecarts_au_temoin.append(np.abs(um - mel * VOXEL_UM))
        lignes.append(dict(spire=w["rang"], cellules=int(okl.sum()),
                           sens="+" if sens > 0 else "-",
                           force_corr=round(force, 3),
                           force_corr_autre_sens=round(scores[-sens][2], 3),
                           force_corr_melange=round(force_mel, 3), **deciles(um)))

    if not toutes:
        raise RuntimeError("aucune spire mesurable dans la boîte")

    lues = deciles(np.concatenate(toutes))
    melangees = deciles(np.concatenate(toutes_melangees)) if toutes_melangees else deciles(
        np.zeros(0))
    pub = _publiees(lu)
    r = dict(
        fragment="PHerc0500P2", volume=VOLUME, voxel_um=VOXEL_UM, zarr=ZARR,
        boite=dict(centre=list(BOITE_CENTRE), cote_voxels=cote),
        pas_nominal_um=ecart_um,
        fenetre_um=[round(bas * VOXEL_UM, 1), round(haut * VOXEL_UM, 1)],
        demi_gabarit_um=round(demi_gab * VOXEL_UM, 1),
        spires=len(lignes), par_spire=lignes,
        longueurs_lues=lues, longueurs_publiees=pub, temoin_melange=melangees,
        accord=accord_des_distributions(lues, pub),
        accord_du_temoin=accord_des_distributions(melangees, pub),
        cout=cache.cout() | dict(voxels_absents=vol.absents, reprises_reseau=vol.reprises),
    )
    # ⚠⚠ LE VERDICT PORTE SUR LES TROIS DÉCILES, pas sur la seule médiane : une lecture qui
    # tomberait juste au milieu et raterait les deux queues mesurerait la fenêtre, pas la
    # matière — la médiane d'un tirage uniforme dans [0,5 L ; 1,5 L] vaut exactement L.
    # ⚠⚠⚠ LES SPIRES PUBLIÉES PARTAGENT UNE ORIENTATION DE GRILLE — mesuré ailleurs, sur les
    # douze paires, où le sens retenu est le même pour toutes. Une lecture qui porterait du
    # signal choisirait donc le MÊME sens partout. Qu'elle en change d'une spire à l'autre est
    # une seconde preuve, et celle-là ne demande **aucune cible**.
    r["sens_unanime"] = len({e["sens"] for e in lignes}) == 1
    r["spires_au_sens_minoritaire"] = min(
        sum(1 for e in lignes if e["sens"] == "+"),
        sum(1 for e in lignes if e["sens"] == "-"))
    r["ecart_median_relatif"] = r["accord"]["mediane"]
    r["la_lecture_retrouve_les_ecarts_publies"] = bool(
        all(v is not None and abs(v) < 0.25 for v in r["accord"].values()))
    # ⚠⚠⚠ LA COMPARAISON DES DISTRIBUTIONS NE DISCRIMINE PAS, ET LE DIRE EST LE RÉSULTAT. La
    # lecture et son témoin rendent les mêmes trois déciles à quelques micromètres près ; un
    # champ qui aurait annoncé « elle bat le témoin » sur cette base aurait été vrai au sens
    # arithmétique et faux au sens qui compte. C'est la comparaison CELLULE PAR CELLULE qui
    # tranche, et elle dit l'inverse.
    r["les_distributions_se_separent"] = bool(
        all(v is not None for v in r["accord"].values())
        and all(v is not None for v in r["accord_du_temoin"].values())
        and max(abs(a - b) for a, b in zip(r["accord"].values(),
                                           r["accord_du_temoin"].values())) > 0.1)
    ec = np.concatenate(ecarts_au_temoin) if ecarts_au_temoin else np.zeros(0)
    r["ecart_au_temoin_um"] = deciles(ec)
    # ⚠⚠ L'ÉCHELLE DE RÉFÉRENCE EST LA LARGEUR DE LA FENÊTRE, pas un nombre : deux lectures qui
    # diffèrent d'un dixième de la fenêtre où elles cherchent toutes deux sont la même lecture.
    largeur = (haut - bas) * VOXEL_UM
    r["largeur_de_la_fenetre_um"] = round(largeur, 1)
    r["part_de_la_fenetre_qui_separe_du_temoin"] = (
        None if ec.size == 0 else round(float(np.median(ec)) / largeur, 3))
    # ⚠⚠⚠ ET LA RÉFÉRENCE EST DÉRIVÉE, PAS CHOISIE. Si la lecture et son témoin étaient deux
    # tirages INDÉPENDANTS et uniformes dans la même fenêtre de largeur W, la médiane de leur
    # écart vaudrait exactement W(1 − 1/√2) ≈ 0,293 W. Une lecture qui porte du signal doit en
    # être NETTEMENT en dessous — elle et son témoin partiraient du même endroit. Ma première
    # version comparait à 0,15, un nombre que j'avais posé ; celui-ci se calcule.
    r["ecart_attendu_si_tirages_independants"] = round(1.0 - 1.0 / np.sqrt(2.0), 3)
    r["indiscernable_du_temoin"] = bool(
        ec.size > 0
        and r["part_de_la_fenetre_qui_separe_du_temoin"]
        > r["ecart_attendu_si_tirages_independants"] / 2.0)
    # ⚠⚠⚠ ET LA BORNE HAUTE TRONQUE LA QUEUE : la fenêtre se ferme à une longueur et demie
    # nominale, et le neuvième décile PUBLIÉ est au-delà. Les deux contraintes — exclure la
    # deuxième voisine, atteindre le neuvième décile — sont incompatibles sur ce corpus, et
    # c'est un fait sur la nappe, pas un réglage à corriger.
    r["borne_haute_um"] = round(haut * VOXEL_UM, 1)
    r["la_fenetre_tronque_la_queue_publiee"] = bool(pub["p90"] > haut * VOXEL_UM)
    r["etendue_lue_um"] = (None if lues["p90"] is None else round(lues["p90"] - lues["p10"], 1))
    r["etendue_publiee_um"] = round(pub["p90"] - pub["p10"], 1)
    return r


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    from le_raccrochage_a_la_matiere import Volume  # noqa: PLC0415

    # --- les bornes, dérivées ---
    bas, haut = bornes_de_recherche(60.0)
    v("la fenêtre s'ouvre à une demi-longueur", bas == 30.0, str(bas))
    v("... et se ferme à une longueur et demie", haut == 90.0, str(haut))
    # ⚠⚠ ELLE DOIT EXCLURE LA FEUILLE DE DÉPART (0) ET LA SUIVANTE APRÈS LA VOISINE (2 L) :
    # sans ça « la prochaine crête » désigne trois objets différents selon le point.
    v("... donc elle exclut la feuille de départ et la deuxième voisine",
      bas > 0.0 and haut < 120.0)

    # --- un volume dont les feuilles sont à une distance connue et INÉGALE ---
    # ⚠⚠⚠ L'INÉGALITÉ EST LE CŒUR DE LA FIXTURE, et ma première version ne l'avait pas : avec
    # des feuilles régulièrement espacées, la ligne entière est périodique, donc N'IMPORTE QUEL
    # motif y trouve la période — le gabarit mélangé rendait 59,9 pour une vraie réponse de 60.
    # Un témoin qu'une fixture périodique satisfait ne teste rien. Ici les écarts valent 55, 70
    # puis 55 : lire la longueur LOCALE veut enfin dire quelque chose, et le témoin peut échouer.
    forme = (300, 64, 64)
    bloc = np.zeros(forme, dtype=np.uint8)
    zz = np.arange(forme[0])[:, None, None]
    creux = [40, 95, 165, 220]
    for c in creux:
        bloc |= (55 + 95 * np.exp(-((zz - c) ** 2) / 40.0)).astype(np.uint8)
    # ⚠⚠⚠ ET LES LIGNES DOIVENT DIFFÉRER ENTRE ELLES. Sans bruit, ce volume est constant en x
    # et en y : les vingt-quatre lignes sont la MÊME ligne, donc le témoin du gabarit mélangé
    # a un échantillon de UN et sa médiane est l'unique réponse qu'il a tirée. Il rendait 54,85
    # pour une vraie réponse de 55 — vrai par dégénérescence, pas parce qu'il retrouve la
    # feuille. Un bruit qui varie le long de z ET d'une colonne à l'autre le rend capable
    # d'échouer.
    zz3, yy3, xx3 = np.meshgrid(*[np.arange(n_) for n_ in forme], indexing="ij")
    grain = (((zz3 * 15485863 + yy3 * 7919 + xx3 * 104729) % 41) - 20).astype(np.int16)
    bloc = np.clip(bloc.astype(np.int16) + grain, 0, 255).astype(np.uint8)
    faux = dict(shape=list(forme), chunks=[300, 64, 64], dtype="|u1",
                dimension_separator="/", compressor=None)

    class VolumeFictif(Volume):
        def _bloc(self, cz, cy, cx):
            return bloc

    vf = VolumeFictif("", faux, {})
    from le_raccrochage_a_la_matiere import le_long, profil_autour  # noqa: PLC0415

    t_gab = np.arange(-15.0, 15.1, 1.0)
    d = np.tile(np.array([0.0, 0.0, 1.0]), (24, 1))

    def lire_depuis(z0: float, bas: float, haut: float, melange=None):
        pts = np.array([[float(x), 20.0, z0] for x in range(20, 44)])
        vg_, okg_ = le_long(pts, d, t_gab, vf)
        g_ = profil_autour(vg_[okg_])
        return longueurs_lues(pts, d, g_, bas, haut, vf, 15, melanger=melange)[:2]

    lg55, ok55 = lire_depuis(40.0, 27.5, 82.5)
    lg70, ok70 = lire_depuis(95.0, 35.0, 105.0)
    v("la longueur lue suit l'écart LOCAL, ici 55",
      bool(ok55.all()) and abs(float(np.median(lg55)) - 55.0) < 2.0,
      str(float(np.median(lg55))))
    v("... et là 70, sur le même volume", bool(ok70.all())
      and abs(float(np.median(lg70)) - 70.0) < 2.0, str(float(np.median(lg70))))
    # ⚠⚠⚠ ET LE GABARIT MÉLANGÉ N'EST PAS LE BON TÉMOIN ICI — mesuré, pas supposé. Il rend
    # 54,7 pour une vraie réponse de 55, sur des lignes pourtant toutes différentes. La raison
    # est réelle : une permutation garde la DISTRIBUTION des valeurs du gabarit, et contre un
    # profil aussi piqué qu'une crête isolée, presque n'importe quel vecteur de cette
    # distribution corrèle au maximum sur la crête. Le témoin du mélange discrimine sur la
    # donnée réelle, où le profil est bruité et peu piqué ; il ne discrimine pas ici, et le
    # dire vaut mieux que de l'invoquer.
    mel, _ = lire_depuis(40.0, 27.5, 82.5, melange=np.random.default_rng(3))
    v("un gabarit mélangé retrouve QUAND MÊME une crête isolée, et c'est une limite du témoin",
      abs(float(np.median(mel)) - 55.0) < 3.0, str(float(np.median(mel))))
    # ⚠⚠⚠ LE TÉMOIN QUI DISCRIMINE : un volume SANS feuille dans la fenêtre. La lecture ne doit
    # alors rendre aucune longueur concentrée — c'est structurel et sans seuil réglé, on compare
    # l'étalement des réponses à celui obtenu sur le vrai volume.
    plat = np.clip(np.full(forme, 90, dtype=np.int16) + grain, 0, 255).astype(np.uint8)

    class VolumePlat(Volume):
        def _bloc(self, cz, cy, cx):
            return plat

    vp = VolumePlat("", faux, {})
    pts_p = np.array([[float(x), 20.0, 40.0] for x in range(20, 44)])
    vgp, okgp = le_long(pts_p, d, t_gab, vf)
    lg_plat, _, _ = longueurs_lues(pts_p, d, profil_autour(vgp[okgp]), 27.5, 82.5, vp, 15)
    etal_vrai = float(np.percentile(lg55, 90) - np.percentile(lg55, 10))
    etal_plat = float(np.percentile(lg_plat, 90) - np.percentile(lg_plat, 10))
    v("sans feuille dans la fenêtre, les longueurs lues s'étalent", etal_plat > 5 * etal_vrai,
      f"{etal_plat:.1f} contre {etal_vrai:.1f}")
    v("... alors qu'avec une feuille elles se concentrent", etal_vrai < 2.0,
      f"{etal_vrai:.2f}")
    # ⚠⚠ Et la recherche doit rester DANS sa fenêtre, sinon les bornes ne veulent rien dire.
    v("aucune longueur ne sort de la fenêtre",
      bool((lg55 >= 27.5).all() and (lg55 <= 82.5).all()),
      f"{lg55.min()} .. {lg55.max()}")
    # ⚠ Une ligne illisible est écartée, pas comblée.
    _, hors, _ = longueurs_lues(np.array([[20.0, 20.0, 295.0]]), np.array([[0.0, 0.0, 1.0]]),
                             profil_autour(le_long(
                                 np.array([[20.0, 20.0, 40.0]]),
                                 np.array([[0.0, 0.0, 1.0]]), t_gab, vf)[0]),
                             30.0, 90.0, vf, 15)
    v("une ligne qui sort du volume est écartée", not hors.any())

    # --- les déciles et l'accord ---
    # ⚠ Les effectifs sont choisis pour que le décile tombe SUR une valeur : `np.percentile`
    # interpole, donc dix valeurs sur cent mettent le dixième centile entre deux paliers et
    # rendent 19, ce qui a fait échouer ma première version — l'attendu était faux, pas le code.
    ech = np.array([10.0] * 20 + [20.0] * 60 + [40.0] * 20)
    dec = deciles(ech)
    v("les déciles rendent les deux queues et le milieu",
      dec["p10"] == 10.0 and dec["mediane"] == 20.0 and dec["p90"] == 40.0, str(dec))
    v("un échantillon vide ne rend pas de déciles", deciles(np.zeros(0))["n"] == 0)
    acc = accord_des_distributions(dec, dict(p10=10.0, mediane=20.0, p90=40.0))
    v("deux distributions identiques s'accordent à zéro",
      all(abs(x) < 1e-9 for x in acc.values()), str(acc))
    # ⚠⚠⚠ LE CONTRÔLE QUI SÉPARE LA MÉDIANE DES QUEUES : deux distributions peuvent partager
    # leur milieu et n'avoir aucune queue en commun. Un accord jugé sur la seule médiane
    # déclarerait celles-là identiques.
    serre = accord_des_distributions(dict(p10=19.0, mediane=20.0, p90=21.0),
                                     dict(p10=10.0, mediane=20.0, p90=40.0))
    v("... et deux distributions de même médiane, aux queues absentes, ne s'accordent pas",
      abs(serre["mediane"]) < 1e-9 and abs(serre["p10"]) > 0.4 and abs(serre["p90"]) > 0.9,
      str(serre))
    v("l'écart est rendu en part de la médiane publiée",
      abs(accord_des_distributions(dict(p10=None, mediane=30.0, p90=None),
                                   dict(p10=10.0, mediane=20.0, p90=40.0))["mediane"]
          - 0.5) < 1e-9)

    # ⚠⚠⚠ LE SENS DOIT ÊTRE CHOISI PAR LA FORCE DE LA CORRÉLATION, et ce contrôle existe parce
    # que la première version le choisissait par le nombre de lignes lisibles — presque toujours
    # égal des deux côtés, donc son `max` retombait sur le premier sens essayé. Le sens était
    # codé en dur derrière un commentaire qui prétendait le dériver. Ici la matière n'est que
    # d'UN côté, donc les deux forces doivent se séparer nettement.
    pts_s = np.array([[float(x), 20.0, 40.0] for x in range(20, 44)])
    vgs, okgs = le_long(pts_s, d, t_gab, vf)
    gs = profil_autour(vgs[okgs])
    _, _, f_plus = longueurs_lues(pts_s, d, gs, 27.5, 82.5, vf, 15)
    _, _, f_moins = longueurs_lues(pts_s, -d, gs, 27.5, 82.5, vf, 15)
    v("la force de la corrélation sépare les deux sens", f_plus > f_moins + 0.05,
      f"{f_plus:.3f} contre {f_moins:.3f}")
    # ⚠ Et elle doit être rendue AVEC la lecture, sinon l'appelant ne peut pas s'en servir.
    v("... et elle est rendue à côté des longueurs", isinstance(f_plus, float))

    # --- la référence des deux tirages indépendants ---
    # ⚠⚠⚠ CE NOMBRE DÉCIDE, DONC IL SE VÉRIFIE : la médiane de |X − Y| pour deux uniformes
    # indépendants sur une largeur W vaut W(1 − 1/√2). C'est l'étalon auquel l'écart mesuré
    # entre une lecture et son témoin se compare — s'il l'atteint, les deux sont deux tirages
    # dans la fenêtre et la lecture n'a rien lu.
    ru = np.random.default_rng(5)
    x_, y_ = ru.uniform(0.0, 1.0, 200000), ru.uniform(0.0, 1.0, 200000)
    v("deux tirages indépendants dans une fenêtre s'écartent de W(1 − 1/√2)",
      abs(float(np.median(np.abs(x_ - y_))) - (1.0 - 1.0 / np.sqrt(2.0))) < 0.003,
      f"{float(np.median(np.abs(x_ - y_))):.4f} contre {1.0 - 1.0 / np.sqrt(2.0):.4f}")
    # ⚠ Et deux tirages CORRÉLÉS s'en écartent nettement moins — sans quoi l'étalon ne
    # séparerait rien.
    z_ = 0.9 * x_ + 0.1 * y_
    v("... et deux tirages corrélés s'écartent beaucoup moins",
      float(np.median(np.abs(x_ - z_))) < (1.0 - 1.0 / np.sqrt(2.0)) / 2.0,
      f"{float(np.median(np.abs(x_ - z_))):.4f}")

    # --- les écarts publiés, lus de la mesure des spires ---
    faux_lu = dict(sauts={"1": [dict(p10_um=60.0, mediane_um=130.0, p90_um=300.0),
                                dict(p10_um=62.0, mediane_um=140.0, p90_um=290.0)]})
    pub = _publiees(faux_lu)
    v("les écarts publiés sont pris sur les paires consécutives",
      pub["mediane"] == 135.0 and pub["n"] == 2, str(pub))

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--echantillon", type=int, default=2000)
    p.add_argument("--cote", type=float, default=None)
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(a.echantillon, cote=a.cote)
    print(f"pas nominal {r['pas_nominal_um']} µm · fenêtre {r['fenetre_um']} µm · "
          f"{r['spires']} spires")
    print(f"\n{'spire':>6} {'cell.':>6} {'sens':>5} {'p10':>8} {'médiane':>9} {'p90':>8}")
    print("-" * 48)
    for e in r["par_spire"]:
        print(f"{e['spire']:>6} {e['cellules']:>6} {e['sens']:>5} {e['p10']:>7.1f}µ "
              f"{e['mediane']:>8.1f}µ {e['p90']:>7.1f}µ")
    for nom, cle in (("lues dans le volume", "longueurs_lues"),
                     ("publiées (spires)", "longueurs_publiees"),
                     ("témoin mélangé", "temoin_melange")):
        d = r[cle]
        print(f"\n{nom:>22} : p10 {d['p10']} · médiane {d['mediane']} · p90 {d['p90']} "
              f"({d['n']} valeurs)")
    print(f"\naccord (part de la médiane publiée) : {r['accord']}")
    print(f"écart au témoin, cellule par cellule : médiane "
          f"{r['ecart_au_temoin_um']['mediane']} µm sur une fenêtre de "
          f"{r['largeur_de_la_fenetre_um']} µm, soit "
          f"{r['part_de_la_fenetre_qui_separe_du_temoin']}")
    print(f"la fenêtre se ferme à {r['borne_haute_um']} µm et le p90 publié est à "
          f"{r['longueurs_publiees']['p90']} µm — tronquée : "
          f"{'OUI' if r['la_fenetre_tronque_la_queue_publiee'] else 'NON'}")
    print(f"témoin                              : {r['accord_du_temoin']}")
    print(f"étendue lue {r['etendue_lue_um']} µm contre {r['etendue_publiee_um']} publiée")
    print(f"coût : {r['cout']['blocs_telecharges']} blocs, {r['cout']['mebioctets']} Mio")
    print(f"\nsens retenu unanime sur les {r['spires']} spires : "
          f"{'OUI' if r['sens_unanime'] else 'NON'} "
          f"({r['spires_au_sens_minoritaire']} au sens minoritaire) — les grilles publiées, "
          "elles, partagent une orientation")
    print(f"\n→ indiscernable du témoin : "
          f"{'OUI' if r['indiscernable_du_temoin'] else 'NON'}"
          f"  ({r['part_de_la_fenetre_qui_separe_du_temoin']} contre "
          f"{r['ecart_attendu_si_tirages_independants']} attendu pour deux tirages "
          f"indépendants dans la fenêtre)")
    print(f"→ la lecture retrouve les écarts publiés : "
          f"{'OUI' if r['la_lecture_retrouve_les_ecarts_publies'] else 'NON'}"
          f"\n→ les distributions se séparent du témoin : "
          f"{'OUI' if r['les_distributions_se_separent'] else 'NON'}"
          " — donc les déciles ne tranchent pas, seule la comparaison cellule par cellule le fait")
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
