#!/usr/bin/env python3
"""Un critère mesuré à une profondeur de rendu peut-il juger une trace mesurée à une autre ?

⚠⚠ **La question de `29` N4, reformulée par la mesure.** N4 demandait « choisir une
référence défendable pour le critère du tiers central », après que
[`36`](../docs/36_lorigine_de_la_pile.md) eut montré qu'un segment officiel n'en est pas une.
Chercher une meilleure référence suppose que le critère, lui, est une propriété de la
surface. Ce fichier teste cette supposition — et elle ne tient pas.

⭐⭐ **Ce qui rend la question mal posée** : le rendu impose un `plafond_um` PROPORTIONNEL à
sa profondeur. Une trace dont la matière est plus loin que ce plafond ne rapporte pas sa
distance, elle rapporte **le plafond**. Un seuil absolu comparé à une valeur censurée ne
compare pas deux surfaces, il compare deux réglages — et c'est exactement la troncature que
[`35`](../docs/35_le_tirage_sur_douze_rouleaux.md) a déjà payée sur le budget de générations.

⚠ Deux critères ne se transfèrent pas l'un à l'autre. `au_bord` et `part_plates` sont des
grandeurs différentes, et ce fichier publie leur corrélation précisément pour qu'on ne
transporte pas la dérive de l'un sur l'autre — le raccourci que ce dépôt a failli prendre.

Usage :
    uv run python analysis/src/derive_avec_profondeur.py --docs docs \\
        --json docs/derive_profondeur.json
    python3 analysis/src/derive_avec_profondeur.py --verifier
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# ⚠ Les criteres portes par un balayage de profondeur, et ce qu'ils valent.
# `ecart_um` est CENSURE par construction ; les deux autres sont des fractions, donc
# bornees a [0,1] sans plafond impose par le rendu. Les traiter pareil serait l'erreur.
CRITERES = ("ecart_um", "au_bord", "part_plates")
CENSURABLES = ("ecart_um",)


def mediane(xs):
    """La médiane, écrite ici plutôt qu'importée : ce fichier ne doit dépendre que de la
    bibliothèque standard pour rester lançable hors de l'environnement d'inférence."""
    v = sorted(xs)
    n = len(v)
    if not n:
        return None
    return v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2.0


def spearman(xs, ys):
    """ρ de Spearman, à la main — pas de scipy sur ce chemin.

    ⚠ Les ex æquo reçoivent leur rang MOYEN. Les numéroter dans l'ordre d'arrivée ferait
    dépendre le résultat de l'ordre des lignes du fichier, ce qui n'est pas une propriété
    des données.
    """
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
            moyen = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1):
                r[ordre[k]] = moyen
            i = j + 1
        return r

    rx, ry = rangs(xs), rangs(ys)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    dx = sum((a - mx) ** 2 for a in rx) ** 0.5
    dy = sum((b - my) ** 2 for b in ry) ** 0.5
    return (num / (dx * dy)) if dx > 0 and dy > 0 else None


def charger(dossier: Path) -> dict[int, dict]:
    """Les balayages de profondeur présents, indexés par profondeur de rendu."""
    out = {}
    for p in sorted(dossier.glob("second_axe_*.json")):
        try:
            prof = int(p.stem.rsplit("_", 1)[1])
        except ValueError:
            continue
        out[prof] = json.loads(p.read_text(encoding="utf-8"))
    return out


def apparier(a: dict, b: dict) -> list[tuple[dict, dict]]:
    """Les traces présentes aux DEUX profondeurs, appariées par identité.

    ⚠⚠ Par `(rouleau, répétition)` et jamais par position dans la liste. Deux balayages
    n'ont aucune raison d'ordonner leurs lignes pareil, et un appariement positionnel
    comparerait la trace d'un rouleau à celle d'un autre en produisant des nombres
    parfaitement plausibles. C'est le piège que `apparier_volumes` a déjà payé sur les
    scans.
    """
    par_cle = {(l["rouleau"], l["repetition"]): l for l in b.get("lignes", [])}
    return [(l, par_cle[(l["rouleau"], l["repetition"])])
            for l in a.get("lignes", [])
            if (l["rouleau"], l["repetition"]) in par_cle]


def derive(paires, critere: str) -> dict:
    """De combien un critère bouge entre deux profondeurs, sur les mêmes traces.

    ⚠⚠ Les traces CENSURÉES sont écartées et comptées, jamais moyennées. Une valeur
    censurée n'est pas la distance de la trace, c'est le plafond du rendu : la faire entrer
    dans une dérive mesurerait le déplacement du plafond en croyant mesurer la surface. Et
    comme le plafond monte avec la profondeur, l'erreur irait toujours dans le même sens —
    donc elle ressemblerait à un effet.
    """
    ecarts, censurees = [], 0
    for x, y in paires:
        if critere in CENSURABLES and (x.get("censure") or y.get("censure")):
            censurees += 1
            continue
        if x.get(critere) is None or y.get(critere) is None:
            continue
        ecarts.append(abs(float(y[critere]) - float(x[critere])))
    return {"critere": critere, "n_compare": len(ecarts), "n_censurees": censurees,
            "derive_mediane": mediane(ecarts), "derive_max": max(ecarts) if ecarts else None}


def plafonds_distincts(sweep: dict) -> list[float]:
    """Les plafonds réellement présents dans un balayage, et pas celui de son en-tête.

    ⚠⚠ Un balayage a UN `plafond_um` dans son en-tête et un par ligne, et ils diffèrent :
    la cohorte mélange deux tailles de voxel (8,64 et 9,362 µm), donc le plafond du rendu
    est proportionnel au voxel du rouleau. Prendre celui de l'en-tête fait passer les
    traces de l'autre voxel pour des traces SOUS le plafond alors qu'elles sont
    exactement AU leur — c'est-à-dire fait disparaître la moitié de la censure.
    """
    return sorted({float(l["plafond_um"]) for l in sweep.get("lignes", [])
                   if l.get("plafond_um") is not None})


def censure_coherente(sweep: dict) -> dict:
    """« Censurée » veut-il bien dire « à son propre plafond » ?

    ⭐ L'invariant est épinglé plutôt que supposé. Tout le raisonnement de `47` repose sur
    le fait qu'une trace marquée censurée rapporte le réglage et non sa distance ; si le
    drapeau voulait dire autre chose, la lecture entière serait fausse.
    """
    au_plafond = hors = 0
    for l in sweep.get("lignes", []):
        if not l.get("censure"):
            continue
        pl, e = l.get("plafond_um"), l.get("ecart_um")
        if pl is not None and e is not None and abs(float(e) - float(pl)) < 1e-6:
            au_plafond += 1
        else:
            hors += 1
    return {"censurees_au_plafond": au_plafond, "censurees_ailleurs": hors,
            "coherente": hors == 0}


def confronter(sweeps: dict[int, dict], basse: int, haute: int) -> dict:
    """Le rapport complet entre deux profondeurs de rendu."""
    a, b = sweeps[basse], sweeps[haute]
    paires = apparier(a, b)
    d = {"profondeur_basse": basse, "profondeur_haute": haute,
         "traces_appariees": len(paires),
         "plafond_bas_um": a.get("plafond_um"), "plafond_haut_um": b.get("plafond_um"),
         "censurees_en_bas": sum(1 for l in a.get("lignes", []) if l.get("censure")),
         "censurees_en_haut": sum(1 for l in b.get("lignes", []) if l.get("censure")),
         "lignes_en_bas": len(a.get("lignes", [])),
         "lignes_en_haut": len(b.get("lignes", [])),
         "plafonds_bas_um": plafonds_distincts(a),
         "plafonds_haut_um": plafonds_distincts(b),
         "censure_bas": censure_coherente(a), "censure_haut": censure_coherente(b),
         "derives": [derive(paires, c) for c in CRITERES]}
    if d["plafond_bas_um"] and d["plafond_haut_um"]:
        d["rapport_plafonds"] = d["plafond_haut_um"] / d["plafond_bas_um"]
        d["rapport_profondeurs"] = haute / basse
    # ⚠⚠ La correlation entre criteres, publiee POUR QU'ON NE TRANSFERE PAS la derive de
    # l'un a l'autre. Deux criteres faiblement -- voire negativement -- correles ne sont pas
    # la meme quantite, et ce depot a failli transporter la derive de `au_bord` sur le
    # critere du tiers central pour la seule raison qu'ils parlent tous deux d'un profil.
    xs = [float(x["au_bord"]) for x, _ in paires if x.get("au_bord") is not None]
    ys = [float(x["part_plates"]) for x, _ in paires if x.get("au_bord") is not None]
    d["rho_au_bord_part_plates"] = spearman(xs, ys) if len(xs) == len(ys) else None
    return d


def verdict(d: dict) -> dict:
    """Ce que la mesure autorise à dire, et à quelle portée.

    ⭐ La question de N4 — « quelle référence ? » — n'est pas tranchée par un meilleur
    choix de référence. Elle est **dissoute** : tant qu'une part notable des traces bute
    sur le plafond du rendu, un seuil absolu compare des plafonds. Le critère doit être lu
    à DEUX profondeurs, comme l'exposant α, et alors il n'a plus besoin de référence.
    """
    n_bas = d.get("lignes_en_bas") or 0
    part = (d.get("censurees_en_bas") or 0) / n_bas if n_bas else None
    stables = [x["critere"] for x in d["derives"]
               if x["derive_mediane"] is not None and x["derive_mediane"] < 0.01]
    return {"part_censuree_en_bas": part,
            "criteres_stables_en_profondeur": stables,
            "seuil_absolu_defendable": bool(part is not None and part < 0.10 and stables),
            "raison": (
                "un seuil absolu comparerait des plafonds : "
                f"{d.get('censurees_en_bas')}/{n_bas} traces butent sur le plafond du rendu "
                f"le moins profond, et ce plafond monte d'un facteur "
                f"{d.get('rapport_plafonds', float('nan')):.2f} avec la profondeur"
                if part is not None and part >= 0.10 else
                "aucune censure notable : un seuil absolu peut être discuté")}


def verifier() -> int:
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    v("la médiane d'un nombre pair de points est la moyenne des deux du milieu",
      mediane([1, 2, 3, 4]) == 2.5)
    v("... et d'un nombre impair, celui du milieu", mediane([5, 1, 3]) == 3)
    v("une liste vide n'a pas de médiane", mediane([]) is None)

    v("ρ vaut +1 sur un ordre identique", abs(spearman([1, 2, 3, 4], [9, 10, 11, 12]) - 1) < 1e-12)
    v("... et −1 sur un ordre inversé", abs(spearman([1, 2, 3, 4], [4, 3, 2, 1]) + 1) < 1e-12)
    # ⚠⚠ Les ex aequo au rang MOYEN : numerotes dans l'ordre d'arrivee, rho dependrait de
    # l'ordre des lignes du fichier, qui n'est pas une propriete des donnees.
    v("les ex æquo ne dépendent pas de l'ordre des lignes",
      abs(spearman([1, 1, 2, 3], [5, 6, 7, 8])
          - spearman([1, 1, 2, 3], [6, 5, 7, 8])) < 1e-12)
    v("moins de trois points ne donnent pas de ρ", spearman([1, 2], [3, 4]) is None)

    # ⚠⚠ TROIS traces, et pas deux, et c'est un temoin qui a impose ce chiffre. Avec DEUX
    # traces la mediane est la moyenne des deux ecarts, et la somme des ecarts est la meme
    # quelle que soit la facon dont on apparie -- donc l'appariement positionnel rendait
    # EXACTEMENT le meme nombre que l'appariement par identite. La sonde ne pouvait pas
    # echouer. A trois, la mediane cesse d'etre une moyenne et les deux se separent.
    a = {"lignes": [{"rouleau": "A", "repetition": "r1", "au_bord": 0.10,
                     "part_plates": 0.5, "ecart_um": 90.0, "censure": True},
                    {"rouleau": "B", "repetition": "r1", "au_bord": 0.20,
                     "part_plates": 0.4, "ecart_um": 30.0, "censure": False},
                    {"rouleau": "C", "repetition": "r1", "au_bord": 0.30,
                     "part_plates": 0.3, "ecart_um": 45.0, "censure": False}],
         "plafond_um": 90.0}
    # ⚠ Les lignes sont dans l'ORDRE INVERSE : c'est ce qui rend la sonde capable d'echouer.
    b = {"lignes": [{"rouleau": "C", "repetition": "r1", "au_bord": 0.90,
                     "part_plates": 0.35, "ecart_um": 70.0, "censure": False},
                    {"rouleau": "B", "repetition": "r1", "au_bord": 0.25,
                     "part_plates": 0.4, "ecart_um": 55.0, "censure": False},
                    {"rouleau": "A", "repetition": "r1", "au_bord": 0.12,
                     "part_plates": 0.9, "ecart_um": 180.0, "censure": True}],
         "plafond_um": 180.0}
    pa = apparier(a, b)
    v("l'appariement est par identité, pas par position", len(pa) == 3)
    dab = derive(pa, "au_bord")
    v("... et la dérive s'en trouve juste",
      abs(dab["derive_mediane"] - 0.05) < 1e-12, f"{dab['derive_mediane']}")
    # ⚠⚠ Et la sonde le DIT plutot que de le supposer : on calcule ce que l'appariement
    # positionnel donnerait, et on exige que ce soit un autre nombre. Sans ca, rien
    # n'atteste que ce temoin distingue quoi que ce soit.
    positionnel = derive(list(zip(a["lignes"], b["lignes"])), "au_bord")
    v("... et l'appariement positionnel donnerait un AUTRE nombre",
      abs(positionnel["derive_mediane"] - dab["derive_mediane"]) > 0.05,
      f"{positionnel['derive_mediane']} contre {dab['derive_mediane']}")

    # ⚠⚠ La censure : une valeur au plafond n'est pas une distance. La compter ferait
    # mesurer le deplacement du PLAFOND (90 -> 180) en croyant mesurer la surface.
    de = derive(pa, "ecart_um")
    v("une trace censurée est écartée de la dérive", de["n_compare"] == 2)
    v("... et comptée", de["n_censurees"] == 1)
    v("... et la dérive restante est celle de la trace mesurée",
      abs(de["derive_max"] - 25.0) < 1e-12, f"{de['derive_max']}")
    # ⚠ Le controle du controle : un critere NON censurable garde toutes ses traces.
    v("un critère non censurable garde toutes ses traces",
      derive(pa, "au_bord")["n_censurees"] == 0)

    # ⚠⚠ Deux plafonds dans une meme cohorte : la sonde qui a corrige la figure. Prendre
    # celui de l'en-tete faisait passer les traces de l'autre voxel pour des traces SOUS le
    # plafond, donc faisait disparaitre la moitie de la censure.
    a["lignes"][0]["plafond_um"] = 90.0
    a["lignes"][1]["plafond_um"] = 86.0
    a["lignes"][2]["plafond_um"] = 86.0
    v("les plafonds distincts d'une cohorte sont tous rapportés",
      plafonds_distincts(a) == [86.0, 90.0], str(plafonds_distincts(a)))
    v("une trace censurée À SON plafond est cohérente",
      censure_coherente({"lignes": [{"censure": True, "plafond_um": 86.0,
                                     "ecart_um": 86.0}]})["coherente"])
    # ⚠ Et le controle : une trace marquee censuree AILLEURS qu'a son plafond doit etre
    # signalee -- sinon le drapeau pourrait vouloir dire autre chose sans qu'on le sache.
    incoherente = censure_coherente({"lignes": [{"censure": True, "plafond_um": 86.0,
                                                 "ecart_um": 40.0}]})
    v("... et une trace censurée AILLEURS est signalée", incoherente["coherente"] is False)
    v("... et comptée", incoherente["censurees_ailleurs"] == 1)
    v("une trace non censurée n'entre pas dans le compte",
      censure_coherente({"lignes": [{"censure": False, "plafond_um": 86.0,
                                     "ecart_um": 40.0}]})["censurees_au_plafond"] == 0)

    c = confronter({21: a, 41: b}, 21, 41)
    v("le rapport des plafonds est publié", abs(c["rapport_plafonds"] - 2.0) < 1e-12)
    v("les censures sont comptées de chaque côté",
      c["censurees_en_bas"] == 1 and c["censurees_en_haut"] == 1)
    ver = verdict(c)
    v("une censure de moitié interdit le seuil absolu",
      ver["seuil_absolu_defendable"] is False)
    v("... et la raison nomme le plafond", "plafond" in ver["raison"])
    # ⚠ Et le controle du controle : sans censure et sans derive, un seuil absolu
    # redevient discutable -- sinon la garde eteindrait aussi les cas ou elle ne sert pas.
    propre = {"lignes": [{"rouleau": "A", "repetition": "r1", "au_bord": 0.10,
                          "part_plates": 0.5, "ecart_um": 30.0, "censure": False}],
              "plafond_um": 90.0}
    propre2 = {"lignes": [{"rouleau": "A", "repetition": "r1", "au_bord": 0.101,
                           "part_plates": 0.5, "ecart_um": 30.0, "censure": False}],
               "plafond_um": 180.0}
    v("sans censure ni dérive, un seuil absolu reste discutable",
      verdict(confronter({21: propre, 41: propre2}, 21, 41))["seuil_absolu_defendable"])

    if echecs:
        print(f"\nECHEC ({echecs} failures, {controles} checks)")
        return 1
    print(f"ALL PASS ({echecs} failures, {controles} checks)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--docs", type=Path, default=Path("docs"))
    ap.add_argument("--json", type=Path)
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()

    sweeps = charger(a.docs)
    if len(sweeps) < 2:
        print(f"il faut au moins deux balayages dans {a.docs}", file=sys.stderr)
        return 1
    profs = sorted(sweeps)
    # ⚠ On confronte les deux profondeurs qui portent le PLUS de traces communes, pas les
    # deux extremes : une profondeur qui n'a qu'une trace ne peut porter aucune mediane.
    meilleures = max(((x, y) for i, x in enumerate(profs) for y in profs[i + 1:]),
                     key=lambda xy: len(apparier(sweeps[xy[0]], sweeps[xy[1]])))
    d = confronter(sweeps, *meilleures)
    d["verdict"] = verdict(d)
    d["profondeurs_disponibles"] = {str(p): len(sweeps[p].get("lignes", [])) for p in profs}

    print(f"\n  profondeurs disponibles : "
          + ", ".join(f"{p} ({len(sweeps[p].get('lignes', []))} traces)" for p in profs))
    print(f"  confrontées : {d['profondeur_basse']} contre {d['profondeur_haute']} — "
          f"{d['traces_appariees']} traces communes")
    if d["plafonds_bas_um"] and len(d["plafonds_bas_um"]) > 1:
        print(f"  ⚠ la cohorte a {len(d['plafonds_bas_um'])} plafonds distincts en bas "
              f"({', '.join(f'{x:.2f}' for x in d['plafonds_bas_um'])} µm) — deux tailles "
              f"de voxel")
    for cote, nom in (("censure_bas", "en bas"), ("censure_haut", "en haut")):
        c = d[cote]
        if not c["coherente"]:
            print(f"  ⚠⚠ {c['censurees_ailleurs']} trace(s) marquées censurées {nom} ne "
                  f"sont PAS à leur plafond — le drapeau ne veut pas ce qu'on croit")
    print(f"  plafond du rendu : {d['plafond_bas_um']} µm contre {d['plafond_haut_um']} µm "
          f"(×{d.get('rapport_plafonds', float('nan')):.2f} pour "
          f"×{d.get('rapport_profondeurs', float('nan')):.2f} de profondeur)")
    print(f"  traces au plafond : {d['censurees_en_bas']}/{d['lignes_en_bas']} en bas, "
          f"{d['censurees_en_haut']}/{d['lignes_en_haut']} en haut")

    print(f"\n  {'critère':<14} {'comparées':>10} {'censurées':>10} "
          f"{'dérive méd.':>12} {'dérive max':>11}")
    print("  " + "-" * 62)
    for x in d["derives"]:
        med = "—" if x["derive_mediane"] is None else f"{x['derive_mediane']:.3f}"
        mx = "—" if x["derive_max"] is None else f"{x['derive_max']:.3f}"
        print(f"  {x['critere']:<14} {x['n_compare']:>10} {x['n_censurees']:>10} "
              f"{med:>12} {mx:>11}")

    if d.get("rho_au_bord_part_plates") is not None:
        print(f"\n  ρ(au_bord, part_plates) = {d['rho_au_bord_part_plates']:+.3f} — "
              f"⚠ deux grandeurs distinctes, la dérive de l'une ne se transporte pas sur "
              f"l'autre")

    ver = d["verdict"]
    print(f"\n  ⚠⚠ {ver['raison']}.")
    if not ver["seuil_absolu_defendable"]:
        print("      La question de N4 — « quelle référence ? » — n'est donc pas tranchée")
        print("      par un meilleur choix de référence : elle est DISSOUTE. Un critère")
        print("      doit être lu à DEUX profondeurs, comme l'exposant α, et il cesse")
        print("      alors d'avoir besoin d'une référence.")

    if a.json:
        a.json.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8")
        print(f"\n  écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
