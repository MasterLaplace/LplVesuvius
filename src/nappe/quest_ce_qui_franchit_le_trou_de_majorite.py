"""Là où une bande perd sa majorité, qu'est-ce qui franchit la couture sur la même spire ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LA MOINDRE RÈGLE NE SOIT ESSAYÉE SUR LA MATIÈRE. La seule chose
regardée avant d'écrire est la PRÉSENCE : où le consensus manque dans `221`, `223` et `224`, et quelles
lignes restent au trou de `224` — jamais un pas.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P70`. `224` a fermé trois boucles sur quatre ; la quatrième et
le grand rectangle restent ouverts parce que la bande de la colonne 213 n'a pas de majorité à deux
coutures. `221` a un trou de ce genre au milieu d'une rangée, et les bords du segment en ont. Le prix
demande 100 % du recto : il faut franchir ces trous.

⭐⭐ AUCUNE LECTURE NEUVE : les six bandes de `224` suffisent.

## Les règles, déclarées

- LE MAILLAGE : un pas NUL à chaque couture du trou. Dans ce volume, qui est la surface du segment
  aplatie, un pas nul continue le feuillet à la profondeur du maillage : c'est suivre le maillage à
  travers le trou, sans rien lire.
- LES LIGNES PRÉSENTES : la médiane des lignes qui lisent encore au trou — moins de trois, sinon il n'y
  aurait pas de trou. ⚠⚠ C'est le vote d'une minorité, et `224` a mesuré ce qu'il coûte : une ligne seule
  par côté dépasse le demi-feuillet dans 21 boucles sur 54.

⚠ Le détour par la surface n'est pas une règle ici : son erreur est la fermeture de sa boucle, quelle que
soit la longueur du trou, et le trou de `224` est justement sur le seul côté que les deux boucles ouvertes
partagent.

## Ce qui se mesure, dans l'ordre

1. ⭐⭐⭐⭐ LES RÈGLES, SUR DES COUTURES OÙ LA MAJORITÉ EXISTE. Les longueurs de trou sont celles que les
   six bandes MONTRENT — jamais choisies. Pour chaque longueur, chaque fenêtre de coutures consécutives où
   le consensus existe partout est cachée, et chaque règle la franchit : le maillage par des pas nuls, les
   lignes présentes par toutes les paires et toutes les lignes seules de la bande. L'écart est celui de la
   somme franchie à la somme du consensus. Une règle FRANCHIT une longueur quand aucune fenêtre ne s'écarte
   d'un demi-feuillet.
2. ⭐⭐⭐ LA RÈGLE RETENUE, par un critère posé ici : parmi les règles qui s'appliquent aux trous des boucles
   et franchissent TOUTES les longueurs observées, celle dont l'écart le plus grand, à la longueur de ces
   trous, est le plus petit — à égalité, le maillage. Les lignes présentes sont jugées au nombre de lignes
   que le trou réel garde : deux, une.
3. ⭐⭐⭐⭐ LE TROU FRANCHI : la règle retenue écrit ses pas dans le trou, et l'analyse de `224` — la même,
   appelée — ferme alors toutes les boucles, le grand rectangle compris, contre le demi-feuillet et contre
   des marches indépendantes. L'autre règle est portée comme contrôle nommé.

⚠⚠ Avant tout, l'analyse de `224` est rejouée sans rien remplir, et elle doit retomber sur ses fermetures
publiées : sinon la tranche ne compare pas ce qu'elle croit comparer, et elle est refusée.

## Les issues, exclusives

- aucune règle ne franchit toutes les longueurs observées ;
- une règle franchit, mais une boucle dépasse alors le demi-feuillet ;
- une règle franchit, les boucles restent dessous, mais le grand rectangle reste ouvert ;
- une règle franchit, et toutes les boucles, grand rectangle compris, restent sur la même spire.

⚠⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : la référence de la simulation est le consensus, pas la vérité.
Une règle qui s'en écarte peu reproduit le consensus ; si la matière a, au trou, un pas que le consensus
n'aurait pas vu, rien ici ne le dit.

Usage :
    uv run python src/nappe/quest_ce_qui_franchit_le_trou_de_majorite.py --verifier
    uv run python src/nappe/quest_ce_qui_franchit_le_trou_de_majorite.py \\
        --json docs/mesures/quest_ce_qui_franchit_le_trou_de_majorite.json
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))

from deux_chemins_arrivent_ils_sur_la_meme_spire import (analyser,  # noqa: E402
                                                          ce_que_223_a_rendu,
                                                          les_pas_des_six_bandes,
                                                          relire_une_bande)
from le_consensus_traverse_t_il_la_rangee import le_consensus  # noqa: E402
from le_vote_ramene_t_il_les_rangees_sur_le_feuillet import ce_que_219_a_rendu  # noqa: E402
from que_montrent_ces_deux_vues import DEMI_PAS_EN_VOXELS  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
CE_QUE_224_A_RENDU = MESURES / "deux_chemins_arrivent_ils_sur_la_meme_spire.json"

LES_REGLES = ("le_maillage", "les_lignes_presentes")
LES_NOMS = {"le_maillage": "LE MAILLAGE", "les_lignes_presentes": "LES LIGNES PRÉSENTES"}
LES_SIMULEES = ("le_maillage", "deux_lignes", "une_ligne")

LA_QUESTION_DECLAREE = ("là où une bande perd sa majorité, qu'est-ce qui franchit la couture sur la "
                        "même spire ?")
LA_MESURE_DECLAREE = ("l'écart de chaque règle au consensus sur des fenêtres cachées de chaque longueur de "
                      "trou observée, puis les boucles de `224` fermées par la règle retenue")


# ─────────────────────────────── ce qui est relu ───────────────────────────────

def ce_que_224_a_rendu(chemin: Path = CE_QUE_224_A_RENDU) -> dict:
    """La lecture publiée de `224`, ses bandes, ses centres et ses fermetures — relus, jamais recalculés."""
    if not Path(chemin).exists():
        return {"decidable": False, "raison": f"{Path(chemin).name} est absent"}
    try:
        d = json.loads(Path(chemin).read_text())
    except (ValueError, OSError) as e:
        return {"decidable": False, "raison": f"{Path(chemin).name} est illisible : {e}"}
    if not d.get("decidable"):
        return {"decidable": False, "raison": "`224` est indécidable"}
    for cle in ("les_bandes", "les_bandes_declarees", "les_centres", "les_boucles", "la_grille"):
        if not d.get(cle):
            return {"decidable": False, "raison": f"`224` ne publie pas {cle}"}
    return {"decidable": True, "relues": {k: relire_une_bande(x) for k, x in d["les_bandes"].items()},
            "bandes": d["les_bandes_declarees"], "R": [int(x) for x in d["les_centres"]["rangees"]],
            "C": [int(x) for x in d["les_centres"]["colonnes"]], "la_grille": [int(x) for x in d["la_grille"]],
            "les_boucles": d["les_boucles"], "graine": int(d["graine"]), "tirages": int(d["tirages"]),
            "replicats": int(d["replicats"])}


def les_etendues(R, C, rangees: int, colonnes: int) -> dict:
    """Où chaque bande a été lue : celles de `219` et `223` sur toute la grille, les quatre de `224` sur leur
    portion. En coutures, `[de, à)`."""
    return {("rangees", int(R[0])): (int(C[0]), int(C[2])), ("rangees", int(R[1])): (0, int(colonnes) - 1),
            ("rangees", int(R[2])): (int(C[0]), int(C[2])),
            ("colonnes", int(C[0])): (int(R[0]), int(R[2])), ("colonnes", int(C[1])): (0, int(rangees) - 1),
            ("colonnes", int(C[2])): (int(R[0]), int(R[2]))}


# ─────────────────────────────── les trous ───────────────────────────────

def les_trous(cons: dict, de: int, a: int) -> list[list[int]]:
    """Les suites de coutures SANS consensus dans `[de, à)` : `[début, longueur]`, dans l'ordre."""
    out, debut = [], None
    for s in range(int(de), int(a)):
        if s not in cons:
            if debut is None:
                debut = s
        elif debut is not None:
            out.append([debut, s - debut])
            debut = None
    if debut is not None:
        out.append([debut, int(a) - debut])
    return out


def les_fenetres(cons: dict, de: int, a: int, k: int) -> list[int]:
    """Les débuts des fenêtres de `k` coutures consécutives, toutes avec un consensus, dans `[de, à)`."""
    return [s for s in range(int(de), int(a) - int(k) + 1) if all((s + i) in cons for i in range(int(k)))]


def les_trous_des_boucles(pas_par_bande: dict, R, C) -> list[dict]:
    """Les trous sur le PÉRIMÈTRE des boucles — ceux qui les laissent ouvertes —, et les lignes qui y lisent."""
    out = []
    for (sens, centre), pas in sorted(pas_par_bande.items()):
        de, a = (C[0], C[2]) if sens == "rangees" else (R[0], R[2])
        for debut, n in les_trous(le_consensus(pas), de, a):
            out.append({"la_bande": f"{sens}_{centre}", "le_sens": sens, "le_centre": int(centre),
                        "le_debut": int(debut), "la_longueur": int(n),
                        "les_lignes_presentes": {str(s): sorted(int(l_) for l_ in pas if s in pas[l_])
                                                 for s in range(debut, debut + n)}})
    return out


# ─────────────────────────────── les règles ───────────────────────────────

def la_somme_des_lignes(pas: dict, lignes, s: int, k: int) -> float | None:
    """La somme sur `k` coutures de la médiane des `lignes` — ou rien si l'une manque à une couture."""
    tot = 0.0
    for c in range(int(s), int(s) + int(k)):
        v = [float(pas[l_][c]) for l_ in lignes if c in pas[l_]]
        if len(v) != len(lignes):
            return None
        tot += float(np.median(v))
    return tot


def resumer(ecarts, demi: float = DEMI_PAS_EN_VOXELS) -> dict:
    a = np.asarray(ecarts, dtype=float)
    if not len(a):
        return {"combien": 0, "combien_au_dela_du_demi_pli": 0, "la_plus_grande": None, "la_mediane": None}
    return {"combien": int(len(a)), "combien_au_dela_du_demi_pli": int(np.sum(a >= float(demi))),
            "la_plus_grande": round(float(a.max()), 4), "la_mediane": round(float(np.median(a)), 4)}


def simuler(pas_par_bande: dict, etendues: dict, longueurs, demi: float = DEMI_PAS_EN_VOXELS) -> dict:
    """Pour chaque longueur de trou observée, l'écart de chaque règle au consensus, fenêtre par fenêtre.

    ⚠⚠ La fenêtre est CACHÉE puis franchie : le maillage par des pas nuls, les lignes présentes par chaque
    paire et chaque ligne seule qui couvrent la fenêtre sans un trou. Toutes, sans tirage.
    """
    ecarts = {int(k): {r: [] for r in LES_SIMULEES} for k in longueurs}
    for cle in sorted(pas_par_bande):
        pas = pas_par_bande[cle]
        cons = le_consensus(pas)
        de, a = etendues[cle]
        lignes = sorted(pas)
        for k in ecarts:
            for s in les_fenetres(cons, de, a, k):
                ref = float(sum(float(cons[s + i]) for i in range(k)))
                ecarts[k]["le_maillage"].append(abs(ref))
                for m, nom in ((2, "deux_lignes"), (1, "une_ligne")):
                    for sous in itertools.combinations(lignes, m):
                        x = la_somme_des_lignes(pas, sous, s, k)
                        if x is not None:
                            ecarts[k][nom].append(abs(x - ref))
    return {str(k): {r: resumer(e, demi) for r, e in d.items()} for k, d in sorted(ecarts.items())}


def la_cle_simulee(regle: str, trous: list[dict]) -> str | None:
    """Sous quelle forme une règle est jugée : les lignes présentes au nombre que les trous réels gardent."""
    if regle == "le_maillage":
        return "le_maillage"
    if not trous:
        return None
    m = min(len(v) for t in trous for v in t["les_lignes_presentes"].values())
    return None if m < 1 else ("deux_lignes" if m >= 2 else "une_ligne")


def la_regle_retenue(simulation: dict, trous: list[dict]) -> dict:
    """Parmi les règles qui s'appliquent et franchissent TOUTES les longueurs, le plus petit écart maximal
    à la longueur des trous des boucles — à égalité, le maillage."""
    if not trous:
        return {"decidable": False, "raison": "aucun trou sur le périmètre des boucles"}
    candidates, franchit = {}, {}
    for regle in LES_REGLES:
        cle = la_cle_simulee(regle, trous)
        if cle is None:
            franchit[regle] = None
            continue
        ok = all(simulation[k][cle]["combien"] > 0 and simulation[k][cle]["combien_au_dela_du_demi_pli"] == 0
                 for k in simulation)
        franchit[regle] = bool(ok)
        if ok:
            pire = max(float(simulation[str(t["la_longueur"])][cle]["la_plus_grande"]) for t in trous)
            candidates[regle] = (pire, LES_REGLES.index(regle), cle)
    if not candidates:
        return {"decidable": True, "la_regle": None, "franchit_toutes_les_longueurs": franchit}
    r = min(candidates, key=lambda x: candidates[x][:2])
    return {"decidable": True, "la_regle": r, "la_cle_simulee": candidates[r][2],
            "lecart_le_plus_grand_a_la_longueur_des_trous": round(candidates[r][0], 4),
            "franchit_toutes_les_longueurs": franchit}


def les_pas_dune_regle(regle: str, pas: dict, trou: dict) -> dict | None:
    """Les pas qu'une règle écrit dans un trou réel — ou rien, si elle ne s'y applique pas."""
    seams = range(int(trou["le_debut"]), int(trou["le_debut"]) + int(trou["la_longueur"]))
    if regle == "le_maillage":
        return {int(s): 0.0 for s in seams}
    out = {}
    for s in seams:
        v = [float(pas[l_][s]) for l_ in sorted(pas) if s in pas[l_]]
        if not v:
            return None
        out[int(s)] = float(np.median(v))
    return out


def le_remplissage(regle: str, pas_par_bande: dict, trous: list[dict]) -> dict | None:
    """`{(sens, centre): {couture: pas}}` pour tous les trous des boucles, ou rien si un trou refuse la règle."""
    out = {}
    for t in trous:
        k = (t["le_sens"], int(t["le_centre"]))
        x = les_pas_dune_regle(regle, pas_par_bande[k], t)
        if x is None:
            return None
        out.setdefault(k, {}).update(x)
    return out


# ─────────────────────────────── le verdict ───────────────────────────────

def _ce_qui_reste(regle: str | None, depasse: bool, grand_ferme: bool) -> str:
    """Les quatre issues, EXCLUSIVES."""
    if regle is None:
        return "AUCUNE RÈGLE NE FRANCHIT TOUTES LES LONGUEURS DE TROU OBSERVÉES SANS QUITTER LE FEUILLET"
    n = LES_NOMS[regle]
    if depasse:
        return f"LE TROU SE FRANCHIT PAR {n}, MAIS UN CHEMIN ARRIVE ALORS SUR UNE AUTRE SPIRE"
    if not grand_ferme:
        return f"LE TROU SE FRANCHIT PAR {n}, MAIS LE GRAND RECTANGLE RESTE OUVERT"
    return f"LE TROU SE FRANCHIT PAR {n}, ET TOUTES LES BOUCLES, GRAND RECTANGLE COMPRIS, RESTENT SUR LA MÊME SPIRE"


def _les_boucles_en_bref(a: dict) -> dict:
    out = {}
    for n, b in a["les_boucles"].items():
        x = {"fermable": bool(b.get("fermable"))}
        if b.get("fermable"):
            x.update({"la_fermeture_en_voxels": b["la_fermeture_en_voxels"],
                      "sous_le_demi_pli": b["sous_le_demi_pli"], "le_nul": b.get("le_nul")})
        out[n] = x
    return out


def mesurer(graine: int | None = None, tirages: int | None = None, replicats: int | None = None,
            avec_etalon: bool = True, par219: dict | None = None, par223: dict | None = None,
            par224: dict | None = None, demi: float = DEMI_PAS_EN_VOXELS) -> dict:
    """La mesure entière — et elle NE LIT PAS LE VOLUME."""
    par219 = ce_que_219_a_rendu() if par219 is None else par219
    par223 = ce_que_223_a_rendu() if par223 is None else par223
    par224 = ce_que_224_a_rendu() if par224 is None else par224
    base = {"la_question_declaree": LA_QUESTION_DECLAREE, "la_mesure_declaree": LA_MESURE_DECLAREE}
    for nom, par in (("219", par219), ("223", par223), ("224", par224)):
        if not par.get("decidable"):
            return {**base, "decidable": False, "raison": f"`{nom}` : {par.get('raison')}"}
    g = par224["graine"] if graine is None else int(graine)
    t_ = par224["tirages"] if tirages is None else int(tirages)
    rp_ = par224["replicats"] if replicats is None else int(replicats)
    R, C = par224["R"], par224["C"]
    gy, gx = par224["la_grille"]
    pas = les_pas_des_six_bandes(par219, par223, par224["relues"], par224["bandes"], R, C)
    base.update({"graine": g, "tirages": t_, "replicats": rp_, "demi_pli_en_voxels": int(demi)})

    # ⚠⚠ D'ABORD, 224 REJOUÉ SANS RIEN REMPLIR : il doit retomber sur ses fermetures publiées.
    sans = analyser(pas, R, C, g, t_, rp_, False)
    if not sans.get("decidable"):
        return {**base, "decidable": False, "raison": f"l'analyse de `224` : {sans.get('raison')}"}
    for n, b in par224["les_boucles"].items():
        m = sans["les_boucles"].get(n) or {}
        if bool(m.get("fermable")) != bool(b.get("fermable")) or (
                b.get("fermable") and m["la_fermeture_en_voxels"] != b["la_fermeture_en_voxels"]):
            return {**base, "decidable": False,
                    "raison": f"l'analyse de `224` rejouée ne retombe pas sur la boucle {n}"}
    base["la_reproduction_de_224"] = {"decidable": True, "les_boucles_relues": len(par224["les_boucles"]),
                                      "les_boucles_fermables": sum(1 for b in par224["les_boucles"].values()
                                                                   if b.get("fermable"))}

    etendues = les_etendues(R, C, gy, gx)
    trous_par_bande = {f"{s}_{c}": les_trous(le_consensus(p), *etendues[(s, c)])
                       for (s, c), p in sorted(pas.items())}
    longueurs = sorted({int(n) for v in trous_par_bande.values() for _, n in v})
    if not longueurs:
        return {**base, "decidable": False, "raison": "aucune bande n'a de trou de majorité"}
    sim = simuler(pas, etendues, longueurs, demi)
    trous = les_trous_des_boucles(pas, R, C)
    choix = la_regle_retenue(sim, trous)
    if not choix.get("decidable"):
        return {**base, "decidable": False, "raison": choix.get("raison")}

    franchissements = {}
    for regle in LES_REGLES:
        rem = le_remplissage(regle, pas, trous)
        if rem is None:
            franchissements[regle] = {"applicable": False}
            continue
        a = analyser(pas, R, C, g, t_, rp_, bool(avec_etalon and regle == choix.get("la_regle")), demi, rem)
        if not a.get("decidable"):
            return {**base, "decidable": False, "raison": f"{regle} : {a.get('raison')}"}
        franchissements[regle] = {
            "applicable": True, "les_coutures_remplies": a["les_coutures_remplies"],
            "les_boucles": _les_boucles_en_bref(a), "lepreuve": {k: v for k, v in a["lepreuve"].items()
                                                                  if k != "par_rectangle"},
            "letalon_de_lepreuve": a["letalon_de_lepreuve"],
            "le_grand_rectangle_en_deux_chemins": (
                a["les_boucles"]["le_grand_rectangle"].get("les_deux_chemins_en_voxels")),
            "la_plus_grande_fermeture_en_valeur_absolue":
                a["le_verdict"]["la_plus_grande_fermeture_en_valeur_absolue"],
            "les_boucles_qui_depassent": a["le_verdict"]["les_boucles_qui_depassent"],
            "les_boucles_ouvertes": a["le_verdict"]["les_boucles_ouvertes"],
            "mieux_que_des_marches_independantes": a["le_verdict"]["mieux_que_des_marches_independantes"]}

    r = choix.get("la_regle")
    f_ = franchissements.get(r) or {}
    depasse = bool(f_.get("les_boucles_qui_depassent"))
    grand = bool((f_.get("les_boucles") or {}).get("le_grand_rectangle", {}).get("fermable"))
    return {**base, "decidable": True, "les_trous_par_bande": trous_par_bande,
            "les_longueurs_observees": longueurs, "la_simulation": sim, "les_trous_des_boucles": trous,
            "la_regle_retenue": choix, "les_franchissements": franchissements,
            "le_verdict": {"la_regle": r, "les_boucles_qui_depassent": f_.get("les_boucles_qui_depassent"),
                           "les_boucles_ouvertes": f_.get("les_boucles_ouvertes"),
                           "la_plus_grande_fermeture_en_valeur_absolue":
                               f_.get("la_plus_grande_fermeture_en_valeur_absolue"),
                           "le_grand_rectangle_se_ferme": grand,
                           "mieux_que_des_marches_independantes": f_.get("mieux_que_des_marches_independantes"),
                           "ce_qui_reste_a_mesurer": _ce_qui_reste(r, depasse, grand)}}


def afficher(r: dict) -> None:
    if not r.get("decidable"):
        print(f"indécidable : {r.get('raison')}")
        return
    print(f"224 rejoué : {r['la_reproduction_de_224']}")
    for k, v in r["les_trous_par_bande"].items():
        print(f"  trous {k} : {v}")
    print(f"longueurs observées : {r['les_longueurs_observees']}")
    for k, d in r["la_simulation"].items():
        print(f"  k={k} · " + " · ".join(f"{n} {x['combien_au_dela_du_demi_pli']}/{x['combien']} max "
                                         f"{x['la_plus_grande']} méd {x['la_mediane']}" for n, x in d.items()))
    print(f"trous des boucles : {r['les_trous_des_boucles']}")
    print(f"règle retenue : {r['la_regle_retenue']}")
    for regle, f in r["les_franchissements"].items():
        if not f.get("applicable"):
            print(f"  {regle} : ne s'applique pas")
            continue
        print(f"  {regle} · remplies {f['les_coutures_remplies']} · " + " · ".join(
            f"{n} {b.get('la_fermeture_en_voxels', 'ouverte')}" for n, b in f["les_boucles"].items()))
        e = f["lepreuve"]
        if e.get("decidable"):
            print(f"    épreuve · T {e['la_statistique']} contre {e['la_statistique_mediane_du_nul']} · p "
                  f"{e['la_valeur_p']}")
        t = f.get("letalon_de_lepreuve")
        if t:
            print(f"    étalon · {t['combien_concluent_mieux']}/{t['les_replicats']} (borne {t['la_borne']}) · "
                  f"tient {t['elle_tient_sa_garantie']}")
    print(f"VERDICT · {r['le_verdict']['ce_qui_reste_a_mesurer']}")


# ─────────────────────────────── la batterie ───────────────────────────────

def verifier() -> int:
    import copy

    from deux_chemins_arrivent_ils_sur_la_meme_spire import les_centres
    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        if not ok:
            echecs.append(f"{nom} {detail}")

    def _sur(f, *a, **k):
        try:
            return f(*a, **k)
        except Exception as e:  # noqa: BLE001
            return {"decidable": False, "raison": f"exception {type(e).__name__}: {e}"}

    def _ok(f):
        try:
            return bool(f())
        except Exception:  # noqa: BLE001
            return False

    # ── les trous
    cons = {s: 1.0 for s in range(0, 20) if s not in (0, 1, 7, 12, 13, 14, 19)}
    v("★★★★ les trous sont les suites sans consensus, bords compris",
      les_trous(cons, 0, 20) == [[0, 2], [7, 1], [12, 3], [19, 1]], str(les_trous(cons, 0, 20)))
    v("★★★ une étendue sans trou n'en a pas, une étendue vide non plus",
      les_trous(cons, 2, 7) == [] and les_trous(cons, 5, 5) == [])
    v("★★★★ une fenêtre n'est prise que là où le consensus existe à chaque couture",
      les_fenetres(cons, 0, 20, 3) == [2, 3, 4, 8, 9, 15, 16] and les_fenetres(cons, 0, 20, 5) == [2],
      str(les_fenetres(cons, 0, 20, 3)))

    # ── les longueurs observées sont celles que 221 et 223 publient
    p219, p223 = ce_que_219_a_rendu(), ce_que_223_a_rendu()

    def _complement(troncons, n):  # noqa: E306
        dedans = {s for a_, b_, _k in troncons for s in range(a_, b_ + 1)}
        return les_trous({s: 0.0 for s in dedans}, 0, n)
    d221 = json.loads((MESURES / "le_consensus_traverse_t_il_la_rangee.json").read_text())
    d223 = json.loads((MESURES / "le_consensus_traverse_t_il_la_hauteur.json").read_text())
    v("★★★★ les trous de la bande de 219 sont exactement le complément des tronçons que 221 publie",
      _ok(lambda: les_trous(le_consensus(p219["les_pas_par_rangee"]), 0, p219["les_coutures_dune_rangee"])
          == _complement(d221["les_troncons_du_consensus"], d221["les_coutures_dune_rangee"])))
    v("★★★★ et ceux de la bande de 223, du complément que 223 publie",
      _ok(lambda: les_trous(le_consensus(p223["les_pas_par_colonne"]), 0, d223["les_coutures_dune_colonne"])
          == _complement(d223["les_troncons_du_consensus"], d223["les_coutures_dune_colonne"])))
    et = les_etendues([99, 198, 297], [71, 142, 213], 396, 285)
    v("★★★ les bandes publiées sont prises sur toute la grille, les quatre de 224 sur leur portion",
      et[("rangees", 198)] == (0, 284) and et[("colonnes", 142)] == (0, 395)
      and et[("rangees", 99)] == (71, 213) and et[("colonnes", 213)] == (99, 297))

    # ── les règles
    pas = {1: {0: 1.0, 1: 2.0, 2: 3.0}, 2: {0: 1.0, 1: 4.0, 2: 3.0}, 3: {0: 1.0, 2: 3.0}}
    v("★★★★ les lignes présentes rendent la médiane de leurs pas, couture par couture",
      la_somme_des_lignes(pas, (1, 2), 0, 3) == 1.0 + 3.0 + 3.0 and la_somme_des_lignes(pas, (3,), 0, 1) == 1.0)
    v("★★★ une ligne qui manque à une couture ne franchit pas la fenêtre",
      la_somme_des_lignes(pas, (1, 3), 0, 3) is None)
    r_ = resumer([1.0, 36.0, 40.0, 2.0])
    v("★★★ au-delà du demi-feuillet, c'est à partir du demi-feuillet",
      r_["combien_au_dela_du_demi_pli"] == 2 and r_["la_plus_grande"] == 40.0 and r_["combien"] == 4)
    g = np.random.default_rng(5)
    base_ = {c: float(g.normal(0.0, 1.0)) for c in range(40)}
    bande = {l_: dict(base_) for l_ in range(5)}
    bande[4] = {c: x + (50.0 if c == 20 else 0.0) for c, x in base_.items()}
    sim = _sur(simuler, {("rangees", 1): bande}, {("rangees", 1): (0, 40)}, [1, 3])
    v("★★★★ le maillage s'écarte de la somme du consensus, les lignes sans écart ne s'en écartent pas",
      _ok(lambda: sim["1"]["le_maillage"]["combien"] == 40
          and sim["1"]["le_maillage"]["la_plus_grande"] == round(max(abs(x) for x in base_.values()), 4)
          and sim["3"]["deux_lignes"]["la_mediane"] == 0.0
          and sim["3"]["le_maillage"]["la_plus_grande"] == round(max(
              abs(sum(base_[s + i] for i in range(3))) for s in range(38)), 4)))
    v("★★★★ une ligne qui s'écarte ne compte que dans les paires et les lignes seules qui la prennent",
      _ok(lambda: sim["1"]["une_ligne"]["combien_au_dela_du_demi_pli"] == 1
          and sim["1"]["deux_lignes"]["combien_au_dela_du_demi_pli"] == 0
          and sim["1"]["deux_lignes"]["la_plus_grande"] == 25.0
          and sim["3"]["une_ligne"]["combien_au_dela_du_demi_pli"] == 3
          and sim["1"]["deux_lignes"]["combien"] == 40 * 10 and sim["1"]["une_ligne"]["combien"] == 40 * 5),
      str(sim.get("1")))

    # ── la règle retenue
    def _s(maillage, deux, une):  # noqa: E306
        return {"combien": 10, "combien_au_dela_du_demi_pli": 0, "la_plus_grande": maillage}, \
            {"combien": 10, "combien_au_dela_du_demi_pli": 0, "la_plus_grande": deux}, \
            {"combien": 10, "combien_au_dela_du_demi_pli": 0, "la_plus_grande": une}

    t2 = [{"la_longueur": 2, "les_lignes_presentes": {"140": [213, 215], "141": [213, 215]}}]
    t1 = [{"la_longueur": 2, "les_lignes_presentes": {"140": [213], "141": [213, 215]}}]
    t0 = [{"la_longueur": 2, "les_lignes_presentes": {"140": [], "141": [213]}}]
    s_ = {"2": dict(zip(LES_SIMULEES, _s(5.0, 3.0, 9.0))), "7": dict(zip(LES_SIMULEES, _s(8.0, 6.0, 20.0)))}
    v("★★★★ la règle retenue a le plus petit écart maximal à la longueur des trous des boucles",
      la_regle_retenue(s_, t2)["la_regle"] == "les_lignes_presentes"
      and la_regle_retenue(s_, t2)["la_cle_simulee"] == "deux_lignes")
    v("★★★★ les lignes présentes sont jugées au nombre de lignes que le trou garde",
      la_regle_retenue(s_, t1)["la_regle"] == "le_maillage" and la_cle_simulee("les_lignes_presentes", t1)
      == "une_ligne" and la_cle_simulee("les_lignes_presentes", t0) is None)
    s2 = copy.deepcopy(s_)
    s2["2"]["deux_lignes"]["la_plus_grande"] = 5.0
    v("★★★ à égalité, le maillage", la_regle_retenue(s2, t2)["la_regle"] == "le_maillage")
    s3 = copy.deepcopy(s_)
    s3["7"]["deux_lignes"]["combien_au_dela_du_demi_pli"] = 1
    v("★★★★ une règle qui laisse une seule fenêtre quitter le feuillet, à une seule longueur, n'est pas retenue",
      la_regle_retenue(s3, t2)["la_regle"] == "le_maillage"
      and la_regle_retenue(s3, t2)["franchit_toutes_les_longueurs"]["les_lignes_presentes"] is False)
    s4 = copy.deepcopy(s3)
    s4["2"]["le_maillage"]["combien_au_dela_du_demi_pli"] = 1
    v("★★★ sans règle qui franchit tout, aucune n'est retenue", la_regle_retenue(s4, t2)["la_regle"] is None)
    v("★★ sans trou dans les boucles, pas de choix", not la_regle_retenue(s_, []).get("decidable"))
    v("★★ une longueur sans aucune fenêtre ne compte pas comme franchie", _ok(lambda: la_regle_retenue(
        {**s2, "17": dict(zip(LES_SIMULEES, [dict(x, combien=0) for x in _s(1.0, 1.0, 1.0)]))},
        t2)["la_regle"] is None))

    # ── les pas écrits au trou
    bb = {213: {139: 1.0, 142: 2.0}, 215: {140: 3.0, 141: 5.0}, 211: {140: 1.0, 141: 1.0}}
    tr = {"le_sens": "colonnes", "le_centre": 213, "le_debut": 140, "la_longueur": 2}
    v("★★★★ le maillage écrit des pas nuls, les lignes présentes leur médiane",
      les_pas_dune_regle("le_maillage", bb, tr) == {140: 0.0, 141: 0.0}
      and les_pas_dune_regle("les_lignes_presentes", bb, tr) == {140: 2.0, 141: 3.0})
    v("★★★ sans aucune ligne à une couture du trou, les lignes présentes ne s'appliquent pas",
      les_pas_dune_regle("les_lignes_presentes", {213: {139: 1.0}}, tr) is None
      and le_remplissage("les_lignes_presentes", {("colonnes", 213): {213: {139: 1.0}}}, [tr]) is None)

    # ── le remplissage dans l'analyse de 224
    R, C = [2, 5, 8], [1, 4, 7]
    gg = np.random.default_rng(11)
    D = gg.normal(0.0, 5.0, (11, 10))
    pb = {}
    for r in R:
        pb[("rangees", r)] = {l_: {c: float(D[r, c + 1] - D[r, c]) for c in range(0, 9)}
                              for l_ in range(r - 2, r + 3)}
    for c in C:
        pb[("colonnes", c)] = {l_: {r: float(D[r + 1, c] - D[r, c]) for r in range(0, 10)}
                               for l_ in range(c - 2, c + 3)}
    vrai = {3: pb[("colonnes", 7)][7][3], 4: pb[("colonnes", 7)][7][4]}
    for l_ in (5, 6, 8):
        for s in (3, 4):
            pb[("colonnes", 7)][l_].pop(s)
    ouvert = _sur(analyser, pb, R, C, 3, 19, 2, False)
    rempli = _sur(analyser, pb, R, C, 3, 19, 2, False, DEMI_PAS_EN_VOXELS, {("colonnes", 7): vrai})
    v("★★★★ un trou rempli de ses vrais pas ferme sa boucle et le grand rectangle, exactement",
      _ok(lambda: ouvert["le_verdict"]["les_boucles_ouvertes"] == ["haut_droite", "le_grand_rectangle"]
          and rempli["le_verdict"]["les_boucles_ouvertes"] == []
          and abs(rempli["les_boucles"]["haut_droite"]["la_fermeture_en_voxels"]) < 1e-9
          and abs(rempli["les_boucles"]["le_grand_rectangle"]["la_fermeture_en_voxels"]) < 1e-9))
    v("★★★★ et la couverture nomme encore le trou comblé, que les coutures remplies disent",
      _ok(lambda: rempli["la_couverture_du_consensus"]["colonnes_7"]["les_coutures_sans_consensus"] == [3, 4]
          and rempli["les_coutures_remplies"] == {"colonnes_7": {"3": round(vrai[3], 4), "4": round(vrai[4], 4)}}
          and "les_coutures_remplies" not in ouvert))
    faux = _sur(analyser, pb, R, C, 3, 19, 2, False, DEMI_PAS_EN_VOXELS, {("colonnes", 7): {2: 0.0, 3: 0.0}})
    v("★★★★ une couture qui a un consensus n'est jamais remplie", not faux.get("decidable")
      and "refusé" in str(faux.get("raison")), str(faux.get("raison")))

    # ── les issues
    iss = {_ce_qui_reste(r_, d_, g_) for r_ in ("le_maillage",) for d_ in (True, False) for g_ in (True, False)}
    iss.add(_ce_qui_reste(None, False, True))
    v("★★★★ quatre issues distinctes, et dépasser prime sur le grand rectangle",
      len(iss) == 4 and _ce_qui_reste("le_maillage", True, False) == _ce_qui_reste("le_maillage", True, True))
    v("★★★ l'issue nomme la règle", "LES LIGNES PRÉSENTES" in _ce_qui_reste("les_lignes_presentes", False, True))

    # ── la mesure entière, sur la matière publiée
    par224 = ce_que_224_a_rendu()
    v("★★★ `224` est relu, avec ses centres et sa grille",
      par224.get("decidable") and par224["R"] == les_centres(396) and par224["C"] == les_centres(285)
      and par224["la_grille"] == [396, 285])
    m = _sur(mesurer, None, 49, 2, False)
    v("★★★★ la mesure entière est décidable et rejoue d'abord 224 à l'identique",
      m.get("decidable") and m["la_reproduction_de_224"]["les_boucles_fermables"] == 3, str(m.get("raison")))
    v("★★★★ les longueurs simulées sont exactement celles des trous que les bandes montrent",
      _ok(lambda: m["les_longueurs_observees"] == sorted({n for vv in m["les_trous_par_bande"].values()
                                                          for _, n in vv})
          and sorted(m["la_simulation"]) == sorted(str(k) for k in m["les_longueurs_observees"])))
    v("★★★★ les trous des bandes publiées, dans la mesure, sont ceux que 221 et 223 publient",
      _ok(lambda: [tuple(x) for x in m["les_trous_par_bande"]["rangees_198"]]
          == [tuple(x) for x in _complement(d221["les_troncons_du_consensus"], d221["les_coutures_dune_rangee"])]
          and [tuple(x) for x in m["les_trous_par_bande"]["colonnes_142"]]
          == [tuple(x) for x in _complement(d223["les_troncons_du_consensus"], d223["les_coutures_dune_colonne"])]))
    v("★★★★ les trous des boucles sont ceux que 224 laisse ouverts",
      _ok(lambda: [(t["la_bande"], t["le_debut"], t["la_longueur"]) for t in m["les_trous_des_boucles"]]
          == [("colonnes_213", 140, 2)]))
    faux224 = copy.deepcopy(par224)
    faux224["les_boucles"]["bas_gauche"]["la_fermeture_en_voxels"] += 1.0
    v("★★★★ une analyse de 224 qui ne retombe pas sur ses fermetures publiées est refusée, par sa raison",
      "ne retombe pas" in str(_sur(mesurer, None, 49, 2, False, None, None, faux224).get("raison")))

    for e_ in echecs:
        print(f"  ÉCHEC {e_}")
    print(f"{Path(__file__).name}   "
          f"{'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path, default=None)
    p.add_argument("--sans-etalon", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(avec_etalon=not a.sans_etalon)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=2))
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
