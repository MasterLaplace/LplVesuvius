"""L'erreur commune à un chunk est-elle celle de la TRANSITION qui produit le creux ?

⭐⭐⭐⭐ POURQUOI CE FICHIER, ET C'EST `R4-P55` QUI LE NOMME. Deux découpages sans rien de commun ont
mesuré la même quantité : **14,9372 voxels** par le plan (`205`) et **15,7743 voxels** par la
profondeur (`206`). Aucun des deux ne l'atteint, et aucun ne dit d'où elle vient.

⭐ OR `179` A DÉJÀ PUBLIÉ UNE LONGUEUR DU MÊME ORDRE, ET C'EST CELLE QUI FABRIQUE LE CREUX : la
transition juste suffisante vaut **19 voxels**. Une frontière étalée sur cette longueur ne peut pas
être localisée mieux que cette longueur — ce serait une borne de l'INSTRUMENT et non du bruit, donc
irréductible par tout moyennage, ce qui expliquerait d'un coup les deux refus de `205` et de `206`.

⭐⭐⭐⭐ ET LA PRÉDICTION SE POSE AVANT LA MESURE : si l'erreur EST la transition, alors une matière
à transition plus étroite doit rendre une erreur plus petite, dans le même rapport. `179` porte
l'échelle entière — sa bissection l'a balayée — donc cette tranche peut POSER la transition et lire
l'erreur au lieu de la subir.

⚠⚠ LE PIÈGE EST ÉCRIT D'AVANCE, ET C'EST CELUI DE `179` LUI-MÊME : son échelle a été balayée SANS
BRUIT, alors que le rouleau en porte. `179` a mesuré que le creux tient jusqu'au bruit **16** de
`156`, donc l'échelle est ici portée à ce bruit-là — sinon elle mesurerait un instrument plus propre
que celui qui lit le rouleau, et le rapport publié serait flatteur.

⚠⚠⚠ ET LA PORTÉE DE CETTE TRANCHE EST BORNÉE, DITE PLUTÔT QUE TUE : la fixture de `179` espace ses
frontières de **36 couches** là où le rouleau a un pas de **72,0833 voxels**. Ce qui se teste ici est
donc la PROPORTIONNALITÉ entre la transition et l'erreur, pas l'égalité de deux nombres mesurés sur
deux matières différentes.

Usage :
    uv run python src/nappe/la_transition_fixe_t_elle_lerreur_de_chunk.py --verifier
    uv run python src/nappe/la_transition_fixe_t_elle_lerreur_de_chunk.py \\
        --json docs/mesures/la_transition_fixe_t_elle_lerreur_de_chunk.json
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

from la_coherence_creuse_t_elle_a_la_frontiere import (CONTRASTE_DE_LA_FIXTURE,  # noqa: E402
                                                       COUCHES_DE_LA_CAMPAGNE,
                                                       PLIS_DE_LA_FIXTURE,
                                                       les_frontieres_de_la_fixture,
                                                       le_verdict_du_creux)
from la_recette_posee_sur_le_rouleau import DELAI, PERMUTATIONS  # noqa: E402
from ouvrir_les_quinze import _rng  # noqa: E402
from le_creux_bouge_t_il_avec_le_maillage import lappariement  # noqa: E402
from le_creux_change_t_il_avec_la_profondeur_lue import (ce_que_179_a_rendu,  # noqa: E402
                                                         ce_que_le_plan_a_rendu)
from quelle_fenetre_lit_une_bascule import courbe_de_la_fixture  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
GRAINE = 20261017

LA_QUESTION_DECLAREE = ("l'erreur avec laquelle le creux situe une frontière croît-elle avec la "
                        "TRANSITION qui la fabrique ?")
LES_EPREUVES_DECLAREES = ("l'erreur de localisation est-elle appariée à la transition",)
GARANTIE = 1.0 / (PERMUTATIONS + 1)
GARANTIE_PAR_EPREUVE = GARANTIE / len(LES_EPREUVES_DECLAREES)


def ce_que_179_a_mesure_en_plus(chemin: Path | None = None) -> dict:
    """Les bornes de l'échelle, relues chez `179` : le voxel, le bruit tenu, l'espacement.

    ⚠⚠ LES TROIS SONT DES BORNES DE L'ECHELLE, ET AUCUNE N'EST CHOISIE ICI. Le voxel est le pas de
    la bissection de `179`, le bruit est le plus grand qu'elle ait tenu, et l'espacement des
    frontieres de sa fixture est le plafond : une transition plus large que lui ferait se recouvrir
    deux frontieres, et « localiser une frontiere » cesserait d'avoir un sens.
    """
    p = Path(chemin) if chemin is not None else (
        MESURES / "la_coherence_creuse_t_elle_a_la_frontiere.json")
    if not p.is_file():
        return {"decidable": False, "raison": "la mesure de `179` est absente"}
    d = json.loads(p.read_text(encoding="utf-8"))
    v = d.get("le_verdict") or {}
    if d.get("voxel_um") is None or d.get("pli_en_couches") is None:
        return {"decidable": False, "raison": "`179` ne publie pas ses bornes d'échelle"}
    return {"decidable": True,
            "le_voxel_en_um": d.get("voxel_um"),
            "lespacement_des_frontieres_en_couches": d.get("pli_en_couches"),
            "le_plus_grand_bruit_tenu": v.get("le_plus_grand_bruit_tenu"),
            "les_couches_de_la_campagne": d.get("couches"),
            "les_plis_de_la_fixture": d.get("plis_grossiers")}


def lechelle_des_transitions(transition_du_rouleau, espacement, voxel_um) -> dict:
    """Les transitions à poser, en voxels — les deux bouts dérivés, aucun choisi.

    ⚠⚠ LE PLANCHER EST LA TRANSITION DU ROULEAU DIVISEE PAR DEUX et le plafond est l'ESPACEMENT DES
    FRONTIERES : en dessous du plancher on ne mesure plus rien que `179` ait deja borne, et au-dessus
    du plafond deux frontieres se recouvrent, donc « localiser une frontiere » n'a plus de sens. Le
    pas est le VOXEL, qui est la tolerance de la bissection de `179`.

    ⭐ ET LA TRANSITION DU ROULEAU EST DANS L'ECHELLE PAR CONSTRUCTION : c'est le barreau contre
    lequel les nombres de `205` et de `206` se comparent.
    """
    if transition_du_rouleau is None or espacement is None or voxel_um is None:
        return {"decidable": False, "raison": "une borne de `179` manque"}
    t = float(transition_du_rouleau)
    plafond = float(espacement)
    plancher = t / 2.0
    if plancher >= plafond:
        return {"decidable": False,
                "raison": f"le plancher {round(plancher, 4)} atteint déjà le plafond "
                          f"{round(plafond, 4)}"}
    barreaux = [float(x) for x in range(int(np.ceil(plancher)), int(np.floor(plafond)) + 1)]
    if float(t) not in barreaux:
        barreaux = sorted(set(barreaux) | {float(t)})
    return {"decidable": True,
            "les_transitions_en_voxels": barreaux,
            "la_transition_du_rouleau_en_voxels": round(t, 4),
            "le_plancher_en_voxels": round(plancher, 4),
            "le_plafond_en_voxels": round(plafond, 4),
            "le_pas_en_voxels": round(float(voxel_um) / float(voxel_um), 4)}


def lerreur_a_cette_transition(transition_en_voxels: float, voxel_um: float, pas_um: float,
                               bruit: float, decalages: int, graine: int,
                               couches: int = COUCHES_DE_LA_CAMPAGNE,
                               plis: int = PLIS_DE_LA_FIXTURE,
                               permutations: int = PERMUTATIONS) -> dict:
    """Avec quelle erreur le creux situe-t-il une frontière POSÉE, à cette transition ?

    ⭐⭐⭐⭐ LA FRONTIERE EST CONNUE AVANT LA MESURE ET LUE PAR LE VRAI LECTEUR : `179` la derive du
    pas, du nombre de plis et du decalage, jamais de la courbe qu'on met a l'epreuve. L'erreur est
    donc un ECART a une verite, pas une dispersion de lectures entre elles.

    ⚠⚠ LES DECALAGES BALAYENT LA PHASE DE LA FENETRE DANS LA FEUILLE, qui n'est pas connue sur
    donnees reelles : mesurer a un seul decalage rendrait une loterie, ce que `173` a deja paye.

    ⚠ Un decalage ou le lecteur ne rend RIEN est compte a part, jamais remplace par une erreur nulle.
    """
    ecarts, muets, lus = [], 0, 0
    for k in range(int(decalages)):
        dec = float(pas_um) * k / float(decalages)
        courbe = courbe_de_la_fixture(int(couches), dec, CONTRASTE_DE_LA_FIXTURE, int(plis),
                                      float(voxel_um), float(pas_um),
                                      transition_um=float(transition_en_voxels) * float(voxel_um),
                                      bruit=float(bruit))
        attendues = les_frontieres_de_la_fixture(int(couches), dec, int(plis),
                                                 float(voxel_um), float(pas_um))
        lu = le_verdict_du_creux(courbe, None, int(permutations), int(graine) + 7 * k)
        if lu.get("frontiere_lue") is None or not attendues:
            muets += 1
            continue
        lus += 1
        ecarts.append(float(min(abs(int(lu["frontiere_lue"]) - x) for x in attendues)))
    if len(ecarts) < 3:
        return {"decidable": False, "raison": "moins de trois décalages lisibles",
                "la_transition_en_voxels": round(float(transition_en_voxels), 4),
                "les_decalages_muets": int(muets)}
    e = np.asarray(ecarts, dtype=float)
    return {"decidable": True,
            "la_transition_en_voxels": round(float(transition_en_voxels), 4),
            "les_decalages": int(decalages),
            "les_decalages_lus": int(lus),
            "les_decalages_muets": int(muets),
            "lerreur_quadratique_en_voxels": round(float(np.sqrt(float(np.mean(e * e)))), 4),
            "lerreur_mediane_en_voxels": round(float(np.median(e)), 4),
            "lerreur_maximale_en_voxels": round(float(e.max()), 4)}


def la_courbe_des_transitions(lignes) -> dict:
    """L'erreur en fonction de la transition, barreau par barreau.

    ⚠⚠⚠ LE COMPTE DE DECALAGES MUETS VOYAGE AVEC CHAQUE BARREAU : une transition ou le lecteur se
    tait presque partout rend une erreur calculee sur ce qui reste, donc sur les cas FACILES. La
    publier seule recompenserait un instrument qui a le droit de ne pas repondre.
    """
    lisibles = [x for x in lignes if x.get("decidable")]
    if len(lisibles) < 3:
        return {"decidable": False, "raison": "moins de trois transitions lisibles",
                "les_barreaux": lignes}
    t = [float(x["la_transition_en_voxels"]) for x in lisibles]
    e = [float(x["lerreur_quadratique_en_voxels"]) for x in lisibles]
    return {"decidable": True, "les_barreaux": lignes,
            "les_transitions_lisibles": len(lisibles),
            "la_plus_petite_transition_en_voxels": round(min(t), 4),
            "la_plus_grande_transition_en_voxels": round(max(t), 4),
            "lerreur_a_la_plus_petite_en_voxels": round(e[int(np.argmin(t))], 4),
            "lerreur_a_la_plus_grande_en_voxels": round(e[int(np.argmax(t))], 4),
            "le_rapport_des_erreurs": (round(e[int(np.argmax(t))] / e[int(np.argmin(t))], 4)
                                       if e[int(np.argmin(t))] > 0 else None),
            "le_rapport_des_transitions": round(max(t) / min(t), 4),
            "les_transitions": [round(x, 4) for x in t],
            "les_erreurs": [round(x, 4) for x in e]}


def juger(courbe: dict, epreuve: dict, echelle: dict, par_le_plan: dict,
          par_179: dict) -> dict:
    """L'erreur suit-elle la transition, et que vaut-elle à celle du rouleau ?

    ⚠⚠⚠ CE QUI EST COMPARE AUX NOMBRES DE `205` ET DE `206` EST LE BARREAU A LA TRANSITION DU
    ROULEAU, et rien d'autre. Comparer la courbe entiere a un nombre unique ferait dire a la
    fixture ce qu'elle ne dit pas.

    ⚠⚠ ET LA COMPARAISON RESTE BORNEE : la fixture espace ses frontieres de trente-six couches la
    ou le rouleau a un pas de soixante-douze. Ce qui se teste est la PROPORTIONNALITE, pas l'egalite
    de deux nombres mesures sur deux matieres differentes.
    """
    if not courbe.get("decidable") or not epreuve.get("decidable"):
        return {"decidable": False, "raison": "la courbe ou l'épreuve manque"}
    t_rouleau = echelle.get("la_transition_du_rouleau_en_voxels")
    au_rouleau = next((x for x in courbe["les_barreaux"]
                       if x.get("decidable")
                       and abs(float(x["la_transition_en_voxels"])
                               - float(t_rouleau or -1)) < 1e-9), None)
    chunk = par_le_plan.get("le_bruit_de_chunk_en_voxels")
    lue = (None if au_rouleau is None else au_rouleau["lerreur_quadratique_en_voxels"])
    return {"decidable": True,
            "la_transition_du_rouleau_en_voxels": t_rouleau,
            "lerreur_a_la_transition_du_rouleau_en_voxels": lue,
            "lerreur_de_chunk_de_205_en_voxels": chunk,
            "le_rapport_a_lerreur_de_chunk": (round(float(lue) / float(chunk), 4)
                                              if lue and chunk else None),
            "la_correlation_absolue": epreuve["la_correlation_absolue"],
            "la_valeur_p": epreuve["la_valeur_p"],
            "lerreur_suit_la_transition": bool(epreuve["les_deux_pas_sont_apparies"]),
            "le_rapport_des_transitions": courbe["le_rapport_des_transitions"],
            "le_rapport_des_erreurs": courbe["le_rapport_des_erreurs"],
            "lerreur_croit_elle_aussi_vite": (
                round(float(courbe["le_rapport_des_erreurs"])
                      / float(courbe["le_rapport_des_transitions"]), 4)
                if courbe.get("le_rapport_des_erreurs") else None),
            "lespacement_des_frontieres_en_couches": par_179.get(
                "lespacement_des_frontieres_en_couches"),
            "le_bruit_porte": par_179.get("le_plus_grand_bruit_tenu")}


def une_erreur_fabriquee(transitions, pente: float, bruit: float, graine: int) -> list[dict]:
    """Des erreurs qui suivent — ou non — la transition, à dispersion égale.

    ⭐⭐⭐⭐ LA PENTE EST LA SEULE CHOSE QUI CHANGE ENTRE LES DEUX FACES : le bruit pose est le meme
    des deux cotes. Une face negative plus bruitee serait plus facile a refuser, donc elle ne
    mesurerait pas le bon refus.
    """
    r = _rng(int(graine))
    return [{"decidable": True, "la_transition_en_voxels": float(t),
             "lerreur_quadratique_en_voxels": float(pente) * float(t)
             + float(r.normal(0.0, float(bruit))),
             "les_decalages_muets": 0}
            for t in transitions]


def sur_letalon(transitions, pente: float = 0.5, bruit: float = 1.0, graine: int = GRAINE,
                replicats: int = 12, tirages: int = PERMUTATIONS) -> dict:
    """L'épreuve voit-elle une erreur qui suit la transition, et se tait-elle sinon ?

    ⚠⚠⚠ LES DEUX FACES SUR REPLICATS, ET LA FACE NEGATIVE EN A DAVANTAGE — la lecon de `202`.
    ⭐ LA FACE NEGATIVE POSE UNE PENTE NULLE ET GARDE LE MEME BRUIT : c'est le refus difficile.
    """
    vus, rapports = 0, []
    for i in range(int(replicats)):
        lignes = une_erreur_fabriquee(transitions, pente, bruit, int(graine) + 1000 * i)
        cb = la_courbe_des_transitions(lignes)
        if not cb.get("decidable"):
            continue
        ep = lappariement(cb["les_transitions"], cb["les_erreurs"], tirages,
                          int(graine) + i, GARANTIE_PAR_EPREUVE)
        vus += int(bool(ep.get("les_deux_pas_sont_apparies")))
        if cb.get("le_rapport_des_erreurs"):
            rapports.append(float(cb["le_rapport_des_erreurs"]))
    replicats_du_refus = int(2.0 / float(GARANTIE_PAR_EPREUVE))
    faux, plats = 0, []
    for i in range(replicats_du_refus):
        lignes = une_erreur_fabriquee(transitions, 0.0, bruit,
                                      int(graine) + 500000 + 1000 * i)
        cb = la_courbe_des_transitions(lignes)
        if not cb.get("decidable"):
            continue
        ep = lappariement(cb["les_transitions"], cb["les_erreurs"], tirages,
                          int(graine) + 77 + i, GARANTIE_PAR_EPREUVE)
        faux += int(bool(ep.get("les_deux_pas_sont_apparies")))
        if cb.get("le_rapport_des_erreurs"):
            plats.append(float(cb["le_rapport_des_erreurs"]))
    return {"decidable": True,
            "les_transitions_par_replicat": len(list(transitions)),
            "la_pente_posee": float(pente), "le_bruit_pose": float(bruit),
            "replicats": int(replicats), "les_vus": int(vus),
            "la_part_trouvee": round(float(vus) / float(replicats), 4),
            "le_rapport_median_sur_la_face_positive": (round(float(np.median(rapports)), 4)
                                                       if rapports else None),
            "les_replicats_du_refus": int(replicats_du_refus), "les_faux": int(faux),
            "le_taux_de_faux": round(float(faux) / float(replicats_du_refus), 4),
            "le_rapport_median_sur_la_face_negative": (round(float(np.median(plats)), 4)
                                                       if plats else None),
            "la_garantie": round(float(GARANTIE_PAR_EPREUVE), 4),
            "letalon_separe": bool(vus >= replicats
                                   and faux / float(replicats_du_refus)
                                   <= float(GARANTIE_PAR_EPREUVE) * 2.0 + 1e-12)}


def mesurer(delai: float = DELAI, graine: int = GRAINE, replicats: int = 12,
            decalages: int = 12) -> dict:
    """L'échelle des transitions, l'erreur à chacune, l'épreuve et l'étalon."""
    par_179 = ce_que_179_a_rendu()
    bornes = ce_que_179_a_mesure_en_plus()
    par_le_plan = ce_que_le_plan_a_rendu()
    if not bornes.get("decidable"):
        return {"decidable": False, "raison": bornes.get("raison")}
    echelle = lechelle_des_transitions(par_179.get("la_transition_en_voxels"),
                                       bornes.get("lespacement_des_frontieres_en_couches"),
                                       bornes.get("le_voxel_en_um"))
    if not echelle.get("decidable"):
        return {"decidable": False, "raison": echelle.get("raison")}
    import combien_dinterstices_traverses as C  # noqa: PLC0415
    bruit = float(bornes.get("le_plus_grand_bruit_tenu") or 0.0)
    lignes = [lerreur_a_cette_transition(t, float(C.VOXEL_FIN_UM), float(C.PAS_UM), bruit,
                                         int(decalages), int(graine) + 101 * i)
              for i, t in enumerate(echelle["les_transitions_en_voxels"])]
    courbe = la_courbe_des_transitions(lignes)
    epreuve = (lappariement(courbe["les_transitions"], courbe["les_erreurs"], PERMUTATIONS,
                            graine, GARANTIE_PAR_EPREUVE)
               if courbe.get("decidable") else {"decidable": False,
                                                "raison": "la courbe est indécidable"})
    return {
        "graine": int(graine), "tirages": int(PERMUTATIONS),
        "la_question_declaree": LA_QUESTION_DECLAREE,
        "les_epreuves_declarees": list(LES_EPREUVES_DECLAREES),
        "la_garantie_par_epreuve": round(float(GARANTIE_PAR_EPREUVE), 7),
        "ce_que_179_a_rendu": par_179,
        "les_bornes_de_179": bornes,
        "ce_que_205_a_rendu": par_le_plan,
        "lechelle_des_transitions": echelle,
        "le_bruit_porte": bruit,
        "les_decalages": int(decalages),
        "la_courbe": courbe,
        "lepreuve": epreuve,
        "le_verdict": juger(courbe, epreuve, echelle, par_le_plan, bornes),
        "letalon": sur_letalon(echelle["les_transitions_en_voxels"], graine=graine,
                               replicats=replicats),
    }


def afficher(r: dict) -> None:
    if not r.get("decidable", True) and "raison" in r:
        print(f"INDÉCIDABLE : {r['raison']}")
        return
    ec = r.get("lechelle_des_transitions") or {}
    print(f"LA TRANSITION FIXE-T-ELLE L'ERREUR DE CHUNK   transitions "
          f"{ec.get('le_plancher_en_voxels')} à {ec.get('le_plafond_en_voxels')} voxels · "
          f"celle du rouleau {ec.get('la_transition_du_rouleau_en_voxels')} · bruit "
          f"{r.get('le_bruit_porte')} · {r.get('les_decalages')} décalages")
    cb = r.get("la_courbe") or {}
    for nom, clef in (("LA TRANSITION", "la_transition_en_voxels"),
                      ("L'ERREUR", "lerreur_quadratique_en_voxels"),
                      ("DÉCALAGES LUS", "les_decalages_lus"),
                      ("DÉCALAGES MUETS", "les_decalages_muets")):
        print(f"  {nom:<17} " + " · ".join(
            str(x.get(clef)) for x in (cb.get("les_barreaux") or [])))
    ep = r.get("lepreuve") or {}
    if ep.get("decidable"):
        print(f"  L'ÉPREUVE         |r| = {ep['la_correlation_absolue']} contre "
              f"{ep['la_correlation_absolue_mediane_du_nul']} au mélange · "
              f"{ep['les_melanges_au_moins_aussi_forts']}/{ep['tirages']} · P = "
              f"{ep['la_valeur_p']} · appariés {ep['les_deux_pas_sont_apparies']}")
    ve = r.get("le_verdict") or {}
    if ve.get("decidable"):
        print(f"  LE VERDICT        à la transition du rouleau "
              f"({ve['la_transition_du_rouleau_en_voxels']} voxels) l'erreur vaut "
              f"{ve['lerreur_a_la_transition_du_rouleau_en_voxels']} · `205` en isolait "
              f"{ve['lerreur_de_chunk_de_205_en_voxels']} · rapport "
              f"{ve['le_rapport_a_lerreur_de_chunk']}")
        print(f"                    les transitions varient de "
              f"{ve['le_rapport_des_transitions']} et les erreurs de "
              f"{ve['le_rapport_des_erreurs']} · aussi vite "
              f"{ve['lerreur_croit_elle_aussi_vite']}")
    et = r.get("letalon") or {}
    if et.get("decidable"):
        print(f"  L'ÉTALON          sépare {et['letalon_separe']} · trouve "
              f"{et['la_part_trouvee']} des {et['replicats']} réplicats (rapport "
              f"{et['le_rapport_median_sur_la_face_positive']}) · {et['les_faux']} faux sur "
              f"{et['les_replicats_du_refus']} = {et['le_taux_de_faux']} pour "
              f"{et['la_garantie']} garantis (rapport "
              f"{et['le_rapport_median_sur_la_face_negative']})")


def verifier() -> int:
    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        if not ok:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    v("★★ une seule question est déclarée", isinstance(LA_QUESTION_DECLAREE, str))
    v("★★★ une seule épreuve est déclarée, donc la garantie reste entière",
      len(LES_EPREUVES_DECLAREES) == 1
      and abs(GARANTIE_PAR_EPREUVE - 1.0 / (PERMUTATIONS + 1)) < 1e-12)

    # ⚠⚠ LES TROIS BORNES VIENNENT DE `179`, ET AUCUNE N'EST TAPEE ICI.
    b = ce_que_179_a_mesure_en_plus()
    brut = json.loads((MESURES / "la_coherence_creuse_t_elle_a_la_frontiere.json")
                      .read_text(encoding="utf-8"))
    v("★★★★ le voxel, l'espacement et le bruit tenu sont relus chez `179`",
      b["decidable"] and b["le_voxel_en_um"] == brut["voxel_um"]
      and b["lespacement_des_frontieres_en_couches"] == brut["pli_en_couches"]
      and b["le_plus_grand_bruit_tenu"] == brut["le_verdict"]["le_plus_grand_bruit_tenu"],
      str(b))
    v("★★★ `179` absent est dit, jamais remplacé",
      not ce_que_179_a_mesure_en_plus(Path("/pas/de/fichier.json"))["decidable"])

    # ⭐⭐⭐⭐ L'ECHELLE A SES DEUX BOUTS DERIVES, ET ELLE PORTE LE BARREAU DU ROULEAU.
    e = lechelle_des_transitions(19.0, 36, 2.4)
    v("★★★★ le plancher est la moitié de la transition du rouleau, le plafond l'espacement",
      e["decidable"] and abs(e["le_plancher_en_voxels"] - 9.5) < 1e-9
      and abs(e["le_plafond_en_voxels"] - 36.0) < 1e-9,
      f"{e.get('le_plancher_en_voxels')} à {e.get('le_plafond_en_voxels')}")
    # ⚠⚠ LA SONDE PREND UNE TRANSITION QUI NE TOMBE PAS SUR UN BARREAU ENTIER : avec dix-neuf, le
    # barreau existe deja par le pas du voxel, donc l'insertion explicite n'etait exercee par rien
    # et un bris qui la retirait restait vert.
    eb = lechelle_des_transitions(19.5, 36, 2.4)
    v("★★★★ la transition du ROULEAU est dans l'échelle même quand elle ne tombe pas sur un "
      "barreau entier",
      19.0 in e["les_transitions_en_voxels"]
      and 19.5 in eb["les_transitions_en_voxels"],
      str(eb["les_transitions_en_voxels"][:6]))
    v("★★★ le pas de l'échelle est le VOXEL, la tolérance de la bissection de `179`",
      all(abs(bb - aa - 1.0) < 1e-9
          for aa, bb in zip(e["les_transitions_en_voxels"],
                            e["les_transitions_en_voxels"][1:])),
      str(e["les_transitions_en_voxels"]))
    v("★★★★ une échelle dont le plancher dépasse le plafond est REFUSÉE, jamais retournée",
      not lechelle_des_transitions(100.0, 36, 2.4)["decidable"])
    v("★★★ une borne absente ne donne AUCUNE échelle",
      not lechelle_des_transitions(None, 36, 2.4)["decidable"]
      and not lechelle_des_transitions(19.0, None, 2.4)["decidable"])

    # ⚠⚠⚠ LA COURBE PORTE LES DECALAGES MUETS A COTE DE L'ERREUR.
    lignes = une_erreur_fabriquee([10.0, 20.0, 30.0], 0.5, 0.0, 3)
    cb = la_courbe_des_transitions(lignes)
    v("★★★★ le rapport des erreurs suit celui des transitions quand la pente est droite",
      cb["decidable"]
      and abs(float(cb["le_rapport_des_erreurs"]) - 3.0) < 1e-6
      and abs(float(cb["le_rapport_des_transitions"]) - 3.0) < 1e-9,
      f"{cb.get('le_rapport_des_erreurs')} contre {cb.get('le_rapport_des_transitions')}")
    v("★★★★ chaque barreau porte son compte de décalages MUETS — sinon l'erreur ne se lit que "
      "sur les cas faciles",
      all("les_decalages_muets" in x for x in cb["les_barreaux"]))
    v("★★★ moins de trois transitions lisibles ne rendent AUCUNE courbe",
      not la_courbe_des_transitions(
          une_erreur_fabriquee([10.0, 20.0], 0.5, 0.0, 3))["decidable"])
    v("★★★ un barreau indécidable est gardé dans la liste, jamais effacé",
      len(la_courbe_des_transitions(
          lignes + [{"decidable": False, "la_transition_en_voxels": 40.0,
                     "les_decalages_muets": 12}])["les_barreaux"]) == 4)

    # ⭐ LE VRAI LECTEUR, SUR LA VRAIE MATIERE DE `179`.
    import combien_dinterstices_traverses as C  # noqa: PLC0415
    lu = lerreur_a_cette_transition(19.0, float(C.VOXEL_FIN_UM), float(C.PAS_UM), 0.0, 6, 5,
                                    permutations=7)
    # ⚠⚠⚠ L'ERREUR EST UN ECART A LA VERITE, DONC ELLE EST PETITE DEVANT LE CUBE. Une sonde qui se
    # contentait de « elle est positive » restait verte quand le code publiait la COUCHE LUE au lieu
    # de son ecart a la frontiere : un indice de couche vaut quelques dizaines, un ecart quelques
    # unites, et seul le second peut tomber sous la moitie de l'espacement des frontieres.
    # ⚠⚠⚠ LA BORNE EST CELLE QUE `179` PUBLIE, ET ELLE EST SERREE : a la transition juste
    # suffisante, son ecart median a la frontiere vaut ZERO et la largeur de son creux vaut cinq
    # couches. Un ecart a la verite tient donc dans cette largeur ; une COUCHE LUE vaut quelques
    # dizaines. Une borne large — le quart du cube — laissait passer le bris.
    largeur = brut["le_verdict"]["largeur_du_creux_a_la_borne"]
    v("★★★★ la fixture de `179` rend un ÉCART À LA VÉRITÉ, pas un indice de couche",
      lu["decidable"] and lu["les_decalages_lus"] >= 3
      and float(lu["lerreur_mediane_en_voxels"]) <= float(largeur),
      f"médiane {lu.get('lerreur_mediane_en_voxels')} pour une largeur de creux de {largeur}")
    lus_, muets_ = lu.get("les_decalages_lus"), lu.get("les_decalages_muets")
    v("★★★★ un décalage où le lecteur se TAIT est compté à part, jamais une erreur nulle",
      lus_ is not None and muets_ is not None
      and int(lus_) + int(muets_) == lu["les_decalages"],
      f"{lus_} + {muets_} pour {lu.get('les_decalages')}")
    muet = lerreur_a_cette_transition(0.0, float(C.VOXEL_FIN_UM), float(C.PAS_UM), 0.0, 4, 5,
                                      permutations=7)
    v("★★★★ une transition NULLE — le rasoir de `179` — ne rend AUCUNE erreur",
      not muet["decidable"] and muet.get("les_decalages_muets", 0) >= 1,
      str(muet.get("raison")))

    # ⚠⚠⚠ L'EPREUVE EST CELLE DE `202`, IMPORTEE ET NON REECRITE.
    # ⚠⚠ L'EPREUVE A BESOIN D'ASSEZ DE BARREAUX : sur trois points, une permutation tiree au
    # hasard laisse |r| = 1 une fois sur trois — le retournement donne la meme correlation absolue —
    # donc la valeur p ne peut pas descendre sous la garantie, quelle que soit la matiere.
    cbn = la_courbe_des_transitions(
        une_erreur_fabriquee([float(x) for x in range(10, 30)], 0.5, 1.0, 13))
    ep = lappariement(cbn["les_transitions"], cbn["les_erreurs"], PERMUTATIONS, 5,
                      GARANTIE_PAR_EPREUVE)
    v("★★★★ une erreur qui suit la transition est VUE appariée",
      ep["decidable"] and ep["les_deux_pas_sont_apparies"],
      str(ep.get("la_correlation_absolue")))
    plates = une_erreur_fabriquee([float(x) for x in range(10, 30)], 0.0, 1.0, 9)
    cbp = la_courbe_des_transitions(plates)
    epp = lappariement(cbp["les_transitions"], cbp["les_erreurs"], PERMUTATIONS, 6,
                       GARANTIE_PAR_EPREUVE)
    v("★★★★ une erreur qui ne suit RIEN n'est pas appariée",
      not epp["les_deux_pas_sont_apparies"], str(epp.get("la_valeur_p")))
    v("★★★★ la fixture ne change QUE la pente : même bruit des deux côtés",
      abs((une_erreur_fabriquee([10.0], 0.5, 1.0, 1)[0]["lerreur_quadratique_en_voxels"]
           - 0.5 * 10.0)
          - une_erreur_fabriquee([10.0], 0.0, 1.0, 1)[0]["lerreur_quadratique_en_voxels"])
      < 1e-9)

    # ⚠⚠ LE VERDICT COMPARE LE BARREAU DU ROULEAU, ET LUI SEUL.
    lignes_r = une_erreur_fabriquee([9.5, 19.0, 36.0], 0.8, 0.0, 4)
    cbr = la_courbe_des_transitions(lignes_r)
    epr = lappariement(cbr["les_transitions"], cbr["les_erreurs"], PERMUTATIONS, 7,
                       GARANTIE_PAR_EPREUVE)
    jug = juger(cbr, epr, {"la_transition_du_rouleau_en_voxels": 19.0},
                {"le_bruit_de_chunk_en_voxels": 14.9372},
                {"lespacement_des_frontieres_en_couches": 36,
                 "le_plus_grand_bruit_tenu": 16.0})
    v("★★★★ le verdict lit le barreau À LA TRANSITION DU ROULEAU, pas la courbe entière",
      jug["decidable"]
      and abs(float(jug["lerreur_a_la_transition_du_rouleau_en_voxels"]) - 0.8 * 19.0) < 1e-6,
      str(jug.get("lerreur_a_la_transition_du_rouleau_en_voxels")))
    v("★★★ il porte le rapport à l'erreur de chunk de `205`, relue et jamais recalculée",
      abs(float(jug["le_rapport_a_lerreur_de_chunk"])
          - round(0.8 * 19.0 / 14.9372, 4)) < 1e-3)
    v("★★★★ il dit si l'erreur croît AUSSI VITE que la transition",
      abs(float(jug["lerreur_croit_elle_aussi_vite"]) - 1.0) < 1e-3,
      str(jug.get("lerreur_croit_elle_aussi_vite")))
    v("★★★ une épreuve indécidable ne rend AUCUN verdict",
      not juger(cbr, {"decidable": False}, {}, {}, {})["decidable"])

    # ⭐ L'ETALON, EN PETIT.
    et = sur_letalon([float(x) for x in range(10, 30)], 0.5, 1.0, GRAINE, replicats=3,
                     tirages=PERMUTATIONS)
    v("★★★★ l'étalon voit une erreur qui suit la transition",
      et["la_part_trouvee"] >= 0.99, str(et.get("la_part_trouvee")))
    v("★★★★ la face négative a DEUX fois le compte que la garantie exige — la leçon de `202`",
      et["les_replicats_du_refus"] == int(2.0 / GARANTIE_PAR_EPREUVE))
    v("★★★★ sur une erreur qui ne suit rien, le taux de faux tient la garantie",
      et["le_taux_de_faux"] <= GARANTIE_PAR_EPREUVE * 2.0 + 1e-12,
      f"{et.get('les_faux')} faux sur {et.get('les_replicats_du_refus')}")
    v("★★★ l'étalon sépare ses deux faces, et il le DIT", et["letalon_separe"] is True)
    v("★★★★ le rapport est publié sur les DEUX faces, et la pentue monte PLUS",
      et["le_rapport_median_sur_la_face_positive"]
      > et["le_rapport_median_sur_la_face_negative"],
      f"{et.get('le_rapport_median_sur_la_face_positive')} contre "
      f"{et.get('le_rapport_median_sur_la_face_negative')}")

    for e_ in echecs:
        print(f"  ÉCHEC {e_}")
    print(f"{Path(__file__).name}   "
          f"{'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--verifier", action="store_true")
    ap.add_argument("--json", type=Path, default=None)
    ap.add_argument("--graine", type=int, default=GRAINE)
    ap.add_argument("--replicats", type=int, default=12)
    ap.add_argument("--decalages", type=int, default=12)
    a = ap.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(DELAI, a.graine, a.replicats, a.decalages)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
