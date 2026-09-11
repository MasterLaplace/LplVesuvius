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
    """Les instructions qui disent d'entrer dans un dossier que le dépôt n'a plus.

    ⚠ `docs/archive/` est exclu, et c'est une décision du 2026-09-11 : l'archive est du texte
    GELÉ, ses `cd experiments` et `cd inference_xpu` étaient vrais quand ils ont été écrits et
    personne ne les maintiendra plus. Les signaler apprendrait à ignorer ce contrôle ; ce qu'il
    garde, ce sont les instructions qu'un lecteur suit AUJOURD'HUI — `src/`, `docs/rapports/`.
    Les instructions périmées de l'archive sont recensées dans le registre des contradictions.
    """
    trouvailles = []
    for relatif, texte in sorted(textes.items()):
        if not relatif.startswith(FAMILLES) or not relatif.endswith((".sh", ".py", ".md")):
            continue
        if relatif.startswith("docs/archive/"):
            continue
        for numero, ligne in _instructions(racine / relatif, texte):
            for cible in _CD_TEXTE.findall(ligne):
                if "$" in cible or cible in (".", "..", "-"):
                    continue
                if not (racine / cible).exists():
                    trouvailles.append((relatif, numero, cible))
    return trouvailles


_SCRIPT_LANCE = re.compile(
    r"(?:uv run |python3?|bash|sh|\./)\s+(?<![\w/$.-])((?:src|tools|scripts)/[\w./-]+\.(?:py|sh))")
"""Un chemin de script **qu'on lance**, cité en clair, sans variable ni joker.

⚠⚠ La première version cherchait le chemin SEUL et rendait **76** trouvailles pour **4**
vraies : les batteries de ce dépôt fabriquent des fixtures qui s'appellent
`src/depot/mort.py`, `src/campagnes/a.sh`, `src/figures/dessin.py`… Une alerte qui désigne
soixante-seize lignes ne désigne rien — c'est le reproche que `artefacts_orphelins` s'adresse
à lui-même dans son propre en-tête. Exiger un VERBE de lancement devant sépare la commande
qu'un lecteur copie-colle du nom qu'une fixture invente.

⚠ Le regard arrière refuse `$`, `/`, `.` et `-` juste avant : `$ROOT/src/x.py` et
`../src/x.py` sont assemblés à l'exécution, donc leur existence se juge autrement."""


FIXTURES = {
    ("src/depot/appelants.py", "src/outils/lance.sh"): "fixture de la batterie des appelants",
    ("src/depot/appelants.py", "src/depot/seul.py"): "fixture de la batterie des appelants",
    ("src/depot/appelants.py", "src/depot/mesure_longue.py"): "fixture de la batterie des appelants",
    ("src/outils/lancer.sh", "src/campagnes/campagne_x.sh"): "exemple d'usage dans l'aide de lancer.sh",
    ("src/outils/lancer.sh", "src/outils/.temoin_lancer.sh"): "script temporaire que la batterie ECRIT puis efface",
    ("src/outils/readme_apparie.sh", "src/mesures/inexistant_xyz.py"): "fixture : un chemin qui doit manquer",
    # ⚠ Ajoutees le 2026-08-29 : trois fixtures de batteries que l'alerte designait en
    # permanence. Un defaut qu'on ne peut pas corriger apprend a ignorer l'alerte, ce qui
    # coute plus cher que le defaut.
    ("src/depot/batteries_incapables_dechouer.py", "src/x/c.py"): "fixture de la batterie des batteries",
    ("src/depot/chemins_des_scripts.py", "src/parti/ailleurs.py"): "fixture de cette batterie meme",
    ("src/depot/chemins_des_scripts.py", "src/mesures/inexistant_xyz.py"): "fixture de cette batterie meme",
}
"""Les couples (fichier, cible) qu'on accepte de voir absents, avec la RAISON.

⚠⚠ Un nom inventé par une batterie n'est pas un chemin mort — c'est un cas de test, et
plusieurs le sont *exprès* (`inexistant_xyz.py` existe pour ne pas exister). Les exempter
nommément, plutôt que d'assouplir la règle, garde l'alerte utile : elle désignait 76 lignes
au premier jet, 8 au second, et **2** ici — les deux vraies."""


def scripts_qui_nexistent_plus(textes: dict[str, str],
                               racine: Path = RACINE) -> list[tuple[str, int, str]]:
    """Les commandes qui nomment un script que le dépôt n'a plus.

    ⚠⚠ Cette question s'ajoute aux deux autres parce qu'elle s'est posée TROIS FOIS dans la
    même journée : `carte_difficulte.sh` lisait `/tmp/pred_prix.txt`, que rien ne produit ;
    `campagne_temoin_negatif.sh` appelait `src/infer_ink.py`, déménagé dans `src/xpu/` au
    rangement en dix familles ; et `09` publie encore la même commande morte. Chaque fois la
    panne se lit comme « la commande de reproduction ne marche pas », c'est-à-dire comme un
    résultat qu'on ne peut plus refaire.

    ⚠ Les documents comptent autant que les scripts : une commande publiée dans un `.md` est
    une promesse, et une promesse qu'on ne peut pas tenir vaut moins que pas de promesse.
    """
    trouvailles = []
    for relatif, texte in sorted(textes.items()):
        if not relatif.endswith((".sh", ".py", ".md")):
            continue
        for numero, ligne in enumerate(texte.splitlines(), 1):
            for cible in _SCRIPT_LANCE.findall(ligne):
                if any(c in cible for c in "*?<>{}"):
                    continue
                if (relatif, cible) in FIXTURES:
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

    # --- LA TROISIEME QUESTION : un script nomme mais absent ---------------------------
    # ⚠⚠ Elle s'est posee TROIS FOIS le 2026-08-27, et chaque fois la panne se lisait comme
    # « la commande de reproduction publiee ne marche pas ».
    faux = {
        "docs/x.md": "uv run python src/xpu/infer_ink.py --verifier\n",
        "docs/y.md": "uv run python src/parti/ailleurs.py --verifier\n",
        "docs/z.md": "uv run python $ROOT/src/parti/ailleurs.py\n",
        "docs/w.md": 'CIBLES = {"src/depot/mort.py": "fixture"}\n',
        "src/outils/readme_apparie.sh": "python3 src/mesures/inexistant_xyz.py\n",
    }
    trouve = {(f, c) for f, _, c in scripts_qui_nexistent_plus(faux)}
    v("un script qui existe n'est pas signale",
      ("docs/x.md", "src/xpu/infer_ink.py") not in trouve)
    v("un script LANCE et absent est signale",
      ("docs/y.md", "src/parti/ailleurs.py") in trouve)
    # ⚠ Un chemin assemble a l'execution ne se juge pas ici : c'est l'affaire de
    # `sorties_hors_depot`, et le confondre rendrait deux alertes pour un seul defaut.
    v("un chemin construit avec une variable n'est pas juge",
      ("docs/z.md", "src/parti/ailleurs.py") not in trouve)
    # ⚠⚠ LE controle qui a fait retomber l'alerte de 76 a 8 : un nom de fixture, cite sans
    # verbe de lancement, n'est pas une commande.
    v("un nom cite sans verbe de lancement n'est pas une commande",
      ("docs/w.md", "src/depot/mort.py") not in trouve)
    # ⚠ Et celui qui rend les exemptions auditables : elles portent le COUPLE, pas le nom,
    # donc exempter une fixture n'aveugle pas le meme nom ailleurs.
    v("une fixture exemptee nommement est tue",
      ("src/outils/readme_apparie.sh", "src/mesures/inexistant_xyz.py") not in trouve)
    v("... et la meme cible ailleurs serait signalee",
      ("docs/y.md", "src/parti/ailleurs.py") in trouve)
    v("chaque exemption porte sa raison", all(FIXTURES.values()))

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
    absents = scripts_qui_nexistent_plus(textes)

    for fichier, numero, litteral in sortants:
        print(f"HORS DEPOT  {fichier}:{numero}  {litteral}")
    for fichier, numero, cible in perdus:
        print(f"CD VERS RIEN {fichier}:{numero}  cd {cible}")
    for fichier, numero, cible in absents:
        print(f"SCRIPT ABSENT {fichier}:{numero}  {cible}")

    print(f"\n{len(sortants)} ecriture(s) hors depot, {len(perdus)} cd vers un dossier absent, "
          f"{len(absents)} script(s) nomme(s) mais absent(s)")
    return 1 if absents else 0


if __name__ == "__main__":
    sys.exit(main())
