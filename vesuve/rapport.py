"""Le rapport d'un pipeline : ce que chaque étage a fait, les équations qu'il a appliquées, et où il s'arrête.

Un rapport n'est pas un journal : il ne dit pas ce qui s'est passé seconde par seconde, il dit ce qu'on
peut conclure, étage par étage, et avec quoi. Trois règles :

1. **Chaque équation appliquée est enregistrée** avec ses entrées, sa valeur et le fait du registre qui la
   porte : on lit le rapport et on voit le formulaire à l'œuvre.
2. **Un étage qui ne peut pas conclure le dit**, avec sa raison, et il n'écrit jamais zéro à la place.
3. **Chaque exigence du prix a une ligne** : atteinte, non atteinte, ou non mesurée, et pourquoi. Ce qui
   n'est pas produit est nommé, pas omis.
"""
from __future__ import annotations

import json
import platform
import time
from contextlib import contextmanager
from pathlib import Path

import numpy as np

from vesuve import __version__, noyau
from vesuve.formulaire import equation

FAIT, ARRETE, SAUTE, PARTIEL = "fait", "arrêté", "sauté", "partiel"


def _jsonable(x):
    if isinstance(x, dict):
        return {str(k): _jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_jsonable(v) for v in x]
    if isinstance(x, np.generic):
        return x.item()
    if isinstance(x, float) and x != x:
        return None
    return x


class Etage:
    def __init__(self, ident: str, nom: str, barreau: str):
        self.donnees = {"id": ident, "nom": nom, "barreau": barreau, "etat": FAIT, "equations": [], "sorties": {}}

    def appliquer(self, ident: str, *args, **montrees):
        """Calcule une équation du formulaire et l'enregistre. `montrees` : les entrées à afficher."""
        e = equation(ident)
        if e.calcul is None:
            raise ValueError(f"{ident} est une règle de procédure : la noter avec `constater`")
        valeur = e.calcul(*args)
        self.donnees["equations"].append({"id": e.id, "nom": e.nom, "latex": e.latex, "fait": e.fait,
                                          "entrees": _jsonable(montrees or {"arguments": list(args)}),
                                          "valeur": _jsonable(valeur)})
        return valeur

    def constater(self, ident: str, valeur, **montrees) -> None:
        """Enregistre une équation calculée ailleurs (le certificat), avec ce qu'elle a rendu."""
        e = equation(ident)
        self.donnees["equations"].append({"id": e.id, "nom": e.nom, "latex": e.latex, "fait": e.fait,
                                          "entrees": _jsonable(montrees), "valeur": _jsonable(valeur)})

    def noter(self, **sorties) -> None:
        self.donnees["sorties"].update(_jsonable(sorties))

    def arreter(self, raison: str) -> None:
        self.donnees.update({"etat": ARRETE, "raison": raison})

    def sauter(self, raison: str) -> None:
        self.donnees.update({"etat": SAUTE, "raison": raison})

    def partiel(self, raison: str) -> None:
        self.donnees.update({"etat": PARTIEL, "raison": raison})


class Rapport:
    def __init__(self, prix: str, entrees: dict, journal=None):
        self.prix, self.journal = prix, journal
        self.debut = time.time()
        self.donnees = {"le_logiciel": f"vesuve {__version__}", "le_noyau": noyau.version(), "le_prix": prix,
                        "la_machine": f"{platform.system()} {platform.machine()} python {platform.python_version()}",
                        "le_run": getattr(journal, "run", None), "les_entrees": _jsonable(entrees),
                        "les_etages": [], "les_exigences": [], "larret": None}

    @contextmanager
    def etage(self, ident: str, nom: str, barreau: str = "B1"):
        e = Etage(ident, nom, barreau)
        t0 = time.monotonic()
        try:
            yield e
        finally:
            e.donnees["secondes"] = round(time.monotonic() - t0, 3)
            self.donnees["les_etages"].append(e.donnees)
            if self.journal is not None:
                self.journal.info("ETAGE", prix=self.prix, etage=ident, etat=e.donnees["etat"],
                                  secondes=e.donnees["secondes"])
            if e.donnees["etat"] == ARRETE and self.donnees["larret"] is None:
                self.donnees["larret"] = {"letage": ident, "la_raison": e.donnees["raison"]}

    @property
    def arrete(self) -> bool:
        return self.donnees["larret"] is not None

    def exigence(self, texte: str, etat: str, mesure: str, preuve: str = "") -> None:
        """Une exigence du prix : `atteinte`, `non atteinte`, `non mesurée` ou `sans objet`."""
        self.donnees["les_exigences"].append({"lexigence": texte, "letat": etat, "ce_qui_est_mesure": mesure,
                                              "la_preuve": preuve})

    def ecrire(self, dossier: Path) -> Path:
        dossier = Path(dossier)
        dossier.mkdir(parents=True, exist_ok=True)
        self.donnees["secondes"] = round(time.time() - self.debut, 2)
        (dossier / "rapport.json").write_text(json.dumps(_jsonable(self.donnees), ensure_ascii=False, indent=1))
        (dossier / "rapport.md").write_text(en_markdown(self.donnees))
        return dossier / "rapport.json"


def _valeur(v) -> str:
    if isinstance(v, float):
        return f"{v:.6g}"
    if isinstance(v, (list, tuple)) and len(v) <= 4:
        return ", ".join(_valeur(x) for x in v)
    return str(v)


def en_markdown(d: dict) -> str:
    """La vue lisible du rapport, DÉRIVÉE de `rapport.json` : on ne l'édite pas."""
    lignes = [f"# {d['le_prix']} — rapport", "",
              f"`{d['le_logiciel']}` · noyau `{d['le_noyau']}` · {d['la_machine']} · {d.get('secondes', '?')} s", ""]
    if d["larret"]:
        lignes += [f"> **Arrêté à l'étage {d['larret']['letage']}** : {d['larret']['la_raison']}", ""]
    lignes += ["## Les exigences du prix", "", "| exigence | état | ce qui est mesuré |", "|---|---|---|"]
    lignes += [f"| {x['lexigence']} | **{x['letat']}** | {x['ce_qui_est_mesure']} |" for x in d["les_exigences"]]
    lignes += ["", "## Les étages", ""]
    for e in d["les_etages"]:
        lignes += [f"### {e['id']} — {e['nom']} ({e['barreau']}) : {e['etat']}", ""]
        if e.get("raison"):
            lignes += [f"*{e['raison']}*", ""]
        for q in e["equations"]:
            entrees = ", ".join(f"{k} = {_valeur(v)}" for k, v in q["entrees"].items())
            lignes += [f"- **[{q['id']}] {q['nom']}** (`{q['fait']}`) : $`{q['latex']}`$", "",
                       f"  {entrees} → **{_valeur(q['valeur'])}**", ""]
        for k, v in e["sorties"].items():
            texte = json.dumps(v, ensure_ascii=False) if not isinstance(v, str) else v
            if len(texte) > 300:
                texte = texte[:300] + " …"
            lignes.append(f"- `{k}` : {texte}")
        lignes.append("")
    return "\n".join(lignes) + "\n"
