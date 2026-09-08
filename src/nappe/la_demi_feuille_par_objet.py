#!/usr/bin/env python3
"""La demi-feuille — le critere de marche perdue — vaut-elle la meme chose sur chaque objet ?

⚠⚠⚠ POURQUOI CE FICHIER EXISTE, ET IL CORRIGE UNE OMISSION DE `85`. `85` conclut que le maillage
a 45,532 µm ne peut pas donner le pas inter-feuilles, et que **la demi-feuille de `PHercParis4`
reste un chiffre a mesurer ailleurs**. Elle etait mesuree, a cote, dans un clone de l'arbre :
`winding-ruler/results/atlas_collection_v2.csv` publie la periode inter-spires de **36 objets**,
dont les treize du prix, le temoin, l'objet courant et le candidat. C'est la sixieme fois que
« chercher dehors ce qu'on croit absent » paie dans ce depot, et `67` §1 l'avait deja ecrit pour
ce fichier precis.

⭐⭐⭐ ET LE PREMIER FAIT EST LE PLUS PORTEUR DE TOUT L'APPAREIL DE MARCHE. Le depot derive sa
demi-feuille — **67,75 µm**, le critere qui declare une marche perdue — de **135,5 µm** mesures
sur les douze paires consecutives des treize spires publiees de `PHerc0500P2`. L'atlas mesure
**196,6 µm** de mediane sur le meme fragment, avec p25 = **131,1 µm**. Notre chiffre est donc au
**premier quartile de son propre objet** : la marche est jugee dans le quartile le plus SERRE de
la matiere, donc les portees publiees sont des BORNES BASSES.

⚠⚠ CE NE SONT PAS DEUX MESURES CONTRADICTOIRES, ET LA DIFFERENCE EST DE POPULATION. Les deux
nomment la meme grandeur — la distance d'une surface de feuille a la suivante — mais l'une porte
sur douze paires d'une region et l'autre sur seize coupes et huit cents rayons du fragment
entier. Le lire comme une contradiction serait la faute ; le lire comme un ECHANTILLON est le
resultat.

⚠⚠ Et les chaines d'instrument diffferent aussi, ce qui borne la confiance dans un sens connu :
l'atlas lit des PREDICTIONS de surface le long de rayons, et une prediction qui fusionne deux
feuilles voisines SAUTE un ecart et en rapporte un double — donc l'atlas surestime plutot qu'il
ne sous-estime. Notre chiffre vient de surfaces publiees, donc il est plus direct, mais local.

⚠ Le clone est gitignore (`/data/*`). Ce fichier REFUSE en nommant la commande de clonage plutot
que de deviner : un critere de securite derive d'un fichier absent serait un critere qui echoue a
etre derive.

Usage :
    uv run python src/nappe/la_demi_feuille_par_objet.py
    uv run python src/nappe/la_demi_feuille_par_objet.py --verifier
    uv run python src/nappe/la_demi_feuille_par_objet.py \\
        --json docs/mesures/la_demi_feuille_par_objet.json
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
ATLAS = RACINE / "data" / "repos" / "winding-ruler" / "results" / "atlas_collection_v2.csv"
CLONE = "git clone https://github.com/pscamillo/winding-ruler data/repos/winding-ruler"
WRAPS = RACINE / "docs" / "mesures" / "les_wraps_publies.json"
CARTE = RACINE / "docs" / "carte_separabilite"
COURANT = "PHerc0500P2"
CANDIDAT = "PHercParis4"


def atlas(chemin: Path = ATLAS) -> dict[str, dict]:
    """La periode inter-spires publiee par `winding-ruler`, objet par objet.

    ⚠⚠ LES COLONNES SONT LUES PAR LEUR NOM, jamais par leur position. J'ai lu ce fichier a
    l'`awk` en decalant d'un rang — `lambda_med_um` est la quatorzieme et non la quinzieme — et
    j'ai affiche des p25 en croyant afficher des medianes. Un index dit ce que l'en-tete valait le
    jour ou on l'a compte.
    """
    if not chemin.is_file():
        raise FileNotFoundError(
            f"atlas absent : {chemin.relative_to(RACINE)}\n  le cloner : {CLONE}")
    out = {}
    with chemin.open() as f:
        for ligne in csv.DictReader(f):
            out[ligne["scroll"]] = {
                "lambda_um": float(ligne["lambda_med_um"]),
                "lambda_p25_um": float(ligne["lambda_p25_um"]),
                "lambda_p75_um": float(ligne["lambda_p75_um"]),
                "demi_um": float(ligne["lambda_med_um"]) / 2.0,
                "spires_median": float(ligne["wraps_med"]),
                "spires_p10": float(ligne["wraps_p10"]),
                "spires_p90": float(ligne["wraps_p90"]),
                "coupes": int(ligne["n_slices"]),
                "rayons": int(ligne["n_rays"]),
                "niveau": int(ligne["level"]),
                "zarr": ligne["zarr"],
            }
    return out


def le_notre(chemin: Path = WRAPS) -> dict | None:
    """Le pas inter-feuilles que ce depot a mesure sur les spires publiees, et sa demi-feuille.

    ⚠ Le rang 1 et lui seul : le rang 2 vaut 320,7 µm et le rang 3 454,6 µm, donc les rangs
    superieurs ne sont pas des multiples du premier — l'ecart croit vers l'exterieur. Prendre un
    rang superieur divise par son rang melangerait deux rayons.
    """
    if not chemin.is_file():
        return None
    d = json.loads(chemin.read_text())
    r1 = d.get("resume", {}).get("1")
    if not r1:
        return None
    return {"fragment": d["fragment"], "paires": r1["paires"],
            "pas_um": r1["mediane_um"], "demi_um": r1["mediane_um"] / 2.0,
            "volume": d["volume"], "voxel_um": d["voxel_um"]}


def percentile_estime(valeur: float, e: dict) -> float:
    """A quel percentile de la distribution de cet objet cette valeur tombe-t-elle ?

    ⭐⭐ C'EST CE QUI TRANSFORME UN DESACCORD EN RESULTAT. Deux nombres differents ne disent rien ;
    un nombre SITUE dans la distribution de l'autre dit quelle partie de l'objet il decrit.

    ⚠⚠⚠ ET C'EST UNE CORRECTION D'UNE FAUTE A MOI. Ma premiere version rendait un mot — « au
    premier quartile » — en tolerant 5 % autour de p25. Ce 5 % etait un SEUIL CHOISI POUR QUE LE
    CHIFFRE DU JOUR PASSE, soit le piege numero un de ce depot, et une sonde qui le retirait
    faisait basculer le verdict de « au premier quartile » a « entre le quartile et la mediane ».
    Un percentile n'a aucun seuil : il rend un nombre, et la revendication devient falsifiable.

    ⚠ L'interpolation est LINEAIRE entre les trois quantiles publies, et elle ne pretend pas
    plus : l'atlas ne publie que p25, la mediane et p75, donc on ne peut pas faire mieux sans
    supposer une forme de loi. Hors des bornes, la valeur est bornee a 5 et 95 plutot
    qu'extrapolee — extrapoler sur une queue qu'on n'a pas mesuree serait inventer.
    """
    p25, p50, p75 = e["lambda_p25_um"], e["lambda_um"], e["lambda_p75_um"]
    if valeur <= p25:
        return 5.0 if valeur < p25 else 25.0
    if valeur <= p50:
        return 25.0 + 25.0 * (valeur - p25) / max(1e-9, p50 - p25)
    if valeur <= p75:
        return 50.0 + 25.0 * (valeur - p50) / max(1e-9, p75 - p50)
    return 95.0


def les_treize() -> tuple[set[str], set[str]]:
    """Les treize rouleaux du prix et le temoin, lus sur les fiches de la carte."""
    noms = [p.stem for p in sorted(CARTE.glob("*.json"))]
    return ({n for n in noms if not n.startswith("_TEMOIN_")},
            {n.replace("_TEMOIN_", "") for n in noms if n.startswith("_TEMOIN_")})


def separe(valeurs: list[float]) -> dict:
    """L'etendue relative d'un ensemble de valeurs — un critere qui ne separe pas ne choisit pas.

    ⚠ Le RAPPORT max/min et non un ecart-type : la question est « ces objets sont-ils
    distinguables sur cette grandeur », et un rapport se lit sans supposer une forme de loi.
    """
    if not valeurs:
        return {}
    return {"objets": len(valeurs), "min": round(min(valeurs), 1),
            "max": round(max(valeurs), 1), "rapport": round(max(valeurs) / min(valeurs), 2),
            "median": round(float(np.median(valeurs)), 1)}


def mesurer() -> dict:
    a = atlas()
    n = le_notre()
    prix, temoin = les_treize()
    lignes = []
    for nom, e in sorted(a.items(), key=lambda kv: kv[1]["lambda_um"]):
        lignes.append({"nom": nom, **e,
                       "du_prix": nom in prix, "temoin": nom in temoin,
                       "courant": nom == COURANT, "candidat": nom == CANDIDAT})
    r = {
        "atlas": str(ATLAS.relative_to(RACINE)), "objets": len(lignes),
        "lignes": lignes,
        "le_notre": n,
        "separation": {
            "les_treize": separe([x["demi_um"] for x in lignes if x["du_prix"]]),
            "tout_latlas": separe([x["demi_um"] for x in lignes]),
        },
    }
    if n and n["fragment"] in a:
        e = a[n["fragment"]]
        r["confrontation"] = {
            "fragment": n["fragment"],
            "le_notre_um": n["pas_um"], "paires": n["paires"],
            "atlas_um": e["lambda_um"],
            "atlas_p25_um": e["lambda_p25_um"], "atlas_p75_um": e["lambda_p75_um"],
            "rapport": round(e["lambda_um"] / n["pas_um"], 2),
            "percentile_du_notre": round(percentile_estime(n["pas_um"], e), 1),
            # ⭐⭐⭐ LA CONSEQUENCE, ET ELLE EST LA RAISON DU FICHIER : un critere derive du
            # quartile le plus SERRE est plus exigeant que l'objet, donc les portees publiees
            # sous ce critere sont des bornes BASSES.
            # ⭐⭐⭐ LA REVENDICATION, ET ELLE EST CELLE QU'ON TESTE : notre pas est dans la
            # moitie la plus SERREE de son propre objet, donc le critere derive de lui est plus
            # exigeant que l'objet et les portees publiees sous ce critere sont des bornes
            # BASSES. Le seuil est 50 parce que c'est LA revendication, pas un reglage.
            "notre_critere_est_conservateur": percentile_estime(n["pas_um"], e) < 50.0,
        }
    if CANDIDAT in a and n:
        r["prix_du_changement_dobjet"] = {
            "de": n["fragment"], "vers": CANDIDAT,
            "demi_actuelle_um": n["demi_um"],
            "demi_du_candidat_um": a[CANDIDAT]["demi_um"],
            "plus_permissif_de": round(a[CANDIDAT]["demi_um"] / n["demi_um"] - 1.0, 3),
        }
    return r


def verifier() -> int:
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  FAIL {nom} — {detail}")

    # --- la mécanique, sur des distributions fabriquées --------------------------------------
    faux = {"lambda_um": 200.0, "lambda_p25_um": 130.0, "lambda_p75_um": 330.0}
    v("la valeur du premier quartile rend exactement 25",
      percentile_estime(130.0, faux) == 25.0, str(percentile_estime(130.0, faux)))
    v("... la médiane exactement 50", percentile_estime(200.0, faux) == 50.0)
    v("... et le troisième quartile exactement 75",
      percentile_estime(330.0, faux) == 75.0, str(percentile_estime(330.0, faux)))
    # ⚠⚠ L'INTERPOLATION EST MONOTONE : une valeur plus grande ne peut pas tomber plus bas.
    v("le percentile croît avec la valeur",
      all(percentile_estime(a, faux) <= percentile_estime(b, faux)
          for a, b in zip(range(100, 400, 7), range(101, 401, 7))))
    # ⚠⚠⚠ ET IL N'EXTRAPOLE PAS hors des quantiles publiés : une queue non mesurée ne s'invente
    # pas, donc les valeurs extrêmes sont BORNÉES et non prolongées.
    v("hors des bornes il borne au lieu d'extrapoler",
      percentile_estime(10.0, faux) == 5.0 and percentile_estime(9999.0, faux) == 95.0,
      f"{percentile_estime(10.0, faux)} et {percentile_estime(9999.0, faux)}")
    v("le rapport d'un ensemble à une valeur vaut un", separe([5.0])["rapport"] == 1.0)
    v("... et un ensemble vide ne rend rien plutôt qu'un zéro", separe([]) == {})

    # --- l'atlas réel -------------------------------------------------------------------------
    if not ATLAS.is_file():
        print(f"  ⚠ atlas absent : contrôles sur données réelles sautés — {CLONE}")
        print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, "
              f"{controles} checks)")
        return 1 if echecs else 0

    # ⚠⚠ UN ATLAS MALFORME EST UN ECHEC NOMME, PAS UNE EXCEPTION. Une sonde de cette tranche
    # decalait les colonnes d'un rang et la batterie mourait sur un `int()` : tous les controles
    # suivants n'avaient pas lieu, sans que le compte le dise. C'est la lecon de `84`, repayee.
    try:
        r = mesurer()
    except (ValueError, KeyError, FileNotFoundError) as err:
        v("l'atlas se lit par ses noms de colonne", False, f"{type(err).__name__}: {err}")
        print(f"FAILURES ({echecs} failures, {controles} checks)")
        return 1
    par = {x["nom"]: x for x in r["lignes"]}
    v("l'atlas porte trente-six objets", r["objets"] == 36, str(r["objets"]))
    v("... dont les treize du prix", sum(1 for x in r["lignes"] if x["du_prix"]) == 13,
      str(sum(1 for x in r["lignes"] if x["du_prix"])))
    v("... le témoin, l'objet courant et le candidat",
      any(x["temoin"] for x in r["lignes"]) and COURANT in par and CANDIDAT in par)
    # ⚠ La demi-feuille est la moitié de la période, et ça doit tenir sur chaque ligne.
    v("la demi-feuille est la moitié de la période, partout",
      all(abs(x["demi_um"] * 2 - x["lambda_um"]) < 1e-9 for x in r["lignes"]))

    c = r.get("confrontation")
    v("la confrontation existe", c is not None)
    if c:
        # ⭐⭐⭐ LE FAIT PORTEUR : notre chiffre est au premier quartile de son propre objet.
        # ⭐⭐⭐ LE FAIT PORTEUR, en un nombre plutôt qu'en un mot : notre pas est dans la
        # moitié la plus serrée de son propre objet.
        v("notre pas est dans la moitié la plus serrée de son propre objet",
          c["percentile_du_notre"] < 50.0, f"percentile {c['percentile_du_notre']}")
        v("... et il est proche du premier quartile plutôt que de la médiane",
          c["percentile_du_notre"] < 37.5, f"percentile {c['percentile_du_notre']}")
        v("... donc notre critère est conservateur", c["notre_critere_est_conservateur"],
          f"{c['le_notre_um']} contre p25 {c['atlas_p25_um']}")
        # ⚠ L'écart est réel et se chiffre : ne pas le lisser.
        v("l'écart entre les deux chaînes est publié", c["rapport"] > 1.3,
          f"×{c['rapport']} — {c['le_notre_um']} contre {c['atlas_um']}")
        v("... et le nombre de paires de notre mesure est dit", c["paires"] == 12,
          str(c["paires"]))

    p = r.get("prix_du_changement_dobjet")
    v("le prix du changement d'objet est chiffré", p is not None)
    if p:
        # ⭐⭐ CE QUE `85` DISAIT NON CHIFFRE.
        v("... et le candidat est plus permissif", p["plus_permissif_de"] > 0.25,
          f"+{p['plus_permissif_de']:.1%} — {p['demi_actuelle_um']} → "
          f"{p['demi_du_candidat_um']} µm")

    # ⭐ ET LA QUESTION DU CHOIX DE ROULEAU, PAR LE COTE GEOMETRIQUE : un critere qui ne separe
    # pas ne choisit pas. Les treize tiennent dans un facteur 1,2 sur cette grandeur.
    s = r["separation"]["les_treize"]
    v("les treize du prix tiennent dans un facteur 1,25 de demi-feuille",
      s["rapport"] < 1.25, f"×{s['rapport']} — {s['min']} à {s['max']} µm")
    v("... et l'atlas entier est plus large que les treize",
      r["separation"]["tout_latlas"]["rapport"] > s["rapport"],
      f"×{r['separation']['tout_latlas']['rapport']} contre ×{s['rapport']}")

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    a = p.parse_args()
    if a.verifier:
        return verifier()

    try:
        r = mesurer()
    except FileNotFoundError as err:
        print(f"erreur : {err}", file=sys.stderr)
        return 2
    print(f"{r['objets']} objets dans {r['atlas']}\n")
    print(f"{'objet':14} {'période':>9} {'p25':>7} {'p75':>7} {'demi-feuille':>13} "
          f"{'spires':>7}  rôle")
    for x in r["lignes"]:
        role = ("DU PRIX" if x["du_prix"] else ("témoin" if x["temoin"] else
                ("courant" if x["courant"] else ("CANDIDAT" if x["candidat"] else ""))))
        print(f"{x['nom']:14} {x['lambda_um']:>9.1f} {x['lambda_p25_um']:>7.1f} "
              f"{x['lambda_p75_um']:>7.1f} {x['demi_um']:>13.1f} "
              f"{x['spires_median']:>7.0f}  {role}")
    c = r.get("confrontation")
    if c:
        print(f"\n⭐⭐⭐ CONFRONTATION sur {c['fragment']} :")
        print(f"   ce dépôt   {c['le_notre_um']:.1f} µm  ({c['paires']} paires des spires "
              "publiées)")
        print(f"   l'atlas    {c['atlas_um']:.1f} µm  (p25 {c['atlas_p25_um']:.1f} · "
              f"p75 {c['atlas_p75_um']:.1f})")
        print(f"   notre chiffre tombe au percentile {c['percentile_du_notre']:.0f} de son "
              f"propre objet (×{c['rapport']})")
        print(f"   {'✅' if c['notre_critere_est_conservateur'] else '⛔'} donc le critère de "
              "marche perdue est CONSERVATEUR : les portées publiées sont des bornes basses")
    p4 = r.get("prix_du_changement_dobjet")
    if p4:
        print(f"\n⭐⭐ PRIX DU CHANGEMENT D'OBJET, que `85` disait non chiffré :")
        print(f"   demi-feuille {p4['de']} {p4['demi_actuelle_um']:.2f} µm → "
              f"{p4['vers']} {p4['demi_du_candidat_um']:.2f} µm "
              f"(+{p4['plus_permissif_de']:.1%} de tolérance)")
    s = r["separation"]
    print(f"\n⛔ COMME CRITÈRE DE CHOIX DE ROULEAU : les treize tiennent dans "
          f"×{s['les_treize']['rapport']} ({s['les_treize']['min']} à "
          f"{s['les_treize']['max']} µm de demi-feuille)")
    print(f"   l'atlas entier va jusqu'à ×{s['tout_latlas']['rapport']} — donc l'étroitesse est "
          "celle des treize, pas celle de la mesure")
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False) + "\n")
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
