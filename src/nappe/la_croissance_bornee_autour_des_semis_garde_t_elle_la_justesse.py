"""Une relance depuis la spire dont la croissance ne s'éloigne pas de plus de deux mailles de ses semis garde-t-elle la justesse de la chaîne sans relance sans perdre la surface ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UNE SEULE NAPPE BORNÉE NE SOIT RELANCÉE. Ce qui était vu avant d'écrire : tout ce que `296` à `334`
publient, dont `R4-F519` (relancée depuis sa spire, la chaîne descend six tours publiés en médiane et fait trois sauts faux, tous au
septième saut, contre un sans relance ; sur PHerc0358 elle tient 4 sauts en médiane) et `R4-F520` (à deux de ces trois sauts faux, la spire
n'est sur aucun tour, et c'est la croissance hors des semis qui retrouve un tour publié).

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P131`. Si c'est la croissance loin des semis qui va se poser sur un tour publié quand la spire
se perd, une croissance qui ne s'éloigne pas des semis ne le peut plus ; elle rend moins de surface à chaque relance, et la chaîne peut
rétrécir comme sans relance.

## Ce qui est fait

- **La chaîne** : celle de `333` sur les deux rouleaux, sans rien y changer, sauf la croissance de chaque relance.
- **La croissance bornée** : celle de `305`, partie des mailles semées depuis la spire, qui ne pose rien à plus de deux mailles d'une
  maille semée, en comptant les diagonales. Deux mailles font 20 voxels du plan, un pas de PHerc0358 et un peu plus d'un pas du niveau 2 de
  PHercParis4.
- **Ce qui est jugé** : comme `333`, la descente de `330` sur `5753_0` à `5753_-7` pour PHercParis4, et la tenue de `328` pour PHerc0358.

## Les issues

L'issue de la tranche : **relancée depuis sa spire et bornée à deux mailles, la chaîne descend h tours publiés en médiane sur
PHercParis4 et se trompe f fois, contre 6 et 1 sans relance, et tient h0 sauts en médiane sur PHerc0358, contre 1** ; et, déclaré avant,
la règle de `333` : **elle garde la justesse et rend la surface** si h ≥ 6, f ≤ 1 et h0 > 1 ; **elle perd la justesse** si h < 6 ou
f > 1 ; **elle garde la justesse sans rendre la surface** sinon.

## Rapporté à côté, qui ne décide rien

La part du plan posée par chaque nappe relancée, à comparer à celle de `333`.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : ce que ferait une autre marge ; ni sur quelle feuille tombent les nappes de PHerc0358.

Usage :
    uv run python src/nappe/la_croissance_bornee_autour_des_semis_garde_t_elle_la_justesse.py --verifier
    uv run python src/nappe/la_croissance_bornee_autour_des_semis_garde_t_elle_la_justesse.py \\
        --json docs/mesures/la_croissance_bornee_autour_des_semis_garde_t_elle_la_justesse.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))
sys.path.insert(0, str(RACINE / "src" / "tracecheck"))

import une_nappe_tiree_de_m7_suit_elle_sa_feuille as m300  # noqa: E402
import une_nappe_qui_refuse_de_changer_de_feuille_suit_elle_encore_sa_feuille as m305  # noqa: E402
import une_chaine_relancee_a_chaque_tour_descend_elle_plus_loin as m331  # noqa: E402
import la_relance_partie_de_la_spire_entiere_garde_t_elle_la_justesse as m333  # noqa: E402

LA_MARGE = 2                       # mailles du plan, soit 20 voxels


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    gs = d["les_graines"]["PHercParis4"]
    p4 = [g["la_descente"] for g in gs if g["le_tour_touche"]]
    p0 = [c["tient"] for c in d["les_cotes"]["PHerc0358"]]
    if not p4 or not p0:
        return {"decidable": False, "lissue": "indécidable : rien à comparer"}
    h, h0, f = float(np.median(p4)), float(np.median(p0)), m333.les_sauts_faux(gs)
    f_ = lambda x, un, plusieurs: f"{x:g}".replace(".", ",") + (f" {un}" if x <= 1 else f" {plusieurs}")  # noqa: E731
    tete = (f"relancée depuis sa spire et bornée à {LA_MARGE} mailles, la chaîne descend {f_(h, 'tour publié', 'tours publiés')} en "
            f"médiane sur PHercParis4 et se trompe {f} fois, contre 6 et 1 sans relance, et tient {f_(h0, 'saut', 'sauts')} en médiane "
            f"sur PHerc0358, contre 1")
    if h < m333.LA_DESCENTE_SANS_RELANCE or f > m333.LES_SAUTS_FAUX_SANS_RELANCE:
        suite = "elle perd la justesse"
    elif h0 > m333.LA_TENUE_SANS_RELANCE:
        suite = "elle garde la justesse et rend la surface"
    else:
        suite = "elle garde la justesse sans rendre la surface"
    return {"decidable": True, "h": h, "h0": h0, "f": f, "lissue": f"{tete} ; {suite}"}


def la_relance_de_paris4(lv):
    return lambda p_, n_, s_, o_: m333.la_nappe_de_la_spire_de_paris4(s_, o_, p_, n_, lv, marge=LA_MARGE)


def la_relance_de_0358(lv):
    return lambda p_, n_, s_, o_: m333.la_nappe_de_la_spire(s_, o_, tuple(p_), tuple(n_), lv, marge=LA_MARGE)


def mesurer() -> dict:
    t0 = time.monotonic()
    d = m331.mesurer(relancer4=la_relance_de_paris4, relancer0=la_relance_de_0358, avec_la_spire=True)
    d["la_question"] = __doc__.splitlines()[0]
    d["les_constantes"]["la_marge_en_mailles"] = LA_MARGE
    d["le_verdict"] = le_verdict(d)
    d["les_secondes"] = round(time.monotonic() - t0, 1)
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

    un = np.zeros((9, 9), dtype=bool)
    un[4, 4] = True
    v("★★★★ deux mailles autour d'une maille semée : le carré de cinq, diagonales comprises",
      np.array_equal(m333.les_mailles_permises(un, 2), np.pad(np.ones((5, 5), dtype=bool), 2)))
    v("★★★★ une marge nulle ne permet que les semis, pas toute la grille", np.array_equal(m333.les_mailles_permises(un, 0), un))
    v("★★★ sans semis, rien n'est permis", not m333.les_mailles_permises(np.zeros((9, 9), dtype=bool), 2).any())

    haut = np.array([0.0, 0.0, 1.0])
    graine = (500.0, 300.0, 132.0)
    g2, _ = m300.le_plan(graine, haut)
    plate = lambda idx: (np.abs(idx[..., 0] - 132) <= 1).astype(float)  # noqa: E731
    petite = np.zeros(g2.shape[:2], dtype=bool)
    petite[30:35, 30:35] = True
    b = m333.la_nappe_de_la_spire(g2, petite, graine, haut, plate, marge=LA_MARGE)
    libre = m333.la_nappe_de_la_spire(g2, petite, graine, haut, plate)
    v("★★★★★ sur une feuille plate, la nappe bornée pose les semis et deux mailles autour, pas davantage",
      b["valide"].sum() == 81 and b["valide"][28:37, 28:37].all() and libre["valide"].sum() > 1000, str(b["valide"].sum()))

    def deux_feuilles(idx):
        """S1 en z = 132 sauf dans la bande 540 ≤ x < 560, S2 en z = 136 à partir de x = 540 : le pont de `333`."""
        z, x = idx[..., 0], idx[..., 2]
        s1 = (np.abs(z - 132) <= 1) & ((x < 540) | (x >= 560))
        s2 = (np.abs(z - 136) <= 1) & (x >= 540)
        return (s1 | s2).astype(float)

    gauche = g2[..., 0] < 540
    loin = g2[..., 0] >= 580
    lb = m333.la_nappe_de_la_spire(g2, gauche, graine, haut, deux_feuilles, marge=LA_MARGE)
    ll = m333.la_nappe_de_la_spire(g2, gauche, graine, haut, deux_feuilles)
    v("★★★★★ semée d'un seul côté du pont, la nappe bornée ne va pas se poser au-delà, là où la nappe libre passe sur S2",
      not (lb["valide"] & loin).any() and ll["valide"][loin].all()
      and np.allclose(ll["le_decalage"][loin], 4.0), f"{(lb['valide'] & loin).sum()}")
    v("★★★★ aucun point posé hors des mailles permises",
      not (lb["valide"] & ~m333.la_nappe_de_la_spire(g2, gauche, graine, haut, deux_feuilles, marge=LA_MARGE)["les_semes"]
           & ~m333.les_mailles_permises(lb["les_semes"], LA_MARGE)).any())
    v("★★★★ les relances des deux rouleaux sont bornées", all(
        r(plate)(np.array(graine), haut, g2, petite)["valide"].sum() == 81 for r in (la_relance_de_paris4, la_relance_de_0358)))
    v("★★★ sans marge, la relance est celle de 333", np.array_equal(ll["valide"], m333.la_nappe_de_la_spire(
        g2, gauche, graine, haut, deux_feuilles, marge=None)["valide"]))

    g_ = lambda h, t, arrets=("un tour manqué",): {"la_descente": h, "le_tour_touche": t,  # noqa: E731
                                                   "les_cotes": {f"c{i}": {"larret": a} for i, a in enumerate(arrets)}}
    c_ = lambda h: {"tient": h}  # noqa: E731
    base = {"les_pannes": []}
    vd = le_verdict(dict(base, les_graines={"PHercParis4": [g_(6, True), g_(6, True, ("un saut faux",))]},
                         les_cotes={"PHerc0358": [c_(2), c_(3)]}))
    v("★★★★ h ≥ 6, un saut faux, h0 > 1 : elle garde la justesse et rend la surface",
      vd["lissue"].endswith("elle garde la justesse et rend la surface"), vd["lissue"])
    vd = le_verdict(dict(base, les_graines={"PHercParis4": [g_(6, True, ("un saut faux",)), g_(7, True, ("un saut faux",))]},
                         les_cotes={"PHerc0358": [c_(4)]}))
    v("★★★★ deux sauts faux : elle perd la justesse", vd["lissue"].endswith("elle perd la justesse"))
    vd = le_verdict(dict(base, les_graines={"PHercParis4": [g_(5, True)]}, les_cotes={"PHerc0358": [c_(4)]}))
    v("★★★★ h < 6 : elle perd la justesse", vd["lissue"].endswith("elle perd la justesse"))
    vd = le_verdict(dict(base, les_graines={"PHercParis4": [g_(6, True)]}, les_cotes={"PHerc0358": [c_(1)]}))
    v("★★★ h0 = 1 : elle garde la justesse sans rendre la surface",
      vd["lissue"].endswith("elle garde la justesse sans rendre la surface"))
    v("★★★ la marge est nommée dans l'issue", "bornée à 2 mailles" in vd["lissue"])

    for e in echecs:
        print(f"  ÉCHEC {e}")
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
