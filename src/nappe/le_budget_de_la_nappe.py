"""Jusqu'où une nappe tient-elle ? Les deux budgets, et celui qui lie.

⭐⭐⭐⭐ POURQUOI CE FICHIER. `151` a monté le pipeline complet à partir de cent cinquante documents,
et son maillon ouvert était la MARCHE — une pince qui avance dans le volume. Les tranches `198` à
`211` ont construit tout autre chose : un CHAMP DE PAS sur le treillis des chunks, qu'on intègre en
une surface. Cette voie-là a maintenant son arithmétique complète, et personne ne l'avait écrite en
un seul endroit.

⭐⭐⭐⭐ L'ÉQUATION DE CONCEPTION TIENT EN UNE LIGNE, ET ELLE N'EXISTAIT PAS À `151`. Une marche de
`n` coutures dont le pas a une dispersion `sigma` s'éloigne de son départ d'environ `sigma` fois la
racine de `n` — c'est la convention publiée de `207`, et rien ici ne la change. Elle quitte le
feuillet quand cet écart atteint le demi-feuillet, donc la LONGUEUR TENABLE vaut le carré du rapport
du demi-feuillet à la dispersion. Un seul nombre par budget, et il se compare directement à la
largeur d'une rangée.

⭐⭐⭐⭐ ET IL Y A DEUX BUDGETS, PAS UN — C'EST `R4-L16`. Moyenner `k` rangées ne divise que la part
PROPRE du bruit ; différencier deux rangées annule la part PARTAGÉE tout entière. Traverser et
s'accorder ne consomment donc pas la même quantité, et le pipeline est lié par le plus petit des
deux. `151` ne pouvait pas poser cette question : il n'avait qu'une marche.

⚠⚠⚠ CETTE TRANCHE NE TIRE AUCUN ÉCHANTILLON. Elle relit des mesures publiées et en tire des
conséquences arithmétiques, donc elle ne déclare AUCUNE épreuve et ne consomme AUCUNE part de la
garantie. Ce qui la rend falsifiable est ailleurs, et c'est le TRIANGLE : trois paires de rangées
donnent trois désaccords, et le modèle « chaque rangée porte un bruit qui lui est propre » impose
que les trois variances propres qu'on en tire soient POSITIVES. Une seule négative le réfute.

Usage :
    uv run python src/nappe/le_budget_de_la_nappe.py --verifier
    uv run python src/nappe/le_budget_de_la_nappe.py \\
        --json docs/mesures/le_budget_de_la_nappe.json
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

from que_montrent_ces_deux_vues import (DEMI_PAS_EN_VOXELS,  # noqa: E402
                                        PAS_EN_VOXELS)

MESURES = RACINE / "docs" / "mesures"
CE_QUE_LA_MOYENNE_A_RENDU = MESURES / "la_moyenne_des_rangees_traverse_t_elle.json"
CE_QUE_LACCORD_A_RENDU = MESURES / "les_rangees_saccordent_elles_entre_elles.json"

LA_QUESTION_DECLAREE = ("jusqu'où une nappe tient-elle dans son feuillet, et lequel des deux "
                        "budgets — traverser ou s'accorder — la lie en premier ?")
LES_EPREUVES_DECLAREES: tuple[str, ...] = ()


def ce_que_la_moyenne_a_rendu(chemin: Path = CE_QUE_LA_MOYENNE_A_RENDU) -> dict:
    """Les dispersions de `204` et de `210` — relues chez leur producteur, jamais retapées.

    ⚠⚠⚠ TROIS DISPERSIONS DE TRAVERSEE, ET ELLES DISENT TROIS CHOSES DIFFERENTES : celle du pas
    MOYENNE sur `k` rangees est ce que le pipeline d'aujourd'hui atteint, celle d'UNE rangee est ce
    qu'il atteindrait sans le treillis, et la DERIVE seule est le plancher que la matiere impose a
    un lecteur PARFAIT. Publier la premiere sans la troisieme laisserait croire qu'un meilleur
    instrument leverait la borne.
    """
    if not Path(chemin).is_file():
        return {"decidable": False, "raison": "la mesure de `210` est absente"}
    d = json.loads(Path(chemin).read_text(encoding="utf-8"))
    q = d.get("ce_que_la_moyenne_a_retire") or {}
    p204 = d.get("ce_que_204_a_rendu") or {}
    if not q.get("decidable") or q.get("la_dispersion_du_pas_moyenne_en_voxels") is None:
        return {"decidable": False, "raison": "`210` ne publie pas de dispersion du pas moyenné"}
    if not p204.get("decidable") or p204.get("la_dispersion_en_voxels") is None:
        return {"decidable": False, "raison": "`204` ne publie pas de dispersion du pas"}
    return {"decidable": True,
            "la_dispersion_du_pas_moyenne_en_voxels": q.get(
                "la_dispersion_du_pas_moyenne_en_voxels"),
            "les_rangees_moyennees": q.get("les_rangees_moyennees"),
            "les_coutures_de_210": q.get("les_coutures"),
            "la_dispersion_dune_rangee_en_voxels": p204.get("la_dispersion_en_voxels"),
            "la_derive_en_voxels": p204.get("la_derive_en_voxels"),
            "les_rangees_de_204": p204.get("les_rangees")}


def ce_que_laccord_a_rendu(chemin: Path = CE_QUE_LACCORD_A_RENDU) -> dict:
    """Les trois désaccords par couture de `211` — un par paire de rangées.

    ⚠⚠ LES TROIS SONT LUES ET PAS SEULEMENT CELLE DE L'EPREUVE : le triangle a besoin des trois
    pour exister, et c'est lui qui rend cette tranche refutable. Une seule paire ne peut pas dire
    si le modele tient.
    """
    if not Path(chemin).is_file():
        return {"decidable": False, "raison": "la mesure de `211` est absente"}
    d = json.loads(Path(chemin).read_text(encoding="utf-8"))
    vld = d.get("ce_que_les_desaccords_valent") or {}
    paires = {}
    for cle, x in vld.items():
        if x.get("decidable") and x.get("le_desaccord_par_couture_mesure_en_voxels") is not None:
            paires[str(cle)] = {
                "le_desaccord_par_couture_en_voxels": x[
                    "le_desaccord_par_couture_mesure_en_voxels"],
                "lerreur_dechantillonnage_en_voxels": x.get(
                    "lerreur_dechantillonnage_en_voxels"),
                "les_coutures_communes": x.get("les_coutures_communes")}
    if len(paires) < 3:
        return {"decidable": False, "raison": "`211` ne publie pas trois paires décidables"}
    p208 = d.get("ce_que_208_a_rendu") or {}
    lignes = d.get("les_lignes") or {}
    une = next(iter(lignes.values()), {})
    return {"decidable": True, "les_paires": paires,
            "la_paire_declaree": d.get("la_paire_declaree"),
            "les_rangees": (d.get("les_rangees_du_treillis") or {}).get("les_rangees"),
            "le_bruit_de_la_mediane_selon_208_en_voxels": p208.get(
                "le_bruit_de_la_mediane_en_voxels"),
            "le_bruit_de_la_voisine_selon_208_en_voxels": p208.get(
                "le_bruit_de_la_voisine_en_voxels"),
            "les_colonnes_demandees": une.get("colonnes_demandees")}


def la_longueur_tenable(dispersion, demi: float = DEMI_PAS_EN_VOXELS,
                        periode: float = PAS_EN_VOXELS) -> dict:
    """⭐⭐⭐⭐ L'ÉQUATION DE CONCEPTION : combien de coutures avant de quitter le feuillet.

    ⭐⭐⭐⭐ ELLE EST L'INVERSE EXACTE DE LA CONVENTION DE `207`, ET RIEN D'AUTRE. `207` publie
    l'ecart attendu d'une marche de `n` coutures comme la dispersion fois la racine de `n` ; poser
    cet ecart egal au demi-feuillet et resoudre en `n` rend le carre du rapport. Aucune constante
    n'entre, aucun seuil n'est choisi : le demi-feuillet n'est pas un reglage mais la distance a
    laquelle la surface saute au feuillet voisin.

    ⚠⚠ CE N'EST PAS UNE PROMESSE SUR UNE COURSE, C'EST UNE ECHELLE. Une excursion est une seule
    realisation, tres variable — `207` l'a paye. La longueur tenable dit ou l'ECART ATTENDU croise
    le demi-feuillet, donc environ la moitie des courses de cette longueur sortent deja.
    """
    if dispersion is None or float(dispersion) <= 0.0:
        return {"decidable": False, "raison": "la dispersion est absente ou nulle"}
    s = float(dispersion)
    n = (float(demi) / s) ** 2
    return {"decidable": True,
            "la_dispersion_en_voxels": round(s, 4),
            "le_demi_pli_en_voxels": int(demi),
            "la_longueur_tenable_en_coutures": round(float(n), 2),
            "lecart_attendu_a_cette_longueur_en_voxels": round(float(s * np.sqrt(n)), 4),
            "la_longueur_tenable_en_plis": round(float(n * s * s / (periode * periode)), 6)}


def le_triangle_des_bruits_propres(paires: dict) -> dict:
    """⭐⭐⭐⭐ Les trois variances propres, tirées des trois désaccords — et le modèle s'y réfute.

    ⭐⭐⭐⭐ C'EST CE QUI REND CETTE TRANCHE FALSIFIABLE SANS TIRER UN SEUL ECHANTILLON. Le modele
    de `208` dit qu'une rangee porte un bruit qui lui est PROPRE, et que le desaccord de deux
    rangees est la racine de la somme de leurs carres. Trois rangees donnent trois equations pour
    trois inconnues, donc le systeme est EXACTEMENT determine — et rien ne garantit que sa solution
    soit faite de variances POSITIVES. Une seule negative refute le modele, exactement comme la
    variance commune negative refutait celui de `208`.

    ⚠⚠ ET CE N'EST PAS UNE VERIFICATION VIDE : les trois desaccords mesures sont 2,7138, 2,9794 et
    3,4004, et il suffirait que le plus grand depasse la racine de la somme des carres des deux
    autres pour qu'une variance sorte negative. Le triangle est donc une vraie inegalite sur la
    matiere, pas une identite algebrique.
    """
    cles = sorted(paires)
    if len(cles) != 3:
        return {"decidable": False, "raison": "le triangle demande exactement trois paires"}
    rangees = set()
    for cle in cles:
        morceaux = str(cle).split("-")
        if len(morceaux) != 2:
            return {"decidable": False, "raison": f"la paire « {cle} » n'a pas deux rangées"}
        rangees.update(int(x) for x in morceaux)
    if len(rangees) != 3:
        return {"decidable": False,
                "raison": f"les trois paires portent {len(rangees)} rangées et non trois"}
    v = {}
    for cle in cles:
        a, b = (int(x) for x in str(cle).split("-"))
        s = float(paires[cle]["le_desaccord_par_couture_en_voxels"])
        v[frozenset((a, b))] = s * s
    if len(v) != 3:
        return {"decidable": False, "raison": "deux paires nomment les mêmes rangées"}
    out, negative = {}, []
    for r in sorted(rangees):
        autres = [x for x in sorted(rangees) if x != r]
        # sigma_r^2 = (V(r,a) + V(r,b) - V(a,b)) / 2
        var = (v[frozenset((r, autres[0]))] + v[frozenset((r, autres[1]))]
               - v[frozenset((autres[0], autres[1]))]) / 2.0
        if var < 0.0:
            negative.append(int(r))
        out[str(int(r))] = {
            "la_variance_propre_en_voxels_carres": round(float(var), 4),
            "le_bruit_propre_en_voxels": (None if var < 0.0
                                          else round(float(np.sqrt(var)), 4))}
    return {"decidable": True,
            "les_rangees": sorted(int(x) for x in rangees),
            "les_bruits_propres": out,
            "les_variances_negatives": negative,
            "le_modele_se_refute": bool(negative),
            "le_modele_tient": not bool(negative)}


def ce_que_le_triangle_dit_de_208(triangle: dict, lu: dict) -> dict:
    """Le bruit propre tiré du triangle, contre celui que `208` avait tiré d'une seule paire.

    ⚠⚠⚠ LES DEUX ESTIMATEURS NE LISENT PAS LA MEME CHOSE, ET C'EST POURQUOI L'ECART EST PUBLIE.
    `208` decompose UNE paire en une derive partagee et deux bruits propres, donc il doit supposer
    quelque chose pour separer trois quantites a partir de deux variances et d'une covariance. Le
    triangle n'utilise QUE des differences, donc il est aveugle a la derive partagee et n'a rien a
    supposer. Les deux doivent s'accorder si le modele tient ; l'ecart mesure dit de combien il ne
    tient qu'approximativement, et le taire serait affirmer un accord qui n'a pas ete verifie.
    """
    if not triangle.get("decidable"):
        return {"decidable": False, "raison": "le triangle est indécidable"}
    paire = lu.get("la_paire_declaree") or []
    if len(paire) != 2:
        return {"decidable": False, "raison": "`211` ne nomme pas sa paire déclarée"}
    selon_208 = {str(int(paire[0])): lu.get("le_bruit_de_la_mediane_selon_208_en_voxels"),
                 str(int(paire[1])): lu.get("le_bruit_de_la_voisine_selon_208_en_voxels")}
    out = {}
    for r, x in selon_208.items():
        tri = ((triangle["les_bruits_propres"].get(r) or {})
               .get("le_bruit_propre_en_voxels"))
        if x is None or tri is None:
            continue
        out[r] = {"selon_208_en_voxels": float(x),
                  "selon_le_triangle_en_voxels": float(tri),
                  "le_rapport": round(float(tri) / float(x), 4),
                  "lecart_en_voxels": round(float(tri) - float(x), 4)}
    if not out:
        return {"decidable": False, "raison": "aucune rangée n'est comparable"}
    return {"decidable": True, "les_rangees_comparees": out,
            "le_plus_grand_ecart_en_voxels": round(
                max(abs(x["lecart_en_voxels"]) for x in out.values()), 4)}


def les_deux_budgets(par_210: dict, par_211: dict, demi: float = DEMI_PAS_EN_VOXELS) -> dict:
    """⭐⭐⭐⭐ Les deux budgets côte à côte, et celui qui lie.

    ⭐⭐⭐⭐ C'EST LA QUESTION QUE `151` NE POUVAIT PAS POSER. Son pipeline n'avait qu'une marche,
    donc une seule longueur tenable. Depuis `R4-L16` il y en a deux, elles ne se deduisent pas l'une
    de l'autre, et le pipeline est lie par la PLUS PETITE — donc ameliorer celle qui ne lie pas
    n'achete rien du tout.

    ⚠⚠ LES TROIS PAIRES SONT BUDGETEES, PAS SEULEMENT CELLE DE L'EPREUVE : la plus mauvaise est
    celle qui lie une nappe, puisqu'il suffit d'une couture pour perdre le feuillet.
    """
    if not par_210.get("decidable") or not par_211.get("decidable"):
        return {"decidable": False, "raison": "une des deux mesures manque"}
    traverser = {}
    for nom, cle in (("la_moyenne_des_rangees", "la_dispersion_du_pas_moyenne_en_voxels"),
                     ("une_rangee_seule", "la_dispersion_dune_rangee_en_voxels"),
                     ("le_plancher_de_la_matiere", "la_derive_en_voxels")):
        traverser[nom] = la_longueur_tenable(par_210.get(cle), demi)
    saccorder = {}
    for cle, x in sorted(par_211["les_paires"].items()):
        saccorder[str(cle)] = la_longueur_tenable(
            x.get("le_desaccord_par_couture_en_voxels"), demi)
    atteint = traverser["la_moyenne_des_rangees"]
    pires = [(c, y["la_longueur_tenable_en_coutures"]) for c, y in saccorder.items()
             if y.get("decidable")]
    if not atteint.get("decidable") or not pires:
        return {"decidable": False, "raison": "un des deux budgets est indécidable"}
    pire_cle, pire_n = min(pires, key=lambda t: t[1])
    n_traverser = float(atteint["la_longueur_tenable_en_coutures"])
    lie = "s'accorder" if pire_n < n_traverser else "traverser"
    return {"decidable": True,
            "traverser": traverser,
            "saccorder": saccorder,
            "la_longueur_tenable_en_traversant_en_coutures": round(n_traverser, 2),
            "la_pire_paire": pire_cle,
            "la_longueur_tenable_en_saccordant_en_coutures": round(float(pire_n), 2),
            "le_budget_qui_lie": lie,
            "le_rapport_des_deux_budgets": round(float(pire_n) / n_traverser, 4),
            "ce_que_le_budget_liant_coute_en_coutures": round(
                float(n_traverser - pire_n), 2)}


def ce_que_la_rangee_demande(budgets: dict, colonnes) -> dict:
    """La largeur d'une rangée entière, et la part que chaque budget en couvre.

    ⚠⚠⚠ UNE RANGEE DE `c` COLONNES PORTE `c - 1` COUTURES, ET PAS `c`. Une couture est un
    INTERVALLE entre deux chunks voisins, donc le compte est celui des intervalles. Confondre les
    deux gonflerait la cible d'une couture et ferait croire le budget plus court qu'il n'est —
    l'erreur est petite et elle est du genre qui ne se voit jamais.
    """
    if not budgets.get("decidable") or colonnes is None or int(colonnes) < 2:
        return {"decidable": False, "raison": "les budgets ou la largeur manquent"}
    cibles = int(colonnes) - 1
    n_t = float(budgets["la_longueur_tenable_en_traversant_en_coutures"])
    n_a = float(budgets["la_longueur_tenable_en_saccordant_en_coutures"])
    return {"decidable": True,
            "les_colonnes_dune_rangee": int(colonnes),
            "les_coutures_dune_rangee": int(cibles),
            "la_part_couverte_en_traversant": round(n_t / float(cibles), 4),
            "la_part_couverte_en_saccordant": round(n_a / float(cibles), 4),
            "une_rangee_entiere_traverse": bool(n_t >= float(cibles)),
            "une_rangee_entiere_saccorde": bool(n_a >= float(cibles)),
            "les_coutures_qui_manquent_pour_saccorder": round(
                float(cibles) - n_a, 2)}


def la_nappe_entiere(triangle: dict, budgets: dict) -> dict:
    """⭐⭐⭐⭐ Combien de rangées une nappe peut porter — et la réponse est qu'elles sont gratuites.

    ⭐⭐⭐⭐ LE RESULTAT EST CONTRE-INTUITIF ET IL SORT DU MODELE, PAS D'UNE MESURE. Si chaque rangee
    porte un bruit qui lui est propre et INDEPENDANT de celui des autres, alors le desaccord entre
    la premiere et la derniere rangee d'une bande ne fait intervenir QUE ces deux-la : c'est la
    difference de leurs deux marches propres, et les rangees du milieu n'y entrent pas. Le desaccord
    d'une nappe de trois cent quatre-vingt-seize rangees vaut donc celui d'une paire, et la hauteur
    est GRATUITE.

    ⚠⚠⚠ ET C'EST EXACTEMENT LA OU LE MODELE DOIT ETRE MIS A L'EPREUVE, PARCE QUE LA CONCLUSION EST
    TROP BELLE. Rien n'a mesure le desaccord de deux rangees ELOIGNEES : les trois paires de `211`
    sont toutes voisines ou a deux rangees d'ecart. Si le bruit propre croit avec la distance entre
    rangees — ce qu'une matiere reelle fait volontiers — la hauteur cesse d'etre gratuite, et le
    modele ne le verrait pas. La seule chose que le triangle prouve est que le modele TIENT sur les
    trois rangees mesurees.
    """
    if not triangle.get("decidable") or not budgets.get("decidable"):
        return {"decidable": False, "raison": "le triangle ou les budgets manquent"}
    return {"decidable": True,
            "le_modele_tient_sur_les_rangees_mesurees": bool(triangle["le_modele_tient"]),
            "les_rangees_du_triangle": triangle.get("les_rangees"),
            "la_hauteur_est_gratuite_sous_le_modele": bool(triangle["le_modele_tient"]),
            "la_longueur_tenable_dune_nappe_en_coutures": budgets.get(
                "la_longueur_tenable_en_saccordant_en_coutures"),
            # ⚠⚠ LA CHOSE ET SA RAISON SONT DEUX CHAMPS, PAS UN : une figure a besoin de la
            # chose seule pour tenir sur une ligne, un document a besoin de la raison. Les
            # coudre ensemble obligeait la figure à couper la phrase de la mesure, ce qui est
            # exactement la faute d'un lecteur qui réécrit ce qu'il lit.
            "ce_qui_reste_a_mesurer": "le désaccord de deux rangées ÉLOIGNÉES",
            "pourquoi_il_reste_a_mesurer": ("les trois paires mesurées sont voisines, donc rien "
                                            "ne dit que le bruit propre ne croît pas avec la "
                                            "distance entre rangées")}


def juger(budgets: dict, rangee: dict, triangle: dict, nappe: dict) -> dict:
    """Lequel des deux budgets lie, de combien, et le modèle tient-il.

    ⚠ Tout se lit par `.get()` et la presence est testee avant la valeur : une batterie qui meurt
    avant son verdict ne dit rien.
    """
    if not budgets.get("decidable") or not triangle.get("decidable"):
        return {"decidable": False, "raison": "les budgets ou le triangle manquent"}
    return {"decidable": True,
            "le_budget_qui_lie": budgets.get("le_budget_qui_lie"),
            "la_longueur_tenable_en_traversant_en_coutures": budgets.get(
                "la_longueur_tenable_en_traversant_en_coutures"),
            "la_longueur_tenable_en_saccordant_en_coutures": budgets.get(
                "la_longueur_tenable_en_saccordant_en_coutures"),
            "la_pire_paire": budgets.get("la_pire_paire"),
            "le_rapport_des_deux_budgets": budgets.get("le_rapport_des_deux_budgets"),
            "ce_que_le_budget_liant_coute_en_coutures": budgets.get(
                "ce_que_le_budget_liant_coute_en_coutures"),
            "les_coutures_dune_rangee": (rangee or {}).get("les_coutures_dune_rangee"),
            "la_part_couverte_en_traversant": (rangee or {}).get(
                "la_part_couverte_en_traversant"),
            "la_part_couverte_en_saccordant": (rangee or {}).get(
                "la_part_couverte_en_saccordant"),
            "une_rangee_entiere_traverse": (rangee or {}).get("une_rangee_entiere_traverse"),
            "une_rangee_entiere_saccorde": (rangee or {}).get("une_rangee_entiere_saccorde"),
            "les_coutures_qui_manquent_pour_saccorder": (rangee or {}).get(
                "les_coutures_qui_manquent_pour_saccorder"),
            "le_modele_tient": triangle.get("le_modele_tient"),
            "les_variances_negatives": triangle.get("les_variances_negatives"),
            "la_hauteur_est_gratuite_sous_le_modele": (nappe or {}).get(
                "la_hauteur_est_gratuite_sous_le_modele")}


def mesurer(demi: float = DEMI_PAS_EN_VOXELS,
            lecteur_210=None, lecteur_211=None) -> dict:
    """Les deux budgets, le triangle, et ce qu'une rangée entière demande."""
    par_210 = (lecteur_210 or ce_que_la_moyenne_a_rendu)()
    par_211 = (lecteur_211 or ce_que_laccord_a_rendu)()
    if not par_210.get("decidable"):
        return {"decidable": False, "raison": par_210.get("raison")}
    if not par_211.get("decidable"):
        return {"decidable": False, "raison": par_211.get("raison")}
    triangle = le_triangle_des_bruits_propres(par_211["les_paires"])
    contre_208 = ce_que_le_triangle_dit_de_208(triangle, par_211)
    budgets = les_deux_budgets(par_210, par_211, demi)
    rangee = ce_que_la_rangee_demande(budgets, par_211.get("les_colonnes_demandees"))
    nappe = la_nappe_entiere(triangle, budgets)
    return {
        "la_question_declaree": LA_QUESTION_DECLAREE,
        "les_epreuves_declarees": list(LES_EPREUVES_DECLAREES),
        "le_pas_dun_pli_en_voxels": round(float(PAS_EN_VOXELS), 4),
        "le_demi_pli_en_voxels": int(demi),
        "ce_que_210_a_rendu": par_210,
        "ce_que_211_a_rendu": par_211,
        "le_triangle": triangle,
        "le_triangle_contre_208": contre_208,
        "les_budgets": budgets,
        "ce_quune_rangee_demande": rangee,
        "la_nappe_entiere": nappe,
        "le_verdict": juger(budgets, rangee, triangle, nappe),
    }


def afficher(r: dict) -> None:
    if not r.get("decidable", True) and "raison" in r:
        print(f"INDÉCIDABLE : {r['raison']}")
        return
    b = r.get("les_budgets") or {}
    print(f"LE BUDGET DE LA NAPPE   demi-feuillet {r.get('le_demi_pli_en_voxels')} voxels · "
          f"pli {r.get('le_pas_dun_pli_en_voxels')}")
    for nom, x in (b.get("traverser") or {}).items():
        if x.get("decidable"):
            print(f"  TRAVERSER {nom:<26} {x['la_dispersion_en_voxels']:>7} vx/couture → "
                  f"{x['la_longueur_tenable_en_coutures']:>7} coutures")
    for nom, x in (b.get("saccorder") or {}).items():
        if x.get("decidable"):
            print(f"  S'ACCORDER {nom:<25} {x['la_dispersion_en_voxels']:>7} vx/couture → "
                  f"{x['la_longueur_tenable_en_coutures']:>7} coutures")
    t = r.get("le_triangle") or {}
    if t.get("decidable"):
        print("  LE TRIANGLE       " + " · ".join(
            f"{k}→{(x or {}).get('le_bruit_propre_en_voxels')}"
            for k, x in (t.get("les_bruits_propres") or {}).items())
            + f" · le modèle tient {t['le_modele_tient']}")
    c = r.get("le_triangle_contre_208") or {}
    if c.get("decidable"):
        print("  CONTRE `208`      " + " · ".join(
            f"{k} {x['selon_le_triangle_en_voxels']} pour {x['selon_208_en_voxels']} "
            f"(×{x['le_rapport']})" for k, x in c["les_rangees_comparees"].items()))
    q = r.get("ce_quune_rangee_demande") or {}
    if q.get("decidable"):
        print(f"  UNE RANGÉE        {q['les_coutures_dune_rangee']} coutures · couverte en "
              f"traversant {q['la_part_couverte_en_traversant']} · en s'accordant "
              f"{q['la_part_couverte_en_saccordant']} · il manque "
              f"{q['les_coutures_qui_manquent_pour_saccorder']} coutures")
    v = r.get("le_verdict") or {}
    if v.get("decidable"):
        print(f"  LE VERDICT        le budget qui lie est « {v['le_budget_qui_lie']} » : "
              f"{v['la_longueur_tenable_en_saccordant_en_coutures']} coutures contre "
              f"{v['la_longueur_tenable_en_traversant_en_coutures']} en traversant, soit un "
              f"rapport de {v['le_rapport_des_deux_budgets']}")
        print(f"                    la pire paire est {v['la_pire_paire']} · une rangée entière "
              f"traverse {v['une_rangee_entiere_traverse']} · s'accorde "
              f"{v['une_rangee_entiere_saccorde']}")
    n = r.get("la_nappe_entiere") or {}
    if n.get("decidable"):
        print(f"  LA NAPPE          la hauteur est gratuite sous le modèle "
              f"{n['la_hauteur_est_gratuite_sous_le_modele']} · reste à mesurer : "
              f"{n['ce_qui_reste_a_mesurer']}")


def verifier() -> int:
    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        if not ok:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    v("★★ une question est déclarée", isinstance(LA_QUESTION_DECLAREE, str))
    # ⚠⚠⚠ AUCUNE EPREUVE N'EST DECLAREE, ET C'EST UN FAIT SUR LA TRANCHE : elle ne tire aucun
    # echantillon, donc elle ne consomme aucune part de la garantie. Une tranche qui declarerait
    # une epreuve sans tirer paierait un prix pour rien et laisserait croire qu'elle a teste.
    v("★★★★ aucune épreuve n'est déclarée, parce qu'aucun échantillon n'est tiré",
      len(LES_EPREUVES_DECLAREES) == 0)

    # ⭐⭐⭐⭐ L'EQUATION DE CONCEPTION EST L'INVERSE EXACTE DE LA CONVENTION DE `207`, et la sonde
    # le verifie DANS LES DEUX SENS : a la longueur rendue, l'ecart attendu doit valoir le
    # demi-feuillet. Un bris qui oublierait le carre rendrait une longueur plausible et un ecart
    # faux, donc asserter la seule longueur aurait ete satisfait par lui.
    t = la_longueur_tenable(2.0, 36.0)
    v("★★★★ la longueur tenable est le CARRÉ du rapport du demi-feuillet à la dispersion",
      t["decidable"] and abs(t["la_longueur_tenable_en_coutures"] - 324.0) < 1e-9,
      str(t.get("la_longueur_tenable_en_coutures")))
    v("★★★★ et à cette longueur, l'écart attendu vaut EXACTEMENT le demi-feuillet",
      abs(t["lecart_attendu_a_cette_longueur_en_voxels"] - 36.0) < 1e-6,
      str(t.get("lecart_attendu_a_cette_longueur_en_voxels")))
    v("★★★★ doubler la dispersion divise la longueur tenable par QUATRE, pas par deux",
      abs(la_longueur_tenable(4.0, 36.0)["la_longueur_tenable_en_coutures"] - 81.0) < 1e-9,
      str(la_longueur_tenable(4.0, 36.0)["la_longueur_tenable_en_coutures"]))
    v("★★★ un demi-feuillet plus grand allonge la longueur tenable",
      la_longueur_tenable(2.0, 72.0)["la_longueur_tenable_en_coutures"]
      > t["la_longueur_tenable_en_coutures"])
    # ⚠⚠⚠ LES TROIS REFUS SONT GARDES : un bris qui leve la borne sur la dispersion fait DIVISER
    # PAR ZERO, donc la batterie MEURT au lieu de rougir et le bris passe pour une panne de sonde.
    # Une exception est comptee comme un controle EN ECHEC, et nommee.
    for valeur, quoi in ((0.0, "nulle"), (None, "absente"), (-1.0, "négative")):
        try:
            refus = not la_longueur_tenable(valeur, 36.0)["decidable"]
            pourquoi = ""
        except Exception as e:  # noqa: BLE001
            refus, pourquoi = False, f"la batterie est MORTE : {type(e).__name__}"
        v(f"★★★ une dispersion {quoi} ne rend AUCUNE longueur", refus, pourquoi)

    # ⭐⭐⭐⭐ LE TRIANGLE SE RESOUT EXACTEMENT, ET LA FIXTURE EST BATIE POUR QUE LES TROIS BRUITS
    # PROPRES DIFFERENT : avec trois bruits egaux, toute erreur de signe dans la resolution
    # rendrait encore la bonne valeur, et la sonde serait satisfaite par un code faux.
    b1, b2, b3 = 1.0, 2.0, 3.0
    faux_paires = {}
    for (ra, rb, sa, sb) in ((10, 20, b1, b2), (10, 30, b1, b3), (20, 30, b2, b3)):
        faux_paires[f"{ra}-{rb}"] = {
            "le_desaccord_par_couture_en_voxels": float(np.sqrt(sa * sa + sb * sb))}
    tri = le_triangle_des_bruits_propres(faux_paires)
    v("★★★★ le triangle retrouve EXACTEMENT les trois bruits propres qui l'ont fabriqué",
      tri["decidable"]
      and abs(tri["les_bruits_propres"]["10"]["le_bruit_propre_en_voxels"] - b1) < 1e-9
      and abs(tri["les_bruits_propres"]["20"]["le_bruit_propre_en_voxels"] - b2) < 1e-9
      and abs(tri["les_bruits_propres"]["30"]["le_bruit_propre_en_voxels"] - b3) < 1e-9,
      str(tri.get("les_bruits_propres")))
    v("★★★★ et il déclare que le modèle TIENT quand les trois variances sont positives",
      tri["le_modele_tient"] is True and tri["les_variances_negatives"] == [])
    # ⚠⚠⚠ ET LE TRIANGLE DOIT POUVOIR REFUTER, sinon il ne prouve rien : une paire dont le
    # desaccord depasse la racine de la somme des carres des deux autres rend une variance
    # NEGATIVE. C'est une inegalite sur la matiere, pas une identite algebrique.
    casse = dict(faux_paires)
    casse["20-30"] = {"le_desaccord_par_couture_en_voxels": 99.0}
    tri_casse = le_triangle_des_bruits_propres(casse)
    v("★★★★ un désaccord trop grand rend une variance NÉGATIVE et RÉFUTE le modèle",
      tri_casse["decidable"] and tri_casse["le_modele_se_refute"]
      and tri_casse["les_variances_negatives"], str(tri_casse.get("les_variances_negatives")))
    v("★★★★ et la rangée réfutée ne publie AUCUN bruit propre plutôt qu'une racine de négatif",
      tri_casse["les_bruits_propres"]["10"]["le_bruit_propre_en_voxels"] is None,
      str(tri_casse["les_bruits_propres"]["10"]))
    v("★★★ deux paires seulement ne rendent AUCUN triangle",
      not le_triangle_des_bruits_propres(
          {k: faux_paires[k] for k in ("10-20", "10-30")})["decidable"])
    # ⚠⚠⚠ ET UNE QUATRIEME PAIRE AUSSI, MEME SI ELLE NOMME LES MEMES TROIS RANGEES. Les paires
    # sont rangees par ensemble non ordonne, donc « 20-10 » ecrase « 10-20 » sans bruit et le
    # triangle se calculerait sur celle qui a ete ecrite en dernier. Un bris qui n'exige plus
    # exactement trois paires restait vert, parce que les deux paires du cas precedent etaient
    # deja refusees par un AUTRE garde.
    quatre = dict(faux_paires)
    quatre["20-10"] = {"le_desaccord_par_couture_en_voxels": 99.0}
    v("★★★★ une QUATRIÈME paire, même sur les mêmes rangées, ne rend AUCUN triangle",
      not le_triangle_des_bruits_propres(quatre)["decidable"],
      str(le_triangle_des_bruits_propres(quatre).get("raison")))
    v("★★★ trois paires qui ne portent pas trois rangées ne rendent AUCUN triangle",
      not le_triangle_des_bruits_propres(
          {"10-20": faux_paires["10-20"], "20-10": faux_paires["10-20"],
           "10-30": faux_paires["10-30"]})["decidable"])
    v("★★★ une paire mal formée ne rend AUCUN triangle",
      not le_triangle_des_bruits_propres(
          {"dix": faux_paires["10-20"], "10-30": faux_paires["10-30"],
           "20-30": faux_paires["20-30"]})["decidable"])

    # ⭐⭐⭐⭐ LES DEUX BUDGETS, ET LEQUEL LIE. La fixture est batie pour que l'accord lie, puis
    # RENVERSEE pour que la traversee lie — un bris qui rendrait toujours le meme nom resterait
    # vert sur une seule des deux.
    p210 = {"decidable": True, "la_dispersion_du_pas_moyenne_en_voxels": 2.0,
            "la_dispersion_dune_rangee_en_voxels": 3.0, "la_derive_en_voxels": 1.0,
            "les_rangees_moyennees": 3}
    p211 = {"decidable": True, "les_paires": {
        k: {"le_desaccord_par_couture_en_voxels":
            faux_paires[k]["le_desaccord_par_couture_en_voxels"]} for k in faux_paires},
        "la_paire_declaree": [10, 20], "les_colonnes_demandees": 285}
    bu = les_deux_budgets(p210, p211, 36.0)
    v("★★★★ le budget de traversée est celui du pas MOYENNÉ, pas celui d'une rangée seule",
      bu["decidable"]
      and abs(bu["la_longueur_tenable_en_traversant_en_coutures"] - 324.0) < 1e-9,
      str(bu.get("la_longueur_tenable_en_traversant_en_coutures")))
    v("★★★★ le budget d'accord est celui de la PIRE paire, pas de la paire déclarée",
      bu["la_pire_paire"] == "20-30", str(bu.get("la_pire_paire")))
    v("★★★★ et c'est l'accord qui lie quand il est plus court",
      bu["le_budget_qui_lie"] == "s'accorder", str(bu.get("le_budget_qui_lie")))
    renverse = les_deux_budgets(
        {**p210, "la_dispersion_du_pas_moyenne_en_voxels": 30.0}, p211, 36.0)
    v("★★★★ et c'est la TRAVERSÉE qui lie quand c'est elle qui est plus courte",
      renverse["le_budget_qui_lie"] == "traverser", str(renverse.get("le_budget_qui_lie")))
    v("★★★ le plancher de la matière est budgété lui aussi, parce qu'un lecteur parfait le paie",
      (bu["traverser"].get("le_plancher_de_la_matiere") or {}).get("decidable") is True)
    v("★★★ une mesure absente ne rend AUCUN budget",
      not les_deux_budgets({"decidable": False}, p211, 36.0)["decidable"]
      and not les_deux_budgets(p210, {"decidable": False}, 36.0)["decidable"])

    # ⚠⚠⚠ UNE RANGEE DE `c` COLONNES PORTE `c - 1` COUTURES : un bris qui prend `c` gonfle la
    # cible et fait croire le budget plus court qu'il n'est.
    q = ce_que_la_rangee_demande(bu, 285)
    v("★★★★ une rangée de 285 colonnes porte 284 coutures, pas 285",
      q["decidable"] and q["les_coutures_dune_rangee"] == 284,
      str(q.get("les_coutures_dune_rangee")))
    v("★★★★ la part couverte est le rapport de la longueur tenable à ce compte",
      abs(q["la_part_couverte_en_traversant"] - round(324.0 / 284.0, 4)) < 1e-9,
      str(q.get("la_part_couverte_en_traversant")))
    v("★★★★ une rangée entière traverse ici, et elle ne s'accorde PAS",
      q["une_rangee_entiere_traverse"] is True and q["une_rangee_entiere_saccorde"] is False)
    v("★★★ une largeur d'une seule colonne ne rend AUCUNE cible",
      not ce_que_la_rangee_demande(bu, 1)["decidable"])
    v("★★★ une largeur absente ne rend AUCUNE cible",
      not ce_que_la_rangee_demande(bu, None)["decidable"])

    # ⚠⚠⚠ LA HAUTEUR EST GRATUITE SOUS LE MODELE, ET LA TRANCHE LE DIT COMME UNE CONSEQUENCE DU
    # MODELE ET NON COMME UNE MESURE. La sonde verifie que ce qui reste a mesurer est NOMME :
    # une conclusion trop belle qui ne nommerait pas sa condition serait la faute.
    na = la_nappe_entiere(tri, bu)
    v("★★★★ la nappe déclare la hauteur gratuite SOUS LE MODÈLE, et le modèle tient ici",
      na["decidable"] and na["la_hauteur_est_gratuite_sous_le_modele"] is True)
    v("★★★★ et elle NOMME ce qui reste à mesurer plutôt que de conclure",
      isinstance(na.get("ce_qui_reste_a_mesurer"), str)
      and "éloignées" in na["ce_qui_reste_a_mesurer"].lower())
    v("★★★★ un modèle réfuté retire la gratuité de la hauteur",
      la_nappe_entiere(tri_casse, bu)["la_hauteur_est_gratuite_sous_le_modele"] is False)

    # ⚠⚠ LE VERDICT SE REND ET NE MEURT PAS, meme prive de ses parties facultatives.
    for absent, quoi in (({}, "la rangée"), (None, "la rangée absente")):
        try:
            jv = juger(bu, absent, tri, na)
            ok_j = jv.get("decidable") is True
            pourquoi = ""
        except Exception as e:  # noqa: BLE001
            ok_j, pourquoi = False, f"la batterie est MORTE : {type(e).__name__}"
        v(f"★★★★ le verdict se rend même sans {quoi}", ok_j, pourquoi)
    v("★★★ des budgets indécidables ne rendent AUCUN verdict",
      not juger({"decidable": False}, q, tri, na)["decidable"])
    v("★★★ un triangle indécidable ne rend AUCUN verdict",
      not juger(bu, q, {"decidable": False}, na)["decidable"])
    # ⚠⚠⚠ ET UN DICTIONNAIRE SANS LA CLEF `decidable` DU TOUT, parce que c'est CE cas que le
    # `.get()` existe pour tenir : un bris qui l'ecrit en indexation directe passe tous les
    # appels dont le dictionnaire porte la clef, et ne meurt que sur celui qui ne la porte pas.
    for absent, ou in (("budgets", "les budgets"), ("triangle", "le triangle")):
        try:
            rendu = (juger({}, q, tri, na) if absent == "budgets"
                     else juger(bu, q, {}, na))
            ok_a, pourquoi = rendu.get("decidable") is False, str(rendu.get("raison"))
        except Exception as e:  # noqa: BLE001
            ok_a, pourquoi = False, f"la batterie est MORTE : {type(e).__name__}"
        v(f"★★★★ {ou} sans clef `decidable` est refusé, et le verdict ne MEURT pas",
          ok_a, pourquoi)

    # ⚠⚠⚠ LES LECTEURS REFUSENT PLUTOT QUE DE DEVINER.
    v("★★★ `210` absent est refusé, pas remplacé",
      not ce_que_la_moyenne_a_rendu(Path("/absent/210.json"))["decidable"])
    v("★★★ `211` absent est refusé, pas remplacé",
      not ce_que_laccord_a_rendu(Path("/absent/211.json"))["decidable"])
    import tempfile  # noqa: PLC0415
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "x.json"
        p.write_text(json.dumps({"ce_que_la_moyenne_a_retire": {"decidable": True}}),
                     encoding="utf-8")
        v("★★★ un `210` sans dispersion du pas moyenné est refusé",
          not ce_que_la_moyenne_a_rendu(p)["decidable"])
        p.write_text(json.dumps({"ce_que_les_desaccords_valent": {
            "1-2": {"decidable": True, "le_desaccord_par_couture_mesure_en_voxels": 1.0}}}),
            encoding="utf-8")
        v("★★★★ un `211` qui ne publie qu'UNE paire est refusé — le triangle en demande trois",
          not ce_que_laccord_a_rendu(p)["decidable"])

    # ⭐⭐⭐⭐ ET LA CHAINE ENTIERE EST EXERCEE SUR DES LECTEURS FABRIQUES, parce qu'une chaine
    # dont chaque maillon est sonde separement peut encore etre mal cablee.
    out = mesurer(36.0, lambda: p210, lambda: p211)
    v("★★★★ la mesure complète rend les deux budgets, le triangle et le verdict",
      (out.get("les_budgets") or {}).get("decidable")
      and (out.get("le_triangle") or {}).get("decidable")
      and (out.get("le_verdict") or {}).get("decidable"), str(out.get("raison")))
    v("★★★★ elle publie ce qu'une rangée demande, sans quoi les budgets ne se comparent à rien",
      (out.get("ce_quune_rangee_demande") or {}).get("decidable") is True)
    v("★★★ elle compare le triangle à la décomposition de `208`",
      "le_triangle_contre_208" in out)
    v("★★★ un `210` indécidable rend la mesure indécidable, avec sa raison",
      (lambda x: x.get("decidable") is False and x.get("raison"))(
          mesurer(36.0, lambda: {"decidable": False, "raison": "essai"}, lambda: p211)))

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
    a = ap.parse_args()
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
