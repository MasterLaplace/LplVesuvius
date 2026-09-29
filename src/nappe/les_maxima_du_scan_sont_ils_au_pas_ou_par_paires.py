"""Le long de la normale d'une nappe de m7 d'une seule feuille, les maxima du scan sont-ils espacés du pas du rouleau, ou par paires, les deux couches d'une même feuille ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UN SEUL PROFIL LONG NE SOIT LU. Ce qui était vu avant d'écrire : tout ce que `300` à `310`
publient, dont `304` : les sauts d'un peu plus d'un demi-pas des nappes du vote, 12 à 13,5 voxels, ont en travers d'eux un creux, lu
comme le passage à la feuille voisine ; et `308` : le profil moyen de la nappe croissante de la graine 6, sur ±21 voxels, a un
second maximum à −9 voxels de son plus dense.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE. Un pas du rouleau vaut 20 voxels, 187 µm ; deux feuilles à 12,5 voxels l'une de l'autre veulent
dire un pas écrasé à 117 µm. Mais une feuille de papyrus est faite de deux couches de fibres croisées, et deux couches séparées par
un mince creux font aussi deux maxima et un creux entre eux. Les deux lectures diffèrent par ce qui suit : des feuilles écrasées
se suivent à 12,5 voxels, les couches d'une même feuille viennent par paires, un écart court puis un écart long, dont la somme vaut
le pas.

## Ce qui est fait

- **Les nappes** : les nappes croissantes de `305` qui suivent l'empilement (graines 3, 6 et 7), telles que `307` les a préparées ;
  les nappes du vote de `301` des graines 3, 4, 6, 7 et 8, telles qu'elles sont rangées ; et, sur PHercParis4, le tracé humain des
  vingt-quatre blocs neufs de `309`, bloc par bloc.
- **Le profil long** : le scan brut le long de la normale de chaque point, sur deux pas et deux voxels de part et d'autre, chaque
  profil ramené à moyenne nulle et écart un, moyenné par surface.
- **Les maxima** : ceux du profil moyen lissé sur trois voxels (poids 1, 2, 1) dont la proéminence dépasse 0,1.
- **La forme** : les écarts entre maxima consécutifs, comparés au pas p. **Au pas** si tous sont entre 0,75 p et 1,25 p ; si tous
  sont courts (sous 0,75 p), **par paires** quand, groupés deux à deux dans l'ordre (à partir du premier ou du second), chaque
  paire somme entre 0,85 p et 1,15 p, et **serrés** sinon ; **indécidable** avec moins de deux écarts, ou quand courts et longs se
  mêlent.

## L'issue

Sur les nappes d'une seule feuille des graines 3 et 6 (sans déchirure ni boucle ouverte, `R4-F486`) : **les maxima du scan sont
au pas**, **par paires** ou **serrés** si les deux nappes s'accordent ; **les deux nappes ne s'accordent pas** sinon. Le reste est
rapporté. ⚠ Corrigé avant publication, le 2026-09-29 : une nappe dont la forme est indécidable rend la tranche **indécidable**,
et non « les deux nappes ne s'accordent pas », ce que la première version disait de deux nappes indécidables toutes deux.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : ce que sont les deux maxima d'une paire, ni qu'une nappe du vote, qui mêle deux décalages,
donne un profil moyen lisible.

Usage :
    uv run python src/nappe/les_maxima_du_scan_sont_ils_au_pas_ou_par_paires.py --verifier
    uv run python src/nappe/les_maxima_du_scan_sont_ils_au_pas_ou_par_paires.py --preparer
    uv run python src/nappe/les_maxima_du_scan_sont_ils_au_pas_ou_par_paires.py --lire 4
    uv run python src/nappe/les_maxima_du_scan_sont_ils_au_pas_ou_par_paires.py \\
        --json docs/mesures/les_maxima_du_scan_sont_ils_au_pas_ou_par_paires.json
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
import les_nappes_de_m7_suivent_elles_leur_feuille_sur_des_graines_neuves as m301  # noqa: E402
import le_juge_voit_il_lentre_deux_feuilles as m307  # noqa: E402
import un_juge_de_position_separe_t_il_la_feuille_de_lentre_deux as m308  # noqa: E402
import le_plus_dense_dit_il_si_une_surface_est_sur_sa_feuille as m309  # noqa: E402

LE_DOSSIER = RACINE / "data" / "maxima_au_pas"
LE_PLAN = LE_DOSSIER / "plan.json"
LA_PROEMINENCE = 0.1
LES_NAPPES_DUNE_SEULE_FEUILLE = (3, 6)


def le_pas_en_voxels(volume: str) -> float:
    return m308.LES_PAS_UM[volume] / m298.LES_VOLUMES[volume]["le_voxel_um"]


def la_demi_fenetre_longue(volume: str) -> int:
    """Deux pas et deux voxels, arrondis."""
    return int(round(2.0 * le_pas_en_voxels(volume))) + 2


def les_maxima(profil: list, proeminence: float = LA_PROEMINENCE) -> list[int]:
    """Les décalages, en voxels le long de la normale, des maxima du profil lissé (1, 2, 1) de proéminence au moins donnée."""
    from scipy.signal import find_peaks

    if len(profil) < 5:
        return []
    p = np.asarray(profil, dtype=float)
    lisse = np.convolve(np.pad(p, 1, mode="edge"), [0.25, 0.5, 0.25], mode="valid")
    pics, _ = find_peaks(lisse, prominence=proeminence)
    return [int(i) - len(p) // 2 for i in pics]


def la_forme(maxima: list[int], pas: float) -> str:
    e = np.diff(sorted(maxima)).astype(float)
    if len(e) < 2:
        return "indécidable"
    if all(0.75 * pas <= x <= 1.25 * pas for x in e):
        return "au pas"
    if all(x < 0.75 * pas for x in e):
        for phase in (0, 1):
            ks = range(phase, len(e) - 1, 2)
            if len(ks) and all(0.85 * pas <= e[k] + e[k + 1] <= 1.15 * pas for k in ks):
                return "par paires"
        return "serrés"
    return "indécidable"


def le_verdict(d: dict) -> dict:
    formes = [n["la_forme"] for n in d["phercs0358"] if n["la_surface"] in
              [f"croissante_g{r}" for r in LES_NAPPES_DUNE_SEULE_FEUILLE]]
    if len(formes) != len(LES_NAPPES_DUNE_SEULE_FEUILLE):
        return {"decidable": False, "lissue": "indécidable : une nappe d'une seule feuille manque"}
    if "indécidable" in formes:
        return {"decidable": False, "la_forme": None,
                "lissue": f"indécidable : le profil moyen long ne garde pas assez de maxima pour dire ({formes[0]} et "
                          f"{formes[1]})"}
    if len(set(formes)) == 1:
        f = formes[0]
        return {"decidable": True, "la_forme": f,
                "lissue": f"sur les deux nappes d'une seule feuille, les maxima du scan sont {f}"}
    return {"decidable": True, "la_forme": None,
            "lissue": f"les deux nappes d'une seule feuille ne s'accordent pas : {formes[0]} et {formes[1]}"}


# ── Les étapes ─────────────────────────────────────────────────────────────────────────────────────────────────────

def les_surfaces() -> dict:
    from la_spire_voisine_est_elle_a_un_pas import les_normales

    out = {"PHerc0358": {}, "PHercParis4": {}}
    plan307 = json.loads(m307.LE_PLAN.read_text())
    for cle, info in plan307["les_surfaces"].items():
        if cle.startswith("PHerc0358__g") and cle.endswith("_p0"):
            r = int(cle.split("__g")[1].split("_")[0])
            f = np.load(RACINE / info["le_fichier"])
            out["PHerc0358"][f"croissante_g{r}"] = [(f["points"], f["normales"])]
    z = np.load(m301.LES_NAPPES)
    for r in (3, 4, 6, 7, 8):
        pts, ok = z[f"g{r}_nappe"], z[f"g{r}_nappe_ok"]
        nn, nok = les_normales(pts, ok)
        m = ok & nok
        out["PHerc0358"][f"vote_g{r}"] = [(pts[m], nn[m])]
    plan309 = json.loads(m309.LE_PLAN.read_text())
    f = np.load(RACINE / plan309["les_surfaces"]["PHercParis4__p0"]["le_fichier"])
    for i, b in enumerate(plan309["les_blocs"]):
        m = f["groupe"] == i
        out["PHercParis4"][f"bloc_{b[0]}_{b[1]}"] = [(f["points"][m], f["normales"][m])]
    return out


def preparer() -> dict:
    t0 = time.monotonic()
    plan = {"les_morceaux": {}}
    for volume, surfaces in les_surfaces().items():
        v = m298.LES_VOLUMES[volume]
        vol = m298.LesMorceaux(volume, v["url"], v["niveau"])
        T = la_demi_fenetre_longue(volume)
        tous = set()
        for morceaux in surfaces.values():
            for pts, nrm in morceaux:
                if len(pts):
                    c = m298.les_coordonnees(pts, nrm, v["facteur"], T)
                    tous |= m298.les_morceaux_complets(c[m298.dans_le_volume(c, vol.forme)], vol.taille)
        cles = sorted(tous)
        LE_DOSSIER.mkdir(parents=True, exist_ok=True)
        (LE_DOSSIER / f"morceaux_{volume}.json").write_text(json.dumps(cles))
        plan["les_morceaux"][volume] = {"combien": len(cles)}
    plan["les_secondes"] = round(time.monotonic() - t0, 1)
    LE_PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=1))
    return plan


def lire(ouvriers: int = 4) -> dict:
    out = {}
    for volume, v in m298.LES_VOLUMES.items():
        cles = [tuple(c) for c in json.loads((LE_DOSSIER / f"morceaux_{volume}.json").read_text())]
        vol = m298.LesMorceaux(volume, v["url"], v["niveau"])
        comptes = {"deja": 0, "tire": 0, "absent": 0}
        with ThreadPoolExecutor(ouvriers) as ex:
            for r in ex.map(lambda c: vol.tirer(*c), cles):
                comptes[r] += 1
        out[volume] = dict(comptes, combien=len(cles))
    return out


def le_profil_long(vol, pts, nrm, facteur, T) -> tuple[list, int]:
    if not len(pts):
        return [], 0
    c = m298.les_coordonnees(pts, nrm, facteur, T)
    dedans = m298.dans_le_volume(c, vol.forme)
    if not dedans.any():
        return [], 0
    prof = m298.les_profils(vol, c[dedans])
    prof = prof[~m298.sans_matiere(prof)]
    return m298.le_profil_moyen(prof), int(len(prof))


def mesurer() -> dict:
    t0 = time.monotonic()
    d = {"la_question": __doc__.splitlines()[0], "les_constantes": {"la_proeminence": LA_PROEMINENCE}}
    for volume, surfaces in les_surfaces().items():
        v = m298.LES_VOLUMES[volume]
        vol = m298.LesMorceaux(volume, v["url"], v["niveau"])
        T, pas = la_demi_fenetre_longue(volume), le_pas_en_voxels(volume)
        d["les_constantes"][volume] = {"la_demi_fenetre_voxels": T, "le_pas_voxels": round(pas, 3)}
        lignes = []
        for nom, morceaux in surfaces.items():
            profil, n = le_profil_long(vol, *morceaux[0], v["facteur"], T)
            mx = les_maxima(profil)
            lignes.append({"la_surface": nom, "les_points_juges": n, "les_maxima": mx,
                           "les_ecarts": [int(x) for x in np.diff(mx)], "la_forme": la_forme(mx, pas),
                           "le_profil_moyen": profil})
        d["phercs0358" if volume == "PHerc0358" else "paris4"] = lignes
        print(f"{volume} ({time.monotonic() - t0:.0f} s)", flush=True)
    formes = [x["la_forme"] for x in d["paris4"]]
    d["paris4_les_formes"] = {f: formes.count(f) for f in ("au pas", "par paires", "serrés", "indécidable")}
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

    v("★★★ la demi-fenêtre longue : deux pas et deux voxels", la_demi_fenetre_longue("PHerc0358") == 42
      and la_demi_fenetre_longue("PHercParis4") == 38)
    u = np.arange(-42, 43)
    au_pas = list(np.cos(2 * np.pi * u / 20.0))
    v("★★★★ des maxima au pas du rouleau", les_maxima(au_pas) == [-40, -20, 0, 20, 40]
      and la_forme(les_maxima(au_pas), 20.0) == "au pas", str(les_maxima(au_pas)))
    paires = sum(np.exp(-((u - c) / 2.0) ** 2) for c in (-40, -27.5, -20, -7.5, 0, 12.5, 20, 32.5, 40))
    v("★★★★ des maxima par paires : 12,5 puis 7,5, qui somment au pas",
      la_forme(les_maxima(list(paires)), 20.0) == "par paires", str(les_maxima(list(paires))))
    serres = sum(np.exp(-((u - c) / 2.0) ** 2) for c in (-37.5, -25, -12.5, 0, 12.5, 25, 37.5))
    v("★★★★ des maxima serrés à 12,5", la_forme(les_maxima(list(serres)), 20.0) == "serrés")
    v("★★★ trop peu de maxima : indécidable", la_forme([0, 20], 20.0) == "indécidable" and la_forme([], 20.0) == "indécidable")
    v("★★★ les paires se cherchent à partir du premier écart comme du second",
      la_forme([0, 8, 20, 32], 20.0) == "par paires" and la_forme([0, 12, 24, 32], 20.0) == "par paires")
    encoche = list(np.cos(2 * np.pi * u / 20.0))
    encoche[42] = 0.9
    v("★★★ le lissage efface une encoche d'un voxel au sommet d'un maximum", les_maxima(encoche) == les_maxima(au_pas),
      str(les_maxima(encoche)))
    v("★★★ courts et longs mêlés : indécidable", la_forme([0, 20, 25, 45], 20.0) == "indécidable")
    v("★★★ deux écarts de 12,5 ne font pas une paire : ils somment à 25, hors de 0,85 à 1,15 pas",
      la_forme([0, 12, 25, 37], 20.0) == "serrés")
    v("★★★ un écart trop long : indécidable, pas au pas", la_forme([0, 20, 50], 20.0) == "indécidable")
    bruit = list(0.02 * np.sin(u * 1.7))
    v("★★★ sous la proéminence, pas de maximum", les_maxima(bruit) == [])
    ok_ = le_verdict({"phercs0358": [{"la_surface": "vote_g4", "la_forme": "serrés"},
                                     {"la_surface": "croissante_g3", "la_forme": "par paires"},
                                     {"la_surface": "croissante_g6", "la_forme": "par paires"}]})
    v("★★★★ l'issue : les deux nappes d'une seule feuille, et elles seules", ok_["la_forme"] == "par paires")
    ko = le_verdict({"phercs0358": [{"la_surface": "croissante_g3", "la_forme": "au pas"},
                                    {"la_surface": "croissante_g6", "la_forme": "par paires"}]})
    v("★★★ l'issue : deux nappes qui ne s'accordent pas", ko["la_forme"] is None and "ne s'accordent pas" in ko["lissue"])
    v("★★★ l'issue : indécidable si une nappe ne garde pas assez de maxima",
      not le_verdict({"phercs0358": [{"la_surface": "croissante_g3", "la_forme": "indécidable"},
                                     {"la_surface": "croissante_g6", "la_forme": "indécidable"}]})["decidable"])
    v("★★★ l'issue : indécidable s'il en manque une",
      not le_verdict({"phercs0358": [{"la_surface": "croissante_g3", "la_forme": "au pas"}]})["decidable"])

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
    print(json.dumps(d["le_verdict"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
