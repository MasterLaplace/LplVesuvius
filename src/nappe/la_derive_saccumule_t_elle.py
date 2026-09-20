"""La dérive s'accumule-t-elle le long d'une spire, ou les écarts se compensent-ils ?

⭐⭐⭐⭐ POURQUOI CE FICHIER, ET C'EST `R4-P47` QUI LE NOMME. `198` a mesuré le serpentement LOCAL en
cent quatre-vingt-neuf endroits d'un segment et a établi qu'il ne se groupe pas. Mais un treillis
**saute** d'un endroit à l'autre : il ne peut rien dire de ce qui s'additionne **entre** eux. Or
c'est l'accumulation qui fait perdre une feuille — un demi-voxel par chunk sur trois cents chunks
est un pli entier, et chaque mesure locale y paraîtrait irréprochable.

⭐⭐⭐⭐ LA QUESTION SE POSE DONC SUR UNE LIGNE DE CHUNKS CONTIGUS, et elle change de nature : il ne
s'agit plus de recaler un chunk sur LUI-MÊME mais **sur son voisin**. Ce qui est mesuré est le PAS
d'une couture à l'autre, puis sa somme.

⚠⚠⚠ ET LA SEULE QUESTION DÉCLARÉE EST CELLE-CI : les pas **s'additionnent-ils** ou se
**compensent-ils** ? Une marche au hasard de `n` pas dérive comme la racine de `n` ; une dérive
systématique dérive comme `n`. Le nul est donc le **tirage des SIGNES** des pas observés, qui garde
leurs tailles et détruit leur ordre de marche — et c'est le seul nul qui réponde à cette question,
puisque permuter les pas laisse leur somme inchangée.

⚠⚠ ET DEUX LIMITES SONT NOMMÉES. La première : un pas plus grand qu'une demi-période se confond avec
un pas en arrière, donc le compte de pas qui **saturent** est publié le long de la ligne. La
seconde : un chunk manquant **coupe** la contiguïté, donc la ligne se lit en **tronçons** et la
dérive s'accumule à l'intérieur de chacun, jamais par-dessus un trou.

Usage :
    uv run python src/nappe/la_derive_saccumule_t_elle.py --verifier
    uv run python src/nappe/la_derive_saccumule_t_elle.py \\
        --json docs/mesures/la_derive_saccumule_t_elle.json
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

from la_recette_posee_sur_le_rouleau import DELAI, PERMUTATIONS  # noqa: E402
from ou_le_maillage_quitte_t_il_son_feuillet import (ABSENT_DU_DEPOT,  # noqa: E402
                                                     LE_RESEAU_A_ECHOUE,
                                                     lattente_avant_le_prochain_essai,
                                                     le_segment_declare,
                                                     les_pannes_de_reseau, un_chunk)
from ouvrir_les_quinze import _rng  # noqa: E402
from combien_dinterstices_traverses import VOXEL_FIN_UM  # noqa: E402
from que_montrent_ces_deux_vues import (DEMI_PAS_EN_VOXELS,  # noqa: E402
                                        PAS_EN_VOXELS, la_rangee_montree, une_section)
from zarr_depth import BUCKET, array_meta  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
CE_QUE_LA_CARTE_A_RENDU = MESURES / "ou_le_maillage_quitte_t_il_son_feuillet.json"
GRAINE = 20261007

LA_QUESTION_DECLAREE = "les pas s'additionnent-ils, ou se compensent-ils ?"

# ⚠⚠ L'ATTENTE ENTRE DEUX ESSAIS EST UN BUDGET, ET LA MESURE L'A EXIGEE : une ligne de deux cent
# quatre-vingt-cinq chunks a perdu cent cinquante-deux requetes sur des echecs de resolution de nom,
# et AUCUNE reprise n'a abouti parce que les quatre essais tenaient dans quelques millisecondes.
LA_PAUSE_ENTRE_ESSAIS = 0.5
REPLICATS = 20


def la_largeur_du_bord(chemin: Path = CE_QUE_LA_CARTE_A_RENDU, cote: int = 128) -> int:
    """La largeur de la bande de bord — DÉRIVÉE du serpentement que `198` a publié.

    ⭐⭐⭐⭐ UN PAS SE MESURE AU BORD, PAS SUR TOUT LE CHUNK : ce qu'on veut est la discontinuité à la
    COUTURE, et moyenner un chunk entier la noierait dans son propre serpentement. Reste à savoir
    quelle largeur de bande on peut moyenner sans que la bande serpente elle-même.

    ⚠⚠ LA REGLE EST UNE TOLERANCE D'UN VOXEL, et le chiffre vient de `198` : son serpentement median
    vaut `m` voxels sur `cote` colonnes, donc une bande de `w` colonnes serpente de `w·m/cote`, et on
    prend la plus grande puissance de deux qui garde cela sous un voxel. Aucun nombre n'est tape.

    ⚠ Sans la mesure de `198`, la fonction RE FUSE de deviner : elle rend la plus petite largeur
    utile, et le fait savoir par son compte de colonnes.
    """
    m = None
    if Path(chemin).is_file():
        d = json.loads(Path(chemin).read_text(encoding="utf-8"))
        m = (d.get("les_quantiles") or {}).get("le_median_en_voxels")
    if not m or float(m) <= 0.0:
        return 1
    plafond = float(cote) / float(m)
    w = 1
    while w * 2 <= plafond:
        w *= 2
    return int(w)


def la_ligne_declaree(gy: int) -> int:
    """La rangée MÉDIANE de la grille de chunks — la seule nommable sans avoir rien regardé."""
    return int(gy) // 2


def un_pas(gauche: np.ndarray, droite: np.ndarray, largeur: int,
           plage: int = DEMI_PAS_EN_VOXELS) -> dict:
    """Le décalage en profondeur qui aligne le bord GAUCHE de `droite` sur le bord DROIT de `gauche`.

    ⚠⚠⚠ LA PLAGE EST LA DEMI-PERIODE, ET C'EST UNE BORNE : un pas plus grand se confond avec un pas
    en arriere d'un pli. Le compte de pas qui saturent est publie a cote, sinon une couture qui a
    saute une feuille entiere se lirait comme une couture parfaite.
    """
    g, d = np.asarray(gauche, dtype=float), np.asarray(droite, dtype=float)
    if g.ndim != 2 or d.ndim != 2 or g.shape[0] != d.shape[0]:
        return {"decidable": False, "raison": "coupes incompatibles"}
    w = max(1, min(int(largeur), g.shape[1], d.shape[1]))
    a = g[:, -w:].mean(axis=1)
    b = d[:, :w].mean(axis=1)
    a, b = a - a.mean(), b - b.mean()
    if float(np.dot(a, a)) <= 0.0 or float(np.dot(b, b)) <= 0.0:
        return {"decidable": False, "raison": "bord plat"}
    p = int(min(int(plage), (len(a) - 1) // 2))
    if p < 1:
        return {"decidable": False, "raison": "plage nulle"}
    # ⚠⚠⚠ LA CORRELATION EST NORMALISEE PAR L'ENERGIE DES DEUX FENETRES, ET NON PAR LEUR LONGUEUR,
    # PARCE QUE CE PAS S'ACCUMULE. Une division par la longueur suffit a estimer un ETALEMENT — c'est
    # ce que `197` et `198` mesurent — mais elle deplace le maximum d'un voxel quand la fenetre ne
    # porte qu'un pli et demi, et un voxel de biais repete trois cents fois fait quatre plis.
    scores = []
    for k in range(-p, p + 1):
        aa = a[max(0, k):len(a) + min(0, k)]
        bb = b[max(0, -k):len(b) + min(0, -k)]
        e = float(np.dot(aa, aa)) * float(np.dot(bb, bb))
        scores.append(float(np.dot(aa, bb)) / (e ** 0.5) if e > 0.0 else -1.0)
    # ⚠⚠ LE SIGNE EST CELUI DU DEPLACEMENT DU CHUNK DE DROITE, et la premiere version le rendait a
    # l'envers : l'argmax de la correlation croisee vaut MOINS le decalage cherche.
    k = -(int(np.argmax(scores)) - p)
    return {"decidable": True, "le_pas_en_voxels": int(k), "la_plage": int(p),
            "il_sature": bool(abs(k) >= p), "la_largeur_du_bord": int(w)}


def les_troncons(lus: dict, colonnes: list[int]) -> list[list[int]]:
    """Les suites de colonnes CONTIGUËS effectivement lues — un trou coupe la ligne.

    ⚠⚠⚠ LA DERIVE NE S'ACCUMULE PAS PAR-DESSUS UN TROU : deux chunks separes par un chunk absent ne
    sont pas voisins, et recaler l'un sur l'autre inventerait un pas que personne n'a mesure.
    """
    out, courant = [], []
    for c in colonnes:
        if c in lus:
            courant.append(int(c))
            continue
        if len(courant) > 1:
            out.append(courant)
        courant = []
    if len(courant) > 1:
        out.append(courant)
    return out


def la_marche(sections: dict, troncons: list[list[int]], largeur: int,
              plage: int = DEMI_PAS_EN_VOXELS) -> dict:
    """Les pas d'une couture à l'autre, et ce qu'ils font en s'accumulant."""
    pas, par_troncon, satures = [], [], 0
    for tr in troncons:
        ici = []
        for a, b in zip(tr, tr[1:]):
            r = un_pas(sections[a], sections[b], largeur, plage)
            if not r.get("decidable"):
                continue
            ici.append(int(r["le_pas_en_voxels"]))
            satures += int(r["il_sature"])
        if not ici:
            continue
        cumul = np.cumsum(ici)
        par_troncon.append({
            "colonnes": [int(tr[0]), int(tr[-1])], "chunks": len(tr), "pas": len(ici),
            # ⭐⭐⭐⭐ LA TRACE CUMULEE EST PUBLIEE PAR LE PRODUCTEUR : c'est l'accumulation
            # elle-meme, donc la chose que cette tranche mesure, et une figure qui la recalculerait
            # en serait une SECONDE definition. ⚠ Elle est rendue TRONCON PAR TRONCON, jamais d'un
            # bout a l'autre : accumuler par-dessus un trou inventerait un pas que personne n'a lu.
            "le_cumul_en_voxels": [int(x) for x in cumul],
            "le_deplacement_net_en_voxels": int(cumul[-1]),
            "le_deplacement_net_en_plis": round(float(cumul[-1]) / PAS_EN_VOXELS, 6),
            "lexcursion_maximale_en_voxels": int(np.max(np.abs(cumul))),
            "lexcursion_maximale_en_plis": round(float(np.max(np.abs(cumul)))
                                                 / PAS_EN_VOXELS, 6)})
        pas.extend(ici)
    if not pas:
        return {"decidable": False, "raison": "aucun pas lisible"}
    a = np.asarray(pas, dtype=float)
    return {"decidable": True, "les_pas": len(pas), "les_troncons": par_troncon,
            "les_pas_qui_saturent": int(satures),
            "le_pas_median_en_voxels": round(float(np.median(np.abs(a))), 4),
            "le_pas_quadratique_en_voxels": round(float(np.sqrt(float(np.mean(a * a)))), 4),
            "le_deplacement_net_en_voxels": int(np.sum(a)),
            "le_deplacement_net_en_plis": round(float(np.sum(a)) / PAS_EN_VOXELS, 6),
            "lexcursion_maximale_en_plis": (
                round(max((abs(float(t["lexcursion_maximale_en_plis"]))
                           for t in par_troncon), default=0.0), 6)),
            "les_pas_en_voxels": [int(x) for x in pas]}


def combien_de_chunks_avant(pas_quadratique: float, distance_en_voxels: float,
                            cote: int = 128) -> dict:
    """Après combien de chunks une marche au hasard de ce pas atteint cette distance ?

    ⭐⭐⭐⭐ C'EST LE NOMBRE QUE LA TRANCHE EXISTE POUR RENDRE. Dire « les pas se compensent » se lit
    comme une bonne nouvelle, et c'en est une seulement si la marche reste petite. Or une marche au
    hasard DERIVE : elle avance comme la racine du nombre de pas, donc la question utile n'est pas
    « y a-t-il un biais » mais « au bout de combien de coutures le feuillet est-il perdu ».

    ⚠ La reponse est exacte et sans reglage : `n = (distance / pas)²`, puis la largeur en
    millimetres suit du cote d'un chunk et du voxel.
    """
    q = float(pas_quadratique)
    if q <= 0.0:
        return {"decidable": False, "raison": "pas quadratique nul"}
    n = (float(distance_en_voxels) / q) ** 2
    return {"decidable": True, "les_chunks": round(n, 2),
            "la_largeur_en_mm": round(n * float(cote) * VOXEL_FIN_UM / 1000.0, 3)}


def contre_les_signes(pas, tirages: int = PERMUTATIONS, graine: int = GRAINE) -> dict:
    """Le déplacement net dépasse-t-il celui de TOUS les tirages de signes des mêmes pas ?

    ⭐⭐⭐⭐ C'EST LE SEUL NUL QUI REPONDE A LA QUESTION. Permuter les pas laisse leur somme
    INCHANGEE, donc un nul par permutation serait vide par construction — le defaut que `179` a paye
    sous un autre costume. Tirer les SIGNES garde les tailles et remplace la marche observee par une
    marche au hasard : si les pas s'additionnent, l'observe dépasse ; s'ils se compensent, non.
    """
    a = np.asarray(list(pas), dtype=float)
    if len(a) < 2:
        return {"decidable": False, "raison": "moins de deux pas"}
    obs = abs(float(np.sum(a)))
    r = _rng(graine)
    nuls = []
    for _ in range(int(tirages)):
        signes = r.integers(0, 2, size=len(a)) * 2 - 1
        nuls.append(abs(float(np.sum(a * signes))))
    au_moins = int(sum(1 for x in nuls if x >= obs))
    quad = float(np.sqrt(float(np.sum(a * a))))
    return {"decidable": True, "tirages": int(tirages),
            "le_deplacement_net_en_voxels": round(obs, 4),
            "le_deplacement_du_nul_median_en_voxels": round(float(np.median(nuls)), 4),
            "les_tirages_au_moins_aussi_loin": au_moins,
            "la_marche_au_hasard_en_voxels": round(quad, 4),
            "combien_de_marches_au_hasard": round(obs / quad, 4) if quad > 0 else None,
            "ca_saccumule": bool(au_moins == 0)}


def une_ligne_fabriquee(chunks: int, couches: int, colonnes: int, pas_pose: float,
                        bruit: float, graine: int, periode: float = PAS_EN_VOXELS) -> dict:
    """Une ligne de coupes dont la dérive est CONSTRUITE — systématique ou au hasard.

    ⚠⚠ `pas_pose` NUL rend une marche au hasard de meme taille de pas : les deux faces portent donc
    le MEME bruit et ne different que par la presence d'un biais.
    """
    r = _rng(graine)
    out, offset = {}, 0.0
    z = np.arange(int(couches), dtype=float)[:, None]
    for c in range(int(chunks)):
        offset += float(pas_pose) + float(r.normal(0.0, bruit))
        x = np.arange(int(colonnes), dtype=float)[None, :]
        out[c] = 120.0 + 40.0 * np.cos(2.0 * np.pi * (z - offset) / float(periode)) \
            + r.normal(0.0, 1.0, size=(int(couches), int(colonnes)))
    return out


def la_part_vue(pas_pose: float, bruit: float, chunks: int, replicats: int,
                tirages: int, graine: int, largeur: int = 16) -> dict:
    """La part des réplicats où une ligne de ce biais est déclarée accumulée."""
    vus = 0
    for k in range(int(replicats)):
        secs = une_ligne_fabriquee(chunks, 109, 64, pas_pose, bruit, int(graine) + k)
        m = la_marche(secs, [list(range(int(chunks)))], largeur)
        if not m.get("decidable"):
            continue
        vus += int(bool(contre_les_signes(m["les_pas_en_voxels"], tirages,
                                          int(graine) + k).get("ca_saccumule")))
    return {"vus": int(vus), "replicats": int(replicats),
            "la_part": float(vus) / float(replicats)}


def sur_letalon(tirages: int = PERMUTATIONS, graine: int = GRAINE,
                replicats: int = REPLICATS, chunks: int = 24, bruit: float = 2.0,
                echelle=(0.0, 0.5, 1.0, 2.0, 4.0)) -> dict:
    """Les deux faces : une dérive systématique s'accumule, une marche au hasard non.

    ⚠⚠⚠ LES DEUX FACES SONT MESUREES SUR REPLICATS — la lecon que `198` a payee : une face negative
    jugee sur un tirage unique tombe du mauvais cote une fois sur vingt par construction.
    """
    courbe, trouvee = [], None
    for f in echelle:
        x = la_part_vue(f, bruit, chunks, replicats, tirages, graine)
        courbe.append({"le_biais_pose": float(f), "part_des_replicats": float(x["la_part"])})
        if trouvee is None and f > 0.0 and x["la_part"] >= 1.0:
            trouvee = float(f)
    faux = la_part_vue(0.0, bruit, chunks, replicats, tirages, graine)
    garantie = 1.0 / (int(tirages) + 1)
    return {"la_courbe": courbe, "le_biais_quil_faut": trouvee,
            "replicats": int(replicats), "les_chunks": int(chunks), "le_bruit": float(bruit),
            "le_taux_de_faux": float(faux["la_part"]), "les_faux": int(faux["vus"]),
            "la_garantie": float(garantie),
            "letalon_separe": bool(trouvee is not None
                                   and faux["la_part"] <= float(garantie) + 1e-12)}


def la_ligne(volume: dict, delai: float = DELAI, colonnes: int | None = None,
             ouvrir=None, meta=None, chercher=None) -> dict:
    """Les coupes de TOUS les chunks d'une rangée du segment, dans l'ordre."""
    url = f"{BUCKET}/{volume['cle']}"
    if meta is None:
        try:
            meta = array_meta(url, 0, delai)
        except Exception as e:  # noqa: BLE001
            return {"decidable": False, "raison": f"le volume ne répond pas : {type(e).__name__}"}
    prof, hy, hx = meta["chunks"]
    _, rows, cols = meta["shape"]
    gy, gx = -(-rows // hy), -(-cols // hx)
    ligne = la_ligne_declaree(gy)
    voulues = list(range(gx if colonnes is None else min(int(colonnes), gx)))
    prendre = ouvrir or (lambda cy, cx: un_chunk(url, meta, cy, cx, delai, chercher,
                                                pause=LA_PAUSE_ENTRE_ESSAIS))
    sections, refus, reprises = {}, {}, 0
    for cx in voulues:
        bloc, pourquoi = prendre(int(ligne), int(cx))
        if bloc is not None and pourquoi and str(pourquoi).startswith("repris"):
            reprises += int(str(pourquoi).split()[-1])
            pourquoi = None
        if bloc is None:
            refus[pourquoi] = refus.get(pourquoi, 0) + 1
            continue
        b = np.asarray(bloc, dtype=float)
        if float(b.max()) <= 0.0:
            refus["vide"] = refus.get("vide", 0) + 1
            continue
        sections[int(cx)] = une_section(b, la_rangee_montree(b.shape[1]))
    return {"decidable": bool(sections), "segment": volume["segment"],
            "grille_de_chunks": [int(gy), int(gx)], "la_rangee": int(ligne),
            "colonnes_demandees": len(voulues), "colonnes_lues": len(sections),
            "les_reprises_du_reseau": int(reprises), "refuses": refus,
            "sections": sections, "les_colonnes": voulues}


def mesurer(delai: float = DELAI, tirages: int = PERMUTATIONS, graine: int = GRAINE,
            replicats: int = REPLICATS, colonnes: int | None = None,
            ouvrir=None, meta=None, chercher=None) -> dict:
    """La marche le long d'une rangée entière, et la seule question déclarée."""
    v = le_segment_declare()
    if v is None:
        return {"decidable": False, "raison": "aucun volume recensé"}
    lg = la_ligne(v, delai, colonnes, ouvrir, meta, chercher)
    if not lg.get("decidable"):
        return {"decidable": False, "raison": lg.get("raison", "la ligne est vide")}
    pannes = les_pannes_de_reseau(lg.get("refuses"))
    if pannes:
        return {"decidable": False,
                "raison": f"{pannes} chunks perdus par le réseau — une ligne dont le fil est "
                          f"tombé n'est pas une ligne contiguë",
                "la_ligne": {k: x for k, x in lg.items() if k != "sections"}}
    largeur = la_largeur_du_bord()
    troncons = les_troncons(lg["sections"], lg["les_colonnes"])
    m = la_marche(lg["sections"], troncons, largeur)
    if not m.get("decidable"):
        return {"decidable": False, "raison": m.get("raison", "aucun pas"),
                "la_ligne": {k: x for k, x in lg.items() if k != "sections"}}
    return {
        "graine": int(graine), "tirages": int(tirages),
        "la_question_declaree": LA_QUESTION_DECLAREE,
        "la_largeur_du_bord": int(largeur),
        "le_pas_dun_pli_en_voxels": round(float(PAS_EN_VOXELS), 4),
        "la_plage_de_recalage": int(DEMI_PAS_EN_VOXELS),
        "la_ligne": {k: x for k, x in lg.items() if k not in ("sections", "les_colonnes")},
        "les_troncons": len(troncons),
        "la_marche": {k: x for k, x in m.items() if k != "les_pas_en_voxels"},
        "les_pas_en_voxels": m["les_pas_en_voxels"],
        "le_verdict": contre_les_signes(m["les_pas_en_voxels"], tirages, graine),
        # ⭐⭐⭐⭐ CE QUE « LES PAS SE COMPENSENT » COUTE QUAND MEME : une marche au hasard avance
        # comme la racine du nombre de pas, donc le feuillet se perd au bout d'un nombre de coutures
        # qui se CALCULE, sans aucun reglage.
        "avant_un_demi_pli": combien_de_chunks_avant(
            m["le_pas_quadratique_en_voxels"], DEMI_PAS_EN_VOXELS),
        "avant_un_pli": combien_de_chunks_avant(
            m["le_pas_quadratique_en_voxels"], PAS_EN_VOXELS),
        "letalon": sur_letalon(tirages, graine, replicats),
    }


def afficher(r: dict) -> None:
    if not r.get("decidable", True):
        print(f"LA DÉRIVE S'ACCUMULE-T-ELLE   indécidable : {r.get('raison')}")
        return
    lg, m, ve = r["la_ligne"], r["la_marche"], r["le_verdict"]
    print(f"LA DÉRIVE S'ACCUMULE-T-ELLE   segment {lg['segment']} · rangée {lg['la_rangee']} de "
          f"{lg['grille_de_chunks'][0]} · {lg['colonnes_lues']} chunks lus sur "
          f"{lg['colonnes_demandees']} · refus {lg['refuses'] or '—'}")
    print(f"  LES PAS           {m['les_pas']} pas en {r['les_troncons']} tronçons · bord "
          f"{r['la_largeur_du_bord']} colonnes · médian {m['le_pas_median_en_voxels']} vx · "
          f"quadratique {m['le_pas_quadratique_en_voxels']} · saturent "
          f"{m['les_pas_qui_saturent']}")
    print(f"  L'ACCUMULATION    net {m['le_deplacement_net_en_voxels']} vx "
          f"({m['le_deplacement_net_en_plis']} pli) · excursion maximale "
          f"{m['lexcursion_maximale_en_plis']} pli")
    a1, a2 = r.get("avant_un_demi_pli") or {}, r.get("avant_un_pli") or {}
    if a1.get("decidable"):
        print(f"  LA PORTÉE         un demi-pli après {a1['les_chunks']} chunks "
              f"({a1['la_largeur_en_mm']} mm) · un pli après {a2['les_chunks']} "
              f"({a2['la_largeur_en_mm']} mm)")
    if ve.get("decidable"):
        print(f"  LE VERDICT        {ve['le_deplacement_net_en_voxels']} contre "
              f"{ve['le_deplacement_du_nul_median_en_voxels']} au nul de signes · "
              f"{ve['les_tirages_au_moins_aussi_loin']} tirages aussi loin · "
              f"{ve['combien_de_marches_au_hasard']} marches au hasard · s'accumule "
              f"{ve['ca_saccumule']}")
    e = r["letalon"]
    print(f"  L'ÉTALON          sépare {e['letalon_separe']} · biais dérivé "
          f"{e['le_biais_quil_faut']} · taux de faux {e['le_taux_de_faux']} pour "
          f"{round(e['la_garantie'], 4)} garantis · courbe " + " · ".join(
              f"{x['le_biais_pose']:g}→{x['part_des_replicats']:g}" for x in e["la_courbe"]))


def verifier() -> int:
    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        if not ok:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    v("★★ une seule question est déclarée", isinstance(LA_QUESTION_DECLAREE, str),
      LA_QUESTION_DECLAREE)
    v("★★★★ la largeur du bord est DÉRIVÉE du serpentement publié par `198`",
      la_largeur_du_bord() == 16,
      f"{la_largeur_du_bord()} colonnes pour un serpentement médian de 5 voxels sur 128")
    v("★★★ et une mesure absente ne la fait pas deviner",
      la_largeur_du_bord(Path("/n/existe/pas.json")) == 1)
    v("★★★ la pause entre essais est déclarée et non nulle",
      LA_PAUSE_ENTRE_ESSAIS > 0.0
      and lattente_avant_le_prochain_essai(2, LA_PAUSE_ENTRE_ESSAIS) == 2.0,
      str(LA_PAUSE_ENTRE_ESSAIS))
    v("★★ la rangée est la médiane de la grille", la_ligne_declaree(396) == 198
      and la_ligne_declaree(9) == 4)

    # ⭐⭐⭐⭐ UN PAS SE VERIFIE SUR UNE MATIERE DONT LE DECALAGE EST POSE.
    base = une_ligne_fabriquee(2, 109, 64, 0.0, 0.0, 3)
    v("★★★ un pas nul est lu nul",
      un_pas(base[0], base[1], 16)["le_pas_en_voxels"] == 0,
      str(un_pas(base[0], base[1], 16)["le_pas_en_voxels"]))
    for pose in (3, -5, 11):
        deux = une_ligne_fabriquee(2, 109, 64, float(pose), 0.0, 3)
        lu = un_pas(deux[0], deux[1], 16)["le_pas_en_voxels"]
        v(f"★★★★ un pas posé de {pose} est lu {pose}", lu == pose, f"lu {lu}")
    v("★★★ une coupe au bord plat est indécidable",
      un_pas(np.ones((40, 8)), np.ones((40, 8)), 4).get("decidable") is False)
    v("★★ deux coupes de profondeurs différentes sont refusées",
      un_pas(np.zeros((40, 8)), np.zeros((30, 8)), 4).get("decidable") is False)
    # ⚠⚠⚠ UN PAS PLUS GRAND QU'UNE DEMI-PERIODE NE SATURE PAS : IL ALIASE, ET C'EST PIRE. La sonde
    # affirmait la mauvaise panne. Une couture qui a saute un feuillet entier se lit comme un PETIT
    # pas EN ARRIERE, et rien dans le pas seul ne permet de la distinguer d'une couture presque
    # parfaite. C'est la limite que cette tranche doit nommer plutot que taire.
    trop = float(DEMI_PAS_EN_VOXELS + 5)
    gros = une_ligne_fabriquee(2, 109, 64, trop, 0.0, 3)
    lu_gros = un_pas(gros[0], gros[1], 16)["le_pas_en_voxels"]
    v("★★★★ un pas plus grand qu'une demi-période ALIASE au lieu de saturer",
      abs(lu_gros - (trop - PAS_EN_VOXELS)) <= 1.0,
      f"posé {trop}, lu {lu_gros}, aliasé attendu {round(trop - PAS_EN_VOXELS, 2)}")
    v("★★★★ et il change de SIGNE, donc il ressemble à une couture presque parfaite",
      lu_gros < 0 < trop and abs(lu_gros) < DEMI_PAS_EN_VOXELS,
      f"lu {lu_gros} pour un vrai pas de {trop}")
    bord = une_ligne_fabriquee(2, 109, 64, float(DEMI_PAS_EN_VOXELS), 0.0, 3)
    v("★★★ tandis qu'un pas EXACTEMENT à la demi-période sature et le dit",
      un_pas(bord[0], bord[1], 16)["il_sature"],
      str(un_pas(bord[0], bord[1], 16)["le_pas_en_voxels"]))

    # ⚠⚠⚠ UN TROU COUPE LA LIGNE, ET LA DERIVE NE L'ENJAMBE PAS.
    tr = les_troncons({0: 1, 1: 1, 2: 1, 5: 1, 6: 1}, list(range(8)))
    v("★★★★ un trou coupe la ligne en tronçons", tr == [[0, 1, 2], [5, 6]], str(tr))
    v("★★★ un chunk isolé ne fait pas un tronçon",
      les_troncons({0: 1, 3: 1}, list(range(5))) == [])
    v("★★ une ligne entière fait un seul tronçon",
      les_troncons({i: 1 for i in range(4)}, list(range(4))) == [[0, 1, 2, 3]])

    # ⭐⭐⭐⭐ LA MARCHE ACCUMULE, ET SON NUL EST CELUI DES SIGNES.
    secs = une_ligne_fabriquee(12, 109, 64, 2.0, 0.0, 3)
    m = la_marche(secs, [list(range(12))], 16)
    v("★★★★ une dérive systématique accumule son déplacement",
      m["le_deplacement_net_en_voxels"] == 22, str(m["le_deplacement_net_en_voxels"]))
    v("★★★ et l'excursion maximale est rendue en plis",
      abs(m["lexcursion_maximale_en_plis"] - 22.0 / PAS_EN_VOXELS) < 1e-6,
      str(m["lexcursion_maximale_en_plis"]))
    v("★★★ chaque tronçon porte ses bornes et son compte",
      m["les_troncons"][0]["chunks"] == 12 and m["les_troncons"][0]["pas"] == 11,
      str({k: x for k, x in m["les_troncons"][0].items() if k != "le_cumul_en_voxels"}))
    v("★★★★ et sa trace cumulée, qui est l'accumulation elle-même",
      m["les_troncons"][0]["le_cumul_en_voxels"] == [2 * (k + 1) for k in range(11)],
      str(m["les_troncons"][0]["le_cumul_en_voxels"]))
    v("★★★ le dernier point de la trace EST le déplacement net",
      m["les_troncons"][0]["le_cumul_en_voxels"][-1]
      == m["les_troncons"][0]["le_deplacement_net_en_voxels"])
    v("★★ une marche sans pas lisible est indécidable",
      la_marche({}, [], 16).get("decidable") is False)

    # ⚠⚠⚠ LE NUL PAR PERMUTATION SERAIT VIDE PAR CONSTRUCTION, ET LA SONDE LE MONTRE.
    pas_test = [3, -1, 4, -1, 5, -9, 2, 6]
    v("★★★★ permuter les pas laisse leur somme INCHANGÉE, donc un tel nul ne dirait rien",
      abs(float(np.sum(_rng(1).permutation(pas_test))) - float(np.sum(pas_test))) < 1e-12,
      "c'est pourquoi le nul tire les SIGNES")
    v("★★★★ tandis qu'un tirage de signes déplace la somme",
      len({abs(float(np.sum(np.asarray(pas_test)
                            * (_rng(k).integers(0, 2, size=8) * 2 - 1))))
           for k in range(8)}) > 1)

    v("★★★★ une dérive systématique dépasse tous les tirages de signes",
      contre_les_signes([2] * 12, 19, 5)["ca_saccumule"],
      str(contre_les_signes([2] * 12, 19, 5)["les_tirages_au_moins_aussi_loin"]))
    r0 = _rng(9)
    alea = [int(x) for x in r0.integers(-3, 4, size=40)]
    v("★★★★ et une marche au hasard ne les dépasse PAS",
      not contre_les_signes(alea, 19, 5)["ca_saccumule"],
      f"{contre_les_signes(alea, 19, 5)['les_tirages_au_moins_aussi_loin']} tirages aussi loin")
    v("★★★ le nombre de marches au hasard est publié à côté",
      contre_les_signes([2] * 12, 19, 5)["combien_de_marches_au_hasard"] is not None)
    v("★★ moins de deux pas est indécidable",
      contre_les_signes([1], 19, 5).get("decidable") is False)

    # ⭐⭐⭐⭐ LA PORTEE D'UNE MARCHE AU HASARD SE CALCULE, ET SE VERIFIE A LA MAIN.
    c1 = combien_de_chunks_avant(5.0, 50.0)
    v("★★★★ une marche de pas 5 atteint 50 voxels après cent chunks",
      abs(c1["les_chunks"] - 100.0) < 1e-6, str(c1["les_chunks"]))
    v("★★★ et la largeur en millimètres suit du côté d'un chunk",
      abs(c1["la_largeur_en_mm"] - 100.0 * 128 * VOXEL_FIN_UM / 1000.0) < 1e-6,
      str(c1["la_largeur_en_mm"]))
    v("★★★ un pas deux fois plus grand porte quatre fois plus loin",
      abs(combien_de_chunks_avant(10.0, 50.0)["les_chunks"] * 4.0 - c1["les_chunks"]) < 1e-6)
    v("★★ un pas quadratique nul est indécidable",
      combien_de_chunks_avant(0.0, 50.0).get("decidable") is False)

    # ⭐⭐⭐⭐ L'ETALON, SES DEUX FACES SUR REPLICATS.
    e = sur_letalon(19, 5, 6, chunks=16, bruit=2.0, echelle=(0.0, 2.0))
    v("★★★★ l'étalon sépare ses deux faces", e["letalon_separe"],
      f"biais {e['le_biais_quil_faut']}, taux de faux {e['le_taux_de_faux']}")
    v("★★★ le biais retenu est vu à TOUS les réplicats",
      e["le_biais_quil_faut"] is not None
      and la_part_vue(e["le_biais_quil_faut"], 2.0, 16, 6, 19, 5)["la_part"] >= 1.0,
      str(e["le_biais_quil_faut"]))
    v("★★★★ et la face SANS biais tient la garantie",
      e["le_taux_de_faux"] <= e["la_garantie"] + 1e-12,
      f"{e['le_taux_de_faux']} contre {e['la_garantie']}")
    v("★★★ la courbe entière est publiée", len(e["la_courbe"]) == 2,
      str([x["part_des_replicats"] for x in e["la_courbe"]]))

    # ⚠⚠⚠ LA LIGNE S'EXERCE SANS RESEAU, ET SES REFUS SE COMPTENT PAR LEUR RAISON.
    faux_meta = {"chunks": [109, 8, 64], "shape": [109, 8 * 5, 64 * 9], "dtype": "|u1"}

    def _faux_ouvrir(absents=(), coupes=()):
        secs = une_ligne_fabriquee(9, 109, 64, 1.0, 0.0, 3)

        def _prendre(cy, cx):
            if (cy, cx) in coupes:
                return None, f"{LE_RESEAU_A_ECHOUE} : transport : coupure"
            if (cy, cx) in absents:
                return None, ABSENT_DU_DEPOT
            s = secs[int(cx) % 9]
            return np.broadcast_to(s[:, None, :], (109, 8, 64)), None
        return _prendre

    lg = la_ligne({"segment": "S", "cle": "x"}, 0.01, None, _faux_ouvrir(absents={(2, 3)}),
                  faux_meta)
    v("★★★★ la ligne est la rangée médiane de la grille", lg["la_rangee"] == 2,
      f"{lg['la_rangee']} sur {lg['grille_de_chunks'][0]}")
    v("★★★ elle demande toutes les colonnes de la grille",
      lg["colonnes_demandees"] == 9 and lg["colonnes_lues"] == 8,
      f"{lg['colonnes_lues']} sur {lg['colonnes_demandees']}")
    v("★★★★ et un chunk absent du dépôt est compté par sa raison",
      lg["refuses"].get(ABSENT_DU_DEPOT) == 1, str(lg["refuses"]))
    mc = mesurer(0.01, 19, 5, 4, None, _faux_ouvrir(coupes={(2, 1)}), faux_meta)
    v("★★★★ une ligne dont le RÉSEAU a lâché est REFUSÉE", mc.get("decidable") is False
      and "réseau" in str(mc.get("raison")), str(mc.get("raison"))[:90])
    mm = mesurer(0.01, 19, 5, 4, None, _faux_ouvrir(absents={(2, 3)}), faux_meta)
    v("★★★★ tandis qu'une ligne trouée est mesurée en TRONÇONS",
      mm.get("decidable", True) and mm["les_troncons"] == 2, str(mm.get("les_troncons")))
    v("★★★ et son verdict porte sur les pas des deux tronçons réunis",
      mm["la_marche"]["les_pas"] == 6, str(mm["la_marche"]["les_pas"]))

    nom = "la_derive_saccumule_t_elle.py"
    if echecs:
        print(f"{nom}   {len(echecs)} ÉCHECS sur {faits}")
        for e_ in echecs:
            print(f"   ✗ {e_}")
    else:
        print(f"{nom:<46} ALL PASS (0 failures, {faits} checks)")
    return len(echecs)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--colonnes", type=int)
    p.add_argument("--json", type=Path)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(colonnes=a.colonnes)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
