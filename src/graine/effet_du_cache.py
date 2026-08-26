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


def mediane(v: list[float]) -> float:
    """La médiane, calculée ici plutôt qu'importée — pas de dépendance pour trois lignes."""
    x = sorted(v)
    n = len(x)
    return x[n // 2] if n % 2 else (x[n // 2 - 1] + x[n // 2]) / 2


def grouper(essais: list[dict]) -> list[dict]:
    """Une ligne par valeur de `--cache-gb`, avec la médiane et l'étendue de ses essais.

    ⚠⚠ **Pourquoi la médiane et pas la moyenne** : un essai qui tombe sur une lenteur réseau
    tire une moyenne sans limite, et le cache disque n'est jamais matérialisé ici — vérifié,
    le répertoire passé à `-v` reste vide — donc chaque essai retélécharge et le chronomètre
    porte autant le réseau que le réglage. La médiane de trois essais survit à un mauvais.

    ⚠ L'étendue est conservée à côté, parce que c'est **elle** qui décide si la différence
    entre deux valeurs veut dire quelque chose.
    """
    par: dict[int, list[dict]] = {}
    for e in essais:
        if e.get("secondes", 0) > 0:
            par.setdefault(e["cache_gb"], []).append(e)
    out = []
    for gb, lot in sorted(par.items()):
        t = [x["secondes"] for x in lot]
        r = [x["pic_rss_kio"] / 1048576.0 for x in lot]
        out.append({"cache_gb": gb, "n": len(lot),
                    "secondes": mediane(t), "etendue_s": max(t) - min(t),
                    "pic_go": mediane(r),
                    "empreinte": lot[0].get("empreinte"),
                    "empreintes": sorted({x.get("empreinte") for x in lot if x.get("empreinte")})})
    return out


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

    ok = grouper(essais)
    d["valeurs"] = [e["cache_gb"] for e in ok]
    d["repetitions"] = [e["n"] for e in ok]
    if len(ok) < 2:
        d["verdict"] = "insuffisant"
        d["raison"] = "il faut au moins deux valeurs de --cache-gb chronométrées"
        return d

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
    # ⚠⚠ Le contrôle qui décide si l'on a le droit de parler de temps. Si l'étendue DANS
    # une valeur dépasse l'écart ENTRE les valeurs, la série ne mesure pas le réglage : elle
    # mesure la variance de run. C'est la leçon que `campagne_thread_limit.sh` avait déjà
    # écrite, appliquée ici parce que le cache disque n'est jamais matérialisé et que chaque
    # essai retélécharge.
    d["etendue_intra_max_s"] = round(max(e["etendue_s"] for e in ok), 2)
    d["ecart_inter_s"] = round(lent["secondes"] - vite["secondes"], 2)
    d["temps_concluant"] = d["ecart_inter_s"] > d["etendue_intra_max_s"]
    # ⚠⚠ Un booleen cache la marge, et une marge mince se lit comme une conclusion solide.
    # Le rapport est publie a cote du verdict : a 1,1 la serie « passe » sans convaincre,
    # a 10 elle est ecrasante, et rien dans un « concluant » nu ne les distingue.
    d["marge_temps"] = (round(d["ecart_inter_s"] / d["etendue_intra_max_s"], 2)
                        if d["etendue_intra_max_s"] > 0 else None)
    d["marge_mince"] = bool(d["marge_temps"] is not None and d["marge_temps"] < 1.5)
    if not d["temps_concluant"]:
        # ⚠ La mémoire, elle, reste concluante : elle ne dépend pas du réseau. On refuse
        # de conclure sur le TEMPS sans jeter la moitié qui tient.
        d["verdict"] = "temps non concluant"
        d["raison"] = (f"l'étendue dans une même valeur ({d['etendue_intra_max_s']} s) "
                       f"dépasse l'écart entre valeurs ({d['ecart_inter_s']} s) : cette "
                       f"série mesure la variance de run, pas le réglage")
        d["recommande_par_la_memoire"] = min(
            (e for e in ok), key=lambda e: (e["pic_go"], e["cache_gb"]))["cache_gb"]
        return d

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
    if d["verdict"] == "temps non concluant":
        print(f"\n  ⚠⚠ {d['raison']}")
        print(f"  ⭐ mais la mémoire, elle, ne dépend pas du réseau : "
              f"--cache-gb {d['recommande_par_la_memoire']} pour le pic le plus bas")
        return
    print(f"  temps : {d['plus_lent']['secondes']:.0f} s à --cache-gb "
          f"{d['plus_lent']['cache_gb']}  →  {d['plus_rapide']['secondes']:.0f} s à "
          f"{d['plus_rapide']['cache_gb']}   ({d['gain_relatif']:.0%})")
    print(f"  pic de RSS : {d['pic_min_go']:.2f} à {d['pic_max_go']:.2f} Go")
    if d.get("marge_temps") is not None:
        print(f"  marge du temps : écart inter {d['ecart_inter_s']:.1f} s contre "
              f"étendue intra {d['etendue_intra_max_s']:.1f} s  "
              f"→ ×{d['marge_temps']:.2f}"
              + ("   ⚠ mince : le temps penche, il ne tranche pas"
                 if d["marge_mince"] else ""))
    print(f"\n  ⭐ {d['verdict']}   (le plus petit à moins de 5 % du meilleur ; "
          f"pic {d['pic_du_recommande_go']:.2f} Go)")
    if d.get("marge_mince"):
        print(f"     ⭐ la MÉMOIRE, elle, tranche sans ambiguïté : "
              f"{d['pic_min_go']:.2f} contre {d['pic_max_go']:.2f} Go")
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

    # ⚠⚠ Repetitions : trois essais par valeur, et l ecart INTRA doit pouvoir annuler la
    # conclusion sur le temps. Sans ce controle la serie publierait « 45 % plus rapide »
    # a partir de la meteo du reseau.
    bruyant = ([e(2, 60, 2.9), e(2, 130, 2.9), e(2, 95, 2.9)]
               + [e(8, 100, 8.0), e(8, 105, 8.0), e(8, 102, 8.0)])
    rb = confronter(bruyant, ram_go=32)
    v("une étendue intra plus grande que l'écart inter annule le temps",
      rb["verdict"] == "temps non concluant", rb["verdict"])
    v("... et la mémoire reste conclue", rb["recommande_par_la_memoire"] == 2)
    # ⚠ Valeur attendue calculée à la main et INDÉPENDAMMENT : les médianes sont 95
    # (de 60/95/130) et 102 (de 100/102/105), donc l'écart inter vaut 7 — pas 42, qui est
    # ce qu'on obtient en comparant des extrêmes. Ma première version écrivait 42 et le
    # témoin a corrigé le rédacteur, pas le code.
    v("... et le refus chiffre les deux étendues",
      rb["etendue_intra_max_s"] == 70.0 and rb["ecart_inter_s"] == 7.0,
      f"{rb['etendue_intra_max_s']} / {rb['ecart_inter_s']}")
    net = ([e(2, 60, 2.9), e(2, 62, 2.9), e(2, 61, 2.9)]
           + [e(8, 200, 8.0), e(8, 202, 8.0), e(8, 201, 8.0)])
    rn = confronter(net, ram_go=32)
    v("une série propre conclut bien sur le temps", rn["temps_concluant"])
    v("... avec une marge écrasante", rn["marge_temps"] > 10 and not rn["marge_mince"],
      str(rn["marge_temps"]))
    # ⚠⚠ Le cas reel de ce depot : 70,3 contre 61,7. La regle passe, et il faut que le
    # rapport le DISE -- sinon un « concluant » nu se lit comme une conclusion solide.
    # ⚠ La fixture reprend la série RÉELLE, valeur bruyante comprise : c'est elle qui
    # crée la marge mince (--cache-gb 2 s'étend sur 61,7 s), et une fixture qui l'omet
    # rend ×2,92 au lieu de ×1,14 — donc ne teste pas le cas qu'on veut attraper.
    mince = ([e(1, 71, 1.8), e(1, 67, 1.8), e(1, 80, 1.8)]
             + [e(2, 144, 3.0), e(2, 110, 3.0), e(2, 82, 3.0)]
             + [e(8, 141, 4.5), e(8, 153, 4.5), e(8, 129, 4.5)])
    rm = confronter(mince, ram_go=32)
    v("une marge mince est signalée comme telle", rm["marge_mince"], str(rm["marge_temps"]))
    v("... tout en concluant quand même", rm["temps_concluant"])
    v("... et sans marge mince quand elle est large", not rn["marge_mince"])
    v("... et recommande la valeur rapide", rn["recommande"] == 2, rn["verdict"])
    v("les répétitions sont comptées", rn["repetitions"] == [3, 3], str(rn["repetitions"]))
    v("la médiane est utilisée, pas la moyenne", mediane([1, 2, 100]) == 2)

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
    ap.add_argument("--json", type=Path, default=Path("docs/mesures/etalon_rendu.json"))
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
