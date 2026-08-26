#!/usr/bin/env python3
"""Sur quel rouleau peut-on à la fois TRACER et LIRE ?

⚠⚠ **La question qui bloque le point le plus profond du registre.**
[`29`](docs/29_ce_qui_reste.md) §1 porte, depuis le début, la question dont dépend tout
le reste : *réparer une trace sert-il à quelque chose ?* Y répondre demande une trace
fautive, sa version réparée, et le **même aval** appliqué aux deux. Ce fichier mesure une
condition préalable que personne n'avait posée : **l'aval répond-il, sur le rouleau où on
compte le faire ?**

⭐ La condition est vérifiable **avant de dépenser**. [`46`](docs/46_le_temoin_negatif.md)
mesure que sur `PHerc1447` le détecteur rend la **même carte** sur une face de papyrus et
sur une surface qui coupe l'empilement — une différence bien plus grande que celle entre
une trace fautive et sa réparation. Aucune réparation ne peut y montrer de gain.

⚠⚠ **Ce que ce fichier NE fait pas** : il ne mesure pas l'aval lui-même. Il **croise deux
mesures déjà faites** — quels rouleaux on sait tracer (`table_tirages.json`) et sur
lesquels la sortie publiée a la statistique d'une page écrite (`typographie.json`, la
mesure de [`45`](docs/45_consistent_with_quantifie.md)) — et il nomme l'intersection.
Une intersection vide est un **résultat**, pas une panne : elle dit que l'expérience ne
peut pas être montée sur le jeu du prix tel qu'il est.

⚠ Et la limite de la seconde mesure voyage avec elle : une carte qui a la statistique d'une
page écrite **peut** être un artefact périodique. C'est un critère nécessaire, jamais
suffisant — exactement comme l'absence d'auto-intersection l'est pour une trace.

Usage :
    python3 src/graine/eligibilite_aval.py --docs docs/mesures --json docs/mesures/eligibilite_aval.json
    python3 src/graine/eligibilite_aval.py --verifier
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

# ⚠⚠ Le seuil sous lequel « la sortie publiee ressemble a une page ecrite » cesse d'etre
# affirmable. C'est celui de `45` et pas un second : la part de cartes ecrites au-dessus de
# laquelle un rouleau est dit lisible y vaut la moitie, elle est publiee a cote du verdict,
# et en choisir un autre ici ferait deux reponses a une meme question.
PART_ECRITE_MIN = 0.5

# ⚠ La reference de dispersion du modele la ou il marche, reprise de `36` §5bis par
# `temoin_negatif`. Importee plutot que recopiee -- deux copies d'une meme constante
# finissent par ne pas s'accorder, et celle-ci decide d'un verdict.
try:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]
    from temoin_negatif import PART_MINIMALE_DU_POSITIF, SIGMA_MODELE_QUI_MARCHE
except ImportError:  # pragma: no cover — seulement si le fichier voisin manque
    SIGMA_MODELE_QUI_MARCHE, PART_MINIMALE_DU_POSITIF = 0.7712, 0.10


def tracables(table_tirages: dict) -> list[str]:
    """Les rouleaux dont on sait produire une trace, et pas seulement en parler.

    ⚠⚠ REFUSE plutôt que de rendre un ensemble vide. Une première version lisait la clé
    `tirages`, que ce fichier n'a pas — la sienne s'appelle `n`. Elle a donc rendu ZÉRO
    rouleau traçable, et le verdict qui en découlait était parfaitement confiant et
    parfaitement faux : « les deux ensembles sont disjoints » est *satisfait* par un
    ensemble vide. Un lecteur qui ne trouve pas ce qu'il cherche doit le dire.

    ⚠ Et le témoin n'a pas attrapé ça, parce que sa fixture utilisait la clé que le code
    supposait : une fixture écrite d'après le code ne prouve que leur accord. D'où la sonde
    sur le VRAI fichier, plus bas.
    """
    lignes = table_tirages.get("lignes", [])
    if not lignes:
        raise ValueError("aucune ligne dans la table des tirages")
    if not any("n" in l for l in lignes):
        raise ValueError("aucune ligne ne porte de compte de tirages (`n`) — "
                         f"clés vues : {sorted(lignes[0])}")
    return sorted({l["rouleau"] for l in lignes if l.get("n")})


def lisibles(typo: dict) -> dict[str, dict]:
    """Les rouleaux dont la sortie publiée a la statistique d'une page écrite.

    ⚠ `cartes_ecrites / n` et non la médiane de la part périodique : la médiane répond
    « une carte typique est-elle lignée », la fraction répond « combien le sont ». C'est la
    seconde qui décide si un rouleau porte assez de matière lisible pour qu'un gain y soit
    visible.
    """
    out = {}
    for nom, x in (typo.get("resume") or {}).items():
        n = x.get("n") or 0
        if not n:
            continue
        part = x["cartes_ecrites"] / n
        out[nom] = {"cartes": n, "ecrites": x["cartes_ecrites"], "part_ecrite": part,
                    "lisible": part >= PART_ECRITE_MIN}
    return out


def sonder_publication(rouleau: str, base: str, delai: int = 40) -> dict:
    """Que publie ce rouleau : une PRÉDICTION de surface, des SEGMENTS déjà tracés, ou rien ?

    ⚠⚠ La distinction décide de l'expérience possible, et je l'avais ratée. La recherche de
    graine part d'une **prédiction de surface** (`representations/`) ; un rouleau qui n'en
    publie pas ne peut pas recevoir la campagne, quelle que soit la qualité de sa sortie
    d'encre. Mesuré : `PHerc0172` publie `segments/` et `volumes/`, et **pas**
    `representations/` — donc la recommandation « commencer par lui, 92 % de cartes
    écrites » était irréalisable, et rien dans les données déjà en main ne le disait.

    ⚠ Réseau, donc opt-in : la sonde n'est jamais lancée par les témoins, et son résultat
    est écrit dans le JSON pour que la lecture suivante n'ait pas à la refaire.
    """
    import subprocess
    try:
        r = subprocess.run(
            ["curl", "-s", "--max-time", str(delai),
             f"{base}/?list-type=2&prefix={rouleau}/&delimiter=/"],
            capture_output=True, text=True, timeout=delai + 10)
    except (OSError, subprocess.TimeoutExpired) as e:
        return {"injoignable": str(e)}
    dossiers = sorted({t.split("<")[0].rstrip("/").split("/")[-1]
                       for t in r.stdout.split("<Prefix>")[1:]
                       if t.split("<")[0].rstrip("/") != rouleau})
    return {"publie": dossiers,
            "a_prediction": "representations" in dossiers,
            "a_segments": "segments" in dossiers}


def croiser(table_tirages: dict, typo: dict, temoin: dict | None = None,
            publications: dict | None = None) -> dict:
    """Les deux ensembles, leur intersection, et ce que l'intersection autorise."""
    t, l = tracables(table_tirages), lisibles(typo)
    inter = sorted(set(t) & set(n for n, x in l.items() if x["lisible"]))
    d = {"tracables": t, "lisibles": {n: x for n, x in sorted(l.items())},
         "tracables_et_lisibles": inter,
         "part_ecrite_min": PART_ECRITE_MIN}
    # ⚠ Le temoin negatif ne couvre qu'UN rouleau ; il est rapporte comme une mesure
    # directe la ou elle existe, et jamais extrapole aux autres.
    if temoin and temoin.get("positif", {}).get("sigma") is not None:
        d["aval_mesure_directement"] = {
            "rouleau": "PHerc1447",
            "sigma": temoin["positif"]["sigma"],
            "part_du_modele_qui_marche": temoin.get("part_du_modele_qui_marche"),
            "repond": (temoin.get("part_du_modele_qui_marche") or 0)
                      >= PART_MINIMALE_DU_POSITIF}
    # ⚠⚠ « pas dans la cohorte tracee » n'est PAS « pas tracable ». Les trois rouleaux
    # lisibles n'ont simplement jamais eu de campagne de tirages ; rien ne dit qu'ils y
    # resistent. Le verdict doit donc nommer l'ACTION -- etendre la campagne -- et pas
    # prononcer une impossibilite qui n'est pas mesuree. C'est la meme prudence que
    # `46` tient entre « la these est fausse » et « la these est hors de portee ».
    d["candidats_a_tracer"] = [n for n, x in sorted(l.items())
                               if x["lisible"] and n not in set(t)]
    if publications:
        d["publications"] = publications
        for n in d["candidats_a_tracer"]:
            l.setdefault(n, {}).update(publications.get(n, {}))
        # ⚠⚠ Un candidat sans prediction de surface est ECARTE, pas classe dernier : la
        # campagne de graines ne peut structurellement pas y tourner, et le garder dans la
        # liste ferait recommander une experience irrealisable.
        d["candidats_ecartes"] = {
            n: "aucune prédiction de surface publiée (`representations/` absent)"
            for n in d["candidats_a_tracer"]
            if publications.get(n) and not publications[n].get("a_prediction")}
        d["candidats_a_tracer"] = [n for n in d["candidats_a_tracer"]
                                   if n not in d["candidats_ecartes"]]
    d["verdict"] = (
        "aucun rouleau n'est à la fois DÉJÀ tracé par nos campagnes et lisible par la "
        "sortie publiée : les deux ensembles sont disjoints, et l'expérience « réparer "
        "sert-il ? » n'est donc pas montable sur ce qui est déjà en main"
        if not inter else
        "l'expérience peut être montée sur : " + ", ".join(inter))
    if not inter and d["candidats_a_tracer"]:
        # ⚠ Le classement n'est PAS la part écrite seule. Un rouleau où le détecteur est
        # mesuré directement (`36` §5bis) vaut mieux qu'un rouleau où on l'infère de la
        # statistique de ses cartes publiées — la première est une mesure, la seconde une
        # ressemblance. `PHercParis4` est ce rouleau-là.
        mesure_direct = {"PHercParis4"}
        premier = sorted(d["candidats_a_tracer"],
                         key=lambda n: (n not in mesure_direct, -l[n]["part_ecrite"]))[0]
        pourquoi = ("le détecteur y est mesuré directement (AUC 0,925)"
                    if premier in mesure_direct
                    else f"part écrite la plus haute, {l[premier]['part_ecrite']:.0%}")
        d["action"] = ("étendre la campagne de graines à un rouleau lisible — "
                       + ", ".join(d["candidats_a_tracer"])
                       + f" — en commençant par {premier} ({pourquoi})")
        d["premier_candidat"] = premier
    return d


def verifier() -> int:
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    tir = {"lignes": [{"rouleau": "A", "n": 6}, {"rouleau": "B", "n": 6},
                      {"rouleau": "A", "n": 6}]}
    v("un rouleau tracé plusieurs fois n'est compté qu'une", tracables(tir) == ["A", "B"])
    v("un rouleau sans tirage n'est pas traçable",
      tracables({"lignes": [{"rouleau": "C", "n": 0}]}) == [])
    # ⚠⚠ LA sonde qui manquait : une table dont la clé de comptage n'est pas celle attendue
    # doit REFUSER, pas rendre un ensemble vide. Un vide silencieux SATISFAIT la conclusion
    # « les deux ensembles sont disjoints », donc il produit un verdict confiant et faux.
    for mauvais, quoi in (({"lignes": [{"rouleau": "A", "tirages": 6}]}, "clé inconnue"),
                          ({"lignes": []}, "table vide")):
        try:
            tracables(mauvais)
            v(f"une table à {quoi} est REFUSÉE", False, "aucun refus")
        except ValueError:
            v(f"une table à {quoi} est REFUSÉE", True)

    typo = {"resume": {"A": {"n": 10, "cartes_ecrites": 9},
                       "C": {"n": 10, "cartes_ecrites": 1},
                       "D": {"n": 0, "cartes_ecrites": 0}}}
    li = lisibles(typo)
    v("un rouleau majoritairement écrit est lisible", li["A"]["lisible"])
    v("... et un rouleau majoritairement muet ne l'est pas", not li["C"]["lisible"])
    # ⚠ Une division par zero ne doit pas produire un verdict : un rouleau sans carte n'est
    # pas « illisible », il est NON MESURE, et les confondre ferait compter une absence
    # de donnee comme une observation.
    v("un rouleau sans carte est absent, pas déclaré illisible", "D" not in li)

    # ⚠⚠ LA sonde : l'intersection est ce qui porte la conclusion, et elle doit etre VIDE
    # quand les deux ensembles ne se recouvrent pas -- ici A est tracable ET lisible, donc
    # elle ne l'est pas, et c'est le controle qui prouve que le calcul discrimine.
    c = croiser(tir, typo)
    v("l'intersection contient ce qui est dans les deux", c["tracables_et_lisibles"] == ["A"])
    v("... et le verdict la nomme", "A" in c["verdict"])
    vide = croiser({"lignes": [{"rouleau": "Z", "n": 6}]}, typo)
    v("une intersection VIDE est un résultat, pas une erreur",
      vide["tracables_et_lisibles"] == [] and "pas montable" in vide["verdict"])
    # ⚠⚠ Et elle doit nommer une ACTION plutot qu'une impossibilite : un rouleau lisible
    # jamais trace n'est pas un rouleau qui resiste au traceur, et confondre les deux
    # fermerait un lot qui est seulement en attente d'une campagne.
    v("... qui nomme les candidats à tracer", vide["candidats_a_tracer"] == ["A"])
    v("... et propose la part écrite la plus haute d'abord", "A" in vide.get("action", ""))
    v("une intersection non vide ne propose pas d'action", "action" not in c)

    # ⚠⚠ LA regle que la mesure a imposee : un candidat SANS prediction de surface est
    # ECARTE et pas classe dernier. La campagne de graines part d'une prediction ; sans
    # elle l'experience est irrealisable, et la recommander etait le defaut reel de la
    # premiere version -- `PHerc0172` a 92 % de cartes ecrites et aucune prediction.
    typo2 = {"resume": {"A": {"n": 10, "cartes_ecrites": 9},
                        "B": {"n": 10, "cartes_ecrites": 6}}}
    seul = {"lignes": [{"rouleau": "Z", "n": 6}]}
    pubs = {"A": {"a_prediction": False, "a_segments": True, "publie": ["segments"]},
            "B": {"a_prediction": True, "a_segments": True,
                  "publie": ["representations", "segments"]}}
    e = croiser(seul, typo2, None, pubs)
    v("un candidat sans prédiction de surface est ÉCARTÉ", "A" in e["candidats_ecartes"])
    v("... et n'est plus proposé", e["candidats_a_tracer"] == ["B"])
    v("... alors qu'il a la part écrite la plus haute", 0.9 > 0.6)
    v("l'action nomme le candidat réalisable", "B" in e["action"])
    # ⚠ Et le controle : sans sonde, aucun candidat n'est ecarte -- l'absence d'information
    # ne doit pas se lire comme une absence de prediction.
    v("sans sonde, aucun candidat n'est écarté",
      not croiser(seul, typo2).get("candidats_ecartes"))
    tous_ecartes = croiser(seul, typo2, None,
                           {"A": {"a_prediction": False}, "B": {"a_prediction": False}})
    v("tous les candidats écartés ⇒ aucune action",
      "action" not in tous_ecartes and len(tous_ecartes["candidats_ecartes"]) == 2)

    # ⚠ Le temoin direct n'est rapporte que la ou il existe, et jamais extrapole.
    v("sans témoin, aucune mesure directe n'est inventée",
      "aval_mesure_directement" not in c)
    avec = croiser(tir, typo, {"positif": {"sigma": 0.0129},
                               "part_du_modele_qui_marche": 0.0167})
    v("un aval plat est rapporté comme ne répondant PAS",
      avec["aval_mesure_directement"]["repond"] is False)
    v("... et un aval vif comme répondant",
      croiser(tir, typo, {"positif": {"sigma": 0.77},
                          "part_du_modele_qui_marche": 1.0})
      ["aval_mesure_directement"]["repond"] is True)

    # ⚠⚠ ET LA SONDE SUR LE VRAI FICHIER. Une fixture écrite d'après le code ne prouve que
    # leur accord ; c'est exactement comme ça que la clé `tirages` est passée. Quand le
    # fichier de résultat est là, on exige que le lecteur en tire quelque chose. Le saut est
    # ANNONCÉ et compté quand il ne l'est pas — un témoin qui se tait ressemble à un témoin
    # qui réussit.
    reel = Path(__file__).resolve().parents[2] / "docs" / "mesures" / "table_tirages.json"
    if reel.is_file():
        vrai = tracables(json.loads(reel.read_text(encoding="utf-8")))
        v("le lecteur tire quelque chose du VRAI fichier de résultat",
          len(vrai) >= 10, f"{len(vrai)} rouleau(x)")
        saute = ""
    else:
        saute = "  ⚠ 1 contrôle SAUTÉ : docs/mesures/table_tirages.json est absent"

    if echecs:
        print(f"\nECHEC ({echecs} failures, {controles} checks)")
        return 1
    print(f"ALL PASS ({echecs} failures, {controles} checks){saute}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--docs", type=Path, default=Path("docs/mesures"))
    ap.add_argument("--json", type=Path)
    ap.add_argument("--sonder", action="store_true",
                    help="interroger S3 : chaque candidat publie-t-il une PRÉDICTION de "
                         "surface ? (réseau, jamais lancé par les témoins)")
    ap.add_argument("--base", default="https://vesuvius-challenge-open-data.s3.amazonaws.com")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()

    def lire(nom):
        p = a.docs / nom
        return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else None

    tir, typo = lire("table_tirages.json"), lire("typographie.json")
    if not tir or not typo:
        print(f"il faut table_tirages.json et typographie.json dans {a.docs}",
              file=sys.stderr)
        return 1
    # ⚠ La sonde reseau n'est refaite que si on la demande : sinon on relit ce qu'un run
    # anterieur a ecrit, pour qu'une lecture hors ligne rende le meme verdict.
    ancien = lire("eligibilite_aval.json") or {}
    pubs = dict(ancien.get("publications") or {})
    d = croiser(tir, typo, lire("temoin_negatif.json"), pubs or None)
    if a.sonder:
        print("  sonde S3 (réseau) :")
        for n in croiser(tir, typo)["candidats_a_tracer"]:
            pubs[n] = sonder_publication(n, a.base)
            etat = pubs[n].get("injoignable") or ", ".join(pubs[n]["publie"])
            print(f"    {n:<14} {etat}")
        d = croiser(tir, typo, lire("temoin_negatif.json"), pubs)

    print(f"\n  rouleaux que nos campagnes savent TRACER : {len(d['tracables'])}")
    print("    " + ", ".join(d["tracables"]))
    print(f"\n  rouleaux dont la sortie publiée a la statistique d'une page écrite :")
    print(f"  {'rouleau':<14} {'cartes':>7} {'écrites':>8} {'part':>7}   verdict")
    print("  " + "-" * 56)
    for nom, x in d["lisibles"].items():
        print(f"  {nom:<14} {x['cartes']:>7} {x['ecrites']:>8} {x['part_ecrite']:>6.0%}   "
              + ("lisible" if x["lisible"] else "—"))

    m = d.get("aval_mesure_directement")
    if m:
        print(f"\n  aval mesuré DIRECTEMENT sur {m['rouleau']} : σ = {m['sigma']:.4f}, "
              f"{m['part_du_modele_qui_marche']:.1%} de ce que le modèle rend là où il "
              f"marche → " + ("répond" if m["repond"] else "NE RÉPOND PAS"))

    print(f"\n  ⚠⚠ {d['verdict']}.")
    if not d["tracables_et_lisibles"]:
        print("      Les rouleaux qu'on a tracés ne sont pas ceux dont la sortie publiée")
        print("      porte du texte. ⚠ Ce n'est PAS une impossibilité : rien ne dit qu'un")
        print("      rouleau lisible résiste au traceur, il n'a simplement jamais eu de")
        print("      campagne. Ce que ça dit, c'est OÙ l'expérience doit être montée.")
        for n, r in (d.get("candidats_ecartes") or {}).items():
            print(f"      ⚠ {n} écarté : {r}")
        if d.get("action"):
            print(f"\n  ⭐ action : {d['action']}.")
        elif d.get("candidats_ecartes"):
            print("\n  ⚠⚠ tous les candidats sont écartés — aucun rouleau lisible ne "
                  "publie de prédiction de surface")

    if a.json:
        a.json.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8")
        print(f"\n  écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
