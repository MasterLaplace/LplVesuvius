"""Un juge de position, qui compare le scan à la place d'une surface au scan à un demi-pas de part et d'autre, sépare-t-il la feuille de l'entre-deux ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UN SEUL CONTRASTE DE POSITION NE SOIT CALCULÉ. Ce qui était vu avant d'écrire : tout ce que
`298` à `307` publient, dont `R4-F488` : le juge de `301` note le tracé humain de PHercParis4 décalé d'un demi-pas sur sa feuille
dans 47 comparaisons sur 48, parce que l'alignement est l'amplitude du profil moyen, et qu'un décalage uniforme translate ce
profil sans changer son amplitude.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P108`. Ce que l'alignement jette, c'est l'endroit du profil moyen où tombe la
surface. Le même profil moyen, lu à sa place, dit si la surface est plus dense que ce qui est à un demi-pas d'elle : sur une feuille,
elle l'est ; entre deux feuilles, ce qui est à un demi-pas, ce sont les feuilles.

## Ce qui est fait

- **Les surfaces** : celles que `307` a préparées, sans en changer une : sur PHercParis4, le tracé humain des vingt-quatre blocs de
  l'étalonnage de `301`, décalé de −1 à +1 pas par quarts de pas ; sur PHerc0358, les nappes croissantes de `305` qui suivent leur
  feuille, aux mêmes décalages.
- **Le profil moyen** : celui du juge de `301`, chaque profil du scan brut le long de la normale ramené à moyenne nulle et écart un,
  sur ±200 µm, moyenné par bloc ou par nappe.
- **Le contraste de position** : la valeur du profil moyen à la place de la surface, moins la moyenne de ses valeurs à un demi-pas
  de part et d'autre (9 voxels de 9,6 µm sur PHercParis4, 10 de 9,362 µm sur PHerc0358). Une surface est **posée sur une feuille**
  si ce contraste est positif.

## L'issue

**Le juge de position sépare la feuille de l'entre-deux** si, sur PHercParis4, le tracé non décalé est posé sur une feuille pour au
moins 90 % des blocs, et le tracé décalé d'un demi-pas, des deux côtés réunis, pour au plus 5 % des 48 comparaisons, sans aucun
contraste absent : la règle de `301` et de `307`. Sinon **il ne la sépare pas**, avec les parts. Indécidable si une lecture échoue.

## Rapporté à côté, qui ne décide rien

La part des blocs posés sur une feuille à chaque décalage ; le contraste de chaque nappe de PHerc0358 à chaque décalage, et donc à
sa place.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : sur quelle face de sa feuille une surface est posée, ni ce que vaut ce juge là où le pas
change d'une spire à l'autre.

Usage :
    uv run python src/nappe/un_juge_de_position_separe_t_il_la_feuille_de_lentre_deux.py --verifier
    uv run python src/nappe/un_juge_de_position_separe_t_il_la_feuille_de_lentre_deux.py \\
        --json docs/mesures/un_juge_de_position_separe_t_il_la_feuille_de_lentre_deux.json
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

import la_matiere_dit_elle_si_la_surface_est_sur_sa_feuille as m298  # noqa: E402
import lalignement_des_profils_dit_il_si_une_premiere_surface_suit_sa_feuille as m299  # noqa: E402
import le_juge_voit_il_lentre_deux_feuilles as m307  # noqa: E402

LES_PAS_UM = {"PHercParis4": 173.0, "PHerc0358": 187.24}


def le_demi_pas(volume: str) -> int:
    """Le demi-pas du rouleau, en voxels du niveau jugé, arrondi."""
    return int(round(LES_PAS_UM[volume] / 2.0 / m298.LES_VOLUMES[volume]["le_voxel_um"]))


def le_contraste(profil: list, demi: int) -> float | None:
    """La valeur du profil moyen au centre, moins la moyenne de ses valeurs à `demi` de part et d'autre ; None sans profil."""
    if not profil:
        return None
    p = np.asarray(profil, dtype=float)
    T = len(p) // 2
    if demi <= 0 or demi > T:
        return None
    return round(float(p[T] - (p[T - demi] + p[T + demi]) / 2.0), 4)


def la_part_posee(cs: list) -> float | None:
    """La part des contrastes positifs ; un contraste absent compte comme non posé."""
    if not cs:
        return None
    return round(sum(1 for c in cs if c is not None and c > 0) / len(cs), 4)


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    blocs = d["paris4"]["les_blocs"]
    sur = la_part_posee([b["les_contrastes"]["p0"] for b in blocs])
    entre = la_part_posee([b["les_contrastes"][k] for b in blocs for k in ("m0_5", "p0_5")])
    n = 2 * len(blocs)
    poses = sum(1 for b in blocs for k in ("m0_5", "p0_5") if b["les_contrastes"][k] is not None
                and b["les_contrastes"][k] > 0)
    k0 = sum(1 for b in blocs if b["les_contrastes"]["p0"] is not None and b["les_contrastes"]["p0"] > 0)
    absents = sum(1 for b in blocs for k in ("p0", "m0_5", "p0_5") if b["les_contrastes"][k] is None)
    separe = (bool(blocs) and absents == 0 and sur is not None and entre is not None
              and sur >= m307.LE_TAUX_SUR_LA_FEUILLE and entre <= m307.LE_TAUX_ENTRE_DEUX)
    return {"decidable": True, "separe": separe, "la_part_posee_a_sa_place": sur, "la_part_posee_au_demi_pas": entre,
            "les_absents": absents,
            "lissue": ("le juge de position sépare la feuille de l'entre-deux : le tracé est posé sur sa feuille, décalé d'un "
                       f"demi-pas il ne l'est plus que dans {poses} des {n} comparaisons" if separe else
                       f"le juge de position ne sépare pas la feuille de l'entre-deux : le tracé est posé sur une feuille dans "
                       f"{k0} des {len(blocs)} blocs, et décalé d'un demi-pas dans {poses} des {n} comparaisons")}


def mesurer() -> dict:
    t0 = time.monotonic()
    plan = json.loads(m307.LE_PLAN.read_text())
    decs = [m307.le_nom(x) for x in m307.LES_DECALAGES]
    res: dict = {}
    for volume, v in m298.LES_VOLUMES.items():
        vol = m298.LesMorceaux(volume, v["url"], v["niveau"])
        T = m298.la_demi_fenetre(volume)
        for cle, info in plan["les_surfaces"].items():
            if cle.startswith(volume + "__") and "__" not in cle[len(volume) + 2:]:
                res[cle] = m299.juger(vol, RACINE / info["le_fichier"], v["facteur"], T)
        print(f"{volume} ({time.monotonic() - t0:.0f} s)", flush=True)
    hp, hq = le_demi_pas("PHercParis4"), le_demi_pas("PHerc0358")
    blocs = []
    for i, b in enumerate(plan["les_blocs"]):
        cs = {k: le_contraste(res[f"PHercParis4__{k}"][i]["le_profil_moyen"], hp) for k in decs}
        blocs.append({"le_bloc": b, "les_contrastes": cs,
                      "le_profil_moyen_a_sa_place": res["PHercParis4__p0"][i]["le_profil_moyen"]})
    moyen = [round(float(x), 4) for x in np.mean([b["le_profil_moyen_a_sa_place"] for b in blocs], axis=0)] if blocs else []
    courbe = [{"le_decalage_en_pas": x, "la_part_posee": la_part_posee([b["les_contrastes"][m307.le_nom(x)] for b in blocs])}
              for x in m307.LES_DECALAGES]
    rangs = sorted({int(k.split("__g")[1].split("_")[0]) for k in res if k.startswith("PHerc0358__g")})
    nappes = []
    for r in rangs:
        cs = {k: (le_contraste(res[f"PHerc0358__g{r}_{k}"][0]["le_profil_moyen"], hq)
                  if res.get(f"PHerc0358__g{r}_{k}") else None) for k in decs}
        nappes.append({"le_rang": r, "les_contrastes": cs, "posee_sur_une_feuille": cs["p0"] is not None and cs["p0"] > 0,
                       "le_relief": m298.le_relief(res[f"PHerc0358__g{r}_p0"][0]["le_profil_moyen"]),
                       "le_profil_moyen_a_sa_place": res[f"PHerc0358__g{r}_p0"][0]["le_profil_moyen"]})
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"les_demi_pas_voxels": {"PHercParis4": hp, "PHerc0358": hq},
                            "les_decalages_en_pas": list(m307.LES_DECALAGES)},
         "les_pannes": plan["les_pannes"],
         "paris4": {"les_blocs": blocs, "la_courbe": courbe, "le_relief_du_profil_moyen_des_blocs": m298.le_relief(moyen)},
         "phercs0358": {"les_nappes": nappes}}
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

    v("★★★ le demi-pas : 9 voxels sur PHercParis4, 10 sur PHerc0358",
      le_demi_pas("PHercParis4") == 9 and le_demi_pas("PHerc0358") == 10)
    u = np.arange(-21, 22)
    sur = list(np.cos(2 * np.pi * u / 18.0))
    entre = list(np.cos(2 * np.pi * (u + 9) / 18.0))
    v("★★★★ sur un empilement régulier, le contraste est positif sur la feuille et négatif entre deux",
      le_contraste(sur, 9) > 0 and le_contraste(entre, 9) < 0, f"{le_contraste(sur, 9)} {le_contraste(entre, 9)}")
    pente = list(u / 21.0)
    v("★★★ un profil qui monte d'un bout à l'autre n'a pas de contraste", abs(le_contraste(pente, 9)) < 1e-9)
    v("★★★ un contraste compare bien les deux côtés", le_contraste([0, 1, 0, 0, 0], 2) == 0.0
      and le_contraste([0, 0, 1, 0, 0], 2) == 1.0 and le_contraste([2, 0, 1, 0, 0], 2) == 0.0)
    v("★★★ sans profil, ou au-delà de la fenêtre, pas de contraste", le_contraste([], 9) is None
      and le_contraste([0.0] * 11, 9) is None)
    v("★★★★ la part posée : un contraste absent compte comme non posé", la_part_posee([0.1, None, -0.1, 0.2]) == 0.5)

    def blocs_(a, b):
        return [{"les_contrastes": {"p0": a[i], "m0_5": b[2 * i], "p0_5": b[2 * i + 1]}} for i in range(len(a))]

    ok_ = le_verdict({"paris4": {"les_blocs": blocs_([0.5] * 20, [-0.5] * 40)}})
    v("★★★★ sépare : le tracé posé partout, le demi-pas nulle part", ok_["separe"] and "dans 0 des 40" in ok_["lissue"],
      ok_["lissue"])
    ko = le_verdict({"paris4": {"les_blocs": blocs_([0.5] * 19 + [-0.5], [-0.5] * 37 + [0.5] * 3)}})
    v("★★★★ ne sépare pas : trois demi-pas posés sur quarante dépassent 5 %", not ko["separe"]
      and "dans 19 des 20 blocs, et décalé d'un demi-pas dans 3 des 40" in ko["lissue"], ko["lissue"])
    v("★★★★ les deux côtés du demi-pas comptent",
      not le_verdict({"paris4": {"les_blocs": [{"les_contrastes": {"p0": 0.5, "m0_5": -0.5, "p0_5": 0.5}}] * 20}})["separe"])
    v("★★★ un contraste absent empêche la séparation",
      not le_verdict({"paris4": {"les_blocs": blocs_([0.5] * 20, [-0.5] * 39 + [None])}})["separe"])
    v("★★★ indécidable si une lecture échoue", not le_verdict({"les_pannes": ["x"]})["decidable"])

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
