"""Les spires des chaînes de m7, relues au plus dense du scan, restent-elles chacune au cœur d'une feuille ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UNE SEULE SPIRE DES CHAÎNES NE SOIT RELUE AU PLUS DENSE. Ce qui était vu avant d'écrire : tout ce
que `303` à `309` publient, dont `R4-F490` : les surfaces de `m7` de PHerc0358 appuyées sur la prédiction sont à 0 à 2 voxels du
plus dense de leur profil moyen, sauf trois, qui avaient quitté leur feuille.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P110`. `303` dit que la chaîne reste parallèle à l'empilement pendant quatre sauts,
et `307` que ce juge ne voit que l'orientation. Aucun référent ne peut étalonner un juge de position (`309`), mais la place du plus
dense se lit sans juge : spire par spire, elle dit si la chaîne reste au cœur d'une feuille, et le pas dit si elle avance d'une
spire.

## Ce qui est fait

- **Les chaînes** : celle de `303` (le vote, cinq graines, dix côtés, quatre sauts) et celle de `306` (les sauts croissants, deux
  graines, quatre côtés), telles que ces tranches les ont préparées pour leur juge, sans en changer un point.
- **La lecture** : le profil moyen du juge de `301`, et le décalage de son plus dense par rapport à la spire.
- **Au cœur d'une feuille** : le plus dense à au plus un quart de pas de la spire, 5 voxels.

## Les issues

Par côté, le dernier saut h tel que les spires 1 à h sont toutes au cœur d'une feuille ; 0 si la première ne l'est pas. **L'issue de
la tranche, sur la chaîne de `303`** : elle reste au cœur d'une feuille jusqu'au saut H sur au moins la moitié des dix côtés, H le
plus grand saut pour lequel c'est vrai. La chaîne de `306` est rapportée.

## Rapporté à côté, qui ne décide rien

Pour chaque spire : le pas médian et la part appuyée sur `m7` que `303` et `306` publient.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : que « au plus dense » veuille dire « sur une feuille », ni que les spires soient consécutives.

Usage :
    uv run python src/nappe/la_chaine_relue_au_plus_dense_reste_t_elle_au_coeur_dune_feuille.py --verifier
    uv run python src/nappe/la_chaine_relue_au_plus_dense_reste_t_elle_au_coeur_dune_feuille.py \\
        --json docs/mesures/la_chaine_relue_au_plus_dense_reste_t_elle_au_coeur_dune_feuille.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))
sys.path.insert(0, str(RACINE / "src" / "tracecheck"))

import la_matiere_dit_elle_si_la_surface_est_sur_sa_feuille as m298  # noqa: E402
import lalignement_des_profils_dit_il_si_une_premiere_surface_suit_sa_feuille as m299  # noqa: E402
import le_plus_dense_dit_il_si_une_surface_est_sur_sa_feuille as m309  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
LES_CHAINES = {
    "vote": {"le_plan": RACINE / "data" / "chaine_de_m7" / "plan.json",
             "la_mesure": MESURES / "la_chaine_tiree_de_m7_suit_elle_sa_feuille_au_dela_du_premier_saut.json",
             "le_pas": "le_pas_median_des_appuyes_voxels", "lappui": "la_part_appuyee"},
    "croissante": {"le_plan": RACINE / "data" / "chaine_dune_seule_feuille" / "plan.json",
                   "la_mesure": MESURES / "la_chaine_dune_seule_feuille_suit_elle_sa_feuille_sur_quatre_spires.json",
                   "le_pas": "le_pas_median_voxels", "lappui": "la_part_du_plan"},
}


def le_dernier_au_coeur(sauts: list[dict]) -> int:
    h = 0
    for s in sauts:
        if not s["au_coeur"]:
            break
        h += 1
    return h


def le_verdict(d: dict) -> dict:
    cotes = d["les_chaines"].get("vote", [])
    if not cotes:
        return {"decidable": False, "lissue": "indécidable : aucun côté de la chaîne de 303"}
    derniers = [c["le_dernier_saut_au_coeur"] for c in cotes]
    n = len(derniers)
    H = max((h for h in range(1, 5) if sum(1 for x in derniers if x >= h) * 2 >= n), default=0)
    return {"decidable": True, "H": H, "les_derniers": derniers,
            "lissue": (f"la chaîne de 303 reste au cœur d'une feuille jusqu'au saut {H} sur au moins la moitié des {n} côtés"
                       if H else f"la chaîne de 303 quitte le cœur de sa feuille dès le premier saut sur plus de la moitié des "
                                 f"{n} côtés")}


def mesurer() -> dict:
    t0 = time.monotonic()
    v = m298.LES_VOLUMES["PHerc0358"]
    vol = m298.LesMorceaux("PHerc0358", v["url"], v["niveau"])
    T = m298.la_demi_fenetre("PHerc0358")
    quart = m309.le_quart_de_pas("PHerc0358")
    out = {}
    for nom, c in LES_CHAINES.items():
        plan = json.loads(c["le_plan"].read_text())
        publie = {(x["le_rang"], x["le_cote"]): x for x in json.loads(c["la_mesure"].read_text())["les_cotes"]}
        cotes = []
        for cote in plan["les_cotes"]:
            e = {"le_rang": cote["le_rang"], "le_cote": cote["le_cote"], "les_sauts": []}
            pub = publie[(cote["le_rang"], cote["le_cote"])]
            for s, p in zip(cote["les_sauts"], pub["les_sauts"]):
                cle = f"g{cote['le_rang']}_{cote['le_cote']}_{s['le_saut']}"
                r = m299.juger(vol, RACINE / plan["les_surfaces"][cle]["le_fichier"], v["facteur"], T)
                pd = m309.le_plus_dense(r[0]["le_profil_moyen"]) if r else None
                e["les_sauts"].append({"le_saut": s["le_saut"], "le_plus_dense": pd,
                                       "au_coeur": pd is not None and abs(pd) <= quart,
                                       "les_points_juges": r[0]["les_points_juges"] if r else 0,
                                       "le_pas_median_voxels": p.get(c["le_pas"]), "lappui": p.get(c["lappui"]),
                                       "le_juge_de_301": p.get("la_piece")})
            e["le_dernier_saut_au_coeur"] = le_dernier_au_coeur(e["les_sauts"])
            cotes.append(e)
            print(json.dumps({k: v_ for k, v_ in e.items() if k != "les_sauts"}), flush=True)
        out[nom] = cotes
    d = {"la_question": __doc__.splitlines()[0], "les_constantes": {"le_quart_de_pas_voxels": quart},
         "les_chaines": out}
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

    s = [{"au_coeur": True}, {"au_coeur": False}, {"au_coeur": True}]
    v("★★★★ le dernier saut au cœur s'arrête au premier qui en sort", le_dernier_au_coeur(s) == 1
      and le_dernier_au_coeur(s[1:]) == 0 and le_dernier_au_coeur([{"au_coeur": True}] * 4) == 4)
    vd = le_verdict({"les_chaines": {"vote": [{"le_dernier_saut_au_coeur": x} for x in (4, 4, 2, 0, 1, 3, 4, 0, 2, 1)]}})
    v("★★★ l'issue : le plus grand saut tenu sur au moins la moitié des côtés", vd["H"] == 2, str(vd))
    vd = le_verdict({"les_chaines": {"vote": [{"le_dernier_saut_au_coeur": 0}] * 6 + [{"le_dernier_saut_au_coeur": 4}] * 4}})
    v("★★★ l'issue : dès le premier saut si moins de la moitié y reste", vd["H"] == 0 and "dès le premier" in vd["lissue"])
    vd = le_verdict({"les_chaines": {"vote": [{"le_dernier_saut_au_coeur": 4}] * 5 + [{"le_dernier_saut_au_coeur": 0}] * 5}})
    v("★★★ « au moins la moitié » compte la moitié exacte", vd["H"] == 4, str(vd))
    v("★★★ l'issue ne regarde que la chaîne de 303",
      le_verdict({"les_chaines": {"croissante": [{"le_dernier_saut_au_coeur": 4}]}})["decidable"] is False)
    v("★★★ le quart de pas vient de 309", m309.le_quart_de_pas("PHerc0358") == 5)

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
