"""L'arithmétique d'une boucle : le consensus de ses côtés, sa fermeture, son nul, son profil.

Une boucle de coins `(r0, r1, c0, c1)` a quatre côtés, chacun une bande. Le long d'un côté, le pas du
CONSENSUS à chaque couture est la médiane des lignes présentes, s'il y en a une majorité (`k // 2 + 1`).
Un trou de majorité d'au plus 17 coutures se franchit à pas nul (la règle « le maillage » de `225`) ;
plus long, la boucle est ouverte à cette largeur. La fermeture est

    L = H(r0 ; c0 → c1) + V(c1 ; r0 → r1) − H(r1 ; c0 → c1) − V(c0 ; r0 → r1)

et la boucle est sous le demi-feuillet quand |L| < 36 voxels (`R4-F393`). Port de `src/nappe/` :
`le_consensus_traverse_t_il_la_rangee.py`, `quest_ce_qui_franchit_le_trou_de_majorite.py`,
`deux_chemins_*.py`, `une_bande_plus_large_ferme_t_elle_le_grand_rectangle.py`,
`une_aile_plus_etroite_tient_elle.py`, `ou_laile_de_droite_se_separe.py`, `sous_laile_qui_evite_la_colonne.py`.
"""
from __future__ import annotations

import numpy as np

from vesuve import noyau
from vesuve.treillis.geometrie import LES_LARGEURS, les_lignes

LE_DEMI_FEUILLET = 36.0
L_ARRONDI = 5e-5  # une fermeture est publiée à quatre décimales


def la_majorite(k: int) -> int:
    return int(k) // 2 + 1


def les_cotes(coins) -> list[tuple]:
    """`(sens, centre, de, à, signe, nom)` : le chemin par la rangée d'abord moins celui par la colonne."""
    r0, r1, c0, c1 = coins
    return [("rangees", r0, c0, c1, +1, "haut"), ("colonnes", c1, r0, r1, +1, "droite"),
            ("rangees", r1, c0, c1, -1, "bas"), ("colonnes", c0, r0, r1, -1, "gauche")]


def le_consensus(pas: dict, minimum: int) -> dict:
    """Le pas médian à chaque couture où au moins `minimum` lignes ont lu, et rien d'autre."""
    colonnes = sorted(set().union(*[set(x) for x in pas.values()]))
    out = {}
    for c in colonnes:
        v = [pas[r][c] for r in pas if c in pas[r]]
        if len(v) >= int(minimum):
            out[int(c)] = float(np.median(v))
    return out


def les_trous(cons: dict, de: int, a: int) -> list[list[int]]:
    """Les suites de coutures sans consensus dans `[de, à)` : `[début, longueur]`."""
    out, debut = [], None
    for s in range(int(de), int(a)):
        if s not in cons:
            if debut is None:
                debut = s
        elif debut is not None:
            out.append([debut, s - debut])
            debut = None
    if debut is not None:
        out.append([debut, int(a) - debut])
    return out


def a_une_largeur(pas: dict, centre: int, k: int) -> dict:
    """Les lignes centrées d'une largeur k, et elles seules."""
    garde = set(les_lignes(centre, k))
    return {l_: s for l_, s in pas.items() if l_ in garde}


def le_consensus_franchi(pas_k: dict, k: int, de: int, a: int) -> tuple[dict, list]:
    """Le consensus à une largeur, et ses trous franchis à pas nul (« le maillage »)."""
    cons = le_consensus(pas_k, la_majorite(k))
    trous = les_trous(cons, de, a)
    for debut, n in trous:
        cons = {**cons, **{int(s): 0.0 for s in range(int(debut), int(debut) + int(n))}}
    return cons, trous


def les_sommes_par_blocs(pas, tirages: int, graine: int) -> np.ndarray:
    """Le nul : la somme d'une marche faite des pas CENTRÉS du côté, tirés par blocs de ⌈n^(1/3)⌉.

    ⚠ En numpy et non dans le noyau : ce nul ne se reproduit au bit près que dans l'ordre de sommation
    de numpy, et la graine qu'il consomme est déclarée par la mesure.
    """
    a = np.asarray(pas, dtype=float)
    a = a - float(np.mean(a))
    n = len(a)
    b = max(1, min(noyau.longueur_de_bloc(max(1, n)), n))
    k = -(-n // b)
    longueurs = np.full(k, b)
    longueurs[-1] = n - b * (k - 1)
    debuts = np.random.default_rng(int(graine)).integers(0, n - b + 1, size=(int(tirages), k))
    cs = np.concatenate(([0.0], np.cumsum(a)))
    return (cs[debuts + longueurs] - cs[debuts]).sum(axis=1)


def une_largeur(pas_par_bande: dict, coins, k: int, graine: int, tirages: int,
                demi: float = LE_DEMI_FEUILLET) -> dict:
    """À une largeur : la fermeture, sa dispersion, et le nul de ses quatre côtés tirés par blocs."""
    pas_cotes, cotes, L = {}, [], 0.0
    for sens, centre, de, a, signe, nom in les_cotes(coins):
        cons, _tr = le_consensus_franchi(a_une_largeur(pas_par_bande[(sens, centre)], centre, k), k, de, a)
        s = float(sum(float(cons[x]) for x in range(int(de), int(a))))
        L += signe * s
        pas_cotes[nom] = (signe, [float(cons[x]) for x in range(int(de), int(a))])
        cotes.append({"le_cote": nom, "la_somme_en_voxels": round(s, 4)})
    centres = [np.asarray(p, dtype=float) - float(np.mean(p)) for _s, p in pas_cotes.values()]
    disp = float(np.sqrt(sum(float(np.dot(c, c)) for c in centres) / sum(len(c) for c in centres)))
    nul = sum(sg * les_sommes_par_blocs(p, tirages, int(graine) + 101 * i)
              for i, (_nom, (sg, p)) in enumerate(sorted(pas_cotes.items())))
    an = np.abs(np.asarray(nul, dtype=float))
    return {"la_largeur": int(k), "la_fermeture_en_voxels": round(float(L), 4),
            "sous_le_demi_pli": bool(abs(L) < float(demi)), "les_cotes": cotes,
            "la_dispersion_du_pas_en_voxels": round(disp, 4),
            "le_nul": {"la_fermeture_mediane_en_valeur_absolue": round(float(np.median(an)), 4),
                       "la_part_sous_le_demi_pli": round(float(np.mean(an < float(demi))), 4),
                       "la_part_sous_la_fermeture": round(float(np.mean(an <= abs(L))), 4)}}


def une_largeur_du_segment(pas_par_bande: dict, coins, k: int, plus_long: int, graine: int, tirages: int) -> dict:
    """À une largeur : ouverte si un trou dépasse ce que `225` a franchi, sinon fermée et jugée."""
    trous = []
    for sens, centre, de, a, _signe, nom in les_cotes(coins):
        cons = le_consensus(a_une_largeur(pas_par_bande[(sens, centre)], centre, k), la_majorite(k))
        trous += [{"le_cote": nom, "le_debut": int(d), "la_longueur": int(n)} for d, n in les_trous(cons, de, a)]
    trop = [t for t in trous if t["la_longueur"] > int(plus_long)]
    if trop:
        return {"fermable": False, "la_largeur": int(k), "les_trous": trous, "les_trous_trop_longs": trop}
    return {**une_largeur(pas_par_bande, coins, k, graine, tirages), "fermable": True, "les_trous": trous}


def analyser_jusqua(pas: dict, coins, plus_long: int, graine: int, tirages: int, k: int) -> dict:
    """L'instrument à chaque largeur de l'échelle jusqu'à k : au-delà, les bandes n'ont pas les lignes."""
    return {"la_largeur_jugee": int(k),
            "par_largeur": {str(w): une_largeur_du_segment(pas, coins, w, plus_long, graine, tirages)
                            for w in LES_LARGEURS if w <= int(k)}}


# ── l'emboîtement et le profil ───────────────────────────────────────────────────────────────────

def les_longs_cotes(cote: str) -> tuple[str, str]:
    return ("gauche", "droite") if cote in ("droite", "gauche") else ("haut", "bas")


def lemboitement(par_sb: list[dict], entiere: dict, cote: str) -> str | None:
    """Là où ni la boucle ni ses sous-boucles n'ont de trou sur leurs longs côtés, les sous-boucles
    somment à la boucle, à l'arrondi près. Rend la raison d'un refus, ou None."""
    longs = les_longs_cotes(cote)

    def _troue(x):
        return any(t["le_cote"] in longs for t in x["les_trous"])
    for k in sorted(entiere["par_largeur"], key=int):
        xa, xs = entiere["par_largeur"][k], [sb["par_largeur"][k] for sb in par_sb]
        if not xa["fermable"] or _troue(xa) or any(not x["fermable"] or _troue(x) for x in xs):
            continue
        s = float(sum(float(x["la_fermeture_en_voxels"]) for x in xs))
        if abs(s - float(xa["la_fermeture_en_voxels"])) > L_ARRONDI * (len(xs) + 1) + 1e-9:
            return (f"à {k} lignes, les sous-boucles somment à {round(s, 4)} voxels et la boucle ferme à "
                    f"{xa['la_fermeture_en_voxels']} : l'emboîtement ne retombe pas")
    return None


def le_profil(par_sb: list[dict], k: int) -> list[dict]:
    """La fermeture cumulée, coupe après coupe, tant qu'aucune sous-boucle n'est ouverte."""
    cum, out = 0.0, []
    for sb in par_sb:
        x = sb["par_largeur"][str(k)]
        if not x["fermable"]:
            return out
        cum += float(x["la_fermeture_en_voxels"])
        out.append({"la_coupe": int(sb["entre"][1]), "le_cumul_en_voxels": round(cum, 4)})
    return out


def le_verdict_des_tranches(dec: dict, par_sb: list[dict], demi: float, k: int) -> dict:
    """Ouverte, ou franchit-elle le demi-feuillet à une coupe, et où est son pic."""
    ouv = [sb["entre"] for sb in par_sb if not sb["par_largeur"][str(k)]["fermable"]]
    base = {"les_ecarts_au_dela_de_la_portee": [list(x) for x in dec["les_ecarts_au_dela_de_la_portee"]]}
    if ouv:
        return {**base, "les_sous_boucles_ouvertes": ouv, "franchit": False, "le_pic": None}
    prof = le_profil(par_sb, k)
    fr = [p for p in prof if abs(float(p["le_cumul_en_voxels"])) >= float(demi)]
    return {**base, "les_sous_boucles_ouvertes": [], "franchit": bool(fr),
            "le_pic": max(prof, key=lambda p: abs(float(p["le_cumul_en_voxels"])))}


# ── les trois boucles (`236`) ────────────────────────────────────────────────────────────────────

def les_bouts(sens: str) -> tuple[str, str]:
    return ("haut", "bas") if sens == "colonnes" else ("gauche", "droite")


def lemboitement_des_trois(par: dict, sens: str, jonction: int) -> str | None:
    """Là où aucun trou ne touche la jonction sur un bout, la large est la somme des deux autres."""
    bouts = les_bouts(sens)

    def _touche(t):
        return t["le_cote"] in bouts and int(t["le_debut"]) <= int(jonction) <= int(t["le_debut"]) + int(t["la_longueur"])
    for k in sorted(par["laile"]["par_largeur"], key=int):
        xs = {n: par[n]["par_largeur"][k] for n in ("laile", "letroite", "la_large")}
        if any(not x["fermable"] or any(_touche(t) for t in x["les_trous"]) for x in xs.values()):
            continue
        s = float(xs["laile"]["la_fermeture_en_voxels"]) + float(xs["letroite"]["la_fermeture_en_voxels"])
        if abs(s - float(xs["la_large"]["la_fermeture_en_voxels"])) > 3 * L_ARRONDI + 1e-9:
            return (f"à {k} lignes, l'aile et l'étroite somment à {round(s, 4)} voxels et la large ferme à "
                    f"{xs['la_large']['la_fermeture_en_voxels']} : l'emboîtement ne retombe pas")
    return None
