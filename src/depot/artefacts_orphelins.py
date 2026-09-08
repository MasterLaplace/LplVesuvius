#!/usr/bin/env python3
"""Quel artefact versionne n'a AUCUN producteur dans l'arbre ?

⚠ La regle centrale du depot : *un chiffre publie dont le calcul n'est pas dans l'arbre
n'est pas un resultat, c'est une anecdote.* Elle porte sur les chiffres ; elle vaut aussi
pour les ARTEFACTS qui les portent. Un fichier de mesure versionne dont le script est
reste dans un terminal est un resultat qu'on ne peut ni rejouer, ni verifier, ni corriger.

⚠⚠ Ce script existe parce que le cas s'est produit : `docs/06` §3.2 nomme
`baseline_sweep.py` et `variant_correlate.py` comme les outils d'une mesure, et **aucun
des deux n'est dans l'arbre**. Dix-sept artefacts `docs/sweep_*.jsonl` en dependent.

⚠⚠⚠ ET DEPUIS `88`, CE FICHIER EST UNE ECHELLE D'ESCALADE, PAS UNE HEURISTIQUE UNIQUE.
`87` a mesure ce que valait sa reponse : sur 486 artefacts de `docs/mesures/`, **46 % du
verdict reposait sur une tige de douze caracteres ou moins**, la plus courte a QUATRE --
`juge_scroll4.json` etait declare produit parce que le mot `juge` apparait quelque part dans
`src/`. Une garde dont la moitie du verdict tient a quatre caracteres ne peut pas echouer
sur cette moitie.

⭐⭐⭐ Le remede n'est pas un prefixe plus etroit -- son propre compromis etait deja assume :
chercher le nom exact signalait **389 orphelins sur 568**, et une alerte qui designe les
deux tiers du corpus ne designe rien. Le remede est que la provenance soit **OBSERVEE**.
`lplv enchainer` inventorie les racines surveillees avant et apres chaque etage, donc un
enregistrement de chaine sait quel verbe a ecrit quel fichier. Trois barreaux, par certitude
decroissante :

  1. **OBSERVE** -- un enregistrement de chaine credite ce fichier a un verbe. Certain.
  2. **DEVINE** -- l'heuristique de tige a matche. C'est la DETTE, et elle est chiffree avec
     la longueur de tige qui l'a acceptee.
  3. **ORPHELIN** -- ni l'un ni l'autre. C'est l'alerte.

⚠⚠ L'INVARIANT DE L'ECHELLE (skill `concevoir-avant-coder`) : *un barreau a le droit de
baisser la PRETENTION du resultat, jamais de baisser la BARRE, et jamais en silence.* Ce
fichier disait « produit » pour les barreaux 1 et 2 indistinctement ; il dit desormais par
QUEL barreau chaque artefact est passe, et publie le compte du barreau 2. **Cette dette ne
peut que retrecir** : chaque chaine ecrite deplace des artefacts du barreau 2 vers le 1.

⚠ La dette n'est PAS une erreur et ne fait PAS echouer la garde : la rendre rouge sur 46 %
du corpus la ferait desapprendre. Ce qui echoue reste un orphelin -- plus, desormais, une
incoherence de l'echelle elle-meme.

Usage :
    python3 src/depot/artefacts_orphelins.py [--verifier]
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
# ⚠ `src/excision` en fait partie : `docs/11` nomme
# `src/excision/sensibilite_centre.py`, et l'omettre faisait signaler comme
# orphelin un artefact parfaitement produit. Une liste de sources trop etroite fabrique
# des faux positifs, et un audit qui en fabrique cesse d'etre lu.
SOURCES = ("src",)
"""⚠ UN seul dossier depuis le repli du 2026-08-26 : `tracecheck/`, `experiments/` et
`inference_xpu/` sont des familles de `src/`. La liste en portait quatre, une par dossier de
premier niveau — qu'elle se reduise a une est le signe que la disposition est juste."""
SUFFIXES = (".json", ".jsonl", ".tsv", ".txt")

# ⚠ En dessous de cette longueur, une tige cesse d'etre un identifiant et devient un mot de la
# langue — `juge`, `onde`, `saut`. Le seuil est DERIVE et non choisi : douze caracteres est la
# longueur du plus court nom de module du depot. Il ne fait echouer RIEN ; il chiffre la dette.
TIGE_CREDIBLE = 12

# ⚠⚠⚠ `src/` EN FAIT PARTIE DEPUIS QUE L'ECHELLE L'A EXIGE, et c'est une reparation
# d'ACCESSIBILITE et non un elargissement de portee. La table `EXEMPTS` exemptait
# `src/outils/repos.tsv` d'un parcours qui ne retenait que `docs/` et `data/` : la decision ne
# protegeait donc RIEN, et un controle neuf l'a dit. Le skill tranche entre « injoignable »
# — un defaut, on repare l'accessibilite — et « rare » — un filet en bon etat. Celle-ci etait
# injoignable.
# ⚠ Le cout est nul, mesure : `git ls-files src/**` ne rend qu'UN fichier a suffixe d'artefact,
# et c'est exactement celui que la table nomme. Le parcours de 430 s est dans la lecture des
# sources, pas dans cette liste.
RACINES_BALAYEES = ("docs/", "data/", "src/")

# ⚠ Ces artefacts sont produits par une chaine externe (VC3D, un outil `vc_*`) ou sont des
# entrees plutot que des sorties. Les exclure est une DECISION, pas un oubli : chacun est
# nomme, et la raison avec.
EXEMPTS = {
    "docs/mesures/excision_samples.tsv": "sortie de l'experience d'excision (src/excision)",
    "src/outils/repos.tsv": "manifeste ecrit a la main, pas une mesure",
}


ELAGUES = (".venv", "__pycache__", ".git", "node_modules")
"""⚠⚠ Ce qu il ne faut PAS traverser. `rglob("*")` descend dans un dossier avant de le
jeter : depuis que les environnements virtuels vivent avec leur code (`src/xpu/.venv`,
6,3 Gio), un parcours non elague lit des dizaines de milliers de fichiers de
`site-packages`. Mesure : ce controle est passe de 90 secondes a **plus de 47 minutes**
sans rien produire de plus. Troisieme fois que ce depot paie `rglob` non elague."""


def provenance_observee(base: Path = RACINE) -> dict[str, str]:
    """Quel verbe a ecrit quel fichier, LU dans les enregistrements de chaine.

    ⭐⭐⭐ C'EST LE PREMIER BARREAU DE L'ECHELLE, et il ne devine rien : `lplv enchainer`
    inventorie les racines surveillees avant et apres chaque etage, donc ce que porte
    l'enregistrement est un fait du run, pas une correspondance de chaine de caracteres.

    ⚠⚠ Un enregistrement qui credite un fichier DISPARU est rendu quand meme, et l'appelant le
    signale : un enregistrement perime continue d'affirmer une provenance, donc le taire
    laisserait la garde s'appuyer sur un fait qui n'est plus vrai.

    ⚠ Le dernier enregistrement gagne, et l'ordre est celui des noms de fichier -- donc stable.
    Deux chaines qui produisent le meme artefact sont un fait normal (une regenere ce que
    l'autre a cree), et il n'y a rien a arbitrer : les deux l'ont bien ecrit.
    """
    out: dict[str, str] = {}
    dossier = base / "docs" / "mesures"
    if not dossier.is_dir():
        return out
    for f in sorted(dossier.glob("enchainer_*.json")):
        try:
            record = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        # ⚠ Un run a SEC n'observe rien par construction : le compter serait crediter une
        # provenance qu'aucune ecriture n'a produite.
        if record.get("sec"):
            continue
        for artefact, verbe in (record.get("provenance_observee") or {}).items():
            out[artefact] = verbe
    return out


def corpus_scripts() -> str:
    parts = []
    for d in SOURCES:
        pile = [RACINE / d]
        while pile:
            dossier = pile.pop()
            try:
                entrees = list(dossier.iterdir())
            except OSError:
                continue
            for f in entrees:
                if f.is_dir():
                    if f.name not in ELAGUES:
                        pile.append(f)
                elif f.suffix in (".py", ".sh"):
                    parts.append(f.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(parts)


def artefacts() -> list[Path]:
    out = subprocess.run(["git", "ls-files"], cwd=RACINE, capture_output=True, text=True)
    return [RACINE / l for l in out.stdout.splitlines()
            if l.startswith(RACINES_BALAYEES) and Path(l).suffix in SUFFIXES]


def nomme_par(nom: str, src: str) -> bool:
    """Le nom, ou la racine dont il derive, apparait-il dans un script ?

    ⚠ Un artefact s'appelle souvent `sweep_PHerc0139.jsonl` alors que le script ecrit
    `sweep_$SCROLL.jsonl`. On teste donc le nom entier, puis des prefixes de plus en plus
    courts, jusqu'a une racine d'au moins quatre caracteres -- en dessous, un prefixe
    matche n'importe quoi et l'heuristique cesserait de pouvoir signaler quoi que ce soit.
    """
    return longueur_du_match(nom, src) is not None


def longueur_du_match(nom: str, src: str) -> int | None:
    """A QUELLE LONGUEUR de tige le match s'est-il produit ? `None` si jamais.

    ⚠⚠⚠ POURQUOI CETTE FONCTION EXISTE A COTE DE `nomme_par`. Un booleen dit « produit » sans
    dire a quel PRIX, et `87` a mesure ce que ce prix vaut : 46 % des verdicts tenaient a douze
    caracteres ou moins, douze d'entre eux a QUATRE. Un match sur le nom entier est une
    provenance ; un match sur quatre caracteres est une coincidence de vocabulaire. La longueur
    est donc rendue, pour que la dette du barreau 2 soit chiffree et non seulement comptee.

    ⚠ `nomme_par` reste la porte booleenne, parce que c'est ce que le verdict demande — et les
    deux passent par ICI, donc elles ne peuvent pas se desaccorder sur ce qu'est un match.
    """
    if nom in src:
        return len(nom)
    tige = Path(nom).stem
    while len(tige) >= 4:
        if re.search(r"\b" + re.escape(tige), src):
            return len(tige)
        coupe = max(tige.rfind("_"), tige.rfind("-"))
        if coupe < 4:
            break
        tige = tige[:coupe]
    return None


def verifier_la_mecanique() -> int:
    """L'echelle et ses deux lecteurs, sur entree FABRIQUEE — en millisecondes.

    ⚠⚠ POURQUOI CETTE FONCTION EST SEPAREE DU PARCOURS. Le parcours coute ~430 secondes ; une
    logique qu'on ne peut exercer qu'en le payant est une logique qu'on n'exerce pas. Ces
    controles ne touchent ni l'arbre ni le disque du depot, donc ils peuvent tourner a chaque
    edition, et ils sortent AVANT que le parcours ne commence.
    """
    import json as _json  # noqa: PLC0415
    import shutil  # noqa: PLC0415
    import tempfile  # noqa: PLC0415

    echecs = controles = 0

    def v(nom: str, cond: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  FAIL {nom} — {detail}")

    faux = 'def mesurer_la_portee(): pass\nchemin = "docs/mesures/le_sens_du_rang.json"'
    # ⭐ La longueur du match EST le prix du verdict : un nom entier est une provenance,
    # quatre caracteres une coincidence de vocabulaire.
    v("un nom complet rend sa longueur entiere",
      longueur_du_match("le_sens_du_rang.json", faux) == 20,
      str(longueur_du_match("le_sens_du_rang.json", faux)))
    v("... une tige tronquee rend la longueur au moment du match",
      longueur_du_match("mesurer_la_portee_du_truc.json", faux) == 17,
      str(longueur_du_match("mesurer_la_portee_du_truc.json", faux)))
    v("... et ce qui ne matche jamais rend None",
      longueur_du_match("zzz_inconnu.json", faux) is None)
    # ⚠⚠ LES DEUX FONCTIONS PASSENT PAR LA MEME, donc elles ne peuvent pas se desaccorder sur
    # ce qu'est un match — c'est pour ca que `nomme_par` delegue au lieu de refaire la boucle.
    v("la porte booleenne s'accorde avec la longueur",
      all(nomme_par(n, faux) == (longueur_du_match(n, faux) is not None)
          for n in ("le_sens_du_rang.json", "zzz_inconnu.json",
                    "mesurer_la_portee_du_truc.json")))
    # ⚠ Le plancher : en dessous de quatre caracteres, un prefixe matche n'importe quoi.
    v("une tige de moins de quatre caracteres n'est jamais essayee",
      longueur_du_match("abc.json", "xxx abc yyy") is None,
      str(longueur_du_match("abc.json", "xxx abc yyy")))

    d = Path(tempfile.mkdtemp(prefix="orph_"))
    try:
        (d / "docs" / "mesures").mkdir(parents=True)
        # ⚠⚠⚠ UN RUN A SEC N'OBSERVE RIEN PAR CONSTRUCTION : le crediter serait affirmer une
        # provenance qu'aucune ecriture n'a produite.
        (d / "docs" / "mesures" / "enchainer_sec.json").write_text(_json.dumps(
            {"sec": True, "provenance_observee": {"docs/mesures/fantome.json": "v"}}),
            encoding="utf-8")
        v("un run a sec ne credite rien", provenance_observee(d) == {},
          str(provenance_observee(d)))
        (d / "docs" / "mesures" / "enchainer_vrai.json").write_text(_json.dumps(
            {"sec": False, "provenance_observee": {"docs/mesures/vrai.json": "le_verbe"}}),
            encoding="utf-8")
        v("un run reel credite son artefact au verbe qui l'a ecrit",
          provenance_observee(d) == {"docs/mesures/vrai.json": "le_verbe"},
          str(provenance_observee(d)))
        # ⚠ Un enregistrement illisible ne doit pas faire tomber la garde : elle vaut mieux
        # degradee d'un enregistrement que muette.
        (d / "docs" / "mesures" / "enchainer_casse.json").write_text("pas du json",
                                                                     encoding="utf-8")
        v("un enregistrement illisible ne fait pas tomber la garde",
          len(provenance_observee(d)) == 1, str(provenance_observee(d)))
        v("l'absence de tout enregistrement rend un dictionnaire vide",
          provenance_observee(d / "nulle_part") == {})
    finally:
        shutil.rmtree(d, ignore_errors=True)

    if echecs:
        print(f"FAILURES ({echecs} failures, {controles} checks) — mécanique, "
              "parcours NON payé")
        return 3
    print(f"  mécanique : {controles} contrôles verts avant le parcours\n")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verifier", action="store_true",
                    help="sortie 3 s'il existe un artefact orphelin non exempte")
    a = ap.parse_args()

    # ⚠⚠⚠ LES CONTROLES SUR ENTREE FABRIQUEE TOURNENT AVANT LE PARCOURS, ET C'EST DELIBERE.
    # Ce garde coute ~430 secondes — mesure par `lplv enchainer` — donc une logique exercable
    # seulement par le parcours complet est une logique que personne ne teste en developpant.
    # Ceux-ci coutent des millisecondes et attrapent les fautes d'echelle avant de payer le
    # parcours ; s'ils echouent, on sort SANS le payer.
    if a.verifier and (rc := verifier_la_mecanique()) != 0:
        return rc

    src = corpus_scripts()
    tous = artefacts()
    observee = provenance_observee()
    orphelins: list[str] = []
    # ⭐⭐⭐ LES TROIS BARREAUX, par certitude decroissante. Ce qui est nouveau n'est pas le
    # verdict — un artefact produit reste produit — mais le fait de dire PAR QUEL BARREAU.
    observes: list[str] = []
    devines: list[tuple[int, str]] = []
    exemptes_vus: list[str] = []
    for f in tous:
        rel = str(f.relative_to(RACINE))
        if rel in EXEMPTS:
            exemptes_vus.append(rel)
            continue
        # --- barreau 1 : OBSERVE. Une chaine a vu ce fichier apparaitre pendant un etage.
        if rel in observee:
            observes.append(rel)
            continue
        # --- barreau 2 : DEVINE, et la longueur de tige qui l'a accepte est retenue.
        # ⚠ Un artefact par SEGMENT s'appelle d'apres l'horodatage du segment, que
        # AUCUN script ne peut contenir -- le script ecrit `<dossier>/<segment>.json`,
        # et c'est le DOSSIER qu'il nomme. Chercher le nom de fichier seul signalait
        # 389 orphelins sur 568, dont la quasi-totalite est produite : une alerte qui
        # designe les deux tiers du corpus ne designe rien.
        L = longueur_du_match(f.name, src)
        if L is not None:
            devines.append((L, rel))
            continue
        if f.parent != RACINE / "docs":
            L = longueur_du_match(f.parent.name, src)
            if L is not None:
                devines.append((L, rel))
                continue
        # --- barreau 3 : ORPHELIN. Ni observe, ni devine.
        orphelins.append(rel)
    # ⚠⚠ UN ENREGISTREMENT PERIME AFFIRME UNE PROVENANCE QUI N'EST PLUS VRAIE. Le taire
    # laisserait la garde s'appuyer dessus ; il est donc compte et nomme.
    # ⚠⚠⚠ ET « DISPARU » SE TESTE SUR LE DISQUE, PAS SUR LA LISTE FILTREE. Ma premiere version
    # comparait les credits de chaine a `tous`, qui ne retient que `SUFFIXES` — donc les trois
    # PNG qu'une chaine venait d'ecrire etaient declares disparus alors qu'ils sont commites.
    # Un fichier qui existe sans etre un artefact GARDE n'est pas un fichier disparu.
    perimes = sorted(k for k in observee if not (RACINE / k).is_file())

    import collections  # noqa: PLC0415

    faibles = [(L, r) for L, r in devines if L <= TIGE_CREDIBLE]
    hist = collections.Counter(L for L, _ in faibles)
    print(f"{len(tous)} artefacts versionnés, {len(EXEMPTS)} exemptés, "
          f"**{len(orphelins)} sans producteur**\n")
    # ⭐⭐⭐ L'ECHELLE, PUBLIEE. Ce que ce fichier ne disait pas : par quel barreau chaque
    # artefact est passe. Un « produit » observe et un « produit » devine sur quatre
    # caracteres etaient la meme ligne.
    print(f"  ⭐ barreau 1 — OBSERVÉ par une chaîne     : {len(observes):>5}")
    print(f"  ⚠  barreau 2 — DEVINÉ par la tige         : {len(devines):>5}"
          f"   (dont {len(faibles)} sur ≤{TIGE_CREDIBLE} caractères)")
    print(f"  ⛔ barreau 3 — ORPHELIN                   : {len(orphelins):>5}")
    if hist:
        print("     longueur de tige acceptée, la dette : "
              + " · ".join(f"{L} car. ×{c}" for L, c in sorted(hist.items())))
    print(f"\n  la dette du barreau 2 ne peut que RÉTRÉCIR : chaque chaîne écrite déplace")
    print("  des artefacts vers le barreau 1. `lplv enchainer --help`")
    for o in sorted(orphelins):
        print(f"\n  ⚠ {o}")
    if perimes:
        # ⚠⚠ Un enregistrement qui crédite un fichier disparu continue d'affirmer une
        # provenance qui n'est plus vraie.
        print(f"\n  ⚠⚠ {len(perimes)} enregistrement(s) de chaîne créditent un fichier "
              "disparu :")
        for k in perimes[:6]:
            print(f"    {k}")
    if EXEMPTS:
        print("\n  exemptés, avec la raison :")
        for k, val in EXEMPTS.items():
            hors = "" if k in exemptes_vus else "   ⚠ hors du parcours : exemption morte"
            print(f"    {k} — {val}{hors}")

    if not a.verifier:
        return 0
    print()
    echecs = 0

    def v(nom: str, cond: bool, detail: str = "") -> None:
        nonlocal echecs
        if not cond:
            echecs += 1
        print(f"  {'✅' if cond else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # ⚠⚠⚠ CE QUI ECHOUE, ET CE QUI NE DOIT PAS. La dette du barreau 2 est PUBLIEE, jamais
    # assertie a zero : la rendre rouge sur 46 % du corpus ferait desapprendre la garde, et son
    # propre compromis l'avait deja etabli. Ce qui echoue est un orphelin — et, desormais, une
    # incoherence de l'echelle elle-meme.
    v("aucun artefact versionné n'est sans producteur", not orphelins,
      f"{len(orphelins)} — " + ", ".join(sorted(orphelins)[:3]))
    # ⭐⭐ L'INVARIANT DE L'ECHELLE : un artefact credite par une chaine ne doit JAMAIS avoir
    # besoin de l'heuristique. Si l'ordre des barreaux etait inverse, la garde devinerait ce
    # qu'elle sait, et la dette publiee serait fausse dans le sens rassurant.
    v("aucun artefact observé n'est passé par la tige",
      not (set(observes) & {r for _, r in devines}),
      str(sorted(set(observes) & {r for _, r in devines})[:3]))
    # ⚠⚠ Un enregistrement perime affirme une provenance qui n'est plus vraie.
    v("aucun enregistrement de chaîne ne crédite un fichier disparu", not perimes,
      f"{len(perimes)} — " + ", ".join(perimes[:3]))
    # ⚠ Et l'echelle doit couvrir TOUT le corpus : un artefact qui ne serait dans aucun
    # barreau aurait ete perdu par le classement lui-meme.
    # ⚠⚠⚠ ET LES EXEMPTES SE COMPTENT PAR CEUX QUI ONT ETE RENCONTRES, pas par la taille de la
    # table. Ma premiere version soustrayait `len(EXEMPTS)` : or `src/outils/repos.tsv` commence
    # par `src/`, et `artefacts()` ne retient que `docs/` et `data/` — il etait donc exempte
    # d'un parcours qui ne l'aurait jamais vu, et le compte tombait a cote d'une unite.
    v("les trois barreaux couvrent tout le corpus, exemptés déduits",
      len(observes) + len(devines) + len(orphelins) == len(tous) - len(exemptes_vus),
      f"{len(observes)}+{len(devines)}+{len(orphelins)} pour "
      f"{len(tous)}-{len(exemptes_vus)} rencontrés")
    # ⭐ ET UNE EXEMPTION QUE LE PARCOURS NE RENCONTRE JAMAIS EST UNE EXEMPTION MORTE : elle
    # laisse croire qu'une decision protege quelque chose alors qu'elle ne protege rien.
    mortes = sorted(set(EXEMPTS) - set(exemptes_vus))
    v("aucune exemption ne porte sur un fichier hors du parcours", not mortes,
      f"{len(mortes)} — " + ", ".join(mortes))
    if echecs:
        return 3
    print(f"\nALL PASS (0 failures, {len(tous)} checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
