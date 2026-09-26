"""Décaler le segment d'un pas puis le recaler sur la feuille retrouve-t-il sa spire voisine ?

⭐⭐⭐⭐ LE PREMIER TRANSFERT QUE LA CHAÎNE FAIT ELLE-MÊME. Pour chaque point de `20230702185753`, on part
d'un pas inter-feuilles le long de sa normale, d'un côté puis de l'autre, et on cherche la feuille dans la
fenêtre d'un demi-feuillet autour : de 36 à 108 voxels. La feuille est lue dans les deux prédictions de
surface publiées pour PHercParis4 (`m7` et `ps256`), au niveau 2 du volume à 2,4 µm, soit des voxels de
9,6 µm. La surface produite est la spire voisine, point par point.

⭐⭐⭐⭐ ET ELLE EST JUGÉE CONTRE UNE VÉRITÉ QUI N'A RIEN À VOIR AVEC LA MÉTHODE. `20230702185753` fait
plus d'un tour : `la_spire_voisine_est_elle_a_un_pas.py` mesure qu'en face de 99,7 % de ses points il y a
un autre de ses propres points, sur le tour d'avant ou d'après. Ce second point a été placé par le même
traceur humain, sans connaître cette méthode. Un transfert réussi retombe sur lui ; un transfert qui a
sauté d'une spire tombe à un pas de lui.

⚠⚠⚠ LE TÉMOIN EST CELUI QUI PRÉDIT SANS RIEN LIRE. Un décalage fixe d'un pas, sans regarder la matière,
retombe déjà sur la bonne spire partout où l'écart réel reste dans la fenêtre. Le recalage ne vaut que
s'il fait MIEUX que ce témoin, et les deux sont comptés sur les mêmes points.

⚠⚠ LA RÈGLE DE RECALAGE EST UNE, ET ELLE EST DÉCLARÉE AVANT LA MESURE : parmi les plages où la
prédiction voit de la feuille le long du rayon, garder celle dont le centre est le plus proche d'un pas.
Une seconde règle essayée après coup serait un choix fait en regardant le score.

⚠⚠ LA DEUXIÈME RÈGLE EST CELLE DE LA CHAÎNE, TRANSPOSÉE, ET ELLE EST DITE POSTÉRIEURE. La première mesure
a montré que les échecs du recalage ne sont pas isolés : ils forment des traînées et des taches, là où la
prédiction ne voit pas la feuille ou en voit une autre. C'est exactement le cas que le consensus de
`218`–`228` traite pour les pas : une ligne qui lit mal est battue par ses voisines. Transposé en deux
dimensions, avec les nombres de la chaîne et aucun autre : la médiane des neuf recalages d'un carré de
3 × 3 mailles, retenue si la majorité (cinq) a vu une feuille. Puis un second recalage vise cette médiane
au lieu du pas global, et le consensus est refait. Chaque étage est noté à part, et la première règle
garde son score : c'est elle qui a été déclarée avant de regarder.

⚠⚠ LA TROISIÈME RÈGLE, AUSSI POSTÉRIEURE, EST LE VOTE ITÉRÉ. Le second étage n'a fait qu'un tour de
vote. Itéré, chaque point vise la médiane de ses huit voisins et prend la feuille la plus proche de cette
cible, mais SEULEMENT si elle en est à moins d'un demi-feuillet : au-delà, ce serait une autre spire que
celle des voisins, et le point garde la cible. Les zones sûres propagent ainsi leur choix de proche en
proche. L'itération s'arrête quand moins d'un point sur mille change, ou au bout de trente tours.

⭐⭐⭐ LA QUATRIÈME RÈGLE SE PASSE DU PAS, ET C'EST CE QUI LA DISTINGUE. Les trois premières visent un pas
inter-feuilles : là où l'écart réel s'en éloigne de plus d'un demi-feuillet (une feuille décollée, une
zone écrasée), elles ratent par construction, exactement comme le témoin. La quatrième compte les
feuilles comme on les compterait à l'œil : le long de la normale, on passe la feuille du segment (la plage
qui couvre t = 0) et on prend la SUIVANTE, sur trois pas de portée. Aucun pas n'y entre. Ses pannes sont
d'une autre nature : une feuille manquée dans la prédiction fait sauter une spire, une fausse feuille
dans l'interstice fait tomber trop près. Elle est aussi passée au vote itéré.

⚠⚠ ET LE REPÈRE EST VÉRIFIÉ, PAS SUPPOSÉ. Le facteur entre le maillage et la prédiction est lu dans les
deux `.zarray`, jamais écrit à la main. Et un contrôle nommé exige que la prédiction voie le segment
LUI-MÊME à t = 0 : si les axes étaient permutés, elle ne le verrait nulle part, et tout le reste serait
un score sur du bruit.

Usage :
    uv run python src/nappe/le_transfert_retrouve_t_il_la_spire_voisine.py --verifier
    uv run python src/nappe/le_transfert_retrouve_t_il_la_spire_voisine.py \\
        --json docs/mesures/le_transfert_retrouve_t_il_la_spire_voisine.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))
sys.path.insert(0, str(RACINE / "src" / "tracecheck"))

from la_spire_voisine_est_elle_a_un_pas import (DEMI_PAS_EN_VOXELS, LA_FENETRE,  # noqa: E402
                                                LE_CACHE, LE_SEGMENT, LES_TEMOINS, PAS_EN_VOXELS,
                                                les_couches_du_segment, les_normales,
                                                lire_tifxyz, telecharger)
from tracecheck import get_with_reason  # noqa: E402
from zarr_depth import BUCKET, array_meta, decode  # noqa: E402

# ⚠⚠ DEUX PRÉDICTIONS PUBLIÉES, LUES AU MÊME NIVEAU (9,6 µm) ET PAR LA MÊME RÈGLE : ce n'est pas un choix
# de la meilleure, c'est la question de savoir si le résultat tient à la prédiction ou à la méthode.
LES_PREDICTIONS = {
    "m7": ("PHercParis4/representations/predictions/surfaces/"
           "20260411134726-surface-20260413222639-surface-m7-L2-th0.2.zarr", 0),
    "ps256": ("PHercParis4/representations/predictions/surfaces/"
              "20260411134726-surface-20260413141734-surface-recto-2um-ps256-L0-th0.45.zarr", 2),
}
LE_VOLUME = "PHercParis4/volumes/20260411134726-2.400um-0.2m-78keV-masked.zarr"
LA_MAILLE = 8
LE_CONTROLE = 12.0   # la demi-largeur, en voxels, où la prédiction doit voir le segment lui-même
DELAI = 120.0
LES_FILS = 16


def le_facteur(chemin: str, niveau: int, delai: float = DELAI) -> tuple[int, dict]:
    """Le rapport entier entre le volume à 2,4 µm et la prédiction, lu dans leurs deux `.zarray`."""
    vol = array_meta(f"{BUCKET}/{LE_VOLUME}", 0, delai)
    pred = array_meta(f"{BUCKET}/{chemin}", niveau, delai)
    rapports = [v / p for v, p in zip(vol["shape"], pred["shape"])]
    f = int(round(rapports[0]))
    if any(abs(r - f) > 0.01 * f for r in rapports):
        raise RuntimeError(f"le rapport des formes n'est pas le même sur les trois axes : {rapports}")
    return f, pred


def les_echantillons(p: np.ndarray, n: np.ndarray, cote: float, facteur: int) -> tuple[np.ndarray, np.ndarray]:
    """Les profondeurs t le long de chaque rayon, et l'indice (z, y, x) dans la prédiction."""
    lo, hi = LA_FENETRE
    if cote == 0:
        t = np.arange(-LE_CONTROLE, LE_CONTROLE + 1.0)
    else:
        t = cote * np.arange(np.ceil(lo), np.floor(hi) + 1.0)
    pos = p[:, None, :] + t[None, :, None] * n[:, None, :]          # (points, t, xyz)
    idx = np.floor(pos[..., ::-1] / facteur).astype(np.int64)       # (points, t, zyx)
    return t, idx


def lire_les_valeurs(idx: np.ndarray, pred: dict, lire_chunk) -> np.ndarray:
    """La valeur de la prédiction en chaque indice, chunk par chunk, sans garder les chunks en mémoire."""
    ch = np.asarray(pred["chunks"])
    forme = np.asarray(pred["shape"])
    plat = idx.reshape(-1, 3)
    dedans = np.all((plat >= 0) & (plat < forme), axis=1)
    val = np.zeros(len(plat), dtype=np.uint8)
    cles = plat // ch
    code = (cles[:, 0] * 100000 + cles[:, 1]) * 100000 + cles[:, 2]
    ordre = np.argsort(code, kind="stable")
    code_o = code[ordre]
    bornes = np.flatnonzero(np.diff(code_o)) + 1
    groupes = np.split(ordre, bornes)
    uniques = [tuple(cles[g[0]]) for g in groupes]

    def un(k):
        g, c = groupes[k], uniques[k]
        g = g[dedans[g]]
        if not len(g):
            return
        bloc = lire_chunk(c)
        if bloc is None:
            return
        loc = plat[g] - np.asarray(c) * ch
        val[g] = bloc[loc[:, 0], loc[:, 1], loc[:, 2]]

    with ThreadPoolExecutor(max_workers=LES_FILS) as pool:
        list(pool.map(un, range(len(groupes))))
    return val.reshape(idx.shape[:2])


def recaler(t: np.ndarray, vu: np.ndarray, cote: float, cibles: np.ndarray | None = None) -> np.ndarray:
    """La plage de feuille dont le centre est le plus proche de la cible ; NaN si le rayon ne voit rien.

    La cible est un pas (la règle déclarée) ou, au second étage, la médiane des voisins de chaque point.
    """
    out = np.full(vu.shape[0], np.nan)
    for k in range(vu.shape[0]):
        m = vu[k]
        if not m.any():
            continue
        cible = cote * PAS_EN_VOXELS if cibles is None or not np.isfinite(cibles[k]) else cibles[k]
        bords = np.flatnonzero(np.diff(np.concatenate([[0], m.astype(np.int8), [0]])))
        centres = [(t[a] + t[b - 1]) / 2.0 for a, b in zip(bords[::2], bords[1::2])]
        out[k] = min(centres, key=lambda c: abs(c - cible))
    return out


LE_CARRE = 3   # les neuf lignes de la chaîne (`228`), en carré de mailles
LA_MAJORITE = LE_CARRE * LE_CARRE // 2 + 1


def le_consensus(carte: np.ndarray, carre: int = LE_CARRE) -> np.ndarray:
    """La médiane des recalages d'un carré de mailles autour de chaque point, si la majorité en a vu un."""
    h, w = carte.shape
    r = carre // 2
    bord = np.pad(carte, r, constant_values=np.nan)
    pile = np.stack([bord[i:i + h, j:j + w] for i in range(carre) for j in range(carre)])
    vus = np.isfinite(pile).sum(axis=0)
    with np.errstate(all="ignore"):
        med = np.nanmedian(np.where(vus[None] > 0, pile, 0.0), axis=0)
    return np.where(vus >= carre * carre // 2 + 1, med, np.nan)


LA_PORTEE = 3.0 * PAS_EN_VOXELS   # la feuille suivante est cherchée sur trois pas


def les_echantillons_longs(p: np.ndarray, n: np.ndarray, cote: float, facteur: int) -> tuple[np.ndarray, np.ndarray]:
    """Les rayons de la feuille du segment jusqu'à trois pas, pour compter les feuilles."""
    t = cote * np.arange(0.0, np.floor(LA_PORTEE) + 1.0)
    pos = p[:, None, :] + t[None, :, None] * n[:, None, :]
    return t, np.floor(pos[..., ::-1] / facteur).astype(np.int64)


def la_feuille_suivante(t: np.ndarray, vu: np.ndarray) -> np.ndarray:
    """Le centre de la première plage de feuille APRÈS celle du segment ; NaN si le rayon n'en voit pas.

    La plage du segment est celle qui touche |t| ≤ LE_CONTROLE. Si le rayon ne voit pas le segment, la
    suivante est la première plage au-delà de LE_CONTROLE.
    """
    out = np.full(vu.shape[0], np.nan)
    a_t = np.abs(t)
    for k in range(vu.shape[0]):
        m = vu[k]
        if not m.any():
            continue
        bords = np.flatnonzero(np.diff(np.concatenate([[0], m.astype(np.int8), [0]])))
        plages = list(zip(bords[::2], bords[1::2]))
        suivantes = [(a, b) for a, b in plages if a_t[a] > LE_CONTROLE]
        propre = [(a, b) for a, b in plages if a_t[a] <= LE_CONTROLE]
        if propre:
            fin = propre[0][1]
            suivantes = [(a, b) for a, b in plages if a >= fin]
        if suivantes:
            a, b = suivantes[0]
            out[k] = (t[a] + t[b - 1]) / 2.0
    return out


LES_TOURS_DE_VOTE = 30
LE_REPOS = 1e-3   # l'itération s'arrête quand moins d'un point sur mille change


def les_centres(t: np.ndarray, vu: np.ndarray) -> list[np.ndarray]:
    """Les centres des plages de feuille vues le long de chaque rayon."""
    out = []
    for k in range(vu.shape[0]):
        m = vu[k]
        if not m.any():
            out.append(np.empty(0))
            continue
        bords = np.flatnonzero(np.diff(np.concatenate([[0], m.astype(np.int8), [0]])))
        out.append(np.array([(t[a] + t[b - 1]) / 2.0 for a, b in zip(bords[::2], bords[1::2])]))
    return out


def le_vote_itere(centres: list[np.ndarray], depart: np.ndarray, sur_la_grille, gi, gj,
                  tours: int = LES_TOURS_DE_VOTE, votant: np.ndarray | None = None) -> tuple[np.ndarray, list[int]]:
    """Chaque point vise la médiane de ses voisins et prend la feuille la plus proche à moins d'un
    demi-feuillet ; sinon il garde la cible. Rend le champ final et le nombre de points changés par tour.
    Avec `votant`, seuls les points marqués entrent dans la médiane de leurs voisins."""
    courant = depart.copy()
    changes = []
    for _ in range(tours):
        voix = courant if votant is None else np.where(votant, courant, np.nan)
        cible = le_consensus(sur_la_grille(voix))[gi, gj]
        cible = np.where(np.isfinite(cible), cible, courant)
        neuf = cible.copy()
        for k, c in enumerate(centres):
            if len(c):
                d = np.abs(c - cible[k])
                m = int(np.argmin(d))
                if d[m] < DEMI_PAS_EN_VOXELS:
                    neuf[k] = c[m]
        n_change = int((np.abs(neuf - courant) > 0.5).sum())
        changes.append(n_change)
        courant = neuf
        if n_change < LE_REPOS * len(courant):
            break
    return courant, changes


def juger(t_snap: np.ndarray, t_soi: np.ndarray, cote: float) -> dict:
    """Le transfert recalé et le témoin qui prédit sans lire, contre la couche du segment lui-même."""
    note = np.isfinite(t_soi)
    naif = cote * PAS_EN_VOXELS - t_soi[note]
    trouve = np.isfinite(t_snap[note])
    recale = t_snap[note] - t_soi[note]
    r = {"les_points_notes": int(note.sum())}
    if not note.any():
        return r
    r["le_temoin_sans_lecture"] = {
        "la_part_sur_la_bonne_spire": round(float((np.abs(naif) < DEMI_PAS_EN_VOXELS).mean()), 4),
        "lerreur_mediane_voxels": round(float(np.median(np.abs(naif))), 4)}
    ok = np.abs(recale[trouve]) < DEMI_PAS_EN_VOXELS
    r["le_recalage"] = {
        "la_part_ou_une_feuille_est_vue": round(float(trouve.mean()), 4),
        "la_part_sur_la_bonne_spire": round(float((np.abs(np.where(trouve, recale, np.inf)) < DEMI_PAS_EN_VOXELS).mean()), 4),
        "la_part_sur_la_bonne_spire_parmi_les_vues": round(float(ok.mean()), 4) if trouve.any() else None,
        "lerreur_mediane_voxels": round(float(np.median(np.abs(recale[trouve]))), 4) if trouve.any() else None,
        "lerreur_mediane_sur_la_bonne_spire": round(float(np.median(np.abs(recale[trouve][ok]))), 4) if ok.any() else None}
    return r


def la_carte_des_issues(estime: np.ndarray, t_soi: np.ndarray, sur_la_grille, present: np.ndarray) -> list[str]:
    """Une rangée de caractères par rangée de mailles : « v » la bonne spire, « x » une autre, « . » aucune
    couche en face pour juger, « o » rien d'estimé, espace hors du segment. C'est ce que la figure dessine,
    et c'est versionné avec la mesure : la figure ne relit rien d'autre."""
    e = sur_la_grille(estime)
    v = sur_la_grille(t_soi)
    lignes = []
    for i in range(e.shape[0]):
        rang = []
        for j in range(e.shape[1]):
            if not present[i, j]:
                rang.append(" ")
            elif not np.isfinite(v[i, j]):
                rang.append(".")
            elif not np.isfinite(e[i, j]):
                rang.append("o")
            else:
                rang.append("v" if abs(e[i, j] - v[i, j]) < DEMI_PAS_EN_VOXELS else "x")
        lignes.append("".join(rang).rstrip())
    return lignes


def lecteur_du_depot(pred: dict, cache: Path, nom: str, chemin: str, niveau: int, delai: float = DELAI):
    """Un chunk de la prédiction, mis en cache brut ; un chunk absent du dépôt vaut sa valeur de fond."""
    url = f"{BUCKET}/{chemin}/{niveau}"
    forme = tuple(pred["chunks"])
    attendu = int(np.prod(forme))
    stats = {"lus": 0, "absents": 0, "octets": 0, "pannes": []}

    def lire(c):
        cle = "/".join(str(int(x)) for x in c)
        f = cache / nom / f"{cle.replace('/', '_')}.blosc"
        if f.exists():
            brut = f.read_bytes()
        else:
            brut, raison = get_with_reason(f"{url}/{cle}", delai)
            if brut is None:
                if raison == "absent":
                    stats["absents"] += 1
                    return np.full(forme, pred.get("fill_value") or 0, dtype=np.uint8)
                stats["pannes"].append(f"{cle} : {raison}")
                return None
            f.parent.mkdir(parents=True, exist_ok=True)
            tmp = f.with_suffix(".tmp")
            tmp.write_bytes(brut)
            tmp.replace(f)
        stats["lus"] += 1
        stats["octets"] += len(brut)
        d = decode(brut, pred, attendu)
        if d is None:
            stats["pannes"].append(f"{cle} : taille inattendue")
            return None
        return np.frombuffer(d, dtype=np.uint8).reshape(forme)

    return lire, stats


def mesurer(cache: Path = LE_CACHE, maille: int = LA_MAILLE, delai: float = DELAI,
            segment: str = LE_SEGMENT, rangees: tuple[float, float] | None = None) -> dict:
    """Le transfert sur `segment`, restreint si demandé à une tranche de ses rangées (en fractions).

    ⚠ Une tranche de RANGÉES garde toutes les colonnes, donc tous les tours que le segment fait : c'est ce
    qui laisse à chaque point sa spire voisine dans la tranche. Les témoins tiers ne servent qu'au segment
    pour lequel ils sont nommés.
    """
    debut = time.monotonic()
    d = telecharger(segment, cache, delai)
    if isinstance(d, str):
        return {"decidable": False, "la_raison": d}
    ref, valide, esp = lire_tifxyz(d)
    if rangees is not None:
        h = ref.shape[0]
        a, b = int(h * rangees[0]), int(h * rangees[1])
        ref, valide = ref[a:b], valide[a:b]
    temoins = []
    for nom_t in (LES_TEMOINS if segment == LE_SEGMENT else {}):
        dt = telecharger(nom_t, cache, delai)
        if isinstance(dt, str):
            return {"decidable": False, "la_raison": dt}
        pts, val, _ = lire_tifxyz(dt)
        temoins.append((pts, val))
    # ⚠⚠ DEUX VÉRITÉS, NOTÉES CÔTE À CÔTE : le segment seul, et le segment avec ses témoins, qui comblent
    # les tours qu'il n'a pas tracés. Un transfert juste noté faux faute du bon tour se voit à leur écart.
    verites = {"le_segment_seul": les_couches_du_segment(ref, valide, esp, maille)["les_cartes"]}
    if temoins:
        verites["le_segment_et_ses_temoins"] = les_couches_du_segment(ref, valide, esp, maille,
                                                                      temoins=temoins)["les_cartes"]
    normales, ok = les_normales(ref, valide)
    grille = np.zeros_like(ok)
    grille[::maille, ::maille] = True
    ii, jj = np.nonzero(ok & grille)
    p, n = ref[ii, jj], normales[ii, jj]
    forme = np.full(ok.shape, np.nan)[::maille, ::maille].shape
    gi, gj = ii // maille, jj // maille

    def sur_la_grille(val):
        c = np.full(forme, np.nan)
        c[gi, gj] = val
        return c

    out = {"le_segment": segment, "les_rangees": list(rangees) if rangees else None,
           "la_maille": maille, "les_points": int(len(p)),
           "la_fenetre_voxels": [round(x, 4) for x in LA_FENETRE],
           "la_regle": "la plage de feuille dont le centre est le plus proche d'un pas",
           "les_predictions": {}}
    for nom_p, (chemin, niveau) in LES_PREDICTIONS.items():
        facteur, pred = le_facteur(chemin, niveau, delai)
        lire, stats = lecteur_du_depot(pred, cache, nom_p, chemin, niveau, delai)
        r = {"le_chemin": chemin, "le_niveau": niveau, "le_facteur": facteur}
        t0, idx0 = les_echantillons(p, n, 0, facteur)
        vu0 = lire_les_valeurs(idx0, pred, lire) > 0
        r["le_controle_du_repere"] = {"la_part_des_points_ou_la_prediction_voit_le_segment":
                                      round(float(vu0.any(axis=1).mean()), 4)}
        for nom, cote in (("du_cote_plus", 1.0), ("du_cote_moins", -1.0)):
            t, idx = les_echantillons(p, n, cote, facteur)
            vu = lire_les_valeurs(idx, pred, lire) > 0
            snap = recaler(t, vu, cote)
            cons1 = le_consensus(sur_la_grille(snap))[gi, gj]
            snap2 = recaler(t, vu, cote, cons1)
            cons2 = le_consensus(sur_la_grille(snap2))[gi, gj]
            final = np.where(np.isfinite(cons2), cons2, cote * PAS_EN_VOXELS)
            vote, changes = le_vote_itere(les_centres(t, vu), final, sur_la_grille, gi, gj)
            tl, idxl = les_echantillons_longs(p, n, cote, facteur)
            vul = lire_les_valeurs(idxl, pred, lire) > 0
            suivante = la_feuille_suivante(tl, vul)
            depart_s = np.where(np.isfinite(suivante), suivante, cote * PAS_EN_VOXELS)
            vote_s, changes_s = le_vote_itere(les_centres(tl, vul), depart_s, sur_la_grille, gi, gj)
            np.save(cache / f"transfert_{segment}_{nom_p}_{nom}.npy", sur_la_grille(vote))
            np.save(cache / f"transfert_suivante_{segment}_{nom_p}_{nom}.npy", sur_la_grille(vote_s))
            r[nom] = {}
            for verite, cartes in verites.items():
                t_soi = cartes["plus" if cote > 0 else "moins"][gi, gj]
                j = juger(snap, t_soi, cote)
                j["les_etages_posterieurs"] = {
                    "le_consensus": juger(cons1, t_soi, cote).get("le_recalage"),
                    "le_second_recalage": juger(snap2, t_soi, cote).get("le_recalage"),
                    "le_second_consensus": juger(cons2, t_soi, cote).get("le_recalage"),
                    "le_consensus_sinon_le_pas": juger(final, t_soi, cote).get("le_recalage"),
                    "le_vote_itere": juger(vote, t_soi, cote).get("le_recalage"),
                    "la_feuille_suivante": juger(suivante, t_soi, cote).get("le_recalage"),
                    "la_feuille_suivante_sinon_le_pas_puis_le_vote": juger(vote_s, t_soi, cote).get("le_recalage")}
                j["les_changements_par_tour"] = changes
                j["les_changements_par_tour_de_la_suivante"] = changes_s
                if nom_p == next(iter(LES_PREDICTIONS)) and verite == "le_segment_seul":
                    present = np.isfinite(sur_la_grille(np.zeros(len(gi))))
                    j["les_cartes"] = {
                        "sans_lecture": la_carte_des_issues(np.full(len(gi), cote * PAS_EN_VOXELS), t_soi,
                                                            sur_la_grille, present),
                        "la_feuille_suivante_puis_le_vote": la_carte_des_issues(vote_s, t_soi, sur_la_grille, present)}
                r[nom][verite] = j
                np.save(cache / f"verite_{segment}_{verite}_{nom}.npy", sur_la_grille(t_soi))
        r["la_lecture"] = {"chunks_lus": stats["lus"], "chunks_absents": stats["absents"],
                           "mo_lus": round(stats["octets"] / 1e6, 1), "les_pannes": stats["pannes"][:20],
                           "combien_de_pannes": len(stats["pannes"])}
        out["les_predictions"][nom_p] = r
    out["les_secondes"] = round(time.monotonic() - debut, 1)
    out["decidable"] = all(not r["la_lecture"]["combien_de_pannes"] for r in out["les_predictions"].values())
    return out


def afficher(r: dict) -> None:
    if "les_points" not in r:
        print(f"indécidable : {r.get('la_raison')}")
        return
    print(f"{r['les_points']} points, maille {r['la_maille']}, {r['les_secondes']} s")
    for nom_p, rp in r["les_predictions"].items():
        lec = rp["la_lecture"]
        print(f"— prédiction {nom_p} (facteur {rp['le_facteur']}) : voit le segment sur "
              f"{rp['le_controle_du_repere']['la_part_des_points_ou_la_prediction_voit_le_segment']:.3f} ; "
              f"{lec['chunks_lus']} chunks, {lec['mo_lus']} Mo, {lec['combien_de_pannes']} pannes")
        for nom in ("du_cote_plus", "du_cote_moins"):
            for verite, j in rp[nom].items():
                if "le_recalage" not in j:
                    continue
                a, b = j["le_temoin_sans_lecture"], j["le_recalage"]
                f = j["les_etages_posterieurs"]["le_consensus_sinon_le_pas"]
                w = j["les_etages_posterieurs"]["le_vote_itere"]
                print(f"  {nom:14s} {verite:26s} {j['les_points_notes']:6d} notés   sans lecture "
                      f"{a['la_part_sur_la_bonne_spire']:.3f} ({a['lerreur_mediane_voxels']:.1f} vx)   recalé "
                      f"{b['la_part_sur_la_bonne_spire']:.3f} ({b['lerreur_mediane_voxels']} vx)   consensus sinon le pas "
                      f"{f['la_part_sur_la_bonne_spire']:.3f}   vote itéré {w['la_part_sur_la_bonne_spire']:.3f} "
                      f"({w['lerreur_mediane_voxels']} vx, {len(j['les_changements_par_tour'])} tours)")
                fs = j["les_etages_posterieurs"]["la_feuille_suivante"]
                vs = j["les_etages_posterieurs"]["la_feuille_suivante_sinon_le_pas_puis_le_vote"]
                print(f"  {'':41s} feuille suivante {fs['la_part_sur_la_bonne_spire']:.3f} "
                      f"(vue {fs['la_part_ou_une_feuille_est_vue']:.3f}, {fs['lerreur_mediane_voxels']} vx)   "
                      f"puis vote {vs['la_part_sur_la_bonne_spire']:.3f} ({vs['lerreur_mediane_voxels']} vx)")


# ---------------------------------------------------------------------------------------------------
def verifier() -> int:
    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        if not ok:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    # ⭐⭐⭐⭐ LA RÈGLE, sur un rayon fabriqué : deux plages de feuille, celle retenue est la plus proche d'un pas.
    t = np.arange(36.0, 109.0)
    vu = np.zeros((1, len(t)), bool)
    vu[0, (t >= 40) & (t <= 44)] = True
    vu[0, (t >= 80) & (t <= 86)] = True
    v("★★★★ entre deux feuilles vues, la règle garde la plus proche d'un pas", recaler(t, vu, 1.0)[0] == 83.0,
      str(recaler(t, vu, 1.0)[0]))
    v("★★★ un rayon qui ne voit rien ne recale pas", np.isnan(recaler(t, np.zeros((1, len(t)), bool), 1.0)[0]))
    tm = -t
    v("★★★ de l'autre côté la cible est moins un pas", recaler(tm, vu, -1.0)[0] == -83.0)

    # ⭐⭐⭐⭐ LE JUGE : un recalage qui retombe sur la couche du segment est sur la bonne spire, le témoin
    # sans lecture ne l'est que si l'écart réel est dans la fenêtre.
    t_soi = np.array([72.0, 100.0, 120.0, np.nan])
    snap = np.array([73.0, 99.0, 121.0, 70.0])
    j = juger(snap, t_soi, 1.0)
    v("★★★★ un point sans couche en face n'est pas noté", j["les_points_notes"] == 3)
    v("★★★★ le témoin sans lecture rate l'écart de 120 et tient les deux autres",
      j["le_temoin_sans_lecture"]["la_part_sur_la_bonne_spire"] == round(2 / 3, 4))
    v("★★★★ le recalage qui retombe sur la couche est sur la bonne spire partout",
      j["le_recalage"]["la_part_sur_la_bonne_spire"] == 1.0)
    faux = juger(np.array([72.0 + 72.0, np.nan, 121.0, 0.0]), t_soi, 1.0)
    v("★★★★ un recalage parti d'une spire, ou qui ne voit rien, est compté raté",
      faux["le_recalage"]["la_part_sur_la_bonne_spire"] == round(1 / 3, 4),
      str(faux["le_recalage"]["la_part_sur_la_bonne_spire"]))


    # ⭐⭐⭐ LE CONSENSUS : un point qui a lu une autre feuille est battu par ses huit voisins, un trou isolé
    # est comblé, et un carré où la majorité n'a rien vu reste vide plutôt que d'inventer.
    c = np.full((5, 5), 70.0)
    c[2, 2] = 142.0
    c[1, 3] = np.nan
    k = le_consensus(c)
    v("★★★★ un recalage parti d'une spire est battu par ses voisins", k[2, 2] == 70.0, str(k[2, 2]))
    v("★★★ un trou isolé est comblé par ses voisins", k[1, 3] == 70.0, str(k[1, 3]))
    vide = np.full((5, 5), np.nan)
    vide[2, 2] = 70.0
    vide[2, 3] = 70.0
    v("★★★★ sans majorité, le consensus ne dit rien", np.isnan(le_consensus(vide)[2, 2]))
    v("★★ la majorité est celle de la chaîne, cinq sur neuf", LA_MAJORITE == 5)
    # ⚠⚠ LE SECOND RECALAGE vise la médiane des voisins : entre deux feuilles, il prend celle qu'elle désigne.
    v("★★★★ le second recalage prend la feuille que la médiane désigne, pas celle du pas global",
      recaler(t, vu, 1.0, np.array([43.0]))[0] == 42.0)

    # ⭐⭐⭐⭐ LE VOTE ITÉRÉ : une traînée d'une rangée partie sur l'autre spire est ramenée par ses voisins.
    H, W = 9, 9
    gi_, gj_ = np.nonzero(np.ones((H, W), bool))

    def grille_(val):
        c = np.full((H, W), np.nan)
        c[gi_, gj_] = val
        return c

    vrai = np.full(H * W, 70.0)
    centres_ = [np.array([70.0, 142.0]) for _ in range(H * W)]   # chaque rayon voit les deux feuilles
    depart = vrai.copy()
    depart[gi_ == 4] = 142.0
    fin, ch = le_vote_itere(centres_, depart, grille_, gi_, gj_)
    v("★★★★ le vote itéré ramène une traînée d'une rangée sur la spire de ses voisins",
      np.all(np.abs(fin - vrai) < 1.0), str(np.round(fin.reshape(H, W)[4], 1)))
    v("★★★ et il s'arrête au repos", ch[-1] < LE_REPOS * H * W + 1, str(ch))
    # ⚠⚠⚠ MAIS UNE TACHE PLUS LARGE QUE LE DEMI-CARRÉ RESTE OÙ ELLE EST : une médiane garde ce que la
    # majorité dit, et au cœur d'une bande de trois rangées la majorité est la bande. Le vote ne répare
    # donc que les pannes fines ; c'est une propriété, et elle est assertée pour ne pas être oubliée.
    epais = vrai.copy()
    epais[(gi_ >= 3) & (gi_ <= 5)] = 142.0
    fin3, _ = le_vote_itere(centres_, epais, grille_, gi_, gj_)
    v("★★★★ une bande de trois rangées partie sur l'autre spire n'est PAS ramenée par le vote",
      np.all(np.abs(fin3.reshape(H, W)[4] - 142.0) < 1.0), str(np.round(fin3.reshape(H, W)[4], 1)))
    # ⚠⚠⚠ UNE FEUILLE À PLUS D'UN DEMI-FEUILLET DE LA CIBLE N'EST PAS PRISE : le point garde la cible.
    loin_ = [np.array([140.0]) for _ in range(H * W)]
    fin2, _ = le_vote_itere(loin_, vrai.copy(), grille_, gi_, gj_)
    v("★★★★ une feuille à plus d'un demi-feuillet des voisins n'est pas prise", np.all(np.abs(fin2 - 70.0) < 1.0))

    # ⭐⭐⭐ LA FEUILLE SUIVANTE : on passe la sienne et on prend la suivante, quel que soit l'écart.
    tl = np.arange(0.0, 217.0)
    ray = np.zeros((3, len(tl)), bool)
    ray[:, :4] = True                                   # la feuille du segment, à t = 0
    ray[0, 120:126] = True                              # une feuille décollée, à 122
    ray[1, 40:44] = True                                # une zone écrasée, à 41
    ray[1, 90:95] = True
    ray[2, 4:6] = False
    sv = la_feuille_suivante(tl, ray)
    v("★★★★ derrière une feuille décollée, la suivante est à 122 même si un pas en vaut 72",
      sv[0] == 122.5, str(sv[0]))
    v("★★★★ dans une zone écrasée, la suivante est la première, à 41", sv[1] == 41.5, str(sv[1]))
    v("★★★ un rayon qui ne voit que le segment n'a pas de suivante", np.isnan(sv[2]))
    sans_soi = np.zeros((1, len(tl)), bool)
    sans_soi[0, 70:76] = True
    v("★★★ si le rayon ne voit pas le segment, la suivante est la première au-delà du contrôle",
      la_feuille_suivante(tl, sans_soi)[0] == 72.5)
    v("★★ et elle se lit de l'autre côté aussi", la_feuille_suivante(-tl, ray)[0] == -122.5)

    # ⚠ LA CARTE DES ISSUES dit la bonne spire, une autre, rien à juger, rien d'estimé, et le dehors.
    gi2, gj2 = np.array([0, 0, 0, 0]), np.array([0, 1, 2, 3])

    def g2(val):
        c = np.full((1, 5), np.nan)
        c[gi2, gj2] = val
        return c

    carte = la_carte_des_issues(np.array([72.0, 150.0, np.nan, 72.0]), np.array([70.0, 72.0, 72.0, np.nan]), g2,
                                np.isfinite(g2(np.zeros(4))))
    v("★★★ la carte des issues code chaque cas par son caractère", carte == ["vxo."], str(carte))
    # ⚠⚠⚠ LE REPÈRE : une prédiction fabriquée, deux feuilles en z, lue chunk par chunk à travers le vrai
    # chemin. Un rayon à travers une frontière de chunk doit lire les deux chunks.
    f = 4
    pred = {"shape": [64, 64, 64], "chunks": [16, 16, 16], "fill_value": 0}
    vol = np.zeros(pred["shape"], np.uint8)
    z0 = 30   # la feuille du segment, en voxels de prédiction
    vol[z0, :, :] = 255
    ecart = 20  # la voisine, à 20 voxels de prédiction = 80 voxels du maillage
    vol[z0 + ecart, :, :] = 255
    lus = []

    def lire(c):
        lus.append(c)
        a = np.asarray(c) * 16
        return vol[a[0]:a[0] + 16, a[1]:a[1] + 16, a[2]:a[2] + 16]

    p = np.array([[100.0, 100.0, z0 * f + 2.0], [140.0, 60.0, z0 * f + 2.0]])
    n = np.array([[0.0, 0.0, 1.0], [0.0, 0.0, 1.0]])
    t0, i0 = les_echantillons(p, n, 0, f)
    vu0 = lire_les_valeurs(i0, pred, lire) > 0
    v("★★★★ la prédiction voit le segment lui-même à t = 0", vu0.any(axis=1).all())
    tp, ip = les_echantillons(p, n, 1.0, f)
    s = recaler(tp, lire_les_valeurs(ip, pred, lire) > 0, 1.0)
    v("★★★★ le recalage retrouve la voisine à son vrai écart, à un voxel de prédiction près",
      np.all(np.abs(s - (ecart * f - 2.0 + f / 2.0)) <= f), str(s))
    v("★★★ le rayon a traversé plusieurs chunks", len(set(lus)) >= 2, str(set(lus)))
    tm, im = les_echantillons(p, n, -1.0, f)
    v("★★★ de l'autre côté il n'y a rien, et rien n'est inventé",
      np.isnan(recaler(tm, lire_les_valeurs(im, pred, lire) > 0, -1.0)).all())
    # ⚠⚠ UN AXE PERMUTÉ : la feuille est un plan de z, lire en (x, y, z) ne la voit plus à t = 0.
    idx_faux = i0[..., ::-1]
    v("★★★★ des axes permutés font tomber le contrôle du repère",
      not (lire_les_valeurs(idx_faux, pred, lire) > 0).any(axis=1).all())
    # ⚠ UN INDICE HORS DU VOLUME VAUT LE FOND, jamais une valeur voisine.
    loin = np.array([[1e6, 1e6, 1e6]])
    tl, il = les_echantillons(loin, n[:1], 0, f)
    v("★★ un rayon hors du volume ne voit rien", not (lire_les_valeurs(il, pred, lire) > 0).any())

    for e_ in echecs:
        print(f"  ÉCHEC {e_}")
    print(f"{Path(__file__).name}   "
          f"{'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} ({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path, default=None)
    p.add_argument("--maille", type=int, default=LA_MAILLE)
    p.add_argument("--delai", type=float, default=DELAI)
    p.add_argument("--segment", default=LE_SEGMENT)
    p.add_argument("--rangees", type=float, nargs=2, default=None, metavar=("DEBUT", "FIN"),
                   help="une tranche des rangées du segment, en fractions")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(LE_CACHE, a.maille, a.delai, a.segment, tuple(a.rangees) if a.rangees else None)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=2))
        print(f"\nécrit : {a.json}")
    return 0 if r.get("decidable") else 2


if __name__ == "__main__":
    raise SystemExit(main())
