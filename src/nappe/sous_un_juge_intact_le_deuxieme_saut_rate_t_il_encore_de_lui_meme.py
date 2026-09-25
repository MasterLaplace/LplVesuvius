"""Sous un juge qui ne se déchire pas, le deuxième saut rate-t-il encore de lui-même ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LES RATÉS DU DEUXIÈME SAUT NE SOIENT REJUGÉS. Ce qui était vu avant d'écrire : tout ce que
`248` et `252` à `277` publient. `277` range les ratés du deuxième saut de la chaîne partie de la spire corrigée : 1220 dont
le premier saut était juste, 627 dont il avait raté. Le deuxième saut rate surtout de lui-même, et ses ratés propres tombent
surtout trop près de la deuxième couche. Mais `248` publie que 0,7205 des ratés trop près du deuxième saut du témoin tombent
là où les couches du segment sautent plus d'un pas et demi, et `252` que c'est là que la couche du juge se déchire : elle
saute d'un tour entre deux mailles voisines, ce qu'une feuille ne fait pas.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P95`. `277` conclut que chaque saut demande sa correction. Si ses ratés propres
sont surtout des déchirures du juge, cette conclusion ne tient pas, et corriger le premier saut pourrait suffire.

## Le rejugement

Les deux chaînes de `276`, refaites telles quelles, rejugées par le juge intact de `253`, déclaré avant la mesure de `253` :
au saut h, un point n'est noté que si la h-ième couche du segment existe en face de lui, n'est bordée d'aucune falaise (une
voisine à un demi-feuillet ou plus, `252`) et tient à la plus grande pièce de la couche. Un raté du deuxième saut est hérité
si le premier saut de la même chaîne avait raté, propre s'il était juste, sur les points que le juge note aux deux sauts,
comme dans `277`.

⚠ Sous le juge de `248`, les deux chaînes doivent redonner le rangement de `277`, compte pour compte ; sinon la mesure est
indécidable.

## Les issues, exclusives, sur la chaîne partie de la spire corrigée, sous le juge intact

- les ratés propres sont plus nombreux que les ratés hérités : le deuxième saut rate encore surtout de lui-même ;
- ils ne le sont pas : sous un juge intact, il rate surtout parce que le premier a raté.

⚠ Rapporté à côté : le même rangement pour le témoin, et sous le juge sans falaise de `253`, qui ne retient que la règle de la
falaise ; parmi les ratés propres de `277`, ceux que le juge intact écarte.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : une couche qui glisse d'une spire à l'autre par des pentes douces reste continue et le
juge intact la garde ; un point juste dont le juge se déchire est écarté. Une correction du deuxième saut.

Usage :
    uv run python src/nappe/sous_un_juge_intact_le_deuxieme_saut_rate_t_il_encore_de_lui_meme.py --verifier
    uv run python src/nappe/sous_un_juge_intact_le_deuxieme_saut_rate_t_il_encore_de_lui_meme.py \\
        --json docs/mesures/sous_un_juge_intact_le_deuxieme_saut_rate_t_il_encore_de_lui_meme.json
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

from la_chaine_rejugee_hors_des_dechirures import les_notes_intactes  # noqa: E402
from la_surface_produite_se_dechire_t_elle import la_falaise  # noqa: E402
from les_rates_du_deuxieme_saut_viennent_ils_du_premier import les_origines  # noqa: E402
from repartir_de_la_spire_corrigee_rend_il_le_saut_suivant_plus_juste import les_deux_chaines, les_justes  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_277_A_PUBLIE = LES_MESURES / "les_rates_du_deuxieme_saut_viennent_ils_du_premier.json"
LES_CHAINES = ("le_temoin", "partie_de_la_spire_corrigee")


def sous_le_juge(v: np.ndarray, note: np.ndarray) -> np.ndarray:
    """La couche là où le juge note, NaN ailleurs : un point que le juge ne note pas n'est ni juste ni raté."""
    return np.where(note, v, np.nan)


def les_propres_ecartes(t1: np.ndarray, t2: np.ndarray, v1: np.ndarray, v2: np.ndarray, garde1: np.ndarray,
                        garde2: np.ndarray) -> dict:
    """Parmi les ratés propres sous le juge de `248`, ceux qu'un autre juge écarte à l'un des deux sauts."""
    note = np.isfinite(v1) & np.isfinite(v2)
    propre = note & les_justes(t1, v1) & ~les_justes(t2, v2)
    ecarte = propre & ~(garde1 & garde2)
    return {"les_propres": int(propre.sum()), "ecartes": int(ecarte.sum()), "gardes": int((propre & ~ecarte).sum())}


def le_verdict(r: dict) -> dict:
    if not r.get("decidable"):
        return {"lissue": "indécidable : sous le juge de 248, les deux chaînes ne redonnent pas le rangement de 277"}
    o = r["le_juge_intact"]["partie_de_la_spire_corrigee"]
    if o["les_propres"] > o["les_herites"]:
        return {"lissue": "sous un juge intact, le deuxième saut rate encore surtout de lui-même"}
    return {"lissue": "sous un juge intact, le deuxième saut rate surtout parce que le premier a raté"}


def mesurer() -> dict:
    debut = time.monotonic()
    c = les_deux_chaines()
    if isinstance(c, str):
        return {"decidable": False, "la_raison": c, "le_verdict": le_verdict({})}
    v, gi, gj, grille = c["verite"], c["gi"], c["gj"], c["sur_la_grille"]
    chaines = {"le_temoin": (c["pt"], c["temoin"]), "partie_de_la_spire_corrigee": (c["pc"], c["corrigee"])}
    juges = {"le_juge_de_248": [np.isfinite(x) for x in v[:2]],
             "le_juge_intact": [les_notes_intactes(x, grille, gi, gj) for x in v[:2]],
             "le_juge_sans_falaise": [np.isfinite(x) & ~la_falaise(grille(x))[gi, gj] for x in v[:2]]}
    out = {}
    for nom_j, notes in juges.items():
        v1, v2 = sous_le_juge(v[0], notes[0]), sous_le_juge(v[1], notes[1])
        out[nom_j] = {k: les_origines(tau[0], tau[1], v1, v2, ch[1]["le_pas"]) for k, (tau, ch) in chaines.items()}
    publie = json.loads(CE_QUE_277_A_PUBLIE.read_text())
    out["le_rangement_de_277"] = {k: {"reproduit": out["le_juge_de_248"][k] == publie[k]} for k in LES_CHAINES}
    intact = juges["le_juge_intact"]
    out["les_propres_de_277_que_le_juge_intact_ecarte"] = {
        k: les_propres_ecartes(tau[0], tau[1], v[0], v[1], intact[0], intact[1]) for k, (tau, _) in chaines.items()}
    out["les_points_notes"] = {nom_j: int((n[0] & n[1]).sum()) for nom_j, n in juges.items()}
    out["la_lecture"] = {"combien_de_pannes": len(c["stats"]["pannes"])}
    out["decidable"] = (all(x["reproduit"] for x in out["le_rangement_de_277"].values())
                        and not out["la_lecture"]["combien_de_pannes"])
    out["le_verdict"] = le_verdict(out)
    out["les_secondes"] = round(time.monotonic() - debut, 1)
    return out


# ── LA BATTERIE ────────────────────────────────────────────────────────────────────────────────────────────────────

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

    v1 = np.array([70.0, 70.0, 70.0, 70.0])
    v2 = np.array([140.0, 140.0, 140.0, 140.0])
    t1 = np.array([70.0, 70.0, 140.0, 70.0])
    t2 = np.array([72.0, 72.0, 210.0, 140.0])        # deux propres, un hérité, un juste
    note2 = np.array([True, False, True, True])      # le juge écarte la deuxième couche du deuxième point
    o = les_origines(t1, t2, v1, sous_le_juge(v2, note2), np.zeros(4), 1.0)
    v("★★★★ un point que le juge ne note pas n'est ni juste ni raté : il sort du rangement",
      o["les_points_notes_aux_deux_sauts"] == 3 and o["les_propres"] == 1 and o["les_herites"] == 1, str(o))
    e = les_propres_ecartes(t1, t2, v1, v2, np.ones(4, bool), note2)
    v("★★★★ parmi les ratés propres du juge de 248, un point écarté à l'un des deux sauts est compté écarté",
      e == {"les_propres": 2, "ecartes": 1, "gardes": 1}, str(e))
    e1 = les_propres_ecartes(t1, t2, v1, v2, np.array([True, False, True, True]), np.ones(4, bool))
    v("★★★ écarté au premier saut aussi", e1["ecartes"] == 1, str(e1))

    # Le juge intact écarte une couche qui saute d'un tour entre deux mailles voisines.
    carte = np.full((6, 6), 70.0)
    carte[:, 4:] = 140.0                                   # une déchirure, et une petite pièce au-delà
    gi_, gj_ = np.nonzero(np.ones((6, 6), bool))

    def grille_(val):
        c_ = np.full((6, 6), np.nan)
        c_[gi_, gj_] = val
        return c_

    it = les_notes_intactes(carte[gi_, gj_], grille_, gi_, gj_)
    v("★★★ le juge intact écarte les bords d'une déchirure et la petite pièce", not it.reshape(6, 6)[:, 3:].any()
      and it.reshape(6, 6)[:, :3].all(), str(it.reshape(6, 6).astype(int)))

    r_ = lambda p, h: {"decidable": True, "le_juge_intact": {"partie_de_la_spire_corrigee":  # noqa: E731
                                                                 {"les_propres": p, "les_herites": h}}}
    v("★★★★ les issues se lisent sous le juge intact : de lui-même si les propres sont plus nombreux, sinon hérité",
      "encore surtout de lui-même" in le_verdict(r_(3, 2))["lissue"]
      and "parce que le premier" in le_verdict(r_(2, 2))["lissue"] and "indécidable" in le_verdict({})["lissue"])

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
    r = mesurer()
    print(json.dumps(r, ensure_ascii=False, indent=1))
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=1))
        print(f"\nécrit : {a.json}")
    return 0 if r.get("decidable") else 2


if __name__ == "__main__":
    raise SystemExit(main())
