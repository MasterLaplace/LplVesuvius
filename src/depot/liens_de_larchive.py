#!/usr/bin/env python3
"""Réparer les liens RELATIFS des documents archivés — et refuser s'il en reste un cassé.

⚠⚠ POURQUOI CE FICHIER EXISTE, ET POURQUOI `deplacer.py` NE SUFFIT PAS. `deplacer` réécrit les
citations du chemin d'un fichier qui bouge (`docs/07_x.md` → `docs/archive/07_x.md`), partout
dans l'arbre. Il ne touche pas aux liens que le fichier déplacé porte VERS ce qui n'a pas bougé :
`](images/x.png)` écrit depuis `docs/` désigne `docs/images/x.png` ; le même lien lu depuis
`docs/archive/` désigne `docs/archive/images/x.png`, qui n'existe pas. Cent quinze documents,
deux cent trois images, trente-deux mesures, soixante scripts. Un `sed` par motif ferait le
travail en apparence et laisserait en silence chaque cas qu'aucun motif n'avait prévu.

⭐ AUCUNE RÈGLE PAR MOTIF. Chaque lien est RÉSOLU depuis l'endroit où le document vivait — ce
que l'auteur voulait désigner — puis RÉEXPRIMÉ depuis l'endroit où il vit maintenant. Si la
cible a bougé elle aussi, on suit son déplacement. Trois candidats pour la résolution, dans
l'ordre : l'ancien dossier du document (le sens de l'auteur), la racine du dépôt (les liens
« racine » de `00_carnet_de_bord` et de `HANDOFF`, que `deplacer` a réécrits en
`docs/archive/…` et qui ne se lisent donc plus depuis `docs/archive/`), et le nouveau dossier
(un lien déjà juste). Le premier qui existe gagne.

⚠ La carte du déplacement n'est PAS un fichier : elle est DÉRIVÉE de la disposition.
`docs/archive/X.md` vivait dans `docs/X.md`, `docs/archive/HANDOFF.md` à la racine,
`docs/archive/registres/X` dans `docs/registres/X`. Un JSON de carte serait une seconde
description de la même chose, libre de dériver ; `git log --follow` porte déjà l'historique.

⭐ L'INVARIANT est celui de `deplacer` : après application, `liens_casses` — l'outil qui
existe déjà pour ça, IMPORTÉ et jamais réécrit — doit rendre zéro lien cassé dans
`docs/archive/`, hors citations verbatim. Un lien qui était déjà cassé AVANT le déplacement
est laissé tel quel et COMPTÉ : inventer une cible n'est pas réparer.

⚠⚠ PIÈGE PAYÉ LE 2026-09-11, et il concerne ce fichier même. `deplacer.py` réécrit toute
occurrence de `HANDOFF.md` non précédée d'un caractère de mot — y compris celle qui termine
`docs/archive/HANDOFF.md`, son propre chemin d'arrivée. Ce fichier, non suivi par git au moment
du déménagement, a été réécrit DEUX fois (un premier passage mal cartographié, puis le bon) et
sa fixture s'est retrouvée avec `docs/archive/docs/archive/docs/archive/HANDOFF.md/…`. Il a été
restauré depuis le transcript. Le risque ne se reproduit pas tant que `HANDOFF.md` n'existe
plus à la racine — `plan_depuis` refuse un fichier absent — mais un fichier NEUF qui nomme un
chemin en cours de déménagement doit être commité AVANT qu'on lance `deplacer --ecrire`.

⚠ Par défaut ce fichier ne fait RIEN d'autre que rapporter. `--ecrire` applique.

Usage :
    uv run python src/depot/liens_de_larchive.py              # à blanc
    uv run python src/depot/liens_de_larchive.py --ecrire
    uv run python src/depot/liens_de_larchive.py --verifier
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
ARCHIVE = Path("docs") / "archive"

LIEN = re.compile(r"\]\(([^)\s<>]+)\)")
"""Un lien markdown `](cible)`. Les autolinks `<…>` et les blocs de code ne sont pas des
liens : le premier n'est jamais relatif, le second est du texte. ⚠ Le motif exclut l'espace,
donc `](a b)` — une cible avec titre — n'est pas lu : le dépôt n'en écrit pas, et le rater
vaut mieux qu'en couper un en deux."""

EXTERNES = ("http://", "https://", "mailto:", "#", "/")


def ancien_chemin(nouveau: Path) -> Path | None:
    """Où ce fichier vivait AVANT l'archivage — dérivé de la disposition, jamais listé.

    Rend `None` pour un fichier qui n'est pas dans `docs/archive/` : il n'a pas bougé.
    """
    try:
        rel = nouveau.relative_to(ARCHIVE)
    except ValueError:
        return None
    if rel == Path("HANDOFF.md"):
        return Path("HANDOFF.md")
    return Path("docs") / rel


def nouveau_chemin(ancien: Path) -> Path:
    """L'inverse : où un fichier de l'ancienne disposition vit maintenant, s'il a bougé."""
    if ancien == Path("HANDOFF.md"):
        return ARCHIVE / "HANDOFF.md"
    parties = ancien.parts
    if len(parties) >= 2 and parties[0] == "docs":
        if parties[1] == "registres":
            return ARCHIVE / "registres" / Path(*parties[2:])
        if len(parties) == 2 and ancien.suffix == ".md" and parties[1][:1].isdigit():
            return ARCHIVE / parties[1]
    return ancien


def _normaliser(p: Path) -> Path:
    """`docs/../src/x` → `src/x`, sans toucher au disque."""
    return Path(os.path.normpath(str(p)))


def resoudre(cible: str, ancien: Path, nouveau: Path, racine: Path) -> Path | None:
    """La cible RÉELLE d'un lien, relative à la racine — ou `None` si aucune lecture n'existe.

    ⚠ L'ordre des candidats est le sens : l'ancien dossier d'abord, parce que c'est ce que
    l'auteur écrivait ; la racine ensuite, pour les liens « racine » ; le nouveau dossier en
    dernier, pour ne jamais préférer un accident de disposition à l'intention.
    """
    nu = cible.split("#", 1)[0]
    if not nu:
        return None
    candidats = [ancien.parent / nu, Path(nu), nouveau.parent / nu]
    for c in candidats:
        c = _normaliser(c)
        c = nouveau_chemin(c)  # si la cible a bougé aussi, on la suit
        if (racine / c).exists():
            return c
    return None


def reecrire(texte: str, nouveau: Path, racine: Path) -> tuple[str, dict]:
    """Le texte réécrit et son bilan : liens vus, réécrits, déjà justes, laissés cassés."""
    ancien = ancien_chemin(nouveau)
    bilan = {"vus": 0, "reecrits": 0, "justes": 0, "casses": []}
    if ancien is None:
        return texte, bilan

    def remplacer(m: re.Match) -> str:
        cible = m.group(1)
        if cible.startswith(EXTERNES):
            return m.group(0)
        bilan["vus"] += 1
        reel = resoudre(cible, ancien, nouveau, racine)
        if reel is None:
            bilan["casses"].append(cible)
            return m.group(0)
        ancre = cible[len(cible.split("#", 1)[0]):]
        neuf = os.path.relpath(str(racine / reel), str(racine / nouveau.parent)) + ancre
        if neuf == cible:
            bilan["justes"] += 1
            return m.group(0)
        bilan["reecrits"] += 1
        return f"]({neuf})"

    return LIEN.sub(remplacer, texte), bilan


def fichiers_archives(racine: Path) -> list[Path]:
    return sorted(p.relative_to(racine) for p in (racine / ARCHIVE).rglob("*.md"))


def appliquer(racine: Path, ecrire: bool = False) -> dict:
    rapport = {"fichiers": 0, "touches": 0, "vus": 0, "reecrits": 0, "justes": 0,
               "casses": {}, "applique": ecrire}
    for rel in fichiers_archives(racine):
        texte = (racine / rel).read_text(encoding="utf-8", errors="replace")
        neuf, b = reecrire(texte, rel, racine)
        rapport["fichiers"] += 1
        for k in ("vus", "reecrits", "justes"):
            rapport[k] += b[k]
        if b["casses"]:
            rapport["casses"][str(rel)] = b["casses"]
        if b["reecrits"]:
            rapport["touches"] += 1
            if ecrire:
                (racine / rel).write_text(neuf, encoding="utf-8")
    return rapport


def casses_restants(racine: Path) -> list[tuple[str, str]]:
    """Ce que `liens_casses` — l'outil du dépôt — voit encore de cassé dans l'archive.

    ⭐ Importé, pas réécrit : une seconde définition de « lien cassé » finirait par ne plus
    être la même que celle qui garde le reste de l'arbre.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from liens_casses import liens_casses  # noqa: PLC0415
    cites: list = []
    out = []
    for f, cible, _corr in liens_casses(racine, cites):
        rel = Path(f).relative_to(racine) if Path(f).is_absolute() else Path(f)
        if str(rel).startswith(str(ARCHIVE)):
            out.append((str(rel), cible))
    return out


# ---------------------------------------------------------------------------

def verifier() -> int:
    import tempfile

    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        print(f"  {'ok  ' if ok else 'ECHEC'} {nom}" + (f"  — {detail}" if detail else ""))
        if not ok:
            echecs += 1

    print("liens de l'archive — batterie")
    v("l'ancien chemin d'un document archivé est dans docs/",
      ancien_chemin(ARCHIVE / "07_x.md") == Path("docs/07_x.md"))
    v("... HANDOFF vivait à la racine", ancien_chemin(ARCHIVE / "HANDOFF.md") == Path("HANDOFF.md"))
    v("... un registre vivait dans docs/registres/",
      ancien_chemin(ARCHIVE / "registres" / "f.md") == Path("docs/registres/f.md"))
    v("... et un fichier hors archive n'a pas bougé", ancien_chemin(Path("docs/rapports/x.md")) is None)
    v("l'inverse suit un document", nouveau_chemin(Path("docs/07_x.md")) == ARCHIVE / "07_x.md")
    v("... ne suit PAS une image", nouveau_chemin(Path("docs/images/a.png")) == Path("docs/images/a.png"))
    v("... ni un rapport", nouveau_chemin(Path("docs/rapports/R1.md")) == Path("docs/rapports/R1.md"))

    with tempfile.TemporaryDirectory() as d:
        r = Path(d)
        # L'arbre APRÈS déplacement, tel que `deplacer` le laisse : les fichiers ont bougé,
        # et les liens « racine » ont été réécrits en `docs/archive/…`.
        for p in ("docs/images", "docs/mesures", "docs/archive/registres", "src/nappe", "docs/rapports"):
            (r / p).mkdir(parents=True)
        (r / "docs/images/a.png").write_text("x")
        (r / "docs/mesures/m.json").write_text("{}")
        (r / "src/nappe/s.py").write_text("x")
        (r / "README.md").write_text("x")
        (r / "docs/archive/07_x.md").write_text("x")
        (r / "docs/archive/61_y.md").write_text(
            "![a](images/a.png) [m](mesures/m.json) [s](../src/nappe/s.py) "
            "[v](07_x.md#sec) [racine](docs/archive/07_x.md) [h](../docs/archive/HANDOFF.md) "
            "[r](../README.md) [ext](https://x.org/a) [anc](#ici) [mort](images/absente.png)")
        (r / "docs/archive/HANDOFF.md").write_text(
            "[d](docs/archive/07_x.md) [i](docs/images/a.png) [s](src/nappe/s.py) [rd](README.md)")
        (r / "docs/archive/registres/fiches.md").write_text(
            "[d](../07_x.md) [i](../images/a.png) [s](../../src/nappe/s.py)")

        rap = appliquer(r, ecrire=True)
        t = (r / "docs/archive/61_y.md").read_text()
        v("une image gagne un `../`", "](../images/a.png)" in t, t)
        v("une mesure aussi", "](../mesures/m.json)" in t)
        v("un script gagne un second `../`", "](../../src/nappe/s.py)" in t)
        v("un voisin archivé reste un voisin, ancre comprise", "](07_x.md#sec)" in t)
        v("un lien RACINE réécrit par deplacer redevient un voisin", "[racine](07_x.md)" in t)
        v("HANDOFF, réécrit par deplacer, redevient un voisin", "[h](HANDOFF.md)" in t)
        v("le README de la racine gagne deux `../`", "](../../README.md)" in t)
        v("un lien externe n'est pas touché", "](https://x.org/a)" in t)
        v("une ancre seule n'est pas touchée", "](#ici)" in t)
        # ⚠ Le cas qui distingue réparer d'inventer.
        v("un lien DÉJÀ cassé est laissé tel quel", "](images/absente.png)" in t)
        v("... et compté", rap["casses"].get("docs/archive/61_y.md") == ["images/absente.png"], str(rap["casses"]))
        h = (r / "docs/archive/HANDOFF.md").read_text()
        v("depuis HANDOFF : le document devient un voisin", "[d](07_x.md)" in h, h)
        v("... l'image remonte d'un cran", "[i](../images/a.png)" in h)
        v("... le script de deux", "[s](../../src/nappe/s.py)" in h)
        v("... le README de deux", "[rd](../../README.md)" in h)
        f = (r / "docs/archive/registres/fiches.md").read_text()
        v("depuis un registre : le document ne change pas", "[d](../07_x.md)" in f, f)
        v("... l'image gagne un cran", "[i](../../images/a.png)" in f)
        v("... le script aussi", "[s](../../../src/nappe/s.py)" in f)
        v("le rapport compte les fichiers touchés", rap["touches"] == 3, str(rap))
        # ⚠ Une seconde passe ne doit RIEN changer : l'opération est idempotente.
        rap2 = appliquer(r, ecrire=False)
        v("une seconde passe ne réécrit rien", rap2["reecrits"] == 0, str(rap2))

    print(f"\n{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--ecrire", action="store_true", help="APPLIQUE. Sans ça, rapport à blanc.")
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = appliquer(RACINE, ecrire=a.ecrire)
    print(f"{r['fichiers']} document(s) archivé(s) · {r['vus']} lien(s) relatif(s) vu(s) · "
          f"{r['reecrits']} réécrit(s) dans {r['touches']} fichier(s) · {r['justes']} déjà juste(s)")
    n_casses = sum(len(v) for v in r["casses"].values())
    if n_casses:
        print(f"  ⚠ {n_casses} lien(s) déjà cassé(s) AVANT l'archivage, laissé(s) tel(s) quel(s) "
              f"dans {len(r['casses'])} fichier(s) :")
        for f, cs in list(r["casses"].items())[:12]:
            print(f"     {f}: {', '.join(cs[:4])}{' …' if len(cs) > 4 else ''}")
    if a.ecrire:
        restants = casses_restants(RACINE)
        r["casses_apres_selon_liens_casses"] = restants
        print(f"  {'✅' if not restants else '⛔'} `liens_casses` voit {len(restants)} lien(s) cassé(s) "
              f"dans docs/archive/ après application")
        for f, c in restants[:12]:
            print(f"     {f} → {c}")
    else:
        print("  à blanc — relancer avec --ecrire")
    if a.json:
        a.json.write_text(json.dumps(r, indent=1, ensure_ascii=False), encoding="utf-8")
    return 0 if not (a.ecrire and r.get("casses_apres_selon_liens_casses")) else 3


if __name__ == "__main__":
    sys.exit(main())
