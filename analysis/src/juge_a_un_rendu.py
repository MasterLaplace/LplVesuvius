#!/usr/bin/env python3
"""Peut-on juger une spire avec UN rendu au lieu de deux ?

⚠⚠ Pourquoi la question vaut d'etre posee. Le test de convergence (`38`) demande **deux**
rendus de la meme surface, et un rendu est l'etape la plus chere de tout ce depot : sur les
campagnes de `43`, chaque spire coute deux rendus de ~3000x3000 sur 31 puis 81 couches. Un
juge a un seul rendu diviserait par deux le cout de toute campagne d'enchainement, et
permettrait d'essayer plusieurs candidats par tour la ou on n'en essaie qu'un.

Le candidat naturel est `au_bord_relief`, deja calcule par `depth_profile` : la part des
fenetres dont le pic de contraste tombe **au bord** de la fenetre rendue. C'est exactement
la forme locale de ce que le test de convergence mesure globalement — un pic au bord veut
dire « il n'y a pas de pic la-dedans ».

⚠⚠ ET IL FAUT LE VERIFIER AVANT DE S'EN SERVIR. Un proxy qui se trompe sur les cas
difficiles est pire qu'aucun proxy : il fait economiser du calcul en rendant des verdicts
faux, et un verdict faux d'apparence normale est ce que ce depot traque. Le test est donc
une correlation de rang contre le vrai α, sur toutes les spires deja jugees des deux facons.

⚠ On ne se contente pas du ρ global : ce qui compte est le comportement sur les spires que
le vrai juge **condamne**. Un proxy peut trier correctement les bonnes et rater toutes les
mauvaises, et le ρ global le cacherait.

Usage :
    uv run python analysis/src/juge_a_un_rendu.py --racine data --json docs/juge_a_un_rendu.json
"""
from __future__ import annotations

import argparse
import glob
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from derive_ou_loterie import permutation, spearman  # noqa: E402

# α au-dela duquel le vrai juge dit « en travers » (seuil de test_convergence).
SEUIL_TRAVERS = 0.75


def etiquette_de(dossier: str) -> str:
    base = Path(dossier).name
    return "" if base == "spires" else base.removeprefix("spires_") + "_"


def recolter(racine: Path, fenetre: int = 31) -> list[dict]:
    """Apparier, pour chaque spire, la statistique d'UN rendu et l'α des DEUX."""
    lignes = []
    for prof in sorted(glob.glob(str(racine / "spires*" / "spire*" / f"profil_{fenetre}c.json"))):
        p = Path(prof)
        campagne, spire = p.parts[-3], p.parts[-2]
        verdict = RACINE / "docs" / f"spire_{etiquette_de(campagne)}{spire}.json"
        if not verdict.is_file():
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        d = d[0] if isinstance(d, list) else d
        s = json.loads(verdict.read_text(encoding="utf-8"))["series"][0]
        lignes.append({
            "campagne": campagne, "spire": spire,
            "au_bord": d.get("au_bord_relief"),
            "part_plates": d.get("part_plates"),
            "ecart_un_rendu_um": d.get("ecart_trace_um_median"),
            "alpha": s["alpha"], "verdict": s["verdict"],
        })
    return lignes


def juger_le_juge(lignes: list[dict], clef: str = "au_bord") -> dict:
    xs = [l[clef] for l in lignes if l[clef] is not None]
    ys = [l["alpha"] for l in lignes if l[clef] is not None]
    if len(xs) < 4:
        return {"n": len(xs), "assez": False}
    r = permutation(xs, ys)
    # ⚠ Le chiffre qui decide vraiment : parmi les spires que le VRAI juge condamne, combien
    # le proxy aurait-il seulement signalees ? Un proxy qui les rate toutes est inutilisable
    # meme avec un beau ρ global.
    mauvaises = [l for l in lignes if l["alpha"] >= SEUIL_TRAVERS and l[clef] is not None]
    seuil_proxy = sorted(xs)[len(xs) // 2] if xs else 0.0
    # ⚠ Comparaison INCLUSIVE : avec un `>` strict, la spire dont la statistique vaut
    # exactement la médiane n'était pas comptée, et un proxy parfait sortait à 3 sur 4.
    # Le témoin l'a attrapé.
    rattrapees = [l for l in mauvaises if l[clef] >= seuil_proxy]
    return {
        "n": len(xs), "assez": True, "clef": clef,
        "rho": r["rho"], "p": r["p"], "exact": r["exact"],
        "mauvaises": len(mauvaises), "mauvaises_signalees": len(rattrapees),
        "seuil_proxy_median": seuil_proxy,
    }


def verifier() -> int:
    echecs = 0

    def ok(cond, quoi):
        nonlocal echecs
        print(("  ✅ " if cond else "  ❌ ") + quoi)
        if not cond:
            echecs += 1

    print("Témoins de juge_a_un_rendu")

    ok(etiquette_de("data/spires") == "", "la campagne de base n'a pas d'étiquette")
    ok(etiquette_de("data/spires_dedans") == "dedans_", "une campagne nommée porte la sienne")

    # Un proxy PARFAIT doit ressortir, et signaler toutes les mauvaises.
    parfait = [{"au_bord": a, "alpha": a, "verdict": ""} for a in
               (0.0, 0.1, 0.2, 0.3, 0.9, 1.0, 1.2, 1.5)]
    r = juger_le_juge(parfait)
    ok(r["rho"] > 0.99, f"un proxy parfait a ρ = {r['rho']:.2f}")
    ok(r["mauvaises"] == 4 and r["mauvaises_signalees"] == 4,
       f"…et signale les 4 mauvaises ({r['mauvaises_signalees']}/4)")

    # ⚠⚠ Un proxy INVERSE des cas difficiles : bon ρ global, et il rate toutes les mauvaises.
    # C'est le mode de panne que le ρ seul cacherait, d'où le second chiffre.
    piege = [{"au_bord": 0.9, "alpha": 0.0, "verdict": ""},
             {"au_bord": 0.8, "alpha": 0.1, "verdict": ""},
             {"au_bord": 0.7, "alpha": 0.2, "verdict": ""},
             {"au_bord": 0.6, "alpha": 0.3, "verdict": ""},
             {"au_bord": 0.0, "alpha": 1.0, "verdict": ""},
             {"au_bord": 0.0, "alpha": 1.2, "verdict": ""},
             {"au_bord": 0.0, "alpha": 1.4, "verdict": ""},
             {"au_bord": 0.0, "alpha": 1.6, "verdict": ""}]
    rp = juger_le_juge(piege)
    ok(rp["mauvaises"] == 4 and rp["mauvaises_signalees"] == 0,
       f"un proxy qui rate TOUTES les mauvaises est vu comme tel "
       f"({rp['mauvaises_signalees']}/4) — la sonde")

    ok(juger_le_juge([{"au_bord": 0.1, "alpha": 0.2, "verdict": ""}])["assez"] is False,
       "trop peu de points : le juge refuse de juger")
    ok(juger_le_juge([{"au_bord": None, "alpha": 0.2, "verdict": ""}] * 8)["assez"] is False,
       "des statistiques absentes ne comptent pas comme des points")

    print(f"\n{'tous les témoins passent' if not echecs else f'{echecs} échec(s)'}")
    return 1 if echecs else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--racine", type=Path, default=RACINE / "data")
    ap.add_argument("--fenetre", type=int, default=31)
    ap.add_argument("--json")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()

    lignes = recolter(a.racine, a.fenetre)
    if not lignes:
        print("aucune spire jugée des deux façons", file=sys.stderr)
        return 3

    print(f"{'campagne':<18}{'spire':<9}{'au bord':>9}{'plates':>8}"
          f"{'écart 1 rendu':>15}{'α (2 rendus)':>14}")
    for l in lignes:
        print(f"{l['campagne']:<18}{l['spire']:<9}"
              f"{(l['au_bord'] if l['au_bord'] is not None else -1):>9.3f}"
              f"{(l['part_plates'] if l['part_plates'] is not None else -1):>8.3f}"
              f"{l['ecart_un_rendu_um']:>15.1f}{l['alpha']:>+14.3f}")

    for clef in ("au_bord", "ecart_un_rendu_um"):
        r = juger_le_juge(lignes, clef)
        if not r["assez"]:
            print(f"\n  {clef} : {r['n']} point(s), trop peu")
            continue
        print(f"\n  {clef} contre α : ρ = {r['rho']:+.3f}  p = {r['p']:.3f}  (n = {r['n']})")
        print(f"    spires que le vrai juge condamne (α ≥ {SEUIL_TRAVERS}) : "
              f"{r['mauvaises']} — dont {r['mauvaises_signalees']} au-dessus de la médiane "
              f"du proxy")
        if r["mauvaises"] and r["mauvaises_signalees"] == 0:
            print("    ⚠⚠ INUTILISABLE : il rate TOUTES les spires condamnées. "
                  "Un proxy qui se trompe sur les cas difficiles fait économiser du calcul "
                  "en rendant des verdicts faux.")
        elif r["p"] >= 0.05:
            print("    ⚠ aucune relation détectable — ne remplace pas les deux rendus")
        else:
            print("    ✅ relation détectable ; reste à vérifier qu'elle tient sur les cas durs")

    if a.json:
        Path(a.json).write_text(json.dumps(
            {"spires": lignes,
             "juges": {c: juger_le_juge(lignes, c)
                       for c in ("au_bord", "ecart_un_rendu_um")}},
            indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"\n  écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
