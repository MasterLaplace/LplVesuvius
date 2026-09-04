#!/usr/bin/env python3
"""Ce que la proximité rend quand SEULE la graine du tirage change.

⚠⚠⚠ CE FICHIER EXISTE PARCE QU'UNE FRACTION DONT LE NUMÉRATEUR EST UNE CELLULE N'EST PAS UNE
FRACTION. `reparation_et_proximite.py` rend une table (avant, après) dont la plus grosse
variation vaut **+398 %** — et `1 / 0.0004037 = 2477`, qui est exactement le nombre de cellules
`usable` de ce maillage. La variation la plus spectaculaire de la table est donc le passage
d'un compte à un chiffre à un autre compte à un chiffre. `fraction_below_third` est un
**indicateur déguisé en fraction** dès que la queue basse est vide.

⚠⚠ ET LE TIRAGE N'EST PAS APPARIÉ, malgré une mesure qui se dit appariée. `proximity.py` fait
`generator.choice(points.shape[0], take, replace=False)` avec une graine fixe — donc
reproductible **à maillage égal**. Or la réparation RETIRE des quads, donc `points.shape[0]`
change, donc `choice` rend un **autre sous-ensemble**. « Avant » et « après » ne sont pas
mesurés sur les mêmes cellules : ce sont deux sous-échantillons différents d'un phénomène
**spatialement groupé** (un pli est une région, pas un point), et c'est la condition exacte
dans laquelle une régression vers la moyenne fabrique des changements de signe.

⭐ CE QUE CE FICHIER TRANCHE, et il ne peut le trancher que parce qu'il ne bouge RIEN d'autre :
il rejoue la même mesure, sur le **même fichier**, en ne changeant que la graine. Toute
variation observée est celle du tirage, par construction — il n'existe aucune autre cause
possible. Si cette variation est du même ordre que celle de la table (avant, après), alors la
table ne peut pas porter d'énoncé sur le signe.

⭐⭐ ET IL PROPOSE LA COLONNE À LIRE À LA PLACE. `proximity.py` publie `shortfall`, dont sa
propre docstring dit qu'il « utilise TOUTE la queue basse et pondère chaque cellule par son
écart -- il n'y a aucune coupure a choisir ». Une moyenne sur des milliers de cellules ne peut
pas sauter d'un facteur cinq parce qu'une cellule est entrée ou sortie du tirage. Le rapport
compare les deux sur la même série de graines : c'est la comparaison qui décide, pas moi.

⚠ CE QU'IL N'ÉTABLIT PAS : que la réparation ne fait rien. Il établit que **cette colonne-là**
ne permet pas de le dire. La question de `07` reste ouverte et se rejoue sur `shortfall`.

Usage :
    uv run python src/excision/le_bruit_de_lechantillon.py --graines 12 \\
        --json docs/mesures/le_bruit_de_lechantillon.json
    uv run python src/excision/le_bruit_de_lechantillon.py --verifier
"""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
PROXIMITY = RACINE / "src" / "excision" / "proximity.py"
WINDCHECK = RACINE / "data" / "repos" / "windcheck"
APPARIEE = RACINE / "docs" / "mesures" / "reparation_et_proximite_scroll1.json"
DEFAUT_JSON = RACINE / "docs" / "mesures" / "le_bruit_de_lechantillon.json"

GRAINE_PUBLIEE = 42
"""⚠ La graine de `proximity.py`. Elle est **incluse** dans le balayage : ce qu'on veut savoir,
c'est où la valeur publiée tombe dans la distribution de ses propres voisines, pas si une
autre graine donnerait autre chose."""

CHEMINS_REFUSES = ("tifxyz_flattened", "tifxyz_normalized")
"""⚠⚠ Les mêmes que `reparation_et_proximite.CHEMINS_REFUSES`, et pour la même raison : un
maillage **aplati** rend des coordonnées qui ne sont pas celles du scan."""


def maillage_de(trace: Path) -> Path | None:
    """
    @brief Où vivent les plans `x/y/z.tif` d'une trace locale, ou None.

    ⚠⚠ Les traces de `windcheck` nichent leur maillage sous `<trace>/mesh/<...>.tifxyz/`. C'est
    la quatrième fois que ce dépôt résout cette disposition ; elle est ici parce que le seul
    autre porteur (`reparation_et_proximite`) importerait ce module en retour.
    """
    if (trace / "x.tif").is_file():
        return trace
    for meta in sorted(trace.glob("**/meta.json")):
        dossier = meta.parent
        if any(x in str(dossier) for x in CHEMINS_REFUSES):
            continue
        if (dossier / "x.tif").is_file():
            return dossier
    return None


def _proximite(maillage: Path, graine: int) -> dict | None:
    """
    @brief La proximité anormale d'un maillage pour une graine de tirage donnée.
    """
    r = subprocess.run(
        ["uv", "run", "python", str(PROXIMITY), str(maillage),
         "--json", "--label", f"graine{graine}", "--seed", str(graine)],
        capture_output=True, text=True, cwd=RACINE, timeout=1800)
    if r.returncode != 0:
        return None
    for ligne in reversed(r.stdout.splitlines()):
        if ligne.strip().startswith("{"):
            try:
                return json.loads(ligne)
            except json.JSONDecodeError:
                continue
    return None


def _etendue_pct(valeurs: list[float]) -> float | None:
    """
    @brief L'étendue d'une série, en pourcentage de sa médiane.

    ⚠ En pourcentage de la MÉDIANE et non du minimum : la table (avant, après) exprime ses
    variations en pourcentage de la valeur « avant », qui est une valeur tirée au hasard parmi
    les possibles. Rapporter à la médiane compare deux dispersions plutôt qu'une dispersion à
    un tirage particulier.
    """
    valeurs = [x for x in valeurs if x is not None]
    if len(valeurs) < 2:
        return None
    m = statistics.median(valeurs)
    return 100.0 * (max(valeurs) - min(valeurs)) / m if m else None


def rho_de_rangs(a: list[float], b: list[float]) -> float:
    """
    @brief La corrélation de rangs de Spearman entre deux séries appariées.

    ⚠ Écrite ici, en dix lignes, plutôt qu'importée de `scipy` : ce module est une batterie de
    contrôles, et une batterie qui ne tourne pas faute d'une dépendance scientifique est une
    batterie que personne ne lance. Les égalités reçoivent leur rang **moyen**, sans quoi deux
    traces à la même valeur seraient départagées par leur position dans le fichier.
    """
    def rangs(v: list[float]) -> list[float]:
        ordre = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(ordre):
            j = i
            while j + 1 < len(ordre) and v[ordre[j + 1]] == v[ordre[i]]:
                j += 1
            moyen = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1):
                r[ordre[k]] = moyen
            i = j + 1
        return r
    ra, rb = rangs(a), rangs(b)
    n = len(ra)
    ma, mb = sum(ra) / n, sum(rb) / n
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    da = sum((x - ma) ** 2 for x in ra) ** 0.5
    db = sum((y - mb) ** 2 for y in rb) ** 0.5
    return num / (da * db) if da and db else 0.0


def traces_de_la_table() -> list[tuple[str, float, float]]:
    """
    @brief Les traces mesurées par la table appariée, avec leur variation publiée.

    ⚠⚠ Ce sont **les mêmes traces**, délibérément. Balayer les graines sur un autre lot
    comparerait deux dispersions prises sur deux populations, ce qui ne trancherait rien : la
    question est de savoir ce que vaut *cette* table.
    """
    if not APPARIEE.is_file():
        raise SystemExit(
            f"table appariée absente : {APPARIEE}\n"
            "  la produire d'abord : uv run python src/excision/reparation_et_proximite.py "
            "--corpus scroll1 --limite 10 --json " + str(APPARIEE))
    d = json.loads(APPARIEE.read_text())
    return [(p["trace"], p["fbt_avant"], p["variation_pct"]) for p in d["paires"]]


def mesurer(n_graines: int = 12, limite: int = 0) -> dict:
    base = WINDCHECK / "data" / "scroll1_tifxyz"
    graines = [GRAINE_PUBLIEE] + [i for i in range(1, 64) if i != GRAINE_PUBLIEE][:n_graines - 1]

    lignes, sautes = [], []
    lot = traces_de_la_table()
    if limite:
        lot = lot[:limite]
    for nom, fbt_publie, var_publiee in lot:
        maille = maillage_de(base / nom) if (base / nom).is_dir() else None
        if maille is None:
            # ⚠⚠ CHAQUE SAUT EST RAPPORTE : « zero ligne » et « rien d'eligible » ne doivent
            # pas se ressembler.
            sautes.append((nom, "maillage introuvable"))
            continue
        serie = []
        for g in graines:
            r = _proximite(maille, g)
            if r is None:
                sautes.append((nom, f"proximité a échoué (graine {g})"))
                continue
            serie.append(dict(graine=g, usable=r["usable"], measured=r["measured"],
                              sampled=r["sampled"],
                              fbt=r["fraction_below_third"], shortfall=r["shortfall"]))
        if len(serie) < 2:
            continue
        fbts = [x["fbt"] for x in serie]
        shorts = [x["shortfall"] for x in serie]
        lignes.append(dict(
            trace=nom, graines=len(serie),
            fbt_publie=fbt_publie, variation_publiee_pct=var_publiee,
            # ⚠⚠⚠ LE COMPTE, A COTE DE LA FRACTION. `fbt x usable` est le nombre de cellules
            # sous le tiers -- la grandeur que la fraction cache. Un denominateur de 2477 fait
            # d'une cellule un « 0,04 % » qui a l'air d'une mesure.
            cellules_min=min(round(x["fbt"] * x["usable"]) for x in serie),
            cellules_max=max(round(x["fbt"] * x["usable"]) for x in serie),
            usable_median=statistics.median(x["usable"] for x in serie),
            sampled=serie[0]["sampled"],
            fbt_min=min(fbts), fbt_max=max(fbts), fbt_median=statistics.median(fbts),
            fbt_etendue_pct=_etendue_pct(fbts),
            shortfall_min=min(shorts), shortfall_max=max(shorts),
            shortfall_median=statistics.median(shorts),
            shortfall_etendue_pct=_etendue_pct(shorts),
            serie=serie,
        ))
    return dict(graine_publiee=GRAINE_PUBLIEE, n_graines=n_graines, lignes=lignes,
                sautes=[{"trace": t, "raison": r} for t, r in sautes])


CORRELATE = RACINE / "src" / "excision" / "correlate.py"
INDEX_PUBLIE = WINDCHECK / "results" / "index.json"


def balayer_population(n_graines: int = 5,
                       champs: tuple[str, ...] = ("fraction_below_third", "shortfall")) -> dict:
    """
    @brief Le rho de `07` §8 dépend-il de la graine ? — mesuré sur TOUTE la population.

    ⚠⚠⚠ CE MODE EXISTE PARCE QUE MON PREMIER CONTRÔLE PORTAIT SUR LA MAUVAISE POPULATION.
    J'avais comparé les classements de graine à graine sur les **dix** traces de la table
    appariée — or ces dix-là sont choisies par leur COUVERTURE, donc resserrées, et un
    classement se dégrade d'autant plus vite que les valeurs sont proches. Le contrôle est
    tombé (rho de rangs 0,697 au pire), et il avait raison de tomber : il ne disait rien de la
    population de `07`, qui compte 46 traces et s'étale bien plus large. C'est le piège que ce
    dépôt a déjà payé — conclure d'un sous-ensemble sur l'ensemble.

    ⭐ La corrélation est calculée par `correlate.py`, jamais réécrite ici : c'est lui qui
    porte la jointure sur le nom de trace, le rang de Spearman, et surtout le traitement du
    **confond de longueur**. En redériver une seconde version donnerait deux réponses à « la
    proximité dit-elle quelque chose que le compte de croisements ne dit pas ».

    ⚠ `shortfall` est balayé en même temps, pour le même prix : savoir que la colonne stable
    tient aussi son classement est ce qui permettrait d'en faire la colonne de référence.
    """
    if not INDEX_PUBLIE.is_file():
        raise SystemExit(f"index publié absent : {INDEX_PUBLIE}")
    base = WINDCHECK / "data" / "scroll1_tifxyz"
    graines = [GRAINE_PUBLIEE] + [i for i in range(1, 64) if i != GRAINE_PUBLIEE][:n_graines - 1]

    resultats = {c: [] for c in champs}
    mesurees = {}
    with tempfile.TemporaryDirectory() as tmp:
        for g in graines:
            jsonl = Path(tmp) / f"proximite_graine{g}.jsonl"
            lignes = []
            for dossier in sorted(base.iterdir()):
                if not dossier.is_dir():
                    continue
                maille = maillage_de(dossier)
                if maille is None:
                    continue
                r = _proximite(maille, g)
                # ⚠ Une trace qui ne fait pas un tour sort en erreur et n'est PAS une panne :
                # elle est hors du domaine de la metrique. On la saute comme le fait le
                # runner publie, sans la compter comme un echec.
                if r is None:
                    continue
                r["label"] = dossier.name
                lignes.append(json.dumps(r))
            jsonl.write_text("\n".join(lignes) + "\n", encoding="utf-8")
            mesurees[g] = len(lignes)
            for champ in champs:
                sortie = Path(tmp) / f"rho_{champ}_{g}.json"
                proc = subprocess.run(
                    ["uv", "run", "python", str(CORRELATE), str(jsonl), str(INDEX_PUBLIE),
                     "--field", champ, "--json", str(sortie)],
                    capture_output=True, text=True, cwd=RACINE, timeout=600)
                if proc.returncode != 0 or not sortie.is_file():
                    continue
                d = json.loads(sortie.read_text())
                resultats[champ].append(dict(graine=g, n=d.get("n"),
                                             rho=d["rho_croisements"],
                                             p=d.get("p_croisements")))
    return dict(graines=graines, traces_mesurees=mesurees, rho=resultats)


def _verifier(r: dict | None = None) -> int:
    echecs = 0
    comptees = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, comptees
        comptees += 1
        print(f"  {'ok  ' if ok else 'FAIL'}  {nom}" + (f"   [{detail}]" if detail else ""))
        if not ok:
            echecs += 1

    if not r or not r.get("lignes"):
        print("  (aucune mesure en cache — la produire avec --json)")
        return 0
    lignes = r["lignes"]

    print("le tirage n'est pas apparié, et l'échantillon utile est petit")
    v("le tirage ne dépend que de la taille du maillage, donc la réparation le change",
      "generator.choice(points.shape[0]" in PROXIMITY.read_text(),
      "proximity.py : choice(points.shape[0], take, replace=False)")
    # ⚠⚠ J'AVAIS ECRIT « l'echantillon effectif est sous le quart du demande » -- generalise
    # depuis la SEULE trace que j'avais chronometree a la main, et la mesure l'a fait tomber :
    # `usable` va de 12 % a 69 % du tirage selon la trace. Ce qui est vrai, et plus utile,
    # c'est que le DENOMINATEUR n'est pas une constante. 20000 cellules sont tirees, mais
    # seules celles qui ont un vis-a-vis non adjacent dans le rayon sont mesurables, et ce
    # nombre varie d'un facteur cinq d'une trace a l'autre. Donc « 0,04 % » sur deux traces ne
    # designe pas le meme compte, et une table qui compare des fractions entre traces compare
    # des mesures prises sur des echantillons de tailles tres differentes.
    utiles = [x["usable_median"] for x in lignes]
    facteur = max(utiles) / min(utiles) if min(utiles) else 0.0
    v("... et l'échantillon EFFECTIF n'est pas une constante d'une trace à l'autre",
      facteur >= 2.0,
      f"de {min(utiles):.0f} à {max(utiles):.0f} cellules utiles sur "
      f"{lignes[0]['sampled']} tirées — facteur {facteur:.1f}")
    # ⚠ Et la trace dont la variation publiee est la plus spectaculaire est justement celle ou
    # la metrique a le MOINS de matiere. Ce n'est pas une coincidence, c'est le meme fait.
    plus_petite = min(lignes, key=lambda x: x["usable_median"])
    plus_forte = max((x for x in lignes if x["variation_publiee_pct"] is not None),
                     key=lambda x: abs(x["variation_publiee_pct"]))
    v("... et la variation publiée la plus forte tombe sur l'échantillon le plus maigre",
      plus_petite["trace"] == plus_forte["trace"],
      f"{plus_forte['trace'][-8:]} : {plus_forte['variation_publiee_pct']:+.0f} % sur "
      f"{plus_petite['usable_median']:.0f} cellules utiles")

    print("\nune fraction dont le numérateur tient sur un chiffre")
    v("au moins une trace de la table compte moins de dix cellules sous le tiers",
      any(x["cellules_max"] < 10 for x in lignes),
      " · ".join(f"{x['trace'][-8:]}:{x['cellules_min']}–{x['cellules_max']}"
                 for x in lignes if x["cellules_max"] < 10))

    print("\nà maillage IDENTIQUE, la graine seule déplace déjà la colonne lue")
    # ⚠⚠⚠ LE CONTROLE QUI DECIDE, et il est ecrit pour pouvoir tomber : si le balayage des
    # graines rendait une etendue negligeable devant la variation publiee, la table (avant,
    # apres) tiendrait, et c'est CE resultat qui s'imprimerait. C'est la comparaison qui
    # tranche, pas une opinion sur l'echantillonnage.
    couples = [(x, abs(x["variation_publiee_pct"])) for x in lignes
               if x["variation_publiee_pct"] is not None and x["fbt_etendue_pct"] is not None]
    noyees = [x for x, var in couples if x["fbt_etendue_pct"] >= var]
    v("le bruit de graine seul égale ou dépasse la variation publiée, sur la majorité",
      len(noyees) > len(couples) / 2,
      f"{len(noyees)}/{len(couples)} traces · étendues "
      + " · ".join(f"{x['fbt_etendue_pct']:.0f} %" for x in lignes[:5]) + " …")

    print("\nla réconciliation avec `07` §8 : ce n'est pas la colonne qui est mauvaise, "
          "c'est la TÂCHE qui a changé")
    # ⚠⚠⚠ `07` §8 valide `fraction_below_third` par un rho de +0,769 sur 46 traces -- une
    # tache de CLASSEMENT ENTRE traces -- et montre qu'aucune grandeur sans seuil ne l'egale
    # (`shortfall` n'y fait que +0,340). Ce document a raison. Ce que je mesure ici est une
    # autre propriete : la precision d'une DIFFERENCE APPARIEE a l'interieur d'une trace. Les
    # deux ne se contredisent pas, elles sont les deux moities du meme fait -- `fbt` a un gros
    # signal ET un gros bruit. Entre traces le signal est enorme (un facteur >10 sur la
    # valeur), donc le bruit se paie sans consequence et le classement tient. Avant/apres, le
    # signal est minuscule (la reparation retire ~0,03 % de l'aire), donc le meme bruit le
    # noie. L'erreur n'etait pas de choisir cette colonne : c'etait de transporter une
    # grandeur validee pour ORDONNER vers une tache de DIFFERENCE.
    medians = [x["fbt_median"] for x in lignes if x["fbt_median"]]
    entre_traces_pct = 100.0 * (max(medians) - min(medians)) / statistics.median(medians)
    bruit_median_pct = statistics.median(x["fbt_etendue_pct"] for x in lignes
                                         if x["fbt_etendue_pct"] is not None)
    effet_median_pct = statistics.median(abs(x["variation_publiee_pct"]) for x in lignes
                                         if x["variation_publiee_pct"] is not None)
    v("entre traces, le signal écrase le bruit de graine — donc le classement de `07` §8 tient",
      entre_traces_pct > 3 * bruit_median_pct,
      f"écart entre traces {entre_traces_pct:.0f} % contre bruit {bruit_median_pct:.0f} %")
    v("... mais avant/après, l'effet est PLUS PETIT que ce même bruit",
      effet_median_pct < bruit_median_pct,
      f"effet médian {effet_median_pct:.0f} % contre bruit {bruit_median_pct:.0f} %")

    print("\net le défaut NE se généralise pas : le classement entre traces, lui, survit")
    # ⚠⚠⚠ LA QUESTION QUI DECIDE DE LA PORTEE. Les deux autres consommateurs de cette colonne
    # (`correlate.py`, `baseline_sweep.py`) font un travail ENTRE traces, pas une difference
    # appariee. Si la graine reordonnait les traces, tout ce qui repose sur `fbt` tomberait avec
    # la table (avant, apres) -- y compris le rho de +0,769 de `07` §8 et son plateau de seuil.
    # La reponse se calcule sans aucune mesure nouvelle : les memes 12 graines sont deja la, il
    # suffit de comparer les CLASSEMENTS qu'elles produisent. Ecrit pour tomber si elles ne
    # s'accordaient pas.
    def rangs_stables(sous_ensemble: list[dict]) -> list[float]:
        k_max = min(len(x["serie"]) for x in sous_ensemble)
        colonnes = [[x["serie"][k]["fbt"] for x in sous_ensemble] for k in range(k_max)]
        return [rho_de_rangs(colonnes[0], autre) for autre in colonnes[1:]]

    # ⚠⚠⚠ MON PREMIER CONTROLE ICI DISAIT « changer la graine ne reordonne pas les traces », et
    # il est TOMBE (rho de rangs 0,697 au pire). Il avait raison de tomber, et pour une raison
    # que je n'avais pas vue : ces dix traces sont choisies par leur COUVERTURE, donc leurs
    # valeurs sont resserrees, et un classement se degrade d'autant plus vite. Baisser le seuil
    # pour le faire passer aurait ete un reglage apres coup. Ce qui se mesure, et qui explique
    # le mecanisme plutot que de le contourner : le desordre vient des traces dont le COMPTE
    # est a un chiffre. Le classement de `07` §8, lui, se mesure sur SA population -- mode
    # `--population`, qui rappelle `correlate.py` a plusieurs graines.
    # ⚠⚠ DEUX HYPOTHESES MORTES, ECRITES POUR QU'ON NE LES REFASSE PAS. (1) « le classement
    # survit au changement de graine » : faux ici, rho de rangs 0,697 au pire. (2) « le desordre
    # vient des traces dont le compte est a un chiffre » : faux aussi -- les retirer donne 0,700
    # contre 0,697, soit rien. La methode de ce depot dit d'arreter de deviner a la troisieme
    # tentative et de prendre un INSTRUMENT : c'est le mode `--population`, qui rappelle
    # `correlate.py` a plusieurs graines sur les 46 traces de `07` §8. Ce qui reste asserte ici
    # est ce que ce sous-ensemble etablit et rien de plus.
    tous = rangs_stables(lignes)
    gros = [x for x in lignes if x["cellules_min"] >= 10]
    v("sur ce sous-ensemble resserré, le classement N'EST PAS robuste à la graine",
      min(tous) < 0.85,
      f"rho de rangs min {min(tous):.3f} sur {len(lignes)} traces · "
      f"{min(rangs_stables(gros)):.3f} sans les comptes à un chiffre "
      f"({len(gros)} traces) — la population de `07` se mesure avec --population")

    print("\net la colonne SANS SEUIL, elle, tient")
    # ⚠⚠ LA MOITIE CONSTRUCTIVE. Demolir la colonne lue ne dit pas quoi lire. `shortfall`
    # moyenne toute la queue basse sur des milliers de cellules, donc une cellule qui entre ou
    # sort du tirage ne peut pas la deplacer d'un facteur. Si ce controle tombait, il faudrait
    # conclure que la mesure entiere est trop bruitee -- pas seulement une colonne.
    v("l'étendue de `shortfall` est bien plus petite que celle de `fraction_below_third`",
      all(x["shortfall_etendue_pct"] < x["fbt_etendue_pct"] for x in lignes
          if x["fbt_etendue_pct"] and x["shortfall_etendue_pct"] is not None),
      " · ".join(f"{x['shortfall_etendue_pct']:.1f} % contre {x['fbt_etendue_pct']:.0f} %"
                 for x in lignes[:4]) + " …")
    pires = max(x["shortfall_etendue_pct"] for x in lignes
                if x["shortfall_etendue_pct"] is not None)
    v("... et elle reste sous dix pour cent, même au pire",
      pires < 10.0, f"pire étendue {pires:.1f} %")

    print()
    if echecs:
        print(f"  ECHEC ({echecs} failures)")
    else:
        print(f"  ALL PASS (0 failures, {comptees} checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--graines", type=int, default=12, help="nombre de graines balayées")
    p.add_argument("--limite", type=int, default=0, help="ne traiter que les N premières traces")
    p.add_argument("--population", action="store_true",
                   help="balayer les graines sur TOUT le corpus et recalculer le rho de `07` §8")
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    a = p.parse_args()

    if a.population:
        rp = balayer_population(a.graines)
        for champ, serie in rp["rho"].items():
            if not serie:
                continue
            rhos = [x["rho"] for x in serie]
            print(f"{champ:24s} rho ~ croisements : "
                  + " · ".join(f"{x:+.3f}" for x in rhos)
                  + f"   etendue {max(rhos) - min(rhos):.3f} sur {len(rhos)} graines"
                  + f"   (n = {serie[0]['n']})")
        if a.json:
            a.json.parent.mkdir(parents=True, exist_ok=True)
            a.json.write_text(json.dumps(rp, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"\necrit : {a.json}")
        return 0

    if a.verifier and not a.json:
        garde = json.loads(DEFAUT_JSON.read_text()) if DEFAUT_JSON.is_file() else None
        return 1 if _verifier(garde) else 0

    r = mesurer(a.graines, a.limite)
    print(f"{r['n_graines']} graines, maillage inchangé — seul le tirage bouge\n")
    print(f"  {'trace':32s} {'cellules':>10s} {'fbt étendue':>12s} "
          f"{'Δ publiée':>10s} {'shortfall étendue':>18s}")
    for x in r["lignes"]:
        var = f"{x['variation_publiee_pct']:+.0f} %" if x["variation_publiee_pct"] is not None else "  —"
        print(f"  {x['trace'][:32]:32s} {x['cellules_min']:4d}–{x['cellules_max']:<5d} "
              f"{x['fbt_etendue_pct']:11.0f} % {var:>10s} "
              f"{x['shortfall_etendue_pct']:17.1f} %")
    for x in r.get("sautes", []):
        print(f"  ⚠ {x['trace']:32s} sautée — {x['raison']}", file=sys.stderr)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nécrit : {a.json}")
    if a.verifier:
        print()
        return 1 if _verifier(r) else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
