"""La dérive est-elle un fluage ou des sauts ? — la question de `158`, posable depuis `159`.

⭐⭐⭐⭐ POURQUOI CE FICHIER. `158` demandait si les feuilles qu'une marche perd en bouclant son tour
sont un **fluage** régulier ou des **sauts** discrets, parce que les deux ne demandent pas la même
suite : des sauts, quelque chose peut les attraper — c'est littéralement « ce qui remplace l'humain
qui corrige le transfert de spire à spire » ; un fluage, aucune correction locale ne le pourra.
`158` a reçu « zéro saut » d'un instrument incapable d'en voir, et `159` a montré pourquoi : le
déroulage de `suivre` **borne tout pas à une demi-feuille par construction**.

⭐⭐⭐ L'ÉNONCÉ N'A AUCUN SEUIL. Les feuilles sont espacées d'une épaisseur, donc « ce pas a franchi
plus d'une **demi**-feuille » et « ce pas a changé de feuille » sont le MÊME énoncé — celui du
demi-pas de la contrainte de `142` et de la demi-épaisseur du rejet de `155`.

⚠⚠ ET LA DÉCOMPOSITION EST EXACTE : `dérive exacte = somme des sauts + somme du fluage`, terme à
terme. Publier l'une des deux parts sans l'autre laisserait croire à un reste négligeable, et c'est
précisément ce qu'il faut mesurer plutôt que supposer.

⚠ La spirale NUE est le contrôle : `159` y mesure zéro pas replié à tort, donc la décomposition doit
y rendre zéro saut et un fluage égal à la dérive repliée. Une décomposition qui trouverait des sauts
là où l'instrument est exact mesurerait son propre bruit.

Usage :
    uv run python src/nappe/le_fluage_ou_les_sauts.py --verifier
    uv run python src/nappe/le_fluage_ou_les_sauts.py \\
        --json docs/mesures/le_fluage_ou_les_sauts.json
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
# (nom, deux, contrainte, rejeter) — la barre de `144`, et le bras qui boucle des tours sur la
# matière du rouleau depuis `158`.
REGLES = (("la pince de `144`", True, True, False),
          ("une mâchoire avec rejet", False, False, True))
LA_SPIRALE_NUE = (0.0, 0.0)


def _cadre():
    return _PAS(), _VOXEL(), AVANCE_EN_LONGUEUR_DONDE * LONGUEUR_DONDE_UM


def _marcher(vol, k, departs, pas_um, voxel_um, avance_um, regle):
    _n, deux, contrainte, rejeter = regle
    depart, n0 = un_depart(vol, 2.0 * np.pi * k / int(departs), RAYON_MM, voxel_um, pas_um)
    vol.lectures = 0
    return suivre(vol, depart, n0, LARGEUR_DE_REFERENCE * pas_um, pas_um, voxel_um, deux,
                  contrainte, avance_um, vol.centre_yx_vx, tours=TOURS, fenetre_du_cap=FENETRE,
                  rejeter=rejeter, derouler_exactement=True)


def _resume(xs: list[dict]) -> dict:
    """Ce qu'un paquet de marches dit de la décomposition.

    ⚠⚠ LA DISPERSION EST PUBLIÉE AVEC LA MÉDIANE. Treize marches ne portent pas une médiane toutes
    seules, et un partage qui serait net sur l'une et inversé sur l'autre se lirait comme un partage
    moyen. Le compte de marches où les sauts l'emportent est un COMPTE, pas une moyenne.

    ⚠ Une marche qui n'a pas marché ne dérive pas : elle est SAUTÉE et comptée à part.
    """
    # ⚠⚠ UNE MARCHE QUI N'A FAIT AUCUN PAS N'A PAS DE DECOMPOSITION, et ce n'est pas une
    # decomposition NULLE : `_le_deroulage_exact` ne rend rien quand il n'y a qu'une seule phase.
    # Elle est donc SAUTEE et COMPTEE a part — payé ici, la mesure a levé sur la matière du rouleau
    # à bruit nul, où la pince ne franchit pas son premier pas.
    dec = [x for x in xs if x.get("decidable")
           and x.get("derive_exacte_en_feuilles") is not None]
    sans_pas = sum(1 for x in xs if x.get("decidable")
                   and x.get("derive_exacte_en_feuilles") is None)
    if not dec:
        return {"decidable": False, "raison": "aucune marche décidable qui ait fait un pas",
                "marches": len(xs), "marches_sans_un_pas": sans_pas}
    ex = [abs(float(x["derive_exacte_en_feuilles"])) for x in dec]
    sa = [abs(float(x["derive_des_sauts_en_feuilles"])) for x in dec]
    fl = [abs(float(x["derive_du_fluage_en_feuilles"])) for x in dec]
    pas = [int(x["pas"]) for x in dec]
    qs = [int(x["pas_qui_sautent"]) for x in dec]
    # ⚠⚠ LA PART DES PAS QUI SAUTENT SE CALCULE PAR MARCHE PUIS SE MÉDIANE, jamais sur les totaux :
    # une grille de totaux moyennerait sur l'axe où la différence vit.
    parts = [q / p for q, p in zip(qs, pas) if p]
    return {"decidable": True, "marches": len(xs), "decidables": len(dec),
            "marches_sans_un_pas": sans_pas,
            "derive_exacte_mediane": round(float(statistics.median(ex)), 4),
            "derive_exacte_max": round(float(max(ex)), 4),
            "derive_repliee_mediane": round(float(statistics.median(
                [abs(float(x["derive_en_feuilles"])) for x in dec])), 4),
            "sauts_medians": round(float(statistics.median(sa)), 4),
            "fluage_median": round(float(statistics.median(fl)), 4),
            "pas_qui_sautent": int(sum(qs)), "pas_marches": int(sum(pas)),
            "part_des_pas_qui_sautent_mediane": (round(float(statistics.median(parts)), 4)
                                                 if parts else None),
            # ⭐⭐ LE COMPTE QUI TRANCHE : sur combien de marches les SAUTS portent-ils plus que le
            # fluage ? C'est un compte de marches, et il survit à une population bimodale là où une
            # médiane de rapports n'y survivrait pas.
            "marches_ou_les_sauts_lemportent": int(sum(1 for a, b in zip(sa, fl) if a > b)),
            "marches_sans_aucun_saut": int(sum(1 for q in qs if q == 0))}


def la_decomposition(matieres=MATIERES, bruits=BRUITS, regles=REGLES,
                     departs: int = DEPARTS) -> dict:
    """Où la dérive se fait, matière par matière et règle par règle."""
    from combien_de_pas_la_matiere_porte import (  # noqa: PLC0415
        VolumeFabriqueEnSpiraleFroissee)

    pas_um, voxel_um, avance_um = _cadre()
    cases = []
    for regle in regles:
        for ecr, amp in matieres:
            for bruit in bruits:
                vol = _matiere(VolumeFabriqueEnSpiraleFroissee, ecr, amp, bruit,
                               LONGUEUR_DONDE_UM, RAYON_MM)
                xs = [_marcher(vol, k, departs, pas_um, voxel_um, avance_um, regle)
                      for k in range(int(departs))]
                cases.append({"regle": regle[0], "nom": _nom(ecr, amp),
                              "ecrasement": float(ecr), "amplitude_um": float(amp),
                              "bruit": float(bruit), "departs": int(departs),
                              **_resume(xs)})
    return {"decidable": bool(cases), "cases": cases,
            "regles": [r[0] for r in regles], "bruits": [float(b) for b in bruits],
            "departs": int(departs)}


def par_matiere(d: dict) -> list[dict]:
    """Le partage matière par matière, toutes règles et tous bruits confondus."""
    out = []
    for nom in dict.fromkeys(c["nom"] for c in d["cases"]):
        cs = [c for c in d["cases"] if c["nom"] == nom and c.get("decidable")]
        if not cs:
            continue
        out.append({
            "nom": nom,
            "decidables": int(sum(c["decidables"] for c in cs)),
            "pas_qui_sautent": int(sum(c["pas_qui_sautent"] for c in cs)),
            "pas_marches": int(sum(c["pas_marches"] for c in cs)),
            "marches_sans_aucun_saut": int(sum(c["marches_sans_aucun_saut"] for c in cs)),
            "marches_ou_les_sauts_lemportent": int(sum(c["marches_ou_les_sauts_lemportent"]
                                                       for c in cs)),
            "derive_exacte_mediane": round(float(statistics.median(
                [c["derive_exacte_mediane"] for c in cs])), 4),
            "derive_repliee_mediane": round(float(statistics.median(
                [c["derive_repliee_mediane"] for c in cs])), 4)})
    return out


def juger(d: dict) -> dict:
    """Fluage ou sauts — et le contrôle qui rend la réponse lisible.

    ⚠⚠⚠ LA SPIRALE NUE EST LE CONTRÔLE : `159` y mesure zéro pas replié à tort, donc la
    décomposition doit y rendre ZÉRO saut. Une décomposition qui en trouverait là mesurerait son
    propre bruit, et tout le reste du tableau ne voudrait rien dire.
    """
    if not d.get("decidable"):
        return {"decidable": False, "raison": "aucune case mesurée"}
    mat = par_matiere(d)
    nue = next((m for m in mat if m["nom"] == _nom(*LA_SPIRALE_NUE)), None)
    dure = max(mat, key=lambda m: m["pas_qui_sautent"])
    return {"decidable": True, "par_matiere": mat,
            "le_controle_de_la_spirale_nue": {
                "nom": nue["nom"] if nue else None,
                "pas_qui_sautent": nue["pas_qui_sautent"] if nue else None,
                "marches_sans_aucun_saut": nue["marches_sans_aucun_saut"] if nue else None,
                "decidables": nue["decidables"] if nue else None,
                "il_tient": bool(nue is not None and nue["pas_qui_sautent"] == 0
                                 and nue["marches_sans_aucun_saut"] == nue["decidables"])},
            "la_matiere_qui_saute_le_plus": dure["nom"],
            # ⭐⭐⭐⭐ ET LA RÉPONSE : les deux parts sont-elles du même ordre, ou l'une écrase-t-elle
            # l'autre ? Le compte de marches où les sauts l'emportent le dit sans moyenner.
            "marches_ou_les_sauts_lemportent": int(sum(m["marches_ou_les_sauts_lemportent"]
                                                       for m in mat)),
            "marches_sans_aucun_saut": int(sum(m["marches_sans_aucun_saut"] for m in mat)),
            "decidables": int(sum(m["decidables"] for m in mat)),
            # ⚠⚠ ET LE FAIT QUI REND LE RESTE LISIBLE : la dérive REPLIÉE est petite là où l'exacte
            # est énorme, parce que le repliement efface chaque changement de feuille.
            "le_repliement_cache_la_derive": bool(
                dure["derive_repliee_mediane"] < dure["derive_exacte_mediane"])}


def mesurer(matieres=MATIERES, bruits=BRUITS, regles=REGLES, departs: int = DEPARTS) -> dict:
    d = la_decomposition(matieres, bruits, regles, departs)
    return {"decomposition": d, "juger": juger(d)}


def reagreger(r: dict) -> dict:
    """Recalcule le verdict depuis les cases rangées — sans remarcher."""
    r["juger"] = juger(r["decomposition"])
    return r


def afficher(r: dict) -> None:
    if "message" in r:
        print(f"⚠ {r['message']}")
        return
    j = r["juger"]
    if not j.get("decidable"):
        print(f"⚠ {j.get('raison', 'indécidable')}")
        return
    c = j["le_controle_de_la_spirale_nue"]
    marque = "★" if c["il_tient"] else "✗"
    print(f"{marque} contrôle — la spirale NUE ne saute pas : {c['pas_qui_sautent']} pas, "
          f"{c['marches_sans_aucun_saut']}/{c['decidables']} marches sans aucun saut")
    print(f"\n   {'matière':>34} | {'déc.':>4} | {'pas qui sautent':>15} | {'sans saut':>9} | "
          f"{'repliée':>8} | {'exacte':>9}")
    for m in j["par_matiere"]:
        print(f"   {m['nom']:>34} | {m['decidables']:>4d} | "
              f"{m['pas_qui_sautent']:>7d}/{m['pas_marches']:<7d} | "
              f"{m['marches_sans_aucun_saut']:>9d} | {m['derive_repliee_mediane']:>8.4f} | "
              f"{m['derive_exacte_mediane']:>9.4f}")
    print(f"\n   la matière qui saute le plus : « {j['la_matiere_qui_saute_le_plus']} »")
    print(f"   marches où les SAUTS l'emportent sur le fluage : "
          f"{j['marches_ou_les_sauts_lemportent']} sur {j['decidables']}")
    print(f"   marches sans AUCUN saut : {j['marches_sans_aucun_saut']} sur {j['decidables']}")
    print(f"\n{'★★★★' if j['le_repliement_cache_la_derive'] else '✗'} le repliement CACHE-t-il la "
          f"dérive ? {j['le_repliement_cache_la_derive']}")



def _suivi(pas: int, exacte: float, sauts: float, fluage: float, qui_sautent: int,
           repliee: float = 0.0) -> dict:
    return {"decidable": True, "pas": int(pas), "derive_exacte_en_feuilles": float(exacte),
            "derive_des_sauts_en_feuilles": float(sauts),
            "derive_du_fluage_en_feuilles": float(fluage),
            "pas_qui_sautent": int(qui_sautent), "derive_en_feuilles": float(repliee)}


def verifier() -> int:
    import contextlib  # noqa: PLC0415
    import io  # noqa: PLC0415

    from la_pince_tient_elle_la_feuille import _le_deroulage_exact  # noqa: PLC0415

    echecs = controles = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    print("— la décomposition est EXACTE, pas approchée —")
    # Une serie dont un pas franchit 0,8 feuille, un autre 0,3, un troisieme 1,4.
    ph = [0.0, 0.8, 1.1, 2.5]
    an = [0.0, 0.01, 0.02, 0.03]
    ex = _le_deroulage_exact(ph, an)
    v("⭐⭐⭐⭐ `exacte = sauts + fluage`, terme à terme",
      abs(ex["derive_des_sauts_en_feuilles"] + ex["derive_du_fluage_en_feuilles"]
          - ex["derive_exacte_en_feuilles"]) < 1e-9,
      f"{ex['derive_des_sauts_en_feuilles']} + {ex['derive_du_fluage_en_feuilles']} = "
      f"{ex['derive_exacte_en_feuilles']}")
    v("⭐⭐⭐ ... et les deux pas au-delà d'une demi-feuille sont comptés, le troisième non",
      ex["pas_qui_sautent"] == 2
      and abs(ex["derive_du_fluage_en_feuilles"] - 0.3) < 1e-9,
      f"{ex['pas_qui_sautent']} pas sautent, fluage {ex['derive_du_fluage_en_feuilles']}")
    # ⚠⚠ LA BORNE EST STRICTE : un pas d'EXACTEMENT une demi-feuille n'a pas change de feuille.
    ex2 = _le_deroulage_exact([0.0, 0.5, 1.0], [0.0, 0.01, 0.02])
    v("⚠⚠ un pas d'exactement une demi-feuille ne SAUTE pas — la borne est stricte",
      ex2["pas_qui_sautent"] == 0 and abs(ex2["derive_du_fluage_en_feuilles"] - 1.0) < 1e-9)

    print("\n— le résumé ne moyenne pas sur l'axe où la différence vit —")
    # Deux marches : l'une courte qui saute beaucoup, l'autre longue qui ne saute presque pas.
    # ⚠⚠ LA FIXTURE DOIT DISCRIMINER : avec DEUX marches, un compte de marches et une comparaison
    # de TOTAUX rendent tous deux 1, donc la sonde ne mordait pas. Trois marches, dont deux où les
    # sauts l'emportent, séparent les deux lectures — vérifié en cassant le code.
    xs = [_suivi(10, 9.0, 8.0, 1.0, 8), _suivi(1000, 3.0, 1.0, 2.0, 2),
          _suivi(100, 5.0, 4.0, 1.0, 40)]
    r = _resume(xs)
    v("⭐⭐⭐ la part des pas qui sautent se calcule PAR MARCHE puis se médiane",
      abs(r["part_des_pas_qui_sautent_mediane"] - 0.4) < 1e-9,
      f"{r['part_des_pas_qui_sautent_mediane']} — et non "
      f"{(8 + 2 + 40) / (10 + 1000 + 100):.4f} qui serait le rapport des totaux")
    v("⭐⭐ « les sauts l'emportent » est un COMPTE de marches, pas une comparaison de totaux",
      r["marches_ou_les_sauts_lemportent"] == 2 and r["marches_sans_aucun_saut"] == 0,
      f"{r['marches_ou_les_sauts_lemportent']} sur {r['decidables']} — une comparaison de totaux "
      f"ne pourrait rendre que 0 ou 1")
    # ⚠⚠ L'ATTENDU SE DÉRIVE DE LA FIXTURE : écrit en dur, il est devenu faux à la marche que je
    # venais d'ajouter pour rendre la sonde précédente discriminante.
    avec_absente = _resume(xs + [{"decidable": False}])
    v("⚠ une marche qui n'a pas marché est SAUTÉE et comptée à part",
      avec_absente["decidables"] == len(xs) and avec_absente["marches"] == len(xs) + 1,
      f"{avec_absente['decidables']} décidables sur {avec_absente['marches']}")
    v("⚠⚠ ... et sans aucune marche décidable, le résumé le DIT au lieu de rendre zéro",
      _resume([{"decidable": False}])["decidable"] is False)
    # ⚠⚠⚠ UNE MARCHE QUI N'A FAIT AUCUN PAS N'A PAS DE DÉCOMPOSITION, et ce n'est pas une
    # décomposition NULLE. Payé : la mesure a levé sur la matière du rouleau à bruit nul, où la
    # pince ne franchit pas son premier pas et où `_le_deroulage_exact` ne rend donc rien.
    zero_pas = {"decidable": True, "pas": 0, "derive_en_feuilles": 0.0}
    avec_zero = _resume(xs + [zero_pas])
    v("⭐⭐⭐ une marche SANS AUCUN PAS est sautée et COMPTÉE, jamais lue comme une dérive nulle",
      avec_zero["decidables"] == len(xs) and avec_zero["marches_sans_un_pas"] == 1
      and avec_zero["derive_exacte_mediane"] == r["derive_exacte_mediane"],
      f"{avec_zero['marches_sans_un_pas']} marche sans un pas, médiane inchangée")
    v("⚠⚠ ... et si AUCUNE n'a fait un pas, le résumé le dit et compte quand même",
      _resume([zero_pas, zero_pas])["decidable"] is False
      and _resume([zero_pas, zero_pas])["marches_sans_un_pas"] == 2)

    print("\n— le contrôle de la spirale nue —")
    def case(nom, sans_saut, qui_sautent, dec=12):
        return {"regle": "r", "nom": nom, "ecrasement": 0.0, "amplitude_um": 0.0, "bruit": 0.0,
                "departs": dec, "decidable": True, "marches": dec, "decidables": dec,
                "derive_exacte_mediane": 30.0 if qui_sautent else 0.02,
                "derive_exacte_max": 40.0, "derive_repliee_mediane": 0.4 if qui_sautent else 0.02,
                "sauts_medians": 20.0 if qui_sautent else 0.0, "fluage_median": 10.0,
                "pas_qui_sautent": qui_sautent, "pas_marches": 1000,
                "part_des_pas_qui_sautent_mediane": 0.1 if qui_sautent else 0.0,
                "marches_ou_les_sauts_lemportent": 9 if qui_sautent else 0,
                "marches_sans_aucun_saut": sans_saut}
    bon = {"decidable": True, "regles": ["r"], "bruits": [0.0], "departs": 12,
           "cases": [case("spirale nue", 12, 0), case("spirale écrasée et froissée 100 µm", 0, 900)]}
    j = juger(bon)
    v("⭐⭐⭐⭐ le contrôle tient quand la spirale nue ne saute pas du tout",
      j["le_controle_de_la_spirale_nue"]["il_tient"] is True
      and j["la_matiere_qui_saute_le_plus"] == "spirale écrasée et froissée 100 µm")
    mauvais = {**bon, "cases": [case("spirale nue", 10, 5),
                               case("spirale écrasée et froissée 100 µm", 0, 900)]}
    v("⭐⭐⭐ ... et il TOMBE dès que la spirale nue saute, fût-ce cinq pas",
      juger(mauvais)["le_controle_de_la_spirale_nue"]["il_tient"] is False)
    v("⚠⚠ et le repliement qui cache la dérive est LU sur la matière qui saute le plus",
      j["le_repliement_cache_la_derive"] is True
      and juger({**bon, "cases": [case("spirale nue", 12, 0)]})[
          "le_repliement_cache_la_derive"] is False,
      "sur une matière qui ne saute pas, repliée et exacte coïncident")

    print("\n— `mesurer`, `reagreger`, `afficher` —")
    petite = mesurer(matieres=(LA_SPIRALE_NUE,), bruits=(0.0,), regles=(REGLES[0],), departs=2)
    v("⚠ sur la spirale NUE, aucune marche ne saute",
      petite["juger"]["le_controle_de_la_spirale_nue"]["il_tient"] is True)
    avant = json.loads(json.dumps(petite["decomposition"]))
    r2 = reagreger(json.loads(json.dumps(petite)))
    v("⭐⭐⭐ `reagreger` ne touche PAS un seul nombre mesuré", r2["decomposition"] == avant)
    tampon = io.StringIO()
    with contextlib.redirect_stdout(tampon):
        afficher({"juger": j, "decomposition": bon})
    sortie = tampon.getvalue()
    v("⚠ `afficher` rend le contrôle, le tableau et les deux comptes",
      "contrôle" in sortie and "matière" in sortie and "SAUTS" in sortie,
      f"{len(sortie)} caractères")
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
