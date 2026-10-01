"""Sur la graine 4, côté plus, de PHerc0358, la suivie que le vote désigne tient-elle les comptes avec les deux autres chaînes si son premier saut, à 1,40 pas, est compté double comme les leurs, à 1,67 et 1,76 pas ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LE PREMIER SAUT DE LA SUIVIE NE SOIT RECOMPTÉ. Ce qui était vu avant d'écrire : tout ce que `296` à
`380` publient, dont `R4-F566` (sur la graine 4, côté plus, la compagne et la tierce tiennent leurs comptes entre elles, 27 paires sur
27 ; la suivie, dont le premier saut fait 1,40 pas et compte 1, les tient avec la compagne sur 14 paires de 27 et avec la tierce sur 11
de 24 ; le vote la désigne, et rien n'est validé). ⚠ Cette tranche ne lit pas `m7` : elle relit les paires et les sauts que `380` publie.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P178`. Une chaîne que le vote désigne est rejetée. Si la suivie de la graine 4, côté plus,
n'a pas glissé, mais compte un tour de moins parce que son premier saut est tombé sous le seuil du double, l'accord peut corriger son
compte au lieu de la rejeter.

## Ce qui est fait

- **Le recompte** : le premier saut de la suivie compté double, ses autres sauts inchangés ; ses comptes corrigés en sont relevés d'un tour.
  Rien d'autre ne change : ni les paires, ni ce que « même feuille » y dit, ni les sauts des deux autres chaînes.
- **Les couples, le vote et les statuts** : ceux de `372`, `373` et `374`, lus comme `380` les lit.
- **Le contrôle** : sur chaque côté de `380` où les trois couples tiennent, décaler d'un tour les comptes de la suivie, en changeant le
  genre de son premier saut (simple en double, double en simple, nul en simple), doit défaire ses deux couples. Sans quoi un couple tiendrait
  à un tour près, et le recompte ne prouverait rien.
- **La règle** : si, après le recompte, les deux couples de la suivie tiennent, **oui, seul le seuil du saut double la séparait des deux
  autres** ; si aucun ne tient, **non** ; sinon, **en partie**. Indécidable si la relecture ne redonne pas les statuts de `380` sur la graine
  4, côté plus, ou si le contrôle échoue.

## Les issues

L'issue de la tranche : **après le recompte, la suivie tient les comptes avec la compagne sur a paires de n et avec la tierce sur b de m**,
puis ce que dit la règle.

## Rapporté à côté, qui ne décide rien

Les surfaces validées après le recompte, le plus grand compte validé, le vote.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : si le premier saut de la suivie a réellement franchi deux feuilles. Elle dit seulement si un compte
relevé d'un tour fait tenir les paires ; ce qu'il y a entre la nappe et la première surface, seul `m7` le dirait.

Usage :
    uv run python src/nappe/la_suivie_de_la_graine_4_tient_elle_les_comptes_si_son_premier_saut_est_compte_double.py --verifier
    uv run python src/nappe/la_suivie_de_la_graine_4_tient_elle_les_comptes_si_son_premier_saut_est_compte_double.py \\
        --json docs/mesures/la_suivie_de_la_graine_4_tient_elle_les_comptes_si_son_premier_saut_est_compte_double.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))
sys.path.insert(0, str(RACINE / "src" / "tracecheck"))

import le_glissement_se_voit_il_dans_la_chaine_seule as m369  # noqa: E402
import quelles_surfaces_laccord_de_trois_chaines_valide_t_il_sur_pherc0358 as m374  # noqa: E402
import laccord_de_trois_chaines_valide_t_il_sur_les_cotes_que_324_na_pas_retenus as m380  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_380_A_PUBLIE = LES_MESURES / "laccord_de_trois_chaines_valide_t_il_sur_les_cotes_que_324_na_pas_retenus.json"
LE_COTE = (4, "plus")
SUIVIE, COMPAGNE, TIERCE = m374.SUIVIE, m374.COMPAGNE, m374.TIERCE
LE_DECALAGE = {m369.SIMPLE: m369.DOUBLE, m369.DOUBLE: m369.SIMPLE, m369.NUL: m369.SIMPLE}


def recompter(sauts: list[dict], h: int, genre: str) -> list[dict]:
    """Les sauts d'une chaîne, le saut `h` compté comme `genre`, les comptes corrigés recalculés depuis la nappe de départ."""
    out, w = [], 0
    for s in sauts:
        g = genre if s["le_saut"] == h else s["le_genre"]
        w += m369.LES_PAS[g]
        out.append({**s, "le_genre": g, "le_compte_corrige": w})
    return out


def relire(c: dict, sauts: dict | None = None) -> dict:
    """Le côté publié par `380`, relu comme `380` le lit, avec ses sauts ou ceux qu'on lui donne."""
    return m380.le_cote(c["le_rang"], c["le_cote"], c["les_paires"], sauts or c["les_sauts"])


def decaler_la_suivie(c: dict) -> dict:
    """Le côté relu, les comptes de la suivie décalés d'un tour par le genre de son premier saut."""
    s = c["les_sauts"][SUIVIE]
    return relire(c, {**c["les_sauts"], SUIVIE: recompter(s, 1, LE_DECALAGE[s[0]["le_genre"]])})


def les_couples_de_la_suivie(cote: dict) -> dict:
    return {k: cote["les_couples"][k] for k in (f"{SUIVIE}|{COMPAGNE}", f"{SUIVIE}|{TIERCE}")}


def redonne(relu: dict, publie: dict) -> bool:
    """Le côté relu a les statuts, les comptes et les couples que `380` publie."""
    return bool(m380.les_statuts(relu) == m380.les_statuts(publie) and relu["les_couples"] == publie["les_couples"])


def le_controle(cotes: list[dict]) -> dict:
    """Sur chaque côté où les trois couples tiennent, ce que deviennent les couples de la suivie quand ses comptes sont décalés d'un tour."""
    out = {}
    for c in cotes:
        if all(v["tient"] for v in relire(c)["les_couples"].values()):
            out[f"{c['le_rang']} {c['le_cote']}"] = {k: v["tient"] for k, v in les_couples_de_la_suivie(decaler_la_suivie(c)).items()}
    return out


def le_verdict(d: dict) -> dict:
    if not d.get("redonne_380"):
        return {"decidable": False, "lissue": "indécidable : la relecture ne redonne pas les statuts de 380 sur la graine 4, côté plus"}
    ctl = d["le_controle"]
    if not ctl or any(any(v.values()) for v in ctl.values()):
        return {"decidable": False, "lissue": "indécidable : un décalage d'un tour ne défait pas les couples de la suivie partout"}
    sc, st = (d["apres"]["les_couples"][k] for k in (f"{SUIVIE}|{COMPAGNE}", f"{SUIVIE}|{TIERCE}"))
    tete = (f"après le recompte, la suivie tient les comptes avec la compagne sur {sc['tiennent']} paires de {sc['les_paires']} et avec "
            f"la tierce sur {st['tiennent']} de {st['les_paires']}")
    n = sc["tient"] + st["tient"]
    suite = "oui, seul le seuil du saut double la séparait des deux autres" if n == 2 else "non" if n == 0 else "en partie"
    return {"decidable": True, "lissue": f"{tete} ; {suite}"}


def le_resume(cote: dict) -> dict:
    validees = [s for s in cote["les_surfaces"] if s["le_statut"] == m374.VALIDEE]
    return {"les_couples": cote["les_couples"], "le_vote": cote["le_vote"], "validees": len(validees),
            "le_plus_loin": max((s["le_compte"] for s in validees), default=None),
            "par_statut": {k: sum(s["le_statut"] == k for s in cote["les_surfaces"])
                           for k in (m374.VALIDEE, m374.EN_PARTIE, m374.CONTREDITE, m374.SEULE)},
            "les_surfaces": cote["les_surfaces"]}


def mesurer() -> dict:
    d380 = json.loads(CE_QUE_380_A_PUBLIE.read_text())
    c = next(x for x in d380["les_cotes"] if (x["le_rang"], x["le_cote"]) == LE_COTE)
    avant = relire(c)
    s = c["les_sauts"][SUIVIE]
    apres = relire(c, {**c["les_sauts"], SUIVIE: recompter(s, 1, m369.DOUBLE)})
    d = {"la_question": __doc__.splitlines()[0], "le_cote": list(LE_COTE),
         "le_premier_saut_de_la_suivie": {"lecart_median": s[0]["lecart_median"], "le_genre": s[0]["le_genre"],
                                          "en_pas": round(s[0]["lecart_median"] / m369.LE_PAS, 3)},
         "redonne_380": redonne(avant, c),
         "avant": le_resume(avant), "apres": le_resume(apres), "le_controle": le_controle(d380["les_cotes"])}
    d["le_verdict"] = le_verdict(d)
    return d


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

    sa = lambda *gs: [{"le_saut": h, "le_genre": g, "le_compte_corrige": 0} for h, g in enumerate(gs, 1)]  # noqa: E731
    r = recompter(sa(m369.SIMPLE, m369.SIMPLE, m369.NUL, m369.SIMPLE), 1, m369.DOUBLE)
    v("★★★★ le recompte : le premier saut compté double relève tous les comptes d'un tour",
      [x["le_compte_corrige"] for x in r] == [2, 3, 3, 4] and r[0]["le_genre"] == m369.DOUBLE and r[2]["le_genre"] == m369.NUL, str(r))
    v("★★★★ le recompte ne touche que le saut nommé",
      [x["le_compte_corrige"] for x in recompter(sa(m369.DOUBLE, m369.SIMPLE), 2, m369.NUL)] == [2, 2])
    v("★★★★ le décalage d'un tour : simple en double, double en simple, nul en simple",
      LE_DECALAGE == {m369.SIMPLE: m369.DOUBLE, m369.DOUBLE: m369.SIMPLE, m369.NUL: m369.SIMPLE}
      and all(abs(m369.LES_PAS[b] - m369.LES_PAS[a]) == 1 for a, b in LE_DECALAGE.items()))

    p = lambda h, k, m: {"le_saut_suivi": h, "le_saut_compagnon": k, "meme_feuille": m}  # noqa: E731
    sc = lambda *ws: [{"le_saut": h, "le_genre": g, "le_compte_corrige": w} for h, (g, w) in enumerate(ws, 1)]  # noqa: E731
    paires = {f"{SUIVIE}|{COMPAGNE}": [p(h, h, True) for h in range(1, 6)], f"{SUIVIE}|{TIERCE}": [p(h, h, True) for h in range(1, 6)],
              f"{COMPAGNE}|{TIERCE}": [p(h, h, True) for h in range(1, 6)]}
    deux = [(m369.DOUBLE, 2)] + [(m369.SIMPLE, w) for w in range(3, 7)]
    un = [(m369.SIMPLE, 1)] + [(m369.SIMPLE, w) for w in range(2, 6)]
    c_ = {"le_rang": 4, "le_cote": "plus", "les_paires": paires, "les_sauts": {SUIVIE: sc(*un), COMPAGNE: sc(*deux), TIERCE: sc(*deux)}}
    av = relire(c_)
    ap = relire(c_, {**c_["les_sauts"], SUIVIE: recompter(c_["les_sauts"][SUIVIE], 1, m369.DOUBLE)})
    v("★★★★ une suivie qui compte un tour de moins est désignée ; recomptée, ses deux couples tiennent",
      av["le_vote"] == SUIVIE and not any(x["tient"] for x in les_couples_de_la_suivie(av).values())
      and all(x["tient"] for x in les_couples_de_la_suivie(ap).values()) and ap["le_vote"] is None)
    v("★★★★ la relecture : statuts, comptes et couples comparés à ceux que 380 publie",
      lambda: redonne(av, av) and not redonne(av, {**av, "les_couples": ap["les_couples"]})
      and not redonne(av, {**av, "les_surfaces": [{**x, "le_compte": x["le_compte"] + 1} for x in av["les_surfaces"]]})
      and not redonne(av, {**av, "les_surfaces": [{**x, "le_statut": m374.SEULE} for x in av["les_surfaces"]]}))
    ok3 = {**c_, "les_sauts": {SUIVIE: sc(*deux), COMPAGNE: sc(*deux), TIERCE: sc(*deux)}}
    v("★★★★ le contrôle : décaler d'un tour une suivie qui tenait défait ses deux couples ; un côté qui ne tient pas n'est pas contrôlé",
      lambda: le_controle([ok3, c_]) == {"4 plus": {f"{SUIVIE}|{COMPAGNE}": False, f"{SUIVIE}|{TIERCE}": False}})

    def d_(a, b, ok=True, ctl=None):
        cp = lambda t: {"tiennent": t, "les_paires": 10, "tient": t >= 9}  # noqa: E731
        return {"redonne_380": ok, "le_controle": {"6 moins": {"x": False}} if ctl is None else ctl,
                "apres": {"les_couples": {f"{SUIVIE}|{COMPAGNE}": cp(a), f"{SUIVIE}|{TIERCE}": cp(b)}}}
    v("★★★★ la règle : les deux couples tiennent, oui ; aucun, non ; un, en partie",
      le_verdict(d_(10, 9))["lissue"].endswith("la séparait des deux autres") and le_verdict(d_(3, 2))["lissue"].endswith("; non")
      and le_verdict(d_(10, 2))["lissue"].endswith("; en partie") and "sur 10 paires de 10 et avec la tierce sur 9 de 10" in le_verdict(d_(10, 9))["lissue"])
    v("★★★ indécidable sans la relecture de 380, ou si le contrôle échoue ou ne s'applique pas",
      not le_verdict(d_(10, 10, ok=False))["decidable"] and not le_verdict(d_(10, 10, ctl={"6 moins": {"x": True}}))["decidable"]
      and not le_verdict(d_(10, 10, ctl={}))["decidable"] and le_verdict(d_(10, 10))["decidable"])

    for e_ in echecs:
        print(f"  ÉCHEC {e_}")
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
    d = mesurer()
    texte = json.dumps(d, ensure_ascii=False, indent=1)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(texte + "\n")
    print(json.dumps(d["le_verdict"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
