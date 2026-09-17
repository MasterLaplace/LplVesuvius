"""De quoi une frontière du rouleau est-elle faite ? — l'espacement des creux le dit.

⭐⭐⭐⭐ POURQUOI CE FICHIER. `180` a mesuré que le rouleau CREUSE, partout — vingt-sept chunks sur
vingt-sept contre 1,35 attendus par hasard, à une profondeur qui dépasse celle d'une frontière
construite — et qu'une matière sans frontière au même niveau de cohérence ne creuse pas. Mais l'écart
que le creux sépare vaut **27,363°**, soit trois dixièmes d'un quart de tour : ce n'est pas la
frontière recto/verso de `14` §1, et trois causes restaient possibles sans qu'aucune soit écartée.

⭐⭐⭐⭐ CE QUI SÉPARE LES CAUSES EST L'ESPACEMENT, ET IL EST DÉRIVÉ. Une frontière de PLI se répète
tous les `pas/2` micromètres, un interstice entre deux FEUILLES tous les `pas`. À 2,4 µm cela fait
**36** couches contre **72**, et `175` mesure que les 109 couches de la campagne portent
**3,024 plis**. Un lecteur qui ne rend qu'un creux par chunk ne peut pas trancher ; il en faut
plusieurs.

⚠⚠⚠ ET LA LIBERTÉ D'EN CHERCHER PLUSIEURS SE PAIE, EXACTEMENT COMME `179` A PAYÉ CELLE DE LA
LARGEUR. Chercher un second creux après avoir retiré le premier est une seconde chance, et une
permutation appliquée creux par creux ne la price pas. Ce qui la price est de faire subir à CHAQUE
mélange la MÊME recherche séquentielle, et de comparer le k-ième creux réel au k-ième creux de
chaque mélange. Le mélange a alors exactement le même nombre d'occasions, au même rang.

⚠⚠ LA BANDE D'EXCLUSION EST DÉRIVÉE DU CREUX LUI-MÊME, pas choisie : deux centres plus proches que
la largeur du creux trouvé désignent le MÊME creux, donc on exclut cette largeur autour de lui. Une
bande plus large interdirait de trouver la frontière suivante, une plus étroite compterait deux fois
la même.

⭐⭐⭐⭐ LES DEUX ÉTALONS SONT DE LA MÊME FAMILLE ET NE DIFFÈRENT QUE PAR L'ESPACEMENT DE LEURS
FRONTIÈRES. `plis=2` donne une matière dont les frontières sont aux PLIS ; `plis=1` avec des feuilles
d'angles indépendants donne une matière dont les seules frontières sont aux FEUILLES. Même
recouvrement, même bruit, même lecteur : ce qui les sépare est la seule chose qu'on mesure.

⚠ Le chemin du rouleau est celui de `176` et `180`, appelé et non recopié.

Usage :
    uv run python src/nappe/de_quoi_une_frontiere_est_elle_faite.py --verifier
    uv run python src/nappe/de_quoi_une_frontiere_est_elle_faite.py \\
        --json docs/mesures/de_quoi_une_frontiere_est_elle_faite.json
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))

from la_coherence_creuse_t_elle_a_la_frontiere import (  # noqa: E402
    CONTRASTE_DE_LA_FIXTURE, PLIS_DE_LA_FIXTURE, le_creux, le_creux_nul, les_largeurs_du_creux)
from la_coupe_cherchee_trouve_t_elle_la_frontiere import COUCHES_MINIMALES  # noqa: E402
from la_profondeur_tourne_t_elle_ou_bascule_t_elle import PERMUTATIONS  # noqa: E402
from la_recette_posee_sur_le_rouleau import (COTE_DU_TREILLIS, DELAI,  # noqa: E402
                                             SEGMENTS, la_courbe_dun_chunk, les_chunks,
                                             les_volumes)
from le_rouleau_creuse_t_il import ce_que_le_creux_separe  # noqa: E402
from quelle_fenetre_lit_une_bascule import courbe_de_la_fixture  # noqa: E402
from zarr_depth import BUCKET, array_meta  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
CE_QUE_LA_FIXTURE_A_RENDU = MESURES / "la_coherence_creuse_t_elle_a_la_frontiere.json"
CE_QUE_LE_ROULEAU_A_RENDU = MESURES / "le_rouleau_creuse_t_il.json"
GRAINE = 20260921
DECALAGES = 12
COUCHES = 109


def les_deux_espacements(voxel_um: float, pas_um: float) -> dict:
    """Les deux espacements que la matière peut porter, en couches — DÉRIVÉS du pas et du voxel.

    ⚠ Une feuille est faite de deux plis, donc une frontière de PLI revient deux fois plus souvent
    qu'une frontière de FEUILLE. Aucun des deux nombres n'est écrit à la main.
    """
    return {"un_pli": int(round(float(pas_um) / float(PLIS_DE_LA_FIXTURE) / float(voxel_um))),
            "une_feuille": int(round(float(pas_um) / float(voxel_um)))}


def la_bande_dexclusion(largeur: int, largeurs=None,
                        minimum: int = COUCHES_MINIMALES) -> int:
    """De combien de couches deux creux doivent-ils être séparés pour être DEUX frontières.

    ⚠⚠ DÉRIVÉ DE `178` ET DE `174`, PAS CHOISI : une frontière doit laisser `COUCHES_MINIMALES`
    couches derrière elle, donc deux frontières doivent laisser autant ENTRE elles. Il faut compter
    la demi-largeur du creux déjà pris, celle du suivant — inconnue, donc la plus grande de
    l'échelle — et le segment minimal entre les deux.
    """
    largeurs = list(largeurs) if largeurs is not None else les_largeurs_du_creux(minimum)
    return int(int(largeur) // 2 + int(minimum) + max(largeurs) // 2)


def _cherche(c: np.ndarray, combien: int, minimum: int, largeurs) -> list[dict]:
    """La recherche SÉQUENTIELLE : le creux le plus profond, puis le suivant hors de sa bande.

    ⚠⚠⚠ LA BANDE D'EXCLUSION SE DÉRIVE DE CE QUI FAIT DEUX FRONTIÈRES, ET UNE PREMIÈRE VERSION LA
    PRENAIT TROP ÉTROITE. Elle valait la largeur du creux trouvé, donc deux creux à quatre couches
    d'écart passaient tous les deux, et l'étalon dont les frontières sont aux FEUILLES rendait un
    espacement médian de quatre au lieu de soixante-douze : le contrôle a échoué et la mesure ne
    voulait rien dire. La règle est celle de `178` : deux frontières ne séparent deux segments que
    s'il reste `COUCHES_MINIMALES` couches ENTRE elles, et `174` refuse une tranche plus courte. On
    interdit donc les centres dont le bord tomberait à moins de cela du bord du creux déjà pris, en
    comptant la demi-largeur la plus grande de l'échelle — la largeur du creux suivant n'est pas
    connue au moment où on l'interdit.

    ⚠ L'exclusion est appliquée en interdisant les CENTRES, jamais en modifiant la courbe :
    retoucher les cohérences changerait la moyenne « dehors » et donc la profondeur des suivants.
    """
    interdits: list[tuple[int, int]] = []
    trouves = []
    for _ in range(int(combien)):
        meilleur = None
        for w in largeurs:
            lu = le_creux(c, w, None, minimum)
            if lu is None:
                continue
            # ⚠ On rebalaye en ecartant les centres interdits : `le_creux` rend le maximum global,
            # donc il faut lui retirer les bandes deja prises sans toucher aux valeurs.
            if any(a <= int(lu["couche"]) <= b for a, b in interdits):
                lu = _hors_des_bandes(c, w, minimum, interdits)
                if lu is None:
                    continue
            if meilleur is None or lu["profondeur"] > meilleur["profondeur"]:
                meilleur = lu
        if meilleur is None:
            break
        trouves.append(meilleur)
        bande = la_bande_dexclusion(int(meilleur["largeur"]), largeurs, int(minimum))
        interdits.append((int(meilleur["couche"]) - bande, int(meilleur["couche"]) + bande))
    return trouves


def _hors_des_bandes(c: np.ndarray, largeur: int, minimum: int, interdits) -> dict | None:
    """Le creux le plus profond de cette largeur dont le centre évite les bandes déjà prises."""
    n = int(len(c))
    h = int(largeur) // 2
    total = float(c.sum())
    meilleur = None
    for k in range(int(minimum), n - int(minimum)):
        if any(a <= k <= b for a, b in interdits):
            continue
        a, b = max(0, k - h), min(n, k + h + 1)
        nd = float(b - a)
        dedans = float(c[a:b].sum())
        no = float(n) - nd
        dehors = total - dedans
        if nd <= 0.0 or no <= 0.0 or dehors <= 0.0:
            continue
        p = 1.0 - (dedans / nd) / (dehors / no)
        if meilleur is None or p > meilleur["profondeur"] + 1e-12:
            meilleur = {"couches": n, "largeur": int(largeur), "largeur_de_fenetre": None,
                        "profondeur": round(float(p), 4), "couche": int(k), "depart": 0,
                        "coherence_dedans": round(dedans / nd, 4),
                        "coherence_dehors": round(dehors / no, 4)}
    return meilleur


def plusieurs_creux(coherences, combien: int = 3, permutations: int = PERMUTATIONS,
                    graine: int = GRAINE, minimum: int = COUCHES_MINIMALES) -> dict:
    """Les `combien` creux les plus profonds, chacun comparé au creux DE MÊME RANG des mélanges.

    ⭐⭐⭐⭐ C'EST LE RANG QUI REND LA COMPARAISON HONNÊTE. Le second creux d'une courbe est déjà
    moins profond que le premier par construction ; le comparer au PREMIER creux des mélanges le
    déclarerait toujours perdant, et le comparer à rien le déclarerait toujours gagnant. Chaque
    mélange subit la même recherche séquentielle et rend sa propre suite décroissante, donc le rang
    `k` se compare au rang `k`.

    ⚠ Le nul d'une seule couche est rendu à côté, comme dans `179` : sans lui, « la cohérence tombe
    à 0,08 » ne dit pas si elle y tombe sur une suite ou sur une couche isolée.
    """
    c = np.asarray([float(x) for x in coherences], dtype=float)
    largeurs = les_largeurs_du_creux(minimum)
    reels = _cherche(c, int(combien), int(minimum), largeurs)
    if not reels:
        return {"decidable": False, "raison": "aucun creux", "creux": []}
    rangs: list[list[float]] = [[] for _ in range(len(reels))]
    for t in range(int(permutations)):
        r = np.random.default_rng(int(graine) + t)
        melange = _cherche(c[r.permutation(len(c))], len(reels), int(minimum), largeurs)
        for k in range(len(reels)):
            rangs[k].append(float(melange[k]["profondeur"]) if k < len(melange) else 0.0)
    creux = []
    for k, x in enumerate(reels):
        med = float(statistics.median(rangs[k])) if rangs[k] else 0.0
        creux.append({"rang": k + 1, "couche": int(x["couche"]), "largeur": int(x["largeur"]),
                      "profondeur": float(x["profondeur"]),
                      "profondeur_mediane_des_melanges": round(med, 4),
                      # ⚠⚠ LE MAXIMUM PAR RANG EST PUBLIE PARCE QU'IL EST CE QUI DECROIT VRAIMENT :
                      # la mediane peut coincider d'un rang a l'autre quand la coherence ne prend
                      # que quelques valeurs, alors qu'une recherche sequentielle ne peut PAS
                      # rendre un rang plus profond que le precedent.
                      "profondeur_maximale_des_melanges": (round(float(max(rangs[k])), 4)
                                                           if rangs[k] else None),
                      "excedent": round(float(x["profondeur"]) - med, 4),
                      "depasse_tous_les_melanges": bool(
                          all(float(x["profondeur"]) > y for y in rangs[k]))})
    retenus = [x for x in creux if x["depasse_tous_les_melanges"]]
    couches = sorted(int(x["couche"]) for x in retenus)
    return {"decidable": True, "le_nul": le_creux_nul(c), "permutations": int(permutations),
            "creux": creux, "creux_retenus": len(retenus),
            "couches_retenues": couches,
            "espacements": [int(b - a) for a, b in zip(couches, couches[1:])]}


def _proche(espacements, deux: dict) -> str | None:
    """Lequel des deux espacements dérivés l'espacement médian désigne-t-il ?

    ⚠⚠ C'EST UNE COMPARAISON DE DISTANCES, PAS UN SEUIL : l'espacement mesuré est rangé auprès du
    plus proche des deux nombres que la matière peut porter. Une égalité ne désigne personne plutôt
    que d'être tranchée par l'ordre d'écriture.
    """
    if not espacements:
        return None
    m = float(statistics.median([float(x) for x in espacements]))
    da, db = abs(m - float(deux["un_pli"])), abs(m - float(deux["une_feuille"]))
    if abs(da - db) < 1e-9:
        return None
    return "un_pli" if da < db else "une_feuille"


def lire_un_chunk(courbe, deux: dict, combien: int = 3, permutations: int = PERMUTATIONS,
                  graine: int = GRAINE) -> dict:
    """Les creux d'un chunk, leur espacement, et ce que chacun sépare."""
    lu = plusieurs_creux([x[1] for x in courbe], combien, permutations, graine)
    if not lu.get("decidable"):
        return lu
    separent = [ce_que_le_creux_separe(courbe, int(x["couche"]), int(x["largeur"]))
                for x in lu["creux"] if x["depasse_tous_les_melanges"]]
    return {**lu, "designe": _proche(lu["espacements"], deux),
            "espacement_median": (round(float(statistics.median(lu["espacements"])), 1)
                                  if lu["espacements"] else None),
            "ce_que_les_creux_separent": separent,
            "creux_a_deux_cotes_diriges": int(
                sum(1 for x in separent if x["les_deux_cotes_sont_diriges"]))}


def _med(v):
    return round(float(statistics.median(v)), 4) if v else None


def un_segment(volume: dict, deux: dict, combien: int = 3, cote: int = COTE_DU_TREILLIS,
               permutations: int = PERMUTATIONS, delai: float = DELAI,
               graine: int = GRAINE) -> dict:
    url = f"{BUCKET}/{volume['cle']}"
    try:
        meta = array_meta(url, 0, delai)
    except Exception as e:  # noqa: BLE001
        return {"decidable": False, "segment": volume["segment"],
                "raison": f"le volume ne répond pas : {type(e).__name__}"}
    profond, hy, hx = meta["chunks"]
    _, rows, cols = meta["shape"]
    positions = les_chunks(-(-rows // hy), -(-cols // hx), cote)
    lignes, refus = [], {}
    for cy, cx in positions:
        courbe, pourquoi = la_courbe_dun_chunk(url, meta, cy, cx, delai)
        if courbe is None:
            refus[pourquoi] = refus.get(pourquoi, 0) + 1
            continue
        lignes.append({"chunk": [int(cy), int(cx)],
                       **lire_un_chunk(courbe, deux, combien, permutations, graine)})
    lus = [x for x in lignes if x.get("decidable")]
    espaces = [e for x in lus for e in x["espacements"]]
    return {"decidable": bool(lus), "segment": volume["segment"],
            "chunks_du_treillis": len(positions), "chunks_lus": len(lus), "refuses": refus,
            "creux_retenus": int(sum(x["creux_retenus"] for x in lus)),
            "chunks_a_deux_creux_ou_plus": int(sum(1 for x in lus if x["creux_retenus"] >= 2)),
            "espacements": sorted(espaces),
            "espacement_median": _med(espaces),
            "designent_un_pli": int(sum(1 for x in lus if x["designe"] == "un_pli")),
            "designent_une_feuille": int(sum(1 for x in lus if x["designe"] == "une_feuille")),
            "lignes": lignes}


def un_etalon(plis: int, feuilles_independantes: bool, recouvrement_um: float, bruit: float,
              deux: dict, combien: int = 3, decalages: int = DECALAGES,
              permutations: int = PERMUTATIONS, graine: int = GRAINE) -> dict:
    """La MÊME lecture sur la fixture — aux plis, ou aux feuilles.

    ⚠⚠ LES DEUX ÉTALONS NE DIFFÈRENT QUE PAR L'ESPACEMENT DE LEURS FRONTIÈRES : même recouvrement,
    même bruit, même contraste, même lecteur. `plis=2` porte une frontière tous les demi-pas ;
    `plis=1` à feuilles indépendantes n'en porte qu'aux feuilles, donc tous les pas.
    """
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    vx, pas = float(C.VOXEL_FIN_UM), float(C.PAS_UM)
    lignes = []
    for k in range(int(decalages)):
        dec = pas * k / float(decalages)
        courbe = courbe_de_la_fixture(COUCHES, dec, CONTRASTE_DE_LA_FIXTURE, int(plis), vx, pas,
                                      transition_um=float(recouvrement_um), bruit=float(bruit),
                                      feuilles_independantes=bool(feuilles_independantes))
        lignes.append({"decalage_um": round(dec, 3),
                       **lire_un_chunk(courbe, deux, combien, permutations, graine)})
    lus = [x for x in lignes if x.get("decidable")]
    espaces = [e for x in lus for e in x["espacements"]]
    return {"plis": int(plis), "feuilles_independantes": bool(feuilles_independantes),
            "bruit": float(bruit), "cellules": len(lignes), "lisibles": len(lus),
            "creux_retenus": int(sum(x["creux_retenus"] for x in lus)),
            "cellules_a_deux_creux_ou_plus": int(sum(1 for x in lus if x["creux_retenus"] >= 2)),
            "espacements": sorted(espaces), "espacement_median": _med(espaces),
            "designent_un_pli": int(sum(1 for x in lus if x["designe"] == "un_pli")),
            "designent_une_feuille": int(sum(1 for x in lus if x["designe"] == "une_feuille"))}


def juger(segments: list[dict], etalons: list[dict], deux: dict,
          permutations: int = PERMUTATIONS) -> dict:
    """Les creux du rouleau sont-ils espacés comme des plis ou comme des feuilles ?

    ⚠⚠⚠ LES DEUX ÉTALONS SONT LÀ POUR QUE LA RÉPONSE PUISSE ÊTRE FAUSSE : si le lecteur rangeait
    les deux matières construites du même côté, il ne saurait pas les distinguer et sa lecture du
    rouleau ne dirait rien.
    """
    lus = [s for s in segments if s.get("decidable")]
    if not lus:
        return {"decidable": False, "raison": "aucun segment lisible"}
    aux_plis = next((e for e in etalons if not e["feuilles_independantes"]), None)
    aux_feuilles = next((e for e in etalons if e["feuilles_independantes"]), None)
    espaces = [e for s in lus for e in s["espacements"]]
    chunks = sum(s["chunks_lus"] for s in lus)
    pli = sum(s["designent_un_pli"] for s in lus)
    feuille = sum(s["designent_une_feuille"] for s in lus)
    return {"decidable": True, "segments": len(lus), "chunks_lus": chunks,
            "permutations": int(permutations),
            "un_pli_en_couches": int(deux["un_pli"]),
            "une_feuille_en_couches": int(deux["une_feuille"]),
            "creux_retenus": int(sum(s["creux_retenus"] for s in lus)),
            "chunks_a_deux_creux_ou_plus": int(sum(s["chunks_a_deux_creux_ou_plus"]
                                                   for s in lus)),
            "espacements_mesures": len(espaces),
            "espacement_median_du_rouleau": _med(espaces),
            "espacement_median_aux_plis": (aux_plis["espacement_median"] if aux_plis else None),
            "espacement_median_aux_feuilles": (aux_feuilles["espacement_median"]
                                               if aux_feuilles else None),
            "chunks_qui_designent_un_pli": int(pli),
            "chunks_qui_designent_une_feuille": int(feuille),
            "cellules_aux_plis_qui_designent_un_pli": (aux_plis["designent_un_pli"]
                                                       if aux_plis else None),
            "cellules_aux_feuilles_qui_designent_une_feuille": (
                aux_feuilles["designent_une_feuille"] if aux_feuilles else None),
            "cellules_de_letalon": (aux_plis["cellules"] if aux_plis else None),
            # ⚠⚠ TROIS ENONCES. Le premier dit que les deux etalons se SEPARENT, sans quoi rien de
            # ce qui suit ne veut dire quelque chose. Le second dit ce que le rouleau designe. Le
            # troisieme dit s'il y a assez de creux pour qu'un espacement existe.
            "les_deux_etalons_se_separent": bool(
                aux_plis is not None and aux_feuilles is not None
                and aux_plis["designent_un_pli"] > aux_plis["designent_une_feuille"]
                and aux_feuilles["designent_une_feuille"] > aux_feuilles["designent_un_pli"]),
            "le_rouleau_designe": ("un_pli" if pli > feuille
                                   else ("une_feuille" if feuille > pli else None)),
            "assez_de_creux_pour_un_espacement": bool(
                chunks and sum(s["chunks_a_deux_creux_ou_plus"] for s in lus) > chunks / 2.0)}


def _relire(chemin: Path, cles) -> dict | None:
    if not chemin.exists():
        return None
    v = json.loads(chemin.read_text(encoding="utf-8")).get("le_verdict", {})
    return {k: v.get(k) for k in cles} if v.get(cles[0]) is not None else None


def mesurer(combien: int = 3, segments_n: int = SEGMENTS, cote: int = COTE_DU_TREILLIS,
            permutations: int = PERMUTATIONS, decalages: int = DECALAGES) -> dict:
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    vx, pas = float(C.VOXEL_FIN_UM), float(C.PAS_UM)
    de_179 = _relire(CE_QUE_LA_FIXTURE_A_RENDU, ("le_recouvrement_juste_suffisant_um",))
    de_180 = _relire(CE_QUE_LE_ROULEAU_A_RENDU, ("le_bruit_apparie",))
    if de_179 is None or de_180 is None:
        return {"message": "les mesures de `179` et `180` donnent le recouvrement et le bruit"}
    recouvrement = float(de_179["le_recouvrement_juste_suffisant_um"])
    bruit = float(de_180["le_bruit_apparie"])
    deux = les_deux_espacements(vx, pas)
    volumes = les_volumes(combien=segments_n)
    if not volumes:
        return {"message": "aucun volume de surface à la résolution de la campagne n'est recensé"}
    segs = [un_segment(v, deux, combien, cote, permutations) for v in volumes]
    etalons = [un_etalon(PLIS_DE_LA_FIXTURE, False, recouvrement, bruit, deux, combien,
                         decalages, permutations),
               un_etalon(1, True, recouvrement, bruit, deux, combien, decalages, permutations)]
    return {"creux_par_chunk": int(combien), "cote_du_treillis": int(cote),
            "permutations": int(permutations), "graine": int(GRAINE),
            "decalages": int(decalages), "couches": int(COUCHES),
            "les_deux_espacements": deux,
            "recouvrement_um_de_179": recouvrement, "bruit_apparie_de_180": bruit,
            "les_segments": segs, "les_etalons": etalons,
            "le_verdict": juger(segs, etalons, deux, permutations)}


def afficher(r: dict) -> None:
    if "message" in r:
        print(r["message"])
        return
    v = r["le_verdict"]
    print("DE QUOI UNE FRONTIÈRE EST-ELLE FAITE ?")
    print(f"  {r['creux_par_chunk']} creux par chunk · treillis {r['cote_du_treillis']}×"
          f"{r['cote_du_treillis']} · {r['permutations']} permutations · recouvrement "
          f"{r['recouvrement_um_de_179']} µm (`179`) · bruit {r['bruit_apparie_de_180']} (`180`)")
    print(f"  un pli = {v['un_pli_en_couches']} couches · une feuille = "
          f"{v['une_feuille_en_couches']} couches")
    print()
    for s in r["les_segments"]:
        if not s.get("decidable"):
            print(f"  {s['segment']} — {s.get('raison')}")
            continue
        print(f"  {s['segment']} · {s['chunks_lus']}/{s['chunks_du_treillis']} chunks · creux "
              f"{s['creux_retenus']} · deux creux ou plus {s['chunks_a_deux_creux_ou_plus']}")
        print(f"     espacement médian {s['espacement_median']} · désignent pli "
              f"{s['designent_un_pli']} · feuille {s['designent_une_feuille']}")
    print()
    print("  LES DEUX ÉTALONS · même recouvrement, même bruit, seules les frontières changent")
    for e in r["les_etalons"]:
        quoi = "aux feuilles" if e["feuilles_independantes"] else "aux plis"
        print(f"   {quoi:<14} creux {e['creux_retenus']:>3} · deux ou plus "
              f"{e['cellules_a_deux_creux_ou_plus']:>2}/{e['cellules']} · espacement "
              f"{str(e['espacement_median']):>6} · désignent pli {e['designent_un_pli']:>2} · "
              f"feuille {e['designent_une_feuille']:>2}")
    print()
    print("  ★ LE VERDICT")
    for cle in ("chunks_lus", "creux_retenus", "chunks_a_deux_creux_ou_plus",
                "espacements_mesures", "espacement_median_du_rouleau",
                "espacement_median_aux_plis", "espacement_median_aux_feuilles",
                "chunks_qui_designent_un_pli", "chunks_qui_designent_une_feuille",
                "cellules_aux_plis_qui_designent_un_pli",
                "cellules_aux_feuilles_qui_designent_une_feuille", "cellules_de_letalon",
                "les_deux_etalons_se_separent", "le_rouleau_designe",
                "assez_de_creux_pour_un_espacement"):
        print(f"     {cle:<48} {v.get(cle)}")


def verifier() -> int:
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        if not ok:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    vx, pas = float(C.VOXEL_FIN_UM), float(C.PAS_UM)
    deux = les_deux_espacements(vx, pas)

    # ⚠⚠ LES DEUX ESPACEMENTS SONT DERIVES DU PAS ET DU VOXEL, et l'un vaut exactement le double de
    # l'autre parce qu'une feuille est faite de deux plis.
    v("un pli vaut la moitié d'une feuille", deux["une_feuille"] == 2 * deux["un_pli"],
      str(deux))
    v("et ils viennent du pas et du voxel",
      deux["une_feuille"] == int(round(pas / vx)), str(deux["une_feuille"]))

    # ⚠⚠⚠ LA BANDE D'EXCLUSION EST CE QUI A FAIT ECHOUER LA PREMIERE VERSION : trop etroite, deux
    # creux a quatre couches passaient tous les deux et l'etalon aux FEUILLES rendait un espacement
    # de quatre au lieu de soixante-douze. La regle derivee laisse un segment ENTRE les deux.
    L = les_largeurs_du_creux()
    for w in L:
        v(f"la bande d'exclusion laisse un segment entre deux creux (largeur {w})",
          la_bande_dexclusion(w) >= w // 2 + COUCHES_MINIMALES,
          f"{la_bande_dexclusion(w)} pour une largeur {w}")
    v("elle compte la demi-largeur la plus grande de l'échelle",
      la_bande_dexclusion(L[0]) == L[0] // 2 + COUCHES_MINIMALES + max(L) // 2,
      str(la_bande_dexclusion(L[0])))

    # ⭐⭐⭐⭐ DEUX COURBES CONSTRUITES DONT L'ESPACEMENT EST CHOISI : la reponse est connue AVANT la
    # mesure, et c'est exactement le controle qui a attrape le defaut de la bande.
    for nom, ecart in (("un pli", deux["un_pli"]), ("une feuille", deux["une_feuille"])):
        a = 30 if ecart == deux["un_pli"] else 12
        c = [0.9] * a + [0.15] * 5 + [0.9] * (ecart - 5) + [0.15] * 5
        c = c + [0.9] * (COUCHES - len(c))
        lu = plusieurs_creux(c, 3, PERMUTATIONS, GRAINE)
        v(f"deux creux espacés d'{nom} sont trouvés", lu["creux_retenus"] == 2,
          f"{lu['creux_retenus']} · {lu.get('couches_retenues')}")
        v(f"et leur espacement vaut {ecart}", lu["espacements"] == [int(ecart)],
          str(lu["espacements"]))
        v(f"et il désigne {nom}", _proche(lu["espacements"], deux)
          == ("un_pli" if ecart == deux["un_pli"] else "une_feuille"),
          str(_proche(lu["espacements"], deux)))

    # ⚠ UNE EGALITE NE DESIGNE PERSONNE plutot que d'etre tranchee par l'ordre d'ecriture.
    milieu = (deux["un_pli"] + deux["une_feuille"]) / 2.0
    v("un espacement à mi-chemin ne désigne personne",
      _proche([milieu], deux) is None, str(_proche([milieu], deux)))

    # ⭐⭐⭐⭐ LE RANG EST CE QUI REND LA COMPARAISON HONNETE : le second creux d'une courbe est deja
    # moins profond que le premier, donc le comparer au PREMIER creux des melanges le declarerait
    # toujours perdant. Sur une courbe a UN seul creux, le second rang ne doit pas etre retenu.
    seul = [0.9] * 50 + [0.15] * 5 + [0.9] * (COUCHES - 55)
    lu = plusieurs_creux(seul, 3, PERMUTATIONS, GRAINE)
    v("une courbe à un seul creux n'en retient qu'un", lu["creux_retenus"] == 1,
      f"{lu['creux_retenus']} · {lu.get('couches_retenues')}")
    v("et elle ne rend aucun espacement", lu["espacements"] == [], str(lu["espacements"]))

    # ⚠⚠⚠ ET LE MECANISME DU RANG EST EXERCE PAR UN CONTROLE STRUCTUREL, parce qu'une sonde qui
    # comparait TOUS les rangs au rang 1 des melanges passait au VERT : sur les matieres assertees,
    # le second creux perdait de toute facon.
    # ⚠⚠ MA PREMIERE VERSION DE CE CONTROLE ETAIT FAUSSE ET LA MESURE L'A DIT : elle exigeait que
    # les MEDIANES decroissent, et elles sortent EGALES — avec une coherence a deux valeurs la
    # profondeur est quantifiee, donc la mediane coincide d'un rang a l'autre. Ce qui decroit
    # vraiment est le MAXIMUM par rang, et il le fait par construction : un rang suivant est cherche
    # hors de la bande du precedent, donc il ne peut pas etre plus profond. Comparer tout au rang 1
    # rend les trois maximums EGAUX.
    maxima = [x["profondeur_maximale_des_melanges"] for x in lu["creux"]]
    v("les maximums des mélanges décroissent strictement avec le rang",
      len(maxima) >= 2 and all(a > b for a, b in zip(maxima, maxima[1:])), str(maxima))

    # ⚠ UNE COHERENCE PLATE NE CREUSE NULLE PART.
    plat = plusieurs_creux([0.4] * COUCHES, 3, PERMUTATIONS, GRAINE)
    v("une cohérence plate ne retient aucun creux",
      not plat.get("decidable") or plat["creux_retenus"] == 0, str(plat.get("creux_retenus")))

    # ⭐⭐⭐⭐ LE CHEMIN PHYSIQUE : les deux etalons DOIVENT se separer, sinon rien de ce que le
    # rouleau rend ne veut dire quelque chose. C'est le controle qui a echoue et qui a impose la
    # reparation de la bande.
    de_179 = _relire(CE_QUE_LA_FIXTURE_A_RENDU, ("le_recouvrement_juste_suffisant_um",))
    de_180 = _relire(CE_QUE_LE_ROULEAU_A_RENDU, ("le_bruit_apparie",))
    v("les mesures de `179` et `180` donnent le recouvrement et le bruit",
      de_179 is not None and de_180 is not None)
    if de_179 is not None and de_180 is not None:
        rec = float(de_179["le_recouvrement_juste_suffisant_um"])
        bruit = float(de_180["le_bruit_apparie"])
        # ⚠⚠ LES DOUZE DECALAGES, PAS TROIS, ET C'EST UNE SONDE QUI L'A IMPOSE : une fenetre de
        # 109 couches ne contient DEUX frontieres de feuille que dans une minorite des cas — la
        # mesure en compte quatre sur douze — donc un balayage court rend zero cellule a deux
        # creux et le controle ne peut alors ni reussir ni echouer.
        aux_plis = un_etalon(PLIS_DE_LA_FIXTURE, False, rec, bruit, deux, 3, DECALAGES,
                             PERMUTATIONS)
        aux_feuilles = un_etalon(1, True, rec, bruit, deux, 3, DECALAGES, PERMUTATIONS)
        v("une fenêtre de la campagne ne porte pas toujours deux frontières de feuille",
          0 < aux_feuilles["cellules_a_deux_creux_ou_plus"] < aux_feuilles["cellules"],
          f"{aux_feuilles['cellules_a_deux_creux_ou_plus']}/{aux_feuilles['cellules']}")
        v("l'étalon aux plis désigne le pli",
          aux_plis["designent_un_pli"] > aux_plis["designent_une_feuille"],
          f"pli {aux_plis['designent_un_pli']} · feuille {aux_plis['designent_une_feuille']} · "
          f"espacement {aux_plis['espacement_median']}")
        v("l'étalon aux feuilles désigne la feuille",
          aux_feuilles["designent_une_feuille"] > aux_feuilles["designent_un_pli"],
          f"pli {aux_feuilles['designent_un_pli']} · feuille "
          f"{aux_feuilles['designent_une_feuille']} · espacement "
          f"{aux_feuilles['espacement_median']}")
        v("et les deux se séparent",
          juger([{"decidable": True, "chunks_lus": 1, "creux_retenus": 2,
                  "chunks_a_deux_creux_ou_plus": 1, "espacements": [30],
                  "designent_un_pli": 1, "designent_une_feuille": 0}],
                [aux_plis, aux_feuilles], deux)["les_deux_etalons_se_separent"])

    # ⭐⭐⭐⭐ LES ENONCES DU VERDICT TOMBENT CHACUN SUR L'ENTREE QUI LE VISE.
    def _seg(chunks, pli, feuille, deuxplus, espaces):
        return {"decidable": True, "chunks_lus": int(chunks), "creux_retenus": 2 * int(chunks),
                "chunks_a_deux_creux_ou_plus": int(deuxplus), "espacements": list(espaces),
                "designent_un_pli": int(pli), "designent_une_feuille": int(feuille)}

    def _et(pli_ok, feuille_ok):
        return [{"plis": 2, "feuilles_independantes": False, "cellules": 12, "lisibles": 12,
                 "creux_retenus": 24, "cellules_a_deux_creux_ou_plus": 12,
                 "espacements": [36], "espacement_median": 36.0,
                 "designent_un_pli": 12 if pli_ok else 0,
                 "designent_une_feuille": 0 if pli_ok else 12},
                {"plis": 1, "feuilles_independantes": True, "cellules": 12, "lisibles": 12,
                 "creux_retenus": 12, "cellules_a_deux_creux_ou_plus": 6,
                 "espacements": [72], "espacement_median": 72.0,
                 "designent_un_pli": 0 if feuille_ok else 6,
                 "designent_une_feuille": 6 if feuille_ok else 0}]

    bon = juger([_seg(20, 18, 1, 18, [36] * 20)], _et(True, True), deux)
    v("le rouleau désigne le pli quand ses chunks le désignent",
      bon["le_rouleau_designe"] == "un_pli", str(bon["le_rouleau_designe"]))
    v("et il y a assez de creux pour un espacement",
      bon["assez_de_creux_pour_un_espacement"])
    inv = juger([_seg(20, 1, 18, 18, [72] * 20)], _et(True, True), deux)
    v("il désigne la feuille quand ses chunks la désignent",
      inv["le_rouleau_designe"] == "une_feuille", str(inv["le_rouleau_designe"]))
    ex = juger([_seg(20, 9, 9, 18, [50] * 20)], _et(True, True), deux)
    v("une égalité ne désigne personne", ex["le_rouleau_designe"] is None,
      str(ex["le_rouleau_designe"]))
    pauvre = juger([_seg(20, 18, 1, 3, [36] * 3)], _et(True, True), deux)
    v("trop peu de chunks à deux creux retire le troisième énoncé",
      not pauvre["assez_de_creux_pour_un_espacement"])
    for pli_ok, feuille_ok, quoi in ((False, True, "aux plis"), (True, False, "aux feuilles")):
        x = juger([_seg(20, 18, 1, 18, [36] * 20)], _et(pli_ok, feuille_ok), deux)
        v(f"un étalon {quoi} qui se trompe retire le premier énoncé",
          not x["les_deux_etalons_se_separent"])
    vide = juger([{"decidable": False, "segment": "x", "raison": "muet"}], _et(True, True), deux)
    v("aucun segment lisible rend un verdict indécidable", not vide["decidable"])

    nom = "de_quoi_une_frontiere_est_elle_faite.py"
    if echecs:
        print(f"{nom}   {len(echecs)} ÉCHECS sur {faits}")
        for e in echecs:
            print(f"   ✗ {e}")
        return 1
    print(f"{nom:<46} ALL PASS (0 failures, {faits} checks)")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    p.add_argument("--creux", type=int, default=3)
    p.add_argument("--cote", type=int, default=COTE_DU_TREILLIS)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(a.creux, SEGMENTS, a.cote)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
