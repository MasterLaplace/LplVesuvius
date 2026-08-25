#!/usr/bin/env python3
"""Que produit un détecteur d'encre sur un substrat dont on SAIT qu'il n'en porte pas ?

⚠⚠ **Le contrôle négatif que le domaine n'a pas.** Le papier fondateur d'EduceLab rapporte
un taux de faux positifs de 0,051 — mais sur des images qui contiennent de l'encre partout
autour. Il ne mesure jamais ce que le détecteur produit sur un substrat **connu sans
encre**. Le témoin parfait était pourtant dans leur scan — la feuille de papier de support
sur laquelle les fragments sont montés, imagée dans la même session, au même voxel — et le
nettoyage manuel le supprime : *« These are removed manually. »*

⭐⭐ **Le nôtre est meilleur, et il est déjà mesuré.** Une de nos traces sort à α = +1,01 :
sa distance à la matière **suit la fenêtre de rendu**, donc il n'y a aucune feuille à
portée — la surface est posée *en travers* de l'empilement. Ce n'est pas une supposition
sur la nature d'un substrat, c'est une **preuve géométrique** qu'il n'y a pas de face de
papyrus là. Toute « encre » que le modèle y rapporte est un faux positif par construction.

⚠ Ce fichier ne fait que **comparer deux prédictions**. Il ne juge ni l'une ni l'autre :
c'est la campagne qui garantit que les deux viennent du même volume, du même modèle, de la
même région et du même pas. Sans cette garantie, la comparaison ne voudrait rien dire, et
elle n'est pas vérifiable ici.

⚠⚠ **Ce que ce contrôle NE peut pas faire, et il faut le dire avant de le lire.** La région
rendue fait 1100 px de côté et le pas de balayage 8, donc la carte de prédiction fait
~137 px : **deux ordres de grandeur trop petite** pour que l'instrument typographique de
[`45`] y voie un interligne, qui demande des fenêtres de 512 px. On compare donc ce qu'une
carte de cette taille porte réellement — le **niveau** et la **dispersion** de la
prédiction — et pas sa typographie. Prétendre le contraire serait mesurer du bruit.

Usage :
    uv run python analysis/src/temoin_negatif.py \\
        --positif data/temoin_negatif/sur_sa_feuille.npy \\
        --negatif data/temoin_negatif/en_travers.npy \\
        --json docs/temoin_negatif.json
    python3 ../analysis/src/temoin_negatif.py --verifier
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


# ⚠⚠ **L'ECART-TYPE DU MODELE LA OU IL MARCHE.** Mesure dans `36` §5bis : sur Scroll 1, a
# 2,4 µm, ou ce modele atteint une AUC de 0,925, sa sortie a un ecart-type de 0,7712 pour une
# etendue de 4,453. Sur `PHerc1447` a 8,64 µm il rend 0,0171 -- QUARANTE-CINQ FOIS moins,
# c'est-a-dire une constante.
#
# ⭐ Ce nombre n'est pas un reglage, c'est ce qui rend ce controle capable d'echouer POUR LA
# BONNE RAISON. Sans lui, deux cartes plates donneraient un rapport proche de 1 et le
# verdict serait « le detecteur ne distingue pas le temoin » -- alors que la cause serait
# qu'il ne detecte rien nulle part sur ce rouleau. Un controle negatif ne veut rien dire
# tant que le controle POSITIF n'a pas montre qu'il y a quelque chose a controler.
SIGMA_MODELE_QUI_MARCHE = 0.7712
PART_MINIMALE_DU_POSITIF = 0.10

# ⚠⚠ CE QUE DEUX CARTES INDEPENDANTES DONNERAIENT, DERIVE ET NON CHOISI. Si deux cartes de
# meme dispersion sigma sont independantes, leur difference a un ecart-type sigma·racine(2),
# donc la mediane de sa valeur absolue vaut 0,6745·sigma·racine(2) = 0,9539·sigma. Rapporte
# a sigma, l'ecart attendu entre deux cartes SANS RAPPORT est donc proche de 1.
#
# ⭐ C'est la reference qui rend « est-ce la meme carte ? » repondable sans regler quoi que
# ce soit : on compare l'ecart observe a celui qu'auraient deux cartes etrangeres l'une a
# l'autre. Une premiere version comparait l'ecart a l'echelle utile du modele -- et DEUX
# CARTES PLATES INDEPENDANTES la satisfaisaient, parce qu'un petit ecart ABSOLU ne veut pas
# dire « la meme carte », il veut dire « deux cartes plates ». Ce sont les temoins qui l'ont
# dit, pas la relecture.
ECART_SI_INDEPENDANT = 0.9539


def decrire(carte) -> dict:
    """Ce qu'une carte de prédiction porte, sans jamais supposer qu'elle porte du texte.

    ⭐ `sigma` est la grandeur qui compte, et `36` §5bis l'a déjà utilisée : un modèle qui
    ne trouve rien ne rend pas zéro, il rend une **constante**. C'est l'écart-type qui
    l'attrape, pas la moyenne — une constante haute et une prédiction riche ont la même
    moyenne et des dispersions incomparables.
    """
    import numpy as np
    a = np.asarray(carte, dtype=np.float64).ravel()
    a = a[np.isfinite(a)]
    if a.size < 16:
        return {"n": int(a.size), "impossible": "carte trop petite"}
    q = np.percentile(a, [5, 50, 95])
    return {"n": int(a.size), "moyenne": float(a.mean()), "sigma": float(a.std()),
            "p05": float(q[0]), "mediane": float(q[1]), "p95": float(q[2]),
            "contraste_p95_p50": float(q[2] - q[1]),
            # ⚠ La part de la carte au-dessus de son propre milieu de plage : sur une
            # prediction constante elle s'effondre ou explose, sur une prediction
            # structuree elle reste dans une plage etroite.
            "part_haute": float((a > (a.min() + a.max()) / 2).mean())}


def _accord_pixel(positif, negatif) -> dict:
    """À quel point les deux cartes sont-elles la MÊME carte, pixel par pixel ?

    ⚠⚠ **Deux cartes de même écart-type ne sont pas la même carte.** Le rapport des σ dit
    que les deux prédictions ont la même *amplitude* ; il ne dit rien de savoir si elles
    disent la même *chose*. Or c'est là qu'est la question : un détecteur qui rend deux
    cartes différentes de même amplitude RÉPOND à ses entrées, même faiblement. Un
    détecteur qui rend deux fois la même carte sur deux surfaces géométriquement
    incompatibles ne répond pas du tout.

    ⭐ `ecart_median` est rapporté **en unités de la sortie du modèle là où il marche**, pas
    en valeur absolue : une différence de 0,004 ne veut rien dire tant qu'on ne sait pas si
    la sortie utile s'étale sur 0,01 ou sur 4,5.

    ⚠ Ne vaut que si les deux cartes ont la même forme — deux régions différentes n'ont
    aucune raison de se correspondre pixel à pixel, et les corréler serait un chiffre sans
    objet. Le refus est explicite.
    """
    import numpy as np
    a = np.asarray(positif, dtype=np.float64)
    b = np.asarray(negatif, dtype=np.float64)
    if a.shape != b.shape:
        return {"accord_pixel": None,
                "accord_impossible": f"formes différentes : {a.shape} contre {b.shape}"}
    a, b = a.ravel(), b.ravel()
    bon = np.isfinite(a) & np.isfinite(b)
    a, b = a[bon], b[bon]
    if a.size < 16:
        return {"accord_pixel": None, "accord_impossible": "trop peu de points communs"}
    sa, sb = a.std(), b.std()
    rho = float(((a - a.mean()) * (b - b.mean())).mean() / (sa * sb)) if sa > 0 and sb > 0 \
        else None
    ecart = float(np.median(np.abs(a - b)))
    interne = (float(sa) + float(sb)) / 2.0
    return {"accord_pixel": rho,
            "ecart_median": ecart,
            # ⚠ « en unites de l'echelle utile » repond a « est-ce visible ? ». « en unites
            # de la variation interne » repond a « est-ce la meme carte ? ». Deux questions,
            # deux nombres -- la premiere version n'avait que la premiere, et branchait
            # dessus.
            "ecart_median_en_sigma_utile": ecart / SIGMA_MODELE_QUI_MARCHE,
            "ecart_median_en_variation_interne": (ecart / interne) if interne > 0 else None,
            "ecart_attendu_si_independantes": ECART_SI_INDEPENDANT}


def decrire_entree(dossier: Path, top: int, left: int, cote: int,
                   depart: int, couches: int = 26) -> dict:
    """Ce que le modèle a REÇU, et pas seulement ce qu'il a rendu.

    ⚠⚠ **Le contrôle du contrôle.** Deux prédictions identiques ont une explication
    ennuyeuse avant d'en avoir une intéressante : si les deux fenêtres tombent hors des
    données, le modèle reçoit du noir deux fois et rend deux fois la même constante. Ce
    serait une tautologie, pas un résultat -- et elle ressemblerait exactement à un
    détecteur inerte. Sans cette mesure, la conclusion serait invérifiable.

    ⭐ La grandeur qui tranche est la **dispersion de l'entrée** : une fenêtre pleine de
    papyrus a du contraste, une fenêtre hors données n'en a aucun.
    """
    import numpy as np
    from PIL import Image
    tifs = sorted(dossier.glob("*.tif"))[depart:depart + couches]
    if not tifs:
        return {"impossible": f"aucune couche dans {dossier} à partir de {depart}"}
    stats = []
    for t in tifs:
        a = np.asarray(Image.open(t), dtype=np.float64)
        a = a[top:top + cote, left:left + cote]
        if a.size == 0:
            return {"impossible": f"fenêtre hors de l'image dans {t.name}"}
        stats.append((float(a.mean()), float(a.std()), float((a > 0).mean())))
    m = np.asarray(stats)
    return {"dossier": str(dossier), "couches": len(tifs),
            "fenetre": [top, left, cote, cote],
            "moyenne": float(m[:, 0].mean()), "sigma": float(m[:, 1].mean()),
            "part_non_nulle": float(m[:, 2].mean())}


def entrees_distinctes(a: dict, b: dict) -> dict:
    """Les deux fenêtres portent-elles réellement de la matière, et une matière DIFFÉRENTE ?

    ⚠ Deux réponses séparées, parce que deux pannes séparées : une fenêtre vide invalide
    l'expérience, deux fenêtres identiques la rendent tautologique. Les confondre ferait
    passer l'une pour l'autre.
    """
    if "impossible" in a or "impossible" in b:
        return {"entrees_valides": False,
                "pourquoi": a.get("impossible") or b.get("impossible")}
    vides = [n for n, x in (("positif", a), ("négatif", b)) if x["sigma"] <= 0.0]
    # ⚠ Le seuil de « ce sont deux fenetres differentes » n'est pas un reglage : deux
    # rendus du MEME contenu auraient les memes statistiques a la precision de calcul pres.
    # On demande seulement qu'elles ne soient pas egales, et on publie l'ecart.
    ecart = abs(a["sigma"] - b["sigma"]) / max(a["sigma"], b["sigma"], 1e-12)
    return {"entrees_valides": not vides,
            "fenetres_vides": vides,
            "ecart_relatif_sigma_entree": float(ecart),
            "entrees_identiques": ecart < 1e-9}


def comparer(positif, negatif) -> dict:
    """Le rapport des dispersions, et ce qu'il veut dire.

    ⚠⚠ Le verdict porte sur un RAPPORT, pas sur un seuil absolu. Un écart-type dépend de
    l'échelle de sortie du modèle, qui n'est pas la même d'un modèle à l'autre ; le rapport
    entre deux prédictions du **même** modèle, lui, est comparable. C'est la même raison qui
    fait que le test de convergence de `38` lit un exposant plutôt qu'une distance.
    """
    p, n = decrire(positif), decrire(negatif)
    # ⚠⚠ DEUX ECHECS QUI NE SE RESSEMBLENT PAS, ET QUI PARTAGEAIENT UNE CLE. `impossible`
    # veut dire « on n'a pas pu mesurer » -- il n'y a rien a rapporter. `raison` veut dire
    # « on a mesure, et le resultat ne permet pas de conclure » -- il y a tout a rapporter.
    # La premiere version les nommait toutes deux `raison`, donc le chemin d'impression du
    # second cas etait INATTEIGNABLE : une experience reelle, non concluante, sortait sur
    # une ligne d'erreur, en code de retour 1, sans ecrire son JSON. Le cas ou publier les
    # chiffres compte le plus etait exactement celui qui les jetait.
    if "impossible" in p or "impossible" in n:
        return {"positif": p, "negatif": n, "impossible": "une des cartes est trop petite"}
    rapport = (p["sigma"] / n["sigma"]) if n["sigma"] > 0 else float("inf")
    d = {"positif": p, "negatif": n, "rapport_sigma": rapport,
         **_accord_pixel(positif, negatif),
         "rapport_contraste": ((p["contraste_p95_p50"] / n["contraste_p95_p50"])
                               if n["contraste_p95_p50"] > 0 else float("inf")),
         "sigma_reference": SIGMA_MODELE_QUI_MARCHE,
         "part_du_modele_qui_marche": p["sigma"] / SIGMA_MODELE_QUI_MARCHE}
    # ⚠⚠ LA GARDE : si le controle POSITIF ne montre pas de structure, il n'y a pas de
    # detecteur en marche a tester, et le controle negatif ne peut rien dire. Refuser est
    # la seule reponse honnete -- un rapport proche de 1 se lirait sinon comme « le temoin
    # trompe le detecteur » alors qu'il veut dire « le detecteur est eteint des deux cotes ».
    if d["part_du_modele_qui_marche"] >= PART_MINIMALE_DU_POSITIF:
        d["concluant"] = True
        d["porte"] = "forte"
        return d

    d["raison"] = (
        f"le contrôle POSITIF est plat : σ = {p['sigma']:.4f}, soit "
        f"{d['part_du_modele_qui_marche']:.1%} de ce que ce modèle rend là où il "
        f"marche ({SIGMA_MODELE_QUI_MARCHE}). Il n'y a pas de détecteur en marche à "
        f"contrôler, donc le témoin négatif ne peut rien dire")

    # ⚠⚠ MAIS IL RESTE UNE AFFIRMATION, PLUS ETROITE, QUI ELLE TIENT. Le controle fort
    # visait : « le detecteur signale de l'encre la ou la geometrie prouve qu'il n'y a pas
    # de feuille ». Il est hors de portee -- le detecteur ne signale rien nulle part ici.
    #
    # ⭐ Le controle FAIBLE, lui, se lit sur la meme mesure : si les deux cartes sont la
    # MEME carte, alors la sortie du modele ne depend pas de la presence d'une feuille. Ce
    # n'est pas la these visee, c'est une these differente -- et elle est etablie, pas
    # supposee. La distinction doit rester visible dans le resultat, sinon un lecteur
    # prendrait l'une pour l'autre.
    #
    # ⚠ Le seuil est LE MEME que celui de la platitude, et volontairement : « les deux
    # cartes different de moins d'un dixieme de ce que le modele resout la ou il marche ».
    # Un second nombre, choisi separement, serait un reglage de plus a defendre.
    e = d.get("ecart_median_en_variation_interne")
    if e is not None and e < PART_MINIMALE_DU_POSITIF * ECART_SI_INDEPENDANT:
        d["concluant"] = True
        d["porte"] = "faible"
        d["these_etablie"] = (
            "la sortie du modèle ne dépend PAS de la présence d'une feuille : sur une "
            "surface qui suit une face de papyrus et sur une surface qui coupe "
            "l'empilement, il rend la même carte — leur écart vaut "
            f"{e:.1%} de ce que chacune varie, contre "
            f"{ECART_SI_INDEPENDANT:.0%} si elles étaient étrangères l'une à l'autre")
        d["these_hors_de_portee"] = (
            "que le détecteur signale de l'encre là où il n'y a pas de feuille — il n'en "
            "signale nulle part sur ce rouleau")
    else:
        d["concluant"] = False
        d["porte"] = "aucune"
    return d


def verifier() -> int:
    import numpy as np
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    rng = np.random.default_rng(0)
    riche = rng.normal(0.5, 0.20, size=(120, 120)).clip(0, 1)
    plate = np.full((120, 120), 0.5) + rng.normal(0, 0.002, size=(120, 120))

    d = decrire(riche)
    v("une carte structurée a une dispersion", d["sigma"] > 0.1, f"{d['sigma']:.4f}")
    v("... et un contraste p95−p50", d["contraste_p95_p50"] > 0.1)
    dp = decrire(plate)
    v("une carte CONSTANTE a une dispersion effondrée", dp["sigma"] < 0.01,
      f"{dp['sigma']:.5f}")

    c = comparer(riche, plate)
    v("le rapport des sigmas sépare les deux", c["rapport_sigma"] > 20,
      f"{c['rapport_sigma']:.1f}")
    # ⚠⚠ LA sonde : deux cartes ÉQUIVALENTES doivent donner un rapport proche de 1. Sans
    # ce controle, un instrument qui rendrait toujours un grand rapport passerait pour un
    # discriminant alors qu'il ne discriminerait rien.
    autre = rng.normal(0.5, 0.20, size=(120, 120)).clip(0, 1)
    c2 = comparer(riche, autre)
    v("... et ne sépare PAS deux cartes équivalentes",
      0.8 < c2["rapport_sigma"] < 1.25, f"{c2['rapport_sigma']:.3f}")
    # ⚠ La moyenne, elle, ne discrimine pas : les deux cartes de synthese ont la meme.
    # C'est pourquoi le verdict porte sur sigma et non sur le niveau.
    v("la moyenne ne distingue pas une constante d'une prédiction riche",
      abs(decrire(riche)["moyenne"] - dp["moyenne"]) < 0.02,
      f"{decrire(riche)['moyenne']:.3f} contre {dp['moyenne']:.3f}")

    v("une carte trop petite est REFUSÉE, pas décrite",
      "impossible" in decrire(np.zeros(4)))
    v("... et la comparaison refuse aussi",
      "impossible" in comparer(np.zeros(4), riche))
    v("une carte strictement constante ne divise pas par zéro",
      comparer(riche, np.full((50, 50), 0.5))["rapport_sigma"] == float("inf"))

    # ⚠⚠ LA garde, et sa sonde. Deux cartes PLATES donnent un rapport proche de 1, qui se
    # lirait « le temoin trompe le detecteur » alors qu'il veut dire « le detecteur est
    # eteint des deux cotes ». Le controle doit REFUSER de conclure.
    plate2 = np.full((120, 120), 0.5) + rng.normal(0, 0.002, size=(120, 120))
    mort = comparer(plate, plate2)
    v("deux cartes plates rendent un rapport proche de 1",
      0.5 < mort["rapport_sigma"] < 2.0, f"{mort['rapport_sigma']:.3f}")
    v("... et l'expérience est déclarée NON CONCLUANTE", mort["concluant"] is False)
    # ⚠ Insensible a la casse : la raison ecrit « POSITIF » en capitales, et un test
    # sensible a la casse aurait echoue sur une chaine parfaitement correcte.
    v("... en nommant le contrôle fautif",
      "positif" in (mort.get("raison") or "").lower(), mort.get("raison"))
    # ⚠ Et le controle du controle : une experience ou le positif a de la structure DOIT
    # rester concluante, sinon la garde eteindrait aussi les mesures valides.
    v("une expérience dont le positif a de la structure reste concluante",
      comparer(riche, plate)["concluant"] is True)

    # ⚠⚠ LE TEMOIN QUI MANQUAIT, ET QUI AURAIT ATTRAPE LE DEFAUT. « on n'a pas pu mesurer »
    # et « on a mesure, et ca ne conclut pas » partageaient la cle `raison`, donc le second
    # sortait par le chemin d'erreur du premier : une ligne, un code de retour 1, aucun
    # JSON. Un resultat non concluant est un RESULTAT -- il doit porter ses deux
    # descriptions et rester imprimable.
    v("une expérience non concluante n'est pas une expérience impossible",
      "impossible" not in mort)
    v("... et elle porte quand même ses deux mesures",
      "sigma" in mort["positif"] and "sigma" in mort["negatif"])
    v("... et le rapport reste chiffré",
      isinstance(mort.get("rapport_sigma"), float))
    v("une expérience IMPOSSIBLE, elle, n'a pas de verdict",
      "concluant" not in comparer(np.zeros(4), riche))

    # ⚠⚠ L'ACCORD PIXEL A PIXEL. Deux cartes de meme sigma ne sont pas la meme carte : le
    # rapport des sigmas ne peut pas faire cette difference, et c'est pourtant elle qui
    # separe « le detecteur repond faiblement » de « le detecteur ne repond pas ».
    ap_ = _accord_pixel(riche, riche + 1e-6)
    v("deux cartes quasi identiques s'accordent pixel à pixel",
      ap_["accord_pixel"] > 0.999, f"{ap_['accord_pixel']:.5f}")
    v("... et leur écart est négligeable devant l'échelle utile",
      ap_["ecart_median_en_sigma_utile"] < 1e-4)
    v("... et devant leur propre variation",
      ap_["ecart_median_en_variation_interne"] < 1e-3)
    # ⚠⚠ LA SONDE QUI A CORRIGE LE CRITERE. Deux cartes plates INDEPENDANTES ont un petit
    # ecart ABSOLU -- et un ecart proche de 1 rapporte a leur propre variation. C'est ce
    # second nombre qui repond a « est-ce la meme carte ? », et la loi qui le predit est
    # VERIFIEE ici plutot que supposee.
    ind = _accord_pixel(plate, plate2)
    v("deux cartes indépendantes s'écartent de la valeur PRÉDITE par la loi",
      0.75 < ind["ecart_median_en_variation_interne"] / ECART_SI_INDEPENDANT < 1.25,
      f"{ind['ecart_median_en_variation_interne']:.3f} contre {ECART_SI_INDEPENDANT}")
    ap2 = _accord_pixel(riche, autre)
    v("deux cartes de MÊME σ mais différentes ne s'accordent PAS",
      abs(ap2["accord_pixel"]) < 0.1, f"{ap2['accord_pixel']:+.4f}")
    v("... alors que le rapport des σ les déclarait équivalentes",
      0.8 < comparer(riche, autre)["rapport_sigma"] < 1.25)
    v("des formes différentes sont REFUSÉES, pas corrélées de force",
      _accord_pixel(riche, np.zeros((7, 7)))["accord_pixel"] is None)

    # ⚠ LA PORTEE FAIBLE, et sa sonde. Deux cartes plates ET identiques etablissent la
    # these etroite ; deux cartes plates mais DIFFERENTES n'etablissent rien du tout.
    faible = comparer(plate, plate + 1e-7)
    v("deux cartes plates ET identiques établissent la thèse étroite",
      faible.get("porte") == "faible", faible.get("porte"))
    v("... qui nomme aussi ce qui reste hors de portée",
      "these_hors_de_portee" in faible)
    plate_autre = np.full((120, 120), 0.5) + rng.normal(0, 0.002, size=(120, 120))
    v("deux cartes plates mais DIFFÉRENTES n'établissent rien",
      comparer(plate, plate_autre).get("porte") == "aucune")
    v("une expérience à portée forte est marquée comme telle",
      comparer(riche, plate).get("porte") == "forte")

    # ⚠⚠ LE CONTROLE DU CONTROLE : une fenetre d'entree vide invalide l'experience, et deux
    # entrees identiques la rendent tautologique. Deux pannes, deux reponses.
    pleine = {"sigma": 39.0, "moyenne": 89.0, "part_non_nulle": 0.93, "couches": 26}
    vide = {"sigma": 0.0, "moyenne": 0.0, "part_non_nulle": 0.0, "couches": 26}
    v("une fenêtre d'entrée VIDE invalide l'expérience",
      entrees_distinctes(pleine, vide)["entrees_valides"] is False)
    v("... en nommant laquelle", "négatif" in entrees_distinctes(pleine, vide)["fenetres_vides"])
    v("deux entrées IDENTIQUES sont signalées comme tautologiques",
      entrees_distinctes(pleine, dict(pleine))["entrees_identiques"] is True)
    v("deux entrées pleines et distinctes passent",
      entrees_distinctes(pleine, {**pleine, "sigma": 35.0})["entrees_valides"] is True
      and not entrees_distinctes(pleine, {**pleine, "sigma": 35.0})["entrees_identiques"])
    v("une entrée illisible est refusée, pas décrite",
      entrees_distinctes({"impossible": "x"}, pleine)["entrees_valides"] is False)

    if echecs:
        print(f"\nECHEC ({echecs} failures, {controles} checks)")
        return 1
    print(f"ALL PASS ({echecs} failures, {controles} checks)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--positif", type=Path, help="prédiction sur la surface qui CONVERGE")
    ap.add_argument("--negatif", type=Path, help="prédiction sur la surface EN TRAVERS")
    ap.add_argument("--json", type=Path)
    # ⚠⚠ Le controle du controle. Sans les entrees, deux cartes identiques ont une
    # explication ennuyeuse (deux fenetres vides) indistinguable de la conclusion.
    ap.add_argument("--entree-positif", type=Path, help="dossier de couches du positif")
    ap.add_argument("--entree-negatif", type=Path, help="dossier de couches du négatif")
    ap.add_argument("--fenetre-positif", type=int, nargs=3, metavar=("TOP", "LEFT", "DEPART"))
    ap.add_argument("--fenetre-negatif", type=int, nargs=3, metavar=("TOP", "LEFT", "DEPART"))
    ap.add_argument("--cote", type=int, default=1100)
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()
    if not a.positif or not a.negatif:
        ap.error("nommer les deux cartes, ou --verifier")

    import numpy as np
    for f in (a.positif, a.negatif):
        if not f.is_file():
            print(f"absent : {f} — lancer d'abord tools/campagne_temoin_negatif.sh",
                  file=sys.stderr)
            return 1
    d = comparer(np.load(a.positif), np.load(a.negatif))
    if a.entree_positif and a.entree_negatif and a.fenetre_positif and a.fenetre_negatif:
        ep = decrire_entree(a.entree_positif, a.fenetre_positif[0], a.fenetre_positif[1],
                            a.cote, a.fenetre_positif[2])
        en = decrire_entree(a.entree_negatif, a.fenetre_negatif[0], a.fenetre_negatif[1],
                            a.cote, a.fenetre_negatif[2])
        d["entree_positif"], d["entree_negatif"] = ep, en
        d.update(entrees_distinctes(ep, en))
    if "impossible" in d:
        print(f"⚠ {d['impossible']}", file=sys.stderr)
        return 1

    print(f"\n  {'':<22} {'n':>7} {'moyenne':>9} {'sigma':>9} {'p95−p50':>9} "
          f"{'part haute':>11}")
    print("  " + "-" * 72)
    for nom, k in (("sur sa feuille  α=+0,00", "positif"),
                   ("en travers      α=+1,01", "negatif")):
        x = d[k]
        print(f"  {nom:<22} {x['n']:>7} {x['moyenne']:>9.4f} {x['sigma']:>9.4f} "
              f"{x['contraste_p95_p50']:>9.4f} {x['part_haute']:>11.3f}")

    if "entree_positif" in d and "impossible" not in d["entree_positif"]:
        print(f"\n  CE QUE LE MODÈLE A REÇU (moyenne des couches) :")
        for nom, k in (("sur sa feuille", "entree_positif"),
                       ("en travers", "entree_negatif")):
            x = d[k]
            print(f"    {nom:<16} moyenne {x['moyenne']:>8.2f}  σ {x['sigma']:>8.2f}  "
                  f"non nul {x['part_non_nulle']:>6.1%}  ({x['couches']} couches)")
        if not d.get("entrees_valides", True):
            print(f"    ⚠⚠ FENÊTRE VIDE : {d['fenetres_vides']} — l'expérience est nulle")
        elif d.get("entrees_identiques"):
            print("    ⚠⚠ LES DEUX ENTRÉES SONT IDENTIQUES — la comparaison est tautologique")
        else:
            print(f"    ⭐ deux fenêtres distinctes et pleines : leurs σ diffèrent de "
                  f"{d['ecart_relatif_sigma_entree']:.1%}")

    print(f"\n  rapport des écarts-types : ×{d['rapport_sigma']:.1f}")
    print(f"  rapport des contrastes   : ×{d['rapport_contraste']:.1f}")
    print(f"  σ du positif rapporté au modèle qui marche : "
          f"{d['part_du_modele_qui_marche']:.1%} de {SIGMA_MODELE_QUI_MARCHE}")
    if d.get("accord_pixel") is not None:
        print(f"  accord PIXEL À PIXEL des deux cartes : ρ = {d['accord_pixel']:+.4f}, "
              f"écart médian {d['ecart_median']:.5f}")
        if d.get("ecart_median_en_variation_interne") is not None:
            print(f"    soit {d['ecart_median_en_variation_interne']:.1%} de ce que chaque "
                  f"carte varie (deux cartes étrangères : {ECART_SI_INDEPENDANT:.0%}), et "
                  f"{d['ecart_median_en_sigma_utile']:.2%} de l'échelle utile du modèle")
    elif d.get("accord_impossible"):
        print(f"  accord pixel à pixel : non mesurable — {d['accord_impossible']}")

    if d.get("porte") == "faible":
        print(f"\n  ⚠⚠ LA THÈSE VISÉE EST HORS DE PORTÉE — {d['raison']}.")
        print("      `36` §5bis l'avait déjà mesuré, et sur le volume de surface PUBLIÉ :")
        print("      notre chaîne n'y est pour rien, le modèle est inerte sur ce rouleau.")
        print(f"\n  ⭐⭐ MAIS UNE THÈSE PLUS ÉTROITE EST ÉTABLIE : {d['these_etablie']}.")
        print("      Une feuille et une coupe en travers de l'empilement ne se ressemblent")
        print("      pas dans la direction que ce modèle mange. Rendre la même carte sur")
        print("      les deux, ce n'est pas répondre faiblement : c'est ne pas répondre.")
        print("      ⚠ Ce qui reste NON établi : " + d["these_hors_de_portee"] + ".")
    elif not d.get("concluant", True):
        print(f"\n  ⚠⚠ EXPÉRIENCE NON CONCLUANTE — {d['raison']}.")
        print("      Ce n'est pas un échec du témoin, c'est un échec du contrôle positif :")
        print("      `36` §5bis avait déjà mesuré que ce modèle rend une CONSTANTE sur ce")
        print("      rouleau. Un témoin négatif valide demande un rouleau où le détecteur")
        print("      fonctionne — et une surface en travers de CE rouleau-là, que ce dépôt")
        print("      ne possède pas.")
    elif d["rapport_sigma"] >= 3.0:
        print("\n  ⭐⭐ Le détecteur se TAIT là où la géométrie prouve qu'il n'y a pas de")
        print("      feuille. C'est le contrôle négatif que le papier fondateur n'a pas :")
        print("      un substrat connu sans encre, dans le même volume et le même modèle.")
    elif d["rapport_sigma"] <= 1.5:
        print("\n  ⚠⚠ Le détecteur produit AUTANT de structure sur une surface dont on a la")
        print("      preuve géométrique qu'elle n'est pas une feuille. Ce qu'il rapporte")
        print("      là est un faux positif par construction — et rien ne le distinguait.")
    else:
        print("\n  ⚠ Écart intermédiaire : le détecteur est plus discret sur le témoin, sans")
        print("    s'y taire. À ne pas lire comme une validation.")

    if a.json:
        a.json.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8")
        print(f"\n  écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
