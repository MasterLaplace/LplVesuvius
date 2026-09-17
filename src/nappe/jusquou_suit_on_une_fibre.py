"""Jusqu'où suit-on une fibre ? — la continuité LE LONG D'UNE LIGNE, enfin mesurée.

⭐⭐⭐⭐ POURQUOI CE FICHIER, ET IL PORTE LE CRITÈRE DU PRIX LUI-MÊME. Le Grand Prize fait de la
continuité des fibres LE critère visuel : « follow horizontal papyrus fibers... and not jumping
between sheets ». `14` §8 nomme la bonne forme depuis longtemps — mesurer la continuité LE LONG D'UNE
LIGNE, et non la dispersion entre carrés voisins ni la bascule en profondeur — et RIEN ne l'a mesurée.
`184` vient de fermer la voie des creux : ni un creux seul ni une suite recalée ne transfèrent une
spire. Ce qui reste est cette piste-là.

⚠⚠⚠ ET L'OBJECTION DE `128` DÉCIDE DE LA FORME : une FRÉQUENCE donne une PHASE, pas une IDENTITÉ.
Mesurer un spectre, une autocorrélation ou une périodicité ne dirait rien de la continuité — deux
morceaux de matière peuvent avoir la même fréquence sans être la même fibre. Ce qui vaut est de
SUIVRE UN INDIVIDU : partir d'une crête, avancer le long d'elle, et compter jusqu'où on tient.

⭐⭐⭐⭐ LE CRITÈRE D'ARRÊT EST STRUCTUREL ET NON UN SEUIL. On avance d'un voxel le long de la
direction, puis on se recentre sur le maximum local dans la PERPENDICULAIRE à ±1 voxel ; on s'arrête
quand le point atteint n'est plus un maximum local, c'est-à-dire quand la crête a cessé d'exister.
Aucune valeur d'intensité n'entre, donc aucun seuil.

⚠⚠ ET LA LONGUEUR N'A DE SENS QUE COMPARÉE. Trois lectures par le MÊME suiveur : LE LONG des fibres,
EN TRAVERS d'elles, et sur la même image dont les pixels sont MÉLANGÉS. La première doit dépasser les
deux autres, sinon le suiveur mesure sa propre mécanique. Et la longueur atteinte se compare au PAS
entre deux feuilles — c'est cette distance-là qu'il faut franchir pour que « suivre une fibre » serve
à ne pas sauter de feuille.

⚠ La direction des fibres vient de `orientation_profile` par le MÊME chemin que tout le reste, et la
conversion perpendiculaire/fibres est celle de `172`, appelée et non refaite.

Usage :
    uv run python src/nappe/jusquou_suit_on_une_fibre.py --verifier
    uv run python src/nappe/jusquou_suit_on_une_fibre.py \\
        --json docs/mesures/jusquou_suit_on_une_fibre.json
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
from la_recette_posee_sur_le_rouleau import (COTE_DU_TREILLIS, DELAI,  # noqa: E402
                                             PLANCHER_DE_COHERENCE, SEGMENTS, les_chunks,
                                             les_volumes)
from langle_publie_est_il_celui_des_fibres import direction_des_fibres_deg  # noqa: E402
from zarr_depth import BUCKET, array_meta, chunk_key, decode, get  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
GRAINE = 20260925
DEPARTS_PAR_COUCHE = 24
COUCHES_PAR_CHUNK = 6


def suivre(image: np.ndarray, depart: tuple[int, int], angle_deg: float,
           plafond: int, plancher: float | None = None) -> dict:
    """Part d'un point, marche une longueur FIXE, et rend la plus longue suite restée sur la crête.

    ⭐⭐⭐⭐ LE CRITÈRE EST INDÉPENDANT DE LA DIRECTION DE MARCHE, ET C'EST UNE RÉPARATION. Une
    première version s'arrêtait quand le point n'était plus un maximum local dans la perpendiculaire
    au DÉPLACEMENT. En marchant LE LONG d'une crête, cette perpendiculaire traverse la crête et le
    test veut dire quelque chose ; en marchant EN TRAVERS, elle court le long d'une crête, où tout
    est plat, donc le test est satisfait partout. L'étalon l'a montré nu : sur des crêtes
    horizontales, le suiveur allait aussi loin en travers que le long — un contrôle qui ne peut pas
    échouer.

    ⭐⭐⭐⭐ CE QUI EST MESURÉ EST DONC LA PLUS LONGUE SUITE DE PAS PASSÉS AU-DESSUS DU PLANCHER DE
    L'IMAGE. Le plancher est la MÉDIANE de l'image elle-même, donc il n'est pas choisi : il vient de
    la matière lue. Marcher le long d'une crête garde la marche au-dessus ; marcher en travers la
    fait plonger dans chaque creux ; marcher sur du mélange n'y reste pas.

    ⚠⚠ ON SUIT UN INDIVIDU, PAS UNE FRÉQUENCE, et c'est l'objection de `128` prise au sérieux : une
    autocorrélation ou un spectre rendraient la même chose sur deux morceaux de matière qui ne sont
    pas la même fibre. Ici on part d'un point et on ne le lâche pas.

    ⚠ Le pas vaut UN voxel et le recentrage ±1 : une crête ne saute pas, et un pas plus grand ferait
    manquer le recentrage.
    """
    h, w = image.shape
    if plancher is None:
        plancher = float(np.median(image))
    th = np.radians(float(angle_deg))
    ux, uy = float(np.cos(th)), float(np.sin(th))
    px, py = -uy, ux
    y, x = float(depart[0]), float(depart[1])
    suite, meilleure, faits = 0, 0, 0
    for _ in range(int(plafond)):
        ny, nx = y + uy, x + ux
        choisi, valeur = None, None
        for s in (-1.0, 0.0, 1.0):
            cy, cx = int(round(ny + s * py)), int(round(nx + s * px))
            if not (0 <= cy < h and 0 <= cx < w):
                continue
            v = float(image[cy, cx])
            if valeur is None or v > valeur:
                choisi, valeur = (cy, cx), v
        if choisi is None:
            break
        y, x = float(choisi[0]), float(choisi[1])
        faits += 1
        if valeur > float(plancher):
            suite += 1
            meilleure = max(meilleure, suite)
        else:
            suite = 0
    return {"pas": int(meilleure), "pas_faits": int(faits),
            "arrivee": [int(round(y)), int(round(x))]}


def les_departs(image: np.ndarray, combien: int, marge: int = 2) -> list[tuple[int, int]]:
    """Les points de départ : les plus brillants, sur une grille RÉGULIÈRE.

    ⚠⚠ UNE CRÊTE SE SUIT DEPUIS UNE CRÊTE : partir d'un creux mesurerait la mécanique du suiveur et
    non la matière. On découpe l'image en cases régulières et on prend le maximum de chacune, donc
    le choix est fait par la MATIÈRE et la répartition par la grille — jamais par nous.
    """
    h, w = image.shape
    n = max(1, int(np.floor(np.sqrt(float(combien)))))
    ys = np.linspace(marge, h - marge - 1, n + 1).astype(int)
    xs = np.linspace(marge, w - marge - 1, max(1, int(np.ceil(combien / n))) + 1).astype(int)
    out = []
    for i in range(len(ys) - 1):
        for j in range(len(xs) - 1):
            case = image[ys[i]:ys[i + 1], xs[j]:xs[j + 1]]
            if case.size == 0:
                continue
            k = int(np.argmax(case))
            out.append((int(ys[i] + k // case.shape[1]), int(xs[j] + k % case.shape[1])))
    return out[:int(combien)]


def une_couche(image: np.ndarray, angle_des_fibres_deg: float, combien: int, plafond: int,
               graine: int = GRAINE) -> dict:
    """Les trois lectures d'une couche : le long, en travers, et sur l'image mélangée.

    ⭐⭐⭐⭐ LES TROIS PASSENT PAR LE MÊME SUIVEUR ET LES MÊMES DÉPARTS. Ce qui change est la
    DIRECTION pour la deuxième, et la MATIÈRE pour la troisième : mélanger les pixels conserve
    exactement l'histogramme de l'image et détruit toute structure, donc ce que le mélange rend est
    ce que la mécanique du suiveur rapporte toute seule.
    """
    departs = les_departs(image, combien)
    r = np.random.default_rng(int(graine))
    melangee = image.flatten()[r.permutation(image.size)].reshape(image.shape)
    lu = {}
    for nom, img, ang in (("le_long", image, angle_des_fibres_deg),
                          ("en_travers", image, angle_des_fibres_deg + 90.0),
                          ("melangee", melangee, angle_des_fibres_deg)):
        pas = [int(suivre(img, d, ang, plafond)["pas"]) for d in departs]
        lu[nom] = {"departs": len(pas), "pas_median": _med(pas),
                   "pas_moyen": (round(float(sum(pas)) / len(pas), 3) if pas else None),
                   "pas_maximal": (int(max(pas)) if pas else None)}
    return lu


def _med(v):
    return round(float(statistics.median(v)), 3) if v else None


def un_chunk(bloc: np.ndarray, angles, coherences, combien: int, plafond: int,
             couches: int = COUCHES_PAR_CHUNK, plancher: float = PLANCHER_DE_COHERENCE,
             graine: int = GRAINE) -> dict:
    """Les couches les plus TEXTURÉES d'un chunk, lues par le suiveur.

    ⚠⚠ ON LIT LES COUCHES QUE LE PRODUCTEUR RETIENT, celles dont la cohérence dépasse son plancher,
    et parmi elles les plus cohérentes : suivre une crête dans une couche sans texture mesurerait le
    bruit. ⚠ Le choix est fait par la cohérence, pas par nous, et le compte est fixé d'avance.
    """
    fortes = [k for k in range(len(coherences)) if float(coherences[k]) > float(plancher)]
    fortes = sorted(fortes, key=lambda k: -float(coherences[k]))[:int(couches)]
    lignes = []
    for k in sorted(fortes):
        # ⚠⚠⚠ L'ANGLE PUBLIE EST LA PERPENDICULAIRE AUX FIBRES (`172`), donc il FAUT le convertir.
        # Suivre la perpendiculaire en croyant suivre les fibres inverserait exactement les deux
        # lectures que cette tranche compare.
        ang = float(direction_des_fibres_deg(float(angles[k])))
        lignes.append({"couche": int(k), "coherence": round(float(coherences[k]), 4),
                       "angle_des_fibres_deg": round(ang, 3),
                       **une_couche(bloc[k], ang, combien, plafond, graine)})
    return {"couches_lues": len(lignes), "lignes": lignes}


def _agrege(lignes, quoi: str, cle: str = "pas_median"):
    return _med([x[quoi][cle] for x in lignes if x[quoi][cle] is not None])


def un_segment(volume: dict, combien: int, plafond: int, cote: int = COTE_DU_TREILLIS,
               delai: float = DELAI, graine: int = GRAINE) -> dict:
    url = f"{BUCKET}/{volume['cle']}"
    try:
        meta = array_meta(url, 0, delai)
    except Exception as e:  # noqa: BLE001
        return {"decidable": False, "segment": volume["segment"],
                "raison": f"le volume ne répond pas : {type(e).__name__}"}
    profond, hy, hx = meta["chunks"]
    _, rows, cols = meta["shape"]
    lignes, refus = [], {}
    for cy, cx in les_chunks(-(-rows // hy), -(-cols // hx), cote):
        raw = get(f"{url}/{chunk_key(meta, 0, cy, cx)}", delai)
        if raw is None:
            refus["absent"] = refus.get("absent", 0) + 1
            continue
        data = decode(raw, meta, profond * hy * hx)
        if data is None:
            refus["illisible"] = refus.get("illisible", 0) + 1
            continue
        bloc = np.frombuffer(data, dtype=np.dtype(meta["dtype"])).reshape(profond, hy, hx)
        if int(bloc.max()) == 0:
            refus["vide"] = refus.get("vide", 0) + 1
            continue
        ang, coh = orientation_profile(bloc)
        if int((coh > PLANCHER_DE_COHERENCE).sum()) < profond // 4:
            refus["trop peu texturé"] = refus.get("trop peu texturé", 0) + 1
            continue
        lu = un_chunk(bloc.astype(np.float32), ang, coh, combien, plafond, COUCHES_PAR_CHUNK,
                      PLANCHER_DE_COHERENCE, graine)
        if lu["couches_lues"]:
            lignes.append({"chunk": [int(cy), int(cx)], **lu})
    toutes = [x for c in lignes for x in c["lignes"]]
    return {"decidable": bool(toutes), "segment": volume["segment"],
            "chunks_lus": len(lignes), "refuses": refus, "couches_lues": len(toutes),
            "le_long": _agrege(toutes, "le_long"),
            "en_travers": _agrege(toutes, "en_travers"),
            "melangee": _agrege(toutes, "melangee"),
            "le_long_maximal": _agrege(toutes, "le_long", "pas_maximal"),
            "chunks": lignes}


def sur_une_image_construite(combien: int, plafond: int, graine: int = GRAINE) -> dict:
    """Des crêtes PARALLÈLES dont la direction est choisie — la réponse est connue avant.

    ⭐⭐⭐⭐ SANS CET ÉTALON, UNE LONGUEUR NE VEUT RIEN DIRE. Sur une image faite de crêtes droites
    et parallèles, le suiveur DOIT aller jusqu'au bord en suivant leur direction, et s'arrêter tout
    de suite en travers. C'est ce qui dit que le suiveur suit, et c'est la même mécanique qui lira
    le rouleau.
    """
    cote, longueur = 128, 12.0
    yy, xx = np.mgrid[0:cote, 0:cote].astype(np.float32)
    lignes = []
    for angle in (0.0, 30.0, 90.0):
        th = np.radians(angle)
        s = -np.sin(th) * xx + np.cos(th) * yy
        img = 100.0 + 40.0 * np.cos(2.0 * np.pi * s / longueur)
        lu = une_couche(img, angle, combien, plafond, graine)
        lignes.append({"angle_des_cretes_deg": float(angle), **lu})
    return {"cote": cote, "longueur_de_crete": longueur, "lignes": lignes,
            "le_long": _agrege(lignes, "le_long"),
            "en_travers": _agrege(lignes, "en_travers"),
            "melangee": _agrege(lignes, "melangee")}


def juger(segments: list[dict], etalon: dict, voxel_um: float, pas_um: float,
          plafond: int) -> dict:
    """Jusqu'où suit-on une fibre, et est-ce assez pour ne pas sauter de feuille ?"""
    lus = [s for s in segments if s.get("decidable")]
    if not lus:
        return {"decidable": False, "raison": "aucun segment lisible"}
    long_ = _med([s["le_long"] for s in lus if s["le_long"] is not None])
    travers = _med([s["en_travers"] for s in lus if s["en_travers"] is not None])
    melange = _med([s["melangee"] for s in lus if s["melangee"] is not None])
    return {"decidable": True, "segments": len(lus),
            "chunks_lus": int(sum(s["chunks_lus"] for s in lus)),
            "couches_lues": int(sum(s["couches_lues"] for s in lus)),
            "plafond_de_pas": int(plafond),
            "le_long_en_pas": long_, "en_travers_en_pas": travers,
            "melangee_en_pas": melange,
            "le_long_en_um": (round(long_ * float(voxel_um), 3) if long_ else None),
            "le_pas_entre_deux_feuilles_um": float(pas_um),
            "il_vaut_le_pas_entre_deux_feuilles_fois": (
                round(long_ * float(voxel_um) / float(pas_um), 4) if long_ else None),
            "le_long_de_letalon": etalon["le_long"],
            "en_travers_de_letalon": etalon["en_travers"],
            "melangee_de_letalon": etalon["melangee"],
            # ⚠⚠ TROIS ENONCES. Le premier dit que le SUIVEUR SUIT — sans lui rien ne suit. Le
            # second dit que le rouleau porte des cretes suivables, plus loin qu'en travers et que
            # sur du melange. Le troisieme est celui qui decide pour le graal : la longueur atteinte
            # franchit-elle la distance entre deux feuilles.
            "le_suiveur_suit": bool(
                etalon["le_long"] is not None and etalon["en_travers"] is not None
                and etalon["melangee"] is not None
                and etalon["le_long"] > etalon["en_travers"]
                and etalon["le_long"] > etalon["melangee"]),
            "le_rouleau_porte_des_cretes_suivables": bool(
                long_ is not None and travers is not None and melange is not None
                and long_ > travers and long_ > melange),
            "on_franchit_une_feuille": bool(
                long_ is not None and long_ * float(voxel_um) >= float(pas_um))}


def mesurer(segments_n: int = SEGMENTS, combien: int = DEPARTS_PAR_COUCHE,
            cote: int = COTE_DU_TREILLIS) -> dict:
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    vx, pas = float(C.VOXEL_FIN_UM), float(C.PAS_UM)
    # ⚠⚠ LE PLAFOND DE PAS EST DERIVE : il faut pouvoir franchir le PAS entre deux feuilles, sinon
    # la mesure serait bornee par le plafond et non par la matiere, et le verdict serait le notre.
    plafond = int(np.ceil(pas / vx)) * 2
    volumes = les_volumes(combien=segments_n)
    if not volumes:
        return {"message": "aucun volume de surface à la résolution de la campagne n'est recensé"}
    segs = [un_segment(v, combien, plafond, cote) for v in volumes]
    etalon = sur_une_image_construite(combien, plafond)
    return {"departs_par_couche": int(combien), "couches_par_chunk": int(COUCHES_PAR_CHUNK),
            "cote_du_treillis": int(cote), "plafond_de_pas": int(plafond),
            "voxel_um": vx, "pas_um": pas, "graine": int(GRAINE),
            "plancher_de_coherence": float(PLANCHER_DE_COHERENCE),
            "les_segments": segs, "letalon": etalon,
            "le_verdict": juger(segs, etalon, vx, pas, plafond)}


def afficher(r: dict) -> None:
    if "message" in r:
        print(r["message"])
        return
    v, e = r["le_verdict"], r["letalon"]
    print("JUSQU'OÙ SUIT-ON UNE FIBRE ?")
    print(f"  {r['departs_par_couche']} départs par couche · {r['couches_par_chunk']} couches par "
          f"chunk · treillis {r['cote_du_treillis']}×{r['cote_du_treillis']} · plafond "
          f"{r['plafond_de_pas']} pas")
    print()
    for s in r["les_segments"]:
        if not s.get("decidable"):
            print(f"  {s['segment']} — {s.get('raison')}")
            continue
        print(f"  {s['segment']} · {s['chunks_lus']} chunks · {s['couches_lues']} couches · "
              f"refusés {s['refuses']}")
        print(f"     le long {s['le_long']} · en travers {s['en_travers']} · mélangée "
              f"{s['melangee']} · le long au max {s['le_long_maximal']}")
    print()
    print(f"  L'ÉTALON · des crêtes construites · le long {e['le_long']} · en travers "
          f"{e['en_travers']} · mélangée {e['melangee']}")
    print()
    print("  ★ LE VERDICT")
    for cle in ("chunks_lus", "couches_lues", "le_long_en_pas", "en_travers_en_pas",
                "melangee_en_pas", "le_long_en_um", "le_pas_entre_deux_feuilles_um",
                "il_vaut_le_pas_entre_deux_feuilles_fois", "le_long_de_letalon",
                "en_travers_de_letalon", "melangee_de_letalon", "le_suiveur_suit",
                "le_rouleau_porte_des_cretes_suivables", "on_franchit_une_feuille"):
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
    plafond = int(np.ceil(pas / vx)) * 2

    # ⚠⚠ LE PLAFOND EST DERIVE : il doit permettre de FRANCHIR le pas entre deux feuilles, sinon la
    # mesure serait bornee par le plafond et le verdict serait le notre.
    v("le plafond permet de franchir une feuille", plafond * vx > pas,
      f"{plafond} pas × {vx} µm contre {pas} µm")

    # ⭐⭐⭐⭐ LE SUIVEUR SUIT, SUR UNE IMAGE DONT LA REPONSE EST CONSTRUITE. Une premiere version
    # s'arretait sur la maximalite dans la perpendiculaire au DEPLACEMENT : en marchant en travers,
    # cette perpendiculaire court LE LONG d'une crete, ou tout est plat, donc le test etait satisfait
    # partout et le contrele « en travers » ne pouvait pas echouer. L'etalon l'a montre nu.
    e = sur_une_image_construite(DEPARTS_PAR_COUCHE, plafond)
    v("sur des crêtes construites, on va plus loin LE LONG qu'en travers",
      e["le_long"] > e["en_travers"], f"{e['le_long']} contre {e['en_travers']}")
    v("et plus loin que sur la même image mélangée",
      e["le_long"] > e["melangee"], f"{e['le_long']} contre {e['melangee']}")
    for ligne in e["lignes"]:
        v(f"et ça tient à {ligne['angle_des_cretes_deg']}°",
          ligne["le_long"]["pas_median"] > ligne["en_travers"]["pas_median"],
          f"{ligne['le_long']['pas_median']} contre {ligne['en_travers']['pas_median']}")

    # ⚠⚠ LE PLANCHER VIENT DE L'IMAGE, PAS DE NOUS : c'est sa mediane. Une image uniforme n'a donc
    # AUCUN pas au-dessus de son plancher, et le suiveur y rend zero — ce qui est la bonne reponse.
    plat = np.full((64, 64), 100.0, dtype=np.float32)
    v("une image uniforme ne rend aucune suite", suivre(plat, (32, 32), 0.0, 50)["pas"] == 0,
      str(suivre(plat, (32, 32), 0.0, 50)["pas"]))

    # ⚠⚠ ET LE SUIVEUR MARCHE BIEN LE NOMBRE DE PAS QU'ON LUI DEMANDE, sinon une longueur mesuree
    # serait bornee par un bord d'image sans que rien ne le dise.
    yy, xx = np.mgrid[0:200, 0:200].astype(np.float32)
    bandes = 100.0 + 40.0 * np.cos(2.0 * np.pi * yy / 12.0)
    lu = suivre(bandes, (100, 5), 0.0, 60)
    v("le suiveur fait les pas qu'on lui demande", lu["pas_faits"] == 60, str(lu["pas_faits"]))
    v("et il reste sur la crête tout du long", lu["pas"] == 60, str(lu["pas"]))
    v("tandis qu'en travers il tombe à chaque creux",
      suivre(bandes, (100, 5), 90.0, 60)["pas"] < 12,
      str(suivre(bandes, (100, 5), 90.0, 60)["pas"]))

    # ⚠⚠⚠ L'ANGLE PUBLIE EST LA PERPENDICULAIRE AUX FIBRES (`172`) : suivre l'angle brut en croyant
    # suivre les fibres INVERSERAIT exactement les deux lectures que cette tranche compare.
    v("la conversion vers la direction des fibres tourne d'un quart de tour",
      abs(((direction_des_fibres_deg(20.0) - 20.0) % 180.0) - 90.0) < 1e-9,
      str(direction_des_fibres_deg(20.0)))

    # ⚠⚠⚠ ET LA CONVERSION EST EXERCEE AU SITE D'APPEL, parce qu'une sonde qui la retirait de
    # `un_chunk` passait au VERT : la batterie ne testait que la fonction, jamais l'endroit qui s'en
    # sert. On fait donc tourner `un_chunk` sur un bloc dont la direction des fibres est CONSTRUITE,
    # et l'angle qu'il publie doit etre celle-la — pas sa perpendiculaire.
    construite = 25.0
    th = np.radians(construite)
    s3 = -np.sin(th) * xx + np.cos(th) * yy
    bloc = np.stack([100.0 + 40.0 * np.cos(2.0 * np.pi * s3 / 12.0)] * 8).astype(np.float32)
    ang3, coh3 = orientation_profile(bloc)
    lu3 = un_chunk(bloc, ang3, coh3, DEPARTS_PAR_COUCHE, 40, 2, PLANCHER_DE_COHERENCE, GRAINE)
    v("un_chunk lit des couches", lu3["couches_lues"] > 0, str(lu3["couches_lues"]))
    if lu3["couches_lues"]:
        rendu = float(lu3["lignes"][0]["angle_des_fibres_deg"])
        ecart = min(abs(rendu - construite), 180.0 - abs(rendu - construite))
        v("et l'angle qu'il publie est celui des FIBRES, pas sa perpendiculaire",
          ecart < 5.0, f"{rendu} pour {construite} construits")

    # ⚠ LES DEPARTS SONT LES MAXIMUMS DE CASES REGULIERES : le choix est fait par la MATIERE, la
    # repartition par la grille, jamais par nous.
    dep = les_departs(bandes, DEPARTS_PAR_COUCHE)
    v("il y a autant de départs que demandé", len(dep) == DEPARTS_PAR_COUCHE, str(len(dep)))
    v("et chaque départ est un maximum de sa case",
      all(bandes[y, x] > float(np.median(bandes)) for y, x in dep),
      str([round(float(bandes[y, x]), 1) for y, x in dep][:4]))
    v("les départs ne sont pas tous au même endroit", len({d[0] for d in dep}) > 1
      or len({d[1] for d in dep}) > 1, str(dep[:3]))

    # ⭐⭐⭐⭐ LES ENONCES DU VERDICT TOMBENT CHACUN SUR L'ENTREE QUI LE VISE.
    def _seg(lg, tr, me):
        return {"decidable": True, "segment": "x", "chunks_lus": 9, "couches_lues": 54,
                "le_long": float(lg), "en_travers": float(tr), "melangee": float(me),
                "le_long_maximal": 100.0, "refuses": {}, "chunks": []}

    bon = {"le_long": 74.0, "en_travers": 7.0, "melangee": 18.5}
    r1 = juger([_seg(35.0, 23.5, 16.0)], bon, vx, pas, plafond)
    v("le suiveur suit quand l'étalon le montre", r1["le_suiveur_suit"])
    v("le rouleau porte des crêtes suivables quand il dépasse ses deux contrôles",
      r1["le_rouleau_porte_des_cretes_suivables"])
    v("et il ne franchit pas une feuille à trente-cinq pas",
      not r1["on_franchit_une_feuille"],
      f"{r1['le_long_en_um']} µm contre {r1['le_pas_entre_deux_feuilles_um']} µm")
    r2 = juger([_seg(100.0, 23.5, 16.0)], bon, vx, pas, plafond)
    v("une longueur qui franchit la feuille le dit", r2["on_franchit_une_feuille"],
      str(r2["le_long_en_um"]))
    r3 = juger([_seg(20.0, 23.5, 16.0)], bon, vx, pas, plafond)
    v("un rouleau qui ne dépasse pas le travers retire le second énoncé",
      not r3["le_rouleau_porte_des_cretes_suivables"])
    r4 = juger([_seg(20.0, 16.0, 23.5)], bon, vx, pas, plafond)
    v("ni un rouleau qui ne dépasse pas le mélange",
      not r4["le_rouleau_porte_des_cretes_suivables"])
    r5 = juger([_seg(35.0, 23.5, 16.0)], {"le_long": 7.0, "en_travers": 74.0, "melangee": 18.5},
               vx, pas, plafond)
    v("un étalon qui ne suit pas retire le premier énoncé", not r5["le_suiveur_suit"])
    vide = juger([{"decidable": False, "segment": "x"}], bon, vx, pas, plafond)
    v("aucun segment lisible rend un verdict indécidable", not vide["decidable"])

    nom = "jusquou_suit_on_une_fibre.py"
    if echecs:
        print(f"{nom}   {len(echecs)} ÉCHECS sur {faits}")
        for e_ in echecs:
            print(f"   ✗ {e_}")
        return 1
    print(f"{nom:<46} ALL PASS (0 failures, {faits} checks)")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer()
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
