"""Rayon par rayon, là où m7 ne voit pas de feuille après celle d'une nappe, le profil du scan a-t-il un maximum à un pas, aussi souvent que là où m7 en voit une ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UN SEUL MAXIMUM NE SOIT COMPTÉ RAYON PAR RAYON. Ce qui était vu avant d'écrire : tout ce que
`303` à `319` publient, dont `R4-F500` : la moyenne des profils efface le maximum qu'elle cherche, et une saillance entre deux
fenêtres fixes lit la forme du creux qui suit la feuille de la nappe ; les profils moyens des deux groupes, sur la figure de `319`.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P117`. Compter, rayon par rayon, s'il y a un maximum local entre 12 et 28 voxels ne
dépend ni de l'endroit exact de la feuille suivante, que la moyenne efface, ni de la profondeur du creux, que la saillance lisait.

## Ce qui est fait

- **Les rayons** : ceux que `319` a préparés, sans en changer un, depuis les points des nappes du vote de `301` que `m7` appuie, de
  chaque côté, avec leurs deux groupes : `m7` voit une plage à 5 à 30 voxels, ou n'en voit aucune.
- **Un rayon montre une feuille à un pas** si son profil du scan, ramené à moyenne nulle et écart un et lissé sur trois voxels (1, 2,
  1), a un maximum local entre 12 et 28 voxels de proéminence au moins 0,5.
- **Par groupe** : la part des rayons qui montrent une feuille à un pas.

- **Le témoin tangent, ajouté après la première mesure, le 2026-09-29** : les mêmes rayons, mais le long d'une direction du plan de la
  nappe au lieu de sa normale, centrés au même point ; une feuille parallèle à la nappe ne les traverse pas, et la part qui y « montre
  une feuille » est celle que le bruit seul donne. Il ne change pas l'issue, il dit ce qu'elle vaut.

## Les issues

Par côté : **le scan montre la feuille que m7 manque** si la part des rayons où `m7` ne voit rien vaut au moins la moitié de celle où
il voit ; **il ne la montre pas** si elle en vaut moins du quart ; **mêlé** entre les deux ; **non lu** si le témoin, les rayons où `m7`
voit, montre une feuille sur moins de 30 % de ses rayons, ou sous 100 rayons dans un groupe. L'issue : sur k des côtés lus, le scan
montre la feuille que `m7` manque.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : que le maximum soit la spire suivante plutôt qu'une couche de la même feuille.

Usage :
    uv run python src/nappe/rayon_par_rayon_le_scan_montre_t_il_la_feuille_que_m7_manque.py --verifier
    uv run python src/nappe/rayon_par_rayon_le_scan_montre_t_il_la_feuille_que_m7_manque.py \\
        --json docs/mesures/rayon_par_rayon_le_scan_montre_t_il_la_feuille_que_m7_manque.json
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
import le_scan_montre_t_il_la_feuille_que_m7_manque as m319  # noqa: E402

LA_PROEMINENCE = 0.5
LE_TEMOIN_MINIMUM = 0.3


def montre(profils: np.ndarray, u: np.ndarray = m319.LES_U, proeminence: float = LA_PROEMINENCE) -> np.ndarray:
    """Pour chaque profil (n, len(u)), vrai s'il a, une fois normé et lissé, un maximum local entre 12 et 28 voxels de proéminence
    au moins donnée."""
    from scipy.signal import find_peaks

    if not len(profils):
        return np.zeros(0, dtype=bool)
    m = profils.mean(axis=1, keepdims=True)
    s = profils.std(axis=1, keepdims=True)
    z = (profils - m) / np.where(s > 0, s, 1.0)
    lisse = (np.pad(z, ((0, 0), (1, 1)), mode="edge")[:, :-2] * 0.25 + z * 0.5
             + np.pad(z, ((0, 0), (1, 1)), mode="edge")[:, 2:] * 0.25)
    dedans = (u >= 12) & (u <= 28)
    out = np.zeros(len(profils), dtype=bool)
    for k, p in enumerate(lisse):
        pics, _ = find_peaks(p, prominence=proeminence)
        out[k] = bool(dedans[pics].any()) if len(pics) else False
    return out


def la_lecture(f_voit: float | None, f_rien: float | None, n_voit: int, n_rien: int) -> str:
    if (n_voit < m319.LE_MINIMUM or n_rien < m319.LE_MINIMUM or f_voit is None or f_rien is None
            or f_voit < LE_TEMOIN_MINIMUM):
        return "non lu"
    r = f_rien / f_voit
    if r >= 0.5:
        return "le scan montre la feuille que m7 manque"
    if r < 0.25:
        return "il ne la montre pas"
    return "mêlé"


def le_verdict(d: dict) -> dict:
    lus = [c for c in d["les_cotes"] if c["la_lecture"] != "non lu"]
    if not lus:
        return {"decidable": False, "lissue": "indécidable : aucun côté lu"}
    k = sum(1 for c in lus if c["la_lecture"] == "le scan montre la feuille que m7 manque")
    j = sum(1 for c in lus if c["la_lecture"] == "il ne la montre pas")
    return {"decidable": True, "k": k, "j": j, "n": len(lus),
            "lissue": f"rayon par rayon, sur {k} des {len(lus)} côtés lus, le scan montre la feuille que m7 manque ; sur {j}, "
                      "il ne la montre pas"}


def la_tangente(n: np.ndarray) -> np.ndarray:
    """Une direction unitaire du plan perpendiculaire à chaque normale."""
    a = np.where(np.abs(n[:, :1]) < 0.9, np.array([[1.0, 0.0, 0.0]]), np.array([[0.0, 1.0, 0.0]]))
    t = np.cross(n, a)
    return t / np.linalg.norm(t, axis=1, keepdims=True)


def les_profils_lus(vol, coords: np.ndarray, taille) -> tuple[np.ndarray, np.ndarray]:
    """Les profils des coordonnées, après avoir tiré les morceaux qui manquent ; et le masque des profils lus."""
    dedans = m298.dans_le_volume(coords, vol.forme)
    for cle in sorted(m298.les_morceaux_complets(coords[dedans], taille)):
        vol.tirer(*cle)
    prof = np.zeros((len(coords), coords.shape[1]), dtype=np.float32)
    if dedans.any():
        prof[dedans] = m298.les_profils(vol, coords[dedans])
    return prof, dedans & ~m298.sans_matiere(prof)


def mesurer() -> dict:
    t0 = time.monotonic()
    plan = json.loads(m319.LE_PLAN_JSON.read_text())
    z = np.load(m319.LE_PLAN)
    v = m298.LES_VOLUMES["PHerc0358"]
    vol = m298.LesMorceaux("PHerc0358", v["url"], v["niveau"])
    T = m298.la_demi_fenetre("PHerc0358")
    cotes = []
    for c in plan["les_cotes"]:
        base = f"g{c['le_rang']}_{c['le_cote']}"
        pts, nrm, voit = z[f"{base}_points"], z[f"{base}_normales"], z[f"{base}_voit"]
        prof, bon = les_profils_lus(vol, m298.les_coordonnees(pts, nrm, v["facteur"], T), vol.taille)
        tprof, tbon = les_profils_lus(vol, m298.les_coordonnees(pts, la_tangente(nrm), v["facteur"], T), vol.taille)
        e = {"le_rang": c["le_rang"], "le_cote": c["le_cote"]}
        mt = montre(tprof[tbon])
        e["le_temoin_tangent"] = {"les_rayons_lus": int(len(mt)),
                                  "la_part_qui_montre": round(float(mt.mean()), 4) if len(mt) else None}
        for g, masque in (("m7_voit", voit), ("m7_ne_voit_rien", ~voit)):
            mo = montre(prof[bon & masque])
            e[g] = {"les_rayons_lus": int(len(mo)), "la_part_qui_montre": round(float(mo.mean()), 4) if len(mo) else None}
        e["la_lecture"] = la_lecture(e["m7_voit"]["la_part_qui_montre"], e["m7_ne_voit_rien"]["la_part_qui_montre"],
                                     e["m7_voit"]["les_rayons_lus"], e["m7_ne_voit_rien"]["les_rayons_lus"])
        cotes.append(e)
        print(json.dumps(e, ensure_ascii=False), flush=True)
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"la_proeminence": LA_PROEMINENCE, "le_temoin_minimum": LE_TEMOIN_MINIMUM,
                            "le_minimum": m319.LE_MINIMUM}, "les_cotes": cotes}
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

    u = m319.LES_U
    feuille = np.exp(-(u / 3.0) ** 2) + np.exp(-((u - 20.0) / 3.0) ** 2)
    remonte = np.exp(-(u / 3.0) ** 2) - np.exp(-((u - 7.0) / 3.0) ** 2) + np.clip((u - 7.0) / 34.0, 0, None)
    loin = np.exp(-(u / 3.0) ** 2) + np.exp(-((u - 36.0) / 3.0) ** 2)
    m = montre(np.stack([feuille, remonte, loin]))
    v("★★★★ une feuille à un pas se voit ; une remontée sans maximum, non ; une feuille à 36 voxels, non",
      list(m) == [True, False, False], str(m))
    rng = np.random.default_rng(3)
    bruit = rng.normal(0, 0.02, size=(50, len(u))) + feuille[None, :]
    v("★★★ un peu de bruit ne l'efface pas", montre(bruit).mean() > 0.9)
    petit = np.exp(-(u / 3.0) ** 2) + 0.01 * np.exp(-((u - 20.0) / 3.0) ** 2)
    v("★★★ un maximum sous la proéminence ne compte pas", not montre(petit[None, :])[0])
    v("★★★★ montre : la moitié du témoin", la_lecture(0.6, 0.3, 500, 500) == "le scan montre la feuille que m7 manque")
    v("★★★★ ne montre pas : moins du quart", la_lecture(0.6, 0.1, 500, 500) == "il ne la montre pas")
    v("★★★ entre le quart et la moitié : mêlé", la_lecture(0.6, 0.24, 500, 500) == "mêlé")
    v("★★★ un témoin qui ne montre rien ne se lit pas", la_lecture(0.2, 0.2, 500, 500) == "non lu")
    v("★★★ sous 100 rayons : non lu", la_lecture(0.6, 0.6, 500, 99) == "non lu")
    vd = le_verdict({"les_cotes": [{"la_lecture": "le scan montre la feuille que m7 manque"}, {"la_lecture": "non lu"},
                                   {"la_lecture": "il ne la montre pas"}]})
    v("★★★ l'issue : k et j des côtés lus", vd["k"] == 1 and vd["j"] == 1 and vd["n"] == 2)
    n_ = np.array([[0.0, 0.0, 1.0], [1.0, 0.0, 0.0], [0.6, 0.8, 0.0]])
    t_ = la_tangente(n_)
    v("★★★ la tangente : unitaire et perpendiculaire à la normale", np.allclose(np.linalg.norm(t_, axis=1), 1.0)
      and np.allclose((t_ * n_).sum(axis=1), 0.0))

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
