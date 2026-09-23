"""Où s'arrête le segment, et le plus grand rectangle que le dépôt porte ferme-t-il sous le demi-feuillet ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LE DÉPÔT NE SOIT LISTÉ ET QUE LA MOINDRE LIGNE NOUVELLE NE SOIT LUE. La
seule chose regardée avant d'écrire est que le dépôt se liste, et la forme de ses clés.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P78`. `232` a dérivé le rectangle du segment entier des bords
de la croix centrale, et il est resté ouvert : la rangée 11 et la colonne 268 perdent leur majorité sur des
tronçons de 48 à 171 coutures, là où le dépôt ne porte pas de chunks. Les bords de la croix ne sont pas ceux
du segment. Où s'arrête-t-il, et une boucle qu'il porte tout entière ferme-t-elle sous le demi-feuillet ?

## La présence, listée

Le tableau du niveau 0 est découpé en chunks de 128 sur 128, sur toute sa profondeur, et le dépôt n'écrit
pas un chunk vide. La liste des clés du dépôt dit donc, chunk par chunk, où le segment porte quelque chose,
sans lire une seule valeur. ⚠⚠ Un chunk absent de la liste n'est pas un chunk mal lu : une requête qui
échoue rend la mesure indécidable, jamais absente.

⚠⚠⚠ LA PRÉSENCE EST CONTRÔLÉE PAR CE QUE `232` A LU : pour chacune de ses trente-six lignes, les chunks que
la liste dit absents sur la portion lue sont exactement ceux que la lecture a comptés « absents du dépôt ».
Sinon, refus.

## Le rectangle, dérivé

Une bande de neuf lignes, centrées par la fonction de `219`, TIENT sur un côté quand, à chaque couture du
côté, ses NEUF lignes ont leurs deux chunks dans le dépôt. ⚠⚠ Pas seulement la majorité de `228` : la
présence ne dit rien de la texture, et une bande dont juste cinq lignes seraient présentes perdrait sa
majorité au premier chunk trop peu texturé. Les neuf présentes laissent à la texture la marge de quatre
lignes que la majorité accorde. Le rectangle est le plus grand dont les quatre bandes tiennent : le plus
long chemin d'un coin à l'autre, la demi-somme de ses côtés ; à égalité la plus grande aire, puis la plus
petite rangée, puis la plus petite colonne. Le code dérive le rectangle de la liste, et rien d'autre ; il
n'est pas choisi.

## Ce qui se lit, et ce qui le contrôle

Les quatre bandes, neuf lignes chacune, par le lecteur de `224`. ⚠⚠⚠ Partout où une bande croise une bande
publiée — `219`, `223`, `224`, `232` —, les pas relus retombent à l'arrondi, sur les mêmes coutures, sinon
refus. ⚠⚠ Et les chunks que la lecture compte absents du dépôt sont ceux que la liste dit absents.

## Ce qui se mesure

L'instrument de `228`, sur ce rectangle, à chaque largeur de l'échelle de `218`, avec la garde de `232` :
un trou de majorité se franchit par le maillage, et seulement jusqu'aux 17 coutures que `225` a essayées.

## Les issues, exclusives, jugées à neuf lignes

- le dépôt ne porte pas de rectangle plus grand que le grand rectangle de `224` : il n'y a pas d'échelle
  au-delà de la moitié du segment à mesurer, et rien n'est lu ;
- un trou plus long que ceux que `225` a franchis : le rectangle reste ouvert ;
- la fermeture atteint le demi-feuillet : ses deux chemins arrivent sur deux spires ;
- elle reste dessous : ils arrivent sur la même.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : une boucle, un segment ; le plus grand rectangle n'est pas tout le
segment, et une fermeture sous le demi-feuillet dit que deux chemins s'accordent, pas lequel est sur la
bonne spire.

Usage :
    uv run python src/nappe/ou_sarrete_le_segment.py --verifier
    uv run python src/nappe/ou_sarrete_le_segment.py --lire <lecture.json>
    uv run python src/nappe/ou_sarrete_le_segment.py --depuis <lecture.json> --json docs/mesures/ou_sarrete_le_segment.json
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))

from cinq_rangees_designent_elles_la_fautive import les_rangees_a_lire  # noqa: E402
from deux_chemins_arrivent_ils_sur_la_meme_spire import (_la_definition,  # noqa: E402
                                                          ce_que_223_a_rendu, lire_les_bandes,
                                                          relire_une_bande)
from deux_chemins_du_segment_entier_arrivent_ils_sur_la_meme_spire import (analyser,  # noqa: E402
                                                                            ce_que_225_a_publie,
                                                                            ce_que_228_a_publie,
                                                                            les_bandes_a_lire,
                                                                            les_pas_des_bandes)
from lajustement_de_toutes_les_boucles_garde_t_il_la_spire import ce_que_225_a_rendu  # noqa: E402
from la_recette_posee_sur_le_rouleau import DELAI  # noqa: E402
from le_vote_ramene_t_il_les_rangees_sur_le_feuillet import ce_que_219_a_rendu  # noqa: E402
from ou_est_lerreur_de_la_boucle_en_haut_a_gauche import (la_reproduction_croisee,  # noqa: E402
                                                          le_domaine, les_pas_dune_bande,
                                                          les_sources_publiees)
from ou_le_maillage_quitte_t_il_son_feuillet import le_segment_declare  # noqa: E402
from quest_ce_qui_franchit_le_trou_de_majorite import ce_que_224_a_rendu  # noqa: E402
from une_bande_plus_large_ferme_t_elle_le_grand_rectangle import la_majorite, les_largeurs  # noqa: E402
from zarr_depth import BUCKET, get  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
CE_QUE_232_A_PUBLIE = MESURES / "deux_chemins_du_segment_entier_arrivent_ils_sur_la_meme_spire.json"
ABSENT = "absent du dépôt"
LE_NIVEAU = 0
LA_PAGE = 1000

LA_QUESTION_DECLAREE = ("où s'arrête le segment, et le plus grand rectangle que le dépôt porte ferme-t-il sous le "
                        "demi-feuillet ?")
LA_MESURE_DECLAREE = ("la présence des chunks listée dans le dépôt, le plus grand rectangle dont les quatre bandes "
                      "de neuf lignes y tiennent, et l'instrument de `228` sur ce rectangle")


# ─────────────────────────────── la présence ───────────────────────────────

def les_cles_dune_page(xml: bytes) -> tuple[list[str], str | None]:
    """Les clés d'une page de liste S3, et le jeton de la suivante — ou rien si c'est la dernière."""
    racine = ET.fromstring(xml)
    ns = racine.tag.split("}")[0] + "}" if racine.tag.startswith("{") else ""
    cles = [e.text for e in racine.iter(f"{ns}Key")]
    tronque = (racine.findtext(f"{ns}IsTruncated") or "").strip().lower() == "true"
    jeton = racine.findtext(f"{ns}NextContinuationToken") if tronque else None
    if tronque and not jeton:
        raise ValueError("une page tronquée sans jeton")
    return cles, jeton


def la_presence_des_cles(cles, prefixe: str, meta: dict) -> dict:
    """La grille de présence du niveau 0, depuis les clés listées : `{"la_grille", "les_rangees"}`.

    ⚠⚠ Le tableau n'a qu'un chunk dans la profondeur, et toute clé qui en nommerait un second est refusée :
    elle voudrait dire que la grille n'est pas celle que le lecteur de `224` parcourt.
    """
    profond, hy, hx = [int(x) for x in meta["chunks"]]
    nz, ny, nx = [int(x) for x in meta["shape"]]
    if profond != nz:
        return {"decidable": False, "raison": "le tableau a plus d'un chunk dans la profondeur"}
    gy, gx = -(-ny // hy), -(-nx // hx)
    sep = meta.get("dimension_separator", ".")
    A = np.zeros((gy, gx), dtype=bool)
    for cle in cles:
        if not cle.startswith(prefixe):
            continue
        reste = cle[len(prefixe):]
        if reste.startswith("."):
            continue
        parties = reste.split(sep)
        if len(parties) != 3 or not all(p.isdigit() for p in parties):
            return {"decidable": False, "raison": f"une clé qui n'est pas un chunk : {reste}"}
        cz, cy, cx = (int(p) for p in parties)
        if cz != 0 or not (0 <= cy < gy and 0 <= cx < gx):
            return {"decidable": False, "raison": f"une clé hors de la grille : {reste}"}
        A[cy, cx] = True
    return {"decidable": True, "la_grille": [gy, gx],
            "les_rangees": ["".join("1" if x else "0" for x in ligne) for ligne in A]}


def lister_le_depot(volume: dict, delai: float = DELAI, obtenir=None) -> dict:
    """La présence des chunks du niveau 0, par la liste des clés du dépôt — jamais une valeur lue.

    ⚠⚠⚠ UNE PAGE QUI NE RÉPOND PAS REND LA LISTE INDÉCIDABLE : compter ses chunks absents ferait d'une panne de
    réseau un bord du segment.
    """
    obtenir = obtenir or (lambda u: get(u, delai))
    url = f"{BUCKET}/{volume['cle']}"
    brut = obtenir(f"{url}/{LE_NIVEAU}/.zarray")
    if brut is None:
        return {"decidable": False, "raison": "le tableau ne répond pas"}
    meta = json.loads(brut)
    prefixe = f"{volume['cle']}/{LE_NIVEAU}/"
    cles, jeton, pages = [], None, 0
    while True:
        q = f"{BUCKET}/?list-type=2&prefix={urllib.parse.quote(prefixe)}&max-keys={LA_PAGE}"
        if jeton is not None:
            q += f"&continuation-token={urllib.parse.quote(jeton, safe='')}"
        page = obtenir(q)
        if page is None:
            return {"decidable": False, "raison": f"la page {pages + 1} de la liste ne répond pas"}
        try:
            c, jeton = les_cles_dune_page(page)
        except (ET.ParseError, ValueError) as e:
            return {"decidable": False, "raison": f"la page {pages + 1} de la liste est illisible : {e}"}
        cles += c
        pages += 1
        if jeton is None:
            break
    p = la_presence_des_cles(cles, prefixe, meta)
    if not p.get("decidable"):
        return p
    return {**p, "le_segment": volume.get("segment"), "les_pages": pages}


def la_grille_de_presence(presence: dict) -> np.ndarray:
    return np.array([[c == "1" for c in r] for r in presence["les_rangees"]], dtype=bool)


def les_absents_dune_ligne(A: np.ndarray, sens: str, ligne: int, de: int, a: int) -> int:
    """Les chunks que la liste dit absents sur une ligne d'une bande, de `de` à `a` bornes comprises."""
    if sens == "rangees":
        return int((~A[int(ligne), int(de):int(a) + 1]).sum())
    return int((~A[int(de):int(a) + 1, int(ligne)]).sum())


def la_presence_retombe(A: np.ndarray, bandes, publiees: dict) -> dict:
    """Pour chaque ligne lue, les absents de la liste sont-ils ceux que la lecture a comptés ? Sinon, refus."""
    vus = 0
    for b in bandes:
        lec = (publiees.get(b["cle"]) or {}).get("les_lectures") or {}
        for l_ in b["les_lignes"]:
            x = lec.get(str(l_))
            if x is None:
                return {"decidable": False, "raison": f"la ligne {l_} de {b['cle']} n'a pas de lecture publiée"}
            lu = int((x.get("refuses") or {}).get(ABSENT, 0))
            liste = les_absents_dune_ligne(A, b["le_sens"], l_, b["de"], b["a"])
            if lu != liste:
                return {"decidable": False,
                        "raison": (f"la ligne {l_} de {b['cle']} : {lu} chunks absents à la lecture, {liste} selon la "
                                   f"liste — la présence ne retombe pas")}
            vus += 1
    return {"decidable": True, "combien_de_lignes": vus}


# ─────────────────────────────── le rectangle, dérivé ───────────────────────────────

def ce_quil_faut(k: int) -> int:
    """Combien de lignes d'une bande doivent avoir leurs deux chunks dans le dépôt : TOUTES. La majorité de
    `228` garde alors `k − (k // 2 + 1)` lignes de marge pour les chunks trop peu texturés, que la présence
    ne voit pas."""
    return int(k)


def les_bandes_qui_tiennent(A: np.ndarray, k: int) -> tuple[np.ndarray, np.ndarray]:
    """`(sur_la_rangee, sur_la_colonne)` : une bande de rangées centrée en `r` tient à la couture horizontale
    `s` quand ses `k` lignes y ont leurs deux chunks ; de même pour les colonnes.
    `sur_la_rangee[r, s]` pour `s` de 0 à `gx − 2` ; `sur_la_colonne[s, c]` pour `s` de 0 à `gy − 2`."""
    A = np.asarray(A, dtype=bool)
    gy, gx = A.shape
    m, h = ce_quil_faut(k), int(k) // 2
    H = (A[:, :-1] & A[:, 1:]).astype(int)
    V = (A[:-1, :] & A[1:, :]).astype(int)
    rangee = np.zeros((gy, gx - 1), dtype=bool)
    ch = np.vstack([np.zeros((1, gx - 1), dtype=int), np.cumsum(H, axis=0)])
    for r in range(h, gy - h):
        rangee[r] = (ch[r + h + 1] - ch[r - h]) >= m
    colonne = np.zeros((gy - 1, gx), dtype=bool)
    cv = np.hstack([np.zeros((gy - 1, 1), dtype=int), np.cumsum(V, axis=1)])
    for c in range(h, gx - h):
        colonne[:, c] = (cv[:, c + h + 1] - cv[:, c - h]) >= m
    return rangee, colonne


def le_plus_grand_rectangle(A: np.ndarray, k: int) -> tuple[int, int, int, int] | None:
    """Le rectangle `(r0, r1, c0, c1)` dont les quatre bandes tiennent, au plus long chemin `(r1−r0)+(c1−c0)` ;
    à égalité la plus grande aire, puis la plus petite `r0`, puis la plus petite `c0`."""
    A = np.asarray(A, dtype=bool)
    gy, gx = A.shape
    h = int(k) // 2
    rangee, colonne = les_bandes_qui_tiennent(A, k)
    mauvais = np.vstack([np.zeros((1, gx), dtype=int), np.cumsum(~colonne, axis=0)])
    centres = np.zeros(gx, dtype=bool)
    centres[h:gx - h] = True
    meilleur, cle_m = None, None
    rangs = [r for r in range(h, gy - h) if rangee[r].any()]
    for i, r0 in enumerate(rangs):
        for r1 in reversed(rangs[i + 1:]):
            if cle_m is not None and (r1 - r0) + (gx - 1) < cle_m[0]:
                break
            deux = rangee[r0] & rangee[r1]
            if not deux.any():
                continue
            valides = np.flatnonzero(((mauvais[r1] - mauvais[r0]) == 0) & centres)
            if len(valides) < 2:
                continue
            rompu = np.concatenate(([0], np.cumsum(~deux)))
            grp = rompu[valides]
            coupe = np.flatnonzero(np.diff(grp)) + 1
            debuts = np.concatenate(([0], coupe))
            fins = np.concatenate((coupe, [len(valides)])) - 1
            larg = valides[fins] - valides[debuts]
            j = int(np.argmax(larg))
            if larg[j] <= 0:
                continue
            c0, c1 = int(valides[debuts[j]]), int(valides[fins[j]])
            cle = ((r1 - r0) + (c1 - c0), (r1 - r0) * (c1 - c0), -r0, -c0)
            if cle_m is None or cle > cle_m:
                meilleur, cle_m = (int(r0), int(r1), c0, c1), cle
    return meilleur


def le_rectangle_du_depot(A: np.ndarray, k: int, reference: int) -> dict:
    """Le plus grand rectangle, son chemin, et le chemin du grand rectangle de `224` qu'il doit dépasser."""
    coins = le_plus_grand_rectangle(A, k)
    if coins is None:
        return {"decidable": True, "les_coins": None, "le_chemin": 0, "le_chemin_de_224": int(reference),
                "depasse_la_moitie": False}
    r0, r1, c0, c1 = coins
    ch = (r1 - r0) + (c1 - c0)
    return {"decidable": True, "les_coins": list(coins), "le_chemin": int(ch), "le_chemin_de_224": int(reference),
            "depasse_la_moitie": bool(ch > int(reference))}


def lempreinte(A: np.ndarray) -> dict:
    """Ce que le dépôt porte : combien de chunks, sur quelle grille, et dans quel encadrement."""
    ys, xs = np.nonzero(A)
    if not len(ys):
        return {"combien": 0, "sur": int(A.size)}
    return {"combien": int(A.sum()), "sur": int(A.size), "les_rangees": [int(ys.min()), int(ys.max())],
            "les_colonnes": [int(xs.min()), int(xs.max())]}


# ─────────────────────────────── la mesure ───────────────────────────────

def _ce_qui_reste(depasse: bool, ouvert: bool, ferme: bool) -> str:
    """Les quatre issues, EXCLUSIVES, dans cet ordre de priorité."""
    if not depasse:
        return "LE DÉPÔT NE PORTE PAS DE RECTANGLE PLUS GRAND QUE LA MOITIÉ DU SEGMENT : IL N'Y A RIEN AU-DELÀ À MESURER"
    if ouvert:
        return "À NEUF LIGNES, UN TROU PLUS LONG QUE CEUX QUE `225` A FRANCHIS LAISSE LE PLUS GRAND RECTANGLE OUVERT"
    if not ferme:
        return "À NEUF LIGNES, LES DEUX CHEMINS DU PLUS GRAND RECTANGLE ARRIVENT À UN DEMI-FEUILLET L'UN DE L'AUTRE"
    return "À NEUF LIGNES, LES DEUX CHEMINS DU PLUS GRAND RECTANGLE ARRIVENT SUR LA MÊME SPIRE"


def ce_que_232_a_publie(chemin: Path = CE_QUE_232_A_PUBLIE) -> dict:
    """Les quatre bandes que `232` a lues, relues, et leurs lectures ligne à ligne."""
    if not Path(chemin).exists():
        return {"decidable": False, "raison": f"{Path(chemin).name} est absent"}
    try:
        d = json.loads(Path(chemin).read_text())
    except (ValueError, OSError) as e:
        return {"decidable": False, "raison": f"{Path(chemin).name} est illisible : {e}"}
    if not d.get("decidable") or not d.get("les_bandes") or not d.get("les_bandes_declarees"):
        return {"decidable": False, "raison": "`232` ne publie pas ses bandes"}
    return {"decidable": True, "bandes": d["les_bandes_declarees"], "publiees": d["les_bandes"],
            "relues": {k: relire_une_bande(x) for k, x in d["les_bandes"].items()}}


def les_sources(par219: dict, par223: dict, par224: dict, par232: dict) -> dict:
    """Ce qui contrôle une bande neuve : `219`, `223` et `224`, et les quatre bandes de `232`."""
    out = les_sources_publiees(par219, par223, par224)
    for b in par232["bandes"]:
        out[f"232 {b['cle']}"] = {"domaine": le_domaine(b["le_sens"], b["les_lignes"], b["de"], b["a"]),
                                  "pas": les_pas_dune_bande(par232["relues"][b["cle"]])}
    return out


def mesurer(depuis: Path | None = None, par219: dict | None = None, par223: dict | None = None,
            par224: dict | None = None, par225: dict | None = None, pub225: dict | None = None,
            pub228: dict | None = None, par232: dict | None = None, lister=None, lire=None,
            tirages: int | None = None) -> dict:
    """La liste du dépôt, le rectangle qu'elle dérive, la lecture de ses bandes puis l'analyse — ou rejouées."""
    par219 = ce_que_219_a_rendu() if par219 is None else par219
    par223 = ce_que_223_a_rendu() if par223 is None else par223
    par224 = ce_que_224_a_rendu() if par224 is None else par224
    par225 = ce_que_225_a_rendu() if par225 is None else par225
    pub225 = ce_que_225_a_publie() if pub225 is None else pub225
    pub228 = ce_que_228_a_publie() if pub228 is None else pub228
    par232 = ce_que_232_a_publie() if par232 is None else par232
    base = {"la_question_declaree": LA_QUESTION_DECLAREE, "la_mesure_declaree": LA_MESURE_DECLAREE}
    for nom, par in (("219", par219), ("223", par223), ("224", par224), ("225", par225), ("225 publiée", pub225),
                     ("228", pub228), ("232", par232)):
        if not par.get("decidable"):
            return {**base, "decidable": False, "raison": f"`{nom}` : {par.get('raison')}"}
    lecture = json.loads(Path(depuis).read_text()) if depuis is not None else {}
    presence = lecture.get("la_presence") if depuis is not None else None
    if presence is None:
        if depuis is not None:
            return {**base, "decidable": False, "raison": "la lecture ne porte pas la présence"}
        presence = (lister or (lambda: lister_le_depot(le_segment_declare())))()
    base["la_presence"] = presence
    if not presence.get("decidable"):
        return {**base, "decidable": False, "raison": presence.get("raison")}
    if [int(x) for x in presence["la_grille"]] != [int(x) for x in par224["la_grille"]]:
        return {**base, "decidable": False, "raison": "la grille listée n'est pas celle que les bandes parcourent"}
    A = la_grille_de_presence(presence)
    c232 = la_presence_retombe(A, par232["bandes"], par232["publiees"])
    base["la_presence_contre_232"] = c232
    if not c232.get("decidable"):
        return {**base, "decidable": False, "raison": c232.get("raison")}
    k1 = les_largeurs()[-1]
    R, C = par224["R"], par224["C"]
    rect = le_rectangle_du_depot(A, k1, (R[2] - R[0]) + (C[2] - C[0]))
    base.update({"lempreinte": lempreinte(A), "le_rectangle": rect})
    if not rect["depasse_la_moitie"]:
        return {**base, "decidable": True, "le_verdict": {
            "le_rectangle_depasse_la_moitie": False, "ce_qui_reste_a_mesurer": _ce_qui_reste(False, False, False)}}
    coins = rect["les_coins"]
    bandes = les_bandes_a_lire(coins, k1)
    plus_long = max(pub225["les_longueurs_essayees"])
    g = par224["graine"]
    t_ = par224["tirages"] if tirages is None else int(tirages)
    if depuis is not None:
        lu = {"decidable": True, "les_bandes": lecture.get("les_bandes") or {}}
    else:
        lu = lire_les_bandes(bandes, lire=lire)
    base.update({"graine": int(g), "tirages": t_, "la_regle_de_225": par225["la_regle"],
                 "le_plus_long_trou_franchi_par_225": int(plus_long), "les_bandes_declarees": bandes,
                 "les_bandes": lu.get("les_bandes") or {}})
    if not lu.get("decidable"):
        return {**base, "decidable": False, "raison": lu.get("raison")}
    pub = lu["les_bandes"]
    if (sorted(pub) != sorted(b["cle"] for b in bandes)
            or any(_la_definition(pub[b["cle"]]) != _la_definition(b) for b in bandes)):
        return {**base, "decidable": False, "raison": "la lecture n'est pas celle des bandes dérivées"}
    cn = la_presence_retombe(A, bandes, pub)
    base["la_presence_contre_la_lecture"] = cn
    if not cn.get("decidable"):
        return {**base, "decidable": False, "raison": cn.get("raison")}
    relues = {k: relire_une_bande(x) for k, x in pub.items()}
    nouvelles = {b["cle"]: {"domaine": le_domaine(b["le_sens"], b["les_lignes"], b["de"], b["a"]),
                            "pas": les_pas_dune_bande(relues[b["cle"]])} for b in bandes}
    rep = la_reproduction_croisee(nouvelles, les_sources(par219, par223, par224, par232))
    if not rep.get("decidable"):
        return {**base, "decidable": False, "raison": rep.get("raison"), "la_reproduction": rep}
    a = analyser(les_pas_des_bandes(relues, bandes), coins, par225["la_regle"], plus_long, g, t_)
    if not a.get("decidable"):
        return {**base, "decidable": False, "raison": a.get("raison"), "la_reproduction": rep}
    v = a["le_verdict"]
    a["le_verdict"] = {**v, "le_rectangle_depasse_la_moitie": True,
                       "ce_qui_reste_a_mesurer": _ce_qui_reste(True, v["le_segment_entier_reste_ouvert"],
                                                               v["le_segment_entier_se_ferme"])}
    return {**base, "decidable": True, "la_reproduction": rep, "la_moitie_du_segment": pub228["par_largeur"], **a}


def afficher(r: dict) -> None:
    if not r.get("decidable"):
        print(f"indécidable : {r.get('raison')}")
        return
    print(f"empreinte : {r['lempreinte']} · pages {r['la_presence'].get('les_pages')}")
    print(f"contre 232 : {r['la_presence_contre_232']}")
    print(f"rectangle : {r['le_rectangle']}")
    if "par_largeur" in r:
        rp = r["la_reproduction"]
        print(f"contre la lecture : {r['la_presence_contre_la_lecture']}")
        print(f"reproduction : {rp['combien_de_coutures_relues']} coutures {rp['par_croisement']}, écart "
              f"{rp['lecart_le_plus_grand']}")
        for k, x in r["par_largeur"].items():
            if not x["fermable"]:
                print(f"  {k} lignes · OUVERT · trous trop longs {x['les_trous_trop_longs']}")
                continue
            print(f"  {k} lignes · L {x['la_fermeture_en_voxels']} · σ {x['la_dispersion_du_pas_en_voxels']} · nul "
                  f"{x['le_nul']} · trous {x['les_trous']} · côtés {x['les_cotes']}")
    print(f"VERDICT · {r['le_verdict']['ce_qui_reste_a_mesurer']}")


# ─────────────────────────────── la batterie ───────────────────────────────

def verifier() -> int:
    import copy
    import tempfile
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

    # la liste : deux pages, un jeton, des clés qui ne sont pas des chunks
    NS = "http://s3.amazonaws.com/doc/2006-03-01/"

    def _page(cles, jeton=None):  # noqa: E306
        c = "".join(f"<Contents><Key>{x}</Key></Contents>" for x in cles)
        t = (f"<IsTruncated>true</IsTruncated><NextContinuationToken>{jeton}</NextContinuationToken>"
             if jeton else "<IsTruncated>false</IsTruncated>")
        return f'<?xml version="1.0"?><ListBucketResult xmlns="{NS}">{t}{c}</ListBucketResult>'.encode()
    meta = {"chunks": [5, 4, 4], "shape": [5, 12, 10], "dimension_separator": "/"}
    vol = {"segment": "s", "cle": "a/b.zarr"}
    pre = "a/b.zarr/0/"
    pages = {None: _page([pre + ".zarray", pre + "0/0/0", pre + "0/1/2"], "J+/="),
             "J+/=": _page([pre + "0/2/2"])}
    demandes = []

    def _obtenir(u):  # noqa: E306
        demandes.append(u)
        if u.endswith("/.zarray"):
            return json.dumps(meta).encode()
        j = urllib.parse.parse_qs(urllib.parse.urlparse(u).query).get("continuation-token", [None])[0]
        return pages.get(j)
    pr = _sur(lister_le_depot, vol, 1.0, _obtenir)
    v("★★★★ la liste suit le jeton d'une page à l'autre, et la présence couvre les deux pages",
      pr.get("decidable") and pr["la_grille"] == [3, 3] and pr["les_pages"] == 2
      and pr["les_rangees"] == ["100", "001", "001"], str(pr))
    v("★★★ le jeton est encodé dans la requête, jamais passé brut",
      _ok(lambda: "continuation-token=J%2B%2F%3D" in demandes[-1]), str(demandes[-1:]))
    pages_p = dict(pages)
    pages_p["J+/="] = None

    def _panne(u):  # noqa: E306
        if u.endswith("/.zarray"):
            return json.dumps(meta).encode()
        j = urllib.parse.parse_qs(urllib.parse.urlparse(u).query).get("continuation-token", [None])[0]
        return pages_p.get(j)
    pp = _sur(lister_le_depot, vol, 1.0, _panne)
    v("★★★★ une page qui ne répond pas rend la liste indécidable, jamais des chunks absents",
      not pp.get("decidable") and "ne répond pas" in str(pp.get("raison")), str(pp))
    v("★★★ une clé d'un second chunk de profondeur est refusée",
      not la_presence_des_cles([pre + "1/0/0"], pre, meta).get("decidable"))
    v("★★★ une clé hors de la grille est refusée",
      not la_presence_des_cles([pre + "0/3/0"], pre, meta).get("decidable"))
    v("★★ une page tronquée sans jeton est refusée",
      not _ok(lambda: les_cles_dune_page(f'<ListBucketResult xmlns="{NS}"><IsTruncated>true</IsTruncated>'
                                         f'</ListBucketResult>'.encode())))

    # la présence contre une lecture publiée
    A = np.ones((20, 16), dtype=bool)
    A[0:3, 10:16] = False
    b = {"cle": "rangees_2", "le_sens": "rangees", "le_centre": 2, "les_lignes": [1, 2, 3], "de": 5, "a": 15}
    lec = {"rangees_2": {"les_lectures": {"1": {"refuses": {ABSENT: 6}}, "2": {"refuses": {ABSENT: 6}},
                                          "3": {"refuses": {}}}}}
    v("★★★★ les absents de la liste retombent sur ceux de la lecture, ligne par ligne",
      la_presence_retombe(A, [b], lec).get("combien_de_lignes") == 3)
    lec2 = copy.deepcopy(lec)
    lec2["rangees_2"]["les_lectures"]["2"]["refuses"][ABSENT] = 5
    v("★★★★ un chunk de trop ou de moins refuse la présence, par sa raison",
      "ne retombe pas" in str(la_presence_retombe(A, [b], lec2).get("raison")))
    lec3 = copy.deepcopy(lec)
    del lec3["rangees_2"]["les_lectures"]["3"]
    v("★★★ une ligne sans lecture publiée refuse la présence, jamais comptée juste",
      "n'a pas de lecture publiée" in str(la_presence_retombe(A, [b], lec3).get("raison")))
    bc = {"cle": "colonnes_12", "le_sens": "colonnes", "le_centre": 12, "les_lignes": [12], "de": 0, "a": 10}
    v("★★★ une ligne de colonne compte ses absents le long des rangées, bornes comprises",
      les_absents_dune_ligne(A, "colonnes", 12, 0, 10) == 3 and les_absents_dune_ligne(A, "rangees", 1, 5, 15) == 6
      and la_presence_retombe(A, [bc], {"colonnes_12": {"les_lectures": {"12": {"refuses": {ABSENT: 3}}}}})
      .get("decidable"))

    # le rectangle : contre une recherche exhaustive écrite autrement, sur des empreintes au hasard
    def _tient(A_, sens, centre, de, a, k):  # noqa: E306
        m = k
        L = les_rangees_a_lire(centre, k)
        gy, gx = A_.shape
        if min(L) < 0 or max(L) >= (gy if sens == "rangees" else gx):
            return False
        for s in range(de, a):
            n = sum(1 for l_ in L if (A_[l_, s] and A_[l_, s + 1] if sens == "rangees" else A_[s, l_] and A_[s + 1, l_]))
            if n < m:
                return False
        return True

    def _brute(A_, k):  # noqa: E306
        gy, gx = A_.shape
        best, kb = None, None
        for r0 in range(gy):
            for r1 in range(r0 + 1, gy):
                for c0 in range(gx):
                    for c1 in range(c0 + 1, gx):
                        if not (_tient(A_, "rangees", r0, c0, c1, k) and _tient(A_, "rangees", r1, c0, c1, k)
                                and _tient(A_, "colonnes", c0, r0, r1, k) and _tient(A_, "colonnes", c1, r0, r1, k)):
                            continue
                        cle = ((r1 - r0) + (c1 - c0), (r1 - r0) * (c1 - c0), -r0, -c0)
                        if kb is None or cle > kb:
                            best, kb = (r0, r1, c0, c1), cle
        return best
    g = np.random.default_rng(11)
    accord = []
    for i in range(12):
        Ar = np.ones((14, 12), dtype=bool)
        for _ in range(int(g.integers(1, 5))):
            y, x = int(g.integers(0, 14)), int(g.integers(0, 12))
            Ar[max(0, y - int(g.integers(0, 4))):y + 1, max(0, x - int(g.integers(0, 4))):x + 1] = False
        Ar &= g.random((14, 12)) > 0.04
        accord.append(le_plus_grand_rectangle(Ar, 3) == _brute(Ar, 3))
    v("★★★★ le plus grand rectangle est celui d'une recherche exhaustive, sur douze empreintes au hasard",
      all(accord), str(accord))
    Al = np.zeros((30, 24), dtype=bool)
    Al[2:28, 2:12] = True
    Al[18:28, 2:22] = True
    v("★★★★ sur une empreinte en L, le rectangle tient dans le jambage le plus long",
      le_plus_grand_rectangle(Al, 3) == _brute(Al, 3) and le_plus_grand_rectangle(Al, 3) is not None)
    v("★★★★ une bande tient quand ses neuf lignes sont présentes : quatre de marge sur la majorité, pour la texture",
      ce_quil_faut(9) == 9 and ce_quil_faut(9) - la_majorite(9) == 4)
    Am = np.ones((30, 24), dtype=bool)
    Am[0:2, :] = False
    v("★★★★ une bande dont seule la majorité des lignes est présente ne tient pas",
      _ok(lambda: not les_bandes_qui_tiennent(Am, 9)[0][4].any() and les_bandes_qui_tiennent(Am, 9)[0][6].all()))
    v("★★★ à neuf lignes, une bande dont une ligne sort de la grille ne tient pas",
      le_plus_grand_rectangle(np.ones((9, 9), dtype=bool), 9) is None)
    rr = le_rectangle_du_depot(np.ones((40, 30), dtype=bool), 9, 50)
    v("★★★★ sur une grille pleine, le rectangle est le plus extérieur que neuf lignes permettent",
      rr["les_coins"] == [4, 35, 4, 25] and rr["le_chemin"] == 52 and rr["depasse_la_moitie"])
    v("★★★ un chemin égal à celui de 224 ne le dépasse pas",
      not le_rectangle_du_depot(np.ones((40, 30), dtype=bool), 9, 52)["depasse_la_moitie"])
    iss = {_ce_qui_reste(a, b, c) for a in (True, False) for b in (True, False) for c in (True, False)}
    v("★★★★ quatre issues distinctes, et l'absence d'échelle prime, puis le trou",
      len(iss) == 4 and _ce_qui_reste(False, True, True) == _ce_qui_reste(False, False, False)
      and _ce_qui_reste(True, True, True) == _ce_qui_reste(True, True, False))

    # la mesure, sur des publications réelles, une empreinte fabriquée et une lecture qui retombe
    p219, p223, p224, p225 = ce_que_219_a_rendu(), ce_que_223_a_rendu(), ce_que_224_a_rendu(), ce_que_225_a_rendu()
    q225, q228, q232 = ce_que_225_a_publie(), ce_que_228_a_publie(), ce_que_232_a_publie()
    gy, gx = p224["la_grille"]
    Af = np.zeros((gy, gx), dtype=bool)
    Af[30:371, 40:251] = True
    presence_f = {"decidable": True, "la_grille": [gy, gx], "les_pages": 1,
                  "les_rangees": ["".join("1" if x else "0" for x in r) for r in Af]}
    q232f = copy.deepcopy(q232)
    for bb in q232f["bandes"]:
        for l_ in bb["les_lignes"]:
            q232f["publiees"][bb["cle"]]["les_lectures"][str(l_)]["refuses"][ABSENT] = \
                les_absents_dune_ligne(Af, bb["le_sens"], l_, bb["de"], bb["a"])
    src = _sur(les_sources, p219, p223, p224, q232f)
    v("★★★★ les quatre bandes de 232 contrôlent les bandes neuves, à côté de 219, 223 et 224",
      _ok(lambda: sorted(k for k in src if k.startswith("232 ")) == sorted(f"232 {bb['cle']}" for bb in q232f["bandes"])
          and "219" in src and "223" in src))
    v("★★★ l'empreinte compte les chunks du dépôt et son encadrement",
      lempreinte(Af) == {"combien": 341 * 211, "sur": int(gy) * int(gx), "les_rangees": [30, 370],
                         "les_colonnes": [40, 250]})

    def _fabrique(bd):  # noqa: E306
        gg = np.random.default_rng(len(bd["cle"]) + bd["le_centre"])
        dom = le_domaine(bd["le_sens"], bd["les_lignes"], bd["de"], bd["a"])
        pas_ = {}
        for f in ("h", "v"):
            pas_[f] = {}
            for cle in sorted(dom[f]):
                x = next((S_["pas"][f][cle] for S_ in src.values() if f in S_["pas"]
                          and cle in S_["domaine"].get(f, ()) and cle in S_["pas"][f]), None)
                vu = any(f in S_["pas"] and cle in S_["domaine"].get(f, ()) for S_ in src.values())
                if x is not None:
                    pas_[f][cle] = x
                elif not vu:
                    pas_[f][cle] = round(float(gg.normal(0.0, 1.0)), 4)
        le_long_f, trav_f = (("h", "v") if bd["le_sens"] == "rangees" else ("v", "h"))
        ll = {}
        for (r, c), x in pas_[le_long_f].items():
            a_, b_ = (r, c) if bd["le_sens"] == "rangees" else (c, r)
            ll.setdefault(a_, {})[b_] = (x, 0.0, 16)
        tt = {}
        for (r, c), x in pas_[trav_f].items():
            tt.setdefault(r, {})[c] = (x, 0.0, 16)
        lectures = {l_: {"refuses": {ABSENT: les_absents_dune_ligne(Af, bd["le_sens"], l_, bd["de"], bd["a"])}}
                    for l_ in bd["les_lignes"]}
        return {"decidable": True, "le_long": ll, "en_travers": tt, "les_lectures": lectures}
    m = _sur(mesurer, None, p219, p223, p224, p225, q225, q228, q232f, lambda: presence_f, _fabrique, 49)
    v("★★★★ une empreinte et une lecture fabriquées qui retombent passent la mesure entière",
      m.get("decidable") and "par_largeur" in m, str(m.get("raison")))
    v("★★★★ le rectangle est dérivé de l'empreinte listée, et ses bandes sont celles qu'on lit",
      _ok(lambda: m["le_rectangle"]["les_coins"] == [34, 366, 44, 246]
          and m["les_bandes_declarees"] == les_bandes_a_lire([34, 366, 44, 246], 9)), str(m.get("le_rectangle")))
    v("★★★★ la présence est contrôlée par les trente-six lignes de 232, puis par celles qu'on lit",
      _ok(lambda: m["la_presence_contre_232"]["combien_de_lignes"] == 36
          and m["la_presence_contre_la_lecture"]["combien_de_lignes"] == 36))
    v("★★★★ chaque bande neuve est contrôlée par une bande publiée",
      _ok(lambda: {k.split("×")[0] for k in m["la_reproduction"]["par_croisement"]}
          == {bd["cle"] for bd in m["les_bandes_declarees"]}), str(m.get("la_reproduction")))
    v("★★★★ la règle de 225 est appliquée, et la moitié du segment relue de 228",
      _ok(lambda: m["la_regle_appliquee"] == p225["la_regle"] and m["le_plus_long_trou_franchi_par_225"] == 17
          and m["la_moitie_du_segment"]["9"]["la_fermeture_en_voxels"]
          == json.loads((MESURES / "une_bande_plus_large_ferme_t_elle_le_grand_rectangle.json").read_text())
          ["par_largeur"]["9"]["la_fermeture_en_voxels"]))
    v("★★★★ la liste qui ne retombe pas sur 232 est refusée, par sa raison",
      "ne retombe pas" in str(_sur(mesurer, None, p219, p223, p224, p225, q225, q228, q232, lambda: presence_f,
                                   _fabrique, 49).get("raison")))

    def _menteuse(bd):  # noqa: E306
        x = _fabrique(bd)
        l0 = bd["les_lignes"][0]
        x["les_lectures"][l0]["refuses"][ABSENT] += 1
        return x
    v("★★★★ une lecture dont les absents ne sont pas ceux de la liste est refusée",
      "ne retombe pas" in str(_sur(mesurer, None, p219, p223, p224, p225, q225, q228, q232f, lambda: presence_f,
                                   _menteuse, 49).get("raison")))
    Ap = np.zeros((gy, gx), dtype=bool)
    Ap[90:301, 60:201] = True
    presence_p = {"decidable": True, "la_grille": [gy, gx], "les_pages": 1,
                  "les_rangees": ["".join("1" if x else "0" for x in r) for r in Ap]}
    q232p = copy.deepcopy(q232)
    for bb in q232p["bandes"]:
        for l_ in bb["les_lignes"]:
            q232p["publiees"][bb["cle"]]["les_lectures"][str(l_)]["refuses"][ABSENT] = \
                les_absents_dune_ligne(Ap, bb["le_sens"], l_, bb["de"], bb["a"])
    lus_p = []
    mp = _sur(mesurer, None, p219, p223, p224, p225, q225, q228, q232p, lambda: presence_p,
              lambda bd: lus_p.append(bd) or _fabrique(bd), 49)
    v("★★★★ un dépôt qui ne porte rien de plus grand que la moitié du segment ne fait rien lire",
      mp.get("decidable") and not mp["le_verdict"]["le_rectangle_depasse_la_moitie"] and not lus_p
      and "IL N'Y A RIEN AU-DELÀ" in mp["le_verdict"]["ce_qui_reste_a_mesurer"], str(mp.get("le_rectangle")))
    pg = {**presence_f, "la_grille": [gy + 1, gx]}
    v("★★★ une grille listée qui n'est pas celle des bandes est refusée",
      "pas celle que les bandes" in str(_sur(mesurer, None, p219, p223, p224, p225, q225, q228, q232f, lambda: pg,
                                             _fabrique, 49).get("raison")))
    with tempfile.TemporaryDirectory() as tmp:
        dep = Path(tmp) / "lecture.json"
        dep.write_text(json.dumps({"les_bandes": {}}))
        md = _sur(mesurer, dep, p219, p223, p224, p225, q225, q228, q232f, None, None, 49)
        dep.write_text(json.dumps({"la_presence": presence_f, "les_bandes": {"rangees_34": {}}}))
        mb = _sur(mesurer, dep, p219, p223, p224, p225, q225, q228, q232f, None, None, 49)
    v("★★★ une lecture rejouée sans la présence est refusée", "ne porte pas la présence" in str(md.get("raison")))
    with tempfile.TemporaryDirectory() as tmp:
        dep = Path(tmp) / "lecture.json"
        bl_f = les_bandes_a_lire([34, 366, 44, 246], 9)
        faux = {bd["cle"]: {**bd, "le_long": {}, "en_travers": {}, "les_lectures": {}} for bd in bl_f}
        une = next(k for k in sorted(faux) if k.startswith("colonnes"))
        faux[une]["les_lignes"] = [x - 2 for x in faux[une]["les_lignes"]]
        dep.write_text(json.dumps({"la_presence": presence_f, "les_bandes": faux}))
        mf = _sur(mesurer, dep, p219, p223, p224, p225, q225, q228, q232f, None, None, 49)
    v("★★★★ une bande lue sur d'autres lignes que celles dérivées est refusée",
      "pas celle des bandes dérivées" in str(mf.get("raison")), str(mf.get("raison")))

    def _decale(bd):  # noqa: E306
        x = _fabrique(bd)
        for r, s_ in x["en_travers"].items():
            for c in s_:
                s_[c] = (s_[c][0] + 1.0, 0.0, 16)
        return x
    v("★★★★ une lecture qui ne retombe pas sur ce qui est publié est refusée, par sa raison",
      "ne retombe pas sur" in str(_sur(mesurer, None, p219, p223, p224, p225, q225, q228, q232f, lambda: presence_f,
                                       _decale, 49).get("raison")))
    v("★★★★ une lecture qui n'est pas celle des bandes dérivées est refusée",
      "pas celle des bandes dérivées" in str(mb.get("raison")), str(mb.get("raison")))

    for e_ in echecs:
        print(f"  ÉCHEC {e_}")
    print(f"{Path(__file__).name}   "
          f"{'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--lire", type=Path, default=None)
    p.add_argument("--depuis", type=Path, default=None)
    p.add_argument("--json", type=Path, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if a.lire:
        deja = json.loads(a.lire.read_text()) if a.lire.exists() else {}
        a.lire.parent.mkdir(parents=True, exist_ok=True)
        presence = deja.get("la_presence")
        if presence is None:
            presence = lister_le_depot(le_segment_declare())
            if not presence.get("decidable"):
                print(f"indécidable : {presence.get('raison')}")
                return 1
            deja = {"la_presence": presence, "les_bandes": {}}
            a.lire.write_text(json.dumps(deja, ensure_ascii=False))
            print(f"écrit : {a.lire} (la présence, {presence['les_pages']} pages)", flush=True)
        p224 = ce_que_224_a_rendu()
        R, C = p224["R"], p224["C"]
        rect = le_rectangle_du_depot(la_grille_de_presence(presence), les_largeurs()[-1],
                                     (R[2] - R[0]) + (C[2] - C[0]))
        print(f"rectangle : {rect}", flush=True)
        if not rect["depasse_la_moitie"]:
            return 0
        bandes = les_bandes_a_lire(rect["les_coins"], les_largeurs()[-1])

        def ecrire(d):  # noqa: E306
            a.lire.write_text(json.dumps({"la_presence": presence, "les_bandes": d}, ensure_ascii=False))
            print(f"écrit : {a.lire} ({len(d)} bandes)", flush=True)
        lu = lire_les_bandes(bandes, deja.get("les_bandes") or {}, ecrire)
        if not lu.get("decidable"):
            print(f"indécidable : {lu.get('raison')}")
            return 1
        return 0
    r = mesurer(a.depuis)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=2))
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
