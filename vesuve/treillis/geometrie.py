"""La géométrie du certificat : quelles bandes tiennent, où poser les boucles, où les couper.

Tout ici se dérive de la seule grille de présence `A` (vrai quand le chunk existe dans le dépôt) et ne
lit aucun pas. C'est ce qui rend la procédure sans main : le rectangle, les ailes, la troisième ligne
et les coupes sont des fonctions de la présence, jamais d'un résultat lu (`246` §1).

Port de `src/nappe/` : `ou_sarrete_le_segment.py` (tenue, rectangle), `le_segment_au_dela_du_rectangle_se_relie_t_il.py`
(ailes, couverture), `laquelle_des_deux_colonnes_derive.py` (troisième ligne), `ou_laile_de_droite_se_separe.py`
et `le_rectangle_entre_ses_coupes.py` (coupes).
"""
from __future__ import annotations

import bisect

import numpy as np

LES_LARGEURS = (3, 5, 7, 9)  # l'échelle de `218`
LES_COTES = ("haut", "droite", "bas", "gauche")


def les_lignes(centre: int, k: int) -> list[int]:
    """Les `k` lignes contiguës d'une bande centrée en `centre`."""
    debut = int(centre) - int(k) // 2
    return list(range(debut, debut + int(k)))


# ── ce qui tient ─────────────────────────────────────────────────────────────────────────────────

def les_bandes_qui_tiennent(A: np.ndarray, k: int) -> tuple[np.ndarray, np.ndarray]:
    """`sur_la_rangee[r, s]` : la bande de rangées centrée en r a ses k lignes présentes des deux côtés
    de la couture horizontale s ; `sur_la_colonne[s, c]` de même pour la couture verticale s."""
    A = np.asarray(A, dtype=bool)
    gy, gx = A.shape
    h = int(k) // 2
    H = (A[:, :-1] & A[:, 1:]).astype(int)
    V = (A[:-1, :] & A[1:, :]).astype(int)
    rangee = np.zeros((gy, gx - 1), dtype=bool)
    ch = np.vstack([np.zeros((1, gx - 1), dtype=int), np.cumsum(H, axis=0)])
    for r in range(h, gy - h):
        rangee[r] = (ch[r + h + 1] - ch[r - h]) >= int(k)
    colonne = np.zeros((gy - 1, gx), dtype=bool)
    cv = np.hstack([np.zeros((gy - 1, 1), dtype=int), np.cumsum(V, axis=1)])
    for c in range(h, gx - h):
        colonne[:, c] = (cv[:, c + h + 1] - cv[:, c - h]) >= int(k)
    return rangee, colonne


def les_tenues(A: np.ndarray, k: int) -> tuple[np.ndarray, np.ndarray]:
    """Les coutures où une bande ne tient pas, cumulées, pour répondre à `tient` en temps constant."""
    rangee, colonne = les_bandes_qui_tiennent(A, k)
    PR = np.hstack([np.zeros((rangee.shape[0], 1), dtype=int), np.cumsum(~rangee, axis=1)])
    PC = np.vstack([np.zeros((1, colonne.shape[1]), dtype=int), np.cumsum(~colonne, axis=0)])
    return PR, PC


def tient(tenues, sens: str, centre: int, de: int, a: int) -> bool:
    """La bande `(sens, centre)` tient-elle à chaque couture de `[de, a)` ?"""
    PR, PC = tenues
    if int(a) <= int(de):
        return False
    if sens == "rangees":
        return int(PR[int(centre), int(a)] - PR[int(centre), int(de)]) == 0
    return int(PC[int(a), int(centre)] - PC[int(de), int(centre)]) == 0


def le_plus_grand_rectangle(A: np.ndarray, k: int) -> list[int] | None:
    """`[r0, r1, c0, c1]` dont les quatre bandes de k lignes tiennent, au plus long chemin
    `(r1 - r0) + (c1 - c0)`, puis la plus grande aire, puis la plus petite r0, puis la plus petite c0."""
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
                meilleur, cle_m = [int(r0), int(r1), c0, c1], cle
    return meilleur


# ── les ailes ────────────────────────────────────────────────────────────────────────────────────

def _les_coins_de_laile(cote: str, coins, debut: int, fin: int, dehors: int) -> list[int]:
    r0, r1, c0, c1 = (int(x) for x in coins)
    return {"droite": [debut, fin, c1, dehors], "gauche": [debut, fin, dehors, c0],
            "haut": [dehors, r0, debut, fin], "bas": [r1, dehors, debut, fin]}[cote]


def laile(A: np.ndarray, coins, cote: str, k: int, tenues, exclues=()) -> list[int] | None:
    """La plus grande aile d'un côté d'une portion : la plus grande aire, puis le plus long chemin, puis
    le plus petit début, puis la bande extérieure la plus proche ; ou aucune.

    La bande extérieure est à k lignes au moins de l'intérieure, et ne partage aucune ligne avec une
    bande exclue `(centre, largeur)`.
    """
    gy, gx = np.asarray(A).shape
    h = int(k) // 2
    r0, r1, c0, c1 = (int(x) for x in coins)
    if cote in ("droite", "gauche"):
        dedans, lo, hi = (c1 if cote == "droite" else c0), r0, r1
        dehors_ = range(c1 + k, gx - h) if cote == "droite" else range(h, c0 - k + 1)
        travers, exterieure = "rangees", "colonnes"
    else:
        dedans, lo, hi = (r0 if cote == "haut" else r1), c0, c1
        dehors_ = range(h, r0 - k + 1) if cote == "haut" else range(r1 + k, gy - h)
        travers, exterieure = "colonnes", "rangees"
    meilleur, cle_m = None, None
    for x in dehors_:
        if any(abs(int(x) - int(c_)) < (int(k) + int(K)) // 2
               for c_, K in ((e if isinstance(e, (list, tuple)) else (e, k)) for e in exclues)):
            continue
        a_, b_ = min(dedans, x), max(dedans, x)
        ys = [y for y in range(lo, hi + 1) if tient(tenues, travers, y, a_, b_)]
        for ya in ys:
            j0 = bisect.bisect_left(ys, ya + int(k))
            if j0 >= len(ys) or not tient(tenues, exterieure, x, ya, ys[j0]):
                continue
            g, d = j0, len(ys) - 1
            while g < d:  # le plus loin où la bande extérieure tient encore : elle tient par préfixes
                m = (g + d + 1) // 2
                if tient(tenues, exterieure, x, ya, ys[m]):
                    g = m
                else:
                    d = m - 1
            yb, larg = ys[g], b_ - a_
            cle = ((yb - ya) * larg, (yb - ya) + larg, -ya, -larg)
            if cle_m is None or cle > cle_m:
                meilleur, cle_m = (ya, yb, x), cle
    if meilleur is None:
        return None
    ya, yb, x = meilleur
    return _les_coins_de_laile(cote, coins, ya, yb, x)


def la_portion(rect, cote: str, lo: int, hi: int) -> list[int]:
    r0, r1, c0, c1 = (int(x) for x in rect)
    return [int(lo), int(hi), c0, c1] if cote in ("droite", "gauche") else [r0, r1, int(lo), int(hi)]


def le_cote_entier(rect, cote: str) -> tuple[int, int]:
    r0, r1, c0, c1 = (int(x) for x in rect)
    return (r0, r1) if cote in ("droite", "gauche") else (c0, c1)


def lexterieure(cote: str, coins) -> int:
    r0, r1, c0, c1 = (int(x) for x in coins)
    return {"droite": c1, "gauche": c0, "haut": r0, "bas": r1}[cote]


# ── la troisième ligne (`236`) ───────────────────────────────────────────────────────────────────

def les_lignes_de_laile(cote: str, coins) -> tuple[str, int, int, int, int]:
    """`(sens, intérieure, extérieure, lo, hi)` des deux longs côtés d'une aile."""
    a0, a1, b0, b1 = (int(x) for x in coins)
    return {"droite": ("colonnes", b0, b1, a0, a1), "gauche": ("colonnes", b1, b0, a0, a1),
            "haut": ("rangees", a1, a0, b0, b1), "bas": ("rangees", a0, a1, b0, b1)}[cote]


def les_coins_entre(sens: str, p: int, q: int, lo: int, hi: int) -> list[int]:
    return [int(lo), int(hi), int(p), int(q)] if sens == "colonnes" else [int(p), int(q), int(lo), int(hi)]


def la_troisieme_ligne(A: np.ndarray, coins, cote: str, k: int, tenues) -> dict | None:
    """La ligne parallèle la plus proche d'un long côté (à égalité, du côté du rectangle), qui tient sur
    toute la longueur de l'aile avec ses deux bandes de bout."""
    A = np.asarray(A, dtype=bool)
    k, h = int(k), int(k) // 2
    sens, dedans, dehors, lo, hi = les_lignes_de_laile(cote, coins)
    travers = "rangees" if sens == "colonnes" else "colonnes"
    borne = A.shape[1] if sens == "colonnes" else A.shape[0]
    bas_, haut_ = min(dedans, dehors), max(dedans, dehors)
    meilleure, cle_m = None, None
    for c in list(range(h, bas_ - k + 1)) + list(range(haut_ + k, borne - h)):
        proche = bas_ if c < bas_ else haut_
        a_, b_ = min(c, proche), max(c, proche)
        if not (tient(tenues, sens, c, lo, hi) and tient(tenues, travers, lo, a_, b_)
                and tient(tenues, travers, hi, a_, b_)):
            continue
        cle = (abs(c - proche), 0 if proche == dedans else 1)
        if cle_m is None or cle < cle_m:
            meilleure, cle_m = {"la_ligne": int(c), "le_sens": sens, "la_plus_proche": int(proche),
                                "la_plus_loin": int(dehors if proche == dedans else dedans),
                                "du_cote_du_rectangle": proche == dedans, "lecart": int(abs(c - proche))}, cle
    return meilleure


def les_trois_boucles(tl: dict, lo: int, hi: int) -> dict:
    """L'aile, l'étroite (troisième ligne et côté le plus proche), la large (jusqu'au plus loin)."""
    sens, c, p, f = tl["le_sens"], int(tl["la_ligne"]), int(tl["la_plus_proche"]), int(tl["la_plus_loin"])
    return {"laile": les_coins_entre(sens, min(p, f), max(p, f), lo, hi),
            "letroite": les_coins_entre(sens, min(c, p), max(c, p), lo, hi),
            "la_large": les_coins_entre(sens, min(c, f), max(c, f), lo, hi)}


def lexclue(nom: str, tl: dict) -> int:
    """La ligne qu'une des trois boucles n'emprunte pas."""
    return {"laile": int(tl["la_ligne"]), "letroite": int(tl["la_plus_loin"]), "la_large": int(tl["la_plus_proche"])}[nom]


# ── les coupes (`235`, `238`, `245`) ─────────────────────────────────────────────────────────────

def le_travers(cote: str, coins) -> tuple[str, int, int, int, int]:
    """`(sens, lo, hi, de, a)` : les coupes sont des bandes `sens` centrées de lo à hi, tendues de de à a."""
    a0, a1, b0, b1 = (int(x) for x in coins)
    if cote in ("droite", "gauche"):
        return "rangees", a0, a1, b0, b1
    return "colonnes", b0, b1, a0, a1


def les_sous_boucles(cote: str, coins, coupes) -> list[list[int]]:
    a0, a1, b0, b1 = (int(x) for x in coins)
    if cote in ("droite", "gauche"):
        return [[int(coupes[j]), int(coupes[j + 1]), b0, b1] for j in range(len(coupes) - 1)]
    return [[a0, a1, int(coupes[j]), int(coupes[j + 1])] for j in range(len(coupes) - 1)]


def lentre(cote: str, sb) -> list[int]:
    """Les deux coupes qui bornent une sous-boucle, le long de l'aile."""
    return [int(x) for x in (sb[:2] if cote in ("droite", "gauche") else sb[2:])]


def les_rangees_de_partage(coupes, portee: int) -> list[int]:
    """Chaque intervalle entre deux coupes, partagé en le moins de parts égales qui ne dépassent pas la portée."""
    out = []
    for a, b in zip(coupes[:-1], coupes[1:]):
        n = -(-(int(b) - int(a)) // int(portee))
        out += [int(a) + (i * (int(b) - int(a))) // n for i in range(1, n)]
    return out


def les_ecarts_au_dela(coupes, portee: int) -> list[list[int]]:
    return [[int(a), int(b)] for a, b in zip(coupes[:-1], coupes[1:]) if int(b) - int(a) > int(portee)]


def les_coupes_sans_main(coins, cote: str, portee: int, k: int, tenues, lue) -> dict:
    """Les coupes déjà lues d'abord, à k lignes au moins de la précédente et du bout ; puis chaque écart
    qui dépasse la portée, partagé en le moins de parts égales qui ne la dépassent pas, là où la bande tient."""
    k = int(k)
    sens, lo, hi, de, a = le_travers(cote, coins)
    gardees = [int(lo)]
    for y in range(int(lo) + 1, int(hi)):
        if y - gardees[-1] >= k and int(hi) - y >= k and tient(tenues, sens, y, de, a) and lue(sens, y, de, a, k):
            gardees.append(y)
    deja = gardees[1:]
    gardees.append(int(hi))
    coupes = [int(lo)]
    for a_, b_ in zip(gardees[:-1], gardees[1:]):
        for y in les_rangees_de_partage([a_, b_], portee):
            if y - coupes[-1] >= k and b_ - y >= k and tient(tenues, sens, y, de, a):
                coupes.append(int(y))
        coupes.append(int(b_))
    return {"le_sens": sens, "les_bornes": [int(de), int(a)], "les_coupes": coupes, "les_coupes_deja_lues": deja,
            "combien_de_sous_boucles": len(coupes) - 1,
            "le_plus_grand_ecart": max(b - a_ for a_, b in zip(coupes[:-1], coupes[1:])),
            "les_ecarts_au_dela_de_la_portee": les_ecarts_au_dela(coupes, portee)}


# ── la couverture ────────────────────────────────────────────────────────────────────────────────

def lentoure(forme, coins, k: int) -> np.ndarray:
    """Les chunks qu'une boucle entoure, ses bandes comprises."""
    gy, gx = (int(x) for x in forme)
    h = int(k) // 2
    r0, r1, c0, c1 = (int(x) for x in coins)
    M = np.zeros((gy, gx), dtype=bool)
    M[max(0, r0 - h):min(gy, r1 + h + 1), max(0, c0 - h):min(gx, c1 + h + 1)] = True
    return M


def la_couverture_des_boucles(A: np.ndarray, boucles) -> dict:
    """La part de l'empreinte que les boucles entourent, chacune à sa largeur."""
    A = np.asarray(A, dtype=bool)
    M = np.zeros(A.shape, dtype=bool)
    for co, k in boucles:
        M |= lentoure(A.shape, co, k)
    n, tot = int((A & M).sum()), int(A.sum())
    return {"combien": n, "sur": tot, "la_part": round(n / tot, 4) if tot else 0.0}
