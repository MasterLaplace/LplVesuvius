#!/usr/bin/env python3
"""A quel prix peut-on lire le cube ? — l'instrument de `101` et `102`, deux fois moins cher.

⚠⚠⚠ POURQUOI CE FICHIER, ET C'EST `102` QUI L'IMPOSE. `102` a mesure que la matiere porte AU MOINS
deux pas, et sa portee est **censuree** : 17 bandes sur 28 butent sur un plafond de six pas. Relever
ce plafond est donc la marche suivante — mais elle coute **15,4 s par cube** de lecture reseau, donc
trente pas demanderaient **quatorze heures**. Avant de subir ce cout, il faut savoir s'il est
reductible.

⛔⛔⛔ ET ELLE NE L'EST PAS, CE QUE SEUL LE CORPUS ENTIER A PU DIRE. Une economie existait en
principe : echantillonner le cube plus grossierement — un voxel sur deux, MEME portee de 98 µm —
ne change pas ce qu'on regarde, seulement ce qu'on paie. Sur DEUX bandes elle passait haut la main,
0 % de cellules au-dela de dix degres. Sur les VINGT-HUIT, **7,3 %** s'en ecartent — et comme `102`
ENCHAINE les pas, cela abime **36 %** des marches de six pas. Le cube se lit au voxel pres.

⚠⚠⚠ ET C'EST MA PROPRE SONDE QUI ETAIT TOMBEE DANS LE PIEGE que ce depot a deja enregistre deux
fois : *un bord se compte sur le corpus entier, pas sur les bandes qu'on a sondees* (`93`, reecrit
par `95`). J'allais adopter le pas grossier sur deux bandes.

⚠⚠ LE CONTROLE EST APPARIE, ET C'EST TOUTE SA FORCE. Chaque cellule est lue une fois PAR PAS et la
quantite rendue est l'angle entre les reponses. Comparer deux populations differentes ferait dire au
resultat ce qu'on veut, et ce depot l'a deja paye — `derouler_par_le_pas_normal` mesure son temoin
sur les memes cellules, exactement pour ca.

⚠⚠⚠ ET LE COUT SE MESURE, IL NE SE MODELISE PAS. Le comptage de points predisait un gain de SEPT ;
la mesure en rend DEUX. Une lecture distante est dominee par le nombre de PLAGES d'octets — une par
rangee (z, y) — et par un fixe par cube, pas par le nombre de points. Un cube sous-echantillonne
touche toujours une plage par rangee.

⭐⭐ LE PAS RETENU EST DERIVE, PAS CHOISI. Le plus grossier qui satisfait DEUX conditions
independantes : sur un empilement fabrique, l'accord des deux moities passe sous la barre du nul de
SA PROPRE FORME ; sur le vrai volume, AUCUNE cellule ne s'ecarte de plus de dix degres du pas le
plus fin. Un pas de 3 casse la seconde — **15 %** des cellules — et un pas de 4 en casse **40 %**.

⚠ Les primitives vivent dans `101` (`bloc`, `nul_du_tenseur`, `accord_des_moities`) : c'est le module
du cube, et les y laisser evite deux definitions d'une meme forme. Ce fichier ne possede que la
QUESTION du prix.

Usage :
    uv run python src/nappe/le_cube_lu_moins_cher.py --verifier
    uv run python src/nappe/le_cube_lu_moins_cher.py \\
        --json docs/mesures/le_cube_lu_moins_cher.json
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

# ⚠ Les pas balayes vont de 1 a 4 : au-dela, un cube de demi = 20 laisse moins de dix points
# d'arete et l'accord des deux moities ne peut plus RIEN comparer — la garde avoue ne pas savoir
# plutot que de repondre, et c'est le bon mode d'echec.
PAS_BALAYES = (1, 2, 3, 4)
# ⚠⚠ CE SEUIL N'EST PAS UN REGLAGE MAIS UNE ECHELLE PHYSIQUE : dix degres sur une nappe dont
# `101` mesure l'obliquite a 34° est moins d'un tiers de l'ecart qui distingue la matiere du rayon.
# Une direction qui bouge de plus que ca en changeant de finesse ne mesure plus la meme chose.
ECART_TOLERE_DEG = 10.0
CELLULES_PAR_BANDE = 10


def pas_retenu(fabrique: dict, reel: dict,
               tolere: float = ECART_TOLERE_DEG) -> dict:
    """Le pas le plus grossier qui satisfait les DEUX conditions, et pourquoi les autres tombent.

    ⭐⭐⭐ IL EST DERIVE, PAS CHOISI, et les deux conditions sont INDEPENDANTES — l'une vient d'un
    empilement fabrique dont on connait la reponse, l'autre du vrai volume sur cellules appariees.
    Un pas qui ne passerait qu'une des deux serait accepte pour la moitie d'une raison.

    ⚠ La liste des refus est rendue avec eux : « le pas 2 est retenu » ne dit pas pourquoi 3 ne
    l'est pas, et c'est cette raison-la qui empeche de relever le pas plus tard sans la revoir.
    """
    par_pas = {x["pas_echantillon"]: x for x in fabrique.get("lignes", [])}
    reels = {x["pas_echantillon"]: x for x in reel.get("lignes", [])}
    communs = sorted(set(par_pas) & set(reels))
    if not communs:
        return {"message": "aucun pas commun entre le fabriqué et le réel"}
    # ⚠⚠⚠ LE PAS LE PLUS FIN N'EST PAS UNE ECONOMIE A JUGER, C'EST LE STATU QUO. Le compter parmi
    # les candidats produisait la ligne absurde « pas 1 — la garde du fabrique ne tient pas », qui
    # se lit comme un refus de lire le cube en entier. Ce qu'on juge, ce sont les pas PLUS
    # GROSSIERS que la reference, et la reference est rendue a part.
    reference = min(communs)
    verdicts, retenu = [], None
    for pe in [x for x in communs if x > reference]:
        f, r = par_pas[pe], reels[pe]
        garde = bool(f.get("la_garde_tient"))
        accord = bool(r.get("part_au_dela_de_dix_degres", 1.0) <= 0.0)
        ok = garde and accord
        verdicts.append({
            "pas_echantillon": pe,
            "la_garde_du_fabrique_tient": garde,
            "aucune_cellule_reelle_au_dela_du_tolere": accord,
            "part_reelle_au_dela_du_tolere": r.get("part_au_dela_de_dix_degres"),
            "gain_de_temps": r.get("gain_de_temps"),
            "retenu": ok,
            "pourquoi_refuse": (None if ok else
                                ("la garde du fabriqué ne tient pas" if not garde
                                 else "des cellules réelles s'écartent de plus de "
                                      f"{tolere:.0f}°")),
        })
        if ok:
            retenu = pe
    # ⭐⭐⭐ LA CONSEQUENCE SUR UNE MARCHE ENCHAINEE, ET C'EST ELLE QUI DECIDE. Un ecart de plus
    # de dix degres sur 7 % des cellules n'a l'air de rien pris UN pas a la fois — mais `102`
    # ENCHAINE les pas, et la part de marches touchees vaut 1 - (1 - p)^k. A six pas, 7 % par pas
    # font **36 %** de marches abimees. Publier le taux par pas sans sa consequence enchainee
    # laisserait croire l'economie inoffensive.
    for x in verdicts:
        p = x.get("part_reelle_au_dela_du_tolere")
        if p is None:
            continue
        x["part_de_marches_de_six_pas_touchees"] = round(1.0 - (1.0 - p) ** 6, 3)
    ref = par_pas.get(reference, {})
    return {
        "tolere_deg": tolere, "pas_de_reference": reference,
        # ⚠ La reference est DECRITE, jamais jugee : sa garde sur l'empilement fabrique est un
        # fait sur le NIVEAU DE BRUIT teste, pas une raison de ne pas lire le cube en entier.
        "la_garde_du_fabrique_tient_a_la_reference": bool(ref.get("la_garde_tient")),
        "pas_retenu": retenu, "verdicts": verdicts,
        "une_economie_est_possible": retenu is not None,
        "gain_du_pas_retenu": (reels[retenu]["gain_de_temps"]
                               if retenu is not None else None),
    }


def mesurer(cellules: int = CELLULES_PAR_BANDE, demi: int | None = None,
            pas=PAS_BALAYES, bandes_max: int | None = 2, fils: int = 32) -> dict:
    """Le balayage fabrique et le controle apparie sur le vrai volume, plus le pas qu'ils retiennent."""
    import combien_dinterstices_traverses as C  # noqa: PLC0415
    import la_direction_que_la_matiere_montre as D  # noqa: PLC0415

    d = D.DEMI if demi is None else int(demi)
    pas_vx = C.PAS_UM / C.VOXEL_FIN_UM
    fabrique = D.limite_de_sous_echantillonnage(pas_vx, demi=d, pas_echantillon=tuple(pas))
    reel = D.accord_entre_pas(cellules=cellules, demi=d, pas=tuple(pas),
                              bandes_max=bandes_max, fils=fils)
    if "message" in reel:
        return {"message": reel["message"], "fabrique": fabrique}
    return {
        "fragment": C.OBJET, "voxel_fin_um": C.VOXEL_FIN_UM,
        "pas_nominal_um": C.PAS_UM,
        "demi_cube_voxels": d,
        "cote_um_du_cube": round((2 * d + 1) * C.VOXEL_FIN_UM, 1),
        "pas_balayes": list(pas),
        "sur_empilement_fabrique": fabrique,
        "sur_le_vrai_volume": reel,
        "le_pas_retenu": pas_retenu(fabrique, reel),
    }


def afficher(r: dict) -> int:
    """L'affichage, séparé pour que la batterie puisse le lancer — la leçon de `93`."""
    if "message" in r:
        print(f"⚠ {r['message']}")
        return 0
    print(f"{r['fragment']} · cube de {r['cote_um_du_cube']} µm "
          f"({2 * r['demi_cube_voxels'] + 1} voxels d'arête) · même PORTÉE à tous les pas, "
          f"seule la finesse change\n")
    f = r["sur_empilement_fabrique"]
    print("SUR UN EMPILEMENT FABRIQUÉ (réponse connue, bruit σ = "
          f"{f.get('bruit')}) — chaque pas contre la barre de SA forme")
    print(f"{'pas':>4} {'points':>8} {'angle':>8} {'désacc.':>9} {'barre':>8} {'marge':>8}  "
          f"garde")
    for x in f["lignes"]:
        m = x.get("marge_sous_la_barre_deg")
        print(f"{x['pas_echantillon']:>4} {x['points']:>8} {x['angle_deg']:>7.2f}° "
              f"{x['desaccord_des_moities_deg']:>8.2f}° "
              f"{x['barre_de_sa_forme_deg']:>7.2f}° "
              f"{(f'{m:.2f}' if m is not None else 'n/a'):>7}°  "
              f"{'TIENT' if x['la_garde_tient'] else 'NON'}")
    v = r["sur_le_vrai_volume"]
    print(f"\nSUR LE VRAI VOLUME, {v['cellules']} cellules APPARIÉES — chaque cellule lue une "
          f"fois par pas")
    print(f"{'pas':>4} {'rangées':>8} {'s/cube':>8} {'gain':>7} {'écart':>8} {'p90':>7} "
          f"{'>10°':>6}")
    for x in v["lignes"]:
        print(f"{x['pas_echantillon']:>4} {x['rangees_lues']:>8} "
              f"{x['secondes_par_cube']:>8.2f} ×{x['gain_de_temps']:>6.2f} "
              f"{x['ecart_median_au_plus_fin_deg']:>7.2f}° {x['ecart_p90_deg']:>6.2f}° "
              f"{x['part_au_dela_de_dix_degres']:>6.2f}")
    pr = r["le_pas_retenu"]
    if pr["pas_retenu"] is None:
        print("\n⛔⛔ AUCUNE ÉCONOMIE NE PASSE : le cube se lit au voxel près.")
        pire = max((x for x in pr["verdicts"]
                    if x.get("part_de_marches_de_six_pas_touchees") is not None),
                   key=lambda z: -z["pas_echantillon"], default=None)
        moins = min(pr["verdicts"], key=lambda z: z["pas_echantillon"], default=None)
        if moins and moins.get("part_de_marches_de_six_pas_touchees") is not None:
            print(f"   Le moins grossier, le pas {moins['pas_echantillon']}, écarte déjà "
                  f"{100 * moins['part_reelle_au_dela_du_tolere']:.1f} % des cellules de plus")
            print(f"   de {pr['tolere_deg']:.0f}° — ce qui n'a l'air de rien pris UN pas à la "
                  f"fois, mais `102` les ENCHAÎNE :")
            print(f"   à six pas, cela abîme "
                  f"{100 * moins['part_de_marches_de_six_pas_touchees']:.0f} % des marches.")
        del pire
    else:
        print(f"\n★★★ LE PAS RETENU EST {pr['pas_retenu']}, ET IL EST DÉRIVÉ : c'est le plus "
              f"grossier qui passe")
        print(f"   la garde du fabriqué ET n'écarte AUCUNE cellule réelle de plus de "
              f"{pr['tolere_deg']:.0f}°. Il coûte")
        print(f"   ×{pr['gain_du_pas_retenu']:.2f} moins de temps, donc chaque cube de "
              f"{r['cote_um_du_cube']} µm passe de 15,4 s à la moitié.")
    print(f"\n⚠ Le pas de référence est {pr['pas_de_reference']} et il n'est PAS jugé : ce n'est "
          f"pas une économie, c'est le statu quo.")
    print(f"   (sur l'empilement fabriqué à ce bruit, sa garde "
          f"{'tient' if pr['la_garde_du_fabrique_tient_a_la_reference'] else 'ne tient PAS'} — "
          f"un fait sur le niveau de bruit testé, pas une raison de ne pas lire le cube entier.)")
    print("\n⚠ Les refus sont rendus avec leur raison, sinon relever le pas plus tard se ferait "
          "sans la revoir :")
    for x in pr["verdicts"]:
        if x["retenu"]:
            continue
        print(f"   pas {x['pas_echantillon']} — {x['pourquoi_refuse']} "
              f"(part au-delà : {x['part_reelle_au_dela_du_tolere']})")
    print("\n⚠⚠ ET LE GAIN DE TEMPS N'EST PAS LE GAIN DE POINTS : le comptage de points prédisait")
    print("   sept, la mesure rend deux. Une lecture distante est dominée par le nombre de")
    print("   PLAGES d'octets — une par rangée (z, y) — et par un fixe par cube.")
    return 0


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # === LE VERDICT DOIT DEPENDRE DES DEUX CONDITIONS, ET DE CHACUNE SEPAREMENT ============
    def jeu(garde_par_pas, part_par_pas, gains=None):
        gains = gains or {pe: 1.0 + pe for pe in garde_par_pas}
        return (
            {"lignes": [{"pas_echantillon": pe, "la_garde_tient": g}
                        for pe, g in garde_par_pas.items()]},
            {"lignes": [{"pas_echantillon": pe, "part_au_dela_de_dix_degres": p,
                         "gain_de_temps": gains[pe]}
                        for pe, p in part_par_pas.items()]},
        )

    f, r = jeu({1: True, 2: True, 3: True}, {1: 0.0, 2: 0.0, 3: 0.0})
    v("quand les deux conditions tiennent partout, le pas le plus GROSSIER est retenu",
      pas_retenu(f, r)["pas_retenu"] == 3, str(pas_retenu(f, r)["pas_retenu"]))
    # ⚠⚠⚠ LA REFERENCE N'EST PAS UN CANDIDAT. La compter produisait la ligne absurde « pas 1 —
    # la garde ne tient pas », qui se lit comme un refus de lire le cube en entier alors que
    # c'est le statu quo.
    f, r = jeu({1: False, 2: True}, {1: 0.9, 2: 0.0})
    verdict = pas_retenu(f, r)
    v("la référence n'est jamais jugée comme une économie",
      all(x["pas_echantillon"] != 1 for x in verdict["verdicts"]),
      str([x["pas_echantillon"] for x in verdict["verdicts"]]))
    v("... mais son état est DÉCRIT à côté du verdict",
      verdict["la_garde_du_fabrique_tient_a_la_reference"] is False
      and verdict["pas_de_reference"] == 1)
    v("... et une référence en mauvais état n'empêche pas une économie de passer",
      verdict["pas_retenu"] == 2)
    # ⚠⚠ CHAQUE CONDITION DOIT POUVOIR SEULE FAIRE TOMBER UN PAS, sinon l'une des deux ne sert
    # a rien et le verdict serait pris pour la moitie d'une raison.
    f, r = jeu({1: True, 2: True, 3: False}, {1: 0.0, 2: 0.0, 3: 0.0})
    v("la garde du fabriqué seule peut faire tomber un pas",
      pas_retenu(f, r)["pas_retenu"] == 2,
      str([x["pourquoi_refuse"] for x in pas_retenu(f, r)["verdicts"] if not x["retenu"]]))
    f, r = jeu({1: True, 2: True, 3: True}, {1: 0.0, 2: 0.0, 3: 0.15})
    v("... et l'accord sur le VRAI volume seul aussi",
      pas_retenu(f, r)["pas_retenu"] == 2,
      str([x["pourquoi_refuse"] for x in pas_retenu(f, r)["verdicts"] if not x["retenu"]]))
    # ⭐ Et le verdict doit savoir dire « aucun » : sinon il approuverait toujours une economie.
    f, r = jeu({1: True, 2: False, 3: False}, {1: 0.0, 2: 0.5, 3: 0.5})
    aucun = pas_retenu(f, r)
    v("... et il rend « aucun » quand rien ne passe, plutôt qu'un pas par défaut",
      aucun["pas_retenu"] is None and aucun["une_economie_est_possible"] is False)
    # ⭐⭐⭐ ET LA CONSEQUENCE ENCHAINEE EST CALCULEE : un taux par pas n'a l'air de rien pris UN
    # pas a la fois, alors que `102` les ENCHAINE. 1 - (1 - p)^6 est ce qui decide.
    q = next(x for x in aucun["verdicts"] if x["pas_echantillon"] == 2)
    # ⚠ La valeur publiee est ARRONDIE a trois decimales, donc l'attendu doit l'etre aussi :
    # une tolerance plus fine que l'arrondi ferait echouer un calcul juste.
    v("la conséquence sur une marche de six pas est publiée à côté du taux par pas",
      q["part_de_marches_de_six_pas_touchees"] == round(1 - 0.5 ** 6, 3),
      f"{q['part_de_marches_de_six_pas_touchees']} pour un taux de "
      f"{q['part_reelle_au_dela_du_tolere']} par pas")
    # ⚠ Un pas qui ne passe qu'une condition doit etre refuse AVEC la raison qui a mordu.
    f, r = jeu({1: True, 2: False}, {1: 0.0, 2: 0.0})
    ref = [x for x in pas_retenu(f, r)["verdicts"] if not x["retenu"]]
    v("un refus porte la raison qui a mordu, pas un « non » nu",
      len(ref) == 1 and "garde du fabriqué" in ref[0]["pourquoi_refuse"],
      str(ref))
    # ⚠⚠ ET UN PAS FIN QUI TOMBE NE DOIT PAS FAIRE RETENIR UN PAS GROSSIER : le retenu est le
    # plus grossier qui passe, mais chaque pas est juge SEUL.
    f, r = jeu({1: False, 2: True}, {1: 0.0, 2: 0.0})
    v("chaque pas est jugé seul, donc un pas fin qui tombe n'empêche pas un grossier de passer",
      pas_retenu(f, r)["pas_retenu"] == 2)

    # === LA PORTEE EST CONSERVEE, ET C'EST CE QUI DISTINGUE L'ECONOMIE D'UN RETRECISSEMENT ===
    import combien_dinterstices_traverses as C  # noqa: PLC0415
    import la_direction_que_la_matiere_montre as D  # noqa: PLC0415

    for pe in (1, 2, 3):
        b = D.bloc(np.array([1000.0, 1000.0, 1000.0]), demi=12, pas=pe)
        v(f"un pas de {pe} garde la même portée physique",
          int(b[:, 2].max() - b[:, 2].min()) == 24,
          f"{int(b[:, 2].max() - b[:, 2].min())} voxels d'arête")

    # === LE BALAYAGE FABRIQUE, QUI DOIT POUVOIR REFUSER ====================================
    pas_vx = C.PAS_UM / C.VOXEL_FIN_UM
    fab = D.limite_de_sous_echantillonnage(pas_vx, demi=10, pas_echantillon=(1, 2, 8),
                                           tirages=2)
    v("le balayage fabriqué juge chaque pas contre la barre de SA forme",
      all("barre_de_sa_forme_deg" in x for x in fab["lignes"]))
    v("... et refuse un pas si grossier que les deux moitiés n'ont plus rien à comparer",
      not fab["lignes"][-1]["la_garde_tient"],
      f"{fab['lignes'][-1]['cote_en_points']} points d'arête")

    # === LES DONNEES REELLES ==============================================================
    r = mesurer(cellules=3, pas=(1, 2), bandes_max=2)
    if "message" in r:
        print(f"  ⚠ {r['message']} — contrôles sur données réelles sautés")
        print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, "
              f"{controles} checks)")
        return 1 if echecs else 0
    v("la mesure atteint le volume fin",
      r["sur_le_vrai_volume"]["cellules"] >= 3,
      f"{r['sur_le_vrai_volume']['cellules']} cellules")
    # ⚠⚠⚠ LE PAS LE PLUS FIN EST SA PROPRE REFERENCE, donc son ecart doit etre EXACTEMENT nul —
    # sinon la comparaison ne porterait pas sur ce qu'on croit.
    fin = next(x for x in r["sur_le_vrai_volume"]["lignes"] if x["pas_echantillon"] == 1)
    v("le pas le plus fin s'accorde exactement avec lui-même",
      fin["ecart_median_au_plus_fin_deg"] == 0.0 and fin["gain_de_temps"] == 1.0,
      f"écart {fin['ecart_median_au_plus_fin_deg']}°, gain ×{fin['gain_de_temps']}")
    v("chaque pas rend son coût mesuré, pas un coût modélisé",
      all(x["secondes_par_cube"] > 0 for x in r["sur_le_vrai_volume"]["lignes"]))
    # ⚠⚠⚠ CE CONTROLE EST STRUCTUREL, PAS UN RESULTAT. Asserter « un pas plus grossier est
    # retenu » obligerait a reecrire le controle chaque fois que la reponse change — c'est-a-dire
    # un controle qui ne peut pas echouer honnetement. Ce qui doit tenir, c'est que le verdict
    # soit RENDU, que chaque refus porte SA raison, et que la reference ne soit pas jugee.
    pr = r["le_pas_retenu"]
    v("le verdict est rendu avec les raisons de chaque refus",
      "verdicts" in pr and all(x["pourquoi_refuse"] for x in pr["verdicts"]
                               if not x["retenu"]))
    v("... la référence n'étant pas comptée parmi les économies",
      all(x["pas_echantillon"] > pr["pas_de_reference"] for x in pr["verdicts"]))
    v("... et chaque refus porte sa conséquence sur une marche enchaînée",
      all(x.get("part_de_marches_de_six_pas_touchees") is not None
          for x in pr["verdicts"] if not x["retenu"]))
    v("l'affichage tourne sur ce résultat", afficher(r) == 0)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--cellules", type=int, default=CELLULES_PAR_BANDE)
    p.add_argument("--demi", type=int, default=None)
    p.add_argument("--bandes", type=int, default=2)
    p.add_argument("--reagreger", action="store_true")
    p.add_argument("--json", type=Path, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if a.reagreger:
        if a.json is None or not a.json.is_file():
            print("⚠ --reagreger demande un --json existant")
            return 1
        r = json.loads(a.json.read_text())
        # ⚠ Seul le VERDICT est refait : les deux tableaux de mesure sont repris tels quels.
        r["le_pas_retenu"] = pas_retenu(r["sur_empilement_fabrique"], r["sur_le_vrai_volume"])
        afficher(r)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False))
        print(f"\nréagrégé : {a.json}")
        return 0
    r = mesurer(cellules=a.cellules, demi=a.demi, bandes_max=a.bandes)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False))
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
