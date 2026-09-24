"""`vesuve` : un programme, un pipeline par prix.

    vesuve formules [--markdown]          le formulaire : chaque équation, son fait, sa source
    vesuve grand-prize   [options]        dérouler automatiquement, et dire jusqu'où
    vesuve progress      [options]        auditer un segment publié : où a-t-il changé de spire ?
    vesuve first-letters [options]        une zone de 4 cm², rendue, encrée, et ses témoins
    vesuve paris4-title  [options]        chercher le titre de Scroll 1 là où finit le texte
    vesuve demo                           les quatre, hors ligne, sur les données embarquées et locales

Chaque pipeline écrit `rapport.json` et `rapport.md` dans son dossier de sortie, et rend 0 quand il est
allé au bout de ce qu'il sait faire, 2 quand il s'est arrêté (la raison est dans le rapport), 1 sur une
erreur d'usage. Le journal va sur la sortie d'erreur ; `VESUVE_JOURNAL=DEBUG` le rend bavard.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from vesuve import __version__
from vesuve.journal import Journal


def _formules(a) -> int:
    from vesuve.formulaire import LE_FORMULAIRE
    if a.markdown:
        sys.stdout.write(formulaire_en_markdown())
        return 0
    for e in LE_FORMULAIRE.values():
        print(f"[{e.id:>4}] {e.etage:<3} {e.nom} ({e.fait})\n       {e.latex}\n       {e.enonce}")
    return 0


def formulaire_en_markdown() -> str:
    """Le formulaire rendu pour GitHub, DÉRIVÉ du code : `vesuve formules --markdown > FORMULAIRE.md`."""
    from vesuve.formulaire import LE_FORMULAIRE
    lignes = ["# Le formulaire", "",
              "*Généré par `vesuve formules --markdown` depuis `vesuve/formulaire.py` : ne pas éditer à la main.*", "",
              "Chaque équation que le logiciel applique, l'étage du pipeline où elle sert, le fait du registre de "
              "LplVesuvius qui la porte (`docs/rapports/REGISTRE_*.tsv`), et ce qui la calcule. Une équation "
              "marquée **noyau C** est une fonction de `noyau/include/vesuve.h`, vérifiée contre la fonction même "
              "du producteur de recherche ; les autres sont des règles de la procédure, en Python.", ""]
    etages = {"E2": "E2 — l'échelle", "B": "B — le budget de la nappe", "E4": "E4 — le treillis",
              "E5": "E5 — les trous", "E6": "E6 — le certificat", "E7": "E7 — juger sans vérité terrain",
              "E8": "E8 — l'encre, la règle graduée"}
    for cle, titre in etages.items():
        es = [e for e in LE_FORMULAIRE.values() if e.etage == cle]
        if not es:
            continue
        lignes += [f"## {titre}", ""]
        for e in es:
            qui = "noyau C" if e.calcul is not None else "règle de procédure"
            lignes += [f"### [{e.id}] {e.nom}", "", "$$", e.latex, "$$", "", e.enonce, "",
                       f"*Fait* `{e.fait}` · *source* {e.source} · **{qui}**", ""]
    return "\n".join(lignes)


def _grand_prize(a, journal) -> int:
    from vesuve.grand_prize.pipeline import lancer
    r = lancer(a.segment, Path(a.sortie), Path(a.cache), lire=a.lire, tours=a.tours, fils=a.fils,
               lectures=[Path(x) for x in a.lectures], juger=a.juger, encre=not a.sans_encre,
               surface=not a.sans_surface, journal=journal)
    return 2 if r.arrete else 0


def _progress(a, journal) -> int:
    from vesuve.progress.pipeline import lancer
    r = lancer(a.segment, Path(a.sortie), Path(a.cache), lectures=[Path(x) for x in a.lectures],
               juger=a.juger, journal=journal)
    return 2 if r.arrete else 0


def _first_letters(a, journal) -> int:
    from vesuve.first_letters.pipeline import lancer
    r = lancer(Path(a.couches), Path(a.surface), a.rouleau, Path(a.sortie), cote_mm=a.cote_mm,
               modele=Path(a.modele) if a.modele else None, carte=Path(a.carte) if a.carte else None,
               etiquettes=Path(a.etiquettes) if a.etiquettes else None, journal=journal)
    return 2 if r.arrete else 0


def _paris4_title(a, journal) -> int:
    from vesuve.paris4_title.pipeline import lancer
    r = lancer(Path(a.cartes), Path(a.sortie), Path(a.cache), maillages=Path(a.maillages) if a.maillages else None,
               journal=journal)
    return 2 if r.arrete else 0


def _demo(a, journal) -> int:
    from vesuve.demo import lancer
    return lancer(Path(a.sortie), Path(a.cache), journal)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="vesuve", description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    p.add_argument("--version", action="version", version=f"vesuve {__version__}")
    sous = p.add_subparsers(dest="verbe", required=True)

    f = sous.add_parser("formules", help="le formulaire")
    f.add_argument("--markdown", action="store_true", help="le rendre en Markdown (FORMULAIRE.md)")

    def commun(q, sortie):
        q.add_argument("--sortie", default=sortie, help=f"dossier de sortie (défaut {sortie})")
        q.add_argument("--cache", default="cache", help="cache des chunks et des fichiers du bucket (défaut cache)")

    g = sous.add_parser("grand-prize", help="dérouler automatiquement, et dire jusqu'où")
    g.add_argument("--segment", default="20230702185753", help="un segment embarqué (défaut 20230702185753)")
    g.add_argument("--lire", action="store_true", help="lire sur le bucket les bandes que la procédure demande")
    g.add_argument("--tours", type=int, default=6, help="tours de lecture au plus (défaut 6)")
    g.add_argument("--fils", type=int, default=16, help="lectures simultanées (défaut 16)")
    g.add_argument("--lectures", nargs="*", default=[], help="des bandes déjà lues, au format de la chaîne")
    g.add_argument("--juger", type=int, default=0, help="juger N chunks certifiés sur le bucket (défaut 0)")
    g.add_argument("--sans-encre", action="store_true", help="ne pas superposer la carte d'encre publiée")
    g.add_argument("--sans-surface", action="store_true", help="ne pas écrire la surface certifiée (55 Mo lus)")
    commun(g, "sorties/grand-prize")

    q = sous.add_parser("progress", help="auditer un segment publié : où a-t-il changé de spire ?")
    q.add_argument("--segment", default="20230702185753")
    q.add_argument("--lectures", nargs="*", default=[])
    q.add_argument("--juger", type=int, default=0)
    commun(q, "sorties/progress")

    fl = sous.add_parser("first-letters", help="une zone de 4 cm², rendue, encrée, et ses témoins")
    fl.add_argument("--couches", required=True, help="un dossier de couches NN.tif autour d'une surface")
    fl.add_argument("--surface", required=True, help="le tifxyz de cette surface")
    fl.add_argument("--rouleau", required=True, help="le rouleau, pour l'éligibilité et le régime (PHerc1447…)")
    fl.add_argument("--cote-mm", type=float, default=20.0, help="le côté de la zone, en mm (défaut 20 : 4 cm²)")
    fl.add_argument("--modele", default=None, help="le dossier du modèle d'encre (TimeSformer), optionnel")
    fl.add_argument("--carte", default=None, help="une carte d'encre déjà inférée (.npy, logits), de la forme de la pile")
    fl.add_argument("--etiquettes", default=None, help="les étiquettes d'entraînement du modèle, pour le recouvrement")
    commun(fl, "sorties/first-letters")

    t = sous.add_parser("paris4-title", help="chercher le titre de Scroll 1 là où finit le texte")
    t.add_argument("--cartes", required=True, help="le dossier des cartes d'encre publiées de PHercParis4 (wNNN-MMM)")
    t.add_argument("--maillages", default=None, help="le dossier des maillages des bandes (un tifxyz par segment)")
    commun(t, "sorties/paris4-title")

    d = sous.add_parser("demo", help="les quatre pipelines, sur les données embarquées et locales")
    commun(d, "sorties/demo")

    a = p.parse_args(argv)
    journal = Journal()
    if a.verbe == "formules":
        return _formules(a)
    return {"grand-prize": _grand_prize, "progress": _progress, "first-letters": _first_letters,
            "paris4-title": _paris4_title, "demo": _demo}[a.verbe](a, journal)


if __name__ == "__main__":
    raise SystemExit(main())
