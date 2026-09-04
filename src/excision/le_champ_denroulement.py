#!/usr/bin/env python3
"""Peut-on DIRE sur quelle feuille est un point ? — le prédicat d'identité, et son témoin.

⭐⭐⭐ CE QUE CE FICHIER MESURE, ET C'EST LA MOITIÉ QUI MANQUAIT. L'article établit que le
prédicat peint à la main dans le pipeline de référence est un prédicat d'**identité** — *«
regions judged geometrically consistent with a **single sheet** »* — et que le dépôt n'avait
construit que la **présence** (α : il y a une feuille à portée) et le **placement** (`offset` :
la surface est *sur* elle). L'identité est ce qui coûte 775 heures de pinceau par rouleau.

`76` a rendu un référent utilisable : 81 spires consécutives approuvées par des humains, dont
on sait qu'elles comptent vers l'extérieur et qu'un pas d'indice vaut un écart constant. Ce
fichier s'en sert pour construire un **champ d'enroulement** — pour tout point, l'indice de
spire, en continu — et pose la seule question qui décide :

    ce champ, construit SANS une spire, sait-il dire que cette spire est UNE feuille ?

⚠⚠ LA VALIDATION EST À SPIRE EXCLUE, et sans ça la mesure serait vide. Un champ construit sur
toutes les spires assigne évidemment `k` à la spire `k` : il l'a lue. La question utile est
s'il l'**interpole** — c'est-à-dire si connaître les feuilles `k−1` et `k+1` suffit à placer ce
qui est entre elles. Si oui, un traceur qui atterrit n'importe où dans la bande peut être
**informé** de la feuille qu'il suit ; si non, chaque feuille doit être tracée à la main, et le
pinceau reste.

⚠⚠⚠ ET LE TÉMOIN NÉGATIF EST CONSTRUIT, PAS ESPÉRÉ. Une surface qui traverse l'empilement est
fabriquée à partir du référent lui-même : on prend la spire `k` d'un côté et la spire `k+3` de
l'autre, en fondu sur l'angle. Elle est une surface parfaitement lisse, parfaitement plausible,
et elle traverse **trois feuilles** par construction. Le champ DOIT le voir. Sans ce témoin,
« l'écart d'indice le long d'une spire est petit » serait satisfait par un champ constant, qui
ne mesure rien du tout.

⚠ CE QUE CE FICHIER N'ÉTABLIT PAS :

1. **Que le champ vaille hors de la bande publiée.** Il est bâti par interpolation entre des
   spires connues : au-delà de la dernière, il extrapole, et rien ici ne dit ce que vaut cette
   extrapolation. C'est la limite qui compte pour un déploiement.
2. **Que ce soit le seul prédicat d'identité possible.** C'en est un, adossé au référent. Un
   champ dérivé du volume (résidus d'orientation, `69` A2) répondrait sans référent, et reste
   à mesurer.
3. **Qu'un traceur puisse s'en servir en ligne.** Le champ est une table ; l'y brancher est un
   autre lot.

Usage :
    uv run python src/excision/le_champ_denroulement.py --verifier
    uv run python src/excision/le_champ_denroulement.py --json docs/mesures/le_champ_denroulement.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(RACINE / "src" / "excision")]
from le_sens_des_indices import (  # noqa: E402
    SECTEURS, TRANCHES_Z, centre_de, charger, _spires,
)

ECART_INTER_FEUILLES_VX = {"PHerc0139": 154.1 / 9.362, "PHerc0172": 147.4 / 7.91}
"""L'écart inter-feuilles de chaque rouleau, en voxels de SON régime (`76`). Sert à exprimer la
dérive de l'axe dans l'unité qui la rend lisible : « 65 voxels » ne dit rien, « 3,5 feuilles »
dit que l'axe traverse plusieurs feuilles entre deux tranches."""

SEPARATION_ATTENDUE = {"PHerc0139": 2, "PHerc0172": None}
"""Combien de tranches il faut agréger pour que les deux populations cessent de se recouvrir,
**par rouleau**, et `None` quand elles ne cessent jamais.

⚠⚠⚠ Écrit ici parce que c'est un FAIT MESURÉ sur chaque rouleau, pas un réglage. `77` a
d'abord conclu « les deux populations ne se recouvrent pas » — c'était vrai de `PHerc0139` et
**faux** de `PHerc0172`, où elles se recouvrent à tout niveau d'agrégation testé. Un prédicat
qui marche ici et pas là doit dire lequel. ⚠ La CAUSE est trouvée et mesurée ailleurs
(`la_couture.py`, `77` §8) : une couture angulaire. La retirer restaure la séparation, mais
au prix de 8 % de la circonférence.

⚠ Et sur les DEUX rouleaux, une tranche isolée ne suffit jamais. C'est la mesure de ce que
`42` disait qualitativement — *le prédicat doit désigner des régions, pas des points* — et elle
en donne la taille : deux tranches de hauteur sur `PHerc0139`, aucune taille suffisante sur
`PHerc0172`."""

DEFAUTS_CONNUS = (41, 45)
"""Les spires `w_k` dont `76` a mesuré, par une méthode entièrement différente, que la paire
`(k, k+1)` n'est pas à une feuille : `w045`/`w046` sont la MÊME surface (0,0 µm) et
`w041`/`w042` sont à une demi-feuille. ⚠ Écrites ici pour être **retrouvées**, pas pour être
écartées d'office : le contrôle vérifie que ce sont exactement les positions où un « saut d'une
feuille » fabriqué depuis elles n'en est pas un."""

POINTS_MINIMUM = 8
"""Points exigés dans une cellule (tranche, secteur) pour qu'une spire y ait un rayon."""

SAUTS_DU_TEMOIN = (1, 2, 3)
"""De combien de feuilles les surfaces témoins traversent l'empilement. ⚠ **Plusieurs et pas
une seule** : un témoin unique dirait « le champ voit CE saut-là ». Une rampe dit si l'avance
mesure le **nombre de feuilles franchies**, ce qui est la revendication. Et le saut de **1**
est le cas dur — c'est celui qu'un traceur commet réellement."""


def _grille(nuages: dict[int, tuple]) -> tuple[np.ndarray, np.ndarray, dict]:
    """
    @brief Le repère commun : bornes en hauteur, bornes d'angle, et un centre par tranche.

    ⚠ Le centre est ajusté par tranche sur l'UNION de toutes les spires, pour la raison de
    `76` : l'axe erre avec la hauteur, et un centre global mélangerait des feuilles.
    """
    z_tous = np.concatenate([n[2] for n in nuages.values()])
    bords_z = np.linspace(z_tous.min(), z_tous.max(), TRANCHES_Z + 1)
    bords_t = np.linspace(-np.pi, np.pi, SECTEURS + 1)

    centres = {}
    for i, (lo, hi) in enumerate(zip(bords_z, bords_z[1:])):
        xs, ys = [], []
        for x, y, z in nuages.values():
            s = (z >= lo) & (z < hi)
            if s.sum():
                xs.append(x[s])
                ys.append(y[s])
        if xs:
            centres[i] = centre_de(np.concatenate(xs), np.concatenate(ys))
    return bords_z, bords_t, centres


def _rayons(nuage: tuple, bords_z, bords_t, centres) -> dict[tuple[int, int], float]:
    """
    @brief Le rayon médian d'une spire dans chaque cellule (tranche, secteur) qu'elle occupe.
    """
    x, y, z = nuage
    out: dict[tuple[int, int], float] = {}
    for i, (lo, hi) in enumerate(zip(bords_z, bords_z[1:])):
        if i not in centres:
            continue
        s = (z >= lo) & (z < hi)
        if s.sum() < POINTS_MINIMUM:
            continue
        cx, cy = centres[i]
        t = np.digitize(np.arctan2(y[s] - cy, x[s] - cx), bords_t)
        r = np.hypot(x[s] - cx, y[s] - cy)
        for j in range(1, SECTEURS + 1):
            p = r[t == j]
            if len(p) >= POINTS_MINIMUM:
                out[(i, j)] = float(np.median(p))
    return out


def _indice_interpole(rayon: float, table: list[tuple[float, int]]) -> float | None:
    """
    @brief L'indice de spire d'un rayon, interpolé entre les deux spires qui l'encadrent.

    ⚠ Rend `None` hors de la table plutôt qu'une extrapolation. Extrapoler donnerait un nombre
    pour un point dont on ne sait rien, et un prédicat d'identité qui répond partout est un
    prédicat qui ne refuse jamais.
    """
    if len(table) < 2:
        return None
    for (r0, k0), (r1, k1) in zip(table, table[1:]):
        if r0 <= rayon <= r1:
            if r1 == r0:
                return float(k0)
            return float(k0 + (k1 - k0) * (rayon - r0) / (r1 - r0))
    return None


def _juger(cible: dict, autres: dict[int, dict]) -> dict:
    """
    @brief Ce que le champ, bâti sur `autres`, dit des points de `cible`.

    ⚠⚠⚠ LA GRANDEUR QUI DÉCIDE EST L'AVANCE PAR TOUR, PAS LA DISPERSION — et c'est une
    correction de ma première version, obtenue en regardant ses nombres. J'avais mesuré
    l'étendue de l'indice le long d'une spire en attendant qu'elle soit nulle : elle vaut
    **1,4 feuille**, et la surface témoin qui traverse trois feuilles n'en rendait que 2,6,
    soit un rapport de 1,8. Le test ne séparait presque rien.

    La raison est physique et elle rend la première version fausse par construction : **une
    spire EST un tour de spirale**, donc son rayon croît d'exactement un écart inter-feuilles
    sur 360°. Son indice DOIT donc avancer de +1 par tour. Exiger qu'il soit constant, c'est
    exiger que le rouleau ne soit pas enroulé.

    Ce qui distingue une surface d'une seule feuille d'une surface qui saute est donc son
    **avance d'indice sur un tour**.

    ⚠ Et la valeur attendue pour une feuille est **zéro**, pas +1 — seconde correction, elle
    aussi venue de la mesure. Le champ est bâti sur des spires qui spiralent toutes de la même
    façon, donc la spirale est **absorbée dans le champ** : ses surfaces d'iso-indice spiralent
    avec le rouleau. C'est exactement ce qu'un nombre d'enroulement doit faire. Mesuré : une
    spire réelle avance de **−0,005** par tour, une surface qui saute `n` feuilles avance de
    `n`.

    Rendue par tranche de hauteur puis médianée : chaque tranche porte un tour entier, donc
    chacune est une mesure indépendante de la même quantité.
    """
    assignes: dict[tuple[int, int], float] = {}
    for cellule, rayon in cible.items():
        table = sorted((autres[k][cellule], k) for k in autres if cellule in autres[k])
        v = _indice_interpole(rayon, table)
        if v is not None:
            assignes[cellule] = v
    if len(assignes) < 20:
        return dict(cellules=len(assignes))

    # L'avance par tour, une par tranche de hauteur. ⚠ Mesuree par une PENTE ajustee sur tous
    # les secteurs de la tranche et non par la difference des deux extremites : une extremite
    # manquante ou bruitee decalerait toute la tranche.
    avances = []
    par_tranche: dict[int, list[tuple[int, float]]] = {}
    for (tranche, secteur), v in assignes.items():
        par_tranche.setdefault(tranche, []).append((secteur, v))
    for points in par_tranche.values():
        if len(points) < SECTEURS // 2:
            continue
        secteurs = np.array([p[0] for p in points], dtype=float)
        valeurs = np.array([p[1] for p in points], dtype=float)
        pente = np.polyfit(secteurs, valeurs, 1)[0]
        avances.append(float(pente * SECTEURS))

    a = np.array(list(assignes.values()))
    return dict(cellules=len(a), median=float(np.median(a)),
                tranches=len(avances),
                avance_par_tour=float(np.median(avances)) if avances else None,
                avance_p10=float(np.percentile(avances, 10)) if avances else None,
                avance_p90=float(np.percentile(avances, 90)) if avances else None,
                etendue_90=float(np.percentile(a, 95) - np.percentile(a, 5)))


def _temoin_en_travers(rayons: dict[int, dict], depart: int, saut: int) -> dict:
    """
    @brief Une surface qui TRAVERSE `saut` feuilles, fabriquée depuis le référent lui-même.

    Fondu sur l'angle entre la spire `k` et la spire `k + saut` : lisse, plausible, et
    traversant `saut` feuilles par construction. ⚠ C'est ce qui en fait un témoin et non un
    espoir — on ne cherche pas une surface fautive, on en fabrique une dont on connaît la faute.
    """
    bas, haut = depart, depart + saut
    if bas not in rayons or haut not in rayons:
        return {}
    cible = {}
    for cellule in rayons[bas]:
        if cellule not in rayons[haut]:
            continue
        # poids = position angulaire du secteur, donc la surface glisse d'une feuille a
        # l'autre en faisant un tour : c'est exactement ce qu'un saut de spire produit.
        poids = (cellule[1] - 1) / max(1, SECTEURS - 1)
        cible[cellule] = (1 - poids) * rayons[bas][cellule] + poids * rayons[haut][cellule]
    # ⚠ Les DEUX spires qui servent a fabriquer le temoin sont retirees du champ qui le juge :
    # sinon le champ reconnaitrait ses propres bornes et le test serait a moitie truque.
    autres = {k: v for k, v in rayons.items() if k not in (bas, haut)}
    r = _juger(cible, autres)
    r.update(de=bas, vers=haut, saut=saut)
    return r


FACTEUR_SECTEUR_DOUTEUX = 3.0
"""Un secteur angulaire est écarté quand son taux de violation d'ordre dépasse ce multiple de
la médiane des secteurs. ⚠ Le multiple est posé **entre les deux profils mesurés** et non
réglé : sur `PHerc0139` le pire secteur est à ×1,40 de la moyenne (profil plat, rien à
écarter), sur `PHerc0172` à ×4,64 (défaut localisé). Tout seuil entre 2 et 4 donne le même
partage, ce qui est la propriété qu'on veut."""


def secteurs_douteux(rayons: dict[int, dict]) -> list[int]:
    """
    @brief Les secteurs angulaires où l'ordre des spires est violé bien plus qu'ailleurs.

    ⚠⚠⚠ CE FILTRE VIENT D'UNE IMAGE, PAS D'UNE MESURE. `77` §7 avait testé quatre causes
    candidates au fait que `PHerc0172` ne sépare pas, dont « la monotonie des rayons », écartée
    parce que le taux MOYEN de violation est le même sur les deux rouleaux (5,2 % contre
    5,6 %). La moyenne était la mauvaise statistique : ce qui diffère est la **concentration**.
    Dépliée en (angle, rayon), une tranche de `PHerc0172` montre un faisceau de spires
    extérieures qui se croisent entre 330° et 360° — visible en un coup d'œil, invisible à
    toute moyenne.

    ⭐ Le champ suppose que le rayon croît avec l'indice à angle fixe. C'est faux près de la
    **couture** de la spirale, là où une spire finit et où la suivante commence : à cet
    angle-là, `w_k` et `w_{k+1}` sont au même rayon **par définition**, puisque la spirale est
    continue. Un secteur de couture n'est donc pas un défaut de traçage, c'est un endroit où le
    modèle du champ ne s'applique pas.
    """
    violations: dict[int, list[float]] = {}
    for cellule in {c for v in rayons.values() for c in v}:
        presentes = sorted(k for k in rayons if cellule in rayons[k])
        if len(presentes) < 3:
            continue
        suite = [rayons[k][cellule] for k in presentes]
        inversions = sum(1 for i in range(len(suite) - 1) if suite[i + 1] <= suite[i])
        violations.setdefault(cellule[1], []).append(inversions / (len(suite) - 1))
    if not violations:
        return []
    taux = {s: float(np.mean(v)) for s, v in violations.items()}
    mediane = float(np.median(list(taux.values())))
    if mediane <= 0:
        return []
    # ⚠⚠⚠ ON RAPPORTE, ON N'EXCLUT PAS. J'avais d'abord etendu l'arc par contiguite et
    # exclu les 15 secteurs obtenus, ce qui restaurait la separation sur `PHerc0172`. Le
    # temoin negatif a mordu : ecarter AUTANT de secteurs SAINS la restaure aussi, parce que
    # retirer un cinquieme de la circonference fait tomber les tranches mal couvertes sous le
    # seuil de `_separation` et ne laisse que les bonnes. L'effet mesure etait celui du filtre
    # de couverture, pas celui de la couture.
    #
    # A six secteurs, en revanche, la distinction TIENT (`la_couture.py`). Ce fichier se
    # contente donc de NOMMER les secteurs suspects ; ce qu'ils coutent est mesure ailleurs,
    # avec son temoin a compte egal.
    return sorted(s for s, t in taux.items() if t > FACTEUR_SECTEUR_DOUTEUX * mediane)


def _avances_par_tranche(cible: dict, autres: dict[int, dict]) -> dict[int, float]:
    """
    @brief L'avance d'indice, tranche de hauteur par tranche de hauteur.
    """
    assignes = {}
    for cellule, rayon in cible.items():
        table = sorted((autres[k][cellule], k) for k in autres if cellule in autres[k])
        v = _indice_interpole(rayon, table)
        if v is not None:
            assignes[cellule] = v
    par: dict[int, list] = {}
    for (tranche, secteur), v in assignes.items():
        par.setdefault(tranche, []).append((secteur, v))
    out = {}
    for tranche, points in par.items():
        if len(points) < SECTEURS // 2:
            continue
        s = np.array([p[0] for p in points], dtype=float)
        w = np.array([p[1] for p in points], dtype=float)
        out[tranche] = float(np.polyfit(s, w, 1)[0] * SECTEURS)
    return out


def _separation(rayons: dict[int, dict], indices: list[int]) -> dict:
    """
    @brief À quelle taille de région les deux populations cessent-elles de se recouvrir ?

    Rend, pour plusieurs nombres de tranches agrégées, le 9ᵉ décile des vraies spires et le
    1ᵉʳ décile des sauts d'une feuille. La séparation est acquise quand le premier passe sous
    le second — et **elle peut ne jamais l'être**, ce qui est un résultat et non une panne.
    """
    vraies, sauts = [], []
    for k in indices[1:-1]:
        vraies.append(_avances_par_tranche(rayons[k],
                                           {j: v for j, v in rayons.items() if j != k}))
    for k in indices[:-1]:
        if k + 1 not in rayons:
            continue
        cible = {}
        for c in rayons[k]:
            if c in rayons[k + 1]:
                w = (c[1] - 1) / max(1, SECTEURS - 1)
                cible[c] = (1 - w) * rayons[k][c] + w * rayons[k + 1][c]
        sauts.append(_avances_par_tranche(
            cible, {j: v for j, v in rayons.items() if j not in (k, k + 1)}))

    def agreger(serie: list[dict], m: int) -> np.ndarray:
        out = []
        for d in serie:
            t = sorted(d)
            for i in range(0, len(t) - m + 1, m):
                out.append(float(np.median([d[x] for x in t[i:i + m]])))
        return np.array(out)

    paliers = []
    for m in (1, 2, 4, 8, 16):
        v, s = agreger(vraies, m), agreger(sauts, m)
        if len(v) < 5 or len(s) < 5:
            continue
        vp90, sp10 = float(np.percentile(v, 90)), float(np.percentile(s, 10))
        paliers.append(dict(tranches=m, n_vraies=len(v), n_sauts=len(s),
                            vraie_p90=vp90, saut_p10=sp10, separe=bool(vp90 < sp10)))
    acquises = [p["tranches"] for p in paliers if p["separe"]]
    return dict(paliers=paliers, separe=bool(acquises),
                tranches_necessaires=min(acquises) if acquises else None)


def mesurer(rouleau: str = "PHerc0139") -> dict:
    dossiers = _spires(rouleau)
    nuages = {k: v for k, v in ((k, charger(d)) for k, d in dossiers.items()) if v}
    if len(nuages) < 5:
        raise SystemExit(f"moins de cinq spires en cache pour {rouleau}")

    bords_z, bords_t, centres = _grille(nuages)
    rayons = {k: _rayons(n, bords_z, bords_t, centres) for k, n in nuages.items()}
    rayons = {k: v for k, v in rayons.items() if len(v) > 50}

    # ⚠ Les secteurs suspects sont NOMMES et pas exclus — voir `secteurs_douteux`. Les
    # exclure ici ferait de ce fichier le juge et la partie.
    ecartes = secteurs_douteux(rayons)
    indices = sorted(rayons)

    # ⚠⚠ VALIDATION A SPIRE EXCLUE. La spire jugee est retiree du champ qui la juge, sinon la
    # mesure dit seulement que le champ se souvient de ce qu'il a lu.
    a_exclue = []
    for k in indices:
        if k == indices[0] or k == indices[-1]:
            continue  # les extremites n'ont pas d'encadrement : le champ extrapolerait
        r = _juger(rayons[k], {j: v for j, v in rayons.items() if j != k})
        if r.get("cellules", 0) >= 20:
            r.update(spire=k, erreur=abs(r["median"] - k))
            a_exclue.append(r)

    # ⚠⚠ Les temoins sont fabriques a CHAQUE position, pas une fois au milieu. Un temoin
    # unique dit « le champ voit CE saut-la » ; une distribution dit si les deux populations
    # se SEPARENT, ce qui est la seule chose qu'un predicat doit faire.
    temoins = {}
    for saut in SAUTS_DU_TEMOIN:
        serie = []
        for k in indices:
            t = _temoin_en_travers(rayons, k, saut)
            if t and t.get("avance_par_tour") is not None:
                serie.append(t)
        if serie:
            a_ = np.array([t["avance_par_tour"] for t in serie])
            temoins[str(saut)] = dict(
                saut=saut, n=len(serie),
                median=float(np.median(a_)), p10=float(np.percentile(a_, 10)),
                p90=float(np.percentile(a_, 90)), minimum=float(a_.min()),
                positions=[dict(de=t["de"], vers=t["vers"],
                                avance=t["avance_par_tour"]) for t in serie])

    # ⭐⭐⭐ LA SEPARATION SE MESURE, ELLE NE SE SUPPOSE PAS -- et elle depend du rouleau.
    # `77` a d'abord conclu « les deux populations ne se recouvrent pas » sur `PHerc0139`.
    # Mesure sur `PHerc0172` : elles se recouvrent, a tout niveau d'agregation teste. Un
    # predicat qui marche ici et pas la doit DIRE lequel, sinon il ment sur le second rouleau
    # avec les mots du premier.
    #
    # ⚠ Et la separation se joue a l'echelle de la REGION, pas de la tranche : par tranche
    # isolee les deux populations se recouvrent meme sur `PHerc0139`. C'est la mesure de ce
    # que `42` disait deja qualitativement -- « le predicat doit designer des regions, pas des
    # points » -- et elle en donne la taille.
    separation = _separation(rayons, indices)

    # ⚠ Un diagnostic, pas une gate : de combien l'axe se deplace d'une tranche a la suivante,
    # en feuilles. C'est le plus gros ecart entre les deux rouleaux mesures (2,0 contre 3,5
    # feuilles en mediane, 13,6 contre 106,6 au pire) -- et pourtant affiner les tranches ne
    # restaure PAS la separation (`--balayer-tranches`). Garde parce qu'un futur lecteur refera
    # ce raisonnement, et doit trouver la piste ET son refus.
    ordonnes = [centres[i] for i in sorted(centres)]
    pas_axe = [float(np.hypot(b_[0] - a_[0], b_[1] - a_[1]))
               for a_, b_ in zip(ordonnes, ordonnes[1:])]
    feuille_vx = ECART_INTER_FEUILLES_VX.get(rouleau)
    derive = dict(
        tranches=len(ordonnes),
        median_vx=float(np.median(pas_axe)) if pas_axe else None,
        max_vx=float(max(pas_axe)) if pas_axe else None,
        median_feuilles=float(np.median(pas_axe) / feuille_vx)
        if pas_axe and feuille_vx else None,
        max_feuilles=float(max(pas_axe) / feuille_vx) if pas_axe and feuille_vx else None,
    )

    etendues = [x["etendue_90"] for x in a_exclue]
    erreurs = [x["erreur"] for x in a_exclue]
    avances = [x["avance_par_tour"] for x in a_exclue if x.get("avance_par_tour") is not None]
    return dict(
        rouleau=rouleau, spires=len(rayons), indices=[indices[0], indices[-1]],
        jugees_a_spire_exclue=len(a_exclue),
        erreur_mediane=float(np.median(erreurs)) if erreurs else None,
        erreur_p90=float(np.percentile(erreurs, 90)) if erreurs else None,
        etendue_90_mediane=float(np.median(etendues)) if etendues else None,
        etendue_90_p90=float(np.percentile(etendues, 90)) if etendues else None,
        avance_par_tour_mediane=float(np.median(avances)) if avances else None,
        avance_p10=float(np.percentile(avances, 10)) if avances else None,
        avance_p90=float(np.percentile(avances, 90)) if avances else None,
        secteurs_ecartes=ecartes,
        separation=separation,
        derive_de_l_axe=derive,
        temoins_en_travers=temoins,
        defauts_connus=DEFAUTS_CONNUS,
        par_spire=a_exclue,
    )


def balayer_tranches(rouleau: str, comptes=(24, 48, 96)) -> dict:
    """
    @brief La séparation reste-t-elle absente quand on affine les tranches de hauteur ?

    ⚠⚠ Existe parce que la **dérive de l'axe** est la piste la plus séduisante pour expliquer
    que `PHerc0172` ne sépare pas — son axe traverse jusqu'à 106 feuilles entre deux tranches
    consécutives, ce qui devrait rendre les rayons d'une tranche incomparables. Affiner les
    tranches est le remède évident, et **il ne marche pas** : c'est ce que ce balayage mesure.

    ⚠ Séparé du chemin principal parce qu'il refait tout le champ à chaque compte de tranches,
    donc il coûte trois fois une mesure ordinaire. La batterie du dépôt ne l'appelle pas ; il
    est appelé une fois, son résultat est écrit, et la prose cite ce fichier.
    """
    global TRANCHES_Z
    import le_sens_des_indices as sens  # noqa: PLC0415

    dossiers = _spires(rouleau)
    nuages = {k: v for k, v in ((k, charger(d)) for k, d in dossiers.items()) if v}
    ancien = TRANCHES_Z
    paliers = []
    try:
        for compte in comptes:
            TRANCHES_Z = compte
            sens.TRANCHES_Z = compte
            bords_z, bords_t, centres = _grille(nuages)
            rayons = {k: _rayons(n, bords_z, bords_t, centres) for k, n in nuages.items()}
            rayons = {k: v for k, v in rayons.items() if len(v) > 50}
            sep = _separation(rayons, sorted(rayons))
            un = next((p for p in sep["paliers"] if p["tranches"] == 1), None)
            paliers.append(dict(tranches_z=compte, separe=sep["separe"],
                                tranches_necessaires=sep["tranches_necessaires"],
                                vraie_p90=un["vraie_p90"] if un else None,
                                saut_p10=un["saut_p10"] if un else None))
    finally:
        TRANCHES_Z = ancien
        sens.TRANCHES_Z = ancien
    return dict(rouleau=rouleau, paliers=paliers,
                affiner_resout=any(p["separe"] for p in paliers))


def _verifier(r: dict) -> int:
    echecs = 0
    comptees = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, comptees
        comptees += 1
        print(f"  {'ok  ' if ok else 'FAIL'}  {nom}" + (f"   [{detail}]" if detail else ""))
        if not ok:
            echecs += 1

    t = r["temoins_en_travers"]

    print("le champ interpole — une spire retirée est replacée là où elle est")
    v("assez de spires jugées à spire exclue",
      r["jugees_a_spire_exclue"] >= 10, f"{r['jugees_a_spire_exclue']} spires")
    v("l'indice assigné retombe sur le bon, à moins d'une demi-feuille",
      r["erreur_mediane"] is not None and r["erreur_mediane"] < 0.5,
      f"erreur médiane {r['erreur_mediane']:.3f} feuille")
    # ⚠⚠ ET IL FAUT QU'ELLE SOIT NON NULLE. Une erreur exactement nulle est la signature d'un
    # champ qui a LU la spire qu'il juge au lieu de l'interpoler -- mesure : 0,0000 sans
    # exclusion contre 0,0876 avec. Sans ce controle, le contrôle precedent passe dans les
    # deux cas et l'exclusion cesse d'etre verifiee par quoi que ce soit.
    v("... et elle n'est pas nulle, donc la spire a bien été interpolée et non lue",
      r["erreur_mediane"] is not None and r["erreur_mediane"] > 1e-6,
      f"{r['erreur_mediane']:.4f} (une exclusion manquante rendrait exactement 0)")

    print("une surface d'UNE feuille n'avance pas — le champ a absorbé la spirale")
    v("l'avance par tour d'une vraie spire est nulle",
      r["avance_par_tour_mediane"] is not None
      and abs(r["avance_par_tour_mediane"]) < 0.15,
      f"{r['avance_par_tour_mediane']:+.3f} feuille par tour "
      f"[p10 {r['avance_p10']:+.3f}, p90 {r['avance_p90']:+.3f}]")

    print("et l'avance COMPTE les feuilles franchies — la rampe, pas un seul témoin")
    for saut in ("1", "2", "3"):
        if saut in t:
            v(f"un saut fabriqué de {saut} feuille(s) avance d'environ {saut}",
              abs(t[saut]["median"] - int(saut)) < 0.35,
              f"{t[saut]['median']:.3f} sur {t[saut]['n']} positions")

    # ⚠⚠⚠ LE CONTROLE QUI FAIT DE CA UN PREDICAT : deux populations qui ne se recouvrent pas.
    # Sans lui, « la mediane d'un saut vaut 1 » serait compatible avec des distributions si
    # larges qu'aucune surface individuelle ne pourrait etre classee.
    # ⚠⚠ Asserte dans les DEUX SENS : le rouleau doit se comporter comme il a ete mesure. Si
    # `PHerc0139` cessait de separer, ou si `PHerc0172` se mettait a separer, ce controle
    # tomberait -- et le second serait une excellente nouvelle. Un controle ecrit seulement
    # dans le sens « ca separe » aurait force a ne pas enregistrer le second rouleau, donc a
    # ne jamais voir qu'il ne separe pas.
    if "1" in t:
        separe = r["avance_p90"] < t["1"]["p10"]
        attendu_sep = SEPARATION_ATTENDUE.get(r["rouleau"], True) is not None
        v(("les deux populations ne se recouvrent PAS, à l'échelle de la spire entière"
           if attendu_sep else
           "les deux populations SE RECOUVRENT sur ce rouleau — mesuré, et dit"),
          separe == attendu_sep,
          f"vraie spire jusqu'à {r['avance_p90']:+.3f}, saut d'une feuille à partir de "
          f"{t['1']['p10']:.3f}")

    # ⚠⚠ ET LE PREDICAT DIT LUI-MEME OU IL S'APPLIQUE. Une tranche isolee ne suffit jamais,
    # sur aucun des deux rouleaux ; la taille de region necessaire, elle, depend du rouleau et
    # peut ne pas exister. Ces trois controles echouent si un rouleau change de comportement,
    # ce qui est exactement ce qu'on veut savoir.
    print("la couture, trouvée EN REGARDANT après quatre hypothèses mesurées et rejetées")
    ec = r["secteurs_ecartes"]
    v("le rouleau au profil plat n'a rien à écarter, celui à défaut localisé en a",
      (r["rouleau"] == "PHerc0139" and not ec) or (r["rouleau"] != "PHerc0139" and ec)
      if r["rouleau"] in SEPARATION_ATTENDUE else True,
      f"{len(ec)} secteur(s) écarté(s)" + (f" : {ec[0]}–{ec[-1]}" if ec else ""))
    print("le prédicat déclare son échelle — une tranche isolée ne suffit jamais")
    sep = r["separation"]
    attendu = SEPARATION_ATTENDUE.get(r["rouleau"], "?")
    un = next((p for p in sep["paliers"] if p["tranches"] == 1), None)
    v("une tranche de hauteur isolée ne sépare pas",
      un is not None and not un["separe"],
      f"vraie p90 {un['vraie_p90']:+.3f} contre saut p10 {un['saut_p10']:+.3f}"
      if un else "palier absent")
    v(f"le rouleau se comporte comme mesuré ({attendu} tranches)",
      attendu == "?" or sep["tranches_necessaires"] == attendu,
      f"il faut {sep['tranches_necessaires']} tranche(s), attendu {attendu}")
    v("... et le fichier le RAPPORTE au lieu de le supposer",
      isinstance(sep.get("separe"), bool) and len(sep["paliers"]) >= 3,
      f"séparé={sep['separe']} sur {len(sep['paliers'])} paliers")

    # ⚠⚠⚠ LA VALIDATION CROISEE, et c'est le controle le plus fort du fichier. Deux positions
    # rendent un « saut d'une feuille » qui n'avance pas -- et ce sont EXACTEMENT les deux
    # paires que `76` a signalees par une methode entierement differente (comparaison radiale
    # appariee, puis distance au plus proche voisin). Un defaut du referent, vu deux fois,
    # par deux instruments qui ne partagent rien.
    print("la validation croisée — les seuls ratés sont les défauts que `76` avait trouvés")
    if "1" in t and r["separation"]["separe"]:
        rates = sorted(p["de"] for p in t["1"]["positions"]
                       if p["avance"] < r["avance_p90"] + 0.3)
        v("les positions qui n'avancent pas sont exactement les défauts connus",
          rates == sorted(r["defauts_connus"]),
          f"trouvé {rates}, attendu {sorted(r['defauts_connus'])}")

    print()
    if echecs:
        print(f"  ECHEC ({echecs} failures)")
    else:
        print(f"  ALL PASS (0 failures, {comptees} checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--rouleau", default="PHerc0139")
    p.add_argument("--balayer-tranches", type=Path,
                   help="mesurer si affiner les tranches restaure la séparation, et l'écrire")
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    args = p.parse_args()

    if args.balayer_tranches:
        b = balayer_tranches(args.rouleau)
        args.balayer_tranches.parent.mkdir(parents=True, exist_ok=True)
        args.balayer_tranches.write_text(json.dumps(b, indent=2, ensure_ascii=False),
                                         encoding="utf-8")
        for pal in b["paliers"]:
            print(f"  TRANCHES_Z={pal['tranches_z']:3d} : séparé={pal['separe']} · "
                  f"vraie p90 {pal['vraie_p90']:+.3f} · saut p10 {pal['saut_p10']:+.3f}")
        print(f"\naffiner résout : {b['affiner_resout']}")
        print(f"écrit : {args.balayer_tranches}")
        return 0

    r = mesurer(args.rouleau)

    if not args.verifier or args.json:
        print(f"{r['rouleau']} — champ bâti sur {r['spires']} spires "
              f"(w{r['indices'][0]:03d}–w{r['indices'][1]:03d})\n")
        print(f"  validation à spire exclue : {r['jugees_a_spire_exclue']} spires")
        print(f"    erreur d'indice   : médiane {r['erreur_mediane']:.3f} · "
              f"p90 {r['erreur_p90']:.3f} feuille")
        print(f"    étendue p5–p95    : médiane {r['etendue_90_mediane']:.3f} · "
              f"p90 {r['etendue_90_p90']:.3f} feuille")
        print(f"\n  avance par tour d'une VRAIE spire : {r['avance_par_tour_mediane']:+.3f} "
              f"[p10 {r['avance_p10']:+.3f}, p90 {r['avance_p90']:+.3f}]")
        print("\n  témoins fabriqués, à chaque position :")
        for saut, t in sorted(r["temoins_en_travers"].items()):
            print(f"    saut de {saut} feuille(s) : {t['median']:6.3f} "
                  f"[p10 {t['p10']:.3f}, p90 {t['p90']:.3f}]  sur {t['n']} positions")

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nécrit : {args.json}")
    if args.verifier:
        print()
        return 1 if _verifier(r) else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
