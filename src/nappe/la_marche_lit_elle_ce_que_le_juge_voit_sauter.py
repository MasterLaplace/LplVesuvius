"""La marche lit-elle ce que le juge voit sauter ? D'un chunk juste à son voisin raté, ce que la marche lit de l'écart jugé.

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE CE RAPPORT NE SOIT CALCULÉ. Ce qui était vu avant d'écrire : tout ce que `257` à `268`
publient, dont les frontières du voisinage de `259`, qui ne sautent que de 20 à 34 voxels dans la marche, et celles du bloc
`(160, 160)`, marché seul, qui en sautent une glissade là où le juge ne voit rien.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P95`. `268` défait les frontières qui ne sautent pas d'une glissade, et avec elles
les ratés du bloc de `259`. Deux causes le feraient, et elles ne demandent pas la même suite : ou bien le juge voit ces ratés
se faire progressivement, d'un chunk à l'autre, et il n'y a pas de marche franche à trouver ; ou bien le juge les voit sauter
d'un coup, et la marche n'en lit qu'une partie. La première cause est la surface ; la seconde, l'instrument.

## Ce qui se mesure

Sur les marches d'un seul tenant de `265` et bloc par bloc de `264` : pour chaque paire de chunks qui se touchent, dont l'un est
juste et l'autre raté selon le juge, `ΔE` l'écart des erreurs jugées et `ΔD` celui de la différence des marches, du juste vers
le raté. Deux nombres :

1. ce que le juge voit sauter : la médiane de `|ΔE|` ;
2. ce que la marche en lit : la pente de `ΔD` contre `ΔE` par les moindres carrés, passant par zéro, rapportée à ce qu'elle
   retrouve d'une rampe, 0,9636 (`261`).

⚠ Le témoin : la même pente sur les paires dont les deux chunks sont justes.

## Les issues, exclusives, sur les paires des marches d'un seul tenant réunies

- elle lit au moins les trois quarts de ce que le juge voit sauter : la marche lit ce que le juge voit sauter ;
- elle en lit moins de la moitié : la marche n'en lit pas la moitié ;
- sinon : elle en lit une partie.

⚠ Rapporté à côté : chaque voisinage seul, et les blocs marchés seuls.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : si le juge a raison sur ces ratés ; pourquoi la marche en lit ce qu'elle en lit.

Usage :
    uv run python src/nappe/la_marche_lit_elle_ce_que_le_juge_voit_sauter.py --verifier
    uv run python src/nappe/la_marche_lit_elle_ce_que_le_juge_voit_sauter.py \\
        --json docs/mesures/la_marche_lit_elle_ce_que_le_juge_voit_sauter.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))

from la_spire_produite_se_lit_elle_dans_le_treillis import (LA_PREDICTION, LE_BLOC, LE_COTE,  # noqa: E402
                                                            LES_JUGES, lerreur_aux_chunks, lerreur_jugee)
from la_spire_voisine_est_elle_a_un_pas import DEMI_PAS_EN_VOXELS, LE_CACHE, LE_SEGMENT  # noqa: E402
from le_pas_de_fenetre_en_fenetre_voit_il_la_rampe import la_grille  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_261_A_PUBLIE = LES_MESURES / "la_marche_corrige_t_elle_la_spire_produite.json"
CE_QUE_264_A_PUBLIE = LES_MESURES / "la_marche_sait_elle_ou_ne_pas_corriger.json"
CE_QUE_265_A_PUBLIE = LES_MESURES / "le_voisinage_dit_il_quel_niveau_est_le_bon.json"


def les_paires(diff: np.ndarray, erreur: np.ndarray, seuil: float = DEMI_PAS_EN_VOXELS) -> dict[str, np.ndarray]:
    """Les paires de chunks qui se touchent, où la marche et le juge sont tous deux présents : `(ΔE, ΔD)`.

    `franchit` : l'un juste, l'autre raté, orientée du juste vers le raté ; `justes` : les deux justes, orientée de gauche à
    droite et de haut en bas.
    """
    franchit, justes = [], []
    n, m = diff.shape
    ok = np.isfinite(diff) & np.isfinite(erreur)
    with np.errstate(invalid="ignore"):
        rate = np.abs(erreur) >= seuil
    for i in range(n):
        for j in range(m):
            for y, x in ((i + 1, j), (i, j + 1)):
                if y >= n or x >= m or not (ok[i, j] and ok[y, x]):
                    continue
                if rate[i, j] != rate[y, x]:
                    a, b = ((i, j), (y, x)) if not rate[i, j] else ((y, x), (i, j))
                    franchit.append((erreur[b] - erreur[a], diff[b] - diff[a]))
                elif not rate[i, j]:
                    justes.append((erreur[y, x] - erreur[i, j], diff[y, x] - diff[i, j]))
    return {"franchit": np.array(franchit).reshape(-1, 2), "justes": np.array(justes).reshape(-1, 2)}


def ce_qui_est_lu(p: np.ndarray, pente_de_la_rampe: float) -> dict:
    """La médiane de |ΔE|, et la pente de ΔD contre ΔE passant par zéro, rapportée à la pente de la rampe."""
    if len(p) < 2 or float((p[:, 0] ** 2).sum()) <= 0.0:
        return {"les_paires": int(len(p)), "le_saut_juge_median_voxels": None, "la_pente": None, "la_part_lue": None}
    pente = float((p[:, 0] * p[:, 1]).sum() / (p[:, 0] ** 2).sum())
    return {"les_paires": int(len(p)), "le_saut_juge_median_voxels": round(float(np.median(np.abs(p[:, 0]))), 4),
            "la_pente": round(pente, 4), "la_part_lue": round(pente / pente_de_la_rampe, 4),
            "la_part_des_sauts_lus_a_une_demi_glissade": round(float((np.abs(p[:, 1]) >= DEMI_PAS_EN_VOXELS).mean()), 4)}


def reunir(listes: list[dict[str, np.ndarray]], cle: str) -> np.ndarray:
    return np.concatenate([x[cle] for x in listes], axis=0) if listes else np.zeros((0, 2))


def mesurer(cache: Path = LE_CACHE) -> dict:
    d261 = json.loads(CE_QUE_261_A_PUBLIE.read_text())
    d264 = json.loads(CE_QUE_264_A_PUBLIE.read_text())
    d265 = json.loads(CE_QUE_265_A_PUBLIE.read_text())
    pente = float(d261["le_signe"]["la_pente"])
    tau0 = np.load(cache / f"transfert_suivante_{LE_SEGMENT}_{LA_PREDICTION}_{LE_COTE}.npy")
    err = lerreur_jugee(tau0, [np.load(cache / f"verite_{LE_SEGMENT}_{j}_{LE_COTE}.npy") for j in LES_JUGES])
    out = {"la_pente_de_la_rampe": pente, "les_voisinages": {}, "les_blocs": {}}
    pv, pb = [], []
    for nom, b in d265["les_blocs"].items():
        e = lerreur_aux_chunks(err, b["la_rangee"] - LE_BLOC, b["la_colonne"] - LE_BLOC, 3 * LE_BLOC)
        p = les_paires(la_grille(b["la_difference"]), e)
        pv.append(p)
        out["les_voisinages"][nom] = {k: ce_qui_est_lu(p[k], pente) for k in p}
        out["les_voisinages"][nom]["les_paires_qui_franchissent"] = [[round(float(x), 2) for x in q] for q in p["franchit"]]
    for nom, b in d264["les_blocs"].items():
        e = lerreur_aux_chunks(err, b["la_rangee"], b["la_colonne"], LE_BLOC)
        p = les_paires(la_grille(b["la_difference"]), e)
        pb.append(p)
        out["les_blocs"][nom] = {k: ce_qui_est_lu(p[k], pente) for k in p}
    out["dun_seul_tenant"] = {k: ce_qui_est_lu(reunir(pv, k), pente) for k in ("franchit", "justes")}
    out["bloc_par_bloc"] = {k: ce_qui_est_lu(reunir(pb, k), pente) for k in ("franchit", "justes")}
    out["decidable"] = out["dun_seul_tenant"]["franchit"]["la_part_lue"] is not None
    return out


def le_verdict(r: dict) -> dict:
    if not r.get("decidable"):
        return {"lissue": "indécidable"}
    q = r["dun_seul_tenant"]["franchit"]["la_part_lue"]
    if q >= 0.75:
        return {"lissue": "elle en lit au moins les trois quarts : la marche lit ce que le juge voit sauter"}
    if q < 0.5:
        return {"lissue": "elle en lit moins de la moitié : la marche n'en lit pas la moitié"}
    return {"lissue": "elle en lit une partie"}


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

    e = np.zeros((6, 6))
    e[:, 3:] = 72.0
    e[:, 0] = 72.0
    d = 0.5 * e
    p = les_paires(d, e)
    v("★★★★ les paires qui franchissent sont orientées du juste vers le raté, des deux côtés, et comptées une fois",
      lambda: len(p["franchit"]) == 12 and np.allclose(p["franchit"][:, 0], 72.0) and np.allclose(p["franchit"][:, 1], 36.0))
    v("★★★ les paires justes sont celles dont les deux chunks sont justes",
      lambda: len(p["justes"]) == 5 * 2 + 6, str(len(p["justes"])))
    lu = ce_qui_est_lu(p["franchit"], 1.0)
    v("★★★★ une marche qui lit la moitié du saut a une part lue d'un demi",
      lambda: lu["la_part_lue"] == 0.5 and lu["le_saut_juge_median_voxels"] == 72.0, str(lu))
    v("★★★ la part lue se rapporte à la pente de la rampe",
      lambda: ce_qui_est_lu(p["franchit"], 0.5)["la_part_lue"] == 1.0)
    q = np.array([[72.0, 36.0], [72.0, 36.0], [60.0, 96.0], [-80.0, -20.0]])
    v("★★★★ la pente est celle des moindres carrés passant par zéro, pas un rapport de médianes",
      lambda: ce_qui_est_lu(q, 1.0)["la_pente"] == round(float((q[:, 0] * q[:, 1]).sum() / (q[:, 0] ** 2).sum()), 4))
    e2 = e.copy()
    e2[2, 2] = np.nan
    v("★★★ un chunk sans juge n'entre dans aucune paire",
      lambda: len(les_paires(d, e2)["justes"]) == 5 * 2 + 6 - 3 and len(les_paires(d, e2)["franchit"]) == 11)
    v("★★★ sans paire, rien n'est lu", lambda: ce_qui_est_lu(np.zeros((0, 2)), 1.0)["la_part_lue"] is None)

    def verdict(q):
        return le_verdict({"decidable": True, "dun_seul_tenant": {"franchit": {"la_part_lue": q}}})["lissue"]
    v("★★★★ les issues : trois quarts, moins de la moitié, une partie",
      lambda: "lit ce que" in verdict(0.8) and "pas la moitié" in verdict(0.4) and "une partie" in verdict(0.6))

    for x in echecs:
        print(f"  ÉCHEC {x}")
    print(f"{Path(__file__).name}   {'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer()
    r["le_verdict"] = le_verdict(r)
    texte = json.dumps(r, indent=1, ensure_ascii=False)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(texte + "\n")
    print(texte[:5000])
    return 0 if r.get("decidable") else 2


if __name__ == "__main__":
    raise SystemExit(main())
