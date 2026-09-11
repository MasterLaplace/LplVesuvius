#!/usr/bin/env python3
"""Où peut-on MESURER si le modèle lit — et pourquoi ce n'est nulle part sur un rouleau.

⚠⚠⚠ POURQUOI CE FICHIER EXISTE. `59` §« ce qui reste » demande un **discriminant** : ce qui
sépare un objet où le modèle lit d'un objet où il ne lit pas. Chercher un discriminant suppose
qu'on sache mesurer la qualité **des deux côtés**. Or mesurer la qualité demande une vérité
terrain, et ce fichier établit, par énumération, que la vérité terrain n'existe **sur aucun
rouleau atteignable**.

  ⭐⭐⭐ Le partage est net, et il explique dix documents de ce dépôt d'un coup :

    fragment  → étiquettes publiées, modèle PAS entraîné dessus   → **mesurable**
    Scroll 1  → étiquettes publiées, et c'est le jeu D'ENTRAÎNEMENT → mesurer n'y prouve rien
    tout rouleau du prix → **aucune étiquette publiée**            → non mesurable

Donc « le modèle lit-il sur un rouleau qu'il n'a pas vu ? » n'a **pas de réponse mesurable**
avec les données atteignables. Toute affirmation de ce dépôt sur un rouleau passe par σ ou par
une comparaison à un rendu publié — et [`65`](../../docs/archive/65_ce_que_sigma_ne_dit_pas.md) vient
de montrer que σ ne prédit pas la qualité mesurée.

⚠⚠ Ce n'est PAS un échec de recherche, c'est une propriété du corpus publié, et elle se
re-vérifie : le mode réseau relit le dépôt public et refait l'inventaire. Si quelqu'un publie
un jour des étiquettes sur un rouleau, cette commande le dira.

⚠ Ce que ce fichier N'ÉTABLIT PAS : que le modèle ne lise pas sur un rouleau. Il établit qu'on
ne peut pas le mesurer. Les deux sont différents, et les confondre serait exactement le genre
de conclusion que ce dépôt refuse.

⚠⚠⚠ PORTÉE, ET ELLE A ÉTÉ PRISE POUR UNE CONCLUSION (corrigé le 2026-09-02). Ce fichier
interroge **cinq rouleaux nommés**, et son « zéro mesurable » vaut de ces cinq — pas du corpus.
`68` §4 montre que `PHerc0139`, qui n'en est pas, publie le régime du prix ET le régime de
production **recalés l'un sur l'autre**, sur un rouleau dont le titre est transcrit et publié ;
et que les trois fragments de supervision du papier font de même avec une vérité terrain
infrarouge. Le relevé est dans `la_case_vide.py`. **À relancer sur le corpus entier.**

Usage :
    uv run python src/encre/ou_la_verite_existe.py --verifier
    uv run python src/encre/ou_la_verite_existe.py --json docs/mesures/ou_la_verite_existe.json
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]

SEAU = "https://vesuvius-challenge-open-data.s3.amazonaws.com"
FRAGMENTS = "https://dl.ash2txt.org/fragments"

ROULEAUX = ("PHerc1447", "PHerc0172", "PHerc1667", "PHerc0051", "Scroll1")
"""Les rouleaux interrogés par force brute.

⚠⚠⚠ **CETTE LISTE EST UN ANGLE MORT, constaté le 2026-08-29 sur une remarque de l'auteur**
(« il y a 53 rouleaux scannés disponibles, non ? »). Elle en nomme **cinq** ; le dépôt en
publie **45**. J'ai écrit une liste à la main, l'ai interrogée par force brute, et l'ai
appelée « inventaire » — exactement la faute que `59` a déjà payée avec
`campagnes_de_scan.py`, qui n'interrogeait qu'un des deux layouts. **Troisième occurrence.**

⭐ Le remède existait et se lit en une requête :
[`corpus_par_energie.py`](corpus_par_energie.py) lit `metadata.min.json`, l'index que le dépôt
publie — 45 échantillons, 67 scans, chacun avec son énergie, sa résolution et la liste de ce
qui existe par segment. Le catalogue n'était pas à construire, il était à lire.

⚠ Cette liste-ci est **conservée** parce que ce fichier pose une question différente (où
existe une vérité terrain) et que sa conclusion — zéro rouleau mesurable — a été **confirmée
sur les 45** par l'index : aucun type d'artefact du dépôt n'est une étiquette d'encre. Mais
elle doit passer par l'index le jour où on l'étend."""

LOTS_DE_FRAGMENTS = ("Frag1", "Frag2", "Frag3", "Frag4", "Frag5", "Frag6")

MOTIF_VERITE = re.compile(r"inklabels|ground.?truth|/labels/", re.I)
"""Ce à quoi ressemble une vérité terrain publiée.

⚠⚠ ET CE QUI N'EN EST PAS UNE : `ink-detection/…timesformer_scroll5_july_retreat….tif` est
une **sortie de modèle**, pas une étiquette. Le motif ne la matche pas, et c'est délibéré —
prendre une prédiction pour une vérité ferait mesurer un modèle contre un autre modèle, ce qui
donnerait un chiffre élevé et vide de sens. Mesuré : `PHerc0172` publie quatre de ces fichiers
et **zéro** étiquette.
"""

ENTRAINE_SUR = ("Scroll1",)
"""Les objets sur lesquels `timesformer_GP_scroll1` a été entraîné.

⚠⚠ Une AUC mesurée sur du déjà-vu ne dit rien de ce que le modèle ferait ailleurs. C'est
pourquoi « Scroll 1 a des étiquettes » ne rend pas Scroll 1 mesurable : il faut les deux,
des étiquettes **et** l'absence d'entraînement dessus.

⚠ Pour les fragments, `63` §3 note qu'on ne peut pas le vérifier depuis ici — ils sont
probablement hors entraînement (jeu du concours **antérieur**), et la réserve ne va que dans
un sens : une AUC *basse* sur du déjà-vu serait encore plus mauvaise.
"""


def _lister(url: str, timeout: float = 40.0) -> str:
    """Le corps d'une requête, ou une chaîne vide — jamais une exception."""
    try:
        p = subprocess.run(["curl", "-s", "--max-time", str(int(timeout)), url],
                           capture_output=True, text=True, check=False)
        return p.stdout or ""
    except OSError:
        return ""


def cles_du_seau(prefixe: str, maximum: int = 1000, timeout: float = 40.0) -> list[str]:
    """Les clés d'un préfixe du dépôt public."""
    corps = _lister(f"{SEAU}/?list-type=2&prefix={prefixe}&max-keys={maximum}", timeout)
    return [l for l in corps.replace("<", "\n").splitlines() if l.startswith("Key>")]


def verites_dans(cles: list[str]) -> list[str]:
    """Celles des clés qui sont une vérité terrain — jamais une sortie de modèle."""
    return [k[4:] for k in cles if MOTIF_VERITE.search(k)]


def classer(nom: str, verites: int, entraine: bool) -> str:
    """Le statut d'un objet vis-à-vis d'une mesure de qualité.

    ⚠⚠ Trois états, pas deux, et c'est tout l'intérêt : « pas de vérité » et « vérité mais
    entraîné dessus » sont deux impossibilités **différentes**, et les fondre en une seule
    ferait croire qu'il suffirait de publier des étiquettes sur Scroll 1 pour débloquer la
    question. Ça ne suffirait pas.
    """
    if entraine:
        return "entraine_dessus"
    return "mesurable" if verites > 0 else "sans_verite"


def inventaire(timeout: float = 40.0) -> dict:
    """L'inventaire réel, relu depuis les deux dépôts."""
    objets = []
    for r in ROULEAUX:
        cles = cles_du_seau(f"{r}/", timeout=timeout)
        v = verites_dans(cles)
        objets.append({"objet": r, "genre": "rouleau", "cles_vues": len(cles),
                       "verites": len(v), "exemples": v[:2],
                       "entraine_dessus": r in ENTRAINE_SUR,
                       "statut": classer(r, len(v), r in ENTRAINE_SUR)})
    for f in LOTS_DE_FRAGMENTS:
        corps = _lister(f"{FRAGMENTS}/{f}/", timeout)
        volpkg = re.findall(r">([A-Za-z0-9_.-]+\.volpkg)/<", corps)
        surfaces = []
        if volpkg:
            travail = _lister(f"{FRAGMENTS}/{f}/{volpkg[0]}/working/", timeout)
            surfaces = re.findall(r">([A-Za-z0-9_.-]*exposed_surface)/<", travail)
        objets.append({"objet": f, "genre": "fragment", "cles_vues": len(surfaces),
                       "verites": len(surfaces), "exemples": surfaces[:2],
                       "entraine_dessus": f in ENTRAINE_SUR,
                       "statut": classer(f, len(surfaces), f in ENTRAINE_SUR)})
    return {"seau": SEAU, "fragments": FRAGMENTS, "objets": objets,
            "compte": compter(objets)}


def compter(objets: list[dict]) -> dict:
    """Combien d'objets par statut, et surtout : combien de ROULEAUX mesurables."""
    par = {}
    for o in objets:
        par[o["statut"]] = par.get(o["statut"], 0) + 1
    return {
        "par_statut": par,
        "rouleaux_mesurables": sum(1 for o in objets
                                   if o["genre"] == "rouleau" and o["statut"] == "mesurable"),
        "fragments_mesurables": sum(1 for o in objets
                                    if o["genre"] == "fragment" and o["statut"] == "mesurable"),
    }


def rapporter(inv: dict) -> None:
    """La sortie lisible, et la conséquence écrite en toutes lettres."""
    print(f"{'objet':12} {'genre':9} {'verites':>8} {'entraine':>9}  statut")
    for o in inv["objets"]:
        print(f"{o['objet']:12} {o['genre']:9} {o['verites']:8d} "
              f"{'oui' if o['entraine_dessus'] else 'non':>9}  {o['statut']}")
    c = inv["compte"]
    print()
    print(f"  rouleaux mesurables  : {c['rouleaux_mesurables']}")
    print(f"  fragments mesurables : {c['fragments_mesurables']}")
    if c["rouleaux_mesurables"] == 0:
        print()
        print("  ⚠⚠⚠ AUCUN rouleau ne porte de verite terrain exploitable.")
        print("      Donc « le modele lit-il sur un rouleau qu'il n'a pas vu ? » n'a pas de")
        print("      reponse MESURABLE ici — et chercher un discriminant entre rouleaux qui")
        print("      lisent et rouleaux qui ne lisent pas suppose justement cette mesure.")


def verifier() -> int:
    """Auto-test HORS LIGNE : la classification, sur des cas écrits à la main."""
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    # ⚠⚠ LE CONTROLE QUI PORTE LE FICHIER : une sortie de modele n'est PAS une verite.
    sorties = ["Key>PHerc0172/segments/x/ink-detection/PHerc0172-...-timesformer_scroll5"
               "_july_retreat-tile64-stride16.tif",
               "Key>PHerc0172/segments/x/ink-detection/downsampled/....-ds8.jpg"]
    v("une carte d'encre produite par un modele n'est pas une verite",
      verites_dans(sorties) == [], str(verites_dans(sorties)))
    vraies = ["Key>fragments/Frag1/working/54keV_exposed_surface/inklabels.png",
              "Key>x/labels/mask.png", "Key>y/ground_truth.png", "Key>z/ground-truth.png"]
    v("... alors qu'une etiquette publiee en est une", len(verites_dans(vraies)) == 4,
      str(verites_dans(vraies)))
    v("... et le motif ne matche pas n'importe quoi",
      verites_dans(["Key>a/volumes/0/.zarray", "Key>b/photos/x.jpg"]) == [])
    v("... et il rend la cle sans son prefixe",
      verites_dans(["Key>a/inklabels.png"]) == ["a/inklabels.png"])

    # -- classer : les trois etats, et surtout le troisieme.
    v("des etiquettes sans entrainement rendent mesurable",
      classer("Frag1", 3, False) == "mesurable")
    v("aucune etiquette rend sans_verite", classer("PHerc1447", 0, False) == "sans_verite")
    # ⚠⚠ Le cas qui distingue ce fichier d'un simple compteur d'etiquettes : Scroll 1 EN A,
    # et n'est pas mesurable pour autant. Fondre les deux impossibilites ferait croire qu'il
    # suffirait de publier des etiquettes sur Scroll 1.
    v("des etiquettes AVEC entrainement ne rendent PAS mesurable",
      classer("Scroll1", 42, True) == "entraine_dessus")
    v("... et l'entrainement l'emporte meme sans etiquette",
      classer("Scroll1", 0, True) == "entraine_dessus")

    # -- compter : le chiffre qui porte la conclusion.
    faux = [
        {"objet": "R1", "genre": "rouleau", "statut": "sans_verite"},
        {"objet": "R2", "genre": "rouleau", "statut": "entraine_dessus"},
        {"objet": "F1", "genre": "fragment", "statut": "mesurable"},
        {"objet": "F2", "genre": "fragment", "statut": "mesurable"},
    ]
    c = compter(faux)
    v("aucun rouleau mesurable est compte comme zero", c["rouleaux_mesurables"] == 0, str(c))
    v("... et les fragments mesurables sont comptes", c["fragments_mesurables"] == 2, str(c))
    v("... et les statuts sont totalises",
      c["par_statut"] == {"sans_verite": 1, "entraine_dessus": 1, "mesurable": 2}, str(c))
    # ⚠ Le controle qui peut echouer : si un rouleau devenait mesurable, le compte doit BOUGER.
    faux2 = faux + [{"objet": "R3", "genre": "rouleau", "statut": "mesurable"}]
    v("un rouleau mesurable ferait bouger le compte",
      compter(faux2)["rouleaux_mesurables"] == 1, str(compter(faux2)))

    v("les listes d'objets sont ecrites, pas decouvertes",
      len(ROULEAUX) >= 5 and len(LOTS_DE_FRAGMENTS) == 6)
    v("Scroll 1 est declare comme jeu d'entrainement", "Scroll1" in ENTRAINE_SUR)

    print(f"{'ALL PASS' if echecs == 0 else 'ECHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    p.add_argument("--timeout", type=float, default=40.0)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    inv = inventaire(a.timeout)
    rapporter(inv)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(inv, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\n→ {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
