"""Ce que la seconde mâchoire achète encore, une fois qu'un appui peut être rejeté.

⭐⭐⭐⭐ POURQUOI CE FICHIER, ET POURQUOI IL NE REMARCHE RIEN. `156` paie une grille de soixante cases
et en publie le verdict pour la PINCE. Les trois bras y sont pourtant mesurés sur le MÊME départ, et
la mâchoire SEULE munie du rejet y rend **128** réussites pour **20** arrêts — le plus haut compte de
la campagne, contre 123 et 35 pour la pince. Un total qui mène de cinq demande d'être apparié avant
d'être lu, et `apparie` de `147` ne sait pas le faire : il compare le MÊME bras sous deux règles.

⭐⭐⭐ ET LA QUESTION EST CELLE DE `142`, REPOSÉE SOUS LE NOUVEL INSTRUMENT. `142` décompose ce que la
pince achète : la seconde mâchoire divise la dérive par **18,178** parce qu'elle MESURE l'épaisseur
là où une seule ne peut que la supposer, et le refus de changer d'interstice la divise par **1,586**
de plus. Les deux ingrédients sont séparables, et rien n'a redemandé ce qu'ils valent depuis.

⚠⚠ ET LE VERDICT NE PEUT PAS ÊTRE UN COMPTE DE RÉUSSITES SEUL. Une mâchoire seule garde une fenêtre
NOMINALE — c'est l'infirmité exacte que la pince existe pour réparer — donc un verdict qui ne
regarderait que les réussites couronnerait un bras qui réussit en ignorant ce que la pince tient. La
DÉRIVE, et surtout sa QUEUE, se publie à côté.

Usage :
    uv run python src/nappe/ce_que_la_seconde_machoire_achete_encore.py --verifier
    uv run python src/nappe/ce_que_la_seconde_machoire_achete_encore.py \\
        --json docs/mesures/ce_que_la_seconde_machoire_achete_encore.json
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))

from la_pince_tient_elle_la_feuille import BRAS, une_reussite  # noqa: E402

LA_GRILLE = RACINE / "docs" / "mesures" / "la_croix_marche_t_elle_le_tour.json"
# ⚠ La matière que `140` retient comme celle du rouleau, NOMMÉE pour que la barre soit lue et non
# choisie après coup.
LA_MATIERE_DE_140 = (0.2782, 100.0)
LE_BRAS_DE_REFERENCE = "la pince"


def _filtre(en_croix: bool, rejeter: bool):
    """⚠ Une clé absente vaut FAUX : un record d'avant `156` ne connaît pas ces deux mots."""
    def f(c):
        return (bool(c.get("en_croix", False)) is bool(en_croix)
                and bool(c.get("rejeter", False)) is bool(rejeter))
    return f


def apparie_les_bras(grille: dict, filtre, bras_a: str, bras_b: str) -> dict:
    """Le MÊME départ sous deux BRAS : ce qui est gagné, ce qui est perdu, et le solde.

    ⭐⭐⭐⭐ `apparie` de `147` compare le même bras sous deux RÈGLES ; ici la règle est fixe et c'est
    le BRAS qui change. La clé est la même — matière, bruit, angle de départ — parce que
    `les_trois_bras` fait partir les trois du MÊME point, exactement pour que cette comparaison soit
    lisible.

    ⚠⚠ Un départ où le bras ne se pose pas compte comme une NON-réussite et non comme une donnée
    absente : refuser de se poser est une façon d'échouer un transfert, et la sauter ferait passer
    un bras qui refuse beaucoup pour un bras qui réussit souvent.

    ⚠ « Réussite » n'est pas réécrit : c'est `une_reussite` du module partagé, le prédicat JOINT.
    """
    def par_depart(bras):
        out = {}
        for c in grille["cases"]:
            if not filtre(c):
                continue
            for x in c["bras"][bras]["suivis"]:
                out[(c["nom"], float(c["bruit"]), float(x.get("depart_deg", -1.0)))] = x
        return out

    a_, b_ = par_depart(bras_a), par_depart(bras_b)
    communs = sorted(set(a_) & set(b_))
    if not communs:
        return {"decidable": False, "raison": "aucun départ commun aux deux bras"}
    gains = [k for k in communs if une_reussite(a_[k]) and not une_reussite(b_[k])]
    pertes = [k for k in communs if une_reussite(b_[k]) and not une_reussite(a_[k])]
    return {"decidable": True, "bras": bras_a, "contre": bras_b, "paires": len(communs),
            "gains": len(gains), "pertes": len(pertes),
            "solde": len(gains) - len(pertes), "il_ne_perd_rien": not pertes,
            "matieres_gagnees": sorted({k[0] for k in gains}),
            "matieres_perdues": sorted({k[0] for k in pertes})}


def _marches(grille: dict, filtre, bras: str) -> list[dict]:
    return [x for c in grille["cases"] if filtre(c) for x in c["bras"][bras]["suivis"]]


def la_derive_et_le_prix(grille: dict, filtre, bras: str) -> dict:
    """La dérive, sa QUEUE, le prix et le refus — tout ce qu'un compte de réussites ne dit pas.

    ⚠⚠ LA QUEUE EST LA QUANTITÉ QUI DÉCIDE. Une dérive médiane sépare mal deux bras qui réussissent
    presque toujours ; ce qui les sépare est ce qu'ils font quand ils ratent, et `142` a construit la
    seconde mâchoire précisément pour ça.

    ⚠ Une marche indécidable est SAUTÉE ici et COMPTÉE à part : elle n'a pas dérivé, elle n'a pas
    marché — c'est l'appariement, au-dessus, qui la compte comme un échec.
    """
    xs = _marches(grille, filtre, bras)
    dec = [x for x in xs if x.get("decidable")]
    if not dec:
        return {"decidable": False, "raison": f"aucune marche décidable pour « {bras} »"}
    der = [abs(float(x["derive_en_feuilles"])) for x in dec]
    ep = [float(x["epaisseur_um"]) for x in dec if x.get("epaisseur_um") is not None]
    return {"decidable": True, "bras": bras, "marches": len(xs), "decidables": len(dec),
            "reussites": int(sum(1 for x in dec if une_reussite(x))),
            "arrets": int(sum(1 for x in dec
                              if x.get("fin") == "la pince ne peut plus avancer")),
            "derive_mediane": round(float(statistics.median(der)), 4),
            # ⚠⚠ UN MAXIMUM EST UNE SEULE MARCHE, donc il ne porte pas un verdict à lui seul : le
            # p90 est publié à côté, et c'est leur ACCORD qui autorise à parler de « queue ». Le p90
            # est une statistique d'ORDRE exacte — la valeur au rang ⌈0,9·n⌉ — et non une
            # interpolation, pour qu'il reste un nombre qu'une marche a réellement rendu.
            "derive_p90": round(float(sorted(der)[min(len(der) - 1,
                                                      max(0, -(-9 * len(der) // 10) - 1))]), 3),
            "derive_max": round(float(max(der)), 3),
            "lectures_medianes": int(statistics.median([int(x["lectures"]) for x in dec])),
            # ⚠ Le refus de la CONTRAINTE, et il est publié même quand il vaut zéro : un bras libre
            # n'en a pas, et c'est ce zéro qui rend le chiffre de la pince lisible.
            "refus": int(sum(int(x["refus"]) for x in dec)),
            "marches_qui_refusent": int(sum(1 for x in dec if int(x["refus"]) > 0)),
            "epaisseur_mediane_um": (round(float(statistics.median(ep)), 2) if ep else None),
            "part_du_tour_mediane": round(
                float(statistics.median([float(x["part_du_tour"]) for x in dec])), 4)}


def par_instrument(grille: dict) -> dict:
    """Pour chacun des quatre instruments de `156` : ce que chaque bras fait, et ce qu'il échange."""
    out = []
    for v in grille["variantes"]:
        f = _filtre(v["en_croix"], v["rejeter"])
        if not [c for c in grille["cases"] if f(c)]:
            continue
        bloc = {**v, "par_bras": [la_derive_et_le_prix(grille, f, b) for b in BRAS],
                "apparie": [apparie_les_bras(grille, f, b, LE_BRAS_DE_REFERENCE)
                            for b in BRAS if b != LE_BRAS_DE_REFERENCE]}
        out.append(bloc)
    return {"par_instrument": out}


def sur_la_matiere_du_rouleau(grille: dict) -> dict:
    """La matière où personne n'a jamais réussi : jusqu'OÙ chaque bras va, faute de réussir.

    ⭐⭐⭐ UN COMPTE DE RÉUSSITES NUL NE DIT PAS SI LE MUR A BOUGÉ. La part du tour parcourue est la
    seule mesure qui sépare « elle échoue au même endroit » de « elle échoue cinq fois plus loin »,
    et les deux ne demandent pas la même suite.
    """
    out = []
    for v in grille["variantes"]:
        def f(c, v=v):
            return (_filtre(v["en_croix"], v["rejeter"])(c)
                    and (round(float(c["ecrasement"]), 4), round(float(c["amplitude_um"]), 1))
                    == (round(LA_MATIERE_DE_140[0], 4), round(LA_MATIERE_DE_140[1], 1)))
        if not [c for c in grille["cases"] if f(c)]:
            continue
        out.append({**v, "par_bras": [la_derive_et_le_prix(grille, f, b) for b in BRAS]})
    return {"par_instrument": out}


def juger(grille: dict) -> dict:
    """Les deux ingrédients de `142`, repesés sous le rejet — et le total mis à l'épreuve.

    ⚠⚠⚠ UN TOTAL EN AVANCE N'EST PAS UNE VICTOIRE. C'est la règle de `147`, et c'est elle qui décide
    ici : une mâchoire seule peut mener de cinq en ayant perdu huit départs que la pince tenait.
    """
    pi = par_instrument(grille)["par_instrument"]
    if not pi:
        return {"decidable": False, "raison": "aucun instrument dans la grille"}
    # ⭐⭐⭐ LA QUEUE DE CHAQUE BRAS, RAPPORTÉE À CELLE QU'IL AVAIT SOUS `144`. C'est le seul
    # chiffre qui dise À QUI le rejet profite : un appui aberrant corrompt une épaisseur MESURÉE, et
    # l'épaisseur mesurée est ce qui fixe la fenêtre — donc le bras qui mesure devrait en tirer plus
    # que celui qui suppose. Publié comme un rapport parce qu'un couple de queues se lirait comme
    # deux niveaux.
    temoin = next((y for y in pi if not y["en_croix"] and not y["rejeter"]), None)
    queues_temoin = ({b["bras"]: b["derive_max"] for b in temoin["par_bras"] if b.get("decidable")}
                     if temoin is not None else {})
    p90_temoin = ({b["bras"]: b["derive_p90"] for b in temoin["par_bras"] if b.get("decidable")}
                  if temoin is not None else {})
    lignes = []
    for x in pi:
        bras = {b["bras"]: b for b in x["par_bras"] if b.get("decidable")}
        ap = {a["bras"]: a for a in x["apparie"] if a.get("decidable")}
        seule, libre = "une machoire", "deux machoires libres"
        pince = bras.get(LE_BRAS_DE_REFERENCE)
        if pince is None or seule not in bras:
            continue
        lignes.append({
            "nom": x["nom"], "en_croix": x["en_croix"], "rejeter": x["rejeter"],
            # ⭐ Ce que la SECONDE MÂCHOIRE achète : elle se lit contre la mâchoire seule.
            "reussites_seule": bras[seule]["reussites"],
            "reussites_pince": pince["reussites"],
            "seule_gagne": ap.get(seule, {}).get("gains"),
            "seule_perd": ap.get(seule, {}).get("pertes"),
            "seule_gagne_jointement": bool(ap.get(seule, {}).get("gains")
                                           and ap.get(seule, {}).get("il_ne_perd_rien")),
            "derive_max_seule": bras[seule]["derive_max"],
            "derive_max_pince": pince["derive_max"],
            # ⚠ Une division se DIT absente plutôt que de valoir zéro : sans témoin il n'y a pas de
            # rapport, et un rapport inventé se lirait comme un rapport mesuré.
            "queue_divisee_seule": (round(queues_temoin[seule] / bras[seule]["derive_max"], 3)
                                    if queues_temoin.get(seule) and bras[seule]["derive_max"]
                                    else None),
            "queue_divisee_pince": (round(queues_temoin[LE_BRAS_DE_REFERENCE]
                                          / pince["derive_max"], 3)
                                    if queues_temoin.get(LE_BRAS_DE_REFERENCE)
                                    and pince["derive_max"] else None),
            "p90_seule": bras[seule]["derive_p90"],
            "p90_pince": pince["derive_p90"],
            # ⭐⭐⭐ CE QUE LA SECONDE MÂCHOIRE ACHÈTE, EN UN SEUL NOMBRE : de combien la queue de
            # la mâchoire seule dépasse celle de la pince, sous le MÊME instrument. C'est la forme
            # que `142` avait donnée à la question (la seconde mâchoire divise la dérive par
            # 18,178), reposée sur une queue plutôt que sur une médiane.
            "la_seconde_machoire_divise_la_queue_par": (
                round(bras[seule]["derive_p90"] / pince["derive_p90"], 3)
                if pince["derive_p90"] else None),
            "p90_divise_seule": (round(p90_temoin[seule] / bras[seule]["derive_p90"], 3)
                                 if p90_temoin.get(seule) and bras[seule]["derive_p90"]
                                 else None),
            "p90_divise_pince": (round(p90_temoin[LE_BRAS_DE_REFERENCE] / pince["derive_p90"], 3)
                                 if p90_temoin.get(LE_BRAS_DE_REFERENCE) and pince["derive_p90"]
                                 else None),
            "lectures_seule": bras[seule]["lectures_medianes"],
            "lectures_pince": pince["lectures_medianes"],
            # ⭐ Ce que la CONTRAINTE achète : elle se lit contre une paire LIBRE, qui a la seconde
            # mâchoire et pas le refus. C'est la décomposition de `142`, terme par terme.
            "reussites_libre": bras[libre]["reussites"] if libre in bras else None,
            "libre_gagne": ap.get(libre, {}).get("gains"),
            "libre_perd": ap.get(libre, {}).get("pertes"),
            "refus_de_la_pince": pince["refus"],
            "marches_qui_refusent": pince["marches_qui_refusent"],
            "la_contrainte_achete_quelque_chose": bool(
                ap.get(libre, {}).get("gains") is not None
                and (ap[libre]["gains"] or ap[libre]["pertes"]))})
    dur = sur_la_matiere_du_rouleau(grille)["par_instrument"]
    return {"decidable": True, "par_instrument": pi, "sur_la_matiere_du_rouleau": dur,
            "le_verdict": lignes}


def mesurer(grille: Path = LA_GRILLE) -> dict:
    """⚠⚠ NE REMARCHE RIEN : cette tranche relit la grille que `156` a payée.

    ⚠ Une grille absente se DIT et ne se devine pas : un verdict rendu sans elle serait un verdict
    sur rien, et il ressemblerait exactement à un verdict sur quelque chose.
    """
    p = Path(grille)
    if not p.exists():
        return {"message": f"la grille de `156` est absente : {p}"}
    d = json.loads(p.read_text())
    g = d.get("sur_la_grille", {})
    if not g.get("cases"):
        return {"message": f"la grille de `156` est vide : {p}"}
    return {"la_grille": p.name, "departs": int(g["departs"]), "tours": float(g["tours"]),
            "fenetre": int(g["fenetre"]), "cases": len(g["cases"]),
            "bruits": [float(b) for b in g["bruits"]], "juger": juger(g)}


def reagreger(r: dict, grille: Path = LA_GRILLE) -> dict:
    """Relit le verdict depuis la grille de `156`, sans remarcher — et sans toucher la grille."""
    return mesurer(grille) if "message" not in r else r


def afficher(r: dict) -> None:
    if "message" in r:
        print(f"⚠ {r['message']}")
        return
    j = r["juger"]
    if not j.get("decidable"):
        print(f"⚠ {j.get('raison', 'indécidable')}")
        return
    print(f"   la grille de `156` relue : {r['cases']} cases, {r['departs']} départs par case, "
          f"fenêtre {r['fenetre']}")
    print(f"\n   {'instrument':>22} | {'seule':>5} | {'pince':>5} | {'gagne/perd':>10} | "
          f"{'queue seule':>11} | {'queue pince':>11}")
    for x in j["le_verdict"]:
        print(f"   {x['nom']:>22} | {x['reussites_seule']:>5d} | {x['reussites_pince']:>5d} | "
              f"{x['seule_gagne']:>4d}/{x['seule_perd']:<5d} | "
              f"{x['derive_max_seule']:>11.3f} | {x['derive_max_pince']:>11.3f}")
    print("\n   la queue de `144` divisée par celle de chaque instrument — à QUI le rejet "
          "profite :")
    for x in j["le_verdict"]:
        print(f"     {x['nom']:>22} : mâchoire seule ×{x['queue_divisee_seule']} "
              f"(p90 ×{x['p90_divise_seule']}) · pince ×{x['queue_divisee_pince']} "
              f"(p90 ×{x['p90_divise_pince']})")
    print("\n   ce que la CONTRAINTE achète — une paire LIBRE contre la pince :")
    for x in j["le_verdict"]:
        print(f"     {x['nom']:>22} : {x['libre_gagne']} gagnée(s), {x['libre_perd']} perdue(s), "
              f"pour {x['refus_de_la_pince']} refus sur {x['marches_qui_refusent']} marches")
    print("\n   sur la matière du rouleau — jusqu'où chaque bras va, faute de réussir :")
    for x in j["sur_la_matiere_du_rouleau"]:
        print(f"     {x['nom']:>22} : " + " · ".join(
            f"{b['bras']} {b['part_du_tour_mediane']:.4f}" for b in x["par_bras"]
            if b.get("decidable")))
    jointes = [x["nom"] for x in j["le_verdict"] if x["seule_gagne_jointement"]]
    marque = "✗" if not jointes else "★★★★"
    print(f"\n{marque} une mâchoire SEULE bat-elle la pince JOINTEMENT ? "
          f"{bool(jointes)} — {jointes if jointes else 'sous aucun des quatre instruments'}")
    ach = [x["nom"] for x in j["le_verdict"] if x["la_contrainte_achete_quelque_chose"]]
    print(f"   la contrainte achète encore quelque chose sous : "
          f"{ach if ach else 'aucun instrument'}")


def _suivi(depart_deg: float, reussi: bool, derive: float = 0.0, arrete: bool = False,
           refus: int = 0, lectures: int = 1000, part: float = 1.0) -> dict:
    """Un suivi FACTICE, pour éprouver le verdict sans marcher.

    ⚠ Il passe par `une_reussite` comme tout le reste : une fixture qui fabriquerait la réussite
    autrement éprouverait sa propre convention et non celle du dépôt.
    """
    return {"depart_deg": float(depart_deg), "decidable": True,
            "tour_boucle": bool(reussi),
            "derive_en_feuilles": (0.0 if reussi else 3.0) if derive == 0.0 else float(derive),
            "part_du_tour": float(part), "refus": int(refus), "pas": 10,
            "lectures": int(lectures), "appuis_rejetes": 0,
            "epaisseur_um": 156.0,
            "fin": "la pince ne peut plus avancer" if arrete else "tour bouclé"}


def _case_factice(nom: str, bruit: float, en_croix: bool, rejeter: bool, par_bras: dict,
                  ecrasement: float = 0.0, amplitude_um: float = 0.0) -> dict:
    return {"nom": nom, "ecrasement": float(ecrasement), "amplitude_um": float(amplitude_um),
            "bruit": float(bruit), "departs": len(next(iter(par_bras.values()))),
            "en_croix": bool(en_croix), "rejeter": bool(rejeter),
            "bras": {b: {"suivis": par_bras[b]} for b in BRAS}}


def _grille_factice(cases) -> dict:
    return {"departs": 4, "tours": 1.0, "fenetre": 32,
            "bruits": sorted({float(c["bruit"]) for c in cases}),
            "variantes": [{"nom": "témoin", "en_croix": False, "rejeter": False}],
            "cases": list(cases)}


def verifier() -> int:
    import contextlib  # noqa: PLC0415
    import io  # noqa: PLC0415

    echecs = controles = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    print("— un total en avance n'est pas une victoire —")
    # La machoire seule mene 3 contre 2, et elle a PERDU un depart que la pince tenait.
    seule = [_suivi(0, True), _suivi(90, True), _suivi(180, True), _suivi(270, False)]
    pince = [_suivi(0, True), _suivi(90, False), _suivi(180, False), _suivi(270, True)]
    g = _grille_factice([_case_factice("dure", 0.0, False, False,
                                       {"une machoire": seule,
                                        "deux machoires libres": pince,
                                        "la pince": pince})])
    j = juger(g)
    x = j["le_verdict"][0]
    v("⭐⭐⭐⭐ un SOLDE positif ne suffit pas — la mâchoire seule mène et ne gagne PAS jointement",
      x["reussites_seule"] > x["reussites_pince"] and x["seule_perd"] == 1
      and x["seule_gagne_jointement"] is False,
      f"{x['reussites_seule']} contre {x['reussites_pince']}, "
      f"{x['seule_gagne']} gagnée pour {x['seule_perd']} perdue")
    # Et quand elle ne perd rien, elle gagne.
    sans_perte = [_suivi(0, True), _suivi(90, True), _suivi(180, True), _suivi(270, True)]
    g2 = _grille_factice([_case_factice("dure", 0.0, False, False,
                                        {"une machoire": sans_perte,
                                         "deux machoires libres": pince,
                                         "la pince": pince})])
    v("⭐⭐⭐ ... et sans perte, elle gagne jointement",
      juger(g2)["le_verdict"][0]["seule_gagne_jointement"] is True)

    print("\n— l'appariement est fait départ par départ —")
    # Memes COMPTES des deux cotes, mais les reussites ne tombent PAS sur les memes departs :
    # un appariement par rang ou par total rendrait zero, l'appariement par depart rend 2/2.
    a_ = [_suivi(0, True), _suivi(90, True), _suivi(180, False), _suivi(270, False)]
    b_ = [_suivi(0, False), _suivi(90, False), _suivi(180, True), _suivi(270, True)]
    g3 = _grille_factice([_case_factice("dure", 0.0, False, False,
                                        {"une machoire": a_, "deux machoires libres": b_,
                                         "la pince": b_})])
    ap = juger(g3)["le_verdict"][0]
    v("⭐⭐⭐ deux bras à ÉGALITÉ de total peuvent avoir tout échangé — 2 gagnées, 2 perdues",
      ap["reussites_seule"] == ap["reussites_pince"] and ap["seule_gagne"] == 2
      and ap["seule_perd"] == 2,
      f"{ap['reussites_seule']} contre {ap['reussites_pince']}")
    v("⚠ ... et un solde nul n'est donc PAS une victoire jointe",
      ap["seule_gagne_jointement"] is False)
    # ⚠ La cle porte la MATIERE et le BRUIT : deux cases differentes peuvent avoir le meme angle.
    deux_cases = [_case_factice("A", 0.0, False, False,
                                {"une machoire": [_suivi(0, True)],
                                 "deux machoires libres": [_suivi(0, False)],
                                 "la pince": [_suivi(0, False)]}),
                  _case_factice("B", 0.0, False, False,
                                {"une machoire": [_suivi(0, False)],
                                 "deux machoires libres": [_suivi(0, True)],
                                 "la pince": [_suivi(0, True)]})]
    ap2 = juger(_grille_factice(deux_cases))["le_verdict"][0]
    v("⭐⭐ la clé d'appariement porte la MATIÈRE, sinon deux cases au même angle se confondent",
      ap2["seule_gagne"] == 1 and ap2["seule_perd"] == 1,
      f"{ap2['seule_gagne']} gagnée, {ap2['seule_perd']} perdue sur deux matières")

    # ⚠⚠ UN DÉPART OÙ LE BRAS NE SE POSE PAS EST UN ÉCHEC, PAS UNE DONNÉE ABSENTE. Le sauter
    # ferait passer un bras qui refuse beaucoup pour un bras qui réussit souvent.
    pose_pas = [{"depart_deg": 0.0, "decidable": False,
                 "raison": "la pince ne se pose pas au depart"}]
    g_abs = _grille_factice([_case_factice("dure", 0.0, False, False,
                                           {"une machoire": pose_pas,
                                            "deux machoires libres": [_suivi(0, True)],
                                            "la pince": [_suivi(0, True)]})])
    a_abs = apparie_les_bras(g_abs, _filtre(False, False), "une machoire", "la pince")
    v("⭐⭐⭐ un bras qui ne se POSE pas perd le départ, il ne le saute pas",
      a_abs["decidable"] and a_abs["paires"] == 1 and a_abs["pertes"] == 1
      and a_abs["gains"] == 0,
      # ⚠ Le détail se lit en `.get` : une sonde qui LÈVE arrête la batterie et cache les
      # contrôles suivants, donc elle échoue moins bien qu'une sonde qui rend faux.
      f"{a_abs.get('paires')} paire, {a_abs.get('pertes')} perdue, "
      f"{a_abs.get('raison', '')}")

    print("\n— la queue, le prix et le refus —")
    lourde = [_suivi(0, True), _suivi(90, True), _suivi(180, True, derive=40.0),
              _suivi(270, True)]
    legere = [_suivi(0, True), _suivi(90, True), _suivi(180, True, derive=2.0), _suivi(270, True)]
    g4 = _grille_factice([_case_factice("dure", 0.0, False, False,
                                        {"une machoire": lourde,
                                         "deux machoires libres": legere,
                                         "la pince": legere})])
    y = juger(g4)["le_verdict"][0]
    v("⭐⭐⭐⭐ à réussites ÉGALES la queue sépare — un verdict sans elle couronnerait le mauvais bras",
      y["reussites_seule"] == y["reussites_pince"]
      and y["derive_max_seule"] > y["derive_max_pince"],
      f"{y['derive_max_seule']} feuilles contre {y['derive_max_pince']}")
    v("⚠ la dérive est prise en VALEUR ABSOLUE — dériver de quarante feuilles en arrière est aussi "
      "loin qu'en avant",
      la_derive_et_le_prix(_grille_factice([_case_factice(
          "dure", 0.0, False, False,
          {b: [_suivi(0, True, derive=-40.0)] for b in BRAS})]),
          _filtre(False, False), "la pince")["derive_max"] == 40.0)
    # ⚠⚠ LA FIXTURE SE DÉRIVE DE `une_reussite`, ELLE NE S'ÉCRIT PAS AU JUGÉ. Payé ici : j'avais
    # mis `legere` en face, dont la marche à deux feuilles de dérive n'est PAS une réussite — donc
    # la contrainte « achetait » un départ que ma fixture lui avait donné sans le vouloir.
    # ⚠⚠⚠ UN MAXIMUM EST UNE SEULE MARCHE, ET LE p90 PEUT LE CONTREDIRE. Dix marches dont UNE
    # dérive énormément : le maximum dit 40 et le p90 dit 1 — ce sont deux quantités différentes,
    # et un verdict bâti sur la première repose sur un seul départ.
    dix = ([_suivi(i * 10.0, True, derive=1.0) for i in range(9)]
           + [_suivi(90.0, True, derive=40.0)])
    g_q = _grille_factice([_case_factice("dure", 0.0, False, False, {b: dix for b in BRAS})])
    q = la_derive_et_le_prix(g_q, _filtre(False, False), "la pince")
    v("⭐⭐⭐⭐ le p90 est publié à CÔTÉ du maximum, et il ne dit pas la même chose",
      q["derive_max"] == 40.0 and q["derive_p90"] == 1.0,
      f"max {q['derive_max']} contre p90 {q['derive_p90']} sur {q['decidables']} marches")
    v("⚠ le p90 est une statistique d'ORDRE — une valeur qu'une marche a réellement rendue",
      q["derive_p90"] in {abs(x["derive_en_feuilles"]) for x in dix})

    refuse = [_suivi(0, True, refus=3), _suivi(90, True), _suivi(180, True), _suivi(270, True)]
    assert [une_reussite(x) for x in refuse] == [une_reussite(x) for x in sans_perte]
    g5 = _grille_factice([_case_factice("dure", 0.0, False, False,
                                        {"une machoire": legere,
                                         "deux machoires libres": sans_perte,
                                         "la pince": refuse})])
    z = juger(g5)["le_verdict"][0]
    v("⭐⭐ le refus de la CONTRAINTE est COMPTÉ, et il vaut zéro pour un bras libre",
      z["refus_de_la_pince"] == 3 and z["marches_qui_refusent"] == 1
      and la_derive_et_le_prix(g5, _filtre(False, False),
                               "deux machoires libres")["refus"] == 0)
    v("⭐⭐⭐ ... et « elle refuse » n'est PAS « elle achète » : ici elle refuse trois fois pour rien",
      z["la_contrainte_achete_quelque_chose"] is False,
      f"{z['libre_gagne']} gagnée, {z['libre_perd']} perdue contre la paire libre")
    g6 = _grille_factice([_case_factice("dure", 0.0, False, False,
                                        {"une machoire": legere,
                                         "deux machoires libres": pince,
                                         "la pince": sans_perte})])
    v("⚠⚠ ... et le contrôle mord : une contrainte qui gagne un départ est signalée",
      juger(g6)["le_verdict"][0]["la_contrainte_achete_quelque_chose"] is True)

    print("\n— la matière du rouleau —")
    loin = [_suivi(0, False, arrete=True, part=0.40)]
    court = [_suivi(0, False, arrete=True, part=0.02)]
    g7 = _grille_factice([
        _case_factice("celle du rouleau", 0.0, False, False,
                      {"une machoire": loin, "deux machoires libres": court, "la pince": court},
                      ecrasement=LA_MATIERE_DE_140[0], amplitude_um=LA_MATIERE_DE_140[1]),
        _case_factice("une autre", 0.0, False, False,
                      {b: [_suivi(0, True, part=1.0)] for b in BRAS})])
    dur = juger(g7)["sur_la_matiere_du_rouleau"][0]["par_bras"]
    parts = {b["bras"]: b["part_du_tour_mediane"] for b in dur}
    v("⭐⭐⭐ zéro réussite ne dit pas si le mur a bougé — la part du tour le dit",
      parts["une machoire"] == 0.4 and parts["la pince"] == 0.02,
      f"{parts}")
    v("⚠⚠ ... et elle ne regarde QUE la matière du rouleau, pas la grille entière",
      all(b["marches"] == 1 for b in dur))

    print("\n— `mesurer`, `reagreger`, `afficher` —")
    absent = RACINE / "docs" / "mesures" / "_introuvable_157.json"
    r = mesurer(absent)
    v("⚠ une grille absente se DIT, elle ne se devine pas",
      "message" in r and "absente" in r["message"])
    v("⚠ ... et `reagreger` ne fabrique rien depuis un message",
      "message" in reagreger(r, absent))
    vide = RACINE / "docs" / "mesures" / "_vide_157.json"
    vide.write_text(json.dumps({"sur_la_grille": {"cases": []}}))
    try:
        v("⚠ une grille VIDE est refusée, et le refus DIT laquelle",
          "message" in mesurer(vide) and "vide" in mesurer(vide)["message"])
    finally:
        vide.unlink(missing_ok=True)
    if LA_GRILLE.exists():
        vrai = mesurer(LA_GRILLE)
        v("⭐ sur la vraie grille, les quatre instruments sont jugés",
          vrai["juger"]["decidable"] and len(vrai["juger"]["le_verdict"]) == 4,
          f"{len(vrai['juger']['le_verdict'])} instruments")
        avant = json.loads(json.dumps(vrai))
        v("⭐⭐⭐ `reagreger` rend EXACTEMENT le même verdict — il relit, il ne remarche pas",
          reagreger(json.loads(json.dumps(vrai)), LA_GRILLE) == avant)
        tampon = io.StringIO()
        with contextlib.redirect_stdout(tampon):
            afficher(vrai)
        sortie = tampon.getvalue()
        v("⚠ `afficher` rend le tableau, la contrainte et la matière du rouleau",
          "instrument" in sortie and "CONTRAINTE" in sortie and "matière du rouleau" in sortie,
          f"{len(sortie)} caractères")
    tampon = io.StringIO()
    with contextlib.redirect_stdout(tampon):
        afficher({"message": "grille absente"})
    v("⚠ un message est dit, jamais dessiné", "⚠" in tampon.getvalue())

    print(f"\n{'ALL PASS' if echecs == 0 else '⛔ ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path, default=None)
    p.add_argument("--grille", type=Path, default=LA_GRILLE)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--reagreger", type=Path, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = (reagreger(json.loads(a.reagreger.read_text()), a.grille) if a.reagreger is not None
         else mesurer(a.grille))
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    afficher(r)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
