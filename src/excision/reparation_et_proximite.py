#!/usr/bin/env python3
"""La réparation déplace-t-elle la proximité anormale ? — sur une population qu'on croyait absente.

⚠⚠⚠ CE FICHIER EXISTE PARCE QUE LA MESURE QUI A DÉSTABILISÉ `07` N'AVAIT AUCUN PRODUCTEUR.
`docs/mesures/reparation_deplace_la_proximite.json` porte le résultat qui a renversé la
conclusion centrale de `07` — « la réparation ne déplace pas le défaut » — et **rien dans
`src/` ne le produit** : il a été fait au terminal. Une mesure qui renverse une conclusion et
qu'on ne peut pas relancer est le pire cas de la dette `D3`, parce qu'elle a l'air solide.

⭐⭐⭐ ET SON BLOCAGE VENAIT D'UNE GÉNÉRALISATION DEPUIS LE MAUVAIS ROULEAU. `07` conclut que
*« le cas discriminant n'est pas montable sur ce corpus »* : il faudrait une trace **peu
atteinte** ET couvrant plus d'un tour, or sur `PHerc0172` toutes les traces longues sont les
`auto_grown`, les plus atteintes. C'est vrai — **de `PHerc0172`**. Le recensement de
`windcheck` dit autre chose des autres :

    corpus                  traces   sales   span médian
    Scroll 1 (PHercParis4)      55      48      2,70 tours
    PHerc0814                   13      11      3,10 tours
    PHerc0172 (celui de `07`)   53      52      0,92 tour

**Scroll 1 offre 48 traces curatées, sales, et bien au-dessus de la coupure d'un tour.** La
population déclarée absente existe, sur un autre rouleau, et elle est locale.

⚠⚠ ET LE CONFOND DE `07` EST PLUS LARGE QUE CE QU'IL DIT. Sa table compare deux traces
`auto_grown` de `PHerc0172` (qui chutent de 50 % et 22 %) à une trace **curatée de
`PHercParis4`** (qui ne bouge pas) — donc à travers **deux rouleaux ET deux provenances**. Ce
qu'il lit comme « ce n'est pas proportionnel à ce qui est retiré » pourrait être une différence
de **population**. Ce fichier permet de trancher, en mesurant plusieurs traces de la même
provenance.

⚠ CE QU'IL N'ÉTABLIT PAS : rien, tant qu'il n'a pas tourné sur assez de traces. Il rend une
paire (avant, après) par trace, et c'est la distribution qui répondra — pas un exemple.

⚠ Une trace `already_clean` est **gardée et marquée**, jamais jetée : elle dit que la
réparation n'avait rien à retirer, ce qui est une information sur la population et non un
échec. Les jeter ferait croire que toutes les traces sont réparables.

Usage :
    uv run python src/excision/reparation_et_proximite.py --corpus scroll1 --limite 4 \\
        --json docs/mesures/reparation_et_proximite_scroll1.json
    uv run python src/excision/reparation_et_proximite.py --verifier
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
WINDCHECK = RACINE / "data" / "repos" / "windcheck"
PROXIMITY = RACINE / "src" / "excision" / "proximity.py"

CORPUS = {
    "scroll1": ("data/scroll1_tifxyz", "Scroll 1 (PHercParis4)"),
    "scroll5": ("data/scroll5_tifxyz", "Scroll 5 (PHerc0172)"),
}
"""Les corpus locaux de `windcheck`. ⚠ Le nom long est celui de son propre `index.json`, pour
que le recensement et cette mesure parlent du même objet."""

SPAN_MINIMUM = 1.0
"""La couverture minimale, en tours. ⚠⚠ Ce n'est **pas un réglage** : `07` §7 établit qu'une
trace qui ne fait pas un tour **ne peut pas se recouvrir**, donc la métrique n'y rend rien —
« pas un mauvais chiffre, rien ». C'est le domaine de définition de l'instrument."""


def recensement() -> list[dict]:
    """
    @brief Le recensement publié de `windcheck` — statut de croisement et couverture.
    """
    index = WINDCHECK / "results" / "index.json"
    if not index.is_file():
        raise SystemExit(f"recensement absent : {index}")
    return json.loads(index.read_text())


def eligibles(corpus: str) -> list[dict]:
    """
    @brief Les traces d'un corpus qui sont **sales** et **dépassent un tour**.

    ⚠ Les deux conditions, pas une : une trace propre n'a rien à réparer, une trace courte
    n'a rien à mesurer. Relâcher l'une remplirait le résultat de paires vides.
    """
    _, nom_long = CORPUS[corpus]
    return [x for x in recensement()
            if x.get("corpus") == nom_long
            and x.get("crossing_status") == "present"
            and (x.get("covering_span_rev") or 0.0) > SPAN_MINIMUM]


CHEMINS_REFUSES = ("tifxyz_flattened", "tifxyz_normalized")
"""⚠⚠ Les mêmes que `le_sens_des_indices.CHEMINS_REFUSES`, et pour la même raison : un maillage
**aplati** rend des coordonnées qui ne sont pas celles du scan. La proximité y serait calculée
sur une géométrie dépliée, donc parfaitement plausible et fausse."""


def maillage_de(trace: Path) -> Path | None:
    """
    @brief Où vivent les plans `x/y/z.tif` d'une trace locale, ou None.

    ⚠⚠ Les traces de `windcheck` nichent leur maillage sous `<trace>/mesh/<...>.tifxyz/`, pas
    à leur racine — la **même** disposition que les segments publiés de `PHerc0172`. Mon
    premier appel passait la racine, `proximity.py` répondait « plan absent », et le résultat
    était une paire manquante **en silence**. C'est la troisième fois que ce dépôt résout
    cette disposition ; celle-ci renvoie à la règle plutôt que d'en écrire une variante.
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


def _proximite(maillage: Path, etiquette: str, apparie: bool = False) -> dict | None:
    """
    @brief La proximité anormale d'un maillage, par l'instrument de `07`.

    ⚠⚠ `apparie` demande le tirage par POSITION DE GRILLE. Le tirage par défaut indexe les
    cellules **valides**, dont le nombre change avec la réparation, donc « avant » et « après »
    ne portent pas sur les mêmes cellules — c'est ce que `07` §10 mesure. La grille, elle, ne
    change pas, donc un tirage par position est apparié par construction.
    """
    argv = ["uv", "run", "python", str(PROXIMITY), str(maillage), "--json", "--label", etiquette]
    if apparie:
        argv.append("--tirage-par-position")
    r = subprocess.run(argv, capture_output=True, text=True, cwd=RACINE, timeout=1800)
    if r.returncode != 0:
        return None
    for ligne in reversed(r.stdout.splitlines()):
        if ligne.strip().startswith("{"):
            try:
                return json.loads(ligne)
            except json.JSONDecodeError:
                continue
    return None


def _reparer(trace: Path, sortie: Path, threads: int | None = None) -> dict | None:
    """
    @brief La réparation de `windcheck`, et son certificat.

    ⚠⚠ `threads` existe pour une raison mesurée : six réparations de la même trace rendent
    **trois** certificats distincts (3691, 3696, 3698). L'aide de `windcheck transform` revendique
    pourtant une *« frozen scheduling policy »*, et son défaut est `0 = all cores`. Ce dépôt a
    déjà rencontré cette forme — `44` : un traceur dont l'aléa venait de l'horloge sur 22 fils,
    rendu reproductible par une graine posée et `thread_limit: 1`. Forcer un seul fil est donc la
    première hypothèse à tester, et elle se teste au lieu de se supposer.
    """
    argv = ["uv", "run", "windcheck", "transform", str(trace), "--out", str(sortie)]
    if threads is not None:
        argv += ["--threads", str(threads)]
    r = subprocess.run(argv, capture_output=True, text=True, cwd=WINDCHECK, timeout=7200)
    if r.returncode != 0:
        return None
    cert = next(sortie.glob("*_transform_certificate.json"), None)
    if cert is None:
        return None
    d = json.loads(cert.read_text())
    # ⚠⚠⚠ LES CLES SONT VERIFIEES, PAS SUPPOSEES. J'avais ecrit `removed_quads` et
    # `retained_area_pct` ; le certificat porte `n_removed_quads` et
    # `retained_area_fraction`. Un `.get()` sur une clef absente rend `None`, que
    # l'affichage montrait comme **0 quad retire** -- donc « la reparation n'a rien fait »
    # alors qu'on ne savait pas ce qu'elle avait fait. Un nom de clef faux ne doit pas
    # ressembler a une mesure.
    attendues = ("status", "n_removed_quads", "retained_area_fraction")
    manquantes = [k for k in attendues if k not in d]
    if manquantes:
        raise SystemExit(
            f"certificat sans {', '.join(manquantes)} : {cert}\n"
            "  le schéma de `windcheck` a changé — lire le certificat avant de mesurer.")
    return d


def mesurer(corpus: str = "scroll1", limite: int = 0, apparie: bool = False) -> dict:
    dossier, nom_long = CORPUS[corpus]
    base = WINDCHECK / dossier
    lot = eligibles(corpus)
    if limite:
        # ⚠ Les plus COUVRANTES d'abord : c'est la ou la metrique a le plus de matiere, donc
        # ou une paire (avant, apres) est la moins bruitee. Prendre les premieres du fichier
        # melangerait la couverture au resultat.
        lot = sorted(lot, key=lambda x: -(x.get("covering_span_rev") or 0))[:limite]

    paires, sautes = [], []
    for entree in lot:
        nom = entree["segment"]
        trace = base / nom
        # ⚠⚠ CHAQUE SAUT EST RAPPORTE. Ma premiere version rendait `continue` en silence, donc
        # « zero paire » etait indistinguable de « rien n'est eligible ». Un outil qui jette
        # sans le dire fait chercher la panne au mauvais endroit.
        maille = maillage_de(trace) if trace.is_dir() else None
        if maille is None:
            sautes.append((nom, "maillage introuvable"))
            continue
        avant = _proximite(maille, f"{nom}:avant", apparie)
        if not avant:
            sautes.append((nom, "proximité avant a échoué"))
            continue
        with tempfile.TemporaryDirectory() as tmp:
            cert = _reparer(trace, Path(tmp))
            repare = next(Path(tmp).glob("*_transformed.tifxyz"), None)
            repare = maillage_de(repare) if repare else None
            apres = _proximite(repare, f"{nom}:apres", apparie) if repare else None
            if cert is None:
                sautes.append((nom, "réparation a échoué"))
            elif apres is None:
                sautes.append((nom, "proximité après a échoué"))
        if not apres or cert is None:
            continue
        fa = avant.get("fraction_below_third")
        fp = apres.get("fraction_below_third")
        # ⚠⚠⚠ LA COLONNE QUI TIENT EST GARDEE A COTE DE CELLE QUI NE TIENT PAS.
        # `le_bruit_de_lechantillon.py` mesure qu'a maillage IDENTIQUE, changer la seule graine
        # du tirage deplace `fraction_below_third` de 35 a 229 % -- donc plus que la variation
        # (avant, apres) sur 9 des 10 traces de cette table. La cause est arithmetique : `fbt`
        # compte les cellules sous un tiers de leur voisinage, et ce compte vaut entre 0 et 7
        # cellules sur les traces maigres. `shortfall` moyenne TOUTE la queue basse sur des
        # milliers de cellules, et son etendue de graine reste sous 5 %. Les deux sont ecrites
        # cote a cote plutot que l'une remplacee par l'autre : la premiere est le chiffre que
        # `07` a publie, et l'effacer rendrait sa correction invisible.
        sa = avant.get("shortfall")
        sp = apres.get("shortfall")
        paires.append(dict(
            trace=nom, corpus=nom_long,
            span_tours=entree.get("covering_span_rev"),
            statut=cert.get("status"),
            quads_retires=cert["n_removed_quads"],
            aire_gardee_pct=100.0 * cert["retained_area_fraction"],
            aire_excisee_fraction=cert.get("excised_area_fraction"),
            usable_avant=avant.get("usable"), usable_apres=apres.get("usable"),
            cellules_avant=round(fa * avant["usable"]) if fa is not None else None,
            cellules_apres=round(fp * apres["usable"]) if fp is not None else None,
            fbt_avant=fa, fbt_apres=fp,
            variation_pct=(100.0 * (fp - fa) / fa) if fa else None,
            shortfall_avant=sa, shortfall_apres=sp,
            variation_shortfall_pct=(100.0 * (sp - sa) / sa) if sa else None,
        ))
    return dict(corpus=nom_long, eligibles=len(eligibles(corpus)),
                span_minimum=SPAN_MINIMUM,
                tirage="position" if apparie else "index", paires=paires,
                sautes=[{"trace": t, "raison": r} for t, r in sautes])


def mesurer_determinisme(trace: str, repetitions: int = 3,
                         corpus: str = "scroll1", threads: int | None = None) -> dict:
    """
    @brief La même réparation, sur la même trace, plusieurs fois — rend-elle le même certificat ?

    ⚠⚠⚠ CE MODE EXISTE PARCE QUE J'ALLAIS PUBLIER LE CONTRAIRE DEPUIS UN LOG DE `/tmp`. En
    relançant le lot pour ajouter la colonne `shortfall`, `windcheck transform` a rendu **3 698**
    quads retirés là où le run précédent en donnait **3 696** — donc la réparation n'est pas
    déterministe. Écrire ce fait en s'appuyant sur deux sorties de terminal aurait été
    exactement la dette `D3` que ce document dénonce : une affirmation qu'on ne peut pas
    relancer. Ce mode la rend reproductible.

    ⚠ Il ne mesure QUE le certificat (statut, quads retirés, aire gardée), pas la proximité :
    une géométrie de sortie identique suffit à rendre la mesure d'après identique, et une
    géométrie différente suffit à expliquer qu'elle ne le soit pas. Ajouter la proximité ici
    mélangerait deux sources de variation dont ce mode existe pour séparer la première.
    """
    base = WINDCHECK / CORPUS[corpus][0]
    dossier = base / trace
    if not dossier.is_dir():
        raise SystemExit(f"trace absente : {dossier}")
    certificats = []
    for _ in range(repetitions):
        with tempfile.TemporaryDirectory() as tmp:
            cert = _reparer(dossier, Path(tmp), threads)
            if cert is None:
                certificats.append(None)
                continue
            certificats.append({k: cert.get(k) for k in
                                ("status", "n_removed_quads", "retained_area_fraction",
                                 "excised_area_fraction")})
    valides = [c for c in certificats if c]
    distincts = []
    for c in valides:
        if c not in distincts:
            distincts.append(c)
    return dict(trace=trace, repetitions=repetitions, threads=threads,
                certificats=certificats,
                distincts=len(distincts),
                quads=[c["n_removed_quads"] for c in valides],
                deterministe=len(distincts) <= 1)


def _verifier(r: dict | None = None) -> int:
    echecs = 0
    comptees = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, comptees
        comptees += 1
        print(f"  {'ok  ' if ok else 'FAIL'}  {nom}" + (f"   [{detail}]" if detail else ""))
        if not ok:
            echecs += 1

    print("la population que `07` déclarait absente existe — sur un autre rouleau")
    par_corpus = {}
    for x in recensement():
        par_corpus.setdefault(x["corpus"], []).append(x)
    s1 = [x for x in par_corpus.get("Scroll 1 (PHercParis4)", [])
          if x.get("crossing_status") == "present"
          and (x.get("covering_span_rev") or 0) > SPAN_MINIMUM]
    s5 = [x for x in par_corpus.get("Scroll 5 (PHerc0172)", [])
          if x.get("crossing_status") == "present"
          and (x.get("covering_span_rev") or 0) > SPAN_MINIMUM]
    v("Scroll 1 offre des dizaines de traces sales dépassant un tour",
      len(s1) >= 20, f"{len(s1)} traces éligibles")
    # ⚠⚠ Le controle qui explique la generalisation de `07` : sur SON rouleau, la population
    # est effectivement maigre. Sans lui, « `07` s'est trompe » serait gratuit -- il avait
    # raison de son corpus, et tort de conclure sur tous.
    v("... alors que sur le rouleau de `07` elle est bien plus maigre",
      len(s5) < len(s1) / 2, f"{len(s5)} contre {len(s1)}")

    if r and r.get("paires"):
        print("et la mesure appariée tourne")
        v("chaque paire porte un avant ET un après",
          all(p["fbt_avant"] is not None and p["fbt_apres"] is not None
              for p in r["paires"]), f"{len(r['paires'])} paires")
        # ⚠ Une trace `already_clean` est gardee : elle dit que la reparation n'avait rien a
        # retirer, ce qui est une information sur la population.
        v("... et les traces déjà propres sont gardées et marquées",
          all(p.get("statut") for p in r["paires"]),
          ", ".join(sorted({str(p["statut"]) for p in r["paires"]})))
        # ⚠⚠⚠ CE QUE CETTE COLONNE MESURE VRAIMENT -- ET CE N'EST PAS CE QUE J'AI CRU.
        # J'avais lu l'instabilite du SIGNE comme un resultat sur la reparation. Elle n'en est
        # pas un : `le_bruit_de_lechantillon.py` mesure qu'a maillage IDENTIQUE, en ne
        # changeant QUE la graine du tirage, `fraction_below_third` bouge de 35 a 229 % -- donc
        # plus que la variation (avant, apres) sur 9 de ces 10 traces. La cause est
        # arithmetique : `fbt` compte les cellules sous un tiers de leur voisinage, ce compte
        # vaut 0 a 7 cellules sur les traces maigres, et le tirage n'est PAS apparie (la
        # reparation change `points.shape[0]`, donc `choice` rend un autre sous-ensemble).
        # Le controle est garde parce qu'il documente la colonne que `07` a publiee ; ce qu'il
        # etablit desormais, c'est que cette colonne ne peut pas porter d'enonce sur le signe.
        variations = [p["variation_pct"] for p in r["paires"]
                      if p.get("variation_pct") is not None and p["quads_retires"]]
        if len(variations) >= 2:
            v("le signe de `fraction_below_third` n'est pas stable — mais son bruit de graine "
              "non plus (cf. `le_bruit_de_lechantillon`)",
              min(variations) < 0 < max(variations),
              " · ".join(f"{x:+.1f} %" for x in variations))
        # ⚠ Le compte, a cote de la fraction : c'est lui qui montre qu'une variation de +398 %
        # est un passage de une cellule a cinq.
        maigres = [p for p in r["paires"] if (p.get("cellules_avant") or 0) < 10]
        if maigres:
            v("... et au moins une paire compare des comptes à un chiffre",
              True,
              " · ".join(f"{p['trace'][-8:]}:{p['cellules_avant']}→{p['cellules_apres']}"
                         for p in maigres))

        # ⭐⭐⭐ LA QUESTION DE `07`, REJOUEE SUR LA COLONNE QUI TIENT. `shortfall` moyenne toute
        # la queue basse sur des milliers de cellules et ne choisit aucun seuil ; son etendue de
        # graine reste sous 5 %. Une variation qui la depasse est donc attribuable a la
        # reparation, ce qui n'etait pas le cas de `fbt`. Le controle est ecrit pour tomber si
        # les variations restaient dans le bruit -- ce serait alors « la reparation ne deplace
        # rien de mesurable », qui est un resultat different et tout aussi publiable.
        # ⚠⚠⚠ LE RESULTAT, ET C'EST CELUI DES DEUX QUE LE CONTROLE PRE-ENREGISTRAIT COMME
        # « different et tout aussi publiable » : `shortfall` NE bouge PAS au-dela de son bruit
        # d'echantillonnage. Zero paire sur dix depasse +/-5 %, et le signe est melange (3 en
        # hausse, 7 en baisse). Donc, sur la colonne qu'on peut lire, la reparation ne deplace
        # rien de mesurable -- ce qui RESTAURE le titre d'origine de `07`, pour une bien
        # meilleure raison que celle qu'il donnait. Les assertions disent desormais ce qui est
        # mesure ; elles restent falsifiables, un run futur qui verrait un effet les ferait
        # tomber, et ce serait le resultat inverse.
        BRUIT_DE_GRAINE_PCT = 5.0
        vs = [p["variation_shortfall_pct"] for p in r["paires"]
              if p.get("variation_shortfall_pct") is not None and p["quads_retires"]]
        if len(vs) >= 2:
            hors = [x for x in vs if abs(x) > BRUIT_DE_GRAINE_PCT]
            v("`shortfall` ne bouge JAMAIS au-delà de son bruit de graine",
              not hors,
              f"{len(hors)}/{len(vs)} au-delà de ±{BRUIT_DE_GRAINE_PCT:.0f} % · "
              + " · ".join(f"{x:+.1f} %" for x in vs))
            v("... et son signe n'est pas plus stable que celui de l'autre colonne",
              not (min(vs) > 0 or max(vs) < 0),
              f"{sum(1 for x in vs if x > 0)} en hausse, {sum(1 for x in vs if x < 0)} en baisse")
            # ⚠⚠ LA COMPARAISON RIGOUREUSE, quand le balayage de graines est disponible :
            # chaque effet est confronte au bruit de SA PROPRE trace, et non a un plafond
            # commun. Un plafond commun est genereux pour les traces calmes et severe pour les
            # agitees ; l'appariement par trace supprime ce biais.
            bruit = RACINE / "docs" / "mesures" / "le_bruit_de_lechantillon.json"
            if bruit.is_file():
                par_trace = {x["trace"]: x for x in json.loads(bruit.read_text())["lignes"]}
                confrontes, dehors = 0, []
                for p in r["paires"]:
                    b = par_trace.get(p["trace"])
                    if not b or p.get("variation_shortfall_pct") is None:
                        continue
                    confrontes += 1
                    # ⚠ La demi-etendue, parce que l'effet se compte depuis la valeur mediane
                    # tandis que l'etendue couvre les deux cotes.
                    if abs(p["variation_shortfall_pct"]) > b["shortfall_etendue_pct"] / 2:
                        dehors.append(p["trace"])
                if confrontes >= 5:
                    v("... et face au bruit de SA PROPRE trace, la majorité reste dedans",
                      len(dehors) < confrontes / 2,
                      f"{len(dehors)}/{confrontes} dehors : "
                      + (", ".join(x[-8:] for x in dehors) or "aucune"))
        # ⚠⚠⚠ TROIS PASSAGES SUR CETTE MEME ASSERTION, ET C'EST LA MESURE QUI A TRANCHE A CHAQUE
        # FOIS. (1) Deux passages du lot rendent 3 696 puis 3 698 quads : j'ecris « la reparation
        # n'est pas deterministe » -- depuis deux sorties de terminal, c'est-a-dire depuis la
        # dette `D3` que ce fichier existe pour rembourser. (2) Le mode `--determinisme` a trois
        # repetitions rend trois certificats IDENTIQUES : je retracte. (3) A SIX repetitions :
        # 3698, 3696, 3696, 3696, **3691**, 3696 -- TROIS certificats distincts. La premiere
        # affirmation etait juste, la retractation etait fausse, et elle l'etait PAR CHANCE.
        #
        # ⭐ Le commentaire de la retractation disait pourtant « trois repetitions sont une preuve
        # faible de determinisme : elles excluent "different a chaque fois", pas "different de
        # temps en temps" ». Il avait raison et j'ai quand meme laisse le document s'y appuyer.
        # Une reserve ecrite ne dispense pas de la mesure qu'elle appelle.
        #
        # ⚠ Et le 3691 corrige un second point : ce n'est pas une bascule entre DEUX valeurs,
        # donc pas une egalite tranchee par un ordre de parcours. L'etendue mesuree est de sept
        # quads sur ~3 695, soit 0,19 %.
        det = RACINE / "docs" / "mesures" / "reparation_determinisme.json"
        if det.is_file():
            d = json.loads(det.read_text())
            v("la réparation N'EST PAS déterministe",
              not d["deterministe"],
              f"{d['distincts']} certificat(s) distinct(s) en {d['repetitions']} réparations · "
              f"quads {' · '.join(str(x) for x in d['quads'])}")
            q = d.get("quads") or []
            if len(q) >= 3:
                # ⚠ La variation est BORNEE, et c'est ce qui la rend supportable : elle porte sur
                # deux dixiemes de pour cent des quads retires. Assertion ecrite pour tomber si
                # elle s'elargissait -- ce serait un tout autre probleme.
                v("... mais sa variation reste sous un demi pour cent des quads retirés",
                  (max(q) - min(q)) / max(q) < 0.005,
                  f"étendue {max(q) - min(q)} quads sur {max(q)} — "
                  f"{100 * (max(q) - min(q)) / max(q):.2f} %")
                v("... et elle ne bascule pas entre deux valeurs seulement",
                  len(set(q)) >= 3, f"{sorted(set(q))}")
        # ⚠⚠⚠ L'HYPOTHESE DU PARALLELISME, TESTEE CONTRE SON PROPRE CONTROLE. L'aide de
        # `windcheck transform` revendique une « frozen scheduling policy » et defaute a tous
        # les coeurs. `44` a deja vu cette forme et l'a reglee par un fil unique. Le controle
        # compare les DEUX series : si un seul fil suffit a stabiliser, la cause est le
        # parallelisme et la recette de reparation reproductible est connue ; sinon elle est
        # ailleurs, et c'est un resultat different et tout aussi utile.
        det1 = RACINE / "docs" / "mesures" / "reparation_determinisme_1fil.json"
        if det1.is_file() and det.is_file():
            d1 = json.loads(det1.read_text())
            q1 = d1.get("quads") or []
            v("un seul fil est bien ce qui a été demandé", d1.get("threads") == 1,
              str(d1.get("threads")))
            if len(q1) >= 6:
                v("... et à un seul fil, la réparation devient reproductible",
                  len(set(q1)) == 1,
                  f"{len(set(q1))} valeur(s) en {len(q1)} réparations : {sorted(set(q1))}")
                # ⚠ Le controle qui donne son sens au precedent : la serie multi-fils, elle,
                # varie. Sans lui, « une seule valeur » pourrait venir d'une trace qui ne varie
                # jamais, et ne dirait rien des fils.
                v("... alors que la série multi-fils du même trace varie",
                  len(set(q)) >= 2, f"{sorted(set(q))} contre {sorted(set(q1))}")
        # ⚠⚠⚠ LE TIRAGE APPARIE, ET C'EST LUI QUI TRANCHE. Tout ce qui precede est borne par le
        # bruit d'echantillonnage ; ce mode le supprime au lieu de le borner, parce que la
        # GRILLE de parametrisation ne change pas quand la reparation retire des quads (mesure :
        # 756x2940 des deux cotes, 142 cellules perdues sur deux millions). Tirer des POSITIONS
        # rend donc le meme echantillon des deux cotes.
        app = RACINE / "docs" / "mesures" / "reparation_et_proximite_scroll1_apparie.json"
        if app.is_file():
            d = json.loads(app.read_text())
            pa = [x for x in d.get("paires", []) if x.get("usable_avant")]
            v("le lot apparié déclare bien son mode de tirage",
              d.get("tirage") == "position", str(d.get("tirage")))
            if pa:
                # ⚠ La preuve que l'appariement a PRIS : l'echantillon utile ne doit plus
                # bouger que d'une poignee de cellules, la ou le tirage par index en deplacait
                # des dizaines. Ecrit comme une part, parce que les traces n'ont pas la meme
                # taille d'echantillon.
                ecarts = [abs(x["usable_apres"] - x["usable_avant"]) / x["usable_avant"]
                          for x in pa]
                v("... et l'échantillon utile ne bouge presque plus entre avant et après",
                  max(ecarts) < 0.005,
                  f"écart max {100 * max(ecarts):.3f} % sur {len(pa)} paires")
                # ⚠⚠ LE RESULTAT. Avec le bruit retire, l'effet de la reparation sur
                # `shortfall` doit devenir bien plus petit -- ou se reveler, si le bruit le
                # masquait. Les deux sont publiables ; le controle dit lequel on a.
                vs_app = [abs(x["variation_shortfall_pct"]) for x in pa
                          if x.get("variation_shortfall_pct") is not None]
                vs_ind = [abs(x["variation_shortfall_pct"]) for x in r["paires"]
                          if x.get("variation_shortfall_pct") is not None]
                if vs_app and vs_ind:
                    v("... et l'effet mesuré sur `shortfall` devient PLUS PETIT qu'au tirage "
                      "non apparié",
                      statistics.median(vs_app) < statistics.median(vs_ind),
                      f"médiane {statistics.median(vs_app):.2f} % contre "
                      f"{statistics.median(vs_ind):.2f} %")
        v("... et chaque paire a bien retiré quelque chose",
          all(p["quads_retires"] > 0 for p in r["paires"] if p["statut"] != "already_clean"),
          " · ".join(f"{p['quads_retires']} quads" for p in r["paires"]))

    print()
    if echecs:
        print(f"  ECHEC ({echecs} failures)")
    else:
        print(f"  ALL PASS (0 failures, {comptees} checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--corpus", choices=sorted(CORPUS), default="scroll1")
    p.add_argument("--limite", type=int, default=0,
                   help="ne mesurer que les N traces les plus couvrantes")
    p.add_argument("--determinisme", metavar="TRACE",
                   help="réparer N fois la MEME trace et comparer les certificats")
    p.add_argument("--repetitions", type=int, default=3)
    p.add_argument("--threads", type=int, default=None,
                   help="forcer le nombre de fils de `windcheck transform` (0 = tous)")
    p.add_argument("--apparie", action="store_true",
                   help="tirer par POSITION de grille — même échantillon avant et après")
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    a = p.parse_args()

    if a.determinisme:
        d = mesurer_determinisme(a.determinisme, a.repetitions, a.corpus, a.threads)
        print(f"{d['trace']} — {d['repetitions']} réparations"
              + (f", --threads {d['threads']}" if d.get("threads") is not None else ""))
        for i, c in enumerate(d["certificats"], 1):
            if c is None:
                print(f"  {i}. échec")
                continue
            print(f"  {i}. {c['n_removed_quads']:6d} quads retirés · "
                  f"aire gardée {100 * c['retained_area_fraction']:.6f} % · {c['status']}")
        print(f"\n  certificats distincts : {d['distincts']} — "
              + ("DETERMINISTE" if d["deterministe"] else "NON DETERMINISTE"))
        if a.json:
            a.json.parent.mkdir(parents=True, exist_ok=True)
            a.json.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"écrit : {a.json}")
        return 0

    # ⚠⚠ `--verifier` seul RELIT la mesure au lieu de la refaire : une paire coute plusieurs
    # minutes (une reparation plus deux proximites sur des maillages de 1,8 M de cellules),
    # donc une batterie qui remesurerait serait une batterie que personne ne lance. La mesure
    # se refait explicitement avec `--json`.
    if a.verifier and not a.json:
        cache = RACINE / "docs" / "mesures" / f"reparation_et_proximite_{a.corpus}.json"
        garde = json.loads(cache.read_text()) if cache.is_file() else None
        return 1 if _verifier(garde) else 0

    r = mesurer(a.corpus, a.limite, a.apparie)
    print(f"{r['corpus']} — {r['eligibles']} traces éligibles "
          f"(sales et > {r['span_minimum']} tour)\n")
    if r["paires"]:
        # ⚠ `cellules` est imprime A COTE de `fbt` exprès : une fraction dont le numerateur
        # tient sur un chiffre n'est pas une fraction, et seul le compte le montre.
        print(f"  {'trace':46s} {'tours':>6s} {'retiré':>8s} {'cell.':>9s} "
              f"{'Δ fbt':>9s} {'shortfall':>17s} {'Δ short':>8s}")
        for x in r["paires"]:
            var = f"{x['variation_pct']:+.1f} %" if x["variation_pct"] is not None else "   —  "
            vsh = (f"{x['variation_shortfall_pct']:+.1f} %"
                   if x.get("variation_shortfall_pct") is not None else "   —  ")
            cell = f"{x['cellules_avant']}→{x['cellules_apres']}"
            short = (f"{x['shortfall_avant']:.4f}→{x['shortfall_apres']:.4f}"
                     if x.get("shortfall_avant") is not None else "—")
            print(f"  {x['trace']:46s} {x['span_tours']:6.2f} "
                  f"{x['quads_retires']:8d} {cell:>9s} {var:>9s} {short:>17s} {vsh:>8s}")
    for x in r.get("sautes", []):
        print(f"  ⚠ {x['trace']:46s} sautée — {x['raison']}", file=sys.stderr)
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
