"""De quoi meurt-on sur la matière du rouleau, maintenant que le mur a reculé ?

⭐⭐⭐⭐ POURQUOI CE FICHIER. `157` mesure que le rejet multiplie par cinq la part du tour parcourue
sur la matière que `140` retient — celle sur laquelle personne n'a jamais réussi un transfert depuis
`142` — à **zéro** réussite inchangé. Un mur qui recule sans tomber pose une question que ni `156`
ni `157` n'ont posée : de quoi meurt-on MAINTENANT ? C'est le patron de `149`, qui avait compté les
échecs sur les marches que `148` rangeait, appliqué à la seule matière qui compte.

⭐⭐⭐ ET IL SÉPARE DEUX ÉNONCÉS QUE `une_reussite` JOINT À DESSEIN. « Boucler le tour » et « revenir
sur la même feuille » sont la même réussite pour le prédicat du dépôt, et c'est juste — `143` a payé
qu'on les compte à part. Mais pour une AUTOPSIE il faut les regarder séparément, parce qu'ils ne
tombent pas ensemble : une marche peut boucler son tour en ratant sa feuille de douze, et une autre
peut « revenir sur la bonne feuille » en n'ayant pas bougé.

⚠⚠⚠ ET C'EST LA GARDE QUE CE FICHIER EXISTE POUR TENIR. `_resumer_un_bras` prévient depuis `142`
qu'« une pince qui refuse tout ne dérive jamais et ne va nulle part ». Sur cette matière le piège
n'est pas théorique : la part du tour parcourue est publiée À CÔTÉ de chaque compte de feuilles, et
c'est elle qui dit si le compte veut dire quelque chose.

Usage :
    uv run python src/nappe/de_quoi_meurt_on_sur_la_matiere_du_rouleau.py --verifier
    uv run python src/nappe/de_quoi_meurt_on_sur_la_matiere_du_rouleau.py \\
        --json docs/mesures/de_quoi_meurt_on_sur_la_matiere_du_rouleau.json
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
# ⚠ « La même feuille » se décide à une DEMI-feuille : c'est là que l'appariement au plus proche
# bascule, exactement comme le demi-pas qui décide qu'un appui a changé d'interstice. Ce n'est pas
# une tolérance réglée, c'est l'énoncé de la question — et il est écrit ici parce que ce fichier le
# lit sans passer par `une_reussite`, qui le JOINT au tour.
LA_DEMI_FEUILLE = 0.5


def _filtre(en_croix: bool, rejeter: bool):
    """⚠ Une clé absente vaut FAUX : un record d'avant `156` ne connaît pas ces deux mots."""
    def f(c):
        return (bool(c.get("en_croix", False)) is bool(en_croix)
                and bool(c.get("rejeter", False)) is bool(rejeter))
    return f


def _sur_la_matiere(grille: dict, filtre, bruit: float | None = None) -> list[dict]:
    return [c for c in grille["cases"]
            if filtre(c)
            and (round(float(c["ecrasement"]), 4), round(float(c["amplitude_um"]), 1))
            == (round(LA_MATIERE_DE_140[0], 4), round(LA_MATIERE_DE_140[1], 1))
            and (bruit is None or abs(float(c["bruit"]) - float(bruit)) < 1e-12)]


def _impossibles(x: dict) -> int:
    """Les pas où la mâchoire n'a PAS PU se poser, sous les deux noms qu'a portés ce compte.

    ⚠⚠ `suivre` l'a publié sous `poses_refusees` jusqu'au renommage de `168`, qui lui donne son
    nom propre parce qu'un SECOND genre de refus — la pose qui se contredit — portait le même
    depuis `164`, dans le même dictionnaire, et le gagnait en silence.
    """
    v = x.get("poses_impossibles")
    return int(v if v is not None else x["poses_refusees"])


def _med(xs, n=4):
    return round(float(statistics.median(xs)), n) if xs else None


def lautopsie(grille: dict, filtre, bras: str, bruit: float | None = None) -> dict:
    """De quoi meurent les marches d'un bras sur cette matière, et jusqu'où elles vont.

    ⚠⚠ CHAQUE COMPTE DE FEUILLES VOYAGE AVEC LA PART DU TOUR QUI LE PORTE. « Elle revient sur la
    même feuille » est vrai d'une marche qui n'a pas bougé, et c'est la tautologie que `142` nomme ;
    la seule façon de ne pas s'y laisser prendre est de publier les deux ensemble, toujours.

    ⚠ Une marche indécidable est comptée à part et jamais confondue avec une marche arrêtée : ne pas
    se poser au départ et s'arrêter au bout de quarante pas sont deux échecs différents.
    """
    cases = _sur_la_matiere(grille, filtre, bruit)
    if not cases:
        return {"decidable": False, "raison": "aucune case sur la matière du rouleau"}
    xs = [x for c in cases for x in c["bras"][bras]["suivis"]]
    dec = [x for x in xs if x.get("decidable")]
    if not dec:
        return {"decidable": False, "raison": f"aucune marche décidable pour « {bras} »"}
    fins: dict[str, int] = {}
    for x in dec:
        fins[str(x["fin"])] = fins.get(str(x["fin"]), 0) + 1
    boucles = [x for x in dec if x.get("tour_boucle")]
    memes = [x for x in dec if abs(float(x["derive_en_feuilles"])) < LA_DEMI_FEUILLE]
    autres = [x for x in dec if abs(float(x["derive_en_feuilles"])) >= LA_DEMI_FEUILLE]
    der_b = [abs(float(x["derive_en_feuilles"])) for x in boucles]
    return {"decidable": True, "bras": bras, "marches": len(xs), "decidables": len(dec),
            "poses_manquees": len(xs) - len(dec), "fins": fins,
            # ⭐⭐⭐ LES TROIS COMPTES, ET ILS NE TOMBENT PAS ENSEMBLE.
            "tours_boucles": len(boucles), "memes_feuilles": len(memes),
            "reussites_jointes": int(sum(1 for x in dec if une_reussite(x))),
            # ⚠⚠ La part du tour des marches « même feuille », qui dit si ce compte veut dire
            # quelque chose — et celle des autres, pour qu'il y ait de quoi comparer.
            "part_du_tour_des_memes_feuilles": _med([float(x["part_du_tour"]) for x in memes]),
            "part_du_tour_max_des_memes_feuilles": (
                round(max(float(x["part_du_tour"]) for x in memes), 4) if memes else None),
            "part_du_tour_des_autres": _med([float(x["part_du_tour"]) for x in autres]),
            "part_du_tour_mediane": _med([float(x["part_du_tour"]) for x in dec]),
            # ⭐⭐ La dérive des tours BOUCLÉS : de combien de feuilles rate-t-on, quand on arrive ?
            "derive_des_tours_boucles": _med(der_b, 3),
            "derive_min_des_tours_boucles": round(min(der_b), 3) if der_b else None,
            "derive_max_des_tours_boucles": round(max(der_b), 3) if der_b else None,
            # ⚠ De quoi on meurt : la pose, ou la contrainte ? C'est la question de `149`.
            # ⚠⚠⚠ CE MODULE NE MARCHE PAS : il relit la grille STOCKEE de `156`, qui est anterieure
            # au renommage de `168` et porte donc `poses_refusees` avec l'ANCIEN sens — les pas ou
            # la machoire n'a PAS PU SE POSER. Une grille fraichement marchee porterait
            # `poses_impossibles`. Les deux noms sont acceptes ICI et nulle part ailleurs, parce
            # qu'ils designent la MEME quantite de part et d'autre d'un renommage date, et le nom
            # publie ne bouge pas puisque ses chiffres le sont deja.
            "poses_refusees_mediane": _med([_impossibles(x) for x in dec], 1),
            "poses_refusees_totales": int(sum(_impossibles(x) for x in dec)),
            "refus_de_contrainte": int(sum(int(x["refus"]) for x in dec)),
            "pas_median": _med([int(x["pas"]) for x in dec], 1),
            "appuis_rejetes": int(sum(int(x.get("appuis_rejetes", 0)) for x in dec))}


def par_instrument(grille: dict) -> dict:
    out = []
    for v in grille["variantes"]:
        f = _filtre(v["en_croix"], v["rejeter"])
        if not _sur_la_matiere(grille, f):
            continue
        out.append({**v, "par_bras": [lautopsie(grille, f, b) for b in BRAS]})
    return {"par_instrument": out}


def par_bruit(grille: dict, bras: str = "une machoire") -> dict:
    """OÙ les tours se bouclent, bruit par bruit.

    ⚠ Le bras est un PARAMÈTRE et non un choix figé : c'est la mâchoire seule qui boucle, mais un
    fichier qui le supposerait ne pourrait pas montrer que les autres ne bouclent pas.
    """
    out = []
    for v in grille["variantes"]:
        f = _filtre(v["en_croix"], v["rejeter"])
        lignes = []
        for b in grille["bruits"]:
            a = lautopsie(grille, f, bras, bruit=float(b))
            if a.get("decidable"):
                lignes.append({"bruit": float(b), "decidables": a["decidables"],
                               "tours_boucles": a["tours_boucles"],
                               "reussites_jointes": a["reussites_jointes"],
                               "appuis_rejetes": a["appuis_rejetes"]})
        if lignes:
            out.append({**v, "bras": bras, "par_bruit": lignes})
    return {"par_bruit": out}


def juger(grille: dict) -> dict:
    """Ce qui a changé de nature, et ce qui n'a pas changé du tout."""
    pi = par_instrument(grille)["par_instrument"]
    if not pi:
        return {"decidable": False, "raison": "aucune case sur la matière du rouleau"}
    temoin = next((x for x in pi if not x["en_croix"] and not x["rejeter"]), None)
    lignes = []
    for x in pi:
        bras = {b["bras"]: b for b in x["par_bras"] if b.get("decidable")}
        t_bras = ({b["bras"]: b for b in temoin["par_bras"] if b.get("decidable")}
                  if temoin is not None else {})
        for nom, a in bras.items():
            t = t_bras.get(nom)
            lignes.append({
                "instrument": x["nom"], "bras": nom,
                "tours_boucles": a["tours_boucles"], "memes_feuilles": a["memes_feuilles"],
                "reussites_jointes": a["reussites_jointes"], "decidables": a["decidables"],
                "part_du_tour_des_memes_feuilles": a["part_du_tour_des_memes_feuilles"],
                "arrets": a["fins"].get("la pince ne peut plus avancer", 0),
                "poses_refusees_mediane": a["poses_refusees_mediane"],
                "refus_de_contrainte": a["refus_de_contrainte"],
                "pas_median": a["pas_median"],
                "derive_des_tours_boucles": a["derive_des_tours_boucles"],
                # ⭐⭐⭐⭐ LA MORT A-T-ELLE CHANGÉ DE NATURE ? Elle a changé quand des tours se
                # bouclent là où AUCUN ne se bouclait, et pas quand la marche va seulement plus
                # loin : aller plus loin et mourir de la même chose reste la même mort.
                "la_mort_a_change_de_nature": bool(
                    t is not None and a["tours_boucles"] > 0 and t["tours_boucles"] == 0),
                "elle_meurt_toujours_darret": bool(
                    a["fins"].get("la pince ne peut plus avancer", 0) == a["decidables"]),
                "pas_medians_multiplies_par": (
                    round(a["pas_median"] / t["pas_median"], 3)
                    if t is not None and t.get("pas_median") else None)})
    return {"decidable": True, "par_instrument": pi,
            "par_bruit": par_bruit(grille)["par_bruit"], "le_verdict": lignes,
            "le_compte_de_feuilles_recompense_limmobilite":
                le_compte_de_feuilles_recompense_limmobilite(lignes)}


def le_compte_de_feuilles_recompense_limmobilite(lignes: list[dict]) -> dict:
    """L'instrument qui compte le PLUS de « mêmes feuilles » est-il celui qui va le plus loin ?

    ⭐⭐⭐⭐ C'EST LA TAUTOLOGIE DE `142`, RENDUE MESURABLE. « Une pince qui refuse tout ne dérive
    jamais et ne va nulle part » est un avertissement ; ici il devient un couple de nombres, et il
    se lit d'un coup d'oeil quand les deux maxima ne tombent pas sur le même instrument.

    ⚠ Deux comparaisons de maxima sur quatre instruments ne sont pas une corrélation, et ce n'est
    pas ce qui est publié : ce sont deux EXTRÊMES nommés, avec le couple qui les porte.
    """
    out = {}
    for bras in {x["bras"] for x in lignes}:
        ls = [x for x in lignes
              if x["bras"] == bras and x["part_du_tour_des_memes_feuilles"] is not None]
        if len(ls) < 2:
            continue
        # ⚠⚠⚠ L'ÉGALITÉ SE TRANCHE DANS LE SENS QUI REND LA REVENDICATION PLUS DURE. Deux
        # instruments à égalité de feuilles : celui qui est nommé est celui qui va le PLUS LOIN,
        # donc le contrôle rend « ce ne sont pas les mêmes » FAUX là où un départage arbitraire
        # l'aurait rendu vrai. Trancher dans l'autre sens fabriquerait la conclusion qu'on mesure.
        plus = max(ls, key=lambda x: (x["memes_feuilles"], x["part_du_tour_des_memes_feuilles"]))
        loin = max(ls, key=lambda x: (x["part_du_tour_des_memes_feuilles"], x["memes_feuilles"]))
        out[bras] = {
            "plus_de_feuilles": plus["instrument"], "ses_feuilles": plus["memes_feuilles"],
            "sa_part_du_tour": plus["part_du_tour_des_memes_feuilles"],
            "va_le_plus_loin": loin["instrument"], "ses_feuilles_a_lui": loin["memes_feuilles"],
            "sa_part_a_lui": loin["part_du_tour_des_memes_feuilles"],
            "ce_ne_sont_pas_les_memes": bool(plus["instrument"] != loin["instrument"])}
    return out


def mesurer(grille: Path = LA_GRILLE) -> dict:
    """⚠⚠ NE REMARCHE RIEN : cette tranche relit la grille que `156` a payée."""
    p = Path(grille)
    if not p.exists():
        return {"message": f"la grille de `156` est absente : {p}"}
    d = json.loads(p.read_text())
    g = d.get("sur_la_grille", {})
    if not g.get("cases"):
        return {"message": f"la grille de `156` est vide : {p}"}
    return {"la_grille": p.name, "departs": int(g["departs"]), "tours": float(g["tours"]),
            "fenetre": int(g["fenetre"]), "bruits": [float(b) for b in g["bruits"]],
            "matiere": {"ecrasement": LA_MATIERE_DE_140[0], "amplitude_um": LA_MATIERE_DE_140[1]},
            "juger": juger(g)}


def reagreger(r: dict, grille: Path = LA_GRILLE) -> dict:
    """Relit le verdict depuis la grille de `156`, sans remarcher."""
    return mesurer(grille) if "message" not in r else r


def afficher(r: dict) -> None:
    if "message" in r:
        print(f"⚠ {r['message']}")
        return
    j = r["juger"]
    if not j.get("decidable"):
        print(f"⚠ {j.get('raison', 'indécidable')}")
        return
    print(f"   la matière du rouleau, relue de `156` : {r['departs']} départs × "
          f"{len(r['bruits'])} bruits, fenêtre {r['fenetre']}")
    print(f"\n   {'instrument':>22} {'bras':>22} | {'déc.':>4} | {'tours':>5} | {'mêmes f.':>8} "
          f"| {'jointes':>7} | {'part des mêmes f.':>17}")
    for x in j["le_verdict"]:
        marque = " ★" if x["la_mort_a_change_de_nature"] else "  "
        print(f"   {x['instrument']:>22} {x['bras']:>22} | {x['decidables']:>4d} | "
              f"{x['tours_boucles']:>5d} | {x['memes_feuilles']:>8d} | "
              f"{x['reussites_jointes']:>7d} | "
              f"{x['part_du_tour_des_memes_feuilles']:>17}{marque}")
    print("\n   de quoi on meurt — la pose, ou la contrainte ?")
    for x in j["le_verdict"]:
        print(f"     {x['instrument']:>22} {x['bras']:>22} : {x['arrets']}/{x['decidables']} "
              f"arrêts · poses refusées méd. {x['poses_refusees_mediane']} · "
              f"refus de contrainte {x['refus_de_contrainte']} · pas méd. {x['pas_median']}"
              + (f" (×{x['pas_medians_multiplies_par']})"
                 if x["pas_medians_multiplies_par"] else ""))
    print("\n   où les tours se bouclent — une mâchoire seule, bruit par bruit :")
    for x in j["par_bruit"]:
        print(f"     {x['nom']:>22} : " + " · ".join(
            f"bruit {y['bruit']:g} {y['tours_boucles']}/{y['decidables']} tours, "
            f"{y['reussites_jointes']} jointe(s)" for y in x["par_bruit"]))
    im = j.get("le_compte_de_feuilles_recompense_limmobilite", {})
    if im:
        print("\n   le compte « même feuille » récompense-t-il l'IMMOBILITÉ ?")
        for bras, y in sorted(im.items()):
            print(f"     {bras:>22} : le plus de feuilles « {y['plus_de_feuilles']} » "
                  f"({y['ses_feuilles']} à {y['sa_part_du_tour']} de tour) · va le plus loin "
                  f"« {y['va_le_plus_loin']} » ({y['ses_feuilles_a_lui']} à {y['sa_part_a_lui']})")
    changes = [x for x in j["le_verdict"] if x["la_mort_a_change_de_nature"]]
    marque = "★★★★" if changes else "✗"
    print(f"\n{marque} la mort a-t-elle changé de NATURE ? {bool(changes)} — "
          + (" · ".join(f"{x['bras']} sous « {x['instrument']} » : {x['tours_boucles']} tours "
                        f"bouclés, dérive médiane {x['derive_des_tours_boucles']} feuilles"
                        for x in changes) if changes else "nulle part"))


def _suivi(depart_deg: float, boucle: bool, derive: float, part: float,
           fin: str = "la pince ne peut plus avancer", poses_refusees: int = 0,
           refus: int = 0, pas: int = 10, rejetes: int = 0) -> dict:
    """Un suivi FACTICE, pour éprouver l'autopsie sans marcher."""
    return {"depart_deg": float(depart_deg), "decidable": True, "tour_boucle": bool(boucle),
            "derive_en_feuilles": float(derive), "part_du_tour": float(part),
            "fin": str(fin), "poses_impossibles": int(poses_refusees), "refus": int(refus),
            "pas": int(pas), "lectures": 1000, "appuis_rejetes": int(rejetes),
            "epaisseur_um": 156.0}


def _case_factice(bruit: float, en_croix: bool, rejeter: bool, suivis,
                  matiere=LA_MATIERE_DE_140) -> dict:
    return {"nom": "celle du rouleau", "ecrasement": float(matiere[0]),
            "amplitude_um": float(matiere[1]), "bruit": float(bruit), "departs": len(suivis),
            "en_croix": bool(en_croix), "rejeter": bool(rejeter),
            "bras": {b: {"suivis": suivis} for b in BRAS}}


def _grille_factice(cases, variantes=None) -> dict:
    return {"departs": 4, "tours": 1.0, "fenetre": 32,
            "bruits": sorted({float(c["bruit"]) for c in cases}),
            "variantes": variantes or [{"nom": "témoin", "en_croix": False, "rejeter": False}],
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

    print("— « même feuille » est-il un compte de marches IMMOBILES ? —")
    # Deux marches sur la bonne feuille sans avoir bouge, deux qui sont allees loin et ont derive.
    immobiles = [_suivi(0, False, 0.01, 0.03), _suivi(90, False, 0.02, 0.04),
                 _suivi(180, False, 4.0, 0.60), _suivi(270, False, 5.0, 0.70)]
    g = _grille_factice([_case_factice(0.0, False, False, immobiles)])
    a = lautopsie(g, _filtre(False, False), "la pince")
    v("⭐⭐⭐⭐ le compte « même feuille » voyage avec la PART DU TOUR qui le porte",
      a["memes_feuilles"] == 2 and a["part_du_tour_des_memes_feuilles"] == 0.035
      and a["part_du_tour_des_autres"] == 0.65,
      f"{a['memes_feuilles']} marches à {a['part_du_tour_des_memes_feuilles']} de tour, "
      f"contre {a['part_du_tour_des_autres']} pour les autres")
    v("⚠ ... et le MAXIMUM de cette part est publié, parce qu'une médiane cache une exception",
      a["part_du_tour_max_des_memes_feuilles"] == 0.04)
    v("⚠⚠ « la même feuille » se décide à une DEMI-feuille, et la borne est stricte",
      lautopsie(_grille_factice([_case_factice(0.0, False, False,
                                               [_suivi(0, False, 0.5, 0.1),
                                                _suivi(90, False, 0.499, 0.1)])]),
                _filtre(False, False), "la pince")["memes_feuilles"] == 1)

    print("\n— boucler le tour et revenir sur la feuille ne tombent pas ensemble —")
    melange = [_suivi(0, True, 12.0, 1.0, fin="tour bouclé"),
               _suivi(90, True, 0.2, 1.0, fin="tour bouclé"),
               _suivi(180, False, 0.1, 0.05), _suivi(270, False, 9.0, 0.7)]
    g2 = _grille_factice([_case_factice(0.0, False, False, melange)])
    b = lautopsie(g2, _filtre(False, False), "la pince")
    v("⭐⭐⭐ les TROIS comptes diffèrent — 2 tours, 2 mêmes feuilles, 1 seule réussite JOINTE",
      (b["tours_boucles"], b["memes_feuilles"], b["reussites_jointes"]) == (2, 2, 1),
      f"{b['tours_boucles']} tours, {b['memes_feuilles']} feuilles, "
      f"{b['reussites_jointes']} jointes")
    v("⭐⭐ la dérive des tours BOUCLÉS est publiée, et elle n'est pas celle de toutes les marches",
      b["derive_des_tours_boucles"] == 6.1 and b["derive_min_des_tours_boucles"] == 0.2
      and b["derive_max_des_tours_boucles"] == 12.0,
      f"médiane {b['derive_des_tours_boucles']} entre {b['derive_min_des_tours_boucles']} "
      f"et {b['derive_max_des_tours_boucles']}")

    print("\n— de quoi on meurt —")
    morts = [_suivi(0, False, 1.0, 0.05, poses_refusees=21, refus=0, pas=42),
             _suivi(90, False, 1.0, 0.05, poses_refusees=29, refus=1, pas=44),
             _suivi(180, False, 1.0, 0.05, fin="plafond de pas", pas=4000)]
    g3 = _grille_factice([_case_factice(0.0, False, False, morts)])
    c = lautopsie(g3, _filtre(False, False), "la pince")
    v("⭐⭐ les FINS sont comptées une par une, jamais résumées en « échec »",
      c["fins"] == {"la pince ne peut plus avancer": 2, "plafond de pas": 1}, f"{c['fins']}")
    v("⚠ ... et la pose et la contrainte sont comptées SÉPARÉMENT, comme dans `149`",
      c["poses_refusees_totales"] == 50 and c["refus_de_contrainte"] == 1)
    v("⚠⚠ une marche qui ne se POSE pas au départ est comptée à part, jamais comme un arrêt",
      lautopsie(_grille_factice([_case_factice(
          0.0, False, False, [_suivi(0, False, 1.0, 0.05), {"decidable": False}])]),
          _filtre(False, False), "la pince")["poses_manquees"] == 1)

    print("\n— la mort a-t-elle changé de NATURE ? —")
    temoin = _case_factice(0.0, False, False,
                           [_suivi(i * 90.0, False, 1.0, 0.05) for i in range(4)])
    plus_loin = _case_factice(0.0, False, True,
                              [_suivi(i * 90.0, False, 1.0, 0.30, pas=110) for i in range(4)])
    boucle = _case_factice(0.0, True, True,
                           [_suivi(0, True, 4.0, 1.0, fin="tour bouclé"),
                            _suivi(90, False, 1.0, 0.3), _suivi(180, False, 1.0, 0.3),
                            _suivi(270, False, 1.0, 0.3)])
    var = [{"nom": "témoin", "en_croix": False, "rejeter": False},
           {"nom": "plus loin", "en_croix": False, "rejeter": True},
           {"nom": "elle boucle", "en_croix": True, "rejeter": True}]
    g4 = _grille_factice([temoin, plus_loin, boucle], var)
    j4 = {x["instrument"]: x for x in juger(g4)["le_verdict"] if x["bras"] == "la pince"}
    v("⭐⭐⭐⭐ aller PLUS LOIN et mourir de la même chose n'est PAS un changement de nature",
      j4["plus loin"]["la_mort_a_change_de_nature"] is False
      and j4["plus loin"]["elle_meurt_toujours_darret"] is True
      and j4["plus loin"]["pas_medians_multiplies_par"] > 1.0,
      f"pas médians ×{j4['plus loin']['pas_medians_multiplies_par']}, "
      f"{j4['plus loin']['arrets']}/{j4['plus loin']['decidables']} arrêts")
    v("⭐⭐⭐ ... alors qu'un tour BOUCLÉ là où aucun ne se bouclait en est un",
      j4["elle boucle"]["la_mort_a_change_de_nature"] is True
      and j4["elle boucle"]["elle_meurt_toujours_darret"] is False)
    v("⚠ le témoin n'est jamais son propre changement",
      j4["témoin"]["la_mort_a_change_de_nature"] is False)

    print("\n— le compte de feuilles récompense-t-il l'immobilité ? —")
    # « beaucoup » compte trois marches sur la bonne feuille en n'ayant pas bouge ; « loin » n'en
    # compte qu'une, mais elle a fait un demi-tour.
    beaucoup = _case_factice(0.0, False, False,
                             [_suivi(0, False, 0.1, 0.01), _suivi(90, False, 0.1, 0.01),
                              _suivi(180, False, 0.1, 0.01), _suivi(270, False, 9.0, 0.02)])
    loin = _case_factice(0.0, False, True,
                         [_suivi(0, False, 0.1, 0.50), _suivi(90, False, 9.0, 0.60),
                          _suivi(180, False, 9.0, 0.60), _suivi(270, False, 9.0, 0.60)])
    var_i = [{"nom": "beaucoup", "en_croix": False, "rejeter": False},
             {"nom": "loin", "en_croix": False, "rejeter": True}]
    im = juger(_grille_factice([beaucoup, loin], var_i))[
        "le_compte_de_feuilles_recompense_limmobilite"]["la pince"]
    v("⭐⭐⭐⭐ le plus de « mêmes feuilles » et le plus de chemin ne tombent PAS sur le même "
      "instrument",
      im["ce_ne_sont_pas_les_memes"] is True
      and (im["plus_de_feuilles"], im["ses_feuilles"], im["sa_part_du_tour"])
      == ("beaucoup", 3, 0.01)
      and (im["va_le_plus_loin"], im["ses_feuilles_a_lui"], im["sa_part_a_lui"])
      == ("loin", 1, 0.5),
      f"{im['ses_feuilles']} feuilles à {im['sa_part_du_tour']} contre "
      f"{im['ses_feuilles_a_lui']} à {im['sa_part_a_lui']}")
    # ⚠ Et le controle mord dans l'autre sens : quand le meme instrument gagne les deux, il le dit.
    meme = _case_factice(0.0, False, True,
                         [_suivi(0, False, 0.1, 0.50), _suivi(90, False, 0.1, 0.50),
                          _suivi(180, False, 0.1, 0.50), _suivi(270, False, 9.0, 0.60)])
    im2 = juger(_grille_factice([beaucoup, meme], var_i))[
        "le_compte_de_feuilles_recompense_limmobilite"]["la pince"]
    v("⚠⚠⚠ ... et une ÉGALITÉ de feuilles se tranche vers celui qui va le plus loin, donc le "
      "contrôle dit FAUX là où un départage arbitraire aurait dit vrai",
      im2["ce_ne_sont_pas_les_memes"] is False and im2["plus_de_feuilles"] == "loin"
      and im2["ses_feuilles"] == 3,
      f"« {im2['plus_de_feuilles']} », {im2['ses_feuilles']} feuilles à "
      f"{im2['sa_part_du_tour']} de tour")

    print("\n— par bruit, et la matière est FILTRÉE —")
    ailleurs = _case_factice(0.0, False, False,
                             [_suivi(0, True, 0.1, 1.0, fin="tour bouclé")],
                             matiere=(0.0, 0.0))
    g5 = _grille_factice([temoin, ailleurs])
    v("⭐⭐⭐ une autre matière n'entre PAS dans l'autopsie, même si elle boucle",
      lautopsie(g5, _filtre(False, False), "la pince")["tours_boucles"] == 0
      and lautopsie(g5, _filtre(False, False), "la pince")["decidables"] == 4)
    g6 = _grille_factice([_case_factice(0.0, False, True, [_suivi(0, False, 1.0, 0.05)]),
                          _case_factice(16.0, False, True,
                                        [_suivi(0, True, 3.0, 1.0, fin="tour bouclé")])],
                         [{"nom": "rejet", "en_croix": False, "rejeter": True}])
    pb = par_bruit(g6)["par_bruit"][0]["par_bruit"]
    v("⭐⭐ les tours bouclés sont comptés BRUIT PAR BRUIT, pas en total",
      {y["bruit"]: y["tours_boucles"] for y in pb} == {0.0: 0, 16.0: 1},
      f"{[(y['bruit'], y['tours_boucles']) for y in pb]}")

    print("\n— `mesurer`, `reagreger`, `afficher` —")
    absent = RACINE / "docs" / "mesures" / "_introuvable_158.json"
    r = mesurer(absent)
    v("⚠ une grille absente se DIT, elle ne se devine pas",
      "message" in r and "absente" in r["message"])
    v("⚠ ... et `reagreger` ne fabrique rien depuis un message",
      "message" in reagreger(r, absent))
    if LA_GRILLE.exists():
        vrai = mesurer(LA_GRILLE)
        v("⭐ sur la vraie grille, les quatre instruments × trois bras sont jugés",
          vrai["juger"]["decidable"] and len(vrai["juger"]["le_verdict"]) == 12,
          f"{len(vrai['juger']['le_verdict'])} lignes")
        avant = json.loads(json.dumps(vrai))
        v("⭐⭐⭐ `reagreger` rend EXACTEMENT le même verdict — il relit, il ne remarche pas",
          reagreger(json.loads(json.dumps(vrai)), LA_GRILLE) == avant)
        tampon = io.StringIO()
        with contextlib.redirect_stdout(tampon):
            afficher(vrai)
        sortie = tampon.getvalue()
        v("⚠ `afficher` rend les trois comptes, la mort et le partage par bruit",
          "mêmes f." in sortie and "de quoi on meurt" in sortie and "bruit par bruit" in sortie,
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
