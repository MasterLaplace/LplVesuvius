#!/usr/bin/env python3
"""Qui LANCE ce script ? — un seul parcours de l'arbre, et une mention n'est pas un appelant.

⚠⚠ DEUX DÉFAUTS DU GARDE-FOU ACTUEL, et le second est le plus gênant.

**Le coût.** `tools/temoins.sh` cherchait un appelant en lançant un `grep -r` sur tout le dépôt
**par fichier**. Mesuré : **0,80 s** le grep, ~200 fichiers, soit **plus de deux minutes** à lui
seul — le contrôle le plus lent de la batterie, et le seul dont le coût croît avec les
**données** plutôt qu'avec le **code**. Un seul parcours qui construit un index, puis 200
recherches dedans, rend la même réponse.

**⚠⚠ Le silence.** Le garde comptait comme appelant **toute occurrence du nom**, y compris dans
de la prose. Constaté le 2026-08-25 : trois orphelins réels signalés, puis **silencieux au run
suivant parce qu'un document venait de les nommer**. Or une mention en prose n'est pas un
appelant — c'est même souvent le contraire : on écrit le nom d'un script *parce qu'il ne sert
plus*. Ce fichier ne compte que ce qui **exécute**.

  ⭐ Les cinq formes d'exécution du dépôt, et rien d'autre :
    `python x.py` / `uv run … python x.py`   ·   `bash x.sh` / `sh x.sh`   ·   `./…/x.sh`
    une ligne `run "…" … x.py --verifier`     ·   `lplv <verbe>` — le point d'entrée

⚠ `lplv <verbe>` compte, et il faut y penser : depuis que le dépôt a un point d'entrée, un
script peut n'être lancé que par lui. Ne pas le reconnaître ferait déclarer orphelin tout ce
que `lplv` sert.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
LUS = (".py", ".sh", ".md", ".toml", ".txt")
IGNORES = (".git", ".venv", "__pycache__", ".lances", "data", "repos", "build", "site")


def formes_dexecution(nom: str) -> list[re.Pattern]:
    """Les motifs qui EXÉCUTENT `nom`, jamais ceux qui le citent.

    ⚠ `nom` porte son extension (`x.py`), sauf pour la forme `lplv`, qui prend le verbe nu.
    """
    n = re.escape(nom)
    verbe = re.escape(Path(nom).stem)
    return [
        re.compile(r"(?:python3?|uv run(?:\s+--project\s+\S+)?\s+python3?)\s+\S*" + n + r"\b"),
        re.compile(r"(?:bash|sh)\s+\S*" + n + r"\b"),
        re.compile(r"\./\S*" + n + r"\b"),
        re.compile(r"^\s*run\s+\"[^\"]*\"\s+.*" + n + r"\b", re.M),
        re.compile(r"\blplv\s+" + verbe + r"\b"),
        # ⚠ `lancer.sh <script>` : le script est passe en ARGUMENT au lanceur du depot. Sans
        # cette forme, tout ce qui se lance en tache de fond passe pour orphelin.
        re.compile(r"lancer\.sh(?:\s+--\S+)*\s+\S*" + n + r"\b"),
        # ⚠⚠ Une commande ecrite entre backticks AVEC un argument : « Reproductible :
        # `src/outils/x.sh PHerc0172` ». C'est une instruction d'execution, pas une mention.
        # ⭐ La presence d'un argument DANS les backticks est ce qui separe les deux : une
        # simple citation s'ecrit `x.sh` et se ferme aussitot.
        re.compile(r"`\S*" + n + r"\s+\S[^`]*`"),
        # ⚠⚠ SOURCER une bibliotheque shell, c'est l'EXECUTER : son code de premier niveau
        # tourne et ses fonctions deviennent disponibles. Sans cette forme, toute bibliotheque
        # shell du depot passe pour orpheline -- ce qui est arrive a `juger_nappe.sh`, ecrit
        # pour dedupliquer une fonction de jugement et signale comme execute par personne.
        #
        # ⚠ Ancre en DEBUT DE LIGNE (espaces permis) : c'est ce qui separe une execution d'une
        # mention. Un document qui cite `juger_nappe.sh` au fil d'une phrase ne commence pas sa
        # ligne par `.` ou `source`. Le chemin peut etre calcule -- `. "$(dirname ...)/x.sh"` --
        # d'ou le `[^\n]*?` plutot qu'un `\S*`.
        re.compile(r"^[ \t]*(?:\.|source)\s+[^\n]*?" + n + r"\b", re.M),
    ]


SOUS_PROCESSUS = re.compile(r"\bsubprocess\.(?:run|Popen|check_output|call)\b|\bos\.system\b")
"""Ce qui lance un programme depuis Python."""


def execute_par_sous_processus(texte: str, nom: str) -> bool:
    """
    @brief Ce fichier lance-t-il `nom` par un sous-processus, chemin construit compris ?

    ⚠⚠⚠ POURQUOI CETTE FORME EXISTE. `src/excision/proximity.py` est l'instrument central de
    tout l'arc d'excision, appelé par `reparation_et_proximite.py` et `le_bruit_de_lechantillon.py`
    — et il était signalé **exécuté par personne**. La raison : ces deux-là construisent son
    chemin par segments (`RACINE / "src" / "excision" / "proximity.py"`) puis le passent à
    `subprocess.run`, donc aucune ligne du fichier ne ressemble à une commande. Un détecteur qui
    ne voit pas un appelant fait passer un script vivant pour mort, ce qui invite à le
    supprimer : c'est le mode d'échec le plus coûteux qu'il puisse avoir.

    ⭐ Ce n'est PAS un motif de plus dans la liste : c'est une **conjonction**, et c'est elle qui
    évite les faux positifs. Il faut à la fois que le fichier lance un sous-processus **et** que
    le nom apparaisse comme **dernier segment d'un chemin** — construit avec `/` ou écrit en
    chaîne barrée. Une mention en prose (`voir proximity.py`) ne remplit ni l'une ni l'autre.
    """
    if not SOUS_PROCESSUS.search(texte):
        return False
    n = re.escape(nom)
    # Soit `… / "nom"` (construction par segments), soit `"…/nom"` (chemin ecrit d'un bloc).
    return bool(re.search(r"/\s*[\"']" + n + r"[\"']", texte)
                or re.search(r"[\"'][^\"']*/" + n + r"[\"']", texte))


def index_des_lignes(racine: Path = RACINE) -> dict[str, str]:
    """Le texte de chaque fichier lisible, en UN seul parcours de l'arbre.

    ⭐ C'est tout le remède au coût : le parcours est fait une fois, pas une fois par script.
    """
    textes, pile = {}, [racine]
    while pile:
        d = pile.pop()
        try:
            entrees = list(d.iterdir())
        except OSError:
            continue
        for e in entrees:
            if e.name in IGNORES or e.name.startswith("."):
                continue
            if e.is_dir():
                pile.append(e)
            elif e.is_file() and e.suffix in LUS:
                try:
                    textes[str(e.relative_to(racine))] = e.read_text(
                        encoding="utf-8", errors="replace")
                except OSError:
                    continue
    return textes


def appelants(textes: dict[str, str], chemin: str) -> list[str]:
    """Les fichiers qui LANCENT `chemin`. ⚠ Le fichier lui-même ne se compte pas."""
    nom = Path(chemin).name
    verbe_nu = Path(chemin).stem
    motifs = formes_dexecution(nom)
    out = []
    for f, t in textes.items():
        if f == chemin:
            continue
        # ⚠⚠ LE PRE-FILTRE, et il n'est pas cosmetique : sans lui, 210 scripts x 355 textes x
        # 7 motifs font un demi-million de recherches regex, mesure a 38 s -- le controle
        # redevenait le plus lent de la batterie, juste pour une autre raison. Un `in` de chaine
        # ecarte 99 % des paires avant qu'une seule regex ne tourne.
        if nom not in t and verbe_nu not in t:
            continue
        if any(m.search(t) for m in motifs) or execute_par_sous_processus(t, nom):
            out.append(f)
    return sorted(out)


def scripts_du_depot(textes: dict[str, str]) -> list[str]:
    """Les scripts que ce dépôt peut lancer, d'après `lplv.FAMILLES` et rien d'autre.

    ⚠⚠ Cette fonction existe parce qu'il y avait DEUX réponses à « qu'est-ce qu'un script de
    ce dépôt ». `lplv` en nommait cinq familles — `src/`, mais aussi `tracecheck/`,
    `inference_xpu/src/` et `experiments/src/` — pendant que ce fichier jugeait `src/`
    seul.
    Donc `lplv` savait lancer un verbe dont ce garde-fou ne se demandait jamais si quelque
    chose l'exécutait : un orphelin hors de `src/` était invisible par construction.

    ⚠ La liste vit dans `lplv` et pas ici : le point d'entrée est ce qui DÉFINIT ce qu'est un
    greffon, ce fichier ne fait que le vérifier. L'inverse ferait dépendre le point d'entrée
    de son propre contrôle.
    """
    import fnmatch

    from lplv import FAMILLES

    return sorted(f for f in textes
                  if any(fnmatch.fnmatch(f, motif) for motif, _ in FAMILLES))


INVOCATION_NUE = re.compile(
    r"(?:^|`)\s*(?:[A-Z_][A-Z0-9_]*=\S+\s+)*(\./)?((?:src|tools)/[\w./-]+\.(?:sh|py))\s+\S",
    re.M)
r"""Une commande dont le PREMIER mot est un fichier du dépôt — donc qui dépend de son bit `x`.

⚠ Les préfixes `VAR=valeur` sont sautés : `ZARR=… src/outils/x.sh …` lance bien `x.sh`.
⚠ `\s+\S` à la fin exige un ARGUMENT, exactement comme la forme entre backticks de
`formes_dexecution` : sans lui, toute citation `\`x.py\`` serait lue comme une commande.
"""


def invocations_impossibles(racine: Path = RACINE) -> list[dict]:
    """Les commandes écrites dans l'arbre qu'un lecteur ne PEUT PAS lancer telles quelles.

    ⚠⚠ POURQUOI CE CONTRÔLE EXISTE, et c'est une classe que rien ne voyait. Une commande
    documentée sous la forme `src/volume/x.py PHerc0500P2` s'exécute par le bit `x` du
    fichier — et sept scripts du dépôt portent un shebang **sans** ce bit. La commande rend
    donc `Permission denied`, alors qu'elle est écrite, relue, et parfaitement plausible.

      ⭐ C'est la même famille que l'orphelin, prise par l'autre bout : là un script vivant
        passait pour mort, ici une commande morte passe pour vivante. Les deux se lisent
        pareil dans un document.

    ⚠ Le remède est d'écrire la forme canonique du dépôt (`uv run python …`), pas de poser
    le bit `x` : deux de ces sept scripts importent numpy ou PIL, donc un lancement direct
    démarrerait avec le python du système et échouerait à l'import — une commande qui a
    l'air de marcher et casse plus loin est pire que celle qui refuse tout de suite.
    """
    out = []
    for f, texte in sorted(index_des_lignes(racine).items()):
        if not f.endswith(".md"):
            continue
        for n, ligne in enumerate(texte.splitlines(), 1):
            for m in INVOCATION_NUE.finditer(ligne):
                cible = racine / m.group(2)
                if cible.is_file() and not (cible.stat().st_mode & 0o111):
                    out.append({"commande": m.group(2), "ou": f"{f}:{n}"})
    return out


def orphelins(textes: dict[str, str], scripts: list[str]) -> dict:
    """Les scripts que rien n'exécute, et le compte de ce qui a été regardé."""
    sans = [s for s in scripts if not appelants(textes, s)]
    return {"scripts": len(scripts), "fichiers_lus": len(textes),
            "orphelins": sorted(sans), "combien": len(sans)}


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool) -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}")

    T = {
        "src/outils/lance.sh": 'uv run python "$ROOT/src/depot/mesure.py" --json x\n',
        "src/outils/autre.sh": "bash src/outils/lance.sh\n",
        "src/outils/tiers.sh": "./src/outils/autre.sh --verifier\n",
        "src/outils/temoins.sh": 'run "la mesure"  python3 "$ROOT/src/depot/tiers.py" --verifier\n',
        "docs/07.md": "Le script `src/depot/mort.py` ne sert plus à rien depuis mars.\n",
        "docs/08.md": "```bash\nlplv horizon --json docs/mesures/h.json\n```\n",
        "src/depot/mesure.py": "x = 1\n",
        "src/depot/mort.py": "x = 1\n",
        "src/depot/horizon.py": "x = 1\n",
        "src/depot/tiers.py": "x = 1\n",
    }

    v("un `uv run python` compte comme appelant",
      appelants(T, "src/depot/mesure.py") == ["src/outils/lance.sh"])
    v("un `bash` aussi", appelants(T, "src/outils/lance.sh") == ["src/outils/autre.sh"])
    v("un `./` aussi", appelants(T, "src/outils/autre.sh") == ["src/outils/tiers.sh"])
    v("une ligne `run \"…\"` aussi",
      appelants(T, "src/depot/tiers.py") == ["src/outils/temoins.sh"])
    # ⭐ Depuis que le depot a un point d'entree, un script peut n'etre lance QUE par lui.
    v("`lplv <verbe>` compte comme appelant", appelants(T, "src/depot/horizon.py") == ["docs/08.md"])

    # ⚠⚠ LE CONTROLE CENTRAL : une mention en prose N'EST PAS un appelant. Le garde precedent
    # comptait toute occurrence du nom, donc nommer un orphelin dans un document le faisait taire.
    v("une MENTION en prose n'est PAS un appelant", appelants(T, "src/depot/mort.py") == [])
    v("... donc il ressort orphelin", orphelins(T, ["src/depot/mort.py"])["combien"] == 1)
    v("... alors qu'un vrai appelant le sauve",
      orphelins(T, ["src/depot/mesure.py"])["combien"] == 0)

    # ⚠⚠ Deux formes REELLES du depot que la premiere version ratait, trouvees en la lancant
    # sur l'arbre : elle declarait orphelins vingt-cinq scripts qui sont bel et bien lances.
    T4 = {"docs/40.md": "Reproductible : `src/outils/mosaique.sh PHerc0172`.\n",
          "docs/36.md": "./src/outils/lancer.sh --fond src/outils/graine.sh   # en tache de fond\n",
          "docs/12.md": "`src/figures/dessin.py` — trace avec PIL, sans matplotlib.\n",
          "src/outils/mosaique.sh": "", "src/outils/graine.sh": "", "src/figures/dessin.py": ""}
    v("une commande entre backticks AVEC argument est un appelant",
      appelants(T4, "src/outils/mosaique.sh") == ["docs/40.md"])
    v("un script passe en argument a `lancer.sh` aussi",
      appelants(T4, "src/outils/graine.sh") == ["docs/36.md"])
    # ⭐ Le controle qui empeche la forme precedente de tout avaler : une CITATION entre
    # backticks se ferme aussitot, sans argument, et ce n'est pas un appel.
    v("... mais une citation entre backticks SANS argument n'en est pas un",
      appelants(T4, "src/figures/dessin.py") == [])

    # ⚠ Un fichier ne s'appelle pas lui-meme : sinon rien ne serait jamais orphelin.
    T2 = dict(T, **{"src/depot/seul.py": "python src/depot/seul.py\n"})
    v("un fichier ne compte pas comme son propre appelant",
      appelants(T2, "src/depot/seul.py") == [])

    # ⚠ Un nom qui est le PREFIXE d'un autre ne doit pas voler son appelant.
    T3 = {"a.sh": "python src/depot/mesure_longue.py\n",
          "src/depot/mesure.py": "", "src/depot/mesure_longue.py": ""}
    v("un nom prefixe d'un autre ne vole pas son appelant",
      appelants(T3, "src/depot/mesure.py") == []
      and appelants(T3, "src/depot/mesure_longue.py") == ["a.sh"])

    r = orphelins(T, list(T))
    v("le rapport dit combien de fichiers ont ete lus", r["fichiers_lus"] == len(T))
    v("... et combien de scripts ont ete juges", r["scripts"] == len(T))

    # --- contre le VRAI arbre : le cout, qui est la raison d'etre du fichier ---
    import time
    t0 = time.time()
    textes = index_des_lignes()
    duree = time.time() - t0
    # ⚠ Le seuil vient de la MESURE, pas d'un chiffre rond : 355 fichiers en 0,05 s le
    # 2026-08-26, contre 0,80 s x ~200 pour l'ancien garde, soit plus de trois mille fois.
    # ⚠⚠ Ma premiere version annoncait « plus de mille fichiers » et assertait 500 : le
    # libelle et l'assertion disaient deux choses differentes, et aucune des deux n'etait vraie.
    import fnmatch

    from lplv import FAMILLES

    v("l'arbre entier se lit en UN parcours, en moins d'une seconde", duree < 1.0)
    v("... et il couvre les deux langages du depot",
      sum(1 for f in textes if f.endswith(".py")) > 100
      and sum(1 for f in textes if f.endswith(".sh")) > 40)
    v("... et la prose, sans quoi `lplv <verbe>` d'un bloc Reproduire serait invisible",
      sum(1 for f in textes if f.endswith(".md")) > 40)

    # ⚠⚠ Le perimetre du garde-fou doit etre CELUI du point d entree. Il jugeait `src/`
    # seul pendant que `lplv` sait lancer quatre familles de plus : un orphelin hors de
    # `src/` etait invisible par construction, et il y en avait quatre.
    juges = scripts_du_depot(textes)
    # ⚠⚠ Ce controle disait « au moins un script juge est HORS de `src/` ». Le repli du
    # 2026-08-26 l a rendu VACUEUX : tout est dans `src/` desormais, donc il ne pouvait plus
    # que rougir. Ce qui compte n a pas change — le perimetre doit etre DERIVE de
    # `lplv.FAMILLES` et non ecrit en dur — mais ca ne se prouve qu en changeant FAMILLES et
    # en verifiant que le perimetre suit.
    import lplv as _lplv
    familles_reelles = _lplv.FAMILLES
    try:
        _lplv.FAMILLES = (("src/depot/*.py", "python"),)
        restreint = scripts_du_depot(textes)
    finally:
        _lplv.FAMILLES = familles_reelles
    v("le perimetre SUIT lplv.FAMILLES au lieu d'etre ecrit en dur",
      restreint and all(f.startswith("src/depot/") for f in restreint)
      and len(restreint) < len(juges))
    v("... et il couvre chacune des familles declarees",
      all(any(fnmatch.fnmatch(f, motif) for f in juges) for motif, _ in FAMILLES))
    v("... sans rien prendre en dehors",
      all(any(fnmatch.fnmatch(f, m) for m, _ in FAMILLES) for f in juges))

    # ⚠⚠ LE SOUS-PROCESSUS A CHEMIN CONSTRUIT, teste dans LES DEUX SENS. La forme trop large
    # avalerait toute mention dans un fichier qui lance quoi que ce soit ; la forme inerte
    # laisserait `proximity.py` -- l'instrument central de l'arc d'excision -- passer pour mort.
    v("un chemin construit par segments et lance en sous-processus est un appel",
      execute_par_sous_processus(
          'P = RACINE / "src" / "excision" / "proximity.py"\nsubprocess.run([str(P)])',
          "proximity.py"))
    v("... et un chemin ecrit d'un bloc aussi",
      execute_par_sous_processus('x = "src/excision/proximity.py"\nsubprocess.run([x])',
                                 "proximity.py"))
    v("une mention en prose ne compte pas, meme dans un fichier qui lance",
      not execute_par_sous_processus('# voir proximity.py\nsubprocess.run(["ls"])',
                                     "proximity.py"))
    v("... et un chemin qu'on LIT sans le lancer non plus",
      not execute_par_sous_processus(
          'P = RACINE / "src" / "excision" / "proximity.py"\nprint(P.read_text())',
          "proximity.py"))

    # ⚠⚠ LA QUESTION SYMÉTRIQUE : une commande écrite pour être lancée telle quelle, sur un
    # fichier qui n'a pas le bit `x`. Un orphelin est un script vivant qu'on croit mort ;
    # celle-ci est une commande morte qu'on croit vivante, et les deux se lisent pareil.
    import shutil
    import tempfile
    d = Path(tempfile.mkdtemp())
    (d / "docs").mkdir()
    (d / "src" / "outils").mkdir(parents=True)

    def script(nom: str, executable: bool) -> Path:
        f = d / "src" / "outils" / nom
        f.write_text("#!/usr/bin/env python3\n", encoding="utf-8")
        f.chmod(0o755 if executable else 0o644)
        return f

    script("muet.py", False)
    script("pose.sh", True)
    script("nu.sh", False)
    (d / "docs" / "a.md").write_text(
        "Mesure : `src/outils/muet.py --ecrire`.\n"
        "Reproductible : `src/outils/pose.sh PHerc0172`.\n"
        "Canonique : `uv run python src/outils/muet.py --ecrire`.\n"
        "Citation : `src/outils/muet.py` sans argument.\n"
        "ZARR=x NIVEAU=2 src/outils/nu.sh a b\n", encoding="utf-8")
    vus = invocations_impossibles(d)
    cmds = sorted({i["commande"] for i in vus})
    v("une commande nue sur un fichier sans bit `x` est signalée",
      "src/outils/muet.py" in cmds)
    v("... et un fichier exécutable ne l'est pas", "src/outils/pose.sh" not in cmds)
    # ⚠⚠ LE CONTRÔLE QUI EMPÊCHE LE FAUX POSITIF : `uv run python x.py` ne dépend d'aucun bit
    # `x`, donc la forme canonique du dépôt ne doit JAMAIS ressortir. Sans lui, le remède
    # signalerait le remède, et le contrôle deviendrait impossible à mettre au vert.
    v("... et la forme `uv run python` n'en dépend pas, donc ne compte pas",
      sum(1 for i in vus if i["commande"] == "src/outils/muet.py") == 1)
    # ⚠ Une CITATION entre backticks se ferme sans argument : ce n'est pas une commande.
    # C'est la même garde que la septième forme de `formes_dexecution`, et pour la même raison.
    v("... et une citation sans argument non plus",
      sum(1 for i in vus if "a.md:4" in i["ou"]) == 0)
    # ⚠ `ZARR=… src/outils/nu.sh …` lance bien `nu.sh` : sauter les préfixes d'environnement
    # est ce qui empêche un `Permission denied` de passer inaperçu derrière une variable.
    v("un préfixe VAR=valeur ne cache pas la commande", "src/outils/nu.sh" in cmds)

    shutil.rmtree(d, ignore_errors=True)

    # --- contre le VRAI arbre ---
    # ⚠ Le seuil est ZÉRO, pas un plafond : une commande documentée qui rend « Permission
    # denied » n'est pas un défaut qu'on tolère, c'est une mesure que personne ne peut
    # refaire. Mesuré le 2026-09-05 : dix sites, tous réécrits en forme canonique.
    reelles = invocations_impossibles()
    v(f"aucune commande documentée n'est inexécutable ({len(reelles)})", not reelles)

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
    import time
    t0 = time.time()
    textes = index_des_lignes()
    scripts = scripts_du_depot(textes)
    r = orphelins(textes, scripts)
    r["secondes"] = round(time.time() - t0, 2)
    print(f"{r['scripts']} scripts jugés depuis {r['fichiers_lus']} fichiers lus "
          f"en {r['secondes']} s")
    if r["orphelins"]:
        print(f"  ⚠ {r['combien']} script(s) que RIEN n'exécute :")
        for o in r["orphelins"]:
            print(f"      {o}")
    else:
        print("  ✅ aucun")
    # ⚠⚠ La question SYMÉTRIQUE, et elle se lit dans le même document qu'un orphelin : une
    # commande écrite pour être lancée telle quelle, sur un fichier qui n'a pas le bit `x`.
    r["invocations_impossibles"] = invocations_impossibles()
    if r["invocations_impossibles"]:
        print(f"  ⚠ {len(r['invocations_impossibles'])} commande(s) documentée(s) que le bit "
              "`x` manquant rend inexécutable(s) :")
        for i in r["invocations_impossibles"]:
            print(f"      {i['ou']:52s} {i['commande']}")
    if a.json:
        a.json.write_text(json.dumps(r, indent=1, ensure_ascii=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
