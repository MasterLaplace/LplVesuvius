#!/usr/bin/env python3
"""Un rendu ne va pas à vitesse constante, et une moyenne cumulée le cache.

⚠⚠⚠ Pourquoi ce fichier existe, et c'est une erreur à moi. Le 2026-08-28 j'ai publié qu'un
segment coûtait **455 ms par fenêtre** contre 98 pour un autre, et j'ai écarté la contention
« par mesure » en citant 1586 % de CPU. Ce chiffre était juste et ma lecture était fausse :
1586 % sur une machine qui en offre **2200** veut dire que **six cœurs faisaient autre
chose** — c'est-à-dire exactement la contention que je déclarais écartée. Pendant ces trois
heures je faisais tourner des batteries, des balayages et des rendus de figure sur la même
machine.

⭐ Ce que la moyenne cumulée cachait, et qu'une allure instantanée montre du premier coup :
le même run est passé de **0,75 fenêtre par seconde au début à 5,5 à la fin**, soit un
facteur **sept sur lui-même**. Une moyenne sur un intervalle où les conditions changent n'est
la vitesse de rien.

⚠ La leçon transportable : un débit ne se publie pas depuis un cumul. Il se publie depuis un
intervalle où l'on peut dire ce qui tournait à côté, ou pas du tout.

⚠ Ce fichier ne lit que des LIGNES DE PROGRESSION déjà écrites : il ne relance rien, ne
mesure rien lui-même, et ne peut donc pas contredire le rendu qu'il décrit.

Usage :
    uv run python src/encre/allure_du_rendu.py --verifier
    uv run python src/encre/allure_du_rendu.py /tmp/camp1447e.log --fils 16
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]

PROGRESSION = re.compile(
    r"(\d+)/(\d+)\s+fen[êe]tres\s+\(\s*\d+%\)\s+écoulé\s+(\d+)([hm])(\d+)"
)
"""⚠⚠ Le motif accepte `2h54` ET `35m04`, et les DEUX ne veulent pas dire la même chose : au
format `XhYY` le second nombre est des minutes, au format `XmYY` c'est des secondes. Un motif
qui lirait les deux comme « minutes puis secondes » compterait 2 h 54 comme 2 min 54, soit
une allure soixante fois trop grande sur toute la fin d'un long run — et rien dans le
résultat n'aurait l'air faux."""


def secondes_de(premier: str, unite: str, second: str) -> int:
    """Une durée écrite `XhYY` ou `XmYY`, en secondes.

    ⚠ Les secondes sont ABSENTES au-delà d'une heure : `2h54` ne dit rien de plus fin que la
    minute. C'est une perte réelle, dite ici plutôt que masquée, et elle borne la précision
    de toute allure calculée sur deux lignes voisines d'un long run.
    """
    if unite == "h":
        return int(premier) * 3600 + int(second) * 60
    return int(premier) * 60 + int(second)


def points(texte: str) -> list[tuple[int, int]]:
    """Les couples (fenêtres faites, secondes écoulées) d'un log de campagne.

    ⚠⚠ Un log de campagne enchaîne PLUSIEURS rendus, et chacun repart de zéro. Un compteur
    qui recule signale donc un nouveau rendu, et mélanger les deux ferait une allure négative
    ou absurde à la jointure.
    """
    out: list[tuple[int, int]] = []
    for m in PROGRESSION.finditer(texte):
        faites, _total = int(m.group(1)), int(m.group(2))
        out.append((faites, secondes_de(m.group(3), m.group(4), m.group(5))))
    return out


def segments(pts: list[tuple[int, int]]) -> list[list[tuple[int, int]]]:
    """Découpe la suite de points là où le compteur de fenêtres RECULE."""
    lots: list[list[tuple[int, int]]] = []
    for p in pts:
        if not lots or p[0] < lots[-1][-1][0]:
            lots.append([p])
        else:
            lots[-1].append(p)
    return lots


def allures(lot: list[tuple[int, int]]) -> list[float]:
    """Fenêtres par seconde entre points consécutifs, intervalles nuls écartés.

    ⚠ Un intervalle de zéro seconde vient de la résolution à la minute des longs runs, pas
    d'un rendu instantané : le compter ferait une division par zéro ou une allure infinie.
    """
    return [(b[0] - a[0]) / (b[1] - a[1])
            for a, b in zip(lot, lot[1:]) if b[1] > a[1] and b[0] >= a[0]]


def resume_du_lot(lot: list[tuple[int, int]], fils: int) -> dict:
    """Cumul, extrêmes et queue d'un rendu — les trois lectures qui diffèrent."""
    a = allures(lot)
    if not a or lot[-1][1] <= 0:
        return {"points": len(lot), "mesurable": False}
    tri = sorted(a)
    # ⚠⚠ La QUEUE compte à part : c'est le seul intervalle dont on puisse parfois dire ce qui
    # tournait à côté, et c'est celui que la moyenne cumulée dilue le plus.
    queue = a[-min(5, len(a)):]
    cumul = lot[-1][0] / lot[-1][1]
    return {
        "points": len(lot),
        "mesurable": True,
        "fenetres": lot[-1][0],
        "secondes": lot[-1][1],
        "cumul_fen_par_s": round(cumul, 3),
        "cumul_par_fil_seconde": round(cumul / fils, 4) if fils else None,
        "minimum_fen_par_s": round(tri[0], 3),
        "median_fen_par_s": round(tri[len(tri) // 2], 3),
        "maximum_fen_par_s": round(tri[-1], 3),
        "queue_fen_par_s": round(sum(queue) / len(queue), 3),
        "queue_par_fil_seconde": round(sum(queue) / len(queue) / fils, 4) if fils else None,
        "amplitude": round(tri[-1] / tri[0], 2) if tri[0] > 0 else None,
    }


def resume(texte: str, fils: int) -> dict:
    lots = segments(points(texte))
    return {"fils": fils, "rendus": [resume_du_lot(l, fils) for l in lots]}


def verifier() -> int:
    """Auto-test HORS LIGNE, sur des lignes de progression fabriquées."""
    echecs = controles = 0

    def v(nom: str, ok: bool) -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}")

    # --- LA LECTURE DES DEUX FORMES DE DUREE -------------------------------------------
    court = "    3172/22036 fenêtres (14%)  écoulé 35m04  reste ~3h28"
    long_ = "    20712/22036 fenêtres (94%)  écoulé 2h49  reste ~10m51"
    v("la forme minutes-secondes est lue", points(court) == [(3172, 2104)])
    # ⚠ Au-dela d'une heure la ligne perd ses secondes : la resolution tombe a la minute.
    v("la forme heures-minutes est lue", points(long_) == [(20712, 10140)])
    v("les deux formes se lisent dans le meme log",
      [p[0] for p in points(court + "\n" + long_)] == [3172, 20712])
    v("une ligne qui n'est pas une progression est ignoree",
      points("fenetres          : 22036") == [])
    v("l'accent circonflexe n'est pas exige",
      points("  10/100 fenetres ( 5%)  écoulé 1m00") == [(10, 60)])

    # --- LE DECOUPAGE PAR RENDU ---------------------------------------------------------
    # ⚠⚠ Un log de campagne enchaine plusieurs rendus, chacun repartant de zero.
    deux = [(100, 10), (200, 20), (5, 30), (10, 40)]
    v("un compteur qui recule ouvre un nouveau rendu", len(segments(deux)) == 2)
    v("... et chaque rendu garde ses propres points",
      [len(s) for s in segments(deux)] == [2, 2])
    v("un rendu unique reste d'un seul tenant",
      len(segments([(1, 1), (2, 2), (3, 3)])) == 1)
    v("une suite vide ne rend aucun rendu", segments([]) == [])

    # --- L'ALLURE -----------------------------------------------------------------------
    v("l'allure est la pente entre deux points",
      allures([(0, 0), (100, 10)]) == [10.0])
    # ⚠ Un intervalle de zero seconde vient de la resolution a la minute, pas d'un rendu
    # instantane : le compter ferait une division par zero.
    # ⚠ L'intervalle nul est SAUTE, et la paire suivante est calculee sur ses propres
    # bornes : (100-50)/(10-0) = 5, et non sur le point d'origine.
    v("un intervalle de duree nulle est ecarte",
      allures([(0, 0), (50, 0), (100, 10)]) == [5.0])
    v("aucun point ne donne aucune allure", allures([(1, 1)]) == [])

    # --- LES TROIS LECTURES QUI DIFFERENT -----------------------------------------------
    # ⭐ Le coeur du fichier : un run lent puis rapide a un cumul qui n'est la vitesse de rien.
    lent_puis_vite = [(0, 0), (10, 100), (20, 200), (30, 300), (40, 400), (50, 500),
                      (550, 600), (1050, 700), (1550, 800), (2050, 900), (2550, 1000)]
    r = resume_du_lot(lent_puis_vite, 4)
    v("le cumul dilue le run", abs(r["cumul_fen_par_s"] - 2550 / 1000) < 1e-6)
    v("le minimum voit le debut lent", abs(r["minimum_fen_par_s"] - 0.1) < 1e-6)
    v("le maximum voit la fin rapide", abs(r["maximum_fen_par_s"] - 5.0) < 1e-6)
    v("l'amplitude dit de combien le run a change", r["amplitude"] == 50.0)
    # ⚠⚠ La queue ne prend que les cinq derniers intervalles : sur un run assez long pour
    # que le debut ne pese plus, elle voit la fin la ou le cumul voit tout.
    v("la queue ne regarde que la fin",
      abs(r["queue_fen_par_s"] - 5.0) < 1e-6)
    # ⚠⚠ ET LE CONTROLE QUI DONNE SON SENS AU FICHIER : le cumul est STRICTEMENT entre les
    # deux extremes, donc il ne peut representer ni l'un ni l'autre.
    v("le cumul n'est ni le minimum ni le maximum",
      r["minimum_fen_par_s"] < r["cumul_fen_par_s"] < r["maximum_fen_par_s"])
    v("la queue suit la fin et non le cumul",
      r["queue_fen_par_s"] > r["cumul_fen_par_s"])
    v("le debit par fil-seconde divise bien par les fils",
      abs(r["cumul_par_fil_seconde"] - r["cumul_fen_par_s"] / 4) < 1e-6)
    v("un lot sans allure mesurable le dit",
      resume_du_lot([(5, 0)], 4)["mesurable"] is False)

    print(f"\n{'ALL PASS' if not echecs else 'ECHEC'} "
          f"({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("log", nargs="?", type=Path)
    ap.add_argument("--fils", type=int, default=16)
    ap.add_argument("--json", type=Path)
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()
    if not a.log or not a.log.exists():
        ap.error("donner un log de campagne existant, ou --verifier")

    r = resume(a.log.read_text(encoding="utf-8", errors="replace"), a.fils)
    for i, lot in enumerate(r["rendus"], 1):
        if not lot["mesurable"]:
            print(f"  rendu {i} : {lot['points']} point(s), allure non mesurable")
            continue
        print(f"  rendu {i} : {lot['fenetres']} fenêtres en {lot['secondes']} s "
              f"({lot['points']} points)")
        print(f"      cumul   {lot['cumul_fen_par_s']:6.3f} fen/s  "
              f"({lot['cumul_par_fil_seconde']:.4f} par fil-s)")
        print(f"      min/med/max  {lot['minimum_fen_par_s']:.3f} / "
              f"{lot['median_fen_par_s']:.3f} / {lot['maximum_fen_par_s']:.3f}  "
              f"amplitude ×{lot['amplitude']}")
        print(f"      queue   {lot['queue_fen_par_s']:6.3f} fen/s  "
              f"({lot['queue_par_fil_seconde']:.4f} par fil-s)")
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False) + "\n")
        print(f"→ {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
