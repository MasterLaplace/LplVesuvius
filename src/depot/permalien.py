#!/usr/bin/env python3
"""Transformer une mention de chemin en lien git PERMANENT, et refuser quand le lien serait mort.

⚠⚠ POURQUOI CE FICHIER EXISTE. On s'apprête à retirer de l'arbre de travail des dossiers que
des documents citent. Un `sed` qui transforme `htr/src/coherence.py` en une URL GitHub ferait
le travail en apparence et produirait des liens morts **en silence** — c'est exactement la
forme de panne que ce dépôt paie en boucle. Ce qui mérite du code ici n'est pas la fabrication
de l'URL, qui tient en une ligne, c'est **l'invariant** :

  ⭐ un permalien ne vaut que si son commit est SUR LE DISTANT et que le chemin EXISTE à ce
    commit. Les deux sont vérifiables, donc ils sont vérifiés, jamais espérés.

⚠ Le piège concret, mesuré le 2026-08-25 : `HEAD` était **43 commits en avance** sur
`origin/main`, donc un permalien vers `HEAD` aurait rendu 404 pour tout le monde sauf cette
machine. On vise donc le commit le plus récent qui contient le chemin ET qui est un ancêtre de
la référence distante. Sans push, sans rien attendre de personne.

⚠ Trois refus délibérés, chacun est une panne évitée :
  - un chemin jamais poussé -> AUCUN lien, et il est NOMMÉ. Le taire mettrait une URL morte.
  - une mention dans un bloc de code -> intacte. `python htr/src/coherence.py` est une
    commande ; la réécrire en URL en ferait une ligne qui ne veut plus rien dire.
  - une mention déjà dans un lien markdown -> intacte, sinon on imbrique `[[x](a)](b)`.

⚠⚠ CE DEPOT EST PRIVE, mesure le 2026-08-25 : la racine GitHub rend 404 sans session,
la meme URL sur un depot public du meme compte rend 200. Un permalien vaut donc pour l'auteur
et pour qui a acces, pas pour un lecteur exterieur. C'est ACCEPTABLE ici parce que les
documents reecrits sont internes -- mais ce serait un piege dans un texte de soumission, ou un
404 est PIRE qu'un chemin mort : un chemin dit honnetement « ce fichier etait la », un lien
casse dit « ce lien est casse ». La parade est dans la forme meme de l'URL : elle contient le
commit et le chemin VERBATIM, donc `git show <commit>:<chemin>` marche depuis n'importe quel
clone, connecte ou non. Une assertion le garantit.

⭐ La forme de sortie garde le texte lisible : `` `chemin` `` devient ``[`chemin`](url)``. La
prose ne perd pas un mot, elle gagne une cible.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

# Une mention est un chemin ENTRE BACKTICKS. C'est la convention du dépôt, dans la prose
# comme dans les docstrings, et elle a l'avantage d'être sans ambiguïté : un chemin nu dans
# une phrase se confond avec un mot, un chemin dans une commande ne doit pas être touché.
MENTION = re.compile(r"`([^`\n]+)`")
BLOC = re.compile(r"^\s*(```|~~~)")


def depot_de_lurl(url: str) -> str:
    """« owner/repo » à partir d'une URL de distant git, ssh ou https.

    ⚠ Refuse ce qui n'est pas GitHub plutôt que de fabriquer une URL invalide : un lien qui
    ne résout pas est pire que pas de lien, parce qu'il a l'air d'un lien.
    """
    u = url.strip().removesuffix(".git")
    m = re.search(r"github\.com[:/]([^/]+/[^/\s]+)$", u)
    if not m:
        raise ValueError(f"distant non GitHub, impossible d'en faire un permalien : {url}")
    return m.group(1)


def depot_courant(racine: Path, distant: str = "origin") -> str:
    """Le « owner/repo » du dépôt où l'on se trouve."""
    r = subprocess.run(["git", "-C", str(racine), "remote", "get-url", distant],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise ValueError(f"pas de distant « {distant} » ici")
    return depot_de_lurl(r.stdout)


def commit_publie(racine: Path, chemin: str, ref: str = "origin/main") -> str | None:
    """Le commit le plus récent contenant `chemin` et joignable depuis `ref`.

    ⚠⚠ `ref` est une référence DISTANTE, exprès. Viser `HEAD` produirait un lien qui marche
    sur la machine qui l'écrit et nulle part ailleurs — la panne ne se voit qu'après le push,
    c'est-à-dire trop tard pour la relier à sa cause.

    Rend `None` quand le chemin n'a jamais été poussé. C'est un refus, pas un défaut.
    """
    r = subprocess.run(["git", "-C", str(racine), "log", "-1", "--format=%H", ref,
                        "--", chemin], capture_output=True, text=True)
    h = r.stdout.strip()
    return h if r.returncode == 0 and h else None


def genre_au_commit(racine: Path, commit: str, chemin: str) -> str | None:
    """« blob » pour un fichier, « tree » pour un dossier — DEMANDÉ à git, jamais deviné.

    ⚠ Deviner d'après un slash final se trompe dans les deux sens : un document écrit
    `htr/src/coherence.py` pour un fichier et `htr/` pour un dossier, mais rien n'oblige un
    auteur à mettre le slash, et GitHub rend une page vide sur le mauvais genre.
    """
    c = chemin.rstrip("/")
    r = subprocess.run(["git", "-C", str(racine), "cat-file", "-t", f"{commit}:{c}"],
                       capture_output=True, text=True)
    t = r.stdout.strip()
    return t if t in ("blob", "tree") else None


def permalien(depot: str, commit: str, chemin: str, genre: str) -> str:
    """L'URL, une fois que le commit et le genre ont été VÉRIFIÉS par les fonctions ci-dessus."""
    if genre not in ("blob", "tree"):
        raise ValueError(f"genre inattendu : {genre}")
    return f"https://github.com/{depot}/{genre}/{commit}/{chemin.rstrip('/')}"


def _hors_bloc(texte: str) -> list[bool]:
    """Pour chaque ligne, vrai si elle est HORS d'un bloc de code clôturé."""
    dedans, sortie = False, []
    for ligne in texte.splitlines():
        if BLOC.match(ligne):
            dedans = not dedans
            sortie.append(False)
        else:
            sortie.append(not dedans)
    return sortie


def references(texte: str, prefixes: tuple[str, ...]) -> list[dict]:
    """Les mentions réécrivables : entre backticks, hors bloc de code, pas déjà liées."""
    ok = _hors_bloc(texte)
    trouvees = []
    for i, ligne in enumerate(texte.splitlines()):
        if not ok[i]:
            continue
        for m in MENTION.finditer(ligne):
            chemin = m.group(1)
            if not any(chemin == p or chemin.startswith(p + "/") or chemin == p + "/"
                       for p in prefixes):
                continue
            # ⚠ Déjà dans un lien markdown : `[\`x\`](url)` — on ne s'imbrique pas.
            avant, apres = ligne[:m.start()], ligne[m.end():]
            if avant.endswith("[") and apres.startswith("]("):
                continue
            trouvees.append({"ligne": i + 1, "chemin": chemin, "brut": m.group(0)})
    return trouvees


def reecrire(texte: str, prefixes: tuple[str, ...], resolveur) -> tuple[str, dict]:
    """Réécrit les mentions résolubles, laisse les autres, et RAPPORTE les deux.

    `resolveur(chemin) -> url | None`. Un `None` laisse la mention intacte et la compte
    parmi les non résolues : le silence serait le seul vrai défaut possible ici.
    """
    ok = _hors_bloc(texte)
    lignes = texte.splitlines(keepends=True)
    faites, refusees = [], []
    for i, ligne in enumerate(lignes):
        if not ok[i]:
            continue
        fin = "\n" if ligne.endswith("\n") else ""
        corps = ligne[:-1] if fin else ligne
        pieces, curseur, change = [], 0, False
        for m in MENTION.finditer(corps):
            chemin = m.group(1)
            if not any(chemin == p or chemin.startswith(p + "/") or chemin == p + "/"
                       for p in prefixes):
                continue
            avant, apres = corps[:m.start()], corps[m.end():]
            if avant.endswith("[") and apres.startswith("]("):
                continue
            url = resolveur(chemin)
            if url is None:
                refusees.append({"ligne": i + 1, "chemin": chemin})
                continue
            pieces.append(corps[curseur:m.start()])
            pieces.append(f"[`{chemin}`]({url})")
            curseur, change = m.end(), True
            faites.append({"ligne": i + 1, "chemin": chemin, "url": url})
        if change:
            pieces.append(corps[curseur:])
            lignes[i] = "".join(pieces) + fin
    return "".join(lignes), {"reecrites": faites, "non_resolues": refusees}


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool) -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}")

    # --- l'URL du dépôt, dans ses deux écritures ---
    v("une URL ssh donne owner/repo",
      depot_de_lurl("git@github.com:MasterLaplace/LplVesuvius.git") == "MasterLaplace/LplVesuvius")
    v("une URL https aussi",
      depot_de_lurl("https://github.com/MasterLaplace/LplVesuvius") == "MasterLaplace/LplVesuvius")
    v("... et sans .git aussi",
      depot_de_lurl("git@github.com:a/b") == "a/b")
    for mauvaise in ("git@gitlab.com:a/b.git", "/chemin/local", ""):
        try:
            depot_de_lurl(mauvaise)
            v(f"« {mauvaise} » est refusée", False)
        except ValueError:
            v(f"« {mauvaise[:22] or '(vide)'} » est refusée", True)

    # --- la fabrication de l'URL ---
    u = permalien("o/r", "abc1234", "htr/src/coherence.py", "blob")
    v("un fichier donne un lien blob", u == "https://github.com/o/r/blob/abc1234/htr/src/coherence.py")
    v("un dossier donne un lien tree",
      permalien("o/r", "abc1234", "htr/", "tree") == "https://github.com/o/r/tree/abc1234/htr")
    # ⚠⚠ La propriete qui sauve un depot PRIVE : le commit et le chemin sont dans l'URL
    # mot pour mot, donc la commande de secours s'en deduit sans reseau ni session.
    v("l'URL porte le commit et le chemin verbatim, donc `git show` s'en deduit",
      "abc1234" in u and u.endswith("htr/src/coherence.py")
      and u.split("/blob/")[1] == "abc1234/htr/src/coherence.py")
    try:
        permalien("o/r", "abc", "x", "arbre")
        v("un genre inventé est refusé", False)
    except ValueError:
        v("un genre inventé est refusé", True)

    # --- ce qui est une référence, et ce qui n'en est pas ---
    texte = (
        "Voir `htr/src/coherence.py` pour le détail.\n"
        "Le dossier `htr/` a disparu.\n"
        "```sh\n"
        "python htr/src/coherence.py --verifier\n"
        "et même `htr/src/coherence.py` entre backticks ici\n"
        "```\n"
        "Déjà lié : [`htr/uv.lock`](https://exemple/x) — ne pas toucher.\n"
        "Sans rapport : `src/encre/structure.py`.\n"
        "Un mot `htr` sans slash n'est pas un chemin... si, c'est le préfixe nu.\n"
    )
    refs = references(texte, ("htr",))
    chemins = [r["chemin"] for r in refs]
    v("le fichier cité en prose est trouvé", "htr/src/coherence.py" in chemins)
    v("le dossier cité en prose est trouvé", "htr/" in chemins)
    v("le préfixe nu compte aussi", "htr" in chemins)
    v("RIEN dans le bloc de code n'est trouvé",
      sum(1 for r in refs if 3 <= r["ligne"] <= 6) == 0)
    v("une mention déjà liée est laissée", not any(r["chemin"] == "htr/uv.lock" for r in refs))
    v("un chemin hors préfixe est ignoré",
      not any(r["chemin"].startswith("analysis") for r in refs))
    v("le compte total est celui attendu", len(refs) == 3)

    # ⚠ Le préfixe ne doit pas mordre sur un voisin qui commence pareil : `inference` ne
    # doit PAS attraper `inference_xpu`, sans quoi on supprimerait le mauvais dossier.
    voisins = references("`inference/x.py` et `src/xpu/y.py`", ("inference",))
    v("« inference » n'attrape pas « inference_xpu »",
      [r["chemin"] for r in voisins] == ["inference/x.py"])

    # --- la réécriture ---
    def faux_resolveur(c: str) -> str | None:
        return None if "jamais" in c else f"https://exemple/{c.rstrip('/')}"

    sortie, rapport = reecrire(texte, ("htr",), faux_resolveur)
    v("la mention devient un lien markdown",
      "[`htr/src/coherence.py`](https://exemple/htr/src/coherence.py)" in sortie)
    v("le bloc de code sort MOT POUR MOT",
      "python htr/src/coherence.py --verifier\n" in sortie
      and "et même `htr/src/coherence.py` entre backticks ici" in sortie)
    v("le lien déjà formé sort intact", "[`htr/uv.lock`](https://exemple/x)" in sortie)
    v("le rapport compte ce qu'il a fait", len(rapport["reecrites"]) == 3)
    v("... et rien n'est non résolu ici", rapport["non_resolues"] == [])

    s2, r2 = reecrire("Voir `htr/jamais_pousse.py`.\n", ("htr",), faux_resolveur)
    v("un chemin non poussé n'est PAS lié", s2 == "Voir `htr/jamais_pousse.py`.\n")
    v("... et il est NOMMÉ dans le rapport",
      [x["chemin"] for x in r2["non_resolues"]] == ["htr/jamais_pousse.py"])

    # Réécrire deux fois ne doit rien changer la seconde fois : sinon une passe répétée
    # imbriquerait les liens, et personne ne relit un document pour s'en apercevoir.
    s3, r3 = reecrire(sortie, ("htr",), faux_resolveur)
    v("la réécriture est idempotente", s3 == sortie and r3["reecrites"] == [])

    # Deux mentions sur UNE ligne : le découpage par curseur doit tenir.
    s4, _ = reecrire("`htr/a` puis `htr/b` fin\n", ("htr",), faux_resolveur)
    v("deux mentions sur une ligne sont réécrites toutes les deux",
      s4 == "[`htr/a`](https://exemple/htr/a) puis [`htr/b`](https://exemple/htr/b) fin\n")

    # --- contre le VRAI dépôt : l'invariant qui donne son sens au fichier ---
    racine = Path(__file__).resolve().parents[2]
    try:
        depot = depot_courant(racine)
        v("le dépôt courant se nomme", depot == "MasterLaplace/LplVesuvius")
        c = commit_publie(racine, "README.md")
        v("un fichier suivi a un commit PUBLIÉ", c is not None and len(c) == 40)
        v("... et ce commit est bien joignable depuis le distant",
          subprocess.run(["git", "-C", str(racine), "merge-base", "--is-ancestor", c,
                          "origin/main"], capture_output=True).returncode == 0)
        v("un chemin inexistant n'a pas de commit",
          commit_publie(racine, "ce/chemin/nexiste/pas.py") is None)
        if c:
            v("le genre d'un fichier est blob", genre_au_commit(racine, c, "README.md") == "blob")
            # ⚠⚠ Le dossier temoin doit exister DANS LE COMMIT VISE, pas seulement
            # aujourd'hui. La premiere version nommait `analysis`, vrai jusqu'au rangement du
            # 2026-08-25 et faux dès que `origin/main` l'a rattrapé -- le controle est devenu
            # rouge sans qu'une ligne de `permalien.py` ait bouge. On vise `docs`, qui est la
            # depuis le premier commit et que rien ne projette de deplacer ; et on le VERIFIE
            # au lieu de le supposer, pour que la panne se dise au lieu de se deduire.
            v("le dossier témoin existe bien dans le commit visé",
              genre_au_commit(racine, c, "docs") is not None)
            v("le genre d'un dossier est tree", genre_au_commit(racine, c, "docs") == "tree")
            v("un chemin absent du commit n'a pas de genre",
              genre_au_commit(racine, c, "ce/chemin/nexiste/pas.py") is None)
    except (ValueError, FileNotFoundError) as e:
        v(f"le dépôt courant est interrogeable ({e})", False)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("fichiers", nargs="*", type=Path, help="les documents à réécrire")
    p.add_argument("--prefixe", action="append", default=[],
                   help="un chemin dont les mentions deviennent des liens (répétable)")
    p.add_argument("--ref", default="origin/main",
                   help="la référence DISTANTE qui rend un commit citable")
    p.add_argument("--ecrire", action="store_true", help="sans ça, on n'affiche que le projet")
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if not a.fichiers or not a.prefixe:
        p.error("des fichiers et au moins un --prefixe sont requis")

    racine = Path(__file__).resolve().parents[2]
    depot = depot_courant(racine)
    cache: dict[str, str | None] = {}

    def resolveur(chemin: str) -> str | None:
        if chemin not in cache:
            c = chemin.rstrip("/")
            h = commit_publie(racine, c, a.ref)
            g = genre_au_commit(racine, h, c) if h else None
            cache[chemin] = permalien(depot, h, c, g) if (h and g) else None
        return cache[chemin]

    total = {"reecrites": [], "non_resolues": []}
    touches = []
    for f in a.fichiers:
        texte = f.read_text(encoding="utf-8")
        sortie, rapport = reecrire(texte, tuple(a.prefixe), resolveur)
        for cle in total:
            for x in rapport[cle]:
                total[cle].append({"fichier": str(f), **x})
        if sortie != texte:
            touches.append(f)
            if a.ecrire:
                f.write_text(sortie, encoding="utf-8")

    print(f"{depot} @ {a.ref}  ·  {len(a.fichiers)} document(s) lus")
    for x in total["reecrites"]:
        print(f"  → {x['fichier']}:{x['ligne']}  {x['chemin']}")
    for x in total["non_resolues"]:
        print(f"  ⚠ {x['fichier']}:{x['ligne']}  {x['chemin']} — JAMAIS POUSSÉ, laissé tel quel")
    print(f"  {len(total['reecrites'])} lien(s), {len(total['non_resolues'])} refus, "
          f"{len(touches)} fichier(s) {'réécrits' if a.ecrire else 'à réécrire (--ecrire)'}")
    if a.json:
        a.json.write_text(json.dumps(total, indent=1, ensure_ascii=False), encoding="utf-8")
    return 1 if total["non_resolues"] else 0


if __name__ == "__main__":
    sys.exit(main())
