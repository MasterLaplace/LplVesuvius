"""Le rendu qui lira PHerc0358, appliqué au bloc étalon de PHercParis4 depuis son niveau de 9,6 µm, lit-il l'encre, et dans quel sens des couches ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE CE RENDU NE SOIT LU PAR LE DÉTECTEUR. Ce qui était vu avant d'écrire : tout ce que `296` à `408`
publient, dont **`R4-F594`** (`408` : le bloc étalon de `296` ramené à 9,6 µm par moyenne de bloc se lit encore à 0,869 contre la carte
publiée, mais les mêmes couches dans l'ordre inverse ne donnent que −0,0261). Le rendu de ce fichier n'a jamais été lu.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P206`. Le détecteur ne lit que dans un sens des couches, et les normales des surfaces de
PHerc0358 n'ont pas d'orientation connue. La courbure en donne une : une feuille d'un rouleau se creuse vers son axe. Lire le bloc étalon
de PHercParis4 par le rendu même qui lira PHerc0358, les couches empilées dans les deux sens rapportés au creux de la feuille, fixe le
sens sur un juge, la carte d'encre publiée, avant de lire PHerc0358.

## Ce qui est fait

- **La surface** : le maillage du segment de `296` sous le bloc étalon 176_144, ramené au niveau 2 de PHercParis4, 9,6 µm.
- **Le creux** : la normale moyenne de la surface, orientée du côté où ses bords s'écartent du plan de son centre ; c'est là que la
  feuille se creuse.
- **Le rendu**, celui qui lira PHerc0358 : chaque pixel du bloc, à 2,4 µm, placé sur la surface ; le scan du niveau 2 lu en trilinéaire
  le long des normales, les couches 23 à 84 d'une pile dont la surface est la couche 54. **Deux piles** : les couches croissant vers le
  creux, et vers la bosse.
- **Le détecteur** de `296`, sur l'iGPU, une lecture par processus, et la comparaison de son étalonnage, contre la carte sous le bloc et
  la carte décalée de 64 pixels.
- **La règle** : si un sens donne au moins 0,8 et plus que son témoin, et l'autre moins de 0,5, **ce sens est fixé** ; si aucun ne donne
  0,8, **non, le rendu ne lit pas** ; si les deux donnent au moins 0,5, **indécidable, les deux sens lisent**.

## Les issues

L'issue de la tranche : **vers le creux, c ; vers la bosse, b ; témoins t et u**, puis le sens fixé.

## Rapporté à côté, qui ne décide rien

La corrélation entre la couche de la surface de ce rendu et celle de la pile ramenée de `408` ; les téléchargements du niveau 2 ; le temps.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : si la courbure de PHerc0358 se lit aussi bien sur ses surfaces de 6 mm ; rien sur l'encre de
PHerc0358.

Usage :
    uv run python src/nappe/le_rendu_de_pherc0358_lit_il_lencre_de_paris4_et_dans_quel_sens.py --verifier
    uv run python src/nappe/le_rendu_de_pherc0358_lit_il_lencre_de_paris4_et_dans_quel_sens.py --rendre
    uv run --project src/xpu --with albumentations --with zarr --with tqdm --with numcodecs --with imagecodecs \\
        python src/nappe/le_rendu_de_pherc0358_lit_il_lencre_de_paris4_et_dans_quel_sens.py --encre --sens creux
    uv run python src/nappe/le_rendu_de_pherc0358_lit_il_lencre_de_paris4_et_dans_quel_sens.py \\
        --json docs/mesures/le_rendu_de_pherc0358_lit_il_lencre_de_paris4_et_dans_quel_sens.json
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

import le_tour_produit_porte_t_il_le_texte_du_segment as m296  # noqa: E402

LE_DOSSIER = RACINE / "data" / "encre_rendu_paris4"
LA_COUCHE_DE_LA_SURFACE = 54
LE_NIVEAU, LE_FACTEUR = 2, 4
LES_SENS = ("creux", "bosse")
LE_SEUIL, LE_PLANCHER = m296.LE_SEUIL_DETALONNAGE, 0.5


def la_grille_aux_indices(nappe: np.ndarray, valide: np.ndarray, ii: np.ndarray, jj: np.ndarray):
    """Les positions (x, y, z) et normales unitaires de la surface aux indices de grille fractionnaires (`ii`, `jj`), et les pixels dont
    les quatre sommets voisins sont valides et ont une normale."""
    from scipy.ndimage import map_coordinates

    from la_spire_voisine_est_elle_a_un_pas import les_normales

    n, nok = les_normales(nappe, valide)
    ok = valide & nok
    p = np.stack([map_coordinates(nappe[..., c], [ii, jj], order=1) for c in range(3)], -1)
    nn = np.stack([map_coordinates(np.where(ok, n[..., c], 0.0), [ii, jj], order=1) for c in range(3)], -1)
    couvert = map_coordinates(ok.astype(float), [ii, jj], order=1) >= 1.0 - 1e-9
    norme = np.linalg.norm(nn, axis=-1)
    nn = nn / np.where(norme > 0, norme, 1.0)[..., None]
    return p, nn, couvert & (norme > 0)


def le_sens_du_creux(nappe: np.ndarray, valide: np.ndarray) -> float:
    """+1 si la normale de la grille pointe vers le creux de la surface, −1 sinon : le signe de la courbure moyenne, lu comme l'écart
    des sommets au plan du centre, le long de la normale moyenne, ajusté en a·r²."""
    from la_spire_voisine_est_elle_a_un_pas import les_normales

    n, nok = les_normales(nappe, valide)
    m = valide & nok
    p, nm = nappe[m], n[m].mean(axis=0)
    nm = nm / np.linalg.norm(nm)
    c = p.mean(axis=0)
    h = (p - c) @ nm
    r2 = np.sum((p - c - h[:, None] * nm) ** 2, axis=1)
    a = np.polyfit(r2, h, 1)[0]
    return 1.0 if a > 0 else -1.0


def les_decalages_des_couches(pixel: float) -> np.ndarray:
    """Le décalage le long de la normale, en voxels du volume lu, de chaque couche que lit le détecteur."""
    z0, z1 = m296.LES_COUCHES
    return (np.arange(z0, z1) - LA_COUCHE_DE_LA_SURFACE) * pixel


def rendre(p: np.ndarray, nn: np.ndarray, couvert: np.ndarray, decalage: float, pixel: float, lire_profils, bande: int = 32) -> np.ndarray:
    """La pile (y, x, couche) en uint8 : le scan lu le long des normales `nn`, à `decalage` voxels de la surface, les couches croissant
    dans le sens de `nn` ; zéro hors de la surface. `lire_profils(coords)` lit des profils (n, L, 3) en (z, y, x)."""
    t = les_decalages_des_couches(pixel)
    h, w = couvert.shape
    pile = np.zeros((h, w, len(t)), np.uint8)
    for y0 in range(0, h, bande):
        sl = slice(y0, min(h, y0 + bande))
        m = couvert[sl]
        if not m.any():
            continue
        q, n = p[sl][m] + decalage * nn[sl][m], nn[sl][m]
        coords = (q[:, None, :] + t[None, :, None] * n[:, None, :])[..., ::-1]
        bloc = pile[sl]
        bloc[m] = np.clip(np.rint(lire_profils(coords)), 0, 255).astype(np.uint8)
    return pile


def la_surface_du_bloc() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Le maillage du segment sous le bloc étalon, au niveau 2, et les indices de grille de chaque pixel du bloc."""
    ref, ref_ok, _, _, esp = m296.les_maillages()
    by, bx = m296.LE_BLOC_ETALON
    cote = m296.LE_CHUNK * m296.LE_BLOC
    ii, jj = np.meshgrid((by * m296.LE_CHUNK + np.arange(cote)) / esp, (bx * m296.LE_CHUNK + np.arange(cote)) / esp, indexing="ij")
    return ref / LE_FACTEUR, ref_ok, (ii, jj)


def le_volume():
    import la_matiere_dit_elle_si_la_surface_est_sur_sa_feuille as mm

    return mm, mm.LesMorceaux("PHercParis4", mm.LES_VOLUMES["PHercParis4"]["url"], LE_NIVEAU)


def les_morceaux_du_rendu(p, nn, couvert, pixel, taille) -> set:
    """Les morceaux du niveau 2 que les deux piles lisent, voisins de l'interpolation compris."""
    t = np.abs(les_decalages_des_couches(pixel)).max() + 2.0
    q = p[couvert]
    lo, hi = np.floor((q.min(axis=0) - t)[::-1]).astype(int), np.floor((q.max(axis=0) + t)[::-1]).astype(int) + 1
    tz = np.asarray(taille)
    return {(cz, cy, cx) for cz in range(lo[0] // tz[0], hi[0] // tz[0] + 1) for cy in range(lo[1] // tz[1], hi[1] // tz[1] + 1)
            for cx in range(lo[2] // tz[2], hi[2] // tz[2] + 1)}


def preparer_et_rendre() -> int:
    """Le creux, les morceaux tirés s'il en manque, et les deux piles sur le disque."""
    nappe, valide, (ii, jj) = la_surface_du_bloc()
    sous = (slice(int(ii.min()) - 1, int(ii.max()) + 3), slice(int(jj.min()) - 1, int(jj.max()) + 3))
    s = le_sens_du_creux(nappe[sous], valide[sous])
    p, nn, couvert = la_grille_aux_indices(nappe, valide, ii, jj)
    pixel = 1.0 / LE_FACTEUR
    mm, vol = le_volume()
    tires = {"deja": 0, "tire": 0, "absent": 0}
    for cle in sorted(les_morceaux_du_rendu(p, nn, couvert, pixel, vol.taille)):
        tires[vol.tirer(*cle)] += 1
    LE_DOSSIER.mkdir(parents=True, exist_ok=True)
    rendus = {}
    for sens, signe in (("creux", s), ("bosse", -s)):
        t0 = time.monotonic()
        pile = rendre(p, signe * nn, couvert, 0.0, pixel, lambda c: mm.les_profils(vol, c))
        np.save(LE_DOSSIER / f"pile_{sens}.npy", pile)
        rendus[sens] = round(time.monotonic() - t0, 1)
    np.save(LE_DOSSIER / "couvert.npy", couvert)
    plan = {"le_sens_du_creux": s, "les_morceaux": tires, "le_rendu_en_secondes": rendus, "la_couverture": round(float(couvert.mean()), 4)}
    (LE_DOSSIER / "plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1) + "\n")
    print(json.dumps(plan, ensure_ascii=False), flush=True)
    return 0


def encre(sens: str) -> int:
    import le_detecteur_de_296_lit_il_encore_lencre_de_paris4_ramenee_a_9um as m408

    pile = np.load(LE_DOSSIER / f"pile_{sens}.npy")
    r = m408.lencre(pile, LE_DOSSIER / f"encre_{sens}.npy")
    with (LE_DOSSIER / "encre.out").open("a") as o:
        o.write(json.dumps({"le_sens": sens, **r}, ensure_ascii=False) + "\n")
    print(json.dumps({"le_sens": sens, **r}, ensure_ascii=False), flush=True)
    return 0


def le_verdict(d: dict) -> dict:
    c, b = d["les_lectures"].get("creux"), d["les_lectures"].get("bosse")
    if c is None or b is None or c["la_correlation"] is None or b["la_correlation"] is None:
        return {"decidable": False, "lissue": "indécidable : une des deux lectures manque"}
    f = lambda x: f"{x:g}".replace(".", ",")  # noqa: E731
    tete = (f"vers le creux, {f(c['la_correlation'])} ; vers la bosse, {f(b['la_correlation'])} ; "
            f"témoins {f(c['le_temoin'])} et {f(b['le_temoin'])}")
    lit = {s: x["la_correlation"] >= LE_SEUIL and x["la_correlation"] > x["le_temoin"] for s, x in (("creux", c), ("bosse", b))}
    if c["la_correlation"] >= LE_PLANCHER and b["la_correlation"] >= LE_PLANCHER:
        return {"decidable": False, "lissue": f"{tete} ; indécidable, les deux sens lisent"}
    for s, autre in (("creux", b), ("bosse", c)):
        if lit[s] and autre["la_correlation"] < LE_PLANCHER:
            return {"decidable": True, "lissue": f"{tete} ; le sens est fixé : vers {'le creux' if s == 'creux' else 'la bosse'}",
                    "le_sens": s}
    return {"decidable": True, "lissue": f"{tete} ; non, le rendu ne lit pas"}


def mesurer() -> dict:
    import le_detecteur_de_296_lit_il_encore_lencre_de_paris4_ramenee_a_9um as m408

    carte = m296.la_carte_publiee()
    plan = json.loads((LE_DOSSIER / "plan.json").read_text())
    lectures = {s: m408.la_lecture(np.load(LE_DOSSIER / f"encre_{s}.npy"), carte) for s in LES_SENS
                if (LE_DOSSIER / f"encre_{s}.npy").exists()}
    surface = None
    if (m408.LE_DOSSIER / "etalon_ramene_4.npy").exists():
        a = np.load(LE_DOSSIER / "pile_creux.npy")[..., LA_COUCHE_DE_LA_SURFACE - m296.LES_COUCHES[0]].astype(float)
        b = m408.le_bloc_ramene(4)[..., LA_COUCHE_DE_LA_SURFACE - m296.LES_COUCHES[0]].astype(float)
        surface = m296.correlation(a, b, np.load(LE_DOSSIER / "couvert.npy"))[0]
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"le_niveau": LE_NIVEAU, "le_facteur": LE_FACTEUR, "le_seuil": LE_SEUIL, "le_plancher": LE_PLANCHER},
         "le_plan": plan, "les_lectures": lectures, "la_surface_contre_408": surface,
         "les_temps": [json.loads(l) for l in (LE_DOSSIER / "encre.out").read_text().splitlines()] if (LE_DOSSIER / "encre.out").exists() else []}
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

    ii, jj = np.meshgrid(np.arange(21.0), np.arange(21.0), indexing="ij")
    x, y = (jj - 10) * 10.0, (ii - 10) * 10.0
    bol = np.stack([x, y, (x ** 2 + y ** 2) / 400.0], -1)
    ok = np.ones((21, 21), bool)
    from la_spire_voisine_est_elle_a_un_pas import les_normales
    n, _ = les_normales(bol, ok)
    vers_le_haut = float(np.sign(n[10, 10, 2]))
    v("★★★★ un bol se creuse vers le haut : la normale de la grille pointe vers le creux si et seulement si elle monte",
      le_sens_du_creux(bol, ok) == vers_le_haut and le_sens_du_creux(bol * [1, 1, -1], ok) == -float(np.sign(les_normales(bol * [1, 1, -1], ok)[0][10, 10, 2])))
    plan_ = np.stack([x, y, np.zeros_like(x)], -1)
    fi, fj = np.meshgrid(np.arange(0, 20, 0.5), np.arange(0, 20, 0.5), indexing="ij")
    p, nn, couvert = la_grille_aux_indices(plan_, ok, fi, fj)
    v("★★★★ la grille aux indices place chaque pixel sur la surface, avec des normales unitaires",
      np.allclose(p[couvert][:, 2], 0.0) and np.allclose(np.linalg.norm(nn[couvert], axis=-1), 1.0) and np.allclose(p[2, 2], [-90.0, -90.0, 0.0]))
    t = les_decalages_des_couches(0.25)
    v("★★★★ la couche 54 est la surface, 62 couches de 23 à 84", len(t) == 62 and t[54 - 23] == 0.0 and t[0] == -31 * 0.25)
    vu = []
    pile = rendre(p, nn, couvert, 0.0, 0.25, lambda c: (vu.append(c) or c[..., 0] * 0 + np.arange(c.shape[1])[None, :]), bande=8)
    v("★★★★ la pile croît dans le sens des normales, la surface à la couche 54, zéro hors de la surface",
      pile.shape == (40, 40, 62) and pile[~couvert].max() == 0
      and np.allclose(np.concatenate(vu)[:, 1, ::-1] - np.concatenate(vu)[:, 0, ::-1], 0.25 * nn[couvert][:1].repeat(1, 0)[0], atol=1e-9)
      if couvert.any() else False)
    tz = (4, 4, 4)
    v("★★★★ les morceaux du rendu couvrent la surface et ses couches, voisins compris",
      (0, 0, 0) in les_morceaux_du_rendu(p, nn, couvert, 0.25, tz)
      and any(c[0] == -3 for c in les_morceaux_du_rendu(p, nn, couvert, 0.25, tz)))

    lu = lambda c, b, tc=0.05, tb=0.05: {"les_lectures": {"creux": {"la_correlation": c, "le_temoin": tc},  # noqa: E731
                                                          "bosse": {"la_correlation": b, "le_temoin": tb}}}
    v("★★★★ la règle : un sens à 0,8 et l'autre sous 0,5, ce sens ; aucun à 0,8, non ; les deux à 0,5, indécidable",
      le_verdict(lu(0.85, 0.02))["le_sens"] == "creux" and le_verdict(lu(0.01, 0.82))["le_sens"] == "bosse"
      and le_verdict(lu(0.7, 0.1))["lissue"].endswith("; non, le rendu ne lit pas")
      and not le_verdict(lu(0.85, 0.6))["decidable"])
    v("★★★★ l'issue dit les deux corrélations et les deux témoins",
      le_verdict(lu(0.85, 0.02))["lissue"] == "vers le creux, 0,85 ; vers la bosse, 0,02 ; témoins 0,05 et 0,05 ; le sens est fixé : vers le creux")
    v("★★★ un sens qui ne dépasse pas son témoin n'est pas fixé", "le_sens" not in le_verdict(lu(0.85, 0.02, tc=0.9)))

    for e in echecs:
        print(f"  ÉCHEC {e}")
    print(f"{Path(__file__).name}   {'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--rendre", action="store_true", help="le creux, les morceaux et les deux piles")
    p.add_argument("--encre", action="store_true", help="le détecteur sur une pile, sur l'iGPU")
    p.add_argument("--sens", choices=LES_SENS, default=None)
    p.add_argument("--json", type=Path, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if a.rendre:
        return preparer_et_rendre()
    if a.encre:
        return encre(a.sens)
    d = mesurer()
    texte = json.dumps(d, ensure_ascii=False, indent=1)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(texte + "\n")
    print(json.dumps(d["le_verdict"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
