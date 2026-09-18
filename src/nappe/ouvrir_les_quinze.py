"""Ouvrir les quinze — et le faire À L'AVEUGLE, parce que l'œil est un maximiseur sans liste.

⭐⭐⭐⭐ POURQUOI CE FICHIER, ET C'EST `R4-P43` QUI LE NOMME. `194` établit que l'étiquette de `190`
est RÉELLE — **15** chunks sur **81** contre **6,075** attendus, probabilité **0,000937548** — et
qu'elle n'a aucune structure : les segments ne diffèrent pas, les chunks retenants ne se groupent
pas, et aucun des **31** observables déclarés par `191` et `193` ne les touche. Il reste donc une
propriété du chunk, réelle, que rien de ce qui est mesuré ne nomme. Or la chaîne a compté ces quinze
chunks, les a permutés et corrélés, et ne les a **JAMAIS OUVERTS**.

⭐ Et ce dépôt sait ce que ça vaut : `186` a trouvé un défaut en REGARDANT une image, `187` a vu deux
hypothèses fausses céder devant un INSTRUMENT.

⚠⚠⚠ MAIS LE PIÈGE EST ÉCRIT D'AVANCE, ET IL EST LE PIRE DE LA CHAÎNE. Regarder quinze cubes et y
trouver un trait commun EST une maximisation sans liste déclarée — l'œil choisit son observable après
coup et ne le déclare jamais, donc il ne peut rien payer. `191` a payé **19** observables et `193`
**12** ; un œil libre en a une infinité.

⭐⭐⭐⭐ LA SORTIE EST DE RENVERSER CE QUE L'ŒIL DÉCLARE. Il ne déclare pas un TRAIT, il déclare une
ASSIGNATION : quinze tuiles parmi trente, désignées sur une planche où rien ne dit lesquelles
retiennent. Une assignation est UN objet, pas une famille, et son nul est EXACT — c'est la loi
hypergéométrique, comme le compte global de `194` est exactement binomial. L'œil peut alors chercher
ce qu'il veut, aussi longtemps qu'il veut : ce qui est noté est son unique réponse.

⚠⚠ ET LE CONTRÔLE APPARIÉ EST DANS LA PLANCHE ELLE-MÊME. Les quinze qui ne retiennent pas sont tirés
DANS LE MÊME SEGMENT que ceux qu'ils apparient, parce que `193` a mesuré que deux chunks d'un même
segment ne sont pas échangeables. Chercher un trait chez les quinze sans le chercher chez eux serait
exactement l'erreur que la porte annonce.

⚠⚠⚠ ET CE QUE L'AVEUGLE ACHÈTE EST DIT PLUTÔT QUE SURVENDU : il est de PROCÉDURE, pas de serrure. La
planche est produite par un chemin qui n'appelle jamais la fonction qui calcule la clef, donc
l'artefact aveugle ne la porte pas ; mais le code sait la calculer. Ce que le dispositif rend
impossible est la maximisation INCONSCIENTE — pas le mensonge délibéré.

Usage :
    uv run python src/nappe/ouvrir_les_quinze.py --verifier
    uv run python src/nappe/ouvrir_les_quinze.py --aveugle \\
        --json docs/mesures/ouvrir_les_quinze.json
    uv run python src/nappe/ouvrir_les_quinze.py --lever \\
        --json docs/mesures/ouvrir_les_quinze.json
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

from la_recette_posee_sur_le_rouleau import DELAI, les_volumes  # noqa: E402
from ou_le_chunk_se_trouve_t_il import les_etiquettes  # noqa: E402
from zarr_depth import BUCKET, array_meta, chunk_key, decode, get  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
GRAINE = 20261004

# ⚠⚠ LA GARANTIE EST CELLE DE LA CHAINE DEPUIS `176`, RELUE ET NON CHOISIE : un sur vingt. Ici elle
# ne se paie pas en permutations mais en arithmetique exacte, parce qu'une assignation tiree au
# hasard suit une loi sans remise dont chaque terme se calcule.
GARANTIE = 0.05

# ⚠⚠ LA PRECISION PUBLIEE EST DERIVEE DE LA PLANCHE, PAS CHOISIE : la plus petite masse que la loi
# exacte porte vaut l'inverse du nombre de facons de choisir quinze tuiles sur trente, soit environ
# six milliardiemes. Sept decimales sont donc ce qu'il faut pour distinguer toutes les queues sauf
# les deux plus extremes, qui sont deja sous la garantie de plusieurs ordres de grandeur.
DECIMALES = 7

# ⚠⚠⚠ LA COUCHE MONTREE EST NOMMEE PAR L'ARITHMETIQUE, JAMAIS PAR CE QU'ELLE MONTRE. Le milieu d'un
# cube est la seule couche qu'on puisse designer sans avoir regarde aucune des trente ; choisir
# « la plus texturee » ou « celle ou le creux tombe » serait deja une maximisation, et ce serait
# celle-la, exactement, que la porte interdit.
def la_couche_montree(profond: int) -> int:
    """Le milieu du cube — la seule couche nommable sans regarder aucun cube."""
    return int(profond) // 2


# ⚠⚠⚠ LE NIVEAU EST COMMUN AUX TRENTE TUILES, ET C'EST UNE DECISION. Une normalisation PAR TUILE
# rendrait toutes les tuiles egalement contrastees, donc effacerait la luminosite et le contraste —
# deux traits que ni `191` ni `193` n'ont declares, donc deux traits que personne n'a encore payes.
# Un niveau commun, tire du melange des trente, est symetrique entre les deux camps et ne cache rien.
LE_NIVEAU_COMMUN = (1.0, 99.0)

COLONNES_DE_LA_PLANCHE = 6
RANGS_DE_LA_PLANCHE = 5
LES_TUILES = COLONNES_DE_LA_PLANCHE * RANGS_DE_LA_PLANCHE

# ⚠⚠ L'ECHELLE DE FORCE EST DERIVEE DU FORMAT, PAS CHOISIE, ET SON UNITE EST CELLE DU VOLUME : le
# depot publie ses volumes en octets, donc le plus petit ecart que la matiere sache porter vaut UN,
# et l'echelle double a chaque barreau jusqu'au quart de la dynamique. Un barreau n'est PAS un niveau
# de gris de la planche — le niveau commun ne couvre qu'une part de la dynamique, et le rapport des
# deux est publie a cote plutot que suppose.
LECHELLE_DE_FORCE = (0, 1, 2, 4, 8, 16, 32, 64)
REPLICATS = 20

# ⚠⚠⚠ LA LECTURE EST ECRITE ICI, EN CLAIR, ET ELLE EST UNIQUE. Quinze numeros de tuile, lus sur
# `docs/images/195_la_planche_a_laveugle.png` et sur rien d'autre. Un tuple vide veut dire « personne
# n'a encore regarde » — jamais « l'œil n'a rien trouve », qui est un resultat et se note.
LA_LECTURE_A_LAVEUGLE: tuple[int, ...] = (3, 8, 9, 10, 12, 13, 15, 17, 19, 21, 23, 26, 27, 28, 30)
CE_QUE_LŒIL_A_CRU_VOIR = (
    "une striation de fibres PARALLÈLES, continue et d'une seule direction, traversant la tuile "
    "— une feuille bien définie, ni grumeleuse ni vide"
)


def _rng(graine: int) -> np.random.Generator:
    return np.random.default_rng(int(graine))


def apparier(etiquettes: dict, graine: int = GRAINE) -> dict:
    """Chaque chunk qui retient reçoit un chunk qui ne retient pas, TIRÉ DANS SON PROPRE SEGMENT.

    ⭐⭐⭐⭐ L'APPARIEMENT PAR SEGMENT EST CE QUI REND LA PLANCHE LISIBLE. `193` a mesuré que les
    chunks d'un même segment ne sont pas échangeables ; un contrôle tiré n'importe où ferait donc
    voir à l'œil la différence entre deux segments et non entre deux étiquettes, et il la verrait —
    ce serait un vrai trait, répondant à une autre question que celle posée.

    ⚠ Un retenant dont le segment n'a plus de non-retenant disponible est ÉCARTÉ avec son camp,
    jamais apparié ailleurs : une paire boiteuse déséquilibrerait la loi exacte qui suppose quinze
    contre quinze.
    """
    par_segment: dict[str, dict[str, list]] = {}
    for (seg, cy, cx), v in etiquettes.items():
        d = par_segment.setdefault(seg, {"retiennent": [], "non": []})
        d["retiennent" if v["etiquette"] else "non"].append((seg, int(cy), int(cx)))
    paires, sans_paire = [], 0
    r = _rng(graine)
    for seg in sorted(par_segment):
        d = par_segment[seg]
        chauds = sorted(d["retiennent"])
        froids = sorted(d["non"])
        ordre = list(r.permutation(len(froids))) if froids else []
        for i, chaud in enumerate(chauds):
            if i >= len(ordre):
                sans_paire += 1
                continue
            paires.append({"segment": seg, "retient": list(chaud[1:]),
                           "controle": list(froids[int(ordre[i])][1:])})
    return {"paires": paires, "sans_paire": int(sans_paire),
            "segments": len(par_segment),
            "segments_apparies": len({p["segment"] for p in paires}),
            "retenants_en_tout": int(sum(len(d["retiennent"]) for d in par_segment.values())),
            "non_retenants_en_tout": int(sum(len(d["non"]) for d in par_segment.values()))}


def un_bloc(url: str, meta: dict, cy: int, cx: int, delai: float = DELAI):
    """Le cube brut d'un chunk, sans aucun filtre — ce que la chaîne n'avait jamais ouvert."""
    profond, hy, hx = meta["chunks"]
    raw = get(f"{url}/{chunk_key(meta, 0, cy, cx)}", delai)
    if raw is None:
        return None, "absent"
    data = decode(raw, meta, profond * hy * hx)
    if data is None:
        return None, "illisible"
    return np.frombuffer(data, dtype=np.dtype(meta["dtype"])).reshape(profond, hy, hx), None


def les_cubes(paires: list[dict], delai: float = DELAI, garder_le_cube: bool = False) -> dict:
    """Les trente cubes, téléchargés une fois, et la couche du milieu de chacun.

    ⚠⚠ `garder_le_cube` EST NUL PAR DEFAUT, ET C'EST LA REGLE DU DEPOT : une tranche publiee ne se
    corrige jamais en place. `196` a besoin du cube entier pour en tirer une coupe en profondeur ;
    avec le defaut, cette tranche rend exactement ce qu'elle rendait.

    ⚠ Une paire dont un des deux cubes ne répond pas est écartée ENTIÈRE : garder le retenant sans
    son contrôle briserait l'appariement, et la loi exacte compterait quinze contre quatorze.
    """
    cles = {}
    for v in les_volumes(combien=10 ** 6):
        cles[str(v["segment"])] = v["cle"]
    tuiles, refus, gardees = [], {}, []
    metas: dict[str, dict] = {}
    for p in paires:
        seg = p["segment"]
        if seg not in cles:
            refus["segment inconnu"] = refus.get("segment inconnu", 0) + 1
            continue
        url = f"{BUCKET}/{cles[seg]}"
        if seg not in metas:
            try:
                metas[seg] = array_meta(url, 0, delai)
            except Exception as e:  # noqa: BLE001
                refus[f"métadonnées {type(e).__name__}"] = refus.get(
                    f"métadonnées {type(e).__name__}", 0) + 1
                continue
        meta = metas[seg]
        deux = []
        for camp in ("retient", "controle"):
            cy, cx = p[camp]
            bloc, pourquoi = un_bloc(url, meta, int(cy), int(cx), delai)
            if bloc is None:
                refus[pourquoi] = refus.get(pourquoi, 0) + 1
                break
            deux.append((camp, bloc))
        if len(deux) != 2:
            continue
        gardees.append(p)
        for camp, bloc in deux:
            t = {"segment": seg, "chunk": list(p[camp]), "retient": camp == "retient",
                 "couche": np.asarray(bloc[la_couche_montree(bloc.shape[0])], dtype=float)}
            if garder_le_cube:
                t["cube"] = np.asarray(bloc, dtype=float)
            tuiles.append(t)
    return {"tuiles": tuiles, "paires_gardees": gardees, "refuses": refus,
            "couches": {int(m["chunks"][0]) for m in metas.values()}}


def le_niveau_commun(couches: list[np.ndarray], bornes=LE_NIVEAU_COMMUN) -> tuple[float, float]:
    """Les deux niveaux qui mappent les trente tuiles — tirés du mélange, jamais d'une tuile."""
    pile = np.concatenate([np.asarray(c, dtype=float).ravel() for c in couches])
    bas, haut = (float(np.percentile(pile, bornes[0])), float(np.percentile(pile, bornes[1])))
    return (bas, haut if haut > bas else bas + 1.0)


def en_octets(couche: np.ndarray, niveau: tuple[float, float]) -> np.ndarray:
    """Une couche rendue en niveaux de gris — exactement ce que la planche dessinera.

    ⚠⚠ C'EST LA SEULE DEFINITION DU RENDU. La mesure publie ces octets et la figure les pose ; une
    seconde formule dans la figure ferait regarder autre chose que ce qui a ete mesure.
    """
    bas, haut = niveau
    x = (np.asarray(couche, dtype=float) - bas) / (haut - bas)
    return np.clip(np.rint(x * 255.0), 0, 255).astype(np.uint8)


def la_planche(tuiles: list[dict], graine: int = GRAINE) -> dict:
    """L'ordre des tuiles, et l'ADRESSE de chacune — mais jamais son camp.

    ⚠⚠⚠ CETTE FONCTION NE LIT PAS `retient`, ET C'EST STRUCTUREL : sa sortie est identique que les
    camps soient posés d'une façon ou de l'autre, ce que sa sonde vérifie en les retournant tous.
    Le chemin aveugle ne peut donc pas publier la clef par inadvertance, puisqu'il ne la voit pas.

    ⭐ L'ADRESSE, ELLE, EST PUBLIÉE, et c'est un gain : la clef cesse d'être un nombre qu'il faut
    croire sur parole. N'importe qui peut la refaire depuis les mesures de `190` et de `192`, qui
    sont publiées elles aussi. Le voile est sur l'ŒIL, pas sur le lecteur du dépôt.
    """
    r = _rng(graine + 1)
    ordre = [int(i) for i in r.permutation(len(tuiles))]
    return {"ordre": ordre, "tuiles": len(tuiles),
            "adresses": [[str(tuiles[j]["segment"]), int(tuiles[j]["chunk"][0]),
                          int(tuiles[j]["chunk"][1])] for j in ordre],
            "colonnes": int(COLONNES_DE_LA_PLANCHE), "rangs": int(RANGS_DE_LA_PLANCHE)}


def la_cle_depuis_les_adresses(adresses, etiquettes: dict) -> dict:
    """Les positions (à partir de 1) qui retiennent, RELUES des mesures de `190` et de `192`.

    ⚠⚠ C'EST LA SEULE DEFINITION DE LA CLEF. Elle ne vient pas du tirage de telechargement mais de
    l'etiquette publiee, donc une execution qui perdrait un cube ne pourrait pas la deplacer.

    ⚠ Une adresse que l'etiquette ne connait pas est REFUSEE, jamais defautee : une planche dont une
    tuile n'a pas de camp ne se note pas.
    """
    inconnues, cle = [], []
    for i, a in enumerate(adresses):
        v = etiquettes.get((str(a[0]), int(a[1]), int(a[2])))
        if v is None:
            inconnues.append(list(a))
            continue
        if v.get("etiquette"):
            cle.append(i + 1)
    return {"decidable": not inconnues, "la_cle": tuple(cle),
            "les_adresses_inconnues": inconnues}


def la_loi_exacte(tuiles: int, retenants: int, choisies: int, au_moins: int) -> float:
    """P(au moins `au_moins` justes) quand on désigne `choisies` tuiles au hasard — exacte.

    ⭐⭐⭐⭐ C'EST LA LOI HYPERGÉOMÉTRIQUE, ET C'EST TOUT CE QUI REND UNE LECTURE PUBLIABLE. Aucune
    permutation, aucun tirage : le nul d'une assignation est calculable terme à terme, exactement
    comme le compte global de `194` est binomial.
    """
    n, k, m = int(tuiles), int(retenants), int(choisies)
    total = comb(n, m)
    if total == 0:
        return 1.0
    s = 0
    for j in range(max(0, int(au_moins)), min(k, m) + 1):
        s += comb(k, j) * comb(n - k, m - j)
    return float(s) / float(total)


def le_seuil_derive(tuiles: int, retenants: int, choisies: int,
                    garantie: float = GARANTIE) -> dict:
    """Le plus petit compte de justes que la garantie de la chaîne autorise à publier.

    ⚠⚠ LE SEUIL EST DERIVE DE LA GARANTIE ET DE LA TAILLE DE LA PLANCHE, jamais tape. Un seuil
    choisi serait exactement le peche que `179` a nomme.
    """
    seuil = None
    for k in range(0, min(int(retenants), int(choisies)) + 1):
        if la_loi_exacte(tuiles, retenants, choisies, k) <= float(garantie):
            seuil = k
            break
    # ⚠⚠ LA DISTRIBUTION ENTIERE EST PUBLIEE PAR LE PRODUCTEUR, et c'est deliberе : une figure qui
    # la recalculerait serait une SECONDE definition de la loi, libre de ne plus s'accorder avec
    # celle qui rend le seuil.
    # ⚠⚠⚠ LES PROBABILITES SONT ARRONDIES PAR LE PRODUCTEUR, ET C'EST UNE REGLE DU DEPOT : ce qui
    # est enregistre dans `verifier_chiffres` est ce que le document PUBLIE, avec les decimales du
    # producteur — ni completees, ni rognees. Publier ici dix-sept decimales et en imprimer sept
    # ailleurs ferait diverger les deux ecritures d'un meme nombre.
    haut = min(int(retenants), int(choisies))
    distribution = [
        {"justes": k,
         "probabilite": round(float(comb(int(retenants), k)
                                    * comb(int(tuiles) - int(retenants), int(choisies) - k))
                              / float(comb(int(tuiles), int(choisies))), DECIMALES),
         "probabilite_den_avoir_autant_ou_plus": round(
             la_loi_exacte(tuiles, retenants, choisies, k), DECIMALES)}
        for k in range(0, haut + 1)]
    return {"tuiles": int(tuiles), "retenants": int(retenants), "choisies": int(choisies),
            "attendus_par_hasard": float(retenants) * float(choisies) / float(tuiles),
            "la_garantie": float(garantie), "le_seuil": seuil,
            "la_probabilite_au_seuil": (None if seuil is None else
                                        round(la_loi_exacte(tuiles, retenants, choisies, seuil),
                                              DECIMALES)),
            "la_distribution": distribution}


def un_lecteur_mecanique(octets: list[np.ndarray], choisies: int) -> tuple[int, ...]:
    """Le lecteur de l'étalon : il désigne les tuiles les plus CLAIRES, et rien d'autre.

    ⚠⚠⚠ CE LECTEUR NE VAUT PAS L'ŒIL, ET C'EST ECRIT PLUTOT QUE SOUS-ENTENDU. Il connait le trait
    qu'on lui injecte, donc sa sensibilite est une BORNE SUPERIEURE : un trait qu'il ne voit pas a
    tous les replicats, personne ne le voit. L'inverse n'est pas vrai.
    """
    moyennes = [float(np.mean(o)) for o in octets]
    rang = sorted(range(len(moyennes)), key=lambda i: (-moyennes[i], i))
    return tuple(sorted(i + 1 for i in rang[:int(choisies)]))


def la_sensibilite(couches: list[np.ndarray], force: float, seuil: int,
                   replicats: int = REPLICATS, graine: int = GRAINE,
                   par_le_rendu: bool = True) -> float:
    """La part des réplicats où un trait de cette force est retrouvé par le lecteur mécanique.

    ⭐⭐⭐⭐ LE FOND DE L'ÉTALON EST LA VRAIE MATIÈRE, et c'est ce qui rend la mesure utilisable :
    l'étiquette est RETIRÉE À CHAQUE RÉPLICAT — les quinze injectés sont tirés au hasard — donc le
    trait réel du fond, s'il existe, ne peut que NUIRE au lecteur, jamais l'aider. Et la dispersion
    naturelle des trente tuiles est exactement le bruit contre lequel le trait doit ressortir.

    ⚠⚠ L'INJECTION PASSE PAR LE RENDU, donc par la quantification en niveaux de gris : c'est la
    sensibilité du DISPOSITIF qui est mesurée, pas celle d'un lecteur idéal.
    """
    n = len(couches)
    m = n // 2
    r = _rng(graine + 7)
    vus = 0
    for _ in range(int(replicats)):
        injectees = set(int(i) for i in r.permutation(n)[:m])
        cs = [np.asarray(c, dtype=float) + (float(force) if i in injectees else 0.0)
              for i, c in enumerate(couches)]
        if par_le_rendu:
            niveau = le_niveau_commun(cs)
            octets = [en_octets(c, niveau) for c in cs]
        else:
            octets = cs
        lu = un_lecteur_mecanique(octets, m)
        justes = len({i - 1 for i in lu} & injectees)
        vus += int(justes >= int(seuil))
    return float(vus) / float(replicats)


def la_force_quil_faut(couches: list[np.ndarray], seuil: int,
                       echelle=LECHELLE_DE_FORCE, replicats: int = REPLICATS,
                       graine: int = GRAINE) -> dict:
    """La plus petite force de l'échelle vue à TOUS les réplicats — dérivée, pas choisie.

    ⚠⚠⚠ C'EST LA LECON DE `193` ET DE `194` : une face positive marginale n'est pas une face
    positive. La courbe entiere est publiee a cote, sinon le nombre rendu n'a pas de producteur.
    """
    courbe = []
    trouvee = None
    for f in echelle:
        part = la_sensibilite(couches, f, seuil, replicats, graine)
        courbe.append({"force": float(f), "part_des_replicats": float(part)})
        if trouvee is None and part >= 1.0:
            trouvee = float(f)
    return {"la_courbe": courbe, "la_force_quil_faut": trouvee,
            "replicats": int(replicats), "le_seuil": int(seuil)}


def noter(lecture, cle, tuiles: int, choisies: int, seuil: dict) -> dict:
    """Ce que la lecture vaut — le compte de justes et sa probabilité exacte.

    ⚠⚠ UNE LECTURE QUI NE DESIGNE PAS LE BON NOMBRE DE TUILES EST REFUSEE, jamais rognee : la loi
    exacte suppose `choisies` designations, et en corriger le compte apres coup serait ajuster
    l'epreuve a la reponse.
    """
    if not lecture:
        return {"decidable": False, "raison": "aucune lecture n'a été déposée"}
    lu = sorted({int(x) for x in lecture})
    if len(lu) != int(choisies):
        return {"decidable": False,
                "raison": f"{len(lu)} tuiles désignées pour {int(choisies)} attendues"}
    if lu[0] < 1 or lu[-1] > int(tuiles):
        return {"decidable": False, "raison": "une tuile désignée sort de la planche"}
    justes = len(set(lu) & set(int(x) for x in cle))
    p = round(la_loi_exacte(tuiles, len(cle), choisies, justes), DECIMALES)
    s = seuil.get("le_seuil")
    return {"decidable": True, "les_tuiles_designees": lu, "les_justes": int(justes),
            "les_attendus_par_hasard": float(seuil["attendus_par_hasard"]),
            "la_probabilite": float(p), "le_seuil": s,
            "loeil_separe": bool(s is not None and justes >= int(s))}


def _hex(o: np.ndarray) -> str:
    return np.asarray(o, dtype=np.uint8).tobytes().hex()


def mesurer(graine: int = GRAINE, delai: float = DELAI, replicats: int = REPLICATS,
            ouvrir=None) -> dict:
    """Ouvrir les trente cubes et POSER LA PLANCHE — sans jamais calculer la clef.

    ⚠⚠⚠ UNE PLANCHE INCOMPLETE EST REFUSEE, ET CE REFUS EST NE D'UN VRAI DEFAUT : une execution a
    perdu un cube sur le reseau, a pose vingt-huit tuiles au lieu de trente, et a donc TIRE UN AUTRE
    ORDRE. La lecture deposee sur la planche precedente devenait fausse sans que rien ne le dise.
    Une planche est complete ou elle n'existe pas.
    """
    etq = les_etiquettes()
    app = apparier(etq["chunks"], graine)
    cubes = (ouvrir or les_cubes)(app["paires"], delai)
    tuiles = cubes["tuiles"]
    demandes = 2 * len(app["paires"])
    if len(tuiles) != demandes:
        return {"decidable": False,
                "raison": f"{len(tuiles)} cubes rendus sur {demandes} — une planche amputée "
                          f"tirerait un AUTRE ordre et invaliderait toute lecture déposée",
                "refuses": cubes["refuses"]}
    couches = [t["couche"] for t in tuiles]
    niveau = le_niveau_commun(couches)
    octets = [en_octets(c, niveau) for c in couches]
    planche = la_planche(tuiles, graine)
    cote = int(octets[0].shape[0])
    retenants = int(sum(1 for t in tuiles if t["retient"]))
    choisies = retenants
    seuil = le_seuil_derive(len(tuiles), retenants, choisies)
    out = {
        "graine": int(graine),
        "la_couche_montree": "le milieu du cube",
        "le_niveau_commun": {"percentiles": list(LE_NIVEAU_COMMUN),
                             "bas": round(niveau[0], 4), "haut": round(niveau[1], 4)},
        "lappariement": {k: v for k, v in app.items() if k != "paires"},
        "les_cubes": {"demandes": 2 * len(app["paires"]), "rendus": len(tuiles),
                      "paires_gardees": len(cubes["paires_gardees"]),
                      "refuses": cubes["refuses"],
                      "couches_du_cube": sorted(int(x) for x in cubes["couches"])},
        "la_planche": {**planche, "cote": cote,
                       "octets": [_hex(octets[j]) for j in planche["ordre"]]},
        "la_loi_exacte": seuil,
        "la_sensibilite": la_force_quil_faut(couches, int(seuil["le_seuil"] or 10**9),
                                             replicats=replicats, graine=graine),
        "la_lecture_deposee": list(LA_LECTURE_A_LAVEUGLE),
        "ce_que_loeil_a_cru_voir": CE_QUE_LŒIL_A_CRU_VOIR,
        "la_cle": None,
        "la_note": None,
        "le_verdict": {"leve": False,
                       "ce_qui_manque": "la lecture n'est pas encore déposée"
                       if not LA_LECTURE_A_LAVEUGLE else "la levée n'a pas été demandée"},
    }
    return out


def lever(chemin: Path, lecture=LA_LECTURE_A_LAVEUGLE, etiquettes=None) -> dict:
    """Lever l'aveugle SUR LA PLANCHE DEJA PUBLIEE — sans retelecharger quoi que ce soit.

    ⚠⚠⚠ C'EST LA REPARATION DU DEFAUT LE PLUS GRAVE DE CETTE TRANCHE. La premiere version
    recommencait la mesure a la levee : un cube perdu sur le reseau changeait alors le nombre de
    tuiles, donc le tirage de l'ordre, donc la planche — et la lecture deposee etait notee contre une
    planche que personne n'avait regardee. La levee lit desormais l'artefact et rien d'autre.
    """
    d = json.loads(Path(chemin).read_text(encoding="utf-8"))
    if not d.get("decidable", True):
        return d
    planche = d.get("la_planche") or {}
    if not planche.get("adresses"):
        return {**d, "la_note": {"decidable": False,
                                 "raison": "la planche publiée ne porte pas ses adresses"}}
    etq = les_etiquettes()["chunks"] if etiquettes is None else etiquettes
    k = la_cle_depuis_les_adresses(planche["adresses"], etq)
    loi = d["la_loi_exacte"]
    if not k["decidable"]:
        return {**d, "la_note": {"decidable": False,
                                 "raison": f"{len(k['les_adresses_inconnues'])} adresses sans "
                                           f"étiquette publiée"}}
    if len(k["la_cle"]) != int(loi["retenants"]):
        return {**d, "la_note": {
            "decidable": False,
            "raison": f"{len(k['la_cle'])} retenants relus pour {loi['retenants']} annoncés "
                      f"par la planche"}}
    note = noter(lecture, k["la_cle"], int(loi["tuiles"]), int(loi["choisies"]), loi)
    return {**d, "la_cle": list(k["la_cle"]), "la_note": note,
            "la_lecture_deposee": list(lecture),
            "ce_que_loeil_a_cru_voir": CE_QUE_LŒIL_A_CRU_VOIR,
            "le_verdict": {
                "leve": True,
                "loeil_separe": bool(note.get("loeil_separe")),
                "la_force_que_le_dispositif_voit": d["la_sensibilite"]["la_force_quil_faut"],
                "ce_que_le_negatif_borne": (
                    "un trait de luminosité plus faible que la force dérivée n'est vu à aucun "
                    "réplicat ; pour un trait de texture, aucune sensibilité n'est mesurée")}}


def afficher(r: dict) -> None:
    if not r.get("decidable", True):
        print(f"OUVRIR LES QUINZE   indécidable : {r.get('raison')}")
        return
    a, c, l = r["lappariement"], r["les_cubes"], r["la_loi_exacte"]
    print(f"OUVRIR LES QUINZE   {a['retenants_en_tout']} retenants · "
          f"{a['non_retenants_en_tout']} non · {a['segments']} segments · "
          f"{a['sans_paire']} sans paire")
    print(f"  LES CUBES         {c['rendus']} rendus sur {c['demandes']} demandés · "
          f"{c['paires_gardees']} paires · refus {c['refuses'] or '—'}")
    print(f"  LA PLANCHE        {r['la_planche']['tuiles']} tuiles de "
          f"{r['la_planche']['cote']} · {r['la_planche']['colonnes']}×"
          f"{r['la_planche']['rangs']} · niveau commun "
          f"[{r['le_niveau_commun']['bas']} ; {r['le_niveau_commun']['haut']}]")
    print(f"  LA LOI EXACTE     {l['attendus_par_hasard']} justes attendus · seuil "
          f"{l['le_seuil']} · P au seuil {l['la_probabilite_au_seuil']:.6g}")
    s = r["la_sensibilite"]
    print("  LA SENSIBILITÉ    " + " · ".join(
        f"{int(p['force'])}→{p['part_des_replicats']:g}" for p in s["la_courbe"]))
    print(f"                    force dérivée {s['la_force_quil_faut']} "
          f"sur {s['replicats']} réplicats")
    n = r.get("la_note")
    if not r.get("la_cle"):
        print("  LA LEVÉE          PAS FAITE — l'artefact ne porte aucune clef")
        return
    if not (n or {}).get("decidable"):
        print(f"  LA NOTE           indécidable : {(n or {}).get('raison')}")
        return
    print(f"  LA NOTE           {n['les_justes']} justes sur {l['choisies']} · "
          f"attendus {n['les_attendus_par_hasard']} · P = {n['la_probabilite']:.6g} · "
          f"seuil {n['le_seuil']} · l'œil sépare {n['loeil_separe']}")


def verifier() -> int:
    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        if not ok:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    # ⭐⭐⭐⭐ LA LOI EXACTE SE VERIFIE A LA MAIN, TERME A TERME.
    v("★★ désigner tout sur une planche entière est certain",
      abs(la_loi_exacte(10, 5, 10, 5) - 1.0) < 1e-12)
    v("★★ tout juste sur quatre tuiles dont deux retiennent vaut un sixième",
      abs(la_loi_exacte(4, 2, 2, 2) - 1.0 / 6.0) < 1e-12, str(la_loi_exacte(4, 2, 2, 2)))
    v("★★★ et la loi de la planche vaut ce que la combinatoire dit",
      abs(la_loi_exacte(30, 15, 15, 15) - 1.0 / float(comb(30, 15))) < 1e-18,
      str(la_loi_exacte(30, 15, 15, 15)))
    v("la probabilité d'au moins zéro juste vaut un",
      abs(la_loi_exacte(30, 15, 15, 0) - 1.0) < 1e-12)
    v("★★ la précision publiée est DÉRIVÉE de la taille de la planche",
      10.0 ** -DECIMALES < 1.0 / float(comb(30, 15)) * 100.0
      and 10.0 ** -DECIMALES > 1.0 / float(comb(30, 15)),
      f"{10.0 ** -DECIMALES} contre une masse minimale de {1.0 / float(comb(30, 15))}")

    s = le_seuil_derive(30, 15, 15)
    v("★★★★ le seuil est DÉRIVÉ de la garantie, et il vaut onze", s["le_seuil"] == 11,
      str(s["le_seuil"]))
    v("★★★ et il tient la garantie", s["la_probabilite_au_seuil"] <= GARANTIE,
      str(s["la_probabilite_au_seuil"]))
    v("★★★ tandis qu'un juste de moins ne la tient PAS",
      la_loi_exacte(30, 15, 15, s["le_seuil"] - 1) > GARANTIE,
      str(la_loi_exacte(30, 15, 15, s["le_seuil"] - 1)))
    v("les attendus par hasard valent la moitié", abs(s["attendus_par_hasard"] - 7.5) < 1e-12)
    v("★★★ la distribution publiée somme à un",
      abs(sum(x["probabilite"] for x in s["la_distribution"]) - 1.0) < 1e-12,
      str(sum(x["probabilite"] for x in s["la_distribution"])))
    v("★★★ et son mode tombe sur les attendus",
      max(s["la_distribution"], key=lambda x: x["probabilite"])["justes"] == 7
      or max(s["la_distribution"], key=lambda x: x["probabilite"])["justes"] == 8,
      str(max(s["la_distribution"], key=lambda x: x["probabilite"])["justes"]))
    # ⚠⚠ LA TOLERANCE EST DERIVEE DE LA PRECISION PUBLIEE, PAS CHOISIE : les deux ecritures sont
    # arrondies a `DECIMALES`, donc une somme de seize masses peut s'ecarter de seize unites de la
    # derniere decimale publiee. Exiger l'egalite exacte reviendrait a exiger que l'arrondi n'existe
    # pas — la premiere version de cette sonde l'a fait, et elle a dument vire au rouge.
    tol = len(s["la_distribution"]) * 10.0 ** -DECIMALES
    v("★★★★ chaque queue publiée égale la somme des masses au-dessus, à la précision publiée",
      all(abs(x["probabilite_den_avoir_autant_ou_plus"]
              - sum(y["probabilite"] for y in s["la_distribution"] if y["justes"] >= x["justes"]))
          <= tol for x in s["la_distribution"]), f"tolérance dérivée {tol}")
    v("★★★ et la précision publiée distingue toutes les queues sauf les plus extrêmes",
      sum(1 for x in s["la_distribution"]
          if x["probabilite_den_avoir_autant_ou_plus"] > 0.0) >= len(s["la_distribution"]) - 2,
      str(sum(1 for x in s["la_distribution"]
              if x["probabilite_den_avoir_autant_ou_plus"] > 0.0)))
    v("★★ une planche plus grande abaisse le seuil relatif",
      le_seuil_derive(60, 30, 30)["le_seuil"] / 30.0 < s["le_seuil"] / 15.0,
      f"{le_seuil_derive(60, 30, 30)['le_seuil']}/30 contre {s['le_seuil']}/15")

    # ⚠⚠⚠ L'AVEUGLE EST STRUCTUREL, ET LA SONDE RETOURNE LES CAMPS POUR LE PROUVER : une planche
    # qui lirait `retient` d'une quelconque facon changerait quand tous les camps s'inversent.
    faux = [{"retient": i % 2 == 0, "segment": f"S{i % 3}", "chunk": [i, 2 * i]}
            for i in range(30)]
    envers = [{**t, "retient": not t["retient"]} for t in faux]
    p = la_planche(faux, 4242)
    v("★★★★ la planche est la MÊME quand tous les camps s'inversent",
      la_planche(envers, 4242) == p, str(sorted(p)))
    v("★★★ et elle ne porte aucun champ de camp",
      not any("retient" in str(k) or "cle" in str(k) for k in p), str(sorted(p)))
    v("l'ordre est une permutation entière", sorted(p["ordre"]) == list(range(30)))
    v("et il est le même à graine égale", la_planche(faux, 4242)["ordre"] == p["ordre"])
    v("★★ et il change de graine à graine", la_planche(faux, 4243)["ordre"] != p["ordre"])
    etq_faux = {(t["segment"], t["chunk"][0], t["chunk"][1]): {"etiquette": t["retient"]}
                for t in faux}
    k = la_cle_depuis_les_adresses(p["adresses"], etq_faux)
    cle = k["la_cle"]
    v("★★★ la clef désigne autant de positions qu'il y a de retenants",
      k["decidable"] and len(cle) == 15, str(len(cle)))
    v("★★★★ et elle les désigne JUSTES",
      all(faux[p["ordre"][i - 1]]["retient"] for i in cle))
    v("★★★★ une adresse sans étiquette publiée est REFUSÉE, jamais défautée",
      not la_cle_depuis_les_adresses(p["adresses"], {})["decidable"],
      str(len(la_cle_depuis_les_adresses(p["adresses"], {})["les_adresses_inconnues"])))

    # ⭐⭐⭐⭐ LA LEVEE LIT L'ARTEFACT ET RIEN D'AUTRE, ET SES TROIS REFUS SE VERIFIENT.
    import tempfile  # noqa: PLC0415
    seuil15 = le_seuil_derive(30, 15, 15)
    artefact = {"la_planche": p, "la_loi_exacte": seuil15,
                "la_sensibilite": {"la_force_quil_faut": 8.0}}
    with tempfile.TemporaryDirectory() as dd:
        ch = Path(dd) / "a.json"
        ch.write_text(json.dumps(artefact), encoding="utf-8")
        lu = lever(ch, cle, etq_faux)
        v("★★★★ la levée note la lecture contre la planche PUBLIÉE",
          lu["la_note"]["decidable"] and lu["la_note"]["les_justes"] == 15,
          str(lu["la_note"].get("les_justes")))
        v("★★★ et elle republie la clef qu'elle a relue", list(cle) == lu["la_cle"])
        sans = {**artefact, "la_planche": {k2: v2 for k2, v2 in p.items() if k2 != "adresses"}}
        ch.write_text(json.dumps(sans), encoding="utf-8")
        v("★★★ une planche sans adresses est refusée",
          lever(ch, cle, etq_faux)["la_note"]["decidable"] is False)
        boiteux = {**artefact, "la_loi_exacte": {**seuil15, "retenants": 14}}
        ch.write_text(json.dumps(boiteux), encoding="utf-8")
        v("★★★★ un compte de retenants qui ne correspond pas est refusé",
          lever(ch, cle, etq_faux)["la_note"]["decidable"] is False,
          str(lever(ch, cle, etq_faux)["la_note"].get("raison")))
        ch.write_text(json.dumps({"decidable": False, "raison": "planche amputée"}),
                      encoding="utf-8")
        v("★★★ une mesure indécidable traverse la levée sans être notée",
          lever(ch, cle, etq_faux).get("la_note") is None)

    # ⭐⭐⭐⭐ LA NOTE SE VERIFIE SUR LES DEUX FACES, ET SUR SES REFUS.
    parfaite = noter(cle, cle, 30, 15, s)
    v("★★★★ une lecture parfaite est notée parfaite", parfaite["les_justes"] == 15,
      str(parfaite["les_justes"]))
    v("★★★★ et elle sépare", parfaite["loeil_separe"])
    inverse = tuple(i for i in range(1, 31) if i not in cle)
    v("★★★★ une lecture exactement fausse ne sépare pas",
      not noter(inverse, cle, 30, 15, s)["loeil_separe"],
      str(noter(inverse, cle, 30, 15, s)["les_justes"]))
    v("★★★ et sa probabilité vaut un", abs(noter(inverse, cle, 30, 15, s)["la_probabilite"]
                                           - 1.0) < 1e-12)
    v("une lecture absente est indécidable, jamais nulle",
      noter((), cle, 30, 15, s).get("decidable") is False)
    v("★★★ une lecture du mauvais compte est REFUSÉE",
      noter(cle[:14], cle, 30, 15, s).get("decidable") is False,
      str(noter(cle[:14], cle, 30, 15, s).get("raison")))
    v("★★ une tuile hors planche est refusée",
      noter(tuple(list(cle[:14]) + [99]), cle, 30, 15, s).get("decidable") is False)

    # ⚠⚠ LE RENDU EST LA SEULE DEFINITION, ET IL SE VERIFIE AUX DEUX BOUTS.
    c0 = np.linspace(0.0, 100.0, 16).reshape(4, 4)
    o0 = en_octets(c0, (0.0, 100.0))
    v("le rendu envoie le bas sur zéro et le haut sur 255",
      int(o0.min()) == 0 and int(o0.max()) == 255, f"{int(o0.min())}..{int(o0.max())}")
    v("★★ et il écrête au lieu de déborder",
      int(en_octets(np.array([[-50.0, 500.0]]), (0.0, 100.0)).max()) == 255
      and int(en_octets(np.array([[-50.0, 500.0]]), (0.0, 100.0)).min()) == 0)
    n2 = le_niveau_commun([np.zeros((4, 4)), np.full((4, 4), 100.0)])
    v("★★★ le niveau est commun aux tuiles, pas propre à chacune", n2[1] > n2[0] + 50.0,
      str(n2))
    v("★★ un niveau plat reste inversible", le_niveau_commun([np.zeros((4, 4))])[1]
      > le_niveau_commun([np.zeros((4, 4))])[0])

    # ⭐⭐⭐⭐ L'APPARIEMENT TIRE DANS LE SEGMENT, ET CA SE CASSE.
    # ⚠⚠⚠ LA PREMIERE VERSION DE CETTE SONDE ETAIT INCAPABLE D'ECHOUER, ET UN BRIS L'A DIT : elle
    # lisait le champ `segment` de la paire — que ce fichier ecrit lui-meme depuis le RETENANT —
    # au lieu de la PROVENANCE du controle. Tirer les controles dans tout le depot la laissait
    # verte. Ce qui se verifie ici est donc l'APPARTENANCE des coordonnees rendues, et la fixture
    # porte cinq segments pour qu'un tirage libre ne puisse pas les remettre en place par chance.
    # ⚠⚠ ET LE SEGMENT `F` PORTE DEUX RETENANTS : sans lui, reutiliser toujours le meme controle
    # rendait la meme reponse, donc la sonde du doublon etait elle aussi incapable d'echouer.
    froids_par_segment = {chr(65 + i): {(10 * i + 1, 10 * i + 1)} for i in range(5)}
    froids_par_segment["F"] = {(61, 61), (62, 62)}
    etq = {}
    for i in range(5):
        seg = chr(65 + i)
        etq[(seg, 0, 0)] = {"etiquette": True}
        etq[(seg, 10 * i + 1, 10 * i + 1)] = {"etiquette": False}
    etq[("F", 0, 0)] = {"etiquette": True}
    etq[("F", 0, 1)] = {"etiquette": True}
    etq[("F", 61, 61)] = {"etiquette": False}
    etq[("F", 62, 62)] = {"etiquette": False}
    a = apparier(etq, 7)
    v("★★★★ le contrôle d'une paire est un chunk froid DU MÊME SEGMENT",
      len(a["paires"]) == 7
      and all(tuple(p_["controle"]) in froids_par_segment[p_["segment"]] for p_ in a["paires"]),
      str([(p_["segment"], p_["controle"]) for p_ in a["paires"]]))
    v("★★★ et aucun contrôle ne sert deux fois",
      len({(p_["segment"], tuple(p_["controle"])) for p_ in a["paires"]}) == len(a["paires"]))
    v("★★ aucun contrôle n'est un chunk qui retient",
      all(tuple(p_["controle"]) not in ((0, 0), (0, 1)) for p_ in a["paires"]))
    v("★★★ un segment sans contrôle disponible laisse son retenant SANS PAIRE",
      apparier({("C", 0, 0): {"etiquette": True}}, 7)["sans_paire"] == 1)
    v("★★ et alors aucune paire n'est fabriquée",
      not apparier({("C", 0, 0): {"etiquette": True}}, 7)["paires"])
    # ⚠⚠⚠ LA REGLE NEE DU VRAI DEFAUT SE SONDE SANS RESEAU : `mesurer` ouvre ses cubes par une
    # fonction injectable, donc la planche amputee s'exerce de bout en bout au lieu d'etre une
    # ligne que rien ne visite.
    def _cubes_fabriques(paires, _delai, manquants=0):
        rr = _rng(3)
        tt = []
        for pr in paires:
            for camp in ("retient", "controle"):
                tt.append({"segment": pr["segment"], "chunk": list(pr[camp]),
                           "retient": camp == "retient",
                           "couche": rr.normal(120.0, 20.0, size=(8, 8))})
        if manquants:
            tt = tt[:-manquants]
        return {"tuiles": tt, "paires_gardees": paires, "refuses": {},
                "couches": {109}}

    entier = mesurer(replicats=4, ouvrir=lambda pr, d_: _cubes_fabriques(pr, d_, 0))
    v("★★★ une planche entière est mesurée", entier.get("decidable", True)
      and entier["la_planche"]["tuiles"] == 30, str(entier.get("raison"))[:80])
    v("★★★ et elle ne porte toujours pas de clef", entier.get("la_cle") is None)
    ampute = mesurer(replicats=4, ouvrir=lambda pr, d_: _cubes_fabriques(pr, d_, 2))
    v("★★★★ une planche AMPUTÉE est refusée, jamais posée",
      ampute.get("decidable") is False, str(ampute.get("raison"))[:120])

    v("les comptes des deux camps sont rendus",
      a["retenants_en_tout"] == 7 and a["non_retenants_en_tout"] == 7,
      f"{a['retenants_en_tout']}/{a['non_retenants_en_tout']}")

    # ⭐⭐⭐⭐ LE LECTEUR MECANIQUE ET LA SENSIBILITE : LES DEUX FACES, MESUREES SUR REPLICATS.
    r = _rng(11)
    fond = [r.normal(120.0, 18.0, size=(32, 32)) for _ in range(30)]
    v("★★★ le lecteur désigne bien le nombre demandé",
      len(un_lecteur_mecanique([en_octets(c, (0.0, 255.0)) for c in fond], 15)) == 15)
    v("★★★★ un trait énorme est vu à TOUS les réplicats",
      la_sensibilite(fond, 200.0, 11, 8, 11) >= 1.0,
      str(la_sensibilite(fond, 200.0, 11, 8, 11)))
    # ⚠⚠⚠ UN TRAIT NUL N'EST PAS VU « JAMAIS » : IL EST VU AU TAUX QUE LA LOI EXACTE ANNONCE, et
    # c'est la premiere sonde qui l'a dit — huit replicats en avaient rendu un. Ce qui se verifie est
    # donc le TAUX, contre la garantie, et non une absence que le dispositif ne promet pas.
    v("★★★ un trait nul n'est JAMAIS vu à TOUS les réplicats",
      la_sensibilite(fond, 0.0, 11, 8, 11) < 1.0,
      str(la_sensibilite(fond, 0.0, 11, 8, 11)))
    v("★★★★ et le taux de faux du dispositif tient la garantie de la chaîne",
      la_sensibilite(fond, 0.0, 11, 200, 11) <= GARANTIE,
      f"{la_sensibilite(fond, 0.0, 11, 200, 11)} contre {GARANTIE} garantis")
    f = la_force_quil_faut(fond, 11, (0, 8, 64, 256), 8, 11)
    v("★★★★ la force rendue est vue à tous les réplicats",
      f["la_force_quil_faut"] is not None
      and la_sensibilite(fond, f["la_force_quil_faut"], 11, 8, 11) >= 1.0,
      str(f["la_force_quil_faut"]))
    v("★★★ et la courbe entière est publiée à côté", len(f["la_courbe"]) == 4,
      str([x["part_des_replicats"] for x in f["la_courbe"]]))
    v("★★★ la sensibilité MONTE avec la force",
      all(f["la_courbe"][i]["part_des_replicats"] <= f["la_courbe"][i + 1]["part_des_replicats"]
          for i in range(len(f["la_courbe"]) - 1)),
      str([x["part_des_replicats"] for x in f["la_courbe"]]))
    # ⚠⚠⚠ LA QUANTIFICATION FAIT PARTIE DU DISPOSITIF, ET LA SONDE LE MONTRE SUR UNE MATIERE OU LE
    # PAS DE GRIS EST GRAND : deux tuiles extremes etirent le niveau commun, donc un niveau de gris
    # vaut une vingtaine d'unites brutes, et un trait de quatre unites — parfaitement lisible sur les
    # valeurs crues — ne survit pas a l'arrondi.
    rg = _rng(23)
    grossier = [np.full((32, 32), 1000.0 + float(rg.normal(0.0, 0.4))) for _ in range(28)]
    grossier += [np.zeros((32, 32)), np.full((32, 32), 5000.0)]
    nc = le_niveau_commun(grossier)
    pas_de_gris = (nc[1] - nc[0]) / 255.0
    v("★★ le pas de gris de cette matière dépasse largement le trait injecté", pas_de_gris > 8.0,
      f"{pas_de_gris:.3f} unités par niveau")
    brut = la_sensibilite(grossier, 4.0, 11, 12, 23, par_le_rendu=False)
    rendu = la_sensibilite(grossier, 4.0, 11, 12, 23, par_le_rendu=True)
    v("★★★★ un trait sous le pas de gris est vu sur les valeurs crues", brut >= 1.0, str(brut))
    v("★★★★ et il est PERDU par le rendu — la quantification est dans le chemin", rendu < brut,
      f"{rendu} contre {brut}")

    # ⚠⚠⚠ L'ECHELLE ET LES REPLICATS SONT DERIVES, ET CA SE DIT.
    v("★★ l'échelle part du pas de quantification et double",
      LECHELLE_DE_FORCE[0] == 0 and LECHELLE_DE_FORCE[1] == 1
      and all(LECHELLE_DE_FORCE[i + 1] == 2 * LECHELLE_DE_FORCE[i]
              for i in range(1, len(LECHELLE_DE_FORCE) - 1)),
      str(LECHELLE_DE_FORCE))
    v("la garantie est celle de la chaîne", abs(GARANTIE - 0.05) < 1e-12)
    v("la couche montrée est le milieu et rien d'autre",
      la_couche_montree(109) == 54 and la_couche_montree(8) == 4)

    nom = "ouvrir_les_quinze.py"
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
    p.add_argument("--aveugle", action="store_true",
                   help="poser la planche SANS calculer la clef")
    p.add_argument("--lever", action="store_true",
                   help="lever l'aveugle et noter la lecture déposée")
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
