"""`vesuve demo` : les quatre pipelines d'affilée, et un tableau de ce que chacun a conclu.

Grand Prize et Progress tournent sur le segment embarqué, sans rien d'autre (le réseau n'ajoute que la carte
d'encre et la surface). First Letters et le titre de Paris 4 ont besoin de données que le logiciel n'embarque
pas (des piles de couches, des cartes d'encre) : on les lui donne avec `--donnees`, le dossier `data/` de
LplVesuvius, et sans lui ils sont sautés en le disant.
"""
from __future__ import annotations

from pathlib import Path

LES_ENTREES = {
    # ⚠ Le dossier lui-même et non `couches/1447_20250702235910`, qui est un lien vers un chemin ABSOLU de
    # l'hôte : monté dans un conteneur, il pointe dans le vide.
    "first-letters": {"couches": "couches/PHerc1447_complet",
                      "surface": "segments_officiels/20250702235910-auto_grown_20250702235910292",
                      "carte": "out/ink_PHerc1447_complet.npy",
                      "etiquettes": "repos/Vesuvius-Grandprize-Winner/all_labels"},
    "paris4-title": {"cartes": "encre/PHercParis4", "maillages": "paris4_bandes"},
}


def _ce_qui_manque(d: Path | None, entrees: dict) -> str | None:
    """None si tout est là ; sinon chaque entrée absente, par son nom, et si c'est un lien mort."""
    if d is None:
        return "donner --donnees <data/ de LplVesuvius>"
    manque = [f"{v}{' (lien mort)' if (d / v).is_symlink() else ''}" for v in entrees.values() if not (d / v).exists()]
    return ("absent de " + str(d) + " : " + ", ".join(manque)) if manque else None


def lancer(sortie: Path, cache: Path, journal, donnees: Path | None = None) -> int:
    from vesuve.first_letters.pipeline import lancer as first_letters
    from vesuve.grand_prize.pipeline import lancer as grand_prize
    from vesuve.paris4_title.pipeline import lancer as paris4_title
    from vesuve.progress.pipeline import lancer as progress
    lignes = []

    def noter(prix, r=None, raison=""):
        if r is None:
            lignes.append((prix, "sauté", raison))
            return
        ex = r.donnees["les_exigences"]
        atteintes = sum(1 for x in ex if x["letat"] == "atteinte")
        arret = r.donnees["larret"]
        lignes.append((prix, "arrêté à " + arret["letage"] if arret else "au bout",
                       f"{atteintes} exigences atteintes sur {len(ex)}"))

    noter("grand-prize", grand_prize(sortie=sortie / "grand-prize", cache=cache, journal=journal))
    noter("progress", progress(sortie=sortie / "progress", cache=cache, journal=journal))
    d = Path(donnees) if donnees else None
    e = LES_ENTREES["first-letters"]
    manque = _ce_qui_manque(d, e)
    if manque is None:
        noter("first-letters", first_letters(d / e["couches"], d / e["surface"], "PHerc1447", sortie / "first-letters",
                                             carte=d / e["carte"], etiquettes=d / e["etiquettes"], journal=journal))
    else:
        noter("first-letters", raison=manque)
    e = LES_ENTREES["paris4-title"]
    manque = _ce_qui_manque(d, e)
    if manque is None:
        noter("paris4-title", paris4_title(d / e["cartes"], sortie / "paris4-title", cache,
                                           maillages=d / e["maillages"], journal=journal))
    else:
        noter("paris4-title", raison=manque)
    print(f"{'prix':<14} {'issue':<16} ce qui est conclu")
    for prix, issue, quoi in lignes:
        print(f"{prix:<14} {issue:<16} {quoi}")
    print(f"\nles rapports : {sortie}/<prix>/rapport.md")
    return 0
