"""Sur PHerc0358, l'accord de trois chaînes valide-t-il des surfaces sur les côtés de graine que `324` n'a pas retenus, là où son saut ne pose pas au pas ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UNE CHAÎNE NE SOIT LANCÉE SUR LES ONZE CÔTÉS QUE `324` N'A PAS RETENUS. Ce qui était vu avant d'écrire :
tout ce que `296` à `379` publient, dont `R4-F560` (sur les cinq côtés suivis, l'accord de trois chaînes valide 25 surfaces sur 120, sur
3 côtés, jusqu'à 6 tours de la nappe de départ), `R4-F565` (sur PHercParis4, la même règle ne valide que des surfaces sur le bon tour
publié : 46 sur 46 lues) et la table des côtés de `324` : sur les onze côtés non retenus, la part du plan va de 0 à 0,19, et le pas médian,
là où il existe, de 1,7 à 2,85 pas ; les graines 1, 2 et 5 n'ont aucune part du plan, sauf 0,0002 sur la graine 1, côté plus.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P176`. Sur les cinq côtés suivis, l'accord valide des surfaces sans tracé, et ce qui fait
échouer la graine 8 n'est ni sa nappe ni des sauts à cheval (`R4-F563`, `R4-F564`). Savoir s'il valide ailleurs dit s'il tient comme
méthode, ou seulement sur les côtés que `324` a choisis parce que son saut y pose au pas.

## Ce qui est fait

- **Les chaînes** : les trois chaînes de `373`, la suivie, la compagne et la tierce, lancées sur les seize côtés des huit graines au lieu des
  cinq dont le saut de `324` pose au pas. Rien d'autre ne change : ni la nappe de départ, ni le saut, ni la croissance, ni les graines.
- **Les comptes et les témoins** : ceux de `369` et de `374`, inchangés. Chaque saut compte 0 s'il est nul, 2 s'il est double, 1 sinon ;
  une surface est **validée** si chacune des deux autres chaînes a une surface sur la même feuille au même compte corrigé, et qu'aucune ne la
  contredit.
- **Le contrôle** : sur les cinq côtés suivis, les surfaces, leurs comptes et leurs statuts redonnent exactement ceux de `374`.
- **La règle**, sur les onze côtés neufs : des surfaces validées sur au moins deux côtés, **oui, l'accord valide aussi là où le saut ne
  pose pas au pas** ; sur un seul, **en partie** ; sur aucun, **non**. Indécidable si une lecture échoue ou si le contrôle échoue.

## Les issues

L'issue de la tranche : **sur les onze côtés que `324` n'a pas retenus, l'accord de trois chaînes valide n surfaces sur m, sur c côtés,
jusqu'à t tours de la nappe de départ**, puis ce que dit la règle.

## Rapporté à côté, qui ne décide rien

Côté par côté : les surfaces de chaque chaîne, les sauts comptés 0, 1 et 2, où la tierce est posée, ce que `324` disait du côté, et le
contrôle de `374` là où le vote de `373` désigne une chaîne.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : si une surface validée sur un côté neuf est sur la bonne feuille. La vérité de `379` n'existe que
sur PHercParis4, et là où le saut fait près de deux pas, ou plus de deux pas et demi, trois chaînes qui sautent toutes plusieurs feuilles
d'un coup peuvent s'accorder sur un compte faux.

Usage :
    uv run python src/nappe/laccord_de_trois_chaines_valide_t_il_sur_les_cotes_que_324_na_pas_retenus.py --verifier
    uv run python src/nappe/laccord_de_trois_chaines_valide_t_il_sur_les_cotes_que_324_na_pas_retenus.py \\
        --json docs/mesures/laccord_de_trois_chaines_valide_t_il_sur_les_cotes_que_324_na_pas_retenus.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))
sys.path.insert(0, str(RACINE / "src" / "tracecheck"))

import une_chaine_relancee_a_chaque_tour_descend_elle_plus_loin as m331  # noqa: E402
import deux_chaines_voisines_comptent_elles_les_memes_tours_sur_pherc0358 as m368  # noqa: E402
import le_glissement_se_voit_il_dans_la_chaine_seule as m369  # noqa: E402
import une_troisieme_chaine_dit_elle_laquelle_a_glisse_sur_pherc0358 as m372  # noqa: E402
import trois_chaines_aux_comptes_corriges_designent_elles_celle_qui_a_glisse as m373  # noqa: E402
import quelles_surfaces_laccord_de_trois_chaines_valide_t_il_sur_pherc0358 as m374  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_324_A_PUBLIE = LES_MESURES / "le_saut_qui_croit_pose_t_il_au_pas_sur_les_deux_rouleaux.json"
CE_QUE_374_A_PUBLIE = LES_MESURES / "quelles_surfaces_laccord_de_trois_chaines_valide_t_il_sur_pherc0358.json"
SUIVIE, COMPAGNE, TIERCE = m374.SUIVIE, m374.COMPAGNE, m374.TIERCE
LES_GENRES = (m369.NUL, m369.SIMPLE, m369.DOUBLE)


def les_cotes_de_324(d324: dict) -> tuple[list[tuple], set[tuple]]:
    """Tous les côtés de PHerc0358 que `324` a mesurés, dans son ordre, et ceux dont le saut pose au pas."""
    tous = [(c["le_rang"], c["le_cote"]) for c in d324["les_cotes"]["PHerc0358"]]
    suivis = {(c["le_rang"], c["le_cote"]) for c in d324["les_cotes"]["PHerc0358"] if c["le_saut"]["pose_au_pas"]}
    return tous, suivis


def le_cote(rang: int, nom: str, paires: dict, sauts: dict) -> dict:
    """Le côté tel que `374` le lit, depuis les paires des trois couples et les sauts des trois chaînes : statut de chaque surface, vote de
    `373` et contrôle de `374`."""
    couples = {k: m373.le_couple(p, sauts[k.split("|")[0]], sauts[k.split("|")[1]]) for k, p in paires.items()}
    vote = m372.le_vote(couples)
    c373 = {"le_rang": rang, "le_cote": nom, "le_vote": vote, "les_sauts_de_la_tierce": sauts[TIERCE],
            "les_paires": {k: p for k, p in paires.items() if k != f"{SUIVIE}|{COMPAGNE}"}}
    c368 = {"les_paires": paires[f"{SUIVIE}|{COMPAGNE}"]}
    c369 = {SUIVIE: sauts[SUIVIE], COMPAGNE: sauts[COMPAGNE]}
    return {**m374.le_cote(c373, c368, c369), "les_couples": couples}


def les_statuts(cote: dict) -> list[tuple]:
    return [(s["la_chaine"], s["le_saut"], s["le_compte"], s["le_statut"]) for s in cote["les_surfaces"]]


def le_controle_de_374(cotes: list[dict], d374: dict) -> bool:
    """Sur chaque côté que `374` publie, les surfaces, leurs comptes et leurs statuts sont les mêmes ici."""
    ici = {(c["le_rang"], c["le_cote"]): les_statuts(c) for c in cotes}
    return bool(d374["les_cotes"]) and all(ici.get((c["le_rang"], c["le_cote"])) == les_statuts(c) for c in d374["les_cotes"])


def le_bilan(cotes: list[dict]) -> dict:
    """Le bilan de `374` sur les côtés neufs seulement."""
    neufs = [c for c in cotes if not c["suivi_par_324"]]
    b = m374.le_bilan(neufs)
    b["les_cotes_neufs"] = len(neufs)
    b["les_cotes_valides_nommes"] = [f"{c['le_rang']} {c['le_cote']}" for c in neufs
                                     if any(s["le_statut"] == m374.VALIDEE for s in c["les_surfaces"])]
    return b


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("redonne_374"):
        return {"decidable": False, "lissue": "indécidable : les cinq côtés suivis ne redonnent pas les surfaces de 374"}
    b = d["le_bilan"]
    tete = (f"sur les {b['les_cotes_neufs']} côtés que 324 n'a pas retenus, l'accord de trois chaînes valide {b['validees']} surfaces sur "
            f"{b['les_surfaces']}, sur {b['les_cotes_valides']} côtés")
    if b["validees"]:
        tete += f", jusqu'à {b['le_plus_loin']} tours de la nappe de départ"
    n = b["les_cotes_valides"]
    suite = ("oui, l'accord valide aussi là où le saut ne pose pas au pas" if n >= 2 else "en partie" if n == 1 else "non")
    return {"decidable": True, "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    t0 = time.monotonic()
    d324, d374 = (json.loads(x.read_text()) for x in (CE_QUE_324_A_PUBLIE, CE_QUE_374_A_PUBLIE))
    tous, suivis = les_cotes_de_324(d324)
    par_cote = {(c["le_rang"], c["le_cote"]): c["le_saut"] for c in d324["les_cotes"]["PHerc0358"]}
    m368._LES_PAIRES_DE_CHAINES.clear()
    m369._LES_CHAINES.clear()
    m373._LES_TIERCES.clear()
    chaines, lv0, stats0 = m331.les_chaines_de_0358(chainer=m373.le_chaineur(), cotes=set(tous))
    cotes = []
    for c, pc, nap, pt in zip(chaines, m368._LES_PAIRES_DE_CHAINES, m369._LES_CHAINES, m373._LES_TIERCES):
        surfaces = {SUIVIE: pc["suivie"], COMPAGNE: pc["compagne"], TIERCE: pt["tierce"]}
        sauts = {SUIVIE: m369.les_sauts(nap["la_nappe"], pc["suivie"]), COMPAGNE: m369.les_sauts(nap["la_nappe_compagne"], pc["compagne"]),
                 TIERCE: m369.les_sauts(pt["la_nappe"], pt["tierce"])}
        paires = {"|".join(k): m368.les_paires(surfaces[k[0]], surfaces[k[1]]) for k in m373.LES_COUPLES}
        cote = le_cote(c["le_rang"], c["le_cote"], paires, sauts)
        cle = (c["le_rang"], c["le_cote"])
        cote.update({"suivi_par_324": cle in suivis, "ce_que_324_disait": par_cote[cle],
                     "la_graine_compagne": pc["la_graine_compagne"], "la_graine_tierce": pt["la_graine_tierce"], "ou": pt["ou"],
                     "les_surfaces_par_chaine": {x: len(surfaces[x]) for x in surfaces},
                     "les_points_par_surface": {x: [int(len(u[0])) for u in surfaces[x]] for x in surfaces},
                     "les_sauts": sauts,
                     "les_genres": {x: {g: sum(s["le_genre"] == g for s in sauts[x]) for g in LES_GENRES} for x in sauts},
                     "les_paires": paires})
        cotes.append(cote)
        print(json.dumps({"le_rang": cote["le_rang"], "le_cote": cote["le_cote"], "suivi": cote["suivi_par_324"], "ou": pt["ou"],
                          "surfaces": cote["les_surfaces_par_chaine"],
                          "statuts": {k: sum(s["le_statut"] == k for s in cote["les_surfaces"])
                                      for k in (m374.VALIDEE, m374.EN_PARTIE, m374.CONTREDITE, m374.SEULE)}},
                         ensure_ascii=False), flush=True)
    d = {"la_question": __doc__.splitlines()[0],
         "les_pannes": list(stats0["pannes"]), "la_lecture_de_m7": {k: v for k, v in stats0.items() if k != "pannes"},
         "redonne_374": bool(len(cotes) == len(tous) and le_controle_de_374(cotes, d374)), "les_cotes": cotes}
    d["le_bilan"] = le_bilan(cotes)
    d["le_verdict"] = le_verdict(d)
    d["les_secondes"] = round(time.monotonic() - t0, 1)
    return d


def verifier() -> int:
    import inspect

    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        try:
            res = ok() if callable(ok) else ok
        except Exception as exc:  # noqa: BLE001
            echecs.append(f"{nom} — LEVÉE {type(exc).__name__}: {exc}")
            return
        if not res:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    d324 = {"les_cotes": {"PHerc0358": [{"le_rang": r, "le_cote": n, "le_saut": {"pose_au_pas": r == 2}}
                                        for r in (1, 2) for n in ("plus", "moins")]}}
    v("★★★★ les côtés de 324 : tous, dans son ordre, et ceux qui posent au pas",
      lambda: les_cotes_de_324(d324) == ([(1, "plus"), (1, "moins"), (2, "plus"), (2, "moins")], {(2, "plus"), (2, "moins")}))
    v("★★★★ la chaîne de 331 garde ses côtés par défaut, et prend ceux qu'on lui donne",
      lambda: inspect.signature(m331.les_chaines_de_0358).parameters["cotes"].default is None
      and "if cotes is None" in inspect.getsource(m331.les_chaines_de_0358))

    p = lambda h, k, m: {"le_saut_suivi": h, "le_saut_compagnon": k, "meme_feuille": m}  # noqa: E731
    sa = lambda *cs: [{"le_saut": h, "le_compte_corrige": w} for h, w in enumerate(cs, 1)]  # noqa: E731
    paires = {f"{SUIVIE}|{COMPAGNE}": [p(1, 1, True), p(2, 2, True)], f"{SUIVIE}|{TIERCE}": [p(1, 1, True), p(2, 2, False)],
              f"{COMPAGNE}|{TIERCE}": [p(1, 1, True)]}
    sauts = {SUIVIE: sa(1, 2), COMPAGNE: sa(1, 2), TIERCE: sa(1, 2)}
    c = le_cote(3, "plus", paires, sauts)
    st = {(s["la_chaine"], s["le_saut"]): s["le_statut"] for s in c["les_surfaces"]}
    v("★★★★ le côté lu comme 374 : validée par les deux autres, contredite par une autre feuille au même compte",
      st[(SUIVIE, 1)] == m374.VALIDEE and st[(TIERCE, 1)] == m374.VALIDEE and st[(SUIVIE, 2)] == m374.CONTREDITE
      and st[(COMPAGNE, 2)] == m374.EN_PARTIE and (c["le_rang"], c["le_cote"]) == (3, "plus"), str(st))
    v("★★★ le côté porte le vote de 373, le contrôle de 374 et ses trois couples",
      "le_vote" in c and "le_controle" in c and sorted(c["les_couples"]) == sorted(paires))

    s_ = lambda st_: {"la_chaine": SUIVIE, "le_saut": 1, "le_compte": 1, "le_statut": st_}  # noqa: E731
    pub = {"les_cotes": [{"le_rang": 6, "le_cote": "moins", "les_surfaces": [s_(m374.VALIDEE)]}]}
    ici = [{"le_rang": 5, "le_cote": "plus", "les_surfaces": [s_(m374.SEULE)]}, {"le_rang": 6, "le_cote": "moins", "les_surfaces": [s_(m374.VALIDEE)]}]
    v("★★★★ le contrôle : les côtés publiés par 374 sont redonnés, compte et statut de chaque surface",
      lambda: le_controle_de_374(ici, pub)
      and not le_controle_de_374([ici[0], {**ici[1], "les_surfaces": [s_(m374.CONTREDITE)]}], pub)
      and not le_controle_de_374([ici[0], {**ici[1], "les_surfaces": [{**s_(m374.VALIDEE), "le_compte": 2}]}], pub)
      and not le_controle_de_374([ici[0]], pub) and not le_controle_de_374(ici, {"les_cotes": []}))

    cc = lambda r, n, suivi, sts: {"le_rang": r, "le_cote": n, "suivi_par_324": suivi, "le_controle": None,  # noqa: E731
                                   "les_surfaces": [{"le_statut": x, "le_compte": w} for x, w in sts]}
    b = le_bilan([cc(6, "moins", True, [(m374.VALIDEE, 6)]), cc(3, "plus", False, [(m374.VALIDEE, 2), (m374.SEULE, 3)]),
                  cc(4, "moins", False, [(m374.CONTREDITE, 1)])])
    v("★★★★ le bilan ne compte que les côtés neufs : la surface validée d'un côté suivi n'y entre pas",
      (b["les_cotes_neufs"], b["les_surfaces"], b["validees"], b["les_cotes_valides"], b["le_plus_loin"]) == (2, 3, 1, 1, 2)
      and b["les_cotes_valides_nommes"] == ["3 plus"], str(b))

    def d_(n, ok=True, pannes=()):
        return {"redonne_374": ok, "les_pannes": list(pannes),
                "le_bilan": {"les_cotes_neufs": 11, "validees": 4, "les_surfaces": 90, "les_cotes_valides": n, "le_plus_loin": 3}}
    v("★★★★ la règle : deux côtés neufs, oui ; un, en partie ; aucun, non",
      le_verdict(d_(2))["lissue"].endswith("ne pose pas au pas") and le_verdict(d_(1))["lissue"].endswith("; en partie")
      and le_verdict(d_(0))["lissue"].endswith("; non") and "jusqu'à 3 tours" in le_verdict(d_(2))["lissue"])
    v("★★★ indécidable sans le contrôle de 374, ou sur une lecture en panne",
      not le_verdict(d_(2, ok=False))["decidable"] and not le_verdict(d_(2, pannes=("x",)))["decidable"]
      and le_verdict(d_(2))["decidable"])

    for e_ in echecs:
        print(f"  ÉCHEC {e_}")
    print(f"{Path(__file__).name}   {'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    d = mesurer()
    texte = json.dumps(d, ensure_ascii=False, indent=1)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(texte + "\n")
    print(json.dumps(d["le_verdict"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
