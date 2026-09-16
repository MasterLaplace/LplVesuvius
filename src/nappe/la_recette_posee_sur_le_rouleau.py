"""La recette posée sur le vrai rouleau — ce qu'elle y trouve, et ce que ce n'est pas.

⭐⭐⭐⭐ POURQUOI CE FICHIER. `172`–`175` ont construit une recette dont le domaine de validité est
connu : un ajustement en DEUX segments décrit UNE frontière, la fenêtre doit tenir dans un PLI, et
deux fenêtres décalées d'une demi-longueur couvrent tous les décalages. `R4-P30` demande de la poser
sur le rouleau. C'est ce que fait cette tranche, avec le contrôle que la porte exige.

⚠⚠⚠ LE CONTRÔLE EST UNE PERMUTATION DES COUCHES DU MÊME CHUNK, comparée sur la PART ATTEINTE et
jamais sur l'écart. `174` mesure pourquoi : l'écart SURVIT au mélange — le multiensemble des angles
ne change pas — alors que l'ajustement n'y survit pas. Mélanger détruit l'ordre en profondeur et
rien d'autre : chaque couche garde son angle et sa cohérence.

⚠⚠ LA STATISTIQUE EST LA MEILLEURE FENÊTRE DU CHUNK, et le mélange passe par les MÊMES fenêtres.
C'est ce qui contrôle la multiplicité : un chunk découpé en six fenêtres a six occasions de trouver
quelque chose, et le mélange en a six aussi.

⭐⭐⭐⭐ ET LA SECONDE QUESTION N'EST PAS « Y A-T-IL DE L'ORDRE » MAIS « EST-CE UNE BASCULE ». Une
bascule recto/verso est un quart de tour. La même recette, sur la fixture à deux plis dont la
réponse est construite, rend une bascule connue ; la comparer à celle du rouleau est un rapport de
deux nombres mesurés par le MÊME instrument, et aucun seuil n'y entre.

⚠⚠ LA LIMITE DE `174` TIENT ET ELLE EST DITE : une dérive n'est pas séparée d'une marche par un
verdict. Un ordre en profondeur dont l'amplitude n'est pas un quart de tour peut être une rotation
lente, et cette tranche ne les sépare pas.

⚠ LES CHUNKS SE PRENNENT SUR UN TREILLIS RÉGULIER, jamais choisis, et seuls comptent ceux que la
recette du producteur retient — plancher de cohérence et quart des couches texturées, comme
`fiber_orientation.survey`.

Usage :
    uv run python src/nappe/la_recette_posee_sur_le_rouleau.py --verifier
    uv run python src/nappe/la_recette_posee_sur_le_rouleau.py \\
        --json docs/mesures/la_recette_posee_sur_le_rouleau.json
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

from fiber_orientation import orientation_profile  # noqa: E402
from la_coupe_cherchee_trouve_t_elle_la_frontiere import (  # noqa: E402
    ANGLE_DU_PREMIER_PLI_DEG, la_coupe_par_ajustement)
from quelle_fenetre_lit_une_bascule import courbe_de_la_fixture  # noqa: E402
from zarr_depth import BUCKET, array_meta, chunk_key, decode, get  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
VOLUMES = MESURES / "volumes_surface_PHercParis4.txt"
MARQUE_DE_RESOLUTION = "2.4um-"
SEGMENTS = 3
COTE_DU_TREILLIS = 5
PERMUTATIONS = 19
GRAINE = 20260917
PLANCHER_DE_COHERENCE = 0.15
DELAI = 120.0


def les_volumes(chemin: Path = VOLUMES, marque: str = MARQUE_DE_RESOLUTION,
                combien: int = SEGMENTS) -> list[dict]:
    """Les premiers volumes de surface à la résolution de la campagne, DANS L'ORDRE DU FICHIER.

    ⚠⚠ L'ORDRE EST CELUI QUE LE DÉPÔT RECENSE et les `combien` premiers sont pris tels quels : un
    choix parmi eux — les plus texturés, les plus grands — ferait mesurer le choix.
    """
    if not chemin.is_file():
        return []
    out = []
    for ligne in chemin.read_text(encoding="utf-8").splitlines():
        champs = ligne.split("\t")
        if len(champs) < 2 or marque not in champs[1]:
            continue
        out.append({"segment": champs[0], "cle": champs[1]})
        if len(out) >= int(combien):
            break
    return out


def les_chunks(gy: int, gx: int, cote: int = COTE_DU_TREILLIS) -> list[tuple[int, int]]:
    """Un treillis RÉGULIER de positions, sans aucun tirage et identique d'une exécution à l'autre."""
    ys = np.linspace(0, max(0, gy - 1), int(cote))
    xs = np.linspace(0, max(0, gx - 1), int(cote))
    return sorted({(int(y), int(x)) for y in ys for x in xs})


def les_fenetres(couches: int, largeur: int) -> list[int]:
    """Les départs des fenêtres : une largeur de PLI, décalées d'une DEMI-largeur.

    ⚠⚠ LES DEUX VALEURS SONT DÉRIVÉES, PAS CHOISIES. La largeur est celle d'un pli, parce que `175`
    mesure qu'un ajustement en deux segments ne décrit qu'UNE frontière et qu'une fenêtre plus large
    en porte plusieurs. Le pas est la DEMI-largeur, parce que c'est la seule valeur qui met le bord
    d'une fenêtre au centre de la suivante — et une frontière trop près d'un bord n'est pas
    atteignable.

    ⚠ La dernière fenêtre est ramenée sur la fin, sinon les dernières couches ne seraient lues par
    aucune ; le doublon éventuel est écarté.
    """
    if int(largeur) > int(couches):
        return []
    departs = list(range(0, int(couches) - int(largeur) + 1, max(1, int(largeur) // 2)))
    return sorted(set(departs + [int(couches) - int(largeur)]))


def la_bascule_est_lisible(lu: dict) -> bool:
    """La bascule dépasse-t-elle son témoin, lue sur les nombres PUBLIÉS ?

    ⚠⚠⚠ C'EST LA REPARATION D'UN DEFAUT DE `174`, ET ELLE VIT ICI PARCE QUE `174` ET `175` PUBLIENT
    DES COMPTES QUI EN DERIVENT. `la_paire_ajustee` compare les valeurs NON ARRONDIES : sur une
    fenêtre homogène la bascule et le témoin valent tous deux zéro, et un reste de virgule flottante
    de l'ordre de 1e-15 tranche en faveur de la bascule. Le module publie alors « bascule 0,0 ·
    témoin 0,0 · dépasse True » — un booléen qui contredit les deux nombres imprimés à côté de lui.

    ⚠⚠ L'ARRONDI N'EST PAS UN SEUIL AJOUTÉ : c'est la précision que `la_paire_ajustee` publie déjà.
    Comparer autre chose que ce qui est écrit est ce qui a créé le défaut.
    """
    return bool(lu is not None and lu.get("temoin_deg") is not None
                and float(lu["bascule_deg"]) > float(lu["temoin_deg"]))


def lire_un_chunk(courbe, largeur: int) -> dict:
    """La MEILLEURE fenêtre d'un chunk, par la part atteinte.

    ⭐⭐⭐⭐ LA STATISTIQUE EST LE MAXIMUM SUR LES FENÊTRES, et c'est délibéré : un chunk « lit une
    bascule » dès qu'une de ses fenêtres la lit. La multiplicité qui en résulte est contrôlée parce
    que le MÉLANGE passe par exactement les mêmes fenêtres — il a le même nombre d'occasions.

    ⚠ `None` quand aucune fenêtre n'est lisible : un chunk dont aucune part n'a de direction n'est
    pas un chunk sans bascule, c'est un chunk sur lequel la recette ne se prononce pas.
    """
    lus = []
    for depart in les_fenetres(len(courbe), largeur):
        aj = la_coupe_par_ajustement(courbe[depart:depart + int(largeur)])
        if aj is not None:
            lus.append({"depart": int(depart), **aj,
                        "la_bascule_est_lisible": la_bascule_est_lisible(aj)})
    if not lus:
        return {"decidable": False, "raison": "aucune fenêtre lisible",
                "fenetres": len(les_fenetres(len(courbe), largeur))}
    # ⚠⚠⚠ LA PART ATTEINTE SEULE NE CHOISIT PAS, ET `175` L'A MESURE : une fenêtre HOMOGENE rend
    # une part de un, donc un maximum pris sur la part retient une fenêtre où il n'y a rien à
    # trouver. Le choix se fait parmi celles qui LISENT quelque chose ; s'il n'y en a aucune, la
    # meilleure part est rendue quand même, avec le drapeau à faux — un chunk muet se dit.
    qui_lisent = [x for x in lus if x["la_bascule_est_lisible"]]
    meilleur = max(qui_lisent or lus, key=lambda x: x["part_atteinte"])
    return {"decidable": True, "fenetres": len(les_fenetres(len(courbe), largeur)),
            "fenetres_lisibles": len(lus), "fenetres_qui_lisent": len(qui_lisent),
            "depart": meilleur["depart"],
            "coupe": meilleur["coupe"], "part_atteinte": meilleur["part_atteinte"],
            "bascule_deg": meilleur["bascule_deg"], "temoin_deg": meilleur["temoin_deg"],
            "la_bascule_depasse_le_temoin": bool(meilleur["la_bascule_est_lisible"])}


def contre_les_permutations(courbe, largeur: int, permutations: int = PERMUTATIONS,
                            graine: int = GRAINE) -> dict:
    """La lecture réelle, et la même lecture sur des couches MÉLANGÉES.

    ⚠⚠⚠ LA COMPARAISON PORTE SUR LA PART ATTEINTE, JAMAIS SUR L'ÉCART. `174` mesure que l'écart
    maximisé survit au mélange, parce que le multiensemble des angles ne change pas ; l'ajustement
    n'y survit pas, parce que sans ordre en profondeur aucune coupe ne laisse deux parts dirigées.

    ⚠ La graine est fixe et dérivée du numéro de permutation, donc deux exécutions rendent le même
    compte. Un mélange qu'aucune fenêtre ne rend lisible compte comme DÉPASSÉ : le réel fait mieux.
    """
    reel = lire_un_chunk(courbe, largeur)
    if not reel.get("decidable"):
        return {"decidable": False, "raison": reel.get("raison")}
    parts, refuses = [], 0
    for k in range(int(permutations)):
        r = np.random.default_rng(int(graine) + k)
        m = lire_un_chunk([courbe[i] for i in r.permutation(len(courbe))], largeur)
        if m.get("decidable"):
            parts.append(float(m["part_atteinte"]))
        else:
            refuses += 1
    return {**reel, "permutations": int(permutations), "permutations_lues": len(parts),
            "permutations_refusees": int(refuses),
            "part_mediane_des_permutations": (round(float(statistics.median(parts)), 3)
                                              if parts else None),
            "part_maximale_des_permutations": (round(float(max(parts)), 3) if parts else None),
            "elle_depasse_toutes_les_permutations": bool(
                all(reel["part_atteinte"] > x for x in parts)),
            # ⚠⚠ LES DEUX CONDITIONS ENSEMBLE : de l'ordre en profondeur que le melange detruit, ET
            # une MARCHE plutot qu'un bruit lisse — la bascule doit depasser son temoin.
            "elle_lit_quelque_chose": bool(
                all(reel["part_atteinte"] > x for x in parts)
                and reel["la_bascule_depasse_le_temoin"])}


def _med(v):
    return round(float(statistics.median(v)), 3) if v else None


def la_courbe_dun_chunk(url: str, meta: dict, cy: int, cx: int, delai: float = DELAI):
    """La courbe (angle, cohérence) d'un chunk, ou `None` avec la raison du refus.

    ⚠⚠ LE FILTRE EST CELUI DU PRODUCTEUR : un chunk est retenu quand au moins un quart de ses
    couches dépasse le plancher de cohérence, exactement comme `fiber_orientation.survey`. Un filtre
    plus large ferait entrer des fenêtres que `14` n'a jamais lues, et la comparaison à ses
    conclusions cesserait d'en être une.
    """
    profond, hy, hx = meta["chunks"]
    raw = get(f"{url}/{chunk_key(meta, 0, cy, cx)}", delai)
    if raw is None:
        return None, "absent"
    data = decode(raw, meta, profond * hy * hx)
    if data is None:
        return None, "illisible"
    bloc = np.frombuffer(data, dtype=np.dtype(meta["dtype"])).reshape(profond, hy, hx)
    if int(bloc.max()) == 0:
        return None, "vide"
    ang, coh = orientation_profile(bloc)
    if int((coh > PLANCHER_DE_COHERENCE).sum()) < profond // 4:
        return None, "trop peu texturé"
    return [[float(a), float(c)] for a, c in zip(ang, coh)], None


def un_segment(volume: dict, largeur: int, cote: int = COTE_DU_TREILLIS,
               permutations: int = PERMUTATIONS, delai: float = DELAI) -> dict:
    """Un segment : ses chunks du treillis, lus par la recette contre leurs permutations."""
    url = f"{BUCKET}/{volume['cle']}"
    try:
        meta = array_meta(url, 0, delai)
    except Exception as e:  # noqa: BLE001
        return {"decidable": False, "segment": volume["segment"],
                "raison": f"le volume ne répond pas : {type(e).__name__}"}
    profond, hy, hx = meta["chunks"]
    _, rows, cols = meta["shape"]
    gy, gx = -(-rows // hy), -(-cols // hx)
    positions = les_chunks(gy, gx, cote)
    lignes, refus = [], {}
    for cy, cx in positions:
        courbe, pourquoi = la_courbe_dun_chunk(url, meta, cy, cx, delai)
        if courbe is None:
            refus[pourquoi] = refus.get(pourquoi, 0) + 1
            continue
        lignes.append({"chunk": [int(cy), int(cx)],
                       **contre_les_permutations(courbe, largeur, permutations)})
    lus = [x for x in lignes if x.get("decidable")]
    return {"decidable": bool(lus), "segment": volume["segment"],
            "zarr": volume["cle"].rsplit("/", 1)[-1], "couches": int(profond),
            "grille_de_chunks": [int(gy), int(gx)], "largeur": int(largeur),
            "fenetres": len(les_fenetres(int(profond), int(largeur))),
            "chunks_du_treillis": len(positions), "chunks_lus": len(lus), "refuses": refus,
            "part_mediane": _med([x["part_atteinte"] for x in lus]),
            "part_mediane_des_permutations": _med([x["part_mediane_des_permutations"] for x in lus
                                                   if x["part_mediane_des_permutations"]
                                                   is not None]),
            "bascule_mediane_deg": _med([x["bascule_deg"] for x in lus]),
            "temoin_median_deg": _med([x["temoin_deg"] for x in lus]),
            "depassent_toutes_les_permutations": int(
                sum(1 for x in lus if x["elle_depasse_toutes_les_permutations"])),
            "depassent_le_temoin": int(sum(1 for x in lus if x["la_bascule_depasse_le_temoin"])),
            "lisent_quelque_chose": int(sum(1 for x in lus if x["elle_lit_quelque_chose"])),
            "lignes": lignes}


def sur_la_fixture(largeur: int, permutations: int = PERMUTATIONS) -> dict:
    """La MÊME recette sur la fixture à deux plis, dont la réponse est construite.

    ⭐⭐⭐⭐ C'EST L'ÉTALON, ET SANS LUI LA BASCULE DU ROULEAU N'A PAS D'ÉCHELLE. Une bascule
    recto/verso est un quart de tour ; savoir ce que la recette rend sur une matière qui en a une
    permet de dire ce que celle du rouleau n'est pas, sans choisir aucun seuil.

    ⚠ La fixture est lue par le MÊME chemin que le rouleau — mêmes fenêtres, mêmes permutations —
    sinon on comparerait deux instruments en croyant comparer deux matières.
    """
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    vx, pas = C.VOXEL_FIN_UM, C.PAS_UM
    lignes = []
    for k in range(12):
        dec = float(pas) * k / 12.0
        courbe = courbe_de_la_fixture(109, dec, 0.5, 2, vx, pas)
        lignes.append({"decalage_um": round(dec, 3),
                       **contre_les_permutations(courbe, largeur, permutations)})
    lus = [x for x in lignes if x.get("decidable")]
    return {"decidable": bool(lus), "cellules": len(lignes), "lisibles": len(lus),
            "largeur": int(largeur), "angle_du_premier_pli_deg": float(ANGLE_DU_PREMIER_PLI_DEG),
            "part_mediane": _med([x["part_atteinte"] for x in lus]),
            "bascule_mediane_deg": _med([x["bascule_deg"] for x in lus]),
            "temoin_median_deg": _med([x["temoin_deg"] for x in lus]),
            "lisent_quelque_chose": int(sum(1 for x in lus if x["elle_lit_quelque_chose"])),
            "lignes": lignes}


def juger(segments: list[dict], fixture: dict, permutations: int = PERMUTATIONS) -> dict:
    """Ce que le rouleau rend, et ce que ce n'est pas.

    ⚠⚠⚠ LE COMPTE ATTENDU SOUS L'HYPOTHESE NULLE EST PUBLIE A COTE DU COMPTE OBSERVE : avec `K`
    permutations, un chunk les dépasse toutes par hasard une fois sur `K+1`. Sans ce nombre,
    « trois chunks sur soixante » se lirait comme un résultat alors que c'est le hasard.

    ⭐⭐⭐⭐ ET LA SECONDE MOITIÉ EST L'ÉCHELLE : la bascule du rouleau rapportée à celle que la MÊME
    recette rend sur une matière qui a une bascule construite. C'est un rapport de deux nombres
    mesurés, pas un seuil.
    """
    lus = [s for s in segments if s.get("decidable")]
    if not lus:
        return {"decidable": False, "raison": "aucun segment lisible",
                "segments_essayes": len(segments)}
    chunks = sum(s["chunks_lus"] for s in lus)
    depassent = sum(s["depassent_toutes_les_permutations"] for s in lus)
    lisent = sum(s["lisent_quelque_chose"] for s in lus)
    bascule = _med([s["bascule_mediane_deg"] for s in lus
                    if s["bascule_mediane_deg"] is not None])
    etalon = fixture.get("bascule_mediane_deg")
    return {"decidable": True, "segments": len(lus), "segments_essayes": len(segments),
            "chunks_lus": chunks, "permutations": int(permutations),
            "chunks_attendus_par_hasard": round(chunks / (int(permutations) + 1.0), 2),
            "depassent_toutes_les_permutations": int(depassent),
            "depassent_le_temoin": int(sum(s["depassent_le_temoin"] for s in lus)),
            "lisent_quelque_chose": int(lisent),
            "part_mediane_du_rouleau": _med([s["part_mediane"] for s in lus
                                             if s["part_mediane"] is not None]),
            "part_mediane_des_permutations": _med([s["part_mediane_des_permutations"] for s in lus
                                                   if s["part_mediane_des_permutations"]
                                                   is not None]),
            "bascule_mediane_du_rouleau_deg": bascule,
            "bascule_mediane_de_la_fixture_deg": etalon,
            "le_rouleau_vaut_la_fixture_fois": (round(bascule / etalon, 3)
                                                if bascule and etalon else None),
            "temoin_median_du_rouleau_deg": _med([s["temoin_median_deg"] for s in lus
                                                  if s["temoin_median_deg"] is not None]),
            # ⚠⚠ DEUX ENONCES DISTINCTS, ET IL FAUT LES DEUX. Le premier dit s'il y a de l'ordre en
            # profondeur ; le second dit si cet ordre a l'amplitude d'une bascule recto/verso. L'un
            # sans l'autre ferait lire soit « rien », soit « la bascule est la ».
            "il_y_a_de_lordre_en_profondeur": bool(
                chunks and lisent > chunks / (int(permutations) + 1.0)),
            "son_amplitude_est_celle_dune_bascule": bool(
                bascule is not None and etalon is not None and bascule >= etalon)}


def mesurer(combien: int = SEGMENTS, cote: int = COTE_DU_TREILLIS,
            permutations: int = PERMUTATIONS) -> dict:
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    # ⚠⚠ LA LARGEUR EST CELLE D'UN PLI, DERIVEE DU PAS ET DU VOXEL, jamais ecrite a la main.
    largeur = int(round(C.PAS_UM / 2.0 / C.VOXEL_FIN_UM))
    volumes = les_volumes(combien=combien)
    if not volumes:
        return {"message": "aucun volume de surface à la résolution de la campagne n'est recensé"}
    segments = [un_segment(v, largeur, cote, permutations) for v in volumes]
    fixture = sur_la_fixture(largeur, permutations)
    return {"largeur_en_couches": largeur, "pas_um": float(C.PAS_UM),
            "voxel_um": float(C.VOXEL_FIN_UM), "cote_du_treillis": int(cote),
            "permutations": int(permutations), "graine": int(GRAINE),
            "plancher_de_coherence": float(PLANCHER_DE_COHERENCE),
            "les_segments": segments, "la_fixture": fixture,
            "le_verdict": juger(segments, fixture, permutations)}


def afficher(r: dict) -> None:
    if "message" in r:
        print(r["message"])
        return
    fx, v = r["la_fixture"], r["le_verdict"]
    print("LA RECETTE POSÉE SUR LE ROULEAU")
    print(f"  largeur {r['largeur_en_couches']} couches (un pli : {r['pas_um']}/2 µm à "
          f"{r['voxel_um']} µm) · treillis {r['cote_du_treillis']}×{r['cote_du_treillis']} · "
          f"{r['permutations']} permutations")
    print()
    for s in r["les_segments"]:
        if not s.get("decidable"):
            print(f"  {s['segment']} — {s.get('raison')}")
            continue
        print(f"  {s['segment']} · {s['couches']} couches · {s['fenetres']} fenêtres · "
              f"{s['chunks_lus']}/{s['chunks_du_treillis']} chunks · refusés {s['refuses']}")
        print(f"     part {s['part_mediane']} contre permutations "
              f"{s['part_mediane_des_permutations']} · bascule "
              f"{s['bascule_mediane_deg']}° · témoin {s['temoin_median_deg']}° · dépassent "
              f"{s['depassent_toutes_les_permutations']} · lisent "
              f"{s['lisent_quelque_chose']}/{s['chunks_lus']}")
    print()
    print(f"  L'ÉTALON · la MÊME recette sur la fixture à deux plis "
          f"({fx['lisibles']}/{fx['cellules']} lisibles)")
    print(f"     part {fx['part_mediane']} · bascule {fx['bascule_mediane_deg']}° · témoin "
          f"{fx['temoin_median_deg']}° · lisent {fx['lisent_quelque_chose']}/{fx['lisibles']}")
    print()
    if not v.get("decidable"):
        print(f"  ✗ {v.get('raison')}")
        return
    print(f"  ★ LE VERDICT · {v['chunks_lus']} chunks sur {v['segments']} segments · attendu par "
          f"hasard {v['chunks_attendus_par_hasard']}")
    for cle in ("depassent_toutes_les_permutations", "depassent_le_temoin",
                "lisent_quelque_chose", "part_mediane_du_rouleau",
                "part_mediane_des_permutations", "bascule_mediane_du_rouleau_deg",
                "bascule_mediane_de_la_fixture_deg", "le_rouleau_vaut_la_fixture_fois",
                "temoin_median_du_rouleau_deg", "il_y_a_de_lordre_en_profondeur",
                "son_amplitude_est_celle_dune_bascule"):
        print(f"     {cle:<44} {v.get(cle)}")


def verifier() -> int:
    echecs = controles = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    import combien_dinterstices_traverses as C  # noqa: PLC0415
    largeur = int(round(C.PAS_UM / 2.0 / C.VOXEL_FIN_UM))

    # ---- les fenetres : largeur d'un pli, pas d'une demi-largeur, DERIVES
    f = les_fenetres(109, largeur)
    v("la largeur est celle d'un pli, dérivée du pas et du voxel", largeur == 36,
      f"{largeur} couches pour un pli de {C.PAS_UM / 2.0} µm à {C.VOXEL_FIN_UM} µm")
    # ⚠⚠ LE PAS SE VERIFIE PAR SA REGLE : chaque depart est a une demi-largeur du precedent, sauf
    # le dernier qui est ramene sur la fin pour qu'aucune couche ne soit lue par personne.
    v("⚠⚠ les fenêtres avancent d'une DEMI-largeur",
      all(b - a == largeur // 2 for a, b in zip(f, f[1:-1])),
      f"{f}")
    v("... et la dernière est ramenée sur la fin, donc toutes les couches sont lues",
      f[-1] + largeur == 109 and f[0] == 0)
    v("⚠ une fenêtre plus large que la courbe ne rend aucun départ", les_fenetres(20, 36) == [])

    # ---- la lecture d'un chunk : le maximum sur les fenetres
    # ⚠⚠ L'ATTENDU SE DERIVE DE LA FIXTURE : une courbe dont UNE fenetre porte une marche franche
    # et les autres rien doit rendre CETTE fenetre, et sa part doit valoir un.
    plate = [[20.0, 0.9]] * 109
    marche = list(plate)
    for i in range(54, 72):
        marche[i] = [110.0, 0.9]
    # ⚠⚠⚠ LE DEFAUT DE `174`, MESURE PLUTOT QU'AFFIRME : sur une fenetre homogene le module publie
    # une bascule de 0,0 et un temoin de 0,0, et affirme pourtant que la premiere depasse le second.
    homogene = la_coupe_par_ajustement(plate[:largeur])
    v("⚠⚠⚠ `174` publie bascule 0,0 et témoin 0,0 en affirmant que la première dépasse",
      homogene is not None and homogene["bascule_deg"] == 0.0
      and homogene["temoin_deg"] == 0.0 and homogene["la_bascule_depasse_le_temoin"] is True,
      f"bascule {homogene and homogene['bascule_deg']}, témoin "
      f"{homogene and homogene['temoin_deg']}, dépasse "
      f"{homogene and homogene['la_bascule_depasse_le_temoin']}")
    v("⭐⭐⭐⭐ ... et la comparaison réparée, qui lit les nombres PUBLIÉS, dit non",
      la_bascule_est_lisible(homogene) is False)
    # ⚠⚠ ET LE CHOIX DE LA FENETRE SUIT : une part de un ne suffit pas, `175` l'a mesure.
    lu = lire_un_chunk(marche, largeur)
    v("⭐⭐⭐⭐ la lecture d'un chunk retient une fenêtre qui LIT, pas une fenêtre homogène",
      lu["decidable"] and lu["part_atteinte"] == 1.0 and lu["la_bascule_depasse_le_temoin"]
      and lu["bascule_deg"] > 0.0,
      f"départ {lu.get('depart')}, coupe {lu.get('coupe')}, part {lu.get('part_atteinte')}, "
      f"bascule {lu.get('bascule_deg')}°")
    plat = lire_un_chunk(plate, largeur)
    v("⚠ une courbe entièrement plate ne rend aucune bascule",
      not plat["la_bascule_depasse_le_temoin"] and plat["fenetres_qui_lisent"] == 0,
      f"{plat['fenetres_qui_lisent']}/{plat['fenetres_lisibles']} fenêtres qui lisent")
    # ⚠⚠ ET LE MELANGE PASSE PAR LES MEMES FENETRES : c'est ce qui controle la multiplicite.
    cp = contre_les_permutations(marche, largeur, permutations=9)
    v("⭐⭐⭐⭐ la marche bat toutes ses permutations",
      cp["decidable"] and cp["elle_depasse_toutes_les_permutations"]
      and cp["elle_lit_quelque_chose"],
      f"part {cp.get('part_atteinte')} contre permutation max "
      f"{cp.get('part_maximale_des_permutations')}")
    r0 = np.random.default_rng(7)
    bruit = [[float(a), 0.9] for a in r0.uniform(0.0, 180.0, 109)]
    cb = contre_les_permutations(bruit, largeur, permutations=9)
    v("⚠⚠⚠ contrôle : du bruit ne bat PAS toutes ses permutations",
      not cb.get("decidable") or not cb["elle_depasse_toutes_les_permutations"],
      f"{cb.get('part_atteinte')} contre {cb.get('part_maximale_des_permutations')}")

    # ---- le treillis
    t = les_chunks(396, 285, 5)
    v("le treillis couvre la grille de bord à bord et se rejoue à l'identique",
      t[0] == (0, 0) and t[-1] == (395, 284) and t == les_chunks(396, 285, 5),
      f"{len(t)} positions")

    # ---- le verdict compare a un compte CONNU et porte DEUX enonces
    faux = juger([{"decidable": True, "chunks_lus": 40, "part_mediane": 0.9,
                   "part_mediane_des_permutations": 0.8, "bascule_mediane_deg": 20.0,
                   "temoin_median_deg": 10.0, "depassent_toutes_les_permutations": 2,
                   "depassent_le_temoin": 2, "lisent_quelque_chose": 2}],
                 {"bascule_mediane_deg": 90.0}, permutations=19)
    v("⚠⚠⚠ deux chunks sur quarante ne dépassent PAS le hasard, et le verdict le dit",
      faux["chunks_attendus_par_hasard"] == 2.0
      and faux["il_y_a_de_lordre_en_profondeur"] is False,
      f"attendu {faux['chunks_attendus_par_hasard']}")
    v("⭐⭐⭐⭐ ... et une bascule de vingt degrés n'a PAS l'amplitude d'un quart de tour",
      faux["son_amplitude_est_celle_dune_bascule"] is False
      and faux["le_rouleau_vaut_la_fixture_fois"] == 0.222,
      f"×{faux['le_rouleau_vaut_la_fixture_fois']} de l'étalon")
    vrai = juger([{"decidable": True, "chunks_lus": 40, "part_mediane": 0.9,
                   "part_mediane_des_permutations": 0.5, "bascule_mediane_deg": 95.0,
                   "temoin_median_deg": 10.0, "depassent_toutes_les_permutations": 30,
                   "depassent_le_temoin": 30, "lisent_quelque_chose": 30}],
                 {"bascule_mediane_deg": 90.0}, permutations=19)
    v("... et trente sur quarante à quatre-vingt-quinze degrés le dépassent des deux façons",
      vrai["il_y_a_de_lordre_en_profondeur"] and vrai["son_amplitude_est_celle_dune_bascule"])
    v("un lot sans segment lisible n'est pas décidable",
      juger([{"decidable": False}], {}).get("decidable") is False)

    # ---- les volumes viennent du dépôt, filtrés par la RÉSOLUTION
    vols = les_volumes(combien=3)
    v("les volumes de la campagne sont recensés à la résolution voulue",
      len(vols) == 3 and all(MARQUE_DE_RESOLUTION in x["cle"] for x in vols),
      " · ".join(x["segment"] for x in vols))
    v("⚠ et une résolution absente rend une liste VIDE, jamais une autre résolution",
      les_volumes(marque="0.001um-") == [])

    print()
    if echecs:
        print(f"ÉCHEC ({echecs} failures, {controles} checks)")
    else:
        print(f"ALL PASS (0 failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path, default=None)
    p.add_argument("--segments", type=int, default=SEGMENTS)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(combien=a.segments)
    afficher(r)
    if "message" in r:
        return 1
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False))
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
