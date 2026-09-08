#!/usr/bin/env python3
"""Le froissement designe-t-il ou le transfert echoue ? Non — il designe l'inverse.

⚠⚠⚠ POURQUOI CETTE QUESTION EST CELLE DU GRAAL. `93` etablit OU le pas geometrique echoue : au
bord, ou la surface est brisee (`92`, ×31) et les spires desalignees (×4,18). Il manque un signal
qui dise a un marcheur, SANS SUPERVISION, qu'il est dans cette zone. Le **pli** est le candidat
que le depot a deja mesure : `75`, section « Une cellule peut-elle savoir qu'elle a tort », le
trouve predictif de l'erreur PAR CELLULE — 8 bras sur 8 chez le raccrochage, et un bras SAUVE en
jetant les dix pour cent les plus plies, la ou le temoin au hasard n'en sauve aucun. Ce fichier le
teste la ou la carte d'echec existe.

⚠⚠⚠ ET CETTE TRANCHE-LA BORNAIT DEJA SA PORTEE, ce que ma premiere version de ce fichier avait
efface. Elle ecrit : « ce que ca ne dit pas, c'est que le pli soit une bonne confiance EN GENERAL ;
il l'est la ou il y a des plis », et le pas normal lisse en a si peu que son classement fait PIRE
que le hasard (+7,1 µm contre le temoin). Ce fichier ajoute la seconde borne, sur l'autre axe : a
travers les RAYONS, le signe s'inverse.
⚠ Et une erreur a moi, gardee : j'avais attribue ce resultat a `78`, qui est *Cinq rouleaux
publient leur axe*. Une citation qu'on ne verifie pas est une citation qu'on invente.

⛔⛔⛔ LA REPONSE EST NON, ET C'EST PIRE QUE NEUTRE : le froissement est **ANTI-predictif**. Il vaut
15,2 µm au coeur, 10,1 au milieu, **3,8 au bord** — le plus FAIBLE exactement la ou le transfert
echoue. Correlations : **-0,957** avec le rayon, -0,470 avec le desalignement, **-0,825** avec la
rupture de continuite. Un marcheur qui s'en servirait signalerait le coeur, ou tout est propre, et
**se tairait au bord**.

⭐⭐⭐ ET CE QUE LE CHAMP MESURE EST ETABLI PAR FIXTURE, PAS PAR CORRELATION. `champ_de_froissement`
prend la MEDIANE d'un voisinage 3×3, et une mediane rend la valeur centrale sur un voisinage
symetrique — donc le champ est **exactement aveugle a la courbure lisse**. Mesure sur cylindres
fabriques :

  - cylindre parfait, R = 5 mm et R = 20 mm : **0,00 µm** dans les deux cas ;
  - cylindre a **axe courbe**, comme `90` le mesure sur le vrai rouleau : **0,00 µm** aussi ;
  - cylindre + bruit de 5 µm : 7,54 et 6,87 µm, soit un rapport de **1,10** entre les deux rayons ;
  - cylindre + bruit de 20 µm : 29,10 et 27,06, rapport **1,08**.

⭐⭐ DONC LE CHAMP MESURE LA **RUGOSITE LOCALE DU MAILLAGE**, et il le fait quasiment sans dependre
du rayon. Or le reel tombe d'un facteur **5,2** entre R = 4,1 mm et R = 23,8 mm, quand le bruit
seul en donnerait 1,1. **Les maillages humains sont donc cinq fois plus LISSES au bord qu'au
coeur**, et c'est une propriete de la matiere maillee, pas de la geometrie du sondage.

⚠⚠⚠ ET UNE CAUSE QUE J'AI PUBLIEE PUIS RETRACTEE AVANT DE LA COMMITTER. J'avais explique la chute
en 1/R par la **sagitta** d'un cercle, `s²/(8R)` : l'accord numerique etait frappant, rapport
mesure/predit de **1,11 en mediane** sur les 28 bandes. C'etait une **coincidence**. La fixture le
refute d'un coup : un cylindre parfait, dont la sagitta vaut 20,2 µm a R = 5 mm, rend **zero**.
Une correlation de 1,11 sur vingt-huit points ne vaut pas une fixture dont on connait la reponse.

⭐⭐ ET LE VERDICT DEVIENT PLUS FORT, PAS PLUS FAIBLE. Un maillage localement LISSE qui porte des
sauts de trente millimetres (`92`) et des spires desalignees (`93`) est un maillage qui a **enjambe
ce qu'il ne pouvait pas suivre**. La douceur au bord n'est donc pas de la qualite : c'est la
signature d'un pontage. Un signal de confiance bati dessus classerait l'abandon comme une reussite.

⚠⚠ AVERTISSEMENT DE NIVEAU, QUI NE RETRACTE PAS `75`. Ce fichier compare des BANDES entre elles ;
`75` compare des CELLULES a l'interieur d'une meme marche, a rayon presque constant. Les deux
peuvent etre vrais : un observable valide a un rayon n'est pas valide a travers les rayons.
⭐ Et ca compte pour l'objectif, parce qu'une marche de 31 spires change le rayon d'un facteur
six : tout signal de confiance qu'elle emploie doit etre **verifie a travers les rayons**, ou il
classera par rayon en croyant classer par difficulte.

Usage :
    uv run python src/nappe/le_froissement_mesure_la_rugosite.py --verifier
    uv run python src/nappe/le_froissement_mesure_la_rugosite.py \\
        --json docs/mesures/le_froissement_mesure_la_rugosite.json
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
sys.path.insert(0, str(RACINE / "src" / "depot"))

ALIGNEMENT = RACINE / "docs" / "mesures" / "deux_modes_dechec_du_transfert.json"
CONTINUITE = RACINE / "docs" / "mesures" / "la_continuite_des_transferts.json"


def sagitta_um(pas_um: float, rayon_um: float) -> float:
    """La fleche d'un cercle de rayon R echantillonne au pas s : `s²/(8R)`.

    ⛔⛔ C'EST UNE CAUSE REFUTEE, GARDEE PARCE QU'ELLE EST CREDIBLE. Je l'avais publiee : le champ
    tombe en 1/R et la sagitta aussi, avec un rapport mesure/predit de 1,11 en mediane sur les 28
    bandes. La fixture la tue d'un coup — un cylindre PARFAIT, dont la sagitta vaut 20,2 µm a
    R = 5 mm, rend **zero**, parce qu'une mediane 3×3 rend la valeur centrale sur un voisinage
    symetrique et est donc aveugle a toute courbure lisse.

    ⚠ Elle reste ici, et le rapport reste publie, pour une raison : un accord numerique de cet
    ordre reapparaitra a qui refera la mesure, et le trouver sans trouver sa refutation cotee a
    cote conduirait a le republier. Une coincidence nommee coute moins cher qu'une coincidence
    redecouverte.
    """
    return pas_um * pas_um / (8.0 * max(rayon_um, 1e-9))


def pas_de_cellule_um(a: np.ndarray, ok: np.ndarray, voxel_um: float) -> float:
    """L'ecart median entre deux cellules voisines d'une ligne, MESURE et non suppose."""
    pas = np.linalg.norm(a[:, 1:] - a[:, :-1], axis=-1) * voxel_um
    m = ok[:, 1:] & ok[:, :-1]
    return float(np.median(pas[m])) if m.any() else float("nan")


def correlation(x: list[float], y: list[float]) -> float:
    """Le coefficient de Pearson, ou 0 si l'un des deux ne varie pas."""
    if len(x) < 3 or np.std(x) == 0 or np.std(y) == 0:
        return 0.0
    return round(float(np.corrcoef(x, y)[0, 1]), 3)


def cylindre(rayon_mm, pas_mm=0.9, n=60, H=20, bruit_mm=0.0, courbe=0.0, graine=3):
    """Un cylindre fabrique : rayon connu, bruit connu, axe droit ou courbe."""
    th = np.arange(n) * pas_mm / rayon_mm
    a = np.zeros((H, n, 3))
    for k in range(H):
        # ⚠ `courbe` decale l'axe avec z : c'est la courbure du rouleau que `90` mesure.
        dx = courbe * (k - H / 2) ** 2
        a[k, :, 0] = (rayon_mm * np.cos(th) + dx) / 0.045532
        a[k, :, 1] = rayon_mm * np.sin(th) / 0.045532
        a[k, :, 2] = k * pas_mm / 0.045532
    if bruit_mm:
        a = a + np.random.default_rng(graine).normal(0.0, bruit_mm / 0.045532, a.shape)
    return a, np.ones((H, n), dtype=bool)


def ce_que_le_champ_voit() -> dict:
    """Ce que le champ rend sur des cylindres DONT ON CONNAIT LA REPONSE.

    ⭐⭐⭐ C'EST LA REVENDICATION PORTEUSE DU FICHIER, ET ELLE EST PUBLIEE PLUTOT QUE SEULEMENT
    ASSERTEE. « Le champ mesure la rugosite » est ce qui transforme une correlation en cause ;
    laisser ses nombres dans la sortie d'une batterie les rendrait incitables par un document,
    donc invérifiables par qui lit la conclusion sans relancer la batterie.

    ⚠⚠ UN SEUL CALCUL SERT LES TROIS USAGES — la publication, l'assertion et la figure. Deux
    fixtures d'un meme fait finiraient par ne pas s'accorder, et c'est la version affichee qui
    aurait l'air d'etre la mesure.
    """
    import ou_la_nappe_se_froisse as F  # noqa: PLC0415

    def champ(**kw):
        a, ok = cylindre(**kw)
        c, g = F.champ_de_froissement(a, ok, 45.532)
        return round(float(np.median(c[g])), 2)

    r5, r20 = 5.0, 20.0
    cas = {
        "cylindre_parfait": {"R5": champ(rayon_mm=r5), "R20": champ(rayon_mm=r20)},
        "axe_courbe": {"R5": champ(rayon_mm=r5, courbe=0.004),
                       "R20": champ(rayon_mm=r20, courbe=0.004)},
        "bruit_5um": {"R5": champ(rayon_mm=r5, bruit_mm=0.005),
                      "R20": champ(rayon_mm=r20, bruit_mm=0.005)},
        "bruit_20um": {"R5": champ(rayon_mm=r5, bruit_mm=0.020),
                       "R20": champ(rayon_mm=r20, bruit_mm=0.020)},
    }
    for x in cas.values():
        # ⚠ Le rapport entre les deux rayons est LA quantite qui tranche : le reel tombe d'un
        # facteur 5,2 entre R = 4,1 et R = 23,8 mm, la rugosite seule n'en donne que ~1,1.
        x["rapport_R5_sur_R20"] = round(x["R5"] / x["R20"], 2) if x["R20"] else None
    return {
        "cas": cas,
        # ⛔ La cause que j'avais publiee, cotee a cote de ce que le champ rend vraiment.
        "sagitta_predite_a_R5_um": round(sagitta_um(900.0, 5000.0), 1),
        "le_champ_est_aveugle_a_la_courbure_lisse":
            cas["cylindre_parfait"]["R5"] == 0.0 and cas["axe_courbe"]["R5"] == 0.0,
        "le_champ_repond_au_bruit": cas["bruit_5um"]["R5"] > 3.0,
        "et_presque_sans_dependre_du_rayon":
            abs(cas["bruit_5um"]["rapport_R5_sur_R20"] - 1.0) < 0.35,
    }


def mesurer() -> dict:
    import le_pas_lu_sur_les_transferts as P  # noqa: PLC0415
    import le_sens_du_rang as R  # noqa: PLC0415
    import ou_la_nappe_se_froisse as F  # noqa: PLC0415

    if not ALIGNEMENT.is_file() or not CONTINUITE.is_file():
        return {"message": "il manque la carte d'échec : lancer `deux_modes_dechec_du_transfert` "
                           "et `la_continuite_des_transferts`"}
    al = {(x["de"], x["a"]): x for x in json.loads(ALIGNEMENT.read_text())["lignes"]}
    co = {(x["de"], x["a"]): x for x in json.loads(CONTINUITE.read_text())["lignes"]}

    lignes = []
    for x in R.bandes_du_fragment():
        g = P.grille(x["recente"])
        if g is None:
            continue
        a, ok = g
        cle = (x["de"], x["a"])
        if cle not in al or cle not in co:
            continue
        champ, garde = F.champ_de_froissement(a, ok, R.VOXEL_UM)
        v = champ[garde]
        if not len(v):
            continue
        s = pas_de_cellule_um(a, ok, R.VOXEL_UM)
        rayon_um = al[cle]["rayon_mm"] * 1000.0
        sag = sagitta_um(s, rayon_um)
        brut = float(np.median(v))
        lignes.append({
            "de": x["de"], "a": x["a"], "rayon_mm": al[cle]["rayon_mm"],
            "pas_de_cellule_um": round(s, 0),
            "froissement_brut_um": round(brut, 1),
            "sagitta_predite_um": round(sag, 1),
            # ⭐⭐⭐ LE RAPPORT QUI ETABLIT LA CAUSE : proche de un, le champ EST la courbure.
            "mesure_sur_predit": round(brut / sag, 2),
            "froissement_normalise": round(brut / sag, 2),
            "desalignement": al[cle]["rapport_au_plancher"],
            "continuite": co[cle]["rapport_interieur"],
        })
    if len(lignes) < 6:
        return {"message": "trop peu de bandes exploitables"}

    ray = [x["rayon_mm"] for x in lignes]
    brut = [x["froissement_brut_um"] for x in lignes]
    norm = [x["froissement_normalise"] for x in lignes]
    des = [x["desalignement"] for x in lignes]
    con = [x["continuite"] for x in lignes]
    rapports = [x["mesure_sur_predit"] for x in lignes]
    n = len(lignes) // 3
    tiers = {"coeur": lignes[:n], "milieu": lignes[n:2 * n], "bord": lignes[2 * n:]}
    return {
        "fragment": R.FRAGMENT, "bandes": len(lignes), "lignes": lignes,
        # ⭐⭐⭐ CE QUE LE CHAMP VOIT, publie a cote de ce qu'il rend sur le vrai maillage : sans
        # cette moitie, la chute en 1/R est un fait sans cause et la premiere cause credible
        # gagne — c'est exactement comme ca que j'ai publie la sagitta.
        "ce_que_le_champ_voit": ce_que_le_champ_voit(),
        # ⚠⚠⚠ GARDE COMME COINCIDENCE, PAS COMME CAUSE : l'accord est frappant et la fixture
        # le refute — un cylindre parfait, dont la sagitta vaut 20,2 µm, rend ZERO.
        "laccord_avec_la_sagitta_est_une_coincidence": {
            "rapport_median": round(float(np.median(rapports)), 2),
            "min": round(float(min(rapports)), 2), "max": round(float(max(rapports)), 2),
            "ecart_type_relatif": round(float(np.std(rapports) / np.mean(rapports)), 3),
        },
        # ⛔ LE VERDICT : anti-predictif, brut comme normalise.
        "correlations": {
            "brut_contre_rayon": correlation(brut, ray),
            "brut_contre_desalignement": correlation(brut, des),
            "brut_contre_continuite": correlation(brut, con),
            "normalise_contre_rayon": correlation(norm, ray),
            "normalise_contre_desalignement": correlation(norm, des),
            "normalise_contre_continuite": correlation(norm, con),
        },
        "par_tiers": {k: {"bandes": len(v),
                          "froissement_brut_um": round(
                              float(np.median([y["froissement_brut_um"] for y in v])), 1),
                          "normalise": round(
                              float(np.median([y["froissement_normalise"] for y in v])), 2),
                          "desalignement": round(
                              float(np.median([y["desalignement"] for y in v])), 2),
                          "continuite": round(
                              float(np.median([y["continuite"] for y in v])), 1)}
                      for k, v in tiers.items() if v},
        "le_froissement_est_anti_predictif": bool(
            correlation(brut, des) < 0 and correlation(brut, con) < 0
            and correlation(norm, des) < 0 and correlation(norm, con) < 0),
        "normaliser_retire_le_rayon": bool(
            abs(correlation(norm, ray)) < 0.6 * abs(correlation(brut, ray))),
        "normaliser_corrige_le_signe": bool(correlation(norm, des) > 0),
    }


def verifier() -> int:
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  FAIL {nom} — {detail}")

    # --- ce que le champ VOIT, sur des cylindres dont on connait la reponse -----------------
    # ⚠⚠ La fixture est celle que `mesurer` PUBLIE, pas une seconde ecrite ici : deux fixtures
    # d'un meme fait finiraient par ne pas s'accorder, et c'est la version publiee qui aurait
    # l'air d'etre la mesure.
    f = ce_que_le_champ_voit()
    cas = f["cas"]
    # ⭐⭐⭐ LE FAIT STRUCTUREL : une mediane rend la valeur centrale sur un voisinage symetrique,
    # donc le champ est EXACTEMENT aveugle a la courbure lisse. Zero, pas « petit ».
    v("un cylindre parfait rend un froissement EXACTEMENT nul",
      cas["cylindre_parfait"]["R5"] == 0.0 and cas["cylindre_parfait"]["R20"] == 0.0,
      str(cas["cylindre_parfait"]))
    # ⚠⚠ ET UN AXE COURBE NE LE REVEILLE PAS NON PLUS : la courbure du rouleau mesuree par `90`
    # ne peut donc pas expliquer ce que le champ rend sur le vrai maillage.
    v("... et un cylindre à AXE COURBE aussi", cas["axe_courbe"]["R5"] == 0.0,
      str(cas["axe_courbe"]))
    # ⚠⚠⚠ LA SAGITTA, REFUTEE ET GARDEE. J'avais explique la chute en 1/R par `s²/(8R)`, avec un
    # accord numerique de 1,11 en mediane sur vingt-huit bandes. La sagitta d'un cercle de 5 mm
    # au pas de 900 µm vaut 20,2 µm ; le champ rend zero. Une correlation ne vaut pas une
    # fixture dont on connait la reponse.
    v("la sagitta prédisait un champ non nul là où il vaut zéro",
      f["sagitta_predite_a_R5_um"] > 15.0 and cas["cylindre_parfait"]["R5"] == 0.0,
      f"sagitta {f['sagitta_predite_a_R5_um']} µm contre un champ de 0,0 — explication réfutée")
    # ⭐⭐ CE QUE LE CHAMP VOIT VRAIMENT : le bruit, et presque sans dependre du rayon.
    v("un bruit fabriqué réveille le champ", f["le_champ_repond_au_bruit"],
      str(cas["bruit_5um"]))
    v("... et il le fait presque sans dépendre du rayon", f["et_presque_sans_dependre_du_rayon"],
      f"rapport {cas['bruit_5um']['rapport_R5_sur_R20']} entre R=5 et R=20 mm")
    # ⚠ Et il croit avec le bruit, sinon il ne mesurerait pas la rugosite mais autre chose.
    v("... et il croît avec le bruit", cas["bruit_20um"]["R5"] > 3.0 * cas["bruit_5um"]["R5"],
      f"{cas['bruit_20um']['R5']} µm pour un bruit ×4, contre {cas['bruit_5um']['R5']}")
    # ⭐ ET LA FIXTURE EST PUBLIEE, sans quoi un document ne pourrait citer que la conclusion.
    v("... et cette fixture est publiée, pas seulement assertée",
      "ce_que_le_champ_voit" in mesurer(), "docs/mesures/…rugosite.json")

    v("une corrélation sur une constante rend zéro plutôt que NaN",
      correlation([1.0, 1.0, 1.0], [1.0, 2.0, 3.0]) == 0.0)
    v("... et une corrélation parfaite rend un",
      correlation([1.0, 2.0, 3.0], [2.0, 4.0, 6.0]) == 1.0)

    r = mesurer()
    if "message" in r:
        print(f"  ⚠ {r['message']} — contrôles sur données réelles sautés")
        print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, "
              f"{controles} checks)")
        return 1 if echecs else 0

    c, k = r["correlations"], r["laccord_avec_la_sagitta_est_une_coincidence"]
    # ⚠⚠⚠ L'ACCORD AVEC LA SAGITTA EST GARDE COMME COINCIDENCE, PAS COMME CAUSE : il est frappant
    # (1,11 en médiane) et la fixture le réfute d'un coup.
    v("l'accord numérique avec la sagitta est publié comme une coïncidence",
      0.7 < k["rapport_median"] < 1.5, str(k))
    v("... et il tombe avec le rayon d'un facteur bien plus grand que le bruit seul",
      c["brut_contre_rayon"] < -0.8, str(c["brut_contre_rayon"]))
    # ⛔ LE VERDICT : anti-predictif, brut comme normalise.
    v("le froissement est ANTI-prédictif des deux modes d'échec",
      r["le_froissement_est_anti_predictif"], str(c))
    # ⚠⚠ LA NORMALISATION RETIRE LE RAYON MAIS PAS LE SIGNE — les deux moities sont assertees.
    v("normaliser par la sagitta retire l'essentiel du rayon",
      r["normaliser_retire_le_rayon"],
      f"{c['normalise_contre_rayon']} contre {c['brut_contre_rayon']}")
    v("... et NE corrige PAS le signe", not r["normaliser_corrige_le_signe"],
      f"désalignement {c['normalise_contre_desalignement']}")
    # ⚠ Le tiers du bord est bien celui qui echoue ET celui qui froisse le moins.
    p = r["par_tiers"]
    v("le tiers qui échoue le plus est celui qui froisse le moins",
      p["bord"]["continuite"] > p["coeur"]["continuite"]
      and p["bord"]["froissement_brut_um"] < p["coeur"]["froissement_brut_um"], str(p))

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def afficher(r: dict) -> int:
    """L'affichage, séparé pour que la batterie puisse le lancer — la leçon de `93`."""
    k, c, p = r["laccord_avec_la_sagitta_est_une_coincidence"], r["correlations"], r["par_tiers"]
    # ⚠ La fixture est LUE de la mesure, jamais recopiée : un affichage qui porterait ses propres
    # nombres deviendrait la troisième description du même fait, et c'est celle qu'on lit.
    f = r["ce_que_le_champ_voit"]
    cas = f["cas"]
    chute = round(r["lignes"][0]["froissement_brut_um"] / r["lignes"][-1]["froissement_brut_um"], 1)
    print(f"{r['fragment']} · {r['bandes']} bandes\n")
    print(f"{'bande':>10} {'rayon':>7} {'froiss.':>9} {'sagitta':>9} {'mes/préd':>9} "
          f"{'désalign':>9} {'continuité':>11}")
    for x in r["lignes"]:
        print(f"  w{x['de']:03d}-{x['a']:03d} {x['rayon_mm']:>6.1f} "
              f"{x['froissement_brut_um']:>8.1f} {x['sagitta_predite_um']:>8.1f} "
              f"{x['mesure_sur_predit']:>9.2f} {x['desalignement']:>9.2f} "
              f"{x['continuite']:>11.1f}")
    print(f"\n{'ce que le champ VOIT':>26} {'R=5 mm':>8} {'R=20 mm':>10} {'rapport':>12}")
    for nom, cle in (("cylindre parfait", "cylindre_parfait"), ("+ axe courbe", "axe_courbe"),
                     ("+ bruit 5 µm", "bruit_5um"), ("+ bruit 20 µm", "bruit_20um")):
        x = cas[cle]
        rap = f"×{x['rapport_R5_sur_R20']}" if x["rapport_R5_sur_R20"] else "—"
        print(f"{nom:>26} {x['R5']:>8.2f} {x['R20']:>10.2f} {rap:>12}")
    print(f"\n⭐⭐⭐ LE CHAMP MESURE LA RUGOSITÉ DU MAILLAGE, établi par fixture et non par "
          f"corrélation :")
    print(f"   un cylindre parfait rend EXACTEMENT zéro, un cylindre à axe courbe aussi, et seul")
    print(f"   du bruit le réveille — presque sans dépendre du rayon "
          f"(×{cas['bruit_5um']['rapport_R5_sur_R20']} entre R=5 et R=20 mm).")
    print(f"   ⚠⚠ l'accord avec la sagitta ({k['rapport_median']} en médiane, {k['min']} à "
          f"{k['max']}) est une COÏNCIDENCE :")
    print(f"      elle prédit {f['sagitta_predite_a_R5_um']} µm là où le champ vaut zéro. "
          f"réfutée, gardée en fixture.")
    print(f"\n⭐⭐ donc les maillages humains sont ×{chute} plus LISSES au bord qu'au cœur là où")
    print(f"   la rugosité seule n'en donnerait que "
          f"×{cas['bruit_5um']['rapport_R5_sur_R20']} : c'est une propriété de la MATIÈRE")
    print("   maillée, pas de la géométrie du sondage.")
    print(f"\n{'':>26} {'rayon':>8} {'désalign':>10} {'continuité':>12}")
    print(f"{'froissement BRUT':>26} {c['brut_contre_rayon']:>+8.3f} "
          f"{c['brut_contre_desalignement']:>+10.3f} {c['brut_contre_continuite']:>+12.3f}")
    print(f"{'/ SAGITTA':>26} {c['normalise_contre_rayon']:>+8.3f} "
          f"{c['normalise_contre_desalignement']:>+10.3f} "
          f"{c['normalise_contre_continuite']:>+12.3f}")
    print(f"\n⛔ LE FROISSEMENT EST ANTI-PRÉDICTIF : il vaut "
          f"{p['coeur']['froissement_brut_um']} µm au cœur et "
          f"{p['bord']['froissement_brut_um']} µm au bord,")
    print(f"   alors que la continuité y passe de ×{p['coeur']['continuite']} à "
          f"×{p['bord']['continuite']}. un marcheur qui s'en servirait")
    print("   signalerait le cœur, où tout est propre, et se tairait au bord.")
    print(f"\n⚠⚠ normaliser retire le rayon ({c['brut_contre_rayon']} → "
          f"{c['normalise_contre_rayon']}) mais PAS le signe.")
    print("⚠⚠⚠ AVERTISSEMENT DE NIVEAU : `75` compare des CELLULES à rayon constant, ce fichier")
    print("   compare des BANDES à travers les rayons. Les deux peuvent être vrais — mais une")
    print("   marche de 31 spires change le rayon d'un facteur six, donc tout signal de")
    print("   confiance doit être vérifié À TRAVERS les rayons.")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer()
    if "message" in r:
        print(f"⚠ {r['message']}")
        return 1
    code = afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False) + "\n")
        print(f"\nécrit : {a.json}")
    return code


if __name__ == "__main__":
    sys.exit(main())
