#!/usr/bin/env python3
"""La fenêtre du marcheur est GLOBALE, l'espacement des feuilles est LOCAL.

⚠⚠⚠ POURQUOI CE FICHIER, ET IL CORRIGE UNE SUPPOSITION DE `117`. `117` a mesuré que 63 pas voyants
sur 382 sont refusés parce que l'optimum de longueur tombe au bord de la fenêtre [0,5 ; 2,0] × 173,0
µm, 43 au bout court et 20 au bout long. Il a **supposé** — sans le mesurer — que les deux bouts ne
voulaient pas dire la même chose : au bout long un saut de feuille, au bout court un pas qui ne
traverse rien. **Les deux suppositions étaient fausses, et dans les deux sens.**

⭐⭐⭐⭐ **LES DEUX BOUTS SONT DE VRAIS PAS.** Le registre garde, à chaque pas, la fraction de
feuille réellement franchie. L'espacement local qu'elle implique vaut **80,7 µm** au bout court et
**380,2 µm** au bout long — c'est-à-dire de part et d'autre de la fenêtre, exactement comme une
butée le prédit. Le marcheur ne demandait pas l'absurde : il demandait un pas que sa fenêtre ne sait
pas exprimer.

⭐⭐⭐ **ET LA VARIATION N'EST PAS RADIALE**, donc un pas fonction du rayon ne la rattraperait pas.
Les deux bouts se rencontrent à tous les rayons, et l'espacement déduit ne suit pas le rayon. Ce
qu'il faut est une fenêtre centrée sur l'espacement **mesuré localement**, pas sur une constante
globale.

⚠⚠ **LE CONTRÔLE QUI REND TOUT ÇA LISIBLE.** L'espacement déduit vaut `pas / fraction franchie`, et
la fraction a **sa propre fenêtre** [0,35 ; 3,2] avec sa propre butée — un rapport de deux butées ne
veut rien dire. Les pas dont la fraction est elle-même en butée sont donc écartés, et, sur les pas
LIBRES, le déduit doit s'accorder au choisi : l'optimiseur y a justement cherché une feuille. Il
s'accorde à **1,015** de rapport médian, rho **+0,7515**.

⚠ Ce que ce fichier ne tranche pas : si élargir la fenêtre récupère ces 63 pas. Il faut refaire la
course, donc des lectures distantes (`R4-P24`).

  uv run python src/nappe/la_fenetre_est_globale_lespacement_est_local.py --verifier
  uv run python src/nappe/la_fenetre_est_globale_lespacement_est_local.py \
      --json docs/mesures/la_fenetre_est_globale_lespacement_est_local.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from scipy import stats

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
COURSE = RACINE / "docs" / "mesures" / "jusquou_va_t_il_si_on_le_laisse.json"

from ce_qui_porte_le_taux import est_aveugle  # noqa: E402

ESPACEMENT_PUBLIE = (101.0, 177.0, 303.0)
"""Les p5, p50 et p90 de l'espacement entre parties non adjacentes, mesurés par `R2-F07` sur
4 000 cellules.

⚠ Ce sont des **points de comparaison**, pas une mesure de ce fichier, et ils sont passés en
paramètre pour que ça se voie. Les recalculer ici en ferait une seconde mesure du même
espacement, libre de ne plus correspondre à celle qui est publiée."""


def espacement_deduit(etape: dict) -> float | None:
    """L'espacement de feuille que ce pas implique — ou `None` s'il n'est pas déductible.

    ⚠⚠ La fraction franchie a **sa propre fenêtre** et sa propre butée (`fraction_en_butee`).
    Diviser une longueur en butée par une fraction en butée rend un rapport de deux bornes, qui
    n'est une mesure de rien. Ces pas-là sont écartés plutôt qu'inclus avec une réserve : une
    réserve dans un texte ne retire pas le nombre de la médiane.
    """
    f = etape.get("feuilles_franchies")
    if not f or etape.get("fraction_en_butee"):
        return None
    return float(etape["pas_um"]) / float(f)


def pas_voyants(course: dict) -> list[tuple[float, dict]]:
    """Les pas voyants, avec le rayon de leur marche."""
    out = []
    for ligne in course.get("lignes", []):
        for cel in ligne.get("detail", []):
            for e in cel.get("etapes", []):
                if "confirme" in e and not est_aveugle(e):
                    out.append((float(ligne.get("rayon_mm", 0.0)), e))
    return out


def bornes_de_la_fenetre(course: dict) -> tuple[float, float]:
    """Les deux bouts de la fenêtre, LUS dans les pas en butée.

    ⚠ Jamais calculés depuis le pas nominal : ce fichier deviendrait une seconde définition de la
    fenêtre du marcheur, libre de ne plus lui correspondre le jour où elle change.
    """
    longueurs = [float(e["pas_um"]) for _, e in pas_voyants(course) if e.get("en_butee")]
    if not longueurs:
        raise ValueError("aucun pas voyant en butée : la fenêtre n'est pas lisible")
    return min(longueurs), max(longueurs)


def le_deduit_saccorde_t_il_au_choisi(course: dict) -> dict:
    """Sur les pas LIBRES, l'espacement déduit égale-t-il la longueur choisie ?

    ⭐⭐⭐⭐ C'EST LE CONTRÔLE SANS LEQUEL LES DEUX BOUTS NE PROUVENT RIEN. Là où la fenêtre ne
    borne pas, l'optimiseur a cherché une feuille : le pas qu'il a retenu EST une estimation de
    l'espacement. Si le déduit s'y accorde, la fraction franchie est calibrée et le déduit reste
    lisible aux bouts ; s'il ne s'y accorde pas, tout ce fichier mesure un biais.

    ⚠ Le rapport est **apparié**, pas comparé entre médianes : deux médianes de deux distributions
    ne disent rien de l'accord pas à pas, et ma première lecture s'y est trompée — 181,7 contre
    150,0 se lisait comme 21 % de biais, alors que le rapport apparié vaut 1,015.
    """
    libres = [(e, espacement_deduit(e)) for _, e in pas_voyants(course)
              if not e.get("en_butee")]
    couples = [(float(e["pas_um"]), d) for e, d in libres if d]
    if len(couples) < 20:
        return {"decidable": False, "pourquoi": f"{len(couples)} pas libres déductibles"}
    choisis = [a for a, _ in couples]
    deduits = [b for _, b in couples]
    rapports = sorted(a / b for a, b in couples)
    # ⚠⚠ Une entrée CONSTANTE rend un rho indéfini, et `abs(nan) > 0.4` vaut False : sans ce
    # refus, « pas de lien » serait rendu par une série qui n'a aucun lien À TROUVER. C'est la
    # forme exacte d'une vérification qui ne peut pas échouer.
    if len(set(choisis)) < 3 or len(set(deduits)) < 3:
        return {"decidable": False, "pourquoi": "le pas choisi ou le déduit est constant"}
    r, p = stats.spearmanr(choisis, deduits)
    return {"decidable": True, "pas_libres_deductibles": len(couples),
            "rapport_median": round(float(np.median(rapports)), 3),
            "rapport_q1": round(float(np.quantile(rapports, 0.25)), 3),
            "rapport_q3": round(float(np.quantile(rapports, 0.75)), 3),
            "rho": round(float(r), 4), "p": float(p),
            # ⚠ La bande d'acceptation est déclarée ICI, en amont du résultat : ±10 % sur la
            # médiane du rapport apparié. La choisir après avoir vu 1,015 serait la régler.
            "le_deduit_est_calibre": bool(abs(float(np.median(rapports)) - 1.0) <= 0.10)}


def ce_que_la_fenetre_exclut(course: dict) -> dict:
    """Quel espacement les pas en butée impliquent, à chaque bout.

    ⭐⭐⭐⭐ Si le bout court implique un espacement PLUS PETIT que lui et le bout long un
    espacement PLUS GRAND, alors la fenêtre exclut de vrais pas aux deux bouts — et la butée
    veut dire ce que son fichier dit qu'elle veut dire.

    ⚠ La comparaison se fait sur les **quartiles** et pas seulement la médiane : une médiane hors
    fenêtre avec un quartile dedans dirait « parfois », et la différence compte pour qui décide
    d'élargir.
    """
    bas, haut = bornes_de_la_fenetre(course)
    out: dict = {"decidable": True, "bout_court_um": round(bas, 1), "bout_long_um": round(haut, 1)}
    for nom, garde in (("court", lambda e: e["pas_um"] <= bas + 1e-9),
                       ("long", lambda e: e["pas_um"] >= haut - 1e-9)):
        ds = [d for _, e in pas_voyants(course)
              if e.get("en_butee") and garde(e) and (d := espacement_deduit(e))]
        if len(ds) < 5:
            out[f"bout_{nom}"] = {"decidable": False, "pourquoi": f"{len(ds)} pas déductibles"}
            continue
        out[f"bout_{nom}"] = {
            "decidable": True, "pas_deductibles": len(ds),
            "espacement_median_um": round(float(np.median(ds)), 1),
            "q1_um": round(float(np.quantile(ds, 0.25)), 1),
            "q3_um": round(float(np.quantile(ds, 0.75)), 1)}
    c, l = out.get("bout_court", {}), out.get("bout_long", {})
    out["la_fenetre_exclut_de_vrais_pas"] = bool(
        c.get("decidable") and l.get("decidable")
        and c["q3_um"] < bas and l["q1_um"] > haut)
    return out


def ou_tombent_ils_dans_la_distribution_publiee(
        course: dict, publie: tuple[float, float, float] = ESPACEMENT_PUBLIE) -> dict:
    """Les espacements exclus sont-ils dans les queues de ce que `R2-F07` a publié ?

    ⚠ La question compte parce qu'elle sépare deux diagnostics. Si les butées tombaient AU MILIEU
    de la distribution publiée, la fenêtre serait mal placée et le remède trivial. Elles tombent
    dans les queues : la fenêtre couvre le gros de l'espacement et rate ses extrêmes, ce qui est
    un remède différent — élargir coûte des candidats, ou bien il faut centrer localement.
    """
    p5, p50, p90 = publie
    ex = ce_que_la_fenetre_exclut(course)
    c, l = ex.get("bout_court", {}), ex.get("bout_long", {})
    if not (c.get("decidable") and l.get("decidable")):
        return {"decidable": False, "pourquoi": "un des deux bouts n'est pas déductible"}
    return {"decidable": True, "publie_p5_p50_p90": [p5, p50, p90],
            "court_median_um": c["espacement_median_um"],
            "long_median_um": l["espacement_median_um"],
            "court_sous_le_p5": bool(c["espacement_median_um"] < p5),
            "long_au_dessus_du_p90": bool(l["espacement_median_um"] > p90),
            "les_deux_sont_dans_les_queues": bool(
                c["espacement_median_um"] < p5 and l["espacement_median_um"] > p90)}


def la_variation_est_elle_radiale(course: dict) -> dict:
    """Un pas fonction du rayon rattraperait-il ces bouts ?

    ⭐⭐⭐ Si l'espacement suivait le rayon, un pas nominal fonction du rayon suffirait et le remède
    serait bon marché. S'il ne le suit pas, il faut une mesure LOCALE, cellule par cellule.

    ⚠⚠ L'unité du test décisif est la **MARCHE** et non le pas : les vingt pas d'une marche
    partagent son rayon et son départ, donc un test par pas prendrait 287 observations pour 28.
    Le niveau du pas est rendu comme description, et il le dit.
    """
    par_marche: dict[float, list[float]] = {}
    for r, e in pas_voyants(course):
        if not e.get("en_butee") and (d := espacement_deduit(e)):
            par_marche.setdefault(r, []).append(d)
    marches = [(r, float(np.median(v))) for r, v in sorted(par_marche.items()) if len(v) >= 3]
    if len(marches) < 6:
        return {"decidable": False, "pourquoi": f"{len(marches)} marches exploitables"}
    # ⚠⚠ Même refus qu'au contrôle : un espacement constant d'une marche à l'autre ne peut pas
    # « ne pas suivre le rayon », il n'a rien à suivre. Rendre `False` y serait une conclusion
    # tirée d'une absence de données.
    if len({round(b, 6) for _, b in marches}) < 3:
        return {"decidable": False, "pourquoi": "l'espacement médian est constant entre marches"}
    r_m, p_m = stats.spearmanr([a for a, _ in marches], [b for _, b in marches])
    courts = [r for r, e in pas_voyants(course)
              if e.get("en_butee") and e["pas_um"] < (bornes_de_la_fenetre(course)[0] + 1e-9)]
    longs = [r for r, e in pas_voyants(course)
             if e.get("en_butee") and e["pas_um"] > (bornes_de_la_fenetre(course)[1] - 1e-9)]
    mw = None
    if len(courts) >= 5 and len(longs) >= 5:
        _, mw = stats.mannwhitneyu(courts, longs, alternative="two-sided")
    return {"decidable": True, "marches": len(marches),
            "rho_espacement_rayon": round(float(r_m), 4), "p": float(p_m),
            "rayon_median_bout_court_mm": round(float(np.median(courts)), 2) if courts else None,
            "rayon_median_bout_long_mm": round(float(np.median(longs)), 2) if longs else None,
            "p_court_contre_long": round(float(mw), 4) if mw is not None else None,
            "la_variation_suit_le_rayon": bool(abs(r_m) > 0.4 and p_m < 0.05),
            "reserve": "n = 28 marches : un rho qui tombe cesse de rejeter l'absence d'effet, "
                       "il ne la prouve pas"}


def mesurer(course_p: Path = COURSE) -> dict:
    """Tout, depuis le JSON de `113` — aucune lecture distante."""
    course = json.loads(course_p.read_text(encoding="utf-8"))
    if course.get("course_incomplete"):
        raise ValueError(f"{course_p} : course incomplète")
    if not course.get("lignes"):
        raise ValueError(f"{course_p} ne porte aucune marche")
    controle = le_deduit_saccorde_t_il_au_choisi(course)
    # ⚠⚠ Un contrôle INDÉCIDABLE fait refuser tout autant qu'un contrôle rouge : sans lui, les
    # deux bouts seraient publiés sans que rien n'ait vérifié que le déduit veut dire quelque
    # chose. « On n'a pas pu vérifier » n'est pas « c'est bon ».
    if not controle.get("decidable"):
        raise ValueError(f"{course_p} : le contrôle du déduit est indécidable "
                         f"({controle.get('pourquoi')}) — les bouts ne seraient pas lisibles")
    if not controle["le_deduit_est_calibre"]:
        raise ValueError(
            f"{course_p} : l'espacement déduit ne s'accorde pas au pas choisi sur les pas libres "
            f"(rapport médian {controle['rapport_median']}) — les bouts ne seraient pas lisibles")
    return {"source": course_p.name,
            "le_deduit_saccorde_t_il_au_choisi": controle,
            "ce_que_la_fenetre_exclut": ce_que_la_fenetre_exclut(course),
            "ou_tombent_ils_dans_la_distribution_publiee":
                ou_tombent_ils_dans_la_distribution_publiee(course),
            "la_variation_est_elle_radiale": la_variation_est_elle_radiale(course)}


def afficher(r: dict) -> None:
    print(f"source {r['source']}")
    c = r["le_deduit_saccorde_t_il_au_choisi"]
    if c.get("decidable"):
        print(f"\n  contrôle sur {c['pas_libres_deductibles']} pas libres : rapport médian "
              f"{c['rapport_median']} [{c['rapport_q1']} ; {c['rapport_q3']}], "
              f"rho {c['rho']:+.4f}")
        print(f"  ⭐ l'espacement déduit est calibré : {c['le_deduit_est_calibre']}")
    e = r["ce_que_la_fenetre_exclut"]
    if e.get("decidable"):
        for nom in ("court", "long"):
            b = e.get(f"bout_{nom}", {})
            if b.get("decidable"):
                print(f"  bout {nom:<5} ({e[f'bout_{nom}_um']:>5.1f} µm) : espacement déduit "
                      f"{b['espacement_median_um']:>6.1f} µm "
                      f"[{b['q1_um']:.1f} ; {b['q3_um']:.1f}] sur {b['pas_deductibles']} pas")
        print(f"  ⭐ la fenêtre exclut de vrais pas : {e['la_fenetre_exclut_de_vrais_pas']}")
    q = r["ou_tombent_ils_dans_la_distribution_publiee"]
    if q.get("decidable"):
        p5, p50, p90 = q["publie_p5_p50_p90"]
        print(f"\n  contre l'espacement publié (p5 {p5:.0f} · p50 {p50:.0f} · p90 {p90:.0f} µm) : "
              f"les deux sont dans les queues = {q['les_deux_sont_dans_les_queues']}")
    v = r["la_variation_est_elle_radiale"]
    if v.get("decidable"):
        print(f"\n  espacement contre rayon, {v['marches']} marches : rho "
              f"{v['rho_espacement_rayon']:+.4f} (p {v['p']:.4f})")
        print(f"  rayon médian du bout court {v['rayon_median_bout_court_mm']} mm contre "
              f"{v['rayon_median_bout_long_mm']} mm au bout long (p {v['p_court_contre_long']})")
        print(f"  ⭐ la variation suit le rayon : {v['la_variation_suit_le_rayon']}")


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

    def etape(pas_um, feuilles, butee=False, frac_butee=False, aveugle=False):
        return {"pas": 1, "confirme": not butee, "pas_um": pas_um,
                "feuilles_franchies": feuilles, "fraction_en_butee": frac_butee,
                "en_butee": butee,
                "desaccord_des_moities_deg": 0.0 if aveugle else 11.0,
                "planarite": 0.0 if aveugle else 0.4}

    def course(marches):
        return {"lignes": [{"rayon_mm": r, "detail": [{"etapes": es}]}
                           for r, es in marches]}

    # ⭐⭐⭐⭐ Une course où la fenêtre est [80 ; 320] et l'espacement vrai déborde aux deux bouts.
    libres = [etape(150.0 + 3 * k, 1.0) for k in range(12)]
    courts = [etape(80.0, 80.0 / 62.0, butee=True) for _ in range(8)]
    longs = [etape(320.0, 320.0 / 410.0, butee=True) for _ in range(8)]
    c = course([(4.0 + i, libres + courts + longs) for i in range(4)])

    ctrl = le_deduit_saccorde_t_il_au_choisi(c)
    v("le contrôle tourne sur les pas libres", ctrl["decidable"])
    v("... et le rapport apparié vaut un", ctrl["rapport_median"] == 1.0,
      f"{ctrl['rapport_median']}")
    v("... donc le déduit est déclaré calibré", ctrl["le_deduit_est_calibre"])
    v("les bornes sont lues dans les pas", bornes_de_la_fenetre(c) == (80.0, 320.0),
      f"{bornes_de_la_fenetre(c)}")

    ex = ce_que_la_fenetre_exclut(c)
    v("le bout court implique un espacement plus PETIT que lui",
      ex["bout_court"]["espacement_median_um"] == 62.0,
      f"{ex['bout_court']['espacement_median_um']}")
    v("le bout long en implique un plus GRAND",
      ex["bout_long"]["espacement_median_um"] == 410.0,
      f"{ex['bout_long']['espacement_median_um']}")
    v("... donc la fenêtre exclut de vrais pas", ex["la_fenetre_exclut_de_vrais_pas"])

    # ⚠⚠ LA SONDE SYMÉTRIQUE : une fenêtre qui contient l'espacement ne doit PAS être accusée.
    # Sans elle, un test qui répondrait toujours « oui » passerait le contrôle du dessus.
    dedans = course([(4.0 + i, libres
                      + [etape(80.0, 80.0 / 120.0, butee=True) for _ in range(8)]
                      + [etape(320.0, 320.0 / 200.0, butee=True) for _ in range(8)])
                     for i in range(4)])
    v("sonde : une fenêtre qui contient l'espacement n'est pas accusée",
      not ce_que_la_fenetre_exclut(dedans)["la_fenetre_exclut_de_vrais_pas"])

    # ⚠⚠ LA SONDE DU CONTRÔLE : un déduit biaisé doit être VU, et faire refuser la mesure.
    biais = course([(4.0 + i, [etape(150.0 + 3 * k, 0.5) for k in range(12)]
                     + courts + longs) for i in range(4)])
    v("sonde : un déduit biaisé n'est pas déclaré calibré",
      not le_deduit_saccorde_t_il_au_choisi(biais)["le_deduit_est_calibre"],
      f"{le_deduit_saccorde_t_il_au_choisi(biais)['rapport_median']}")

    # ⚠⚠ LA SONDE DE LA FRACTION EN BUTÉE : un rapport de deux bornes doit être ÉCARTÉ.
    v("un pas dont la fraction est en butée n'est pas déductible",
      espacement_deduit(etape(80.0, 3.2, butee=True, frac_butee=True)) is None)
    v("... et un pas sans fraction non plus",
      espacement_deduit({"pas_um": 80.0, "feuilles_franchies": None}) is None)
    avec = course([(4.0 + i, libres
                    + [etape(80.0, 3.2, butee=True, frac_butee=True) for _ in range(8)]
                    + courts + longs) for i in range(4)])
    v("sonde : les fractions en butée sont hors du compte",
      ce_que_la_fenetre_exclut(avec)["bout_court"]["pas_deductibles"] == 32,
      f"{ce_que_la_fenetre_exclut(avec)['bout_court']['pas_deductibles']}")

    q = ou_tombent_ils_dans_la_distribution_publiee(c, (101.0, 177.0, 303.0))
    v("les deux bouts tombent dans les queues du publié", q["les_deux_sont_dans_les_queues"])
    v("sonde : un bout au milieu du publié n'est pas une queue",
      not ou_tombent_ils_dans_la_distribution_publiee(dedans, (101.0, 177.0, 303.0))[
          "les_deux_sont_dans_les_queues"])

    # ⭐⭐⭐ LA RADIALITÉ, et ses deux sondes.
    # ⚠⚠ Un espacement CONSTANT est refusé et non lu comme « ne suit pas le rayon » : `abs(nan)
    # > 0.4` vaut False, donc sans ce refus le test répondrait « pas de lien » à une série qui
    # n'a aucun lien à trouver.
    constant = la_variation_est_elle_radiale(course(
        [(4.0 + 2 * i, [etape(150.0, 1.0) for _ in range(6)]) for i in range(10)]))
    v("sonde : un espacement constant est REFUSÉ, pas lu comme « pas de lien »",
      not constant["decidable"], f"{constant}")
    plat = la_variation_est_elle_radiale(course(
        [(4.0 + 2 * i, [etape(150.0 + (i % 3) * 7, 1.0) for _ in range(6)]) for i in range(10)]))
    v("un espacement qui varie sans suivre le rayon ne suit pas le rayon",
      plat["decidable"] and not plat["la_variation_suit_le_rayon"],
      f"rho {plat.get('rho_espacement_rayon')}")
    montant = la_variation_est_elle_radiale(course(
        [(4.0 + 2 * i, [etape(100.0 + 20 * i, 1.0) for _ in range(6)]) for i in range(10)]))
    v("sonde : un espacement qui monte avec le rayon est VU",
      montant["la_variation_suit_le_rayon"],
      f"rho {montant['rho_espacement_rayon']}")
    v("moins de six marches rend indécidable",
      not la_variation_est_elle_radiale(course(
          [(4.0 + i, [etape(150.0, 1.0) for _ in range(6)]) for i in range(3)]))["decidable"])

    # ⚠ Les refus d'entrée.
    with tempfile.TemporaryDirectory() as dd:
        p = Path(dd) / "c.json"
        p.write_text(json.dumps({"course_incomplete": True, "lignes": []}), encoding="utf-8")
        try:
            mesurer(p)
            v("une course incomplète est refusée", False)
        except ValueError:
            v("une course incomplète est refusée", True)
        p.write_text(json.dumps(biais), encoding="utf-8")
        try:
            mesurer(p)
            v("une course au déduit biaisé est refusée", False)
        except ValueError:
            v("une course au déduit biaisé est refusée", True)
        p.write_text(json.dumps(c), encoding="utf-8")
        r = mesurer(p)
        v("une course valide est mesurée",
          r["ce_que_la_fenetre_exclut"]["la_fenetre_exclut_de_vrais_pas"])
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
