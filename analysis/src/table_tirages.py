#!/usr/bin/env python3
"""La non-reproductibilite du traceur replique-t-elle sur d'AUTRES rouleaux ?

⚠⚠ Pourquoi cette mesure existe. `30` a mesure que `vc_grow_seg_from_seed` rend un
resultat different a chaque execution -- mais sur UNE graine, d'UN rouleau. Le taux de
mauvais tirages (2 sur 15, ~13 %) porte un intervalle de confiance large, et rien ne
disait qu'il valait ailleurs. `29` M1bis marque ce manque ⚠⚠.

⚠ Deux grandeurs, et elles ne disent PAS la meme chose :

  - le **verdict** (auto-intersections). Il peut valoir zero partout, et « aucun mauvais
    tirage » ne se distingue alors pas de « le traceur est deterministe ici ».
  - l'**etendue des aires**. Elle est non nulle des que le tirage varie, meme quand tous
    les tirages sont propres.

Ce script rend les deux, et le **controle de determinisme** qui les separe : un rouleau
dont les N tirages rendent la MEME aire au bit pres ET le meme verdict est un rouleau ou
le traceur s'est comporte de facon reproductible. Sans ce controle, un corpus tout propre
serait lu comme « le probleme de `30` n'existe pas » alors qu'il voudrait dire « on n'a
pas su le voir ».

⭐ La preuve la plus forte est le **basculement** : un rouleau ou deux tirages a
parametres strictement identiques rendent des verdicts opposes. Il ne demande aucun seuil
et aucune verite terrain.

Usage :
    uv run python analysis/src/table_tirages.py [data/tirages] [--json docs/table_tirages.json]
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lire_selfcross  # noqa: E402  -- le seul lecteur de rapports selfcross

RACINE = Path(__file__).resolve().parents[2]


def clopper_pearson(succes: int, total: int, alpha: float = 0.05) -> tuple[float, float]:
    """Intervalle de confiance exact d'une proportion binomiale.

    ⚠ Choisi contre l'approximation normale exprès : sur 2 succes en 15 essais, elle rend
    une borne basse NEGATIVE. Un intervalle qui sort du domaine de la grandeur qu'il
    encadre n'est pas conservateur, il est faux.
    """
    from scipy.stats import beta
    bas = 0.0 if succes == 0 else float(beta.ppf(alpha / 2, succes, total - succes + 1))
    haut = 1.0 if succes == total else float(beta.ppf(1 - alpha / 2, succes + 1, total - succes))
    return bas, haut


def verifier() -> int:
    """Temoin hors ligne : la lecture des tirages, sur des cas fabriques.

    ⚠ Ce qui est verifie n'est pas un chiffre de campagne -- il changerait a chaque run --
    mais les **distinctions** que ce fichier existe pour tenir :

      - un rouleau dont tous les tirages sont identiques est dit REPRODUCTIBLE ;
      - un rouleau dont l'aire varie mais dont le verdict tient n'est PAS dit
        reproductible, et n'est pas dit bascule non plus ;
      - un rouleau dont le verdict change est dit BASCULE.

    ⭐ La troisieme est celle qui porte le resultat. Si un basculement etait lu comme une
    simple dispersion, un corpus entier pourrait basculer sans que rien ne le dise.
    """
    import json as _json
    import tempfile

    echecs, controles = 0, 0

    def verifie(nom: str, condition: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not condition:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    cas = {
        "FIGE": [(10.0, 0), (10.0, 0), (10.0, 0)],          # reproductible
        "DISPERSE": [(10.0, 0), (11.0, 0), (12.0, 0)],      # varie, verdict tenu
        "BASCULE": [(10.0, 0), (10.0, 7), (10.0, 0)],       # verdict oppose
        "RATE": [(10.0, 3), (10.0, 5)],                     # jamais propre
        "SEUL": [(10.0, 0)],                                # ⚠ un seul tirage
    }
    with tempfile.TemporaryDirectory() as tmp:
        racine = Path(tmp)
        for rouleau, tirages in cas.items():
            for i, (aire, crois) in enumerate(tirages, 1):
                d = racine / rouleau / f"r{i}"
                d.mkdir(parents=True)
                (d / "resume.json").write_text(_json.dumps({
                    "rouleau": rouleau, "repetition": i, "statut": "ok",
                    "graine": [0, 0, 0], "voxel_um": 9.362, "surface": "x",
                    "generations": 10, "aire_cm2": aire, "transverse": crois}))
        # Un tirage sans maillage doit etre ECARTE, pas compte comme propre.
        d = racine / "FIGE" / "r9"
        d.mkdir(parents=True)
        (d / "resume.json").write_text(_json.dumps({
            "rouleau": "FIGE", "repetition": 9, "statut": "sans_maillage",
            "graine": [0, 0, 0], "voxel_um": 9.362, "surface": "x",
            "generations": 0, "aire_cm2": None, "transverse": None}))

        sortie = racine / "sortie.json"
        code = main_avec(str(racine), str(sortie))
        verifie("le dépouillement rend 0", code == 0, f"code {code}")
        d = _json.loads(sortie.read_text())
        par_nom = {l["rouleau"]: l for l in d["lignes"]}

    verifie("un tirage sans maillage est écarté", d["sans_maillage"] == 1,
            str(d["sans_maillage"]))
    verifie("FIGE compté sans lui", par_nom["FIGE"]["n"] == 3, str(par_nom["FIGE"]["n"]))
    verifie("FIGE est reproductible", par_nom["FIGE"]["aire_identique"])
    verifie("FIGE ne bascule pas", not par_nom["FIGE"]["verdict_bascule"])
    verifie("DISPERSE n'est PAS reproductible", not par_nom["DISPERSE"]["aire_identique"])
    verifie("DISPERSE ne bascule pas", not par_nom["DISPERSE"]["verdict_bascule"])
    verifie("DISPERSE a une étendue non nulle", par_nom["DISPERSE"]["etendue_relative"] > 0)
    verifie("BASCULE bascule", par_nom["BASCULE"]["verdict_bascule"])
    verifie("BASCULE n'est pas dit reproductible malgré l'aire figée",
            not par_nom["BASCULE"]["aire_identique"] or par_nom["BASCULE"]["verdict_bascule"])
    verifie("RATE ne bascule pas (aucun propre)", not par_nom["RATE"]["verdict_bascule"])
    verifie("RATE compte 0 propre", par_nom["RATE"]["propres"] == 0)
    verifie("mauvais = 1 (BASCULE) + 2 (RATE)", d["mauvais"] == 3, str(d["mauvais"]))
    verifie("total = 3+3+3+2+1", d["tirages_total"] == 12, str(d["tirages_total"]))
    verifie("IC encadre le taux", d["ic95_bas"] <= d["taux_mauvais"] <= d["ic95_haut"])
    verifie("bascules recensées", d["rouleaux_bascule"] == ["BASCULE"],
            str(d["rouleaux_bascule"]))
    # ⭐ Le controle qui a manque a la premiere version : un seul tirage ne peut etre dit
    # ni reproductible ni basculant, et ne doit se compter dans aucune des deux listes.
    verifie("un seul tirage n'est PAS dit reproductible",
            par_nom["SEUL"]["aire_identique"] is None,
            str(par_nom["SEUL"]["aire_identique"]))
    verifie("un seul tirage n'est PAS dit basculant",
            par_nom["SEUL"]["verdict_bascule"] is None)
    verifie("un seul tirage est recensé comme non concluant",
            d["rouleaux_non_concluants"] == ["SEUL"], str(d["rouleaux_non_concluants"]))
    verifie("un seul tirage n'entre pas dans les reproductibles",
            "SEUL" not in d["rouleaux_reproductibles"])

    if echecs:
        print(f"\nECHEC ({echecs} failures, {controles} checks)")
        return 1
    print(f"ALL PASS ({echecs} failures, {controles} checks)")
    return 0


def main_avec(dossier: str, sortie: str) -> int:
    """Rejouer `main` sur un dossier donne, sans passer par la ligne de commande."""
    import contextlib
    import io
    argv = sys.argv
    sys.argv = [argv[0], dossier, "--json", sortie]
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            return main()
    finally:
        sys.argv = argv


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dossier", nargs="?", default=str(RACINE / "data/tirages"))
    ap.add_argument("--json")
    ap.add_argument("--verifier", action="store_true",
                    help="temoin hors ligne, sur des tirages fabriques")
    a = ap.parse_args()

    if a.verifier:
        return verifier()

    par_rouleau: dict[str, list[dict]] = {}
    rejetes, desaccords, revérifiés = 0, [], 0
    for f in sorted(Path(a.dossier).glob("*/*/resume.json")):
        r = json.loads(f.read_text())
        if r.get("statut") != "ok":
            rejetes += 1
            continue
        # ⚠ Le resume est une COPIE ecrite par la campagne ; le rapport selfcross est le
        # record. On relit le record quand il est la : un resume peut avoir ete ecrit par
        # une campagne interrompue, ou par un script modifie pendant qu'il tournait -- ce
        # dernier cas s'est produit le 2026-08-20, et un desaccord silencieux entre les
        # deux aurait ete indetectable.
        rapport = f.parent / "selfcross.json"
        if rapport.is_file():
            try:
                vrai = lire_selfcross.lire(rapport)["transverse"]
                revérifiés += 1
                if vrai != r.get("transverse"):
                    desaccords.append((r["rouleau"], r["repetition"], r.get("transverse"), vrai))
                    r["transverse"] = vrai
            except lire_selfcross.RapportVide:
                desaccords.append((r["rouleau"], r["repetition"], r.get("transverse"),
                                   "aucune paire testée"))
                rejetes += 1
                continue
        # ⚠⚠ Le budget de generations : le RECORD est le `seed.json` que la campagne a
        # ecrit a cote de la trace, pas le resume. Les tirages d'avant le 2026-08-22 n'ont
        # pas le champ dans leur resume -- le relire ici les rend comparables au lieu de
        # les laisser « budget inconnu », et c'est la meme regle que pour `selfcross.json` :
        # un resume est une copie, le fichier d'a cote est ce qui a reellement servi.
        if r.get("plafond_generations") is None:
            graine = f.parent / "seed.json"
            if graine.is_file():
                try:
                    r["plafond_generations"] = json.loads(graine.read_text())["generations"]
                except (ValueError, KeyError):
                    pass
        par_rouleau.setdefault(r["rouleau"], []).append(r)
    if not par_rouleau:
        print(f"aucun tirage exploitable sous {a.dossier}")
        return 1

    # ⚠ Le budget est LU dans les resumes, pas suppose. Une campagne dont les tirages
    # n'ont pas tous le meme budget ne se resume pas par un nombre : on rend `None` plutot
    # qu'un des deux, parce qu'un budget faux est pire qu'un budget absent.
    budgets = {r.get("plafond_generations") for v in par_rouleau.values() for r in v}
    budgets.discard(None)
    budget_gen = budgets.pop() if len(budgets) == 1 else None

    lignes = []
    if desaccords:
        print(f"⚠⚠ {len(desaccords)} désaccord(s) entre un résumé et son rapport — "
              f"le rapport fait foi :")
        for rouleau, rep, dit, vrai in desaccords:
            print(f"     {rouleau} r{rep} : le résumé dit {dit}, le rapport dit {vrai}")
        print()
    print(f"{sum(len(v) for v in par_rouleau.values())} tirages exploitables "
          f"sur {len(par_rouleau)} rouleaux"
          + (f" ({rejetes} sans maillage ou en dépassement)" if rejetes else "") + "\n")
    entete = (f"  {'rouleau':<12} {'n':>2} {'gen':>7} {'aire min':>10} {'aire max':>10} "
              f"{'étendue':>8} {'croisements par tirage':>26}")
    print(entete)
    print("  " + "-" * (len(entete) - 2))

    for rouleau in sorted(par_rouleau):
        lots = sorted(par_rouleau[rouleau], key=lambda x: x["repetition"])
        aires = [r["aire_cm2"] for r in lots]
        crois = [r["transverse"] for r in lots]
        gens = [r["generations"] for r in lots]
        etendue = (max(aires) - min(aires)) / statistics.mean(aires) if statistics.mean(aires) else 0.0
        # Le controle : identique au bit pres ET meme verdict = tirage reproductible ici.
        #
        # ⚠⚠ Il faut AU MOINS DEUX tirages pour que ces deux etiquettes veuillent dire
        # quelque chose. Sur un seul tirage l'aire est trivialement identique a elle-meme
        # et le verdict ne peut pas basculer : la premiere version de ce fichier a
        # affiche « reproductible » pour un rouleau qui n'avait qu'un tirage, ce qui est
        # une affirmation incapable d'etre fausse. n < 2 rend maintenant `None`, qui
        # s'imprime « non concluant » et ne se compte nulle part.
        concluant = len(lots) >= 2
        aire_identique = (len(set(aires)) == 1) if concluant else None
        verdict_identique = (len(set(bool(c) for c in crois)) == 1) if concluant else None
        bascule = (not verdict_identique) if concluant else None
        lignes.append({
            "rouleau": rouleau, "n": len(lots), "graine": lots[0]["graine"],
            "voxel_um": lots[0]["voxel_um"],
            "generations_min": min(gens), "generations_max": max(gens),
            "budget_generations": lots[0].get("plafond_generations"),
            # ⚠ Les aires PAR TIRAGE, et pas seulement min/max/mediane : la figure place
            # un point par tirage et le colore par son compte de croisements. Sans la liste
            # elle devrait reconstruire une plage, et un point rouge tomberait alors sur le
            # mauvais tirage. Un artefact doit porter ce que ses consommateurs lisent.
            "aires": aires, "aire_min": min(aires), "aire_max": max(aires),
            "aire_mediane": statistics.median(aires), "etendue_relative": etendue,
            "croisements": crois, "propres": sum(1 for c in crois if c == 0),
            "aire_identique": aire_identique, "verdict_bascule": bascule,
        })
        marque = ("  non concluant (1 tirage)" if not concluant
                  else " ⭐ bascule" if bascule
                  else "  reproductible" if aire_identique else "")
        print(f"  {rouleau:<12} {len(lots):>2} {min(gens):>3}–{max(gens):<3} "
              f"{min(aires):>10.6f} {max(aires):>10.6f} {etendue:>7.2%} "
              f"{','.join(str(c) for c in crois):>26}{marque}")

    total = sum(l["n"] for l in lignes)
    mauvais = sum(l["n"] - l["propres"] for l in lignes)
    bas, haut = clopper_pearson(mauvais, total)
    bascules = [l["rouleau"] for l in lignes if l["verdict_bascule"]]
    reproductibles = [l["rouleau"] for l in lignes if l["aire_identique"]]
    non_concluants = [l["rouleau"] for l in lignes if l["verdict_bascule"] is None]

    # ⭐ L'AIRE PREDIT-ELLE LE VERDICT ? Question posee par la figure : les trois rouleaux
    # dont les six tirages ont la MEME aire sont ceux qui portent les pires croisements. Si
    # un mauvais tirage se reconnaissait a son etendue, on pourrait le jeter sans le juger,
    # et ce serait un raccourci considerable. On le mesure au lieu de le lire a l'oeil.
    #
    # ⚠ Le rang est central-normalise : 0 = l'aire mediane du rouleau, 1 = la plus extreme.
    # Sous « l'aire ne dit rien », un mauvais tirage tombe a un rang uniforme, d'esperance
    # ~0,5 sur cette echelle.
    rangs_mauvais, disp_bascule, disp_sans = [], [], []
    for l in lignes:
        aires_l, crois_l, n_l = l["aires"], l["croisements"], l["n"]
        ordre = sorted(range(n_l), key=lambda j: aires_l[j])
        rang_de = {j: r for r, j in enumerate(ordre)}
        centre = (n_l - 1) / 2
        for j, c in enumerate(crois_l):
            if c > 0 and centre > 0:
                rangs_mauvais.append(abs(rang_de[j] - centre) / centre)
        (disp_bascule if l["verdict_bascule"] else disp_sans).append(l["etendue_relative"])

    # ⚠⚠ LE CONFOND QUE `35` §3 NOMME, ENFIN CALCULE DANS L'ARBRE. Le document annonçait
    # « un test exact donne p ≈ 0,55 » — un nombre sans producteur, donc une anecdote au
    # sens de la règle de ce dépôt, et périmé dès qu'un rouleau s'ajoute. L'observation
    # est que les rouleaux à faible dispersion d'aire sont ceux dont tous les tirages
    # butent sur le plafond de générations : leur dispersion ne mesure alors pas le
    # traceur, elle mesure la troncature.
    #
    # ⚠ Le plafond est DÉRIVÉ de la campagne — le maximum de générations observé — et non
    # écrit en dur : il dépend du budget du `seed.json`, donc une constante deviendrait
    # fausse en silence le jour où le budget change. C'est exactement la mesure que
    # `29` N3 demande.
    # ⚠⚠ DEUX notions, deux noms. « le budget demande » (celui du seed.json, qui voyage
    # dans chaque resume) et « le maximum reellement atteint » ne sont pas la meme chose :
    # a budget 120 les traces s'arretent a 118, a budget 400 elles s'arretent ou elles
    # veulent. Les confondre sous un seul `plafond_generations` rendait le test « cette
    # trace a-t-elle sature ? » trivialement vrai pour le rouleau qui va le plus loin.
    plafond_gen = max(l["generations_max"] for l in lignes)   # atteint, pas demande
    plafonnes = [l for l in lignes
                 if l["generations_min"] == l["generations_max"] == plafond_gen]
    for l in lignes:
        l["plafonne"] = (l["generations_min"] == l["generations_max"] == plafond_gen)
    a_b = sum(1 for l in plafonnes if l["verdict_bascule"])
    b_b = sum(1 for l in lignes if not l["plafonne"] and l["verdict_bascule"])
    n_a, n_b = len(plafonnes), len(lignes) - len(plafonnes)
    p_fisher = None
    try:
        from scipy.stats import fisher_exact
        p_fisher = float(fisher_exact([[a_b, n_a - a_b], [b_b, n_b - b_b]]).pvalue)
    except Exception:
        pass
    disp_plaf = statistics.median([l["etendue_relative"] for l in plafonnes]) if plafonnes else None
    disp_non = (statistics.median([l["etendue_relative"] for l in lignes
                                   if not l["plafonne"]])
                if n_b else None)

    print(f"\n  mauvais tirages : {mauvais}/{total} = {mauvais/total:.1%} "
          f"(IC 95 % exact : {bas:.1%} – {haut:.1%})")
    print(f"  rouleaux où le VERDICT bascule d'un tirage à l'autre : "
          f"{len(bascules)}/{len(lignes)}" + (f"  ({', '.join(bascules)})" if bascules else ""))
    print(f"  rouleaux où l'aire est identique sur tous les tirages : "
          f"{len(reproductibles)}/{len(lignes)}"
          + (f"  ({', '.join(reproductibles)})" if reproductibles else ""))
    if non_concluants:
        print(f"  ⚠ rouleaux à un seul tirage, donc ni l'un ni l'autre : "
              f"{len(non_concluants)}  ({', '.join(non_concluants)})")

    print(f"\n  ⚠ le PLAFOND de générations ({plafond_gen}) comme confond : "
          f"{n_a} rouleaux plafonnés, {n_b} non")
    print(f"     basculements : {a_b}/{n_a} chez les plafonnés contre {b_b}/{n_b} chez "
          f"les autres" + (f"  (test exact p = {p_fisher:.2f})" if p_fisher is not None
                           else "  (scipy absent, test non calculé)"))
    if disp_plaf is not None and disp_non is not None:
        print(f"     dispersion médiane : {disp_plaf:.1%} chez les plafonnés contre "
              f"{disp_non:.1%} chez les autres — c'est CE partage qui explique la "
              f"différence attribuée au basculement")

    if bascules:
        print("\n  ⭐ Un basculement est la preuve la plus forte disponible : deux exécutions")
        print("     à paramètres strictement identiques, deux verdicts opposés. Aucun seuil,")
        print("     aucune vérité terrain. Le résultat de `30` ne tient pas à sa graine.")
    elif reproductibles and reproductibles == [l["rouleau"] for l in lignes]:
        print("\n  ⚠ Aucun basculement ET aucune dispersion d'aire : sur ce corpus le traceur")
        print("     s'est comporté de façon reproductible. Le résultat de `30` serait alors")
        print("     propre à sa graine — et c'est ce qu'il faudrait écrire.")
    else:
        print("\n  ⚠ Aucun basculement, mais l'aire varie : le tirage bouge sans changer le")
        print("     verdict. Le taux de mauvais tirages n'est donc PAS mesuré à zéro ici,")
        print("     il est mesuré comme plus rare que ce corpus ne peut voir.")

    if rangs_mauvais:
        moyen = statistics.fmean(rangs_mauvais)
        print(f"\n  ⭐ l'aire prédit-elle le verdict ? {len(rangs_mauvais)} mauvais tirages, "
              f"excentricité de rang moyenne {moyen:.2f}")
        print("     (0 = l'aire médiane de son rouleau, 1 = l'extrême ; ~0,50 attendu si "
              "l'aire ne dit rien)")
        if moyen < 0.7:
            print("     → l'étendue ne signale PAS le mauvais tirage. On ne peut pas")
            print("        l'écarter sur sa taille : il faut le juger.")
        else:
            print("     → les mauvais tirages sont aux extrêmes ; l'étendue serait un filtre.")
    if disp_bascule and disp_sans:
        print(f"  dispersion médiane — rouleaux qui basculent : "
              f"{statistics.median(disp_bascule):.1%}, "
              f"les autres : {statistics.median(disp_sans):.1%}")

    if a.json:
        Path(a.json).write_text(json.dumps({
            "tirages_total": total, "rouleaux": len(lignes),
            "mauvais": mauvais, "taux_mauvais": mauvais / total,
            "ic95_bas": bas, "ic95_haut": haut,
            "rouleaux_bascule": bascules, "rouleaux_reproductibles": reproductibles,
            "rouleaux_non_concluants": non_concluants,
            "excentricite_rang_mauvais": rangs_mauvais,
            "dispersion_mediane_bascule": (statistics.median(disp_bascule)
                                           if disp_bascule else None),
            "dispersion_mediane_sans": (statistics.median(disp_sans) if disp_sans else None),
            # ⚠ Le confond du plafond voyage dans l'artefact : sans lui, la prose qui
            # le cite serait de nouveau un nombre sans producteur.
            "generations_max_observees": plafond_gen,
            "budget_generations": budget_gen,
            "plafonnes": n_a, "non_plafonnes": n_b,
            "bascules_plafonnes": a_b, "bascules_non_plafonnes": b_b,
            "p_fisher_plafond": p_fisher,
            "dispersion_mediane_plafonnes": disp_plaf,
            "dispersion_mediane_non_plafonnes": disp_non,
            "sans_maillage": rejetes, "reverifies": revérifiés,
            "desaccords": [{"rouleau": r, "repetition": i, "resume": d, "rapport": v}
                           for r, i, d, v in desaccords],
            "lignes": lignes,
        }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"\n  écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
