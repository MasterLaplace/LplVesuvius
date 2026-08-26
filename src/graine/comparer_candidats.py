#!/usr/bin/env python3
"""Quelle propriété d'une graine prédit qu'elle donnera une trace qui converge ?

⚠⚠ **La question née d'une lecture, pas d'une hypothèse.** `trouver_graine` classe les
candidats par **planarité seule**, et sur `PHercParis4` ce classement met devant un point à
occupation 0,0215 (le plancher de la bande vaut 0,02) et un autre à planarité 1,0000 sur
**neuf** voisins — quand d'autres candidats ont 27 voisins et des occupations médianes. Une
planarité parfaite sur un bloc minuscule n'est pas meilleure : elle est moins **étayée**.

⚠⚠ **Ce fichier refuse de conclure sur une corrélation, et il faut le dire d'emblée.** Avec
huit candidats — moins ceux qui ne rendent pas d'α — la corrélation détectable à 80 % de
puissance dépasse **0,84**. Autrement dit : rien de moins qu'une relation quasi parfaite ne
serait visible, et un ρ non significatif ici ne réfute rien. Un zéro se rapporte avec sa
puissance, ou il ne se rapporte pas.

⭐ Ce que huit points **peuvent** trancher est catégorique : **une seule** trace qui converge
suffirait à changer ce que ce dépôt sait faire. C'est donc le titre du rapport, et les
corrélations viennent après, avec leur plancher.

Usage :
    python3 src/graine/comparer_candidats.py --docs docs/mesures --graines data/prediction_paris4
    python3 src/graine/comparer_candidats.py --verifier
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

PREFIXE = "candidat_paris4_"
# ⚠ Le seuil de verdict vient de `test_convergence`, jamais recopie -- deux definitions de
# « converge » finiraient par ne pas s'accorder.
try:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]
    from test_convergence import ALPHA_TRAVERS, BRUIT_ALPHA
except ImportError:                                      # pragma: no cover
    ALPHA_TRAVERS, BRUIT_ALPHA = 0.7, 0.2


def rho_detectable(n: int, puissance: float = 0.80, alpha: float = 0.05) -> float | None:
    """Le ρ que n observations détectent, par l'approximation de Fisher.

    ⭐ Rapporté à côté d'un ρ non significatif, il transforme « on n'a rien vu » en « on
    aurait vu ceci ». Écrit ici plutôt qu'importé de `croiser_instruments` parce que ce
    fichier ne doit dépendre que de la bibliothèque standard — et la formule tient en une
    ligne, donc la dupliquer coûte moins que de tirer scipy.
    """
    if n < 6:
        return None
    # ⚠ Les quantiles normaux sont ecrits en dur pour les valeurs utilisees, et NOMMES : les
    # recalculer demanderait scipy, et les laisser anonymes rendrait la formule invérifiable.
    z_alpha, z_puissance = 1.959963985, 0.841621234   # 97,5 % et 80 %
    if abs(puissance - 0.80) > 1e-9 or abs(alpha - 0.05) > 1e-9:
        return None
    return math.tanh((z_alpha + z_puissance) / math.sqrt(n - 3))


def spearman(xs, ys) -> float | None:
    """ρ de Spearman, ex æquo au rang moyen."""
    n = len(xs)
    if n < 3:
        return None

    def rangs(v):
        ordre = sorted(range(n), key=lambda i: v[i])
        r = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j + 1 < n and v[ordre[j + 1]] == v[ordre[i]]:
                j += 1
            m = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1):
                r[ordre[k]] = m
            i = j + 1
        return r

    rx, ry = rangs(list(xs)), rangs(list(ys))
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    dx = sum((a - mx) ** 2 for a in rx) ** 0.5
    dy = sum((b - my) ** 2 for b in ry) ** 0.5
    return (num / (dx * dy)) if dx > 0 and dy > 0 else None


def lire_trace(log: Path) -> dict:
    """La génération atteinte et l'aire produite, lues dans le journal du traceur.

    ⚠⚠ **Parce qu'une aire peut ne rien mesurer.** Sur `PHercParis4`, les sept premières
    traces font toutes 0,3174 à 0,3182 cm² — quatre chiffres identiques pour des graines
    situées à des kilovoxels les unes des autres, dans deux prédictions différentes. Elles
    butent toutes sur la génération 59. L'aire mesure donc le **plafond** et pas la donnée,
    et la comparer d'un candidat à l'autre serait comparer un réglage à lui-même. C'est la
    troncature de `35`, à l'état pur.
    """
    if not log.is_file():
        return {}
    t = log.read_text(encoding="utf-8", errors="replace")
    gens = re.findall(r"^gen (\d+) ", t, re.M)
    aires = re.findall(r"generated surface .*?\(([0-9.]+) cm\^2\)", t)
    return {"generation_max": int(gens[-1]) if gens else None,
            "aire_cm2": float(aires[-1]) if aires else None}


def charger(docs: Path, graines: Path, travaux: Path | None = None) -> list[dict]:
    """Chaque candidat, avec ses propriétés de graine ET son verdict de trace.

    ⚠ Les propriétés viennent du fichier de graines, le verdict du fichier de convergence,
    et le lien se fait par l'indice que la campagne a mis dans le nom. Recopier les
    propriétés dans le second fichier aurait été plus simple à lire et aurait créé deux
    sources pour une même valeur.
    """
    props: dict[tuple[str, int], dict] = {}
    for p in sorted(graines.glob("graine_*.json")):
        nom = p.stem.replace("graine_", "")
        for i, c in enumerate(json.loads(p.read_text(encoding="utf-8")).get("candidats", [])):
            props[(nom, i)] = c
    out = []
    for p in sorted(docs.glob(f"{PREFIXE}*.json")):
        m = re.match(rf"{PREFIXE}(.+?)_c(\d+)$", p.stem)
        if not m:
            continue
        cle = (m.group(1), int(m.group(2)))
        c = props.get(cle)
        if c is None:
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        tr = lire_trace(travaux / f"{cle[0]}_c{cle[1]}" / "trace.log") if travaux else {}
        for x in (d.get("series") or ([d] if "verdict" in d else [])):
            out.append({"prediction": cle[0], "candidat": cle[1],
                        "planarite": c.get("planarite"), "occupation": c.get("occupation"),
                        "voisins": c.get("voisins"),
                        "verdict": x.get("verdict"), "alpha": x.get("alpha"), **tr})
    return out


def confronter(lignes: list[dict]) -> dict:
    """Le titre catégorique d'abord, les corrélations ensuite avec leur plancher."""
    convergents = [l for l in lignes if l.get("verdict") == "converge"]
    juges = [l for l in lignes if l.get("alpha") is not None]
    d = {"candidats": len(lignes), "avec_alpha": len(juges),
         "indecidables": sum(1 for l in lignes if l.get("verdict") == "indecidable"),
         "convergents": [f"{l['prediction']}_c{l['candidat']}" for l in convergents],
         "alpha_min": min((l["alpha"] for l in juges), default=None),
         "seuil_converge": ALPHA_TRAVERS, "resolution": BRUIT_ALPHA}
    # ⚠⚠ Si TOUTES les traces butent sur la meme generation, l'aire ne mesure que le
    # plafond -- et il faut le dire avant qu'on ne compare des aires.
    gens = [l["generation_max"] for l in lignes if l.get("generation_max") is not None]
    d["generations_atteintes"] = sorted(set(gens))
    d["toutes_au_plafond"] = bool(gens) and len(set(gens)) == 1
    aires = [l["aire_cm2"] for l in lignes if l.get("aire_cm2") is not None]
    if aires:
        d["aire_min_cm2"], d["aire_max_cm2"] = min(aires), max(aires)
        d["etendue_relative_aires"] = (max(aires) - min(aires)) / max(aires)

    plancher = rho_detectable(len(juges))
    d["rho_detectable"] = plancher
    d["correlations"] = {}
    for cle in ("planarite", "occupation", "voisins"):
        xs = [l[cle] for l in juges if l.get(cle) is not None]
        ys = [l["alpha"] for l in juges if l.get(cle) is not None]
        r = spearman(xs, ys) if len(xs) == len(ys) else None
        if r is None:
            continue
        # ⚠⚠ « concluant » se decide sur la PUISSANCE et pas sur un p : avec huit points,
        # un rho de 0,6 n'est pas une absence d'effet, c'est une absence de puissance.
        d["correlations"][cle] = {
            "rho": r, "n": len(xs),
            "concluant": bool(plancher is not None and abs(r) >= plancher)}
    return d


def verifier() -> int:
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    v("ρ vaut +1 sur un ordre identique",
      abs(spearman([1, 2, 3, 4], [5, 6, 7, 8]) - 1) < 1e-12)
    v("... et −1 sur l'ordre inverse",
      abs(spearman([1, 2, 3, 4], [8, 7, 6, 5]) + 1) < 1e-12)
    v("moins de trois points ne donnent pas de ρ", spearman([1, 2], [3, 4]) is None)

    # ⚠⚠ Le plancher de detection, qui est tout l'interet de ce fichier : a huit points il
    # depasse 0,84, donc presque rien n'est detectable et le dire est le resultat.
    p8 = rho_detectable(8)
    v("le plancher à huit points dépasse 0,84", p8 > 0.84, f"{p8:.3f}")
    v("... et il DÉCROÎT quand n grandit", rho_detectable(80) < p8)
    v("moins de six points n'ont pas de plancher", rho_detectable(5) is None)
    # ⚠ Une puissance ou un alpha non tabules doivent etre REFUSES, pas approximes en
    # silence -- un plancher faux est pire qu'un plancher absent.
    v("une puissance non tabulée est refusée", rho_detectable(20, puissance=0.9) is None)

    base = [{"prediction": "a", "candidat": i, "planarite": 0.99, "occupation": 0.1 * i,
             "voisins": 9 + i, "verdict": "suit la fenêtre", "alpha": 1.0 + 0.01 * i}
            for i in range(8)]
    r = confronter(base)
    v("aucun convergent est dit tel", r["convergents"] == [])
    # ⚠⚠ Une correlation PARFAITE reste non concluante si le plancher est au-dessus : c'est
    # le point du fichier, et sans cette sonde on croirait qu'il conclut.
    v("une corrélation parfaite à huit points est... concluante",
      r["correlations"]["occupation"]["concluant"] is True,
      str(r["correlations"]["occupation"]))
    # ⚠ Le controle : un rho MOYEN, lui, ne doit pas conclure.
    moyen = [dict(x, alpha=1.0 + 0.01 * (i % 3)) for i, x in enumerate(base)]
    rm = confronter(moyen)
    v("... alors qu'une corrélation moyenne ne conclut pas",
      rm["correlations"]["occupation"]["concluant"] is False,
      str(rm["correlations"]["occupation"]))

    # ⚠⚠ Le plafond de generations, et sa sonde. Des aires identiques a quatre chiffres pres
    # ne sont pas une coincidence : c'est une troncature commune, et il faut le DIRE avant
    # que quiconque compare des aires.
    plafonnees = [dict(x, generation_max=59, aire_cm2=0.3174 + 0.0001 * (i % 3))
                  for i, x in enumerate(base)]
    rp = confronter(plafonnees)
    v("des traces toutes à la même génération sont signalées", rp["toutes_au_plafond"])
    v("... et leur étendue d'aire est chiffrée",
      rp["etendue_relative_aires"] < 0.01, f"{rp['etendue_relative_aires']}")
    # ⚠ Le controle : des generations DIFFERENTES ne doivent pas etre dites au plafond,
    # sinon l'avertissement s'afficherait toujours et cesserait d'informer.
    variees = [dict(x, generation_max=40 + i, aire_cm2=0.3 + 0.1 * i)
               for i, x in enumerate(base)]
    v("des générations différentes ne sont PAS dites au plafond",
      confronter(variees)["toutes_au_plafond"] is False)
    v("sans journal de trace, aucune affirmation sur le plafond",
      confronter(base)["toutes_au_plafond"] is False)

    conv = base + [{"prediction": "b", "candidat": 0, "planarite": 0.9, "occupation": 0.4,
                    "voisins": 27, "verdict": "converge", "alpha": 0.02}]
    v("un convergent est nommé", confronter(conv)["convergents"] == ["b_c0"])
    v("... et l'α minimum le suit", abs(confronter(conv)["alpha_min"] - 0.02) < 1e-12)
    # ⚠ Une cellule indecidable n'a pas d'alpha et ne doit pas entrer dans les correlations.
    ind = base + [{"prediction": "b", "candidat": 1, "planarite": 0.9, "occupation": 0.4,
                   "voisins": 27, "verdict": "indecidable", "alpha": None}]
    ri = confronter(ind)
    v("une cellule indécidable est comptée à part", ri["indecidables"] == 1)
    v("... et n'entre pas dans les corrélations",
      ri["correlations"]["occupation"]["n"] == 8)

    if echecs:
        print(f"\nECHEC ({echecs} failures, {controles} checks)")
        return 1
    print(f"ALL PASS ({echecs} failures, {controles} checks)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--docs", type=Path, default=Path("docs/mesures"))
    ap.add_argument("--graines", type=Path, default=Path("data/prediction_paris4"))
    ap.add_argument("--travaux", type=Path, default=Path("data/paris4_candidats"),
                    help="dossiers de travail, pour lire les journaux de trace")
    ap.add_argument("--json", type=Path)
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()

    lignes = charger(a.docs, a.graines, a.travaux)
    if not lignes:
        print(f"aucun candidat tracé sous {a.docs} — lancer "
              f"src/outils/tracer_tous_candidats.sh", file=sys.stderr)
        return 1
    d = confronter(lignes)

    print(f"\n  {'candidat':<12} {'planarité':>10} {'occupation':>11} {'voisins':>8} "
          f"{'α':>8}  verdict")
    print("  " + "-" * 66)
    for l in sorted(lignes, key=lambda x: (x["prediction"], x["candidat"])):
        A = "—" if l["alpha"] is None else f"{l['alpha']:+.2f}"
        print(f"  {l['prediction'] + '_c' + str(l['candidat']):<12} "
              f"{l['planarite']:>10.4f} {l['occupation']:>11.4f} {l['voisins']:>8} "
              f"{A:>8}  {l['verdict']}")

    if d.get("toutes_au_plafond"):
        print(f"\n  ⚠⚠ les {len(lignes)} traces butent TOUTES sur la génération "
              f"{d['generations_atteintes'][0]} — leurs aires "
              f"({d['aire_min_cm2']:.4f} à {d['aire_max_cm2']:.4f} cm², "
              f"{d['etendue_relative_aires']:.2%} d'écart) mesurent le PLAFOND et pas la "
              f"donnée. Aucune n'a eu le droit de pousser.")

    print(f"\n  ⭐ traces qui CONVERGENT : "
          + (", ".join(d["convergents"]) if d["convergents"] else "aucune"))
    if d["alpha_min"] is not None:
        print(f"     α le plus bas obtenu : {d['alpha_min']:+.2f} "
              f"(seuil de condamnation {d['seuil_converge']})")
    print(f"  {d['indecidables']} indécidable(s), {d['avec_alpha']} avec un α")

    if d["rho_detectable"] is not None:
        print(f"\n  ⚠⚠ à {d['avec_alpha']} points, la corrélation détectable à 80 % de "
              f"puissance vaut {d['rho_detectable']:.2f} — rien de moins qu'une relation "
              f"quasi parfaite ne serait visible :")
        for cle, c in d["correlations"].items():
            marque = "⭐" if c["concluant"] else "⚠"
            print(f"     {marque} {cle:<12} ρ = {c['rho']:+.3f}"
                  + ("" if c["concluant"] else "  — sous le plancher, ne conclut rien"))
    else:
        print(f"\n  ⚠⚠ moins de six α : aucune corrélation n'est calculable")

    if a.json:
        a.json.write_text(json.dumps({**d, "lignes": lignes}, indent=2,
                                     ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"\n  écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
