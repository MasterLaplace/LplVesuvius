"""Regarder dans la profondeur — la coupe où la propriété pouvait apparaître.

⭐⭐⭐⭐ POURQUOI CE FICHIER, ET C'EST `R4-P44` QUI LE NOMME. `195` a ouvert les quinze chunks à
l'aveugle et l'œil est tombé exactement sur le hasard — **7** justes sur quinze contre **7,5**
attendus. Mais il regardait **une couche**, et l'étiquette de `190` naît d'une marche qui **CHOISIT
SA COUCHE** en avançant : c'est une propriété de la relation **entre** couches, donc une propriété
que la coupe de `195` ne pouvait structurellement pas porter. Une section le long de la profondeur
montre ce que la marche travaille : les feuillets empilés.

⚠⚠⚠ LA VUE EST DÉCLARÉE AVANT D'ÊTRE REGARDÉE, ET C'EST TOUT CE QUI SÉPARE CETTE TRANCHE DE LA
MAXIMISATION QUE `195` A DÉSAMORCÉE : la rangée médiane du cube, nommée par l'arithmétique. Choisir
la plus parlante des cent vingt-huit sections serait exactement le péché.

⭐⭐⭐⭐ ET LES DEUX DETTES DE `195` SE PAIENT ICI, TOUTES DEUX DÉCLARÉES AVANT LA LECTURE :
1. **L'ÉPREUVE APPARIÉE.** Les quinze paires sont connues ; on peut donc demander, paire par paire,
   si l'œil a désigné le bon des deux. `195` s'est interdit de l'ajouter après coup. Déclarée ici
   AVANT de regarder, elle devient légitime — et son prix est payé : **deux** épreuves sur les mêmes
   données, donc chacune reçoit la moitié de la garantie.
2. **LA SENSIBILITÉ À UN TRAIT DE TEXTURE.** `195` n'avait mesuré que la luminosité, donc son
   silence ne bornait rien d'autre. Un second lecteur, déclaré, lit la STRATIFICATION, et deux
   contrôles nommés montrent que chacun est aveugle au trait de l'autre.

⚠⚠ LA PLANCHE NE PUBLIE PAS LE PLAN PLACE → ADRESSE TANT QU'ELLE EST AVEUGLE, et c'est une
réparation que `195` rendait nécessaire : sa clef est publiée, donc un artefact qui donnerait ici
l'adresse de chaque place se joindrait à elle d'un seul coup d'œil. L'artefact aveugle porte donc
l'ENSEMBLE TRIÉ des trente adresses — de quoi vérifier la composition — et la levée reconstruit le
plan depuis le pipeline déterministe, sans un seul téléchargement.

Usage :
    uv run python src/nappe/regarder_dans_la_profondeur.py --verifier
    uv run python src/nappe/regarder_dans_la_profondeur.py --aveugle \\
        --json docs/mesures/regarder_dans_la_profondeur.json
    uv run python src/nappe/regarder_dans_la_profondeur.py --lever \\
        --json docs/mesures/regarder_dans_la_profondeur.json
"""
from __future__ import annotations

import argparse
import json
import sys
from math import comb
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))

from combien_dinterstices_traverses import PAS_UM, VOXEL_FIN_UM  # noqa: E402
from la_recette_posee_sur_le_rouleau import DELAI  # noqa: E402
from ou_le_chunk_se_trouve_t_il import les_etiquettes  # noqa: E402
from ouvrir_les_quinze import (DECIMALES, GARANTIE, _hex, _rng,  # noqa: E402
                               apparier, en_octets, la_loi_exacte, la_planche,
                               le_niveau_commun, le_seuil_derive, les_cubes, noter,
                               un_lecteur_mecanique)

MESURES = RACINE / "docs" / "mesures"
CE_QUE_LA_SURFACE_A_RENDU = MESURES / "ouvrir_les_quinze.json"

# ⚠⚠ LA GRAINE DIFFERE DE CELLE DE `195`, ET CE N'EST PAS UN DETAIL : sa clef est publiee, donc une
# planche qui reprendrait sa permutation serait lisible d'avance par quiconque l'a vue.
GRAINE = 20261005

# ⚠⚠⚠ LES DEUX EPREUVES SONT DECLAREES ICI, AVANT LA LECTURE, ET LEUR NOMBRE FIXE LE PRIX. Deux
# epreuves sur les memes donnees sont deux chances ; chacune recoit donc la moitie de la garantie que
# la chaine se donne depuis `176`. C'est la regle de famille de `194`, appliquee a des lois exactes.
LES_DEUX_EPREUVES = ("l'assignation entière", "les quinze paires")
GARANTIE_PAR_EPREUVE = GARANTIE / len(LES_DEUX_EPREUVES)

# ⚠⚠ LA PERIODE DE LA TEXTURE POSEE EST DERIVEE DE LA MATIERE, PAS CHOISIE : c'est le pas d'un pli
# rapporte au voxel. Une periode choisie ferait mesurer le reglage plutot que la stratification.
PERIODE_DES_PLIS_EN_VOXELS = PAS_UM / VOXEL_FIN_UM

# ⚠⚠⚠ LES CHAMPS DE L'ARTEFACT AVEUGLE SONT DECLARES ICI, ET LA SONDE EXIGE L'EGALITE EXACTE. Une
# premiere version verifiait l'absence du plan dans un dictionnaire que le test fabriquait lui-meme,
# donc elle ne pouvait pas voir ce que `mesurer` publie : un bris qui ajoutait la liste des retenants
# la laissait verte. Un ENSEMBLE DE CLEFS declare attrape n'importe quel champ ajoute, quel que soit
# son nom.
LES_CHAMPS_DE_LARTEFACT_AVEUGLE = (
    "graine", "la_vue_declaree", "les_deux_epreuves", "la_garantie_par_epreuve",
    "le_niveau_commun", "lappariement", "les_cubes", "la_planche", "la_loi_exacte",
    "la_sensibilite_de_texture", "les_controles_croises", "la_lecture_deposee",
    "ce_que_loeil_a_cru_voir", "la_cle", "la_note", "la_note_appariee", "le_verdict")
LES_CHAMPS_DE_LA_PLANCHE_AVEUGLE = (
    "ordre", "tuiles", "colonnes", "rangs", "hauteur", "largeur", "octets",
    "les_adresses_triees")

LECHELLE_DE_TEXTURE = (0, 1, 2, 4, 8, 16, 32, 64)
REPLICATS = 20

# ⚠⚠⚠ LA LECTURE EST DEPOSEE ICI, EN CLAIR, ET ELLE EST UNIQUE.
LA_LECTURE_A_LAVEUGLE: tuple[int, ...] = (1, 5, 8, 9, 10, 11, 12, 16, 19, 20, 21, 24, 26, 27, 30)
CE_QUE_LŒIL_A_CRU_VOIR = (
    "un feuillet CONTINU et nettement SÉPARÉ de ses voisins, qu'on pourrait suivre d'un bord à "
    "l'autre de la coupe — ni enchevêtrement de feuillets qui fusionnent, ni coupe presque vide"
)


def la_rangee_montree(hauteur: int) -> int:
    """La rangée médiane du cube — la seule nommable sans avoir regardé aucune section."""
    return int(hauteur) // 2


def une_section(bloc: np.ndarray, rangee: int) -> np.ndarray:
    """La coupe (couche, colonne) du cube à cette rangée — ce que la marche traverse.

    ⭐ C'EST LA DIFFERENCE AVEC `195`, ET ELLE EST STRUCTURELLE : sa tuile etait un plan DANS une
    couche, donc un plan ou l'empilement n'existe pas. Celle-ci coupe l'empilement en travers.
    """
    return np.asarray(bloc[:, int(rangee), :], dtype=float)


def les_tuiles_declarees(etiquettes: dict, graine: int = GRAINE) -> dict:
    """L'ordre des tuiles avant tout téléchargement — deux par paire, retenant puis contrôle.

    ⭐⭐⭐⭐ C'EST CE QUI PERMET A LA LEVEE DE NE RIEN RETELECHARGER TOUT EN NE PUBLIANT PAS LE PLAN.
    L'ordre ne depend que de l'etiquette publiee et de la graine, donc il se refait ; l'artefact
    aveugle n'a plus qu'a porter les octets et l'ENSEMBLE des adresses.
    """
    app = apparier(etiquettes, graine)
    tuiles = []
    for i, p in enumerate(app["paires"]):
        for camp in ("retient", "controle"):
            tuiles.append({"segment": p["segment"], "chunk": list(p[camp]),
                           "retient": camp == "retient", "paire": int(i)})
    return {"tuiles": tuiles, "lappariement": {k: v for k, v in app.items() if k != "paires"},
            "paires": app["paires"]}


def la_loi_appariee(informatives: int, justes: int) -> float:
    """P(au moins `justes` bonnes désignations sur `informatives` paires) — binomiale exacte.

    ⭐ UNE PAIRE OU L'ŒIL A DESIGNE LES DEUX, OU AUCUN, NE TRANCHE RIEN : elle est ecartee comme une
    egalite l'est d'un test des signes. Le nul porte donc sur les seules paires informatives.
    """
    n = int(informatives)
    if n <= 0:
        return 1.0
    return float(sum(comb(n, k) for k in range(max(0, int(justes)), n + 1))) / float(2 ** n)


def le_seuil_apparie(informatives: int, garantie: float = GARANTIE_PAR_EPREUVE) -> dict:
    """Le plus petit compte de bonnes désignations que la garantie de l'épreuve autorise."""
    n = int(informatives)
    seuil = None
    for k in range(0, n + 1):
        if la_loi_appariee(n, k) <= float(garantie):
            seuil = k
            break
    # ⚠⚠ LA DISTRIBUTION ENTIERE EST PUBLIEE PAR LE PRODUCTEUR, comme celle de `195` : une figure
    # qui la recalculerait serait une SECONDE definition de la loi appariee.
    distribution = [{"bonnes": k,
                     "probabilite": round(float(comb(n, k)) / float(2 ** n), DECIMALES),
                     "probabilite_den_avoir_autant_ou_plus": round(la_loi_appariee(n, k),
                                                                   DECIMALES)}
                    for k in range(0, n + 1)] if n > 0 else []
    return {"paires_informatives": n, "attendues_par_hasard": n / 2.0,
            "la_garantie": float(garantie), "le_seuil": seuil,
            "la_probabilite_au_seuil": (None if seuil is None
                                        else round(la_loi_appariee(n, seuil), DECIMALES)),
            "la_distribution": distribution}


def noter_par_paires(lecture, places: list[dict],
                     garantie: float = GARANTIE_PAR_EPREUVE) -> dict:
    """L'épreuve appariée : paire par paire, l'œil a-t-il désigné le retenant ?

    ⚠⚠ ELLE EST DECLAREE AVANT LA LECTURE, et c'est la seule chose qui la rende publiable : `195`
    a mesure qu'une epreuve ajoutee apres avoir vu le resultat de la premiere est exactement le
    peche que `191` a paye.
    """
    if not lecture:
        return {"decidable": False, "raison": "aucune lecture n'a été déposée"}
    lu = {int(x) for x in lecture}
    par_paire: dict[int, dict] = {}
    for i, pl in enumerate(places):
        d = par_paire.setdefault(int(pl["paire"]), {})
        d["retient" if pl["retient"] else "controle"] = i + 1
    informatives, justes, muettes = 0, 0, 0
    for _k, d in sorted(par_paire.items()):
        if "retient" not in d or "controle" not in d:
            continue
        a, b = d["retient"] in lu, d["controle"] in lu
        if a == b:
            muettes += 1
            continue
        informatives += 1
        justes += int(a)
    s = le_seuil_apparie(informatives, garantie)
    p = round(la_loi_appariee(informatives, justes), DECIMALES)
    return {"decidable": True, "les_paires": len(par_paire),
            "la_distribution": s["la_distribution"],
            "les_paires_muettes": int(muettes), "les_paires_informatives": int(informatives),
            "les_bonnes_designations": int(justes),
            "les_attendues_par_hasard": s["attendues_par_hasard"],
            "la_probabilite": p, "le_seuil": s["le_seuil"],
            "la_garantie": float(garantie),
            "loeil_separe": bool(s["le_seuil"] is not None and justes >= int(s["le_seuil"]))}


def un_lecteur_de_texture(octets: list[np.ndarray], choisies: int) -> tuple[int, ...]:
    """Le second lecteur de l'étalon : il désigne les tuiles les plus STRATIFIÉES.

    ⚠⚠ LA STATISTIQUE EST L'ECART-TYPE DU PROFIL EN PROFONDEUR — la moyenne de chaque couche le long
    des colonnes, puis sa dispersion d'une couche a l'autre. Elle ne bouge PAS d'un iota quand on
    ajoute une constante a toute la tuile, ce qui est exactement ce qui en fait un lecteur de
    texture et non un second lecteur de luminosite. Le controle nomme le verifie.
    """
    scores = [float(np.std(np.mean(np.asarray(o, dtype=float), axis=1))) for o in octets]
    rang = sorted(range(len(scores)), key=lambda i: (-scores[i], i))
    return tuple(sorted(i + 1 for i in rang[:int(choisies)]))


def une_stratification(section: np.ndarray, amplitude: float,
                       periode: float = PERIODE_DES_PLIS_EN_VOXELS) -> np.ndarray:
    """Une stratification posée le long de la profondeur, à la période d'un pli.

    ⚠⚠⚠ L'ONDE EST CENTREE SUR LA PROFONDEUR DE LA TUILE, ET LA PREMIERE VERSION NE L'ETAIT PAS :
    le cube fait cent neuf couches pour une periode de soixante-douze, donc une sinusoide brute y
    tient une cycle et demi et sa moyenne ne s'annule pas. Le trait posé deplacait alors la
    luminosite de plusieurs niveaux, le lecteur de luminosite le voyait, et le controle croise qui
    doit SEPARER les deux lecteurs virait au rouge — ce qu'il a fait. Un trait de texture qui
    deplace la moyenne est en partie un trait de luminosite.
    """
    z = np.arange(section.shape[0], dtype=float)
    onde = np.sin(2.0 * np.pi * z / float(periode))
    onde = onde - float(np.mean(onde))
    return np.asarray(section, dtype=float) + float(amplitude) * onde[:, None]


def la_sensibilite_de_texture(sections: list[np.ndarray], force: float, seuil: int,
                              replicats: int = REPLICATS, graine: int = GRAINE,
                              lecteur=None, poser=None) -> float:
    """La part des réplicats où une stratification de cette force est retrouvée.

    ⭐ MEME DESSIN QUE `195` : le fond est la VRAIE matiere, l'etiquette est retiree a chaque
    replicat, et le trait passe par le rendu — donc c'est la sensibilite du DISPOSITIF.
    """
    lire = lecteur or un_lecteur_de_texture
    pose = poser or une_stratification
    n = len(sections)
    m = n // 2
    r = _rng(graine + 11)
    vus = 0
    for _ in range(int(replicats)):
        injectees = set(int(i) for i in r.permutation(n)[:m])
        cs = [pose(c, float(force)) if i in injectees else np.asarray(c, dtype=float)
              for i, c in enumerate(sections)]
        niveau = le_niveau_commun(cs)
        octets = [en_octets(c, niveau) for c in cs]
        lu = lire(octets, m)
        vus += int(len({i - 1 for i in lu} & injectees) >= int(seuil))
    return float(vus) / float(replicats)


def la_force_de_texture_quil_faut(sections: list[np.ndarray], seuil: int,
                                  echelle=LECHELLE_DE_TEXTURE, replicats: int = REPLICATS,
                                  graine: int = GRAINE) -> dict:
    """La plus petite amplitude de l'échelle vue à TOUS les réplicats — dérivée, pas choisie."""
    courbe, trouvee = [], None
    for f in echelle:
        part = la_sensibilite_de_texture(sections, f, seuil, replicats, graine)
        courbe.append({"force": float(f), "part_des_replicats": float(part)})
        if trouvee is None and part >= 1.0:
            trouvee = float(f)
    return {"la_courbe": courbe, "la_force_quil_faut": trouvee,
            "replicats": int(replicats), "le_seuil": int(seuil),
            "la_periode_en_voxels": round(float(PERIODE_DES_PLIS_EN_VOXELS), 4)}


def les_deux_controles_croises(sections: list[np.ndarray], seuil: int,
                               replicats: int = REPLICATS, graine: int = GRAINE) -> dict:
    """Chaque lecteur est-il AVEUGLE au trait de l'autre ?

    ⚠⚠⚠ SANS CES DEUX CONTROLES, « un lecteur de texture » N'EST QU'UN NOM. Un lecteur qui monterait
    aussi avec la luminosite mesurerait la meme chose que celui de `195`, et la seconde sensibilite
    ne bornerait rien de neuf.
    """
    def _plat(section, amplitude):
        return np.asarray(section, dtype=float) + float(amplitude)

    grosse = float(max(LECHELLE_DE_TEXTURE))
    return {
        "la_texture_vue_par_le_lecteur_de_texture": la_sensibilite_de_texture(
            sections, grosse, seuil, replicats, graine),
        "la_texture_vue_par_le_lecteur_de_luminosite": la_sensibilite_de_texture(
            sections, grosse, seuil, replicats, graine, lecteur=un_lecteur_mecanique),
        "la_luminosite_vue_par_le_lecteur_de_texture": la_sensibilite_de_texture(
            sections, grosse, seuil, replicats, graine, poser=_plat),
        "la_luminosite_vue_par_le_lecteur_de_luminosite": la_sensibilite_de_texture(
            sections, grosse, seuil, replicats, graine, lecteur=un_lecteur_mecanique,
            poser=_plat),
        "la_force_posee": grosse,
    }


def mesurer(graine: int = GRAINE, delai: float = DELAI, replicats: int = REPLICATS,
            ouvrir=None) -> dict:
    """Ouvrir les trente cubes et poser la planche des COUPES EN PROFONDEUR, sans la clef."""
    etq = les_etiquettes()
    dec = les_tuiles_declarees(etq["chunks"], graine)
    cubes = (ouvrir or les_cubes)(dec["paires"], delai, True)
    brut = cubes["tuiles"]
    demandes = 2 * len(dec["paires"])
    if len(brut) != demandes:
        return {"decidable": False,
                "raison": f"{len(brut)} cubes rendus sur {demandes} — une planche amputée "
                          f"tirerait un AUTRE ordre et invaliderait toute lecture déposée",
                "refuses": cubes["refuses"]}
    # ⚠⚠ L'ORDRE TELECHARGE DOIT ETRE CELUI QUE LA LEVEE SAURA REFAIRE, et ca se verifie plutot que
    # de s'esperer : sans cette egalite, le plan reconstruit designerait d'autres cubes.
    attendu = [(t["segment"], tuple(t["chunk"]), t["retient"]) for t in dec["tuiles"]]
    obtenu = [(t["segment"], tuple(t["chunk"]), t["retient"]) for t in brut]
    if attendu != obtenu:
        return {"decidable": False,
                "raison": "l'ordre des cubes ouverts n'est pas celui que la levée sait refaire"}
    # ⚠⚠⚠ UN CUBE ABSENT EST UN REFUS, JAMAIS UN REPLI SUR LA COUCHE DE `195` : une tranche qui
    # se rabattrait en silence sur l'autre vue repondrait a l'autre question en portant ce titre.
    if any("cube" not in t for t in brut):
        return {"decidable": False,
                "raison": "un cube entier manque, et la coupe en profondeur l'exige"}
    sections = [une_section(t["cube"], la_rangee_montree(t["cube"].shape[1])) for t in brut]
    niveau = le_niveau_commun(sections)
    octets = [en_octets(c, niveau) for c in sections]
    planche = la_planche(dec["tuiles"], graine)
    retenants = int(sum(1 for t in dec["tuiles"] if t["retient"]))
    seuil = le_seuil_derive(len(brut), retenants, retenants, GARANTIE_PAR_EPREUVE)
    return {
        "graine": int(graine),
        "la_vue_declaree": "la coupe (couche, colonne) à la rangée médiane du cube",
        "les_deux_epreuves": list(LES_DEUX_EPREUVES),
        "la_garantie_par_epreuve": GARANTIE_PAR_EPREUVE,
        "le_niveau_commun": {"percentiles": [1.0, 99.0],
                             "bas": round(niveau[0], 4), "haut": round(niveau[1], 4)},
        "lappariement": dec["lappariement"],
        "les_cubes": {"demandes": demandes, "rendus": len(brut),
                      "paires_gardees": len(cubes["paires_gardees"]),
                      "refuses": cubes["refuses"]},
        "la_planche": {"ordre": planche["ordre"], "tuiles": len(brut),
                       "colonnes": planche["colonnes"], "rangs": planche["rangs"],
                       "hauteur": int(sections[0].shape[0]),
                       "largeur": int(sections[0].shape[1]),
                       "octets": [_hex(octets[j]) for j in planche["ordre"]],
                       "les_adresses_triees": sorted(
                           [str(t["segment"]), int(t["chunk"][0]), int(t["chunk"][1])]
                           for t in dec["tuiles"])},
        "la_loi_exacte": seuil,
        "la_sensibilite_de_texture": la_force_de_texture_quil_faut(
            sections, int(seuil["le_seuil"] or 10 ** 9), replicats=replicats, graine=graine),
        "les_controles_croises": les_deux_controles_croises(
            sections, int(seuil["le_seuil"] or 10 ** 9), replicats=replicats, graine=graine),
        "la_lecture_deposee": list(LA_LECTURE_A_LAVEUGLE),
        "ce_que_loeil_a_cru_voir": CE_QUE_LŒIL_A_CRU_VOIR,
        "la_cle": None, "la_note": None, "la_note_appariee": None,
        "le_verdict": {"leve": False,
                       "ce_qui_manque": "la lecture n'est pas encore déposée"
                       if not LA_LECTURE_A_LAVEUGLE else "la levée n'a pas été demandée"},
    }


def ce_que_195_a_rendu(chemin: Path = CE_QUE_LA_SURFACE_A_RENDU) -> int | None:
    """Les justes que `195` a obtenus sur la couche du milieu des MÊMES cubes, RELUS.

    ⚠⚠⚠ RELU, JAMAIS TAPE. La figure portait ce nombre en valeur de repli, donc un chiffre sans
    producteur dessine dans une image publiee — exactement ce que `chiffres_sans_record` existe pour
    attraper. Absent quand la mesure l'est : une comparaison qu'on ne peut pas faire ne se fabrique
    pas.
    """
    if not Path(chemin).is_file():
        return None
    d = json.loads(Path(chemin).read_text(encoding="utf-8"))
    n = (d.get("la_note") or {}).get("les_justes")
    return None if n is None else int(n)


def lever(chemin: Path, lecture=LA_LECTURE_A_LAVEUGLE, etiquettes=None) -> dict:
    """Lever l'aveugle sur la planche publiée, en RECONSTRUISANT le plan place → adresse."""
    d = json.loads(Path(chemin).read_text(encoding="utf-8"))
    if not d.get("decidable", True):
        return d
    planche = d.get("la_planche") or {}
    if not planche.get("ordre") or not planche.get("les_adresses_triees"):
        return {**d, "la_note": {"decidable": False,
                                 "raison": "la planche publiée est incomplète"}}
    etq = les_etiquettes()["chunks"] if etiquettes is None else etiquettes
    dec = les_tuiles_declarees(etq, int(d.get("graine", GRAINE)))
    triees = sorted([str(t["segment"]), int(t["chunk"][0]), int(t["chunk"][1])]
                    for t in dec["tuiles"])
    if [list(x) for x in triees] != [list(x) for x in planche["les_adresses_triees"]]:
        return {**d, "la_note": {
            "decidable": False,
            "raison": "les adresses reconstruites ne sont pas celles que la planche publie"}}
    places = [dec["tuiles"][j] for j in planche["ordre"]]
    cle = tuple(i + 1 for i, t in enumerate(places) if t["retient"])
    loi = d["la_loi_exacte"]
    if len(cle) != int(loi["retenants"]):
        return {**d, "la_note": {"decidable": False,
                                 "raison": f"{len(cle)} retenants reconstruits pour "
                                           f"{loi['retenants']} annoncés"}}
    note = noter(lecture, cle, int(loi["tuiles"]), int(loi["choisies"]), loi)
    appariee = noter_par_paires(lecture, places, float(d["la_garantie_par_epreuve"]))
    return {**d, "la_cle": list(cle), "la_note": note, "la_note_appariee": appariee,
            "ce_que_195_rendait": ce_que_195_a_rendu(),
            "la_planche": {**planche,
                           "adresses": [[t["segment"], int(t["chunk"][0]), int(t["chunk"][1])]
                                        for t in places]},
            "la_lecture_deposee": list(lecture),
            "ce_que_loeil_a_cru_voir": CE_QUE_LŒIL_A_CRU_VOIR,
            "le_verdict": {
                "leve": True,
                "loeil_separe_sur_lassignation": bool(note.get("loeil_separe")),
                "loeil_separe_sur_les_paires": bool(appariee.get("loeil_separe")),
                "loeil_separe": bool(note.get("loeil_separe")
                                     or appariee.get("loeil_separe")),
                "la_force_de_texture_que_le_dispositif_voit":
                    d["la_sensibilite_de_texture"]["la_force_quil_faut"]}}


def afficher(r: dict) -> None:
    if not r.get("decidable", True):
        print(f"REGARDER DANS LA PROFONDEUR   indécidable : {r.get('raison')}")
        return
    l, c, p = r["la_loi_exacte"], r["les_cubes"], r["la_planche"]
    print(f"REGARDER DANS LA PROFONDEUR   {c['rendus']} cubes sur {c['demandes']} · "
          f"{c['paires_gardees']} paires · coupe {p['hauteur']}×{p['largeur']}")
    print(f"  LES ÉPREUVES      {len(r['les_deux_epreuves'])} déclarées · garantie par épreuve "
          f"{r['la_garantie_par_epreuve']}")
    print(f"  LA LOI EXACTE     {l['attendus_par_hasard']} justes attendus · seuil "
          f"{l['le_seuil']} · P au seuil {l['la_probabilite_au_seuil']}")
    s = r["la_sensibilite_de_texture"]
    print("  LA TEXTURE        " + " · ".join(
        f"{int(x['force'])}→{x['part_des_replicats']:g}" for x in s["la_courbe"]))
    print(f"                    force dérivée {s['la_force_quil_faut']} · période "
          f"{s['la_periode_en_voxels']} voxels")
    k = r["les_controles_croises"]
    print(f"  LES CROISÉS       texture/texture {k['la_texture_vue_par_le_lecteur_de_texture']} · "
          f"texture/luminosité {k['la_texture_vue_par_le_lecteur_de_luminosite']} · "
          f"luminosité/texture {k['la_luminosite_vue_par_le_lecteur_de_texture']} · "
          f"luminosité/luminosité {k['la_luminosite_vue_par_le_lecteur_de_luminosite']}")
    if not r.get("la_cle"):
        print("  LA LEVÉE          PAS FAITE — l'artefact ne porte ni clef ni plan")
        return
    n, a = r["la_note"], r["la_note_appariee"]
    if n.get("decidable"):
        print(f"  L'ASSIGNATION     {n['les_justes']} justes sur {l['choisies']} · attendus "
              f"{n['les_attendus_par_hasard']} · P = {n['la_probabilite']} · seuil {n['le_seuil']}"
              f" · sépare {n['loeil_separe']}")
    else:
        print(f"  L'ASSIGNATION     indécidable : {n.get('raison')}")
    if a.get("decidable"):
        print(f"  LES PAIRES        {a['les_bonnes_designations']} bonnes sur "
              f"{a['les_paires_informatives']} informatives ({a['les_paires_muettes']} muettes) · "
              f"attendues {a['les_attendues_par_hasard']} · P = {a['la_probabilite']} · seuil "
              f"{a['le_seuil']} · sépare {a['loeil_separe']}")


def verifier() -> int:
    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        if not ok:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    # ⚠⚠⚠ LES DEUX EPREUVES SONT DECLAREES, ET LEUR NOMBRE FIXE LE PRIX.
    v("★★ deux épreuves sont déclarées", len(LES_DEUX_EPREUVES) == 2, str(LES_DEUX_EPREUVES))
    v("★★★★ la garantie par épreuve est DÉRIVÉE de leur nombre",
      abs(GARANTIE_PAR_EPREUVE - GARANTIE / 2.0) < 1e-15, str(GARANTIE_PAR_EPREUVE))
    # ⚠⚠ ET LE PRIX NE RELACHE JAMAIS UN SEUIL, MAIS IL NE LE DEPLACE PAS TOUJOURS : sur cette
    # planche les deux lois exactes SAUTENT la garantie d'un compte a l'autre, donc la moitie de
    # garantie tombe dans le meme intervalle. Le prix est declare et paye, et il se trouve gratuit
    # ici. Le dire est plus utile que de laisser croire qu'il a mordu.
    v("★★★ une garantie resserrée ne relâche JAMAIS le seuil",
      le_seuil_derive(30, 15, 15, GARANTIE_PAR_EPREUVE)["le_seuil"]
      >= le_seuil_derive(30, 15, 15, GARANTIE)["le_seuil"],
      f"{le_seuil_derive(30, 15, 15, GARANTIE_PAR_EPREUVE)['le_seuil']} contre "
      f"{le_seuil_derive(30, 15, 15, GARANTIE)['le_seuil']}")
    v("★★★★ et elle le DÉPLACE dès que le prix est assez lourd",
      le_seuil_derive(30, 15, 15, GARANTIE / 4.0)["le_seuil"]
      > le_seuil_derive(30, 15, 15, GARANTIE)["le_seuil"],
      f"{le_seuil_derive(30, 15, 15, GARANTIE / 4.0)['le_seuil']} à quatre épreuves")
    v("★★ la période de la texture est DÉRIVÉE du pas d'un pli",
      abs(PERIODE_DES_PLIS_EN_VOXELS - PAS_UM / VOXEL_FIN_UM) < 1e-12,
      str(round(PERIODE_DES_PLIS_EN_VOXELS, 4)))
    v("la rangée montrée est la médiane et rien d'autre",
      la_rangee_montree(128) == 64 and la_rangee_montree(9) == 4)

    # ⭐⭐⭐⭐ LA VUE EST BIEN UNE COUPE EN PROFONDEUR, ET C'EST CE QUI LA DISTINGUE DE `195`.
    cube = np.arange(5 * 4 * 3, dtype=float).reshape(5, 4, 3)
    sec = une_section(cube, 2)
    v("★★★ la section a la profondeur pour première dimension", sec.shape == (5, 3),
      str(sec.shape))
    v("★★★★ et elle traverse l'empilement, là où une couche ne le traverse pas",
      list(sec[:, 0]) == [6.0, 18.0, 30.0, 42.0, 54.0], str(list(sec[:, 0])))

    # ⭐⭐⭐⭐ LA LOI APPARIEE EST EXACTE, ET ELLE SE VERIFIE A LA MAIN.
    v("★★ toutes bonnes sur trois paires vaut un huitième",
      abs(la_loi_appariee(3, 3) - 0.125) < 1e-12, str(la_loi_appariee(3, 3)))
    v("au moins zéro bonne vaut un", abs(la_loi_appariee(9, 0) - 1.0) < 1e-12)
    v("★★ aucune paire informative ne tranche rien",
      abs(la_loi_appariee(0, 0) - 1.0) < 1e-12)
    sa = le_seuil_apparie(15)
    v("★★★★ le seuil apparié est DÉRIVÉ de la garantie de l'épreuve", sa["le_seuil"] == 12,
      str(sa["le_seuil"]))
    v("★★★ et il tient la garantie", sa["la_probabilite_au_seuil"] <= GARANTIE_PAR_EPREUVE,
      str(sa["la_probabilite_au_seuil"]))
    v("★★★ tandis qu'une bonne de moins ne la tient PAS",
      la_loi_appariee(15, sa["le_seuil"] - 1) > GARANTIE_PAR_EPREUVE,
      str(la_loi_appariee(15, sa["le_seuil"] - 1)))
    v("les attendues par hasard valent la moitié des informatives",
      abs(sa["attendues_par_hasard"] - 7.5) < 1e-12)
    v("★★★ la distribution appariée publiée somme à un, à la précision publiée",
      abs(sum(x["probabilite"] for x in sa["la_distribution"]) - 1.0)
      <= len(sa["la_distribution"]) * 10.0 ** -DECIMALES,
      str(sum(x["probabilite"] for x in sa["la_distribution"])))
    v("★★★ et elle est symétrique, comme un tirage à pile ou face l'est",
      all(abs(sa["la_distribution"][k]["probabilite"]
              - sa["la_distribution"][15 - k]["probabilite"]) < 1e-12 for k in range(16)))
    v("★★ aucune paire informative ne donne aucune distribution",
      le_seuil_apparie(0)["la_distribution"] == [])

    # ⭐⭐⭐⭐ L'EPREUVE APPARIEE SE VERIFIE SUR SES DEUX FACES ET SUR SES PAIRES MUETTES.
    places = []
    for i in range(15):
        places.append({"paire": i, "retient": True})
        places.append({"paire": i, "retient": False})
    parfaite = tuple(range(1, 31, 2))
    a1 = noter_par_paires(parfaite, places)
    v("★★★★ une lecture parfaite désigne les quinze retenants",
      a1["les_bonnes_designations"] == 15 and a1["les_paires_informatives"] == 15,
      f"{a1['les_bonnes_designations']}/{a1['les_paires_informatives']}")
    v("★★★★ et elle sépare sur les paires", a1["loeil_separe"])
    a2 = noter_par_paires(tuple(range(2, 32, 2)), places)
    v("★★★★ une lecture exactement fausse ne sépare pas", not a2["loeil_separe"],
      str(a2["les_bonnes_designations"]))
    a3 = noter_par_paires(tuple(range(1, 5)) + tuple(range(5, 27, 2)), places)
    v("★★★★ une paire dont les deux tuiles sont désignées est MUETTE, pas fausse",
      a3["les_paires_muettes"] >= 2 and a3["les_paires_informatives"] == 15 - a3[
          "les_paires_muettes"],
      f"{a3['les_paires_muettes']} muettes, {a3['les_paires_informatives']} informatives")
    v("une lecture absente est indécidable", noter_par_paires((), places)["decidable"] is False)

    # ⭐⭐⭐⭐ LES DEUX LECTEURS, ET LES DEUX CONTROLES CROISES QUI LES SEPARENT.
    r = _rng(17)
    fond = [r.normal(120.0, 14.0, size=(48, 40)) for _ in range(30)]
    v("★★★ le lecteur de texture désigne le nombre demandé",
      len(un_lecteur_de_texture([en_octets(c, (0.0, 255.0)) for c in fond], 15)) == 15)
    plat = np.full((48, 40), 100.0)
    v("★★★★ le lecteur de texture est INSENSIBLE à une constante ajoutée",
      abs(float(np.std(np.mean(plat + 50.0, axis=1)))
          - float(np.std(np.mean(plat, axis=1)))) < 1e-12)
    strie = une_stratification(plat, 20.0)
    v("★★★★ et il MONTE avec une stratification",
      float(np.std(np.mean(strie, axis=1))) > 1.0,
      str(round(float(np.std(np.mean(strie, axis=1))), 4)))
    v("★★★★ une stratification ne déplace PAS la moyenne de la tuile",
      abs(float(np.mean(strie)) - float(np.mean(plat))) < 1e-9,
      str(round(float(np.mean(strie)) - float(np.mean(plat)), 9)))
    v("★★★ et elle ne la déplace sur AUCUNE profondeur de tuile",
      max(abs(float(np.mean(une_stratification(np.zeros((h, 5)), 20.0))))
          for h in (48, 72, 109, 128)) < 1e-9,
      str(max(abs(float(np.mean(une_stratification(np.zeros((h, 5)), 20.0))))
              for h in (48, 72, 109, 128))))
    k = les_deux_controles_croises(fond, 11, 8, 17)
    v("★★★★ une texture posée est vue par le lecteur de TEXTURE",
      k["la_texture_vue_par_le_lecteur_de_texture"] >= 1.0,
      str(k["la_texture_vue_par_le_lecteur_de_texture"]))
    v("★★★★ et PAS par celui de luminosité — le contrôle croisé qui les sépare",
      k["la_texture_vue_par_le_lecteur_de_luminosite"] < 1.0,
      str(k["la_texture_vue_par_le_lecteur_de_luminosite"]))
    v("★★★★ une luminosité posée est vue par le lecteur de LUMINOSITÉ",
      k["la_luminosite_vue_par_le_lecteur_de_luminosite"] >= 1.0,
      str(k["la_luminosite_vue_par_le_lecteur_de_luminosite"]))
    v("★★★★ et PAS par celui de texture",
      k["la_luminosite_vue_par_le_lecteur_de_texture"] < 1.0,
      str(k["la_luminosite_vue_par_le_lecteur_de_texture"]))
    f = la_force_de_texture_quil_faut(fond, 11, (0, 8, 64), 8, 17)
    v("★★★★ la force de texture rendue est vue à tous les réplicats",
      f["la_force_quil_faut"] is not None
      and la_sensibilite_de_texture(fond, f["la_force_quil_faut"], 11, 8, 17) >= 1.0,
      str(f["la_force_quil_faut"]))
    v("★★★ et la courbe entière est publiée", len(f["la_courbe"]) == 3,
      str([x["part_des_replicats"] for x in f["la_courbe"]]))
    v("★★★ une texture nulle n'est JAMAIS vue à tous les réplicats",
      la_sensibilite_de_texture(fond, 0.0, 11, 8, 17) < 1.0,
      str(la_sensibilite_de_texture(fond, 0.0, 11, 8, 17)))

    # ⚠⚠⚠ L'ORDRE DES TUILES SE REFAIT SANS RESEAU, ET C'EST CE QUI PORTE LA LEVEE.
    etq = {}
    for i in range(6):
        seg = chr(65 + i)
        etq[(seg, 0, 0)] = {"etiquette": True}
        etq[(seg, 10 * i + 1, 10 * i + 1)] = {"etiquette": False}
    dec = les_tuiles_declarees(etq, 99)
    v("★★★ chaque paire donne deux tuiles, retenant puis contrôle",
      len(dec["tuiles"]) == 12 and dec["tuiles"][0]["retient"]
      and not dec["tuiles"][1]["retient"], str(len(dec["tuiles"])))
    v("★★★★ et l'ordre est le MÊME à graine égale, donc refaisable sans réseau",
      [(t["segment"], t["chunk"], t["retient"]) for t in les_tuiles_declarees(etq, 99)["tuiles"]]
      == [(t["segment"], t["chunk"], t["retient"]) for t in dec["tuiles"]])
    v("★★★ ce que `195` a rendu est RELU de sa mesure, jamais tapé",
      ce_que_195_a_rendu() == 7, str(ce_que_195_a_rendu()))
    v("★★★ et il est absent quand la mesure l'est",
      ce_que_195_a_rendu(Path("/n/existe/pas.json")) is None)
    v("★★ chaque tuile porte le rang de sa paire",
      sorted({t["paire"] for t in dec["tuiles"]}) == list(range(6)))

    # ⭐⭐⭐⭐ LA PLANCHE AVEUGLE NE PUBLIE PAS LE PLAN, ET LA LEVEE LE RECONSTRUIT.
    import tempfile  # noqa: PLC0415
    pl = la_planche(dec["tuiles"], 99)
    seuil6 = le_seuil_derive(12, 6, 6, GARANTIE_PAR_EPREUVE)
    triees = sorted([str(t["segment"]), int(t["chunk"][0]), int(t["chunk"][1])]
                    for t in dec["tuiles"])
    artefact = {"graine": 99, "la_garantie_par_epreuve": GARANTIE_PAR_EPREUVE,
                "la_loi_exacte": seuil6,
                "la_sensibilite_de_texture": {"la_force_quil_faut": 8.0},
                "la_planche": {"ordre": pl["ordre"], "tuiles": 12,
                               "les_adresses_triees": triees}}
    cle_vraie = tuple(i + 1 for i, j in enumerate(pl["ordre"]) if dec["tuiles"][j]["retient"])
    with tempfile.TemporaryDirectory() as dd:
        ch = Path(dd) / "a.json"
        ch.write_text(json.dumps(artefact), encoding="utf-8")
        lu = lever(ch, cle_vraie, etq)
        v("★★★★ la levée reconstruit le plan et note la lecture",
          lu["la_note"]["decidable"] and lu["la_note"]["les_justes"] == 6,
          str(lu["la_note"].get("les_justes")))
        v("★★★★ et elle note AUSSI l'épreuve appariée",
          lu["la_note_appariee"]["decidable"]
          and lu["la_note_appariee"]["les_bonnes_designations"] == 6,
          str(lu["la_note_appariee"].get("les_bonnes_designations")))
        faux = {**artefact, "la_planche": {**artefact["la_planche"],
                                           "les_adresses_triees": triees[:-1]
                                           + [["Z", 9, 9]]}}
        ch.write_text(json.dumps(faux), encoding="utf-8")
        v("★★★★ une planche dont les adresses ne se reconstruisent pas est REFUSÉE",
          lever(ch, cle_vraie, etq)["la_note"]["decidable"] is False,
          str(lever(ch, cle_vraie, etq)["la_note"].get("raison")))
        ch.write_text(json.dumps({**artefact,
                                  "la_planche": {"tuiles": 12}}), encoding="utf-8")
        v("★★★ une planche sans ordre est refusée",
          lever(ch, cle_vraie, etq)["la_note"]["decidable"] is False)
        ch.write_text(json.dumps({"decidable": False, "raison": "amputée"}), encoding="utf-8")
        v("★★★ une mesure indécidable traverse la levée sans être notée",
          lever(ch, cle_vraie, etq).get("la_note") is None)

    # ⚠⚠⚠ UNE PLANCHE AMPUTEE EST REFUSEE, ET LA REGLE S'EXERCE SANS RESEAU.
    def _cubes_fabriques(paires, _delai, _garder=True, manquants=0, melanger=False):
        rr = _rng(4)
        tt = []
        for pr in paires:
            for camp in ("retient", "controle"):
                tt.append({"segment": pr["segment"], "chunk": list(pr[camp]),
                           "retient": camp == "retient",
                           "cube": rr.normal(120.0, 20.0, size=(12, 8, 6))})
        if melanger:
            tt = tt[1:] + tt[:1]
        if manquants:
            tt = tt[:-manquants]
        return {"tuiles": tt, "paires_gardees": paires, "refuses": {}}

    def lever_sur(res):
        import tempfile as _t  # noqa: PLC0415
        with _t.TemporaryDirectory() as dd2:
            ch2 = Path(dd2) / "b.json"
            ch2.write_text(json.dumps({k: v for k, v in res.items()}), encoding="utf-8")
            return lever(ch2, (1, 2, 3))

    entier = mesurer(replicats=3, ouvrir=lambda pr, d_, g_: _cubes_fabriques(pr, d_, g_))
    v("★★★ une planche entière est mesurée", entier.get("decidable", True)
      and entier["la_planche"]["tuiles"] == 30, str(entier.get("raison"))[:90])
    # ⚠⚠⚠ LA SONDE PORTE SUR CE QUE `mesurer` PUBLIE, PAS SUR UNE FIXTURE DU TEST.
    v("★★★★ l'artefact aveugle porte EXACTEMENT les champs déclarés, ni un de plus",
      sorted(entier) == sorted(LES_CHAMPS_DE_LARTEFACT_AVEUGLE),
      str(sorted(set(entier) ^ set(LES_CHAMPS_DE_LARTEFACT_AVEUGLE))))
    v("★★★★ et sa planche aussi, donc aucun plan place → adresse n'y tient",
      sorted(entier["la_planche"]) == sorted(LES_CHAMPS_DE_LA_PLANCHE_AVEUGLE),
      str(sorted(set(entier["la_planche"]) ^ set(LES_CHAMPS_DE_LA_PLANCHE_AVEUGLE))))
    v("★★★ ni clef, ni note, ni note appariée",
      entier.get("la_cle") is None and entier.get("la_note") is None
      and entier.get("la_note_appariee") is None)
    v("★★★★ tandis que la levée, elle, publie le plan reconstruit",
      "adresses" in lever_sur(entier)["la_planche"],
      str(sorted(lever_sur(entier)["la_planche"]))[:120])
    v("★★★★ une planche AMPUTÉE est refusée",
      mesurer(replicats=3,
              ouvrir=lambda pr, d_, g_: _cubes_fabriques(pr, d_, g_, 2)).get("decidable")
      is False)
    v("★★★★ un ordre de cubes que la levée ne saurait refaire est refusé",
      mesurer(replicats=3, ouvrir=lambda pr, d_, g_: _cubes_fabriques(
          pr, d_, g_, 0, True)).get("decidable") is False)

    nom = "regarder_dans_la_profondeur.py"
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
    p.add_argument("--aveugle", action="store_true")
    p.add_argument("--lever", action="store_true")
    p.add_argument("--json", type=Path)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if a.lever and not LA_LECTURE_A_LAVEUGLE:
        print("refus : aucune lecture n'a été déposée, la levée n'aurait rien à noter")
        return 1
    if a.lever:
        if not a.json or not a.json.is_file():
            print("refus : la levée lit la planche publiée, il faut donc son chemin")
            return 1
        r = lever(a.json)
    else:
        r = mesurer()
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
