#!/usr/bin/env python3
"""Quelle FORME a ce depot ? — le graphe, la retrouvabilite, et ce que les gardes ne voient pas.

⚠⚠⚠ POURQUOI CE FICHIER EXISTE. L'auteur a formule la plainte : *« plein de scripts dans tous les
sens, pas un gros logiciel avec des plugins, des duplicata, des trucs abandonnes qu'on refait
sans le savoir »*. Une plainte se traite avec un chiffre, pas avec un acquiescement — et le
chiffre doit etre RE-MESURABLE, parce que c'est lui qui dira si un refactor a servi.

⭐⭐⭐ ET LA MESURE A TROUVE UN DEFAUT DANS UNE GARDE DU DEPOT. `artefacts_orphelins` declare
« 0 artefact sans producteur » ; son test tronque la tige d'un nom jusqu'a QUATRE caracteres,
donc `juge_inconnu.json` est declare produit parce que le mot `juge` apparait quelque part dans
`src/`. Mesure : **46 % du verdict repose sur une tige de douze caracteres ou moins**. Sa propre
docstring assume le compromis — chercher le nom exact signalait 389 orphelins sur 568, « une
alerte qui designe les deux tiers du corpus ne designe rien » — donc le remede n'est PAS un
prefixe plus etroit : c'est que le producteur soit **DECLARE** au lieu d'etre devine.

⚠⚠ CE FICHIER NE JUGE PAS, IL COMPTE. Un module isole n'est pas forcement mort — une batterie
qui ne lit que le volume n'a rien a importer. Un artefact non retrouvable n'est pas forcement
orphelin. Ce qui est mesure est la **retrouvabilite** et la **connexite**, pas la valeur : le
seul verdict porte est sur la garde, parce qu'une garde qui ne peut pas echouer est un defaut
quel que soit l'etat de ce qu'elle garde.

⚠ Les deux `.venv` sous `src/` et les lanceurs geles sont EXCLUS et comptes a part : les
compter ferait annoncer trente mille modules la ou le depot en a trois cent cinquante.

Usage :
    uv run python src/depot/la_forme_du_depot.py
    uv run python src/depot/la_forme_du_depot.py --verifier
    uv run python src/depot/la_forme_du_depot.py --json docs/mesures/la_forme_du_depot.json
"""

from __future__ import annotations

import argparse
import ast
import collections
import itertools
import json
import re
import statistics
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
MESURES = RACINE / "docs" / "mesures"
# ⚠ Ce qu'on ne traverse pas, et pourquoi : deux environnements virtuels vivent sous `src/` et
# portent ~30 000 fichiers de dependances. Les compter ferait dire « 30 657 modules » d'un depot
# qui en a 355, et c'est exactement le genre de chiffre qui rend un diagnostic inutilisable.
EXCLUS = (".venv", "__pycache__", "node_modules", ".git")
IMPORT = re.compile(r"^\s*(?:from|import)\s+([a-z_][a-z0-9_]*)", re.M)
# ⚠ Ce qui n'est PAS du vocabulaire de domaine : mots-clefs, bibliotheques, contrat de greffon,
# et primitives de dessin. Les garder ferait ressembler toutes les figures entre elles pour la
# seule raison qu'elles dessinent, ce qui est vrai et n'apprend rien.
BRUIT_TECHNIQUE = set("""self args parser main verifier mesurer dessiner prose afficher cond
echecs controles path json numpy argparse pathlib sys collections math subprocess tempfile
tifffile add argument parse store true false action type default help nargs detail exit dumps
loads read text write bytes open exists file glob rglob name stem suffix parent parents resolve
iterdir print sorted list dict tuple float bool round abs min max any all zip enumerate insert
range append extend items keys values format join split strip replace lower upper startswith
endswith mkdir relative asarray array zeros ones concatenate splitlines setdefault group copy
argumentparser rawdescriptionhelpformatter systemexit runtimeerror ndarray astype reshape arange
linspace float32 float64 uint8 uint16 int32 shape size save draw imagedraw image line rectangle
temporarydirectory stderr sortie racine total debut valeurs noms brut meta index""".split())
DEFINITION = re.compile(r"^def ([a-z_][a-z0-9_]*)", re.M)
# ⚠ La longueur PLANCHER de la garde `artefacts_orphelins`, recopiee ici parce que c'est elle
# qu'on mesure. Un desaccord entre les deux serait un diagnostic qui juge autre chose que la
# garde ; le controle verifie qu'elle vaut toujours quatre chez elle.
PLANCHER_TIGE = 4
# ⚠ Le seuil au-dela duquel une tige cesse d'etre une coincidence plausible. Il est DERIVE et
# non choisi : douze caracteres est la longueur du plus court nom de module du depot, donc en
# dessous on matche des mots de la langue et non des identifiants.
TIGE_CREDIBLE = 12


def sous_src() -> list[Path]:
    """Les modules du depot, sans les dependances embarquees."""
    return sorted(p for p in (RACINE / "src").rglob("*.py")
                  if not any(x in p.parts for x in EXCLUS))


def graphe(modules: list[Path]) -> dict:
    """Qui importe qui, parmi les modules du depot.

    ⚠⚠ L'ARETE EST UN IMPORT ET RIEN D'AUTRE. Deux modules qui lisent le meme artefact ne sont
    pas relies : le premier peut disparaitre sans que le second cesse de compiler. Compter cette
    lecture comme une arete ferait paraitre connexe un depot ou rien ne depend de rien.
    """
    noms = {p.stem for p in modules}
    imp = {p.stem: set() for p in modules}
    for p in modules:
        for m in IMPORT.finditer(p.read_text(errors="replace")):
            n = m.group(1)
            if n in noms and n != p.stem:
                imp[p.stem].add(n)
    entrant = collections.Counter()
    for a, bs in imp.items():
        for b in bs:
            entrant[b] += 1
    isoles = sorted(n for n in noms if not imp[n] and entrant[n] == 0)
    return {
        "modules": len(noms),
        "aretes": sum(len(v) for v in imp.values()),
        "sans_dependance": sorted(n for n in noms if not imp[n]),
        "isoles": isoles,
        # ⭐ Le NOYAU DE FAIT : ce que le depot partage reellement, par opposition a ce qu'il
        # devrait partager. C'est la liste qui dit ou une primitive doit remonter.
        "noyau_de_fait": [{"module": n, "importe_par": c} for n, c in entrant.most_common(12)],
    }


def duplication(modules: list[Path]) -> dict:
    """Quels noms de fonction sont definis dans plusieurs modules ?

    ⚠⚠ TOUS LES DOUBLONS NE SONT PAS DES DOUBLONS. `main`, `verifier`, `mesurer`, `dessiner`,
    `prose` sont le CONTRAT de greffon du depot : leur repetition est ce que `lplv` exploite, et
    la supprimer casserait le point d'entree. Ils sont donc nommes et ecartes ici plutot que
    comptes — un diagnostic qui les melangerait annoncerait 338 duplications d'une convention.
    """
    contrat = {"main", "verifier", "mesurer", "dessiner", "prose", "_verifier", "afficher"}
    ou = collections.defaultdict(set)
    for p in modules:
        for m in DEFINITION.finditer(p.read_text(errors="replace")):
            ou[m.group(1)].add(p.stem)
    suspects = {f: sorted(v) for f, v in ou.items()
                if f not in contrat and not f.startswith("__") and len(v) >= 4}
    return {
        "contrat_de_greffon": sorted(contrat),
        "noms_suspects": len(suspects),
        "les_pires": [{"nom": f, "modules": len(v), "ou": v[:6]}
                      for f, v in sorted(suspects.items(), key=lambda kv: -len(kv[1]))[:12]],
    }


def retrouvabilite(modules: list[Path]) -> dict:
    """Un artefact publie est-il retrouvable par son NOM dans le code ?

    ⚠⚠⚠ C'EST LA MESURE QUI JUGE LA GARDE. `artefacts_orphelins` accepte un artefact si une TIGE
    de son nom, tronquee jusqu'a quatre caracteres, apparait dans un script. On refait donc son
    test et on rend **a quelle longueur** le match s'est produit. Un match sur le nom entier est
    une provenance ; un match sur quatre caracteres est une coincidence de vocabulaire.
    """
    src = "\n".join(p.read_text(errors="replace") for p in (RACINE / "src").rglob("*")
                    if p.is_file() and p.suffix in (".py", ".sh")
                    and not any(x in p.parts for x in EXCLUS))

    def longueur_du_match(nom: str) -> int | None:
        if nom in src:
            return len(nom)
        tige = Path(nom).stem
        while len(tige) >= PLANCHER_TIGE:
            if re.search(r"\b" + re.escape(tige), src):
                return len(tige)
            coupe = max(tige.rfind("_"), tige.rfind("-"))
            if coupe < PLANCHER_TIGE:
                break
            tige = tige[:coupe]
        return None

    arts = sorted(MESURES.glob("*.json"))
    exact = faibles = jamais = 0
    hist: collections.Counter = collections.Counter()
    pires: list[tuple[int, str]] = []
    for a in arts:
        L = longueur_du_match(a.name)
        if L is None:
            jamais += 1
            continue
        if L == len(a.name):
            exact += 1
            continue
        hist[L] += 1
        if L <= TIGE_CREDIBLE:
            faibles += 1
            pires.append((L, a.name))
    return {
        "artefacts": len(arts),
        "nom_complet": exact,
        "apres_troncature": len(arts) - exact - jamais,
        "jamais_retrouves": jamais,
        # ⭐⭐⭐ LE CHIFFRE QUI CONDAMNE LA GARDE : la part de son verdict qui repose sur une tige
        # trop courte pour etre un identifiant.
        "sur_tige_peu_credible": faibles,
        "part_peu_credible": round(faibles / max(1, len(arts)), 3),
        "tige_la_plus_courte": min(hist) if hist else None,
        "histogramme_des_tiges": dict(sorted(hist.items())),
        "exemples": [{"tige": L, "artefact": n} for L, n in sorted(pires)[:10]],
    }


def surface(modules: list[Path]) -> dict:
    """Combien de modules exposent le contrat, et combien sont enregistres dans la batterie ?"""
    temoins = (RACINE / "src" / "outils" / "temoins.sh").read_text(errors="replace")
    # ⚠⚠⚠ LE CHEMIN EST ENTRE GUILLEMETS DANS LE SCRIPT, et ma premiere version faisait
    # `Path(champ).name` sur `"$ROOT/src/depot/x.py"` — donc `x.py"`, guillemet compris, et le
    # compte sortait a ZERO. Le controle d'a cote n'assertait que « c'est un entier », donc il
    # a laisse passer un zero qui etait un bug : une verification incapable d'echouer, dans le
    # module qui diagnostique les verifications incapables d'echouer.
    # ⭐ On extrait donc par MOTIF le nom de fichier, sans supposer la forme du chemin.
    lances = set(re.findall(r"([a-z0-9_]+\.py)\"?\s+--verifier", temoins))
    avec_verifier = avec_json = enregistres = 0
    for p in modules:
        t = p.read_text(errors="replace")
        if "--verifier" in t:
            avec_verifier += 1
        if '"--json"' in t or "'--json'" in t:
            avec_json += 1
        if p.name in lances:
            enregistres += 1
    # ⭐⭐ LE MANQUE DE TEST SE LIT PAR DOSSIER ET NON GLOBALEMENT, parce que tous les dossiers
    # n'ont pas la meme obligation : `apprendre/` porte des recits pedagogiques et `outils/` des
    # lanceurs, dont une batterie ne dirait rien. Un pourcentage global melangerait les deux et
    # ferait conclure « le depot n'est pas teste » d'un depot teste a 75 %.
    sans: dict[str, int] = collections.Counter()
    total: dict[str, int] = collections.Counter()
    for p in modules:
        total[p.parent.name] += 1
        if "--verifier" not in p.read_text(errors="replace"):
            sans[p.parent.name] += 1
    return {"modules": len(modules), "exposent_verifier": avec_verifier,
            "exposent_json": avec_json, "enregistres_dans_la_batterie": enregistres,
            # ⚠ Un module qui expose `--verifier` sans etre enregistre est une batterie que
            # personne ne lance : elle passe pour verte en n'ayant jamais tourne.
            "verifiables_non_enregistres": avec_verifier - enregistres,
            "sans_batterie": sum(sans.values()),
            "sans_batterie_par_dossier": [
                {"dossier": d, "sans": c, "total": total[d],
                 "part": round(c / total[d], 2)}
                for d, c in sorted(sans.items(), key=lambda kv: -kv[1])]}


def hors_arbre() -> dict:
    """Ce qui gonfle l'arbre sans etre du depot — compte a part, jamais melange."""
    def compte(motif: str, racine: Path) -> int:
        return sum(1 for p in racine.rglob(motif) if p.is_file())

    venvs = [p for p in (RACINE / "src").rglob(".venv") if p.is_dir()]
    return {
        "venv_sous_src": len(venvs),
        "fichiers_dans_ces_venv": sum(compte("*", v) for v in venvs),
        "lanceurs_geles": compte("*.sh", RACINE / ".lances" / "gel")
        if (RACINE / ".lances" / "gel").is_dir() else 0,
        "json_versionnes": len(subprocess.run(
            ["git", "ls-files", "*.json"], cwd=RACINE, capture_output=True,
            text=True).stdout.splitlines()),
        "json_dans_docs_mesures": len(list(MESURES.glob("*.json"))),
    }


def vocabulaire(chemin: Path) -> set[str]:
    """Les mots de DOMAINE d'un module, lus par l'AST et non par une expression reguliere.

    ⚠⚠⚠ POURQUOI L'AST ET PAS UN GREP. Ce depot a des docstrings enormes en francais : une
    expression reguliere sur le fichier entier rend `pour`, `dans`, `chaque` — les mots de la
    prose fuient dans le vocabulaire et la mesure ne categorise plus rien. L'AST ne voit que les
    identifiants reellement declares ou lus.

    ⚠ Les identifiants composes sont DECOUPES sur le tiret bas, parce que c'est la ou le domaine
    apparait en clair : `ecart_inter_feuilles` porte `ecart`, `inter`, `feuilles`, et garder le
    nom entier ferait de chaque identifiant un mot unique — donc zero recouvrement partout.
    """
    try:
        arbre = ast.parse(chemin.read_text(errors="replace"))
    except SyntaxError:
        return set()
    out: set[str] = set()
    for n in ast.walk(arbre):
        nom = (n.name if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
               else n.id if isinstance(n, ast.Name)
               else n.attr if isinstance(n, ast.Attribute)
               else n.arg if isinstance(n, ast.arg) else None)
        if not nom:
            continue
        for w in nom.lower().lstrip("_").split("_"):
            if len(w) >= 4 and w not in BRUIT_TECHNIQUE and not w.isdigit():
                out.add(w)
    return out


def cohesion(modules: list[Path]) -> dict:
    """Les dossiers correspondent-ils au DOMAINE, ou le coupent-ils en travers ?

    ⭐⭐⭐ C'EST LA MESURE QUI DECIDE S'IL FAUT RE-PARTITIONNER. On compare, par dossier, la
    ressemblance de vocabulaire ENTRE SES MODULES a la ressemblance de ses modules avec le reste
    du depot. Un rapport eleve dit que le dossier est un vrai domaine ; un rapport proche de un
    dit que le nom du dossier ne predit rien.

    ⚠⚠ ET UN RAPPORT SOUS UN EST UN VERDICT : le dossier regroupe des modules qui se ressemblent
    MOINS entre eux qu'avec un module pris au hasard.

    ⚠ L'echantillonnage du « reste » est regulier et non aleatoire — un tirage rendrait un
    chiffre different a chaque run, et une mesure qui bouge sans que le depot bouge ne peut pas
    servir de reference.
    """
    voc = {p: vocabulaire(p) for p in modules}
    voc = {p: v for p, v in voc.items() if len(v) >= 8}

    def jaccard(a: set, b: set) -> float:
        return len(a & b) / max(1, len(a | b))

    par: dict[str, list[Path]] = collections.defaultdict(list)
    for p in voc:
        par[p.parent.name].append(p)
    lignes = []
    for d, ps in sorted(par.items(), key=lambda kv: -len(kv[1])):
        if len(ps) < 3:
            continue
        intra = [jaccard(voc[a], voc[b]) for a, b in itertools.combinations(ps, 2)]
        autres = [q for q in voc if q.parent.name != d]
        inter = [jaccard(voc[a], voc[b]) for a in ps[:14] for b in autres[::7]]
        mi = statistics.median(intra) if intra else 0.0
        me = statistics.median(inter) if inter else 0.0
        lignes.append({"dossier": d, "modules": len(ps),
                       "cohesion_interne": round(mi, 4),
                       "hors_dossier": round(me, 4),
                       "rapport": round(mi / me, 2) if me else None})
    rapports = [x["rapport"] for x in lignes if x["rapport"] is not None]
    return {
        "modules_retenus": len(voc),
        "lignes": lignes,
        "rapport_global": round(
            statistics.median([x["cohesion_interne"] for x in lignes])
            / max(1e-9, statistics.median([x["hors_dossier"] for x in lignes])), 2),
        # ⚠⚠ La cohesion ABSOLUE compte autant que le rapport : 0,04 veut dire que deux modules
        # d'un meme dossier partagent quatre pour cent de leur vocabulaire, donc qu'ils ne
        # partagent pas du code mais REEXPRIMENT chacun un domaine commun.
        "cohesion_mediane_absolue": round(
            statistics.median([x["cohesion_interne"] for x in lignes]), 4),
        "dossiers_sous_le_hasard": [x["dossier"] for x in lignes
                                    if x["rapport"] is not None and x["rapport"] < 1.0],
        "dossiers_a_peine_au_dessus": [x["dossier"] for x in lignes
                                       if x["rapport"] is not None
                                       and 1.0 <= x["rapport"] < 1.3],
        "rapport_min": min(rapports) if rapports else None,
    }


def cles_repetees_du_texte(texte: str, nom_du_module: str) -> list[dict]:
    """Le detecteur lui-meme, sur du TEXTE — donc sondable sans ecrire un fichier."""
    import ast  # noqa: PLC0415
    import collections  # noqa: PLC0415

    try:
        arbre = ast.parse(texte, filename=nom_du_module)
    except SyntaxError:
        return []
    out = []
    for n in ast.walk(arbre):
        if not isinstance(n, ast.Dict):
            continue
        noms = [k.value for k in n.keys
                if isinstance(k, ast.Constant) and isinstance(k.value, str)]
        for cle, combien in collections.Counter(noms).items():
            if combien > 1:
                out.append({"module": nom_du_module, "ligne": int(n.lineno),
                            "cle": str(cle), "fois": int(combien)})
    return out


def cles_repetees(modules: list[Path]) -> dict:
    """Les dictionnaires ecrits avec DEUX FOIS la meme cle — Python garde la seconde, en silence.

    ⚠⚠⚠ POURQUOI CETTE MESURE EXISTE, ET ELLE A UNE DATE. Du 15 au 16 septembre 2026, `suivre`
    rendait un dictionnaire portant `poses_refusees` DEUX FOIS : une fois pour les pas ou la
    machoire n'a pas pu se poser, une fois pour les poses qui se contredisent. La seconde gagnait,
    donc le premier compte n'etait plus publie DU TOUT, et trois modules anterieurs lisaient ce nom
    en attendant l'ancien sens. Rien n'echouait : un nom stable avait change de sens.

    ⚠⚠ CE DEFAUT EST INVISIBLE APRES COUP. Une fois le dictionnaire construit, Python a deja
    efface la premiere valeur : aucune verification sur l'OBJET ne peut le voir. Il ne se trouve
    qu'a la SOURCE, ce qui est exactement ce que cette fonction lit.

    ⚠ Une repetition dont les deux valeurs sont IDENTIQUES est inoffensive, et elle est comptee
    quand meme : c'est la meme faute d'ecriture, et la prochaine main qui en changera une seule
    fera la dangereuse.
    """
    trouvees = []
    for f in modules:
        try:
            texte = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        trouvees += cles_repetees_du_texte(texte, str(f.relative_to(RACINE)))
    return {"combien": len(trouvees), "ou": trouvees}


def mesurer() -> dict:
    mods = sous_src()
    return {"modules_du_depot": len(mods), "graphe": graphe(mods),
            "duplication": duplication(mods), "retrouvabilite": retrouvabilite(mods),
            "surface": surface(mods), "cohesion": cohesion(mods),
            "cles_repetees": cles_repetees(mods), "hors_arbre": hors_arbre()}


def verifier() -> int:
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  FAIL {nom} — {detail}")

    r = mesurer()
    g, d, t, s, h = (r["graphe"], r["duplication"], r["retrouvabilite"],
                     r["surface"], r["hors_arbre"])

    # --- le graphe ---------------------------------------------------------------------------
    v("le dépôt compte quelques centaines de modules, pas des dizaines de milliers",
      300 <= r["modules_du_depot"] <= 600, str(r["modules_du_depot"]))
    v("... et les venv embarqués sont comptés À PART",
      h["fichiers_dans_ces_venv"] > 10_000 and h["venv_sous_src"] >= 1, str(h))
    v("le graphe a des arêtes", g["aretes"] > 0, str(g["aretes"]))
    # ⚠⚠ LE FAIT QUI PORTE LA PLAINTE : un tiers des modules ne touche rien et n'est touché
    # par rien. Ce n'est pas un verdict de mort, c'est une mesure de connexité.
    v("les modules isolés sont comptés et nommés",
      len(g["isoles"]) > 0 and isinstance(g["isoles"][0], str), str(len(g["isoles"])))
    v("le noyau de fait est nommé", len(g["noyau_de_fait"]) > 0
      and g["noyau_de_fait"][0]["importe_par"] > 20, str(g["noyau_de_fait"][:2]))

    # --- la duplication ----------------------------------------------------------------------
    # ⚠⚠ LE CONTRAT DE GREFFON N'EST PAS UNE DUPLICATION, et le confondre annoncerait 338
    # doublons d'une convention que `lplv` exploite.
    v("le contrat de greffon est écarté du compte des doublons",
      all(x not in [y["nom"] for y in d["les_pires"]] for x in d["contrat_de_greffon"]),
      str([y["nom"] for y in d["les_pires"]][:5]))
    v("des noms suspects restent après cet écart", d["noms_suspects"] > 0,
      str(d["noms_suspects"]))

    # --- la retrouvabilité, et le verdict sur la garde --------------------------------------
    v("tous les artefacts de docs/mesures sont examinés", t["artefacts"] > 400,
      str(t["artefacts"]))
    # ⭐⭐⭐ LE VERDICT : une part importante du « 0 orphelin » repose sur une tige trop courte
    # pour être un identifiant. Une garde dont la moitié du verdict tient à quatre caractères
    # ne peut pas échouer sur cette moitié.
    v("une part notable du verdict de la garde repose sur une tige peu crédible",
      t["part_peu_credible"] > 0.25,
      f"{t['part_peu_credible']:.0%} sur ≤{TIGE_CREDIBLE} caractères")
    v("... et la tige la plus courte est au plancher de la garde",
      t["tige_la_plus_courte"] == PLANCHER_TIGE, str(t["tige_la_plus_courte"]))
    # ⚠ Le plancher est RECOPIE de la garde : s'il change chez elle, ce diagnostic mesure autre
    # chose qu'elle sans le dire.
    garde = (RACINE / "src" / "depot" / "artefacts_orphelins.py").read_text(errors="replace")
    v("le plancher de tige recopié ici est encore celui de la garde",
      f"len(tige) >= {PLANCHER_TIGE}" in garde and f"coupe < {PLANCHER_TIGE}" in garde,
      "artefacts_orphelins a changé de plancher")
    v("les exemples les plus faibles sont nommés", len(t["exemples"]) > 0
      and t["exemples"][0]["tige"] == PLANCHER_TIGE, str(t["exemples"][:2]))

    # --- la surface --------------------------------------------------------------------------
    v("la majorité des modules expose le contrat de vérification",
      s["exposent_verifier"] > s["modules"] // 2,
      f"{s['exposent_verifier']}/{s['modules']}")
    # ⚠⚠ UNE BATTERIE NON ENREGISTREE PASSE POUR VERTE EN N'AYANT JAMAIS TOURNE. Le compte est
    # publié plutôt qu'asserti à zéro : beaucoup de modules exposent `--verifier` sans être une
    # batterie du dépôt, et exiger l'égalité serait un contrôle qui ne peut pas passer.
    # ⚠⚠⚠ ET CE CONTROLE DOIT POUVOIR ECHOUER. Sa premiere version n'assertait que « c'est un
    # entier », donc elle a laisse passer un ZERO qui venait d'un bug de decoupage du script de
    # batterie. Le compte est desormais borne par le bas : le depot enregistre plus de deux
    # cents batteries, donc un compte effondre est un defaut de LECTURE et non du depot.
    v("les batteries enregistrées sont réellement comptées",
      s["enregistres_dans_la_batterie"] > 150,
      f"{s['enregistres_dans_la_batterie']} — un compte effondré vient du découpage, "
      "pas du dépôt")
    v("... et l'écart avec les vérifiables reste positif",
      s["verifiables_non_enregistres"] >= 0,
      str(s["verifiables_non_enregistres"]))
    # ⭐⭐ ET LE MANQUE DE TEST EST PUBLIE PAR DOSSIER : un pourcentage global melangerait
    # `apprendre/` — des recits, qu'une batterie ne juge pas — avec `excision/`, ou l'absence
    # est un vrai trou. Confondre les deux fait conclure « pas teste » d'un depot teste a 75 %.
    v("le manque de batterie est publié par dossier",
      len(s["sans_batterie_par_dossier"]) > 3
      and all(0 <= x["part"] <= 1 for x in s["sans_batterie_par_dossier"]),
      str(s["sans_batterie_par_dossier"][:3]))
    v("... et les dossiers légitimement sans batterie sont visibles",
      any(x["dossier"] == "apprendre" and x["part"] == 1.0
          for x in s["sans_batterie_par_dossier"]),
      "apprendre/ porte des récits, pas des mesures")

    # --- la cohésion -------------------------------------------------------------------------
    co = r["cohesion"]
    # ⚠⚠⚠ L'AST EST CE QUI REND LA MESURE POSSIBLE : une expression régulière sur le fichier
    # entier laisserait fuir la prose française des docstrings dans le vocabulaire.
    v("le vocabulaire est lu par l'AST, donc sans la prose",
      "pour" not in BRUIT_TECHNIQUE
      and not (vocabulaire(RACINE / "src" / "depot" / "la_forme_du_depot.py") & {
          "pour", "dans", "chaque", "donc"}),
      "des mots de prose sont entrés dans le vocabulaire")
    v("les dossiers sont comparés au reste du dépôt", len(co["lignes"]) > 8,
      str(len(co["lignes"])))
    # ⭐⭐⭐ LE VERDICT QUI DÉCIDE DU REFACTOR : si les dossiers correspondaient fortement au
    # domaine, re-partitionner serait inutile ; s'ils étaient sous le hasard partout, ce serait
    # urgent. La mesure rend un entre-deux, et c'est ce chiffre qui doit être publié.
    v("le rapport global est publié et modeste",
      1.2 < co["rapport_global"] < 4.0, f"×{co['rapport_global']}")
    # ⚠⚠ ET LA COHÉSION ABSOLUE EST LE FAIT LE PLUS DUR : quatre pour cent de vocabulaire
    # partagé dit que les modules ne partagent pas du code mais réexpriment un domaine.
    v("la cohésion absolue est publiée à côté du rapport",
      0.0 < co["cohesion_mediane_absolue"] < 0.15,
      str(co["cohesion_mediane_absolue"]))
    # ⛔ Un dossier sous le hasard est un verdict, pas une nuance.
    v("un dossier sous le hasard est nommé s'il existe",
      isinstance(co["dossiers_sous_le_hasard"], list)
      and co["rapport_min"] is not None,
      f"min ×{co['rapport_min']} — {co['dossiers_sous_le_hasard']}")

    # --- les cles ecrites deux fois ------------------------------------------------------------
    # ⚠⚠⚠ CE DEFAUT NE SE VOIT QU'A LA SOURCE. Python garde la SECONDE valeur d'une cle repetee,
    # donc une fois le dictionnaire construit la premiere a disparu et aucune verification sur
    # l'objet ne peut la retrouver. Il a coute, du 15 au 16 septembre 2026, un compte qui a cesse
    # d'etre publie sans que rien n'echoue, pendant que trois modules lisaient encore son nom.
    cr = r["cles_repetees"]
    v("aucun dictionnaire du dépôt n'écrit deux fois la même clé",
      cr["combien"] == 0, str(cr["ou"][:3]))
    # ⚠⚠ ET LE DETECTEUR DOIT MORDRE : un controle a zero est aussi ce que rend un detecteur qui
    # ne regarde rien. La sonde est une source FABRIQUEE, donc elle n'ecrit aucun fichier.
    sonde = cles_repetees_du_texte(
        "def f():\n    return {'a': 1, 'b': 2, 'a': 3}\n", "sonde")
    v("... et le détecteur le VOIT quand on lui en donne une",
      len(sonde) == 1 and sonde[0]["cle"] == "a" and sonde[0]["fois"] == 2,
      str(sonde))
    v("... et il ne crie pas sur un dictionnaire sain",
      not cles_repetees_du_texte("def f():\n    return {'a': 1, 'b': 2}\n", "sonde"))

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    a = p.parse_args()
    if a.verifier:
        return verifier()

    r = mesurer()
    g, d, t, s, h = (r["graphe"], r["duplication"], r["retrouvabilite"],
                     r["surface"], r["hors_arbre"])
    print(f"■ LE GRAPHE — {g['modules']} modules, {g['aretes']} arêtes d'import")
    print(f"   {len(g['sans_dependance'])} n'importent aucun module du dépôt "
          f"({len(g['sans_dependance']) / g['modules']:.0%})")
    print(f"   {len(g['isoles'])} ISOLÉS — n'importent rien, ne sont importés par rien "
          f"({len(g['isoles']) / g['modules']:.0%})")
    print("   le noyau de fait :")
    for x in g["noyau_de_fait"][:6]:
        print(f"     {x['importe_par']:>3} × {x['module']}")
    print(f"\n■ LA DUPLICATION — {d['noms_suspects']} noms définis dans 4 modules ou plus, "
          "contrat de greffon écarté")
    for x in d["les_pires"][:8]:
        print(f"   {x['modules']:>3} × {x['nom']:<16} {', '.join(x['ou'][:3])}…")
    print(f"\n■ LA RETROUVABILITÉ — {t['artefacts']} artefacts de docs/mesures/")
    print(f"   {t['nom_complet']:>4} retrouvés par leur nom COMPLET "
          f"({t['nom_complet'] / t['artefacts']:.0%})")
    print(f"   {t['apres_troncature']:>4} seulement après troncature "
          f"({t['apres_troncature'] / t['artefacts']:.0%})")
    print(f"   {t['jamais_retrouves']:>4} jamais retrouvés")
    print(f"   ⚠⚠ {t['sur_tige_peu_credible']} ({t['part_peu_credible']:.0%}) déclarés produits "
          f"sur une tige de ≤{TIGE_CREDIBLE} caractères")
    print(f"   ⚠⚠⚠ la plus courte tige acceptée : {t['tige_la_plus_courte']} caractères — "
          "ex. " + ", ".join(x["artefact"] for x in t["exemples"][:3]))
    print(f"\n■ LA SURFACE — {s['exposent_verifier']}/{s['modules']} exposent `--verifier`, "
          f"{s['exposent_json']} exposent `--json`")
    print(f"   {s['enregistres_dans_la_batterie']} enregistrés dans la batterie, "
          f"{s['verifiables_non_enregistres']} vérifiables non enregistrés")
    print(f"   {s['sans_batterie']} modules sans batterie, par dossier :")
    for x in s["sans_batterie_par_dossier"][:6]:
        print(f"     {x['dossier']:<12} {x['sans']:>3} / {x['total']:>3}  ({x['part']:.0%})")
    co = r["cohesion"]
    print(f"\n■ LA COHÉSION — les dossiers correspondent-ils au domaine ? "
          f"rapport global ×{co['rapport_global']}")
    print(f"   cohésion interne médiane {co['cohesion_mediane_absolue']} — deux modules d'un "
          "même dossier partagent 4 % de leur vocabulaire")
    for x in co["lignes"][:5]:
        print(f"     {x['dossier']:<12} {x['modules']:>3} modules · "
              f"×{x['rapport']}")
    if co["dossiers_sous_le_hasard"]:
        print(f"   ⛔ SOUS LE HASARD : {', '.join(co['dossiers_sous_le_hasard'])} — leurs "
              "modules se ressemblent moins entre eux qu'avec un module au hasard")
    if co["dossiers_a_peine_au_dessus"]:
        print(f"   ⚠ à peine au-dessus : {', '.join(co['dossiers_a_peine_au_dessus'])}")
    print(f"\n■ HORS DÉPÔT, compté à part — {h['venv_sous_src']} venv sous src/ portant "
          f"{h['fichiers_dans_ces_venv']} fichiers · {h['lanceurs_geles']} lanceurs gelés")
    print(f"   {h['json_versionnes']} .json versionnés, dont "
          f"{h['json_dans_docs_mesures']} dans docs/mesures/")
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False) + "\n")
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
