#!/usr/bin/env python3
"""Toute batterie qui existe est-elle LANCEE par `temoins.sh` ?

⚠⚠⚠ POURQUOI CE FICHIER EXISTE, ET CE N'EST PAS PARCE QUE LA GARDE MANQUAIT. `temoins.sh` la
porte deja : il balaie `src/*/*.py`, retient ceux qui declarent `--verifier`, et signale ceux
qu'aucune de ses lignes ne lance. Le probleme n'est pas son absence, c'est qu'elle **n'est
atteignable qu'en run COMPLET** — or le run complet prend trop longtemps pour tourner a chaque
tranche, et la consigne permanente est de ne lancer que les batteries touchees. Une batterie
neuve mais oubliee passe donc entre les deux : verte quand on la lance a la main, jamais lancee
autrement.

⭐ Ce fichier rend la MEME question repondable en une seconde, hors ligne. Une garde qu'on ne
peut pas se permettre de faire tourner est une garde qui ne garde rien.

⭐ C'est arrive le 2026-09-07 : `la_cellule_sait_elle_quelle_a_tort` a vecu deux tranches sans
etre enregistree, parce qu'un patch avait echoue en silence et que rien ne pouvait le dire a
moins de payer le run complet. Cette garde-ci coute une seconde.

⚠⚠ ET ELLE VERIFIE LES DEUX SENS. Une ligne de `temoins.sh` qui pointe vers un fichier disparu
est l'autre moitie du meme defaut : le run echoue au milieu, ou pire, le shell avale l'erreur et
le compte baisse sans que personne ne sache lequel manque.

⚠ Ce qui compte comme batterie : un module qui **se teste lui-meme**, donc qui declare
`--verifier` ET porte un `def verifier(`. Un module qui n'a que l'un des deux n'est pas une
batterie — c'est soit un drapeau mort, soit une fonction sans surface.

Usage :
    uv run python src/depot/batteries_enregistrees.py
    uv run python src/depot/batteries_enregistrees.py --verifier
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
TEMOINS = RACINE / "src" / "outils" / "temoins.sh"
SOURCES = RACINE / "src"
# ⚠ Les modules qui n'ont deliberement pas leur place dans le run complet, avec la raison. Une
# exemption sans raison ecrite est une batterie qu'on a cesse de lancer sans le decider.
EXEMPTES = {
    "src/depot/lplv.py": "point d'entree des verbes : il LANCE les autres, il n'est pas lance",
}


def batteries(racine: Path = SOURCES, base: Path | None = None) -> list[str]:
    """Les modules qui se testent eux-memes, en chemins relatifs a `base`.

    ⚠ `base` existe pour que la fixture du controle puisse vivre ailleurs que dans le depot :
    sans lui, la garde ne serait exercable que sur elle-meme, ce qui est exactement le genre de
    controle qui ne peut pas echouer.
    """
    base = (RACINE if base is None else base)
    out = []
    for f in sorted(racine.rglob("*.py")):
        if "__pycache__" in f.parts:
            continue
        t = f.read_text(errors="ignore")
        if '"--verifier"' in t and "def verifier(" in t:
            out.append(str(f.relative_to(base)))
    return out


def lancees(temoins: Path = TEMOINS) -> list[str]:
    """Les chemins que `temoins.sh` lance, extraits de ses seules lignes `run`.

    ⚠⚠ LES COMMENTAIRES SONT ECARTES, et ce n'est pas une precaution theorique : la premiere
    version lisait tout le fichier et a rapporte `src/famille/x.py` comme ligne pointant vers un
    fichier disparu — or c'est un chemin d'EXEMPLE dans un commentaire qui explique justement un
    motif de recherche. Une garde qui accuse un commentaire est une garde qu'on apprend a
    ignorer.
    """
    if not temoins.is_file():
        return []
    out = []
    for ligne in temoins.read_text().splitlines():
        nu = ligne.lstrip()
        if not nu.startswith("run "):
            continue
        out += re.findall(r'\$ROOT/(src/[^\s"]+\.py)', ligne)
    return out


def mesurer(racine: Path = SOURCES, temoins: Path = TEMOINS) -> dict:
    """Les batteries oubliees, et les lignes qui pointent vers rien."""
    toutes = batteries(racine)
    prises = set(lancees(temoins))
    oubliees = [b for b in toutes if b not in prises and b not in EXEMPTES]
    fantomes = sorted({c for c in prises if not (RACINE / c).is_file()})
    return dict(batteries=len(toutes), lancees=len(prises),
                oubliees=oubliees, fantomes=fantomes,
                exemptees={k: v for k, v in EXEMPTES.items() if k in toutes})


def verifier() -> int:
    import tempfile  # noqa: PLC0415

    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    with tempfile.TemporaryDirectory() as d:
        r, t = Path(d) / "src", Path(d) / "t.sh"
        (r / "z").mkdir(parents=True)
        # ⚠⚠ LA FIXTURE PORTE LES QUATRE CAS, et c'est ce qui rend la garde capable d'echouer :
        # une batterie lancee, une OUBLIEE, un module qui n'en est pas une, et une ligne qui
        # pointe vers rien. Une fixture ou tout va bien ne prouverait que l'absence de plantage.
        (r / "z" / "prise.py").write_text('"--verifier"\ndef verifier(): pass\n')
        (r / "z" / "oubliee.py").write_text('"--verifier"\ndef verifier(): pass\n')
        (r / "z" / "pas_une.py").write_text('"--verifier"\n# aucun def verifier\n')
        (r / "z" / "moitie.py").write_text("def verifier(): pass\n# aucun drapeau\n")
        t.write_text('run "a" python "$ROOT/src/z/prise.py" --verifier\n'
                     'run "b" python "$ROOT/src/z/disparue.py" --verifier\n')

        vues = batteries(r, base=Path(d))
        v("un module qui déclare --verifier ET porte def verifier est une batterie",
          "src/z/prise.py" in vues, str(vues))
        noms = {Path(y).name for y in vues}
        v("... et un module qui n'a que le drapeau n'en est pas une",
          "pas_une.py" not in noms, str(sorted(noms)))
        v("... ni un module qui n'a que la fonction", "moitie.py" not in noms)
        v("... les deux vraies batteries sont vues", noms == {"prise.py", "oubliee.py"},
          str(sorted(noms)))
        pris = lancees(t)
        v("les chemins lancés sont extraits des lignes run", len(pris) == 2, str(pris))

    r2 = mesurer()
    v("la garde tourne sur le dépôt réel",
      r2["batteries"] > 100 and r2["lancees"] > 100,
      f"{r2['batteries']} batteries · {r2['lancees']} lancées")
    # ⭐⭐⭐ LE VERDICT : aucune batterie oubliée, aucune ligne fantôme. C'est cette garde-là qui
    # remplace le run complet pour la seule question qu'un run complet répondait tout seul.
    v("aucune batterie n'est oubliée par temoins.sh", not r2["oubliees"],
      str(r2["oubliees"][:5]) if r2["oubliees"] else f"{r2['batteries']} vérifiées")
    v("... et aucune ligne de temoins.sh ne pointe vers un fichier disparu",
      not r2["fantomes"], str(r2["fantomes"][:5]))
    # ⚠ UNE EXEMPTION SANS RAISON ÉCRITE est une batterie qu'on a cessé de lancer sans le décider.
    v("... et toute exemption porte sa raison",
      all(isinstance(x, str) and x for x in EXEMPTES.values()), str(sorted(EXEMPTES)))

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer()
    print(f"{r['batteries']} batteries qui se testent · {r['lancees']} chemins lancés par "
          f"temoins.sh")
    for k, why in r["exemptees"].items():
        print(f"  exemptée : {k} — {why}")
    if r["oubliees"]:
        print(f"\n⛔ {len(r['oubliees'])} batterie(s) OUBLIÉE(S) par temoins.sh :")
        for x in r["oubliees"]:
            print(f"    {x}")
    if r["fantomes"]:
        print(f"\n⛔ {len(r['fantomes'])} ligne(s) qui pointent vers un fichier disparu :")
        for x in r["fantomes"]:
            print(f"    {x}")
    if not r["oubliees"] and not r["fantomes"]:
        print("  ✅ toute batterie est lancée, et toute ligne pointe vers un fichier")
    return 1 if (r["oubliees"] or r["fantomes"]) else 0


if __name__ == "__main__":
    sys.exit(main())
