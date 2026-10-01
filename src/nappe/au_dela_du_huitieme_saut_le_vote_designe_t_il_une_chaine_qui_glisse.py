"""Sur PHerc0358, au-delà du huitième saut, sur les graines 4 et 6, côté moins, le vote de 372 désigne-t-il une chaîne qui glisse, et à quel saut son glissement commence-t-il ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LE VOTE NE SOIT RELU SUR LES CHAÎNES À SEIZE SAUTS. Ce qui était vu avant d'écrire : tout ce que `296` à
`389` publient, dont `R4-F575` (à seize sauts, l'accord aux comptes de `m7` contredit 47 surfaces au-delà du huitième saut pour 8 qu'il
valide, sur les graines 4 et 6, côté moins, surtout) et les couples que `389` publie : sur la graine 4, côté moins, la suivie et la tierce
tiennent leurs comptes sur 74 paires de 75, la suivie et la compagne sur 64 de 76, la compagne et la tierce sur 71 de 81 ; sur la graine 6,
côté moins, la compagne et la tierce sur 77 de 80, la suivie et la compagne sur 66 de 82, la suivie et la tierce sur 58 de 74. ⚠ Cette
tranche ne lit pas `m7` : elle relit les paires et les comptes que `389` publie.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P187`. Une chaîne qui glisse se voit à ce qu'elle contredit les deux autres pendant que celles-ci
s'accordent ; savoir à quel saut le glissement commence dit où la chaîne a quitté sa feuille, et si la limite de `389` est celle d'une chaîne
ou celle de la méthode.

## Ce qui est fait

- **Les couples et le vote** : ceux de `372` et `373`, sur les paires et les comptes de `m7` de `389`, côté par côté.
- **Le début du glissement** : pour la chaîne que le vote désigne, la première paire qui contredit avec chacune des deux autres, dans l'ordre
  du plus petit saut de la chaîne désignée puis de l'autre ; le glissement commence au plus petit des deux sauts de la chaîne désignée.
- **La règle**, sur les graines 4 et 6, côté moins : si le vote désigne une chaîne sur les deux, **oui** ; sur une, **en partie** ; sur
  aucune, **non**.

## Les issues

L'issue de la tranche : **le vote désigne une chaîne sur n des deux côtés**, et à quel saut chacune commence à glisser, puis ce que dit la
règle.

## Rapporté à côté, qui ne décide rien

Le vote et le début du glissement sur les autres côtés où les chaînes vont au-delà du huitième saut ; si le glissement commence au-delà du
huitième saut.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : si la chaîne désignée a glissé plutôt que les deux autres ensemble, ni sur quelle feuille elle est
passée.

Usage :
    uv run python src/nappe/au_dela_du_huitieme_saut_le_vote_designe_t_il_une_chaine_qui_glisse.py --verifier
    uv run python src/nappe/au_dela_du_huitieme_saut_le_vote_designe_t_il_une_chaine_qui_glisse.py \\
        --json docs/mesures/au_dela_du_huitieme_saut_le_vote_designe_t_il_une_chaine_qui_glisse.json
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

import une_troisieme_chaine_dit_elle_laquelle_a_glisse_sur_pherc0358 as m372  # noqa: E402
import trois_chaines_aux_comptes_corriges_designent_elles_celle_qui_a_glisse as m373  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_389_A_PUBLIE = LES_MESURES / "laccord_aux_comptes_de_m7_valide_t_il_encore_a_seize_sauts_sur_pherc0358.json"
LES_COTES = ((4, "moins"), (6, "moins"))
LES_HUIT = 8


def les_paires(brutes: list) -> list[dict]:
    return [{"le_saut_suivi": h, "le_saut_compagnon": k, "meme_feuille": m} for h, k, m in brutes]


def les_couples(paires: dict, comptes: dict) -> dict:
    sa = lambda cs: [{"le_compte_corrige": w} for w in cs]  # noqa: E731
    return {k: m373.le_couple(p, sa(comptes[k.split("|")[0]]), sa(comptes[k.split("|")[1]])) for k, p in paires.items()}


def le_debut(paires: dict, comptes: dict, x: str) -> dict:
    """Pour la chaîne `x`, la première paire qui contredit avec chacune des deux autres, dans l'ordre du saut de `x` puis de l'autre, et le
    plus petit saut de `x` où l'une d'elles tombe ; None sans contradiction."""
    out = {}
    for k, ps in paires.items():
        a, b = k.split("|")
        if x not in (a, b):
            continue
        y = b if a == x else a
        cand = []
        for p in ps:
            hx, hy = (p["le_saut_suivi"], p["le_saut_compagnon"]) if a == x else (p["le_saut_compagnon"], p["le_saut_suivi"])
            if p["meme_feuille"] != (comptes[x][hx - 1] == comptes[y][hy - 1]):
                cand.append((hx, hy))
        out[y] = min(cand) if cand else None
    sauts = [v[0] for v in out.values() if v is not None]
    return {"les_premieres": out, "le_saut": min(sauts) if sauts else None}


def par_saut(paires: dict, comptes: dict, x: str) -> dict:
    """Pour chaque saut de la chaîne `x`, ses paires avec les deux autres qui contredisent les comptes, et toutes ses paires."""
    out = {}
    for k, ps in paires.items():
        a, b = k.split("|")
        if x not in (a, b):
            continue
        y = b if a == x else a
        for p in ps:
            hx, hy = (p["le_saut_suivi"], p["le_saut_compagnon"]) if a == x else (p["le_saut_compagnon"], p["le_saut_suivi"])
            n = out.setdefault(hx, [0, 0])
            n[0] += int(p["meme_feuille"] != (comptes[x][hx - 1] == comptes[y][hy - 1]))
            n[1] += 1
    return {h: out[h] for h in sorted(out)}


def le_cote(c: dict) -> dict:
    paires = {k: les_paires(v) for k, v in c["les_paires"].items()}
    couples = les_couples(paires, c["les_comptes"])
    vote = m372.le_vote(couples)
    debut = le_debut(paires, c["les_comptes"], vote) if vote else None
    return {"le_rang": c["le_rang"], "le_cote": c["le_cote"], "les_couples": couples, "le_vote": vote, "le_debut": debut,
            "au_dela_du_huitieme": None if not debut or debut["le_saut"] is None else debut["le_saut"] > LES_HUIT,
            "par_saut": par_saut(paires, c["les_comptes"], vote) if vote else None}


def le_verdict(d: dict) -> dict:
    vus = [c for c in d["les_cotes"] if (c["le_rang"], c["le_cote"]) in LES_COTES]
    n = sum(c["le_vote"] is not None for c in vus)
    tete = f"au-delà du huitième saut, le vote désigne une chaîne sur {n} des {len(vus)} côtés"
    for c in vus:
        if c["le_vote"]:
            tete += f", la {c['le_vote']} de la graine {c['le_rang']}, côté {c['le_cote']}, à partir de son saut {c['le_debut']['le_saut']}"
    suite = "oui, une chaîne glisse" if n == len(vus) else "en partie" if n else "non"
    return {"decidable": True, "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    d389 = json.loads(CE_QUE_389_A_PUBLIE.read_text())
    cotes = [le_cote(c) for c in d389["les_cotes"] if any(len(v) > LES_HUIT for v in c["les_comptes"].values())]
    d = {"la_question": __doc__.splitlines()[0], "les_cotes": cotes}
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

    paires = {"suivie|compagne": les_paires([[h, h, True] for h in range(1, 11)]),
              "suivie|tierce": les_paires([[h, h, True] for h in range(1, 11)]),
              "compagne|tierce": les_paires([[h, h, True] for h in range(1, 11)])}
    bon = list(range(1, 11))
    glisse = [1, 2, 3, 4, 5, 6, 7, 9, 10, 11]
    comptes = {"suivie": bon, "compagne": glisse, "tierce": bon}
    c = le_cote({"le_rang": 4, "le_cote": "moins", "les_paires": {k: [[p["le_saut_suivi"], p["le_saut_compagnon"], p["meme_feuille"]] for p in v]
                                                                     for k, v in paires.items()}, "les_comptes": comptes})
    v("★★★★ le vote désigne la chaîne qui contredit les deux autres", c["le_vote"] == "compagne", str(c["le_vote"]))
    v("★★★★ le début : le premier saut de la chaîne désignée qui contredit, avec chacune des deux autres",
      c["le_debut"] == {"les_premieres": {"suivie": (8, 8), "tierce": (8, 8)}, "le_saut": 8} and c["au_dela_du_huitieme"] is False, str(c["le_debut"]))
    d2 = le_debut({"compagne|tierce": les_paires([[3, 9, True], [9, 9, True]])}, {"compagne": [1] * 9, "tierce": [2] * 9}, "tierce")
    v("★★★★ dans une paire où la chaîne est la seconde, ses sauts sont lus du bon côté", d2["les_premieres"] == {"compagne": (9, 3)}, str(d2))
    d3 = le_debut({"suivie|compagne": les_paires([[5, 5, True], [6, 6, True]]), "suivie|tierce": les_paires([[8, 8, True]])},
                  {"suivie": [1, 2, 3, 4, 6, 7, 8, 9], "compagne": [1, 2, 3, 4, 5, 6, 7, 8], "tierce": [1, 2, 3, 4, 5, 6, 7, 8]}, "suivie")
    v("★★★★ le début est le plus petit des deux premiers sauts", d3["le_saut"] == 5 and d3["les_premieres"] == {"compagne": (5, 5), "tierce": (8, 8)},
      str(d3))
    d4 = le_debut({"suivie|compagne": les_paires([[2, 2, False]])}, {"suivie": [1, 2], "compagne": [1, 2]}, "suivie")
    v("★★★★ une autre feuille au même compte contredit aussi", d4["le_saut"] == 2, str(d4))
    v("★★★★ par saut : les paires de la chaîne qui contredisent, et toutes ses paires",
      lambda: c["par_saut"][8] == [2, 2] and c["par_saut"][7] == [0, 2] and len(c["par_saut"]) == 10)
    v("★★★ sans contradiction, pas de début", le_debut(paires, {x: bon for x in ("suivie", "compagne", "tierce")}, "suivie")["le_saut"] is None)
    vus = lambda a, b: {"les_cotes": [{"le_rang": 4, "le_cote": "moins", "le_vote": a, "le_debut": {"le_saut": 9}},  # noqa: E731
                                      {"le_rang": 6, "le_cote": "moins", "le_vote": b, "le_debut": {"le_saut": 10}},
                                      {"le_rang": 7, "le_cote": "plus", "le_vote": "suivie", "le_debut": {"le_saut": 2}}]}
    v("★★★★ la règle : sur les deux côtés, oui ; sur un, en partie ; sur aucun, non ; les autres côtés ne comptent pas",
      le_verdict(vus("compagne", "suivie"))["lissue"].endswith("une chaîne glisse") and le_verdict(vus("compagne", None))["lissue"].endswith("en partie")
      and le_verdict(vus(None, None))["lissue"].endswith("; non")
      and "la compagne de la graine 4, côté moins, à partir de son saut 9" in le_verdict(vus("compagne", "suivie"))["lissue"])

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
