#!/usr/bin/env python3
"""Chaque image de `docs/` est-elle celle que son producteur rend AUJOURD'HUI ?

⚠⚠ POURQUOI CE FICHIER EXISTE. `images_des_docs.sh` vérifie qu'une image référencée **existe**,
et qu'aucune ne traîne sans référence. Ce sont de bonnes questions et ce ne sont pas celle-ci :
une image peut exister, être référencée, et **ne plus correspondre à ses données**.

Mesuré le 2026-08-26, en cherchant tout autre chose : **trois images** de `docs/` diffèrent de
ce que leur producteur rend. `51_appuis.png` a été commise le 23 août ; son entrée
`docs/mesures/appui_de_pente.json` a bougé le 24. L'image n'a jamais été refaite. Rien ne l'a dit, et
un lecteur ne peut pas le savoir : une figure périmée s'affiche exactement comme une figure à
jour.

  ⭐ C'est la même classe que la fraîcheur des cartouches embarquées, que le dépôt garde déjà —
    appliquée aux figures, qui sont ce qu'un lecteur regarde en premier.

⚠ Le contrôle **régénère** dans un dossier temporaire et compare les octets. Il ne touche
jamais `docs/images/` : dire qu'une image est périmée et la remplacer sont deux actes, et le
second appartient à qui écrit le document.

⚠ Une figure dont l'entrée manque est **impossible à juger**, pas périmée. Confondre les deux
ferait passer pour un défaut ce qui n'est qu'une donnée absente — et c'est ainsi qu'un contrôle
devient du bruit qu'on cesse de lire.

⚠ Coût mesuré : **1,6 s** pour les neuf figures régénérables du dépôt. C'est ce qui rend la
question posable à chaque batterie plutôt qu'une fois par an.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]


def figures(racine: Path = RACINE) -> list[Path]:
    """Les modules qui savent écrire une image, c'est-à-dire ceux qui déclarent `--sortie`."""
    out = []
    # ⚠⚠ `.venv` est ELAGUE : depuis que les environnements vivent avec leur code
    # (`src/xpu/.venv`), un parcours de `src/` traverse 8 885 fichiers de `site-packages`.
    # Le coût n'est pas le pire : un module de bibliothèque qui contiendrait `"--sortie"` et
    # `images/` serait pris pour une figure de ce dépôt.
    # ⚠⚠⚠ `src/depot/` est ÉLAGUÉ AUSSI, et pour une raison différente de `.venv` : une
    # batterie d'hygiène porte des **fixtures** — des chemins d'image écrits pour être
    # inexistants, parce que c'est ce que le contrôle négatif exige. Ce fichier-ci se
    # signalait ainsi lui-même comme « image absente : docs/images/y.png », soit un défaut
    # permanent, impossible à corriger et impossible à distinguer d'un vrai. C'est le piège
    # « une sonde qui scanne son propre fichier se matche elle-même », que ce dépôt a déjà
    # payé six fois — le remède est d'exclure la classe, pas de nommer ce fichier.
    for f in sorted((racine / "src").rglob("*.py")):
        if "__pycache__" in f.parts or ".venv" in f.parts or "depot" in f.parts:
            continue
        try:
            t = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if '"--sortie"' in t and "images/" in t:
            out.append(f)
    return out


def sortie_par_defaut(module: Path) -> Path | None:
    """L'image que ce module écrit quand on ne lui dit rien — lue dans sa déclaration."""
    import re
    t = module.read_text(encoding="utf-8", errors="replace")
    # ⚠ Le dépôt déclare sa sortie sous DEUX formes, et une seule regex n'en voyait qu'une —
    # 25 figures sur 36 passaient alors pour « sans sortie déclarée », donc pour non jugeables.
    # ⚠ Et la déclaration peut tenir sur deux lignes : chercher ligne à ligne les raterait.
    # ⚠⚠ Le premier motif nommait la constante « racine » en MINUSCULES, donc une figure
    # écrite avec la convention majuscule du dépôt (`RACINE`) passait pour « sans sortie
    # déclarée », c'est-à-dire pour non jugeable — silencieusement. La couverture d'un
    # garde-fou ne doit pas dépendre de l'orthographe d'une variable : tout identifiant
    # suivi d'un chemin `docs/images/` déclare une sortie, quel que soit son nom.
    # ⚠⚠ Et une TROISIEME orthographe, payee le 2026-08-29 : un chemin construit SEGMENT
    # par segment (`RACINE / "docs" / "images" / "x.png"`). La figure passait pour « sans
    # sortie declaree », donc pour non jugeable, exactement comme la casse de `racine`
    # l'avait fait avant. Meme lecon, troisieme costume : ce qu'on cherche est un chemin
    # d'image, pas une facon de l'ecrire.
    for motif in (r'default=\w+\s*/\s*"(docs/images/[^"]+)"',
                  r'default=Path\(\s*"(docs/images/[^"]+)"\s*\)',
                  r'default=Path\(__file__\)[^\n]*?/\s*"(docs/images/[^"]+)"',
                  r'default=\w+\s*/\s*"docs"\s*/\s*"images"\s*/\s*"([^"]+)"'):
        m = re.search(motif, t, re.S)
        if m:
            g = m.group(1)
            return RACINE / (g if g.startswith("docs/") else f"docs/images/{g}")
    return None


def empreinte(chemin: Path) -> str | None:
    try:
        return hashlib.sha256(chemin.read_bytes()).hexdigest()
    except OSError:
        return None


def arguments_declares(module: Path) -> list[str]:
    """Les drapeaux avec lesquels ce module écrit SON image publiée, lus dans son `Usage :`.

    ⚠⚠ POURQUOI CETTE FONCTION EXISTE, et le défaut qu'elle répare est de la pire espèce.
    Ce contrôle rejouait chaque figure **sans aucun argument**. Une figure dont la forme
    publiée demande un drapeau était donc régénérée dans une forme que **personne ne
    publie**, et l'image légitime était déclarée PÉRIMÉE. Mesuré le 2026-09-05 :
    `figure_le_nul_verso.py` publie son panorama des trois segments (`--tous`) et se voyait
    comparée au dessin d'un seul segment — verdict rouge, image parfaitement à jour.

      ⭐ Un faux positif est plus coûteux ici qu'un silence : il apprend à ne plus lire le
        contrôle, et le jour où une figure dérive vraiment, la ligne rouge ne se distingue
        pas de celle qu'on a pris l'habitude d'ignorer.

    ⚠ La ligne `--verifier` est écartée : c'est la batterie du module, pas son dessin.

    ⚠ `--sortie` est retiré de ce qui est rendu — le juge fournit le sien, vers un dossier
    temporaire. Le garder ferait écrire la figure dans `docs/images/`, c'est-à-dire ferait
    RÉPARER au contrôle ce qu'il a pour seul métier de CONSTATER.
    """
    import shlex
    t = module.read_text(encoding="utf-8", errors="replace")
    tete = t.split('"""')[1] if t.count('"""') >= 2 else ""
    if "Usage :" not in tete:
        return []
    bloc = tete.split("Usage :", 1)[1]
    # ⚠ Une invocation peut tenir sur plusieurs lignes, continuées par une barre inverse —
    # que la docstring écrit `\\` pour survivre à l'échappement de Python.
    plat = bloc.replace("\\\n", " ").replace("\\", " ")
    invocations = []
    for ligne in plat.splitlines():
        ligne = ligne.strip()
        if module.name not in ligne or "--verifier" in ligne:
            continue
        try:
            mots = shlex.split(ligne)
        except ValueError:
            continue
        for i, mot in enumerate(mots):
            if mot.endswith(module.name):
                invocations.append(mots[i + 1:])
                break
    if not invocations:
        return []

    def sans_sortie(mots: list[str]) -> tuple[list[str], str | None]:
        garde, cible, saute = [], None, False
        for i, mot in enumerate(mots):
            if saute:
                saute = False
                continue
            if mot == "--sortie":
                cible = mots[i + 1] if i + 1 < len(mots) else None
                saute = True
                continue
            if mot.startswith("--sortie="):
                cible = mot.split("=", 1)[1]
                continue
            garde.append(mot)
        return garde, cible

    # ⚠ On PRÉFÈRE l'invocation dont la sortie est celle qu'on va comparer. Sans ce filtre,
    # une figure qui documente deux dessins ferait juger l'image de l'un avec les arguments
    # de l'autre — un rouge qui ne veut rien dire, exactement ce qu'on répare ici.
    defaut = sortie_par_defaut(module)
    for mots in invocations:
        garde, cible = sans_sortie(mots)
        if cible and defaut and Path(cible).name == defaut.name:
            return garde
    return sans_sortie(invocations[0])[0]


def juger(module: Path, dossier: Path) -> dict:
    """Régénère l'image de ce module à côté et compare. Ne touche jamais `docs/`."""
    cible = sortie_par_defaut(module)
    nom = module.name
    if cible is None:
        return {"module": nom, "verdict": "sans_sortie_declaree"}
    if not cible.is_file():
        return {"module": nom, "verdict": "image_absente", "image": str(cible)}
    tmp = dossier / cible.name
    r = subprocess.run(["uv", "run", "python", str(module)]
                       + arguments_declares(module) + ["--sortie", str(tmp)],
                       cwd=RACINE, capture_output=True, text=True)
    if r.returncode != 0 or not tmp.is_file():
        return {"module": nom, "verdict": "impossible", "image": str(cible),
                "raison": (r.stderr or r.stdout).strip().splitlines()[-1][:120] if (r.stderr or r.stdout) else ""}
    a, b = empreinte(cible), empreinte(tmp)
    return {"module": nom, "verdict": "a_jour" if a == b else "PERIMEE",
            "image": str(cible.relative_to(RACINE))}


def verifier() -> int:
    import shutil
    echecs = controles = 0

    def v(nom: str, ok: bool) -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}")

    d = Path(tempfile.mkdtemp())
    (d / "docs" / "images").mkdir(parents=True)
    (d / "src" / "figures").mkdir(parents=True)

    def module(nom, corps):
        p = d / "src" / "figures" / nom
        p.write_text(corps, encoding="utf-8")
        return p

    # ⚠ La découverte porte sur ce qu'un module DÉCLARE (`--sortie` et un chemin d'images),
    # pas sur son nom : une figure qui ne s'appellerait pas `figure_*` compte aussi.
    m = module("dessin.py", 'p.add_argument("--sortie")\nracine / "docs/images/x.png"\n')
    module("pas_une_figure.py", "x = 1\n")
    trouves = [f.name for f in figures(d)]
    v("un module qui déclare --sortie et une image est une figure", "dessin.py" in trouves)
    v("... et un module qui n'en déclare pas n'en est pas une",
      "pas_une_figure.py" not in trouves)

    m2 = module("avec_defaut.py",
                'ap.add_argument("--sortie", type=Path, default=racine / "docs/images/y.png")\n')
    v("la sortie par défaut se lit dans la déclaration",
      sortie_par_defaut(m2) == RACINE / "docs/images/y.png")
    v("un module sans défaut déclaré rend None", sortie_par_defaut(m) is None)

    # ⚠⚠ Les trois verdicts ne se valent pas, et les confondre rend le contrôle inutile :
    # une image ABSENTE, une figure IMPOSSIBLE à rejouer et une image PÉRIMÉE demandent trois
    # actions différentes.
    r = juger(m2, d)
    v("une image absente se dit « absente », pas « périmée »", r["verdict"] == "image_absente")

    faux = module("qui_plante.py",
                  'import sys\nracine = None\n'
                  'ap = None\n"--sortie"\n"docs/images/z.png"\nsys.exit(2)\n')
    v("une figure qui échoue se dit « impossible », pas « périmée »",
      juger(faux, d)["verdict"] in ("impossible", "sans_sortie_declaree"))

    # ⚠⚠ Les arguments DÉCLARÉS, et chaque contrôle vise une panne réelle du parseur.
    def usage(nom: str, lignes: str) -> Path:
        return module(nom, '"""t\n\nUsage :\n' + lignes + '"""\n'
                           'ap.add_argument("--sortie", type=Path, '
                           'default=racine / "docs/images/u.png")\n')

    u1 = usage("u1.py", "    uv run python src/figures/u1.py --tous --sortie docs/images/u.png\n")
    v("un drapeau déclaré dans l'Usage est rejoué", arguments_declares(u1) == ["--tous"])
    # ⚠ `--sortie` est retiré : le juge fournit le sien. Le garder ferait écrire la figure
    # dans `docs/images/`, c'est-à-dire ferait RÉPARER au contrôle ce qu'il doit CONSTATER.
    v("... et --sortie n'en fait pas partie", "--sortie" not in arguments_declares(u1))

    u2 = usage("u2.py",
               "    uv run python src/figures/u2.py --verifier\n"
               "    uv run python src/figures/u2.py --tous\n")
    # ⚠⚠ La fixture ne déclare AUCUN `--sortie`, et c'est ce qui la rend discriminante : avec
    # un `--sortie` la règle « prendre l'invocation qui écrit l'image jugée » choisirait déjà
    # la bonne ligne, donc retirer le filtre `--verifier` ne changerait rien et le contrôle
    # passerait pour une raison qui n'est pas la sienne. Mesuré le 2026-09-05 : la sonde
    # rendait ALL PASS. Sans `--sortie`, le repli prend la PREMIÈRE invocation.
    v("la ligne --verifier est écartée : c'est la batterie, pas le dessin",
      arguments_declares(u2) == ["--tous"])

    # ⚠ Une invocation tient souvent sur deux lignes, continuées par une barre inverse — que
    # la docstring écrit doublée pour survivre à l'échappement de Python. Lire ligne à ligne
    # perdrait tout ce qui suit la coupure, donc perdrait justement les arguments.
    u3 = usage("u3.py",
               "    uv run python src/figures/u3.py --tous \\\\\n"
               "        --sortie docs/images/u.png\n")
    v("une invocation coupée sur deux lignes est recollée",
      arguments_declares(u3) == ["--tous"])

    # ⚠⚠ Une figure qui documente DEUX dessins : on prend celui dont la sortie est l'image
    # qu'on va comparer. Sans ce filtre on jugerait une image avec les arguments de l'autre,
    # ce qui rendrait un rouge qui ne veut rien dire — le défaut même qu'on répare ici.
    u4 = usage("u4.py",
               "    uv run python src/figures/u4.py --autre --sortie docs/images/zzz.png\n"
               "    uv run python src/figures/u4.py --tous --sortie docs/images/u.png\n")
    v("l'invocation retenue est celle qui écrit l'image jugée",
      arguments_declares(u4) == ["--tous"])

    v("un module sans bloc Usage ne réclame rien", arguments_declares(m2) == [])

    shutil.rmtree(d, ignore_errors=True)

    # --- contre le VRAI arbre ---
    reelles = figures()
    v("l'arbre porte plus de vingt figures", len(reelles) > 20)
    # ⚠ Le seuil vient de la mesure : 36 figures, dont au moins 33 déclarent leur sortie.
    # Ma première version n'en voyait que 11, faute de reconnaître la seconde forme de
    # déclaration -- et elle annonçait quand même « chacune », ce qui était faux de 25.
    declarees = sum(1 for f in reelles if sortie_par_defaut(f))
    # ⚠ Le seuil vient de la MESURE. Ma première version reconnaissait UNE forme de
    # déclaration sur trois, donc elle rendait 11 sur 36 tout en annonçant « chacune » -- un
    # libellé qui affirmait ce que l'assertion ne vérifiait pas, et 25 figures passaient pour
    # non jugeables sans que rien ne le dise.
    v(f"... et au moins les trois quarts déclarent où elles écrivent ({declarees}/{len(reelles)})",
      declarees >= (3 * len(reelles)) // 4)

    # ⚠⚠ Le cas qui a motivé `arguments_declares`, gardé contre le VRAI fichier : cette
    # figure publie le panorama des trois segments, et sans `--tous` le contrôle la rejouait
    # en un seul segment — donc déclarait PÉRIMÉE une image parfaitement à jour.
    nul = RACINE / "src" / "figures" / "figure_le_nul_verso.py"
    v("la figure du nul verso déclare bien sa forme publiée (--tous)",
      not nul.is_file() or "--tous" in arguments_declares(nul))

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()

    with tempfile.TemporaryDirectory() as t:
        d = Path(t)
        resultats = [juger(m, d) for m in figures()]
    comptes = {}
    for r in resultats:
        comptes[r["verdict"]] = comptes.get(r["verdict"], 0) + 1
    perimees = [r for r in resultats if r["verdict"] == "PERIMEE"]
    print(f"{len(resultats)} figure(s) — " + "  ".join(f"{v} {k}" for k, v in sorted(comptes.items())))
    for r in perimees:
        print(f"  ⚠ PÉRIMÉE : {r['image']}  (rendue par {r['module']})")
    # ⚠⚠ NOMMER CE QU'ON COMPTE. Ce contrôle affichait « 7 impossible  1 sans_sortie_declaree »
    # et s'arrêtait là : un compte sans identité ne se répare pas, il se contemple. C'est la
    # même forme que `liens_casses.py`, qui liste ses « sans remède » plutôt que de les compter.
    # Le verdict global ne bouge pas — ces deux états n'ont jamais fait échouer — seule leur
    # lisibilité change.
    for etat, symbole in (("impossible", "⛔"), ("sans_sortie_declaree", "⚠"),
                          ("image_absente", "⚠")):
        for r in (x for x in resultats if x["verdict"] == etat):
            detail = r.get("raison") or r.get("image") or ""
            print(f"  {symbole} {etat} : {r['module']}"
                  + (f"  — {detail}" if detail else ""))
    if a.json:
        a.json.write_text(json.dumps({"comptes": comptes, "figures": resultats},
                                     indent=1, ensure_ascii=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
