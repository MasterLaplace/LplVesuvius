#!/usr/bin/env python3
"""Un recalage LOCAL peut-il ce qu'un modèle lisse ne peut pas ? — l'ouverture, prise autrement.

⚠⚠ POURQUOI CE FICHIER EXISTE. `75` C1 a mesuré qu'un modèle polynomial du champ de décalage
**ne prédit pas** un carreau qu'il n'a pas vu : 21 cellules d'erreur en laissant-un-dehors
contre **17** pour le champ **nul**. La cause est chiffrée — le problème d'**ouverture** : le
plateau des décalages acceptables est allongé **9 fois sur 1** en médiane, parce qu'un bord
droit ne contraint que la composante perpendiculaire.

⭐⭐ Le remède classique de l'ouverture n'est pas un modèle global, c'est l'**agrégation
locale** : deux carreaux voisins dont les bords ne sont pas parallèles donnent deux équations
indépendantes, et déterminent ensemble les deux composantes — à condition que le déplacement
soit à peu près constant sur le voisinage. C'est Lucas–Kanade, et c'est exactement ce qu'un
polynôme de bas degré **ne fait pas** : il impose une forme globale au lieu de lire le
voisinage.

⚠⚠⚠ **Et la question se tranche sur les carreaux DÉJÀ mesurés**, sans rien recalculer : chacun
porte sa normale, donc le conditionnement d'un voisinage se lit. Ce fichier mesure, pour chaque
rayon, si les normales d'un voisinage **couvrent les deux directions**, et si le déplacement
résolu dessus prédit le carreau omis **mieux que zéro**.

  ⚠ Le contrôle est le **champ nul**, comme pour le polynôme, et pour la même raison : sur un
    champ dont la médiane des normes vaut 60 cellules, prédire zéro est déjà une prédiction
    honorable, et tout ce qui ne la bat pas ne mesure rien.

⚠ Ce fichier ne recale rien. Il dit si un recalage local **est possible avec ces carreaux-là**,
ce qui décide entre « densifier autrement les mêmes bords » et « aller chercher du contenu
intérieur ».

Usage :
    uv run python src/encre/le_recalage_local.py --verifier
    uv run python src/encre/le_recalage_local.py \\
        --json docs/mesures/le_recalage_local.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
MESURE = RACINE / "docs" / "mesures" / "le_recalage_des_etiquettes.json"

RAYONS = (256, 384, 512, 768, 1024, 1536)
"""Les rayons balayés, en cellules de la grille réduite.

⚠ Balayés et non choisis : un rayon trop petit ne réunit que des bords parallèles, un rayon
trop grand suppose un déplacement constant là où il ne l'est pas. Le résultat est la COURBE,
pas un point — et si aucun rayon ne bat le champ nul, c'est le fait."""


def voisinage(carreaux: list[dict], k: int, rayon: float) -> list[int]:
    """Les indices des carreaux à moins de `rayon` du k-ième — **sans lui**.

    ⚠⚠ L'exclusion est ce qui rend la validation honnête : un voisinage qui contiendrait le
    carreau jugé le prédirait par construction, et l'erreur mesurerait un ajustement au lieu
    d'une prédiction.
    """
    ci, cj = carreaux[k]["i"], carreaux[k]["j"]
    return [n for n, c in enumerate(carreaux)
            if n != k and (c["i"] - ci) ** 2 + (c["j"] - cj) ** 2 <= rayon * rayon]


def normales(carreaux: list[dict], indices: list[int]) -> np.ndarray:
    """Les directions **mesurées** de chaque carreau du voisinage.

    ⚠ Un carreau sans normale déclarée a eu un optimum NET, donc ses deux composantes sont
    contraintes : il compte pour deux directions orthogonales, pas pour zéro.
    """
    out = []
    for n in indices:
        d = carreaux[n].get("normale")
        if d is None:
            out += [[1.0, 0.0], [0.0, 1.0]]
        else:
            out.append([float(d[0]), float(d[1])])
    return np.array(out, dtype=float) if out else np.zeros((0, 2))


def conditionnement(dirs: np.ndarray) -> float:
    """
    @brief Dans quelle mesure ces directions couvrent-elles le plan ? — de 0 à 1.

    ⚠⚠ C'est le rapport des valeurs propres de @f$\\sum_k n_k n_k^T@f$ : **1** quand les
    directions sont isotropes, **0** quand elles sont toutes parallèles. C'est la forme exacte
    du problème d'ouverture — des bords tous parallèles ne déterminent qu'une composante,
    quel que soit leur nombre.
    """
    if dirs.shape[0] < 2:
        return 0.0
    m = dirs.T @ dirs
    val = np.linalg.eigvalsh(m)
    return float(val[0] / val[-1]) if val[-1] > 0 else 0.0


def resoudre_localement(carreaux: list[dict], indices: list[int]) -> tuple[float, float] | None:
    """Le déplacement que le voisinage détermine, par flot normal — ou `None`.

    ⚠ Une équation par carreau, celle qu'il MESURE : écrire les deux reviendrait à affirmer une
    mesure qu'on n'a pas, et c'est ce qui a fait échouer le modèle global.
    """
    lignes, valeurs = [], []
    for n in indices:
        c = carreaux[n]
        d = c.get("normale")
        if d is None:
            lignes += [[1.0, 0.0], [0.0, 1.0]]
            valeurs += [float(c["di"]), float(c["dj"])]
            continue
        lignes.append([float(d[0]), float(d[1])])
        valeurs.append(float(d[0]) * c["di"] + float(d[1]) * c["dj"])
    if len(lignes) < 2:
        return None
    a = np.array(lignes)
    if conditionnement(a) < 1e-6:
        return None
    sol = np.linalg.lstsq(a, np.array(valeurs), rcond=None)[0]
    return float(sol[0]), float(sol[1])


def laisser_un_dehors(carreaux: list[dict], rayon: float) -> dict:
    """L'erreur de prédiction d'un carreau omis, contre celle du champ NUL.

    ⚠⚠ Les deux erreurs sont calculées **sur les mêmes carreaux** — ceux que le voisinage sait
    résoudre : comparer une prédiction faite sur un sous-ensemble à un champ nul évalué sur
    tous comparerait deux populations.
    """
    erreurs, nuls, en, nn, conds, tailles, resolus = [], [], [], [], [], [], 0
    for k, c in enumerate(carreaux):
        vs = voisinage(carreaux, k, rayon)
        cond = conditionnement(normales(carreaux, vs))
        d = resoudre_localement(carreaux, vs) if vs else None
        if d is None:
            continue
        resolus += 1
        conds.append(cond)
        tailles.append(len(vs))
        erreurs.append(float(np.hypot(d[0] - c["di"], d[1] - c["dj"])))
        nuls.append(float(np.hypot(c["di"], c["dj"])))
        # ⚠⚠ ET LA COMPOSANTE NORMALE, séparément. La norme entière inclut la direction que le
        # carreau NE MESURE PAS : `75` C1 le dit — « une bonne moitié de ce décalage est dans
        # la direction non contrainte ». Juger une prédiction de flot normal sur la norme
        # entière lui reproche de ne pas prédire ce que personne n'a mesuré.
        u = c.get("normale")
        if u is not None:
            en.append(abs(u[0] * (d[0] - c["di"]) + u[1] * (d[1] - c["dj"])))
            nn.append(abs(u[0] * c["di"] + u[1] * c["dj"]))
    if not erreurs:
        return {"rayon": rayon, "resolus": 0}
    out = {"rayon": rayon, "resolus": resolus, "carreaux": len(carreaux),
           "voisins_median": int(np.median(tailles)),
           "voisins_max": int(max(tailles)),
           # ⚠⚠⚠ « Local » doit se VÉRIFIER : au-delà d'un certain rayon le voisinage est tout
           # le fragment, et ce qu'on mesurerait alors n'est plus une agrégation locale mais un
           # modèle global d'ordre zéro. Rendu plutôt que supposé.
           "voisinage_est_global": bool(max(tailles) >= len(carreaux) - 1),
           "conditionnement_median": round(float(np.median(conds)), 4),
           "erreur_mediane": round(float(np.median(erreurs)), 2),
           "erreur_p90": round(float(np.percentile(erreurs, 90)), 2),
           "erreur_du_champ_nul": round(float(np.median(nuls)), 2),
           "bat_le_champ_nul": bool(np.median(erreurs) < np.median(nuls))}
    if en:
        out.update({"erreur_normale_mediane": round(float(np.median(en)), 2),
                    "champ_nul_normal": round(float(np.median(nn)), 2),
                    "bat_le_nul_sur_la_normale": bool(np.median(en) < np.median(nn))})
    return out


def balayer(carreaux: list[dict], rayons=RAYONS) -> list[dict]:
    """Le laissant-un-dehors à chaque rayon — la COURBE, pas un point."""
    return [laisser_un_dehors(carreaux, r) for r in rayons]


def charger(chemin: Path = MESURE) -> list[dict]:
    """Les carreaux contraints, LUS dans la mesure de `75` C1 plutôt que recalculés."""
    if not chemin.is_file():
        return []
    return (json.loads(chemin.read_text()).get("champ_local") or {}).get("carreaux") or []


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # --- le conditionnement, qui EST le problème d'ouverture ---
    v("des directions orthogonales couvrent le plan",
      abs(conditionnement(np.array([[1.0, 0.0], [0.0, 1.0]])) - 1.0) < 1e-9)
    # ⚠⚠ LE CAS QUI COMPTE : des bords tous parallèles ne déterminent qu'une composante, quel
    # que soit leur NOMBRE. C'est l'ouverture, et c'est ce qu'un compte de carreaux masque.
    v("... et cent bords parallèles n'en couvrent qu'une",
      conditionnement(np.array([[1.0, 0.0]] * 100)) < 1e-9, "cent carreaux, une seule direction")
    v("... et deux directions proches le couvrent mal",
      0.0 < conditionnement(np.array([[1.0, 0.0], [0.9950, 0.0998]])) < 0.02,
      f"{conditionnement(np.array([[1.0, 0.0], [0.9950, 0.0998]])):.4f}")
    v("une seule direction ne conditionne rien", conditionnement(np.array([[1.0, 0.0]])) == 0.0)

    # --- la résolution locale ---
    droit = [{"i": 0, "j": 0, "di": 3.0, "dj": -5.0, "normale": [1.0, 0.0]},
             {"i": 0, "j": 100, "di": 3.0, "dj": -5.0, "normale": [0.0, 1.0]}]
    d = resoudre_localement(droit, [0, 1])
    v("deux bords perpendiculaires déterminent le déplacement",
      d is not None and abs(d[0] - 3.0) < 1e-9 and abs(d[1] + 5.0) < 1e-9, str(d))
    # ⚠⚠ Et deux bords PARALLÈLES ne le déterminent pas : le solveur doit REFUSER plutôt que
    # rendre une des infinies solutions, qui aurait l'air d'une mesure.
    para = [{"i": 0, "j": 0, "di": 3.0, "dj": -5.0, "normale": [1.0, 0.0]},
            {"i": 0, "j": 100, "di": 3.0, "dj": 40.0, "normale": [1.0, 0.0]}]
    v("... et deux bords parallèles font REFUSER, au lieu de rendre une des infinies solutions",
      resoudre_localement(para, [0, 1]) is None)
    v("un carreau sans normale déclarée compte pour DEUX directions",
      normales([{"i": 0, "j": 0, "di": 0, "dj": 0}], [0]).shape[0] == 2)

    # --- le voisinage ---
    grille = [{"i": 0, "j": 0, "di": 0.0, "dj": 0.0, "normale": [1.0, 0.0]},
              {"i": 0, "j": 100, "di": 0.0, "dj": 0.0, "normale": [0.0, 1.0]},
              {"i": 0, "j": 900, "di": 0.0, "dj": 0.0, "normale": [0.0, 1.0]}]
    v("le voisinage prend ce qui est à portée", voisinage(grille, 0, 200) == [1])
    # ⚠⚠ L'EXCLUSION DE SOI : un voisinage qui contiendrait le carreau jugé le prédirait par
    # construction, et l'erreur mesurerait un ajustement au lieu d'une prédiction.
    v("... et JAMAIS le carreau jugé lui-même", 0 not in voisinage(grille, 0, 10000))

    # --- le laissant-un-dehors, dans les deux sens ---
    # ⭐ Un champ RÉELLEMENT constant est prédit exactement, donc la méthode peut réussir.
    constant = [{"i": 0, "j": 0, "di": 7.0, "dj": 2.0, "normale": [1.0, 0.0]},
                {"i": 0, "j": 100, "di": 7.0, "dj": 2.0, "normale": [0.0, 1.0]},
                {"i": 100, "j": 0, "di": 7.0, "dj": 2.0, "normale": [0.7071, 0.7071]},
                {"i": 100, "j": 100, "di": 7.0, "dj": 2.0, "normale": [0.7071, -0.7071]}]
    r = laisser_un_dehors(constant, 1000)
    v("un champ constant est prédit exactement et bat le champ nul",
      r["erreur_mediane"] < 0.01 and r["bat_le_champ_nul"], str(r))
    # ⚠⚠ Et le contrôle inverse : un champ ALÉATOIRE ne doit pas battre le nul, sinon la
    # mesure serait satisfaite par n'importe quoi.
    rng = np.random.default_rng(42)
    bruit = [{"i": int(a), "j": int(b), "di": float(rng.normal(0, 60)),
              "dj": float(rng.normal(0, 60)),
              "normale": [float(np.cos(t)), float(np.sin(t))]}
             for a, b, t in zip(rng.integers(0, 2000, 40), rng.integers(0, 2000, 40),
                                rng.uniform(0, np.pi, 40))]
    rb = laisser_un_dehors(bruit, 3000)
    v("... alors qu'un champ aléatoire ne le bat pas",
      not rb["bat_le_champ_nul"], f"{rb['erreur_mediane']} contre {rb['erreur_du_champ_nul']}")

    # --- contre les VRAIS carreaux ---
    carreaux = charger()
    if not carreaux:
        print("  ⚠ carreaux absents : la partie « vrai arbre » n'a pas tourné")
    else:
        b = balayer(carreaux)
        v(f"les {len(carreaux)} carreaux mesurés sont chargés", len(carreaux) >= 30)
        utiles = [x for x in b if x.get("resolus")]
        v("... et au moins un rayon les résout", len(utiles) >= 1,
          f"{len(utiles)} rayons sur {len(b)}")
        # ⭐⭐ Sur la NORME ENTIÈRE, l'agrégation locale bat bel et bien le champ nul aux
        # grands rayons — et j'avais écrit l'assertion dans l'autre sens, en supposant qu'elle
        # échouerait comme le polynôme. C'est la mesure qui a corrigé.
        gagnants = [x for x in utiles if x["bat_le_champ_nul"]]
        v(f"sur la norme entière, l'agrégation locale bat le champ nul aux grands rayons "
          f"({len(gagnants)}/{len(utiles)})", len(gagnants) >= 2,
          " · ".join(f"r{x['rayon']}: {x['erreur_mediane']} contre "
                     f"{x['erreur_du_champ_nul']}" for x in utiles))
        # ⚠⚠⚠ ET C'EST UN MIRAGE, mesuré : sur la composante NORMALE — la seule que chaque
        # carreau mesure réellement — aucun rayon ne bat le champ nul. Le gain de la norme
        # entière vient donc **entièrement de la direction non contrainte**, c'est-à-dire d'une
        # grandeur que personne n'a mesurée. C'est le péché cardinal du dépôt sous un costume
        # de plus : une amélioration sur la composante que la mesure ne contient pas.
        normaux = [x for x in utiles if "bat_le_nul_sur_la_normale" in x]
        v("... mais AUCUN ne le bat sur la composante NORMALE, la seule qui soit mesurée",
          normaux and not any(x["bat_le_nul_sur_la_normale"] for x in normaux),
          " · ".join(f"r{x['rayon']}: {x['erreur_normale_mediane']} contre "
                     f"{x['champ_nul_normal']}" for x in normaux))
        # ⚠⚠⚠ Et il faut ASSERTER que la composante normale en est une. Sans ces deux
        # contrôles, la remplacer par la norme entière ne fait rien échouer — les deux verdicts
        # restent « ne bat pas » — et la distinction qui porte tout le résultat n'est vérifiée
        # par rien. Mesuré le 2026-09-05 : la sonde rendait ALL PASS.
        v("... et la composante normale est STRICTEMENT plus petite que la norme, partout",
          all(x["erreur_normale_mediane"] < x["erreur_mediane"] for x in normaux),
          " · ".join(f"r{x['rayon']}: {x['erreur_normale_mediane']} < {x['erreur_mediane']}"
                     for x in normaux))
        # ⭐⭐ LE MIRAGE, asserté : les deux métriques rendent des verdicts DIFFÉRENTS. Si elles
        # mesuraient la même chose, elles s'accorderaient partout — et il n'y aurait rien à dire.
        v("... et les deux métriques se CONTREDISENT à au moins un rayon — c'est le mirage",
          any(x["bat_le_champ_nul"] != x["bat_le_nul_sur_la_normale"] for x in normaux),
          " · ".join(f"r{x['rayon']}: norme {x['bat_le_champ_nul']}, "
                     f"normale {x['bat_le_nul_sur_la_normale']}" for x in normaux))
        # ⚠ Et le voisinage reste LOCAL : sans ce contrôle, un « gain » aux grands rayons
        # pourrait n'être qu'un modèle global d'ordre zéro déguisé.
        v("... et le voisinage n'est jamais tout le fragment",
          not any(x.get("voisinage_est_global") for x in utiles),
          f"au plus {max(x['voisins_max'] for x in utiles)} voisins sur {len(carreaux)}")
        # ⭐ La cause, chiffrée : les directions ne couvrent jamais le plan. À 1 elles seraient
        # isotropes ; le meilleur rayon plafonne bien en dessous.
        v("... parce que les directions ne couvrent jamais le plan",
          max(x["conditionnement_median"] for x in utiles) < 0.7,
          " · ".join(f"r{x['rayon']}: {x['conditionnement_median']}" for x in utiles))

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--mesure", type=Path, default=MESURE)
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    carreaux = charger(a.mesure)
    if not carreaux:
        raise SystemExit(f"aucun carreau dans {a.mesure}")
    b = balayer(carreaux)
    print(f"{'rayon':>7} {'résolus':>9} {'cond. médian':>13} {'erreur méd.':>12} "
          f"{'p90':>7} {'champ nul':>10} {'bat ?':>6}")
    print("-" * 72)
    for x in b:
        if not x.get("resolus"):
            print(f"{x['rayon']:>7} {'0':>9}  aucun voisinage résoluble")
            continue
        print(f"{x['rayon']:>7} {x['resolus']:>9} {x['conditionnement_median']:>13.4f} "
              f"{x['erreur_mediane']:>12.2f} {x['erreur_p90']:>7.2f} "
              f"{x['erreur_du_champ_nul']:>10.2f} {'OUI' if x['bat_le_champ_nul'] else 'non':>6}")
    r = {"carreaux": len(carreaux), "balayage": b,
         "un_rayon_bat_le_champ_nul": any(x.get("bat_le_champ_nul") for x in b)}
    print("\nun rayon bat le champ nul : "
          + ("OUI" if r["un_rayon_bat_le_champ_nul"] else "NON"))
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
