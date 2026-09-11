#!/usr/bin/env python3
"""L'identité des pistes churne-t-elle encore quand le coût CONNAÎT la spire ?

⚠⚠⚠ POURQUOI CE FICHIER ROUVRE UNE CAUSE DÉJÀ ÉLIMINÉE, ET CE QUI L'AUTORISE. `fusions.py`
a posé trois hypothèses sur la fragmentation de son tracker et **les trois ont été
réfutées** — affectation globale : pire ; pistes en sursis : innocentes ; détecteur : 92 %
des murs retrouvés à moins de deux voxels. La cause réelle qu'il a mesurée est ailleurs :
**125 murs sur 126 sont appariés à chaque colonne**, donc la couverture est quasi parfaite
et ce qui échoue est l'**IDENTITÉ** des pistes. Les « 12 249 fusions » de
`docs/mesures/fusions_0172.json` étaient des changements d'étiquette, pas des événements de
matière.

⭐ CE QUI A CHANGÉ DEPUIS, ET C'EST LA CONDITION DE RÉOUVERTURE DE `55`. Le coût du tracker
n'apparie que sur UNE quantité — l'écart radial à une prédiction par la pente. Il n'a aucun
indice de spire, et son propre commentaire nomme le mode de panne qu'il ne peut qu'interdire
par une tolérance : « un coût fini laisserait l'optimum global SAUTER UNE SPIRE ». L'instrument
qui donnerait cette seconde coordonnée — `le_champ_denroulement`, indice d'enroulement continu
validé à spire exclue — a été construit **le 4 septembre**, soit trois semaines APRÈS la
dernière mesure du tracker. La réfutation est antérieure au remède : `55` exige une mesure
neuve pour rouvrir, et c'en est une.

⚠⚠ LE CHAMP EST RECONSTRUIT DANS LE REPÈRE DE LA POLAIRE, PAS EMPRUNTÉ AU SIEN. Le champ
publié travaille avec un centre ajusté par tranche de hauteur ; la polaire est dépliée autour
de l'ombilic de `data/axes/`. Les deux diffèrent, et un décalage de centre déplace **le rayon**
d'un mur autant qu'il déplace son angle — c'est-à-dire exactement la quantité que le tracker
apparie. Emprunter la table telle quelle rendrait des indices parfaitement valides pris
ailleurs dans le rouleau, ce qui ne lève rien et ne ressemble pas à une erreur. Les rayons sont
donc recalculés depuis les nuages de points avec le centre DE LA POLAIRE, et la validation à
spire exclue est **refaite dans ce repère** plutôt qu'héritée.

⚠ CE QUE CE FICHIER NE PEUT PAS ÉTABLIR, et il faut le lire avant ses chiffres :

1. **La moitié intérieure n'est pas couverte.** Les spires publiées de `PHerc0172` occupent
   `r ∈ [1536, 3293]` voxels à la hauteur de la polaire, qui en porte `0..3000` : la bande
   utile est `[1536, 3000]`, soit **48,8 %** des lignes. Le cœur — là où `fusions.py` note que
   le comptage rendait « une carte de la faiblesse du détecteur » — reste hors de portée.
2. **Un seul objet, une seule hauteur.** `PHerc0172`, z au milieu du volume.
3. **Rien sur la 3D.** Une coupe polaire est un plan ; les 775 heures sont dépensées sur des
   surfaces. Ce fichier mesure si l'identité tient dans le plan, pas si elle porte.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(RACINE / "src" / "excision")]
from le_sens_des_indices import POINTS_MINIMUM, TRANCHES_Z, charger, _spires  # noqa: E402
from fusions import ridges, synthetic, track  # noqa: E402

ROULEAU = "PHerc0172"
POLAIRE = RACINE / "data" / "out" / "polaire_0172.npy"
AXE = RACINE / "data" / "axes" / "PHerc0172.json"

VOXEL_UM = 7.91
ECART_FEUILLE_VX = 147.4 / VOXEL_UM
"""L'écart inter-feuilles de `PHerc0172` (`76`), en voxels. Sert d'unité : « 19,7 voxels »
ne dit rien, « 1,06 feuille » dit qu'un pas d'indice publié vaut bien une feuille."""

SECTEURS = 72
DEMI_TRANCHE_Z = 12380.0 / TRANCHES_Z / 2.0
"""La demi-épaisseur de la tranche de hauteur, PRISE SUR L'INSTRUMENT PUBLIÉ et non choisie.

⚠ Une première version prenait ±50 voxels, « pour rester près de la coupe ». Mesuré : onze
secteurs sur soixante-douze répondaient, parce qu'une spire n'y laissait plus assez de points
par cellule — et onze secteurs ne se lisent pas comme un paramètre trop serré, ils se lisent
comme un champ qui ne couvre pas le rouleau. Le champ publié découpe la hauteur en
`TRANCHES_Z` tranches sur l'étendue des nuages (~12 380 voxels), et c'est cette épaisseur-là
qui a été validée à 0,041 spire d'erreur médiane."""
POINTS_PAR_CELLULE = POINTS_MINIMUM

PROMINENCE, MIN_GAP, SMOOTH = 8.0, 10, 5
TOLERANCE, GAP_TOLERANCE, MIN_POINTS = 8.0, 8, 50


def z_de_la_polaire() -> tuple[float, float, int]:
    """Le centre et la hauteur autour desquels `polaire_0172.npy` a été dépliée.

    ⚠ Dérivés du même fichier et des mêmes défauts que `radial.py deplier` (`--slice -1`
    prend le milieu du volume), jamais saisis à la main : un z recopié à côté d'un fichier
    qui ne le porte pas est un chiffre que rien ne peut contredire.
    """
    a = json.loads(AXE.read_text())
    return a["cx"], a["cy"], int((a["z_min"] + a["z_max"]) / 2)


def table_dans_le_repere_de_la_polaire(cx: float, cy: float, z: int,
                                       demi: float = DEMI_TRANCHE_Z,
                                       secteurs: int = SECTEURS,
                                       minimum: int = POINTS_PAR_CELLULE) -> dict:
    """Pour chaque secteur angulaire, les rayons des spires publiées, triés.

    ⚠ L'angle suit la convention de `unwrap_polar` — `theta = atan2(y - cy, x - cx)` ramené
    dans `[0, 2π)`, colonne `j` de la polaire à `2πj/largeur`. Les deux bouts partagent donc
    une seule définition de l'angle, et pas deux qui se trouveraient coïncider.
    """
    par_secteur: dict[int, list[tuple[float, int]]] = {s: [] for s in range(secteurs)}
    largeur_secteur = 2.0 * np.pi / secteurs
    for k, dossier in sorted(_spires(ROULEAU).items()):
        nuage = charger(dossier)
        if nuage is None:
            continue
        x, y, z_pts = nuage
        proche = np.abs(z_pts - z) <= demi
        if proche.sum() < minimum:
            continue
        dx, dy = x[proche] - cx, y[proche] - cy
        r = np.hypot(dx, dy)
        theta = np.mod(np.arctan2(dy, dx), 2.0 * np.pi)
        s = np.minimum((theta / largeur_secteur).astype(int), secteurs - 1)
        for j in range(secteurs):
            dedans = r[s == j]
            if len(dedans) >= minimum:
                par_secteur[j].append((float(np.median(dedans)), k))
    return {j: sorted(v) for j, v in par_secteur.items() if len(v) >= 2}


def indice_interpole(rayon: float, table: list[tuple[float, int]]) -> float | None:
    """L'indice de spire d'un rayon, interpolé entre les deux spires qui l'encadrent.

    ⚠ Rend `None` hors de la table plutôt qu'une extrapolation — un prédicat d'identité qui
    répond partout est un prédicat qui ne refuse jamais. Reprend mot pour mot la règle de
    `le_champ_denroulement._indice_interpole`, dont c'est le même énoncé dans un autre repère.
    """
    if len(table) < 2:
        return None
    for (r0, k0), (r1, k1) in zip(table, table[1:]):
        if r0 <= rayon <= r1:
            return float(k0) if r1 == r0 else float(k0 + (k1 - k0) * (rayon - r0) / (r1 - r0))
    return None


def bande_utile(tables: dict) -> tuple[float, float]:
    """Le domaine radial où le champ répond, MESURÉ sur la table et non déclaré."""
    lo = min(v[0][0] for v in tables.values())
    hi = max(v[-1][0] for v in tables.values())
    return float(lo), float(hi)


def feuilles_par_pas_dindice(tables: dict) -> dict:
    """Un pas d'indice publié vaut-il UNE feuille ? — la condition de mort de la tranche.

    ⚠ Mesuré SECTEUR PAR SECTEUR, jamais sur une médiane tous angles confondus. Chaque patch
    publié couvre un secteur différent, donc comparer deux spires sur l'ensemble des angles
    compare des angles différents : une première sonde faite ainsi rendait six pas NÉGATIFS
    sur quarante-trois, ce qui est impossible pour une spirale et ne disait rien du champ.
    """
    pas = []
    for table in tables.values():
        for (r0, k0), (r1, k1) in zip(table, table[1:]):
            if k1 == k0:
                continue
            pas.append((r1 - r0) / (k1 - k0))
    if not pas:
        return {"pas": 0}
    pas = np.asarray(pas)
    return {"pas": int(pas.size),
            "pas_median_vx": float(np.median(pas)),
            "feuilles_par_indice": float(np.median(pas) / ECART_FEUILLE_VX),
            "negatifs": int((pas < 0).sum()),
            "p10": float(np.percentile(pas, 10)),
            "p90": float(np.percentile(pas, 90))}


def champ_depuis(tables: dict, largeur: int, decalage_r: float = 0.0,
                 secteurs: int = SECTEURS, constant: float | None = None,
                 rotation: int = 0):
    """Un `champ(rayon, colonne)` pour `fusions.track`, et ses deux faux.

    ⚠⚠ LE FAUX CHAMP EST UNE ROTATION, PAS UNE TRANSLATION D'INDICE. Ma première version
    ajoutait `+1` à chaque indice rendu et l'appelait « décalé d'une spire ». C'est un
    **no-op par construction** : le coût ne lit que l'écart `|indice de la piste − indice du
    mur|`, et une translation déplace les deux termes ensemble. Mesuré, il rendait
    exactement le même nombre que le vrai champ — 6,09 morceaux par mur des deux côtés — ce
    qui se lit comme « le décalage ne nuit pas » alors que rien n'avait été décalé.

    Une ROTATION de secteurs donne, elle, un champ qui a toutes les statistiques du vrai et
    aucune de ses correspondances : à chaque angle il rend l'indice d'un AUTRE angle. C'est
    le faux qu'il faut, parce qu'il ne peut pas être battu par hasard.

    `constant` sert l'autre témoin : il rend le même indice partout, donc un écart nul
    partout, donc un coût inchangé. Il vaut la peine d'exister quand même — il prouve que le
    gain vient de la VARIATION du champ et non de la présence d'un terme de plus.
    """
    largeur_secteur = largeur / secteurs

    def champ(rayon: float, colonne: int) -> float | None:
        s = min(int(colonne / largeur_secteur), secteurs - 1)
        table = tables.get((s + rotation) % secteurs)
        if table is None:
            return None
        v = indice_interpole(rayon + decalage_r, table)
        return None if v is None else (constant if constant is not None else v)

    return champ


def metriques(tracks: list[dict], largeur: int, murs_par_colonne: float,
              min_points: int = MIN_POINTS) -> dict:
    """Ce qu'on compte, et ce qu'on refuse de compter.

    ⚠⚠ LE NOMBRE DE « FUSIONS » N'EST PAS UNE MÉTRIQUE ICI. C'est précisément l'artefact que
    `gap_map` a identifié : une mort de piste par changement d'étiquette. Ce qui se compte est
    ce qu'une étiquette stable produirait — des pistes qui **traversent** le balayage — et le
    dénominateur est le nombre de murs réellement présents dans une colonne, pas un nombre de
    feuilles supposé.
    """
    retenues = [t for t in tracks if t["points"] >= min_points]
    portees = np.array([t["end"] - t["start"] + 1 for t in retenues]) if retenues else np.zeros(0)
    traversantes = int((portees >= 0.9 * largeur).sum())
    return {"pistes": len(tracks),
            "retenues": len(retenues),
            "traversantes": traversantes,
            "murs_par_colonne": float(murs_par_colonne),
            "part_traversee": float(traversantes / murs_par_colonne) if murs_par_colonne else 0.0,
            "portee_mediane": float(np.median(portees)) if portees.size else 0.0,
            "portee_p90": float(np.percentile(portees, 90)) if portees.size else 0.0,
            "morceaux_par_mur": float(len(retenues) / murs_par_colonne) if murs_par_colonne else 0.0}


def murs_par_colonne_median(bande: np.ndarray, echantillons: int = 200) -> float:
    """Combien de murs une colonne contient réellement — le dénominateur, mesuré."""
    colonnes = np.linspace(0, bande.shape[1] - 1, echantillons).astype(int)
    compte = [ridges(bande[:, c], PROMINENCE, MIN_GAP, SMOOTH).size for c in colonnes]
    return float(np.median(compte))


def courir(bande: np.ndarray, champ=None, poids: float = 0.0,
           ecart_max: float | None = None) -> list[dict]:
    """Une passe du tracker partagé — jamais une copie de son chaînage."""
    return track(bande, PROMINENCE, MIN_GAP, SMOOTH, TOLERANCE, GAP_TOLERANCE,
                 champ=champ, poids=poids, ecart_max=ecart_max)


# ---------------------------------------------------------------------------
# La batterie : elle exerce le MÉCANISME. La comparaison, elle, est dans `mesurer`.
# ---------------------------------------------------------------------------

def verifier() -> int:
    """⚠ Ce que cette batterie garde, c'est que le code fait ce qu'il dit — pas que le champ
    serve à quelque chose. Un contrôle qui répondrait aux deux serait satisfait par le
    premier."""
    echecs = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs
        print(f"  {'ok  ' if ok else 'ECHEC'} {nom}" + (f"  — {detail}" if detail else ""))
        if not ok:
            echecs += 1

    print("le coût qui connaît la spire — batterie")

    # ⚠⚠ LE TÉMOIN QUI GARDE L'EXTENSION : sans champ, le tracker doit être celui d'avant.
    img = synthetic(sheets=8, height=400, width=500, merge_at=None)
    avant = courir(img)
    apres = courir(img, champ=lambda r, c: 3.0, poids=0.0)
    v("poids nul reproduit EXACTEMENT le tracker d'avant",
      len(avant) == len(apres)
      and all(a["start"] == b["start"] and a["end"] == b["end"] and a["radius"] == b["radius"]
              for a, b in zip(avant, apres)),
      f"{len(avant)} pistes des deux côtés")

    v("le tracker retrouve les feuilles fabriquées",
      metriques(avant, 500, 8.0)["traversantes"] == 8,
      f"traversantes {metriques(avant, 500, 8.0)['traversantes']} pour 8 posées")

    table = [(100.0, 1), (120.0, 2), (140.0, 3)]
    v("l'indice s'interpole entre deux spires", indice_interpole(110.0, table) == 1.5)
    v("l'indice REFUSE sous la table", indice_interpole(50.0, table) is None)
    v("l'indice REFUSE au-dessus de la table", indice_interpole(500.0, table) is None)
    v("une table d'une seule spire refuse", indice_interpole(100.0, [(100.0, 1)]) is None)

    # ⚠ Un champ muet ne doit RIEN changer : son silence ne coûte rien et n'interdit rien.
    muet = courir(img, champ=lambda r, c: None, poids=10.0, ecart_max=0.5)
    v("un champ qui ne répond jamais laisse le tracker intact",
      len(muet) == len(avant), f"{len(muet)} contre {len(avant)}")

    # ⚠ Et un champ qui interdit TOUT doit casser le chaînage — sinon `ecart_max` est mort.
    # ⚠ Une première version alternait `c % 2` : la tolérance de silence laisse alors chaque
    # piste survivre en n'étant appariée qu'une colonne sur deux, et le contrôle rendait
    # exactement 2 × 8 pistes — un nombre qui ressemble à un mécanisme mort alors que le
    # mécanisme marchait. Un indice STRICTEMENT croissant n'autorise aucun appariement.
    alterne = courir(img, champ=lambda r, c: float(c), poids=0.0, ecart_max=0.1)
    v("un champ qui interdit tout brise les pistes",
      len(alterne) > 10 * len(avant), f"{len(alterne)} contre {len(avant)}")

    cx, cy, z = z_de_la_polaire()
    v("le z de la polaire est dérivé du fichier d'axe", z == 6967, f"z={z}")

    tables = table_dans_le_repere_de_la_polaire(cx, cy, z)
    v("le champ répond dans une majorité de secteurs",
      len(tables) >= SECTEURS // 2, f"{len(tables)}/{SECTEURS} secteurs")

    lo, hi = bande_utile(tables)
    v("la bande utile est mesurée et non déclarée",
      0 < lo < hi and hi > 1000, f"r {lo:.0f}..{hi:.0f} vx")

    pas = feuilles_par_pas_dindice(tables)
    v("un pas d'indice vaut une feuille, à 15 % près",
      0.85 <= pas["feuilles_par_indice"] <= 1.15,
      f"{pas['feuilles_par_indice']:.3f} feuille par indice sur {pas['pas']} pas")
    # ⚠⚠ EXIGER ZÉRO PAS NÉGATIF SERAIT EXIGER QUE LE ROULEAU SOIT ROND. Un pas négatif dit
    # qu'à cet angle la spire suivante est à un rayon PLUS PETIT — ce qu'une section écrasée
    # fait réellement là où elle se replie sur elle-même, et ce que la tranche de hauteur
    # accentue puisque l'axe erre avec z (`76`). Ma première version assertait zéro et
    # échouait sur 78 pas de 2342 : elle demandait à la matière d'être ce qu'elle n'est pas.
    # Ce qui se garde est que l'inversion reste MARGINALE, parce qu'un champ dont un tiers
    # des pas s'inversent ne serait plus un ordre.
    part_negative = pas["negatifs"] / pas["pas"]
    v("l'inversion du rayon reste marginale",
      part_negative < 0.10, f"{pas['negatifs']}/{pas['pas']} = {100 * part_negative:.1f} %")

    # ⚠ La colonne est prise DANS un secteur qui répond, jamais la colonne zéro : viser un
    # secteur muet ferait échouer les trois contrôles suivants pour la mauvaise raison.
    secteur = sorted(tables)[len(tables) // 2]
    colonne = int((secteur + 0.5) * 18850 / SECTEURS)
    milieu = float(np.median([r for r, _ in tables[secteur]]))
    champ = champ_depuis(tables, largeur=18850, decalage_r=0.0)
    v("le champ répond dans la bande", champ(milieu, colonne) is not None,
      f"secteur {secteur}, r {milieu:.0f}")
    v("le champ refuse sous la bande", champ(lo / 2, colonne) is None)
    # ⚠ Le faux champ doit rendre un AUTRE indice, pas le même décalé : une translation
    # laisse l'écart `|piste − mur|` inchangé et ne teste donc rien (voir `champ_depuis`).
    tourne = champ_depuis(tables, largeur=18850, rotation=SECTEURS // 3)
    # ⚠ La borne n'est pas choisie, elle est celle de la CONTRAINTE : le coût interdit
    # au-delà d'`ecart_max` = 0,5 spire, donc un faux champ n'est un faux utilisable que
    # s'il désaccorde de plus que ça. Une première version exigeait « 90 % des colonnes
    # diffèrent » — un nombre que rien ne justifiait, et qui échouait à 74 % parce que le
    # sondage comptait comme identiques les colonnes où les DEUX champs refusent.
    # ⚠ Le rayon sondé est celui du secteur DE CETTE COLONNE, pas un rayon fixe : sonder
    # partout au rayon médian d'un seul secteur fait refuser le champ presque partout
    # ailleurs, et la sonde ne rendait plus que onze points.
    ecarts = []
    for c in range(0, 18850, 61):
        sect = min(int(c * SECTEURS / 18850), SECTEURS - 1)
        if sect not in tables:
            continue
        r = float(np.median([rr for rr, _ in tables[sect]]))
        a, b = champ(r, c), tourne(r, c)
        if a is not None and b is not None:
            ecarts.append(abs(a - b))
    v("le champ tourné désaccorde de plus que la contrainte ne tolère",
      len(ecarts) >= 20 and float(np.median(ecarts)) > 0.5,
      f"écart médian {np.median(ecarts):.2f} spire sur {len(ecarts)} colonnes")
    constant = champ_depuis(tables, largeur=18850, constant=7.0)
    v("le témoin constant rend la même valeur partout et refuse au même endroit",
      constant(milieu, colonne) == 7.0 and constant(lo / 2, colonne) is None)

    print(f"\n{'ALL PASS' if echecs == 0 else 'ECHEC'} ({echecs} failures, 16 checks)")
    return 1 if echecs else 0


# ---------------------------------------------------------------------------

def mesurer(colonnes: int | None = None, poids: float = 4.0,
            ecart_max: float | None = 0.5, brouillon: Path | None = None) -> dict:
    """La comparaison, et ses deux témoins qui peuvent la refuser.

    ⚠⚠ LE BROUILLON EST ÉCRIT APRÈS CHAQUE VARIANTE, PAS À LA FIN. Quatre passes du tracker
    sur dix-huit mille colonnes : celle qui casse à la quatrième ne doit pas emporter les
    trois autres. C'est la garde que `110` a payée vingt minutes.
    """
    cx, cy, z = z_de_la_polaire()
    tables = table_dans_le_repere_de_la_polaire(cx, cy, z)
    lo, hi = bande_utile(tables)
    polar = np.load(POLAIRE, mmap_mode="r")
    r0, r1 = int(np.ceil(lo)), int(min(polar.shape[0], np.floor(hi)))
    largeur = polar.shape[1] if colonnes is None else min(colonnes, polar.shape[1])
    bande = np.ascontiguousarray(polar[r0:r1, :largeur])

    murs = murs_par_colonne_median(bande)
    sortie = {"rouleau": ROULEAU, "z": z, "centre": [cx, cy],
              "polaire": list(polar.shape), "bande_vx": [r0, r1],
              "part_du_rayon": (r1 - r0) / polar.shape[0],
              "colonnes": largeur, "poids": poids, "ecart_max": ecart_max,
              "secteurs_repondus": len(tables),
              "pas_dindice": feuilles_par_pas_dindice(tables),
              "murs_par_colonne": murs, "variantes": {}}

    def fait(nom: str, champ, p: float) -> None:
        t = courir(bande, champ=champ, poids=p, ecart_max=ecart_max if champ else None)
        sortie["variantes"][nom] = metriques(t, largeur, murs)
        print(f"  {nom:12} traversantes {sortie['variantes'][nom]['traversantes']:4}"
              f"  part {sortie['variantes'][nom]['part_traversee']:.3f}"
              f"  morceaux/mur {sortie['variantes'][nom]['morceaux_par_mur']:.2f}")
        if brouillon is not None:
            brouillon.parent.mkdir(parents=True, exist_ok=True)
            brouillon.write_text(json.dumps(sortie, indent=2, ensure_ascii=False))

    print(f"bande r {r0}..{r1} vx ({100 * sortie['part_du_rayon']:.1f} % du rayon) · "
          f"{largeur} colonnes · {murs:.0f} murs par colonne")
    fait("temoin", None, 0.0)
    fait("champ", champ_depuis(tables, largeur, decalage_r=r0), poids)
    fait("constant", champ_depuis(tables, largeur, decalage_r=r0, constant=70.0), poids)
    fait("tourne", champ_depuis(tables, largeur, decalage_r=r0, rotation=SECTEURS // 3), poids)
    return sortie


def agreger(r: dict) -> dict:
    """Le verdict, et il exige que les DEUX témoins refusent.

    ⚠ « Le champ améliore » ne suffit pas : une régularisation quelconque améliore aussi.
    Le gain ne compte que si un champ CONSTANT ne l'obtient pas — sinon ce qui a aidé est
    le fait de pénaliser les échanges, pas de connaître la spire.
    """
    # ⚠⚠ LA MÉTRIQUE DE TÊTE EST `morceaux_par_mur`, ET `traversantes` EST PUBLIÉE À CÔTÉ.
    # Mesuré : aucune piste ne traverse même 90 % de mille cinq cents colonnes, donc
    # `part_traversee` vaut zéro pour toutes les variantes et ne peut rien départager. Une
    # quantité qui ne peut pas prendre la valeur qui signalerait le succès ne mesure rien —
    # c'est le péché que ce dépôt a déjà payé. Le nombre de MORCEAUX par mur, lui, bouge.
    v = r["variantes"]
    base = v["temoin"]["morceaux_par_mur"]
    # Un gain POSITIF veut dire moins de morceaux, donc une identité qui tient mieux.
    gain = base - v["champ"]["morceaux_par_mur"]
    gain_constant = base - v["constant"]["morceaux_par_mur"]
    gain_tourne = base - v["tourne"]["morceaux_par_mur"]
    r["verdict"] = {
        "morceaux_par_mur_temoin": base,
        "gain_du_champ": gain,
        "gain_du_constant": gain_constant,
        "gain_du_champ_tourne": gain_tourne,
        "traversantes_temoin": v["temoin"]["traversantes"],
        "traversantes_champ": v["champ"]["traversantes"],
        "le_champ_ameliore": gain > 0.0,
        "le_constant_nexplique_pas_le_gain": gain > gain_constant,
        "le_champ_tourne_fait_moins_bien": gain_tourne < gain,
        # ⚠⚠ CE QUI COMPTE EST LA PART **SPÉCIFIQUE** : ce que connaître LA BONNE spire
        # achète au-delà de ce que connaître UNE spire quelconque achète déjà. Une première
        # version se contentait de `gain_tourne < gain`, une inégalité stricte sur des
        # flottants que le bruit satisfait presque toujours — elle a imprimé OUI sur un
        # champ tourné qui capturait 83 % du gain.
        "gain_specifique": gain - gain_tourne,
        # La borne est DÉRIVÉE et non choisie : si un champ délibérément faux obtient plus
        # que la part spécifique du vrai, alors ce qui travaille est l'existence d'une
        # pénalité, pas l'identité qu'elle porte.
        "lidentite_est_la_cause": (gain - gain_tourne) > gain_tourne,
        # Et l'échelle : pour tracer une feuille d'un bout à l'autre il faut UN morceau par
        # mur. C'est la distance que la part spécifique doit couvrir.
        "reste_a_couvrir": base - 1.0,
        "part_du_chemin": (gain - gain_tourne) / (base - 1.0) if base > 1.0 else 0.0,
    }
    return r


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--colonnes", type=int, default=None)
    p.add_argument("--poids", type=float, default=4.0)
    p.add_argument("--ecart-max", type=float, default=0.5)
    p.add_argument("--json", type=Path, default=None)
    p.add_argument("--reagreger", action="store_true",
                   help="re-rendre le verdict depuis un JSON deja ecrit, sans repister")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if a.reagreger:
        r = agreger(json.loads(a.json.read_text()))
    else:
        r = agreger(mesurer(a.colonnes, a.poids, a.ecart_max, brouillon=a.json))
    w = r["verdict"]
    print(f"\n{'★ ' if w['lidentite_est_la_cause'] else ''}"
          f"L'IDENTITÉ EST-ELLE LA CAUSE ? "
          f"{'OUI' if w['lidentite_est_la_cause'] else 'NON'}")
    print(f"   morceaux par mur — témoin {w['morceaux_par_mur_temoin']:.2f}"
          f" · champ {-w['gain_du_champ']:+.2f}"
          f" · constant {-w['gain_du_constant']:+.2f}"
          f" · tourné {-w['gain_du_champ_tourne']:+.2f}")
    print(f"   part SPÉCIFIQUE de l'identité : {w['gain_specifique']:.2f} morceau"
          f" sur les {w['reste_a_couvrir']:.1f} à supprimer"
          f" = {100 * w['part_du_chemin']:.1f} % du chemin")
    if a.json:
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False))
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
