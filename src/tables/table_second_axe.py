#!/usr/bin/env python3
"""Les deux axes s'accordent-ils ? -- la parade a la malediction du vainqueur, mesuree.

⚠⚠ Pourquoi ce fichier existe. `35` mesure que le traceur est un tirage, et `31` §4 en tire
une methode : tirer N fois et selectionner. Son piege est nomme depuis `30` §4 -- prendre le
minimum de N tirages avec un juge bruite fait remonter la CHANCE autant que la qualite. Le
protocole honnete est de **selectionner sur un axe et valider sur l'autre**, et il n'a
jamais ete teste.

  axe 1 : `vc_tifxyz_selfcross` -- la surface se traverse-t-elle elle-meme ? Geometrie pure.
  axe 2 : la profondeur -- ou est la matiere par rapport a la trace, lue dans le VOLUME.

Les deux ne partagent aucune information : le premier ne lit jamais le volume, le second ne
regarde jamais la surface contre elle-meme.

⭐ **La comparaison est INTRA-rouleau**, et c'est ce qui la rend concluante : sur un rouleau
qui bascule on tient le mauvais tirage ET des propres, meme graine, memes parametres. La
question est alors exactement : *le tirage que l'axe 1 condamne est-il aussi le pire selon
l'axe 2 ?*

⚠⚠ **LA CENSURE EST IMPRIMEE AVANT LE RESULTAT.** `ecart_trace_um_median` ne peut pas
depasser `(couches // 2) × voxel_um` : au-dela, le pic est hors de la pile rendue et la
mesure bute sur son plafond. Un axe dont la moitie des valeurs sont au plafond ne peut pas
departager, et un accord mesure sur des ex-aequo artificiels ne veut rien dire. Le taux de
censure decide donc de la lisibilite de tout ce qui suit, et il est dit en premier.

Usage :
    uv run python src/tables/table_second_axe.py [data/second_axe] [--json docs/second_axe.json]
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]


def charger(dossier: Path, table: Path) -> tuple[list[dict], list[str]]:
    """Lire les profils et les rattacher a leur verdict d'axe 1."""
    axe1 = {}
    if table.is_file():
        for l in json.loads(table.read_text())["lignes"]:
            for i, c in enumerate(l["croisements"], 1):
                axe1[(l["rouleau"], f"r{i}")] = {
                    "transverse": c, "aire": l["aires"][i - 1],
                    "bascule": l["verdict_bascule"]}

    lignes, orphelins = [], []
    for f in sorted(dossier.glob("*.json")):
        d = json.loads(f.read_text())
        # ⚠ Le nom du fichier porte l'identite. La premiere version de la campagne annotait
        # le JSON et levait un TypeError (le profil est une LISTE) : la mesure etait ecrite,
        # l'etiquette perdue. On lit donc le nom, qui n'a jamais ete perdu.
        tige = f.stem
        if "_" not in tige:
            orphelins.append(tige)
            continue
        rouleau, rep = tige.rsplit("_", 1)
        profils = d.get("profils") if isinstance(d, dict) else d
        if not profils:
            orphelins.append(tige)
            continue
        p = profils[0]
        cle = (rouleau, rep)
        if cle not in axe1:
            orphelins.append(tige)
            continue
        couches = d.get("couches") if isinstance(d, dict) else None
        couches = couches or (len(p.get("layers") or []) or 21)
        plafond = (couches // 2) * p["voxel_um"]
        lignes.append({
            "rouleau": rouleau, "repetition": rep,
            "transverse": axe1[cle]["transverse"],
            "bascule": axe1[cle]["bascule"],
            "ecart_um": p["ecart_trace_um_median"],
            "au_bord": p["au_bord_intensite"],
            "part_plates": p["part_plates"],
            "plafond_um": plafond,
            "censure": p["ecart_trace_um_median"] >= plafond - 1e-6,
        })
    return lignes, orphelins


def verifier() -> int:
    """Temoin hors ligne : l'accord, le desaccord, l'ex-aequo, et la censure.

    ⭐ Le controle qui compte est le troisieme. Un ex-aequo n'est PAS un accord : si le
    mauvais tirage et le meilleur propre butent tous deux sur le plafond, ils sont egaux
    par CENSURE et non par mesure. Les compter comme un accord ferait dire a cet
    instrument que les deux axes s'accordent alors qu'il n'a rien pu departager -- ce qui
    est exactement l'erreur que ce fichier existe pour ne pas commettre.
    """
    import tempfile

    echecs, controles = 0, 0

    def verifie(nom: str, cond: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    # 4 rouleaux : accord franc, desaccord franc, ex-aequo par censure, sans mauvais tirage.
    cas = {
        "ACCORD":   [(1, 80.0, 0.90), (0, 40.0, 0.30), (0, 50.0, 0.40)],
        "DESACCORD": [(1, 40.0, 0.30), (0, 80.0, 0.90), (0, 50.0, 0.40)],
        "EXAEQUO":  [(1, 93.62, 0.50), (0, 93.62, 0.50), (0, 20.0, 0.20)],
        "SANSMAUVAIS": [(0, 30.0, 0.30), (0, 40.0, 0.40)],
    }
    with tempfile.TemporaryDirectory() as tmp:
        # ⚠ La table vit HORS du repertoire de profils : `charger` lit tout `*.json` du
        # dossier, donc un fichier etranger pose la serait signale comme orphelin. Le
        # temoin l'a attrape a sa premiere execution -- comportement correct de l'outil,
        # fixture fautive.
        racine = Path(tmp) / "profils"
        racine.mkdir()
        table = Path(tmp) / "table.json"
        table.write_text(json.dumps({"lignes": [
            {"rouleau": r, "n": len(v),
             "croisements": [c for c, _, _ in v],
             "aires": [1.0] * len(v),
             "verdict_bascule": any(c for c, _, _ in v) and not all(c for c, _, _ in v)}
            for r, v in cas.items()]}))
        for r, v in cas.items():
            for i, (_, ecart, bord) in enumerate(v, 1):
                (racine / f"{r}_r{i}.json").write_text(json.dumps({
                    "rouleau": r, "repetition": f"r{i}", "couches": 21,
                    "profils": [{"ecart_trace_um_median": ecart,
                                 "au_bord_intensite": bord, "part_plates": 0.5,
                                 "voxel_um": 9.362, "layers": list(range(21))}]}))
        lignes, orphelins = charger(racine, table)

    verifie("tous les tirages sont rattachés", len(lignes) == 11, str(len(lignes)))
    verifie("aucun orphelin", not orphelins, str(orphelins))
    par = {(l["rouleau"], l["repetition"]): l for l in lignes}
    verifie("le plafond est calculé depuis le nombre de couches",
            abs(par[("ACCORD", "r1")]["plafond_um"] - 10 * 9.362) < 1e-6,
            str(par[("ACCORD", "r1")]["plafond_um"]))
    verifie("une valeur au plafond est marquée censurée", par[("EXAEQUO", "r1")]["censure"])
    verifie("une valeur sous le plafond ne l'est pas", not par[("ACCORD", "r1")]["censure"])

    # Le coeur : accord / desaccord / ex-aequo, sur la statistique censurable.
    def juge(rouleau: str, stat: str) -> tuple[bool, bool]:
        lots = [l for l in lignes if l["rouleau"] == rouleau]
        m = [l for l in lots if l["transverse"]]
        p_ = [l for l in lots if not l["transverse"]]
        if not m or not p_:
            return (False, False)
        pm, pp = max(l[stat] for l in m), max(l[stat] for l in p_)
        return (pm > pp, pm == pp)

    verifie("accord franc reconnu", juge("ACCORD", "ecart_um") == (True, False))
    verifie("désaccord franc reconnu", juge("DESACCORD", "ecart_um") == (False, False))
    verifie("ex-aequo N'EST PAS un accord", juge("EXAEQUO", "ecart_um") == (False, True))
    verifie("un rouleau sans mauvais tirage n'est pas testable",
            juge("SANSMAUVAIS", "ecart_um") == (False, False))
    verifie("l'autre statistique est jugée séparément",
            juge("ACCORD", "au_bord") == (True, False))

    if echecs:
        print(f"\nECHEC ({echecs} failures, {controles} checks)")
        return 1
    print(f"ALL PASS ({echecs} failures, {controles} checks)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dossier", nargs="?", default=str(RACINE / "data/second_axe"))
    ap.add_argument("--table", type=Path, default=RACINE / "docs/table_tirages.json")
    ap.add_argument("--json")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()

    if a.verifier:
        return verifier()

    lignes, orphelins = charger(Path(a.dossier), a.table)
    if not lignes:
        print(f"aucun profil exploitable sous {a.dossier}")
        return 1

    censures = sum(1 for l in lignes if l["censure"])
    print(f"{len(lignes)} tirages avec les DEUX axes"
          + (f"  ({len(orphelins)} profil(s) sans verdict d'axe 1)" if orphelins else "") + "\n")
    print(f"  ⚠⚠ CENSURE : {censures}/{len(lignes)} écarts sont au plafond de "
          f"{lignes[0]['plafond_um']:.1f} µm ({lignes[0]['plafond_um'] / lignes[0].get('voxel', 9.362):.0f} "
          f"couches de part et d'autre de la trace).")
    if censures > len(lignes) / 2:
        print("     La moitié des valeurs bute sur le plafond : l'écart ne peut PAS")
        print("     départager, et tout accord mesuré dessus porterait sur des ex-aequo")
        print("     artificiels. Lire `au_bord`, qui n'est pas censuré — ou rendre plus")
        print("     de couches, ce qui est la seule vraie correction.\n")
    else:
        print()

    entete = (f"  {'rouleau':<12} {'tir.':>5} {'axe 1':>10} {'écart µm':>9} "
              f"{'au bord':>8} {'plates':>7}")
    print(entete)
    print("  " + "-" * (len(entete) - 2))
    for l in sorted(lignes, key=lambda x: (x["rouleau"], x["repetition"])):
        marque = " ⚠ plafond" if l["censure"] else ""
        r = "MAUVAIS" if l["transverse"] else "propre"
        print(f"  {l['rouleau']:<12} {l['repetition']:>5} {r:>10} "
              f"{l['ecart_um']:>9.2f} {l['au_bord']:>8.3f} {l['part_plates']:>7.3f}{marque}")

    # ⭐ Le test : dans chaque rouleau qui bascule, le tirage condamne par l'axe 1 est-il
    # aussi le pire selon l'axe 2 ? On le pose sur les deux statistiques d'axe 2, parce que
    # l'une est censuree et l'autre non.
    accords = {"ecart_um": 0, "au_bord": 0}
    testables = 0
    detail = []
    par_rouleau: dict[str, list[dict]] = {}
    for l in lignes:
        par_rouleau.setdefault(l["rouleau"], []).append(l)
    for rouleau, lots in sorted(par_rouleau.items()):
        mauvais = [l for l in lots if l["transverse"]]
        propres = [l for l in lots if not l["transverse"]]
        if not mauvais or not propres:
            continue
        testables += 1
        d = {"rouleau": rouleau}
        for stat in ("ecart_um", "au_bord"):
            pire_mauvais = max(l[stat] for l in mauvais)
            pire_propre = max(l[stat] for l in propres)
            gagne = pire_mauvais > pire_propre
            egal = pire_mauvais == pire_propre
            accords[stat] += 1 if gagne else 0
            d[stat] = {"mauvais": pire_mauvais, "propre_max": pire_propre,
                       "accord": gagne, "ex_aequo": egal}
        detail.append(d)

    print(f"\n  ⭐ le tirage condamné par l'axe 1 est-il le pire selon l'axe 2 ?"
          f"  ({testables} rouleaux testables)")
    for stat, nom in (("ecart_um", "écart à la trace"), ("au_bord", "part au bord")):
        exa = sum(1 for d in detail if d[stat]["ex_aequo"])
        print(f"     {nom:<18} : {accords[stat]}/{testables} d'accord"
              + (f"  ⚠ dont {exa} ex-aequo" if exa else ""))
    if testables:
        print("\n  ⚠ Sur quatre rouleaux au plus, aucun de ces comptes n'est significatif.")
        print("     Ce qui se lit est la DIRECTION, et seulement si elle est franche :")
        print("     4/4 ou 0/4 disent quelque chose, 2/4 ne dit rien.")

    if a.json:
        Path(a.json).write_text(json.dumps({
            "tirages": len(lignes), "censures": censures,
            "plafond_um": lignes[0]["plafond_um"],
            "rouleaux_testables": testables, "accords": accords,
            "detail": detail, "lignes": lignes, "orphelins": orphelins,
        }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"\n  écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
