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


def _proximite(maillage: Path, etiquette: str) -> dict | None:
    """
    @brief La proximité anormale d'un maillage, par l'instrument de `07`.
    """
    r = subprocess.run(
        ["uv", "run", "python", str(PROXIMITY), str(maillage), "--json", "--label", etiquette],
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


def _reparer(trace: Path, sortie: Path) -> dict | None:
    """
    @brief La réparation de `windcheck`, et son certificat.
    """
    r = subprocess.run(["uv", "run", "windcheck", "transform", str(trace), "--out", str(sortie)],
                       capture_output=True, text=True, cwd=WINDCHECK, timeout=3600)
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


def mesurer(corpus: str = "scroll1", limite: int = 0) -> dict:
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
        avant = _proximite(maille, f"{nom}:avant")
        if not avant:
            sautes.append((nom, "proximité avant a échoué"))
            continue
        with tempfile.TemporaryDirectory() as tmp:
            cert = _reparer(trace, Path(tmp))
            repare = next(Path(tmp).glob("*_transformed.tifxyz"), None)
            repare = maillage_de(repare) if repare else None
            apres = _proximite(repare, f"{nom}:apres") if repare else None
            if cert is None:
                sautes.append((nom, "réparation a échoué"))
            elif apres is None:
                sautes.append((nom, "proximité après a échoué"))
        if not apres or cert is None:
            continue
        fa = avant.get("fraction_below_third")
        fp = apres.get("fraction_below_third")
        paires.append(dict(
            trace=nom, corpus=nom_long,
            span_tours=entree.get("covering_span_rev"),
            statut=cert.get("status"),
            quads_retires=cert["n_removed_quads"],
            aire_gardee_pct=100.0 * cert["retained_area_fraction"],
            aire_excisee_fraction=cert.get("excised_area_fraction"),
            fbt_avant=fa, fbt_apres=fp,
            variation_pct=(100.0 * (fp - fa) / fa) if fa else None,
        ))
    return dict(corpus=nom_long, eligibles=len(eligibles(corpus)),
                span_minimum=SPAN_MINIMUM, paires=paires,
                sautes=[{"trace": t, "raison": r} for t, r in sautes])


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
        # ⚠⚠⚠ LE RESULTAT, ET IL VA PLUS LOIN QUE `07`. Ce document conclut que la variation
        # « n'est pas proportionnelle a ce qui est retire ». Sur deux traces de la MEME
        # provenance et du MEME rouleau, ce n'est pas la proportionnalite qui manque : le
        # SIGNE lui-meme change. Ecrit comme un controle pour qu'un run futur qui les
        # verrait toutes aller dans le meme sens le FASSE TOMBER -- ce serait le resultat.
        variations = [p["variation_pct"] for p in r["paires"]
                      if p.get("variation_pct") is not None and p["quads_retires"]]
        if len(variations) >= 2:
            v("le signe de la variation n'est pas stable, même à provenance égale",
              min(variations) < 0 < max(variations),
              " · ".join(f"{x:+.1f} %" for x in variations))
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
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    a = p.parse_args()

    # ⚠⚠ `--verifier` seul RELIT la mesure au lieu de la refaire : une paire coute plusieurs
    # minutes (une reparation plus deux proximites sur des maillages de 1,8 M de cellules),
    # donc une batterie qui remesurerait serait une batterie que personne ne lance. La mesure
    # se refait explicitement avec `--json`.
    if a.verifier and not a.json:
        cache = RACINE / "docs" / "mesures" / f"reparation_et_proximite_{a.corpus}.json"
        garde = json.loads(cache.read_text()) if cache.is_file() else None
        return 1 if _verifier(garde) else 0

    r = mesurer(a.corpus, a.limite)
    print(f"{r['corpus']} — {r['eligibles']} traces éligibles "
          f"(sales et > {r['span_minimum']} tour)\n")
    if r["paires"]:
        print(f"  {'trace':46s} {'tours':>6s} {'retiré':>8s} {'avant':>8s} {'après':>8s} {'Δ':>8s}")
        for x in r["paires"]:
            var = f"{x['variation_pct']:+.1f} %" if x["variation_pct"] is not None else "   —  "
            print(f"  {x['trace']:46s} {x['span_tours']:6.2f} "
                  f"{x['quads_retires']:8d} {x['fbt_avant'] * 100:7.3f}% "
                  f"{x['fbt_apres'] * 100:7.3f}% {var:>8s}")
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
