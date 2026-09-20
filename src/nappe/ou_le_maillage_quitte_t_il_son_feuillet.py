"""Où le maillage quitte-t-il son feuillet — sur un segment entier, et non sur trente vignettes.

⭐⭐⭐⭐ POURQUOI CE FICHIER, ET C'EST `R4-P46` QUI LE NOMME. `197` a mesuré la quantité que le
déroulage doit corriger — de combien la surface dépliée quitte son feuillet — mais sur **trente
vignettes**, et la même tranche a mesuré pourquoi ce n'est pas assez : une vignette couvre un segment
sur cent vingt-quatre mille. La question se pose donc à l'échelle du **segment**.

⭐⭐⭐⭐ ET CE QUE ÇA REND EST UNE CARTE : où la surface a quitté son feuillet, et de combien. C'est
la **première moitié** de ce qui remplace l'humain du transfert — savoir **où** il faut corriger — et
elle se mesure sans rien inventer, avec l'instrument que `197` a livré.

⚠⚠⚠ UNE SEULE QUESTION EST DÉCLARÉE, ET ELLE L'EST AVANT DE REGARDER : **le serpentement est-il
GROUPÉ sur le segment ?** Si oui, un correcteur peut être local et ciblé ; si non, le défaut est
partout et il faut le traiter partout. Une seule question, donc la garantie de la chaîne s'applique
telle quelle : dix-neuf mélanges, un sur vingt.

⚠⚠ ET DEUX LIMITES SONT NOMMÉES PLUTÔT QUE TUES. La première : le treillis est un **budget**, pas
une propriété de la matière — deux cent cinquante-six positions, une par téléchargement. La seconde,
plus importante : ce qui est cartographié est le serpentement **LOCAL**, dans les trois dixièmes de
millimètre d'un chunk. La dérive **accumulée** d'un bout à l'autre du segment demanderait des chunks
contigus, et cette tranche ne la mesure pas.

Usage :
    uv run python src/nappe/ou_le_maillage_quitte_t_il_son_feuillet.py --verifier
    uv run python src/nappe/ou_le_maillage_quitte_t_il_son_feuillet.py \\
        --json docs/mesures/ou_le_maillage_quitte_t_il_son_feuillet.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from math import comb
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))

from la_recette_posee_sur_le_rouleau import (DELAI, PERMUTATIONS,  # noqa: E402
                                             les_chunks, les_volumes)
from letiquette_a_t_elle_une_structure import _distance_moyenne  # noqa: E402
from ouvrir_les_quinze import _rng  # noqa: E402
from que_montrent_ces_deux_vues import (DEMI_PAS_EN_VOXELS, LES_DECILES,  # noqa: E402
                                        PAS_EN_VOXELS, la_rangee_montree,
                                        le_serpentement, une_section)
from zarr_depth import BUCKET, array_meta, chunk_key, decode  # noqa: E402

sys.path.insert(0, str(RACINE / "src" / "tracecheck"))
from tracecheck import get_with_reason  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
GRAINE = 20261006

# ⚠⚠ LE COTE DU TREILLIS EST UN BUDGET, ET C'EST DIT : deux cent cinquante-six positions valent deux
# cent cinquante-six telechargements. Ce qui est une propriete du dessin, et non du budget, c'est que
# le treillis soit REGULIER — aucune position n'est choisie pour ce qu'elle contient.
COTE_DE_LA_CARTE = 16

# ⚠⚠⚠ UNE SEULE QUESTION EST DECLAREE, donc la garantie de la chaine s'applique telle quelle.
LA_QUESTION_DECLAREE = "le serpentement est-il groupé sur le segment ?"

# ⚠⚠ LE PIRE DECILE EST CELUI QUE `197` EMPLOIE DEJA POUR MESURER UN SERPENTEMENT : relu, pas choisi.
LE_DECILE_DU_PIRE = LES_DECILES[1]

REPLICATS = 20


# ⚠⚠⚠ UN CHUNK QUI N'EXISTE PAS ET UN LIEN QUI TOMBE SONT DEUX FAITS DIFFERENTS, et les confondre
# transforme un enonce sur LE FIL en enonce sur LA DONNEE. Le depot l'a paye le 2026-08-26 et a
# ecrit la regle dans `tracecheck.get_with_reason` ; elle est REUTILISEE ici plutot que reecrite.
LE_RESEAU_A_ECHOUE = "le réseau a échoué"
ABSENT_DU_DEPOT = "absent du dépôt"

# ⚠⚠ LE NOMBRE DE REPRISES EST UN BUDGET, ET C'EST DIT. Mais l'idee, elle, n'en est pas un : un 404
# est une REPONSE — le depot dit que ce chunk n'existe pas, et il le redira — tandis qu'une panne de
# transport n'est pas une reponse. Redemander est donc la facon EMPIRIQUE de distinguer les deux,
# la ou le code d'erreur seul ne fait que les nommer.
LES_REPRISES = 3


def lattente_avant_le_prochain_essai(essai: int, base: float) -> float:
    """L'attente entre deux essais — elle DOUBLE, et une base nulle la supprime.

    ⚠⚠⚠ REDEMANDER AUSSITOT NE SERT A RIEN CONTRE UNE PANNE QUI DURE, et la mesure l'a dit : une
    ligne de deux cent quatre-vingt-cinq chunks a perdu cent cinquante-deux requetes sur des echecs
    de resolution de nom, et pas une seule reprise n'a abouti — les quatre essais tenaient dans
    quelques millisecondes. Une attente qui double couvre un intervalle utile sans jamais rendre une
    panne longue acceptable : celle-la reste un refus.

    ⚠ La base NULLE est le defaut, donc toute tranche anterieure garde exactement son comportement.
    """
    return float(base) * (2.0 ** max(0, int(essai)))


def un_chunk(url: str, meta: dict, cy: int, cx: int, delai: float = DELAI,
             chercher=None, reprises: int = LES_REPRISES, pause: float = 0.0):
    """Le cube brut d'un chunk, et la RAISON PRÉCISE quand il n'y en a pas.

    ⚠⚠⚠ C'EST LA REPARATION D'UN DEFAUT QUE LA MESURE A SUBI : une coupure de connexion a fait
    passer le compte de positions lues de cent quatre-vingt-neuf a cent dix, et le compte d'absents
    de soixante-six a cent quarante-cinq — sans que rien ne le dise, puisque les deux raisons
    tombaient dans le meme mot. Le chiffre publie comme « positions sans surface » etait donc un
    chiffre sur le RESEAU autant que sur le maillage.

    ⚠⚠ `chercher` EST INJECTABLE POUR QUE LA REGLE SOIT SONDABLE : sans cela, la seule ligne qui
    separe un chunk absent d'un lien tombe n'etait visitee par aucune sonde, et un bris qui les
    reconfondait restait vert.
    """
    profond, hy, hx = meta["chunks"]
    chef = chercher or get_with_reason
    cle = f"{url}/{chunk_key(meta, 0, cy, cx)}"
    raw, pourquoi, reprises_faites = None, None, 0
    for essai in range(max(1, int(reprises) + 1)):
        raw, pourquoi = chef(cle, delai)
        if raw is not None or pourquoi == "absent":
            break
        reprises_faites = essai + 1
        attente = lattente_avant_le_prochain_essai(essai, pause)
        if attente > 0.0 and essai < int(reprises):
            time.sleep(attente)
    if raw is None:
        return None, (ABSENT_DU_DEPOT if pourquoi == "absent"
                      else f"{LE_RESEAU_A_ECHOUE} : {pourquoi}")
    data = decode(raw, meta, profond * hy * hx)
    if data is None:
        return None, "illisible"
    bloc = np.frombuffer(data, dtype=np.dtype(meta["dtype"])).reshape(profond, hy, hx)
    return bloc, (None if not reprises_faites else f"repris {reprises_faites}")


def les_pannes_de_reseau(refuses: dict) -> int:
    """Le compte de positions perdues par le FIL, toutes raisons de transport confondues."""
    return int(sum(n for quoi, n in (refuses or {}).items()
                   if str(quoi).startswith(LE_RESEAU_A_ECHOUE)))


def le_segment_declare() -> dict | None:
    """Le PREMIER segment du recensement, dans l'ordre du fichier — jamais choisi.

    ⚠ La regle est celle de `la_recette_posee_sur_le_rouleau` : un segment choisi pour sa taille ou
    sa texture ferait mesurer le choix.
    """
    v = les_volumes(combien=1)
    return v[0] if v else None


def le_parcours(positions, prendre) -> dict:
    """Le serpentement en chaque position demandée, et le COMPTE de ce qui n'a pas répondu.

    ⚠⚠⚠ CE QUI NE REPOND PAS EST COMPTE PAR SA RAISON, JAMAIS DEFAUTE A ZERO. Une position hors du
    maillage n'a pas un serpentement nul : elle n'a pas de surface, et la confondre avec une surface
    parfaitement tenue ferait une carte qui s'ameliore la ou le segment s'arrete.

    ⚠ Extrait de `la_carte` pour etre exercable sans reseau : la premiere version gardait ce
    parcours a l'interieur, donc la branche des refus n'etait visitee par aucune sonde.
    """
    lues, refus, reprises = [], {}, 0
    for cy, cx in positions:
        bloc, pourquoi = prendre(int(cy), int(cx))
        if bloc is not None and pourquoi and str(pourquoi).startswith("repris"):
            # ⚠ Une position reprise est une position LUE : ce qui se compte a cote est le nombre de
            # fois ou le fil a flanche, parce qu'un lien tres instable doit se voir.
            reprises += int(str(pourquoi).split()[-1])
            pourquoi = None
        if bloc is None:
            refus[pourquoi] = refus.get(pourquoi, 0) + 1
            continue
        b = np.asarray(bloc, dtype=float)
        if float(b.max()) <= 0.0:
            refus["vide"] = refus.get("vide", 0) + 1
            continue
        s = le_serpentement(une_section(b, la_rangee_montree(b.shape[1])))
        if not s.get("decidable"):
            quoi = s.get("raison", "indécidable")
            refus[quoi] = refus.get(quoi, 0) + 1
            continue
        lues.append({"position": [int(cy), int(cx)], **s})
    return {"lues": lues, "refuses": refus, "reprises": int(reprises)}


def la_carte(volume: dict, cote: int = COTE_DE_LA_CARTE, delai: float = DELAI,
             ouvrir=None, meta=None, chercher=None) -> dict:
    """Le serpentement en chaque position d'un treillis régulier couvrant TOUT le segment.

    ⚠⚠ `meta` EST INJECTABLE POUR QUE LE TREILLIS SOIT EXERCABLE SANS RESEAU : sans cela, la seule
    ligne qui decide de la COUVERTURE de la carte n'etait visitee par aucune sonde, et un bris qui
    reduisait le treillis a quatre positions la laissait verte.
    """
    url = f"{BUCKET}/{volume['cle']}"
    if meta is None:
        try:
            meta = array_meta(url, 0, delai)
        except Exception as e:  # noqa: BLE001
            return {"decidable": False, "raison": f"le volume ne répond pas : {type(e).__name__}"}
    prof, hy, hx = meta["chunks"]
    _, rows, cols = meta["shape"]
    gy, gx = -(-rows // hy), -(-cols // hx)
    positions = les_chunks(gy, gx, int(cote))
    parcouru = le_parcours(positions, ouvrir
                           or (lambda cy, cx: un_chunk(url, meta, cy, cx, delai, chercher)))
    lues, refus = parcouru["lues"], parcouru["refuses"]
    reprises_faites = int(parcouru.get("reprises", 0))
    # ⚠⚠⚠ LES COORDONNEES DU TREILLIS SONT PUBLIEES, ET C'EST UN DEFAUT VU EN REGARDANT LA CARTE :
    # sans elles, une figure ne peut ranger les positions lues que par leur RANG entre elles, donc
    # une ligne entierement vide est COMPRIMEE et la geometrie dessinee n'est plus celle du treillis.
    # Un trou doit se voir a sa place.
    return {"decidable": bool(lues), "segment": volume["segment"],
            "grille_de_chunks": [int(gy), int(gx)], "couches": int(prof),
            "positions_du_treillis": len(positions), "positions_lues": len(lues),
            "les_reprises_du_reseau": reprises_faites, "les_reprises_permises": int(LES_REPRISES),
            "les_lignes_du_treillis": sorted({int(p[0]) for p in positions}),
            "les_colonnes_du_treillis": sorted({int(p[1]) for p in positions}),
            "refuses": refus, "les_positions": lues}


def les_quantiles(lues: list[dict]) -> dict:
    """Comment le serpentement se distribue sur le segment — et ce qui sature."""
    if not lues:
        return {"decidable": False, "raison": "aucune position lue"}
    v = np.asarray([float(x["le_serpentement_en_voxels"]) for x in lues], dtype=float)
    sat = [int(x.get("les_colonnes_saturees", 0)) for x in lues]
    return {"decidable": True, "positions": len(lues),
            "le_median_en_voxels": round(float(np.median(v)), 4),
            "le_median_en_plis": round(float(np.median(v)) / PAS_EN_VOXELS, 6),
            "le_decile_haut_en_voxels": round(float(np.percentile(v, LE_DECILE_DU_PIRE)), 4),
            "le_decile_haut_en_plis": round(float(np.percentile(v, LE_DECILE_DU_PIRE))
                                            / PAS_EN_VOXELS, 6),
            "le_maximal_en_voxels": round(float(np.max(v)), 4),
            "les_positions_qui_saturent": int(sum(1 for x in sat if x > 0)),
            "la_part_qui_sature": round(float(sum(1 for x in sat if x > 0)) / len(lues), 6)}


def le_groupement(lues: list[dict], tirages: int = PERMUTATIONS, graine: int = GRAINE,
                  decile: float = LE_DECILE_DU_PIRE) -> dict:
    """Les positions du PIRE décile se tiennent-elles près les unes des autres ?

    ⭐⭐⭐⭐ C'EST LA SEULE QUESTION DE LA TRANCHE, ET SA REPONSE DECIDE DE LA FORME DU CORRECTEUR :
    un defaut groupe se corrige localement, un defaut disperse se corrige partout.

    ⚠⚠ LE MELANGE GARDE LE COMPTE et redistribue le pire decile sur les MEMES positions : sans cela
    il comparerait aussi la forme du treillis, qui n'a rien a voir avec la question.
    """
    if len(lues) < 4:
        return {"decidable": False, "raison": "trop peu de positions"}
    v = np.asarray([float(x["le_serpentement_en_voxels"]) for x in lues], dtype=float)
    pts = [(int(x["position"][0]), int(x["position"][1])) for x in lues]
    seuil = float(np.percentile(v, decile))
    pires = [p for p, y in zip(pts, v) if y >= seuil]
    if len(pires) < 2:
        return {"decidable": False, "raison": "moins de deux positions dans le pire décile"}
    obs = _distance_moyenne(pires)
    if obs is None:
        return {"decidable": False, "raison": "distance indéfinie"}
    r = _rng(graine)
    nuls = []
    for _ in range(int(tirages)):
        idx = r.permutation(len(pts))[:len(pires)]
        d = _distance_moyenne([pts[int(i)] for i in idx])
        if d is not None:
            nuls.append(float(d))
    if not nuls:
        return {"decidable": False, "raison": "aucun mélange lisible"}
    au_moins = int(sum(1 for x in nuls if x <= float(obs)))
    return {"decidable": True, "le_seuil_du_pire_decile": round(seuil, 4),
            "les_positions_du_pire_decile": len(pires), "tirages": int(tirages),
            "la_distance_moyenne": round(float(obs), 4),
            "la_distance_moyenne_du_nul": round(float(np.median(nuls)), 4),
            "les_melanges_au_moins_aussi_serres": au_moins,
            "ca_se_groupe": bool(au_moins == 0)}


def un_treillis(cote: int) -> list[tuple[int, int]]:
    """Les positions d'un treillis carré — la géométrie par défaut des sondes."""
    return [(y, x) for y in range(int(cote)) for x in range(int(cote))]


def une_carte_fabriquee(positions, force: float, groupee: bool, graine: int,
                        bruit: float = 2.0, part_chaude: float = 0.1) -> list[dict]:
    """Une carte dont la réponse est construite — groupée ou dispersée, à force ÉGALE.

    ⭐⭐⭐⭐ ELLE PREND LES POSITIONS PLUTOT QU'UN COTE, ET C'EST LA REPARATION DE `193` APPLIQUEE
    ICI : un etalon pose sur un treillis plein ne dit rien d'une carte trouee. La carte reelle a des
    positions qui n'ont pas repondu, et l'etalon doit avoir EXACTEMENT les memes.

    ⚠⚠ LES DEUX FACES PORTENT LE MEME NOMBRE DE POSITIONS CHAUDES ET LA MEME FORCE : ce qui change
    entre elles est la PLACE, et rien d'autre. Sinon l'etalon mesurerait la force.
    """
    r = _rng(graine)
    pts = [(int(p[0]), int(p[1])) for p in positions]
    n = max(2, int(round(float(part_chaude) * len(pts))))
    if groupee:
        cy = int(np.median([p[0] for p in pts]))
        cx = int(np.median([p[1] for p in pts]))
        ordre = sorted(pts, key=lambda p: (max(abs(p[0] - cy), abs(p[1] - cx)), p))
        chauds = set(ordre[:n])
    else:
        chauds = {pts[int(i)] for i in r.permutation(len(pts))[:n]}
    out = []
    for p in pts:
        base = float(abs(r.normal(0.0, bruit)))
        out.append({"position": [p[0], p[1]], "chaude": bool(p in chauds),
                    "le_serpentement_en_voxels": base + (float(force) if p in chauds else 0.0),
                    "les_colonnes_saturees": 0})
    return out


def le_taux_tient_la_garantie(vus: int, replicats: int, garantie: float) -> dict:
    """Un compte de faux est-il COMPATIBLE avec la garantie, ou la dépasse-t-il vraiment ?

    ⚠⚠⚠ « INFERIEUR OU EGAL A LA GARANTIE » EST LE MAUVAIS CRITERE, ET LA MESURE L'A DIT : sur vingt
    replicats, un dispositif qui se trompe une fois sur vingt rend DEUX faux une fois sur quatre. Ce
    qui se verifie est donc la probabilite exacte d'en voir autant ou plus sous la garantie — et un
    etalon n'est declare casse que si ce compte serait lui-meme surprenant au meme niveau.
    """
    n, k, q = int(replicats), int(vus), float(garantie)
    pr = float(sum(comb(n, j) * q ** j * (1.0 - q) ** (n - j) for j in range(max(0, k), n + 1)))
    return {"les_faux": k, "replicats": n, "le_taux": (k / n) if n else 0.0,
            "la_garantie": q, "la_probabilite_den_avoir_autant": pr,
            "il_tient": bool(pr > q)}


def la_part_vue(positions, force: float, groupee: bool, replicats: int = REPLICATS,
                tirages: int = PERMUTATIONS, graine: int = GRAINE,
                part_chaude: float = 0.1) -> dict:
    """La part des réplicats où une carte de cette forme est déclarée groupée.

    ⚠⚠⚠ LES DEUX FACES PASSENT PAR LA MEME FONCTION, ET C'EST LE REMEDE : la premiere version ne
    mesurait sur replicats que la face POSITIVE et jugeait la negative sur un TIRAGE UNIQUE. La
    mesure reelle l'a dit — l'etalon a rendu « ne separe pas » parce que son unique carte dispersee
    etait tombee du mauvais cote, ce qui arrive une fois sur vingt par construction. C'est
    exactement le defaut que `193` a trouve dans `191`.
    """
    vus = 0
    for k in range(int(replicats)):
        c = une_carte_fabriquee(positions, force, groupee, int(graine) + k,
                                part_chaude=part_chaude)
        vus += int(bool(le_groupement(c, tirages, int(graine) + k).get("ca_se_groupe")))
    return {"vus": int(vus), "replicats": int(replicats),
            "la_part": float(vus) / float(replicats)}


def la_force_quil_faut(positions, echelle=(0.0, 2.0, 4.0, 8.0, 16.0),
                       replicats: int = REPLICATS, tirages: int = PERMUTATIONS,
                       graine: int = GRAINE, part_chaude: float = 0.1) -> dict:
    """La plus petite force de l'échelle vue à TOUS les réplicats — dérivée, pas choisie."""
    courbe, trouvee = [], None
    for f in echelle:
        x = la_part_vue(positions, f, True, replicats, tirages, graine, part_chaude)
        courbe.append({"force": float(f), "part_des_replicats": float(x["la_part"])})
        if trouvee is None and x["la_part"] >= 1.0:
            trouvee = float(f)
    return {"la_courbe": courbe, "la_force_quil_faut": trouvee, "replicats": int(replicats),
            "les_positions": len(list(positions))}


def sur_letalon(positions, tirages: int = PERMUTATIONS, graine: int = GRAINE,
                replicats: int = REPLICATS, part_chaude: float = 0.1,
                garantie: float = 1.0 / (PERMUTATIONS + 1),
                echelle=(0.0, 2.0, 4.0, 8.0, 16.0)) -> dict:
    """Les deux faces de la question, MESURÉES SUR RÉPLICATS toutes les deux.

    ⚠⚠⚠ ET LA FACE NEGATIVE EST JUGEE SUR SON TAUX, PAS SUR UN TIRAGE : le dispositif se trompe une
    fois sur vingt par construction, donc une unique carte dispersee declaree groupee ne dit rien —
    et c'est pourtant ce qui avait fait rendre « l'etalon ne separe pas » a la premiere mesure.
    """
    pts = [(int(p[0]), int(p[1])) for p in positions]
    f = la_force_quil_faut(pts, echelle=echelle, replicats=replicats, tirages=tirages,
                           graine=graine, part_chaude=part_chaude)
    force = f["la_force_quil_faut"]
    if force is None:
        # ⚠⚠ LES DEUX BRANCHES RENDENT LES MEMES CHAMPS, et c'est un defaut qui a fait tomber une
        # sonde : un dictionnaire dont la FORME depend du succes est un piege pour tout ce qui le
        # lit. Ici les valeurs manquent, la structure non.
        return {"la_sensibilite": f, "la_force_posee": None, "le_taux_de_faux": None,
                "les_faux": None, "la_garantie": float(garantie),
                "la_part_chaude": float(part_chaude), "le_taux_de_faux_tient": None,
                "letalon_separe": False}
    faux = la_part_vue(pts, force, False, replicats, tirages, graine, part_chaude)
    tient = le_taux_tient_la_garantie(faux["vus"], faux["replicats"], float(garantie))
    return {"la_sensibilite": f, "la_force_posee": float(force),
            "le_taux_de_faux": float(faux["la_part"]), "les_faux": int(faux["vus"]),
            "la_garantie": float(garantie), "la_part_chaude": float(part_chaude),
            "le_taux_de_faux_tient": tient,
            "letalon_separe": bool(f["la_courbe"] and tient["il_tient"])}


def mesurer(cote: int = COTE_DE_LA_CARTE, delai: float = DELAI, tirages: int = PERMUTATIONS,
            graine: int = GRAINE, replicats: int = REPLICATS, ouvrir=None, meta=None) -> dict:
    """La carte d'un segment entier, ses quantiles, et la seule question déclarée."""
    v = le_segment_declare()
    if v is None:
        return {"decidable": False, "raison": "aucun volume recensé"}
    c = la_carte(v, cote, delai, ouvrir, meta)
    if not c.get("decidable"):
        return {"decidable": False, "raison": c.get("raison", "la carte est vide"),
                "la_carte": {k: x for k, x in c.items() if k != "les_positions"}}
    # ⚠⚠⚠ UNE CARTE MESUREE A TRAVERS UN LIEN QUI TOMBE N'EST PAS UNE CARTE : le compte de positions
    # sans surface serait alors un compte de requetes perdues. Le refus est la seule reponse juste,
    # et il nomme ce qui a manque.
    pannes = les_pannes_de_reseau(c.get("refuses"))
    if pannes:
        return {"decidable": False,
                "raison": f"{pannes} positions perdues par le réseau — un compte de couverture "
                          f"mesuré à travers un lien qui tombe n'en est pas un",
                "la_carte": {k: x for k, x in c.items() if k != "les_positions"}}
    lues = c["les_positions"]
    return {
        "graine": int(graine), "tirages": int(tirages),
        "la_question_declaree": LA_QUESTION_DECLAREE,
        "le_cote_de_la_carte": int(cote),
        "le_pas_dun_pli_en_voxels": round(float(PAS_EN_VOXELS), 4),
        "la_plage_de_recalage": int(DEMI_PAS_EN_VOXELS),
        "le_decile_du_pire": float(LE_DECILE_DU_PIRE),
        "la_carte": {k: x for k, x in c.items() if k != "les_positions"},
        "les_positions": lues,
        "les_quantiles": les_quantiles(lues),
        "le_groupement": le_groupement(lues, tirages, graine),
        # ⭐⭐⭐⭐ L'ETALON EST POSE SUR LES POSITIONS REELLEMENT LUES, trous compris, et sur la meme
        # part chaude que le pire decile : `193` a mesure qu'un etalon pose ailleurs ne dit rien.
        "letalon": sur_letalon([x["position"] for x in lues], tirages, graine, replicats,
                               part_chaude=1.0 - LE_DECILE_DU_PIRE / 100.0),
    }


def afficher(r: dict) -> None:
    if not r.get("decidable", True):
        print(f"OÙ LE MAILLAGE QUITTE SON FEUILLET   indécidable : {r.get('raison')}")
        return
    c, q, g = r["la_carte"], r["les_quantiles"], r["le_groupement"]
    print(f"OÙ LE MAILLAGE QUITTE SON FEUILLET   segment {c['segment']} · grille "
          f"{c['grille_de_chunks'][0]}×{c['grille_de_chunks'][1]} chunks · treillis "
          f"{r['le_cote_de_la_carte']}×{r['le_cote_de_la_carte']}")
    print(f"  LA CARTE          {c['positions_lues']} lues sur {c['positions_du_treillis']} · "
          f"refus {c['refuses'] or '—'}")
    print(f"  LES QUANTILES     médian {q['le_median_en_voxels']} vx "
          f"({q['le_median_en_plis']} pli) · décile haut {q['le_decile_haut_en_voxels']} · "
          f"maximal {q['le_maximal_en_voxels']} · saturent {q['les_positions_qui_saturent']} "
          f"({q['la_part_qui_sature']})")
    if g.get("decidable"):
        print(f"  LE GROUPEMENT     {g['les_positions_du_pire_decile']} positions au-delà de "
              f"{g['le_seuil_du_pire_decile']} vx · distance {g['la_distance_moyenne']} contre "
              f"{g['la_distance_moyenne_du_nul']} au nul · "
              f"{g['les_melanges_au_moins_aussi_serres']} mélanges au moins aussi serrés · "
              f"se groupe {g['ca_se_groupe']}")
    else:
        print(f"  LE GROUPEMENT     indécidable : {g.get('raison')}")
    e = r["letalon"]
    print(f"  L'ÉTALON          sépare {e['letalon_separe']} · force dérivée "
          f"{e['la_force_posee']} · taux de faux {e['le_taux_de_faux']} pour "
          f"{e['la_garantie']} garantis · courbe " + " · ".join(
              f"{int(x['force'])}→{x['part_des_replicats']:g}"
              for x in e["la_sensibilite"]["la_courbe"]))


def verifier() -> int:
    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        if not ok:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    v("★★ une seule question est déclarée", isinstance(LA_QUESTION_DECLAREE, str),
      LA_QUESTION_DECLAREE)
    v("★★ le pire décile est RELU de `197`, pas choisi", LE_DECILE_DU_PIRE == LES_DECILES[1],
      str(LE_DECILE_DU_PIRE))
    premiers = les_volumes(combien=1)
    v("★★ le segment est le PREMIER du recensement, jamais choisi",
      (le_segment_declare() or {}).get("segment")
      == (premiers[0]["segment"] if premiers else None))

    # ⭐⭐⭐⭐ LES QUANTILES SE VERIFIENT SUR UNE CARTE CONSTRUITE.
    faux = [{"position": [i, 0], "le_serpentement_en_voxels": float(i),
             "les_colonnes_saturees": 1 if i > 7 else 0} for i in range(10)]
    q = les_quantiles(faux)
    v("★★★ le médian est celui des valeurs", abs(q["le_median_en_voxels"] - 4.5) < 1e-9,
      str(q["le_median_en_voxels"]))
    v("★★★ le décile haut aussi", abs(q["le_decile_haut_en_voxels"] - 8.1) < 1e-6,
      str(q["le_decile_haut_en_voxels"]))
    v("★★★ et le maximal", abs(q["le_maximal_en_voxels"] - 9.0) < 1e-9)
    v("★★★★ la part qui sature est comptée, jamais tue",
      q["les_positions_qui_saturent"] == 2 and abs(q["la_part_qui_sature"] - 0.2) < 1e-9,
      f"{q['les_positions_qui_saturent']} / {q['la_part_qui_sature']}")
    v("★★ le médian est rendu en plis aussi",
      abs(q["le_median_en_plis"] - 4.5 / PAS_EN_VOXELS) < 1e-6)
    v("une carte vide est indécidable", les_quantiles([]).get("decidable") is False)

    # ⭐⭐⭐⭐ LES DEUX FACES DU GROUPEMENT, A FORCE EGALE.
    gr = le_groupement(une_carte_fabriquee(un_treillis(12), 40.0, True, 11), 19, 11)
    v("★★★★ un groupement posé est vu comme groupé", gr["ca_se_groupe"],
      f"{gr['la_distance_moyenne']} contre {gr['la_distance_moyenne_du_nul']}")
    di = le_groupement(une_carte_fabriquee(un_treillis(12), 40.0, False, 11), 19, 11)
    v("★★★★ et une dispersion posée ne l'est PAS", not di["ca_se_groupe"],
      f"{di['la_distance_moyenne']} contre {di['la_distance_moyenne_du_nul']}")
    # ⚠⚠⚠ LA PREMIERE VERSION DE CETTE SONDE COMPARAIT `les_positions_du_pire_decile`, qui est
    # calcule sur le DECILE des valeurs et vaut donc toujours un dixieme du treillis quel que soit le
    # nombre de positions chaudes injectees. Un bris qui donnait trois fois moins de chaudes a la
    # face dispersee la laissait verte. Ce qui se verifie est le compte INJECTE.
    cg = sum(1 for x in une_carte_fabriquee(un_treillis(12), 40.0, True, 11) if x["chaude"])
    cd = sum(1 for x in une_carte_fabriquee(un_treillis(12), 40.0, False, 11) if x["chaude"])
    v("★★★★ les deux faces INJECTENT le même nombre de positions chaudes", cg == cd,
      f"{cg} contre {cd}")
    v("★★★ et ce nombre est le dixième du treillis, dérivé et non tapé",
      cg == max(2, int(round(0.1 * 144))), f"{cg} pour 144 positions")

    # ⚠⚠⚠ LE NUL DOIT TIRER EXACTEMENT AUTANT DE POSITIONS QUE L'OBSERVE, ET ON LE VERIFIE PAR UNE
    # IDENTITE : sur une carte ou toutes les valeurs sont EGALES, le pire decile est le treillis
    # entier, donc chaque melange retire le treillis entier et sa distance vaut exactement
    # l'observee. Un nul qui tirerait moins de points la ferait diverger.
    plate = [{"position": [y, x], "le_serpentement_en_voxels": 3.0,
              "les_colonnes_saturees": 0} for y in range(6) for x in range(6)]
    gp = le_groupement(plate, 19, 11)
    v("★★★★ le nul tire EXACTEMENT autant de positions que l'observé",
      gp["decidable"] and abs(gp["la_distance_moyenne"]
                              - gp["la_distance_moyenne_du_nul"]) < 1e-9,
      f"{gp.get('la_distance_moyenne')} contre {gp.get('la_distance_moyenne_du_nul')}")
    v("★★★ et une carte entièrement égale ne se groupe donc pas", not gp["ca_se_groupe"],
      str(gp["les_melanges_au_moins_aussi_serres"]))
    v("★★ une carte trop petite est indécidable",
      le_groupement([{"position": [0, 0], "le_serpentement_en_voxels": 1.0}]).get("decidable")
      is False)

    t12 = un_treillis(12)
    f = la_force_quil_faut(t12, echelle=(0.0, 40.0), replicats=5, tirages=19, graine=11)
    v("★★★★ la force rendue est vue à TOUS les réplicats",
      f["la_force_quil_faut"] is not None
      and la_part_vue(t12, f["la_force_quil_faut"], True, 5, 19, 11)["la_part"] >= 1.0,
      str(f["la_force_quil_faut"]))
    v("★★★★ et une force nulle n'est PAS vue à tous les réplicats",
      la_part_vue(t12, 0.0, True, 5, 19, 11)["la_part"] < 1.0,
      str(la_part_vue(t12, 0.0, True, 5, 19, 11)["la_part"]))
    v("★★★ la courbe entière est publiée", len(f["la_courbe"]) == 2,
      str([x["part_des_replicats"] for x in f["la_courbe"]]))
    # ⚠⚠⚠ LA FACE NEGATIVE PASSE PAR LA MEME FONCTION, SUR REPLICATS.
    tf = la_part_vue(t12, 40.0, False, 20, 19, 11)
    tt = le_taux_tient_la_garantie(tf["vus"], tf["replicats"], 1.0 / (PERMUTATIONS + 1))
    v("★★★★ le taux de faux d'une carte DISPERSÉE est COMPATIBLE avec la garantie",
      tt["il_tient"], f"{tf['vus']} faux sur {tf['replicats']}, probabilité "
      f"{round(tt['la_probabilite_den_avoir_autant'], 6)}")
    v("★★★★ tandis que la face groupée est vue à tous les réplicats",
      la_part_vue(t12, 40.0, True, 20, 19, 11)["la_part"] >= 1.0)
    # ⚠⚠ ET LE CRITERE SAIT DIRE NON : un dispositif qui se tromperait la moitie du temps ne tient
    # pas, tandis que deux faux sur vingt tiennent — ce que « inferieur a la garantie » refusait.
    v("★★★★ deux faux sur vingt tiennent la garantie",
      le_taux_tient_la_garantie(2, 20, 0.05)["il_tient"],
      str(round(le_taux_tient_la_garantie(2, 20, 0.05)["la_probabilite_den_avoir_autant"], 6)))
    v("★★★★ mais dix faux sur vingt ne la tiennent PAS",
      not le_taux_tient_la_garantie(10, 20, 0.05)["il_tient"],
      str(le_taux_tient_la_garantie(10, 20, 0.05)["la_probabilite_den_avoir_autant"]))
    v("★★★ et zéro faux la tient trivialement",
      le_taux_tient_la_garantie(0, 20, 0.05)["il_tient"])
    # ⭐⭐⭐⭐ ET L'ETALON SE POSE SUR UNE CARTE TROUEE, COMME LA VRAIE.
    troue = [p for i, p in enumerate(t12) if i % 4]
    v("★★★ un étalon posé sur une carte trouée garde ses positions",
      len(une_carte_fabriquee(troue, 40.0, True, 11)) == len(troue),
      f"{len(troue)} positions")

    # ⚠⚠⚠ LE PARCOURS S'EXERCE SANS RESEAU, ET IL COMPTE CE QUI NE REPOND PAS PAR SA RAISON.
    def _faux_ouvrir(vides=(), absents=(), plats=(), coupes=(), repris=None):
        repris = repris or {}

        def _prendre(cy, cx):
            if (cy, cx) in coupes:
                return None, f"{LE_RESEAU_A_ECHOUE} : transport : coupure"
            if (cy, cx) in absents:
                return None, ABSENT_DU_DEPOT
            if (cy, cx) in vides:
                return np.zeros((16, 8, 6)), None
            if (cy, cx) in plats:
                return np.full((16, 8, 6), 120.0), None
            z = np.arange(16, dtype=float)[:, None, None]
            onde = 120.0 + 40.0 * np.cos(2.0 * np.pi * z / 8.0)
            bloc = np.broadcast_to(onde, (16, 8, 6)) + float(cy)
            n = repris.get((cy, cx))
            return bloc, (f"repris {int(n)}" if n else None)
        return _prendre

    grille = [(y, x) for y in range(4) for x in range(4)]
    pc = le_parcours(grille, _faux_ouvrir(vides={(0, 0), (1, 1)}, absents={(2, 2)},
                                          plats={(3, 3)}))
    v("★★★★ une position absente est comptée par sa RAISON, jamais lue",
      pc["refuses"].get(ABSENT_DU_DEPOT) == 1, str(pc["refuses"]))
    v("★★★★ une position VIDE est comptée comme vide, pas comme un serpentement nul",
      pc["refuses"].get("vide") == 2, str(pc["refuses"]))
    v("★★★ une coupe au profil plat est comptée par sa raison",
      pc["refuses"].get("profil moyen plat") == 1, str(pc["refuses"]))
    v("★★★ et les autres positions sont lues",
      len(pc["lues"]) == len(grille) - 4, f"{len(pc['lues'])} sur {len(grille)}")
    v("★★★ chaque position lue porte son adresse",
      all(len(x["position"]) == 2 for x in pc["lues"]))
    v("★★ un parcours sans position ne lit rien et ne refuse rien",
      le_parcours([], _faux_ouvrir()) == {"lues": [], "refuses": {}, "reprises": 0})

    v("★★ un volume qui ne répond pas rend une carte indécidable",
      la_carte({"segment": "S", "cle": "pas/un/zarr"}, 3, 0.01).get("decidable") is False)

    # ⚠⚠⚠ LE TREILLIS COUVRE LE SEGMENT ENTIER, ET C'EST LA SEULE RAISON D'ETRE DE LA TRANCHE : une
    # carte qui n'en visiterait qu'un coin repondrait a la question de `197`, pas a celle-ci.
    faux_meta = {"chunks": [16, 8, 6], "shape": [16, 8 * 40, 6 * 40], "dtype": "|u1"}
    for c_ in (4, 7):
        carte = la_carte({"segment": "S", "cle": "x"}, c_, 0.01,
                         ouvrir=_faux_ouvrir(), meta=faux_meta)
        v(f"★★★★ un treillis de {c_} couvre {c_ * c_} positions",
          carte["positions_du_treillis"] == c_ * c_,
          f"{carte['positions_du_treillis']} positions")
        ys = sorted({p["position"][0] for p in carte["les_positions"]})
        xs = sorted({p["position"][1] for p in carte["les_positions"]})
        v(f"★★★★ et il va d'un bord à l'autre de la grille à {c_}",
          ys[0] == 0 and ys[-1] == 39 and xs[0] == 0 and xs[-1] == 39,
          f"lignes {ys[0]}..{ys[-1]}, colonnes {xs[0]}..{xs[-1]}")
    ct = la_carte({"segment": "S", "cle": "x"}, 4, 0.01, ouvrir=_faux_ouvrir(absents={(0, 0)}),
                  meta=faux_meta)
    v("★★★★ les coordonnées du treillis sont publiées, trous compris",
      len(ct["les_lignes_du_treillis"]) == 4 and len(ct["les_colonnes_du_treillis"]) == 4,
      f"{ct['les_lignes_du_treillis']} × {ct['les_colonnes_du_treillis']}")
    v("★★★★ et elles contiennent une position que PERSONNE n'a lue",
      0 in ct["les_lignes_du_treillis"] and 0 in ct["les_colonnes_du_treillis"]
      and [0, 0] not in [x["position"] for x in ct["les_positions"]],
      "la position (0,0) est dans le treillis et absente des lues")
    # ⚠⚠⚠ UN CHUNK ABSENT DU DEPOT ET UNE PANNE DE RESEAU NE SE COMPTENT PAS ENSEMBLE, ET LA MESURE
    # REFUSE LA SECONDE : c'est le defaut qu'une coupure de connexion a revele en faisant passer les
    # positions lues de 189 a 110 sans que rien ne le dise.
    # ⚠⚠⚠ LA REGLE ELLE-MEME SE SONDE, ET NON SEULEMENT SES APPELANTS.
    meta_un = {"chunks": [4, 2, 2], "shape": [4, 8, 8], "dtype": "|u1",
               "compressor": None, "codec": None}
    for retour, attendu in ((("absent",), ABSENT_DU_DEPOT),
                            (("transport : coupure",), LE_RESEAU_A_ECHOUE),
                            (("delai depasse",), LE_RESEAU_A_ECHOUE),
                            (("http 500",), LE_RESEAU_A_ECHOUE)):
        _b, pourquoi = un_chunk("u", meta_un, 0, 0, 1.0,
                                chercher=lambda _u, _t, r=retour[0]: (None, r))
        v(f"★★★★ « {retour[0]} » est classé « {attendu} »",
          str(pourquoi).startswith(attendu), f"{pourquoi}")

    # ⭐⭐⭐⭐ UNE PANNE DE TRANSPORT SE REDEMANDE, UN 404 NON — et c'est ce qui distingue les deux
    # EMPIRIQUEMENT plutot que par le seul code d'erreur.
    essais = {"n": 0}

    def _capricieux(_u, _t):
        essais["n"] += 1
        if essais["n"] <= 2:
            return None, "transport : coupure"
        return b"\x00" * (4 * 2 * 2), None

    meta_r = {"chunks": [4, 2, 2], "shape": [4, 8, 8], "dtype": "|u1",
              "compressor": None, "codec": None}
    b_, p_ = un_chunk("u", meta_r, 0, 0, 1.0, chercher=_capricieux, reprises=3)
    v("★★★★ une panne de transport est REDEMANDÉE, et le chunk finit par être lu",
      b_ is not None and str(p_).startswith("repris"), f"{p_} après {essais['n']} essais")
    essais2 = {"n": 0}

    def _toujours_casse(_u, _t):
        essais2["n"] += 1
        return None, "transport : coupure"

    _b2, p2_ = un_chunk("u", meta_r, 0, 0, 1.0, chercher=_toujours_casse, reprises=3)
    v("★★★★ mais une panne qui PERSISTE reste une panne, après le budget de reprises",
      str(p2_).startswith(LE_RESEAU_A_ECHOUE) and essais2["n"] == 4,
      f"{p2_} après {essais2['n']} essais")
    essais3 = {"n": 0}

    def _absent(_u, _t):
        essais3["n"] += 1
        return None, "absent"

    _b3, p3_ = un_chunk("u", meta_r, 0, 0, 1.0, chercher=_absent, reprises=3)
    v("★★★★ tandis qu'un 404 n'est JAMAIS redemandé : c'est une réponse",
      p3_ == ABSENT_DU_DEPOT and essais3["n"] == 1, f"{essais3['n']} essai(s)")

    # ⚠⚠⚠ UNE POSITION REPRISE EST UNE POSITION LUE, PAS UN REFUS : la compter comme un refus
    # ferait disparaitre de la carte tout ce que le fil a fait redemander, donc ferait un trou de
    # maillage la ou il n'y en a pas.
    pc3 = le_parcours(grille, _faux_ouvrir(repris={(0, 0): 1, (1, 1): 2}))
    v("★★★★ une position REPRISE est comptée comme lue, jamais comme un refus",
      len(pc3["lues"]) == len(grille) and not pc3["refuses"],
      f"{len(pc3['lues'])} lues, refus {pc3['refuses']}")
    v("★★★★ et le compte de reprises dit combien de fois le fil a flanché",
      pc3["reprises"] == 3, str(pc3["reprises"]))
    v("★★ un parcours sans reprise en compte zéro",
      le_parcours(grille, _faux_ouvrir())["reprises"] == 0)

    pc2 = le_parcours(grille, _faux_ouvrir(absents={(0, 1)}, coupes={(1, 2), (2, 3)}))
    v("★★★★ une panne de réseau est comptée À PART d'un chunk absent du dépôt",
      pc2["refuses"].get(ABSENT_DU_DEPOT) == 1
      and les_pannes_de_reseau(pc2["refuses"]) == 2, str(pc2["refuses"]))
    # ⚠⚠⚠ L'ATTENTE SE SONDE SANS DORMIR : c'est une fonction pure, donc elle se verifie.
    v("★★★★ l'attente DOUBLE d'un essai à l'autre",
      [lattente_avant_le_prochain_essai(k, 0.5) for k in range(4)] == [0.5, 1.0, 2.0, 4.0],
      str([lattente_avant_le_prochain_essai(k, 0.5) for k in range(4)]))
    v("★★★★ et une base nulle la supprime, donc rien d'antérieur ne change",
      all(lattente_avant_le_prochain_essai(k, 0.0) == 0.0 for k in range(4)))
    v("★★★ trois reprises à une demi-seconde couvrent trois secondes et demie",
      abs(sum(lattente_avant_le_prochain_essai(k, 0.5) for k in range(3)) - 3.5) < 1e-9,
      str(sum(lattente_avant_le_prochain_essai(k, 0.5) for k in range(3))))
    v("★★★ et le compte de pannes ramasse toutes les raisons de transport",
      les_pannes_de_reseau({f"{LE_RESEAU_A_ECHOUE} : a": 3,
                            f"{LE_RESEAU_A_ECHOUE} : b": 4, ABSENT_DU_DEPOT: 9}) == 7)
    v("★★ et il vaut zéro quand rien n'a été perdu par le fil",
      les_pannes_de_reseau({ABSENT_DU_DEPOT: 9, "illisible": 2}) == 0)
    m_coupe = mesurer(cote=5, delai=0.01, tirages=19, graine=11, replicats=3,
                      ouvrir=_faux_ouvrir(coupes={(0, 0)}), meta=faux_meta)
    v("★★★★ une carte dont le RÉSEAU a lâché est REFUSÉE, jamais publiée",
      m_coupe.get("decidable") is False and "réseau" in str(m_coupe.get("raison")),
      str(m_coupe.get("raison"))[:100])
    m_abs = mesurer(cote=5, delai=0.01, tirages=19, graine=11, replicats=3,
                    ouvrir=_faux_ouvrir(absents={(0, 0)}), meta=faux_meta)
    v("★★★★ tandis qu'une carte à trous de MAILLAGE est publiée avec son compte",
      m_abs.get("decidable", True)
      and m_abs["la_carte"]["refuses"].get(ABSENT_DU_DEPOT) == 1,
      str(m_abs["la_carte"]["refuses"]))

    # ⚠⚠⚠ LE CHEMIN PAR DEFAUT DE LA CARTE SE SONDE AUSSI : toutes les sondes injectent un ouvreur,
    # donc la ligne qui choisit le lecteur reel n'etait visitee par AUCUNE — et une reference morte
    # y a survecu jusqu'a ce que la mesure plante en plein telechargement.
    cd_ = la_carte({"segment": "S", "cle": "x"}, 3, 0.01, meta=faux_meta,
                   chercher=lambda _u, _t: (None, "transport : coupure"))
    v("★★★★ le chemin PAR DÉFAUT de la carte passe bien par `un_chunk`",
      les_pannes_de_reseau(cd_.get("refuses")) == cd_["positions_du_treillis"],
      f"{cd_.get('refuses')}")
    v("★★★ et une carte dont tout a échoué n'est pas décidable",
      cd_.get("decidable") is False)

    v("★★★ la grille de chunks est celle que les métadonnées disent",
      la_carte({"segment": "S", "cle": "x"}, 4, 0.01, ouvrir=_faux_ouvrir(),
               meta=faux_meta)["grille_de_chunks"] == [40, 40])

    # ⭐⭐⭐⭐ LA MESURE ENTIERE S'EXERCE SANS RESEAU, ET C'EST CE QUI PERMET DE VERIFIER QUE L'ETALON
    # EST POSE SUR LES POSITIONS REELLEMENT LUES : un etalon pose sur un treillis plein repondrait a
    # la question d'une carte que personne n'a mesuree.
    m = mesurer(cote=5, delai=0.01, tirages=19, graine=11, replicats=3,
                ouvrir=_faux_ouvrir(absents={(0, 0), (39, 39)}), meta=faux_meta)
    v("★★★ une mesure entière se fait sans réseau", m.get("decidable", True)
      and m["la_carte"]["positions_lues"] == 23, str(m.get("raison"))[:80])
    v("★★★★ l'étalon est posé sur EXACTEMENT les positions lues",
      m["letalon"]["la_sensibilite"]["les_positions"] == m["la_carte"]["positions_lues"],
      f"{m['letalon']['la_sensibilite']['les_positions']} contre "
      f"{m['la_carte']['positions_lues']}")
    v("★★★ et sa part chaude est celle du pire décile, dérivée et non tapée",
      abs(m["letalon"]["la_part_chaude"] - (1.0 - LE_DECILE_DU_PIRE / 100.0)) < 1e-9,
      str(m["letalon"].get("la_part_chaude")))

    nom = "ou_le_maillage_quitte_t_il_son_feuillet.py"
    e = sur_letalon(t12, 19, 11, 10)
    v("★★★★ l'étalon sépare ses deux faces, les DEUX mesurées sur réplicats",
      e["letalon_separe"],
      f"force {e['la_force_posee']}, taux de faux {e['le_taux_de_faux']} pour une garantie de "
      f"{e['la_garantie']}")
    v("★★★ et sa force est DÉRIVÉE de la sensibilité",
      e["la_sensibilite"]["la_force_quil_faut"] is not None,
      str(e["la_sensibilite"]["la_force_quil_faut"]))
    # ⚠⚠⚠ UN ETALON DONT AUCUNE FORCE N'EST VUE NE SEPARE PAS, ET IL LE DIT : sans cette face, un
    # dispositif aveugle rendrait « separe » en n'ayant jamais rien vu.
    aveugle = sur_letalon(t12, 19, 11, 5, echelle=(0.0,))
    v("★★★★ un étalon dont aucune force n'est vue ne sépare PAS",
      not aveugle["letalon_separe"] and aveugle["la_force_posee"] is None,
      str(aveugle["la_force_posee"]))
    v("★★★ et il ne publie alors aucun taux de faux, jamais zéro",
      aveugle["le_taux_de_faux"] is None)
    # ⚠⚠⚠ LES DEUX FACES DOIVENT ETRE MESUREES SUR LE MEME NOMBRE DE REPLICATS, et c'est un
    # invariant structurel : un bris qui ramenait la face negative a UN tirage rendait « separe »
    # sans que rien ne le voie, puisque zero faux sur un tirage tient n'importe quelle garantie.
    v("★★★★ la face négative est mesurée sur AUTANT de réplicats que la positive",
      e["le_taux_de_faux_tient"]["replicats"] == e["la_sensibilite"]["replicats"],
      f"{e['le_taux_de_faux_tient']['replicats']} contre "
      f"{e['la_sensibilite']['replicats']}")

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
