#!/usr/bin/env python3
"""Une graine MIEUX ÉTAYÉE trace-t-elle mieux ? — les huit candidats, et la réponse est non.

⚠⚠ POURQUOI CE FICHIER EXISTE. `src/outils/tracer_tous_candidats.sh` pose une question précise
et son en-tête l'argumente bien : `trouver_graine` classe sur la **planarité seule**, et sur
`PHercParis4` ce classement met devant un point à planarité 1,0000 sur **neuf** voisins, là où
les suivants ont **vingt-sept** voisins — un bloc 3×3×3 plein — pour des planarités de 0,987 à
0,997. *« Une planarité de 1,0000 sur neuf voisins n'est pas MEILLEURE que 0,987 sur
vingt-sept : elle est moins ÉTAYÉE. »* Trois dix-millièmes séparent les planarités là où
l'occupation varie d'un **facteur vingt**.

La campagne a tourné, les huit candidats sont tracés, **et son résultat n'a jamais été publié**.
Ce fichier le lit et le rend.

  ⭐⭐ **Réponse : zéro sur huit.** Aucun candidat ne converge, et l'étai n'y change rien — les
    trois mieux soutenus (27 voisins) échouent exactement comme les deux moins soutenus (9).

⭐⭐⭐ **Et l'échec a une signature plus dure que « α ≈ 1 »** : pour **sept** candidats sur huit,
l'écart rapporté **égale exactement la demi-fenêtre**, au voxel près — 48,0 µm à 41 couches
(20 × 2,4) et 192,0 µm à 161 (80 × 2,4). Un écart qui vaut le bord de la fenêtre dans les deux
fenêtres n'est pas une mesure de distance à une feuille : c'est **l'absence de tout pic**, la
panne que `49` §2 nomme. La série d'écarts est alors le rapport des fenêtres, et α vaut 1 **par
identité**, quoi qu'il y ait dans le volume.

⚠ Ce fichier **ne corrige pas** le classement de `trouver_graine` : inventer un score composite
serait choisir la réponse. Il joint ce qui a été mesuré et laisse la conclusion là où elle est.

⚠⚠ La jointure se fait **par indice** (`c0` ↔ `candidats[0]`), et elle est **gardée** : un
décalage attribuerait le verdict d'un candidat aux propriétés d'un autre, ce qui est
exactement la façon dont une table devient fausse sans qu'aucune ligne n'ait l'air fausse.

Usage :
    uv run python src/nappe/la_graine_mieux_etayee.py --verifier
    uv run python src/nappe/la_graine_mieux_etayee.py \\
        --json docs/mesures/la_graine_mieux_etayee.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]

GRAINES = RACINE / "data" / "prediction_paris4"
TRACES = RACINE / "data" / "paris4_candidats"
VERDICTS = RACINE / "docs" / "mesures"
PREDICTIONS = ("m7", "ps256")

CAS = re.compile(r"^candidat_paris4_(?P<pred>[a-z0-9]+)_c(?P<indice>\d+)\.json$")


def candidats(prediction: str, racine: Path = GRAINES) -> list[dict]:
    """Les points que `trouver_graine` a proposés, dans SON ordre de classement.

    ⚠ L'ordre est celui du fichier et il n'est pas retrié : c'est ce classement-là qui est
    en cause, donc le réordonner effacerait le sujet de la mesure.
    """
    f = racine / f"graine_{prediction}.json"
    if not f.is_file():
        return []
    return json.loads(f.read_text())["candidats"]


def verdict(prediction: str, indice: int, racine: Path = VERDICTS) -> dict | None:
    """Le verdict de convergence d'un candidat tracé, ou `None` s'il n'a pas été tracé."""
    f = racine / f"candidat_paris4_{prediction}_c{indice}.json"
    if not f.is_file():
        return None
    series = json.loads(f.read_text()).get("series") or []
    return series[0] if series else None


def profil(prediction: str, indice: int, couches: int, racine: Path = TRACES) -> dict | None:
    """Le profil de profondeur d'un candidat à une fenêtre donnée."""
    f = racine / f"{prediction}_c{indice}" / f"profil_{couches}c.json"
    if not f.is_file():
        return None
    d = json.loads(f.read_text())
    return d[0] if isinstance(d, list) else d


def ecart_est_le_bord(ecart_um: float, couches: int, voxel_um: float,
                      tolerance_um: float = 1e-6) -> bool:
    """
    @brief L'écart rapporté vaut-il EXACTEMENT la demi-fenêtre ?

    ⚠⚠ C'est la signature de « aucun pic » : quand le profil est plat, l'argmax tombe au bord
    et la distance rapportée est la moitié de la fenêtre. Dans deux fenêtres emboîtées, le
    rapport des écarts vaut alors celui des fenêtres, donc α ≈ 1 **par identité** — un verdict
    qui parle du volume alors qu'il ne parle que de l'instrument.

    ⚠ La comparaison est EXACTE et non approchée : un écart « proche » du bord peut être une
    vraie feuille qui s'y trouve, un écart égal au bord au voxel près ne peut pas l'être.
    """
    return abs(ecart_um - (couches // 2) * voxel_um) <= tolerance_um


def joindre(predictions=PREDICTIONS, graines: Path = GRAINES, mesures: Path = VERDICTS,
            traces: Path = TRACES, fenetres=(41, 161)) -> list[dict]:
    """Les candidats et leurs verdicts, appariés par indice.

    ⚠⚠ REFUSE si un verdict existe sans candidat correspondant : la jointure est positionnelle,
    donc un décalage attribuerait silencieusement les propriétés du mauvais point.
    """
    out = []
    for pred in predictions:
        liste = candidats(pred, graines)
        traces_vues = sorted(int(m.group("indice")) for f in mesures.glob("candidat_paris4_*.json")
                             if (m := CAS.match(f.name)) and m.group("pred") == pred)
        if traces_vues and max(traces_vues) >= len(liste):
            raise SystemExit(
                f"{pred} : verdict c{max(traces_vues)} sans candidat correspondant "
                f"({len(liste)} candidats) — la jointure par indice serait fausse")
        for i in traces_vues:
            c, v = liste[i], verdict(pred, i, mesures)
            if v is None:
                continue
            ligne = {"prediction": pred, "indice": i,
                     "planarite": c["planarite"], "occupation": c["occupation"],
                     "voisins": c["voisins"], "xyz": [c["x"], c["y"], c["z"]],
                     "verdict": v.get("verdict"), "amplitude": v.get("amplitude"),
                     "serie": v.get("serie")}
            bords = []
            for n in fenetres:
                p = profil(pred, i, n, traces)
                if p is None:
                    continue
                ligne.setdefault("voxel_um", p.get("voxel_um"))
                ligne[f"fenetres_{n}"] = p.get("windows")
                ligne[f"part_plates_{n}"] = p.get("part_plates")
                ligne[f"au_bord_{n}"] = p.get("au_bord_intensite")
                ligne[f"ecart_um_{n}"] = p.get("ecart_trace_um_median")
                bords.append(ecart_est_le_bord(p["ecart_trace_um_median"], n, p["voxel_um"]))
            ligne["ecart_est_le_bord"] = bool(bords) and all(bords)
            out.append(ligne)
    return out


def resume(table: list[dict]) -> dict:
    """Ce que la table dit, en grandeurs qu'on peut publier."""
    if not table:
        return {"candidats": 0}
    convergents = [l for l in table if l["verdict"] == "converge"]
    return {"candidats": len(table),
            "convergents": len(convergents),
            "au_bord_par_identite": sum(1 for l in table if l["ecart_est_le_bord"]),
            "voisins_min": min(l["voisins"] for l in table),
            "voisins_max": max(l["voisins"] for l in table),
            "occupation_min": min(l["occupation"] for l in table),
            "occupation_max": max(l["occupation"] for l in table),
            "planarite_min": min(l["planarite"] for l in table),
            "planarite_max": max(l["planarite"] for l in table),
            "verdicts": sorted({l["verdict"] for l in table})}


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # --- l'identité « l'écart vaut le bord » ---
    v("un écart égal à la demi-fenêtre est reconnu", ecart_est_le_bord(192.0, 161, 2.4))
    v("... et à l'autre fenêtre aussi", ecart_est_le_bord(48.0, 41, 2.4))
    # ⚠ La comparaison est EXACTE : un écart d'un voxel en deçà est une vraie mesure, pas le
    # bord. Une tolérance large ferait passer des feuilles réelles pour des non-mesures.
    v("... et un écart d'un voxel en deçà ne l'est PAS",
      not ecart_est_le_bord(189.6, 161, 2.4), "189,6 = 79 couches")
    v("... ni un écart de zéro", not ecart_est_le_bord(0.0, 161, 2.4))

    # --- la jointure, gardée ---
    import shutil
    import tempfile
    d = Path(tempfile.mkdtemp())
    (d / "g").mkdir()
    (d / "m").mkdir()
    (d / "t").mkdir()

    def poser(n_candidats: int, n_verdicts: int) -> None:
        for x in (d / "g", d / "m"):
            for f in x.glob("*.json"):
                f.unlink()
        (d / "g" / "graine_p.json").write_text(json.dumps({"candidats": [
            {"planarite": 1.0 - 0.001 * k, "occupation": 0.1 * (k + 1), "voisins": 9 + k,
             "x": k, "y": k, "z": k} for k in range(n_candidats)]}), encoding="utf-8")
        for k in range(n_verdicts):
            (d / "m" / f"candidat_paris4_p_c{k}.json").write_text(
                json.dumps({"series": [{"verdict": "suit la fenêtre", "amplitude": 0.04,
                                        "serie": [[41, 48.0], [161, 192.0]]}]}),
                encoding="utf-8")

    poser(3, 3)
    t = joindre(("p",), d / "g", d / "m", d / "t")
    v("la jointure apparie chaque verdict à SON candidat",
      [l["voisins"] for l in t] == [9, 10, 11], str([l["voisins"] for l in t]))
    # ⚠⚠ LE CONTRÔLE QUI COMPTE : un verdict sans candidat ferait glisser toute la table d'un
    # cran, et chaque ligne resterait plausible. Le refus est ce qui l'empêche.
    poser(2, 3)
    v("un verdict sans candidat est REFUSÉ, pas ignoré",
      _leve(lambda: joindre(("p",), d / "g", d / "m", d / "t")))
    # ⚠ L'inverse est légitime : un candidat qu'on n'a pas tracé n'est pas une erreur.
    poser(5, 2)
    v("... alors qu'un candidat non tracé est simplement absent de la table",
      len(joindre(("p",), d / "g", d / "m", d / "t")) == 2)

    r = resume(joindre(("p",), d / "g", d / "m", d / "t"))
    v("le résumé compte les convergents", r["convergents"] == 0, str(r))
    v("... et couvre l'étendue de l'étai", r["voisins_min"] == 9 and r["voisins_max"] == 10)
    shutil.rmtree(d, ignore_errors=True)

    # --- contre les VRAIES mesures ---
    table = joindre()
    if not table:
        print("  ⚠ mesures absentes : la partie « vrai arbre » n'a pas tourné")
    else:
        r = resume(table)
        v(f"les huit candidats sont joints ({r['candidats']})", r["candidats"] == 8, str(r))
        # ⭐⭐ LA CONCLUSION, assertée dans le sens où elle a été mesurée. Elle tombe le jour où
        # un candidat converge — et ce serait une excellente nouvelle.
        v("aucun ne converge", r["convergents"] == 0)
        # ⚠⚠ Et le contrôle qui empêche « on n'a essayé que des graines mal étayées » : l'étai
        # va de neuf voisins à vingt-sept, soit du point le moins soutenu au bloc 3×3×3 plein.
        v(f"... et l'étendue de l'étai est couverte ({r['voisins_min']}–{r['voisins_max']} "
          f"voisins, occupation {r['occupation_min']:.4f}–{r['occupation_max']:.2f})",
          r["voisins_min"] <= 9 and r["voisins_max"] >= 27
          and r["occupation_max"] / max(r["occupation_min"], 1e-9) > 10)
        v(f"... et sept écarts sur huit VALENT le bord de la fenêtre "
          f"({r['au_bord_par_identite']}/8)", r["au_bord_par_identite"] == 7)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def _leve(f) -> bool:
    try:
        f()
    except SystemExit:
        return True
    except Exception:  # noqa: BLE001
        return False
    return False


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    table = joindre()
    if not table:
        raise SystemExit("aucun candidat tracé : data/prediction_paris4 ou docs/mesures manquent")
    r = resume(table)
    print(f"{'candidat':12s} {'planarite':>10s} {'occup.':>7s} {'vois.':>6s} "
          f"{'verdict':>18s} {'ecart 41':>9s} {'ecart 161':>10s} {'= bord ?':>9s}")
    print("-" * 92)
    for l in table:
        print(f"{l['prediction']}_c{l['indice']:<8d} {l['planarite']:10.4f} "
              f"{l['occupation']:7.4f} {l['voisins']:6d} {l['verdict']:>18s} "
              f"{l.get('ecart_um_41', float('nan')):9.1f} "
              f"{l.get('ecart_um_161', float('nan')):10.1f} "
              f"{'oui' if l['ecart_est_le_bord'] else 'non':>9s}")
    print(f"\n{r['convergents']} convergent(s) sur {r['candidats']} — "
          f"étai de {r['voisins_min']} à {r['voisins_max']} voisins, "
          f"occupation {r['occupation_min']:.4f} à {r['occupation_max']:.2f}")
    print(f"{r['au_bord_par_identite']}/{r['candidats']} écarts valent EXACTEMENT le bord "
          "de la fenêtre — donc aucun pic, et α = 1 par identité")
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps({"resume": r, "candidats": table}, indent=2,
                                     ensure_ascii=False), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
