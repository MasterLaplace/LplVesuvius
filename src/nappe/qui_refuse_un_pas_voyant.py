#!/usr/bin/env python3
"""Quand le marcheur VOIT et ne confirme pas, qu'est-ce qui refuse — la matière ou la fenêtre ?

⚠⚠⚠ POURQUOI CE FICHIER EXISTE. `115` a mesuré que là où le volume répond, le marcheur tient
**0,7618** de ses pas, à tout rayon. Restent **91 pas voyants non confirmés** sur 382, et c'est
exactement là que l'humain corrige. La question du graal n'est pas « combien » mais **« quoi »** :
le prédicat de `102` est une conjonction de trois termes, donc chaque refus a une cause nommable.

⭐⭐⭐⭐ **ET DEUX TIERS DES REFUS NE VIENNENT PAS DE LA MATIÈRE.** `en_butee` veut dire que
l'optimum de longueur de pas est tombé sur une **extrémité de la fenêtre de candidats** — la
matière y dit « au moins ceci » ou « au plus ceci », donc ce n'est pas une mesure, c'est une
butée. Le fichier qui produit ce drapeau l'écrit lui-même. Refuser dessus est prudent et juste ;
mais ce refus est **celui de l'instrument**, et il est réparable par une fenêtre plus large, pas
par un correcteur de trajectoire.

⚠⚠ **CE QU'ON PEUT ET NE PEUT PAS EN CONCLURE.** Un pas en butée aurait pu échouer AUSSI sur la
matière si la fenêtre avait été plus large : on ne le saura qu'en refaisant la course. Le taux que
la matière seule autoriserait est donc une **borne supérieure**, jamais une mesure — et il est
rendu comme telle.

⚠ La décomposition n'est PAS la tautologie que `115` écarte. `115` refusait de **corréler** les
termes du prédicat à son résultat ; ici on demande, pour un refus déjà constaté, **lequel** des
termes était faux. C'est une description exhaustive, pas un lien, et elle se vérifie : le prédicat
reconstruit doit rendre `confirme` sur les 560 pas, sinon la décomposition porte sur autre chose.

⚠ Aucune lecture distante : tout se calcule sur les 560 étapes que `113` a gardées.

  uv run python src/nappe/qui_refuse_un_pas_voyant.py --verifier
  uv run python src/nappe/qui_refuse_un_pas_voyant.py \
      --json docs/mesures/qui_refuse_un_pas_voyant.json
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
COURSE = RACINE / "docs" / "mesures" / "jusquou_va_t_il_si_on_le_laisse.json"

from ce_qui_porte_le_taux import est_aveugle  # noqa: E402

TERMES = ("interstices", "accord", "butee")
"""Les trois termes de `confirme = (interstices == 1) et (accord > barre) et (non en_butee)`.

⚠ L'ordre est celui du prédicat de `102`, et il est gardé : une décomposition dont les colonnes
changent d'ordre d'une tranche à l'autre se relit mal, et les comparaisons entre campagnes
deviennent un exercice de vigilance."""


def termes_faux(etape: dict, barre_interstice: float) -> tuple[str, ...]:
    """Lesquels des trois termes du prédicat sont faux pour ce pas.

    ⚠⚠ La barre est **passée**, jamais recopiée : elle est écrite dans la course
    (`barre_de_linterstice`), et une constante ici serait une seconde source libre de ne plus
    correspondre à la course qu'on lit.
    """
    out = []
    if etape.get("interstices_traverses") != 1:
        out.append("interstices")
    if not (etape.get("accord_de_linterstice", 0.0) > barre_interstice):
        out.append("accord")
    if etape.get("en_butee"):
        out.append("butee")
    return tuple(out)


def le_predicat_est_il_bien_reconstruit(course: dict) -> dict:
    """Le prédicat reconstruit rend-il `confirme` sur les 560 pas ?

    ⭐⭐⭐⭐ C'EST LA GARDE SANS LAQUELLE TOUTE LA DÉCOMPOSITION PORTE SUR AUTRE CHOSE. Si un seul
    pas est confirmé alors qu'un terme est faux, ou refusé alors que les trois tiennent, c'est que
    la conjonction n'est pas celle qu'on croit — et compter « qui refuse » n'aurait aucun sens.

    ⚠ Le test porte sur **tous** les pas, aveugles compris : un prédicat qui ne vaudrait que sur
    les voyants serait un prédicat différent, et c'est précisément ce qu'on veut exclure.
    """
    barre = course.get("barre_de_linterstice")
    if barre is None:
        return {"decidable": False, "pourquoi": "la course ne porte pas sa barre d'interstice"}
    pas = [e for l in course.get("lignes", []) for m in l.get("detail", [])
           for e in m.get("etapes", []) if "confirme" in e]
    ecarts = [e for e in pas if bool(e["confirme"]) != (not termes_faux(e, barre))]
    return {"decidable": True, "pas": len(pas), "barre_de_linterstice": barre,
            "desaccords": len(ecarts),
            "le_predicat_est_celui_quon_croit": len(pas) > 0 and not ecarts}


def qui_refuse(course: dict) -> dict:
    """Parmi les pas VOYANTS non confirmés, lequel des trois termes a refusé.

    ⭐⭐⭐⭐ La ligne qui décide est `butee_seule` : ces pas-là n'ont **rien** contre eux sinon que
    l'optimum de longueur est tombé au bord de la fenêtre de candidats. Ce n'est pas la matière
    qui refuse, c'est l'instrument qui ne sait pas répondre.

    ⚠ Les combinaisons sont rendues **entières** et pas seulement les marginales : « 63 pas en
    butée » et « 20 pas dont l'accord manque » se recouvrent, donc les additionner donnerait plus
    de refus qu'il n'y a de pas refusés.
    """
    barre = course.get("barre_de_linterstice")
    if barre is None:
        return {"decidable": False, "pourquoi": "la course ne porte pas sa barre d'interstice"}
    pas = [e for l in course.get("lignes", []) for m in l.get("detail", [])
           for e in m.get("etapes", []) if "confirme" in e]
    voyants = [e for e in pas if not est_aveugle(e)]
    refuses = [e for e in voyants if not e.get("confirme")]
    if not refuses:
        return {"decidable": False, "pourquoi": "aucun pas voyant refusé"}
    combinaisons: dict[str, int] = {}
    marginales = dict.fromkeys(TERMES, 0)
    for e in refuses:
        t = termes_faux(e, barre)
        combinaisons["+".join(t) if t else "(aucun)"] = \
            combinaisons.get("+".join(t) if t else "(aucun)", 0) + 1
        for x in t:
            marginales[x] += 1
    sans_butee = [e for e in refuses if "butee" not in termes_faux(e, barre)]
    confirmes = [e for e in voyants if e.get("confirme")]
    return {
        "decidable": True,
        "pas": len(pas), "voyants": len(voyants),
        "voyants_confirmes": len(confirmes),
        "voyants_refuses": len(refuses),
        "combinaisons": dict(sorted(combinaisons.items(), key=lambda kv: -kv[1])),
        "marginales": marginales,
        "butee_seule": combinaisons.get("butee", 0),
        "refuses_par_la_matiere_seule": len(sans_butee),
        # ⚠⚠ BORNE SUPÉRIEURE, et le nom le dit : un pas en butée aurait pu échouer aussi sur la
        # matière avec une fenêtre plus large. Écrire « le marcheur confirmerait 91 % » serait
        # promettre ce qu'une re-course seule peut rendre.
        "taux_au_plus_si_la_fenetre_ne_bornait_pas": round(
            len(confirmes) / max(1, len(confirmes) + len(sans_butee)), 4),
        "part_des_refus_qui_sont_une_butee": round(
            marginales["butee"] / len(refuses), 4)}


def les_bouts_de_la_fenetre(course: dict) -> dict:
    """Les pas en butée touchent-ils le bout COURT ou le bout LONG de la fenêtre ?

    ⭐⭐⭐ Les deux bouts n'ont pas le même remède. Au bout court, la matière demande un pas plus
    petit que la moitié du pas nominal ; au bout long, plus du double. Confondre les deux ferait
    élargir la fenêtre du mauvais côté.

    ⚠⚠ Les bornes de la fenêtre sont **lues dans les pas eux-mêmes** (le minimum et le maximum
    des longueurs choisies par les pas en butée), puis **comparées** au pas nominal que la course
    déclare. Les écrire en constantes ferait de ce fichier une seconde définition de la fenêtre du
    marcheur, libre de ne plus lui correspondre.
    """
    pas = [e for l in course.get("lignes", []) for m in l.get("detail", [])
           for e in m.get("etapes", []) if "confirme" in e]
    voyants = [e for e in pas if not est_aveugle(e)]
    en_butee = [e for e in voyants if e.get("en_butee")]
    if not en_butee:
        return {"decidable": False, "pourquoi": "aucun pas voyant en butée"}
    longueurs = [float(e["pas_um"]) for e in en_butee]
    bas, haut = min(longueurs), max(longueurs)
    nominal = course.get("pas_nominal_um")
    # ⚠⚠ La distribution est GARDÉE plutôt que résumée : les candidats de longueur sont un jeu
    # FINI (le balayage les énumère), donc un compte par candidat est exact et pas un histogramme
    # à classes choisies. La figure la dessine ; la recalculer ailleurs en ferait un second
    # producteur du même nombre.
    par_candidat: dict[float, dict[str, int]] = {}
    for e in voyants:
        cle = round(float(e["pas_um"]), 1)
        c = par_candidat.setdefault(cle, {"um": cle, "libres": 0, "en_butee": 0})
        c["en_butee" if e.get("en_butee") else "libres"] += 1
    return {
        "par_candidat": [par_candidat[k] for k in sorted(par_candidat)],
        "decidable": True, "pas_en_butee": len(en_butee),
        "bout_court_um": round(bas, 1), "bout_long_um": round(haut, 1),
        "au_bout_court": sum(1 for x in longueurs if x <= bas + 1e-9),
        "au_bout_long": sum(1 for x in longueurs if x >= haut - 1e-9),
        "entre_les_deux": sum(1 for x in longueurs if bas + 1e-9 < x < haut - 1e-9),
        "pas_nominal_um": nominal,
        "facteur_bas": round(bas / nominal, 3) if nominal else None,
        "facteur_haut": round(haut / nominal, 3) if nominal else None,
        # ⚠ Un pas en butée qui ne serait ni à un bout ni à l'autre serait un drapeau qui ne veut
        # pas dire ce qu'il dit ; le contrôle est ici plutôt que dans un commentaire.
        "tous_aux_bouts": sum(1 for x in longueurs
                              if bas + 1e-9 < x < haut - 1e-9) == 0}


def profil_de_profondeur(course: dict, voyants_seuls: bool) -> list[dict]:
    """Le taux de confirmation par rang de pas, sur tous les pas ou sur les seuls voyants.

    ⚠⚠ Un pas aveugle ne confirme jamais et ils sont concentrés en QUEUE de marche (`116`). Ils
    tirent donc le taux tardif vers le bas, et le profil de `113` mesurait la profondeur ET la
    cécité à la fois. C'est le même défaut que `115` a trouvé sur le rayon, un axe plus loin.
    """
    par_rang: dict[int, list[dict]] = {}
    for ligne in course.get("lignes", []):
        for cel in ligne.get("detail", []):
            for k, e in enumerate(cel.get("etapes", []), 1):
                if "confirme" not in e:
                    continue
                if voyants_seuls and est_aveugle(e):
                    continue
                par_rang.setdefault(k, []).append(e)
    return [{"pas": k, "marches": len(v),
             "confirmes": sum(1 for e in v if e.get("confirme"))}
            for k, v in sorted(par_rang.items())]


def le_taux_baisse_t_il_chez_les_voyants(course: dict) -> dict:
    """`113` mesurait un taux plat avec la profondeur. Tient-il une fois les aveugles retirés ?

    ⭐⭐⭐ ET LE CONTRÔLE EST DANS LA MÊME SORTIE : le test est refait sur TOUS les pas, et doit
    rendre ce que `113` a publié. Si ce n'est pas le cas, ce fichier ne lit pas la même chose que
    la tranche qu'il prolonge, et son résultat sur les voyants ne veut rien dire.

    ⚠ Le test lui-même est **importé** de `113`, jamais réécrit : deux implémentations d'une même
    probabilité sont deux occasions de ne pas s'accorder, et le partage en tiers y est déjà
    déclaré avant de voir les chiffres.
    """
    from jusquou_va_t_il_si_on_le_laisse import (  # noqa: PLC0415
        le_taux_baisse_avec_la_profondeur)
    tous = le_taux_baisse_avec_la_profondeur(profil_de_profondeur(course, False))
    voy = le_taux_baisse_avec_la_profondeur(profil_de_profondeur(course, True))
    publie = course.get("le_taux_baisse_avec_la_profondeur", {})
    accord = None
    if tous.get("decidable") and publie.get("decidable"):
        accord = bool(abs(tous["taux_precoce"] - publie["taux_precoce"]) < 1e-9
                      and abs(tous["taux_tardif"] - publie["taux_tardif"]) < 1e-9)
    return {"sur_tous_les_pas": tous, "sur_les_voyants": voy,
            "publie_par_113": {k: publie.get(k) for k in
                               ("taux_precoce", "taux_tardif", "p_sous_un_taux_constant")},
            # ⭐⭐⭐ Le contrôle positif : sans lui, « plat chez les voyants » pourrait venir d'un
            # lecteur qui ne lit pas les mêmes pas que `113`.
            "le_lecteur_retrouve_113": accord}


def mesurer(course_p: Path = COURSE) -> dict:
    """Tout, depuis le JSON de `113` — aucune lecture distante."""
    course = json.loads(course_p.read_text(encoding="utf-8"))
    if course.get("course_incomplete"):
        raise ValueError(f"{course_p} : course incomplète")
    if not course.get("lignes"):
        raise ValueError(f"{course_p} ne porte aucune marche")
    garde = le_predicat_est_il_bien_reconstruit(course)
    if garde.get("decidable") and not garde["le_predicat_est_celui_quon_croit"]:
        raise ValueError(
            f"{course_p} : le prédicat reconstruit ne rend pas `confirme` sur "
            f"{garde['desaccords']} pas — la décomposition porterait sur autre chose")
    return {"source": course_p.name,
            "le_predicat_est_il_bien_reconstruit": garde,
            "qui_refuse": qui_refuse(course),
            "les_bouts_de_la_fenetre": les_bouts_de_la_fenetre(course),
            "le_taux_baisse_t_il_chez_les_voyants": le_taux_baisse_t_il_chez_les_voyants(course)}


def afficher(r: dict) -> None:
    g = r["le_predicat_est_il_bien_reconstruit"]
    print(f"source {r['source']} · prédicat reconstruit sur {g.get('pas')} pas, "
          f"{g.get('desaccords')} désaccord(s)")
    q = r["qui_refuse"]
    if q.get("decidable"):
        print(f"\n  {q['voyants']} pas voyants · {q['voyants_confirmes']} confirmés · "
              f"{q['voyants_refuses']} refusés")
        for cle, n in q["combinaisons"].items():
            print(f"    {n:>4}  {cle}")
        print(f"  ⭐ {q['butee_seule']} refusés par la SEULE butée "
              f"({q['part_des_refus_qui_sont_une_butee']:.0%} des refus touchent la fenêtre)")
        print(f"  ⚠ la matière seule en refuse {q['refuses_par_la_matiere_seule']}, donc le taux "
              f"vaudrait AU PLUS {q['taux_au_plus_si_la_fenetre_ne_bornait_pas']}")
    f = r["les_bouts_de_la_fenetre"]
    if f.get("decidable"):
        print(f"\n  fenêtre [{f['bout_court_um']} ; {f['bout_long_um']}] µm "
              f"= [{f['facteur_bas']} ; {f['facteur_haut']}] × {f['pas_nominal_um']} µm")
        print(f"  {f['au_bout_court']} au bout court · {f['au_bout_long']} au bout long · "
              f"{f['entre_les_deux']} entre les deux")
    d = r["le_taux_baisse_t_il_chez_les_voyants"]
    t, v = d["sur_tous_les_pas"], d["sur_les_voyants"]
    if t.get("decidable") and v.get("decidable"):
        print(f"\n  profondeur, tous les pas : {t['taux_precoce']} → {t['taux_tardif']} "
              f"(p {t['p_sous_un_taux_constant']})   [113 publie "
              f"{d['publie_par_113']['taux_precoce']} → {d['publie_par_113']['taux_tardif']}]")
        print(f"  profondeur, voyants seuls : {v['taux_precoce']} → {v['taux_tardif']} "
              f"(p {v['p_sous_un_taux_constant']})")
        print(f"  ⭐ le lecteur retrouve 113 : {d['le_lecteur_retrouve_113']}")


def verifier() -> int:
    """La batterie, hors ligne, sur des courses FABRIQUÉES — et cinq sondes."""
    import tempfile
    echecs = controles = 0

    def v(nom, obtenu, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not obtenu:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f" — {detail}" if detail else ""))

    BARRE = 0.33

    def etape(aveugle=False, interstices=1, accord=0.6, butee=False, pas_um=173.0):
        """Un pas fabriqué, dont `confirme` est CALCULÉ par le prédicat de `102`.

        ⚠⚠ Le champ n'est pas posé à la main : une fixture où `confirme` serait écrit
        indépendamment des trois termes ne pourrait pas faire échouer la garde de reconstruction,
        qui est précisément le contrôle que ce fichier existe pour avoir.
        """
        return {"pas": 1, "interstices_traverses": interstices,
                "accord_de_linterstice": accord, "en_butee": butee, "pas_um": pas_um,
                "desaccord_des_moities_deg": 0.0 if aveugle else 12.0,
                "planarite": 0.0 if aveugle else 0.5,
                "confirme": (interstices == 1 and accord > BARRE and not butee)}

    def course(etapes_par_marche, nominal=173.0):
        return {"barre_de_linterstice": BARRE, "pas_nominal_um": nominal,
                "lignes": [{"rayon_mm": 4.0 + i, "detail": [{"etapes": es}]}
                           for i, es in enumerate(etapes_par_marche)]}

    # ⭐⭐⭐⭐ LA GARDE : le prédicat reconstruit doit rendre `confirme`.
    c = course([[etape(), etape(butee=True), etape(accord=0.1), etape(interstices=2),
                 etape(aveugle=True, interstices=0, accord=0.0)] for _ in range(4)])
    g = le_predicat_est_il_bien_reconstruit(c)
    v("le prédicat reconstruit rend `confirme` sur tous les pas",
      g["le_predicat_est_celui_quon_croit"], f"{g['desaccords']} désaccords")
    v("... et il compte bien tous les pas", g["pas"] == 20, f"{g['pas']}")
    # ⚠⚠ LA sonde qui compte : un seul pas où la conjonction ne tient pas doit être VU. Sans elle
    # toute la décomposition pourrait porter sur un prédicat qui n'est pas celui du marcheur.
    faux = json.loads(json.dumps(c))
    faux["lignes"][0]["detail"][0]["etapes"][1]["confirme"] = True
    v("sonde : un pas confirmé malgré une butée est signalé",
      not le_predicat_est_il_bien_reconstruit(faux)["le_predicat_est_celui_quon_croit"])
    v("... et il est compté", le_predicat_est_il_bien_reconstruit(faux)["desaccords"] == 1)
    sans = json.loads(json.dumps(c))
    del sans["barre_de_linterstice"]
    v("une course sans barre rend indécidable",
      not le_predicat_est_il_bien_reconstruit(sans)["decidable"])

    # ⭐⭐⭐⭐ LA DÉCOMPOSITION.
    q = qui_refuse(c)
    v("les pas aveugles sont hors du compte", q["voyants"] == 16, f"{q['voyants']}")
    v("les refus voyants sont comptés", q["voyants_refuses"] == 12, f"{q['voyants_refuses']}")
    v("la butée seule est isolée", q["butee_seule"] == 4, f"{q['butee_seule']}")
    v("la matière seule en refuse huit", q["refuses_par_la_matiere_seule"] == 8,
      f"{q['refuses_par_la_matiere_seule']}")
    # 4 confirmés sur 4 + 8 refusés par la matière -> 4/12 = 0,3333
    v("la borne supérieure ignore les butées",
      q["taux_au_plus_si_la_fenetre_ne_bornait_pas"] == 0.3333,
      f"{q['taux_au_plus_si_la_fenetre_ne_bornait_pas']}")
    v("les marginales se recouvrent, donc ne s'additionnent pas",
      sum(q["marginales"].values()) >= q["voyants_refuses"])
    # ⚠ Une combinaison double doit apparaître comme telle, jamais éclatée en deux lignes.
    c2 = course([[etape(interstices=2, accord=0.1)] * 3])
    q2 = qui_refuse(c2)
    v("sonde : une double cause est rendue entière",
      q2["combinaisons"].get("interstices+accord") == 3, f"{q2['combinaisons']}")
    v("aucun pas refusé rend indécidable",
      not qui_refuse(course([[etape()] * 3]))["decidable"])

    # ⭐⭐⭐ LES BOUTS DE LA FENÊTRE.
    c3 = course([[etape(butee=True, pas_um=86.5)] * 3 + [etape(butee=True, pas_um=346.0)] * 2
                 + [etape()] * 5])
    f = les_bouts_de_la_fenetre(c3)
    v("le bout court est lu dans les pas", f["bout_court_um"] == 86.5, f"{f['bout_court_um']}")
    v("le bout long aussi", f["bout_long_um"] == 346.0, f"{f['bout_long_um']}")
    v("les deux bouts sont comptés séparément",
      (f["au_bout_court"], f["au_bout_long"]) == (3, 2),
      f"{f['au_bout_court']}/{f['au_bout_long']}")
    v("les facteurs sont dérivés du pas nominal",
      (f["facteur_bas"], f["facteur_haut"]) == (0.5, 2.0),
      f"{f['facteur_bas']}/{f['facteur_haut']}")
    v("... et tous les pas en butée sont aux bouts", f["tous_aux_bouts"])
    # ⚠ La distribution par candidat doit compter les MÊMES pas que les deux bouts, sinon la
    # figure dessinerait un corpus et le texte en annoncerait un autre.
    v("la distribution par candidat couvre tous les pas voyants",
      sum(c["libres"] + c["en_butee"] for c in f["par_candidat"]) == 10,
      f"{sum(c['libres'] + c['en_butee'] for c in f['par_candidat'])}")
    v("... et les butées y sont au même compte",
      sum(c["en_butee"] for c in f["par_candidat"]) == f["pas_en_butee"])
    v("... et les candidats sont rangés par longueur croissante",
      [c["um"] for c in f["par_candidat"]] == sorted(c["um"] for c in f["par_candidat"]))
    # ⚠⚠ LA sonde symétrique : un drapeau de butée sur un pas qui n'est à aucun bout est un
    # drapeau qui ne veut pas dire ce qu'il dit, et le contrôle doit le voir.
    c4 = course([[etape(butee=True, pas_um=86.5), etape(butee=True, pas_um=200.0),
                  etape(butee=True, pas_um=346.0)]])
    v("sonde : une butée au milieu de la fenêtre est signalée",
      not les_bouts_de_la_fenetre(c4)["tous_aux_bouts"])
    v("aucune butée rend indécidable",
      not les_bouts_de_la_fenetre(course([[etape()] * 3]))["decidable"])

    # ⭐⭐⭐ LA PROFONDEUR, et son contrôle positif.
    # vingt pas par marche, les cinq derniers aveugles sur la moitié des marches
    longue = []
    for i in range(12):
        es = [etape(accord=0.6 if (k + i) % 3 else 0.1) for k in range(15)]
        es += [etape(aveugle=True, interstices=0, accord=0.0) if i % 2 else etape()
               for _ in range(5)]
        longue.append(es)
    c5 = course(longue)
    prof_tous = profil_de_profondeur(c5, False)
    prof_voy = profil_de_profondeur(c5, True)
    v("le profil de tous les pas a vingt rangs", len(prof_tous) == 20, f"{len(prof_tous)}")
    v("celui des voyants aussi, mais moins peuplé en queue",
      prof_voy[-1]["marches"] < prof_tous[-1]["marches"],
      f"{prof_voy[-1]['marches']} contre {prof_tous[-1]['marches']}")
    v("... et les rangs sans aveugle sont identiques",
      prof_voy[0]["marches"] == prof_tous[0]["marches"])
    d = le_taux_baisse_t_il_chez_les_voyants(c5)
    v("le test tourne sur les deux populations",
      d["sur_tous_les_pas"]["decidable"] and d["sur_les_voyants"]["decidable"])
    # ⚠ Retirer les aveugles ne peut que REMONTER le taux tardif : ils ne confirment jamais.
    v("retirer les aveugles remonte le taux tardif",
      d["sur_les_voyants"]["taux_tardif"] >= d["sur_tous_les_pas"]["taux_tardif"],
      f"{d['sur_les_voyants']['taux_tardif']} contre {d['sur_tous_les_pas']['taux_tardif']}")
    # ⚠⚠ Le contrôle positif exige que la course PUBLIE son propre résultat ; une course qui ne le
    # publie pas rend `None` et le dit, plutôt que de se déclarer d'accord avec rien.
    v("sans résultat publié, l'accord est indécidable et non « vrai »",
      d["le_lecteur_retrouve_113"] is None)
    c6 = json.loads(json.dumps(c5))
    c6["le_taux_baisse_avec_la_profondeur"] = {
        "decidable": True,
        "taux_precoce": d["sur_tous_les_pas"]["taux_precoce"],
        "taux_tardif": d["sur_tous_les_pas"]["taux_tardif"],
        "p_sous_un_taux_constant": d["sur_tous_les_pas"]["p_sous_un_taux_constant"]}
    v("avec un résultat publié qui correspond, l'accord est vrai",
      le_taux_baisse_t_il_chez_les_voyants(c6)["le_lecteur_retrouve_113"])
    c7 = json.loads(json.dumps(c6))
    c7["le_taux_baisse_avec_la_profondeur"]["taux_tardif"] += 0.1
    v("sonde : un désaccord avec le publié est signalé",
      not le_taux_baisse_t_il_chez_les_voyants(c7)["le_lecteur_retrouve_113"])

    # ⚠ Les refus d'entrée.
    with tempfile.TemporaryDirectory() as dd:
        p = Path(dd) / "c.json"
        p.write_text(json.dumps({"course_incomplete": True, "lignes": []}), encoding="utf-8")
        try:
            mesurer(p)
            v("une course incomplète est refusée", False)
        except ValueError:
            v("une course incomplète est refusée", True)
        p.write_text(json.dumps({"lignes": []}), encoding="utf-8")
        try:
            mesurer(p)
            v("une course sans marche est refusée", False)
        except ValueError:
            v("une course sans marche est refusée", True)
        # ⚠⚠ Et une course dont le prédicat ne se reconstruit pas est REFUSÉE, pas mesurée : une
        # décomposition sur un prédicat qu'on a mal lu compte des causes qui n'en sont pas.
        p.write_text(json.dumps(faux), encoding="utf-8")
        try:
            mesurer(p)
            v("une course au prédicat irréconciliable est refusée", False)
        except ValueError:
            v("une course au prédicat irréconciliable est refusée", True)
        p.write_text(json.dumps(c6), encoding="utf-8")
        r = mesurer(p)
        v("une course valide est mesurée", r["qui_refuse"]["decidable"])
        afficher(r)

    print(f"\n{'ALL PASS' if echecs == 0 else 'ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--course", type=Path, default=COURSE)
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(a.course)
    afficher(r)
    if a.json:
        a.json.write_text(json.dumps(r, indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
