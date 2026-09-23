"""À l'échelle du segment, deux chemins de consensus vers le même chunk arrivent-ils sur la même spire ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LA MOINDRE BANDE NOUVELLE NE SOIT LUE. La seule chose regardée avant
d'écrire est la PRÉSENCE du consensus sur les deux bandes déjà publiées — celui des rangées de `219`
existe aux coutures 17 à 214, celui des colonnes de `223` aux coutures 7 à 391 — et le nombre de pas
par ligne, jamais une valeur.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P69`. `221` traverse une bande de rangées, `223` une bande de
colonnes, et elles ne se croisent qu'en un bloc de cinq chunks sur cinq. Une surface exige que tous les
chemins vers un même chunk y arrivent au même endroit. `222` l'a mesuré à l'échelle de quatre chunks ;
cette tranche le mesure à l'échelle du segment, par des BOUCLES DE CONSENSUS.

## Le rectangle, dérivé

Les bandes publiées sont au centre de la grille : la rangée `396 // 2 = 198`, la colonne `285 // 2 = 142`.
Les bandes nouvelles sont à mi-chemin entre ce centre et chaque bord, de part et d'autre : `m ± m // 2`,
soit les rangées 99 et 297 et les colonnes 71 et 213. ⚠⚠ DEUX bandes de chaque sorte et non une : une
seule aurait fermé un seul rectangle, dans un quadrant que la grille ne désigne pas. Deux ferment les
QUATRE rectangles autour de la croix centrale, congruents — quatre fermetures comparables au lieu d'une
— et un GRAND RECTANGLE, leur somme, qui ne passe que par les bandes nouvelles.

Chaque bande a le nombre de lignes de `219` — cinq, relu — centrées par la fonction même de `219`. Une
bande de rangées n'est lue qu'entre les colonnes 71 et 213, une bande de colonnes qu'entre les rangées 99
et 297 : ce que les boucles traversent, rien de plus.

## Ce qui se lit, et ce qui le contrôle

Le lecteur de `222` pour une bande de rangées, celui de `223` pour une bande de colonnes : le même chunk,
le même filtre du producteur, la même bande de bord, la même estimation. ⚠⚠⚠ CHAQUE BANDE NOUVELLE CROISE
UNE BANDE PUBLIÉE. Une bande de rangées coupe les colonnes 140–144 de `223` et relit leurs pas
VERTICAUX ; une bande de colonnes coupe les rangées 196–200 de `219` et relit leurs pas HORIZONTAUX — ce
que le lecteur de colonnes coupe désormais, par la coupe même de `la_ligne`. Sur ces croisements les pas
relus retombent à l'arrondi de la quatrième décimale, sur exactement les mêmes coutures, sinon la lecture
est REFUSÉE par son nom ; une bande sans aucune couture relue l'est aussi, faute de contrôle.

## Ce qui se mesure

Pour un rectangle de coins `(r0, c0)` et `(r1, c1)`, la FERMETURE

    L = H(r0 ; c0→c1) + V(c1 ; r0→r1) − H(r1 ; c0→c1) − V(c0 ; r0→r1)

où H et V sommes les pas du CONSENSUS le long d'un côté — la médiane des lignes présentes, au moins trois
sur cinq, l'instrument de `221`. `L` est l'écart entre les deux chemins de `(r0, c0)` à `(r1, c1)` : par
la rangée d'abord, ou par la colonne d'abord. Une géométrie la ferme exactement ; ce qui reste est
l'erreur accumulée des quatre côtés.

1. ⭐⭐⭐⭐ LE VERDICT : chaque boucle fermable, `|L|` contre le demi-feuillet. ⚠⚠ Un côté où le consensus
   manque à une seule couture laisse sa boucle OUVERTE : elle est comptée, jamais comblée.
2. ⭐⭐⭐ L'ÉPREUVE, et c'est le piège que la porte nomme : chaque côté est une marche, donc le nul d'une
   fermeture n'est pas zéro mais la somme de quatre marches indépendantes. `T = Σ L²` sur les quatre
   rectangles fermables, contre `T` quand chacun des DOUZE demi-côtés est tiré par blocs de ses propres
   pas centrés (`⌈n^(1/3)⌉`, `R4-L22`), indépendamment des autres, les rectangles partageant les
   demi-côtés qu'ils partagent. Les boucles se ferment MIEUX que des marches indépendantes quand
   `p ≤ 0,05` — c'est-à-dire que les chemins portent une géométrie commune, et pas seulement un bruit
   assez petit. ⚠ Pour chaque boucle, la part du nul sous le demi-feuillet : ce que le bruit seul aurait
   laissé passer.
3. ⭐⭐⭐ L'ÉTALON DE L'ÉPREUVE : sur des demi-côtés indépendants fabriqués — la dépendance d'un pas au `θ`
   DÉRIVÉ de l'autocorrélation que montrent les demi-côtés lus, leurs longueurs et leurs dispersions —
   l'épreuve ne doit conclure « mieux » qu'au taux de sa garantie, à deux écarts-types binomiaux près.
   Sinon elle ne tranche pas, et c'est dit.
4. ⭐⭐ LES CONTRÔLES NOMMÉS : la MOYENNE des lignes présentes au lieu de la médiane ; et les boucles d'UNE
   LIGNE PAR CÔTÉ — toutes les combinaisons de lignes qui couvrent leur côté sans un trou —, sur les
   mêmes coutures que le consensus.

## Les issues, exclusives

- une boucle fermable dépasse le demi-feuillet : deux chemins de consensus arrivent sur des spires
  différentes ;
- toutes restent dessous, et mieux que des marches indépendantes ;
- toutes restent dessous, mais pas mieux : c'est la petitesse du bruit qui les y mène ;
- toutes restent dessous, et l'épreuve ne tranche pas.

⚠⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : la part du pas que les lignes d'une bande PARTAGENT ne se retire
par aucun consensus, et elle s'additionne le long des quatre côtés ; si elle est de la géométrie, la
boucle la ferme, si elle est une erreur commune à une bande, rien de local ne la distingue.

Usage :
    uv run python src/nappe/deux_chemins_arrivent_ils_sur_la_meme_spire.py --verifier
    uv run python src/nappe/deux_chemins_arrivent_ils_sur_la_meme_spire.py --lire <lecture.json>
    uv run python src/nappe/deux_chemins_arrivent_ils_sur_la_meme_spire.py --depuis <lecture.json> \\
        --json docs/mesures/deux_chemins_arrivent_ils_sur_la_meme_spire.json
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))

from cinq_rangees_designent_elles_la_fautive import les_rangees_a_lire  # noqa: E402
from combien_de_rangees_faut_il_pour_lire_le_pas import LES_RANGEES, la_ligne  # noqa: E402
from la_recette_posee_sur_le_rouleau import DELAI  # noqa: E402
from le_consensus_traverse_t_il_la_hauteur import (la_colonne,  # noqa: E402
                                                   les_pas_dune_colonne)
from le_consensus_traverse_t_il_la_rangee import (le_consensus,  # noqa: E402
                                                  le_theta_dune_autocorrelation,
                                                  les_troncons, une_serie_dependante)
from le_vote_ramene_t_il_les_rangees_sur_le_feuillet import ce_que_219_a_rendu  # noqa: E402
from lecart_extreme_est_il_porte_par_une_rangee import GARANTIE  # noqa: E402
from les_boucles_se_ferment_elles import (LA_TOLERANCE_DE_REPRODUCTION,  # noqa: E402
                                          _un_pas, lire_la_surface)
from ou_le_maillage_quitte_t_il_son_feuillet import (le_segment_declare,  # noqa: E402
                                                     les_pannes_de_reseau)
from ouvrir_les_quinze import _rng  # noqa: E402
from pourquoi_lerreur_declaree_est_trop_petite import la_longueur_de_bloc  # noqa: E402
from que_montrent_ces_deux_vues import DEMI_PAS_EN_VOXELS  # noqa: E402
from zarr_depth import BUCKET, array_meta  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
CE_QUE_223_A_RENDU = MESURES / "le_consensus_traverse_t_il_la_hauteur.json"
GRAINE = 20261105
TIRAGES = 999
REPLICATS = 200

LA_QUESTION_DECLAREE = ("à l'échelle du segment, deux chemins de consensus vers le même chunk "
                        "arrivent-ils sur la même spire ?")
LA_MESURE_DECLAREE = ("la fermeture de chaque boucle de consensus — les quatre rectangles autour de la "
                      "croix centrale et le grand rectangle — contre le demi-feuillet, puis Σ L² sur "
                      "les quatre rectangles contre des demi-côtés tirés par blocs indépendamment")

LES_SENS = ("rangees", "colonnes")


# ─────────────────────────────── ce qui est relu, et ce qui est dérivé ───────────────────────────────

def ce_que_223_a_rendu(chemin: Path = CE_QUE_223_A_RENDU) -> dict:
    """Les pas verticaux des colonnes de `223`, relus de SA lecture publiée — jamais recalculés."""
    if not Path(chemin).exists():
        return {"decidable": False, "raison": f"{Path(chemin).name} est absent"}
    try:
        d = json.loads(Path(chemin).read_text())
    except (ValueError, OSError) as e:
        return {"decidable": False, "raison": f"{Path(chemin).name} est illisible : {e}"}
    if not d.get("decidable"):
        return {"decidable": False, "raison": "`223` est indécidable"}
    v_ = d.get("les_pas_verticaux_par_colonne")
    cols = d.get("les_colonnes_declarees") or []
    grilles = {tuple(x.get("grille_de_chunks") or [])
               for x in (d.get("les_colonnes_lues") or {}).values()}
    if not isinstance(v_, dict) or not v_ or len(grilles) != 1:
        return {"decidable": False, "raison": "`223` ne publie ni sa lecture ni sa grille"}
    if sorted(int(c) for c in v_) != sorted(int(c) for c in cols):
        return {"decidable": False, "raison": "la lecture de `223` n'est pas celle de ses colonnes"}
    pas = {int(c): {int(r): float(x[0]) for r, x in s.items()} for c, s in v_.items()}
    gy, gx = next(iter(grilles))
    return {"decidable": True, "les_pas_par_colonne": pas, "les_colonnes": sorted(pas),
            "la_grille": [int(gy), int(gx)]}


def les_centres(cote: int) -> list[int]:
    """Le centre de la grille et, de part et d'autre, le point à mi-chemin du bord : `m ± m // 2`.

    ⚠ SYMÉTRIQUES AUTOUR DU CENTRE, donc les quatre rectangles sont congruents et leurs fermetures se
    comparent : mêmes longueurs de côtés, mêmes nombres de coutures.
    """
    m = int(cote) // 2
    return [m - m // 2, m, m + m // 2]


def les_bandes_a_lire(rangees: int, colonnes: int, combien: int) -> list[dict]:
    """Les quatre bandes nouvelles — deux de rangées, deux de colonnes —, et la portion de chacune."""
    R, C = les_centres(rangees), les_centres(colonnes)
    out = []
    for r in (R[0], R[2]):
        out.append({"cle": f"rangees_{r}", "le_sens": "rangees", "le_centre": int(r),
                    "les_lignes": les_rangees_a_lire(r, combien), "de": int(C[0]), "a": int(C[2])})
    for c in (C[0], C[2]):
        out.append({"cle": f"colonnes_{c}", "le_sens": "colonnes", "le_centre": int(c),
                    "les_lignes": les_rangees_a_lire(c, combien), "de": int(R[0]), "a": int(R[2])})
    return out


# ─────────────────────────────── la lecture ───────────────────────────────

def les_pas_horizontaux_entre(gauche: dict, droite: dict) -> dict:
    """Le pas de chaque couture entre deux colonnes de chunks voisines, indexé par la RANGÉE.

    ⚠⚠ LE SENS EST CELUI DE `les_pas_horizontaux` : le bord droit du chunk de gauche contre le bord
    gauche du chunk de droite. Pris à l'envers, une boucle sommerait ce côté contre les trois autres et
    ne se fermerait jamais.
    """
    out = {}
    coupes = gauche.get("les_rangees_lues") or []
    for r in sorted(gauche.get("droits") or {}):
        if r not in (droite.get("gauches") or {}):
            continue
        x = _un_pas(gauche["droits"][r], droite["gauches"][r], coupes)
        if x is not None:
            out[int(r)] = x
    return out


def lire_une_bande(bande: dict, volume: dict | None = None, delai: float = DELAI, ouvrir=None,
                   meta=None, lire_une=None) -> dict:
    """Une bande : ses pas LE LONG de sa direction, par ligne, et ses pas EN TRAVERS, qui la contrôlent.

    `le_long` : `{ligne: {couture: pas}}` ; `en_travers` : `{rangée: {colonne: pas}}`, à l'indexation de
    la grille — le pas vertical sous la rangée du dessus, le pas horizontal à la colonne de gauche.
    """
    voulues = list(range(int(bande["de"]), int(bande["a"]) + 1))
    if bande["le_sens"] == "rangees":
        if lire_une is None:
            def lire_une(r):  # noqa: E306
                return la_ligne(volume, delai, None, ouvrir, meta, LES_RANGEES, int(r),
                                les_bords_verticaux=True, les_colonnes_voulues=voulues)
        lu = lire_la_surface(bande["les_lignes"], delai, ouvrir, meta, volume, lire_une)
        if not lu.get("decidable"):
            return lu
        return {"decidable": True, "le_long": lu["h"], "en_travers": lu["v"],
                "les_lectures": lu["les_lignes"]}
    if lire_une is None:
        def lire_une(c):  # noqa: E306
            return la_colonne(volume, delai, int(c), ouvrir, meta, LES_RANGEES, voulues,
                              les_bords_horizontaux=True)
    le_long, en_travers, lectures, precedente = {}, {}, {}, None
    for c in [int(x) for x in bande["les_lignes"]]:
        lc = lire_une(c)
        if not lc.get("decidable"):
            return {"decidable": False, "raison": f"la colonne {c} est vide : {lc.get('raison')}"}
        pannes = les_pannes_de_reseau(lc.get("refuses"))
        if pannes:
            return {"decidable": False,
                    "raison": (f"{pannes} chunks perdus par le réseau sur la colonne {c} — une "
                               f"colonne dont le fil est tombé n'est pas comparable")}
        le_long[c] = les_pas_dune_colonne(lc)
        if precedente is not None:
            for r, x in les_pas_horizontaux_entre(precedente[1], lc).items():
                en_travers.setdefault(int(r), {})[precedente[0]] = x
        precedente = (c, lc)
        lectures[c] = {k: x for k, x in lc.items() if k not in ("bas", "hauts", "droits", "gauches")}
    return {"decidable": True, "le_long": le_long, "en_travers": en_travers, "les_lectures": lectures}


def _p(x) -> list:
    return [round(float(x[0]), 4), round(float(x[1]), 4), int(x[2])]


def _la_definition(bande: dict) -> dict:
    return {k: bande[k] for k in ("le_sens", "le_centre", "les_lignes", "de", "a")}


def publier_une_bande(bande: dict, lu: dict) -> dict:
    """Une bande sous la forme qui se rejoue : `[pas, désaccord, coupes]` par couture, quatre décimales."""
    def _d(d):  # noqa: E306
        return {str(a): {str(b): _p(x) for b, x in sorted(s.items())} for a, s in sorted(d.items())}
    return {**_la_definition(bande), "le_long": _d(lu["le_long"]), "en_travers": _d(lu["en_travers"]),
            "les_lectures": {str(k): x for k, x in sorted(lu["les_lectures"].items())}}


def relire_une_bande(d: dict) -> dict:
    def _r(x):  # noqa: E306
        return {int(a): {int(b): (float(t[0]), float(t[1]), int(t[2])) for b, t in s.items()}
                for a, s in (x or {}).items()}
    return {**{k: d.get(k) for k in ("le_sens", "le_centre", "les_lignes", "de", "a")},
            "le_long": _r(d.get("le_long")), "en_travers": _r(d.get("en_travers")),
            "les_lectures": d.get("les_lectures") or {}}


def lire_les_bandes(bandes, deja: dict | None = None, ecrire=None, delai: float = DELAI, ouvrir=None,
                    meta=None, volume=None, lire=None) -> dict:
    """Les bandes, une à une — et une lecture interrompue reprend à la bande suivante.

    ⚠⚠ UNE BANDE EST LUE ENTIÈRE OU PAS DU TOUT : elle n'est écrite que finie, donc une reprise ne
    raccorde jamais deux moitiés de bande. Une bande déjà écrite n'est reprise que si sa définition est
    celle d'aujourd'hui. ⚠ Une ligne vide ou dont le fil est tombé arrête tout, par son nom.
    """
    publiees = {k: x for k, x in (deja or {}).items()}
    if lire is None:
        if volume is None:
            volume = le_segment_declare()
            if volume is None:
                return {"decidable": False, "raison": "aucun volume recensé", "les_bandes": publiees}
        if meta is None:
            try:
                meta = array_meta(f"{BUCKET}/{volume['cle']}", 0, delai)
            except Exception as e:  # noqa: BLE001
                return {"decidable": False, "les_bandes": publiees,
                        "raison": f"le volume ne répond pas : {type(e).__name__}"}

        def lire(bande):  # noqa: E306
            return lire_une_bande(bande, volume, delai, ouvrir, meta)
    for bande in bandes:
        ancienne = publiees.get(bande["cle"])
        if ancienne is not None and _la_definition(ancienne) == _la_definition(bande):
            continue
        lu = lire(bande)
        if not lu.get("decidable"):
            return {"decidable": False, "raison": f"la bande {bande['cle']} : {lu.get('raison')}",
                    "les_bandes": publiees}
        publiees[bande["cle"]] = publier_une_bande(bande, lu)
        if ecrire is not None:
            ecrire(publiees)
    return {"decidable": True, "les_bandes": publiees}


def la_reproduction(bandes: dict, par219: dict, par223: dict,
                    tolerance: float = LA_TOLERANCE_DE_REPRODUCTION) -> dict:
    """Là où une bande nouvelle croise une bande publiée, les pas relus retombent-ils ? Sinon, refus.

    ⚠⚠ UNE BANDE DE RANGÉES relit les pas VERTICAUX de `223` à ses colonnes ; UNE BANDE DE COLONNES les
    pas HORIZONTAUX de `219` à ses rangées. Les mêmes coutures des deux côtés : un pas que l'un lit et
    l'autre non serait un chunk que les deux lecteurs ne retiennent pas pareil.
    """
    v223 = {(int(r), int(c)): float(x) for c, s in par223["les_pas_par_colonne"].items()
            for r, x in s.items()}
    h219 = {(int(r), int(c)): float(x) for r, s in par219["les_pas_par_rangee"].items()
            for c, x in s.items()}
    par_bande, ecarts = {}, []
    for cle in sorted(bandes):
        b = bandes[cle]
        lignes = [int(x) for x in b["les_lignes"]]
        if b["le_sens"] == "rangees":
            publies, croisees = v223, [(r, c) for r in lignes[:-1] for c in par223["les_colonnes"]]
        else:
            publies, croisees = h219, [(r, c) for r in par219["les_rangees"] for c in lignes[:-1]]
        vus = 0
        for r, c in croisees:
            chez_eux = (r, c) in publies
            chez_moi = c in (b["en_travers"].get(r) or {})
            if chez_eux != chez_moi:
                return {"decidable": False,
                        "raison": (f"la couture ({r}, {c}) de la bande {cle} est lue par un seul des "
                                   f"deux lecteurs")}
            if not chez_eux:
                continue
            e = abs(float(b["en_travers"][r][c][0]) - publies[(r, c)])
            if e > float(tolerance):
                return {"decidable": False,
                        "raison": (f"la couture ({r}, {c}) de la bande {cle} ne retombe pas sur ce qui "
                                   f"est publié (écart {e:.4g} voxel) — deux lecteurs différents")}
            ecarts.append(e)
            vus += 1
        if not vus:
            return {"decidable": False,
                    "raison": f"la bande {cle} ne croise aucune couture publiée — rien ne la contrôle"}
        par_bande[cle] = vus
    return {"decidable": True, "combien_de_coutures_relues": int(sum(par_bande.values())),
            "par_bande": par_bande, "lecart_le_plus_grand": round(float(max(ecarts)), 6),
            "la_tolerance": float(tolerance)}


# ─────────────────────────────── les boucles ───────────────────────────────

def les_boucles_declarees(R, C) -> dict:
    """Les quatre rectangles autour de la croix centrale, et le grand rectangle qui est leur somme."""
    out = {}
    for i, ni in ((0, "haut"), (1, "bas")):
        for j, nj in ((0, "gauche"), (1, "droite")):
            out[f"{ni}_{nj}"] = (int(R[i]), int(R[i + 1]), int(C[j]), int(C[j + 1]))
    out["le_grand_rectangle"] = (int(R[0]), int(R[2]), int(C[0]), int(C[2]))
    return out


def les_cotes(coins) -> list[tuple]:
    """Les quatre côtés d'un rectangle `(r0, r1, c0, c1)` : `(sens, centre, de, à, signe, nom)`.

    ⚠⚠ LES SIGNES FONT LA BOUCLE : le chemin par la rangée d'abord (haut puis droite) moins le chemin
    par la colonne d'abord (gauche puis bas). Une géométrie les rend égaux.
    """
    r0, r1, c0, c1 = coins
    return [("rangees", r0, c0, c1, +1, "haut"), ("colonnes", c1, r0, r1, +1, "droite"),
            ("rangees", r1, c0, c1, -1, "bas"), ("colonnes", c0, r0, r1, -1, "gauche")]


def les_demi_cotes(R, C) -> list[tuple]:
    """Les douze demi-côtés `(sens, centre, de, à)` : chaque bande coupée par la croix centrale."""
    out = []
    for r in R:
        out += [("rangees", int(r), int(C[0]), int(C[1])), ("rangees", int(r), int(C[1]), int(C[2]))]
    for c in C:
        out += [("colonnes", int(c), int(R[0]), int(R[1])), ("colonnes", int(c), int(R[1]), int(R[2]))]
    return out


def _les_morceaux(cote: tuple, demi_cotes) -> list[tuple]:
    sens, centre, de, a = cote[:4]
    return [d for d in demi_cotes if d[0] == sens and d[1] == centre and d[2] >= de and d[3] <= a]


def la_somme(cons: dict, de: int, a: int) -> tuple:
    """La somme des pas du consensus sur `[de, a)`, dans l'ordre — ou les coutures où il manque."""
    manquantes = [int(s) for s in range(int(de), int(a)) if s not in cons]
    if manquantes:
        return None, manquantes
    return float(sum(float(cons[s]) for s in range(int(de), int(a)))), []


def les_sommes(cons_par_bande: dict, demi_cotes) -> dict:
    """La somme de chaque demi-côté, ou `None` quand le consensus y manque à une couture."""
    return {d: la_somme(cons_par_bande.get((d[0], d[1])) or {}, d[2], d[3])[0] for d in demi_cotes}


def la_fermeture(sommes: dict, coins, demi_cotes):
    """`L` composée des sommes des demi-côtés — la même composition pour la matière et pour le nul.

    ⚠⚠ ÉCRITE UNE FOIS : une fermeture calculée autrement dans le nul serait un nul d'une autre boucle.
    Les sommes peuvent être des nombres ou des tableaux de tirages. `None` quand un morceau manque.
    """
    L = 0.0
    for cote in les_cotes(coins):
        for d in _les_morceaux(cote, demi_cotes):
            if sommes.get(d) is None:
                return None
            L = L + cote[4] * sommes[d]
    return L


def les_deux_chemins(cons_par_bande: dict, coins) -> dict:
    """Les deux chemins du coin `(r0, c0)` au coin `(r1, c1)`, cumulés couture par couture."""
    r0, r1, c0, c1 = coins

    def _pas(sens, centre, de, a):  # noqa: E306
        c_ = cons_par_bande[(sens, centre)]
        return [float(c_[s]) for s in range(de, a)]

    def _cumul(st):  # noqa: E306
        return [round(float(x), 4) for x in np.concatenate(([0.0], np.cumsum(st)))]
    return {"par_la_rangee_dabord": _cumul(_pas("rangees", r0, c0, c1) + _pas("colonnes", c1, r0, r1)),
            "par_la_colonne_dabord": _cumul(_pas("colonnes", c0, r0, r1) + _pas("rangees", r1, c0, c1)),
            "le_coude": int(c1 - c0), "lautre_coude": int(r1 - r0)}


def les_boucles_dune_ligne(pas_par_bande: dict, coins, demi: float = DEMI_PAS_EN_VOXELS) -> dict:
    """Le contrôle nommé : chaque côté parcouru par UNE ligne de sa bande, qui le couvre sans un trou.

    ⚠ Toutes les combinaisons, sans tirage : même boucle, mêmes coutures que le consensus.
    """
    options, couvrent = [], {}
    for sens, centre, de, a, signe, nom in les_cotes(coins):
        pas = pas_par_bande[(sens, centre)]
        o = [(int(l_), signe * float(sum(float(pas[l_][s]) for s in range(de, a))))
             for l_ in sorted(pas) if all(s in pas[l_] for s in range(de, a))]
        couvrent[nom] = [x[0] for x in o]
        options.append(o)
    if any(not o for o in options):
        return {"decidable": False, "raison": "un côté n'a aucune ligne sans trou",
                "les_lignes_qui_couvrent": couvrent}
    f = [sum(x[1] for x in combo) for combo in itertools.product(*options)]
    a_ = np.abs(np.asarray(f, dtype=float))
    return {"decidable": True, "les_lignes_qui_couvrent": couvrent, "combien": len(f),
            "la_fermeture_mediane_en_valeur_absolue": round(float(np.median(a_)), 4),
            "la_plus_grande_en_valeur_absolue": round(float(a_.max()), 4),
            "combien_sous_le_demi_pli": int(np.sum(a_ < float(demi))),
            "les_fermetures_en_voxels": sorted(round(float(x), 4) for x in f)}


# ─────────────────────────────── le nul, l'épreuve, l'étalon ───────────────────────────────

def les_sommes_par_blocs(pas, tirages: int, graine: int, bloc: int | None = None) -> np.ndarray:
    """La somme d'une marche de la longueur du demi-côté, faite de ses pas CENTRÉS tirés par blocs.

    ⚠⚠ C'EST LA SOMME, là où `les_marches_par_blocs` de `221` rend la distance au départ : la même
    matière — pas centrés (`R4-L22`), blocs mobiles de `⌈n^(1/3)⌉` —, une autre lecture de la marche.
    """
    a = np.asarray(pas, dtype=float)
    a = a - float(np.mean(a))
    n = len(a)
    b = max(1, min(int(la_longueur_de_bloc(n) if bloc is None else bloc), n))
    k = -(-n // b)
    longueurs = np.full(k, b)
    longueurs[-1] = n - b * (k - 1)
    debuts = _rng(int(graine)).integers(0, n - b + 1, size=(int(tirages), k))
    cs = np.concatenate(([0.0], np.cumsum(a)))
    return (cs[debuts + longueurs] - cs[debuts]).sum(axis=1)


def lautocorrelation_commune(series) -> float | None:
    """L'autocorrélation au premier décalage, mise en commun sur des séries centrées chacune."""
    num = den = 0.0
    for s in series:
        a = np.asarray(s, dtype=float)
        if len(a) < 2:
            continue
        a = a - float(np.mean(a))
        num += float(np.dot(a[:-1], a[1:]))
        den += float(np.dot(a, a))
    return (num / den) if den > 0.0 else None


def lepreuve(pas_des_demi_cotes: dict, rectangles: dict, demi_cotes, tirages: int = TIRAGES,
             graine: int = GRAINE, garantie: float = GARANTIE,
             demi: float = DEMI_PAS_EN_VOXELS) -> dict:
    """Les rectangles se ferment-ils mieux que des demi-côtés tirés indépendamment ?

    `pas_des_demi_cotes` : `{demi-côté: [pas du consensus]}` pour les demi-côtés complets ;
    `rectangles` : `{nom: coins}` des rectangles fermables.
    """
    if not rectangles:
        return {"decidable": False, "raison": "aucun rectangle fermable"}
    obs = {d: float(np.sum(p)) for d, p in pas_des_demi_cotes.items()}
    nul = {d: les_sommes_par_blocs(p, tirages, int(graine) + 101 * i)
           for i, (d, p) in enumerate(sorted(pas_des_demi_cotes.items()))}
    L_obs = {n: float(la_fermeture(obs, c, demi_cotes)) for n, c in rectangles.items()}
    L_nul = {n: np.asarray(la_fermeture(nul, c, demi_cotes), dtype=float) for n, c in rectangles.items()}
    T = float(sum(x * x for x in L_obs.values()))
    Tn = np.sum([x * x for x in L_nul.values()], axis=0)
    aussi = int(np.sum(Tn <= T))
    p = (1.0 + aussi) / (1.0 + int(tirages))
    return {"decidable": True, "les_rectangles": sorted(rectangles), "tirages": int(tirages),
            "la_statistique": round(T, 4), "la_statistique_mediane_du_nul": round(float(np.median(Tn)), 4),
            "le_rapport_au_nul": round(T / float(np.median(Tn)), 4) if float(np.median(Tn)) > 0 else None,
            "tirages_au_moins_aussi_fermes": aussi, "la_valeur_p": round(float(p), 4),
            "la_garantie": float(garantie), "mieux_que_des_marches_independantes": bool(p <= garantie),
            "par_rectangle": {n: {"la_fermeture_mediane_du_nul_en_valeur_absolue":
                                  round(float(np.median(np.abs(L_nul[n]))), 4),
                                  "la_part_du_nul_sous_le_demi_pli":
                                  round(float(np.mean(np.abs(L_nul[n]) < float(demi))), 4),
                                  "la_part_du_nul_sous_la_fermeture":
                                  round(float(np.mean(np.abs(L_nul[n]) <= abs(L_obs[n]))), 4)}
                              for n in sorted(rectangles)}}


def sur_letalon(longueurs: dict, dispersions: dict, rectangles: dict, demi_cotes, theta: float,
                replicats: int = REPLICATS, tirages: int = TIRAGES, graine: int = GRAINE,
                garantie: float = GARANTIE) -> dict:
    """L'épreuve tient-elle sa garantie quand les demi-côtés SONT indépendants ?

    ⚠⚠⚠ LA RÉPONSE EST CONNUE : chaque demi-côté est une série à dépendance d'un pas, au `θ` dérivé de la
    matière, à la longueur et à la dispersion du demi-côté lu, tirée indépendamment des autres. L'épreuve
    ne doit y conclure « mieux » qu'au taux de sa garantie.
    """
    oui = 0
    echelle = float(np.sqrt(1.0 + float(theta) ** 2))
    for i in range(int(replicats)):
        matiere = {d: une_serie_dependante(theta, int(n), int(graine) + 100000 + 1000 * i + 7 * j)
                   * float(dispersions[d]) / echelle
                   for j, (d, n) in enumerate(sorted(longueurs.items()))}
        e = lepreuve(matiere, rectangles, demi_cotes, tirages, int(graine) + 3 * i + 1, garantie)
        oui += int(bool(e.get("mieux_que_des_marches_independantes")))
    taux = oui / float(replicats)
    borne = float(garantie) + 2.0 * float(np.sqrt(garantie * (1.0 - garantie) / float(replicats)))
    return {"decidable": True, "le_theta": round(float(theta), 4), "les_replicats": int(replicats),
            "tirages": int(tirages), "combien_concluent_mieux": int(oui), "le_taux": round(taux, 4),
            "la_borne": round(borne, 4), "elle_tient_sa_garantie": bool(taux <= borne)}


# ─────────────────────────────── le verdict ───────────────────────────────

def _ce_qui_reste(depasse: bool, mieux: bool | None) -> str:
    """Les quatre issues, EXCLUSIVES — et dépasser le demi-feuillet prime sur tout le reste."""
    if depasse:
        return ("À L'ÉCHELLE DU SEGMENT, DEUX CHEMINS DE CONSENSUS ARRIVENT SUR DES SPIRES "
                "DIFFÉRENTES")
    tete = "À L'ÉCHELLE DU SEGMENT, DEUX CHEMINS DE CONSENSUS ARRIVENT SUR LA MÊME SPIRE"
    if mieux is None:
        return f"{tete} ; L'ÉPREUVE CONTRE DES MARCHES INDÉPENDANTES NE TRANCHE PAS"
    if mieux:
        return f"{tete}, ET LES BOUCLES SE FERMENT MIEUX QUE DES MARCHES INDÉPENDANTES"
    return (f"{tete}, MAIS PAS MIEUX QUE DES MARCHES INDÉPENDANTES : C'EST LA PETITESSE DU BRUIT QUI "
            f"LES Y MÈNE")


def juger(boucles: dict, epreuve: dict, etalon: dict | None) -> dict:
    fermees = {n: b for n, b in boucles.items() if b.get("fermable")}
    depassent = sorted(n for n, b in fermees.items() if not b["sous_le_demi_pli"])
    mieux = None
    if epreuve.get("decidable") and etalon and etalon.get("elle_tient_sa_garantie"):
        mieux = bool(epreuve["mieux_que_des_marches_independantes"])
    return {"les_boucles_fermables": len(fermees),
            "les_boucles_ouvertes": sorted(n for n, b in boucles.items() if not b.get("fermable")),
            "les_boucles_qui_depassent": depassent,
            "la_plus_grande_fermeture_en_valeur_absolue":
                (round(max(abs(b["la_fermeture_en_voxels"]) for b in fermees.values()), 4)
                 if fermees else None),
            "lepreuve_tient": (bool(etalon.get("elle_tient_sa_garantie")) if etalon else None),
            "mieux_que_des_marches_independantes": mieux,
            "ce_qui_reste_a_mesurer": _ce_qui_reste(bool(depassent), mieux)}


# ─────────────────────────────── l'analyse ───────────────────────────────

def analyser(pas_par_bande: dict, R, C, graine: int = GRAINE, tirages: int = TIRAGES,
             replicats: int = REPLICATS, avec_etalon: bool = True,
             demi: float = DEMI_PAS_EN_VOXELS) -> dict:
    """Tout ce qui se calcule sur les six bandes — pur.

    `pas_par_bande` : `{(sens, centre): {ligne: {couture: pas}}}` pour les trois bandes de rangées
    (coutures = colonnes de gauche) et les trois bandes de colonnes (coutures = rangées du dessus).
    """
    attendues = {("rangees", int(r)) for r in R} | {("colonnes", int(c)) for c in C}
    if set(pas_par_bande) != attendues:
        return {"decidable": False, "raison": "les bandes analysées ne sont pas les six dérivées"}
    cons = {k: le_consensus(p) for k, p in pas_par_bande.items()}
    moy = {k: le_consensus(p, forme="moyenne") for k, p in pas_par_bande.items()}
    demi_cotes = les_demi_cotes(R, C)
    declarees = les_boucles_declarees(R, C)
    sommes, sommes_moy = les_sommes(cons, demi_cotes), les_sommes(moy, demi_cotes)

    couverture = {}
    for (sens, centre), c_ in sorted(cons.items()):
        de, a = (C[0], C[2]) if sens == "rangees" else (R[0], R[2])
        dedans = {s: x for s, x in c_.items() if de <= s < a}
        couverture[f"{sens}_{centre}"] = {
            "les_coutures_du_perimetre": int(a - de), "les_coutures_avec_consensus": len(dedans),
            "les_troncons": [[int(t[0]), int(t[-1]), len(t)] for t in les_troncons(dedans)],
            "les_coutures_sans_consensus": [int(s) for s in range(de, a) if s not in dedans]}

    boucles = {}
    for nom, coins in declarees.items():
        manquantes = {}
        for sens, centre, de, a, signe, nc in les_cotes(coins):
            _, m = la_somme(cons[(sens, centre)], de, a)
            if m:
                manquantes[nc] = m
        base = {"les_coins": [[coins[0], coins[2]], [coins[1], coins[3]]],
                "les_coutures_par_chemin": int((coins[1] - coins[0]) + (coins[3] - coins[2]))}
        if manquantes:
            boucles[nom] = {**base, "fermable": False, "les_coutures_manquantes": manquantes}
            continue
        L = float(la_fermeture(sommes, coins, demi_cotes))
        Lm = la_fermeture(sommes_moy, coins, demi_cotes)
        boucles[nom] = {**base, "fermable": True, "la_fermeture_en_voxels": round(L, 4),
                        "sous_le_demi_pli": bool(abs(L) < float(demi)),
                        "les_cotes_en_voxels": {nc: round(sg * float(la_somme(cons[(s_, c_)], d_, a_)[0]), 4)
                                                for s_, c_, d_, a_, sg, nc in les_cotes(coins)},
                        "la_fermeture_de_la_moyenne_en_voxels": (round(float(Lm), 4) if Lm is not None
                                                                 else None),
                        "les_deux_chemins_en_voxels": les_deux_chemins(cons, coins),
                        "les_boucles_dune_ligne": les_boucles_dune_ligne(pas_par_bande, coins, demi)}

    if not any(b.get("fermable") for b in boucles.values()):
        return {"decidable": False, "les_boucles": boucles,
                "raison": "aucune boucle ne se ferme : un côté de chacune manque de consensus"}
    rectangles = {n: c for n, c in declarees.items()
                  if n != "le_grand_rectangle" and boucles[n].get("fermable")}
    pas_dc = {d: [float(cons[(d[0], d[1])][s]) for s in range(d[2], d[3])]
              for d in demi_cotes if sommes[d] is not None}
    ep = lepreuve(pas_dc, rectangles, demi_cotes, tirages, graine, GARANTIE, demi)
    if boucles["le_grand_rectangle"].get("fermable"):
        # ⚠ LE GRAND RECTANGLE EST LA SOMME DES QUATRE — hors de Σ L², où il compterait deux fois.
        nul = {d: les_sommes_par_blocs(p, tirages, int(graine) + 101 * i)
               for i, (d, p) in enumerate(sorted(pas_dc.items()))}
        Lg = np.asarray(la_fermeture(nul, declarees["le_grand_rectangle"], demi_cotes), dtype=float)
        boucles["le_grand_rectangle"]["le_nul"] = {
            "la_fermeture_mediane_du_nul_en_valeur_absolue": round(float(np.median(np.abs(Lg))), 4),
            "la_part_du_nul_sous_le_demi_pli": round(float(np.mean(np.abs(Lg) < float(demi))), 4)}
    for n in rectangles:
        boucles[n]["le_nul"] = ep["par_rectangle"][n]
    rho1 = lautocorrelation_commune(pas_dc.values())
    theta = le_theta_dune_autocorrelation(rho1 if rho1 is not None else 0.0)
    etalon = None
    if avec_etalon and ep.get("decidable"):
        etalon = sur_letalon({d: len(p) for d, p in pas_dc.items()},
                             {d: float(np.std(p)) for d, p in pas_dc.items()},
                             rectangles, demi_cotes, theta, replicats, tirages, graine)
    return {"decidable": True, "le_demi_pli_en_voxels": int(demi),
            "les_centres": {"rangees": [int(r) for r in R], "colonnes": [int(c) for c in C]},
            "la_couverture_du_consensus": couverture,
            "les_demi_cotes": {f"{d[0]}_{d[1]}_{d[2]}_{d[3]}": {
                "les_coutures": int(d[3] - d[2]),
                "la_somme_en_voxels": (round(float(sommes[d]), 4) if sommes[d] is not None else None),
                "lecart_type_des_pas_en_voxels": (round(float(np.std(pas_dc[d])), 4) if d in pas_dc
                                                  else None)} for d in demi_cotes},
            "les_boucles": boucles, "lepreuve": ep,
            "lautocorrelation_commune_au_premier_decalage": (round(float(rho1), 4)
                                                             if rho1 is not None else None),
            "letalon_de_lepreuve": etalon, "le_verdict": juger(boucles, ep, etalon)}


def mesurer(depuis: Path | None = None, delai: float = DELAI, graine: int = GRAINE,
            tirages: int = TIRAGES, replicats: int = REPLICATS, avec_etalon: bool = True,
            par219: dict | None = None, par223: dict | None = None, lire=None) -> dict:
    """La lecture des quatre bandes puis l'analyse — ou l'analyse seule, rejouée."""
    par219 = ce_que_219_a_rendu() if par219 is None else par219
    par223 = ce_que_223_a_rendu() if par223 is None else par223
    for nom, par in (("219", par219), ("223", par223)):
        if not par.get("decidable"):
            return {"decidable": False, "raison": f"`{nom}` : {par.get('raison')}",
                    "la_question_declaree": LA_QUESTION_DECLAREE}
    gy, gx = par223["la_grille"]
    combien = len(par219["les_rangees"])
    if int(par219["les_coutures_dune_rangee"]) != int(gx) - 1 or len(par223["les_colonnes"]) != combien:
        return {"decidable": False, "raison": "`219` et `223` ne partagent ni la grille ni la bande",
                "la_question_declaree": LA_QUESTION_DECLAREE}
    R, C = les_centres(gy), les_centres(gx)
    if (sorted(par219["les_rangees"]) != les_rangees_a_lire(R[1], combien)
            or sorted(par223["les_colonnes"]) != les_rangees_a_lire(C[1], combien)):
        return {"decidable": False, "raison": "les bandes publiées ne sont pas au centre de la grille",
                "la_question_declaree": LA_QUESTION_DECLAREE}
    bandes = les_bandes_a_lire(gy, gx, combien)
    if depuis is not None:
        lu = {"decidable": True, "les_bandes": json.loads(Path(depuis).read_text()).get("les_bandes") or {}}
    else:
        lu = lire_les_bandes(bandes, delai=delai, lire=lire)
    base = {"graine": int(graine), "tirages": int(tirages), "replicats": int(replicats),
            "la_question_declaree": LA_QUESTION_DECLAREE, "la_mesure_declaree": LA_MESURE_DECLAREE,
            "la_grille": [int(gy), int(gx)], "les_bandes_declarees": bandes,
            "les_bandes": lu.get("les_bandes") or {}}
    if not lu.get("decidable"):
        return {**base, "decidable": False, "raison": lu.get("raison")}
    publiees = lu["les_bandes"]
    if (sorted(publiees) != sorted(b["cle"] for b in bandes)
            or any(_la_definition(publiees[b["cle"]]) != _la_definition(b) for b in bandes)):
        return {**base, "decidable": False, "raison": "la lecture n'est pas celle des bandes dérivées"}
    relues = {k: relire_une_bande(x) for k, x in publiees.items()}
    rep = la_reproduction(relues, par219, par223)
    if not rep.get("decidable"):
        return {**base, "decidable": False, "raison": rep.get("raison"), "la_reproduction": rep}
    pas_par_bande = {("rangees", int(R[1])): par219["les_pas_par_rangee"],
                     ("colonnes", int(C[1])): par223["les_pas_par_colonne"]}
    for b in bandes:
        pas_par_bande[(b["le_sens"], int(b["le_centre"]))] = {
            int(l_): {int(s): float(x[0]) for s, x in d.items()}
            for l_, d in relues[b["cle"]]["le_long"].items()}
    a = analyser(pas_par_bande, R, C, graine, tirages, replicats, avec_etalon)
    return {**base, "la_reproduction": rep, **a}


def afficher(r: dict) -> None:
    if not r.get("decidable"):
        print(f"indécidable : {r.get('raison')}")
        return
    rp = r["la_reproduction"]
    print(f"reproduction : {rp['combien_de_coutures_relues']} coutures {rp['par_bande']}, écart "
          f"{rp['lecart_le_plus_grand']}")
    for k, c in r["la_couverture_du_consensus"].items():
        print(f"  {k} · {c['les_coutures_avec_consensus']}/{c['les_coutures_du_perimetre']} · "
              f"sans consensus {c['les_coutures_sans_consensus'][:12]}")
    for n, b in r["les_boucles"].items():
        if not b.get("fermable"):
            print(f"  {n} · OUVERTE · {b['les_coutures_manquantes']}")
            continue
        u = b["les_boucles_dune_ligne"]
        un = (f"{u['combien_sous_le_demi_pli']}/{u['combien']} sous le demi-pli, médiane "
              f"{u['la_fermeture_mediane_en_valeur_absolue']}" if u.get("decidable") else u.get("raison"))
        nl = b.get("le_nul") or {}
        print(f"  {n} · L {b['la_fermeture_en_voxels']} · moyenne "
              f"{b['la_fermeture_de_la_moyenne_en_voxels']} · côtés {b['les_cotes_en_voxels']} · nul "
              f"médian {nl.get('la_fermeture_mediane_du_nul_en_valeur_absolue')} "
              f"({nl.get('la_part_du_nul_sous_le_demi_pli')} dessous) · une ligne : {un}")
    e = r["lepreuve"]
    if e.get("decidable"):
        print(f"épreuve · T {e['la_statistique']} contre {e['la_statistique_mediane_du_nul']} (rapport "
              f"{e['le_rapport_au_nul']}) · p {e['la_valeur_p']} · mieux "
              f"{e['mieux_que_des_marches_independantes']}")
    t = r.get("letalon_de_lepreuve")
    if t:
        print(f"étalon · ρ1 {r['lautocorrelation_commune_au_premier_decalage']} → θ {t['le_theta']} · "
              f"{t['combien_concluent_mieux']}/{t['les_replicats']} = {t['le_taux']} (borne "
              f"{t['la_borne']}) · tient {t['elle_tient_sa_garantie']}")
    print(f"VERDICT · {r['le_verdict']['ce_qui_reste_a_mesurer']}")


# ─────────────────────────────── la batterie ───────────────────────────────

def verifier() -> int:
    import tempfile

    import combien_de_rangees_faut_il_pour_lire_le_pas as cdr
    from les_boucles_se_ferment_elles import _une_grille, les_pas_horizontaux
    from ou_le_maillage_quitte_t_il_son_feuillet import LE_RESEAU_A_ECHOUE
    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        if not ok:
            echecs.append(f"{nom} {detail}")

    def _sur(f, *a, **k):
        try:
            return f(*a, **k)
        except Exception as e:  # noqa: BLE001
            return {"decidable": False, "raison": f"exception {type(e).__name__}: {e}"}

    def _ok(f):
        try:
            return bool(f())
        except Exception:  # noqa: BLE001
            return False

    # ── ce qui est dérivé
    v("★★★★ les centres sont le milieu de la grille et, de part et d'autre, le mi-chemin du bord",
      les_centres(396) == [99, 198, 297] and les_centres(285) == [71, 142, 213]
      and les_centres(12) == [3, 6, 9], str((les_centres(396), les_centres(285))))
    v("★★★ les bandes centrales sont celles de `219` et de `223`, par la fonction de `219`",
      les_rangees_a_lire(les_centres(396)[1], 5) == [196, 197, 198, 199, 200]
      and les_rangees_a_lire(les_centres(285)[1], 5) == [140, 141, 142, 143, 144])
    bd = les_bandes_a_lire(396, 285, 5)
    v("★★★★ quatre bandes nouvelles, lues sur la seule portion que les boucles traversent",
      [b["cle"] for b in bd] == ["rangees_99", "rangees_297", "colonnes_71", "colonnes_213"]
      and bd[0]["les_lignes"] == [97, 98, 99, 100, 101] and (bd[0]["de"], bd[0]["a"]) == (71, 213)
      and bd[2]["les_lignes"] == [69, 70, 71, 72, 73] and (bd[2]["de"], bd[2]["a"]) == (99, 297),
      str(bd[:1]))
    dc = les_demi_cotes([99, 198, 297], [71, 142, 213])
    decl = les_boucles_declarees([99, 198, 297], [71, 142, 213])
    v("★★★ douze demi-côtés, quatre rectangles congruents et le grand",
      len(dc) == 12 and len(set(dc)) == 12 and len(decl) == 5
      and {(c[1] - c[0], c[3] - c[2]) for n, c in decl.items() if n != "le_grand_rectangle"} == {(99, 71)}
      and decl["le_grand_rectangle"] == (99, 297, 71, 213))

    # ── les lecteurs, sur une grille fabriquée
    filtre = cdr.la_courbe_dun_bloc
    cdr.la_courbe_dun_bloc = lambda b: ([], None)
    try:
        f_ = lambda r, c: 2 * r - c + (r * c) % 5  # noqa: E731
        ouvrir, meta = _une_grille(12, 12, 60, 32, f_, 7, droite=2, bas=5)
        vol = {"cle": "x", "segment": "s"}
        entiere = _sur(la_ligne, vol, 0.0, None, ouvrir, meta, 16, 4, les_bords_verticaux=True)
        portion = _sur(la_ligne, vol, 0.0, None, ouvrir, meta, 16, 4, les_bords_verticaux=True,
                       les_colonnes_voulues=range(3, 10))
        he, hp = les_pas_horizontaux(entiere), les_pas_horizontaux(portion)
        v("★★★★ une portion de rangée lit les pas de la rangée entière, sur ses seules coutures",
          sorted(hp) == list(range(3, 9)) and all(hp[c] == he[c] for c in hp)
          and portion["colonnes_lues"] == 7, str(sorted(hp)))
        v("★★★ une portion hors du treillis est refusée",
          not _sur(la_ligne, vol, 0.0, None, ouvrir, meta, 16, 4,
                   les_colonnes_voulues=[11, 12]).get("decidable"))
        v("★★★ une portion de colonne hors du treillis est refusée",
          not _sur(la_colonne, vol, 0.0, 4, ouvrir, meta, 16, [-1, 0]).get("decidable"))
        c4 = _sur(la_colonne, vol, 0.0, 4, ouvrir, meta, 16, range(2, 9), les_bords_horizontaux=True)
        c5 = _sur(la_colonne, vol, 0.0, 5, ouvrir, meta, 16, range(2, 9), les_bords_horizontaux=True)
        hc = les_pas_horizontaux_entre(c4, c5) if c4.get("decidable") and c5.get("decidable") else {}
        rangs = {r: les_pas_horizontaux(_sur(la_ligne, vol, 0.0, None, ouvrir, meta, 16, r))
                 for r in range(2, 9)}
        v("★★★★ la marche en colonne coupe les bords gauche et droit comme la marche en rangée",
          sorted(hc) == list(range(2, 9)) and all(hc[r] == rangs[r][4] for r in hc),
          str({r: (hc.get(r), rangs[r].get(4)) for r in range(2, 4)}))
        v("★★★★ et le pas horizontal lu en colonne est la profondeur de droite moins celle de gauche",
          _ok(lambda: all(abs(hc[r][0] - (f_(r, 5) - f_(r, 4) - 2)) < 1e-9 for r in hc)),
          str({r: hc[r][0] for r in list(hc)[:3]}))
        v("★★★ sans le drapeau, la colonne ne coupe pas les bords gauche et droit",
          "droits" not in _sur(la_colonne, vol, 0.0, 4, ouvrir, meta, 16, range(2, 4)))

        # une bande de chaque sorte, lue par `lire_une_bande`
        br = {"cle": "rangees_3", "le_sens": "rangees", "le_centre": 3, "les_lignes": [2, 3, 4],
              "de": 3, "a": 9}
        bc = {"cle": "colonnes_3", "le_sens": "colonnes", "le_centre": 3, "les_lignes": [2, 3, 4],
              "de": 3, "a": 9}
        lr = _sur(lire_une_bande, br, vol, 0.0, ouvrir, meta)
        lc_ = _sur(lire_une_bande, bc, vol, 0.0, ouvrir, meta)
        v("★★★★ une bande de rangées rend ses pas le long, par ligne, et les pas verticaux en travers",
          _ok(lambda: sorted(lr["le_long"]) == [2, 3, 4] and sorted(lr["le_long"][3]) == list(range(3, 9))
              and all(abs(lr["le_long"][r][c][0] - (f_(r, c + 1) - f_(r, c) - 2)) < 1e-9
                      for r in lr["le_long"] for c in lr["le_long"][r])
              and sorted(lr["en_travers"]) == [2, 3]
              and all(abs(lr["en_travers"][r][c][0] - (f_(r + 1, c) - f_(r, c) - 5)) < 1e-9
                      for r in lr["en_travers"] for c in lr["en_travers"][r])))
        v("★★★★ une bande de colonnes rend ses pas le long, par ligne, et les pas horizontaux en travers",
          _ok(lambda: sorted(lc_["le_long"]) == [2, 3, 4]
              and all(abs(lc_["le_long"][c][r][0] - (f_(r + 1, c) - f_(r, c) - 5)) < 1e-9
                      for c in lc_["le_long"] for r in lc_["le_long"][c])
              and sorted(lc_["le_long"][2]) == list(range(3, 9))
              and all(sorted(s) == [2, 3] for s in lc_["en_travers"].values())
              and all(abs(lc_["en_travers"][r][c][0] - (f_(r, c + 1) - f_(r, c) - 2)) < 1e-9
                      for r in lc_["en_travers"] for c in lc_["en_travers"][r])))
        panne = _sur(lire_une_bande, bc, vol, 0.0, ouvrir, meta, lire_une=lambda c: {
            **la_colonne(vol, 0.0, c, ouvrir, meta, 16, range(3, 10), les_bords_horizontaux=True),
            "refuses": {f"{LE_RESEAU_A_ECHOUE} x": 1}})
        v("★★★ une colonne dont le fil est tombé arrête la bande, par sa raison",
          not panne.get("decidable") and "réseau" in str(panne.get("raison")), str(panne.get("raison")))
        v("★★ une ligne vide arrête la bande", not _sur(lire_une_bande, bc, lire_une=lambda c: {
            "decidable": False}).get("decidable"))
        cdr.la_courbe_dun_bloc = lambda b: (None, "trop peu texturé")
        tout = _sur(lire_une_bande, br, vol, 0.0, ouvrir, meta)
        v("★★★★ le filtre du producteur est appelé sur chaque chunk de la bande",
          not tout.get("decidable") and "vide" in str(tout.get("raison")), str(tout.get("raison")))
        cdr.la_courbe_dun_bloc = lambda b: ([], None)

        # la lecture reprend là où elle s'est arrêtée, et se relit
        appels = []

        def _lire(b):  # noqa: E306
            appels.append(b["cle"])
            return lire_une_bande(b, vol, 0.0, ouvrir, meta)
        ecrits = []
        premiere = _sur(lire_les_bandes, [br], lire=_lire, ecrire=lambda d: ecrits.append(dict(d)))
        v("★★★ chaque bande est écrite finie, une à une", premiere.get("decidable") and len(ecrits) == 1)
        suite = _sur(lire_les_bandes, [br, bc], deja=premiere.get("les_bandes"), lire=_lire)
        v("★★★★ une lecture reprise ne relit pas la bande déjà finie",
          suite.get("decidable") and appels == ["rangees_3", "colonnes_3"], str(appels))
        autre = dict(br, a=8)
        _sur(lire_les_bandes, [autre], deja=suite.get("les_bandes"), lire=_lire)
        v("★★★ une bande écrite sous une autre définition est relue", appels[-1] == "rangees_3",
          str(appels))
        v("★★★ la lecture se publie et se relit à la quatrième décimale",
          _ok(lambda: relire_une_bande(json.loads(json.dumps(publier_une_bande(br, lr))))["le_long"]
              == {a: {b: (round(x[0], 4), round(x[1], 4), x[2]) for b, x in s.items()}
                  for a, s in lr["le_long"].items()}))

        # ⭐ DE BOUT EN BOUT : une géométrie fabriquée, lue par les lecteurs, se ferme sur les cinq boucles.
        # ⚠ Le champ est BILINÉAIRE, pour que le pas de chaque ligne soit affine dans l'indice de la ligne :
        # la médiane d'une bande est alors sa ligne centrale, et la boucle des lignes centrales se ferme
        # exactement. Le terme croisé fait que deux côtés opposés diffèrent — un signe faux se verrait.
        fb = lambda r, c: (r - 5) * (c - 5) + (r % 2) - (c % 2)  # noqa: E731
        ouvrir, meta = _une_grille(10, 10, 60, 32, fb, 7, droite=2, bas=5)
        R_, C_ = les_centres(10), les_centres(10)
        l_ctr = {r: les_pas_horizontaux(_sur(la_ligne, vol, 0.0, None, ouvrir, meta, 16, r))
                 for r in les_rangees_a_lire(R_[1], 3)}
        c_ctr = {c: les_pas_dune_colonne(_sur(la_colonne, vol, 0.0, c, ouvrir, meta, 16))
                 for c in les_rangees_a_lire(C_[1], 3)}
        f219 = {"decidable": True, "les_rangees": sorted(l_ctr), "les_coutures_dune_rangee": 9,
                "les_pas_par_rangee": {r: {c: round(x[0], 4) for c, x in s.items()}
                                       for r, s in l_ctr.items()}}
        f223 = {"decidable": True, "les_colonnes": sorted(c_ctr), "la_grille": [10, 10],
                "les_pas_par_colonne": {c: {r: round(x[0], 4) for r, x in s.items()}
                                        for c, s in c_ctr.items()}}
        m = _sur(mesurer, None, 0.0, 5, 50, 4, True, f219, f223,
                 lambda b: lire_une_bande(b, vol, 0.0, ouvrir, meta))
        v("★★★★ de bout en bout, une géométrie fabriquée se ferme sur les cinq boucles",
          m.get("decidable") and m["le_verdict"]["les_boucles_fermables"] == 5
          and all(abs(b["la_fermeture_en_voxels"]) < 1e-6 for b in m["les_boucles"].values()),
          str(m.get("raison") or {n: b.get("la_fermeture_en_voxels") for n, b in m["les_boucles"].items()}))
        v("★★★★ et chaque bande nouvelle y est contrôlée par une bande publiée",
          _ok(lambda: sorted(m["la_reproduction"]["par_bande"]) == sorted(
              b["cle"] for b in les_bandes_a_lire(10, 10, 3))
              and m["la_reproduction"]["par_bande"]["rangees_3"] == 2 * 3
              and m["la_reproduction"]["par_bande"]["colonnes_7"] == 3 * 2), str(m.get("la_reproduction")))
        v("★★★ et ses côtés opposés diffèrent : la sonde verrait un signe faux",
          _ok(lambda: abs(m["les_boucles"]["haut_gauche"]["les_cotes_en_voxels"]["haut"]
                          + m["les_boucles"]["haut_gauche"]["les_cotes_en_voxels"]["bas"]) > 1.0))
        v("★★★ les deux chemins partent ensemble et finissent à l'écart de la fermeture",
          _ok(lambda: all(b["les_deux_chemins_en_voxels"]["par_la_rangee_dabord"][0] == 0.0
                          and abs(b["les_deux_chemins_en_voxels"]["par_la_rangee_dabord"][-1]
                                  - b["les_deux_chemins_en_voxels"]["par_la_colonne_dabord"][-1]
                                  - b["la_fermeture_en_voxels"]) < 1e-3
                          for b in m["les_boucles"].values())))
        mal = {**f219, "les_rangees": [1, 2, 3]}
        v("★★★ des bandes publiées hors du centre de la grille sont refusées, par leur raison",
          "centre de la grille" in str(_sur(mesurer, None, 0.0, 5, 50, 4, False, mal, f223,
                                            lambda b: lire_une_bande(b, vol, 0.0, ouvrir, meta)
                                            ).get("raison")))
        with tempfile.TemporaryDirectory() as t:
            fch = Path(t) / "l.json"
            bonnes = m.get("les_bandes") or {}
            fch.write_text(json.dumps({"les_bandes": bonnes}))
            rejeu = _sur(mesurer, fch, 0.0, 5, 50, 4, False, f219, f223)
            v("★★★ la mesure se rejoue depuis sa lecture publiée",
              rejeu.get("decidable") and rejeu["les_boucles"] == m["les_boucles"])
            fch.write_text(json.dumps({"les_bandes": {k: x for k, x in bonnes.items()
                                                      if k != "colonnes_7"}}))
            v("★★★★ une lecture qui n'a pas les bandes dérivées est refusée, par sa raison",
              "bandes dérivées" in str(_sur(mesurer, fch, 0.0, 5, 50, 4, False, f219, f223).get("raison")))
            fausse = json.loads(json.dumps(bonnes))
            try:
                # ⚠ la matière fabriquée elle-même peut manquer sous un bris : la sonde rougit, sans mourir
                fausse["rangees_3"]["en_travers"]["2"][str(f223["les_colonnes"][0])][0] += 1.0
            except (KeyError, IndexError):
                fausse = {}
            fch.write_text(json.dumps({"les_bandes": fausse}))
            v("★★★★ une lecture qui ne retombe pas sur la bande publiée est refusée, par sa raison",
              "ne retombe pas" in str(_sur(mesurer, fch, 0.0, 5, 50, 4, False, f219, f223).get("raison")))
    finally:
        cdr.la_courbe_dun_bloc = filtre

    # ── la reproduction, en elle-même
    p219 = {"les_rangees": [196, 197], "les_pas_par_rangee": {196: {69: 1.5, 70: 2.0}, 197: {69: 0.5}}}
    p223 = {"les_colonnes": [140], "les_pas_par_colonne": {140: {97: -1.0, 98: 3.0}}}
    bandes_ok = {"colonnes_71": {"le_sens": "colonnes", "les_lignes": [69, 70, 71],
                                 "en_travers": {196: {69: (1.5, 0, 16), 70: (2.0, 0, 16)},
                                                197: {69: (0.5, 0, 16)}, 50: {69: (9.0, 0, 16)}}},
                 "rangees_99": {"le_sens": "rangees", "les_lignes": [97, 98, 99],
                                "en_travers": {97: {140: (-1.0, 0, 16)}, 98: {140: (3.0, 0, 16)}}}}
    rp = _sur(la_reproduction, bandes_ok, p219, p223)
    v("★★★ des pas qui retombent sont reproduits, bande par bande, sur les seules coutures croisées",
      rp.get("decidable") and rp["par_bande"] == {"colonnes_71": 3, "rangees_99": 2}, str(rp))
    b1 = json.loads(json.dumps(bandes_ok, default=list))

    def _refait(x):  # noqa: E306
        return {k: {**b, "en_travers": {int(r): {int(c): tuple(t) for c, t in s.items()}
                                        for r, s in b["en_travers"].items()}} for k, b in x.items()}
    b1 = _refait(b1)
    b1["colonnes_71"]["en_travers"][196][70] = (2.1, 0, 16)
    v("★★★★ un écart au-delà de l'arrondi est refusé",
      "ne retombe pas" in str(_sur(la_reproduction, b1, p219, p223).get("raison")))
    b2 = _refait(json.loads(json.dumps(bandes_ok, default=list)))
    b2["rangees_99"]["en_travers"][98].pop(140)
    v("★★★★ une couture lue d'un seul côté est refusée",
      "un seul des deux" in str(_sur(la_reproduction, b2, p219, p223).get("raison")))
    b3 = _refait(json.loads(json.dumps(bandes_ok, default=list)))
    b3["colonnes_71"]["en_travers"][197][70] = (4.0, 0, 16)
    v("★★★ et dans l'autre sens aussi",
      "un seul des deux" in str(_sur(la_reproduction, b3, p219, p223).get("raison")))
    b4 = _refait(json.loads(json.dumps(bandes_ok, default=list)))
    b4["colonnes_71"]["les_lignes"] = [10, 11, 12]
    b4["colonnes_71"]["en_travers"] = {}
    v("★★★ une bande qui ne croise aucune couture publiée n'est pas contrôlée, et est refusée",
      "aucune couture publiée" in str(_sur(la_reproduction, b4, p219, p223).get("raison")))

    # ── les boucles, sur des pas fabriqués
    R, C = [2, 5, 8], [1, 4, 7]
    g = np.random.default_rng(11)
    D = g.normal(0.0, 5.0, (11, 10))
    pas = {}
    for r in R:
        pas[("rangees", r)] = {l_: {c: float(D[r, c + 1] - D[r, c]) for c in range(0, 9)}
                               for l_ in range(r - 2, r + 3)}
    for c in C:
        pas[("colonnes", c)] = {l_: {r: float(D[r + 1, c] - D[r, c]) for r in range(0, 10)}
                                for l_ in range(c - 2, c + 3)}
    a = _sur(analyser, pas, R, C, 3, 199, 10, False)
    ok_a = bool(a.get("decidable"))

    def _a(f):  # noqa: E306
        # ⚠⚠ chaque sonde de l'analyse TOURNE, même quand l'analyse a échoué.
        return ok_a and _ok(f)
    v("★★★ l'analyse est décidable sur des pas fabriqués", ok_a, str(a.get("raison")))
    v("★★★★ une géométrie ferme exactement les cinq boucles",
      _a(lambda: all(abs(b["la_fermeture_en_voxels"]) < 1e-9 for b in a["les_boucles"].values())))
    v("★★★★ et l'épreuve la reconnaît : aucun tirage indépendant ne se ferme aussi bien",
      _a(lambda: a["lepreuve"]["la_statistique"] == 0.0 and a["lepreuve"]["tirages_au_moins_aussi_fermes"] == 0
         and len(a["lepreuve"]["les_rectangles"]) == 4
         and a["lepreuve"]["la_valeur_p"] == round(1.0 / 200.0, 4)
         and a["lepreuve"]["mieux_que_des_marches_independantes"]), str(a.get("lepreuve", {}).get("la_valeur_p")))
    p2 = {k: {l_: dict(s) for l_, s in x.items()} for k, x in pas.items()}
    for l_ in p2[("colonnes", 7)]:
        p2[("colonnes", 7)][l_][3] += 40.0
    a2 = _sur(analyser, p2, R, C, 3, 199, 10, False)
    v("★★★★ un pas de plus sur le côté droit ouvre sa boucle de ce pas, avec son signe, et le grand aussi",
      _ok(lambda: abs(a2["les_boucles"]["haut_droite"]["la_fermeture_en_voxels"] - 40.0) < 1e-9
          and abs(a2["les_boucles"]["le_grand_rectangle"]["la_fermeture_en_voxels"] - 40.0) < 1e-9
          and abs(a2["les_boucles"]["haut_gauche"]["la_fermeture_en_voxels"]) < 1e-9))
    v("★★★★ et au-delà du demi-feuillet, le verdict nomme les deux boucles qui dépassent",
      _ok(lambda: a2["le_verdict"]["les_boucles_qui_depassent"] == ["haut_droite", "le_grand_rectangle"]
          and not a2["les_boucles"]["haut_droite"]["sous_le_demi_pli"]
          and "DIFFÉRENTES" in a2["le_verdict"]["ce_qui_reste_a_mesurer"]))
    p3 = {k: {l_: dict(s) for l_, s in x.items()} for k, x in pas.items()}
    for l_ in p3[("rangees", 5)]:
        p3[("rangees", 5)][l_][2] += 4.0
    a3 = _sur(analyser, p3, R, C, 3, 199, 10, False)
    v("★★★★ un pas sur la croix centrale ouvre les deux boucles qui la partagent, en sens contraires",
      _ok(lambda: abs(a3["les_boucles"]["haut_gauche"]["la_fermeture_en_voxels"] + 4.0) < 1e-9
          and abs(a3["les_boucles"]["bas_gauche"]["la_fermeture_en_voxels"] - 4.0) < 1e-9
          and abs(a3["les_boucles"]["le_grand_rectangle"]["la_fermeture_en_voxels"]) < 1e-9))
    hn = np.random.default_rng(4)
    pb = {k: {l_: {s: v_ + float(hn.normal(0.0, 3.0)) for s, v_ in d.items()} for l_, d in x.items()}
          for k, x in pas.items()}
    ab = _sur(analyser, pb, R, C, 3, 199, 10, False)
    v("★★★★ le grand rectangle est la somme des quatre, sur une matière bruitée",
      _ok(lambda: abs(sum(ab["les_boucles"][n]["la_fermeture_en_voxels"] for n in
                          ("haut_gauche", "haut_droite", "bas_gauche", "bas_droite"))
                      - ab["les_boucles"]["le_grand_rectangle"]["la_fermeture_en_voxels"]) < 1e-3))
    p4 = {k: {l_: dict(s) for l_, s in x.items()} for k, x in pas.items()}
    for l_ in (6, 7, 8):
        p4[("rangees", 8)][l_].pop(5)
    a4 = _sur(analyser, p4, R, C, 3, 199, 10, False)
    v("★★★★ une couture sans majorité ouvre sa boucle et le grand rectangle, et elle est nommée",
      _ok(lambda: a4["le_verdict"]["les_boucles_ouvertes"] == ["bas_droite", "le_grand_rectangle"]
          and a4["les_boucles"]["bas_droite"]["les_coutures_manquantes"] == {"bas": [5]}
          and a4["la_couverture_du_consensus"]["rangees_8"]["les_coutures_sans_consensus"] == [5]
          and a4["lepreuve"]["les_rectangles"] == ["bas_gauche", "haut_droite", "haut_gauche"]))
    p5 = {k: {l_: dict(s) for l_, s in x.items()} for k, x in pas.items()}
    p5[("rangees", 2)][0].pop(3)
    for s in range(1, 4):
        p5[("rangees", 2)][1][s] += 100.0
    a5 = _sur(analyser, p5, R, C, 3, 199, 10, False)

    def _une_ligne():  # noqa: E306
        u = a5["les_boucles"]["haut_gauche"]["les_boucles_dune_ligne"]
        return (u["les_lignes_qui_couvrent"]["haut"] == [1, 2, 3, 4] and u["combien"] == 4 * 5 * 5 * 5
                and u["combien_sous_le_demi_pli"] == 3 * 5 * 5 * 5
                and abs(a5["les_boucles"]["haut_gauche"]["la_fermeture_en_voxels"]) < 1e-9)
    v("★★★★ le contrôle d'une ligne ne prend que les lignes sans trou, et la médiane ignore l'écart",
      _ok(_une_ligne), str(a5.get("les_boucles", {}).get("haut_gauche", {}).get("les_boucles_dune_ligne", {})
                           .get("les_lignes_qui_couvrent")))
    v("★★★ le contrôle nommé est la moyenne des lignes, et elle ne l'ignore pas",
      _ok(lambda: abs(a5["les_boucles"]["haut_gauche"]["la_fermeture_de_la_moyenne_en_voxels"]
                      - (100.0 / 5 + 100.0 / 5 + 100.0 / 4)) < 1e-6))
    p6 = {k: {l_: {s: x for s, x in d.items() if not (k == ("colonnes", 4) and s == 4)}
              for l_, d in x_.items()} for k, x_ in pas.items()}
    for l_ in p6[("rangees", 8)]:
        p6[("rangees", 8)][l_].pop(2)
    for l_ in p6[("colonnes", 1)]:
        p6[("colonnes", 1)][l_].pop(3)
    for l_ in p6[("colonnes", 7)]:
        p6[("colonnes", 7)][l_].pop(6)
    a6 = _sur(analyser, p6, R, C, 3, 19, 2, False)
    v("★★★ sans aucune boucle fermable, l'analyse est indécidable par sa raison",
      not a6.get("decidable") and "aucune boucle" in str(a6.get("raison")), str(a6.get("raison")))
    v("★★ six bandes et pas une de moins", not _sur(analyser, {k: x for k, x in pas.items()
                                                              if k != ("colonnes", 7)},
                                                   R, C, 3, 19, 2, False).get("decidable"))

    # ── le nul et l'épreuve
    s0 = les_sommes_par_blocs([2.0] * 30, 50, 1)
    v("★★★ une marche de pas constants, centrée, ne va nulle part", bool(np.all(np.abs(s0) < 1e-9)))
    s1, s1b = les_sommes_par_blocs(np.arange(40.0), 300, 5), les_sommes_par_blocs(np.arange(40.0), 300, 5)
    v("★★★ les sommes par blocs se rejouent à la graine", bool(np.array_equal(s1, s1b)))
    serie = np.random.default_rng(2).normal(0.0, 1.0, 64)
    s2 = les_sommes_par_blocs(serie, 4000, 8)
    # ⚠ LA VARIANCE ATTENDUE EST CELLE QUE LES BLOCS DE LA SÉRIE DONNENT, pas celle d'une série sans
    # dépendance : un tirage par blocs garde la corrélation courte que l'échantillon montre, c'est son rôle.
    b_, c_ = la_longueur_de_bloc(64), serie - float(np.mean(serie))
    cs_ = np.concatenate(([0.0], np.cumsum(c_)))
    attendu = (64 // b_) * float(np.var(cs_[b_:] - cs_[:-b_]))
    v("★★★ la somme tirée a la variance que lui donnent les blocs de la série, blocs indépendants",
      abs(float(np.var(s2)) / attendu - 1.0) < 0.1, f"{float(np.var(s2)):.3f} contre {attendu:.3f}")
    s3 = les_sommes_par_blocs(serie, 20, 8, bloc=64)
    v("★★★ la longueur de bloc demandée est tenue : un bloc de toute la série rend sa somme centrée",
      la_longueur_de_bloc(64) == 4 and bool(np.all(np.abs(s3) < 1e-9)))
    grr = np.random.default_rng(6)
    pdc = {d: list(grr.normal(0.0, 1.0, d[3] - d[2])) for d in dc}
    rect = {n: c for n, c in decl.items() if n != "le_grand_rectangle"}
    e1 = _sur(lepreuve, pdc, rect, dc, 199, 3)
    obs1 = {d: float(np.sum(p_)) for d, p_ in pdc.items()}
    T1 = sum(float(la_fermeture(obs1, c, dc)) ** 2 for c in rect.values())
    v("★★★★ la statistique est Σ L² sur les quatre rectangles, sans le grand",
      _ok(lambda: abs(e1["la_statistique"] - round(T1, 4)) < 1e-6 and len(e1["les_rectangles"]) == 4))
    v("★★★ la valeur p compte les tirages au moins aussi fermés, plus un",
      _ok(lambda: e1["la_valeur_p"] == round((1 + e1["tirages_au_moins_aussi_fermes"]) / 200.0, 4)))
    nul = {d: np.asarray([1.0, 2.0]) * (i + 1) for i, d in enumerate(dc)}
    gr = la_fermeture(nul, decl["le_grand_rectangle"], dc)
    qu = sum(la_fermeture(nul, c, dc) for c in rect.values())
    v("★★★★ dans le nul aussi, les rectangles partagent leurs demi-côtés et le grand est leur somme",
      bool(np.allclose(gr, qu)))
    v("★★ sans rectangle fermable, pas d'épreuve", not _sur(lepreuve, pdc, {}, dc).get("decidable"))
    memes = {d: list(np.random.default_rng(1).normal(0.0, 1.0, d[3] - d[2])) for d in dc}
    e2 = _sur(lepreuve, memes, rect, dc, 199, 3)
    v("★★★★ chaque demi-côté du nul est tiré indépendamment : deux séries égales ne tirent pas pareil",
      _ok(lambda: e2["la_statistique"] == 0.0 and e2["la_statistique_mediane_du_nul"] > 1.0),
      str(e2.get("la_statistique_mediane_du_nul")))
    et = _sur(sur_letalon, {d: d[3] - d[2] for d in dc}, {d: 1.0 for d in dc}, rect, dc, 0.1, 40, 199, 7)
    v("★★★ l'étalon conclut « mieux » au plus au taux de sa garantie sur des demi-côtés indépendants",
      et.get("decidable") and et["le_taux"] <= et["la_borne"], str(et))
    et9 = _sur(sur_letalon, {d: d[3] - d[2] for d in dc}, {d: 1.0 for d in dc}, rect, dc, 0.9, 40, 199, 7)
    v("★★★★ et l'étalon voit une épreuve qui conclut trop : des pas qui se rendent à la couture suivante",
      et9.get("decidable") and not et9["elle_tient_sa_garantie"] and et9["le_taux"] > 0.5, str(et9))
    v("★★★ la borne de l'étalon est la garantie à deux écarts-types binomiaux",
      _ok(lambda: abs(et["la_borne"] - round(GARANTIE + 2 * np.sqrt(GARANTIE * (1 - GARANTIE) / 40), 4))
          < 1e-9))
    th = le_theta_dune_autocorrelation(lautocorrelation_commune([[1.0, -1.0, 1.0, -1.0], [2.0, 0.0, 2.0]]))
    v("★★★ l'autocorrélation commune est mise en commun sur des séries centrées chacune",
      _ok(lambda: abs(lautocorrelation_commune([[1.0, -1.0, 1.0, -1.0], [2.0, 0.0, 2.0]])
                      + 43.0 / 60.0) < 1e-9 and th > 0.0))
    at = _sur(analyser, pb, R, C, 3, 99, 6, True)

    def _theta():  # noqa: E306
        pdc_ = [[float(le_consensus(pb[(d[0], d[1])])[s]) for s in range(d[2], d[3])]
                for d in les_demi_cotes(R, C)]
        return abs(at["letalon_de_lepreuve"]["le_theta"]
                   - round(le_theta_dune_autocorrelation(lautocorrelation_commune(pdc_)), 4)) < 1e-9
    v("★★★★ l'étalon est tiré au θ DÉRIVÉ de l'autocorrélation des demi-côtés lus", _ok(_theta))

    # ── les issues
    iss = {_ce_qui_reste(d, m_) for d in (True, False) for m_ in (True, False, None)}
    v("★★★★ quatre issues distinctes, et dépasser le demi-feuillet prime",
      len(iss) == 4 and _ce_qui_reste(True, None) == _ce_qui_reste(True, False) == _ce_qui_reste(True, True))
    j = juger({"a": {"fermable": True, "sous_le_demi_pli": True, "la_fermeture_en_voxels": 3.0},
               "b": {"fermable": False}}, {"decidable": True, "mieux_que_des_marches_independantes": True},
              {"elle_tient_sa_garantie": False})
    v("★★★★ une épreuve dont l'étalon ne tient pas ne tranche pas, et une boucle ouverte est comptée",
      j["mieux_que_des_marches_independantes"] is None and j["les_boucles_ouvertes"] == ["b"]
      and "NE TRANCHE PAS" in j["ce_qui_reste_a_mesurer"])
    j2 = juger({"a": {"fermable": True, "sous_le_demi_pli": False, "la_fermeture_en_voxels": -40.0}},
               {"decidable": True, "mieux_que_des_marches_independantes": True},
               {"elle_tient_sa_garantie": True})
    v("★★★ une fermeture au-delà du demi-feuillet nomme sa boucle",
      j2["les_boucles_qui_depassent"] == ["a"] and "DIFFÉRENTES" in j2["ce_qui_reste_a_mesurer"]
      and j2["la_plus_grande_fermeture_en_valeur_absolue"] == 40.0)

    # ── ce qui est relu
    par = ce_que_223_a_rendu()
    v("★★★ `223` est relu, avec sa grille et ses cinq colonnes",
      par.get("decidable") and par["la_grille"] == [396, 285] and par["les_colonnes"] == [140, 141, 142, 143, 144])

    for e_ in echecs:
        print(f"  ÉCHEC {e_}")
    print(f"{Path(__file__).name}   "
          f"{'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--lire", type=Path, default=None,
                   help="lit les quatre bandes et écrit la lecture seule, bande par bande — et reprend")
    p.add_argument("--depuis", type=Path, default=None,
                   help="rejoue l'analyse depuis une lecture, sans relire le volume")
    p.add_argument("--json", type=Path, default=None)
    p.add_argument("--graine", type=int, default=GRAINE)
    p.add_argument("--tirages", type=int, default=TIRAGES)
    p.add_argument("--replicats", type=int, default=REPLICATS)
    p.add_argument("--sans-etalon", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if a.lire:
        par219, par223 = ce_que_219_a_rendu(), ce_que_223_a_rendu()
        if not (par219.get("decidable") and par223.get("decidable")):
            print(f"indécidable : {par219.get('raison') or par223.get('raison')}")
            return 1
        gy, gx = par223["la_grille"]
        bandes = les_bandes_a_lire(gy, gx, len(par219["les_rangees"]))
        deja = (json.loads(a.lire.read_text()).get("les_bandes") or {}) if a.lire.exists() else {}
        a.lire.parent.mkdir(parents=True, exist_ok=True)

        def ecrire(d):  # noqa: E306
            a.lire.write_text(json.dumps({"les_bandes": d}, ensure_ascii=False, indent=1))
            print(f"écrit : {a.lire} ({len(d)} bandes)", flush=True)
        lu = lire_les_bandes(bandes, deja, ecrire)
        if not lu.get("decidable"):
            print(f"indécidable : {lu.get('raison')}")
            return 1
        return 0
    r = mesurer(a.depuis, DELAI, a.graine, a.tirages, a.replicats, avec_etalon=not a.sans_etalon)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=2))
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
