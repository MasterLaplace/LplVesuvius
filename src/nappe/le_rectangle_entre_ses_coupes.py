"""Entre deux coupes de `224`, le profil du plus grand rectangle reste-t-il sous le demi-feuillet ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LA MOINDRE LIGNE NOUVELLE NE SOIT LUE. Ce qui était vu avant d'écrire : ce que `238`
publie, et sa figure.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P84`. `238` a coupé le plus grand rectangle de `233` aux rangées 99, 198 et
297 : son cumul y vaut 14,1485, 9,3985 et −14,7265, loin du demi-feuillet. Mais ses tranches font de 73 à 99 rangées, et
entre deux coupes le profil n'est pas vu ; la traversée du demi-feuillet par l'aile de droite, dans `235`, allait de la
coupe 163 à la coupe 203.

## Les coupes de plus, dérivées

LA PORTÉE est la plus longue traversée que `235` publie : de la première à la dernière coupe où le cumul de l'aile de
droite atteint le demi-feuillet. Chaque tranche de `238` est partagée en le moins de parts égales possible dont aucune ne
dépasse la portée ; les rangées de partage sont les coupes de plus, gardées là où leur bande de neuf lignes tient d'une
colonne du rectangle à l'autre. ⚠⚠ Rien n'est choisi, et la garantie est exacte : une traversée qui dure au moins la
portée, d'un seul tenant, touche forcément une coupe — sauf là où une coupe de plus a dû être retirée, et c'est dit.

## Ce qui se lit, et ce qui le contrôle

Les coupes de plus seules, par le lecteur de `224`. ⚠⚠ Les quatre bandes du rectangle et les coupes de `238` ne sont pas
relues : leurs pas sont ceux que `233` et `238` publient. ⚠⚠⚠ Partout où une coupe neuve croise une bande publiée — `219`,
`223`, `224`, `232`, `233`, `234` —, les pas relus retombent à l'arrondi, sinon refus ; une coupe qui ne croise aucune bande
publiée est refusée. ⚠⚠ Les chunks que la lecture compte absents du dépôt sont ceux que la présence dit absents.

## Ce qui se mesure

L'instrument de `228` sur chaque tranche fine, d'une coupe à la suivante. ⚠⚠⚠ DEUX EMBOÎTEMENTS : les tranches fines
somment à la fermeture que `233` publie pour le rectangle, et celles qui tombent entre deux coupes de `238` à la tranche que
`238` publie entre elles ; là où aucune n'a de trou sur une colonne, à l'arrondi près, sinon refus. LE PROFIL : la
fermeture cumulée depuis la rangée 26, coupe après coupe.

## Les issues, exclusives, jugées à neuf lignes

- aucune coupe de plus ne tient : rien de plus n'est vu, et rien n'est lu ;
- une tranche fine garde un trou plus long que ceux que `225` a franchis : elle reste ouverte ;
- le profil atteint le demi-feuillet à une coupe : le rectangle ne ferme qu'au bout ;
- il reste dessous à chaque coupe : aucune traversée d'au moins la portée ne lui échappe.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : une traversée plus courte que la portée, entre deux coupes.

Usage :
    uv run python src/nappe/le_rectangle_entre_ses_coupes.py --verifier
    uv run python src/nappe/le_rectangle_entre_ses_coupes.py --lire <lecture.json>
    uv run python src/nappe/le_rectangle_entre_ses_coupes.py --depuis <lecture.json> \\
        --json docs/mesures/le_rectangle_entre_ses_coupes.json
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

from deux_chemins_arrivent_ils_sur_la_meme_spire import (_la_definition,  # noqa: E402
                                                          ce_que_223_a_rendu, lire_les_bandes,
                                                          relire_une_bande)
from deux_chemins_du_segment_entier_arrivent_ils_sur_la_meme_spire import (analyser,  # noqa: E402
                                                                            ce_que_225_a_publie,
                                                                            les_pas_des_bandes)
from lajustement_de_toutes_les_boucles_garde_t_il_la_spire import ce_que_225_a_rendu  # noqa: E402
from le_rectangle_tient_il_sur_son_profil import (la_fermeture_de_233,  # noqa: E402
                                                  le_verdict_du_rectangle, les_bandes_des_coupes_du_rectangle,
                                                  les_coupes_du_rectangle)
from le_segment_au_dela_du_rectangle_se_relie_t_il import ce_que_233_a_publie  # noqa: E402
from le_vote_ramene_t_il_les_rangees_sur_le_feuillet import ce_que_219_a_rendu  # noqa: E402
from letroite_reste_t_elle_sans_ecart import ce_que_235_a_publie, les_franchissements  # noqa: E402
from ou_est_lerreur_de_la_boucle_en_haut_a_gauche import (la_reproduction_croisee,  # noqa: E402
                                                          le_domaine, les_pas_dune_bande)
from ou_laile_de_droite_se_separe import (ce_que_234_a_publie, le_profil,  # noqa: E402
                                          lemboitement, les_sources_de_235, les_sous_boucles)
from ou_sarrete_le_segment import (ABSENT, ce_que_232_a_publie,  # noqa: E402
                                   la_grille_de_presence, la_presence_retombe, les_absents_dune_ligne)
from que_montrent_ces_deux_vues import DEMI_PAS_EN_VOXELS  # noqa: E402
from quest_ce_qui_franchit_le_trou_de_majorite import ce_que_224_a_rendu  # noqa: E402
from une_bande_plus_large_ferme_t_elle_le_grand_rectangle import les_largeurs  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
CE_QUE_238_A_PUBLIE = MESURES / "le_rectangle_tient_il_sur_son_profil.json"

LA_QUESTION_DECLAREE = ("entre deux coupes de `224`, le profil du plus grand rectangle reste-t-il sous le "
                        "demi-feuillet ?")
LA_MESURE_DECLAREE = ("chaque tranche de `238` partagée en parts égales d'au plus la plus longue traversée que `235` "
                      "publie, les tranches fines, et la fermeture cumulée coupe après coupe")


def ce_que_238_a_publie(chemin: Path = CE_QUE_238_A_PUBLIE) -> dict:
    """Les coupes du rectangle, relues, et ses tranches, telles que `238` les publie."""
    try:
        d = json.loads(Path(chemin).read_text())
    except (ValueError, OSError) as e:
        return {"decidable": False, "raison": f"{Path(chemin).name} est absent ou illisible : {e}"}
    if not d.get("decidable") or not d.get("par_tranche") or not d.get("les_bandes") \
            or not d.get("les_bandes_declarees") or not d.get("les_coupes"):
        return {"decidable": False, "raison": "`238` ne publie pas ses coupes ou ses tranches"}
    return {"decidable": True, "coupes": [int(x) for x in d["les_coupes"]], "bandes": d["les_bandes_declarees"],
            "publiees": d["les_bandes"], "relues": {k: relire_une_bande(x) for k, x in d["les_bandes"].items()},
            "par_tranche": d["par_tranche"]}


# ─────────────────────────────── la portée et les coupes de plus ───────────────────────────────

def la_portee(profil235, demi: float) -> int | None:
    """La plus longue traversée que `235` publie : de la première à la dernière coupe où le cumul atteint le
    demi-feuillet. Aucune si le cumul ne l'atteint pas, ou ne l'atteint qu'à une coupe."""
    fr = [int(p["la_coupe"]) for p in les_franchissements(profil235, demi)]
    if len(fr) < 2:
        return None
    return fr[-1] - fr[0]


def les_rangees_de_partage(coupes, portee: int) -> list[int]:
    """Chaque intervalle entre deux coupes, partagé en le moins de parts égales qui ne dépassent pas la portée."""
    out = []
    for a, b in zip(coupes[:-1], coupes[1:]):
        n = -(-(int(b) - int(a)) // int(portee))
        out += [int(a) + (i * (int(b) - int(a))) // n for i in range(1, n)]
    return out


def les_ecarts_au_dela(coupes, portee: int) -> list[list[int]]:
    """Les intervalles entre deux coupes gardées qui dépassent la portée : là, la garantie ne tient pas."""
    return [[int(a), int(b)] for a, b in zip(coupes[:-1], coupes[1:]) if int(b) - int(a) > int(portee)]


# ─────────────────────────────── la mesure ───────────────────────────────

def mesurer(depuis: Path | None = None, par219: dict | None = None, par223: dict | None = None,
            par224: dict | None = None, par225: dict | None = None, pub225: dict | None = None,
            par232: dict | None = None, par233: dict | None = None, fer233: dict | None = None,
            par234: dict | None = None, par235: dict | None = None, par238: dict | None = None, lire=None,
            tirages: int | None = None, demi: float | None = None) -> dict:
    """Les coupes de plus, leur lecture, puis les tranches fines et le profil — ou rejoués."""
    par219 = ce_que_219_a_rendu() if par219 is None else par219
    par223 = ce_que_223_a_rendu() if par223 is None else par223
    par224 = ce_que_224_a_rendu() if par224 is None else par224
    par225 = ce_que_225_a_rendu() if par225 is None else par225
    pub225 = ce_que_225_a_publie() if pub225 is None else pub225
    par232 = ce_que_232_a_publie() if par232 is None else par232
    par233 = ce_que_233_a_publie() if par233 is None else par233
    fer233 = la_fermeture_de_233() if fer233 is None else fer233
    par234 = ce_que_234_a_publie() if par234 is None else par234
    par235 = ce_que_235_a_publie() if par235 is None else par235
    par238 = ce_que_238_a_publie() if par238 is None else par238
    base = {"la_question_declaree": LA_QUESTION_DECLAREE, "la_mesure_declaree": LA_MESURE_DECLAREE}
    for nom, par in (("219", par219), ("223", par223), ("224", par224), ("225", par225), ("225 publiée", pub225),
                     ("232", par232), ("233", par233), ("233 analyse", fer233), ("234", par234), ("235", par235),
                     ("238", par238)):
        if not par.get("decidable"):
            return {**base, "decidable": False, "raison": f"`{nom}` : {par.get('raison')}"}
    demi = float(DEMI_PAS_EN_VOXELS) if demi is None else float(demi)
    presence = par233["presence"]
    if [int(x) for x in presence["la_grille"]] != [int(x) for x in par224["la_grille"]]:
        return {**base, "decidable": False, "raison": "la grille de `233` n'est pas celle que les bandes parcourent"}
    A = la_grille_de_presence(presence)
    for nom, par in (("233", par233), ("238", par238)):
        c_ = la_presence_retombe(A, par["bandes"], par["publiees"])
        base[f"la_presence_contre_{nom}"] = c_
        if not c_.get("decidable"):
            return {**base, "decidable": False, "raison": c_.get("raison")}
    portee = la_portee(par235.get("profil") or [], demi)
    if portee is None:
        return {**base, "decidable": False, "raison": "`235` ne publie aucune traversée : il n'y a pas de portée"}
    k1 = les_largeurs()[-1]
    coins = [int(x) for x in par233["coins"]]
    c238 = par238["coupes"]
    partage = les_rangees_de_partage(c238, portee)
    coupes = les_coupes_du_rectangle(A, coins, c238[1:-1] + partage, k1)
    nouvelles_c = [c for c in coupes if c not in c238]
    base.update({"le_rectangle": coins, "la_portee": int(portee), "les_coupes_de_238": c238,
                 "les_rangees_de_partage": partage,
                 "les_coupes": coupes, "les_coupes_de_plus": nouvelles_c,
                 "les_ecarts_au_dela_de_la_portee": les_ecarts_au_dela(coupes, portee)})
    if not nouvelles_c:
        return {**base, "decidable": True, "le_verdict": le_verdict_du_rectangle(1, [], demi, k1)}
    bandes = les_bandes_des_coupes_du_rectangle([coupes[0]] + nouvelles_c + [coupes[-1]], coins[2], coins[3], k1)
    plus_long = max(pub225["les_longueurs_essayees"])
    g = par224["graine"]
    t_ = par224["tirages"] if tirages is None else int(tirages)
    if depuis is not None:
        lu = {"decidable": True, "les_bandes": json.loads(Path(depuis).read_text()).get("les_bandes") or {}}
    else:
        lu = lire_les_bandes(bandes, lire=lire)
    base.update({"graine": int(g), "tirages": t_, "la_regle_de_225": par225["la_regle"],
                 "le_plus_long_trou_franchi_par_225": int(plus_long), "les_bandes_declarees": bandes,
                 "les_bandes": lu.get("les_bandes") or {}})
    if not lu.get("decidable"):
        return {**base, "decidable": False, "raison": lu.get("raison")}
    pub = lu["les_bandes"]
    if (sorted(pub) != sorted(b["cle"] for b in bandes)
            or any(_la_definition(pub[b["cle"]]) != _la_definition(b) for b in bandes)):
        return {**base, "decidable": False, "raison": "la lecture n'est pas celle des coupes dérivées"}
    cn = la_presence_retombe(A, bandes, pub)
    base["la_presence_contre_la_lecture"] = cn
    if not cn.get("decidable"):
        return {**base, "decidable": False, "raison": cn.get("raison")}
    relues = {k: relire_une_bande(x) for k, x in pub.items()}
    nouvelles = {b["cle"]: {"domaine": le_domaine(b["le_sens"], b["les_lignes"], b["de"], b["a"]),
                            "pas": les_pas_dune_bande(relues[b["cle"]])} for b in bandes}
    sources = les_sources_de_235(par219, par223, par224, par232, par233, par234)
    for b in par238["bandes"]:
        sources[f"238 {b['cle']}"] = {"domaine": le_domaine(b["le_sens"], b["les_lignes"], b["de"], b["a"]),
                                      "pas": les_pas_dune_bande(par238["relues"][b["cle"]])}
    rep = la_reproduction_croisee(nouvelles, sources)
    if not rep.get("decidable"):
        return {**base, "decidable": False, "raison": rep.get("raison"), "la_reproduction": rep}
    pas = les_pas_des_bandes(par233["relues"], par233["bandes"])
    pas.update(les_pas_des_bandes(par238["relues"], par238["bandes"]))
    pas.update(les_pas_des_bandes(relues, bandes))  # une coupe est à neuf lignes au moins de toute autre
    par_tranche = []
    for sb in les_sous_boucles("droite", coins, coupes):
        a = analyser(pas, sb, par225["la_regle"], plus_long, g, t_)
        if not a.get("decidable"):
            return {**base, "decidable": False, "raison": f"la tranche {sb} : {a.get('raison')}", "la_reproduction": rep}
        par_tranche.append({"entre": [int(sb[0]), int(sb[1])], "les_coins": sb, **a})
    emb = lemboitement(par_tranche, fer233, "droite")
    if not emb.get("decidable"):
        return {**base, "decidable": False, "raison": emb.get("raison"), "la_reproduction": rep, "lemboitement": emb}
    par_238 = []
    for t238 in par238["par_tranche"]:
        a_, b_ = t238["entre"]
        dedans = [sb for sb in par_tranche if a_ <= sb["entre"][0] and sb["entre"][1] <= b_]
        e_ = lemboitement(dedans, t238, "droite")
        if not e_.get("decidable"):
            return {**base, "decidable": False, "la_reproduction": rep,
                    "raison": f"la tranche {t238['entre']} de `238` : {e_.get('raison')}"}
        par_238.append({"entre": [a_, b_], "combien_de_largeurs_jugees": e_["combien_de_largeurs_jugees"]})
    return {**base, "decidable": True, "la_reproduction": rep, "la_regle_appliquee": par225["la_regle"],
            "par_tranche": par_tranche, "lemboitement": emb, "lemboitement_par_tranche_de_238": par_238,
            "le_profil": le_profil(par_tranche, k1),
            "le_verdict": le_verdict_du_rectangle(len(coupes) - 1, par_tranche, demi, k1)}


def afficher(r: dict) -> None:
    if not r.get("decidable"):
        print(f"indécidable : {r.get('raison')}")
        return
    print(f"portée : {r['la_portee']} · coupes de 238 : {r['les_coupes_de_238']} · partage : {r['les_rangees_de_partage']}")
    print(f"coupes : {r['les_coupes']} · au-delà de la portée : {r['les_ecarts_au_dela_de_la_portee']}")
    if "par_tranche" in r:
        rp = r["la_reproduction"]
        print(f"contre la lecture : {r['la_presence_contre_la_lecture']}")
        print(f"reproduction : {rp['combien_de_coutures_relues']} coutures, écart {rp['lecart_le_plus_grand']}, "
              f"{sorted({k.split('×')[1] for k in rp['par_croisement']})}")
        print(f"emboîtement : {r['lemboitement']}")
        print(f"emboîtement par tranche de 238 : {r['lemboitement_par_tranche_de_238']}")
        for sb in r["par_tranche"]:
            x = sb["par_largeur"]["9"]
            print(f"  {sb['entre']} · 9 lignes · " + (f"L {x['la_fermeture_en_voxels']} · σ "
                                                       f"{x['la_dispersion_du_pas_en_voxels']} · nul {x['le_nul']}"
                                                       if x["fermable"] else "OUVERT"))
        print(f"profil : {r['le_profil']}")
    print(f"VERDICT · {r['le_verdict']}")


# ─────────────────────────────── la batterie ───────────────────────────────

def verifier() -> int:
    import copy
    import tempfile

    from le_rectangle_tient_il_sur_son_profil import mesurer as mesurer_238
    from le_segment_au_dela_du_rectangle_se_relie_t_il import les_sources_de_234
    from le_segment_au_dela_du_rectangle_se_relie_t_il import mesurer as mesurer_234
    from ou_sarrete_le_segment import les_sources
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

    # la portée et le partage
    def _p(cs, cum):  # noqa: E306
        return [{"la_coupe": c, "le_cumul_en_voxels": x} for c, x in zip(cs, cum)]
    v("★★★★ la portée va de la première à la dernière coupe où le cumul atteint le demi-feuillet",
      la_portee(_p([153, 163, 173, 183, 203, 213], [-27, -36.7, -40.2, -31.9, -37.7, -30.7]), 36.0) == 40)
    v("★★★ une seule coupe au-delà, ou aucune : pas de portée",
      la_portee(_p([10, 20], [-36.5, 0]), 36.0) is None and la_portee(_p([10], [1]), 36.0) is None)
    v("★★★ le demi-feuillet se compte en valeur absolue",
      la_portee(_p([10, 30], [36.0, -36.0]), 36.0) == 20)
    v("★★★★ chaque tranche est partagée en le moins de parts égales qui ne dépassent pas la portée",
      les_rangees_de_partage([26, 99, 198, 297, 384], 40) == [62, 132, 165, 231, 264, 326, 355])
    v("★★★ une tranche plus courte que la portée n'est pas partagée, une tranche d'exactement la portée non plus",
      les_rangees_de_partage([0, 30, 70], 40) == [])
    v("★★★ les écarts au-delà de la portée sont nommés, un écart égal à la portée n'en est pas",
      les_ecarts_au_dela([26, 62, 132, 198], 40) == [[62, 132], [132, 198]] and les_ecarts_au_dela([0, 40, 70], 40) == [])
    v("★★★★ après le partage, aucun écart ne dépasse la portée",
      not les_ecarts_au_dela(sorted([26, 99, 198, 297, 384] + les_rangees_de_partage([26, 99, 198, 297, 384], 40)), 40))

    # la mesure, sur des publications réelles, une empreinte et un champ fabriqués
    p219, p223, p224, p225 = ce_que_219_a_rendu(), ce_que_223_a_rendu(), ce_que_224_a_rendu(), ce_que_225_a_rendu()
    q225, q232, q233 = ce_que_225_a_publie(), ce_que_232_a_publie(), ce_que_233_a_publie()
    v("★★★★ ce que 238 et 235 publient se relit : les coupes 99, 198 et 297, et une portée de 40 rangées",
      _ok(lambda: ce_que_238_a_publie()["coupes"] == [26, 99, 198, 297, 384]
          and la_portee(ce_que_235_a_publie()["profil"], float(DEMI_PAS_EN_VOXELS)) == 40))
    gy, gx = p224["la_grille"]
    Af = np.zeros((gy, gx), dtype=bool)
    Af[5:395, 3:281] = True
    Af[5:18, :] = False
    Af[200:395, 250:281] = False

    def _champ(f, r, c):  # noqa: E306
        return round((((r * 2654435761) ^ (c * 40503 + (0 if f == "h" else 97))) % 1001) / 1000.0 * 0.6 - 0.3, 4)

    def _plat(f, r, c):  # noqa: E306
        return _champ(f, r, c) + (0.3 if f == "v" and c <= 11 else 0.0)

    def _entre_deux(f, r, c):  # noqa: E306
        # la colonne de droite s'écarte puis revient entre les coupes 99 et 198 de 238 : elles ne la voient pas
        x = _plat(f, r, c)
        if f == "v" and 239 <= c <= 247:
            x += 0.6 if 99 <= r < 148 else (-0.6 if 148 <= r < 197 else 0.0)
        return x

    def _sur_lempreinte(A_, champ):  # noqa: E306
        q2, q3 = copy.deepcopy(q232), copy.deepcopy(q233)
        for q in (q2, q3):
            for bb in q["bandes"]:
                for l_ in bb["les_lignes"]:
                    q["publiees"][bb["cle"]]["les_lectures"][str(l_)]["refuses"][ABSENT] = \
                        les_absents_dune_ligne(A_, bb["le_sens"], l_, bb["de"], bb["a"])
        autres = les_sources(p219, p223, p224, q2)

        def _lue_ailleurs(f, cle):  # noqa: E306
            return any(f in S_["pas"] and cle in S_["domaine"].get(f, ()) for S_ in autres.values())
        for bb in q3["bandes"]:
            rl = q3["relues"][bb["cle"]]
            f_long, f_trav = ("h", "v") if bb["le_sens"] == "rangees" else ("v", "h")
            for a_, s_ in rl["le_long"].items():
                for b_, t in s_.items():
                    r, c = (a_, b_) if bb["le_sens"] == "rangees" else (b_, a_)
                    if not _lue_ailleurs(f_long, (r, c)):
                        s_[b_] = (champ(f_long, r, c),) + tuple(t[1:])
            for r, s_ in rl["en_travers"].items():
                for c, t in s_.items():
                    if not _lue_ailleurs(f_trav, (r, c)):
                        s_[c] = (champ(f_trav, r, c),) + tuple(t[1:])
        q3["presence"] = {"decidable": True, "la_grille": [gy, gx], "les_pages": 1,
                          "les_rangees": ["".join("1" if x else "0" for x in r) for r in A_]}
        return q2, q3

    def _fabrique(bd_, src, champ):  # noqa: E306
        dom = le_domaine(bd_["le_sens"], bd_["les_lignes"], bd_["de"], bd_["a"])
        le_long_f, trav_f = (("h", "v") if bd_["le_sens"] == "rangees" else ("v", "h"))
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
                    pas_[f][cle] = champ(f, *cle)
        ll = {}
        for (r, c), x in pas_[le_long_f].items():
            a_, b_ = (r, c) if bd_["le_sens"] == "rangees" else (c, r)
            ll.setdefault(a_, {})[b_] = (x, 0.0, 16)
        tt = {}
        for (r, c), x in pas_[trav_f].items():
            tt.setdefault(r, {})[c] = (x, 0.0, 16)
        lectures = {l_: {"refuses": {ABSENT: les_absents_dune_ligne(Af, bd_["le_sens"], l_, bd_["de"], bd_["a"])}}
                    for l_ in bd_["les_lignes"]}
        return {"decidable": True, "le_long": ll, "en_travers": tt, "les_lectures": lectures}

    def _publie(m_, lecteur):  # noqa: E306
        with tempfile.TemporaryDirectory() as tmp:
            pj = Path(tmp) / "m.json"
            pj.write_text(json.dumps(m_, ensure_ascii=False))
            return lecteur(pj)
    q235p = {"decidable": True, "profil": _p([153, 163, 173, 183, 203, 213], [-27, -36.7, -40.2, -31.9, -37.7, -30.7])}

    def _scenario(champ):  # noqa: E306
        q2, q3 = _sur_lempreinte(Af, champ)
        s0 = les_sources_de_234(p219, p223, p224, q2, q3)
        m4 = _sur(mesurer_234, None, p219, p223, p224, p225, q225, q2, q3, lambda b: _fabrique(b, s0, champ), 49)
        q4 = _publie(m4, ce_que_234_a_publie)
        s1 = les_sources_de_235(p219, p223, p224, q2, q3, q4) if q4.get("decidable") else {}
        pas_ = les_pas_des_bandes(q3["relues"], q3["bandes"])
        f3 = {"decidable": True, "par_largeur": analyser(pas_, q3["coins"], p225["la_regle"],
                                                         max(q225["les_longueurs_essayees"]), p224["graine"],
                                                         49)["par_largeur"]}
        m8 = _sur(mesurer_238, None, p219, p223, p224, p225, q225, q2, q3, f3, q4, lambda b: _fabrique(b, s1, champ),
                  49, 36.0)
        q8 = _publie(m8, ce_que_238_a_publie)
        s2 = dict(s1)
        if q8.get("decidable"):
            for b in q8["bandes"]:
                s2[f"238 {b['cle']}"] = {"domaine": le_domaine(b["le_sens"], b["les_lignes"], b["de"], b["a"]),
                                         "pas": les_pas_dune_bande(q8["relues"][b["cle"]])}
        return q2, q3, q4, f3, q8, s2
    q232f, q233f, q234f, f233f, q238f, src2 = _scenario(_plat)
    v("★★★★ 238 rejoué sur l'empreinte fabriquée : ses trois coupes, ses quatre tranches",
      _ok(lambda: q238f["coupes"] == [26, 99, 198, 297, 384] and len(q238f["par_tranche"]) == 4),
      str(q238f.get("raison")))
    lus = []

    def _lit(b):  # noqa: E306
        lus.append(b)
        return _fabrique(b, src2, _plat)
    m = _sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, f233f, q234f, q235p, q238f, _lit, 49, 36.0)
    v("★★★★ une empreinte et une lecture fabriquées qui retombent passent la mesure entière",
      m.get("decidable") and "par_tranche" in m, str(m.get("raison")))
    v("★★★★ seules les coupes de plus se lisent, et toutes tiennent sur une grille qui le permet",
      _ok(lambda: m["les_coupes_de_plus"] == [62, 132, 165, 231, 264, 326, 355]
          and [b["le_centre"] for b in lus] == [62, 132, 165, 231, 264, 326, 355]
          and not m["les_ecarts_au_dela_de_la_portee"]), str(m.get("les_coupes")))
    v("★★★★ chaque coupe de plus est contrôlée par les deux colonnes de 233",
      _ok(lambda: all(any(k.startswith(f"{b['cle']}×233 colonnes_22") for k in m["la_reproduction"]["par_croisement"])
                      and any(k.startswith(f"{b['cle']}×233 colonnes_243") for k in m["la_reproduction"]["par_croisement"])
                      for b in m["les_bandes_declarees"])))
    v("★★★★ onze tranches fines, qui somment au rectangle et, deux ou trois à la fois, aux tranches de 238",
      _ok(lambda: len(m["par_tranche"]) == 11 and m["lemboitement"]["par_largeur"]["9"]["jugeable"]
          and [x["entre"] for x in m["lemboitement_par_tranche_de_238"]] == [[26, 99], [99, 198], [198, 297], [297, 384]]
          and all(x["combien_de_largeurs_jugees"] >= 1 for x in m["lemboitement_par_tranche_de_238"])),
      str(m.get("lemboitement_par_tranche_de_238")))
    v("★★★★ la règle de 225 est appliquée, le profil et le verdict sont ceux des tranches fines",
      _ok(lambda: m["la_regle_appliquee"] == p225["la_regle"] and m["le_plus_long_trou_franchi_par_225"] == 17
          and m["le_profil"] == le_profil(m["par_tranche"], 9)
          and m["le_verdict"] == le_verdict_du_rectangle(11, m["par_tranche"], 36.0, 9)))
    q232e, q233e, q234e, f233e, q238e, src_e = _scenario(_entre_deux)
    me = _sur(mesurer, None, p219, p223, p224, p225, q225, q232e, q233e, f233e, q234e, q235p, q238e,
              lambda b: _fabrique(b, src_e, _entre_deux), 49, 36.0)
    ecarts = {q["la_coupe"]: round(float(q["le_cumul_en_voxels"]) - float(p_["le_cumul_en_voxels"]), 4)
              for q, p_ in zip(me.get("le_profil") or [], m.get("le_profil") or [])}
    v("★★★★ une colonne qui s'écarte puis revient entre deux coupes de 238 : elles ne la voient pas, les coupes de plus "
      "oui",
      _ok(lambda: abs(ecarts[99]) <= 0.01 and abs(ecarts[198]) <= 0.01 and abs(ecarts[132] - 0.6 * 33) <= 0.01
          and abs(ecarts[165] - (0.6 * 49 - 0.6 * 17)) <= 0.01), str(ecarts))
    q238x = copy.deepcopy(q238f)
    if q238x.get("decidable"):
        q238x["par_tranche"][1]["par_largeur"]["9"]["la_fermeture_en_voxels"] += 1.0
    v("★★★★ des tranches fines qui ne somment pas à la tranche de 238 qui les contient sont refusées",
      "de `238`" in str(_sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, f233f, q234f, q235p, q238x,
                             lambda b: _fabrique(b, src2, _plat), 49, 36.0).get("raison")))
    f233x = copy.deepcopy(f233f)
    f233x["par_largeur"]["9"]["la_fermeture_en_voxels"] += 1.0
    v("★★★★ des tranches fines qui ne somment pas au rectangle de 233 sont refusées",
      "l'emboîtement ne retombe pas" in str(_sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, f233x,
                                                  q234f, q235p, q238f, lambda b: _fabrique(b, src2, _plat), 49, 36.0)
                                             .get("raison")))
    v("★★★★ sans traversée publiée par 235, pas de portée, et rien n'est lu",
      "pas de portée" in str(_sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, f233f, q234f,
                                  {"decidable": True, "profil": _p([10], [1.0])}, q238f, _lit, 49, 36.0).get("raison")))

    def _menteuse(b):  # noqa: E306
        x = _fabrique(b, src2, _plat)
        x["les_lectures"][b["les_lignes"][0]]["refuses"][ABSENT] += 1
        return x
    v("★★★★ une lecture dont les absents ne sont pas ceux de la présence est refusée",
      "ne retombe pas" in str(_sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, f233f, q234f, q235p,
                                   q238f, _menteuse, 49, 36.0).get("raison")))

    def _decale(b):  # noqa: E306
        x = _fabrique(b, src2, _plat)
        for r, s_ in x["en_travers"].items():
            for c in s_:
                s_[c] = (s_[c][0] + 1.0, 0.0, 16)
        return x
    v("★★★★ une coupe qui ne retombe pas sur ce qui est publié est refusée, par sa raison",
      "ne retombe pas sur" in str(_sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, f233f, q234f, q235p,
                                       q238f, _decale, 49, 36.0).get("raison")))
    q238p = copy.deepcopy(q238f)
    if q238p.get("decidable"):
        b0_ = q238p["bandes"][0]
        q238p["publiees"][b0_["cle"]]["les_lectures"][str(b0_["les_lignes"][0])]["refuses"][ABSENT] += 1
    v("★★★★ une présence qui ne retombe pas sur les coupes de 238 est refusée, par sa raison",
      "ne retombe pas" in str(_sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, f233f, q234f, q235p,
                                   q238p, _lit, 49, 36.0).get("raison")))
    with tempfile.TemporaryDirectory() as tmp:
        dep = Path(tmp) / "lecture.json"
        faux = {k: dict(x) for k, x in (m.get("les_bandes") or {}).items()}
        if faux:
            une = sorted(faux)[0]
            faux[une] = {**faux[une], "les_lignes": [x - 2 for x in faux[une]["les_lignes"]]}
        dep.write_text(json.dumps({"les_bandes": faux}))
        mf = _sur(mesurer, dep, p219, p223, p224, p225, q225, q232f, q233f, f233f, q234f, q235p, q238f, None, 49, 36.0)
        dep.write_text(json.dumps({"les_bandes": m.get("les_bandes") or {}}))
        mj = _sur(mesurer, dep, p219, p223, p224, p225, q225, q232f, q233f, f233f, q234f, q235p, q238f, None, 49, 36.0)
    v("★★★★ une coupe lue sur d'autres lignes que celles dérivées est refusée",
      "pas celle des coupes dérivées" in str(mf.get("raison")), str(mf.get("raison")))
    v("★★★★ la mesure se rejoue depuis sa lecture publiée, à l'identique",
      _ok(lambda: json.dumps(mj, sort_keys=True) == json.dumps(m, sort_keys=True)))

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
        par233, par235, par238 = ce_que_233_a_publie(), ce_que_235_a_publie(), ce_que_238_a_publie()
        for nom, par in (("233", par233), ("235", par235), ("238", par238)):
            if not par.get("decidable"):
                print(f"indécidable : `{nom}` : {par.get('raison')}")
                return 1
        portee = la_portee(par235["profil"], float(DEMI_PAS_EN_VOXELS))
        if portee is None:
            print("indécidable : `235` ne publie aucune traversée")
            return 1
        A = la_grille_de_presence(par233["presence"])
        k1 = les_largeurs()[-1]
        coins = [int(x) for x in par233["coins"]]
        c238 = par238["coupes"]
        coupes = les_coupes_du_rectangle(A, coins, c238[1:-1] + les_rangees_de_partage(c238, portee), k1)
        nouvelles_c = [c for c in coupes if c not in c238]
        print(f"portée : {portee} · coupes : {coupes} · de plus : {nouvelles_c}", flush=True)
        if not nouvelles_c:
            return 0
        bandes = les_bandes_des_coupes_du_rectangle([coupes[0]] + nouvelles_c + [coupes[-1]], coins[2], coins[3], k1)
        print(f"bandes : {[(b['cle'], len(b['les_lignes']) * (b['a'] - b['de'] + 1)) for b in bandes]}", flush=True)
        deja = json.loads(a.lire.read_text()) if a.lire.exists() else {}
        a.lire.parent.mkdir(parents=True, exist_ok=True)

        def ecrire(d):  # noqa: E306
            a.lire.write_text(json.dumps({"les_bandes": d}, ensure_ascii=False))
            print(f"écrit : {a.lire} ({len(d)} bandes)", flush=True)
        lu = lire_les_bandes(bandes, deja.get("les_bandes") or {}, ecrire)
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
