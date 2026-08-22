#!/usr/bin/env python3
"""Quelle taille de cache de chunks donner au rendu, mesurée plutôt que devinée.

⚠⚠ **D'où vient ce fichier.** Le rendu d'une surface de 3,66 cm² tenait **28,2 Go** de RSS
sur une machine de 31,8, avec 3,4 Go en swap et le cache de pages du noyau écrasé à 442 Mo —
et **23,7 % d'un cœur** alors que la machine en a 22 et que le processus avait 59 threads. Il
n'était pas limité par le calcul : il attendait la mémoire. La cause était dans nos propres
arguments — `--cache-gb` vaut **16 par défaut** et aucun des 28 appels du dépôt ne le règle.

⚠ Ce que ce fichier cherche n'est pas « le plus rapide » mais **le plus petit qui ne coûte
rien** : un cache qui déborde de la RAM disponible transforme un gain de cache en swap, et le
swap coûte bien plus que le cache ne rapporte. Le point d'inflexion se mesure ; le choisir au
jugé est exactement ce qui a produit la situation ci-dessus.

⚠⚠ Et la première chose vérifiée n'est pas une performance : c'est que **la sortie ne bouge
pas**. Un réglage qui change les pixels n'est pas un réglage de performance — ce serait dire
que tous les rendus déjà publiés dépendaient d'une valeur que personne n'avait posée.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# ⚠ Marge laissée au reste du système. Un cache dimensionné sur la RAM TOTALE ignore que le
# noyau, le cache de pages et le processus lui-même en veulent aussi — et c'est précisément
# l'erreur qui a mis 3,4 Go en swap.
PART_UTILISABLE = 0.5


def confronter(essais: list[dict], ram_go: float | None = None) -> dict:
    d: dict = {"n_essais": len(essais),
               "valeurs": [e["cache_gb"] for e in essais]}
    if not essais:
        d["verdict"] = "insuffisant"
        d["raison"] = "aucun essai"
        return d

    # ⭐ La correction passe AVANT la performance : si les sorties diffèrent, aucune des
    # secondes gagnées ne compte, parce qu'on ne rendrait plus la même chose.
    emp = {e.get("empreinte") for e in essais if e.get("empreinte")}
    d["sorties_identiques"] = len(emp) <= 1
    if not d["sorties_identiques"]:
        d["verdict"] = "REGLAGE NON NEUTRE"
        d["raison"] = (f"{len(emp)} sorties différentes selon --cache-gb : ce n'est pas un "
                       f"réglage de performance, c'est un réglage qui change le résultat")
        return d

    ok = [e for e in essais if e.get("secondes", 0) > 0]
    if len(ok) < 2:
        d["verdict"] = "insuffisant"
        d["raison"] = "il faut au moins deux essais chronométrés"
        return d

    for e in ok:
        e["pic_go"] = e["pic_rss_kio"] / 1048576.0
    lent = max(ok, key=lambda e: e["secondes"])
    vite = min(ok, key=lambda e: e["secondes"])
    d["plus_lent"] = {"cache_gb": lent["cache_gb"], "secondes": lent["secondes"]}
    d["plus_rapide"] = {"cache_gb": vite["cache_gb"], "secondes": vite["secondes"]}
    d["gain_relatif"] = (lent["secondes"] - vite["secondes"]) / lent["secondes"]
    d["pic_min_go"] = round(min(e["pic_go"] for e in ok), 2)
    d["pic_max_go"] = round(max(e["pic_go"] for e in ok), 2)

    # ⚠⚠ Le nombre qui décide : le plus PETIT cache dont le temps est à moins de 5 % du
    # meilleur. Prendre simplement le plus rapide choisirait souvent le plus gros, donc
    # reconduirait le défaut qu'on est en train de corriger.
    seuil = vite["secondes"] * 1.05
    tenables = sorted((e for e in ok if e["secondes"] <= seuil), key=lambda e: e["cache_gb"])
    d["assez_bons"] = [e["cache_gb"] for e in tenables]
    d["recommande"] = tenables[0]["cache_gb"] if tenables else vite["cache_gb"]
    d["pic_du_recommande_go"] = round(
        next(e["pic_go"] for e in ok if e["cache_gb"] == d["recommande"]), 2)

    if ram_go:
        d["ram_go"] = ram_go
        d["plafond_prudent_gb"] = int(ram_go * PART_UTILISABLE)
        # ⚠ Un pic qui dépasse la part utilisable est une prédiction de swap, pas une
        # observation : on le dit comme tel.
        d["depasse_la_part_utilisable"] = d["pic_du_recommande_go"] > d["plafond_prudent_gb"]

    d["verdict"] = f"--cache-gb {d['recommande']}"
    return d


def rapporter(d: dict) -> None:
    if d["verdict"] == "insuffisant":
        print(f"  ⚠ {d['raison']}")
        return
    if d["verdict"] == "REGLAGE NON NEUTRE":
        print(f"  ⚠⚠ {d['raison']}")
        return
    print(f"  sorties identiques sur les {d['n_essais']} essais  ✅")
    print(f"  temps : {d['plus_lent']['secondes']:.0f} s à --cache-gb "
          f"{d['plus_lent']['cache_gb']}  →  {d['plus_rapide']['secondes']:.0f} s à "
          f"{d['plus_rapide']['cache_gb']}   ({d['gain_relatif']:.0%})")
    print(f"  pic de RSS : {d['pic_min_go']:.2f} à {d['pic_max_go']:.2f} Go")
    print(f"\n  ⭐ {d['verdict']}   (le plus petit à moins de 5 % du meilleur ; "
          f"pic {d['pic_du_recommande_go']:.2f} Go)")
    if d.get("depasse_la_part_utilisable"):
        print(f"  ⚠⚠ ce pic dépasse la moitié des {d['ram_go']:.0f} Go de la machine — "
              f"prévoir du swap")


def _verifier() -> int:
    ech, ok = [], True

    def v(nom, cond, det=""):
        nonlocal ok
        ech.append((nom, bool(cond), det))
        ok = ok and bool(cond)

    def e(gb, sec, rss_go, emp="aaa"):
        return {"cache_gb": gb, "secondes": sec,
                "pic_rss_kio": int(rss_go * 1048576), "empreinte": emp}

    # ⭐ Le cas central : au-dela de 4 Go le temps ne bouge plus, donc 4 suffit -- et prendre
    # le plus rapide aurait choisi 16, c est-a-dire reconduit le defaut.
    plat = [e(1, 200, 1.2), e(2, 130, 2.1), e(4, 101, 4.0), e(8, 100, 7.9), e(16, 99, 15.5)]
    r = confronter(plat, ram_go=32)
    v("le plus petit cache assez bon est recommandé", r["recommande"] == 4, r["verdict"])
    v("... et ce n'est PAS le plus rapide", r["plus_rapide"]["cache_gb"] == 16)
    v("le gain est chiffré", 0.5 < r["gain_relatif"] < 0.55, f"{r['gain_relatif']}")
    v("le pic du recommandé est rapporté", abs(r["pic_du_recommande_go"] - 4.0) < 0.01)
    v("les sorties identiques sont constatées", r["sorties_identiques"])

    # ⚠⚠ Le controle qui prime sur tout : si les sorties different, le fichier REFUSE de
    # parler de performance. Une seconde gagnee sur un autre resultat n est pas un gain.
    faux = [e(1, 200, 1.2, "aaa"), e(16, 99, 15.5, "bbb")]
    rf = confronter(faux, ram_go=32)
    v("des sorties différentes annulent toute conclusion de perf",
      rf["verdict"] == "REGLAGE NON NEUTRE")
    v("... et le dit en clair", "change le résultat" in rf["raison"])
    v("... sans recommander quoi que ce soit", "recommande" not in rf)

    # ⚠ La prediction de swap : un pic au-dela de la moitie de la RAM est annonce.
    gros = [e(8, 300, 20.0), e(16, 290, 28.0)]
    rg = confronter(gros, ram_go=32)
    v("un pic au-delà de la part utilisable est signalé", rg["depasse_la_part_utilisable"])
    v("... et la part utilisable est dérivée de la RAM", rg["plafond_prudent_gb"] == 16)
    petit = [e(1, 300, 1.0), e(2, 295, 2.0)]
    v("... et ne se déclenche pas quand le pic est modeste",
      confronter(petit, ram_go=32)["depasse_la_part_utilisable"] is False)

    v("aucun essai, aucun verdict", confronter([])["verdict"] == "insuffisant")
    v("un seul essai chronométré ne conclut pas",
      confronter([e(4, 100, 4.0)])["verdict"] == "insuffisant")
    v("sans RAM déclarée, aucune prédiction de swap",
      "depasse_la_part_utilisable" not in confronter(plat))

    for nom, o, det in ech:
        if not o:
            print(f"  FAIL {nom}" + (f"  [{det}]" if det else ""))
    print(f"{'ALL PASS' if ok else 'FAILURES'} "
          f"({sum(1 for _, o, _ in ech if not o)} failures, {len(ech)} checks)")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", type=Path, default=Path("docs/etalon_rendu.json"))
    ap.add_argument("--ram-go", type=float)
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return _verifier()
    if not a.json.exists():
        print(f"aucun étalonnage dans {a.json}", file=sys.stderr)
        return 2
    d = json.loads(a.json.read_text(encoding="utf-8"))
    ram = a.ram_go
    if ram is None:
        try:
            with open("/proc/meminfo") as f:
                for l in f:
                    if l.startswith("MemTotal:"):
                        ram = int(l.split()[1]) / 1048576.0
                        break
        except Exception:
            ram = None
    r = confronter(d.get("essais") or [], ram_go=ram)
    rapporter(r)
    d["resume"] = r
    a.json.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
