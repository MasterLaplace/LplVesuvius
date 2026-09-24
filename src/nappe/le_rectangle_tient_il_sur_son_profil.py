"""Le plus grand rectangle de `233`, jugé sur son profil et non à son bout, reste-t-il sous le demi-feuillet ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LA MOINDRE LIGNE NOUVELLE NE SOIT LUE. Ce qui était vu avant d'écrire : ce que `237`
publie et sa figure, et la liste des bandes que les tranches publiées ont déclarées : aucune bande de rangées de neuf
lignes ne traverse le rectangle de part en part hors de ses deux bouts.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P83`. `237` a montré que l'aile de droite de `234` fermait au bout, à
−35,6938 voxels, après avoir franchi le demi-feuillet en chemin, jusqu'à −40,2188 : juger une boucle à son bout ne
suffit pas. Le plus grand rectangle de `233`, des rangées 26 à 384 et des colonnes 22 à 243, ferme à −11,8449 voxels
à neuf lignes, au bout. Ses boucles partielles, de la rangée 26 à une rangée intérieure, restent-elles sous le
demi-feuillet ?

## Les coupes, reprises de `224`

Une COUPE est une bande de rangées de neuf lignes tendue d'une colonne du rectangle à l'autre, qui tient au sens de
`233`. Les coupes sont les rangées que `224` a dérivées pour ses boucles et publiées comme ses centres de rangées ;
une rangée dont la bande ne tient pas est retirée, et ses deux intervalles se fondent. ⚠⚠ Elles ne sont pas choisies,
et elles sont peu nombreuses : lire une coupe du rectangle coûte deux cent vingt-deux colonnes de neuf lignes. Entre
deux coupes, le profil n'est pas vu.

## Ce qui se lit, et ce qui le contrôle

Les coupes seules, par le lecteur de `224`. ⚠⚠ Les quatre bandes du rectangle ne sont pas relues : leurs pas sont ceux
que `233` publie. ⚠⚠⚠ Partout où une coupe croise une bande publiée — `219`, `223`, `224`, `232`, `233`, `234` —, les pas
relus retombent à l'arrondi, sinon refus ; une coupe qui ne croise aucune bande publiée est refusée. ⚠⚠ Les chunks que
la lecture compte absents du dépôt sont ceux que la présence dit absents.

## Ce qui se mesure

L'instrument de `228` sur chaque tranche du rectangle, d'une coupe à la suivante, à chaque largeur, avec la garde de
`232`. ⚠⚠⚠ LES TRANCHES S'EMBOÎTENT : la somme de leurs fermetures est celle du rectangle ; là où aucune tranche n'a de
trou sur une colonne, elle retombe sur ce que `233` publie, à l'arrondi près, sinon refus. LE PROFIL : la fermeture
cumulée depuis la rangée 26, coupe après coupe.

## Les issues, exclusives, jugées à neuf lignes

- aucune coupe ne tient : le rectangle ne se découpe pas, et rien n'est lu ;
- une tranche garde un trou plus long que ceux que `225` a franchis : elle reste ouverte ;
- le profil atteint le demi-feuillet à une coupe : le rectangle ne ferme qu'au bout ;
- il reste dessous à chaque coupe : le rectangle tient sur son profil, là où il est vu.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : ce que fait le profil entre deux coupes ; ni, si une tranche s'écarte, laquelle de
ses lignes dérive.

Usage :
    uv run python src/nappe/le_rectangle_tient_il_sur_son_profil.py --verifier
    uv run python src/nappe/le_rectangle_tient_il_sur_son_profil.py --lire <lecture.json>
    uv run python src/nappe/le_rectangle_tient_il_sur_son_profil.py --depuis <lecture.json> \\
        --json docs/mesures/le_rectangle_tient_il_sur_son_profil.json
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
                                                          ce_que_223_a_rendu, lire_les_bandes,
                                                          relire_une_bande)
from deux_chemins_du_segment_entier_arrivent_ils_sur_la_meme_spire import (analyser,  # noqa: E402
                                                                            ce_que_225_a_publie,
                                                                            les_pas_des_bandes)
from lajustement_de_toutes_les_boucles_garde_t_il_la_spire import ce_que_225_a_rendu  # noqa: E402
from le_segment_au_dela_du_rectangle_se_relie_t_il import (CE_QUE_233_A_PUBLIE,  # noqa: E402
                                                           ce_que_233_a_publie, les_tenues, tient)
from le_vote_ramene_t_il_les_rangees_sur_le_feuillet import ce_que_219_a_rendu  # noqa: E402
from letroite_reste_t_elle_sans_ecart import les_franchissements  # noqa: E402
from ou_est_lerreur_de_la_boucle_en_haut_a_gauche import (la_reproduction_croisee,  # noqa: E402
                                                          le_domaine, les_pas_dune_bande)
from ou_laile_de_droite_se_separe import (ce_que_234_a_publie, le_profil,  # noqa: E402
                                          lemboitement, les_sources_de_235, les_sous_boucles)
from ou_sarrete_le_segment import (ABSENT, ce_que_232_a_publie,  # noqa: E402
                                   la_grille_de_presence, la_presence_retombe, les_absents_dune_ligne)
from que_montrent_ces_deux_vues import DEMI_PAS_EN_VOXELS  # noqa: E402
from quest_ce_qui_franchit_le_trou_de_majorite import ce_que_224_a_rendu  # noqa: E402
from une_bande_plus_large_ferme_t_elle_le_grand_rectangle import les_largeurs  # noqa: E402

LA_QUESTION_DECLAREE = ("le plus grand rectangle de `233`, jugé sur son profil et non à son bout, reste-t-il sous le "
                        "demi-feuillet ?")
LA_MESURE_DECLAREE = ("le rectangle de `233` coupé aux rangées que `224` publie, là où la bande de neuf lignes tient, "
                      "l'instrument de `228` sur chaque tranche, et la fermeture cumulée coupe après coupe")


def la_fermeture_de_233(chemin: Path = CE_QUE_233_A_PUBLIE) -> dict:
    """L'analyse du rectangle, largeur par largeur, telle que `233` la publie."""
    try:
        d = json.loads(Path(chemin).read_text())
    except (ValueError, OSError) as e:
        return {"decidable": False, "raison": f"{Path(chemin).name} est illisible : {e}"}
    if not d.get("par_largeur"):
        return {"decidable": False, "raison": "`233` ne publie pas l'analyse de son rectangle"}
    return {"decidable": True, "par_largeur": d["par_largeur"]}


# ─────────────────────────────── les coupes, reprises ───────────────────────────────

def les_coupes_du_rectangle(A: np.ndarray, coins, rangees, k: int, tenues=None) -> list[int]:
    """Les deux bouts du rectangle, et les rangées données qui tombent strictement entre eux, à `k` lignes au moins
    de tout ce qui est gardé, là où la bande de neuf lignes tient d'une colonne à l'autre."""
    r0, r1, c0, c1 = [int(x) for x in coins]
    k = int(k)
    PR, PC = tenues if tenues is not None else les_tenues(np.asarray(A, dtype=bool), k)
    gardees = [r0]
    for r in sorted(int(x) for x in rangees):
        if r - gardees[-1] >= k and r1 - r >= k and tient(PR, PC, "rangees", r, c0, c1):
            gardees.append(r)
    return gardees + [r1]


def les_bandes_des_coupes_du_rectangle(coupes, c0: int, c1: int, k: int) -> list[dict]:
    """Les coupes intérieures, à lire."""
    return [{"cle": f"rangees_{c}_{c0}_{c1}", "le_sens": "rangees", "le_centre": int(c),
             "les_lignes": les_rangees_a_lire(int(c), int(k)), "de": int(c0), "a": int(c1)} for c in coupes[1:-1]]


# ─────────────────────────────── le verdict ───────────────────────────────

def _ce_qui_reste(sans_coupe: bool, ouverte: bool, franchit: bool) -> str:
    """Les quatre issues, EXCLUSIVES, dans cet ordre de priorité."""
    if sans_coupe:
        return "AUCUNE COUPE NE TIENT DANS LE RECTANGLE : IL NE SE DÉCOUPE PAS"
    if ouverte:
        return "À NEUF LIGNES, UN TROU PLUS LONG QUE CEUX QUE `225` A FRANCHIS LAISSE UNE TRANCHE OUVERTE"
    if franchit:
        return "À NEUF LIGNES, LE PROFIL DU RECTANGLE ATTEINT LE DEMI-FEUILLET À UNE COUPE : IL NE FERME QU'AU BOUT"
    return "À NEUF LIGNES, LE PROFIL DU RECTANGLE RESTE SOUS LE DEMI-FEUILLET À CHAQUE COUPE"


def le_verdict_du_rectangle(combien: int, par_tranche: list[dict], demi: float, k1: int) -> dict:
    """Le verdict à la plus large, depuis les tranches."""
    kk = str(k1)
    base = {"la_largeur_jugee": int(k1), "combien_de_tranches": int(combien)}
    if int(combien) < 2:
        return {**base, "les_tranches_ouvertes": [], "franchit": False, "reste_dessous": False,
                "ce_qui_reste_a_mesurer": _ce_qui_reste(True, False, False)}
    ouv = [sb["entre"] for sb in par_tranche if not sb["par_largeur"][kk]["fermable"]]
    if ouv:
        return {**base, "les_tranches_ouvertes": ouv, "franchit": False, "reste_dessous": False,
                "ce_qui_reste_a_mesurer": _ce_qui_reste(False, True, False)}
    prof = le_profil(par_tranche, k1)
    fr = les_franchissements(prof, demi)
    pic = max(prof, key=lambda p: abs(float(p["le_cumul_en_voxels"])))
    return {**base, "les_tranches_ouvertes": [], "franchit": bool(fr), "reste_dessous": not fr, "le_pic": pic,
            "les_franchissements": fr, "ce_qui_reste_a_mesurer": _ce_qui_reste(False, False, bool(fr))}


# ─────────────────────────────── la mesure ───────────────────────────────

def mesurer(depuis: Path | None = None, par219: dict | None = None, par223: dict | None = None,
            par224: dict | None = None, par225: dict | None = None, pub225: dict | None = None,
            par232: dict | None = None, par233: dict | None = None, fer233: dict | None = None,
            par234: dict | None = None, lire=None, tirages: int | None = None, demi: float | None = None) -> dict:
    """Les coupes du rectangle, leur lecture, puis les tranches et le profil — ou rejoués."""
    par219 = ce_que_219_a_rendu() if par219 is None else par219
    par223 = ce_que_223_a_rendu() if par223 is None else par223
    par224 = ce_que_224_a_rendu() if par224 is None else par224
    par225 = ce_que_225_a_rendu() if par225 is None else par225
    pub225 = ce_que_225_a_publie() if pub225 is None else pub225
    par232 = ce_que_232_a_publie() if par232 is None else par232
    par233 = ce_que_233_a_publie() if par233 is None else par233
    fer233 = la_fermeture_de_233() if fer233 is None else fer233
    par234 = ce_que_234_a_publie() if par234 is None else par234
    base = {"la_question_declaree": LA_QUESTION_DECLAREE, "la_mesure_declaree": LA_MESURE_DECLAREE}
    for nom, par in (("219", par219), ("223", par223), ("224", par224), ("225", par225), ("225 publiée", pub225),
                     ("232", par232), ("233", par233), ("233 analyse", fer233), ("234", par234)):
        if not par.get("decidable"):
            return {**base, "decidable": False, "raison": f"`{nom}` : {par.get('raison')}"}
    demi = float(DEMI_PAS_EN_VOXELS) if demi is None else float(demi)
    presence = par233["presence"]
    if [int(x) for x in presence["la_grille"]] != [int(x) for x in par224["la_grille"]]:
        return {**base, "decidable": False, "raison": "la grille de `233` n'est pas celle que les bandes parcourent"}
    A = la_grille_de_presence(presence)
    c_ = la_presence_retombe(A, par233["bandes"], par233["publiees"])
    base["la_presence_contre_233"] = c_
    if not c_.get("decidable"):
        return {**base, "decidable": False, "raison": c_.get("raison")}
    k1 = les_largeurs()[-1]
    coins = [int(x) for x in par233["coins"]]
    r0, r1, c0, c1 = coins
    coupes = les_coupes_du_rectangle(A, coins, par224["R"], k1)
    base.update({"le_rectangle": coins, "la_fermeture_du_rectangle": fer233["par_largeur"][str(k1)]
                 .get("la_fermeture_en_voxels"), "les_rangees_de_224": [int(x) for x in par224["R"]],
                 "les_coupes": coupes})
    if len(coupes) < 3:
        return {**base, "decidable": True, "le_verdict": le_verdict_du_rectangle(len(coupes) - 1, [], demi, k1)}
    bandes = les_bandes_des_coupes_du_rectangle(coupes, c0, c1, k1)
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
        return {**base, "decidable": False, "raison": "la lecture n'est pas celle des coupes reprises"}
    cn = la_presence_retombe(A, bandes, pub)
    base["la_presence_contre_la_lecture"] = cn
    if not cn.get("decidable"):
        return {**base, "decidable": False, "raison": cn.get("raison")}
    relues = {k: relire_une_bande(x) for k, x in pub.items()}
    nouvelles = {b["cle"]: {"domaine": le_domaine(b["le_sens"], b["les_lignes"], b["de"], b["a"]),
                            "pas": les_pas_dune_bande(relues[b["cle"]])} for b in bandes}
    rep = la_reproduction_croisee(nouvelles, les_sources_de_235(par219, par223, par224, par232, par233, par234))
    if not rep.get("decidable"):
        return {**base, "decidable": False, "raison": rep.get("raison"), "la_reproduction": rep}
    pas = les_pas_des_bandes(par233["relues"], par233["bandes"])
    pas.update(les_pas_des_bandes(relues, bandes))  # une coupe est à neuf lignes au moins des bouts
    par_tranche = []
    for sb in les_sous_boucles("droite", coins, coupes):
        a = analyser(pas, sb, par225["la_regle"], plus_long, g, t_)
        if not a.get("decidable"):
            return {**base, "decidable": False, "raison": f"la tranche {sb} : {a.get('raison')}", "la_reproduction": rep}
        par_tranche.append({"entre": [int(sb[0]), int(sb[1])], "les_coins": sb, **a})
    emb = lemboitement(par_tranche, fer233, "droite")
    if not emb.get("decidable"):
        return {**base, "decidable": False, "raison": emb.get("raison"), "la_reproduction": rep, "lemboitement": emb}
    return {**base, "decidable": True, "la_reproduction": rep, "la_regle_appliquee": par225["la_regle"],
            "par_tranche": par_tranche, "lemboitement": emb, "le_profil": le_profil(par_tranche, k1),
            "le_verdict": le_verdict_du_rectangle(len(coupes) - 1, par_tranche, demi, k1)}


def afficher(r: dict) -> None:
    if not r.get("decidable"):
        print(f"indécidable : {r.get('raison')}")
        return
    print(f"rectangle : {r['le_rectangle']} · fermeture publiée {r['la_fermeture_du_rectangle']}")
    print(f"rangées de 224 : {r['les_rangees_de_224']} · coupes : {r['les_coupes']}")
    if "par_tranche" in r:
        rp = r["la_reproduction"]
        print(f"contre la lecture : {r['la_presence_contre_la_lecture']}")
        print(f"reproduction : {rp['combien_de_coutures_relues']} coutures {rp['par_croisement']}, écart "
              f"{rp['lecart_le_plus_grand']}")
        print(f"emboîtement : {r['lemboitement']}")
        for sb in r["par_tranche"]:
            for k, x in sb["par_largeur"].items():
                if not x["fermable"]:
                    print(f"  {sb['entre']} · {k} lignes · OUVERT · {x['les_trous_trop_longs']}")
                    continue
                print(f"  {sb['entre']} · {k} lignes · L {x['la_fermeture_en_voxels']} · σ "
                      f"{x['la_dispersion_du_pas_en_voxels']} · nul {x['le_nul']} · trous {x['les_trous']} · côtés "
                      f"{x['les_cotes']}")
        print(f"profil : {r['le_profil']}")
    print(f"VERDICT · {r['le_verdict']}")


# ─────────────────────────────── la batterie ───────────────────────────────

def verifier() -> int:
    import copy
    import itertools
    import tempfile

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

    # les coupes reprises
    Ap = np.ones((396, 285), dtype=bool)
    co = [26, 384, 22, 243]
    v("★★★★ sur une grille pleine, les rangées de 224 sont les coupes, entre les deux bouts",
      _ok(lambda: les_coupes_du_rectangle(Ap, co, [99, 198, 297], 9) == [26, 99, 198, 297, 384]))
    Ah = Ap.copy()
    Ah[200, 100] = False
    v("★★★★ une rangée dont une ligne perd un chunk d'une colonne à l'autre est retirée, et elle seule",
      _ok(lambda: les_coupes_du_rectangle(Ah, co, [99, 198, 297], 9) == [26, 99, 297, 384]))
    Ah2 = Ap.copy()
    Ah2[200, 243] = False
    v("★★★ la coupe est vérifiée jusqu'à la colonne de droite comprise",
      _ok(lambda: les_coupes_du_rectangle(Ah2, co, [99, 198, 297], 9) == [26, 99, 297, 384]))
    v("★★★★ une rangée à moins de neuf lignes d'un bout ou d'une coupe gardée est écartée",
      _ok(lambda: les_coupes_du_rectangle(Ap, co, [30, 99, 104, 380], 9) == [26, 99, 384]))
    v("★★★ une rangée hors du rectangle est écartée, et l'ordre donné n'importe pas",
      _ok(lambda: les_coupes_du_rectangle(Ap, co, [400, 297, 10, 99], 9) == [26, 99, 297, 384]))
    bd = _sur(les_bandes_des_coupes_du_rectangle, [26, 99, 198, 297, 384], 22, 243, 9)
    v("★★★★ seules les coupes intérieures se lisent, d'une colonne du rectangle à l'autre",
      _ok(lambda: [b["cle"] for b in bd] == ["rangees_99_22_243", "rangees_198_22_243", "rangees_297_22_243"]
          and bd[0]["les_lignes"] == list(range(95, 104))))

    # le verdict, sur des tranches fabriquées
    def _sb(e, L, fermable=True):  # noqa: E306
        return {"entre": list(e), "par_largeur": {"9": {"fermable": fermable, "la_fermeture_en_voxels": L}}}
    es = [(26, 99), (99, 198), (198, 297), (297, 384)]
    vd = le_verdict_du_rectangle(4, [_sb(e, L) for e, L in zip(es, [-10, -20, 5, 13.1551])], 36.0, 9)
    v("★★★★ un profil qui reste sous le demi-feuillet à chaque coupe : le rectangle tient sur son profil",
      vd["reste_dessous"] and not vd["franchit"] and "RESTE SOUS" in vd["ce_qui_reste_a_mesurer"]
      and vd["le_pic"] == {"la_coupe": 198, "le_cumul_en_voxels": -30.0}, str(vd))
    vf = le_verdict_du_rectangle(4, [_sb(e, L) for e, L in zip(es, [-10, -30, 20, 8.1551])], 36.0, 9)
    v("★★★★ un profil qui atteint le demi-feuillet à une coupe : le rectangle ne ferme qu'au bout",
      vf["franchit"] and not vf["reste_dessous"] and [p["la_coupe"] for p in vf["les_franchissements"]] == [198]
      and "QU'AU BOUT" in vf["ce_qui_reste_a_mesurer"])
    ve = le_verdict_du_rectangle(4, [_sb(e, L) for e, L in zip(es, [-10, -26, 20, 4])], 36.0, 9)
    v("★★★ atteindre le demi-feuillet suffit", ve["franchit"] and [p["la_coupe"] for p in ve["les_franchissements"]]
      == [198])
    vo = le_verdict_du_rectangle(4, [_sb(e, L) for e, L in zip(es, [-10, -30, 20, 8])][:1]
                                 + [_sb((99, 198), 0.0, fermable=False)] + [_sb(e, 1.0) for e in es[2:]], 36.0, 9)
    v("★★★★ une tranche ouverte prime", vo["les_tranches_ouvertes"] == [[99, 198]] and not vo["franchit"]
      and not vo["reste_dessous"] and "OUVERTE" in vo["ce_qui_reste_a_mesurer"])
    v0 = _sur(le_verdict_du_rectangle, 1, [], 36.0, 9)
    v("★★★★ sans coupe, rien ne se juge", _ok(lambda: "NE SE DÉCOUPE PAS" in v0["ce_qui_reste_a_mesurer"]
                                              and not v0["reste_dessous"] and not v0["franchit"]))
    v("★★★ les quatre issues sont distinctes",
      len({_ce_qui_reste(a, b, c) for a, b, c in itertools.product((True, False), repeat=3)}) == 4)

    # la mesure, sur des publications réelles, une empreinte et un champ fabriqués
    p219, p223, p224, p225 = ce_que_219_a_rendu(), ce_que_223_a_rendu(), ce_que_224_a_rendu(), ce_que_225_a_rendu()
    q225, q232, q233 = ce_que_225_a_publie(), ce_que_232_a_publie(), ce_que_233_a_publie()
    f233 = la_fermeture_de_233()
    v("★★★★ ce que 233 et 224 publient se relit : le rectangle, sa fermeture, les rangées de 224",
      _ok(lambda: q233["coins"] == [26, 384, 22, 243] and f233["par_largeur"]["9"]["la_fermeture_en_voxels"] == -11.8449
          and p224["R"] == [99, 198, 297]))
    gy, gx = p224["la_grille"]
    Af = np.zeros((gy, gx), dtype=bool)
    Af[5:395, 3:281] = True
    Af[5:18, :] = False
    Af[200:395, 250:281] = False

    def _champ(f, r, c):  # noqa: E306
        return round((((r * 2654435761) ^ (c * 40503 + (0 if f == "h" else 97))) % 1001) / 1000.0 * 0.6 - 0.3, 4)

    def _plat(f, r, c):  # noqa: E306
        return _champ(f, r, c) + (0.3 if f == "v" and c <= 11 else 0.0)

    def _aller_retour(f, r, c):  # noqa: E306
        # la colonne de droite du rectangle s'écarte puis revient
        x = _plat(f, r, c)
        if f == "v" and 239 <= c <= 247:
            x += 0.6 if 26 <= r < 198 else (-0.6 if 198 <= r < 370 else 0.0)
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

    def _scenario(champ):  # noqa: E306
        q2, q3 = _sur_lempreinte(Af, champ)
        s0 = les_sources_de_234(p219, p223, p224, q2, q3)
        m4 = _sur(mesurer_234, None, p219, p223, p224, p225, q225, q2, q3, lambda b: _fabrique(b, s0, champ), 49)
        with tempfile.TemporaryDirectory() as tmp:
            pj = Path(tmp) / "m.json"
            pj.write_text(json.dumps(m4, ensure_ascii=False))
            q4 = ce_que_234_a_publie(pj)
        s1 = les_sources_de_235(p219, p223, p224, q2, q3, q4) if q4.get("decidable") else {}
        pas_ = les_pas_des_bandes(q3["relues"], q3["bandes"])
        f3 = {"decidable": True, "par_largeur": analyser(pas_, q3["coins"], p225["la_regle"],
                                                         max(q225["les_longueurs_essayees"]), p224["graine"],
                                                         49)["par_largeur"]}
        return q2, q3, q4, s1, f3
    q232f, q233f, q234f, src1, f233f = _scenario(_plat)
    lus = []

    def _lit(b):  # noqa: E306
        lus.append(b)
        return _fabrique(b, src1, _plat)
    m = _sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, f233f, q234f, _lit, 49, 36.0)
    v("★★★★ une empreinte et une lecture fabriquées qui retombent passent la mesure entière",
      m.get("decidable") and "par_tranche" in m, str(m.get("raison")))
    v("★★★★ les coupes sont les rangées de 224, lues d'une colonne du rectangle à l'autre",
      _ok(lambda: m["les_coupes"] == [26, 99, 198, 297, 384] and [b["cle"] for b in lus]
          == ["rangees_99_22_243", "rangees_198_22_243", "rangees_297_22_243"]), str(m.get("les_coupes")))
    v("★★★★ chaque coupe est contrôlée par les deux colonnes de 233",
      _ok(lambda: all(any(k.startswith(f"{b['cle']}×233 colonnes_22") for k in m["la_reproduction"]["par_croisement"])
                      and any(k.startswith(f"{b['cle']}×233 colonnes_243") for k in m["la_reproduction"]["par_croisement"])
                      for b in m["les_bandes_declarees"])), str(m.get("la_reproduction", {}).get("par_croisement")))
    v("★★★★ quatre tranches, chacune sur ses quatre côtés à chaque largeur",
      _ok(lambda: [sb["les_coins"] for sb in m["par_tranche"]] == [[26, 99, 22, 243], [99, 198, 22, 243],
                                                                   [198, 297, 22, 243], [297, 384, 22, 243]]
          and all(sorted(sb["par_largeur"], key=int) == ["3", "5", "7", "9"] for sb in m["par_tranche"])))
    v("★★★★ les tranches somment à la fermeture du rectangle, à neuf lignes",
      _ok(lambda: m["lemboitement"]["par_largeur"]["9"]["jugeable"]
          and abs(m["le_profil"][-1]["le_cumul_en_voxels"] - f233f["par_largeur"]["9"]["la_fermeture_en_voxels"])
          <= 5e-5 * 5), str(m.get("lemboitement")))
    v("★★★★ la règle de 225 est appliquée, le profil et le verdict sont ceux des tranches",
      _ok(lambda: m["la_regle_appliquee"] == p225["la_regle"] and m["le_plus_long_trou_franchi_par_225"] == 17
          and m["le_profil"] == le_profil(m["par_tranche"], 9)
          and m["le_verdict"] == le_verdict_du_rectangle(4, m["par_tranche"], 36.0, 9)))
    q232a, q233a, q234a, src_a, f233a = _scenario(_aller_retour)
    ma = _sur(mesurer, None, p219, p223, p224, p225, q225, q232a, q233a, f233a, q234a,
              lambda b: _fabrique(b, src_a, _aller_retour), 49, 36.0)
    # la colonne de droite dérive de +0,6 voxel par couture jusqu'à la rangée 198, puis de −0,6 jusqu'à la 370 : le
    # profil en porte la trace coupe après coupe, et le bout rien du tout
    attendu = [0.6 * 73, 0.6 * 172, 0.6 * 172 - 0.6 * 99, 0.0]
    ecarts = [round(float(pa["le_cumul_en_voxels"]) - float(pp["le_cumul_en_voxels"]), 4)
              for pa, pp in zip(ma.get("le_profil") or [], m.get("le_profil") or [])]
    v("★★★★ une colonne qui s'écarte puis revient : le profil la montre à chaque coupe, le bout ne la voit pas",
      _ok(lambda: len(ecarts) == 4 and all(abs(e - x) <= 0.01 for e, x in zip(ecarts, attendu))
          and [q["la_coupe"] for q in ma["le_verdict"]["les_franchissements"]][:2] == [99, 198]),
      str(ecarts) + " " + str(ma.get("raison") or ma.get("le_verdict")))

    def _menteuse(b):  # noqa: E306
        x = _fabrique(b, src1, _plat)
        x["les_lectures"][b["les_lignes"][0]]["refuses"][ABSENT] += 1
        return x
    v("★★★★ une lecture dont les absents ne sont pas ceux de la présence est refusée",
      "ne retombe pas" in str(_sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, f233f, q234f, _menteuse,
                                   49, 36.0).get("raison")))

    def _decale(b):  # noqa: E306
        x = _fabrique(b, src1, _plat)
        for r, s_ in x["en_travers"].items():
            for c in s_:
                s_[c] = (s_[c][0] + 1.0, 0.0, 16)
        return x
    v("★★★★ une coupe qui ne retombe pas sur ce qui est publié est refusée, par sa raison",
      "ne retombe pas sur" in str(_sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, f233f, q234f, _decale,
                                       49, 36.0).get("raison")))
    f233e = copy.deepcopy(f233f)
    f233e["par_largeur"]["9"]["la_fermeture_en_voxels"] += 1.0
    v("★★★★ des tranches qui ne somment pas à ce que 233 publie sont refusées",
      "l'emboîtement ne retombe pas" in str(_sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, f233e,
                                                  q234f, lambda b: _fabrique(b, src1, _plat), 49, 36.0).get("raison")))
    q233p = copy.deepcopy(q233f)
    b0_ = q233p["bandes"][0]
    q233p["publiees"][b0_["cle"]]["les_lectures"][str(b0_["les_lignes"][0])]["refuses"][ABSENT] += 1
    v("★★★★ une présence qui ne retombe pas sur les bandes de 233 est refusée, par sa raison",
      "ne retombe pas" in str(_sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233p, f233f, q234f, _lit, 49,
                                   36.0).get("raison")))
    with tempfile.TemporaryDirectory() as tmp:
        dep = Path(tmp) / "lecture.json"
        faux = {k: dict(x) for k, x in (m.get("les_bandes") or {}).items()}
        if faux:
            une = sorted(faux)[0]
            faux[une] = {**faux[une], "les_lignes": [x - 2 for x in faux[une]["les_lignes"]]}
        dep.write_text(json.dumps({"les_bandes": faux}))
        mf = _sur(mesurer, dep, p219, p223, p224, p225, q225, q232f, q233f, f233f, q234f, None, 49, 36.0)
        dep.write_text(json.dumps({"les_bandes": m.get("les_bandes") or {}}))
        mj = _sur(mesurer, dep, p219, p223, p224, p225, q225, q232f, q233f, f233f, q234f, None, 49, 36.0)
    v("★★★★ une coupe lue sur d'autres lignes que celles reprises est refusée",
      "pas celle des coupes reprises" in str(mf.get("raison")), str(mf.get("raison")))
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
        par233, par224 = ce_que_233_a_publie(), ce_que_224_a_rendu()
        for nom, par in (("233", par233), ("224", par224)):
            if not par.get("decidable"):
                print(f"indécidable : `{nom}` : {par.get('raison')}")
                return 1
        A = la_grille_de_presence(par233["presence"])
        k1 = les_largeurs()[-1]
        coins = [int(x) for x in par233["coins"]]
        coupes = les_coupes_du_rectangle(A, coins, par224["R"], k1)
        print(f"coupes : {coupes}", flush=True)
        if len(coupes) < 3:
            return 0
        bandes = les_bandes_des_coupes_du_rectangle(coupes, coins[2], coins[3], k1)
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
