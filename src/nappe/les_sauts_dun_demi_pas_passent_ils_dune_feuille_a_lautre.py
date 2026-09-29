"""Là où une nappe de m7 saute d'un peu plus d'un demi-pas, le scan montre-t-il un creux entre les deux côtés du saut, ou de la matière ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UN SEUL PROFIL DU SCAN NE SOIT LU EN TRAVERS D'UN SAUT. Ce qui était vu avant d'écrire : tout
ce que `301` à `303` publient, dont la taille des sauts de plus d'un demi-pas (médiane de 11,0 à 18,5 voxels, pour un pas de 20).

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P102`. `302` trouve que les nappes de `m7` qui suivent leur feuille sautent, sur un
carré de voisins sur dix, d'un peu plus d'un demi-pas, et ne sait pas lire ces sauts. Un saut de 12 voxels relie deux surfaces
vues par `m7`, face à face. Ce sont soit les deux faces d'une même feuille, et le papyrus est entre elles ; soit les faces de deux
feuilles voisines qui se regardent, et c'est le vide entre elles. Le scan brut, entre les deux côtés du saut, le dit.

## Ce qui est fait

- **Les nappes** : les cinq de `301` qui suivent leur feuille, retirées de `m7` à l'identique (`302`).
- **Les sauts** : les paires de voisins de la grille (quatre voisins), appuyés tous deux sur `m7`, dont les décalages le long de
  la normale de la graine diffèrent de plus d'un demi-pas (10 voxels).
- **Le profil en travers** : au milieu des deux points de la paire, le long de la normale de la graine, le scan en 41 points, du
  côté bas moins la moitié du saut au côté haut plus la moitié du saut (u = −0,5 à 1,5, le côté bas en u = 0, le haut en u = 1).
  Chaque profil est ramené à moyenne nulle et écart un, et les profils d'une nappe sont moyennés.
- **Le témoin**, rapporté : le même profil entre chaque point appuyé de la nappe et le point de sa spire suivante (côté +), le long
  de la normale recalculée de la nappe, u = 0 sur la nappe, u = 1 sur la spire. Ce sont deux feuilles de `m7` distinctes par
  construction ; entre elles, rien n'est promis.

## L'issue, par nappe

Sur le profil moyen en travers des sauts : **un creux** si sa valeur au milieu (u = 0,5) est sous celles de ses deux côtés (u = 0
et u = 1) ; **de la matière** si elle est au-dessus des deux ; **indécidable** sinon, ou sous 30 sauts.

## L'issue de la tranche

**Les sauts d'un demi-pas passent d'une feuille à la voisine** si au moins trois des cinq nappes montrent un creux ; **ils passent
d'une face à l'autre d'une même feuille** si au moins trois montrent de la matière ; indécidable sinon, ou si une nappe retirée ne
redonne pas celle de `301`.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : ce que vaut chaque saut pris seul ; une moyenne tranche pour la plupart. Ni ce que sont les
sauts d'un pas entier, plus rares. Ni que `m7` marque bien les faces des feuilles : c'est l'hypothèse qui donne un sens au test.

Usage :
    uv run python src/nappe/les_sauts_dun_demi_pas_passent_ils_dune_feuille_a_lautre.py --verifier
    uv run python src/nappe/les_sauts_dun_demi_pas_passent_ils_dune_feuille_a_lautre.py --preparer
    uv run python src/nappe/les_sauts_dun_demi_pas_passent_ils_dune_feuille_a_lautre.py --lire 12
    uv run python src/nappe/les_sauts_dun_demi_pas_passent_ils_dune_feuille_a_lautre.py \\
        --json docs/mesures/les_sauts_dun_demi_pas_passent_ils_dune_feuille_a_lautre.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))
sys.path.insert(0, str(RACINE / "src" / "tracecheck"))

import la_matiere_dit_elle_si_la_surface_est_sur_sa_feuille as m298  # noqa: E402
import une_nappe_tiree_de_m7_suit_elle_sa_feuille as m300  # noqa: E402
import les_nappes_de_m7_suivent_elles_leur_feuille_sur_des_graines_neuves as m301  # noqa: E402
import les_nappes_de_m7_tiennent_elles_sur_une_seule_feuille as m302  # noqa: E402

LE_DOSSIER = RACINE / "data" / "sauts_dun_demi_pas"
LE_PLAN = LE_DOSSIER / "plan.npz"
LE_PLAN_JSON = LE_DOSSIER / "plan.json"
LES_U = np.linspace(-0.5, 1.5, 41)
LE_MINIMUM_DE_SAUTS = 30


# ── Les paires et leurs profils ────────────────────────────────────────────────────────────────────────────────────

def les_sauts(decalage: np.ndarray, valide: np.ndarray, appui: np.ndarray, demi: float) -> np.ndarray:
    """Les paires de voisins (quatre voisins), appuyés et valides tous deux, dont les décalages diffèrent de plus de `demi` :
    (n, 4) indices (i1, j1, i2, j2)."""
    ok = valide & appui
    d = np.where(ok, decalage, np.nan)
    out = []
    with np.errstate(invalid="ignore"):
        h = ok[:, 1:] & ok[:, :-1] & (np.abs(d[:, 1:] - d[:, :-1]) > demi)
        v = ok[1:, :] & ok[:-1, :] & (np.abs(d[1:, :] - d[:-1, :]) > demi)
    for i, j in zip(*np.nonzero(h)):
        out.append((i, j, i, j + 1))
    for i, j in zip(*np.nonzero(v)):
        out.append((i, j, i + 1, j))
    return np.array(out, dtype=int).reshape(-1, 4)


def les_positions_en_travers(plan_a, plan_b, d_a, d_b, normale) -> np.ndarray:
    """(41, 3) positions en (x, y, z) : au milieu latéral des deux points, le long de la normale, de u = −0,5 à 1,5, le côté bas
    en u = 0, le haut en u = 1."""
    bas, haut = (d_a, d_b) if d_a <= d_b else (d_b, d_a)
    milieu = (np.asarray(plan_a) + np.asarray(plan_b)) / 2.0
    t = bas + LES_U * (haut - bas)
    return milieu[None, :] + t[:, None] * np.asarray(normale)[None, :]


def le_profil_moyen(profils: np.ndarray) -> list:
    return m298.le_profil_moyen(profils)


def la_forme(profil: list, n: int) -> str:
    """Un creux, de la matière, ou indécidable, par la valeur au milieu contre celles des deux côtés."""
    if n < LE_MINIMUM_DE_SAUTS or not profil:
        return "indécidable"
    p = np.asarray(profil)
    i0, i5, i1 = int(np.argmin(np.abs(LES_U))), int(np.argmin(np.abs(LES_U - 0.5))), int(np.argmin(np.abs(LES_U - 1.0)))
    if p[i5] < p[i0] and p[i5] < p[i1]:
        return "un creux"
    if p[i5] > p[i0] and p[i5] > p[i1]:
        return "de la matière"
    return "indécidable"


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("les_nappes_se_redonnent"):
        return {"decidable": False, "lissue": "indécidable : une nappe retirée ne redonne pas celle de 301"}
    formes = [n["la_forme"] for n in d["les_nappes"]]
    c, m = formes.count("un creux"), formes.count("de la matière")
    if c >= 3:
        return {"decidable": True, "lissue": f"les sauts d'un demi-pas passent d'une feuille à la voisine ({c} nappes sur "
                                             f"{len(formes)})", "creux": c, "matiere": m}
    if m >= 3:
        return {"decidable": True, "lissue": f"les sauts d'un demi-pas passent d'une face à l'autre d'une même feuille ({m} "
                                             f"nappes sur {len(formes)})", "creux": c, "matiere": m}
    return {"decidable": False, "creux": c, "matiere": m,
            "lissue": f"indécidable : {c} nappes montrent un creux, {m} de la matière"}


# ── Les étapes ─────────────────────────────────────────────────────────────────────────────────────────────────────

def preparer() -> dict:
    from la_spire_voisine_est_elle_a_un_pas import les_normales

    t0 = time.monotonic()
    r, identiques = m302.retirer()
    graines = {tuple((g["x"], g["y"], g["z"])): g for g in m301.les_graines_neuves()}
    suivent = {g["le_rang"]: g for g in m302.les_nappes_qui_suivent()}
    demi = m300.LE_PAS_0358 / 2.0
    tableaux, resume = {}, []
    for rang, x in r["les_nappes"].items():
        src = graines[tuple(suivent[rang]["la_graine"])]
        nz, ny, nx = src["normale_zyx"]
        n = np.array([nx, ny, nz], dtype=float)
        n /= np.linalg.norm(n)
        plan = x["la_nappe"] - x["le_decalage"][..., None] * n[None, None, :]
        paires = les_sauts(x["le_decalage"], x["valide"], x["appui"], demi)
        pos = np.stack([les_positions_en_travers(plan[i1, j1], plan[i2, j2], x["le_decalage"][i1, j1],
                                                 x["le_decalage"][i2, j2], n) for i1, j1, i2, j2 in paires]) \
            if len(paires) else np.zeros((0, len(LES_U), 3))
        s = x["les_sauts"]["plus"]
        nn, nok = les_normales(x["la_nappe"], x["valide"])
        m = x["valide"] & x["appui"] & nok & s["valide"] & s["appui"]
        pas_ = s["le_pas"][m]
        base = x["la_nappe"][m]
        ref = base[:, None, :] + (LES_U[None, :] * pas_[:, None])[..., None] * nn[m][:, None, :]
        tableaux[f"g{rang}_sauts"] = pos
        tableaux[f"g{rang}_temoin"] = ref
        tailles = np.abs(x["le_decalage"][paires[:, 2], paires[:, 3]] - x["le_decalage"][paires[:, 0], paires[:, 1]]) \
            if len(paires) else np.zeros(0)
        resume.append({"le_rang": rang, "les_sauts": int(len(paires)), "les_paires_du_temoin": int(m.sum()),
                       "la_taille_mediane_des_sauts_voxels": round(float(np.median(tailles)), 2) if len(tailles) else None,
                       "le_pas_median_du_temoin_voxels": round(float(np.median(np.abs(pas_))), 2) if len(pas_) else None})
    LE_DOSSIER.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(LE_PLAN, **tableaux)
    v = m298.LES_VOLUMES["PHerc0358"]
    vol = m298.LesMorceaux("PHerc0358", v["url"], v["niveau"])
    tous = set()
    for a in tableaux.values():
        if len(a):
            c = a[..., ::-1]
            tous |= m298.les_morceaux_complets(c[m298.dans_le_volume(c, vol.forme)], vol.taille)
    cles = sorted(tous)
    (LE_DOSSIER / "morceaux.json").write_text(json.dumps(cles))
    plan = {"les_nappes_se_redonnent": identiques, "les_pannes": r["les_pannes"], "les_nappes": resume,
            "les_morceaux": {"combien": len(cles)}, "les_secondes": round(time.monotonic() - t0, 1)}
    LE_PLAN_JSON.write_text(json.dumps(plan, ensure_ascii=False, indent=1))
    return plan


def lire(ouvriers: int = 8) -> dict:
    v = m298.LES_VOLUMES["PHerc0358"]
    vol = m298.LesMorceaux("PHerc0358", v["url"], v["niveau"])
    cles = [tuple(c) for c in json.loads((LE_DOSSIER / "morceaux.json").read_text())]
    comptes = {"deja": 0, "tire": 0, "absent": 0}
    with ThreadPoolExecutor(ouvriers) as ex:
        for r in ex.map(lambda c: vol.tirer(*c), cles):
            comptes[r] += 1
    return dict(comptes, combien=len(cles))


def les_profils_de(vol, positions: np.ndarray) -> np.ndarray:
    """Le scan le long de chaque rangée de positions (x, y, z) ; les profils constants ou hors du volume sont écartés."""
    if len(positions) == 0:
        return np.zeros((0, len(LES_U)))
    c = positions[..., ::-1]
    dedans = m298.dans_le_volume(c, vol.forme)
    pr = m298.les_profils(vol, c[dedans]) if dedans.any() else np.zeros((0, len(LES_U)))
    return pr[~m298.sans_matiere(pr)]


def mesurer() -> dict:
    t0 = time.monotonic()
    plan = json.loads(LE_PLAN_JSON.read_text())
    z = np.load(LE_PLAN)
    v = m298.LES_VOLUMES["PHerc0358"]
    vol = m298.LesMorceaux("PHerc0358", v["url"], v["niveau"])
    nappes = []
    for n in plan["les_nappes"]:
        r = n["le_rang"]
        ps = les_profils_de(vol, z[f"g{r}_sauts"])
        pt = les_profils_de(vol, z[f"g{r}_temoin"])
        ms, mt = le_profil_moyen(ps), le_profil_moyen(pt)
        nappes.append(dict(n, les_sauts_lus=int(len(ps)), les_paires_du_temoin_lues=int(len(pt)),
                           le_profil_en_travers_des_sauts=ms, le_profil_du_temoin=mt,
                           la_forme=la_forme(ms, len(ps)), la_forme_du_temoin=la_forme(mt, len(pt))))
    d = {"la_question": __doc__.splitlines()[0], "les_u": [round(float(u), 3) for u in LES_U],
         "les_constantes": {"le_demi_pas_voxels": m300.LE_PAS_0358 / 2.0, "le_minimum_de_sauts": LE_MINIMUM_DE_SAUTS},
         "les_nappes_se_redonnent": plan["les_nappes_se_redonnent"], "les_pannes": plan["les_pannes"],
         "les_nappes": nappes, "les_morceaux": plan["les_morceaux"]}
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

    ok = np.ones((4, 5), dtype=bool)
    d = np.zeros((4, 5))
    d[:, 3:] = 12.0
    s = les_sauts(d, ok, ok, 10.0)
    v("★★★ les sauts : les paires de voisins qui s'écartent de plus d'un demi-pas, et elles seules",
      len(s) == 4 and all(abs(d[a, b] - d[c, e]) > 10 for a, b, c, e in s))
    ap = ok.copy()
    ap[0, 2] = False
    v("★★★ un saut dont un côté n'est pas appuyé sur m7 n'est pas compté", len(les_sauts(d, ok, ap, 10.0)) == 3)
    p = les_positions_en_travers([0.0, 0.0, 0.0], [10.0, 0.0, 0.0], 12.0, 0.0, [0.0, 0.0, 1.0])
    v("★★★ le profil en travers : au milieu latéral, du bas au haut, le côté bas en u = 0 et le haut en u = 1",
      np.allclose(p[:, 0], 5.0) and np.isclose(p[int(np.argmin(np.abs(LES_U))), 2], 0.0)
      and np.isclose(p[int(np.argmin(np.abs(LES_U - 1.0))), 2], 12.0) and np.isclose(p[0, 2], -6.0))
    creux = list(np.cos(2 * np.pi * LES_U))
    bosse = list(-np.cos(2 * np.pi * LES_U))
    v("★★★★ la forme : un creux au milieu, de la matière au milieu, et rien d'autre",
      la_forme(creux, 100) == "un creux" and la_forme(bosse, 100) == "de la matière"
      and la_forme(list(LES_U), 100) == "indécidable" and la_forme(list(-LES_U), 100) == "indécidable"
      and la_forme(creux, 29) == "indécidable")
    N = lambda f: {"la_forme": f}  # noqa: E731
    base = {"les_nappes_se_redonnent": True, "les_nappes": [N("un creux")] * 3 + [N("de la matière")] * 2}
    v("★★★★ l'issue : trois creux sur cinq, les sauts passent d'une feuille à la voisine",
      le_verdict(base)["lissue"].startswith("les sauts d'un demi-pas passent d'une feuille"))
    b2 = dict(base, les_nappes=[N("de la matière")] * 3 + [N("un creux")] * 2)
    v("★★★★ l'issue : trois de matière, d'une face à l'autre", "d'une face à l'autre" in le_verdict(b2)["lissue"])
    b3 = dict(base, les_nappes=[N("un creux")] * 2 + [N("de la matière")] * 2 + [N("indécidable")])
    v("★★★ l'issue : deux et deux, indécidable", not le_verdict(b3)["decidable"])
    v("★★★ l'issue : indécidable si une nappe ne se redonne pas",
      not le_verdict(dict(base, les_nappes_se_redonnent=False))["decidable"])

    for e in echecs:
        print(f"  ÉCHEC {e}")
    print(f"{Path(__file__).name}   {'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--preparer", action="store_true")
    p.add_argument("--lire", type=int, default=None, metavar="OUVRIERS")
    p.add_argument("--json", type=Path, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if a.preparer:
        print(json.dumps(preparer(), ensure_ascii=False, indent=1))
        return 0
    if a.lire is not None:
        print(json.dumps(lire(a.lire), ensure_ascii=False, indent=1))
        return 0
    d = mesurer()
    texte = json.dumps(d, ensure_ascii=False, indent=1)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(texte + "\n")
    print(texte)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
