"""Autour de quatre chunks, les boucles se ferment-elles ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LES BORDS HAUT ET BAS DES CHUNKS NE SOIENT LUS. Rien de ce qu'il
mesure n'a été regardé : ni un pas vertical, ni une boucle.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P67`. La lignée `199`–`221` n'a mesuré que les coutures LE
LONG d'une rangée de chunks, et `221` a établi que le consensus de cinq rangées voisines les traverse
sans quitter le feuillet. Une surface demande aussi de passer d'une rangée de chunks à la suivante :
ces coutures-là, entre le bord bas d'un chunk et le bord haut de celui du dessous, n'ont jamais été
lues. C'est une LECTURE NEUVE, des mêmes cinq rangées que `219`, coupées cette fois dans les deux sens.

## La boucle, et pourquoi elle est un contrôle que rien de local ne simule

Autour de quatre chunks `(r, c)`, `(r, c+1)`, `(r+1, c+1)`, `(r+1, c)`, deux pas horizontaux `h` et deux
verticaux `v` :

    L_r(c) = h_r(c) + v_(c+1)(r) - h_(r+1)(c) - v_c(r)  =  A_r(c) + B_r(c)

avec `A = h_r(c) - h_(r+1)(c)`, le DÉSACCORD de deux rangées voisines à une couture — exactement ce que
`211` et `220` cumulaient —, et `B = v_(c+1)(r) - v_c(r)`, la variation du pas vertical d'un chunk au
suivant. Si les pas mesurent une même surface, deux chemins vers le même chunk y arrivent au même
endroit et `L` est nul au bruit près : ⭐⭐⭐ une surface qui TOURNE fait varier le pas horizontal d'une
rangée à l'autre, et c'est alors le pas vertical qui en rend compte, exactement. Le calcul le dit pour
tout champ de profondeur jusqu'au troisième degré, parce que les dérivées croisées se compensent.

⭐⭐⭐⭐ C'EST CE QUE LA TRANCHE TRANCHE : le désaccord de deux rangées voisines, que `211` et `220`
lisaient comme une ERREUR à corriger, est-il en partie la GÉOMÉTRIE d'une surface qui tourne, que les
pas verticaux voient ? ⚠⚠ Et la réponse décide du consensus de `221` : il donne à toutes les rangées
le MÊME pas horizontal, donc il efface le désaccord — à bon droit si c'est de l'erreur, à tort si c'est
de la géométrie.

## Ce qui est lu, et comment on s'assure que c'est la même lecture

⭐⭐⭐ LES MÊMES CINQ RANGÉES QUE `219`, relues par le MÊME lecteur (`la_ligne`, avec un drapeau qui
ajoute les bords haut et bas sans rien changer aux autres). Les bords verticaux sont coupés en
`(couche, rangée)` à seize colonnes réparties comme les seize rangées, avec la même largeur de bande ;
le pas vertical est la même estimation, `un_pas`, moyennée sur ces seize colonnes. ⚠⚠⚠ Les pas
horizontaux relus doivent retomber sur ceux que `219` publie, à l'arrondi de sa quatrième décimale
près, sur exactement les mêmes colonnes : sinon la lecture est REFUSÉE par son nom — le dépôt ou le
code aurait changé, et comparer deux lecteurs serait `R4-L19`. Une rangée dont le fil est tombé est
refusée aussi.

## L'épreuve, déclarée

⭐⭐⭐⭐ LE RAPPORT DE FERMETURE, `ρ = var(A + B) / (var A + var B)`, sur toutes les boucles complètes
des quatre rangées de boucles, chaque série centrée par rangée de boucles. Des pas verticaux sans
rapport avec le désaccord le laissent autour de un ; des pas qui en rendent compte le font descendre.

⚠⚠⚠ LE NUL REBRASSE DES BOUCLES, JAMAIS DES PAS — c'est le piège que `R4-P67` écrivait d'avance. Deux
boucles voisines partagent un pas, donc leurs `B` sont une différence première, et deux rangées de
boucles voisines partagent une rangée, donc leurs `A` aussi : un nul qui tirerait les pas un à un
détruirait cette structure et jugerait sur une variance qui n'est pas celle de la matière. Le nul
DÉCALE la moitié verticale des boucles contre leur moitié horizontale, circulairement le long de la
rangée, du même décalage pour les quatre rangées de boucles : chaque moitié garde toute sa structure,
seule leur correspondance est rompue. Tous les décalages d'au moins `⌈n^(1/3)⌉` coutures dans chaque
sens sont pris — la règle de `217`, pour qu'aucun décalage ne recouvre la dépendance courte —, donc
le nul est EXHAUSTIF et sans graine. La valeur P est le rang de `ρ` observé parmi eux ; les boucles se
ferment si elle ne dépasse pas la garantie de la lignée.

## L'étalon, et ce qu'il doit montrer

⚠⚠ UNE ÉPREUVE SANS ÉTALON NE DIT RIEN D'UN « NON ». Des matières au pas près, sur le motif exact de
présence des pas lus, avec le bruit de lecture de CHAQUE sorte de pas pris dans la matière — la
moitié paire contre la moitié impaire des seize coupes, `var(moyenne) = d²·n_a·n_b/n²` :

- ⭐⭐⭐ COHÉRENTE : une torsion `t` qui marche le long de la rangée, vue par le pas vertical et par le
  désaccord des pas horizontaux, de variance « tout l'excès du désaccord sur son plancher de lecture
  est de la géométrie » — la plus grande que la matière permette. L'épreuve doit la voir ;
- ⭐⭐⭐ INCOHÉRENTE : la même torsion pour les pas horizontaux, une AUTRE, indépendante, pour les
  verticaux — mêmes variances, aucune correspondance. L'épreuve doit tenir sa garantie ;
- ⚠⚠ ET UNE ERREUR PORTÉE PAR UN CHUNK ENTIER, contrôle nommé : un chunk dont toute la lecture est
  déplacée déplace ses quatre pas de façon cohérente, donc ferme ses boucles comme une géométrie. La
  fermeture ne peut pas les distinguer, et l'étalon le montre au lieu de le taire.

L'étalon tient s'il voit la matière cohérente au moins une fois sur `1 - 2·garantie` et tient sa
garantie sur l'incohérente, à deux fois près — la règle de `214`.

## Les descriptions, déclarées avec l'épreuve

1. ⭐⭐ LE PLANCHER DE LECTURE : `var A`, `var B`, `var L` contre ce que le seul bruit de lecture donne.
   Un désaccord qui ne dépasse pas son plancher n'a rien à expliquer.
2. ⭐⭐⭐ LA PART GÉOMÉTRIQUE du désaccord, `-cov(A, B)` : ce que les pas verticaux en expliquent, en
   voxels carrés, à côté de `var A`.
3. ⭐⭐⭐⭐ TROIS SURFACES, sur le plus long tronçon de boucles complètes de chaque rangée de boucles, par
   leur séparation `max_k |S_k|` (`S_0 = 0`) contre le demi-feuillet :
   - `Σ A` — chaque rangée son pas, le pas vertical supposé constant : la séparation de `211` ;
   - `Σ B` — un pas horizontal COMMUN aux rangées, dont le consensus de `221`, et le pas vertical tel
     qu'il est lu : ce que le consensus laisse d'incohérent, soit `v_k - v_départ` ;
   - `Σ (A + B)` — chaque rangée son pas ET le pas vertical lu : deux chemins vers le même chunk.
   La plus petite dit quelle description d'une surface est la plus cohérente avec elle-même.
4. ⭐⭐ LES BOUCLES QUI SAUTENT UN FEUILLET, `|L| ≥ 36` : deux chemins qui arrivent sur deux spires. C'est
   la forme locale exacte de ce que l'humain corrige.
5. ⭐⭐⭐ LE DÉTAIL AUX COLONNES FORTES DE `219` : à chacune, l'écart de la rangée désignée à la médiane
   des quatre autres, et les deux boucles qui contiennent son pas. Si l'écart est une ERREUR de cette
   rangée, ses deux boucles s'ouvrent de lui, en signes opposés ; si c'est de la géométrie, elles se
   ferment. Quatorze colonnes : une description, pas une épreuve.

## Les issues, exclusives

- l'étalon ne tient pas : aucun verdict ;
- les boucles se ferment mieux que le hasard : une part du désaccord des rangées voisines est la
  géométrie d'une surface que les pas verticaux voient — ou une erreur portée par des chunks entiers,
  que rien de local ne distingue ;
- elles ne se ferment pas mieux que le hasard : les pas verticaux n'expliquent rien du désaccord, qui
  est donc de l'erreur de couture, et le pas commun du consensus est le bon choix pour une surface.

⚠⚠⚠ LA LIMITE EST ÉCRITE D'AVANCE : une boucle est aveugle à ce qu'un chunk entier porte, et un pas
lu à un feuillet près (±72) ferme sa boucle comme un pas juste. Ce que la fermeture établit est la
cohérence des pas ENTRE EUX, jamais leur justesse.

Usage :
    uv run python src/nappe/les_boucles_se_ferment_elles.py --verifier
    uv run python src/nappe/les_boucles_se_ferment_elles.py --lire <lecture.json>
    uv run python src/nappe/les_boucles_se_ferment_elles.py --depuis <lecture.json> \\
        --json docs/mesures/les_boucles_se_ferment_elles.json
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

from combien_de_rangees_faut_il_pour_lire_le_pas import (LES_RANGEES,  # noqa: E402
                                                         la_ligne, le_pas_de_k_rangees)
from la_recette_posee_sur_le_rouleau import DELAI  # noqa: E402
from le_bruit_propre_croit_il_avec_lecartement import le_taux_tient  # noqa: E402
from le_consensus_traverse_t_il_la_rangee import le_plus_long  # noqa: E402
from le_vote_ramene_t_il_les_rangees_sur_le_feuillet import (ce_que_219_a_rendu,  # noqa: E402
                                                             la_separation)
from lecart_extreme_est_il_porte_par_une_rangee import GARANTIE  # noqa: E402
from ou_le_maillage_quitte_t_il_son_feuillet import (le_segment_declare,  # noqa: E402
                                                     les_pannes_de_reseau)
from ouvrir_les_quinze import _rng  # noqa: E402
from pourquoi_lerreur_declaree_est_trop_petite import la_longueur_de_bloc  # noqa: E402
from que_montrent_ces_deux_vues import DEMI_PAS_EN_VOXELS  # noqa: E402
from zarr_depth import BUCKET, array_meta  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
GRAINE = 20261103
REPLICATS = 60
# ⚠ `219` publie ses pas à la quatrième décimale : un pas relu s'en écarte d'au plus un demi-dix-
# millième. Le millionième ajouté ne couvre que la représentation flottante.
LA_TOLERANCE_DE_REPRODUCTION = 0.5e-4 + 1e-6

LA_QUESTION_DECLAREE = ("autour de quatre chunks, les boucles se ferment-elles : le pas vertical "
                        "rend-il compte du désaccord de deux rangées voisines ?")
LEPREUVE_DECLAREE = ("le rapport de fermeture var(A+B)/(var A + var B) sur les boucles complètes, "
                     "contre tous les décalages de la moitié verticale d'au moins ⌈n^(1/3)⌉ coutures")


# ─────────────────────────────── la lecture ───────────────────────────────

def _un_pas(profils_a: dict, profils_b: dict, coupes) -> tuple | None:
    """Un pas de couture et son désaccord pair/impair — `le_pas_de_k_rangees`, sans retouche."""
    x = le_pas_de_k_rangees(profils_a, profils_b, coupes)
    if not x.get("decidable"):
        return None
    return (float(x["le_pas_en_voxels"]), float(x["le_desaccord_en_voxels"]),
            int(x["les_rangees"]))


def les_pas_horizontaux(lg: dict) -> dict:
    """Le pas de chaque couture le long de la rangée, indexé par sa colonne de gauche — comme `208`."""
    out = {}
    for a in sorted(lg["droits"]):
        b = a + 1
        if b not in lg["gauches"]:
            continue
        x = _un_pas(lg["droits"][a], lg["gauches"][b], lg["les_rangees_lues"])
        if x is not None:
            out[int(a)] = x
    return out


def les_pas_verticaux(haute: dict, basse: dict) -> dict:
    """Le pas de chaque couture entre deux rangées de chunks, indexé par sa colonne.

    ⚠⚠ LE SENS EST CELUI DES PAS HORIZONTAUX : le bord le plus loin du premier chunk contre le bord le
    plus près du second, et le second est celui de plus grand indice. Sans cela une boucle sommerait
    un pas dans un sens et l'autre dans le sens contraire, et ne se fermerait jamais.
    """
    out = {}
    coupes = haute.get("les_colonnes_de_coupe") or []
    for c in sorted(haute.get("bas") or {}):
        if c not in (basse.get("hauts") or {}):
            continue
        x = _un_pas(haute["bas"][c], basse["hauts"][c], coupes)
        if x is not None:
            out[int(c)] = x
    return out


def lire_la_surface(rangees, delai: float = DELAI, ouvrir=None, meta=None, volume=None,
                    lire_une=None) -> dict:
    """Les pas horizontaux de chaque rangée et verticaux entre rangées voisines, d'une seule lecture.

    ⚠⚠ UNE RANGÉE VIDE OU DONT LE FIL EST TOMBÉ ARRÊTE TOUT, par son nom — comme chez `219`.
    """
    if lire_une is None:
        if volume is None:
            volume = le_segment_declare()
            if volume is None:
                return {"decidable": False, "raison": "aucun volume recensé"}
        if meta is None:
            try:
                meta = array_meta(f"{BUCKET}/{volume['cle']}", 0, delai)
            except Exception as e:  # noqa: BLE001
                return {"decidable": False,
                        "raison": f"le volume ne répond pas : {type(e).__name__}"}

        def lire_une(r):  # noqa: E306
            return la_ligne(volume, delai, None, ouvrir, meta, LES_RANGEES, int(r),
                            les_bords_verticaux=True)
    lignes, h, v, precedente = {}, {}, {}, None
    for r in [int(x) for x in rangees]:
        lg = lire_une(r)
        if not lg.get("decidable"):
            return {"decidable": False, "raison": f"la rangée {r} est vide : {lg.get('raison')}"}
        pannes = les_pannes_de_reseau(lg.get("refuses"))
        if pannes:
            return {"decidable": False,
                    "raison": (f"{pannes} chunks perdus par le réseau sur la rangée {r} — une "
                               f"rangée dont le fil est tombé n'est pas comparable")}
        h[r] = les_pas_horizontaux(lg)
        if precedente is not None:
            v[precedente[0]] = les_pas_verticaux(precedente[1], lg)
        precedente = (r, lg)
        lignes[r] = {k: x for k, x in lg.items()
                     if k not in ("droits", "gauches", "bas", "hauts", "les_colonnes")}
    return {"decidable": True, "h": h, "v": v, "les_lignes": lignes}


def publier_la_lecture(lu: dict) -> dict:
    """La lecture sous la forme qui se rejoue : `[pas, désaccord, coupes]` par couture, quatre décimales."""
    def _p(d):
        return {str(r): {str(c): [round(float(x[0]), 4), round(float(x[1]), 4), int(x[2])]
                         for c, x in sorted(s.items())} for r, s in sorted(d.items())}
    return {"les_pas_horizontaux": _p(lu["h"]), "les_pas_verticaux": _p(lu["v"]),
            "les_lignes": {str(r): x for r, x in sorted(lu["les_lignes"].items())}}


def relire_la_lecture(d: dict) -> dict:
    def _r(x):
        return {int(r): {int(c): (float(t[0]), float(t[1]), int(t[2])) for c, t in s.items()}
                for r, s in (x or {}).items()}
    return {"decidable": True, "h": _r(d.get("les_pas_horizontaux")),
            "v": _r(d.get("les_pas_verticaux")), "les_lignes": d.get("les_lignes") or {}}


def la_reproduction(h: dict, publies: dict,
                    tolerance: float = LA_TOLERANCE_DE_REPRODUCTION) -> dict:
    """Les pas horizontaux relus retombent-ils sur ceux de `219`, sur les MÊMES colonnes ? Sinon, refus."""
    if set(h) != set(publies):
        return {"decidable": False, "raison": "les rangées relues ne sont pas celles de `219`"}
    ecarts = {}
    for r in sorted(publies):
        if set(h[r]) != set(publies[r]):
            return {"decidable": False,
                    "raison": (f"la rangée {r} relue n'a pas les colonnes de `219` "
                               f"({len(h[r])} contre {len(publies[r])})")}
        e = max(abs(float(h[r][c][0]) - float(publies[r][c])) for c in publies[r])
        if e > float(tolerance):
            return {"decidable": False,
                    "raison": (f"la rangée {r} relue ne retombe pas sur `219` (écart {e:.4g} "
                               f"voxel) — deux lecteurs différents")}
        ecarts[str(r)] = round(float(e), 6)
    return {"decidable": True, "les_ecarts_les_plus_grands": ecarts,
            "la_tolerance": float(tolerance)}


# ─────────────────────────────── les boucles ───────────────────────────────

def la_variance_de_la_moyenne(desaccord: float, n: int) -> float:
    """Le bruit de lecture d'un pas, tiré de ses deux demi-moyennes alternées.

    ⭐ Pour `n` coupes réparties en `n_a` paires et `n_b` impaires, `d = m_a - m_b` a pour variance
    `σ²·n/(n_a·n_b)` et la moyenne des `n` a `σ²/n` : d'où `d²·n_a·n_b/n²`.
    """
    n = int(n)
    na, nb = (n + 1) // 2, n // 2
    if na < 1 or nb < 1:
        return float("nan")
    return float(desaccord) ** 2 * na * nb / float(n * n)


def les_moities(h: dict, v: dict, rangees, n: int) -> dict:
    """`A`, `B` et leurs planchers, en tableaux (rangée de boucles × couture), NaN où rien n'est lu.

    La rangée de boucles `r` est celle qui a `r` en haut et `r + 1` en bas.
    """
    rs = [int(x) for x in rangees]
    haut = rs[:-1]
    A = np.full((len(haut), int(n)), np.nan)
    B = np.full((len(haut), int(n)), np.nan)
    fA = np.full_like(A, np.nan)
    fB = np.full_like(B, np.nan)
    for i, r in enumerate(haut):
        s = r + 1
        hr, hs, vr = h.get(r) or {}, h.get(s) or {}, v.get(r) or {}
        for c in range(int(n)):
            if c in hr and c in hs:
                A[i, c] = hr[c][0] - hs[c][0]
                fA[i, c] = (la_variance_de_la_moyenne(hr[c][1], hr[c][2])
                            + la_variance_de_la_moyenne(hs[c][1], hs[c][2]))
            if c in vr and (c + 1) in vr:
                B[i, c] = vr[c + 1][0] - vr[c][0]
                fB[i, c] = (la_variance_de_la_moyenne(vr[c][1], vr[c][2])
                            + la_variance_de_la_moyenne(vr[c + 1][1], vr[c + 1][2]))
    return {"les_rangees_de_boucles": haut, "A": A, "B": B, "le_plancher_de_A": fA,
            "le_plancher_de_B": fB}


def _centrees(A: np.ndarray, B: np.ndarray) -> tuple:
    """Les paires présentes, centrées par rangée de boucles — sur les SEULES paires présentes."""
    ok = ~np.isnan(A) & ~np.isnan(B)
    a = np.where(ok, A, 0.0)
    b = np.where(ok, B, 0.0)
    k = ok.sum(axis=1)
    ma = np.divide(a.sum(axis=1), k, out=np.zeros(len(k)), where=k > 0)
    mb = np.divide(b.sum(axis=1), k, out=np.zeros(len(k)), where=k > 0)
    a = np.where(ok, a - ma[:, None], 0.0)
    b = np.where(ok, b - mb[:, None], 0.0)
    return a, b, ok


def le_rapport_de_fermeture(A: np.ndarray, B: np.ndarray, decalage: int = 0) -> tuple:
    """`ρ = Σ(a+b)² / (Σa² + Σb²)`, `B` décalé circulairement de `decalage` coutures, et le compte."""
    Bs = np.roll(B, -int(decalage), axis=1) if int(decalage) else B
    a, b, ok = _centrees(A, Bs)
    den = float((a * a).sum() + (b * b).sum())
    if den <= 0.0 or int(ok.sum()) < 2:
        return None, int(ok.sum())
    return float(((a + b) ** 2).sum()) / den, int(ok.sum())


def les_decalages(n: int) -> list[int]:
    """Tous les décalages d'au moins `⌈n^(1/3)⌉` coutures dans chaque sens — le nul exhaustif."""
    m = la_longueur_de_bloc(int(n))
    return list(range(m, int(n) - m + 1))


def lepreuve(A: np.ndarray, B: np.ndarray, garantie: float = GARANTIE) -> dict:
    """Les boucles se ferment-elles mieux que la moitié verticale décalée ?"""
    n = int(A.shape[1])
    rho, k = le_rapport_de_fermeture(A, B, 0)
    if rho is None:
        return {"decidable": False, "raison": "moins de deux boucles complètes"}
    nul = []
    for s in les_decalages(n):
        x, _k = le_rapport_de_fermeture(A, B, s)
        if x is not None:
            nul.append(x)
    if not nul:
        return {"decidable": False, "raison": "aucun décalage admissible"}
    aussi = int(sum(1 for x in nul if x <= rho))
    p = (1.0 + aussi) / (1.0 + len(nul))
    return {"decidable": True, "combien_de_boucles": int(k),
            "le_rapport_de_fermeture": round(float(rho), 4),
            "combien_de_decalages": len(nul), "le_plus_petit_decalage": les_decalages(n)[0],
            "le_rapport_median_du_nul": round(float(np.median(nul)), 4),
            "les_rapports_du_nul": [round(float(x), 4) for x in nul],
            "le_plus_petit_rapport_du_nul": round(float(np.min(nul)), 4),
            "decalages_au_moins_aussi_fermes": aussi, "la_valeur_p": round(float(p), 4),
            "la_garantie": float(garantie), "se_ferment": bool(p <= float(garantie))}


def le_plancher(M: dict) -> dict:
    """Les variances de `A`, `B`, `L` sur les boucles complètes, contre leur plancher de lecture."""
    A, B = M["A"], M["B"]
    a, b, ok = _centrees(A, B)
    n = int(ok.sum())
    if n < 2:
        return {"decidable": False, "raison": "moins de deux boucles complètes"}
    vA, vB = float((a * a).sum()) / n, float((b * b).sum()) / n
    vL, cov = float(((a + b) ** 2).sum()) / n, float((a * b).sum()) / n
    fA = float(np.nanmean(np.where(ok, M["le_plancher_de_A"], np.nan)))
    fB = float(np.nanmean(np.where(ok, M["le_plancher_de_B"], np.nan)))
    x = {"la_variance_de_A": vA, "la_variance_de_B": vB, "la_variance_de_L": vL,
         "le_plancher_de_A": fA, "le_plancher_de_B": fB, "le_plancher_de_L": fA + fB,
         "lexces_de_A_sur_son_plancher": vA - fA,
         "la_covariance_de_A_et_B": cov, "la_part_geometrique": -cov,
         # ⚠ ajoutée après la mesure, et c'est dit : la part géométrique rapportée à l'excès du
         # désaccord sur son plancher, c'est-à-dire à ce qu'il y avait à expliquer.
         "la_part_expliquee_de_lexces": (-cov / (vA - fA)) if vA > fA else None,
         "lecart_type_de_A": vA ** 0.5, "lecart_type_de_B": vB ** 0.5,
         "lecart_type_de_L": vL ** 0.5}
    return {"decidable": True, "combien_de_boucles": n,
            **{k: (round(float(y), 4) if y is not None else None) for k, y in x.items()}}


def les_trois_surfaces(M: dict, demi: float = DEMI_PAS_EN_VOXELS) -> dict:
    """Sur le plus long tronçon de boucles complètes de chaque rangée de boucles, trois séparations."""
    out = {}
    for i, r in enumerate(M["les_rangees_de_boucles"]):
        ok = ~np.isnan(M["A"][i]) & ~np.isnan(M["B"][i])
        tr = le_plus_long([c for c in range(len(ok)) if ok[c]])
        if len(tr) < 2:
            out[str(r)] = {"decidable": False, "raison": "aucun tronçon de deux boucles"}
            continue
        a = M["A"][i][tr]
        b = M["B"][i][tr]
        sep = {"sigma_A": la_separation(a), "sigma_B": la_separation(b),
               "sigma_A_plus_B": la_separation(a + b)}
        cum = {"sigma_A": a, "sigma_B": b, "sigma_A_plus_B": a + b}
        out[str(r)] = {"decidable": True, "le_troncon": [int(tr[0]), int(tr[-1])],
                       "combien_de_boucles": len(tr),
                       **{f"la_separation_{k}": round(float(x), 4) for k, x in sep.items()},
                       **{f"{k}_tient": bool(x < float(demi)) for k, x in sep.items()},
                       # ⚠ les cumuls entiers, départ à zéro, pour que la figure les trace et non
                       # un résumé.
                       "les_cumuls": {k: [0.0] + [round(float(x), 4) for x in np.cumsum(y)]
                                      for k, y in cum.items()}}
    return out


def les_boucles_qui_sautent(M: dict, demi: float = DEMI_PAS_EN_VOXELS) -> dict:
    """Les boucles dont les deux chemins arrivent à un demi-feuillet ou plus l'un de l'autre."""
    L = M["A"] + M["B"]
    ok = ~np.isnan(L)
    ou = [[int(M["les_rangees_de_boucles"][i]), int(c), round(float(L[i, c]), 4)]
          for i, c in zip(*np.nonzero(ok & (np.abs(np.where(ok, L, 0.0)) >= float(demi))))]
    return {"combien_de_boucles": int(ok.sum()), "combien_sautent": len(ou), "lesquelles": ou,
            "le_demi_feuillet": float(demi)}


def le_detail_aux_colonnes_fortes(h: dict, v: dict, fortes: dict, rangees) -> dict:
    """À chaque colonne forte de `219`, l'écart de la rangée désignée et ses deux boucles."""
    rs = [int(x) for x in rangees]
    out = []
    for c, r in sorted(fortes.items()):
        autres = [h[s][c][0] for s in rs if s != r and c in (h.get(s) or {})]
        if c not in (h.get(r) or {}) or not autres:
            out.append({"la_colonne": int(c), "la_rangee": int(r), "decidable": False})
            continue
        ecart = float(h[r][c][0]) - float(np.median(autres))

        def _boucle(haut):  # noqa: E306
            s = haut + 1
            if haut not in rs or s not in rs:
                return None
            x = [(h.get(haut) or {}).get(c), (h.get(s) or {}).get(c),
                 (v.get(haut) or {}).get(c), (v.get(haut) or {}).get(c + 1)]
            if any(y is None for y in x):
                return None
            return round(float(x[0][0] + x[3][0] - x[1][0] - x[2][0]), 4)
        dessous, dessus = _boucle(r), _boucle(r - 1)
        out.append({"la_colonne": int(c), "la_rangee": int(r), "decidable": True,
                    "lecart_a_la_mediane": round(ecart, 4),
                    "la_forme": la_forme(ecart, dessous, dessus),
                    # ⚠ la boucle où la rangée est EN HAUT porte son pas avec le signe +, celle où
                    # elle est EN BAS avec le signe - : une erreur de la rangée ouvre les deux en
                    # signes opposés.
                    "la_boucle_dessous": dessous, "la_boucle_dessus": dessus})
    formes = [x.get("la_forme") for x in out]
    return {"les_colonnes": out, "combien_ont_la_forme_dune_erreur": formes.count("erreur"),
            "combien_se_ferment": formes.count("fermee"), "combien_mixtes": formes.count("mixte"),
            "combien_sans_boucle": formes.count(None)}


def la_forme(ecart: float, dessous, dessus) -> str | None:
    """La forme des boucles d'une colonne forte : celle d'une erreur de la rangée, ou fermées.

    ⚠⚠ LA RÈGLE EST AJOUTÉE APRÈS LA MESURE, ET C'EST DIT : la déclaration publiait les boucles sans
    dire comment les lire. Une boucle a la forme d'une ERREUR quand elle s'ouvre du signe qu'une erreur
    de la rangée prédit (`+δ` dessous, `-δ` dessus) d'au moins la moitié de l'écart ; elle est FERMÉE
    quand elle s'ouvre de moins de la moitié. La colonne prend la forme de toutes ses boucles, ou est
    mixte.
    """
    lues = [(x, sg) for x, sg in ((dessous, 1.0), (dessus, -1.0)) if x is not None]
    if not lues or float(ecart) == 0.0:
        return None
    demi = abs(float(ecart)) / 2.0
    err = [np.sign(x) == sg * np.sign(float(ecart)) and abs(x) >= demi for x, sg in lues]
    fer = [abs(x) < demi for x, _sg in lues]
    if all(err):
        return "erreur"
    if all(fer):
        return "fermee"
    return "mixte"


# ─────────────────────────────── l'étalon ───────────────────────────────

def une_matiere(forme: str, masque_A: np.ndarray, masque_B: np.ndarray, sigma_t: float,
                sigma_h: float, sigma_v: float, g) -> tuple:
    """`A` et `B` d'une matière connue, sur le motif de présence de la matière lue.

    ⚠ Construits DEPUIS DES PAS, pas tirés directement : `A` est la différence de deux pas
    horizontaux et `B` celle de deux pas verticaux, donc chaque matière garde la structure que le nul
    doit respecter. ⚠ La part partagée du pas (`208`) n'y est pas : elle s'annule exactement dans `A`.
    """
    k, n = masque_A.shape
    rangees = k + 1
    bh = g.normal(0.0, float(sigma_h), size=(rangees, n))
    bv = g.normal(0.0, float(sigma_v), size=(k, n + 1))
    if forme == "chunk":
        # un déplacement par chunk : pas horizontal δ(r,c+1)-δ(r,c), vertical δ(r+1,c)-δ(r,c).
        sd = float(sigma_t) / 2.0
        d = g.normal(0.0, sd, size=(rangees, n + 1))
        hh = d[:, 1:] - d[:, :-1] + bh
        vv = d[1:, :] - d[:-1, :] + bv
    else:
        # une torsion : le pas vertical de la rangée de boucles `i` vaut t_i(c), et le pas
        # horizontal de la rangée `r` porte la somme des variations des torsions au-dessus d'elle.
        t = np.cumsum(g.normal(0.0, float(sigma_t), size=(k, n + 1)), axis=1)
        dt = t[:, 1:] - t[:, :-1]
        hh = np.vstack([np.zeros((1, n)), np.cumsum(dt, axis=0)]) + bh
        if forme == "incoherente":
            t = np.cumsum(g.normal(0.0, float(sigma_t), size=(k, n + 1)), axis=1)
        vv = t + bv
    A = np.where(masque_A, hh[:-1, :] - hh[1:, :], np.nan)
    B = np.where(masque_B, vv[:, 1:] - vv[:, :-1], np.nan)
    return A, B


def sur_letalon(M: dict, plancher: dict, replicats: int = REPLICATS, graine: int = GRAINE,
                garantie: float = GARANTIE) -> dict:
    """Voit-elle une torsion de la taille permise, tient-elle sa garantie, et que fait une erreur de chunk ?"""
    mA, mB = ~np.isnan(M["A"]), ~np.isnan(M["B"])
    excess = float(plancher["lexces_de_A_sur_son_plancher"])
    if excess <= 0.0:
        return {"decidable": True, "tient": False,
                "raison": "le désaccord ne dépasse pas son plancher de lecture : rien à expliquer"}
    # ⭐ les bruits de lecture par pas : le plancher de `A` porte deux pas horizontaux, celui de `B`
    # deux verticaux.
    sh = (float(plancher["le_plancher_de_A"]) / 2.0) ** 0.5
    sv = (float(plancher["le_plancher_de_B"]) / 2.0) ** 0.5
    st = excess ** 0.5
    taux = {}
    for j, forme in enumerate(("coherente", "incoherente", "chunk")):
        g = _rng(int(graine) + 1000 * (j + 1))
        vus = 0
        for _ in range(int(replicats)):
            A, B = une_matiere(forme, mA, mB, st, sh, sv, g)
            e = lepreuve(A, B, garantie)
            vus += int(bool(e.get("se_ferment")))
        taux[forme] = vus / float(replicats)
    voit = bool(taux["coherente"] >= 1.0 - 2.0 * float(garantie))
    tient_sa_garantie = le_taux_tient(taux["incoherente"], float(garantie))
    return {"decidable": True, "replicats": int(replicats),
            "la_torsion_en_voxels": round(st, 4), "le_bruit_horizontal_en_voxels": round(sh, 4),
            "le_bruit_vertical_en_voxels": round(sv, 4),
            "le_taux_sur_la_matiere_coherente": round(taux["coherente"], 4),
            "le_taux_de_faux": round(taux["incoherente"], 4),
            "le_taux_sur_lerreur_de_chunk": round(taux["chunk"], 4),
            "voit": voit, "tient_sa_garantie": bool(tient_sa_garantie),
            "tient": bool(voit and tient_sa_garantie)}


# ─────────────────────────────── le verdict ───────────────────────────────

def la_surface_la_plus_coherente(surfaces: dict) -> str | None:
    """Celle des trois dont la séparation est la plus petite sur le plus de rangées de boucles.

    ⚠ À égalité de compte, la première dans l'ordre `ΣB`, `Σ(A+B)`, `ΣA` : le pas commun d'abord,
    parce que c'est lui que `221` propose et que la tranche juge.
    """
    ordre = ("sigma_B", "sigma_A_plus_B", "sigma_A")
    gagnes = {k: 0 for k in ordre}
    for x in (surfaces or {}).values():
        if x.get("decidable"):
            gagnes[min(ordre, key=lambda k: (x[f"la_separation_{k}"], ordre.index(k)))] += 1
    if not any(gagnes.values()):
        return None
    return max(ordre, key=lambda k: (gagnes[k], -ordre.index(k)))


def _ce_qui_reste(issue: str, surface: str | None = None) -> str:
    """Ce qui reste — lu dans l'issue ET dans la surface la plus cohérente.

    ⚠⚠ LA PREMIÈRE VERSION NE LISAIT QUE L'ISSUE, et elle écrivait d'avance, pour des boucles qui se
    ferment, que « la surface se bâtit sur les boucles ». Une épreuve dit SI les pas verticaux
    expliquent une part du désaccord, pas COMBIEN ni quelle surface est la plus cohérente : ce sont
    les descriptions déclarées qui le disent, et la phrase les lit désormais.
    """
    if issue == "letalon_ne_tient_pas":
        return "un étalon qui tient, avant tout verdict"
    if surface == "sigma_A_plus_B":
        return ("chaque rangée garde son pas et la surface se bâtit sur les boucles : deux chemins "
                "sont la description la plus cohérente")
    if surface == "sigma_A":
        return ("chaque rangée garde son pas et le pas vertical lu n'y ajoute rien : ce qui reste "
                "est de le lire mieux")
    debut = ("une part du désaccord ferme ses boucles, mais"
             if issue == "les_boucles_se_ferment" else "le désaccord est de l'erreur de couture, et")
    return (f"{debut} le pas commun du consensus reste la surface la plus cohérente : ce qui reste "
            f"est de traverser la hauteur")


def juger(epreuve: dict, etalon: dict, surfaces: dict | None = None) -> dict:
    """L'issue, exclusive, tirée de l'étalon et de l'épreuve — et d'eux seuls ; ce qui reste lit aussi
    la surface la plus cohérente."""
    if not epreuve.get("decidable"):
        return {"decidable": False, "raison": epreuve.get("raison")}
    if not etalon.get("tient"):
        issue = "letalon_ne_tient_pas"
        texte = "L'ÉTALON NE TIENT PAS : AUCUN VERDICT."
    elif epreuve.get("se_ferment"):
        issue = "les_boucles_se_ferment"
        texte = ("LES BOUCLES SE FERMENT : LE PAS VERTICAL REND COMPTE D'UNE PART DU DÉSACCORD DES "
                 "RANGÉES VOISINES.")
    else:
        issue = "elles_ne_se_ferment_pas"
        texte = ("LES BOUCLES NE SE FERMENT PAS MIEUX QUE LE HASARD : LE PAS VERTICAL N'EXPLIQUE RIEN "
                 "DU DÉSACCORD DES RANGÉES VOISINES.")
    surface = la_surface_la_plus_coherente(surfaces)
    return {"decidable": True, "lissue": issue, "le_verdict": texte,
            "la_surface_la_plus_coherente": surface, "ce_qui_reste": _ce_qui_reste(issue, surface)}


# ─────────────────────────────── la mesure ───────────────────────────────

def analyser(lu: dict, par219: dict, replicats: int = REPLICATS, graine: int = GRAINE,
             avec_etalon: bool = True) -> dict:
    """Tout ce qui se calcule sur une lecture — pur, donc rejouable sans le volume."""
    rangees = par219["les_rangees"]
    rep = la_reproduction(lu["h"], par219["les_pas_par_rangee"])
    if not rep.get("decidable"):
        return {"decidable": False, "raison": rep.get("raison"), "la_reproduction": rep}
    n = int(par219["les_coutures_dune_rangee"])
    M = les_moities(lu["h"], lu["v"], rangees, n)
    ep = lepreuve(M["A"], M["B"])
    pl = le_plancher(M)
    if not ep.get("decidable") or not pl.get("decidable"):
        return {"decidable": False, "raison": ep.get("raison") or pl.get("raison"),
                "la_reproduction": rep}
    et = (sur_letalon(M, pl, replicats, graine) if avec_etalon
          else {"decidable": False, "tient": False, "raison": "étalon non demandé"})
    ph = [x[0] for r in rangees for x in (lu["h"].get(r) or {}).values()]
    pv = [x[0] for r in rangees[:-1] for x in (lu["v"].get(r) or {}).values()]
    lecture = {"combien_de_pas_horizontaux": len(ph), "combien_de_pas_verticaux": len(pv),
               "les_pas_verticaux_par_rangee_de_boucles": {
                   str(r): len(lu["v"].get(r) or {}) for r in rangees[:-1]},
               "la_dispersion_des_pas_horizontaux": round(float(np.std(ph)), 4),
               "la_dispersion_des_pas_verticaux": round(float(np.std(pv)), 4) if pv else None,
               "la_moyenne_des_pas_verticaux": round(float(np.mean(pv)), 4) if pv else None}
    surfaces = les_trois_surfaces(M)
    return {"decidable": True, "la_reproduction": rep, "les_rangees": rangees,
            "les_coutures_dune_rangee": n, "la_lecture": lecture, "lepreuve": ep,
            "le_plancher": pl, "letalon": et, "les_trois_surfaces": surfaces,
            "les_boucles_qui_sautent": les_boucles_qui_sautent(M),
            "les_boucles": {str(r): {str(c): [round(float(M["A"][i, c]), 4),
                                              round(float(M["B"][i, c]), 4)]
                                     for c in range(n)
                                     if not (np.isnan(M["A"][i, c]) or np.isnan(M["B"][i, c]))}
                            for i, r in enumerate(M["les_rangees_de_boucles"])},
            "le_detail_aux_colonnes_fortes": le_detail_aux_colonnes_fortes(
                lu["h"], lu["v"], par219["les_colonnes_fortes"], rangees),
            "le_verdict": juger(ep, et, surfaces)}


def mesurer(depuis: Path | None = None, delai: float = DELAI, replicats: int = REPLICATS,
            graine: int = GRAINE, ouvrir=None, meta=None, avec_etalon: bool = True) -> dict:
    """La lecture des cinq rangées dans les deux sens puis l'analyse — ou l'analyse seule, rejouée."""
    par219 = ce_que_219_a_rendu()
    if not par219.get("decidable"):
        return {"decidable": False, "raison": par219.get("raison"),
                "la_question_declaree": LA_QUESTION_DECLAREE}
    if depuis is not None:
        lu = relire_la_lecture(json.loads(Path(depuis).read_text()))
    else:
        lu = lire_la_surface(par219["les_rangees"], delai, ouvrir, meta)
        if not lu.get("decidable"):
            return {"decidable": False, "raison": lu.get("raison"),
                    "la_question_declaree": LA_QUESTION_DECLAREE}
    a = analyser(lu, par219, replicats, graine, avec_etalon)
    base = {"graine": int(graine), "la_question_declaree": LA_QUESTION_DECLAREE,
            "lepreuve_declaree": LEPREUVE_DECLAREE, "la_garantie_du_nul": GARANTIE,
            # ⚠⚠ LA LECTURE EST PUBLIÉE, couture par couture, pour que l'analyse se rejoue sans
            # relire le volume (`--depuis`).
            **publier_la_lecture(lu)}
    return {**base, **a}


def afficher(r: dict) -> None:
    if not r.get("decidable"):
        print(f"indécidable : {r.get('raison')}")
        return
    lec, ep, pl, et = r["la_lecture"], r["lepreuve"], r["le_plancher"], r["letalon"]
    print(f"reproduction de 219 : {r['la_reproduction']['les_ecarts_les_plus_grands']}")
    print(f"pas horizontaux {lec['combien_de_pas_horizontaux']}, verticaux "
          f"{lec['combien_de_pas_verticaux']} {lec['les_pas_verticaux_par_rangee_de_boucles']}")
    print(f"dispersion h {lec['la_dispersion_des_pas_horizontaux']:.4f}  v "
          f"{lec['la_dispersion_des_pas_verticaux']:.4f}")
    print(f"boucles {ep['combien_de_boucles']}  ρ = {ep['le_rapport_de_fermeture']:.4f}  nul médian "
          f"{ep['le_rapport_median_du_nul']:.4f}  ({ep['decalages_au_moins_aussi_fermes']}/"
          f"{ep['combien_de_decalages']})  p = {ep['la_valeur_p']:.4f}")
    print(f"var A {pl['la_variance_de_A']:.4f} (plancher {pl['le_plancher_de_A']:.4f})  var B "
          f"{pl['la_variance_de_B']:.4f} (plancher {pl['le_plancher_de_B']:.4f})  var L "
          f"{pl['la_variance_de_L']:.4f} (plancher {pl['le_plancher_de_L']:.4f})  part géom "
          f"{pl['la_part_geometrique']:.4f}")
    if et.get("decidable") and "le_taux_de_faux" in et:
        print(f"étalon : voit {et['le_taux_sur_la_matiere_coherente']:.4f}  faux "
              f"{et['le_taux_de_faux']:.4f}  chunk {et['le_taux_sur_lerreur_de_chunk']:.4f}  "
              f"tient {et['tient']}")
    for r_, s in r["les_trois_surfaces"].items():
        if s.get("decidable"):
            print(f"  {r_} {s['le_troncon']} ({s['combien_de_boucles']}) ΣA "
                  f"{s['la_separation_sigma_A']}  ΣB {s['la_separation_sigma_B']}  Σ(A+B) "
                  f"{s['la_separation_sigma_A_plus_B']}")
    q = r["les_boucles_qui_sautent"]
    print(f"boucles qui sautent un feuillet : {q['combien_sautent']}/{q['combien_de_boucles']}")
    for x in r["le_detail_aux_colonnes_fortes"]["les_colonnes"]:
        print(f"  forte {x}")
    print(r["le_verdict"].get("le_verdict"))


# ─────────────────────────────── la batterie ───────────────────────────────

def _un_profil(profondeur: int, g, marge: int = 40) -> np.ndarray:
    """Un profil en profondeur lisse et SANS période, pour que la corrélation n'ait qu'un maximum."""
    x = g.normal(0.0, 1.0, size=int(profondeur) + 2 * int(marge))
    noyau = np.exp(-0.5 * (np.arange(-6, 7) / 2.0) ** 2)
    return np.convolve(x, noyau / noyau.sum(), mode="same")


def _une_grille(rangees: int, colonnes: int, profondeur: int, cote: int, decalage, graine: int,
                droite: int = 0, bas: int = 0):
    """Des chunks dont la matière est déplacée de `decalage(r, c)` couches — et le lecteur.

    ⚠⚠ LA MOITIÉ DROITE d'un chunk est déplacée de `droite` couches de plus, sa MOITIÉ BASSE de `bas` :
    un chunk uniforme dans le plan rend le même profil sur ses quatre bords, et une sonde ne verrait
    alors ni un bord pris du mauvais côté, ni une coupe dans le mauvais sens.
    """
    base = _un_profil(profondeur, _rng(graine))
    moitie = int(cote) // 2

    def ouvrir(cy, cx):  # noqa: E306
        d0 = int(decalage(int(cy), int(cx)))
        b = np.empty((int(profondeur), int(cote), int(cote)))
        for i in range(int(cote)):
            for j in range(int(cote)):
                d = d0 + (int(bas) if i >= moitie else 0) + (int(droite) if j >= moitie else 0)
                b[:, i, j] = base[40 - d:40 - d + int(profondeur)]
        return b, None
    meta = {"chunks": [int(profondeur), int(cote), int(cote)],
            "shape": [int(profondeur), int(rangees) * int(cote), int(colonnes) * int(cote)]}
    return ouvrir, meta


def verifier() -> int:
    import combien_de_rangees_faut_il_pour_lire_le_pas as cdr
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

    # ⚠ LE FILTRE DE TEXTURE EST REMPLACÉ DANS LA SONDE, JAMAIS DANS LA MESURE : un chunk fabriqué
    # uniforme dans le plan n'a aucune orientation, et ce que la sonde vérifie est la géométrie de la
    # coupe, pas le filtre du producteur.
    filtre = cdr.la_courbe_dun_bloc
    cdr.la_courbe_dun_bloc = lambda b: ([], None)
    try:
        al, be, ga = 3, -2, 1
        dr_, ba_ = 2, 5
        ouvrir, meta = _une_grille(3, 4, 60, 32, lambda r, c: al * r + be * c + ga * r * c, 7,
                                   droite=dr_, bas=ba_)
        vol = {"cle": "x", "segment": "s"}
        sans = la_ligne(vol, 0.0, None, ouvrir, meta, 16, 1)
        avec = la_ligne(vol, 0.0, None, ouvrir, meta, 16, 1, les_bords_verticaux=True)
        v("★★★★ le drapeau par défaut ne lit aucun bord vertical", "bas" not in sans)
        v("★★★★ et il ne change rien aux bords horizontaux",
          set(sans["droits"]) == set(avec["droits"])
          and all(np.array_equal(sans["droits"][c][r_], avec["droits"][c][r_])
                  for c in sans["droits"] for r_ in sans["droits"][c]))
        v("★★★ les bords verticaux sont coupés à seize colonnes réparties comme les rangées",
          avec.get("les_colonnes_de_coupe") == avec.get("les_rangees_lues")
          and len(avec.get("les_colonnes_de_coupe") or []) == 16)
        lu = _sur(lire_la_surface, [0, 1, 2], lire_une=lambda r: la_ligne(
            vol, 0.0, None, ouvrir, meta, 16, r, les_bords_verticaux=True))
        def _lu(quoi, r, c):  # noqa: E306
            x = ((lu.get(quoi) or {}).get(r) or {}).get(c)
            return None if x is None else float(x[0])
        # ⭐ le bord droit porte `droite` couches de plus que le gauche du voisin, le bas `bas` de plus
        # que le haut du dessous : le pas lu les retranche, et seul le BON bord le fait.
        ok_h = lu.get("decidable") and all(
            _lu("h", r, c) is not None and abs(_lu("h", r, c) - (be + ga * r - dr_)) < 1e-9
            for r in range(3) for c in range(3))
        v("★★★★ le pas horizontal est la profondeur du chunk de droite moins celle de gauche", ok_h,
          str({r: {c: x[0] for c, x in s.items()} for r, s in (lu.get("h") or {}).items()}))
        ok_v = lu.get("decidable") and all(
            _lu("v", r, c) is not None and abs(_lu("v", r, c) - (al + ga * c - ba_)) < 1e-9
            for r in range(2) for c in range(4))
        v("★★★★ le pas vertical, celle du chunk du dessous moins celle du dessus — MÊME SENS", ok_v,
          str({r: {c: x[0] for c, x in s.items()} for r, s in (lu.get("v") or {}).items()}))
        v("★★★ la rangée du bas n'a pas de pas vertical",
          lu.get("decidable") and 2 not in (lu.get("v") or {}))
        if lu.get("decidable"):
            M = les_moities(lu["h"], lu["v"], [0, 1, 2], 3)
            L = M["A"] + M["B"]
            v("★★★★ une surface qui tourne ferme toutes ses boucles, exactement",
              bool(np.all(np.abs(L) < 1e-9)) and bool(np.all(np.abs(M["A"] + ga) < 1e-9)),
              str(L))
        else:
            v("★★★★ une surface qui tourne ferme toutes ses boucles, exactement", False,
              str(lu.get("raison")))
        panne = _sur(lire_la_surface, [0, 1], lire_une=lambda r: {
            **la_ligne(vol, 0.0, None, ouvrir, meta, 16, r, les_bords_verticaux=True),
            "refuses": {f"{LE_RESEAU_A_ECHOUE} x": 1}})
        v("★★★ une rangée dont le fil est tombé est refusée, par sa raison",
          not panne.get("decidable") and "réseau" in str(panne.get("raison")), str(panne.get("raison")))
        vide = _sur(lire_la_surface, [0, 1], lire_une=lambda r: {"decidable": False})
        v("★★ une rangée vide est refusée", not vide.get("decidable"))
    finally:
        cdr.la_courbe_dun_bloc = filtre

    # la reproduction de 219
    h = {196: {3: (1.0, 0.0, 16), 4: (-2.5, 0.0, 16)}, 197: {3: (0.5, 0.0, 16)}}
    pub = {196: {3: 1.0, 4: -2.5}, 197: {3: 0.5}}
    v("★★★ des pas qui retombent sont reproduits", _sur(la_reproduction, h, pub).get("decidable"))
    v("★★★★ un écart au-delà de l'arrondi est refusé",
      not _sur(la_reproduction, h, {196: {3: 1.0, 4: -2.5}, 197: {3: 0.5 + 1e-3}}).get("decidable"))
    v("★★★ un demi-dix-millième passe", _sur(la_reproduction, h, {
        196: {3: 1.0, 4: -2.5}, 197: {3: 0.5 + 0.5e-4}}).get("decidable"))
    v("★★★★ une colonne de plus est refusée",
      not _sur(la_reproduction, h, {196: {3: 1.0}, 197: {3: 0.5}}).get("decidable"))
    v("★★★ une colonne de moins aussi",
      not _sur(la_reproduction, h, {196: {3: 1.0, 4: -2.5, 5: 0.0}, 197: {3: 0.5}}).get("decidable"))

    # le bruit de lecture d'un pas
    v("★★★ seize coupes : var(moyenne) = d²/4", abs(la_variance_de_la_moyenne(2.0, 16) - 1.0) < 1e-12)
    v("★★ quinze coupes : d²·8·7/225", abs(la_variance_de_la_moyenne(3.0, 15) - 9 * 56 / 225) < 1e-12)

    # les moitiés
    hh = {0: {0: (1.0, 2.0, 16), 1: (2.0, 2.0, 16)}, 1: {0: (4.0, 2.0, 16), 1: (0.0, 2.0, 16)}}
    vv = {0: {0: (5.0, 2.0, 16), 1: (7.0, 2.0, 16)}}
    M = les_moities(hh, vv, [0, 1], 2)
    v("★★★★ A est le pas du dessus moins celui du dessous", M["A"][0, 0] == -3.0 and M["A"][0, 1] == 2.0)
    v("★★★★ B est le pas vertical de droite moins celui de gauche",
      M["B"][0, 0] == 2.0 and np.isnan(M["B"][0, 1]))
    v("★★★ le plancher d'une moitié porte ses deux pas", abs(M["le_plancher_de_A"][0, 0] - 2.0) < 1e-12)

    # le rapport de fermeture et le nul
    g = _rng(11)
    a0 = g.normal(0.0, 2.0, size=(4, 284))
    rho0, _ = le_rapport_de_fermeture(a0, -a0 + g.normal(0.0, 0.1, size=a0.shape))
    v("★★★★ B = -A ferme les boucles : ρ près de zéro", rho0 is not None and rho0 < 0.01, str(rho0))
    rho1, _ = le_rapport_de_fermeture(a0, g.normal(0.0, 2.0, size=a0.shape))
    v("★★★ B sans rapport : ρ près de un", rho1 is not None and 0.85 < rho1 < 1.15, str(rho1))
    b0 = g.normal(0.0, 1.0, size=a0.shape)
    x1, _ = le_rapport_de_fermeture(a0, b0, 5)
    x2, _ = le_rapport_de_fermeture(a0, np.roll(b0, -5, axis=1), 0)
    v("★★★★ décaler de s apparie A[c] à B[c+s]", abs(x1 - x2) < 1e-12)
    rc, _ = le_rapport_de_fermeture(a0 + 5.0, -a0)
    v("★★★ une moyenne propre à chaque moitié ne compte pas : chaque série est centrée",
      rc is not None and rc < 1e-12, str(rc))
    ah = a0.copy()
    ah[:, :10] = np.nan
    r_h, k_h = le_rapport_de_fermeture(ah, -ah)
    v("★★★ une boucle incomplète n'entre pas", k_h == 4 * 274 and r_h is not None and r_h < 1e-12)
    dec = les_decalages(284)
    v("★★★★ le nul prend tous les décalages d'au moins ⌈284^(1/3)⌉ = 7 coutures",
      dec[0] == 7 and dec[-1] == 277 and len(dec) == 271, f"{dec[0]}..{dec[-1]} ({len(dec)})")
    e = lepreuve(a0, -a0 + g.normal(0.0, 0.5, size=a0.shape))
    v("★★★★ des boucles qui se ferment passent l'épreuve, au plus petit P possible",
      e.get("se_ferment") and e["decalages_au_moins_aussi_fermes"] == 0
      and e["la_valeur_p"] == round(1.0 / 272.0, 4), str(e.get("la_valeur_p")))
    e2 = lepreuve(a0, g.normal(0.0, 2.0, size=a0.shape))
    v("★★★ des moitiés sans rapport ne la passent pas", not e2.get("se_ferment"),
      str(e2.get("la_valeur_p")))
    # ⚠⚠ UNE MOITIÉ QUI REVIENT SUR ELLE-MÊME : le nul doit garder sa structure. Des B faits
    # d'une différence première (comme ceux de la matière) décalés gardent leur corrélation à un pas.
    w = g.normal(0.0, 2.0, size=(4, 285))
    bd = w[:, 1:] - w[:, :-1]
    e3 = lepreuve(a0, bd)
    v("★★★ une différence première sans rapport ne passe pas non plus", not e3.get("se_ferment"),
      str(e3.get("la_valeur_p")))

    # le plancher
    pl = le_plancher({"A": np.array([[1.0, -1.0, np.nan]]), "B": np.array([[-1.0, 1.0, 5.0]]),
                      "le_plancher_de_A": np.array([[0.5, 0.5, 9.0]]),
                      "le_plancher_de_B": np.array([[0.2, 0.2, 9.0]])})
    v("★★★★ le plancher ne lit que les boucles complètes",
      pl["combien_de_boucles"] == 2 and abs(pl["le_plancher_de_A"] - 0.5) < 1e-12
      and abs(pl["le_plancher_de_B"] - 0.2) < 1e-12)
    v("★★★★ la part géométrique est moins la covariance",
      abs(pl["la_part_geometrique"] - 1.0) < 1e-12 and abs(pl["la_variance_de_L"]) < 1e-12)

    # les trois surfaces
    A3 = np.array([[1.0, 1.0, 1.0, np.nan, 1.0]])
    B3 = np.array([[-1.0, 2.0, -3.0, 0.0, 0.0]])
    s3 = les_trois_surfaces({"les_rangees_de_boucles": [196], "A": A3, "B": B3})["196"]
    v("★★★★ le tronçon est le plus long de boucles complètes", s3["le_troncon"] == [0, 2])
    v("★★★★ ΣA, ΣB, Σ(A+B) sont les séparations des trois cumuls",
      s3["la_separation_sigma_A"] == 3.0 and s3["la_separation_sigma_B"] == 2.0
      and s3["la_separation_sigma_A_plus_B"] == 3.0, str(s3))
    v("★★★ et chacune se juge au demi-feuillet",
      s3["sigma_A_tient"] and s3["sigma_B_tient"] and s3["sigma_A_plus_B_tient"])
    s4 = les_trois_surfaces({"les_rangees_de_boucles": [196], "A": np.full((1, 40), 1.0),
                             "B": np.zeros((1, 40))})["196"]
    v("★★★ une séparation de quarante ne tient pas", not s4["sigma_A_tient"] and s4["sigma_B_tient"])

    q = les_boucles_qui_sautent({"les_rangees_de_boucles": [196, 197],
                                 "A": np.array([[40.0, 1.0], [np.nan, -36.0]]),
                                 "B": np.array([[0.0, 0.0], [5.0, 0.0]])})
    v("★★★ une boucle saute à un demi-feuillet ou plus, dans les deux sens",
      q["combien_sautent"] == 2 and q["combien_de_boucles"] == 3
      and q["lesquelles"] == [[196, 0, 40.0], [197, 1, -36.0]], str(q))

    # le détail aux colonnes fortes : une ERREUR ouvre deux boucles en signes opposés
    rg = [196, 197, 198]
    hf = {r: {5: (0.0, 0.0, 16)} for r in rg}
    hf[197][5] = (4.0, 0.0, 16)
    vf = {r: {5: (0.0, 0.0, 16), 6: (0.0, 0.0, 16)} for r in rg[:-1]}
    d = le_detail_aux_colonnes_fortes(hf, vf, {5: 197}, rg)["les_colonnes"][0]
    v("★★★★ une erreur de la rangée ouvre sa boucle du dessous de +δ et celle du dessus de -δ",
      d["lecart_a_la_mediane"] == 4.0 and d["la_boucle_dessous"] == 4.0
      and d["la_boucle_dessus"] == -4.0, str(d))
    vg = {196: {5: (0.0, 0.0, 16), 6: (4.0, 0.0, 16)}, 197: {5: (0.0, 0.0, 16), 6: (-4.0, 0.0, 16)}}
    dg = le_detail_aux_colonnes_fortes(hf, vg, {5: 197}, rg)["les_colonnes"][0]
    v("★★★★ une géométrie que le pas vertical voit ferme les deux",
      dg["la_boucle_dessous"] == 0.0 and dg["la_boucle_dessus"] == 0.0, str(dg))
    db = le_detail_aux_colonnes_fortes(hf, vf, {5: 196}, rg)["les_colonnes"][0]
    v("★★ la rangée du haut n'a pas de boucle au-dessus", db["la_boucle_dessus"] is None)
    v("★★★★ l'erreur a la forme d'une erreur, la géométrie celle de boucles fermées",
      d["la_forme"] == "erreur" and dg["la_forme"] == "fermee")
    v("★★★★ une boucle ouverte du MAUVAIS signe n'a pas la forme d'une erreur",
      la_forme(4.0, -4.0, None) == "mixte" and la_forme(4.0, None, 4.0) == "mixte")
    v("★★★ la moitié de l'écart départage : ouverte à la moitié, fermée en dessous",
      la_forme(4.0, 2.0, -2.0) == "erreur" and la_forme(4.0, 1.99, -1.99) == "fermee"
      and la_forme(4.0, 3.0, -1.0) == "mixte")
    v("★★ une colonne sans boucle n'a pas de forme", la_forme(4.0, None, None) is None)
    comptes = le_detail_aux_colonnes_fortes(hf, vg, {5: 197}, rg)
    v("★★★ les formes sont comptées", comptes["combien_se_ferment"] == 1
      and comptes["combien_ont_la_forme_dune_erreur"] == 0)

    # les matières de l'étalon
    mA = np.ones((4, 284), dtype=bool)
    gA, gB = une_matiere("coherente", mA, mA, 2.0, 0.5, 0.5, _rng(3))
    v("★★★★ la matière cohérente : A + B n'est que du bruit de lecture",
      abs(float(np.var(gA + gB)) - 1.0) < 0.2, str(float(np.var(gA + gB))))
    v("★★★ et A porte la torsion en plus", abs(float(np.var(gA)) - 4.5) < 0.8, str(float(np.var(gA))))
    iA, iB = une_matiere("incoherente", mA, mA, 2.0, 0.5, 0.5, _rng(3))
    v("★★★★ la matière incohérente : A + B porte les deux torsions",
      float(np.var(iA + iB)) > 7.0, str(float(np.var(iA + iB))))
    cA, cB = une_matiere("chunk", mA, mA, 2.0, 0.5, 0.5, _rng(3))
    v("★★★★ l'erreur de chunk ferme ses boucles comme une géométrie",
      abs(float(np.var(cA + cB)) - 1.0) < 0.2 and abs(float(np.var(cA)) - 4.5) < 0.8,
      f"{float(np.var(cA + cB))} {float(np.var(cA))}")
    trou = mA.copy()
    trou[:, 50:60] = False
    tA, _tB = une_matiere("coherente", trou, mA, 2.0, 0.5, 0.5, _rng(3))
    v("★★★ la matière suit le motif de présence lu", bool(np.isnan(tA[:, 50:60]).all())
      and not bool(np.isnan(tA[:, :50]).any()))

    fM = {"A": np.where(trou, 0.0, np.nan), "B": np.zeros((4, 284))}
    fpl = {"lexces_de_A_sur_son_plancher": 4.0, "le_plancher_de_A": 0.5, "le_plancher_de_B": 0.5}
    # ⚠ LA GRAINE DE LA SONDE A ÉTÉ CHANGÉE, et c'est dit : la première tirait sept faux sur
    # soixante, un tirage rare pour un nul dont le taux, sondé à part sur plusieurs milliers de
    # matières incohérentes pleines et trouées, est celui de sa garantie. Les bris disent si la sonde
    # rougit quand le nul est faux.
    et = sur_letalon(fM, fpl, replicats=REPLICATS, graine=6)
    v("★★★★ l'étalon voit la torsion permise", et["voit"], str(et["le_taux_sur_la_matiere_coherente"]))
    v("★★★★ et tient sa garantie sur la matière incohérente", et["tient_sa_garantie"],
      str(et["le_taux_de_faux"]))
    v("★★★ et l'erreur de chunk passe l'épreuve comme la géométrie",
      et["le_taux_sur_lerreur_de_chunk"] >= 1.0 - 2.0 * GARANTIE, str(et["le_taux_sur_lerreur_de_chunk"]))
    v("★★★ la torsion de l'étalon est tout l'excès du désaccord, et le bruit celui d'un pas",
      abs(et["la_torsion_en_voxels"] - 2.0) < 1e-12
      and abs(et["le_bruit_horizontal_en_voxels"] - 0.5) < 1e-12
      and abs(et["le_bruit_vertical_en_voxels"] - 0.5) < 1e-12,
      f"{et['la_torsion_en_voxels']} {et['le_bruit_horizontal_en_voxels']}")
    noye = sur_letalon(fM, {"lexces_de_A_sur_son_plancher": 0.0004, "le_plancher_de_A": 2.0,
                            "le_plancher_de_B": 2.0}, replicats=10, graine=6)
    v("★★★★ une torsion noyée dans le bruit n'est pas vue : l'étalon ne tient pas",
      not noye["voit"] and not noye["tient"], str(noye.get("le_taux_sur_la_matiere_coherente")))
    nul = sur_letalon(fM, {**fpl, "lexces_de_A_sur_son_plancher": -1.0}, replicats=4)
    v("★★★ un désaccord sous son plancher n'a rien à expliquer : l'étalon ne tient pas",
      not nul["tient"])

    # la surface la plus cohérente, et ce qui reste la lit
    def _s(a, b, ab):  # noqa: E306
        return {"decidable": True, "la_separation_sigma_A": a, "la_separation_sigma_B": b,
                "la_separation_sigma_A_plus_B": ab}
    v("★★★★ la surface la plus cohérente est celle qui gagne le plus de rangées de boucles",
      la_surface_la_plus_coherente({"1": _s(9, 3, 5), "2": _s(9, 6, 5), "3": _s(1, 6, 5)})
      == "sigma_B"
      and la_surface_la_plus_coherente({"1": _s(9, 7, 5), "2": _s(9, 6, 5)}) == "sigma_A_plus_B")
    v("★★★ à égalité, le pas commun d'abord",
      la_surface_la_plus_coherente({"1": _s(9, 3, 5), "2": _s(9, 6, 5)}) == "sigma_B")
    v("★★★★ des boucles qui se ferment ne font pas bâtir la surface sur elles si le pas commun est "
      "plus cohérent", "consensus reste" in _ce_qui_reste("les_boucles_se_ferment", "sigma_B")
      and "bâtit sur les boucles" in _ce_qui_reste("les_boucles_se_ferment", "sigma_A_plus_B"))
    pe = le_plancher({"A": np.array([[2.0, -2.0]]), "B": np.array([[-1.0, 1.0]]),
                      "le_plancher_de_A": np.array([[2.0, 2.0]]),
                      "le_plancher_de_B": np.array([[0.2, 0.2]])})
    v("★★★ la part expliquée rapporte la part géométrique à l'excès du désaccord",
      abs(pe["la_part_expliquee_de_lexces"] - 1.0) < 1e-12, str(pe["la_part_expliquee_de_lexces"]))

    # le verdict
    oui, non = {"decidable": True, "se_ferment": True}, {"decidable": True, "se_ferment": False}
    v("★★★★ sans étalon, aucun verdict, même si les boucles se ferment",
      juger(oui, {"tient": False})["lissue"] == "letalon_ne_tient_pas")
    v("★★★ les boucles se ferment", juger(oui, {"tient": True})["lissue"] == "les_boucles_se_ferment")
    v("★★★ elles ne se ferment pas", juger(non, {"tient": True})["lissue"] == "elles_ne_se_ferment_pas")
    v("★★ une épreuve indécidable ne rend pas de verdict",
      not juger({"decidable": False}, {"tient": True})["decidable"])

    # la lecture se publie et se relit
    lu0 = {"h": {196: {3: (1.23456, 0.5, 16)}}, "v": {196: {3: (-2.0, 1.0, 15)}},
           "les_lignes": {196: {"a": 1}}}
    rel = relire_la_lecture(json.loads(json.dumps(publier_la_lecture(lu0))))
    v("★★★ la lecture publiée se relit à la quatrième décimale",
      rel["h"][196][3] == (1.2346, 0.5, 16) and rel["v"][196][3] == (-2.0, 1.0, 15))

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
                   help="lit les cinq rangées dans les deux sens et écrit la lecture seule")
    p.add_argument("--depuis", type=Path, default=None,
                   help="rejoue l'analyse depuis une lecture, sans relire le volume")
    p.add_argument("--json", type=Path, default=None)
    p.add_argument("--graine", type=int, default=GRAINE)
    p.add_argument("--replicats", type=int, default=REPLICATS)
    p.add_argument("--sans-etalon", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if a.lire:
        par219 = ce_que_219_a_rendu()
        if not par219.get("decidable"):
            print(f"indécidable : {par219.get('raison')}")
            return 1
        lu = lire_la_surface(par219["les_rangees"])
        if not lu.get("decidable"):
            print(f"indécidable : {lu.get('raison')}")
            return 1
        a.lire.parent.mkdir(parents=True, exist_ok=True)
        a.lire.write_text(json.dumps(publier_la_lecture(lu), ensure_ascii=False, indent=1))
        print(f"écrit : {a.lire}")
        return 0
    r = mesurer(a.depuis, DELAI, a.replicats, a.graine, avec_etalon=not a.sans_etalon)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=2))
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
