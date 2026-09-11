#!/usr/bin/env python3
"""Enchaine des verbes et OBSERVE ce que chacun ecrit — le pipeline que `lplv` ne savait pas faire.

⚠⚠⚠ POURQUOI CE FICHIER EXISTE, ET CE QU'IL RESOUT AU PASSAGE. `lplv` nomme cent quatre-vingt-dix
greffons et **n'en compose aucun** : il lance UN verbe, avec `os.execvp`, donc le verbe remplace le
processus. Il n'existait aucun moyen de dire « enchaine ceci, puis cela, et arrete-toi a la
premiere panne ». C'est la moitie absente de l'architecture, et `87` l'a mesuree.

⭐⭐⭐ ET IL RESOUT LA PROVENANCE SANS AUCUNE DECLARATION. `87` mesure que la garde
`artefacts_orphelins` declare « 0 orphelin » avec **46 % de son verdict reposant sur une tige de
douze caracteres ou moins** — `juge_scroll4.json` est declare produit parce que le mot `juge`
apparait quelque part. Le remede evident etait de faire DECLARER a chaque module ce qu'il produit,
et la mesure a montre que ca demanderait **314 motifs ecrits a la main** sur 486 artefacts — donc
une seconde description, libre de deriver. Une chaine qui tourne fait mieux : elle **OBSERVE**
quel verbe a ecrit quel fichier. La provenance devient un fait mesure, sans un mot a maintenir.

⚠⚠ `subprocess` ET NON `os.execvp`, et la difference est deliberee. `lplv <verbe>` utilise
`execvp` exactement pour que le code de sortie, les signaux et le terminal soient ceux du verbe —
sa docstring l'explique. Une chaine ne peut pas : un processus remplace ne revient jamais, donc
un seul etage tournerait. Le prix est un maillon de plus qui pourrait avaler un code de retour,
et c'est pourquoi le code de sortie de chaque etage est **enregistre** plutot que consulte au vol.

⚠⚠⚠ LA CHAINE ENTIERE EST VALIDEE AVANT QUE LE PREMIER ETAGE NE TOURNE. Une faute de frappe a la
cinquieme ligne ne doit pas couter les quatre etages du dessus : c'est le seul endroit ou un
lanceur peut etre poli, et ne pas le faire transforme une coquille en perte de temps de calcul.

⚠⚠ CE QUI N'EST PAS FAIT, ET POURQUOI. Ni parallelisme, ni cache, ni reprise, ni reessai. Le
skill `concevoir-avant-coder` §2 est explicite : une couche se construit quand un COMPTEUR montre
ce que la couche du dessous laisse passer. Ce fichier compte donc les etages, leur duree et leurs
artefacts, et les couches viendront de ces chiffres — ou ne viendront pas. Construites d'avance,
on obtiendrait cinq couches dont trois ne servent jamais et qu'on ne peut plus retirer.

⚠ La portee de l'observation est un PARAMETRE et elle est ecrite dans l'enregistrement : `data/`
porte 168 Gio et 98 275 fichiers, donc l'inventorier couterait plus que les etages eux-memes. Un
etage qui n'ecrit que dans `data/` est donc rapporte « rien ecrit **parmi les racines
observees** », jamais « rien ecrit » — un rapport qui tairait sa portee mentirait.

Format d'une chaine — une ligne par etage, `#` et lignes vides ignorees :

    # docs/chaines/exemple.chaine
    le-sens-du-rang --telecharger
    la-demi-feuille-par-objet --json docs/mesures/la_demi_feuille_par_objet.json
    figure-le-sens-du-rang --verifier

Usage :
    uv run python src/depot/enchainer.py --verifier
    uv run python src/depot/enchainer.py docs/chaines/exemple.chaine
    uv run python src/depot/enchainer.py docs/chaines/exemple.chaine --sec
    uv run python src/depot/enchainer.py docs/chaines/exemple.chaine \\
        --json docs/mesures/enchainer_exemple.json
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "depot"))

# ⚠ Les racines OBSERVEES par defaut. `docs/` porte les artefacts et les figures, c'est-a-dire
# ce qu'une chaine produit de publiable. `data/` en est absent DELIBEREMENT : 98 275 fichiers et
# 168 Gio, donc son inventaire couterait plus que les etages.
RACINES_OBSERVEES = ("docs",)
# ⚠ Ce qu'on ne traverse pas en inventoriant : un `.venv` ou un `__pycache__` change a chaque
# run pour des raisons qui n'ont rien a voir avec l'etage, et les compter ferait rapporter des
# artefacts a tous les etages.
IGNORES = (".venv", "__pycache__", ".git", "repos")


class ChaineInvalide(RuntimeError):
    """La chaine ne peut pas tourner, et on le sait AVANT d'avoir lance un etage."""


@dataclass(frozen=True)
class Etage:
    """Un etage : un verbe, ses arguments, et la ligne d'ou il vient."""

    ligne: int
    verbe: str
    arguments: tuple[str, ...]


@dataclass
class Resultat:
    """Ce qu'un etage a fait — y compris quand il n'a rien fait."""

    etage: Etage
    code: int
    secondes: float
    ecrits: list[str] = field(default_factory=list)
    modifies: list[str] = field(default_factory=list)


def lire_chaine(chemin: Path) -> list[Etage]:
    """Les etages d'un fichier de chaine, dans l'ordre.

    ⚠ Le numero de ligne est CONSERVE, parce que c'est la seule chose qui permette de dire ou
    une chaine est fausse. Un message qui nomme le verbe sans sa ligne envoie chercher.
    """
    if not chemin.is_file():
        raise ChaineInvalide(f"chaine introuvable : {chemin}")
    out: list[Etage] = []
    for n, brut in enumerate(chemin.read_text(encoding="utf-8").splitlines(), start=1):
        ligne = brut.split("#", 1)[0].strip()
        if not ligne:
            continue
        morceaux = ligne.split()
        out.append(Etage(ligne=n, verbe=morceaux[0], arguments=tuple(morceaux[1:])))
    if not out:
        raise ChaineInvalide(f"chaine vide : {chemin}")
    return out


def valider(etages: list[Etage], verbes: dict[str, Path]) -> None:
    """Tous les verbes existent-ils ? Leve en NOMMANT la ligne et le verbe fautifs.

    ⚠⚠⚠ APPELE AVANT LE PREMIER ETAGE. Valider au fil de l'eau ferait payer les quatre etages
    du dessus pour une coquille a la cinquieme ligne — et une chaine dure des minutes.
    """
    manquants = [e for e in etages if e.verbe not in verbes]
    if manquants:
        detail = ", ".join(f"ligne {e.ligne} : « {e.verbe} »" for e in manquants)
        raise ChaineInvalide(f"{len(manquants)} verbe(s) inconnu(s) — {detail}")


def inventaire(racines: tuple[str, ...] = RACINES_OBSERVEES,
               base: Path = RACINE) -> dict[str, tuple[int, int]]:
    """L'etat des fichiers observes : taille et date, par chemin relatif.

    ⚠ La date ET la taille : une reecriture qui rend le meme nombre d'octets change la date, et
    une ecriture a la meme seconde change la taille. Un seul des deux laisserait passer une
    moitie des cas.
    """
    out: dict[str, tuple[int, int]] = {}
    for r in racines:
        depart = base / r
        if not depart.is_dir():
            continue
        for p in depart.rglob("*"):
            if not p.is_file() or any(x in p.parts for x in IGNORES):
                continue
            try:
                st = p.stat()
            except OSError:
                continue
            out[str(p.relative_to(base))] = (st.st_size, st.st_mtime_ns)
    return out


def difference(avant: dict, apres: dict) -> tuple[list[str], list[str]]:
    """Ce qui est apparu, et ce qui a change — deux listes et non une.

    ⚠⚠ « CREE » ET « MODIFIE » NE SE DISENT PAS PAREIL. Un etage qui recree un artefact existant
    fait autre chose qu'un etage qui en produit un neuf, et les confondre ferait lire une
    regeneration comme une production.
    """
    crees = sorted(set(apres) - set(avant))
    changes = sorted(k for k in set(apres) & set(avant) if apres[k] != avant[k])
    return crees, changes


def lancer(etage: Etage, chemin: Path, racines: tuple[str, ...],
           sec: bool = False) -> Resultat:
    """Lance un etage et observe ce qu'il a ecrit.

    ⚠ `--sec` ne lance rien : il rend un resultat de code zero sans observation. C'est ce qui
    permet de verifier qu'une chaine est valide sans payer ses minutes — et le resultat le DIT
    (`sec: true` dans l'enregistrement) plutot que de ressembler a un run reussi.
    """
    if sec:
        return Resultat(etage=etage, code=0, secondes=0.0)
    avant = inventaire(racines)
    debut = time.monotonic()
    lignes = ([sys.executable, str(chemin)] if chemin.suffix == ".py"
              else ["bash", str(chemin)]) + list(etage.arguments)
    fini = subprocess.run(lignes, cwd=RACINE, check=False)
    duree = time.monotonic() - debut
    crees, changes = difference(avant, inventaire(racines))
    return Resultat(etage=etage, code=fini.returncode, secondes=round(duree, 2),
                    ecrits=crees, modifies=changes)


def enchainer(chemin: Path, verbes: dict[str, Path],
              racines: tuple[str, ...] = RACINES_OBSERVEES,
              sec: bool = False) -> dict:
    """Lance la chaine, s'arrete a la premiere panne, et rend l'enregistrement du run."""
    etages = lire_chaine(chemin)
    valider(etages, verbes)
    resultats: list[Resultat] = []
    arrete_a = None
    for e in etages:
        r = lancer(e, verbes[e.verbe], racines, sec=sec)
        resultats.append(r)
        if r.code != 0:
            arrete_a = e.ligne
            break
    # ⭐⭐⭐ LA PROVENANCE, OBSERVEE : quel verbe a ecrit quel fichier. Aucune declaration, aucun
    # motif, aucune troncature — un fait du run.
    provenance = {}
    for r in resultats:
        for f in r.ecrits + r.modifies:
            provenance[f] = r.etage.verbe
    # ⚠⚠ UN ETAGE QUI N'A RIEN ECRIT EST NOMME. Le skill l'exige : un repli silencieux
    # transforme une panne en degradation invisible. Ici « rien ecrit » peut etre parfaitement
    # normal (une batterie ne produit rien) — donc c'est RAPPORTE, jamais compte comme un echec.
    # ⚠⚠⚠ ET PAS EN RUN A SEC : rien n'a tourne, donc « n'a rien ecrit » est un FAUX SIGNAL.
    # Ma premiere version listait les six etages d'un run a sec comme muets, ce qui invite a
    # croire que six etages ne produisent rien. Un rapport qui signale l'absence d'un effet
    # qu'il a lui-meme empeche est pire qu'un rapport muet.
    muets = ([] if sec else
             [r.etage.verbe for r in resultats if not r.ecrits and not r.modifies])
    return {
        "chaine": str(chemin.relative_to(RACINE) if chemin.is_relative_to(RACINE) else chemin),
        "sec": sec,
        # ⚠ La portee de l'observation VOYAGE avec le resultat : « rien ecrit » ne veut rien dire
        # sans savoir ou on a regarde.
        "racines_observees": list(racines),
        "etages": len(etages),
        "lances": len(resultats),
        "reussis": sum(1 for r in resultats if r.code == 0),
        "echoues": sum(1 for r in resultats if r.code != 0),
        "non_lances": len(etages) - len(resultats),
        "arrete_a_la_ligne": arrete_a,
        "secondes": round(sum(r.secondes for r in resultats), 2),
        "artefacts_observes": len(provenance),
        "etages_muets": muets,
        "provenance_observee": provenance,
        "detail": [{"ligne": r.etage.ligne, "verbe": r.etage.verbe,
                    "arguments": list(r.etage.arguments), "code": r.code,
                    "secondes": r.secondes, "ecrits": r.ecrits, "modifies": r.modifies}
                   for r in resultats],
    }


def verbes_du_depot() -> dict[str, Path]:
    """Les verbes que `lplv` sait lancer — la MEME decouverte, jamais une seconde.

    ⚠⚠ Deux listes de « quels verbes existent » finiraient par ne pas s'accorder, et une chaine
    qui accepterait un verbe que `lplv` refuse serait un pipeline qu'on ne peut pas rejouer a la
    main. On importe donc `lplv.decouvrir`.
    """
    import lplv  # noqa: PLC0415

    return {v.nom: v.chemin for v in lplv.decouvrir()}


def verifier() -> int:
    import shutil  # noqa: PLC0415
    import tempfile  # noqa: PLC0415

    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  FAIL {nom} — {detail}")

    d = Path(tempfile.mkdtemp(prefix="chaine_"))
    try:
        # --- la lecture du format -----------------------------------------------------------
        f = d / "x.chaine"
        f.write_text("# un commentaire\n\nun-verbe --a 1\n\nautre-verbe  # en fin de ligne\n",
                     encoding="utf-8")
        e = lire_chaine(f)
        v("les commentaires et les lignes vides sont ignorés", len(e) == 2, str(e))
        v("... le verbe et ses arguments sont séparés",
          e[0].verbe == "un-verbe" and e[0].arguments == ("--a", "1"), str(e[0]))
        # ⚠ Le numéro de ligne est la seule chose qui permette de dire OÙ une chaîne est fausse.
        v("... et le numéro de ligne du fichier est conservé",
          (e[0].ligne, e[1].ligne) == (3, 5), str([x.ligne for x in e]))
        # ⚠ Un commentaire en fin de ligne ne doit pas devenir un argument.
        v("un commentaire en fin de ligne n'est pas un argument",
          e[1].arguments == (), str(e[1]))

        vide = d / "vide.chaine"
        vide.write_text("# rien\n\n", encoding="utf-8")
        try:
            lire_chaine(vide)
            v("une chaîne vide est refusée", False, "aucune exception")
        except ChaineInvalide as err:
            v("une chaîne vide est refusée en nommant le fichier", "vide.chaine" in str(err))
        try:
            lire_chaine(d / "jamais.chaine")
            v("une chaîne absente est refusée", False, "aucune exception")
        except ChaineInvalide:
            v("une chaîne absente est refusée", True)

        # --- la validation AVANT le premier étage -------------------------------------------
        # ⚠⚠⚠ C'est la propriété qui rend le lanceur poli : une coquille à la cinquième ligne
        # ne doit pas coûter les quatre étages du dessus.
        try:
            valider(e, {"un-verbe": Path("a.py")})
            v("un verbe inconnu est refusé", False, "aucune exception")
        except ChaineInvalide as err:
            v("un verbe inconnu est refusé AVANT tout lancement", "autre-verbe" in str(err))
            v("... en nommant sa ligne", "ligne 5" in str(err), str(err))
        valider(e, {"un-verbe": Path("a.py"), "autre-verbe": Path("b.py")})
        v("une chaîne dont tous les verbes existent passe la validation", True)

        # --- l'observation -------------------------------------------------------------------
        base = d / "faux"
        (base / "sorties").mkdir(parents=True)
        (base / "sorties" / "deja.json").write_text("1", encoding="utf-8")
        a1 = inventaire(("sorties",), base)
        v("l'inventaire voit un fichier existant", "sorties/deja.json" in a1, str(a1))
        (base / "sorties" / "neuf.json").write_text("2", encoding="utf-8")
        (base / "sorties" / "deja.json").write_text("1234", encoding="utf-8")
        a2 = inventaire(("sorties",), base)
        crees, changes = difference(a1, a2)
        # ⚠⚠ « CRÉÉ » et « MODIFIÉ » sont deux faits différents.
        v("un fichier neuf est vu comme CRÉÉ", crees == ["sorties/neuf.json"], str(crees))
        v("... et un fichier réécrit comme MODIFIÉ", changes == ["sorties/deja.json"],
          str(changes))
        # ⚠ Un `__pycache__` change à chaque run pour des raisons étrangères à l'étage.
        (base / "sorties" / "__pycache__").mkdir()
        (base / "sorties" / "__pycache__" / "x.pyc").write_text("z", encoding="utf-8")
        v("un __pycache__ n'est pas un artefact",
          not any("__pycache__" in k for k in inventaire(("sorties",), base)))
        # ⚠ Une racine absente ne fait pas planter : une chaîne peut observer un dossier qui
        # n'existe pas encore, et c'est le cas normal du premier run.
        v("une racine absente ne lève pas", inventaire(("jamais",), base) == {})

        # --- un vrai run, sur deux étages fabriqués -----------------------------------------
        util = d / "util"
        util.mkdir()
        (util / "ecrit.py").write_text(
            'import pathlib, sys\n'
            'p = pathlib.Path("docs/mesures/_essai_chaine.json")\n'
            'p.parent.mkdir(parents=True, exist_ok=True)\n'
            'p.write_text("{}")\n', encoding="utf-8")
        (util / "muet.py").write_text("import sys\nsys.exit(0)\n", encoding="utf-8")
        (util / "casse.py").write_text("import sys\nsys.exit(7)\n", encoding="utf-8")
        (util / "jamais.py").write_text("raise SystemExit(0)\n", encoding="utf-8")
        vs = {"ecrit": util / "ecrit.py", "muet": util / "muet.py",
              "casse": util / "casse.py", "jamais": util / "jamais.py"}
        # ⚠⚠⚠ LA VALIDATION EN AMONT SE TESTE PAR SON EFFET, PAS PAR SON MESSAGE. Ma première
        # version n'assertait que « l'exception nomme le verbe », et une sonde qui déplaçait la
        # validation DANS la boucle passait les trente contrôles : le premier étage tournait, et
        # rien ne le voyait. Ce qu'il faut asserter est qu'une chaîne invalide n'écrit RIEN.
        temoin = RACINE / "docs" / "mesures" / "_essai_chaine.json"
        if temoin.exists():
            temoin.unlink()
        mauvaise = d / "mauvaise.chaine"
        mauvaise.write_text("ecrit\nverbe-qui-nexiste-pas\n", encoding="utf-8")
        try:
            enchainer(mauvaise, {"ecrit": util / "ecrit.py"})
            v("une chaîne invalide est refusée", False, "aucune exception")
        except ChaineInvalide:
            v("une chaîne invalide est refusée", True)
        v("... et le premier étage n'a PAS tourné, donc rien n'est écrit",
          not temoin.exists(), f"{temoin.name} existe : la validation est arrivée trop tard")

        c = d / "run.chaine"
        c.write_text("ecrit\nmuet\n", encoding="utf-8")
        r = enchainer(c, vs)
        try:
            v("les deux étages tournent", (r["lances"], r["reussis"]) == (2, 2), str(r))
            # ⭐⭐⭐ LA PROVENANCE OBSERVÉE, sans une déclaration.
            v("l'artefact écrit est attribué à l'étage qui l'a écrit",
              r["provenance_observee"].get("docs/mesures/_essai_chaine.json") == "ecrit",
              str(r["provenance_observee"]))
            v("... et il est compté", r["artefacts_observes"] >= 1,
              str(r["artefacts_observes"]))
            # ⚠⚠ UN ÉTAGE MUET EST NOMMÉ, jamais compté comme un échec.
            v("un étage qui n'écrit rien est NOMMÉ", "muet" in r["etages_muets"],
              str(r["etages_muets"]))
            v("... sans être compté comme un échec", r["echoues"] == 0, str(r["echoues"]))
            # ⚠ La portée de l'observation voyage avec le résultat.
            v("le résultat dit où il a regardé",
              r["racines_observees"] == list(RACINES_OBSERVEES), str(r["racines_observees"]))
        finally:
            p = RACINE / "docs" / "mesures" / "_essai_chaine.json"
            if p.exists():
                p.unlink()

        # --- l'arrêt à la première panne ----------------------------------------------------
        c2 = d / "casse.chaine"
        c2.write_text("muet\ncasse\njamais\n", encoding="utf-8")
        r2 = enchainer(c2, vs)
        # ⚠⚠⚠ LA CHAÎNE S'ARRÊTE, et elle dit OÙ. Continuer après une panne ferait travailler
        # les étages suivants sur une entrée qui n'existe pas.
        v("la chaîne s'arrête à la première panne", r2["lances"] == 2, str(r2["lances"]))
        v("... et nomme la ligne où elle s'est arrêtée", r2["arrete_a_la_ligne"] == 2,
          str(r2["arrete_a_la_ligne"]))
        v("... et compte ce qui n'a PAS tourné", r2["non_lances"] == 1, str(r2["non_lances"]))
        v("... et retient le code de sortie de l'étage fautif",
          r2["detail"][1]["code"] == 7, str(r2["detail"][1]))

        # --- le run à sec ---------------------------------------------------------------------
        # ⚠ `--sec` valide sans payer, et le résultat le DIT plutôt que de ressembler à un run.
        r3 = enchainer(c2, vs, sec=True)
        v("un run à sec lance tous les étages sans en exécuter aucun",
          r3["lances"] == 3 and r3["echoues"] == 0, str(r3))
        v("... et l'enregistrement le déclare", r3["sec"] is True)
        v("... et n'observe aucun artefact", r3["artefacts_observes"] == 0)
        # ⚠⚠⚠ ET IL NE SIGNALE PAS D'ETAGES MUETS : rien n'a tourne, donc « n'a rien ecrit »
        # serait un faux signal — celui que ma premiere version emettait sur six etages.
        v("... et ne signale AUCUN étage muet, puisque rien n'a tourné",
          r3["etages_muets"] == [], str(r3["etages_muets"]))
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # --- contre le vrai dépôt ------------------------------------------------------------
    reels = verbes_du_depot()
    # ⚠⚠ LA MÊME DÉCOUVERTE QUE `lplv` : deux listes de verbes finiraient par ne pas s'accorder,
    # et une chaîne qui accepterait un verbe que `lplv` refuse ne serait pas rejouable à la main.
    v("les verbes viennent de la découverte de lplv", len(reels) > 150, str(len(reels)))
    v("... et `enchainer` est lui-même un verbe", "enchainer" in reels,
      "le lanceur de chaîne doit être un greffon comme les autres")

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Une ligne par étage : `<verbe> [arguments…]`. `#` et lignes vides ignorés.")
    p.add_argument("chaine", nargs="?", type=Path, help="le fichier de chaîne à lancer")
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--sec", action="store_true",
                   help="valide la chaîne sans exécuter un seul étage")
    p.add_argument("--observer", nargs="*", default=list(RACINES_OBSERVEES),
                   help="racines dont on observe les écritures (défaut : docs)")
    p.add_argument("--json", type=Path)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if a.chaine is None:
        p.print_help()
        return 2

    try:
        r = enchainer(a.chaine, verbes_du_depot(), tuple(a.observer), sec=a.sec)
    except ChaineInvalide as err:
        print(f"enchainer : {err}", file=sys.stderr)
        return 2

    marque = " (À SEC)" if r["sec"] else ""
    print(f"{r['chaine']}{marque} — {r['lances']}/{r['etages']} étages lancés, "
          f"{r['reussis']} réussis, {r['echoues']} échoués en {r['secondes']} s\n")
    for x in r["detail"]:
        etat = "✅" if x["code"] == 0 else f"⛔ code {x['code']}"
        args = (" " + " ".join(x["arguments"])) if x["arguments"] else ""
        print(f"  {etat}  l.{x['ligne']:<3} {x['verbe']}{args}   {x['secondes']} s")
        for f in x["ecrits"]:
            print(f"         + {f}")
        for f in x["modifies"]:
            print(f"         ~ {f}")
    if r["arrete_a_la_ligne"] is not None:
        print(f"\n⛔ arrêtée à la ligne {r['arrete_a_la_ligne']} — {r['non_lances']} étage(s) "
              "n'ont pas tourné")
    if r["etages_muets"]:
        print(f"\n⚠ {len(r['etages_muets'])} étage(s) n'ont rien écrit parmi "
              f"{', '.join(r['racines_observees'])} : {', '.join(r['etages_muets'])}")
    print(f"\n⭐ provenance OBSERVÉE — {r['artefacts_observes']} artefact(s) attribués à "
          "l'étage qui les a écrits, sans une déclaration")
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False) + "\n")
        print(f"\nécrit : {a.json}")
    return 1 if r["echoues"] else 0


if __name__ == "__main__":
    sys.exit(main())
