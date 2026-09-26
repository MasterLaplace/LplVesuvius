"""Les gains nets publiés de `275` à `289` se distinguent-ils du hasard ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT CE CALCUL. Ce qui était vu avant d'écrire : les comptes que `275` à `289` publient. Depuis `281`,
presque chaque tranche écrit dans « ce qu'elle ne dit pas » qu'elle ne sait pas si son gain net se distingue de zéro : les
modules comparaient deux comptes, sans seuil. Au deuxième saut de la bande, la procédure rend 23 ratés justes pour 9 justes
ratés (`283`), et les tranches suivantes ne font plus bouger que quelques points.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P95`. Chercher ce qui remplace l'humain sur des écarts de l'ordre de dix points n'a
de sens que si ces écarts ne sont pas du bruit. Le test est choisi avant de le calculer, et il ne se règle pas.

## Le test, déclaré avant le calcul

- Un point qu'une correction fait changer de camp est soit un raté rendu juste, soit un juste rendu raté. Si la correction
  n'en savait rien, les deux seraient également probables : le test du signe, binomial exact à une chance sur deux, bilatéral,
  la queue la plus petite doublée.
- Les points d'un même bloc ne sont pas indépendants : un bloc a une ancre et un mélange. Là où les blocs sont publiés, le même
  test est fait sur les blocs qui montent contre ceux qui descendent. C'est le test qui compte.
- Le seuil est 0,05. Il est conventionnel et fixé ici.

Les tranches testées, et rien d'autre :
- les procédures par blocs : `275` et `280` sur le segment `20230702185753`, `281` et `283` sur la bande ;
- les reprises, sur les points seuls : `276` et `279` au deuxième saut du segment ; `284`, `285`, `287` et `288` au troisième
  saut de la bande ; `289` au deuxième.

## Les issues, exclusives, sur le deuxième saut de la bande

- bloc par bloc, le test du signe de `283` passe sous 0,05 : la procédure corrige le deuxième saut de la bande au-delà du hasard ;
- il n'y passe pas : son gain ne se distingue pas du hasard.

⚠ Rapporté à côté : chaque tranche testée, sur les points et, quand ils existent, sur les blocs.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : si une correction vaut quelque chose au-delà des points notés ; l'effet de la
dépendance entre points à l'intérieur d'un bloc au-delà de ce que le test par blocs en retire.

Usage :
    uv run python src/nappe/les_gains_publies_se_distinguent_ils_du_hasard.py --verifier
    uv run python src/nappe/les_gains_publies_se_distinguent_ils_du_hasard.py \\
        --json docs/mesures/les_gains_publies_se_distinguent_ils_du_hasard.json
"""
from __future__ import annotations

import argparse
import json
from math import comb
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
LES_MESURES = RACINE / "docs" / "mesures"
LE_SEUIL = 0.05

# (la tranche, ce qu'elle mesure, le fichier, le chemin des comptes, les blocs publiés ou non)
LES_TRANCHES = (
    ("275", "segment, premier saut, procédure", "la_procedure_sans_juge_tient_elle_sur_le_segment_entier.json",
     ("les_reunis",), True),
    ("280", "segment, deuxième saut, procédure", "la_procedure_sans_juge_corrige_t_elle_le_deuxieme_saut.json",
     ("les_reunis",), True),
    ("281", "bande, premier saut, procédure", "la_procedure_sans_juge_tient_elle_sur_la_bande.json", ("les_reunis",), True),
    ("283", "bande, deuxième saut, procédure", "la_procedure_sans_juge_corrige_t_elle_le_deuxieme_saut_de_la_bande.json",
     ("les_reunis",), True),
    ("276", "segment, deuxième saut, repris de la spire corrigée",
     "repartir_de_la_spire_corrigee_rend_il_le_saut_suivant_plus_juste.json", ("les_sauts", 1), False),
    ("279", "segment, deuxième saut, repris de la spire recalée",
     "recaler_la_spire_corrigee_sur_la_feuille_rend_il_le_deuxieme_saut_plus_juste.json", ("les_sauts", 1), False),
    ("284", "bande, troisième saut, recalé sur le rayon de la bande",
     "repartir_du_deuxieme_saut_corrige_rend_il_le_troisieme_saut_de_la_bande_plus_juste.json", ("les_sauts", 0), False),
    ("285", "bande, troisième saut, recalé sur son rayon",
     "recaler_le_deuxieme_saut_sur_son_rayon_rend_il_le_troisieme_saut_plus_juste.json", ("les_sauts", 0), False),
    ("287", "bande, troisième saut, normales du témoin",
     "les_normales_recalculees_portent_elles_la_perte_du_troisieme_saut.json", ("les_sauts", 0), False),
    ("288", "bande, troisième saut, sans voter pour les voisins",
     "une_reprise_qui_ne_derange_pas_les_voisins_rend_elle_le_troisieme_saut_plus_juste.json", ("les_sauts", 0), False),
    ("289", "bande, deuxième saut, la feuille que l'écart désigne",
     "ramener_sur_la_feuille_que_lecart_designe_corrige_t_il_le_deuxieme_saut_de_la_bande.json",
     ("les_blocs_notes_reunis",), False),
)


def le_test_du_signe(pour: int, contre: int) -> float:
    """La probabilité bilatérale, sous une chance sur deux, d'un écart au moins aussi grand : la queue la plus petite, doublée."""
    n = pour + contre
    if n == 0:
        return 1.0
    k = min(pour, contre)
    queue = sum(comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * queue)


def trois_chiffres(x: float) -> float:
    """Trois chiffres significatifs : une probabilité de 1e-18 ne s'arrondit pas à zéro."""
    return float(f"{x:.3g}")


def une_tranche(tranche: str, quoi: str, fichier: str, chemin: tuple, blocs: bool, racine: Path = LES_MESURES) -> dict:
    d = json.loads((racine / fichier).read_text())
    x = d
    for c in chemin:
        x = x[c]
    pour, contre = x["les_rates_rendus_justes"], x["les_justes_rendus_rates"]
    r = {"la_tranche": tranche, "ce_quelle_mesure": quoi, "sur_les_points": {
        "les_rates_rendus_justes": pour, "les_justes_rendus_rates": contre, "le_gain_net": pour - contre,
        "la_probabilite": trois_chiffres(le_test_du_signe(pour, contre))}}
    if blocs:
        m, dsc = x["les_blocs_qui_montent"], x["les_blocs_qui_descendent"]
        r["sur_les_blocs"] = {"les_blocs_qui_montent": m, "les_blocs_qui_descendent": dsc,
                              "la_probabilite": trois_chiffres(le_test_du_signe(m, dsc))}
    for k in ("sur_les_points", "sur_les_blocs"):
        if k in r:
            r[k]["sous_le_seuil"] = r[k]["la_probabilite"] < LE_SEUIL
    return r


def le_verdict(r: dict) -> dict:
    b = next(t for t in r["les_tranches"] if t["la_tranche"] == "283")["sur_les_blocs"]
    if b["sous_le_seuil"]:
        return {"lissue": "la procédure corrige le deuxième saut de la bande au-delà du hasard"}
    return {"lissue": "le gain de la procédure au deuxième saut de la bande ne se distingue pas du hasard"}


def mesurer() -> dict:
    out = {"le_seuil": LE_SEUIL, "les_tranches": [une_tranche(*t) for t in LES_TRANCHES]}
    out["le_verdict"] = le_verdict(out)
    return out


def verifier() -> int:
    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        try:
            res = ok() if callable(ok) else ok
        except Exception as exc:  # noqa: BLE001
            echecs.append(f"{nom} — LEVÉE {type(exc).__name__}: {exc}")
            return
        if not res:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    v("★★★★ dix pour zéro : deux fois un sur mille vingt-quatre", abs(le_test_du_signe(10, 0) - 2 / 1024) < 1e-12)
    v("★★★★ le test est symétrique", le_test_du_signe(7, 4) == le_test_du_signe(4, 7))
    v("★★★ autant pour que contre, ou rien, vaut un", le_test_du_signe(6, 6) == 1.0 and le_test_du_signe(0, 0) == 1.0)
    v("★★★ un contre zéro vaut un, la queue doublée plafonnée", le_test_du_signe(1, 0) == 1.0)
    v("★★★★ sept contre quatre : deux fois la queue de quatre sur onze",
      abs(le_test_du_signe(7, 4) - 2 * sum(comb(11, i) for i in range(5)) / 2 ** 11) < 1e-12)
    v("★★★★ le seuil est conventionnel, et fixé", LE_SEUIL == 0.05)
    v("★★★ une très petite probabilité ne s'arrondit pas à zéro", trois_chiffres(le_test_du_signe(163, 41)) > 0)
    r_ = lambda s: {"les_tranches": [{"la_tranche": "283", "sur_les_blocs": {"sous_le_seuil": s}}]}  # noqa: E731
    v("★★★★ les issues : au-delà du hasard si les blocs de 283 passent sous le seuil, sinon non",
      "au-delà" in le_verdict(r_(True))["lissue"] and "ne se distingue pas" in le_verdict(r_(False))["lissue"])
    v("★★★ toutes les tranches déclarées se lisent", lambda: len(mesurer()["les_tranches"]) == len(LES_TRANCHES))

    for x in echecs:
        print(f"  ÉCHEC {x}")
    print(f"{Path(__file__).name}   {'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer()
    texte = json.dumps(r, ensure_ascii=False, indent=1)
    print(texte)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(texte + "\n")
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
