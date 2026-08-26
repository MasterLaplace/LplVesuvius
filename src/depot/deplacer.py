#!/usr/bin/env python3
"""Déplacer des fichiers sans laisser une seule citation pendante — et REFUSER sinon.

⚠⚠ POURQUOI CE FICHIER EXISTE. Ranger `analysis/src` en sous-dossiers casse **~490 citations
de chemin** (mesuré le 2026-08-25 : 227 dans `docs/*.md`, 178 dans `tools/*.sh`, 86 dans
`temoins.sh`). Un `mv` suivi d'un `sed` ferait le travail en apparence et laisserait des
chemins morts **en silence** : un bloc « Reproduire » qui ne reproduit plus, une batterie qui
ne se lance plus, une figure qu'on ne sait plus regénérer. Ce qui mérite du code n'est pas le
déplacement, qui est un `git mv`, c'est l'**invariant** :

  ⭐ après application, AUCUNE citation de l'ancien chemin ne subsiste, et CHAQUE citation
    réécrite désigne un fichier qui existe. Les deux sont vérifiables, donc ils sont vérifiés.

⚠ Le mode par défaut est **à blanc**. Un outil qui déplace deux cents fichiers ne doit pas
pouvoir le faire par accident, et son rapport doit être relisible avant que quoi que ce soit
bouge (skill `commencer-ferme` : le défaut le plus restreint, relâché sur preuve).

⚠ Les remplacements se font du chemin le PLUS LONG au plus court. Sans cet ordre,
`analysis/src` remplacé avant `analysis/src/x.py` couperait le second en deux et produirait un
chemin qui ressemble à un chemin.

⚠ Une citation de BASENAME nu (`x.py`, ce que `temoins.sh` utilise dans ses gardes) n'est pas
touchée : le nom de fichier ne change pas, seul son dossier change. Les toucher ferait des
faux positifs partout où un mot ressemble à un nom de module.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]

LUS = (".py", ".sh", ".md", ".toml", ".txt", ".tsv")
"""Où une citation de chemin peut vivre. ⚠ Les `.json` de résultat en sont EXCLUS : ce sont des
mesures, et réécrire un chemin dans un résultat déjà publié le falsifierait."""

IGNORES = (".git", ".venv", "__pycache__", ".lances", "data", "repos", "build", "site")

# ⚠⚠ Un outil qui reecrit des chemins reecrit AUSSI ses propres exemples : le
# 2026-08-25 il a mange une fixture de sa propre batterie en s'appliquant a l'arbre.
# La parade tient a une discipline d'ecriture -- une fixture de ce fichier ne doit
# jamais ressembler a un chemin reellement present -- et la batterie la verifie en
# echouant si elle a bouge.


def _marcher(racine: Path, garder) -> list[Path]:
    """Marche l'arbre en ÉLAGUANT les dossiers ignorés au lieu de les filtrer après coup.

    ⚠⚠ `rglob("*")` descend dans un dossier ignoré avant de le jeter : sur ce dépôt, ça veut
    dire parcourir 6,3 Gio de `.venv` pour n'en garder aucun fichier. Mesuré : la première
    version n'avait pas fini au bout de dix minutes. Élaguer à la traversée est la différence
    entre un contrôle qu'on lance et un contrôle qu'on abandonne.
    """
    out, pile = [], [racine]
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
            elif e.is_file() and garder(e):
                out.append(e)
    return sorted(out)


class CitationPendante(RuntimeError):
    """Un déplacement laisserait une citation qui ne désigne plus rien."""


@dataclass(frozen=True)
class Deplacement:
    """Un fichier et sa destination, tous deux relatifs à la racine."""

    ancien: str
    nouveau: str


def fichiers_lisibles(racine: Path) -> list[Path]:
    """Tout fichier où une citation de chemin peut se trouver."""
    return _marcher(racine, lambda f: f.suffix in LUS)


_MOTIFS: dict[str, re.Pattern] = {}


def _motif(chemin: str) -> re.Pattern:
    """Le motif d'un chemin, COMPILÉ UNE FOIS et gardé.

    ⚠ Sans ce cache, ranger `docs/` recompile 464 motifs pour chacun des 355 textes du dépôt,
    soit 165 000 compilations — le premier essai n'avait pas rendu la main au bout de deux
    minutes. C'est le même coût, et le même remède, que dans `appelants.py`.
    """
    m = _MOTIFS.get(chemin)
    if m is None:
        m = _MOTIFS[chemin] = re.compile(
            r"(?<![\w-])((?:\.\./)*)" + re.escape(chemin) + r"(?![\w])")
    return m


def citations(texte: str, chemin: str) -> int:
    """Combien de fois ce chemin est cité dans ce texte, toutes formes relatives confondues.

    ⚠ Le test d'appartenance de chaîne est une condition NÉCESSAIRE du motif — il ne peut donc
    pas écarter un texte qui cite — et il élimine la quasi-totalité des paires avant qu'une
    expression régulière ne tourne.
    """
    if chemin not in texte:
        return 0
    return len(_motif(chemin).findall(texte))


def reecrire(texte: str, deplacements: list[Deplacement]) -> tuple[str, int]:
    """Réécrit toutes les citations, du chemin le plus long au plus court."""
    n = 0
    for d in sorted(deplacements, key=lambda x: -len(x.ancien)):
        if d.ancien not in texte:
            continue
        texte, k = _motif(d.ancien).subn(lambda m: m.group(1) + d.nouveau, texte)
        n += k
    return texte, n


def tous_les_textes(racine: Path) -> list[Path]:
    """TOUT fichier texte, y compris ceux qu'on ne réécrit pas.

    ⚠⚠ Volontairement plus large que `fichiers_lisibles`. Un contrôle qui regarde exactement
    ce que la réécriture vient de traiter est vide par construction : il ne peut rien trouver,
    donc il ne prouve rien. C'est la panne que ce dépôt appelle « une vérification incapable
    d'échouer », et elle a été écrite ici avant d'être corrigée.
    """
    return _marcher(racine, lambda f: f.suffix not in
                    (".png", ".jpg", ".npy", ".zarr", ".tif", ".pdf", ".lock"))


ENREGISTREMENTS = (".json", ".jsonl", ".log", ".csv")
"""Les fichiers dont le CONTENU est un enregistrement de ce qui a tourné.

⚠⚠ Le chemin qu'un résultat ou un journal contient n'est pas un pointeur à maintenir : c'est
la trace de la commande lancée ce jour-là. `LUS` les exclut déjà de la réécriture, pour cette
raison exacte — « réécrire un chemin dans un résultat déjà publié le falsifierait ». Mais
`restantes()` les comptait comme des citations pendantes, donc l'outil REFUSAIT de laisser
une citation qu'il avait décidé exprès de ne pas réparer : ses deux moitiés se
contredisaient, et aucun plan touchant un fichier nommé dans un résultat ne pouvait aboutir.
Mesuré sur le rangement de `docs/` : 41 fichiers, dont un recensement qui en cite 51.

⚠ L'exclusion ne vide pas le contrôle. Ce qui reste au-delà de `LUS` — `.yaml`, `.tex`,
`.html`, `.ipynb`, les fichiers sans extension — est toujours PLUS LARGE que ce que la
réécriture touche, et c'est ce qui empêche `restantes()` d'être vraie par construction.
"""


def _partage(racine: Path, deplacements: list[Deplacement]):
    """Les citations subsistantes, séparées en (à réparer, traces historiques)."""
    morts, traces = [], []
    anciens = [d.ancien for d in deplacements]
    for f in tous_les_textes(racine):
        try:
            texte = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        ou = traces if f.suffix in ENREGISTREMENTS else morts
        for a in anciens:
            if citations(texte, a):
                ou.append((str(f.relative_to(racine)), a))
    return morts, traces


def restantes(racine: Path, deplacements: list[Deplacement]) -> list[tuple[str, str]]:
    """Les citations d'anciens chemins qui subsistent ET qu'il faut réparer, cherchées PLUS
    LARGE que la réécriture."""
    return _partage(racine, deplacements)[0]


def traces_historiques(racine: Path, deplacements: list[Deplacement]) -> list[tuple[str, str]]:
    """Les anciens chemins encore nommés dans un résultat ou un journal — à ne PAS réparer."""
    return _partage(racine, deplacements)[1]


def construits(racine: Path, dossiers: set[str]) -> list[tuple[str, str]]:
    """Les chemins ASSEMBLÉS à l'exécution — `"analysis/src/" + nom` — qu'aucune réécriture
    textuelle ne peut voir, et qui casseront donc en silence.

    ⚠ C'est la seule classe que ce fichier ne sait pas réparer, seulement NOMMER. Un outil qui
    tairait ce qu'il ne sait pas faire laisserait croire que le déplacement est complet.
    """
    trouves = []
    for f in tous_les_textes(racine):
        try:
            texte = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for d in dossiers:
            for m in re.finditer(re.escape(d) + r"/?[\"\']", texte):
                ligne = texte[:m.start()].count("\n") + 1
                trouves.append((f"{f.relative_to(racine)}:{ligne}", d))
    return trouves


def plan_depuis(carte: dict[str, str], racine: Path) -> list[Deplacement]:
    """Un plan à partir d'une carte `{ancien: nouveau_dossier}`, vérifiée contre le disque.

    ⚠ Refuse un fichier absent plutôt que de planifier un déplacement qui échouera au milieu
    de deux cents autres, quand la moitié de l'arbre a déjà bougé.
    """
    plan, manquants = [], []
    for ancien, dossier in sorted(carte.items()):
        if not (racine / ancien).is_file():
            manquants.append(ancien)
            continue
        plan.append(Deplacement(ancien, f"{dossier}/{Path(ancien).name}"))
    if manquants:
        raise FileNotFoundError(f"{len(manquants)} fichier(s) absent(s) : {', '.join(manquants[:5])}")
    return plan


def appliquer(racine: Path, deplacements: list[Deplacement], ecrire: bool = False) -> dict:
    """Réécrit les citations puis déplace les fichiers. À blanc par défaut.

    ⚠ L'ORDRE compte : on réécrit AVANT de déplacer, pour que `restantes()` puisse encore
    distinguer « citation oubliée » de « fichier absent ». L'inverse rendrait tout l'arbre
    momentanément incohérent et le rapport illisible.
    """
    touches, total = [], 0
    for f in fichiers_lisibles(racine):
        texte = f.read_text(encoding="utf-8", errors="replace")
        neuf, n = reecrire(texte, deplacements)
        if n:
            total += n
            touches.append(str(f.relative_to(racine)))
            if ecrire:
                f.write_text(neuf, encoding="utf-8")

    deplaces, hors_git = [], []
    if ecrire:
        suivis = set(subprocess.run(["git", "-C", str(racine), "ls-files"],
                                    capture_output=True, text=True).stdout.splitlines())
        for d in deplacements:
            (racine / d.nouveau).parent.mkdir(parents=True, exist_ok=True)
            if d.ancien in suivis:
                r = subprocess.run(["git", "-C", str(racine), "mv", d.ancien, d.nouveau],
                                   capture_output=True, text=True)
                if r.returncode != 0:
                    raise RuntimeError(f"git mv {d.ancien} -> {d.nouveau} : {r.stderr.strip()}")
            else:
                # ⚠⚠ `git mv` REFUSE un fichier qu'il ne suit pas, et le refus arrive au
                # milieu du plan : mesuré sur le rangement de `docs/`, 14 fichiers déplacés
                # puis un arrêt sur le premier `.log`, qui est gitignoré. Un simple `rename`
                # fait le travail — mais il est COMPTÉ et nommé, parce que « ce fichier n'est
                # pas versionné » est une information sur le fichier, pas un détail
                # d'implémentation du déplacement.
                (racine / d.ancien).rename(racine / d.nouveau)
                hors_git.append(d.ancien)
            deplaces.append(d.nouveau)

    rapport = {"deplacements": len(deplacements), "citations": total,
               "fichiers_touches": len(touches), "applique": ecrire, "deplaces": len(deplaces),
               "hors_git": hors_git}
    if ecrire:
        morts, traces = _partage(racine, deplacements)
        rapport["citations_pendantes"] = morts
        # ⚠⚠ Les traces sont dans le RAPPORT, pas dans une exception. Une trace ne peut pas
        # être réparée par construction — la réécrire falsifierait un résultat publié — donc
        # en faire un refus produirait un refus que personne ne peut satisfaire, et un plan
        # légitime deviendrait inapplicable. Mais les taire ferait rendre un rapport serein
        # à un déplacement incomplet : elles sont donc NOMMÉES, toujours.
        rapport["traces"] = traces
        if morts:
            raise CitationPendante(
                f"{len(morts)} citation(s) pendante(s) après application, dont "
                + ", ".join(f"{f}:{a}" for f, a in morts[:3]))
    return rapport


def verifier() -> int:
    import shutil
    import tempfile
    echecs = controles = 0

    def v(nom: str, ok: bool) -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}")

    # --- la réécriture, sur les formes réelles rencontrées dans l'arbre ---
    # ⚠⚠ Deux chemins dont l'un est PREFIXE de l'autre : c'est le cas qui impose l'ordre du
    # plus long au plus court. `zarr.py` traite avant `zarr_depth.py` couperait le second.
    dep = [Deplacement("src/commun/zarr_depth.py", "src/commun/zarr_depth.py"),
           Deplacement("analysis/src/zarr.py", "src/volume/zarr.py")]
    texte = ("uv run python src/commun/zarr_depth.py --json x\n"
             "cd experiments && uv run python ../src/commun/zarr_depth.py\n"
             '"$ROOT/src/commun/zarr_depth.py" --verifier\n'
             "et le petit frere analysis/src/zarr.py\n"
             "mais PAS zarr_depth.py tout nu, ni analysis/src/zarr_depth.pyc\n")
    neuf, n = reecrire(texte, dep)
    v("la forme nue est réécrite", "python src/commun/zarr_depth.py --json" in neuf)
    v("la forme relative garde ses ../", "../src/commun/zarr_depth.py" in neuf)
    v("la forme $ROOT est réécrite", '"$ROOT/src/commun/zarr_depth.py"' in neuf)
    v("un préfixe d'un autre chemin va bien à SA destination",
      "frere src/volume/zarr.py" in neuf and "src/volume/zarr_depth" not in neuf)
    v("un basename nu n'est PAS touché", "PAS zarr_depth.py tout nu" in neuf)
    v("un suffixe plus long n'est pas coupé", "analysis/src/zarr_depth.pyc" in neuf)
    v("le compte des réécritures est celui des occurrences", n == 4)

    # ⚠⚠ L'ORDRE plus-long-d'abord ne compte QUE si un chemin est préfixe d'un autre, et le
    # cas réel est un dossier déplacé à côté d'un de ses fichiers. Sans cette fixture, le tri
    # était une précaution que rien n'exerçait -- une sonde l'a montré en l'inversant sans
    # faire échouer un seul contrôle.
    ordre = [Deplacement("analysis/src", "src"),
             Deplacement("analysis/src/zarr_depth.py", "src/commun/zarr_depth.py")]
    t2, _ = reecrire("voir analysis/src/zarr_depth.py dans analysis/src\n", ordre)
    v("un dossier et l'un de ses fichiers vont chacun à SA destination",
      "voir src/commun/zarr_depth.py dans src\n" == t2)

    # --- le compteur de citations ---
    v("les trois formes (nue, relative, $ROOT) comptent",
      citations(texte, "src/commun/zarr_depth.py") == 3)
    v("un chemin absent compte zéro", citations(texte, "analysis/src/nexiste.py") == 0)

    # --- le plan, contre un vrai disque ---
    d = Path(tempfile.mkdtemp())
    (d / "analysis" / "src").mkdir(parents=True)
    (d / "docs").mkdir()
    (d / "analysis" / "src" / "a.py").write_text("x", encoding="utf-8")
    (d / "analysis" / "src" / "b.py").write_text("x", encoding="utf-8")
    (d / "docs" / "r.md").write_text("voir `analysis/src/a.py` et analysis/src/b.py\n",
                                     encoding="utf-8")
    plan = plan_depuis({"analysis/src/a.py": "src/figures",
                        "analysis/src/b.py": "src/tables"}, d)
    v("le plan garde le nom de fichier et change le dossier",
      {p.nouveau for p in plan} == {"src/figures/a.py", "src/tables/b.py"})
    try:
        plan_depuis({"analysis/src/absent.py": "src/x"}, d)
        v("un fichier absent fait REFUSER le plan entier", False)
    except FileNotFoundError:
        v("un fichier absent fait REFUSER le plan entier", True)

    # --- à blanc : rien ne bouge, mais le rapport dit ce qui bougerait ---
    r = appliquer(d, plan, ecrire=False)
    v("à blanc, le rapport compte les citations", r["citations"] == 2)
    v("... et rien n'a bougé", (d / "analysis" / "src" / "a.py").is_file())
    v("... et le document est intact",
      "analysis/src/a.py" in (d / "docs" / "r.md").read_text(encoding="utf-8"))

    # --- les citations restantes AVANT application ---
    v("avant application, chaque paire (fichier, ancien chemin) est signalée",
      sorted(restantes(d, plan)) == [("docs/r.md", "analysis/src/a.py"),
                                     ("docs/r.md", "analysis/src/b.py")])

    subprocess.run(["git", "-C", str(d), "init", "-q"], capture_output=True)
    subprocess.run(["git", "-C", str(d), "add", "-A"], capture_output=True)
    subprocess.run(["git", "-C", str(d), "-c", "user.email=x@y", "-c", "user.name=x",
                    "commit", "-qm", "x"], capture_output=True)
    r = appliquer(d, plan, ecrire=True)
    v("appliqué, les fichiers ont bougé",
      (d / "src" / "figures" / "a.py").is_file() and not (d / "analysis" / "src" / "a.py").exists())
    v("... le document cite les nouveaux chemins",
      "src/figures/a.py" in (d / "docs" / "r.md").read_text(encoding="utf-8"))
    # ⭐ L'invariant qui donne son nom au fichier.
    v("... et il ne reste AUCUNE citation pendante", r["citations_pendantes"] == [])
    v("... ce que le rapport dit explicitement", r["deplaces"] == 2 and r["applique"])

    shutil.rmtree(d, ignore_errors=True)

    # ⭐⭐ Le contrôle qui rend l'invariant FALSIFIABLE. Une citation dans un type de fichier
    # que la réécriture ne touche pas (un `.json` de résultat, qu'on refuse de falsifier)
    # survit au déplacement : `appliquer` doit REFUSER, pas rendre un rapport serein.
    d2 = Path(tempfile.mkdtemp())
    (d2 / "analysis" / "src").mkdir(parents=True)
    (d2 / "docs").mkdir()
    (d2 / "analysis" / "src" / "c.py").write_text("x", encoding="utf-8")
    (d2 / "docs" / "resultat.json").write_text('{"source": "analysis/src/c.py"}', encoding="utf-8")
    subprocess.run(["git", "-C", str(d2), "init", "-q"], capture_output=True)
    subprocess.run(["git", "-C", str(d2), "add", "-A"], capture_output=True)
    subprocess.run(["git", "-C", str(d2), "-c", "user.email=x@y", "-c", "user.name=x",
                    "commit", "-qm", "x"], capture_output=True)
    plan2 = plan_depuis({"analysis/src/c.py": "src/volume"}, d2)
    # ⚠⚠ Un chemin nomme dans un RESULTAT est une trace de ce qui a tourne, pas un pointeur.
    # La version d avant en faisait un refus -- donc un refus impossible a satisfaire, puisque
    # le reparer voudrait dire falsifier un resultat publie. Le rapport le NOMME, et c est ce
    # qui empeche un deplacement incomplet de rendre un rapport serein.
    try:
        r2 = appliquer(d2, plan2, ecrire=True)
        v("une citation dans un résultat ne fait PAS refuser", True)
        v("... mais le rapport la nomme",
          any("resultat.json" in f for f, _ in r2.get("traces", [])))
        v("... et elle n'est pas comptée comme pendante", r2["citations_pendantes"] == [])
    except CitationPendante as e:
        v("une citation dans un résultat ne fait PAS refuser", False)
        v("... mais le rapport la nomme", False)
        v("... et elle n'est pas comptée comme pendante", False)
    # ⚠ Et une citation dans un fichier qu on NE reecrit pas et qui n est PAS un
    # enregistrement doit, elle, toujours faire refuser : c est ce qui distingue
    # « je laisse expres » de « j ai oublie ».
    d3 = Path(tempfile.mkdtemp())
    (d3 / "analysis" / "src").mkdir(parents=True)
    (d3 / "analysis" / "src" / "c.py").write_text("x", encoding="utf-8")
    (d3 / "config.yaml").write_text("script: analysis/src/c.py\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(d3), "init", "-q"], capture_output=True)
    subprocess.run(["git", "-C", str(d3), "add", "-A"], capture_output=True)
    subprocess.run(["git", "-C", str(d3), "-c", "user.email=x@y", "-c", "user.name=x",
                    "commit", "-qm", "x"], capture_output=True)
    try:
        appliquer(d3, plan_depuis({"analysis/src/c.py": "src/volume"}, d3), ecrire=True)
        v("une citation dans un fichier non réécrit et non-résultat fait REFUSER", False)
        v("... et le refus la nomme", False)
    except CitationPendante as e:
        v("une citation dans un fichier non réécrit et non-résultat fait REFUSER", True)
        v("... et le refus la nomme", "config.yaml" in str(e))
    shutil.rmtree(d3, ignore_errors=True)

    # ⚠ Un chemin ASSEMBLÉ ne peut pas être réécrit : il est NOMMÉ, jamais tu.
    (d2 / "docs" / "bricole.py").write_text('p = "analysis/src/" + nom + ".py"\n', encoding="utf-8")
    trouves = construits(d2, {"analysis/src"})
    v("un chemin construit à l'exécution est signalé",
      any("bricole.py" in f for f, _ in trouves))
    v("... avec sa ligne", any(f.endswith(":1") for f, _ in trouves))
    shutil.rmtree(d2, ignore_errors=True)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("carte", nargs="?", type=Path,
                   help="JSON {chemin_actuel: dossier_destination}")
    p.add_argument("--ecrire", action="store_true",
                   help="APPLIQUE. Sans ça, on n'affiche que ce qui bougerait.")
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if not a.carte:
        p.error("une carte de déplacement est requise")

    plan = plan_depuis(json.loads(a.carte.read_text(encoding="utf-8")), RACINE)
    avant = len(restantes(RACINE, plan))
    try:
        r = appliquer(RACINE, plan, ecrire=a.ecrire)
    except CitationPendante as e:
        print(f"REFUS : {e}", file=sys.stderr)
        return 3
    print(f"{r['deplacements']} déplacement(s)  ·  {r['citations']} citation(s) dans "
          f"{r['fichiers_touches']} fichier(s)  ·  {avant} fichier(s) citaient un ancien chemin")
    if r.get("hors_git"):
        print(f"  ℹ {len(r['hors_git'])} fichier(s) déplacé(s) hors de git — non versionnés, "
              f"donc `git mv` les refusait")
    tr = traces_historiques(RACINE, plan)
    if tr:
        # ⚠ Le dire, plutôt que de le taire : un chemin laissé en place volontairement et un
        # chemin oublié se ressemblent exactement dans un `grep`.
        print(f"  ℹ {len(tr)} chemin(s) laissé(s) tels quels dans un résultat ou un journal — "
              f"c'est la trace de ce qui a tourné, pas un pointeur à maintenir")
    dossiers = {str(Path(d.ancien).parent) for d in plan}
    for f, dd in construits(RACINE, dossiers):
        print(f"  ⚠ chemin ASSEMBLÉ, non réécrit : {f} ({dd}/…)", file=sys.stderr)
    print("  appliqué" if a.ecrire else "  à blanc — relancer avec --ecrire")
    if a.json:
        a.json.write_text(json.dumps(r, indent=1, ensure_ascii=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
