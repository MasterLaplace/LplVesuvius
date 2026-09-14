#!/usr/bin/env python3
"""Lire la cause LÀ OÙ LE BRUIT S'ANNULE — deux mécanismes, un seul exact.

⭐⭐⭐⭐ POURQUOI CE FICHIER. `144` établit qu'une mémoire de cap peut se LIRE au lieu de se poser,
et que la règle lit exactement ce qu'elle prétend lire tant qu'il n'y a pas de bruit — **0,0000** sur
une spirale nue ou écrasée, **0,8603** sur un froissement de 100 µm. Elle cesse de séparer les causes
dès que le bruit couvre la rotation : à bruit 16 l'écart entre matières (0,0891) tombe sous la
dispersion dans une matière (0,1197). ⚠ Mais l'ORDRE des matières survit à tous les bruits — ce que
le bruit détruit est la séparation, pas le classement. La règle est donc bonne, et c'est son rapport
signal sur bruit qui manque.

⭐⭐⭐ DEUX MÉCANISMES LE RÉPARENT EN PRINCIPE, ET UN SEUL EST EXACT.

Le **bloc** somme les incréments par paquets de `k` : un bruit indépendant y croît comme `√k` et une
cause cohérente comme `k`, donc le rapport s'améliore. ⚠⚠ Mais il est borné par la cause elle-même :
un froissement de période `p` pas s'ANNULE dans un bloc de `p`, et il ne reste alors que
l'enroulement, qui est cohérent — la règle lirait « persistant » sur une matière froissée. Ici la
période vaut **393,6 / 98,4 = 4 pas**, donc un bloc de 4 est le piège, et il est mesuré comme tel.

La **correction du plancher** retranche une quantité qui se calcule exactement. Pour `n` incréments
indépendants de moyenne nulle, `E|somme| = sigma·racine(2n/pi)` et `E[somme des |.|] =
n·sigma·racine(2/pi)`, donc la cohérence attendue d'un bruit PUR vaut **exactement `1/racine(n)`**.
Une cohérence qui vaut ce plancher ne dit rien ; la retrancher et renormaliser rend une lecture qui
vaut zéro sur du bruit pur et un sur une rotation parfaite. Aucune constante n'y est ajustée.

⚠⚠ LE TÉMOIN EST INTERNE : la variante « bloc 1, sans correction » EST la règle de `144`, et la
mesure doit la reproduire à l'identique. Si elle ne le fait pas, c'est le protocole qui a bougé et
aucune comparaison ne vaut.

⚠ La fenêtre est fixée à **32** — la seule que `144` mesure comme séparant encore à bruit 8. Elle est
donc choisie par une mesure antérieure, pas par moi.

Usage :
    uv run python src/nappe/lire_la_cause_sous_le_bruit.py --verifier
    uv run python src/nappe/lire_la_cause_sous_le_bruit.py \\
        --json docs/mesures/lire_la_cause_sous_le_bruit.json
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

from la_pince_tient_elle_la_feuille import (BRAS, LARGEUR_DE_REFERENCE,  # noqa: E402
                                            MATIERES, _resumer_un_bras, une_case)
from un_cap_qui_lit_la_cause import le_discriminant  # noqa: E402

# ⚠ Fixée par `144`, pas par moi : la seule fenêtre qui séparait encore à bruit 8.
FENETRE = 32
# ⚠ (bloc, correction). Le bloc de 4 est le PIÈGE : c'est la période du froissement, donc il doit
# détruire la lecture — un balayage sans son piège ne borne rien.
VARIANTES = ((1, False), (1, True), (2, False), (2, True), (4, True))
BRUITS = (0.0, 8.0, 16.0)
DEPARTS = 12
TOURS = 1.0
LE_PRECEDENT = RACINE / "docs" / "mesures" / "un_cap_qui_lit_la_cause.json"


def _nom_de_variante(bloc: int, corrige: bool) -> str:
    return f"bloc {int(bloc)}" + (", plancher retranché" if corrige else ", brut")


def sur_la_grille(matieres=MATIERES, bruits=BRUITS, variantes=VARIANTES, fenetre: int = FENETRE,
                  departs: int = DEPARTS, tours: float = TOURS) -> dict:
    """La grille de `144`, à fenêtre fixée, pour chaque variante de lecture."""
    cases = []
    for m in matieres:
        for b in bruits:
            for bloc, corrige in variantes:
                c = une_case(m, b, LARGEUR_DE_REFERENCE, departs, tours=tours,
                             fenetre_du_cap=int(fenetre), bloc_du_cap=int(bloc),
                             corrige_le_bruit=bool(corrige))
                c["variante"] = _nom_de_variante(bloc, corrige)
                cases.append(c)
    return {"departs": int(departs), "tours": float(tours), "fenetre": int(fenetre),
            "bruits": [float(b) for b in bruits],
            "variantes": [{"bloc": int(b), "corrige": bool(c), "nom": _nom_de_variante(b, c)}
                          for b, c in variantes],
            "largeur_en_pas": float(LARGEUR_DE_REFERENCE), "cases": cases}


def _filtre(bloc: int, corrige: bool):
    def f(c):
        return c["bloc_du_cap"] == int(bloc) and bool(c["corrige_le_bruit"]) is bool(corrige)
    return f


def par_variante(grille: dict) -> dict:
    """Pour chaque variante : les réussites, et à quels bruits la lecture sépare encore.

    ⚠ Le calcul de « sépare » n'est pas réécrit ici : c'est celui de `144`, appelé avec un filtre
    sur la variante au lieu d'un filtre sur la fenêtre. Deux écritures de « l'écart entre dépasse la
    dispersion dans » seraient deux réponses à une même question.
    """
    out = []
    for v in grille["variantes"]:
        cases = [c for c in grille["cases"] if _filtre(v["bloc"], v["corrige"])(c)]
        if not cases:
            continue
        d = le_discriminant(grille, _filtre(v["bloc"], v["corrige"]))["par_bruit"]
        bloc = {**v, "cases": len(cases),
                "bruits_ou_elle_separe": [x["bruit"] for x in d if x["la_lecture_separe"]],
                "par_bruit": [{"bruit": x["bruit"],
                               "ecart_entre_matieres": x["ecart_entre_matieres"],
                               "dispersion_dans_une_matiere": x["dispersion_dans_une_matiere"],
                               "la_lecture_separe": x["la_lecture_separe"],
                               "memoire_la_plus_basse": x["memoire_la_plus_basse"],
                               "memoire_la_plus_haute": x["memoire_la_plus_haute"],
                               "par_matiere": x["par_matiere"]} for x in d]}
        for nom in BRAS:
            bloc[nom] = {
                "reussites": int(sum(c["bras"][nom].get("reussites") or 0 for c in cases)),
                "memes_feuilles": int(sum(c["bras"][nom].get("memes_feuilles") or 0
                                          for c in cases)),
                "tours_boucles": int(sum(c["bras"][nom].get("tours_boucles") or 0
                                         for c in cases))}
        out.append(bloc)
    return {"par_variante": out}


def le_temoin_interne(grille: dict, precedent: dict | None) -> dict:
    """La variante « bloc 1, brut » EST la règle de `144` : la mesure doit la reproduire.

    ⚠⚠ Sans ce contrôle, une différence de protocole passerait pour un effet de la correction. On
    compare donc les réussites de cette variante à celles que `144` publie à la même fenêtre.
    """
    ref = None
    if precedent:
        for x in precedent.get("juger", {}).get("contre_le_fixe", {}).get("par_fenetre", []):
            if int(x["fenetre"]) == int(grille["fenetre"]):
                ref = x
                break
    cases = [c for c in grille["cases"] if _filtre(1, False)(c)]
    if ref is None or not cases:
        return {"decidable": False,
                "raison": "la mesure de `144` est absente à cette fenêtre, le témoin manque"}
    out = {"decidable": True, "fenetre": int(grille["fenetre"])}
    for nom in BRAS:
        ici = int(sum(c["bras"][nom].get("reussites") or 0 for c in cases))
        out[nom] = {"ici": ici, "dans_144": int(ref[nom]["reussites"]),
                    "identique": bool(ici == int(ref[nom]["reussites"]))}
    out["le_protocole_est_le_meme"] = all(out[n]["identique"] for n in BRAS)
    return out


def juger(grille: dict, precedent: dict | None) -> dict:
    if not grille.get("cases"):
        return {"decidable": False, "raison": "aucune case à juger"}
    pv = par_variante(grille)["par_variante"]
    out = {"decidable": True, "par_variante": pv,
           "le_temoin_interne": le_temoin_interne(grille, precedent)}
    # ⭐ Le fait qui décide : une variante sépare-t-elle à un bruit où la règle brute échoue ?
    brute = next((x for x in pv if x["bloc"] == 1 and not x["corrige"]), None)
    if brute is not None:
        deja = set(brute["bruits_ou_elle_separe"])
        gains = [{"nom": x["nom"], "bloc": x["bloc"], "corrige": x["corrige"],
                  "bruits_gagnes": sorted(set(x["bruits_ou_elle_separe"]) - deja),
                  "bruits_perdus": sorted(deja - set(x["bruits_ou_elle_separe"])),
                  "reussites_de_la_pince": x["la pince"]["reussites"]}
                 for x in pv if not (x["bloc"] == 1 and not x["corrige"])]
        out["contre_la_regle_brute"] = {
            "bruits_ou_la_brute_separe": sorted(deja),
            "reussites_de_la_brute": brute["la pince"]["reussites"],
            "par_variante": gains,
            "une_variante_va_plus_loin": bool(any(g["bruits_gagnes"] for g in gains))}
    # ⚠ Le piège est nommé d'avance : un bloc qui atteint la période du froissement doit DÉTRUIRE la
    # lecture. S'il ne la détruit pas, c'est que la période n'est pas où je la crois.
    piege = next((x for x in pv if x["bloc"] == 4), None)
    if piege is not None and brute is not None:
        out["le_piege_du_bloc"] = {
            "nom": piege["nom"],
            "bruits_ou_elle_separe": piege["bruits_ou_elle_separe"],
            "elle_perd_ce_que_la_brute_avait": sorted(
                set(brute["bruits_ou_elle_separe"]) - set(piege["bruits_ou_elle_separe"])),
            "le_piege_se_referme": bool(
                set(piege["bruits_ou_elle_separe"]) < set(brute["bruits_ou_elle_separe"]))}
    return out


def mesurer(matieres=MATIERES, bruits=BRUITS, variantes=VARIANTES, fenetre: int = FENETRE,
            departs: int = DEPARTS, tours: float = TOURS, precedent: Path = LE_PRECEDENT) -> dict:
    grille = sur_la_grille(matieres, bruits, variantes, fenetre, departs, tours)
    ref = json.loads(Path(precedent).read_text()) if Path(precedent).exists() else None
    return {"sur_la_grille": grille,
            "le_precedent": str(Path(precedent).name) if ref else None,
            "juger": juger(grille, ref)}


def reagreger(r: dict, precedent: Path = LE_PRECEDENT) -> dict:
    """Recalcule les résumés et le verdict depuis les suivis rangés — sans remarcher."""
    for c in r["sur_la_grille"]["cases"]:
        for nom in BRAS:
            suivis = c["bras"][nom]["suivis"]
            c["bras"][nom] = {"suivis": suivis, **_resumer_un_bras(suivis, int(c["departs"]))}
    ref = json.loads(Path(precedent).read_text()) if Path(precedent).exists() else None
    r["juger"] = juger(r["sur_la_grille"], ref)
    return r


def afficher(r: dict) -> None:
    if "message" in r:
        print(f"⚠ {r['message']}")
        return
    j = r["juger"]
    if not j.get("decidable"):
        print(f"⚠ {j.get('raison', 'indécidable')}")
        return
    g = r["sur_la_grille"]
    print(f"lire la cause sous le bruit — fenêtre {g['fenetre']} (celle que `144` mesure comme la "
          f"seule qui sépare encore à bruit 8), {g['departs']} départs par case, un tour.")
    t = j["le_temoin_interne"]
    if t.get("decidable"):
        marque = "★" if t["le_protocole_est_le_meme"] else "✗"
        print(f"\n   {marque} témoin interne — « bloc 1, brut » doit reproduire `144` : "
              + " · ".join(f"{n} {t[n]['ici']} contre {t[n]['dans_144']}" for n in BRAS))
    else:
        print(f"\n   ⚠ {t.get('raison')}")
    print(f"\n   {'variante':>26} | {'réussites (pince)':>18} | bruits où la lecture sépare")
    for x in j["par_variante"]:
        print(f"   {x['nom']:>26} | {x['la pince']['reussites']:>18d} | "
              f"{x['bruits_ou_elle_separe']}")
    print(f"\n   l'écart entre matières contre la dispersion dans une, par variante :")
    for x in j["par_variante"]:
        print(f"     {x['nom']:>26} : " + " · ".join(
            f"bruit {y['bruit']:g} {y['ecart_entre_matieres']:.4f}/"
            f"{y['dispersion_dans_une_matiere']:.4f}"
            f"{'✓' if y['la_lecture_separe'] else '✗'}" for y in x["par_bruit"]))
    c = j.get("contre_la_regle_brute")
    if c is not None:
        print(f"\n   la règle brute de `144` sépare aux bruits {c['bruits_ou_la_brute_separe']} "
              f"pour {c['reussites_de_la_brute']} réussites :")
        for x in c["par_variante"]:
            print(f"     {x['nom']:>26} : {x['reussites_de_la_pince']:>3d} réussites · gagne "
                  f"{x['bruits_gagnes'] or '—'} · perd {x['bruits_perdus'] or '—'}")
        marque = "★★★★" if c["une_variante_va_plus_loin"] else "✗"
        print(f"\n{marque} une variante lit la cause à un bruit où la règle brute échoue : "
              f"{c['une_variante_va_plus_loin']}")
    p_ = j.get("le_piege_du_bloc")
    if p_ is not None:
        marque = "★" if p_["le_piege_se_referme"] else "⚠"
        print(f"{marque} le piège du bloc se referme comme annoncé : {p_['le_piege_se_referme']} — "
              f"« {p_['nom']} » sépare aux bruits {p_['bruits_ou_elle_separe']} et perd "
              f"{p_['elle_perd_ce_que_la_brute_avait'] or '—'}")


def verifier() -> int:
    echecs = controles = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    def case(bloc, corrige, bruit, nom, mems, r=6):
        return {"ecrasement": 0.0, "amplitude_um": 0.0, "bruit": bruit, "nom": nom,
                "departs": len(mems), "fenetre_du_cap": FENETRE, "bloc_du_cap": bloc,
                "corrige_le_bruit": corrige, "variante": _nom_de_variante(bloc, corrige),
                "bras": {b: {"reussites": r, "memes_feuilles": r, "tours_boucles": r,
                             "suivis": [{"decidable": True, "memoire_mediane": m}
                                        for m in mems]} for b in BRAS}}

    v("une variante porte son bloc ET sa correction dans son nom",
      _nom_de_variante(2, True) != _nom_de_variante(2, False)
      and _nom_de_variante(2, True) != _nom_de_variante(4, True))
    v("le filtre ne retient que sa variante",
      _filtre(1, False)(case(1, False, 0.0, "x", [0.1]))
      and not _filtre(1, True)(case(1, False, 0.0, "x", [0.1]))
      and not _filtre(2, False)(case(1, False, 0.0, "x", [0.1])))

    # ---- ⭐ le calcul de « sépare » n'est pas réécrit : c'est celui de `144`
    grille = {"fenetre": FENETRE, "departs": 2,
              "variantes": [{"bloc": 1, "corrige": False, "nom": _nom_de_variante(1, False)},
                            {"bloc": 2, "corrige": True, "nom": _nom_de_variante(2, True)}],
              "cases": [case(1, False, 0.0, "A", [0.10, 0.12]),
                        case(1, False, 0.0, "B", [0.70, 0.72]),
                        case(2, True, 0.0, "A", [0.40, 0.90]),
                        case(2, True, 0.0, "B", [0.42, 0.92])]}
    pv = par_variante(grille)["par_variante"]
    direct = le_discriminant(grille, _filtre(1, False))["par_bruit"][0]
    v("⭐ « sépare » est celui de `144`, appelé avec un filtre — jamais réécrit",
      pv[0]["par_bruit"][0]["ecart_entre_matieres"] == direct["ecart_entre_matieres"]
      and pv[0]["par_bruit"][0]["la_lecture_separe"] == direct["la_lecture_separe"])
    v("⭐⭐ une variante qui sépare et une qui ne sépare pas sont distinguées",
      pv[0]["bruits_ou_elle_separe"] == [0.0] and pv[1]["bruits_ou_elle_separe"] == [],
      f"{pv[0]['bruits_ou_elle_separe']} contre {pv[1]['bruits_ou_elle_separe']}")
    v("les réussites sont sommées par variante",
      pv[0]["la pince"]["reussites"] == 12 and pv[1]["la pince"]["reussites"] == 12)

    # ---- ⭐⭐ le témoin interne
    ref = {"juger": {"contre_le_fixe": {"par_fenetre": [
        {"fenetre": FENETRE, **{n: {"reussites": 12} for n in BRAS}}]}}}
    t = le_temoin_interne(grille, ref)
    v("⭐⭐ le témoin interne compare « bloc 1, brut » à ce que `144` publie",
      t["decidable"] and t["le_protocole_est_le_meme"] is True,
      f"{t['la pince']}")
    faux = {"juger": {"contre_le_fixe": {"par_fenetre": [
        {"fenetre": FENETRE, **{n: {"reussites": 99} for n in BRAS}}]}}}
    v("⭐⭐ ... et il DIT quand le protocole a bougé",
      le_temoin_interne(grille, faux)["le_protocole_est_le_meme"] is False,
      "sinon une différence de protocole passerait pour un effet de la correction")
    v("sans `144`, le témoin est indécidable et le dit",
      not le_temoin_interne(grille, None)["decidable"])
    v("... et à une fenêtre que `144` n'a pas mesurée non plus",
      not le_temoin_interne({**grille, "fenetre": 999}, ref)["decidable"])

    # ---- ⭐⭐ le jugement : les gains, et le piège
    # ⚠⚠ La fixture se tient FRANCHEMENT de part et d'autre de la limite. Ma première version
    # posait un écart entre matières EXACTEMENT égal à la dispersion interne : elle ne testait plus
    # la règle mais l'ordre des dernières décimales flottantes, et elle répondait au hasard.
    def grille_de(variantes, sepa):
        cases = []
        for bloc, corr in variantes:
            for bruit in (0.0, 8.0):
                ecart = 0.9 if (bloc, corr, bruit) in sepa else 0.002
                cases.append(case(bloc, corr, bruit, "A", [0.10, 0.11]))
                cases.append(case(bloc, corr, bruit, "B", [0.10 + ecart, 0.11 + ecart]))
        return {"fenetre": FENETRE, "departs": 2,
                "variantes": [{"bloc": b, "corrige": c, "nom": _nom_de_variante(b, c)}
                              for b, c in variantes], "cases": cases}

    g1 = grille_de([(1, False), (1, True)], {(1, False, 0.0), (1, True, 0.0), (1, True, 8.0)})
    j1 = juger(g1, ref)
    v("⭐⭐ une variante qui sépare à un bruit où la brute échoue est dite le faire",
      j1["contre_la_regle_brute"]["une_variante_va_plus_loin"] is True
      and j1["contre_la_regle_brute"]["par_variante"][0]["bruits_gagnes"] == [8.0])
    g2 = grille_de([(1, False), (1, True)], {(1, False, 0.0), (1, True, 0.0)})
    v("... et une qui n'apporte rien est dite ne rien apporter",
      juger(g2, ref)["contre_la_regle_brute"]["une_variante_va_plus_loin"] is False)
    g3 = grille_de([(1, False), (4, True)], {(1, False, 0.0), (1, False, 8.0), (4, True, 0.0)})
    j3 = juger(g3, ref)
    v("⭐⭐ le piège du bloc se referme quand il PERD ce que la brute avait",
      j3["le_piege_du_bloc"]["le_piege_se_referme"] is True
      and j3["le_piege_du_bloc"]["elle_perd_ce_que_la_brute_avait"] == [8.0])
    g4 = grille_de([(1, False), (4, True)],
                   {(1, False, 0.0), (4, True, 0.0), (4, True, 8.0)})
    v("... et il ne se referme pas quand le bloc garde tout",
      juger(g4, ref)["le_piege_du_bloc"]["le_piege_se_referme"] is False,
      "un piège qui ne se referme jamais ne borne rien, et il faut le dire")
    v("un jugement sans case est indécidable", not juger({"cases": []}, ref)["decidable"])

    # ---- ⭐ la règle elle-même, de bout en bout
    vraie = une_case((0.0, 42.4), 8.0, LARGEUR_DE_REFERENCE, departs=1, tours=0.05,
                     fenetre_du_cap=FENETRE, bloc_du_cap=1, corrige_le_bruit=True)
    brute = une_case((0.0, 42.4), 8.0, LARGEUR_DE_REFERENCE, departs=1, tours=0.05,
                     fenetre_du_cap=FENETRE, bloc_du_cap=1, corrige_le_bruit=False)
    mv = [x["memoire_mediane"] for x in vraie["bras"]["la pince"]["suivis"] if x.get("decidable")]
    mb = [x["memoire_mediane"] for x in brute["bras"]["la pince"]["suivis"] if x.get("decidable")]
    v("⭐⭐ sur une vraie matière bruitée, retrancher le plancher monte la mémoire lue",
      bool(mv) and bool(mb) and float(np.median(mv)) > float(np.median(mb)),
      f"corrigée {float(np.median(mv)):.4f} contre brute {float(np.median(mb)):.4f}")
    v("... et la variante voyage jusque dans la case",
      vraie["bloc_du_cap"] == 1 and vraie["corrige_le_bruit"] is True)

    # ---- réagréger
    petit = {"sur_la_grille": {"cases": [vraie], "departs": 1, "tours": 0.05, "fenetre": FENETRE,
                               "bruits": [8.0], "largeur_en_pas": LARGEUR_DE_REFERENCE,
                               "variantes": [{"bloc": 1, "corrige": True,
                                              "nom": _nom_de_variante(1, True)}]}}
    petit["juger"] = juger(petit["sur_la_grille"], None)
    v("⭐ réagréger depuis les suivis rangés rend le MÊME verdict, sans remarcher",
      reagreger(json.loads(json.dumps(petit)), Path("/inexistant.json"))["juger"]
      == petit["juger"])

    import contextlib  # noqa: PLC0415
    import io  # noqa: PLC0415

    tampon = io.StringIO()
    with contextlib.redirect_stdout(tampon):
        afficher({"message": "précédent absent"})
    v("un message est dit, jamais dessiné", "⚠" in tampon.getvalue())

    print(f"\n{'ALL PASS' if echecs == 0 else 'ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path, default=None)
    p.add_argument("--departs", type=int, default=DEPARTS)
    p.add_argument("--tours", type=float, default=TOURS)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--reagreger", type=Path, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if a.reagreger is not None:
        r = reagreger(json.loads(a.reagreger.read_text()))
        afficher(r)
        a.reagreger.write_text(json.dumps(r, ensure_ascii=False, indent=2))
        print(f"\n→ {a.reagreger}")
        return 0
    r = mesurer(departs=a.departs, tours=a.tours)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=2))
        print(f"\n→ {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
