#!/usr/bin/env python3
"""`lplv` — le point d'entrée qui nomme les cent quatre-vingt-dix greffons déjà là.

⚠⚠ CE FICHIER NE CRÉE PAS UNE ARCHITECTURE, IL LUI DONNE UN NOM. Mesuré le 2026-08-25 :
sur les modules de `src/`, la quasi-totalité ont un `main()`, beaucoup exposent `--verifier` et
**65 exposent `--json`**. Cent vingt-cinq greffons de forme uniforme existaient, sans registre
et sans point d'entrée. La question n'était donc pas *faut-il des plugins* — le skill dit d'en
construire au deuxième implémenteur réel, il y en a cent vingt-cinq — mais *pourquoi n'ont-ils
pas de registre*.

⭐ CE QUE ÇA ACHÈTE, ET C'EST LA SEULE RAISON : **une aide qui ne peut pas périmer**, parce
qu'elle est dérivée du code et non recopiée à côté. `lplv --help` liste les verbes avec la
première ligne de leur docstring ; `lplv <verbe> --help` **exécute le module avec `--help`**.

⚠⚠ Cette exécution est le cœur du dessin, et l'alternative tentante est le piège : re-lire
l'`argparse` du module pour en re-fabriquer une aide produirait une **seconde description** de
la même chose, libre de diverger de la première — soit exactement la panne que ce point
d'entrée existe pour empêcher. On délègue au module ; il n'y a donc rien à tenir à jour.

⚠ CE QU'ON NE FAIT PAS, et le §4 du plan le dit : pas de registre à l'exécution, pas de cycle
de vie, pas de version de contrat, pas de mode dégradé. Les modules sont dans le même dépôt et
lancés par le même interpréteur : la découverte par le système de fichiers suffit, et tout le
reste serait le prix d'un **liage tardif dont personne n'a besoin ici** (skill §7).

⚠ Un nom en double serait une ambiguïté SILENCIEUSE — `lplv x` lancerait celui que l'ordre du
système de fichiers a mis devant. Mesuré à zéro aujourd'hui, et **refusé plutôt que départagé**
si ça change : départager, c'est choisir à la place de l'auteur sans le lui dire.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]

FAMILLES: tuple[tuple[str, str], ...] = (
    ("src/*/*.py", "python"),
    ("src/*/*.sh", "shell"),
    ("tracecheck/*.py", "python"),
    ("inference_xpu/src/*.py", "python"),
    ("experiments/src/*/*.py", "python"),
)
"""Où vivent les greffons. ⚠ Même liste que `artefacts_orphelins.SOURCES` : deux listes de
« où est le code de ce dépôt » finiraient par ne pas s'accorder, et c'est déjà arrivé ici."""


class VerbeAmbigu(RuntimeError):
    """Deux fichiers revendiquent le même nom de verbe."""


@dataclass(frozen=True)
class Verbe:
    """Un greffon, tel qu'il se décrit LUI-MÊME. Rien ici n'est écrit à la main ailleurs."""

    nom: str
    chemin: Path
    langage: str
    resume: str
    verifie: bool
    donne_json: bool


def resume_de(chemin: Path) -> str:
    """La première ligne de la docstring (Python) ou du bandeau de commentaires (shell).

    ⭐ C'est EXACTEMENT la chaîne que le module donne déjà à son `argparse`
    (`description=__doc__.splitlines()[0]`, convention du dépôt), donc le résumé de `lplv` et
    l'aide du module ne peuvent pas diverger : c'est le même octet.
    """
    try:
        texte = chemin.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    if chemin.suffix == ".py":
        for marque in ('"""', "'" * 3):
            i = texte.find(marque)
            if i == -1:
                continue
            # ⚠ Une docstring de module vient AVANT tout code : un guillemet triple trouvé
            # après un `def` appartient à une fonction et décrirait la mauvaise chose.
            avant = texte[:i]
            if any(l.strip() and not l.startswith(("#", '"', "'", "from ", "import "))
                   for l in avant.splitlines()):
                continue
            reste = texte[i + 3:]
            return reste.splitlines()[0].strip() if reste else ""
        return ""
    # Shell : le bandeau de commentaires sous le shebang.
    for ligne in texte.splitlines()[1:]:
        d = ligne.strip()
        if not d:
            continue
        if d.startswith("#"):
            return d.lstrip("#").strip()
        break
    return ""


def expose(chemin: Path, option: str) -> bool:
    """Le fichier déclare-t-il cette option ?

    ⚠ Deux écritures, parce que les deux langages déclarent différemment, et une seule des
    deux ferait passer la moitié du dépôt pour muette.
    """
    try:
        texte = chemin.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    if chemin.suffix == ".py":
        return f'add_argument("{option}"' in texte or f"add_argument('{option}'" in texte
    return f'= "{option}" ]' in texte or f"{option})" in texte


def decouvrir(racine: Path = RACINE) -> list[Verbe]:
    """Tous les verbes, triés par nom. Lève `VerbeAmbigu` si deux fichiers se disputent un nom."""
    par_nom: dict[str, Verbe] = {}
    doubles: list[tuple[str, Path, Path]] = []
    for motif, langage in FAMILLES:
        for f in sorted(racine.glob(motif)):
            if "__pycache__" in f.parts or not f.is_file():
                continue
            nom = f.stem
            # ⚠ Un nom qui commence par `_` n'est pas un verbe : `__init__.py` est un
            # marqueur de paquet, et `lplv __init__` ne veut rien dire. Mesuré : c'est le
            # SEUL fichier de l'arbre dans ce cas, et le seul sans résumé -- les deux
            # symptômes désignent la même chose.
            if nom.startswith("_"):
                continue
            v = Verbe(nom=nom, chemin=f, langage=langage, resume=resume_de(f),
                      verifie=expose(f, "--verifier"), donne_json=expose(f, "--json"))
            if nom in par_nom:
                doubles.append((nom, par_nom[nom].chemin, f))
                continue
            par_nom[nom] = v
    if doubles:
        detail = " ; ".join(f"{n} : {a.relative_to(racine)} et {b.relative_to(racine)}"
                            for n, a, b in doubles)
        raise VerbeAmbigu(f"{len(doubles)} nom(s) revendiqué(s) deux fois — {detail}")
    return sorted(par_nom.values(), key=lambda v: v.nom)


def trouver(verbes: list[Verbe], nom: str) -> Verbe | None:
    """Le verbe portant ce nom, ou `None`."""
    for v in verbes:
        if v.nom == nom:
            return v
    return None


def proches(verbes: list[Verbe], nom: str, combien: int = 5) -> list[str]:
    """Les noms les plus proches, pour qu'une faute de frappe ne rende pas une liste de 190."""
    import difflib
    tous = [v.nom for v in verbes]
    approx = difflib.get_close_matches(nom, tous, n=combien, cutoff=0.5)
    sous = [n for n in tous if nom and nom in n and n not in approx]
    return (approx + sous)[:combien]


def commande(v: Verbe, arguments: list[str]) -> list[str]:
    """La ligne de commande qui lance ce verbe, sans l'exécuter.

    ⚠ `--project` pointe la RACINE : c'est l'environnement qui porte PIL, numcodecs, numpy,
    scipy et tifffile. Les emprunts à `inference/` ont coûté une conclusion fausse sur le
    rouleau, faute d'un `numcodecs` dans l'environnement emprunté.
    """
    if v.langage == "python":
        return ["uv", "run", "--project", str(RACINE), "python", str(v.chemin), *arguments]
    return ["bash", str(v.chemin), *arguments]


def aide(verbes: list[Verbe], racine: Path = RACINE) -> str:
    """`lplv --help` : les verbes et leur résumé, groupés par dossier."""
    largeur = max((len(v.nom) for v in verbes), default=0)
    lignes = [f"lplv — {len(verbes)} verbes découverts dans l'arbre.", "",
              "  lplv <verbe> [options]     lance le verbe",
              "  lplv <verbe> --help        SON aide, produite par lui-même",
              "  lplv --verbes [--json]     la liste, brute",
              "  lplv --version            de quel palier il s'agit", ""]
    par_dossier: dict[str, list[Verbe]] = {}
    for v in verbes:
        par_dossier.setdefault(str(v.chemin.parent.relative_to(racine)), []).append(v)
    for dossier in sorted(par_dossier):
        lignes.append(f"{dossier}/")
        for v in par_dossier[dossier]:
            marques = ("v" if v.verifie else " ") + ("j" if v.donne_json else " ")
            resume = v.resume if len(v.resume) <= 96 else v.resume[:95] + "…"
            lignes.append(f"  {marques} {v.nom:<{largeur}}  {resume}")
        lignes.append("")
    lignes.append("  v = auto-test (--verifier)   j = sortie JSON (--json)")
    return "\n".join(lignes)


RECENSEMENT = RACINE / "docs/verbes.json"
"""Le recensement produit par `lplv --verbes --json`. ⚠ Il n'est PAS la source de vérité des
verbes -- le système de fichiers l'est -- il sert uniquement à distinguer « inconnu » de
« absent de ce palier », ce qu'un arbre allégé ne peut pas savoir tout seul."""


def familles_presentes(verbes: list[Verbe], racine: Path = RACINE) -> list[str]:
    """Les dossiers d'où viennent réellement les verbes de CE build."""
    return sorted({str(v.chemin.parent.relative_to(racine)) for v in verbes})


def connu_ailleurs(nom: str, recensement: Path = RECENSEMENT) -> str | None:
    """Le dossier où ce verbe vivait dans l'arbre complet, ou `None` s'il n'a jamais existé."""
    if not recensement.is_file():
        return None
    try:
        for v in json.loads(recensement.read_text(encoding="utf-8")):
            if v.get("nom") == nom:
                return str(Path(v["chemin"]).parent)
    except (ValueError, KeyError, OSError):
        return None
    return None


def version(verbes: list[Verbe], racine: Path = RACINE) -> str:
    """⚠ Dit DE QUEL palier il s'agit : sans ça, un rapport de panne ne permet pas de savoir
    quel programme a tourné, et on débogue le mauvais (skill `doc-derivee`)."""
    return f"lplv · {len(verbes)} verbes · familles : {', '.join(familles_presentes(verbes, racine))}"


def verifier() -> int:
    """Auto-test hors ligne."""
    import shutil
    import tempfile
    echecs = controles = 0

    def v(nom: str, ok: bool) -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}")

    d = Path(tempfile.mkdtemp())
    (d / "src" / "mesures").mkdir(parents=True)
    (d / "src" / "outils").mkdir()

    py = d / "src" / "mesures" / "mesurer_un_truc.py"
    py.write_text('#!/usr/bin/env python3\n"""Mesurer un truc, en une phrase.\n\nEt le detail apres.\n"""\n'
                  'import argparse\np = argparse.ArgumentParser()\np.add_argument("--verifier")\n',
                  encoding="utf-8")
    sh = d / "src" / "outils" / "lancer_un_truc.sh"
    sh.write_text('#!/usr/bin/env bash\n# Lancer un truc, en une phrase.\n# Et le detail apres.\nset -u\n'
                  'if [ "${1:-}" = "--json" ]; then echo x; fi\n', encoding="utf-8")
    muet = d / "src" / "mesures" / "sans_docstring.py"
    muet.write_text("#!/usr/bin/env python3\nimport sys\n", encoding="utf-8")
    prive = d / "src" / "mesures" / "__init__.py"
    prive.write_text('"""paquet"""\n', encoding="utf-8")

    v("le resume python est la premiere ligne de docstring",
      resume_de(py) == "Mesurer un truc, en une phrase.")
    v("le resume shell est la premiere ligne du bandeau",
      resume_de(sh) == "Lancer un truc, en une phrase.")
    v("un fichier sans docstring rend une chaine vide, pas une erreur", resume_de(muet) == "")
    v("un fichier absent aussi", resume_de(d / "nexiste_pas.py") == "")

    v("l'option declaree en python est vue", expose(py, "--verifier"))
    v("... et celle qui ne l'est pas ne l'est pas", not expose(py, "--json"))
    v("l'option declaree en shell est vue", expose(sh, "--json"))
    v("... et celle qui ne l'est pas ne l'est pas", not expose(sh, "--verifier"))

    verbes = decouvrir(d)
    noms = [x.nom for x in verbes]
    v("les deux familles sont decouvertes",
      noms == ["lancer_un_truc", "mesurer_un_truc", "sans_docstring"])
    v("un nom qui commence par _ n'est PAS un verbe", "__init__" not in noms)
    v("le langage est celui du fichier",
      trouver(verbes, "lancer_un_truc").langage == "shell"
      and trouver(verbes, "mesurer_un_truc").langage == "python")
    v("la liste est triee", noms == sorted(noms))

    # ⚠⚠ Le controle central : deux fichiers qui revendiquent un nom sont une ambiguite
    # SILENCIEUSE -- `lplv x` lancerait celui que le systeme de fichiers a mis devant. Refuse.
    (d / "src" / "outils" / "mesurer_un_truc.py").write_text('"""Un homonyme."""\n', encoding="utf-8")
    try:
        decouvrir(d)
        v("un nom revendique deux fois est REFUSE", False)
        v("... et le refus nomme les deux fichiers", False)
    except VerbeAmbigu as e:
        v("un nom revendique deux fois est REFUSE", True)
        v("... et le refus nomme les deux fichiers",
          "src/mesures/mesurer_un_truc.py" in str(e) and "src/outils/mesurer_un_truc.py" in str(e))
    (d / "src" / "outils" / "mesurer_un_truc.py").unlink()
    verbes = decouvrir(d)

    # ⭐ La propriete qui fait qu'un palier allege reste utilisable : une famille dont le
    # dossier n'existe pas rend ZERO verbe, sans erreur. La release ne porte ni
    # `experiments/src` ni `inference_xpu/src` ; un point d'entree qui exigerait leur presence
    # y serait mort, et un palier mort est celui qui pourrit (skill §7).
    v("une famille absente ne casse rien, elle rend zero verbe",
      len(decouvrir(d)) == 3 and not (d / "experiments").exists())

    v("un verbe inconnu ne se trouve pas", trouver(verbes, "nexiste_pas") is None)
    v("une faute de frappe suggere le bon", "mesurer_un_truc" in proches(verbes, "mesurer_un_truk"))

    c = commande(trouver(verbes, "mesurer_un_truc"), ["--json", "x.json"])
    v("un verbe python passe par uv depuis la RACINE",
      c[:4] == ["uv", "run", "--project", str(RACINE)] and c[4] == "python")
    v("... et ses arguments sont a la fin, dans l'ordre", c[-2:] == ["--json", "x.json"])
    c = commande(trouver(verbes, "lancer_un_truc"), ["--verifier"])
    v("un verbe shell passe par bash", c[0] == "bash" and c[-1] == "--verifier")

    # ⭐ La propriete qui rend l'aide inperissable : TOUT ce qui suit le verbe part verbatim,
    # y compris `--help` et `--json`. Si `lplv` mangeait l'un des deux, il faudrait ecrire une
    # seconde aide a cote de celle du module -- exactement ce que ce fichier existe pour eviter.
    for passant in (["--help"], ["--json"], ["--verifier"], ["--help", "--json"], []):
        c = commande(trouver(verbes, "mesurer_un_truc"), passant)
        if c[len(c) - len(passant):] != passant:
            v(f"les arguments {passant} passent verbatim", False)
            break
    else:
        v("--help, --json et --verifier passent VERBATIM au verbe", True)

    # --- ce que `doc-derivee` exige d'un palier allégé ---
    # ⚠⚠ « inconnu » et « absent de ce palier » ne se disent pas pareil et ne SORTENT pas
    # pareil : confondre les deux fait échouer quelqu'un qui a suivi la doc.
    recensement = d / "recensement.json"
    recensement.write_text(json.dumps([
        {"nom": "mesurer_un_truc", "chemin": "src/mesures/mesurer_un_truc.py"},
        {"nom": "parti_ailleurs", "chemin": "experiments/src/excision/parti_ailleurs.py"},
    ]), encoding="utf-8")
    v("un verbe du recensement absent d'ici est LOCALISÉ",
      connu_ailleurs("parti_ailleurs", recensement) == "experiments/src/excision")
    v("un nom qui n'a jamais existé rend None",
      connu_ailleurs("jamais_vu", recensement) is None)
    v("sans recensement, on ne prétend rien savoir",
      connu_ailleurs("parti_ailleurs", d / "absent.json") is None)
    v("un recensement illisible ne fait pas planter",
      connu_ailleurs("x", py) is None)

    v("la version dit de quel palier il s'agit",
      "3 verbes" in version(verbes, d) and "src/mesures" in version(verbes, d))
    v("... et nomme les familles réellement présentes",
      familles_presentes(verbes, d) == ["src/mesures", "src/outils"])

    texte = aide(verbes, d)
    v("l'aide nomme chaque verbe", all(x.nom in texte for x in verbes))
    v("... et porte son resume", "Mesurer un truc, en une phrase." in texte)
    v("... et compte les verbes", f"{len(verbes)} verbes" in texte)
    v("... et distingue ceux qui s'auto-testent", "v = auto-test" in texte)

    shutil.rmtree(d, ignore_errors=True)

    # --- contre le VRAI arbre : ce que le chantier revendique ---
    reels = decouvrir()
    v("l'arbre reel ne porte AUCUN nom ambigu", len(reels) > 150)
    v("... et chaque verbe a un resume", all(x.resume for x in reels))
    v("... dont ceux qui s'auto-testent sont une part connue",
      sum(1 for x in reels if x.verifie) > 80)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    argv = sys.argv[1:]
    if argv and argv[0] == "--verifier":
        return verifier()

    try:
        verbes = decouvrir()
    except VerbeAmbigu as e:
        print(f"lplv : {e}", file=sys.stderr)
        return 2

    if argv and argv[0] in ("--version", "-V"):
        print(version(verbes))
        return 0

    if not argv or argv[0] in ("-h", "--help"):
        print(aide(verbes))
        return 0

    if argv[0] == "--verbes":
        if "--json" in argv:
            print(json.dumps([{"nom": v.nom, "chemin": str(v.chemin.relative_to(RACINE)),
                               "langage": v.langage, "resume": v.resume,
                               "verifie": v.verifie, "json": v.donne_json} for v in verbes],
                             indent=1, ensure_ascii=False))
        else:
            for v in verbes:
                print(v.nom)
        return 0

    nom, reste = argv[0], argv[1:]
    v = trouver(verbes, nom)
    if v is None:
        # ⚠⚠ « inconnu » et « absent de CE palier » sont deux faits différents, et les
        # confondre fait échouer quelqu'un qui a suivi la doc (skill `doc-derivee`). Le
        # recensement, produit par `lplv` lui-même et emporté par la release, sait lequel
        # des deux c'est -- sans lui, on ne peut que le taire.
        ailleurs = connu_ailleurs(nom)
        if ailleurs is not None:
            print(f"lplv : « {nom} » existe, mais son dossier n'est pas dans ce palier "
                  f"({ailleurs}).", file=sys.stderr)
            print(f"  Ce palier porte : {', '.join(familles_presentes(verbes))}.",
                  file=sys.stderr)
            return 3
        print(f"lplv : verbe inconnu « {nom} »", file=sys.stderr)
        suggestions = proches(verbes, nom)
        if suggestions:
            print("  vouliez-vous dire : " + ", ".join(suggestions), file=sys.stderr)
        print("  `lplv --help` liste les verbes.", file=sys.stderr)
        return 2

    # ⚠⚠ `exec` et non `subprocess` : le verbe REMPLACE ce processus, donc son code de sortie,
    # ses signaux et son terminal sont les siens. Un sous-processus ajouterait un maillon qui
    # peut avaler un Ctrl-C ou un code de retour, et un code de retour avale est exactement ce
    # qui fait lire un echec comme un succes.
    ligne = commande(v, reste)
    os.execvp(ligne[0], ligne)
    return 127


if __name__ == "__main__":
    sys.exit(main())
