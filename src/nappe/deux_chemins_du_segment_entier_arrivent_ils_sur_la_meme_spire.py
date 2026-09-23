"""À l'échelle du segment entier, deux chemins de consensus à neuf lignes arrivent-ils sur la même spire ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LA MOINDRE LIGNE NOUVELLE NE SOIT LUE. La seule chose regardée avant
d'écrire est la PRÉSENCE : les trous que `225` publie sur les deux bandes centrales, jamais une valeur.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P77`. Sans main, `231` ne sépare plus du bruit les erreurs
d'une dizaine de voxels que portent ses cellules. Ce qu'une procédure sans main peut encore vérifier, c'est
le critère lui-même, le demi-feuillet ; et `228` ne l'a mesuré qu'à la moitié du segment, où le grand
rectangle ferme à −28,75 voxels à neuf lignes.

## Le rectangle, dérivé

Le recto qu'on lit s'arrête là où le consensus des bandes centrales s'arrête : `225` publie les trous de la
colonne 142 de `223`, sur toute la hauteur, et ceux de la rangée 198 de `219`, sur toute la largeur. Les
trous qui touchent un bord de la grille sont les bords du segment ; entre eux s'étend ce qui se lit, en
chunks. Les bandes du rectangle entier sont les plus extérieures dont les NEUF lignes, centrées par la
fonction de `219`, tombent toutes dans cette étendue — deux rangées, deux colonnes. ⚠⚠ C'est l'échelle
suivante de `224` : ses bandes étaient à mi-chemin du bord, celles-ci sont au bord de ce qui se lit. Le
code les dérive des trous publiés, et rien d'autre ; aucune n'est choisie.

## Ce qui se lit, et ce qui le contrôle

Les quatre bandes, neuf lignes chacune, par le lecteur de `224` : une bande de rangées entre les deux
colonnes du rectangle, une bande de colonnes entre ses deux rangées, bornes comprises. ⚠⚠⚠ CHAQUE BANDE
CROISE UNE BANDE PUBLIÉE : une rangée coupe les colonnes de `223`, une colonne les rangées de `219`. Partout
où deux lectures lisent la même couture, elles retombent à l'arrondi, sur les mêmes coutures, sinon refus ;
une bande qu'aucune couture publiée ne contrôle est refusée aussi.

## Les trous

Un trou de majorité est franchi par la règle que `225` a retenue, le maillage, et SEULEMENT jusqu'à la plus
longue longueur que `225` a essayée. ⚠⚠ Un trou plus long n'a été franchi par aucune règle éprouvée : il
laisse le rectangle ouvert à cette largeur, compté, jamais comblé.

## Ce qui se mesure, à chaque largeur de l'échelle de `218`

L'instrument de `228`, sur le rectangle entier : la fermeture, le bruit seul — les quatre côtés tirés
indépendamment par blocs de leurs propres pas centrés (`R4-L22`) —, et la dispersion du pas du consensus.

## Les issues, exclusives, jugées à neuf lignes

- un trou plus long que ceux que `225` a franchis : le segment entier reste ouvert ;
- la fermeture atteint le demi-feuillet : les deux chemins du segment entier arrivent sur deux spires ;
- elle reste dessous : ils arrivent sur la même.

⚠ Et à chaque largeur, la part des tirages du bruit seul sous le demi-feuillet : ce que le bruit seul aurait
laissé passer à cette échelle.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : une boucle, un segment, et une fermeture est un tirage ; sous le
demi-feuillet, elle dit que deux chemins s'accordent, pas lequel est sur la bonne spire.

Usage :
    uv run python src/nappe/deux_chemins_du_segment_entier_arrivent_ils_sur_la_meme_spire.py --verifier
    uv run python src/nappe/deux_chemins_du_segment_entier_arrivent_ils_sur_la_meme_spire.py --lire <lecture.json>
    uv run python src/nappe/deux_chemins_du_segment_entier_arrivent_ils_sur_la_meme_spire.py \\
        --depuis <lecture.json> --json docs/mesures/deux_chemins_du_segment_entier_arrivent_ils_sur_la_meme_spire.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))

from cinq_rangees_designent_elles_la_fautive import les_rangees_a_lire  # noqa: E402
from deux_chemins_arrivent_ils_sur_la_meme_spire import (_la_definition,  # noqa: E402
                                                          ce_que_223_a_rendu, les_cotes,
                                                          les_deux_chemins, lire_les_bandes,
                                                          relire_une_bande)
from lajustement_de_toutes_les_boucles_garde_t_il_la_spire import ce_que_225_a_rendu  # noqa: E402
from le_consensus_traverse_t_il_la_rangee import le_consensus  # noqa: E402
from le_vote_ramene_t_il_les_rangees_sur_le_feuillet import ce_que_219_a_rendu  # noqa: E402
from ou_est_lerreur_de_la_boucle_en_haut_a_gauche import (la_reproduction_croisee,  # noqa: E402
                                                          le_domaine, les_pas_dune_bande,
                                                          les_sources_publiees)
from quest_ce_qui_franchit_le_trou_de_majorite import ce_que_224_a_rendu, les_trous  # noqa: E402
from que_montrent_ces_deux_vues import DEMI_PAS_EN_VOXELS  # noqa: E402
from une_bande_plus_large_ferme_t_elle_le_grand_rectangle import (a_une_largeur,  # noqa: E402
                                                                   la_majorite, le_consensus_franchi,
                                                                   les_largeurs, une_largeur)

MESURES = RACINE / "docs" / "mesures"
CE_QUE_225_A_PUBLIE = MESURES / "quest_ce_qui_franchit_le_trou_de_majorite.json"
CE_QUE_228_A_PUBLIE = MESURES / "une_bande_plus_large_ferme_t_elle_le_grand_rectangle.json"

LA_QUESTION_DECLAREE = ("à l'échelle du segment entier, deux chemins de consensus à neuf lignes arrivent-ils sur "
                        "la même spire ?")
LA_MESURE_DECLAREE = ("à chaque largeur de l'échelle de `218`, la fermeture du rectangle dérivé des bords du "
                      "segment, le bruit seul de ses quatre côtés tirés par blocs, et la dispersion du pas")


# ─────────────────────────────── ce qui est publié ───────────────────────────────

def ce_que_225_a_publie(chemin: Path = CE_QUE_225_A_PUBLIE) -> dict:
    """Les trous que `225` publie par bande, et les longueurs de trou qu'elle a essayées."""
    if not Path(chemin).exists():
        return {"decidable": False, "raison": f"{Path(chemin).name} est absent"}
    try:
        d = json.loads(Path(chemin).read_text())
    except (ValueError, OSError) as e:
        return {"decidable": False, "raison": f"{Path(chemin).name} est illisible : {e}"}
    if not d.get("decidable") or not d.get("les_trous_par_bande") or not d.get("les_longueurs_observees"):
        return {"decidable": False, "raison": "`225` ne publie ni ses trous ni ses longueurs"}
    return {"decidable": True,
            "les_trous_par_bande": {k: [[int(a), int(n)] for a, n in v] for k, v in d["les_trous_par_bande"].items()},
            "les_longueurs_essayees": sorted(int(x) for x in d["les_longueurs_observees"])}


def ce_que_228_a_publie(chemin: Path = CE_QUE_228_A_PUBLIE) -> dict:
    """La moitié du segment, par largeur : la fermeture du grand rectangle et la part du bruit seul sous le
    demi-feuillet — relues, jamais recalculées."""
    if not Path(chemin).exists():
        return {"decidable": False, "raison": f"{Path(chemin).name} est absent"}
    try:
        d = json.loads(Path(chemin).read_text())
    except (ValueError, OSError) as e:
        return {"decidable": False, "raison": f"{Path(chemin).name} est illisible : {e}"}
    if not d.get("decidable") or not d.get("par_largeur"):
        return {"decidable": False, "raison": "`228` ne publie pas ses largeurs"}
    return {"decidable": True,
            "par_largeur": {k: {"la_fermeture_en_voxels": x["la_fermeture_en_voxels"],
                                "la_part_du_nul_sous_le_demi_pli": x["le_nul"]["la_part_sous_le_demi_pli"],
                                "la_fermeture_mediane_du_nul": x["le_nul"]["la_fermeture_mediane_en_valeur_absolue"]}
                            for k, x in d["par_largeur"].items()}}


# ─────────────────────────────── le rectangle, dérivé ───────────────────────────────

def letendue(trous, coutures: int) -> tuple[int, int]:
    """Les chunks entre les deux bords du segment, bornes comprises : `(premier, dernier)`.

    Un trou qui commence à la couture 0 est le bord de début, un trou qui finit à la dernière couture est le bord
    de fin ; ⚠⚠ un trou intérieur n'est pas un bord. La couture `s` joint les chunks `s` et `s + 1`.
    """
    premier, dernier = 0, int(coutures)
    for debut, n in trous:
        if int(debut) == 0:
            premier = int(n)
        if int(debut) + int(n) == int(coutures):
            dernier = int(debut)
    return premier, dernier


def les_bandes_du_bord(premier: int, dernier: int, combien: int) -> tuple[int, int]:
    """Les centres des deux bandes les plus extérieures dont TOUTES les lignes tombent dans `[premier, dernier]`."""
    dans = [c for c in range(int(premier), int(dernier) + 1)
            if min(les_rangees_a_lire(c, combien)) >= int(premier)
            and max(les_rangees_a_lire(c, combien)) <= int(dernier)]
    if not dans:
        return None
    return dans[0], dans[-1]


def le_rectangle(par225: dict, R, C, grille, combien: int) -> dict:
    """Le rectangle du segment entier, `(r0, r1, c0, c1)`, dérivé des trous des bandes centrales publiés par `225`."""
    gy, gx = int(grille[0]), int(grille[1])
    t_col = par225["les_trous_par_bande"].get(f"colonnes_{int(C[1])}")
    t_rang = par225["les_trous_par_bande"].get(f"rangees_{int(R[1])}")
    if t_col is None or t_rang is None:
        return {"decidable": False, "raison": "`225` ne publie pas les trous des deux bandes centrales"}
    er, ec = letendue(t_col, gy - 1), letendue(t_rang, gx - 1)
    br, bc = les_bandes_du_bord(*er, combien), les_bandes_du_bord(*ec, combien)
    if br is None or bc is None:
        return {"decidable": False, "raison": "l'étendue du segment ne tient pas une bande"}
    return {"decidable": True, "letendue_en_rangees": list(er), "letendue_en_colonnes": list(ec),
            "les_coins": [br[0], br[1], bc[0], bc[1]]}


def les_bandes_a_lire(coins, combien: int) -> list[dict]:
    """Les quatre bandes du rectangle : une rangée entre ses deux colonnes, une colonne entre ses deux rangées."""
    r0, r1, c0, c1 = [int(x) for x in coins]
    out = []
    for r in (r0, r1):
        out.append({"cle": f"rangees_{r}", "le_sens": "rangees", "le_centre": r,
                    "les_lignes": les_rangees_a_lire(r, combien), "de": c0, "a": c1})
    for c in (c0, c1):
        out.append({"cle": f"colonnes_{c}", "le_sens": "colonnes", "le_centre": c,
                    "les_lignes": les_rangees_a_lire(c, combien), "de": r0, "a": r1})
    return out


# ─────────────────────────────── la mesure, largeur par largeur ───────────────────────────────

def les_trous_des_cotes(pas_par_bande: dict, coins, k: int) -> list[dict]:
    """Les trous de majorité de chaque côté, à la largeur `k` — ceux que le franchissement aurait à passer."""
    out = []
    for sens, centre, de, a, _signe, nom in les_cotes(coins):
        cons = le_consensus(a_une_largeur(pas_par_bande[(sens, centre)], centre, k), la_majorite(k))
        for debut, n in les_trous(cons, de, a):
            out.append({"le_cote": nom, "le_debut": int(debut), "la_longueur": int(n)})
    return out


def une_largeur_du_segment(pas_par_bande: dict, coins, k: int, regle: str, plus_long: int, graine: int,
                           tirages: int, demi: float = DEMI_PAS_EN_VOXELS) -> dict:
    """À une largeur : ouvert si un trou dépasse ce que `225` a franchi, sinon l'instrument de `228`."""
    trous = les_trous_des_cotes(pas_par_bande, coins, k)
    trop = [t for t in trous if t["la_longueur"] > int(plus_long)]
    if trop:
        return {"decidable": True, "fermable": False, "la_largeur": int(k), "les_trous": trous,
                "les_trous_trop_longs": trop}
    r0, r1, c0, c1 = [int(x) for x in coins]
    # `une_largeur` de `228` ferme le rectangle `(R[0], R[2], C[0], C[2])` ; le milieu n'y entre pas.
    x = une_largeur(pas_par_bande, [r0, r1, r1], [c0, c1, c1], k, regle, graine, tirages, demi)
    if not x.get("decidable"):
        return x
    return {**x, "fermable": True, "les_trous": trous}


def _ce_qui_reste(ouvert: bool, ferme: bool) -> str:
    """Les trois issues, EXCLUSIVES — et un trou non franchi prime."""
    if ouvert:
        return "À NEUF LIGNES, UN TROU PLUS LONG QUE CEUX QUE `225` A FRANCHIS LAISSE LE SEGMENT ENTIER OUVERT"
    if not ferme:
        return "À NEUF LIGNES, LES DEUX CHEMINS DU SEGMENT ENTIER ARRIVENT À UN DEMI-FEUILLET L'UN DE L'AUTRE"
    return "À NEUF LIGNES, LES DEUX CHEMINS DU SEGMENT ENTIER ARRIVENT SUR LA MÊME SPIRE"


def analyser(pas_par_bande: dict, coins, regle: str, plus_long: int, graine: int, tirages: int,
             demi: float = DEMI_PAS_EN_VOXELS) -> dict:
    """Toutes les largeurs de l'échelle, et le verdict à la plus large — pur."""
    par = {}
    for k in les_largeurs():
        x = une_largeur_du_segment(pas_par_bande, coins, k, regle, plus_long, graine, tirages, demi)
        if not x.get("decidable"):
            return {"decidable": False, "raison": x.get("raison")}
        par[str(k)] = x
    k1 = les_largeurs()[-1]
    x9 = par[str(k1)]
    ouvert = not x9["fermable"]
    ferme = (not ouvert) and bool(x9["sous_le_demi_pli"])
    chemins = None
    if not ouvert:
        cons = {}
        for sens, centre, de, a, _s, _n in les_cotes(coins):
            c_, _t = le_consensus_franchi(a_une_largeur(pas_par_bande[(sens, centre)], centre, k1), k1, de, a,
                                          regle)
            cons[(sens, int(centre))] = c_
        chemins = les_deux_chemins(cons, [int(x) for x in coins])
    return {"decidable": True, "la_regle_appliquee": regle, "les_largeurs": les_largeurs(), "par_largeur": par,
            "les_deux_chemins": chemins,
            "le_verdict": {"la_largeur_jugee": int(k1), "le_segment_entier_reste_ouvert": bool(ouvert),
                           "le_segment_entier_se_ferme": bool(ferme),
                           "ce_qui_reste_a_mesurer": _ce_qui_reste(ouvert, ferme)}}


def les_pas_des_bandes(relues: dict, bandes) -> dict:
    """`{(sens, centre): {ligne: {couture: pas}}}` : les pas le long de chaque bande lue."""
    return {(b["le_sens"], int(b["le_centre"])): {int(l_): {int(s): float(x[0]) for s, x in d.items()}
                                                  for l_, d in relues[b["cle"]]["le_long"].items()}
            for b in bandes}


def mesurer(depuis: Path | None = None, par219: dict | None = None, par223: dict | None = None,
            par224: dict | None = None, par225: dict | None = None, pub225: dict | None = None,
            pub228: dict | None = None, lire=None, tirages: int | None = None) -> dict:
    """La lecture des quatre bandes puis l'analyse — ou l'analyse seule, rejouée."""
    par219 = ce_que_219_a_rendu() if par219 is None else par219
    par223 = ce_que_223_a_rendu() if par223 is None else par223
    par224 = ce_que_224_a_rendu() if par224 is None else par224
    par225 = ce_que_225_a_rendu() if par225 is None else par225
    pub225 = ce_que_225_a_publie() if pub225 is None else pub225
    pub228 = ce_que_228_a_publie() if pub228 is None else pub228
    base = {"la_question_declaree": LA_QUESTION_DECLAREE, "la_mesure_declaree": LA_MESURE_DECLAREE}
    for nom, par in (("219", par219), ("223", par223), ("224", par224), ("225", par225), ("225 publiée", pub225),
                     ("228", pub228)):
        if not par.get("decidable"):
            return {**base, "decidable": False, "raison": f"`{nom}` : {par.get('raison')}"}
    k1 = les_largeurs()[-1]
    rect = le_rectangle(pub225, par224["R"], par224["C"], par224["la_grille"], k1)
    if not rect.get("decidable"):
        return {**base, "decidable": False, "raison": rect.get("raison")}
    coins = rect["les_coins"]
    bandes = les_bandes_a_lire(coins, k1)
    plus_long = max(pub225["les_longueurs_essayees"])
    g = par224["graine"]
    t_ = par224["tirages"] if tirages is None else int(tirages)
    if depuis is not None:
        lu = {"decidable": True, "les_bandes": json.loads(Path(depuis).read_text()).get("les_bandes") or {}}
    else:
        lu = lire_les_bandes(bandes, lire=lire)
    base.update({"graine": int(g), "tirages": t_, "les_largeurs_de_218": les_largeurs(),
                 "la_regle_de_225": par225["la_regle"], "le_plus_long_trou_franchi_par_225": int(plus_long),
                 "le_rectangle": rect, "les_bandes_declarees": bandes, "la_moitie_du_segment": pub228["par_largeur"],
                 "les_bandes": lu.get("les_bandes") or {}})
    if not lu.get("decidable"):
        return {**base, "decidable": False, "raison": lu.get("raison")}
    pub = lu["les_bandes"]
    if (sorted(pub) != sorted(b["cle"] for b in bandes)
            or any(_la_definition(pub[b["cle"]]) != _la_definition(b) for b in bandes)):
        return {**base, "decidable": False, "raison": "la lecture n'est pas celle des bandes dérivées"}
    relues = {k: relire_une_bande(x) for k, x in pub.items()}
    nouvelles = {b["cle"]: {"domaine": le_domaine(b["le_sens"], b["les_lignes"], b["de"], b["a"]),
                            "pas": les_pas_dune_bande(relues[b["cle"]])} for b in bandes}
    rep = la_reproduction_croisee(nouvelles, les_sources_publiees(par219, par223, par224))
    if not rep.get("decidable"):
        return {**base, "decidable": False, "raison": rep.get("raison"), "la_reproduction": rep}
    a = analyser(les_pas_des_bandes(relues, bandes), coins, par225["la_regle"], plus_long, g, t_)
    if not a.get("decidable"):
        return {**base, "decidable": False, "raison": a.get("raison"), "la_reproduction": rep}
    return {**base, "la_reproduction": rep, **a}


def afficher(r: dict) -> None:
    if not r.get("decidable"):
        print(f"indécidable : {r.get('raison')}")
        return
    rp = r["la_reproduction"]
    print(f"rectangle : {r['le_rectangle']}")
    print(f"reproduction : {rp['combien_de_coutures_relues']} coutures {rp['par_croisement']}, écart "
          f"{rp['lecart_le_plus_grand']}")
    for k, x in r["par_largeur"].items():
        if not x["fermable"]:
            print(f"  {k} lignes · OUVERT · trous trop longs {x['les_trous_trop_longs']}")
            continue
        print(f"  {k} lignes · L {x['la_fermeture_en_voxels']} · σ {x['la_dispersion_du_pas_en_voxels']} · nul "
              f"{x['le_nul']} · trous {x['les_trous']} · côtés {x['les_cotes']} · lignes {x['les_lignes_par_cote']}")
    print(f"VERDICT · {r['le_verdict']['ce_qui_reste_a_mesurer']}")


# ─────────────────────────────── la batterie ───────────────────────────────

def verifier() -> int:
    import numpy as np
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

    # l'étendue : les bords sont les trous qui touchent un bord, et eux seuls
    v("★★★★ l'étendue en rangées : de la fin du trou du haut au début du trou du bas",
      letendue([[0, 7], [392, 3]], 395) == (7, 392), str(letendue([[0, 7], [392, 3]], 395)))
    v("★★★★ l'étendue en colonnes : un trou intérieur n'est pas un bord",
      letendue([[0, 17], [215, 1], [272, 12]], 284) == (17, 272))
    v("★★★ sans trou au bord, l'étendue est la grille entière", letendue([[40, 3]], 100) == (0, 100))
    v("★★★★ les bandes du bord : toutes leurs neuf lignes dans l'étendue, les plus extérieures",
      les_bandes_du_bord(7, 392, 9) == (11, 388) and les_bandes_du_bord(17, 272, 9) == (21, 268)
      and min(les_rangees_a_lire(11, 9)) == 7 and max(les_rangees_a_lire(388, 9)) == 392,
      str(les_bandes_du_bord(7, 392, 9)))
    v("★★ une étendue trop étroite ne tient pas de bande", les_bandes_du_bord(3, 8, 9) is None)
    bl = les_bandes_a_lire([11, 388, 21, 268], 9)
    v("★★★★ quatre bandes de neuf lignes : les rangées entre les colonnes, les colonnes entre les rangées",
      [b["cle"] for b in bl] == ["rangees_11", "rangees_388", "colonnes_21", "colonnes_268"]
      and all(len(b["les_lignes"]) == 9 for b in bl)
      and (bl[0]["de"], bl[0]["a"]) == (21, 268) and (bl[2]["de"], bl[2]["a"]) == (11, 388)
      and bl[2]["les_lignes"] == list(range(17, 26)), str(bl[:1]))

    # les trous des côtés, et la garde de 225
    R0 = [0, 30, 0, 20]
    base = {("rangees", 0): {l_: {s: 0.0 for s in range(0, 20)} for l_ in range(-4, 5)},
            ("rangees", 30): {l_: {s: 0.0 for s in range(0, 20)} for l_ in range(26, 35)},
            ("colonnes", 0): {l_: {s: 0.0 for s in range(0, 30)} for l_ in range(-4, 5)},
            ("colonnes", 20): {l_: {s: 0.0 for s in range(0, 30)} for l_ in range(16, 25)}}

    def _troue(n, cote=("colonnes", 20), debut=5, lignes=9):  # noqa: E306
        x = {k: {l_: dict(s) for l_, s in b.items()} for k, b in base.items()}
        for l_ in sorted(x[cote])[:lignes]:
            for s in range(debut, debut + n):
                x[cote][l_].pop(s, None)
        return x
    t9 = les_trous_des_cotes(_troue(4), R0, 9)
    v("★★★★ un trou de majorité est nommé par son côté, son début et sa longueur",
      t9 == [{"le_cote": "droite", "le_debut": 5, "la_longueur": 4}], str(t9))
    t9b = les_trous_des_cotes(_troue(4, lignes=4), R0, 9)
    v("★★★ cinq lignes sur neuf votent encore : pas de trou à neuf lignes", t9b == [], str(t9b))
    t3 = les_trous_des_cotes(_troue(4, lignes=4), R0, 3)
    v("★★★ à trois lignes, les trois du centre décident : deux présentes sur trois votent encore", t3 == [], str(t3))
    x17 = _sur(une_largeur_du_segment, _troue(17), R0, 9, "le_maillage", 17, 3, 99)
    x18 = _sur(une_largeur_du_segment, _troue(18), R0, 9, "le_maillage", 17, 3, 99)
    v("★★★★ un trou de la plus longue longueur que 225 a franchie se franchit",
      x17.get("decidable") and x17.get("fermable") and x17["les_trous"][0]["la_longueur"] == 17, str(x17.get("raison")))
    v("★★★★ un trou plus long laisse le rectangle ouvert, compté, jamais comblé",
      x18.get("decidable") and x18.get("fermable") is False and x18["les_trous_trop_longs"][0]["la_longueur"] == 18
      and "la_fermeture_en_voxels" not in x18)

    # une largeur, sur des pas fabriqués : une géométrie exacte par côté, du bruit indépendant par ligne
    g = np.random.default_rng(7)
    coins = [0, 80, 0, 60]
    geo = {("rangees", 0): 0.2, ("rangees", 80): -0.3, ("colonnes", 0): 0.1, ("colonnes", 60): 0.35}

    def _bande(cle, n, sd):  # noqa: E306
        return {l_: {s: geo[cle] + float(g.normal(0.0, sd)) for s in range(0, n)}
                for l_ in les_rangees_a_lire(cle[1], 9)}
    pb = {("rangees", 0): _bande(("rangees", 0), 60, 1.0), ("rangees", 80): _bande(("rangees", 80), 60, 1.0),
          ("colonnes", 0): _bande(("colonnes", 0), 80, 1.0), ("colonnes", 60): _bande(("colonnes", 60), 80, 1.0)}
    a = _sur(analyser, pb, coins, "le_maillage", 17, 3, 199)
    v("★★★ l'analyse est décidable sur des pas fabriqués", a.get("decidable"), str(a.get("raison")))
    L_geo = 60 * geo[("rangees", 0)] + 80 * geo[("colonnes", 60)] - 60 * geo[("rangees", 80)] - 80 * geo[("colonnes", 0)]
    v("★★★★ la fermeture est la somme signée des quatre côtés, dans le sens de 224",
      _ok(lambda: abs(sum(c["la_somme_en_voxels"] * sg for c, sg in zip(a["par_largeur"]["9"]["les_cotes"],
                                                                         (1, 1, -1, -1)))
                      - a["par_largeur"]["9"]["la_fermeture_en_voxels"]) < 1e-3
          and abs(a["par_largeur"]["9"]["la_fermeture_en_voxels"] - L_geo) < 25.0))
    v("★★★★ à neuf lignes, chaque côté vote avec ses neuf lignes",
      _ok(lambda: all(n_ == k_ for k_ in (3, 5, 7, 9) for n_ in a["par_largeur"][str(k_)]["les_lignes_par_cote"].values())))
    v("★★★★ les deux chemins partent du même coin et leur écart d'arrivée est la fermeture à neuf lignes",
      _ok(lambda: abs(a["les_deux_chemins"]["par_la_rangee_dabord"][-1] - a["les_deux_chemins"]["par_la_colonne_dabord"][-1]
                      - a["par_largeur"]["9"]["la_fermeture_en_voxels"]) < 1e-2
          and a["les_deux_chemins"]["par_la_rangee_dabord"][0] == 0.0
          and len(a["les_deux_chemins"]["par_la_rangee_dabord"]) == 60 + 80 + 1))
    v("★★★★ le verdict est jugé à neuf lignes, la plus large de l'échelle",
      _ok(lambda: a["le_verdict"]["la_largeur_jugee"] == 9
          and a["le_verdict"]["le_segment_entier_se_ferme"] == a["par_largeur"]["9"]["sous_le_demi_pli"]))
    petit = _sur(analyser, pb, coins, "le_maillage", 17, 3, 199, 0.5)
    v("★★★★ sous un demi-feuillet minuscule, les deux chemins arrivent à un demi-feuillet l'un de l'autre",
      _ok(lambda: petit["le_verdict"]["le_segment_entier_se_ferme"] is False
          and "UN DEMI-FEUILLET" in petit["le_verdict"]["ce_qui_reste_a_mesurer"]))
    pt = {k: {l_: dict(s) for l_, s in b.items()} for k, b in pb.items()}
    for l_ in pt[("colonnes", 60)]:
        for s in range(10, 30):
            pt[("colonnes", 60)][l_].pop(s, None)
    at = _sur(analyser, pt, coins, "le_maillage", 17, 3, 199)
    v("★★★★ un trou trop long à neuf lignes laisse le segment entier ouvert, et cette issue prime",
      _ok(lambda: at["le_verdict"]["le_segment_entier_reste_ouvert"] and at["les_deux_chemins"] is None
          and not at["le_verdict"]["le_segment_entier_se_ferme"]))
    iss = {_ce_qui_reste(x, y) for x in (True, False) for y in (True, False)}
    v("★★★★ trois issues distinctes, et un trou non franchi prime",
      len(iss) == 3 and _ce_qui_reste(True, True) == _ce_qui_reste(True, False))

    # la mesure, sur des publications réelles et une lecture fabriquée qui retombe
    p219, p223, p224, p225 = ce_que_219_a_rendu(), ce_que_223_a_rendu(), ce_que_224_a_rendu(), ce_que_225_a_rendu()
    q225, q228 = ce_que_225_a_publie(), ce_que_228_a_publie()
    rect = _sur(le_rectangle, q225, p224["R"], p224["C"], p224["la_grille"], 9)
    v("★★★★ sur les trous que 225 publie, le rectangle du segment entier est dérivé : rangées 11 et 388, colonnes 21 "
      "et 268", rect.get("les_coins") == [11, 388, 21, 268]
      and rect.get("letendue_en_rangees") == [7, 392] and rect.get("letendue_en_colonnes") == [17, 272], str(rect))
    v("★★★ la plus longue longueur que 225 a franchie est 17 coutures",
      max(q225.get("les_longueurs_essayees") or [0]) == 17)
    src = _sur(les_sources_publiees, p219, p223, p224)
    bl_reelles = les_bandes_a_lire(rect.get("les_coins") or [11, 388, 21, 268], 9)

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
    m = _sur(mesurer, None, p219, p223, p224, p225, q225, q228, _fabrique, 49)
    v("★★★★ une lecture fabriquée qui retombe passe la mesure entière", m.get("decidable"), str(m.get("raison")))
    v("★★★★ chacune des quatre bandes est contrôlée par une bande publiée : les rangées par 223, les colonnes par 219",
      _ok(lambda: {k.split("×")[0]: k.split("×")[1] for k in m["la_reproduction"]["par_croisement"]}
          == {"rangees_11": "223", "rangees_388": "223", "colonnes_21": "219", "colonnes_268": "219"}),
      str(m.get("la_reproduction")))
    v("★★★★ dans la mesure, à neuf lignes, chaque côté vote avec les neuf lignes lues le long de sa bande",
      _ok(lambda: m["par_largeur"]["9"]["fermable"]
          and set(m["par_largeur"]["9"]["les_lignes_par_cote"].values()) == {9}), str(m.get("par_largeur", {}).get("9")))
    v("★★★★ la mesure lit les bandes dérivées, et la règle de 225",
      _ok(lambda: m["les_bandes_declarees"] == bl_reelles and m["la_regle_de_225"] == p225["la_regle"]
          and m["la_regle_appliquee"] == p225["la_regle"]
          and m["le_plus_long_trou_franchi_par_225"] == 17))
    v("★★★ la moitié du segment est relue de 228, telle que publiée",
      _ok(lambda: all(m["la_moitie_du_segment"][k]["la_fermeture_en_voxels"] == x["la_fermeture_en_voxels"]
                      and m["la_moitie_du_segment"][k]["la_part_du_nul_sous_le_demi_pli"]
                      == x["le_nul"]["la_part_sous_le_demi_pli"]
                      for k, x in json.loads(CE_QUE_228_A_PUBLIE.read_text())["par_largeur"].items())))

    def _decale(b):  # noqa: E306
        x = _fabrique(b)
        for r, s in x["en_travers"].items():
            for c in s:
                s[c] = (s[c][0] + 1.0, 0.0, 16)
        return x
    v("★★★★ une lecture qui ne retombe pas sur ce qui est publié est refusée, par sa raison",
      "ne retombe pas" in str(_sur(mesurer, None, p219, p223, p224, p225, q225, q228, _decale, 49).get("raison")))
    autre = {**q225, "les_trous_par_bande": {**q225["les_trous_par_bande"], "colonnes_142": [[0, 9], [392, 3]]}}
    ma = _sur(mesurer, None, p219, p223, p224, p225, autre, q228, _fabrique, 49)
    v("★★★ d'autres bords publiés dérivent d'autres bandes", _ok(lambda: ma["le_rectangle"]["les_coins"] == [13, 388, 21, 268]),
      str(ma.get("le_rectangle")))
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        dep = Path(tmp) / "lecture.json"
        dep.write_text(json.dumps({"les_bandes": {"rangees_11": {}}}))
        md = _sur(mesurer, dep, p219, p223, p224, p225, q225, q228, None, 49)
    v("★★★★ une lecture qui n'est pas celle des bandes dérivées est refusée",
      "pas celle des bandes dérivées" in str(md.get("raison")), str(md.get("raison")))
    with tempfile.TemporaryDirectory() as tmp:
        dep = Path(tmp) / "lecture.json"
        faux = {b["cle"]: {**b, "le_long": {}, "en_travers": {}, "les_lectures": {}} for b in bl_reelles}
        une = next(k for k in sorted(faux) if k.startswith("colonnes"))
        faux[une]["les_lignes"] = [x - 2 for x in faux[une]["les_lignes"]]
        dep.write_text(json.dumps({"les_bandes": faux}))
        mf = _sur(mesurer, dep, p219, p223, p224, p225, q225, q228, None, 49)
    v("★★★★ une bande lue sur d'autres lignes que celles dérivées est refusée",
      "pas celle des bandes dérivées" in str(mf.get("raison")), str(mf.get("raison")))

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
        p224, q225 = ce_que_224_a_rendu(), ce_que_225_a_publie()
        if not (p224.get("decidable") and q225.get("decidable")):
            print(f"indécidable : {p224.get('raison') or q225.get('raison')}")
            return 1
        rect = le_rectangle(q225, p224["R"], p224["C"], p224["la_grille"], les_largeurs()[-1])
        if not rect.get("decidable"):
            print(f"indécidable : {rect.get('raison')}")
            return 1
        bandes = les_bandes_a_lire(rect["les_coins"], les_largeurs()[-1])
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
