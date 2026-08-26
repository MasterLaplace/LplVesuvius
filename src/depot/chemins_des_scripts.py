#!/usr/bin/env python3
"""Les chemins qu'un script CONSTRUIT à l'exécution — la classe qu'une réécriture ne voit pas.

⚠⚠ **Ce fichier existe parce qu'un repli a laissé cinq scripts écrire hors du dépôt.**
`deplacer.py` réécrit les citations *textuelles* d'un chemin ; il ne peut rien pour un
chemin **assemblé à l'exécution**, parce qu'aucune de ses parties ne ressemble au chemin
final. Quand `tools/` est devenu `src/campagnes/`, le `cd` de chaque script a gagné un
niveau et les `"../$OUT"` qui l'accompagnaient ne l'ont pas suivi.

Le symptôme mesuré, et il ne ressemble pas à sa cause : chaque script fait toujours
`mkdir -p "$OUT"` **dans** le dépôt puis écrit dans `"../$OUT"` **dehors**, donc la garde
de reprise `[ -s "$f" ] && continue` ne voit jamais rien et une campagne interrompue
recommence tout. Rien ne lève, rien ne manque, et le dossier créé reste vide.

## Les deux questions, toutes deux dérivées de l'arbre

| question | ce qu'elle attrape |
|---|---|
| un script qui se place à la racine écrit-il en `../` ? | la sortie qui quitte le dépôt |
| une instruction dit-elle d'entrer dans un dossier absent ? | le `cd experiments` d'avant le repli |

⚠ **Rien n'est enregistré dans un registre, et c'est délibéré.** Un mur se juge, un
chemin qui sort du dépôt ne se juge pas : il est faux. Un registre n'apporterait ici
qu'un endroit où déclarer qu'on accepte un défaut.

⚠ La lecture des scripts **saute les corps de heredoc** : `temoins.sh` y écrit des
programmes Python dont le chemin de recherche contient légitimement `../src`, et les
confondre avec une écriture ferait de ce contrôle un bruit qu'on apprend à ignorer.
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from appelants import RACINE, index_des_lignes  # noqa: E402

FAMILLES = ("src/", "docs/")

# `cd "$(dirname "$0")/../.."` et ses variantes : ce qui compte est le nombre de
# niveaux remontés depuis le dossier du script.
_CD_SCRIPT = re.compile(r'^\s*cd\s+"?\$\(dirname\s+"\$0"\)(?P<suite>[^"\s|]*)')
# Un littéral de chemin qui commence par `../`, hors variable.
_SORTANT = re.compile(r'"(\.\./[^"]*)"')
# Une instruction lisible : `cd <dossier>` sans variable ni chemin absolu.
_CD_TEXTE = re.compile(r'(?:^|[;&|]\s*|\s)cd\s+(?P<cible>[A-Za-z_][\w./-]*)')


def _lignes_utiles(texte: str):
    """Les lignes d'un script shell, **corps de heredoc exclus**.

    ⚠ Un heredoc porte du code d'un autre langage. Le lire comme du shell fait
    remonter les chemins de recherche Python de `temoins.sh` comme des écritures.
    """
    fin = None
    for numero, ligne in enumerate(texte.splitlines(), 1):
        if fin is not None:
            if ligne.strip() == fin:
                fin = None
            continue
        ouvre = re.search(r"<<-?\s*'?([A-Za-z_][A-Za-z_0-9]*)'?", ligne)
        if ouvre:
            fin = ouvre.group(1)
        yield numero, ligne


def dossier_de_travail(chemin: Path, texte: str) -> Path | None:
    """Où le script se place, ou `None` s'il ne le dit pas."""
    for _, ligne in _lignes_utiles(texte):
        trouve = _CD_SCRIPT.match(ligne)
        if trouve:
            return (chemin.parent / (trouve.group("suite").lstrip("/") or ".")).resolve()
    return None


def sorties_hors_depot(textes: dict[str, str],
                       racine: Path = RACINE) -> list[tuple[str, int, str]]:
    """Les littéraux `../…` d'un script qui s'est déjà placé à la racine du dépôt.

    ⭐ Le parcours vient d'`appelants.index_des_lignes`, qui élague déjà `.venv` et
    consorts. Un `rglob` de plus aurait été la **quatrième** fois que ce dépôt paie un
    parcours non élagué : la première version de ce fichier a signalé trois `cd` de
    `site-packages`.
    """
    trouvailles = []
    for relatif, texte in sorted(textes.items()):
        if not (relatif.startswith("src/") and relatif.endswith(".sh")):
            continue
        script = racine / relatif
        base = dossier_de_travail(script, texte)
        if base is None:
            continue
        for numero, ligne in _lignes_utiles(texte):
            for litteral in _SORTANT.findall(ligne):
                cible = (base / litteral).resolve()
                if racine not in cible.parents and cible != racine:
                    trouvailles.append((relatif, numero, litteral))
    return trouvailles


def _instructions(chemin: Path, texte: str) -> list[tuple[int, str]]:
    """Les lignes d'un fichier qui **s'adressent à un lecteur**.

    ⚠ Pour un `.py`, seules les **docstrings** comptent. Une chaîne au milieu d'une
    fonction est le plus souvent une fixture de test — `deplacer.py` en porte une qui
    cite exprès un `cd experiments` disparu, et la signaler apprendrait à ignorer ce
    contrôle.
    """
    if chemin.suffix == ".sh":
        return [(n, l) for n, l in _lignes_utiles(texte)]
    if chemin.suffix == ".md":
        lignes, dedans = [], False
        for numero, ligne in enumerate(texte.splitlines(), 1):
            if ligne.lstrip().startswith("```"):
                dedans = ligne.lstrip().startswith(("```bash", "```sh", "```console"))
                continue
            if dedans:
                lignes.append((numero, ligne))
        return lignes
    try:
        arbre = ast.parse(texte)
    except SyntaxError:
        return []
    lignes = []
    for noeud in ast.walk(arbre):
        if not isinstance(noeud, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef,
                                  ast.ClassDef)):
            continue
        doc = ast.get_docstring(noeud)
        if not doc:
            continue
        depart = getattr(noeud, "lineno", 0)
        lignes += [(depart + i, l) for i, l in enumerate(doc.splitlines())]
    return lignes


def cd_vers_le_vide(textes: dict[str, str],
                    racine: Path = RACINE) -> list[tuple[str, int, str]]:
    """Les instructions qui disent d'entrer dans un dossier que le dépôt n'a plus."""
    trouvailles = []
    for relatif, texte in sorted(textes.items()):
        if not relatif.startswith(FAMILLES) or not relatif.endswith((".sh", ".py", ".md")):
            continue
        for numero, ligne in _instructions(racine / relatif, texte):
            for cible in _CD_TEXTE.findall(ligne):
                if "$" in cible or cible in (".", "..", "-"):
                    continue
                if not (racine / cible).exists():
                    trouvailles.append((relatif, numero, cible))
    return trouvailles


def verifier() -> int:
    """Le contrôle se garde lui-même : chaque règle a son cas négatif.

    ⚠ Sans les cas négatifs, un lecteur qui ne verrait **rien** passerait aussi bien
    qu'un lecteur juste, et ce fichier deviendrait la vérification incapable d'échouer
    qu'il existe pour empêcher.
    """
    import tempfile

    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    with tempfile.TemporaryDirectory() as d:
        faux = Path(d)
        (faux / "src" / "campagnes").mkdir(parents=True)
        (faux / "docs").mkdir()

        place = 'cd "$(dirname "$0")/../.." || exit 2\n'
        textes = {
            "src/campagnes/sort.sh": place + 'uv run x --out "../ailleurs/y.json"\n',
            "src/campagnes/reste.sh": place + 'uv run x --out "resultats/y.json"\n',
            "src/campagnes/heredoc.sh": place + "python - <<'PY'\n"
                                        "chemins = ['../src', '../docs']\n" + "PY\n",
            "src/campagnes/sans_cd.sh": 'uv run x --out "../ailleurs.json"\n',
        }
        s = sorties_hors_depot(textes, faux)
        v("un `../` d'un script pose a la racine est signale",
          ("src/campagnes/sort.sh", 2, "../ailleurs/y.json") in s, str(s))
        v("... et un chemin qui RESTE dans le depot ne l'est pas",
          not any(f == "src/campagnes/reste.sh" for f, _, _ in s), str(s))
        # ⚠ `temoins.sh` porte des programmes Python dont le chemin de recherche contient
        # legitimement `../src`. Les lire comme des ecritures ferait de ce controle un
        # bruit qu'on apprend a ignorer, ce qui revient a ne pas l'avoir.
        v("le corps d'un heredoc est ignore",
          not any(f == "src/campagnes/heredoc.sh" for f, _, _ in s), str(s))
        # Un script qui ne dit pas ou il se place ne peut pas etre juge : affirmer qu'il
        # sort serait inventer son point de depart.
        v("un script sans `cd` connu n'est pas juge",
          not any(f == "src/campagnes/sans_cd.sh" for f, _, _ in s), str(s))

        textes = {
            "src/campagnes/a.sh": "cd docs && uv run x\ncd disparu && uv run y\n"
                                  'cd "$AILLEURS" && uv run z\n',
            "src/campagnes/b.py": '"""Usage :\n    cd disparu && uv run b\n"""\n'
                                  'FIXTURE = "cd disparu && uv run vieux"\n',
            "docs/01_x.md": "prose disant cd disparu hors bloc\n"
                            "```bash\ncd disparu && uv run x\n```\n",
        }
        c = cd_vers_le_vide(textes, faux)
        cibles = {(f, cible) for f, _, cible in c}
        v("un `cd` vers un dossier absent est signale",
          ("src/campagnes/a.sh", "disparu") in cibles, str(cibles))
        v("... et un `cd` vers un dossier present ne l'est pas",
          ("src/campagnes/a.sh", "docs") not in cibles, str(cibles))
        v("... ni un `cd` vers une variable", not any("AILLEURS" in x for _, x in cibles),
          str(cibles))
        v("une docstring de .py est une instruction",
          ("src/campagnes/b.py", "disparu") in cibles, str(cibles))
        # ⚠⚠ `deplacer.py` porte une fixture qui cite EXPRES un `cd experiments` disparu.
        # La signaler serait un faux positif permanent, donc un controle qu'on eteint.
        v("... mais une chaine HORS docstring n'en est pas une",
          sum(1 for f, _, _ in c if f == "src/campagnes/b.py") == 1, str(c))
        v("un bloc bash de markdown est une instruction",
          ("docs/01_x.md", "disparu") in cibles, str(cibles))
        v("... mais la prose autour n'en est pas une",
          sum(1 for f, _, _ in c if f == "docs/01_x.md") == 1, str(c))

    # --- et l'arbre reel, qui est la raison d'etre du fichier.
    reels = index_des_lignes()
    v("aucun script du depot n'ecrit dehors", not sorties_hors_depot(reels),
      str(sorties_hors_depot(reels)[:3]))
    v("aucune instruction ne mene dans le vide", not cd_vers_le_vide(reels),
      str(cd_vers_le_vide(reels)[:3]))

    print(f"ALL PASS (0 failures, {controles} checks)" if not echecs
          else f"ECHEC : {echecs} sur {controles}")
    return 0 if not echecs else 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Les chemins qu'un script construit a l'execution sortent-ils du depot ?",
        epilog="Sans argument : l'inventaire. Avec --verifier : sort non nul au premier defaut.")
    parser.add_argument("--verifier", action="store_true")
    args = parser.parse_args()

    if args.verifier:
        return verifier()

    textes = index_des_lignes()
    sortants = sorties_hors_depot(textes)
    perdus = cd_vers_le_vide(textes)

    for fichier, numero, litteral in sortants:
        print(f"HORS DEPOT  {fichier}:{numero}  {litteral}")
    for fichier, numero, cible in perdus:
        print(f"CD VERS RIEN {fichier}:{numero}  cd {cible}")

    print(f"\n{len(sortants)} ecriture(s) hors depot, {len(perdus)} cd vers un dossier absent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
