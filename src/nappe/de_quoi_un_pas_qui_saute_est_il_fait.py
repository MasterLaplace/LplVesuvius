"""De quoi un pas qui saute est-il fait ? — la question que `160` laisse ouverte.

⭐⭐⭐⭐ POURQUOI CE FICHIER. `160` mesure QUE des pas sautent et OÙ (deux matières dures, un pas sur
sept), jamais DE QUOI ce saut est fait. Or un pas a deux moitiés et **une seule est bornée** :
l'avance commandée vaut au plus `avance_um` le long de la tangente, tandis que le recentrage des
mâchoires va où l'interstice se trouve et n'est borné par rien — `159` mesure un déplacement de
centre de 219,79 µm là où l'avance en vaut 98,4. Si c'est la part NORMALE qui sépare les pas qui
sautent des autres, alors la mâchoire s'accroche au **mauvais interstice à la pose**, et `155` ne
traite ce défaut qu'au niveau des APPUIS — jamais au niveau de la pose entière.

⚠⚠ LA COMPARAISON EST APPARIÉE À L'INTÉRIEUR DE CHAQUE MARCHE. Les deux populations — les pas qui
sautent et les autres — viennent du MÊME suiveur, sur la MÊME matière, au MÊME bruit. Deux médianes
prises sur deux marches différentes ne se soustraient pas, et une médiane globale moyennerait
justement sur l'axe où la différence vit : la population est bimodale par construction, puisque
`160` mesure 233 marches sur 342 sans aucun saut.

⚠⚠ ET L'ÉNONCÉ N'A AUCUN SEUIL. Ce qui est compté est « la part normale d'un pas qui saute est plus
grande que celle d'un pas ordinaire », une comparaison exacte entre deux nombres que la même marche
produit. Aucune fraction de feuille, aucun multiple d'épaisseur, aucun nombre choisi.

⚠⚠ UN ÉCART EXACTEMENT NUL N'EST NI UNE SÉPARATION NI SON CONTRAIRE, et ce n'est pas une précaution
d'écriture : sur la pince les deux projections tangentielles valent la même chose au millième près,
parce que l'avance est commandée. Les compter comme « ne sépare pas » les mêlerait aux cas où la
tangente est franchement plus PETITE du côté qui saute, qui disent autre chose.

⚠⚠⚠ LE CONTRÔLE EST OBLIGATOIRE ET IL EST VIDE. `R4-F145` mesure zéro pas qui saute sur la spirale
NUE, donc la comparaison n'y est pas « nulle » : elle n'existe pas. Une population vide doit se
DIRE — rendre zéro ferait lire « les deux moitiés se valent » là où il n'y a rien à comparer.

Usage :
    uv run python src/nappe/de_quoi_un_pas_qui_saute_est_il_fait.py --verifier
    uv run python src/nappe/de_quoi_un_pas_qui_saute_est_il_fait.py \\
        --json docs/mesures/de_quoi_un_pas_qui_saute_est_il_fait.json
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
# (nom, deux, contrainte, rejeter) — les deux mêmes bras que `160`, et pour la même raison : la
# pince de `144` est l'instrument livré, la mâchoire seule avec rejet est celle qui marche le plus
# loin sur la matière du rouleau.
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


def les_deux_camps(x: dict) -> dict | None:
    """Les quatre nombres d'UNE marche, ou rien si la marche n'a pas les deux camps.

    ⚠⚠ RIEN, ET NON DES ZÉROS. Une marche dont aucun pas ne saute n'a pas une part normale nulle
    du côté qui saute : elle n'a pas ce côté. Rendre zéro ferait entrer une marche muette dans un
    compte de marches qui séparent, ce qui est exactement le contraire de ce qu'elle dit.
    """
    t_oui = x.get("sur_la_tangente_um_des_pas_qui_sautent")
    t_non = x.get("sur_la_tangente_um_des_pas_qui_ne_sautent_pas")
    n_oui = x.get("sur_la_normale_um_des_pas_qui_sautent")
    n_non = x.get("sur_la_normale_um_des_pas_qui_ne_sautent_pas")
    if t_oui is None or t_non is None or n_oui is None or n_non is None:
        return None
    return {"tangente_qui_sautent": float(t_oui), "tangente_qui_ne_sautent_pas": float(t_non),
            "normale_qui_sautent": float(n_oui), "normale_qui_ne_sautent_pas": float(n_non),
            "effectif_des_pas_qui_sautent": int(x.get("effectif_des_pas_qui_sautent", 0)),
            "effectif_des_pas_qui_ne_sautent_pas": int(
                x.get("effectif_des_pas_qui_ne_sautent_pas", 0))}


def _sens(oui: float, non: float) -> int:
    """+1 si le côté qui saute est plus grand, −1 s'il est plus petit, 0 s'ils sont ÉGAUX.

    ⚠⚠ L'ÉGALITÉ EST SA PROPRE RÉPONSE. Les deux nombres sortent du même producteur avec les mêmes
    décimales, donc « égal » est un fait mesuré et non une coïncidence d'arrondi — et c'est le fait
    central du côté de la pince, dont l'avance est commandée.
    """
    if oui > non:
        return 1
    if oui < non:
        return -1
    return 0


def _resume(xs: list[dict]) -> dict:
    """Ce qu'un paquet de marches dit du partage, en COMPTES appariés.

    ⚠⚠⚠ TOUT CE QUI EST PUBLIÉ ICI EST UN COMPTE DE MARCHES OU UNE MÉDIANE DE RAPPORTS CALCULÉS
    PAR MARCHE. Une médiane de la part normale prise sur toutes les marches confondues serait une
    moyenne sur l'axe où la différence vit, et le dépôt l'a déjà payé deux fois.
    """
    dec = [x for x in xs if x.get("decidable")]
    camps = [c for c in (les_deux_camps(x) for x in dec) if c is not None]
    sans_saut = sum(1 for x in dec if les_deux_camps(x) is None)
    base = {"marches": len(xs), "decidables": len(dec), "marches_appariables": len(camps),
            "marches_sans_pas_qui_sautent": int(sans_saut)}
    if not camps:
        # ⚠⚠ ET C'EST LE CAS DU CONTRÔLE : sur la spirale nue il n'y a rien à apparier, et le dire
        # est la bonne réponse. `decidable` reste VRAI — la marche a bien eu lieu, c'est la
        # COMPARAISON qui est vide.
        return {**base, "decidable": bool(dec), "apparie": False,
                "raison": "aucune marche n'a de pas qui saute"}
    sn = [_sens(c["normale_qui_sautent"], c["normale_qui_ne_sautent_pas"]) for c in camps]
    st = [_sens(c["tangente_qui_sautent"], c["tangente_qui_ne_sautent_pas"]) for c in camps]
    # ⚠ Un rapport ne se calcule pas contre zéro ; une part rigoureusement nulle du côté ordinaire
    # est possible sur une matière lisse, donc la marche est SAUTÉE du rapport et reste dans les
    # comptes — elle y dit déjà tout ce qu'elle a à dire.
    rn = [c["normale_qui_sautent"] / c["normale_qui_ne_sautent_pas"]
          for c in camps if c["normale_qui_ne_sautent_pas"] > 0.0]
    rt = [c["tangente_qui_sautent"] / c["tangente_qui_ne_sautent_pas"]
          for c in camps if c["tangente_qui_ne_sautent_pas"] > 0.0]
    # ⭐⭐ ET LA DISTRIBUTION ELLE-MÊME EST PUBLIÉE, pas seulement le partage. Ce sont des
    # médianes de médianes — chaque terme est déjà la médiane d'une marche — donc elles résument
    # la distribution et ne se SOUSTRAIENT jamais l'une de l'autre : c'est le compte apparié
    # ci-dessus qui tranche, ces quatre nombres disent seulement à quelle échelle ça se joue.
    # ⚠⚠ Elles portent le nom PROJECTION et non « avance » : seule l'avance COMMANDÉE est bornée
    # par `avance_um`, et la projection du pas sur la tangente ne l'est pas, parce que le
    # recentrage a sa propre composante le long de cette direction.
    ums = {}
    for cote in ("qui_sautent", "qui_ne_sautent_pas"):
        for axe, cle in (("tangente", "tangente"), ("normale", "normale")):
            vals = [c[f"{cle}_{cote}"] for c in camps]
            ums[f"sur_la_{axe}_um_des_pas_{cote}"] = round(float(statistics.median(vals)), 3)
    return {**base, "decidable": True, "apparie": True, **ums,
            "la_normale_separe": int(sum(1 for s in sn if s > 0)),
            "la_normale_separe_a_lenvers": int(sum(1 for s in sn if s < 0)),
            "la_normale_est_egale": int(sum(1 for s in sn if s == 0)),
            "la_tangente_separe": int(sum(1 for s in st if s > 0)),
            "la_tangente_separe_a_lenvers": int(sum(1 for s in st if s < 0)),
            "la_tangente_est_egale": int(sum(1 for s in st if s == 0)),
            # ⭐⭐⭐⭐ LE COMPTE QUI RÉPOND À LA QUESTION. « Seule la normale sépare » veut dire que
            # la part normale est plus grande du côté qui saute ET que la part tangente ne l'est
            # pas — donc que ce qui fait sauter un pas est le RECENTRAGE et rien d'autre.
            "seule_la_normale_separe": int(sum(1 for a, b in zip(sn, st) if a > 0 and b <= 0)),
            "seule_la_tangente_separe": int(sum(1 for a, b in zip(sn, st) if b > 0 and a <= 0)),
            "les_deux_separent": int(sum(1 for a, b in zip(sn, st) if a > 0 and b > 0)),
            "rapport_normal_median": (round(float(statistics.median(rn)), 3) if rn else None),
            "rapport_tangent_median": (round(float(statistics.median(rt)), 3) if rt else None),
            "pas_qui_sautent": int(sum(c["effectif_des_pas_qui_sautent"] for c in camps)),
            "pas_qui_ne_sautent_pas": int(sum(c["effectif_des_pas_qui_ne_sautent_pas"]
                                              for c in camps))}


def lautopsie(matieres=MATIERES, bruits=BRUITS, regles=REGLES, departs: int = DEPARTS) -> dict:
    """De quoi les pas qui sautent sont faits, matière par matière et règle par règle."""
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


def _cumuler(cs: list[dict], nom: str) -> dict:
    """Les comptes d'un groupe de cases — des SOMMES de comptes, jamais des moyennes de rapports."""
    app = [c for c in cs if c.get("apparie")]
    # ⚠⚠ LES MÉDIANES EN µm SE RÉAGRÈGENT PAR MÉDIANE, jamais par somme : ce sont des niveaux,
    # pas des comptes, et les additionner rendrait un nombre qui n'est la mesure de rien.
    # ⚠ Une case sans ces niveaux est SAUTÉE, pas lue comme un zéro : une mesure d'un écrivain
    # antérieur peut parfaitement ne pas les porter, et un niveau absent n'est pas un niveau nul.
    niveaux = {}
    for k in ("sur_la_tangente_um_des_pas_qui_sautent",
              "sur_la_normale_um_des_pas_qui_sautent",
              "sur_la_tangente_um_des_pas_qui_ne_sautent_pas",
              "sur_la_normale_um_des_pas_qui_ne_sautent_pas"):
        vals = [c[k] for c in app if c.get(k) is not None]
        if vals:
            niveaux[k] = round(float(statistics.median(vals)), 3)
    somme = {k: int(sum(c[k] for c in app)) for k in
             ("marches_appariables", "la_normale_separe", "la_normale_separe_a_lenvers",
              "la_normale_est_egale", "la_tangente_separe", "la_tangente_separe_a_lenvers",
              "la_tangente_est_egale", "seule_la_normale_separe", "seule_la_tangente_separe",
              "les_deux_separent", "pas_qui_sautent")} if app else {}
    somme.update(niveaux)
    # ⚠⚠ UNE MÉDIANE DE MÉDIANES RESTE APPARIÉE ICI, parce que chaque terme est déjà un rapport
    # calculé À L'INTÉRIEUR d'une marche. Ce qui serait faux, c'est de médianer les parts ; ce qui
    # est juste, c'est de médianer les rapports.
    rn = [c["rapport_normal_median"] for c in app if c.get("rapport_normal_median") is not None]
    rt = [c["rapport_tangent_median"] for c in app if c.get("rapport_tangent_median") is not None]
    return {"nom": nom, "cases": len(cs), "cases_appariables": len(app),
            "decidables": int(sum(c.get("decidables", 0) for c in cs)),
            "marches_sans_pas_qui_sautent": int(sum(c.get("marches_sans_pas_qui_sautent", 0)
                                                    for c in cs)),
            **somme,
            "rapport_normal_median": (round(float(statistics.median(rn)), 3) if rn else None),
            "rapport_tangent_median": (round(float(statistics.median(rt)), 3) if rt else None)}


def par_matiere(d: dict) -> list[dict]:
    """Le partage matière par matière, toutes règles et tous bruits confondus."""
    return [_cumuler([c for c in d["cases"] if c["nom"] == nom], nom)
            for nom in dict.fromkeys(c["nom"] for c in d["cases"])]


def par_regle(d: dict) -> list[dict]:
    """Le partage bras par bras — et c'est là que les deux instruments se séparent."""
    return [_cumuler([c for c in d["cases"] if c["regle"] == r], r)
            for r in dict.fromkeys(c["regle"] for c in d["cases"])]


def _verdict(g: dict) -> str | None:
    """Quelle moitié fait sauter, pour UN groupe — ou rien si le groupe n'a rien à apparier.

    ⚠⚠ « Le recentrage » exige que la normale sépare SEULE plus souvent que la tangente ne sépare,
    seule ou avec elle : un bras dont les deux moitiés séparent ensemble ne désigne aucune des deux.
    """
    if not g.get("cases_appariables"):
        return None
    seule_n = int(g.get("seule_la_normale_separe", 0))
    seule_t = int(g.get("seule_la_tangente_separe", 0))
    deux = int(g.get("les_deux_separent", 0))
    if seule_n > seule_t + deux:
        return "le recentrage"
    if deux >= seule_n:
        return "les deux moitiés"
    return "l'avance"


def juger(d: dict) -> dict:
    """Quelle moitié du pas fait sauter — et le contrôle VIDE qui rend la réponse lisible.

    ⚠⚠⚠ LE CONTRÔLE EST UNE ABSENCE. Sur la spirale NUE aucun pas ne saute (`R4-F145`), donc la
    comparaison n'y est pas nulle, elle n'y est pas. Le contrôle tient quand le groupe de la
    spirale nue n'a AUCUNE marche appariable et que toutes ses marches sont comptées comme sans
    pas qui saute — pas quand il rend des zéros.
    """
    if not d.get("decidable"):
        return {"decidable": False, "raison": "aucune case mesurée"}
    mat, reg = par_matiere(d), par_regle(d)
    nue = next((m for m in mat if m["nom"] == _nom(*LA_SPIRALE_NUE)), None)
    tous = _cumuler(d["cases"], "tout")
    return {"decidable": True, "par_matiere": mat, "par_regle": reg, "tout": tous,
            "le_controle_de_la_spirale_nue": {
                "nom": nue["nom"] if nue else None,
                "cases_appariables": nue["cases_appariables"] if nue else None,
                "marches_sans_pas_qui_sautent": (nue["marches_sans_pas_qui_sautent"]
                                                 if nue else None),
                "decidables": nue["decidables"] if nue else None,
                "il_est_vide": bool(nue is not None and nue["cases_appariables"] == 0
                                    and nue["marches_sans_pas_qui_sautent"] == nue["decidables"])},
            # ⭐⭐⭐⭐ ET LA RÉPONSE, en comptes appariés : sur combien de marches le RECENTRAGE
            # sépare-t-il seul les pas qui sautent des autres ?
            "seule_la_normale_separe": tous.get("seule_la_normale_separe"),
            "seule_la_tangente_separe": tous.get("seule_la_tangente_separe"),
            "les_deux_separent": tous.get("les_deux_separent"),
            "marches_appariables": tous.get("marches_appariables"),
            # ⚠⚠⚠ LE VERDICT EST PAR BRAS, ET JAMAIS GLOBAL. Payé ici : un verdict pris sur
            # toutes les cases confondues rendait « les deux moitiés », porté ENTIEREMENT par la
            # mâchoire seule, et effaçait la réponse de la pince — qui est l'instrument livré.
            # C'est le péché du dépôt (moyenner sur l'axe où la différence vit) remonté d'un étage,
            # au niveau du verdict. Les comptes de `tout` restent publiés : une somme de comptes
            # est honnête, c'est le MOT unique qui ne l'était pas.
            "le_verdict_par_bras": {g["nom"]: _verdict(g) for g in reg},
            "les_deux_bras_saccordent": bool(len({_verdict(g) for g in reg}) <= 1)}


def mesurer(matieres=MATIERES, bruits=BRUITS, regles=REGLES, departs: int = DEPARTS) -> dict:
    d = lautopsie(matieres, bruits, regles, departs)
    return {"autopsie": d, "juger": juger(d)}


def reagreger(r: dict) -> dict:
    """Recalcule le verdict depuis les cases rangées — sans remarcher."""
    r["juger"] = juger(r["autopsie"])
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
    marque = "★" if c["il_est_vide"] else "✗"
    print(f"{marque} contrôle — sur la spirale NUE la comparaison est VIDE, pas nulle : "
          f"{c['cases_appariables']} case appariable, "
          f"{c['marches_sans_pas_qui_sautent']}/{c['decidables']} marches sans un pas qui saute")
    for titre, groupes in (("par matière", j["par_matiere"]), ("par bras", j["par_regle"])):
        print(f"\n   — {titre} —")
        print(f"   {'':>34} | {'appar.':>6} | {'normale':>18} | {'tangente':>18} | {'seule N':>7}")
        for g in groupes:
            if not g.get("cases_appariables"):
                print(f"   {g['nom']:>34} | {'—':>6} | {'(aucun pas ne saute)':>18} | "
                      f"{'':>18} | {'—':>7}")
                continue
            rn = g["rapport_normal_median"]
            rt = g["rapport_tangent_median"]
            print(f"   {g['nom']:>34} | {g['marches_appariables']:>6d} | "
                  f"{g['la_normale_separe']:>3d}+ {g['la_normale_est_egale']:>3d}= "
                  f"{'×' + format(rn, '.3f') if rn is not None else '—':>9} | "
                  f"{g['la_tangente_separe']:>3d}+ {g['la_tangente_est_egale']:>3d}= "
                  f"{'×' + format(rt, '.3f') if rt is not None else '—':>9} | "
                  f"{g['seule_la_normale_separe']:>7d}")
    print(f"\n   seule la NORMALE sépare : {j['seule_la_normale_separe']} marches ; "
          f"seule la TANGENTE : {j['seule_la_tangente_separe']} ; "
          f"les deux : {j['les_deux_separent']} — sur {j['marches_appariables']} appariables")
    print("\n★★★★ la moitié du pas qui fait SAUTER, PAR BRAS "
          "— un verdict global effacerait la réponse de la pince :")
    for nom, verdict in j["le_verdict_par_bras"].items():
        print(f"      {nom:>26} : {verdict}")
    if not j["les_deux_bras_saccordent"]:
        print("      ⚠ les deux bras NE DISENT PAS la même chose, et c'est le résultat")


def _suivi(t_oui, t_non, n_oui, n_non, e_oui=10, e_non=100) -> dict:
    """Une marche dont les deux camps sont connus — la forme que `suivre` publie."""
    return {"decidable": True,
            "sur_la_tangente_um_des_pas_qui_sautent": float(t_oui),
            "sur_la_tangente_um_des_pas_qui_ne_sautent_pas": float(t_non),
            "sur_la_normale_um_des_pas_qui_sautent": float(n_oui),
            "sur_la_normale_um_des_pas_qui_ne_sautent_pas": float(n_non),
            "effectif_des_pas_qui_sautent": int(e_oui),
            "effectif_des_pas_qui_ne_sautent_pas": int(e_non)}


def _sans_saut() -> dict:
    """Une marche qui a marché et dont aucun pas n'a sauté — donc sans camp qui saute."""
    return {"decidable": True,
            "sur_la_tangente_um_des_pas_qui_ne_sautent_pas": 98.4,
            "sur_la_normale_um_des_pas_qui_ne_sautent_pas": 5.078,
            "effectif_des_pas_qui_ne_sautent_pas": 640}


def verifier() -> int:
    import contextlib  # noqa: PLC0415
    import io  # noqa: PLC0415

    from la_pince_tient_elle_la_feuille import _les_deux_moities_du_pas  # noqa: PLC0415

    echecs = controles = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    print("— les deux moitiés sont des PROJECTIONS, et elles se séparent —")
    # Trois pas depuis l'origine, avec une tangente sur x et une normale sur y : le premier pas
    # avance de 4 en tangente, le deuxieme recentre de 3 en normale, le troisieme fait les deux.
    t = np.array([1.0, 0.0, 0.0])
    n = np.array([0.0, 1.0, 0.0])
    centres = [np.array([0.0, 0.0, 0.0]), np.array([4.0, 0.0, 0.0]),
               np.array([4.0, 3.0, 0.0]), np.array([6.0, 9.0, 0.0])]
    reperes = [(t, n), (t, n), (t, n)]
    m = _les_deux_moities_du_pas(centres, reperes, 1.0, np.array([True, True, False]))
    v("⭐⭐⭐ la projection tangente et la projection normale se lisent séparément",
      abs(m["sur_la_tangente_um_des_pas_qui_sautent"] - 2.0) < 1e-9
      and abs(m["sur_la_normale_um_des_pas_qui_sautent"] - 1.5) < 1e-9
      and abs(m["sur_la_tangente_um_des_pas_qui_ne_sautent_pas"] - 2.0) < 1e-9
      and abs(m["sur_la_normale_um_des_pas_qui_ne_sautent_pas"] - 6.0) < 1e-9,
      f"sautent {m['sur_la_tangente_um_des_pas_qui_sautent']} / "
      f"{m['sur_la_normale_um_des_pas_qui_sautent']}")
    v("⚠⚠ l'effectif accompagne sa médiane, et sous un nom qui ne collisionne avec rien",
      m["effectif_des_pas_qui_sautent"] == 2 and m["effectif_des_pas_qui_ne_sautent_pas"] == 1
      and "pas_qui_sautent" not in m,
      "`pas_qui_sautent` est déjà la clé de `_le_deroulage_exact`")
    # ⚠⚠⚠ LA POPULATION VIDE SE DIT. Aucun pas ne saute : la cle n'existe PAS, elle ne vaut pas 0.
    vide = _les_deux_moities_du_pas(centres, reperes, 1.0, np.array([False, False, False]))
    v("⭐⭐⭐⭐ une population VIDE ne rend pas zéro — la clé n'existe pas",
      "sur_la_normale_um_des_pas_qui_sautent" not in vide
      and "sur_la_normale_um_des_pas_qui_ne_sautent_pas" in vide,
      f"{sorted(k for k in vide if 'qui_sautent' in k)}")

    print("\n— l'appariement est INTERNE à la marche —")
    v("⚠ une marche sans camp qui saute n'est pas appariable, et ce n'est pas un échec",
      les_deux_camps(_sans_saut()) is None and les_deux_camps(_suivi(98.4, 98.4, 75.6, 15.8))
      is not None)
    # ⚠⚠⚠ LA FIXTURE DOIT DISCRIMINER L'APPARIEMENT D'UNE MÉDIANE GLOBALE. Deux marches où la
    # normale sépare CHACUNE chez elle, mais dont les niveaux sont tels qu'une médiane globale des
    # parts normales rendrait le côte « qui saute » PLUS PETIT que le côté ordinaire.
    xs = [_suivi(98.4, 98.4, 30.0, 20.0), _suivi(98.4, 98.4, 300.0, 200.0)]
    globale_oui = statistics.median([30.0, 300.0])
    globale_non = statistics.median([20.0, 200.0])
    r = _resume(xs)
    v("⭐⭐⭐⭐ le compte apparié dit que la normale sépare PARTOUT",
      r["la_normale_separe"] == 2 and r["la_normale_est_egale"] == 0,
      f"{r['la_normale_separe']}/2 marches")
    xs_piege = [_suivi(98.4, 98.4, 30.0, 20.0), _suivi(98.4, 98.4, 25.0, 200.0)]
    piege = _resume(xs_piege)
    v("⭐⭐⭐⭐ ... là où une médiane globale se trompe de sens sur la même paire de marches",
      piege["la_normale_separe"] == 1 and piege["la_normale_separe_a_lenvers"] == 1
      and statistics.median([30.0, 25.0]) < statistics.median([20.0, 200.0]),
      f"globale {statistics.median([30.0, 25.0])} < {statistics.median([20.0, 200.0])}, "
      f"appariée 1 pour et 1 contre — la globale ne peut rendre qu'un seul verdict")
    v("⚠ et sur la première paire la globale tombe juste, donc elle n'est pas toujours fausse",
      globale_oui > globale_non, "c'est bien l'appariement qui est exact, pas la globale qui ment")
    # ⚠⚠ UN ÉCART EXACTEMENT NUL N'EST NI UNE SÉPARATION NI SON CONTRAIRE, et c'est le cas de la
    # pince, dont l'avance est commandée donc identique des deux côtés.
    v("⭐⭐⭐ une tangente ÉGALE des deux côtés est comptée à part, jamais avec « ne sépare pas »",
      r["la_tangente_est_egale"] == 2 and r["la_tangente_separe"] == 0
      and r["la_tangente_separe_a_lenvers"] == 0,
      "l'avance est commandée, donc les deux projections coïncident")
    v("⭐⭐⭐⭐ « seule la normale sépare » exige que la tangente NE sépare PAS",
      r["seule_la_normale_separe"] == 2 and r["les_deux_separent"] == 0
      and _resume([_suivi(150.0, 90.0, 60.0, 20.0)])["les_deux_separent"] == 1
      and _resume([_suivi(150.0, 90.0, 60.0, 20.0)])["seule_la_normale_separe"] == 0)
    v("⚠ le rapport est calculé PAR MARCHE puis médiané, et jamais contre un dénominateur nul",
      abs(r["rapport_normal_median"] - 1.5) < 1e-9
      and _resume([_suivi(98.4, 98.4, 60.0, 0.0)])["rapport_normal_median"] is None,
      f"médiane de (30/20, 300/200) = {r['rapport_normal_median']}")

    print("\n— une comparaison vide se DIT, elle ne rend pas zéro —")
    muet = _resume([_sans_saut(), _sans_saut()])
    v("⭐⭐⭐⭐ sans aucun pas qui saute, le résumé n'est PAS apparié et le dit",
      muet["apparie"] is False and muet["decidable"] is True
      and muet["marches_sans_pas_qui_sautent"] == 2
      and "seule_la_normale_separe" not in muet,
      f"{muet.get('raison')}")
    v("⚠⚠ ... et une marche qui n'a pas marché n'entre ni dans l'un ni dans l'autre",
      _resume([{"decidable": False}])["decidables"] == 0
      and _resume([{"decidable": False}])["decidable"] is False)

    print("\n— le contrôle de la spirale nue —")
    def case(nom, regle, appariables, sans_saut, normale=2, tangente=0, dec=12):
        c = {"regle": regle, "nom": nom, "ecrasement": 0.0, "amplitude_um": 0.0, "bruit": 0.0,
             "departs": dec, "decidable": True, "marches": dec, "decidables": dec,
             "marches_appariables": appariables, "marches_sans_pas_qui_sautent": sans_saut}
        if not appariables:
            return {**c, "apparie": False, "raison": "aucune marche n'a de pas qui saute"}
        return {**c, "apparie": True, "la_normale_separe": normale,
                "la_normale_separe_a_lenvers": 0, "la_normale_est_egale": 0,
                "la_tangente_separe": tangente, "la_tangente_separe_a_lenvers": 0,
                "la_tangente_est_egale": appariables - tangente,
                "seule_la_normale_separe": max(normale - tangente, 0),
                "seule_la_tangente_separe": 0, "les_deux_separent": min(normale, tangente),
                "rapport_normal_median": 5.2, "rapport_tangent_median": 1.0,
                "sur_la_tangente_um_des_pas_qui_sautent": 98.4,
                "sur_la_normale_um_des_pas_qui_sautent": 75.621,
                "sur_la_tangente_um_des_pas_qui_ne_sautent_pas": 98.4,
                "sur_la_normale_um_des_pas_qui_ne_sautent_pas": 15.852,
                "pas_qui_sautent": 31, "pas_qui_ne_sautent_pas": 600}
    # ⚠⚠⚠ LA FIXTURE EST DIMENSIONNÉE SUR CE QUE LA MESURE A RENDU, pas devinée : ma première
    # version, aux proportions inventées, ne reproduisait PAS l'effondrement du verdict global et
    # la sonde la déclarait verte. Ce sont les comptes réels de la grille — pince 41 normale sur
    # 54 contre 13 tangente, mâchoire seule 54 contre 53.
    P_APP, P_N, P_T = 54, 41, 13
    S_APP, S_N, S_T = 54, 54, 53
    bon = {"decidable": True, "regles": ["p", "s"], "bruits": [0.0], "departs": 12,
           "cases": [case(_nom(*LA_SPIRALE_NUE), "p", 0, 12),
                     case("spirale écrasée et froissée 100 µm", "p", P_APP, 116, normale=P_N,
                          tangente=P_T, dec=170),
                     case("spirale écrasée et froissée 100 µm", "s", S_APP, 119, normale=S_N,
                          tangente=S_T, dec=173)]}
    j = juger(bon)
    v("⭐⭐⭐⭐ le contrôle tient quand la spirale nue n'a RIEN à apparier",
      j["le_controle_de_la_spirale_nue"]["il_est_vide"] is True
      and j["le_controle_de_la_spirale_nue"]["cases_appariables"] == 0)
    mauvais = {**bon, "cases": [case(_nom(*LA_SPIRALE_NUE), "p", 1, 11)] + bon["cases"][1:]}
    v("⭐⭐⭐ ... et il TOMBE dès qu'une seule marche y devient appariable",
      juger(mauvais)["le_controle_de_la_spirale_nue"]["il_est_vide"] is False)
    # ⚠⚠ LES ATTENDUS SE DÉRIVENT DE LA FIXTURE : écrits en dur, ils sont devenus faux à la
    # seconde où j'ai redimensionné la fixture sur les comptes réels.
    v("⭐⭐ les deux bras se lisent séparément, et ils ne disent pas la même chose",
      len(j["par_regle"]) == 2
      and j["par_regle"][0]["seule_la_normale_separe"] == max(P_N - P_T, 0)
      and j["par_regle"][1]["les_deux_separent"] == min(S_N, S_T),
      "la pince ne sépare que par la normale, la mâchoire seule par les deux")
    # ⚠⚠⚠ LA FIXTURE EST CELLE QUE LA MESURE A RENDUE : deux bras qui ne disent PAS la même
    # chose. Un verdict global y répondait « les deux moitiés », porté par le seul second bras,
    # et effaçait la réponse du premier — qui est l'instrument livré. Vérifié en cassant le code.
    v("⭐⭐⭐⭐ le verdict est PAR BRAS, et les deux bras peuvent se contredire",
      j["le_verdict_par_bras"]["p"] == "le recentrage"
      and j["le_verdict_par_bras"]["s"] == "les deux moitiés"
      and j["les_deux_bras_saccordent"] is False,
      f"{j['le_verdict_par_bras']}")
    v("⭐⭐⭐⭐ ... et un verdict pris sur les cases CONFONDUES aurait effacé le premier bras",
      _verdict(j["tout"]) == "les deux moitiés" != j["le_verdict_par_bras"]["p"],
      f"confondu « {_verdict(j['tout'])} », pince « {j['le_verdict_par_bras']['p']} »")
    v("⚠⚠ un bras qui n'a rien à apparier n'a pas de verdict, et n'en reçoit pas un par défaut",
      _verdict(case(_nom(*LA_SPIRALE_NUE), "p", 0, 12)) is None
      and _verdict({"cases_appariables": 2, "seule_la_normale_separe": 2,
                    "seule_la_tangente_separe": 0, "les_deux_separent": 0}) == "le recentrage")
    v("⚠ les deux bras qui S'ACCORDENT se disent aussi",
      juger({**bon, "cases": [bon["cases"][0], case("d", "p", 9, 3, normale=9, tangente=0),
                              case("d", "s", 9, 3, normale=9, tangente=0)]})[
          "les_deux_bras_saccordent"] is True)
    v("⚠ une matière sans aucun pas qui saute reste dans le tableau, avec ses marches comptées",
      any(m["cases_appariables"] == 0 and m["marches_sans_pas_qui_sautent"] == 12
          for m in j["par_matiere"]))
    # ⚠⚠ LES NIVEAUX EN µm SE RÉAGRÈGENT PAR MÉDIANE, jamais par somme : additionner deux niveaux
    # rend un nombre qui n'est la mesure de rien, et la sonde le montre plutôt que de l'affirmer.
    v("⚠⚠ les médianes en µm se réagrègent par MÉDIANE et non par somme",
      j["tout"]["sur_la_normale_um_des_pas_qui_sautent"] == 75.621
      and j["tout"]["sur_la_tangente_um_des_pas_qui_sautent"] == 98.4)
    # ⚠ Et une case qui ne les porte pas est sautée, pas lue comme un niveau nul.
    sans_niveaux = {k: v_ for k, v_ in bon["cases"][1].items()
                    if not k.startswith("sur_la_")}
    mixte = _cumuler([sans_niveaux, bon["cases"][2]], "mixte")
    v("⚠ une case sans niveau est SAUTÉE, jamais lue comme un niveau nul",
      mixte["sur_la_normale_um_des_pas_qui_sautent"] == 75.621
      and _cumuler([sans_niveaux], "seule").get(
          "sur_la_normale_um_des_pas_qui_sautent") is None)

    print("\n— `mesurer`, `reagreger`, `afficher` —")
    petite = mesurer(matieres=(LA_SPIRALE_NUE,), bruits=(0.0,), regles=(REGLES[0],), departs=2)
    v("⭐⭐⭐ sur la spirale NUE la mesure réelle ne trouve rien à apparier",
      petite["juger"]["le_controle_de_la_spirale_nue"]["il_est_vide"] is True)
    avant = json.loads(json.dumps(petite["autopsie"]))
    r2 = reagreger(json.loads(json.dumps(petite)))
    v("⭐⭐⭐ `reagreger` ne touche PAS un seul nombre mesuré", r2["autopsie"] == avant)
    tampon = io.StringIO()
    with contextlib.redirect_stdout(tampon):
        afficher({"juger": j, "autopsie": bon})
    sortie = tampon.getvalue()
    v("⚠ `afficher` rend le contrôle, les deux tableaux et le verdict",
      "contrôle" in sortie and "par matière" in sortie and "par bras" in sortie
      and "recentrage" in sortie and "(aucun pas ne saute)" in sortie,
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
