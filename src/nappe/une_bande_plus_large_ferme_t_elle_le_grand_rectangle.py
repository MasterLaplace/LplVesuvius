"""L'erreur du consensus est un bruit qui s'accumule : une bande plus large ferme-t-elle le grand rectangle ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LA MOINDRE LIGNE NOUVELLE NE SOIT LUE.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P73`. De `224` à `227` : les chemins de consensus arrivent sur
la même spire au quart du segment ; leur erreur s'accumule comme une marche et le grand rectangle ferme à
−36,7188 voxels, juste au-delà du demi-feuillet (`225`) ; l'ajuster d'un coup la répand (`226`) ; la
chercher plus finement ne la trouve pas au-delà du bruit (`227`). Ce qui reste à essayer est de réduire le
bruit du pas lui-même.

## La largeur, dérivée

Cinq lignes, c'est le plus petit nombre que `218` a trouvé pour VOIR une rangée qui saute — pas une
largeur choisie contre le bruit. `218` a déclaré son échelle : 3, 5, 7 et 9 lignes. Cette tranche la reprend
telle quelle. Seules les quatre bandes du GRAND RECTANGLE sont élargies — c'est la boucle qui dépasse — de
cinq à neuf lignes : deux lignes de plus de chaque côté, lues comme deux bandes de deux lignes, sur la seule
portion que le grand rectangle traverse. Les cinq lignes du milieu sont celles que `224` a lues et publiées.

Pour chaque largeur `k` de l'échelle, les `k` lignes centrées de chaque bande, par la fonction de `219` ; le
consensus est la médiane des lignes présentes pourvu qu'elles soient une MAJORITÉ, `k // 2 + 1` — trois sur
cinq, comme `221`. Un trou de majorité est franchi par la règle que `225` a retenue, lue dans sa mesure.

## Ce qui contrôle

⚠⚠⚠ La lecture neuve croise les bandes publiées de `219`, `223` et `224` ; partout où deux lectures lisent la
même couture, elles retombent à l'arrondi, sur les mêmes coutures, sinon refus. ⚠⚠⚠ Et à la largeur de
cinq lignes, la fermeture doit retomber EXACTEMENT sur celle que `225` publie pour le grand rectangle : c'est
le même consensus, et sinon la tranche ne compare pas ce qu'elle croit comparer.

## Ce qui se mesure, à chaque largeur

1. ⭐⭐⭐⭐ LA FERMETURE DU GRAND RECTANGLE, contre le demi-feuillet ;
2. ⭐⭐⭐ LE BRUIT SEUL : les quatre côtés tirés indépendamment par blocs de leurs propres pas centrés
   (`R4-L22`, l'instrument de `224`) — la fermeture médiane et la part des tirages sous le demi-feuillet ;
3. ⭐⭐ LA DISPERSION DU PAS du consensus, mise en commun sur les quatre côtés, centrée côté par côté.

## Les issues, exclusives — jugées à neuf lignes contre cinq

- à neuf lignes, le bruit seul ne ferme pas moins qu'à cinq : la largeur ne réduit pas le bruit, et c'est
  le piège de `208`, la part que les lignes voisines partagent ;
- il ferme moins, mais le grand rectangle reste au-delà du demi-feuillet à neuf lignes ;
- il ferme moins, et le grand rectangle se ferme sous le demi-feuillet à neuf lignes.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : une boucle, un segment ; et une fermeture sous le demi-feuillet dit
que deux chemins s'accordent, pas lequel est sur la bonne spire.

Usage :
    uv run python src/nappe/une_bande_plus_large_ferme_t_elle_le_grand_rectangle.py --verifier
    uv run python src/nappe/une_bande_plus_large_ferme_t_elle_le_grand_rectangle.py --lire <lecture.json>
    uv run python src/nappe/une_bande_plus_large_ferme_t_elle_le_grand_rectangle.py --depuis <lecture.json> \\
        --json docs/mesures/une_bande_plus_large_ferme_t_elle_le_grand_rectangle.json
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

from cinq_rangees_designent_elles_la_fautive import les_rangees_a_lire  # noqa: E402
from deux_chemins_arrivent_ils_sur_la_meme_spire import (_la_definition,  # noqa: E402
                                                          ce_que_223_a_rendu, la_somme,
                                                          les_boucles_declarees, les_cotes,
                                                          les_sommes_par_blocs, lire_les_bandes,
                                                          relire_une_bande)
from lajustement_de_toutes_les_boucles_garde_t_il_la_spire import ce_que_225_a_rendu  # noqa: E402
from le_consensus_traverse_t_il_la_rangee import le_consensus  # noqa: E402
from le_vote_ramene_t_il_les_rangees_sur_le_feuillet import ce_que_219_a_rendu  # noqa: E402
from lecart_extreme_est_il_porte_par_une_rangee import LES_NOMBRES_DE_RANGEES  # noqa: E402
from ou_est_lerreur_de_la_boucle_en_haut_a_gauche import (la_reproduction_croisee,  # noqa: E402
                                                          le_domaine, les_pas_dune_bande,
                                                          les_sources_publiees)
from quest_ce_qui_franchit_le_trou_de_majorite import (ce_que_224_a_rendu, les_pas_dune_regle,  # noqa: E402
                                                       les_trous)
from que_montrent_ces_deux_vues import DEMI_PAS_EN_VOXELS  # noqa: E402

LA_BOUCLE = "le_grand_rectangle"
LA_QUESTION_DECLAREE = ("l'erreur du consensus est un bruit qui s'accumule : une bande plus large ferme-t-elle le "
                        "grand rectangle sous le demi-feuillet ?")
LA_MESURE_DECLAREE = ("à chaque largeur de l'échelle de `218`, la fermeture du grand rectangle, le bruit seul de "
                      "ses quatre côtés tirés par blocs, et la dispersion du pas du consensus")


# ─────────────────────────────── ce qui est dérivé ───────────────────────────────

def les_largeurs() -> list[int]:
    """L'échelle que `218` a déclarée, telle quelle."""
    return sorted(int(k) for k in LES_NOMBRES_DE_RANGEES)


def la_majorite(k: int) -> int:
    """Le nombre de lignes présentes qu'il faut pour voter : une majorité, `k // 2 + 1`."""
    return int(k) // 2 + 1


def les_bandes_du_grand_rectangle(R, C) -> list[tuple]:
    """Les quatre bandes du grand rectangle : `(sens, centre, de, à)` en chunks lus."""
    r0, r1, c0, c1 = les_boucles_declarees(R, C)[LA_BOUCLE]
    return [("rangees", r0, c0, c1), ("rangees", r1, c0, c1), ("colonnes", c0, r0, r1), ("colonnes", c1, r0, r1)]


def les_bandes_a_lire(R, C, publiee: int, large: int) -> list[dict]:
    """Les lignes à lire en plus : ce que la largeur `large` a de plus que la largeur `publiee`, de part et
    d'autre, chaque côté lu comme une bande de lignes CONSÉCUTIVES — sinon un pas vertical enjamberait."""
    out = []
    for sens, centre, de, a in les_bandes_du_grand_rectangle(R, C):
        toutes, deja = les_rangees_a_lire(centre, large), set(les_rangees_a_lire(centre, publiee))
        avant = [x for x in toutes if x < min(deja)]
        apres = [x for x in toutes if x > max(deja)]
        for nom, lignes in (("avant", avant), ("apres", apres)):
            if lignes:
                out.append({"cle": f"{sens}_{centre}_{nom}", "le_sens": sens, "le_centre": int(centre),
                            "les_lignes": lignes, "de": int(de), "a": int(a)})
    return out


# ─────────────────────────────── la mesure, largeur par largeur ───────────────────────────────

def a_une_largeur(pas: dict, centre: int, k: int) -> dict:
    """Les lignes centrées d'une largeur `k`, et elles seules."""
    garde = set(les_rangees_a_lire(centre, k))
    return {l_: s for l_, s in pas.items() if l_ in garde}


def le_consensus_franchi(pas_k: dict, k: int, de: int, a: int, regle: str) -> tuple[dict, list]:
    """Le consensus à une largeur, ses trous sur `[de, à)` franchis par la règle de `225`, et ces trous."""
    cons = le_consensus(pas_k, la_majorite(k))
    trous = les_trous(cons, de, a)
    for debut, n in trous:
        x = les_pas_dune_regle(regle, pas_k, {"le_debut": debut, "la_longueur": n})
        if x is None:
            return None, trous
        cons = {**cons, **x}
    return cons, trous


def une_largeur(pas_par_bande: dict, R, C, k: int, regle: str, graine: int, tirages: int,
                demi: float = DEMI_PAS_EN_VOXELS) -> dict:
    """À une largeur : la fermeture du grand rectangle, son bruit seul, la dispersion du pas."""
    coins = les_boucles_declarees(R, C)[LA_BOUCLE]
    cotes, pas_cotes, trous, nlignes = [], {}, {}, {}
    L = 0.0
    for sens, centre, de, a, signe, nom in les_cotes(coins):
        pas_k = a_une_largeur(pas_par_bande[(sens, centre)], centre, k)
        nlignes[nom] = len(pas_k)
        cons, tr = le_consensus_franchi(pas_k, k, de, a, regle)
        if tr:
            trous[f"{sens}_{centre}"] = [list(t) for t in tr]
        if cons is None:
            return {"decidable": False, "raison": f"à {k} lignes, un trou de {sens} {centre} ne se franchit pas",
                    "les_trous": trous}
        s, _m = la_somme(cons, de, a)
        L += signe * s
        pas_cotes[nom] = (signe, [float(cons[x]) for x in range(de, a)])
        cotes.append({"le_cote": nom, "la_somme_en_voxels": round(float(s), 4)})
    centres = [np.asarray(p, dtype=float) - float(np.mean(p)) for _s, p in pas_cotes.values()]
    disp = float(np.sqrt(sum(float(np.dot(c, c)) for c in centres) / sum(len(c) for c in centres)))
    nul = sum(sg * les_sommes_par_blocs(p, tirages, int(graine) + 101 * i)
              for i, (nom, (sg, p)) in enumerate(sorted(pas_cotes.items())))
    an = np.abs(np.asarray(nul, dtype=float))
    return {"decidable": True, "la_largeur": int(k), "la_majorite": la_majorite(k),
            "la_fermeture_en_voxels": round(float(L), 4), "sous_le_demi_pli": bool(abs(L) < float(demi)),
            "les_cotes": cotes, "les_trous_franchis": trous, "les_lignes_par_cote": nlignes,
            "la_dispersion_du_pas_en_voxels": round(disp, 4),
            "le_nul": {"la_fermeture_mediane_en_valeur_absolue": round(float(np.median(an)), 4),
                       "la_part_sous_le_demi_pli": round(float(np.mean(an < float(demi))), 4),
                       "la_part_sous_la_fermeture": round(float(np.mean(an <= abs(L))), 4)}}


def _ce_qui_reste(reduit: bool, ferme: bool) -> str:
    """Les trois issues, EXCLUSIVES — et ne pas réduire le bruit prime."""
    if not reduit:
        return ("À NEUF LIGNES, LE BRUIT SEUL NE FERME PAS MOINS QU'À CINQ : LA LARGEUR NE RÉDUIT PAS LE BRUIT DU "
                "CONSENSUS")
    if not ferme:
        return ("LA LARGEUR RÉDUIT LE BRUIT, MAIS LE GRAND RECTANGLE RESTE AU-DELÀ DU DEMI-FEUILLET À NEUF LIGNES")
    return "UNE BANDE DE NEUF LIGNES FERME LE GRAND RECTANGLE SOUS LE DEMI-FEUILLET"


def analyser(pas_par_bande: dict, R, C, regle: str, graine: int, tirages: int,
             demi: float = DEMI_PAS_EN_VOXELS) -> dict:
    """Toutes les largeurs de l'échelle — pur."""
    par = {}
    for k in les_largeurs():
        x = une_largeur(pas_par_bande, R, C, k, regle, graine, tirages, demi)
        if not x.get("decidable"):
            return {"decidable": False, "raison": x.get("raison")}
        par[str(k)] = x
    ks = les_largeurs()
    k0, k1 = 5, ks[-1]
    reduit = par[str(k1)]["le_nul"]["la_fermeture_mediane_en_valeur_absolue"] < \
        par[str(k0)]["le_nul"]["la_fermeture_mediane_en_valeur_absolue"]
    ferme = par[str(k1)]["sous_le_demi_pli"]
    return {"decidable": True, "les_largeurs": ks, "par_largeur": par,
            "le_verdict": {"le_bruit_diminue_de_cinq_a_neuf": bool(reduit),
                           "le_grand_rectangle_se_ferme_a_neuf": bool(ferme),
                           "ce_qui_reste_a_mesurer": _ce_qui_reste(reduit, ferme)}}


def les_pas_elargis(par224: dict, relues: dict, bandes_lues) -> dict:
    """Pour chaque bande du grand rectangle, ses cinq lignes publiées et les lignes lues ici, réunies."""
    out = {}
    for sens, centre, de, a in les_bandes_du_grand_rectangle(par224["R"], par224["C"]):
        pub = par224["relues"][f"{sens}_{centre}"]["le_long"]
        lignes = {int(l_): {int(s): float(x[0]) for s, x in d.items()} for l_, d in pub.items()}
        for b in bandes_lues:
            if b["le_sens"] == sens and b["le_centre"] == centre:
                for l_, d in relues[b["cle"]]["le_long"].items():
                    lignes[int(l_)] = {int(s): float(x[0]) for s, x in d.items()}
        out[(sens, int(centre))] = lignes
    return out


def mesurer(depuis: Path | None = None, par219: dict | None = None, par223: dict | None = None,
            par224: dict | None = None, par225: dict | None = None, lire=None,
            tirages: int | None = None) -> dict:
    """La lecture des lignes de plus puis l'analyse — ou l'analyse seule, rejouée."""
    par219 = ce_que_219_a_rendu() if par219 is None else par219
    par223 = ce_que_223_a_rendu() if par223 is None else par223
    par224 = ce_que_224_a_rendu() if par224 is None else par224
    par225 = ce_que_225_a_rendu() if par225 is None else par225
    base = {"la_question_declaree": LA_QUESTION_DECLAREE, "la_mesure_declaree": LA_MESURE_DECLAREE}
    for nom, par in (("219", par219), ("223", par223), ("224", par224), ("225", par225)):
        if not par.get("decidable"):
            return {**base, "decidable": False, "raison": f"`{nom}` : {par.get('raison')}"}
    R, C = par224["R"], par224["C"]
    publiee = len(par219["les_rangees"])
    bandes = les_bandes_a_lire(R, C, publiee, les_largeurs()[-1])
    g = par224["graine"]
    t_ = par224["tirages"] if tirages is None else int(tirages)
    if depuis is not None:
        lu = {"decidable": True, "les_bandes": json.loads(Path(depuis).read_text()).get("les_bandes") or {}}
    else:
        lu = lire_les_bandes(bandes, lire=lire)
    base.update({"graine": int(g), "tirages": t_, "les_largeurs_de_218": les_largeurs(),
                 "la_regle_de_225": par225["la_regle"], "les_bandes_declarees": bandes,
                 "les_bandes": lu.get("les_bandes") or {}})
    if not lu.get("decidable"):
        return {**base, "decidable": False, "raison": lu.get("raison")}
    pub = lu["les_bandes"]
    if (sorted(pub) != sorted(b["cle"] for b in bandes)
            or any(_la_definition(pub[b["cle"]]) != _la_definition(b) for b in bandes)):
        return {**base, "decidable": False, "raison": "la lecture n'est pas celle des lignes dérivées"}
    relues = {k: relire_une_bande(x) for k, x in pub.items()}
    nouvelles = {b["cle"]: {"domaine": le_domaine(b["le_sens"], b["les_lignes"], b["de"], b["a"]),
                            "pas": les_pas_dune_bande(relues[b["cle"]])} for b in bandes}
    rep = la_reproduction_croisee(nouvelles, les_sources_publiees(par219, par223, par224))
    if not rep.get("decidable"):
        return {**base, "decidable": False, "raison": rep.get("raison"), "la_reproduction": rep}
    pas = les_pas_elargis(par224, relues, bandes)
    a = analyser(pas, R, C, par225["la_regle"], g, t_)
    if not a.get("decidable"):
        return {**base, "decidable": False, "raison": a.get("raison"), "la_reproduction": rep}
    # ⚠⚠⚠ À CINQ LIGNES, LE GRAND RECTANGLE RETOMBE EXACTEMENT SUR `225`, ou refus.
    f5 = a["par_largeur"][str(publiee)]["la_fermeture_en_voxels"]
    if f5 != par225["les_fermetures"].get(LA_BOUCLE):
        return {**base, "decidable": False, "la_reproduction": rep,
                "raison": f"à {publiee} lignes, le grand rectangle ne retombe pas sur `225` ({f5})"}
    return {**base, "la_reproduction": rep, "la_fermeture_de_225": par225["les_fermetures"][LA_BOUCLE], **a}


def afficher(r: dict) -> None:
    if not r.get("decidable"):
        print(f"indécidable : {r.get('raison')}")
        return
    rp = r["la_reproduction"]
    print(f"reproduction : {rp['combien_de_coutures_relues']} coutures {rp['par_croisement']}, écart "
          f"{rp['lecart_le_plus_grand']}")
    for k, x in r["par_largeur"].items():
        print(f"  {k} lignes · L {x['la_fermeture_en_voxels']} · σ {x['la_dispersion_du_pas_en_voxels']} · nul "
              f"{x['le_nul']} · trous {x['les_trous_franchis']} · côtés {x['les_cotes']}")
    print(f"VERDICT · {r['le_verdict']['ce_qui_reste_a_mesurer']}")


# ─────────────────────────────── la batterie ───────────────────────────────

def verifier() -> int:
    import copy
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

    v("★★★★ les largeurs sont l'échelle de 218, telle quelle", les_largeurs() == [3, 5, 7, 9])
    v("★★★ la majorité : deux sur trois, trois sur cinq, quatre sur sept, cinq sur neuf",
      [la_majorite(k) for k in (3, 5, 7, 9)] == [2, 3, 4, 5])
    R, C = [99, 198, 297], [71, 142, 213]
    bl = les_bandes_a_lire(R, C, 5, 9)
    v("★★★★ huit bandes de deux lignes consécutives, de part et d'autre des cinq publiées, sur le grand rectangle",
      len(bl) == 8 and bl[0]["les_lignes"] == [95, 96] and bl[1]["les_lignes"] == [102, 103]
      and (bl[0]["de"], bl[0]["a"]) == (71, 213) and bl[4]["les_lignes"] == [67, 68]
      and (bl[4]["de"], bl[4]["a"]) == (99, 297) and all(len(b["les_lignes"]) == 2 for b in bl), str(bl[:2]))
    pas = {l_: {s: float(l_) for s in range(3)} for l_ in range(10, 19)}
    v("★★★ une largeur garde ses lignes centrées, et elles seules",
      sorted(a_une_largeur(pas, 14, 5)) == [12, 13, 14, 15, 16] and sorted(a_une_largeur(pas, 14, 3)) == [13, 14, 15])
    pt = {1: {0: 1.0, 1: 1.0}, 2: {0: 2.0}, 3: {0: 3.0}}
    cf, tr = le_consensus_franchi(pt, 3, 0, 2, "le_maillage")
    v("★★★★ un trou de majorité est franchi par la règle de 225, et nommé",
      cf == {0: 2.0, 1: 0.0} and tr == [[1, 1]], str((cf, tr)))
    cf2, _t = le_consensus_franchi({1: {0: 1.0}, 2: {}, 3: {}}, 3, 0, 1, "les_lignes_presentes")
    v("★★★ une ligne seule présente franchit par les lignes présentes", cf2 == {0: 1.0}, str(cf2))
    cf3, _t = le_consensus_franchi({1: {}, 2: {}, 3: {}}, 3, 0, 1, "les_lignes_presentes")
    v("★★ sans aucune ligne, les lignes présentes ne franchissent pas", cf3 is None)

    # une largeur, sur des pas fabriqués : quatre côtés, une géométrie exacte, et du bruit par ligne
    g = np.random.default_rng(5)
    R2, C2 = [0, 40, 80], [0, 30, 60]
    geo = {("rangees", 0): 0.2, ("rangees", 80): -0.3, ("colonnes", 0): 0.1, ("colonnes", 60): 0.35}

    def _bande(cle, n_coutures, sd, centre):  # noqa: E306
        de = C2[0] if cle[0] == "rangees" else R2[0]
        return {l_: {s: geo[cle] + float(g.normal(0.0, sd)) for s in range(de, de + n_coutures)}
                for l_ in range(centre - 4, centre + 5)}
    pb = {("rangees", 0): _bande(("rangees", 0), 60, 1.0, 0), ("rangees", 40): {},
          ("rangees", 80): _bande(("rangees", 80), 60, 1.0, 80),
          ("colonnes", 0): _bande(("colonnes", 0), 80, 1.0, 0), ("colonnes", 30): {},
          ("colonnes", 60): _bande(("colonnes", 60), 80, 1.0, 60)}
    a = _sur(analyser, pb, R2, C2, "le_maillage", 3, 199)
    v("★★★ l'analyse est décidable sur des pas fabriqués", a.get("decidable"), str(a.get("raison")))
    v("★★★★ plus de lignes indépendantes, moins de bruit : la dispersion et le nul décroissent de 3 à 9",
      _ok(lambda: a["par_largeur"]["9"]["la_dispersion_du_pas_en_voxels"] < a["par_largeur"]["5"]["la_dispersion_du_pas_en_voxels"]
          < a["par_largeur"]["3"]["la_dispersion_du_pas_en_voxels"]
          and a["le_verdict"]["le_bruit_diminue_de_cinq_a_neuf"]))
    L_geo = 60 * geo[("rangees", 0)] + 80 * geo[("colonnes", 60)] - 60 * geo[("rangees", 80)] - 80 * geo[("colonnes", 0)]
    v("★★★★ la fermeture est la somme signée des quatre côtés, dans le sens de 224",
      _ok(lambda: abs(sum(c["la_somme_en_voxels"] * sg for c, sg in zip(a["par_largeur"]["9"]["les_cotes"],
                                                                         (1, 1, -1, -1)))
                      - a["par_largeur"]["9"]["la_fermeture_en_voxels"]) < 1e-3
          and abs(a["par_largeur"]["9"]["la_fermeture_en_voxels"] - L_geo) < 25.0))
    # ⚠ une erreur PARTAGÉE par toutes les lignes ne se réduit par aucune largeur : le piège de 208
    commun = {k: {l_: dict(s) for l_, s in x.items()} for k, x in pb.items()}
    ec = g.normal(0.0, 3.0, 80)
    for k in commun:
        for l_ in commun[k]:
            for s in commun[k][l_]:
                commun[k][l_][s] += float(ec[s])
    ac = _sur(analyser, commun, R2, C2, "le_maillage", 3, 199)
    v("★★★★ une erreur que toutes les lignes partagent ne se réduit pas avec la largeur",
      _ok(lambda: ac["par_largeur"]["9"]["la_dispersion_du_pas_en_voxels"] > 0.8 * ac["par_largeur"]["3"]["la_dispersion_du_pas_en_voxels"]))
    iss = {_ce_qui_reste(x, y) for x in (True, False) for y in (True, False)}
    v("★★★★ trois issues distinctes, et ne pas réduire le bruit prime",
      len(iss) == 3 and _ce_qui_reste(False, True) == _ce_qui_reste(False, False))

    # la mesure, sur une lecture fabriquée qui retombe : copiée des sources là où elles lisent
    p219, p223, p224, p225 = ce_que_219_a_rendu(), ce_que_223_a_rendu(), ce_que_224_a_rendu(), ce_que_225_a_rendu()
    src = _sur(les_sources_publiees, p219, p223, p224)

    def _fabrique(b):  # noqa: E306
        gg = np.random.default_rng(len(b["cle"]) + b["le_centre"])
        dom = le_domaine(b["le_sens"], b["les_lignes"], b["de"], b["a"])
        pas_ = {}
        for f in ("h", "v"):
            pas_[f] = {}
            for cle in sorted(dom[f]):
                x = next((S_["pas"][f][cle] for S_ in src.values() if f in S_["pas"]
                          and cle in S_["domaine"].get(f, ()) and cle in S_["pas"][f]), None)
                vu = any(f in S_["pas"] and cle in S_["domaine"].get(f, ()) for S_ in src.values())
                if x is not None:
                    pas_[f][cle] = x
                elif not vu:
                    pas_[f][cle] = round(float(gg.normal(0.0, 1.0)), 4)
        le_long_f, trav_f = (("h", "v") if b["le_sens"] == "rangees" else ("v", "h"))
        ll = {}
        for (r, c), x in pas_[le_long_f].items():
            a_, b_ = (r, c) if b["le_sens"] == "rangees" else (c, r)
            ll.setdefault(a_, {})[b_] = (x, 0.0, 16)
        tt = {}
        for (r, c), x in pas_[trav_f].items():
            tt.setdefault(r, {})[c] = (x, 0.0, 16)
        return {"decidable": True, "le_long": ll, "en_travers": tt, "les_lectures": {}}
    m = _sur(mesurer, None, p219, p223, p224, p225, _fabrique, 49)
    v("★★★★ une lecture fabriquée qui retombe passe la mesure entière, et cinq lignes retombent sur 225",
      m.get("decidable") and m["par_largeur"]["5"]["la_fermeture_en_voxels"] == p225["les_fermetures"][LA_BOUCLE]
      and m["la_reproduction"]["combien_de_coutures_relues"] > 0, str(m.get("raison")))
    v("★★★★ à neuf lignes, chaque côté vote avec ses neuf lignes, les lignes lues ici comprises",
      _ok(lambda: all(n_ == k_ for k_ in (3, 5, 7, 9)
                      for n_ in m["par_largeur"][str(k_)]["les_lignes_par_cote"].values())))
    v("★★★★ chacune des huit bandes nouvelles est contrôlée par une source publiée",
      _ok(lambda: {k.split("×")[0] for k in m["la_reproduction"]["par_croisement"]} == {b["cle"] for b in bl}))
    faux225 = copy.deepcopy(p225)
    faux225["les_fermetures"][LA_BOUCLE] = float(faux225["les_fermetures"][LA_BOUCLE]) + 1.0
    v("★★★★ à cinq lignes, un grand rectangle qui ne retombe pas sur 225 est refusé, par sa raison",
      "ne retombe pas sur `225`" in str(_sur(mesurer, None, p219, p223, p224, faux225, _fabrique, 49).get("raison")))

    def _decale(b):  # noqa: E306
        x = _fabrique(b)
        for r, s in x["en_travers"].items():
            for c in s:
                s[c] = (s[c][0] + 1.0, 0.0, 16)
        return x
    v("★★★★ une lecture qui ne retombe pas sur ce qui est publié est refusée, par sa raison",
      "ne retombe pas" in str(_sur(mesurer, None, p219, p223, p224, p225, _decale, 49).get("raison")))

    for e_ in echecs:
        print(f"  ÉCHEC {e_}")
    print(f"{Path(__file__).name}   "
          f"{'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--lire", type=Path, default=None)
    p.add_argument("--depuis", type=Path, default=None)
    p.add_argument("--json", type=Path, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if a.lire:
        p219, p224 = ce_que_219_a_rendu(), ce_que_224_a_rendu()
        if not (p219.get("decidable") and p224.get("decidable")):
            print(f"indécidable : {p219.get('raison') or p224.get('raison')}")
            return 1
        bandes = les_bandes_a_lire(p224["R"], p224["C"], len(p219["les_rangees"]), les_largeurs()[-1])
        deja = (json.loads(a.lire.read_text()).get("les_bandes") or {}) if a.lire.exists() else {}
        a.lire.parent.mkdir(parents=True, exist_ok=True)

        def ecrire(d):  # noqa: E306
            a.lire.write_text(json.dumps({"les_bandes": d}, ensure_ascii=False, indent=1))
            print(f"écrit : {a.lire} ({len(d)} bandes)", flush=True)
        lu = lire_les_bandes(bandes, deja, ecrire)
        if not lu.get("decidable"):
            print(f"indécidable : {lu.get('raison')}")
            return 1
        return 0
    r = mesurer(a.depuis)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=2))
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
