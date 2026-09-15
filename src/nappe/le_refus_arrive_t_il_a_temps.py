"""Le refus arrive-t-il à temps ? — le PRIX que `162` laisse à payer.

⭐⭐⭐⭐ POURQUOI CE FICHIER, ET IL CORRIGE UNE LECTURE. `162` mesure qu'un énoncé voit **0,9196**
des changements de feuille et le paie d'une précision de **0,397**, donc qu'aucun énoncé ne domine.
Mais un refus ne peut qu'**arrêter** une marche : il n'allonge jamais rien, et il ne se déclenche
qu'**une seule fois**. Une précision calculée sur la marche entière compte donc des refus qui
**n'arriveront jamais**, puisque la marche s'est déjà arrêtée au premier.

⚠⚠⚠ UN TAUX PEUT ÊTRE CALCULÉ SUR UN AXE QUE LA RÈGLE NE PARCOURT PAS. C'est le cousin de « moyenner
sur l'axe où la différence vit » : ici, compter sur un axe que rien ne traverse. La seule question
qui décide d'une règle d'ARRÊT est **où son premier refus tombe**.

⭐⭐⭐ L'ÉNONCÉ N'A AUCUN SEUIL ET IL EST SIGNÉ. Pour une marche, on compare deux indices que la
fixture et le marcheur produisent séparément : le premier pas qui change de feuille, et le premier
refus. Cinq cas, exhaustifs et exclusifs :

- **à temps** : le refus tombe au plus tard sur le pas qui saute, donc tout ce qui est livré est
  propre, et le prix est le nombre de pas perdus ;
- **trop tard** : le refus tombe après, donc la marche a déjà livré du faux ;
- **jamais** : la marche saute et rien ne le dit, ce qui est la panne silencieuse ;
- **arrêtée pour rien** : la marche ne sautait pas et le refus la coupe, ce qui est la seule perte
  sèche ;
- **intacte** : elle ne sautait pas et rien ne l'arrête.

⚠⚠ LA VICTOIRE EST JOINTE, comme depuis `147` : une règle ne vaut sur une matière que si **toute**
marche qui saute y est arrêtée à temps **et** qu'**aucune** marche propre n'y est perdue. Les deux,
jamais l'un des deux.

⚠⚠ CONTRÔLE OBLIGATOIRE ET VIDE : sur la spirale NUE aucun pas ne saute, donc il n'y a rien à
arrêter — et aucune règle ne doit y couper une seule marche.

Usage :
    uv run python src/nappe/le_refus_arrive_t_il_a_temps.py --verifier
    uv run python src/nappe/le_refus_arrive_t_il_a_temps.py \\
        --json docs/mesures/le_refus_arrive_t_il_a_temps.json
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))

from la_pince_tient_elle_la_feuille import (AVANCE_EN_LONGUEUR_DONDE,  # noqa: E402
                                            LARGEUR_DE_REFERENCE, LONGUEUR_DONDE_UM, MATIERES,
                                            RAYON_MM, _matiere, _nom, _PAS, _VOXEL, suivre,
                                            un_depart)

BRUITS = (0.0, 8.0, 16.0)
DEPARTS = 12
TOURS = 1.0
FENETRE = 32
BRAS = (("la pince de `144`", True, True, False),
        ("une mâchoire avec rejet", False, False, True))
ENONCES = ("absolu", "relatif", "etalement")
CAS = ("a_temps", "trop_tard", "jamais", "arretee_pour_rien", "intacte")
LA_SPIRALE_NUE = (0.0, 0.0)


def _cadre():
    return _PAS(), _VOXEL(), AVANCE_EN_LONGUEUR_DONDE * LONGUEUR_DONDE_UM


def _marcher(vol, k, departs, pas_um, voxel_um, avance_um, bras):
    _n, deux, contrainte, rejeter = bras
    depart, n0 = un_depart(vol, 2.0 * np.pi * k / int(departs), RAYON_MM, voxel_um, pas_um)
    vol.lectures = 0
    return suivre(vol, depart, n0, LARGEUR_DE_REFERENCE * pas_um, pas_um, voxel_um, deux,
                  contrainte, avance_um, vol.centre_yx_vx, tours=TOURS, fenetre_du_cap=FENETRE,
                  rejeter=rejeter, derouler_exactement=True)


def elle_tient(comptes: dict) -> bool:
    """La victoire JOINTE, dite UNE seule fois.

    ⚠⚠⚠ ELLE ETAIT ECRITE DEUX FOIS — dans le resume d'une case et dans le cumul d'un groupe — et
    deux calculs d'un meme predicat sont deux occasions de ne pas s'accorder. Trouve en tentant de
    casser le code : l'ancre de la sonde apparaissait deux fois, ce qui EST le symptome.

    Trois moities, et il faut les trois : aucune marche arretee trop tard, aucune panne
    silencieuse, aucune marche propre perdue. Chacune prise seule est satisfaite par une regle
    inutile — celle qui ne se declenche jamais ne perd aucune marche propre.
    """
    return bool(comptes["trop_tard"] == 0 and comptes["jamais"] == 0
                and comptes["arretee_pour_rien"] == 0)


def le_cas(saut, refus) -> str:
    """Le cas d'UNE marche sous UNE règle — cinq cas exhaustifs et exclusifs.

    ⚠⚠ « À TEMPS » EST UNE INÉGALITÉ LARGE, et c'est le sens qui rend la revendication plus DURE :
    un refus qui tombe exactement sur le pas qui saute arrête la marche avant que ce pas ne soit
    livré, donc ce qui sort est propre. Le prendre au sens strict aurait classé « trop tard » un
    arrêt parfaitement placé.

    ⚠⚠ ET UN REFUS ABSENT N'EST PAS UN REFUS AU PAS ZÉRO : la règle ne s'est jamais déclenchée.
    """
    if saut is None:
        return "arretee_pour_rien" if refus is not None else "intacte"
    if refus is None:
        return "jamais"
    return "a_temps" if int(refus) <= int(saut) else "trop_tard"


def _classer(x: dict, regle: str) -> tuple[str, int | None, int | None]:
    """Le cas d'une marche, l'écart signé, et les pas perdus s'il y en a."""
    saut = x.get("premier_saut")
    refus = x.get(f"premier_refus_de_l_{regle}")
    cas = le_cas(saut, refus)
    ecart = (int(refus) - int(saut)) if (saut is not None and refus is not None) else None
    # ⚠ Les pas PERDUS n'ont de sens que pour une marche coupée : ce que la marche aurait encore
    # parcouru. Pour une marche qui saute, ce n'est pas une perte mais un salut.
    perdus = (int(x["pas_examines"]) - int(refus)) if cas == "arretee_pour_rien" else None
    return cas, ecart, perdus


def _resume(xs: list[dict]) -> dict:
    """Ce qu'un paquet de marches dit de chaque règle d'ARRÊT."""
    dec = [x for x in xs if x.get("decidable") and x.get("pas_examines") is not None]
    sans = sum(1 for x in xs if x.get("decidable") and x.get("pas_examines") is None)
    base = {"marches": len(xs), "decidables": len(dec), "marches_sans_un_pas": int(sans)}
    if not dec:
        return {**base, "decidable": False, "raison": "aucune marche décidable qui ait fait un pas"}
    out = {**base, "decidable": True,
           "marches_qui_sautent": int(sum(1 for x in dec if x.get("premier_saut") is not None))}
    for regle in ENONCES:
        if any(f"premier_refus_de_l_{regle}" not in x for x in dec):
            continue
        comptes = dict.fromkeys(CAS, 0)
        ecarts, perdus = [], []
        for x in dec:
            cas, ecart, perdu = _classer(x, regle)
            comptes[cas] += 1
            if ecart is not None:
                ecarts.append(ecart)
            if perdu is not None:
                perdus.append(perdu)
        out[regle] = {
            **comptes,
            "ecart_median": (int(statistics.median(ecarts)) if ecarts else None),
            "pas_perdus_median": (int(statistics.median(perdus)) if perdus else None),
            "pas_perdus_total": int(sum(perdus)),
            "elle_tient": elle_tient(comptes)}
    return out


def lepreuve(matieres=MATIERES, bruits=BRUITS, bras=BRAS, departs: int = DEPARTS) -> dict:
    """Où le premier refus tombe, matière par matière et bras par bras."""
    from combien_de_pas_la_matiere_porte import (  # noqa: PLC0415
        VolumeFabriqueEnSpiraleFroissee)

    pas_um, voxel_um, avance_um = _cadre()
    cases = []
    for b in bras:
        for ecr, amp in matieres:
            for bruit in bruits:
                vol = _matiere(VolumeFabriqueEnSpiraleFroissee, ecr, amp, bruit,
                               LONGUEUR_DONDE_UM, RAYON_MM)
                xs = [_marcher(vol, k, departs, pas_um, voxel_um, avance_um, b)
                      for k in range(int(departs))]
                cases.append({"bras": b[0], "nom": _nom(ecr, amp), "ecrasement": float(ecr),
                              "amplitude_um": float(amp), "bruit": float(bruit),
                              "departs": int(departs), **_resume(xs)})
    return {"decidable": bool(cases), "cases": cases, "bras": [b[0] for b in bras],
            "enonces": list(ENONCES), "bruits": [float(b) for b in bruits],
            "departs": int(departs)}


def _cumuler(cs: list[dict], nom: str) -> dict:
    """Les comptes d'un groupe — des SOMMES de comptes, et les médianes de médianes à part."""
    dec = [c for c in cs if c.get("decidable")]
    out = {"nom": nom, "cases": len(cs), "cases_decidables": len(dec),
           "decidables": int(sum(c.get("decidables", 0) for c in cs)),
           "marches_qui_sautent": int(sum(c.get("marches_qui_sautent", 0) for c in dec))}
    for regle in ENONCES:
        parts = [c[regle] for c in dec if c.get(regle) is not None]
        if not parts:
            continue
        comptes = {k: int(sum(p[k] for p in parts)) for k in CAS}
        ec = [p["ecart_median"] for p in parts if p["ecart_median"] is not None]
        pe = [p["pas_perdus_median"] for p in parts if p["pas_perdus_median"] is not None]
        out[regle] = {
            **comptes,
            "ecart_median": (int(statistics.median(ec)) if ec else None),
            "pas_perdus_median": (int(statistics.median(pe)) if pe else None),
            "pas_perdus_total": int(sum(p["pas_perdus_total"] for p in parts)),
            "elle_tient": elle_tient(comptes)}
    return out


def par_matiere(d: dict) -> list[dict]:
    return [_cumuler([c for c in d["cases"] if c["nom"] == nom], nom)
            for nom in dict.fromkeys(c["nom"] for c in d["cases"])]


def par_bras(d: dict) -> list[dict]:
    return [_cumuler([c for c in d["cases"] if c["bras"] == b], b)
            for b in dict.fromkeys(c["bras"] for c in d["cases"])]


def juger(d: dict) -> dict:
    """Où chaque règle d'arrêt tient, et le contrôle VIDE qui rend la réponse lisible."""
    if not d.get("decidable"):
        return {"decidable": False, "raison": "aucune case mesurée"}
    mat, bras = par_matiere(d), par_bras(d)
    nue = next((m for m in mat if m["nom"] == _nom(*LA_SPIRALE_NUE)), None)
    coupe = {r: (nue.get(r, {}) or {}).get("arretee_pour_rien") for r in ENONCES} if nue else {}
    controle = {"nom": nue["nom"] if nue else None,
                "marches_qui_sautent": nue["marches_qui_sautent"] if nue else None,
                "marches_coupees": coupe,
                "decidables": nue["decidables"] if nue else None}
    controle["il_est_vide"] = bool(
        nue is not None and controle["marches_qui_sautent"] == 0
        and any(v is not None for v in coupe.values())
        and all(v == 0 for v in coupe.values() if v is not None))
    return {"decidable": True, "par_matiere": mat, "par_bras": bras,
            "tout": _cumuler(d["cases"], "tout"),
            "le_controle_de_la_spirale_nue": controle,
            # ⭐⭐⭐⭐ ET LA RÉPONSE : sur quelles matières chaque règle tient-elle la victoire
            # JOINTE ? Un compte de matières, jamais une moyenne de taux.
            "matieres_ou_elle_tient": {
                r: [m["nom"] for m in mat if (m.get(r) or {}).get("elle_tient")]
                for r in ENONCES},
            "elle_tient_par_bras": {
                g["nom"]: {r: (g.get(r) or {}).get("elle_tient") for r in ENONCES} for g in bras}}


def mesurer(matieres=MATIERES, bruits=BRUITS, bras=BRAS, departs: int = DEPARTS) -> dict:
    d = lepreuve(matieres, bruits, bras, departs)
    return {"epreuve": d, "juger": juger(d)}


def reagreger(r: dict) -> dict:
    r["juger"] = juger(r["epreuve"])
    return r


def _court(nom: str) -> str:
    return (nom.replace("spirale ", "").replace("écrasée et froissée", "écr+fro")
            .replace("froissée", "fro").replace("écrasée", "écr")
            .replace("la pince de `144`", "la pince")
            .replace("une mâchoire avec rejet", "mâchoire seule"))


def afficher(r: dict) -> None:
    if "message" in r:
        print(f"⚠ {r['message']}")
        return
    j = r["juger"]
    if not j.get("decidable"):
        print(f"⚠ {j.get('raison', 'indécidable')}")
        return
    c = j["le_controle_de_la_spirale_nue"]
    marque = "★" if c["il_est_vide"] else "✗"
    coupe = " · ".join(f"{k} {v}" for k, v in c["marches_coupees"].items())
    print(f"{marque} contrôle — sur la spirale NUE, {c['marches_qui_sautent']} marche qui saute "
          f"sur {c['decidables']}, et aucune coupée : {coupe}")
    for titre, groupes in (("par bras", j["par_bras"]), ("par matière", j["par_matiere"])):
        print(f"\n   — {titre} —  (à temps · trop tard · jamais · pour rien · intacte)")
        for g in groupes:
            print(f"   {_court(g['nom']):>22} | saute {g['marches_qui_sautent']:>3}"
                  f"/{g['decidables']:<3}")
            for regle in ENONCES:
                t = g.get(regle)
                if t is None:
                    continue
                tient = "★" if t["elle_tient"] else " "
                ec = "—" if t["ecart_median"] is None else f"{t['ecart_median']:+d}"
                pe = "—" if t["pas_perdus_median"] is None else str(t["pas_perdus_median"])
                print(f"   {'':>22} | {tient} {regle:>10} : "
                      f"{t['a_temps']:>3} · {t['trop_tard']:>3} · {t['jamais']:>3} · "
                      f"{t['arretee_pour_rien']:>3} · {t['intacte']:>3}"
                      f"   écart {ec:>4}   perdus {pe}")
    print("\n★★★★ où la victoire JOINTE tient (arrêtée à temps partout ET aucune marche propre "
          "perdue) :")
    for regle, noms in j["matieres_ou_elle_tient"].items():
        print(f"      {regle:>10} : {', '.join(_court(n) for n in noms) if noms else 'nulle part'}")


def _suivi(pas: int, saut, refus: dict) -> dict:
    out = {"decidable": True, "pas_examines": int(pas), "premier_saut": saut}
    for regle in ENONCES:
        out[f"premier_refus_de_l_{regle}"] = refus.get(regle)
    return out


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

    print("— les cinq cas sont exhaustifs et exclusifs —")
    v("⭐⭐⭐ un refus AVANT le saut arrête à temps", le_cas(10, 4) == "a_temps")
    # ⚠⚠ L'INEGALITE EST LARGE, et c'est le sens qui rend la revendication plus DURE : un refus
    # tombant sur le pas qui saute arrete AVANT que ce pas ne soit livre.
    v("⭐⭐⭐⭐ un refus EXACTEMENT sur le pas qui saute arrête encore à temps",
      le_cas(10, 10) == "a_temps" and le_cas(10, 11) == "trop_tard",
      "au sens strict, un arrêt parfaitement placé aurait été compté trop tard")
    v("⭐⭐⭐ une marche qui saute sans qu'aucune règle ne le dise est la panne SILENCIEUSE",
      le_cas(10, None) == "jamais")
    v("⭐⭐⭐⭐ une marche qui ne saute PAS et qu'on coupe est la seule perte sèche",
      le_cas(None, 4) == "arretee_pour_rien" and le_cas(None, None) == "intacte")
    v("⚠⚠ un refus absent n'est PAS un refus au pas zéro",
      le_cas(10, None) != le_cas(10, 0) and le_cas(10, 0) == "a_temps")
    tous = {le_cas(s, r) for s in (None, 5) for r in (None, 3, 5, 9)}
    v("⚠ les cinq cas sont atteignables et il n'y en a pas un sixième",
      tous <= set(CAS) and len(tous) == 5, f"{sorted(tous)}")

    print("— l'écart et les pas perdus disent des choses différentes —")
    x = _suivi(300, 10, {"etalement": 9})
    cas, ecart, perdus = _classer(x, "etalement")
    v("⭐⭐⭐ l'écart est SIGNÉ et vaut la distance au saut", cas == "a_temps" and ecart == -1
      and perdus is None, "une marche qui saute n'a pas de pas PERDUS, elle a un salut")
    y = _suivi(300, None, {"etalement": 40})
    cas2, ecart2, perdus2 = _classer(y, "etalement")
    v("⭐⭐⭐⭐ les pas perdus ne se comptent QUE sur une marche coupée pour rien",
      cas2 == "arretee_pour_rien" and perdus2 == 260 and ecart2 is None,
      "260 pas que la marche aurait encore parcourus proprement")

    print("\n— la victoire est JOINTE —")
    # ⚠⚠⚠ LE PREDICAT EST DIT UNE SEULE FOIS : il etait ecrit dans le resume ET dans le cumul, et
    # deux calculs d'un meme predicat sont deux occasions de diverger. La sonde par cassure l'a
    # revele en butant sur une ancre qui apparaissait deux fois.
    plein = dict.fromkeys(CAS, 0)
    v("⭐⭐⭐⭐ les TROIS moitiés sont exigées, et chacune prise seule laisse passer une règle inutile",
      elle_tient(plein) is True
      and all(elle_tient({**plein, k: 1}) is False
              for k in ("trop_tard", "jamais", "arretee_pour_rien"))
      and elle_tient({**plein, "intacte": 9, "a_temps": 9}) is True,
      "ni une marche intacte ni une marche arrêtée à temps ne peuvent la faire tomber")
    parfaite = _resume([_suivi(300, 10, {r: 9 for r in ENONCES}),
                        _suivi(300, None, {r: None for r in ENONCES})])
    v("⭐⭐⭐⭐ elle tient quand toute marche qui saute est arrêtée à temps ET aucune propre perdue",
      parfaite["etalement"]["elle_tient"] is True
      and parfaite["etalement"]["a_temps"] == 1 and parfaite["etalement"]["intacte"] == 1)
    # ⚠⚠⚠ UNE SEULE DES DEUX MOITIES EST SATISFAITE PAR UNE REGLE INUTILE : celle qui ne se
    # declenche jamais ne perd aucune marche propre.
    inutile = _resume([_suivi(300, 10, {r: None for r in ENONCES}),
                       _suivi(300, None, {r: None for r in ENONCES})])
    v("⭐⭐⭐⭐ ... et une règle qui ne se déclenche JAMAIS ne tient pas, faute de la première moitié",
      inutile["etalement"]["elle_tient"] is False
      and inutile["etalement"]["arretee_pour_rien"] == 0
      and inutile["etalement"]["jamais"] == 1,
      "elle ne perd aucune marche propre, ce qui satisferait la moitié qui flatte")
    trop = _resume([_suivi(300, 10, {r: 11 for r in ENONCES})])
    v("⭐⭐⭐ ... ni une règle qui arrive trop tard", trop["etalement"]["elle_tient"] is False)
    coupeuse = _resume([_suivi(300, 10, {r: 9 for r in ENONCES}),
                        _suivi(300, None, {r: 40 for r in ENONCES})])
    v("⭐⭐⭐ ... ni une règle qui coupe une marche propre",
      coupeuse["etalement"]["elle_tient"] is False
      and coupeuse["etalement"]["pas_perdus_total"] == 260)

    print("\n— le résumé et le cumul somment des COMPTES —")
    v("⚠ une marche qui n'a fait aucun pas est SAUTÉE et comptée",
      _resume([_suivi(300, 10, {r: 9 for r in ENONCES}), {"decidable": True}]
              )["marches_sans_un_pas"] == 1)
    v("⚠⚠ ... et sans aucune marche décidable le résumé le DIT",
      _resume([{"decidable": True}])["decidable"] is False)
    ca = _resume([_suivi(300, 10, {r: 9 for r in ENONCES})])
    cb = _resume([_suivi(300, None, {r: 40 for r in ENONCES})])
    cum = _cumuler([ca, cb], "deux")
    # ⚠⚠ L'ATTENDU SE DERIVE DES DEUX CASES, jamais ecrit en dur.
    v("⭐⭐⭐ `_cumuler` somme les comptes et retient que la victoire ne tient plus",
      cum["etalement"]["a_temps"] == ca["etalement"]["a_temps"] + cb["etalement"]["a_temps"]
      and cum["etalement"]["arretee_pour_rien"] == 1
      and cum["etalement"]["elle_tient"] is False)

    print("\n— le contrôle de la spirale nue —")
    def case(nom, bras_, xs, dec=None):
        return {"bras": bras_, "nom": nom, "ecrasement": 0.0, "amplitude_um": 0.0, "bruit": 0.0,
                "departs": len(xs), **_resume(xs)}
    propre = [_suivi(300, None, {r: None for r in ENONCES})] * 6
    dure = [_suivi(300, 10, {r: 9 for r in ENONCES})] * 4 + [
        _suivi(300, None, {"absolu": None, "relatif": None, "etalement": 40})] * 2
    bon = {"decidable": True, "bras": ["p"], "enonces": list(ENONCES), "bruits": [0.0],
           "departs": 6, "cases": [case(_nom(*LA_SPIRALE_NUE), "p", propre),
                                   case("dure", "p", dure)]}
    j = juger(bon)
    v("⭐⭐⭐⭐ le contrôle tient quand la spirale nue ne saute pas ET n'est jamais coupée",
      j["le_controle_de_la_spirale_nue"]["il_est_vide"] is True)
    coupee = [_suivi(300, None, {"absolu": None, "relatif": None, "etalement": 10})] * 6
    v("⭐⭐⭐⭐ ... et il TOMBE dès qu'une règle coupe une marche là où rien ne saute",
      juger({**bon, "cases": [case(_nom(*LA_SPIRALE_NUE), "p", coupee), bon["cases"][1]]}
            )["le_controle_de_la_spirale_nue"]["il_est_vide"] is False)
    v("⭐⭐⭐ la victoire jointe se lit PAR MATIÈRE, et l'étalement la perd sur la dure",
      j["matieres_ou_elle_tient"]["etalement"] == [_nom(*LA_SPIRALE_NUE)]
      and "dure" in j["matieres_ou_elle_tient"]["absolu"],
      f"{j['matieres_ou_elle_tient']}")

    print("\n— `mesurer`, `reagreger`, `afficher` —")
    petite = mesurer(matieres=(LA_SPIRALE_NUE,), bruits=(0.0,), bras=(BRAS[0],), departs=2)
    v("⭐⭐⭐ sur la spirale NUE la mesure réelle ne coupe aucune marche",
      petite["juger"]["le_controle_de_la_spirale_nue"]["il_est_vide"] is True,
      f"{petite['juger']['le_controle_de_la_spirale_nue']['marches_coupees']}")
    avant = json.loads(json.dumps(petite["epreuve"]))
    r2 = reagreger(json.loads(json.dumps(petite)))
    v("⭐⭐⭐ `reagreger` ne touche PAS un seul nombre mesuré", r2["epreuve"] == avant)
    tampon = io.StringIO()
    with contextlib.redirect_stdout(tampon):
        afficher({"juger": j, "epreuve": bon})
    sortie = tampon.getvalue()
    v("⚠ `afficher` rend le contrôle, les deux tableaux et le verdict",
      "contrôle" in sortie and "par bras" in sortie and "par matière" in sortie
      and "JOINTE" in sortie, f"{len(sortie)} caractères")
    tampon = io.StringIO()
    with contextlib.redirect_stdout(tampon):
        afficher({"message": "rien à montrer"})
    v("⚠ un message est dit, jamais dessiné", "⚠" in tampon.getvalue())

    print(f"\n{'ALL PASS' if echecs == 0 else '⛔ ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path, default=None)
    p.add_argument("--departs", type=int, default=DEPARTS)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--reagreger", type=Path, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = (reagreger(json.loads(a.reagreger.read_text())) if a.reagreger is not None
         else mesurer(departs=int(a.departs)))
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    afficher(r)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
