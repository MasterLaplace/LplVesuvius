"""Une suite de creux se recale-t-elle ? — le transfert de spire à spire, mesuré.

⭐⭐⭐⭐ POURQUOI CE FICHIER, ET C'EST LA QUESTION DU GRAAL. `183` a mesuré qu'un creux pris SEUL se
retrouve chez le chunk voisin plus souvent que par hasard — **0,2222** contre **0,1384** — mais bien
trop rarement pour servir de repère : soixante-quatre paires adjacentes sur quatre-vingt-dix-neuf ne
partagent aucun creux. `R4-P33` nomme ce qui reste : prendre les creux ENSEMBLE plutôt qu'un par un.

⭐⭐⭐⭐ ET IL Y A UNE RAISON PHYSIQUE DE PENSER QUE C'EST ÇA QUI MANQUAIT. Deux chunks voisins ne
sont pas à la même profondeur dans la feuille : la nappe monte et descend, donc tout l'empilement de
l'un peut être DÉCALÉ par rapport à celui de l'autre. Un appariement position par position meurt sur
un décalage global ; un appariement qui cherche le DÉCALAGE ne meurt pas. Et chercher ce décalage
EST l'opération du transfert de spire à spire — c'est exactement ce que l'humain fait à la main.

⚠⚠⚠ LA LIBERTÉ DE CHOISIR UN DÉCALAGE SE PAIE, comme `179` a payé la largeur et `181` le rang. Le
contrôle apparié — le non-voisin — subit EXACTEMENT la même recherche de décalage, sur la même plage,
avec la même tolérance. Sans cela, « les voisins se recalent » ne dirait que « on a le droit de
bouger ».

⚠⚠ LA PLAGE DE DÉCALAGE EST DÉRIVÉE, PAS CHOISIE : au-delà d'un DEMI-PLI, un décalage ferait tomber
une frontière sur la suivante, donc il cesserait d'être un décalage pour devenir un aliasing. La
plage est donc `± pli / 2`, et le pli vient du pas et du voxel comme partout dans cette chaîne.

⚠ Tout le reste est appelé et non recopié : les amas et l'appariement de `183`, le lecteur séquentiel
de `181`, le chemin du rouleau de `176`.

Usage :
    uv run python src/nappe/une_suite_de_creux_se_recale_t_elle.py --verifier
    uv run python src/nappe/une_suite_de_creux_se_recale_t_elle.py \\
        --json docs/mesures/une_suite_de_creux_se_recale_t_elle.json
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

from de_quoi_une_frontiere_est_elle_faite import (CE_QUE_LA_FIXTURE_A_RENDU,  # noqa: E402
                                                  CE_QUE_LE_ROULEAU_A_RENDU, COUCHES, _relire)
from la_coherence_creuse_t_elle_a_la_frontiere import CONTRASTE_DE_LA_FIXTURE  # noqa: E402
from la_feuille_a_t_elle_trois_plis import (lechelle_des_plis,  # noqa: E402
                                            les_creux_a_chercher, lespacement_dun_pli)
from la_profondeur_tourne_t_elle_ou_bascule_t_elle import PERMUTATIONS  # noqa: E402
from la_recette_posee_sur_le_rouleau import (COTE_DU_TREILLIS, DELAI,  # noqa: E402
                                             SEGMENTS, la_courbe_dun_chunk, les_volumes)
from quelle_fenetre_lit_une_bascule import courbe_de_la_fixture  # noqa: E402
from un_creux_se_retrouve_t_il_a_cote import (_creux, la_correspondance,  # noqa: E402
                                              la_tolerance, les_amas)
from zarr_depth import BUCKET, array_meta  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
CE_QUE_LESPACEMENT_A_RENDU = MESURES / "de_quoi_une_frontiere_est_elle_faite.json"
CE_QUE_LE_VOISIN_A_RENDU = MESURES / "un_creux_se_retrouve_t_il_a_cote.json"
GRAINE = 20260924
TIRAGES_NON_VOISINS = 19


def la_plage_de_decalage(voxel_um: float, pas_um: float) -> int:
    """De combien de couches on s'autorise à recaler — DÉRIVÉ, pas choisi.

    ⚠⚠ AU-DELÀ D'UN DEMI-PLI, UN DÉCALAGE FAIT TOMBER UNE FRONTIÈRE SUR LA SUIVANTE : il cesse
    d'être un décalage pour devenir un aliasing, et la mesure rendrait alors une correspondance qui
    ne dit plus que « les frontières sont espacées régulièrement ». La plage vaut donc la moitié
    d'un pli, et le pli vient du pas et du voxel comme partout dans cette chaîne.
    """
    return int(round(lespacement_dun_pli(2, voxel_um, pas_um) / 2.0))


def le_recalage(a, b, tolerance: int, plage: int) -> dict:
    """Le décalage qui apparie le PLUS de creux entre deux suites, et ce qu'il apparie.

    ⭐⭐⭐⭐ C'EST L'OPÉRATION DU TRANSFERT DE SPIRE À SPIRE, réduite à ce qu'elle a de mesurable :
    deux colonnes voisines, un décalage à trouver, et un compte de repères qui tombent en face.

    ⚠⚠⚠ LES ÉGALITÉS SE TRANCHENT PAR L'ÉCART RÉSIDUEL, ET UNE PREMIÈRE VERSION LES TRANCHAIT PAR
    LE PLUS PETIT DÉCALAGE. C'était un biais vers zéro : la tolérance vaut quatre couches, donc un
    décalage de trois est déjà absorbé par un décalage nul, qui l'emportait alors à correspondance
    égale. Le recalage n'aurait pas retrouvé un décalage construit plus petit que la tolérance, et
    l'étalon aurait échoué pour une raison qui n'est pas un défaut de la matière. On retient donc,
    à correspondance égale, le décalage dont les creux appariés tombent le plus exactement en face,
    puis le plus petit en valeur absolue.

    ⚠ La part est celle de `183`, appelée et non redéfinie — appariement exclusif, dénominateur sur
    le plus petit des deux.
    """
    if not list(a) or not list(b):
        return {"decalage": None, "part": None, "apparies": 0}
    meilleur = None
    for s in range(-int(plage), int(plage) + 1):
        lu = la_correspondance(a, [int(y) + s for y in b], int(tolerance))
        cle = (-(lu["part"] or 0.0), float(lu["ecart_median"] or 0.0), abs(s), s)
        if meilleur is None or cle < meilleur[0]:
            meilleur = (cle, {"decalage": int(s), **lu})
    return meilleur[1]


def contre_le_hasard(a, b, tolerance: int, plage: int, permutations: int = PERMUTATIONS,
                     graine: int = GRAINE, couches: int = COUCHES) -> dict:
    """Le recalage réel, et le MÊME recalage contre des creux tirés au hasard.

    ⭐⭐⭐⭐ LA LIBERTÉ DE CHOISIR UN DÉCALAGE SE PAIE ICI. On remplace les creux du voisin par autant
    de creux tirés uniformément dans la même profondeur, et on refait la MÊME recherche sur la MÊME
    plage. Ce que l'excédent mesure est donc ce que le recalage gagne sur ce que « avoir le droit de
    bouger » rapporte tout seul.

    ⚠ Le nombre de creux tirés est celui du voisin, donc la densité est conservée : c'est la
    POSITION qui est détruite, et rien d'autre.
    """
    reel = le_recalage(a, b, tolerance, plage)
    if reel["part"] is None:
        return {"decidable": False, "raison": "une suite est vide"}
    r = np.random.default_rng(int(graine))
    parts = []
    for _ in range(int(permutations)):
        tire = sorted(int(x) for x in r.integers(0, int(couches), len(list(b))))
        parts.append(float(le_recalage(a, tire, tolerance, plage)["part"] or 0.0))
    mediane = float(statistics.median(parts)) if parts else 0.0
    return {"decidable": True, **reel, "tirages": len(parts),
            "part_mediane_des_tirages": round(mediane, 4),
            "part_maximale_des_tirages": round(float(max(parts)), 4) if parts else None,
            "excedent": round(float(reel["part"]) - mediane, 4),
            "depasse_tous_les_tirages": bool(all(float(reel["part"]) > x for x in parts))}


def _med(v):
    return round(float(statistics.median(v)), 4) if v else None


def un_amas(url: str, meta: dict, amas, combien: int, tolerance_par_defaut: int, plage: int,
            permutations: int, graine: int, delai: float = DELAI) -> dict:
    lus = {}
    for cy, cx in amas:
        courbe, _ = la_courbe_dun_chunk(url, meta, cy, cx, delai)
        if courbe is None:
            continue
        creux, largeur = _creux(courbe, combien, permutations, graine)
        if creux:
            lus[(cy, cx)] = {"creux": creux, "largeur": largeur or tolerance_par_defaut}
    paires = []
    for (ay, ax), a in lus.items():
        for (by, bx), b in lus.items():
            if (ay, ax) >= (by, bx) or abs(ay - by) + abs(ax - bx) != 1:
                continue
            tol = la_tolerance(a["largeur"])
            paires.append({"a": [ay, ax], "b": [by, bx],
                           **contre_le_hasard(a["creux"], b["creux"], tol, plage,
                                              permutations, graine)})
    return {"chunks_lus": len(lus), "paires": paires,
            "creux": {f"{cy},{cx}": x["creux"] for (cy, cx), x in lus.items()},
            "largeurs": {f"{cy},{cx}": x["largeur"] for (cy, cx), x in lus.items()}}


def contre_les_non_voisins(amas: list[dict], tolerance_par_defaut: int, plage: int,
                           tirages: int = TIRAGES_NON_VOISINS, graine: int = GRAINE) -> dict:
    """Le MÊME recalage entre chunks qui ne sont PAS voisins — le contrôle apparié de `183`.

    ⚠⚠⚠ ET IL SUBIT LA MÊME RECHERCHE DE DÉCALAGE, SUR LA MÊME PLAGE. Sans cela, comparer un
    voisin recalé à un non-voisin NON recalé mesurerait la liberté de bouger et rien d'autre.
    """
    tous = [(x, a["largeurs"].get(cle) or tolerance_par_defaut, k)
            for k, a in enumerate(amas) for cle, x in a["creux"].items()]
    if len(tous) < 2:
        return {"decidable": False, "raison": "pas assez de chunks"}
    r = np.random.default_rng(int(graine))
    parts, decalages = [], []
    for k, a in enumerate(amas):
        for cle, creux in a["creux"].items():
            tol = la_tolerance(a["largeurs"].get(cle) or tolerance_par_defaut)
            loin = [x for x, _l, j in tous if j != k]
            if not loin:
                continue
            for _ in range(int(tirages)):
                autre = loin[int(r.integers(0, len(loin)))]
                lu = le_recalage(creux, autre, tol, plage)
                if lu["part"] is not None:
                    parts.append(float(lu["part"]))
                    decalages.append(int(lu["decalage"]))
    return {"decidable": bool(parts), "tirages": len(parts),
            "part_moyenne": (round(float(sum(parts) / len(parts)), 4) if parts else None),
            "part_mediane": _med(parts),
            "part_maximale": (round(float(max(parts)), 4) if parts else None)}


def un_segment(volume: dict, combien: int, plage: int, permutations: int = PERMUTATIONS,
               delai: float = DELAI, graine: int = GRAINE) -> dict:
    url = f"{BUCKET}/{volume['cle']}"
    try:
        meta = array_meta(url, 0, delai)
    except Exception as e:  # noqa: BLE001
        return {"decidable": False, "segment": volume["segment"],
                "raison": f"le volume ne répond pas : {type(e).__name__}"}
    profond, hy, hx = meta["chunks"]
    _, rows, cols = meta["shape"]
    groupes = [un_amas(url, meta, a, combien, 7, plage, permutations, graine, delai)
               for a in les_amas(-(-rows // hy), -(-cols // hx), COTE_DU_TREILLIS)]
    groupes = [g for g in groupes if g["chunks_lus"]]
    paires = [p for g in groupes for p in g["paires"] if p.get("decidable")]
    parts = [float(p["part"]) for p in paires]
    loin = contre_les_non_voisins(groupes, 7, plage, TIRAGES_NON_VOISINS, graine)
    return {"decidable": bool(paires), "segment": volume["segment"],
            "amas_lus": len(groupes),
            "chunks_lus": int(sum(g["chunks_lus"] for g in groupes)),
            "paires_adjacentes": len(paires),
            "part_moyenne_des_voisins": (round(float(sum(parts) / len(parts)), 4)
                                         if parts else None),
            "part_mediane_des_voisins": _med(parts),
            "paires_qui_depassent_le_hasard": int(
                sum(1 for p in paires if p.get("depasse_tous_les_tirages"))),
            "decalage_median": _med([abs(int(p["decalage"])) for p in paires]),
            "decalages": sorted(int(p["decalage"]) for p in paires),
            "les_non_voisins": loin, "amas": groupes}


def sur_la_fixture(combien: int, plage: int, recouvrement_um: float, bruit: float,
                   permutations: int = PERMUTATIONS, graine: int = GRAINE) -> dict:
    """La MÊME matière, DÉCALÉE d'un nombre de couches CHOISI — la réponse est connue avant.

    ⭐⭐⭐⭐ C'EST L'ÉTALON QUI DIT SI LE RECALAGE RECALE. On lit une fenêtre, puis la même matière
    décalée en profondeur d'un nombre de couches connu : le décalage rendu doit être celui-là, et la
    correspondance doit être entière. Un recalage qui ne retrouverait pas un décalage construit ne
    dirait rien du rouleau.

    ⚠ Le décalage est posé en micromètres — un nombre entier de couches fois le voxel — pour que la
    réponse attendue soit exactement un entier de couches.
    """
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    vx, pas = float(C.VOXEL_FIN_UM), float(C.PAS_UM)
    lignes = []
    for pose in (0, 3, 7, -5):
        justes, parts = 0, []
        for k in range(4):
            dec = pas * k / 4.0
            a = courbe_de_la_fixture(COUCHES, dec, CONTRASTE_DE_LA_FIXTURE, 2, vx, pas,
                                     transition_um=recouvrement_um, bruit=bruit)
            b = courbe_de_la_fixture(COUCHES, dec + pose * vx, CONTRASTE_DE_LA_FIXTURE, 2, vx,
                                     pas, transition_um=recouvrement_um, bruit=bruit)
            ca, la = _creux(a, combien, permutations, graine)
            cb, _lb = _creux(b, combien, permutations, graine)
            if not ca or not cb:
                continue
            lu = le_recalage(ca, cb, la_tolerance(la or 7), plage)
            parts.append(float(lu["part"] or 0.0))
            # ⚠⚠ LE SIGNE A ETE MESURE, PAS RAISONNE, ET MA PREMIERE REDACTION LE PRENAIT A
            # L'ENVERS : decaler la fenetre de `pose` couches vers le fond place les creux `pose`
            # couches PLUS HAUT dans la fenetre, donc il faut AJOUTER `pose` pour les remettre en
            # face. Le recalage attendu est donc `pose` lui-meme. L'etalon rendait 4/16 tant que
            # l'attendu portait le mauvais signe, et c'est la sonde qui l'a dit.
            justes += int(lu["decalage"] == int(pose))
        lignes.append({"decalage_pose": int(pose), "cellules": 4, "retrouve": int(justes),
                       "part_mediane": _med(parts)})
    return {"lignes": lignes,
            "decalages_retrouves": int(sum(x["retrouve"] for x in lignes)),
            "cellules": int(sum(x["cellules"] for x in lignes)),
            "part_mediane": _med([x["part_mediane"] for x in lignes
                                  if x["part_mediane"] is not None])}


def juger(segments: list[dict], fixture: dict, de_183: dict) -> dict:
    """Une suite de creux se recale-t-elle chez le voisin, plus que le hasard ne le permet ?"""
    lus = [s for s in segments if s.get("decidable")]
    if not lus:
        return {"decidable": False, "raison": "aucun segment lisible"}
    voisins = _med([s["part_moyenne_des_voisins"] for s in lus
                    if s["part_moyenne_des_voisins"] is not None])
    loin = _med([s["les_non_voisins"]["part_moyenne"] for s in lus
                 if s["les_non_voisins"].get("part_moyenne") is not None])
    paires = int(sum(s["paires_adjacentes"] for s in lus))
    depassent = int(sum(s["paires_qui_depassent_le_hasard"] for s in lus))
    sans = de_183.get("part_des_voisins")
    return {"decidable": True, "segments": len(lus),
            "amas_lus": int(sum(s["amas_lus"] for s in lus)),
            "chunks_lus": int(sum(s["chunks_lus"] for s in lus)),
            "paires_adjacentes": paires,
            "paires_qui_depassent_le_hasard": depassent,
            "part_des_voisins_recales": voisins,
            "part_des_non_voisins_recales": loin,
            "part_des_voisins_sans_recalage_de_183": sans,
            "decalage_median": _med([s["decalage_median"] for s in lus
                                     if s["decalage_median"] is not None]),
            "decalages_retrouves_sur_la_fixture": fixture["decalages_retrouves"],
            "cellules_de_la_fixture": fixture["cellules"],
            "part_de_la_fixture": fixture["part_mediane"],
            # ⚠⚠ TROIS ENONCES. Le premier dit que le recalage RECALE — sans lui rien ne suit. Le
            # second dit s'il gagne sur le hasard, controle apparie compris. Le troisieme dit ce
            # qu'il AJOUTE a la lecture position par position de `183`, qui est la seule chose qui
            # justifie de l'avoir construit.
            "le_recalage_retrouve_un_decalage_construit": bool(
                fixture["decalages_retrouves"] == fixture["cellules"]),
            "les_voisins_se_recalent_mieux_que_les_non_voisins": bool(
                voisins is not None and loin is not None and voisins > loin),
            "le_recalage_ajoute_a_183": bool(
                voisins is not None and sans is not None and voisins > sans),
            "ce_quil_ajoute_fois": (round(voisins / sans, 4)
                                    if (voisins and sans) else None),
            # ⚠⚠⚠ ET VOICI CE QUI DECIDE, ET IL FAUT QU'IL SOIT NOMME. Le recalage triple la
            # correspondance, mais il la triple AUSSI chez le non-voisin, et le controle apparie
            # par tirage l'absorbe entierement : si aucune paire ne depasse son propre hasard, le
            # gain est celui de la LIBERTE DE DECALER et non une propriete de la matiere. Publier
            # « ×3 » sans ce booleen ferait lire un artefact comme un resultat.
            "le_gain_vient_de_la_liberte_de_decaler": bool(paires and depassent == 0),
            "part_des_paires_qui_depassent": (round(depassent / float(paires), 4)
                                              if paires else None)}


def mesurer(segments_n: int = SEGMENTS, permutations: int = PERMUTATIONS) -> dict:
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    vx, pas = float(C.VOXEL_FIN_UM), float(C.PAS_UM)
    de_179 = _relire(CE_QUE_LA_FIXTURE_A_RENDU, ("le_recouvrement_juste_suffisant_um",))
    de_180 = _relire(CE_QUE_LE_ROULEAU_A_RENDU, ("le_bruit_apparie",))
    de_181 = _relire(CE_QUE_LESPACEMENT_A_RENDU, ("espacement_median_du_rouleau",))
    de_183 = _relire(CE_QUE_LE_VOISIN_A_RENDU, ("part_des_voisins", "part_des_non_voisins"))
    if not (de_179 and de_180 and de_181 and de_183):
        return {"message": "les mesures de `179` à `183` donnent les réglages et l'échelle"}
    combien = les_creux_a_chercher(
        lechelle_des_plis(vx, pas, float(de_181["espacement_median_du_rouleau"])),
        COUCHES, vx, pas)
    plage = la_plage_de_decalage(vx, pas)
    volumes = les_volumes(combien=segments_n)
    if not volumes:
        return {"message": "aucun volume de surface à la résolution de la campagne n'est recensé"}
    segs = [un_segment(v, combien, plage, permutations) for v in volumes]
    fixture = sur_la_fixture(combien, plage,
                             float(de_179["le_recouvrement_juste_suffisant_um"]),
                             float(de_180["le_bruit_apparie"]), permutations)
    return {"creux_cherches_par_chunk": int(combien), "plage_de_decalage": int(plage),
            "cote_du_treillis": int(COTE_DU_TREILLIS), "couches": int(COUCHES),
            "tirages_de_non_voisins": int(TIRAGES_NON_VOISINS),
            "permutations": int(permutations), "graine": int(GRAINE),
            "recouvrement_um_de_179": float(de_179["le_recouvrement_juste_suffisant_um"]),
            "bruit_apparie_de_180": float(de_180["le_bruit_apparie"]),
            "de_183": de_183, "les_segments": segs, "la_fixture": fixture,
            "le_verdict": juger(segs, fixture, de_183)}


def afficher(r: dict) -> None:
    if "message" in r:
        print(r["message"])
        return
    v, fx = r["le_verdict"], r["la_fixture"]
    print("UNE SUITE DE CREUX SE RECALE-T-ELLE ?")
    print(f"  {r['creux_cherches_par_chunk']} creux · plage ±{r['plage_de_decalage']} couches · "
          f"amas de 2×2 sur le treillis {r['cote_du_treillis']}×{r['cote_du_treillis']} · "
          f"{r['permutations']} tirages par paire")
    print()
    for s in r["les_segments"]:
        if not s.get("decidable"):
            print(f"  {s['segment']} — {s.get('raison')}")
            continue
        loin = s["les_non_voisins"]
        print(f"  {s['segment']} · {s['amas_lus']} amas · {s['paires_adjacentes']} paires")
        print(f"     voisins recalés {s['part_moyenne_des_voisins']} · non-voisins recalés "
              f"{loin.get('part_moyenne')} · dépassent le hasard "
              f"{s['paires_qui_depassent_le_hasard']}/{s['paires_adjacentes']} · décalage "
              f"{s['decalage_median']}")
    print()
    print("  L'ÉTALON · la MÊME matière décalée d'un nombre de couches CHOISI")
    for x in fx["lignes"]:
        print(f"   décalage posé {x['decalage_pose']:>3} · retrouvé {x['retrouve']}/"
              f"{x['cellules']} · part {x['part_mediane']}")
    print()
    print("  ★ LE VERDICT")
    for cle in ("amas_lus", "chunks_lus", "paires_adjacentes", "paires_qui_depassent_le_hasard",
                "part_des_voisins_recales", "part_des_non_voisins_recales",
                "part_des_voisins_sans_recalage_de_183", "ce_quil_ajoute_fois",
                "decalage_median", "decalages_retrouves_sur_la_fixture",
                "cellules_de_la_fixture", "part_de_la_fixture",
                "part_des_paires_qui_depassent",
                "le_recalage_retrouve_un_decalage_construit",
                "les_voisins_se_recalent_mieux_que_les_non_voisins",
                "le_recalage_ajoute_a_183", "le_gain_vient_de_la_liberte_de_decaler"):
        print(f"     {cle:<50} {v.get(cle)}")


def verifier() -> int:
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        if not ok:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    vx, pas = float(C.VOXEL_FIN_UM), float(C.PAS_UM)

    # ⚠⚠ LA PLAGE EST DERIVEE : au-dela d'un DEMI-PLI, un decalage fait tomber une frontiere sur la
    # suivante et cesse d'etre un decalage.
    plage = la_plage_de_decalage(vx, pas)
    v("la plage vaut la moitié d'un pli",
      plage == int(round(lespacement_dun_pli(2, vx, pas) / 2.0)), str(plage))
    v("et elle est plus petite qu'un pli", plage < lespacement_dun_pli(2, vx, pas))

    # ⭐⭐⭐⭐ LE RECALAGE RETROUVE UN DECALAGE CONSTRUIT, sur des suites dont la reponse est connue
    # AVANT la mesure.
    for s in (-7, -3, 0, 3, 7):
        a = [10, 40, 70]
        b = [x - s for x in a]
        lu = le_recalage(a, b, 4, plage)
        v(f"le recalage retrouve un décalage de {s}", lu["decalage"] == s and lu["part"] == 1.0,
          f"{lu['decalage']} · part {lu['part']}")

    # ⚠⚠⚠ ET IL LE RETROUVE MEME SOUS LA TOLERANCE, parce que les egalites se tranchent par l'ECART
    # RESIDUEL. Une premiere version les tranchait par le plus petit decalage : un decalage de trois
    # etait alors absorbe par un decalage NUL, puisque la tolerance vaut quatre.
    lu = le_recalage([10, 40, 70], [7, 37, 67], 4, plage)
    v("un décalage plus petit que la tolérance est retrouvé quand même",
      lu["decalage"] == 3, f"{lu['decalage']} · écart {lu['ecart_median']}")
    v("et l'écart résiduel y est nul", lu["ecart_median"] == 0.0, str(lu["ecart_median"]))

    # ⚠ UN DECALAGE HORS DE LA PLAGE N'EST PAS RETROUVE, et c'est voulu : au-dela d'un demi-pli ce
    # n'est plus un decalage.
    hors = le_recalage([10, 40, 70], [x - (plage + 5) for x in [10, 40, 70]], 4, plage)
    v("un décalage hors de la plage n'est pas retrouvé", hors["part"] < 1.0,
      f"{hors['decalage']} · part {hors['part']}")

    # ⭐⭐⭐⭐ LE CONTROLE APPARIE : des creux TIRES AU HASARD, avec la MEME recherche sur la MEME
    # plage. C'est lui qui dit ce que « avoir le droit de bouger » rapporte tout seul.
    r = np.random.default_rng(GRAINE)
    a = sorted(int(x) for x in r.integers(0, COUCHES, 5))
    bb = sorted(int(x) for x in r.integers(0, COUCHES, 5))
    lu = contre_le_hasard(a, bb, 4, plage, PERMUTATIONS, GRAINE)
    v("le contrôle par tirage se prononce", lu["decidable"])
    # ⚠⚠⚠ CE QUI EST ASSERTE EST QUE LE CONTROLE RECALE LUI AUSSI, et une sonde qui le lui retirait
    # passait au VERT : « la part mediane des tirages est non nulle » est vrai des DEUX cotes, donc
    # cette condition n'ecarte rien. Ce qui ne peut pas etre satisfait par accident est que recaler
    # le tirage rende PLUS que ne pas le recaler — c'est exactement ce que « bouger rapporte tout
    # seul » veut dire, et c'est la moitie du resultat de cette tranche.
    r2 = np.random.default_rng(GRAINE)
    sans, avec = [], []
    for _ in range(19):
        tire = sorted(int(x) for x in r2.integers(0, COUCHES, len(bb)))
        sans.append(float(la_correspondance(a, tire, 4)["part"] or 0.0))
        avec.append(float(le_recalage(a, tire, 4, plage)["part"] or 0.0))
    # ⚠⚠ MA PREMIERE VERSION COMPARAIT LES MEDIANES ET ELLES SORTENT EGALES : avec cinq creux les
    # parts sont des multiples d'un cinquieme, donc la mediane est quantifiee — le meme piege que
    # `182` a paye. Ce qui est EXACTEMENT vrai est que recaler ne peut jamais rendre MOINS, puisque
    # le decalage nul est dans la plage, et qu'il rend STRICTEMENT plus au moins une fois.
    v("recaler un tirage ne rend jamais moins",
      all(x >= y - 1e-12 for x, y in zip(avec, sans)),
      f"{[round(x - y, 3) for x, y in zip(avec, sans)][:5]}")
    v("et il rend strictement plus au moins une fois",
      any(x > y + 1e-12 for x, y in zip(avec, sans)),
      f"{round(sum(avec) / len(avec), 4)} contre {round(sum(sans) / len(sans), 4)} en moyenne")
    v("et le contrôle de la mesure passe bien par le recalage",
      abs(lu["part_mediane_des_tirages"] - statistics.median(avec)) < 1e-9,
      f"{lu['part_mediane_des_tirages']} contre {round(statistics.median(avec), 4)}")

    # ⚠⚠⚠ UN CREUX UNIQUE SE RECALE TOUJOURS, donc il ne peut JAMAIS battre son propre tirage : un
    # seul point se met en face de n'importe quel autre point de la plage. C'est le cas d'EGALITE
    # exacte, et une sonde qui remplacait le « plus grand que » par un « plus grand ou egal »
    # passait au vert faute de l'avoir asserte.
    seul = contre_le_hasard([50], [50], 4, plage, PERMUTATIONS, GRAINE)
    v("un creux unique ne dépasse jamais son propre tirage",
      seul["decidable"] and seul["part"] == 1.0
      and not seul["depasse_tous_les_tirages"],
      f"part {seul.get('part')} · tirages {seul.get('part_mediane_des_tirages')} · "
      f"dépasse {seul.get('depasse_tous_les_tirages')}")
    # ⚠⚠⚠ ET C'EST CE CHIFFRE-LA QUI DIT QUE LE CONTROLE DE LA MESURE RECALE VRAIMENT : un creux
    # unique tire au hasard s'apparie TOUJOURS quand on a le droit de decaler, donc la mediane des
    # tirages vaut exactement un. Sans recalage elle vaut zero, puisqu'un point tire tombe rarement
    # a quatre couches d'un autre. Une sonde qui retirait le recalage du controle passait au vert
    # tant que rien n'assertait cette valeur exacte.
    v("un tirage d'un seul creux s'apparie toujours quand on peut décaler",
      seul.get("part_mediane_des_tirages") == 1.0,
      str(seul.get("part_mediane_des_tirages")))
    v("deux suites identiques dépassent tous leurs tirages",
      contre_le_hasard([10, 40, 70], [10, 40, 70], 4, plage, PERMUTATIONS,
                       GRAINE)["depasse_tous_les_tirages"])
    v("une suite vide ne se prononce pas",
      not contre_le_hasard([10, 40], [], 4, plage, PERMUTATIONS, GRAINE)["decidable"])

    # ⭐⭐⭐⭐ LE CHEMIN PHYSIQUE : la MEME matiere decalee d'un nombre de couches CHOISI. Le signe a
    # ete MESURE et non raisonne — une premiere redaction le prenait a l'envers et l'etalon rendait
    # quatre sur seize.
    de_179 = _relire(CE_QUE_LA_FIXTURE_A_RENDU, ("le_recouvrement_juste_suffisant_um",))
    de_180 = _relire(CE_QUE_LE_ROULEAU_A_RENDU, ("le_bruit_apparie",))
    de_181 = _relire(CE_QUE_LESPACEMENT_A_RENDU, ("espacement_median_du_rouleau",))
    de_183 = _relire(CE_QUE_LE_VOISIN_A_RENDU, ("part_des_voisins",))
    v("les mesures de `179` à `183` donnent les réglages",
      bool(de_179 and de_180 and de_181 and de_183))
    if de_179 and de_180 and de_181:
        combien = les_creux_a_chercher(
            lechelle_des_plis(vx, pas, float(de_181["espacement_median_du_rouleau"])),
            COUCHES, vx, pas)
        fx = sur_la_fixture(combien, plage,
                            float(de_179["le_recouvrement_juste_suffisant_um"]),
                            float(de_180["le_bruit_apparie"]), PERMUTATIONS)
        v("l'étalon retrouve TOUS les décalages construits",
          fx["decalages_retrouves"] == fx["cellules"],
          f"{fx['decalages_retrouves']}/{fx['cellules']} · {fx['lignes']}")
        v("et la correspondance y est entière", fx["part_mediane"] == 1.0,
          str(fx["part_mediane"]))
        v("l'étalon pose des décalages des DEUX signes et un décalage nul",
          {min(x["decalage_pose"] for x in fx["lignes"]) < 0,
           max(x["decalage_pose"] for x in fx["lignes"]) > 0,
           any(x["decalage_pose"] == 0 for x in fx["lignes"])} == {True},
          str([x["decalage_pose"] for x in fx["lignes"]]))

    # ⭐⭐⭐⭐ LES ENONCES DU VERDICT TOMBENT CHACUN SUR L'ENTREE QUI LE VISE.
    def _seg(moy, loin, depassent, paires=10):
        return {"decidable": True, "segment": "x", "amas_lus": 3, "chunks_lus": 12,
                "paires_adjacentes": int(paires),
                "paires_qui_depassent_le_hasard": int(depassent),
                "part_moyenne_des_voisins": float(moy), "part_mediane_des_voisins": float(moy),
                "decalage_median": 4.0, "decalages": [4],
                "les_non_voisins": {"decidable": True, "tirages": 100,
                                    "part_moyenne": float(loin), "part_mediane": float(loin),
                                    "part_maximale": 1.0}}

    fxb = {"decalages_retrouves": 16, "cellules": 16, "part_mediane": 1.0,
           "lignes": [{"decalage_pose": 0, "cellules": 4, "retrouve": 4, "part_mediane": 1.0}]}
    d183 = {"part_des_voisins": 0.2222}
    rien = juger([_seg(0.67, 0.63, 0)], fxb, d183)
    v("aucune paire qui dépasse nomme le gain comme celui de la liberté",
      rien["le_gain_vient_de_la_liberte_de_decaler"])
    v("et les voisins y dépassent quand même les non-voisins",
      rien["les_voisins_se_recalent_mieux_que_les_non_voisins"])
    vrai = juger([_seg(0.67, 0.63, 7)], fxb, d183)
    v("des paires qui dépassent retirent cet énoncé",
      not vrai["le_gain_vient_de_la_liberte_de_decaler"])
    inv = juger([_seg(0.60, 0.63, 0)], fxb, d183)
    v("des voisins qui ne dépassent pas retirent le second énoncé",
      not inv["les_voisins_se_recalent_mieux_que_les_non_voisins"])
    casse = juger([_seg(0.67, 0.63, 0)], {**fxb, "decalages_retrouves": 4}, d183)
    v("un étalon qui ne retrouve pas ses décalages retire le premier",
      not casse["le_recalage_retrouve_un_decalage_construit"])
    vide = juger([{"decidable": False, "segment": "x"}], fxb, d183)
    v("aucun segment lisible rend un verdict indécidable", not vide["decidable"])

    nom = "une_suite_de_creux_se_recale_t_elle.py"
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
