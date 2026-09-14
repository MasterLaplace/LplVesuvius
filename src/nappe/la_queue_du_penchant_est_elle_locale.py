#!/usr/bin/env python3
"""La queue du penchant est-elle LOCALE, ou diffuse ?

⭐⭐⭐⭐ POURQUOI CE FICHIER. `140` reproduit les trois grandeurs du rouleau a **5,5 %** avec
l'ecrasement mesure plus un froissement, et laisse UNE chose ouverte, explicitement : le p90 du
penchant du rouleau (**48,36°**, `137`) depasse largement celui de la meilleure matiere, donc sa
distribution d'angles a une queue que deux causes REGULIERES ne fabriquent pas. Ce reste n'est pas
une curiosite de statisticien. Le graal demande ce qui remplace l'humain qui corrige le transfert de
spire a spire, et un humain corrige **la ou le chemin part de travers** : si l'exces tient dans
quelques morceaux CONTIGUS, une machine a besoin d'une alarme locale et son taux se mesure ; s'il
est etale sur tous les pas, aucune correction locale n'aide et la conversion se traite en bloc.

⭐⭐⭐ ET LA BONNE GRANDEUR N'EST PAS p90/MEDIANE. Sur les fixtures de `140`, un plan froisse rend
p90/mediane **2,137**, AU-DESSUS du rouleau (1,898) — uniquement parce que sa mediane frole zero.
Ce qui relie la queue au nombre publie (**1,186**, `136`) est le progres radial qu'un pas ABANDONNE :
`e = 1 - cos(theta)`. Leur moyenne rend le rapport par `1/(1 - moyenne(e))`, donc leur somme EST
l'exces de chemin, et on peut demander ou il se trouve. Deux questions, et elles se separent :
  · la CONCENTRATION — quelle part de la somme tient dans peu de pas ; elle survit a un melange ;
  · le GROUPEMENT — ces pas sont-ils CONTIGUS ; un melange le detruit.

⚠⚠ DEUX CONFONDS, ET CHACUN RENDRAIT LA MESURE VRAIE POUR LA MAUVAISE RAISON.
  1. Le marcheur porte un CAP (memoire 0,75), donc ses directions successives sont correlees PAR
     CONSTRUCTION. Un test de permutation sur le rouleau seul est donc incapable d'echouer : il
     mesurerait le cap. Ce sont les fixtures, marchees avec le MEME cap, qui le rendent capable
     d'echouer — le rouleau doit depasser ce que le cap fabrique tout seul.
  2. Les fixtures de `140` sont SANS BRUIT, le rouleau non. « La queue du rouleau est plus lourde »
     pourrait donc vouloir dire « le rouleau est bruite ». Le bruit est donc BALAYE (0, 8, 24) et
     jamais pose : ce qu'on regarde est la pente, pas un niveau choisi.

⚠ LES PAS SONT COMPTES A LONGUEUR EGALE. `137` publie les angles pas a pas, pas les avances pas a
pas : l'exces est donc le `1 - cos` non pondere. Le rapport qu'il rend est a verifier contre `136`,
pas a confondre avec lui — c'est un autre estimateur de la meme quantite.

⚠ LA BOITE DES FIXTURES EST ELARGIE. Dans celle de `140`, une marche partie vers les y ou x bas
sort du volume apres dix-huit pas : comparer une marche de rouleau de soixante-quinze pas a une
fixture tronquee a dix-huit serait comparer deux longueurs, pas deux matieres.

Usage :
    uv run python src/nappe/la_queue_du_penchant_est_elle_locale.py --verifier
    uv run python src/nappe/la_queue_du_penchant_est_elle_locale.py \\
        --json docs/mesures/la_queue_du_penchant_est_elle_locale.json
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

CHEMIN = RACINE / "docs" / "mesures" / "le_chemin_penche_t_il_ou_serpente_t_il.json"
# ⚠ Le cap du rouleau qu'on compare est celui dont `137` publie les 25,48° : les fixtures marchent
# avec le meme, sinon la comparaison porterait sur le marcheur et pas sur la matiere.
CAP = 0.75
AMPLITUDE_UM = 100.0
LONGUEUR_DONDE_UM = 393.6
# ⚠ Balaye, jamais pose : un seul niveau de bruit serait un nombre choisi pour que ca tombe.
BRUITS = (0.0, 8.0, 24.0)
RAYON_MM = 10.0
CENTRE_YX_VX = (16000.0, 16000.0)
FORME = (4000, 32000, 32000)
DEPARTS = 12
PAS_MAX = 75
# ⚠ Ce n'est pas un seuil regle sur ce qui passe : c'est ce qu'un test de permutation exige. A huit
# pas il y a quarante mille ordres possibles, donc le nul est peuple ; en dessous il ne l'est pas.
PAS_MINIMAL = 8
TIRAGES = 2000
GRAINE = 7
PARTS = (0.10, 0.20, 0.50)
PART_DES_MORCEAUX = 0.50


def lexces_par_pas(angles_deg) -> np.ndarray:
    """Le progres radial que chaque pas ABANDONNE : `1 - cos(theta)`.

    ⭐ C'est la grandeur qui relie la queue au nombre publie. L'etendue radiale d'une marche vaut
    la somme des `cos`, son chemin la somme des avances, donc a longueur de pas egale le rapport
    chemin/etendue vaut `1 / (1 - moyenne(e))` : la somme des `e` EST l'exces, et demander ou il se
    trouve est une question sur la matiere.

    ⚠ On n'utilise PAS `1/cos - 1`, qui diverge a 90° et change de signe au-dela. `137` compte des
    pas au-dela de 90° ; une grandeur qui explose sur eux ferait dire a une poignee de pas tout ce
    que la mesure raconte.
    """
    return 1.0 - np.cos(np.radians(np.asarray(angles_deg, dtype=float)))


def la_concentration(e) -> dict:
    """Quelle part de l'exces tient dans les pas les plus chers — balayee, jamais seuillee.

    ⚠ Toutes ces grandeurs sont INVARIANTES par melange : elles decrivent la distribution, pas
    l'ordre. C'est ce qui les separe du groupement, et la batterie le verifie.
    """
    x = np.sort(np.asarray(e, dtype=float))[::-1]
    n = x.size
    s = float(x.sum())
    if n == 0 or s <= 0.0:
        return {"decidable": False, "pas": int(n), "raison": "aucun exces a repartir"}
    croissant = x[::-1]
    gini = float((2.0 * np.arange(1, n + 1) - n - 1.0) @ croissant / (n * s))
    moyenne = float(x.mean())
    out = {"decidable": True, "pas": int(n), "moyenne": round(moyenne, 4),
           "rapport": round(1.0 / (1.0 - moyenne), 4) if moyenne < 1.0 else None,
           "gini": round(gini, 4)}
    for part in PARTS:
        k = max(1, int(round(float(part) * n)))
        out[f"part_du_sommet_{int(round(part * 100))}"] = round(float(x[:k].sum() / s), 4)
    return out


def le_groupement(e, tirages: int = TIRAGES, graine: int = GRAINE) -> dict:
    """Les pas chers sont-ils CONTIGUS ? Compare l'ordre reel aux memes valeurs melangees.

    ⭐⭐ Le nul est le MELANGE DES MEMES VALEURS, donc la distribution est tenue fixe et seul
    l'ordre bouge. Un nul tire d'une loi ajustee testerait la loi en meme temps que l'ordre.

    ⚠⚠ Un `z` positif ne prouve rien a lui seul : le marcheur porte un cap, donc il fabrique de la
    correlation sur n'importe quelle matiere. Ce qui se lit est l'ECART aux fixtures.
    """
    x = np.asarray(e, dtype=float)
    n = x.size
    if n < PAS_MINIMAL:
        return {"decidable": False, "pas": int(n),
                "raison": f"moins de {PAS_MINIMAL} pas, le nul n'est pas peuple"}

    def autocorrelation(v: np.ndarray) -> float:
        w = v - v.mean()
        d = float(w @ w)
        return float(w[:-1] @ w[1:] / d) if d > 0.0 else 0.0

    observe = autocorrelation(x)
    tir = np.random.default_rng(int(graine))
    nul = np.array([autocorrelation(tir.permutation(x)) for _ in range(int(tirages))])
    ecart = float(nul.std(ddof=1))
    return {"decidable": True, "pas": int(n), "autocorrelation": round(observe, 4),
            "nul_moyenne": round(float(nul.mean()), 4), "nul_ecart": round(ecart, 4),
            "z": round(float((observe - nul.mean()) / ecart), 2) if ecart > 0.0 else None,
            "p_au_moins_aussi_groupe": round(float((nul >= observe).mean()), 5)}


def les_morceaux_qui_portent(e, part: float = PART_DES_MORCEAUX) -> dict:
    """Combien de MORCEAUX contigus portent cette part de l'exces, et de quelle longueur.

    ⭐⭐ C'est le nombre actionnable : un derouleur qui doit lever une alarme la ou le chemin part
    de travers a besoin de savoir COMBIEN d'endroits regarder par traversee. Deux morceaux se
    surveillent, quinze pas isoles ne se surveillent pas.

    ⚠ Le nombre de pas retenus est MINIMAL par construction : on prend les plus chers jusqu'a
    atteindre la part, donc rien n'est choisi — ni un seuil d'angle, ni une longueur de fenetre.
    """
    x = np.asarray(e, dtype=float)
    n = x.size
    s = float(x.sum())
    if n == 0 or s <= 0.0:
        return {"decidable": False, "pas": int(n), "raison": "aucun exces a repartir"}
    ordre = np.argsort(-x, kind="stable")
    cumul = np.cumsum(x[ordre])
    k = int(np.searchsorted(cumul, float(part) * s) + 1)
    k = min(max(k, 1), n)
    retenus = np.sort(ordre[:k])
    coupures = np.flatnonzero(np.diff(retenus) > 1)
    longueurs = np.diff(np.concatenate(([0], coupures + 1, [k])))
    return {"decidable": True, "pas": int(n), "part": float(part), "pas_retenus": int(k),
            "part_des_pas": round(k / n, 4), "morceaux": int(longueurs.size),
            # ⚠⚠ UN COMPTE DE MORCEAUX DEPEND DE LA LONGUEUR DE LA MARCHE. Les marches du rouleau
            # font 45 pas en mediane, celles des fixtures 75 : comparer les comptes bruts ferait
            # passer pour « moins local » ce qui est seulement « plus court ». Le compte rapporte
            # a cent pas est ce qui se compare.
            "morceaux_par_cent_pas": round(100.0 * longueurs.size / n, 2),
            "longueur_mediane": round(float(np.median(longueurs)), 2),
            "longueur_max": int(longueurs.max())}


def _resumer(angles) -> dict:
    """Les trois blocs d'une marche, ET les angles dont ils sortent.

    ⚠⚠ Les angles pas a pas sont RANGES dans la mesure, des deux cotes. C'est ce qui rend le JSON
    auto-suffisant : une regle de jugement qui change ne doit pas couter une marche de plus, et une
    figure qui veut montrer OU tombe l'exces a besoin de la suite, pas de son resume. `138` a paye
    exactement ca avec son `--reagreger`.
    """
    # ⚠⚠ ON ARRONDIT D'ABORD, ET ON CALCULE ENSUITE. L'inverse rangeait des angles arrondis sous
    # des nombres calcules sur les angles pleins : les chiffres publies n'etaient alors PAS
    # reproductibles depuis les angles publies, ce qui est exactement ce que ce depot appelle un
    # nombre sans producteur. Les deux sources donnent deja deux decimales, donc rien ne bouge —
    # mais l'invariant cesse de dependre de cette coincidence.
    ronds = [round(float(x), 2) for x in angles]
    e = lexces_par_pas(ronds)
    return {"angles_deg": ronds, "p90_sur_mediane": _p90_sur_mediane(ronds),
            "concentration": la_concentration(e),
            "groupement": le_groupement(e), "morceaux": les_morceaux_qui_portent(e)}


def _p90_sur_mediane(angles) -> float | None:
    """La grandeur EVIDENTE, produite pour qu'on puisse montrer qu'elle ne convient pas.

    ⚠⚠ Elle est publiee par ce fichier UNIQUEMENT parce que le document s'en sert pour dire
    pourquoi il ne la retient pas. Un rapport de quantiles ne dit rien quand le denominateur frole
    zero : une matiere dont le penchant median est presque nul rend un p90/mediane enorme sans
    porter le moindre exces. Un chiffre publie dont le calcul n'est pas dans l'arbre est une
    anecdote, donc il est calcule ici plutot que cite de memoire.
    """
    a = np.asarray(angles, dtype=float)
    med = float(np.median(a))
    return round(float(np.percentile(a, 90)) / med, 4) if med > 0.0 else None


def _rejuger(r: dict) -> dict:
    """Recalcule tout ce qui se derive des angles ranges — sans remarcher quoi que ce soit."""
    b = r["le_rouleau"]
    b["marches"] = [{**m, **_resumer(m["angles_deg"])} for m in b["marches"]]
    b.update(_mediane_des_marches(b["marches"]))
    for lot in r["sur_les_fixtures"]["lots"]:
        lot["marches"] = [{**m, **_resumer(m["angles_deg"])} for m in lot["marches"]]
        lot.update(_mediane_des_marches(lot["marches"]))
    r["juger"] = juger(b, r["sur_les_fixtures"])
    return r


def le_rouleau(chemin: Path = CHEMIN, cap: float = CAP) -> dict:
    """Les marches du rouleau que `137` a publiees, et leur queue.

    ⚠ Aucune lecture distante : les angles pas a pas sont deja dans la mesure de `137`. Ce fichier
    ne remarche pas le rouleau, il relit ce qu'une marche a deja rendu.
    """
    if not Path(chemin).exists():
        return {"decidable": False, "message": f"mesure de `137` absente : {chemin}"}
    c = json.loads(Path(chemin).read_text())
    courses = [x for x in c.get("par_course", [])
               if abs(float(x.get("memoire_du_cap", -1.0)) - float(cap)) < 1e-9]
    if not courses:
        return {"decidable": False, "message": f"aucune course a cap {cap}"}
    course = courses[0]
    marches = []
    for m in course.get("marches", []):
        angles = m.get("angles_deg") or []
        if not m.get("decidable") or len(angles) < PAS_MINIMAL:
            continue
        marches.append({"marche": m.get("marche"), "rayon_mm": m.get("rayon_mm"),
                        "penchant_median_deg": m.get("angle_median_deg"), **_resumer(angles)})
    return {"decidable": len(marches) >= 2, "source": str(Path(chemin).name),
            "memoire_du_cap": float(cap), "marches": marches, **_mediane_des_marches(marches)}


def _mediane_des_marches(marches: list[dict]) -> dict:
    """La mediane sur les marches de chaque grandeur, et l'etendue qu'elles couvrent.

    ⚠⚠ On ne MET PAS les marches en commun avant de resumer. Deux marches n'ont ni le meme rayon ni
    le meme exces moyen, donc un gini calcule sur leur reunion mesurerait surtout l'ecart ENTRE
    marches — une moyenne sur l'axe ou vit la difference, ce que ce depot compte comme une faute.
    """
    out: dict = {"n_marches": len(marches)}
    vals = [m["p90_sur_mediane"] for m in marches if m.get("p90_sur_mediane") is not None]
    if vals:
        out["p90_sur_mediane_median"] = round(float(np.median(vals)), 4)
        out["p90_sur_mediane_max"] = round(float(np.max(vals)), 4)
    for bloc, cle, nom in (("concentration", "gini", "gini"),
                           ("concentration", "part_du_sommet_20", "part_du_sommet_20"),
                           ("concentration", "moyenne", "exces_moyen"),
                           ("concentration", "rapport", "rapport"),
                           ("groupement", "z", "z"),
                           ("groupement", "autocorrelation", "autocorrelation"),
                           ("morceaux", "morceaux", "morceaux"),
                           ("morceaux", "morceaux_par_cent_pas", "morceaux_par_cent_pas"),
                           ("concentration", "pas", "pas"),
                           ("morceaux", "longueur_mediane", "longueur_des_morceaux")):
        vals = [m[bloc][cle] for m in marches
                if m.get(bloc, {}).get("decidable") and m[bloc].get(cle) is not None]
        if vals:
            out[f"{nom}_median"] = round(float(np.median(vals)), 4)
            out[f"{nom}_min"] = round(float(np.min(vals)), 4)
            out[f"{nom}_max"] = round(float(np.max(vals)), 4)
    return out


def sur_les_fixtures(ecrasement: float, amplitude_um: float = AMPLITUDE_UM, bruits=BRUITS,
                     departs: int = DEPARTS, pas_max: int = PAS_MAX, rayon_mm: float = RAYON_MM,
                     longueur_donde_um: float = LONGUEUR_DONDE_UM, graine: int = 3) -> dict:
    """La meme queue, sur des matieres dont on connait la cause — et sur la spirale nue.

    ⭐⭐⭐ LA SPIRALE NUE EST LE TEMOIN QUI COMPTE : elle n'a ni ecrasement, ni froissement, ni
    bruit, donc tout groupement qu'on y lit est fabrique par le CAP et par rien d'autre. C'est le
    plancher au-dessus duquel le rouleau doit passer pour que « la queue est locale » veuille dire
    quelque chose.
    """
    from combien_de_pas_la_matiere_porte import VolumeFabriqueEnSpiraleFroissee  # noqa: PLC0415

    import lecrasement_explique_t_il_lobliquite as Q  # noqa: PLC0415

    barres = Q._barres()
    C = barres[-1]
    lots = [(0.0, 0.0, 0.0)] + [(float(ecrasement), float(amplitude_um), float(b)) for b in bruits]
    lots += [(0.0, 0.0, float(max(bruits)))]
    out = []
    for ecr, amp, bruit in lots:
        vol = VolumeFabriqueEnSpiraleFroissee(
            C.PAS_UM, amplitude_um=amp, longueur_donde_um=float(longueur_donde_um),
            ecrasement=ecr, r0_um=float(rayon_mm) * 1000.0, bruit=bruit,
            centre_yx_vx=CENTRE_YX_VX, forme=FORME, graine=int(graine))
        marches = []
        for k in range(int(departs)):
            m = Q.une_marche(vol, 2.0 * np.pi * k / int(departs), barres, rayon_mm, pas_max)
            if m is None or len(m.get("angles_deg", [])) < PAS_MINIMAL:
                continue
            marches.append({"angle_deg": m["angle_deg"], "pas": m["pas"],
                            "rapport_marche": m["rapport"],
                            "penchant_median_deg": m["penchant_median_deg"],
                            "coherence_tangentielle": m["coherence_tangentielle"],
                            **_resumer(m["angles_deg"])})
        out.append({"ecrasement": ecr, "amplitude_um": amp, "bruit": bruit,
                    "nom": _nom_du_lot(ecr, amp, bruit), "marches": marches,
                    **_mediane_des_marches(marches)})
    return {"rayon_mm": float(rayon_mm), "pas_max": int(pas_max), "departs": int(departs),
            "longueur_donde_um": float(longueur_donde_um), "amplitude_um": float(amplitude_um),
            "ecrasement": float(ecrasement), "bruits": [float(b) for b in bruits], "lots": out}


def _nom_du_lot(ecrasement: float, amplitude_um: float, bruit: float) -> str:
    causes = []
    if ecrasement > 0.0:
        causes.append("écrasée")
    if amplitude_um > 0.0:
        causes.append("froissée")
    nom = "spirale nue" if not causes else "spirale " + " et ".join(causes)
    return nom + (f", bruit {bruit:g}" if bruit > 0.0 else ", sans bruit")


def juger(rouleau: dict, fixtures: dict) -> dict:
    """Le rouleau depasse-t-il TOUTE fixture, ou tombe-t-il dedans ?

    ⚠⚠ La comparaison porte sur le MAXIMUM des marches de fixture, pas sur leur mediane. Deux
    medianes qui different alors que les etendues se recouvrent ne separent rien : le rouleau doit
    passer au-dessus de ce que la matiere reguliere fait DE PIRE, sinon la queue qu'il a n'est pas
    une queue qu'elle n'a pas. La part des marches de fixture au-dessus du rouleau est publiee a
    cote, parce qu'elle dit ou le rouleau tombe DANS la distribution et pas seulement sous son bord.

    ⚠⚠ ET LE VERDICT NE PEUT PAS PORTER SUR LE `z`. Un `z` de permutation croit comme la racine du
    nombre de pas a correlation egale, et les marches du rouleau font 45 pas la ou celles des
    fixtures en font 75 : juger dessus favoriserait les fixtures par leur seule longueur. Le
    verdict porte donc sur l'autocorrelation et sur la part du sommet, qui ne portent pas de
    longueur ; le `z` reste publie, parce qu'il dit si le groupement est reel, pas s'il est plus
    fort qu'ailleurs.
    """
    marches = [m for lot in fixtures.get("lots", []) for m in lot.get("marches", [])]
    if not rouleau.get("decidable") or not marches:
        return {"decidable": False,
                "raison": "il faut des marches des deux cotes pour comparer quoi que ce soit"}
    out: dict = {"decidable": True, "marches_du_rouleau": rouleau["n_marches"],
                 "marches_de_fixture": len(marches)}
    for bloc, cle, nom in (("concentration", "gini", "gini"),
                           ("concentration", "part_du_sommet_20", "part_du_sommet_20"),
                           ("groupement", "autocorrelation", "autocorrelation"),
                           ("groupement", "z", "z")):
        med = rouleau.get(f"{nom}_median")
        vals = [m[bloc][cle] for m in marches
                if m.get(bloc, {}).get("decidable") and m[bloc].get(cle) is not None]
        if med is None or not vals:
            continue
        out[f"{nom}_du_rouleau"] = med
        out[f"{nom}_pire_fixture"] = round(float(np.max(vals)), 4)
        out[f"{nom}_part_des_fixtures_au_dessus"] = round(
            float(np.mean(np.asarray(vals) >= med)), 4)
        out[f"le_rouleau_depasse_toute_fixture_en_{nom}"] = bool(med > float(np.max(vals)))
    # ⭐ Le nombre actionnable : combien d'endroits une alarme doit surveiller par traversee.
    out["morceaux_du_rouleau"] = rouleau.get("morceaux_median")
    out["longueur_des_morceaux_du_rouleau"] = rouleau.get("longueur_des_morceaux_median")
    out["pas_du_rouleau_median"] = round(float(np.median(
        [m["concentration"]["pas"] for m in rouleau["marches"]])), 1)
    # ⚠ La pente du bruit : si la queue du rouleau etait du bruit, elle serait atteinte en montant
    # le bruit. On publie la suite, pas un verdict sur un niveau.
    pente = []
    for lot in fixtures.get("lots", []):
        if lot.get("ecrasement", 0.0) > 0.0 and lot.get("z_median") is not None:
            pente.append({"bruit": lot["bruit"], "z_median": lot["z_median"],
                          "autocorrelation_median": lot.get("autocorrelation_median"),
                          "gini_median": lot.get("gini_median"),
                          "morceaux_par_cent_pas_median": lot.get("morceaux_par_cent_pas_median")})
    out["la_pente_du_bruit"] = sorted(pente, key=lambda x: x["bruit"])
    out["morceaux_par_cent_pas_du_rouleau"] = rouleau.get("morceaux_par_cent_pas_median")
    out["morceaux_par_cent_pas_pire_fixture"] = round(float(np.max(
        [m["morceaux"]["morceaux_par_cent_pas"] for m in marches
         if m.get("morceaux", {}).get("decidable")])), 2)
    out["la_queue_est_locale"] = bool(
        out.get("le_rouleau_depasse_toute_fixture_en_autocorrelation")
        and out.get("le_rouleau_depasse_toute_fixture_en_part_du_sommet_20"))
    return out


def mesurer(chemin: Path = CHEMIN, cap: float = CAP, departs: int = DEPARTS,
            pas_max: int = PAS_MAX, bruits=BRUITS) -> dict:
    from lecrasement_explique_t_il_lobliquite import (  # noqa: PLC0415
        lecrasement_que_la_surface_impose)

    rouleau = le_rouleau(chemin, cap)
    if not rouleau.get("decidable"):
        return {"message": rouleau.get("message", "le rouleau n'a pas assez de marches")}
    # ⚠ L'ecrasement se DERIVE de `135` par le meme chemin que `140` — jamais recopie a la main :
    # un attendu ecrit en dur redevient faux des qu'une constante bouge.
    ecrase = lecrasement_que_la_surface_impose()
    fixtures = sur_les_fixtures(ecrase["ecrasement"], departs=departs, pas_max=pas_max,
                                bruits=bruits)
    return {"lecrasement_que_la_surface_impose": ecrase, "le_rouleau": rouleau,
            "sur_les_fixtures": fixtures, "juger": juger(rouleau, fixtures)}


def afficher(r: dict) -> None:
    if "message" in r:
        print(f"⚠ {r['message']}")
        return
    b = r["le_rouleau"]
    print(f"le rouleau, {b['n_marches']} marches de `137` à cap {b['memoire_du_cap']} — "
          f"l'excès `1 − cos θ` et où il se trouve :")
    print(f"   {'marche':>6} {'rayon':>7} {'pas':>4} {'exc. moy':>9} {'rapport':>8} {'gini':>6} "
          f"{'top 20 %':>9} {'ρ₁':>7} {'z':>7} {'morceaux':>9} {'long.':>6}")
    for m in b["marches"]:
        c, g, k = m["concentration"], m["groupement"], m["morceaux"]
        print(f"   {m['marche']:>6} {m['rayon_mm']:>6.2f}mm {c['pas']:>4} {c['moyenne']:>9.4f} "
              f"{(c['rapport'] if c['rapport'] is not None else float('nan')):>8.4f} "
              f"{c['gini']:>6.3f} {c['part_du_sommet_20']:>9.3f} "
              f"{(g.get('autocorrelation') or 0.0):>+7.3f} {(g.get('z') or 0.0):>+7.2f} "
              f"{k['morceaux']:>9} {k['longueur_mediane']:>6.1f}")
    print(f"   {'médiane':>6} {'':>7} {b.get('n_marches', 0):>4} "
          f"{b.get('exces_moyen_median', 0.0):>9.4f} {b.get('rapport_median', 0.0):>8.4f} "
          f"{b.get('gini_median', 0.0):>6.3f} {b.get('part_du_sommet_20_median', 0.0):>9.3f} "
          f"{b.get('autocorrelation_median', 0.0):>+7.3f} {b.get('z_median', 0.0):>+7.2f} "
          f"{b.get('morceaux_median', 0.0):>9.1f} {b.get('longueur_des_morceaux_median', 0.0):>6.1f}")
    f = r["sur_les_fixtures"]
    print(f"\nles fixtures (rayon {f['rayon_mm']} mm, {f['pas_max']} pas, {f['departs']} départs, "
          f"même cap) — écrasement {f['ecrasement']}, froissement {f['amplitude_um']} µm :")
    print(f"   {'matière':>38} {'n':>3} {'pas':>4} {'exc. moy':>9} {'gini':>6} {'top 20 %':>9} "
          f"{'ρ₁':>7} {'z':>7} {'morc./100':>10}")
    for lot in f["lots"]:
        if not lot["marches"]:
            print(f"   {lot['nom']:>38} {0:>3}   aucune marche")
            continue
        print(f"   {lot['nom']:>38} {lot['n_marches']:>3} {lot.get('pas_median', 0.0):>4.0f} "
              f"{lot.get('exces_moyen_median', 0.0):>9.4f} "
              f"{lot.get('gini_median', 0.0):>6.3f} {lot.get('part_du_sommet_20_median', 0.0):>9.3f} "
              f"{lot.get('autocorrelation_median', 0.0):>+7.3f} "
              f"{lot.get('z_median', 0.0):>+7.2f} "
              f"{lot.get('morceaux_par_cent_pas_median', 0.0):>10.2f}")
    j = r.get("juger", {})
    if not j.get("decidable"):
        print(f"\n⚠ {j.get('raison', 'indécidable')}")
        return
    print(f"\n   le rouleau contre la PIRE marche de fixture :")
    for nom, libelle in (("autocorrelation", "groupement (ρ₁)"),
                         ("part_du_sommet_20", "top 20 % de l'excès"),
                         ("gini", "gini de l'excès"), ("z", "significativité (z)")):
        if f"{nom}_du_rouleau" not in j:
            continue
        marque = "★" if j.get(f"le_rouleau_depasse_toute_fixture_en_{nom}") else "✗"
        print(f"     {marque} {libelle:>20} : rouleau {j[f'{nom}_du_rouleau']:>7.3f}  "
              f"pire fixture {j[f'{nom}_pire_fixture']:>7.3f}  "
              f"fixtures au-dessus {j[f'{nom}_part_des_fixtures_au_dessus']:.1%}")
    if j.get("la_pente_du_bruit"):
        print("   la pente du bruit (même matière, bruit croissant) : "
              + " · ".join(f"bruit {x['bruit']:g} → ρ₁ {x['autocorrelation_median']:+.3f}, gini "
                           f"{x['gini_median']:.3f}, {x['morceaux_par_cent_pas_median']:.2f} "
                           f"morceaux/100 pas" for x in j["la_pente_du_bruit"]))
    marque = "★★★★" if j["la_queue_est_locale"] else "✗"
    print(f"\n{marque} la queue est LOCALE : {j['la_queue_est_locale']} — "
          f"{j['morceaux_du_rouleau']:.1f} morceaux de {j['longueur_des_morceaux_du_rouleau']:.1f} "
          f"pas portent la moitié de l'excès d'une traversée de "
          f"{j['pas_du_rouleau_median']:.0f} pas, soit "
          f"{j['morceaux_par_cent_pas_du_rouleau']:.2f} morceaux pour cent pas contre "
          f"{j['morceaux_par_cent_pas_pire_fixture']:.2f} au pire des fixtures")


def verifier() -> int:
    echecs = controles = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # ---- l'excès par pas
    v("un pas radial n'abandonne rien", abs(float(lexces_par_pas([0.0])[0])) < 1e-12)
    v("un pas à 60° en abandonne la moitié", abs(float(lexces_par_pas([60.0])[0]) - 0.5) < 1e-9)
    v("un pas à 90° l'abandonne tout", abs(float(lexces_par_pas([90.0])[0]) - 1.0) < 1e-9)
    v("... et un pas au-delà de 90° reste borné, jamais divergent",
      1.0 < float(lexces_par_pas([120.0])[0]) <= 2.0,
      f"{float(lexces_par_pas([120.0])[0]):.4f}")
    for th in (10.0, 25.48, 40.0):
        e = lexces_par_pas([th] * 50)
        c = la_concentration(e)
        attendu = 1.0 / np.cos(np.radians(th))
        v(f"à angle constant {th}° le rapport rendu est bien 1/cos",
          abs(c["rapport"] - attendu) < 5e-4, f"{c['rapport']} contre {attendu:.4f}")

    # ---- la concentration
    c = la_concentration(np.full(40, 0.2))
    v("une matière sans queue a un gini nul", abs(c["gini"]) < 1e-9)
    v("... et ses vingt pour cent de pas portent vingt pour cent de l'excès",
      abs(c["part_du_sommet_20"] - 0.20) < 1e-9)
    un = np.zeros(40)
    un[7] = 1.0
    c1 = la_concentration(un)
    v("un excès porté par un seul pas a un gini presque un",
      c1["gini"] > 0.97, f"{c1['gini']}")
    tir = np.random.default_rng(11)
    ale = tir.random(60) ** 3
    c2 = la_concentration(ale)
    v("les parts du sommet croissent avec la part demandée",
      c2["part_du_sommet_10"] <= c2["part_du_sommet_20"] <= c2["part_du_sommet_50"])
    v("la concentration refuse un excès nul", not la_concentration(np.zeros(20))["decidable"])

    # ---- ⭐ la grandeur ÉVIDENTE, et pourquoi elle est écartée
    v("p90/médiane est le rapport de deux quantiles des angles",
      abs(_p90_sur_mediane([10.0] * 50 + [40.0] * 50) - 40.0 / 25.0) < 0.02,
      f"{_p90_sur_mediane([10.0] * 50 + [40.0] * 50)}")
    # ⚠ L'attendu est DÉRIVÉ d'une comparaison, jamais d'un seuil posé : la matière qui ne porte
    # presque rien doit rendre un rapport PLUS GRAND que celle qui porte mille fois plus d'excès.
    plat_, charge_ = [0.01] * 90 + [2.0] * 10, [20.0] * 90 + [40.0] * 10
    ep, ec = float(lexces_par_pas(plat_).mean()), float(lexces_par_pas(charge_).mean())
    v("⭐⭐ ... et il est PLUS GRAND sur une matière qui ne porte presque aucun excès",
      _p90_sur_mediane(plat_) > _p90_sur_mediane(charge_) and ep < ec / 100.0,
      f"{_p90_sur_mediane(plat_)} pour un excès {ep:.2e}, contre "
      f"{_p90_sur_mediane(charge_)} pour {ec:.4f}")
    v("... et il est indéfini, jamais deviné, quand la médiane est nulle",
      _p90_sur_mediane([0.0] * 20) is None)

    # ---- ⭐ la sonde de structure : l'une survit au mélange, l'autre non
    bloc = np.concatenate([np.full(12, 1.0), np.full(48, 0.05)])
    melange = np.random.default_rng(5).permutation(bloc)
    cb, cm = la_concentration(bloc), la_concentration(melange)
    v("⭐ la concentration est INVARIANTE par mélange",
      abs(cb["gini"] - cm["gini"]) < 1e-9 and abs(cb["part_du_sommet_20"]
                                                  - cm["part_du_sommet_20"]) < 1e-9,
      f"gini {cb['gini']} contre {cm['gini']}")
    gb, gm = le_groupement(bloc), le_groupement(melange)
    v("⭐ le groupement, lui, est DÉTRUIT par le mélange",
      gb["z"] > 5.0 and abs(gm["z"]) < 3.0, f"bloc z {gb['z']}, mélangé z {gm['z']}")
    v("... et les deux portent bien les mêmes valeurs",
      abs(float(bloc.sum()) - float(melange.sum())) < 1e-9)

    # ---- le groupement
    alterne = np.array([1.0, 0.0] * 20)
    ga = le_groupement(alterne)
    v("une suite qui alterne est ANTI-groupée, donc le z peut aller dans les deux sens",
      ga["z"] < -5.0, f"z {ga['z']}")
    v("le groupement refuse une marche trop courte pour un nul",
      not le_groupement(np.arange(PAS_MINIMAL - 1, dtype=float))["decidable"])
    v("... et l'accepte juste au-dessus", le_groupement(np.arange(PAS_MINIMAL,
                                                                 dtype=float))["decidable"])
    v("le groupement est reproductible à graine égale",
      le_groupement(bloc, graine=3)["z"] == le_groupement(bloc, graine=3)["z"])
    # ⚠⚠ LE CONFOND QUI A FAIT CHANGER LE VERDICT DE GRANDEUR : a correlation egale, un `z` de
    # permutation croit avec la longueur. Les marches du rouleau sont plus COURTES que celles des
    # fixtures, donc juger sur le `z` les aurait desavantagees pour une raison qui n'est pas la
    # matiere. La batterie le montre plutot que de l'affirmer.
    court = np.concatenate([np.full(6, 1.0), np.full(24, 0.05)])
    long_ = np.tile(court, 3)
    gc, gl = le_groupement(court), le_groupement(long_)
    v("⭐⭐ à corrélation quasi égale, le z CROÎT avec la longueur",
      abs(gc["autocorrelation"] - gl["autocorrelation"]) < 0.12 and gl["z"] > gc["z"] * 1.5,
      f"ρ₁ {gc['autocorrelation']} → {gl['autocorrelation']} ; z {gc['z']} → {gl['z']}")
    v("... c'est pourquoi le verdict porte sur ρ₁ et non sur le z",
      "autocorrelation" in le_groupement(court))
    mc, ml = les_morceaux_qui_portent(court), les_morceaux_qui_portent(long_)
    v("⭐ un COMPTE de morceaux croît avec la longueur", ml["morceaux"] > mc["morceaux"],
      f"{mc['morceaux']} → {ml['morceaux']}")
    v("... et le taux EST ce compte rapporté à cent pas, par définition",
      all(abs(x["morceaux_par_cent_pas"] - 100.0 * x["morceaux"] / x["pas"]) <= 0.005
          for x in (mc, ml)), "la tolérance est celle de l'arrondi publié, pas un choix")
    # ⚠ Le taux n'est PAS invariant par repetition — je l'avais ecrit et c'etait faux : la moitie
    # d'une suite repetee ne couvre pas tous ses blocs. Ce qui est vrai, et qui suffit, est qu'il
    # bouge MOINS que le compte.
    v("... et il bouge moins que le compte",
      abs(np.log(ml["morceaux_par_cent_pas"] / mc["morceaux_par_cent_pas"]))
      < abs(np.log(ml["morceaux"] / mc["morceaux"])),
      f"taux {mc['morceaux_par_cent_pas']}→{ml['morceaux_par_cent_pas']}")

    # ---- les morceaux
    mo = les_morceaux_qui_portent(np.concatenate([np.full(10, 1.0), np.zeros(40)]))
    v("un excès d'un seul tenant fait UN morceau", mo["morceaux"] == 1, f"{mo}")
    # ⚠⚠ MES DEUX PREMIERS ATTENDUS ÉTAIENT FAUX, et c'est la batterie qui l'a dit. Avec deux
    # blocs ÉGAUX, la moitié de l'excès tient par définition dans UN seul — le compte de morceaux
    # suit la part demandée, il ne décrit pas le paysage. L'attendu se DÉRIVE donc de la part.
    deux = np.zeros(60)
    deux[5:12] = 1.0
    deux[40:47] = 1.0
    v("deux blocs égaux : la moitié de l'excès tient dans UN seul",
      les_morceaux_qui_portent(deux, 0.50)["morceaux"] == 1)
    v("... et l'excès ENTIER en fait bien deux",
      les_morceaux_qui_portent(deux, 1.0)["morceaux"] == 2)
    trois = np.zeros(60)
    trois[5:10] = 1.0
    trois[20:25] = 0.9
    trois[40:45] = 0.8
    v("trois blocs décroissants : la moitié en traverse DEUX",
      les_morceaux_qui_portent(trois, 0.50)["morceaux"] == 2,
      f"{les_morceaux_qui_portent(trois, 0.50)}")
    peigne = np.zeros(60)
    peigne[::6] = 1.0
    v("un peigne entier fait autant de morceaux que de dents",
      les_morceaux_qui_portent(peigne, 1.0)["morceaux"] == 10,
      f"{les_morceaux_qui_portent(peigne, 1.0)['morceaux']}")
    v("... et un peigne est bien moins groupé qu'un bloc de même excès",
      le_groupement(peigne)["z"] < le_groupement(
          np.concatenate([np.ones(10), np.zeros(50)]))["z"])
    md = les_morceaux_qui_portent(ale, part=0.5)
    x = np.sort(ale)[::-1]
    v("les pas retenus portent bien la part demandée",
      float(x[:md["pas_retenus"]].sum()) >= 0.5 * float(ale.sum()))
    v("⭐ ... et ils sont en nombre MINIMAL, donc rien n'est choisi",
      md["pas_retenus"] == 1 or float(x[:md["pas_retenus"] - 1].sum()) < 0.5 * float(ale.sum()))
    v("le nombre de pas retenus croît avec la part",
      les_morceaux_qui_portent(ale, 0.10)["pas_retenus"]
      <= les_morceaux_qui_portent(ale, 0.20)["pas_retenus"]
      <= les_morceaux_qui_portent(ale, 0.50)["pas_retenus"])
    v("les morceaux refusent un excès nul", not les_morceaux_qui_portent(np.zeros(20))["decidable"])

    # ---- le rouleau, relu de `137`
    r = le_rouleau()
    v("la mesure de `137` se relit et porte la course du bon cap",
      r.get("decidable") and r["memoire_du_cap"] == CAP, str(r.get("message", "")))
    if r.get("decidable"):
        v("... avec au moins huit marches décidables", r["n_marches"] >= 8, f"{r['n_marches']}")
        c = json.loads(CHEMIN.read_text())
        cible = [x for x in c["par_course"] if x["memoire_du_cap"] == CAP][0]
        ecarts = []
        for m in cible["marches"]:
            if not m.get("decidable") or len(m.get("angles_deg", [])) < PAS_MINIMAL:
                continue
            ecarts.append(abs(float(np.median(m["angles_deg"])) - float(m["angle_median_deg"])))
        v("⭐ les angles pas à pas relus SONT ceux dont `137` publie la médiane",
          bool(ecarts) and max(ecarts) < 0.011, f"écart max {max(ecarts):.4f}°" if ecarts else "—")
        v("toutes les marches retenues portent leurs trois blocs",
          all({"concentration", "groupement", "morceaux"} <= set(m) for m in r["marches"]))
        v("une marche INDÉCIDABLE de `137` n'entre pas",
          all(m["marche"] is not None for m in r["marches"])
          and len(r["marches"]) <= len(cible["marches"]))
    v("une source absente est dite, jamais devinée",
      not le_rouleau(Path("/inexistant/137.json")).get("decidable"))
    v("un cap qui n'a pas été marché est dit", not le_rouleau(CHEMIN, cap=0.42).get("decidable"))

    # ---- ⭐ la fixture, et le centre qui vient du volume
    from combien_de_pas_la_matiere_porte import VolumeFabriqueEnSpiraleFroissee  # noqa: PLC0415

    import lecrasement_explique_t_il_lobliquite as Q  # noqa: PLC0415

    barres = Q._barres()
    C = barres[-1]
    vol = VolumeFabriqueEnSpiraleFroissee(C.PAS_UM, amplitude_um=AMPLITUDE_UM,
                                          longueur_donde_um=LONGUEUR_DONDE_UM, ecrasement=0.2782,
                                          r0_um=RAYON_MM * 1000.0, bruit=0.0,
                                          centre_yx_vx=CENTRE_YX_VX, forme=FORME, graine=3)
    m = Q.une_marche(vol, np.pi, barres, RAYON_MM, PAS_MAX)
    v("⭐⭐ une spirale posée AILLEURS que la constante de module rend une marche décidable",
      m is not None, "le centre vient du volume, plus de la constante")
    if m is not None:
        v("... et elle tient les soixante-quinze pas dans la boîte élargie",
          m["pas"] == PAS_MAX, f"{m['pas']} pas")
        v("... la fixture rend ses angles PAS À PAS", len(m["angles_deg"]) == m["pas"])
        v("... et ce sont ceux dont elle publie la médiane",
          abs(float(np.median(m["angles_deg"])) - m["penchant_median_deg"]) < 0.011)
        v("... l'étendue radiale est positive, donc l'axe est le bon",
          m["etendue_radiale_um"] > 0.0, f"{m['etendue_radiale_um']} µm")

    # ---- le jugement
    # ⚠ Une fixture « sans queue » doit etre plate ET DESORDONNEE. Ma premiere version prenait une
    # suite MONOTONE CROISSANTE, dont l'autocorrelation vaut presque un : elle etait donc plus
    # groupee que le bloc qu'elle devait servir de plancher, et le controle disait non pour une
    # raison qui n'avait rien a voir avec la matiere.
    plat = np.random.default_rng(2).permutation(np.linspace(0.10, 0.30, 40))
    faux = {"lots": [{"ecrasement": 0.0, "amplitude_um": 0.0, "bruit": 0.0,
                      "marches": [{"concentration": la_concentration(plat),
                                   "groupement": le_groupement(plat),
                                   "morceaux": les_morceaux_qui_portent(plat)}]}]}
    vrai = {"decidable": True, "n_marches": 3, "marches": [
        {"concentration": la_concentration(bloc), "groupement": le_groupement(bloc),
         "morceaux": les_morceaux_qui_portent(bloc)}] * 3,
        **_mediane_des_marches([{"concentration": la_concentration(bloc),
                                 "groupement": le_groupement(bloc),
                                 "morceaux": les_morceaux_qui_portent(bloc)}] * 3)}
    j = juger(vrai, faux)
    v("un rouleau plus groupé que toute fixture est déclaré LOCAL",
      j.get("la_queue_est_locale") is True, str(j.get("z_pire_fixture")))
    v("⭐ ... et le MÊME objet des deux côtés ne l'est pas",
      juger(vrai, {"lots": [{"ecrasement": 0.0, "amplitude_um": 0.0, "bruit": 0.0,
                             "marches": vrai["marches"]}]}).get("la_queue_est_locale") is False,
      "un contrôle dont les deux entrées sont identiques doit dire NON")
    v("sans fixture le jugement est indécidable", not juger(vrai, {"lots": []})["decidable"])
    v("sans rouleau non plus", not juger({"decidable": False}, faux)["decidable"])

    # ---- l'affichage
    import io  # noqa: PLC0415
    import contextlib  # noqa: PLC0415

    tampon = io.StringIO()
    with contextlib.redirect_stdout(tampon):
        afficher({"message": "mesure de `137` absente"})
    v("un message est dit, jamais dessiné", "⚠" in tampon.getvalue())

    # ---- ⭐ rejuger sans remarcher rend exactement la même chose
    faux_r = {"decidable": True, "n_marches": 2,
              "marches": [{"marche": 1, "rayon_mm": 1.0, **_resumer([10.0, 40.0] * 12)},
                          {"marche": 2, "rayon_mm": 2.0, **_resumer([5.0, 30.0] * 12)}]}
    faux_r.update(_mediane_des_marches(faux_r["marches"]))
    faux_f = {"lots": [{"ecrasement": 0.0, "amplitude_um": 0.0, "bruit": 0.0,
                        "marches": [{"angle_deg": 0.0, **_resumer(list(plat * 100.0))}]}]}
    faux_f["lots"][0].update(_mediane_des_marches(faux_f["lots"][0]["marches"]))
    avant = juger(faux_r, faux_f)
    apres = _rejuger(json.loads(json.dumps(
        {"le_rouleau": faux_r, "sur_les_fixtures": faux_f})))["juger"]
    v("⭐ rejuger depuis les angles rangés rend le MÊME verdict, sans remarcher",
      avant == apres, "sinon la mesure et son jugement ne décrivent pas le même objet")
    v("... et les angles sont bien rangés des deux côtés",
      "angles_deg" in faux_r["marches"][0] and "angles_deg" in faux_f["lots"][0]["marches"][0])

    print(f"\n{'ALL PASS' if echecs == 0 else 'ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path, default=None)
    p.add_argument("--departs", type=int, default=DEPARTS)
    p.add_argument("--pas-max", type=int, default=PAS_MAX)
    p.add_argument("--cap", type=float, default=CAP)
    p.add_argument("--verifier", action="store_true")
    # ⚠ Rejuger sans remarcher : les marches sont dans le JSON, et un verdict qui change de regle
    # ne doit pas couter une heure de marche — c'est le `--reagreger` de `138` sous un autre nom.
    p.add_argument("--rejuger", type=Path, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if a.rejuger is not None:
        r = _rejuger(json.loads(a.rejuger.read_text()))
        afficher(r)
        a.rejuger.write_text(json.dumps(r, ensure_ascii=False, indent=2))
        print(f"\n→ {a.rejuger}")
        return 0
    r = mesurer(cap=a.cap, departs=a.departs, pas_max=a.pas_max)
    afficher(r)
    if "message" in r:
        return 1
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=2))
        print(f"\n→ {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
