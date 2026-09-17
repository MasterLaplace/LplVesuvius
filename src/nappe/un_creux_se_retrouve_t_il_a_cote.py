"""Un creux se retrouve-t-il à côté ? — un repère n'a pas besoin d'être périodique.

⭐⭐⭐⭐ POURQUOI CE FICHIER. `182` a établi une NÉGATION double : à cette échelle la profondeur du
rouleau n'est périodique à aucun pas, et ce n'est pas non plus un empilement régulier plus quelques
fissures. Les creux existent, ils sont profonds, ils séparent de la matière dirigée des deux côtés —
mais leur espacement est irrégulier.

⭐⭐⭐⭐ ET C'EST À CE MOMENT QUE LA QUESTION DU GRAAL REPREND LA MAIN. Ce qui remplace l'humain au
transfert de spire à spire est un REPÈRE, et un repère n'a pas besoin d'être périodique : il a besoin
d'être RETROUVABLE. Un creux à la couche quarante d'un chunk vaut comme repère si le chunk d'à côté
en porte un à la couche quarante aussi. C'est une question sur la correspondance LATÉRALE, et rien
dans toute la chaîne `172`–`182` ne l'a posée — tout y a été lu chunk par chunk, en profondeur.

⚠⚠⚠ ET ELLE EXIGE DE VRAIS VOISINS. Le treillis régulier de `176` sépare ses chunks de dizaines de
positions : deux chunks de ce treillis ne sont voisins de rien. On prend donc des AMAS de deux par
deux chunks ADJACENTS, exactement comme `fiber_orientation.survey` a dû le faire pour la même raison
— « un désaccord entre voisins exige des voisins ».

⚠⚠⚠ LE CONTRÔLE APPARIÉ EST LA CORRESPONDANCE AVEC UN CHUNK QUI N'EST PAS VOISIN. Deux chunks
quelconques ont chacun quelques creux répartis sur cent-neuf couches, donc ils en ont forcément
quelques-uns à la même profondeur par hasard : sans ce contrôle, « les voisins se correspondent » se
lirait comme un résultat alors que c'est de l'arithmétique. Le non-voisin est tiré parmi les chunks
des AUTRES amas, donc il a la même loi de profondeurs et la même densité de creux.

⚠⚠ LA TOLÉRANCE EST DÉRIVÉE DU CREUX LUI-MÊME : deux creux distants de moins d'une demi-largeur plus
une couche sont le même accident de profondeur. C'est la règle que `180` emploie déjà pour dire qu'un
creux tombe sur une frontière construite.

Usage :
    uv run python src/nappe/un_creux_se_retrouve_t_il_a_cote.py --verifier
    uv run python src/nappe/un_creux_se_retrouve_t_il_a_cote.py \\
        --json docs/mesures/un_creux_se_retrouve_t_il_a_cote.json
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
                                                  CE_QUE_LE_ROULEAU_A_RENDU, COUCHES,
                                                  _relire, plusieurs_creux)
from la_coherence_creuse_t_elle_a_la_frontiere import CONTRASTE_DE_LA_FIXTURE  # noqa: E402
from la_feuille_a_t_elle_trois_plis import (lechelle_des_plis,  # noqa: E402
                                            les_creux_a_chercher)
from la_profondeur_tourne_t_elle_ou_bascule_t_elle import PERMUTATIONS  # noqa: E402
from la_recette_posee_sur_le_rouleau import (COTE_DU_TREILLIS, DELAI,  # noqa: E402
                                             SEGMENTS, la_courbe_dun_chunk, les_chunks,
                                             les_volumes)
from quelle_fenetre_lit_une_bascule import courbe_de_la_fixture  # noqa: E402
from zarr_depth import BUCKET, array_meta  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
CE_QUE_LESPACEMENT_A_RENDU = MESURES / "de_quoi_une_frontiere_est_elle_faite.json"
GRAINE = 20260923
TIRAGES_NON_VOISINS = 19


def les_amas(gy: int, gx: int, cote: int = COTE_DU_TREILLIS) -> list[list[tuple[int, int]]]:
    """Des AMAS de deux par deux chunks ADJACENTS, un par position du treillis de `176`.

    ⚠⚠⚠ DES VOISINS, PAS UN TREILLIS LÂCHE. Le treillis de `176` sépare ses chunks de dizaines de
    positions : deux d'entre eux ne sont voisins de rien, et une question sur la correspondance
    LATÉRALE n'a alors aucune paire à mesurer. C'est exactement le défaut que
    `fiber_orientation.survey` a dû réparer, et pour la même raison.

    ⚠⚠ MAIS LES POSITIONS RESTENT CELLES DE `176`, appelées et non redessinées : c'est là que toute
    la chaîne a lu, c'est là que la mesure sait quels chunks répondent, et poser un treillis neuf
    ferait mesurer un autre endroit du rouleau en croyant mesurer une autre question. Chaque
    position devient le coin d'un amas de deux par deux.

    ⚠ Les amas sont donc posés, jamais tirés : un amas choisi ferait mesurer le choix.
    """
    if gy < 2 or gx < 2:
        return []
    amas = []
    for cy, cx in les_chunks(gy, gx, cote):
        y, x = min(int(cy), gy - 2), min(int(cx), gx - 2)
        amas.append([(y, x), (y, x + 1), (y + 1, x), (y + 1, x + 1)])
    return [list(a) for a in dict.fromkeys(tuple(a) for a in amas)]


def la_tolerance(largeur: int) -> int:
    """De combien de couches deux creux peuvent différer et rester LE MÊME accident de profondeur.

    ⚠ DÉRIVÉE DU CREUX, PAS CHOISIE : c'est la règle que `180` emploie déjà pour dire qu'un creux
    tombe sur une frontière construite — une demi-largeur, plus une couche.
    """
    return int(largeur) // 2 + 1


def la_correspondance(a, b, tolerance: int) -> dict:
    """Combien des creux de `a` ont un creux de `b` à la même profondeur.

    ⚠⚠ LA PART EST CALCULÉE SUR LE PLUS PETIT DES DEUX, et un appariement est EXCLUSIF : sans cela,
    un chunk qui porterait beaucoup de creux apparierait tout ce que son voisin lui présente, et la
    part mesurerait une densité au lieu d'une correspondance.
    """
    reste = list(int(x) for x in b)
    apparies = []
    for x in sorted(int(y) for y in a):
        proches = [y for y in reste if abs(y - x) <= int(tolerance)]
        if not proches:
            continue
        y = min(proches, key=lambda z: (abs(z - x), z))
        reste.remove(y)
        apparies.append((x, y))
    denominateur = min(len(list(a)), len(list(b)))
    return {"creux_a": len(list(a)), "creux_b": len(list(b)),
            "apparies": len(apparies),
            "part": (round(len(apparies) / float(denominateur), 4) if denominateur else None),
            "ecart_median": (round(float(statistics.median(
                [abs(x - y) for x, y in apparies])), 2) if apparies else None)}


def _creux(courbe, combien: int, permutations: int, graine: int) -> tuple[list, int | None]:
    lu = plusieurs_creux([x[1] for x in courbe], int(combien), permutations, graine)
    if not lu.get("decidable"):
        return [], None
    retenus = [x for x in lu["creux"] if x["depasse_tous_les_melanges"]]
    largeurs = [int(x["largeur"]) for x in retenus]
    return ([int(x["couche"]) for x in retenus],
            int(statistics.median_low(largeurs)) if largeurs else None)


def un_amas(url: str, meta: dict, amas, combien: int, permutations: int, graine: int,
            delai: float = DELAI) -> dict:
    """Les quatre chunks d'un amas, leurs creux, et les paires ADJACENTES qu'ils forment."""
    lus = {}
    for cy, cx in amas:
        courbe, _ = la_courbe_dun_chunk(url, meta, cy, cx, delai)
        if courbe is None:
            continue
        creux, largeur = _creux(courbe, combien, permutations, graine)
        if creux:
            lus[(cy, cx)] = {"creux": creux, "largeur": largeur}
    paires = []
    for (ay, ax), a in lus.items():
        for (by, bx), b in lus.items():
            if (ay, ax) >= (by, bx):
                continue
            if abs(ay - by) + abs(ax - bx) != 1:
                continue
            tol = la_tolerance(a["largeur"] or 7)
            paires.append({"a": [ay, ax], "b": [by, bx], "tolerance": int(tol),
                           **la_correspondance(a["creux"], b["creux"], tol)})
    return {"chunks_lus": len(lus), "paires_adjacentes": len(paires), "paires": paires,
            "creux": {f"{cy},{cx}": x["creux"] for (cy, cx), x in lus.items()},
            "largeurs": {f"{cy},{cx}": x["largeur"] for (cy, cx), x in lus.items()}}


def contre_les_non_voisins(amas: list[dict], tirages: int = TIRAGES_NON_VOISINS,
                           graine: int = GRAINE) -> dict:
    """La même correspondance entre chunks qui ne sont PAS voisins — le contrôle apparié.

    ⭐⭐⭐⭐ SANS LUI, « LES VOISINS SE CORRESPONDENT » EST DE L'ARITHMÉTIQUE. Deux chunks quelconques
    portent chacun quelques creux répartis sur cent-neuf couches, donc ils en ont forcément
    quelques-uns à la même profondeur par hasard. Le non-voisin est tiré parmi les chunks des AUTRES
    amas, donc il a la même loi de profondeurs et la même densité de creux : ce qui change entre les
    deux mesures est le VOISINAGE, et rien d'autre.
    """
    tous = [(cle, x, k) for k, a in enumerate(amas) for cle, x in a["creux"].items()]
    if len(tous) < 2:
        return {"decidable": False, "raison": "pas assez de chunks"}
    r = np.random.default_rng(int(graine))
    parts = []
    for k, a in enumerate(amas):
        for cle, creux in a["creux"].items():
            largeur = a["largeurs"].get(cle) or 7
            tol = la_tolerance(largeur)
            loin = [x for _c, x, j in tous if j != k]
            if not loin:
                continue
            for _ in range(int(tirages)):
                autre = loin[int(r.integers(0, len(loin)))]
                p = la_correspondance(creux, autre, tol)["part"]
                if p is not None:
                    parts.append(float(p))
    return {"decidable": bool(parts), "tirages": len(parts),
            "part_mediane": (round(float(statistics.median(parts)), 4) if parts else None),
            "part_moyenne": (round(float(sum(parts) / len(parts)), 4) if parts else None),
            "part_maximale": (round(float(max(parts)), 4) if parts else None),
            "tirages_qui_se_correspondent": int(sum(1 for x in parts if x > 0.0))}


def _med(v):
    return round(float(statistics.median(v)), 4) if v else None


def un_segment(volume: dict, combien: int, permutations: int = PERMUTATIONS,
               delai: float = DELAI, graine: int = GRAINE) -> dict:
    url = f"{BUCKET}/{volume['cle']}"
    try:
        meta = array_meta(url, 0, delai)
    except Exception as e:  # noqa: BLE001
        return {"decidable": False, "segment": volume["segment"],
                "raison": f"le volume ne répond pas : {type(e).__name__}"}
    profond, hy, hx = meta["chunks"]
    _, rows, cols = meta["shape"]
    groupes = [un_amas(url, meta, a, combien, permutations, graine, delai)
               for a in les_amas(-(-rows // hy), -(-cols // hx))]
    groupes = [g for g in groupes if g["chunks_lus"]]
    paires = [p for g in groupes for p in g["paires"]]
    loin = contre_les_non_voisins(groupes, TIRAGES_NON_VOISINS, graine)
    parts = [float(p["part"]) for p in paires if p["part"] is not None]
    return {"decidable": bool(paires), "segment": volume["segment"],
            "amas_lus": len(groupes),
            "chunks_lus": int(sum(g["chunks_lus"] for g in groupes)),
            "paires_adjacentes": len(paires),
            # ⚠⚠ LA MOYENNE ET LE MAXIMUM VOYAGENT AVEC LA MEDIANE : une mediane de zero peut
            # cacher une minorite de paires qui se correspondent tres bien, et publier la seule
            # mediane ferait lire « aucune correspondance » la ou il y en a une par endroits.
            "part_moyenne_des_voisins": (round(float(sum(parts) / len(parts)), 4)
                                         if parts else None),
            "part_maximale_des_voisins": (round(float(max(parts)), 4) if parts else None),
            "paires_qui_se_correspondent": int(sum(1 for x in parts if x > 0.0)),
            "part_mediane_des_voisins": _med([p["part"] for p in paires
                                              if p["part"] is not None]),
            "ecart_median_des_voisins": _med([p["ecart_median"] for p in paires
                                              if p["ecart_median"] is not None]),
            "les_non_voisins": loin, "amas": groupes}


def sur_la_fixture(combien: int, recouvrement_um: float, bruit: float, plis: int = 2,
                   permutations: int = PERMUTATIONS, graine: int = GRAINE) -> dict:
    """Deux fenêtres de la MÊME matière, et deux fenêtres de matières INDÉPENDANTES.

    ⭐⭐⭐⭐ LES DEUX BORNES DE LA QUESTION, SUR LE CHEMIN PHYSIQUE. Deux fenêtres au même décalage
    voient exactement les mêmes frontières : c'est ce qu'une correspondance PARFAITE vaut, bruit
    compris. Deux fenêtres à des décalages différents en voient d'autres : c'est ce que l'absence de
    correspondance vaut. Le rouleau se place entre les deux, et aucun seuil n'entre.

    ⚠ Les deux fenêtres « de la même matière » diffèrent par leur BRUIT — graines différentes — donc
    la correspondance mesurée n'est pas une tautologie : elle dit ce que le lecteur retrouve quand la
    matière est la même mais que la lecture ne l'est pas.
    """
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    vx, pas = float(C.VOXEL_FIN_UM), float(C.PAS_UM)
    memes, autres = [], []
    for k in range(6):
        dec = pas * k / 6.0
        a = courbe_de_la_fixture(COUCHES, dec, CONTRASTE_DE_LA_FIXTURE, plis, vx, pas,
                                 transition_um=recouvrement_um, bruit=bruit)
        b = courbe_de_la_fixture(COUCHES, dec, CONTRASTE_DE_LA_FIXTURE, plis, vx, pas + 1e-9,
                                 transition_um=recouvrement_um, bruit=bruit)
        ca, la = _creux(a, combien, permutations, graine)
        cb, lb = _creux(b, combien, permutations, graine + 1)
        if ca and cb:
            memes.append(la_correspondance(ca, cb, la_tolerance(la or 7))["part"])
        # ⚠⚠⚠ LE DECALAGE DOIT DEPLACER LES FRONTIERES, ET UNE PREMIERE VERSION NE LE FAISAIT PAS :
        # decaler d'une DEMI-FEUILLE remet les frontieres de pli exactement aux memes couches, donc
        # « matieres differentes » rendait une correspondance PARFAITE et les deux bornes ne se
        # separaient pas. Un TIERS de pli les deplace de douze couches, trois fois la tolerance.
        dec2 = dec + (pas / 2.0) / 3.0
        c = courbe_de_la_fixture(COUCHES, dec2, CONTRASTE_DE_LA_FIXTURE, plis, vx, pas,
                                 transition_um=recouvrement_um, bruit=bruit)
        cc, _lc = _creux(c, combien, permutations, graine)
        if ca and cc:
            autres.append(la_correspondance(ca, cc, la_tolerance(la or 7))["part"])
    return {"cellules": 6,
            "part_mediane_de_la_meme_matiere": _med([x for x in memes if x is not None]),
            "part_mediane_de_matieres_differentes": _med([x for x in autres if x is not None])}


def juger(segments: list[dict], fixture: dict) -> dict:
    """Un creux se retrouve-t-il chez le voisin, plus souvent que chez un non-voisin ?"""
    lus = [s for s in segments if s.get("decidable")]
    if not lus:
        return {"decidable": False, "raison": "aucun segment lisible"}
    # ⚠⚠ LA COMPARAISON PORTE SUR LA MOYENNE ET NON SUR LA MEDIANE : la mesure rend une mediane de
    # zero des DEUX cotes, donc une comparaison de medianes ne peut rien separer — ce n'est pas un
    # resultat, c'est un estimateur qui ne resout pas ce qu'on lui demande. La moyenne des parts est
    # la meme quantite lue a une resolution que la matiere permet.
    voisins = _med([s["part_moyenne_des_voisins"] for s in lus
                    if s["part_moyenne_des_voisins"] is not None])
    loin = _med([s["les_non_voisins"]["part_moyenne"] for s in lus
                 if s["les_non_voisins"].get("part_moyenne") is not None])
    meme = fixture.get("part_mediane_de_la_meme_matiere")
    diff = fixture.get("part_mediane_de_matieres_differentes")
    return {"decidable": True, "segments": len(lus),
            "amas_lus": int(sum(s["amas_lus"] for s in lus)),
            "chunks_lus": int(sum(s["chunks_lus"] for s in lus)),
            "paires_adjacentes": int(sum(s["paires_adjacentes"] for s in lus)),
            "part_des_voisins": voisins, "part_des_non_voisins": loin,
            "part_mediane_des_voisins": _med([s["part_mediane_des_voisins"] for s in lus
                                              if s["part_mediane_des_voisins"] is not None]),
            "paires_qui_se_correspondent": int(sum(s["paires_qui_se_correspondent"]
                                                   for s in lus)),
            "ecart_median_des_voisins": _med([s["ecart_median_des_voisins"] for s in lus
                                              if s["ecart_median_des_voisins"] is not None]),
            "part_de_la_meme_matiere": meme,
            "part_de_matieres_differentes": diff,
            # ⚠⚠ TROIS ENONCES. Le premier dit que les deux bornes construites se SEPARENT, sinon
            # rien de ce qui suit ne veut dire quelque chose. Le second dit si un creux se retrouve
            # chez le voisin plus souvent que chez un non-voisin. Le troisieme place le rouleau
            # entre les deux bornes plutot que de le declarer bon ou mauvais.
            "les_deux_bornes_se_separent": bool(
                meme is not None and diff is not None and meme > diff),
            "un_creux_se_retrouve_a_cote": bool(
                voisins is not None and loin is not None and voisins > loin),
            "le_rouleau_vaut_la_meme_matiere_fois": (round(voisins / meme, 4)
                                                     if (voisins and meme) else None)}


def mesurer(segments_n: int = SEGMENTS, permutations: int = PERMUTATIONS) -> dict:
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    vx, pas = float(C.VOXEL_FIN_UM), float(C.PAS_UM)
    de_179 = _relire(CE_QUE_LA_FIXTURE_A_RENDU, ("le_recouvrement_juste_suffisant_um",))
    de_180 = _relire(CE_QUE_LE_ROULEAU_A_RENDU, ("le_bruit_apparie",))
    de_181 = _relire(CE_QUE_LESPACEMENT_A_RENDU, ("espacement_median_du_rouleau",))
    if de_179 is None or de_180 is None or de_181 is None:
        return {"message": "les mesures de `179`, `180` et `181` donnent les réglages"}
    plis = lechelle_des_plis(vx, pas, float(de_181["espacement_median_du_rouleau"]))
    combien = les_creux_a_chercher(plis, COUCHES, vx, pas)
    volumes = les_volumes(combien=segments_n)
    if not volumes:
        return {"message": "aucun volume de surface à la résolution de la campagne n'est recensé"}
    segs = [un_segment(v, combien, permutations) for v in volumes]
    fixture = sur_la_fixture(combien, float(de_179["le_recouvrement_juste_suffisant_um"]),
                             float(de_180["le_bruit_apparie"]), 2, permutations)
    return {"creux_cherches_par_chunk": int(combien), "cote_du_treillis": int(COTE_DU_TREILLIS),
            "tirages_de_non_voisins": int(TIRAGES_NON_VOISINS),
            "permutations": int(permutations), "graine": int(GRAINE), "couches": int(COUCHES),
            "recouvrement_um_de_179": float(de_179["le_recouvrement_juste_suffisant_um"]),
            "bruit_apparie_de_180": float(de_180["le_bruit_apparie"]),
            "les_segments": segs, "la_fixture": fixture,
            "le_verdict": juger(segs, fixture)}


def afficher(r: dict) -> None:
    if "message" in r:
        print(r["message"])
        return
    v, fx = r["le_verdict"], r["la_fixture"]
    print("UN CREUX SE RETROUVE-T-IL À CÔTÉ ?")
    print(f"  {r['creux_cherches_par_chunk']} creux cherchés · amas de 2×2 sur le treillis "
          f"{r['cote_du_treillis']}×{r['cote_du_treillis']} · "
          f"{r['tirages_de_non_voisins']} tirages de non-voisins · "
          f"{r['permutations']} permutations")
    print()
    for s in r["les_segments"]:
        if not s.get("decidable"):
            print(f"  {s['segment']} — {s.get('raison')}")
            continue
        loin = s["les_non_voisins"]
        print(f"  {s['segment']} · {s['amas_lus']} amas · {s['chunks_lus']} chunks · "
              f"{s['paires_adjacentes']} paires adjacentes")
        print(f"     voisins moy {s['part_moyenne_des_voisins']} · méd "
              f"{s['part_mediane_des_voisins']} · max {s['part_maximale_des_voisins']} · "
              f"{s['paires_qui_se_correspondent']}/{s['paires_adjacentes']} paires · écart "
              f"{s['ecart_median_des_voisins']}")
        print(f"     non-voisins moy {loin.get('part_moyenne')} · méd "
              f"{loin.get('part_mediane')} sur {loin.get('tirages')} tirages")
    print()
    print(f"  LES DEUX BORNES · même matière {fx['part_mediane_de_la_meme_matiere']} · "
          f"matières différentes {fx['part_mediane_de_matieres_differentes']}")
    print()
    print("  ★ LE VERDICT")
    for cle in ("amas_lus", "chunks_lus", "paires_adjacentes", "paires_qui_se_correspondent",
                "part_des_voisins", "part_des_non_voisins", "part_mediane_des_voisins",
                "ecart_median_des_voisins", "part_de_la_meme_matiere",
                "part_de_matieres_differentes", "le_rouleau_vaut_la_meme_matiere_fois",
                "les_deux_bornes_se_separent", "un_creux_se_retrouve_a_cote"):
        print(f"     {cle:<44} {v.get(cle)}")


def verifier() -> int:
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        if not ok:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    vx, pas = float(C.VOXEL_FIN_UM), float(C.PAS_UM)

    # ⚠⚠⚠ DES VOISINS, ET LA BATTERIE LE VERIFIE : chaque amas est fait de quatre chunks dont les
    # paires adjacentes existent. Un treillis lache n'en aurait aucune, et c'est le defaut que
    # `fiber_orientation.survey` a deja paye.
    amas = les_amas(198, 143)
    v("les amas existent", bool(amas), str(len(amas)))
    # ⚠⚠ QUATRE POSITIONS DISTINCTES QUI FORMENT UN CARRE, et pas seulement « quatre paires a
    # distance un » : une sonde qui dupliquait deux positions passait au VERT, parce qu'un doublon
    # fabrique lui aussi quatre paires adjacentes.
    for a in amas[:4]:
        adj = sum(1 for p in a for q in a
                  if p < q and abs(p[0] - q[0]) + abs(p[1] - q[1]) == 1)
        v(f"l'amas {a[0]} porte quatre positions distinctes", len(set(a)) == 4, str(a))
        v(f"l'amas {a[0]} porte quatre paires adjacentes", adj == 4, str(adj))
        ys, xs = {y for y, _x in a}, {x for _y, x in a}
        v(f"l'amas {a[0]} est un carré", len(ys) == 2 and len(xs) == 2
          and max(ys) - min(ys) == 1 and max(xs) - min(xs) == 1, str(a))
    v("les amas tiennent dans la grille",
      all(0 <= y < 198 and 0 <= x < 143 for a in amas for y, x in a))

    # ⚠ LA TOLERANCE EST DERIVEE DU CREUX.
    v("la tolérance est la demi-largeur plus une couche", la_tolerance(7) == 4,
      str(la_tolerance(7)))
    v("et elle grandit avec la largeur", la_tolerance(3) < la_tolerance(7))

    # ⭐⭐⭐⭐ LA CORRESPONDANCE : la reponse est connue AVANT la mesure sur des listes construites.
    v("deux listes identiques se correspondent entièrement",
      la_correspondance([10, 40, 70], [10, 40, 70], 4)["part"] == 1.0)
    v("deux listes éloignées ne se correspondent pas",
      la_correspondance([10, 40, 70], [95, 96, 97], 4)["part"] == 0.0)
    v("un décalage sous la tolérance se correspond quand même",
      la_correspondance([10, 40, 70], [12, 42, 72], 4)["part"] == 1.0)
    v("un décalage au-dessus ne se correspond pas",
      la_correspondance([10, 40, 70], [20, 50, 80], 4)["part"] == 0.0)

    # ⚠⚠ L'APPARIEMENT EST EXCLUSIF : sans cela un chunk qui porte beaucoup de creux apparierait
    # tout ce que son voisin lui presente, et la part mesurerait une DENSITE et non une
    # correspondance. La reponse est connue : trois creux serres en face d'un seul n'en apparient
    # qu'UN.
    v("un appariement est exclusif",
      la_correspondance([40], [39, 40, 41], 4)["apparies"] == 1,
      str(la_correspondance([40], [39, 40, 41], 4)))
    v("et la part se calcule sur le plus petit des deux",
      la_correspondance([40], [39, 40, 41], 4)["part"] == 1.0)
    v("deux creux d'un côté pour un de l'autre n'en apparient qu'un",
      la_correspondance([40, 41], [40], 4)["apparies"] == 1,
      str(la_correspondance([40, 41], [40], 4)))

    # ⭐⭐⭐⭐ LES DEUX BORNES SUR LE CHEMIN PHYSIQUE, ET ELLES DOIVENT SE SEPARER. Une premiere
    # version decalait la seconde fenetre d'une DEMI-FEUILLE, ce qui remet les frontieres de pli aux
    # MEMES couches : « matieres differentes » rendait alors une correspondance PARFAITE et le
    # controle ne controlait rien.
    de_179 = _relire(CE_QUE_LA_FIXTURE_A_RENDU, ("le_recouvrement_juste_suffisant_um",))
    de_180 = _relire(CE_QUE_LE_ROULEAU_A_RENDU, ("le_bruit_apparie",))
    de_181 = _relire(CE_QUE_LESPACEMENT_A_RENDU, ("espacement_median_du_rouleau",))
    v("les mesures de `179`, `180` et `181` donnent les réglages",
      de_179 and de_180 and de_181)
    if de_179 and de_180 and de_181:
        combien = les_creux_a_chercher(
            lechelle_des_plis(vx, pas, float(de_181["espacement_median_du_rouleau"])),
            COUCHES, vx, pas)
        fx = sur_la_fixture(combien, float(de_179["le_recouvrement_juste_suffisant_um"]),
                            float(de_180["le_bruit_apparie"]), 2, PERMUTATIONS)
        v("la même matière se retrouve entièrement",
          fx["part_mediane_de_la_meme_matiere"] == 1.0,
          str(fx["part_mediane_de_la_meme_matiere"]))
        v("deux matières différentes ne se retrouvent pas",
          fx["part_mediane_de_matieres_differentes"] == 0.0,
          str(fx["part_mediane_de_matieres_differentes"]))
        v("et les deux bornes se séparent",
          fx["part_mediane_de_la_meme_matiere"]
          > fx["part_mediane_de_matieres_differentes"])

    # ⭐⭐⭐⭐ LE CONTROLE DES NON-VOISINS EST EXERCE SUR UNE ENTREE FABRIQUEE, parce qu'une sonde
    # qui le faisait tirer dans le MEME amas passait au VERT : rien dans la batterie ne le touchait.
    # La reponse est connue avant la mesure — deux amas dont les creux sont TRES differents doivent
    # rendre une part nulle entre amas, et une part entiere a l'interieur.
    faux = [{"creux": {"0,0": [10, 40, 70], "0,1": [10, 40, 70]},
             "largeurs": {"0,0": 7, "0,1": 7}},
            {"creux": {"5,5": [95, 96, 97], "5,6": [95, 96, 97]},
             "largeurs": {"5,5": 7, "5,6": 7}}]
    loin = contre_les_non_voisins(faux, 5, GRAINE)
    v("le contrôle tire hors de l'amas", loin["decidable"] and loin["part_moyenne"] == 0.0,
      str(loin))
    v("et il tire autant de fois qu'on lui demande", loin["tirages"] == 4 * 5,
      str(loin["tirages"]))

    # ⭐⭐⭐⭐ LES ENONCES DU VERDICT TOMBENT CHACUN SUR L'ENTREE QUI LE VISE.
    def _seg(moy_voisins, moy_loin):
        return {"decidable": True, "segment": "x", "amas_lus": 3, "chunks_lus": 12,
                "paires_adjacentes": 9, "paires_qui_se_correspondent": 4,
                "part_moyenne_des_voisins": float(moy_voisins),
                "part_mediane_des_voisins": 0.0,
                "part_maximale_des_voisins": 1.0, "ecart_median_des_voisins": 1.0,
                "les_non_voisins": {"decidable": True, "tirages": 200,
                                    "part_moyenne": float(moy_loin), "part_mediane": 0.0,
                                    "part_maximale": 1.0}}

    bon = juger([_seg(0.22, 0.14)], {"part_mediane_de_la_meme_matiere": 1.0,
                                     "part_mediane_de_matieres_differentes": 0.0})
    v("un creux se retrouve à côté quand les voisins dépassent les non-voisins",
      bon["un_creux_se_retrouve_a_cote"])
    v("les deux bornes se séparent quand elles diffèrent", bon["les_deux_bornes_se_separent"])
    v("et le rouleau est rapporté à la même matière",
      bon["le_rouleau_vaut_la_meme_matiere_fois"] == 0.22,
      str(bon["le_rouleau_vaut_la_meme_matiere_fois"]))
    nul = juger([_seg(0.14, 0.22)], {"part_mediane_de_la_meme_matiere": 1.0,
                                     "part_mediane_de_matieres_differentes": 0.0})
    v("des voisins qui ne dépassent pas retirent le second énoncé",
      not nul["un_creux_se_retrouve_a_cote"])
    # ⚠⚠ ET L'EGALITE NE SUFFIT PAS : une sonde qui remplacait le « plus grand que » par un « plus
    # grand ou egal » passait au VERT, parce que le cas asserte etait STRICTEMENT plus petit.
    egal = juger([_seg(0.18, 0.18)], {"part_mediane_de_la_meme_matiere": 1.0,
                                      "part_mediane_de_matieres_differentes": 0.0})
    v("une égalité entre voisins et non-voisins ne se retrouve pas",
      not egal["un_creux_se_retrouve_a_cote"])
    plat = juger([_seg(0.22, 0.14)], {"part_mediane_de_la_meme_matiere": 0.0,
                                      "part_mediane_de_matieres_differentes": 0.0})
    v("des bornes qui ne se séparent pas retirent le premier",
      not plat["les_deux_bornes_se_separent"])
    vide = juger([{"decidable": False, "segment": "x"}],
                 {"part_mediane_de_la_meme_matiere": 1.0,
                  "part_mediane_de_matieres_differentes": 0.0})
    v("aucun segment lisible rend un verdict indécidable", not vide["decidable"])

    nom = "un_creux_se_retrouve_t_il_a_cote.py"
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
