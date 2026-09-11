#!/usr/bin/env python3
"""LE CONTRÔLE DUR : nos cartes sont-elles plus périodiques qu'une surface SANS feuille ?

⚠⚠⚠ POURQUOI CE FICHIER EXISTE, et c'est la question que tout le reste prépare.
[`60`](../../docs/archive/60_la_constante_qui_rendait_le_modele_muet.md) établit que les quatre
surfaces publiées de `PHerc1447` rendent **8 fenêtres périodiques sur 12** là où leurs propres
pixels mélangés en rendent **zéro** — p = 0,0007. Mais mélanger des pixels détruit **toute**
structure spatiale, donc ce test répond « nos cartes sont structurées », ce qui est plus pauvre
que « nos cartes portent de l'écriture ». Le contrôle qui manquait est un **témoin négatif
réel** : une surface qui garde la texture du bloc et dont on prouve **géométriquement**
qu'aucune feuille n'est à portée.

  ⭐⭐⭐ Il en existe deux, et c'est ce qui rend le test possible :
     `en_travers_grand`  α = +1,01  →  5 fenêtres
     `en_travers_2`      α = +0,99  →  2 fenêtres
     ensemble **7**, contre les **6** que `fenetres_par_region.py` déclare nécessaires.

⚠⚠ Le groupement est légitime ici, et la docstring de `fisher_periodicite_groupee` dit
exactement pourquoi : il suppose des observations **distinctes**, et ce serait faux pour deux
rendus d'une même surface. Nos deux témoins viennent de **deux graines différentes**, donc de
deux traces différentes — `data/leur_graine/trace/` et `data/temoin_2/trace/` portent chacun
leur `seed.json`, et la seconde a été **tirée par l'outil**, pas choisie.

⚠ Ce que ce fichier N'ÉTABLIT PAS : que nos cartes portent du grec. Il établit que leur
périodicité n'est pas ce qu'une surface sans feuille produit. Lire les lettres reste l'affaire
du juge de [`09`](../../docs/archive/09_protocole_jugement_modele.md), et cette session en est
disqualifiée.

Usage :
    uv run python src/encre/temoin_contre_nos_cartes.py --verifier
    uv run python src/encre/temoin_contre_nos_cartes.py --json docs/mesures/temoin_contre_nos_cartes.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src"))

# ⚠ Le test vient de `fenetres_par_region`, pas de `typographie` : celui de `typographie`
# refuse de calculer sous huit fenêtres, ce qui est juste pour un test PAR CARTE et faux ici
# — le témoin en a sept, et c'est précisément ce nombre qu'on veut confronter aux douze du
# rouleau. La borne de puissance est appliquée à part, sur le compte du témoin.
from encre.fenetres_par_region import fisher_unilateral  # noqa: E402

SUJET = RACINE / "docs" / "mesures" / "typographie_de_nos_cartes.json"
TEMOIN = RACINE / "docs" / "mesures" / "typographie_temoins_groupes.json"

CARTES_DU_ROULEAU = ("ink_20250702235910", "ink_20250703025628",
                     "ink_20250703034159", "ink_20251105093211")
"""Les quatre surfaces publiées de `PHerc1447`, écrites plutôt que déduites.

⚠⚠ `ink_segment_complet` est dans le même relevé et n'est PAS du rouleau : c'est le témoin
POSITIF de `Scroll 1`, dont on sait déjà qu'il porte du texte. L'inclure ferait dire au test
« du texte connu est plus périodique qu'une surface sans feuille », ce qui est vrai et sans
intérêt — et gonflerait le sujet de moitié. Le piège a déjà été payé une fois, sur le test
groupé de `60`, d'où l'option `--temoin` de `typographie.py`.
"""

TEMOINS_NEGATIFS = ("en_travers_grand", "en_travers_2")
"""Les deux surfaces à α ≈ +1. Une troisième doit être ajoutée ici, donc vue."""


def compter(releve: dict, noms) -> tuple[int, int]:
    """(fenêtres périodiques, fenêtres) sommées sur les cartes nommées.

    ⚠ On somme les cartes NOMMÉES, jamais « toutes celles du fichier » : un relevé porte
    aussi les contrôles par mélange et, dans le cas du sujet, un témoin positif étranger au
    rouleau. Sommer ce qu'on trouve mélangerait les trois.
    """
    per = tot = 0
    for c in releve.get("cartes", []):
        if c.get("carte") in noms and c.get("rouleau") == "nos_cartes":
            per += int(c.get("fenetres_periodiques", 0))
            tot += int(c.get("fenetres", 0))
    return per, tot


def controle_dur(sujet: dict, temoin: dict) -> dict:
    """Le test à deux échantillons : le rouleau contre les surfaces sans feuille.

    ⚠⚠ Unilatéral, et dans le sens DÉCLARÉ D'AVANCE : on demande si le rouleau est **plus**
    périodique que le témoin. Regarder les deux sens après coup doublerait le taux de faux
    positifs, et choisir le sens après avoir vu les chiffres serait pire encore.
    """
    a, na = compter(sujet, CARTES_DU_ROULEAU)
    b, nb = compter(temoin, TEMOINS_NEGATIFS)
    p = fisher_unilateral(a, na - a, b, nb - b) if (na and nb) else None
    # ⚠⚠ LA FRAGILITE EST RAPPORTEE AVEC LE p, ET C'EST OBLIGATOIRE ICI. Sept fenetres de
    # temoin, c'est peu : une fenetre periodique de plus ou de moins change le resultat, et un
    # p de 0,04 publie sans dire ca se lirait comme un p de 0,0007. Le nombre repond a « une
    # fenetre suffirait-elle a renverser ? », qui est la seule question qu'un lecteur pose
    # devant un seuil frole.
    fragilite = {}
    if na and nb:
        if b + 1 <= nb:
            fragilite["si_le_temoin_avait_une_periodique_de_plus"] = fisher_unilateral(
                a, na - a, b + 1, nb - b - 1)
        if b >= 1:
            fragilite["si_le_temoin_en_avait_une_de_moins"] = fisher_unilateral(
                a, na - a, b - 1, nb - b + 1)
        if a >= 1:
            fragilite["si_le_rouleau_en_avait_une_de_moins"] = fisher_unilateral(
                a - 1, na - a + 1, b, nb - b)
    return {
        "rouleau": {"periodiques": a, "fenetres": na,
                    "part": (a / na) if na else None},
        "temoin_negatif": {"periodiques": b, "fenetres": nb,
                           "part": (b / nb) if nb else None},
        "table": [a, na - a, b, nb - b],
        "p": p,
        "fragilite": fragilite,
        "resiste_a_une_fenetre": all(x < 0.05 for x in fragilite.values()) if fragilite else False,
        "fenetres_du_temoin": nb,
        "assez_de_fenetres": nb >= 6,
    }


def rapporter(r: dict) -> None:
    """La sortie lisible, et ce que le chiffre autorise à dire."""
    ro, te = r["rouleau"], r["temoin_negatif"]
    print(f"  PHerc1447, 4 surfaces publiees   {ro['periodiques']}/{ro['fenetres']} "
          f"periodiques ({100 * (ro['part'] or 0):.0f} %)")
    print(f"  temoins NEGATIFS, 2 traces       {te['periodiques']}/{te['fenetres']} "
          f"periodiques ({100 * (te['part'] or 0):.0f} %)")
    print(f"  Fisher unilateral {r['table']} : p = "
          + (f"{r['p']:.4f}" if r["p"] is not None else "—"))
    print()
    if not r["assez_de_fenetres"]:
        print("  ⚠⚠ moins de 6 fenetres de temoin : l'experience n'a pas la puissance,")
        print("     et un p non significatif ne voudrait rien dire.")
        return
    if r["p"] is not None and r["p"] < 0.05:
        print("  ⭐ La periodicite de nos cartes N'EST PAS ce qu'une surface sans feuille")
        print("     produit. Le controle dur de `09` §2 est passe.")
        print()
        print("  ⚠ et sa fragilite, qui doit se lire AVEC le p :")
        for nom, val in r.get("fragilite", {}).items():
            print(f"    {nom.replace('_', ' '):46} p = {val:.4f}"
                  + ("" if val < 0.05 else "   ⚠ renverse"))
        print("    -> " + ("le resultat RESISTE a une fenetre dans les deux sens"
                           if r.get("resiste_a_une_fenetre")
                           else "UNE fenetre suffirait a le renverser"))
    else:
        print("  ⚠ Non significatif. Ce n'est pas « les deux se valent » : c'est que")
        print("    l'ecart n'est pas etabli a ce nombre de fenetres.")


def verifier() -> int:
    """L'instrument peut-il rendre la mauvaise réponse ?"""
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    releve = {"cartes": [
        {"carte": "ink_a", "rouleau": "nos_cartes", "fenetres_periodiques": 2, "fenetres": 3},
        {"carte": "ink_b", "rouleau": "nos_cartes", "fenetres_periodiques": 1, "fenetres": 4},
        {"carte": "ink_a", "rouleau": "controle_melange", "fenetres_periodiques": 0,
         "fenetres": 3},
        {"carte": "etranger", "rouleau": "nos_cartes", "fenetres_periodiques": 9,
         "fenetres": 9},
    ]}
    v("les cartes nommees sont sommees", compter(releve, ("ink_a", "ink_b")) == (3, 7),
      str(compter(releve, ("ink_a", "ink_b"))))
    # ⚠⚠ LES DEUX SONDES QUI COMPTENT : ni le controle par melange, ni une carte etrangere
    # au rouleau ne doivent entrer dans la somme. La seconde est le piege reellement paye
    # sur le test groupe de `60`, ou le temoin positif gonflait le sujet de moitie.
    v("le controle par melange n'entre pas dans la somme",
      compter(releve, ("ink_a",)) == (2, 3), str(compter(releve, ("ink_a",))))
    v("une carte etrangere au rouleau n'y entre pas non plus",
      compter(releve, ("ink_a", "ink_b")) != (12, 16))
    v("une carte absente ne rend rien", compter(releve, ("inconnue",)) == (0, 0))

    # -- controle_dur : le sens, la puissance, et le cas nul.
    fort = controle_dur(
        {"cartes": [{"carte": "x", "rouleau": "nos_cartes",
                     "fenetres_periodiques": 8, "fenetres": 12}]},
        {"cartes": [{"carte": "y", "rouleau": "nos_cartes",
                     "fenetres_periodiques": 0, "fenetres": 8}]})
    # ⚠ On force les noms pour la sonde, sinon rien n'est compte.
    import encre.temoin_contre_nos_cartes as moi
    garde_a, garde_b = moi.CARTES_DU_ROULEAU, moi.TEMOINS_NEGATIFS
    moi.CARTES_DU_ROULEAU, moi.TEMOINS_NEGATIFS = ("x",), ("y",)
    try:
        fort = moi.controle_dur(
            {"cartes": [{"carte": "x", "rouleau": "nos_cartes",
                         "fenetres_periodiques": 8, "fenetres": 12}]},
            {"cartes": [{"carte": "y", "rouleau": "nos_cartes",
                         "fenetres_periodiques": 0, "fenetres": 8}]})
        v("un ecart franc rend un p significatif", fort["p"] is not None and fort["p"] < 0.05,
          str(fort["p"]))
        v("... et la table est dans l'ordre declare", fort["table"] == [8, 4, 0, 8],
          str(fort["table"]))
        egal = moi.controle_dur(
            {"cartes": [{"carte": "x", "rouleau": "nos_cartes",
                         "fenetres_periodiques": 4, "fenetres": 8}]},
            {"cartes": [{"carte": "y", "rouleau": "nos_cartes",
                         "fenetres_periodiques": 4, "fenetres": 8}]})
        v("deux echantillons identiques ne sont pas significatifs", egal["p"] > 0.05,
          str(egal["p"]))
        # ⚠⚠ LE SENS : un temoin PLUS periodique que le sujet ne doit surtout pas passer.
        inverse = moi.controle_dur(
            {"cartes": [{"carte": "x", "rouleau": "nos_cartes",
                         "fenetres_periodiques": 0, "fenetres": 8}]},
            {"cartes": [{"carte": "y", "rouleau": "nos_cartes",
                         "fenetres_periodiques": 8, "fenetres": 12}]})
        v("un temoin PLUS periodique que le sujet n'est pas un succes",
          inverse["p"] > 0.05, str(inverse["p"]))
        maigre = moi.controle_dur(
            {"cartes": [{"carte": "x", "rouleau": "nos_cartes",
                         "fenetres_periodiques": 8, "fenetres": 12}]},
            {"cartes": [{"carte": "y", "rouleau": "nos_cartes",
                         "fenetres_periodiques": 0, "fenetres": 3}]})
        v("moins de six fenetres de temoin est declare sans puissance",
          maigre["assez_de_fenetres"] is False, str(maigre))
        v("... et six en a", moi.controle_dur(
            {"cartes": [{"carte": "x", "rouleau": "nos_cartes",
                         "fenetres_periodiques": 8, "fenetres": 12}]},
            {"cartes": [{"carte": "y", "rouleau": "nos_cartes",
                         "fenetres_periodiques": 0, "fenetres": 6}]})["assez_de_fenetres"])
        # ⚠⚠ La fragilite doit exister ET pouvoir dire non. Un ecart franc y resiste ;
        # un ecart frole ne doit PAS etre annonce comme resistant.
        v("un ecart franc resiste a une fenetre", fort["resiste_a_une_fenetre"] is True,
          str(fort["fragilite"]))
        frole = moi.controle_dur(
            {"cartes": [{"carte": "x", "rouleau": "nos_cartes",
                         "fenetres_periodiques": 8, "fenetres": 12}]},
            {"cartes": [{"carte": "y", "rouleau": "nos_cartes",
                         "fenetres_periodiques": 1, "fenetres": 7}]})
        v("... et un ecart frole ne resiste pas", frole["resiste_a_une_fenetre"] is False,
          str(frole["fragilite"]))
        v("... et la fragilite nomme les trois deplacements",
          len(frole["fragilite"]) == 3, str(list(frole["fragilite"])))
        vide = moi.controle_dur({"cartes": []}, {"cartes": []})
        v("un relevé vide ne rend pas de p", vide["p"] is None, str(vide))
    finally:
        moi.CARTES_DU_ROULEAU, moi.TEMOINS_NEGATIFS = garde_a, garde_b

    v("le temoin positif de Scroll 1 est exclu du sujet",
      "ink_segment_complet" not in CARTES_DU_ROULEAU)
    v("les deux temoins negatifs sont nommes", len(TEMOINS_NEGATIFS) == 2)

    print(f"{'ALL PASS' if echecs == 0 else 'ECHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--sujet", type=Path, default=SUJET)
    p.add_argument("--temoin", type=Path, default=TEMOIN)
    p.add_argument("--json", type=Path)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    for f in (a.sujet, a.temoin):
        if not f.is_file():
            print(f"relevé absent : {f}", file=sys.stderr)
            return 2
    r = controle_dur(json.loads(a.sujet.read_text(encoding="utf-8")),
                     json.loads(a.temoin.read_text(encoding="utf-8")))
    rapporter(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\n→ {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
