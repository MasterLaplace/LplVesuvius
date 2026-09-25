"""Repartir de la spire corrigée rend-il le saut suivant plus juste ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LA CHAÎNE NE REPARTE DE LA SPIRE CORRIGÉE. Ce qui était vu avant d'écrire : tout ce que
`248` et `257` à `275` publient. `275` corrige la spire produite sur les 340 blocs candidats du segment, en une passe et sans
juge : 163 ratés rendus justes pour 41 justes rendus ratés. Mais `248` a montré qu'un saut raté est définitif : la chaîne
reste décalée d'une spire pour tous les sauts suivants. Corriger le premier saut ne sert que si le saut suivant, parti de
lui, retombe sur la bonne spire.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P95`. Ce qui remplace l'humain qui corrige le transfert doit tenir de spire en
spire : la spire corrigée n'est un progrès pour le déroulement que si la chaîne repart d'elle mieux que de la spire produite.

## La procédure

La chaîne de `248` sur le segment `20230702185753`, la prédiction `m7`, du côté plus, quatre sauts, sans rien y changer, deux
fois :
- partie du segment, comme `248` : son premier saut est la spire produite, et c'est le témoin ;
- partie de la spire corrigée de `275` : son premier saut n'est pas lu, il est la spire corrigée, et les sauts suivants sont
  ceux de `248`, chacun parti de la surface que le précédent a produite, le long de SA normale.
Le juge est celui de `248` : au saut h, un point est sur la bonne spire s'il est à moins d'un demi-feuillet de la h-ième couche
du segment, le long de la normale du segment. Le juge ne sert qu'à noter.

⚠ Le témoin doit redonner `248` : son premier saut égal à la spire produite, et à chaque saut les points notés et la part sur
la bonne spire publiés. Sinon la mesure est indécidable. Elle l'est aussi si une lecture de la prédiction tombe en panne.

## Les issues, exclusives, au deuxième saut

- parmi les points notés au deuxième saut, ceux que la chaîne partie de la spire corrigée rend justes là où le témoin les
  ratait sont plus nombreux que ceux qu'elle rend ratés là où il était juste : repartir de la spire corrigée rend le saut
  suivant plus juste ;
- ils ne le sont pas : elle ne le rend pas plus juste.

⚠ Rapporté à côté : les mêmes comptes au premier saut, sous ce juge, et aux troisième et quatrième, que la troisième couche du
segment ne note presque nulle part ; parmi les points notés aux deux premiers sauts dont le premier passe de raté à juste, la
part juste au deuxième saut, pour les deux chaînes.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : une correction du deuxième saut ; l'autre côté, l'autre prédiction ; la bande de `248`,
sur laquelle `275` n'a rien corrigé.

Usage :
    uv run python src/nappe/repartir_de_la_spire_corrigee_rend_il_le_saut_suivant_plus_juste.py --verifier
    uv run python src/nappe/repartir_de_la_spire_corrigee_rend_il_le_saut_suivant_plus_juste.py \\
        --json docs/mesures/repartir_de_la_spire_corrigee_rend_il_le_saut_suivant_plus_juste.json
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

from la_procedure_sans_juge_tient_elle_sur_le_segment_entier import LA_SPIRE_CORRIGEE  # noqa: E402
from la_spire_produite_se_lit_elle_dans_le_treillis import LA_PREDICTION, LE_COTE  # noqa: E402
from la_spire_voisine_est_elle_a_un_pas import (DEMI_PAS_EN_VOXELS, LE_CACHE, LE_SEGMENT,  # noqa: E402
                                                les_normales, lire_tifxyz, telecharger)
from le_transfert_enchaine_tient_il_les_spires import (LES_SAUTS, enchainer, juger_le_saut,  # noqa: E402
                                                       les_couches_ordonnees, lire_le_rayon)
from le_transfert_retrouve_t_il_la_spire_voisine import (DELAI, LA_MAILLE, LES_PREDICTIONS,  # noqa: E402
                                                         le_facteur, lecteur_du_depot)

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_248_A_PUBLIE = LES_MESURES / "le_transfert_enchaine_sur_le_segment_5753.json"
LA_SPIRE_PRODUITE = LE_CACHE / f"transfert_suivante_{LE_SEGMENT}_{LA_PREDICTION}_{LE_COTE}.npy"
# ⚠ Ce que la chaîne partie de la spire corrigée atteint au deuxième saut, gardé pour la tranche qui le corrigera.
LE_DEUXIEME_SAUT = LE_CACHE / f"deuxieme_saut_depuis_la_corrigee_265_{LE_SEGMENT}_{LA_PREDICTION}_{LE_COTE}.npy"
LE_SIGNE = {"du_cote_plus": 1.0, "du_cote_moins": -1.0}[LE_COTE]


def les_profondeurs(chaine: list[dict], p: np.ndarray, n: np.ndarray) -> list[np.ndarray]:
    """La profondeur atteinte à chaque saut, le long de la normale du segment, comme `248` la juge."""
    return [np.einsum("ij,ij->i", s["q"] - p, n) for s in chaine]


def les_justes(tau: np.ndarray, verite: np.ndarray) -> np.ndarray:
    """Les points notés que la profondeur met sur la bonne spire ; un point non noté n'est pas juste."""
    with np.errstate(invalid="ignore"):
        return np.isfinite(verite) & (np.abs(tau - verite) < DEMI_PAS_EN_VOXELS)


def le_bilan_du_saut(tau_t: np.ndarray, tau_c: np.ndarray, verite: np.ndarray) -> dict:
    """Le témoin et la chaîne partie de la spire corrigée, sur les points notés du saut."""
    note = np.isfinite(verite)
    bt, bc = les_justes(tau_t, verite), les_justes(tau_c, verite)
    part = lambda b: round(float(b[note].mean()), 4) if note.any() else None  # noqa: E731
    with np.errstate(invalid="ignore"):
        change = note & ~(np.abs(tau_c - tau_t) < 1e-9)
    rj, jr = int((note & ~bt & bc).sum()), int((note & bt & ~bc).sum())
    return {"les_points_notes": int(note.sum()), "les_points_ou_les_deux_chaines_different": int(change.sum()),
            "le_temoin": part(bt), "partie_de_la_spire_corrigee": part(bc),
            "les_rates_rendus_justes": rj, "les_justes_rendus_rates": jr, "le_gain_net": rj - jr}


def la_reprise(t1: np.ndarray, c1: np.ndarray, t2: np.ndarray, c2: np.ndarray, v1: np.ndarray, v2: np.ndarray) -> dict:
    """Parmi les points notés aux deux premiers sauts dont le premier passe de raté à juste : la part juste au deuxième."""
    r = np.isfinite(v2) & ~les_justes(t1, v1) & les_justes(c1, v1)
    part = lambda b: round(float(b[r].mean()), 4) if r.any() else None  # noqa: E731
    return {"les_points": int(r.sum()), "le_temoin": part(les_justes(t2, v2)),
            "partie_de_la_spire_corrigee": part(les_justes(c2, v2))}


def la_reproduction(juges: list[dict], publie: list[dict]) -> dict:
    """Le témoin, saut par saut, contre ce que `248` publie : les points notés et la part sur la bonne spire."""
    sauts = []
    for h, (j, p) in enumerate(zip(juges, publie), start=1):
        refait = {"les_points_notes": j["les_points_notes"],
                  "la_part_sur_la_bonne_spire": (j.get("le_transfert") or {}).get("la_part_sur_la_bonne_spire")}
        pub = {"les_points_notes": p["les_points_notes"],
               "la_part_sur_la_bonne_spire": p["la_chaine"]["la_part_sur_la_bonne_spire"]}
        sauts.append({"le_saut": h, "publie": pub, "refait": refait, "reproduit": refait == pub})
    return {"les_sauts": sauts, "tous": len(sauts) == len(publie) > 0 and all(s["reproduit"] for s in sauts)}


def le_verdict(r: dict) -> dict:
    if not r.get("decidable"):
        return {"lissue": "indécidable : le témoin ne redonne pas la chaîne publiée par 248, ou une lecture est tombée "
                          "en panne"}
    if r["les_sauts"][1]["le_gain_net"] > 0:
        return {"lissue": "repartir de la spire corrigée rend le saut suivant plus juste"}
    return {"lissue": "repartir de la spire corrigée ne rend pas le saut suivant plus juste"}


def mesurer(cache: Path = LE_CACHE, maille: int = LA_MAILLE, delai: float = DELAI, sauts: int = LES_SAUTS) -> dict:
    debut = time.monotonic()
    d = telecharger(LE_SEGMENT, cache, delai)
    if isinstance(d, str):
        return {"decidable": False, "la_raison": d, "le_verdict": le_verdict({})}
    ref, valide, esp = lire_tifxyz(d)
    couches = les_couches_ordonnees(ref, valide, esp, maille, sauts)
    normales, ok = les_normales(ref, valide)
    grille = np.zeros_like(ok)
    grille[::maille, ::maille] = True
    ii, jj = np.nonzero(ok & grille)
    p, n = ref[ii, jj], normales[ii, jj]
    forme = np.full(ok.shape, np.nan)[::maille, ::maille].shape
    gi, gj = ii // maille, jj // maille

    def sur_la_grille(val):
        c = np.full(forme, np.nan)
        c[gi, gj] = val
        return c

    chemin, niveau = LES_PREDICTIONS[LA_PREDICTION]
    facteur, pred = le_facteur(chemin, niveau, delai)
    lire, stats = lecteur_du_depot(pred, cache, LA_PREDICTION, chemin, niveau, delai)

    def lire_rayon(q, nq, cote, portee):
        return lire_le_rayon(q, nq, cote, portee, facteur, pred, lire)

    cote_ = "plus" if LE_SIGNE > 0 else "moins"
    verite = [couches["les_cartes"][cote_][gi, gj, k] for k in range(sauts)]
    tau0, tau1 = np.load(LA_SPIRE_PRODUITE), np.load(LA_SPIRE_CORRIGEE)
    assert tau0.shape == tau1.shape == forme, (tau0.shape, tau1.shape, forme)
    tau0, tau1 = tau0[gi, gj], tau1[gi, gj]
    temoin = enchainer(p, n, LE_SIGNE, sauts, lire_rayon, sur_la_grille, gi, gj, True)
    corrigee = enchainer(p, n, LE_SIGNE, sauts, lire_rayon, sur_la_grille, gi, gj, True, premier=tau1)
    pt, pc = les_profondeurs(temoin, p, n), les_profondeurs(corrigee, p, n)
    np.save(LE_DEUXIEME_SAUT, sur_la_grille(pc[1]))

    publie = json.loads(CE_QUE_248_A_PUBLIE.read_text())["les_predictions"][LA_PREDICTION][LE_COTE]["les_sauts"]
    juges = [juger_le_saut(pt[h], verite[h], LE_SIGNE, h + 1) for h in range(sauts)]
    with np.errstate(invalid="ignore"):
        ecart_premier = float(np.nanmax(np.abs(temoin[0]["le_pas"] - tau0)))
        differe = ~(np.abs(tau1 - tau0) < 1e-9)
    out = {"le_segment": LE_SEGMENT, "la_prediction": LA_PREDICTION, "le_cote": LE_COTE, "la_maille": maille,
           "les_points": int(len(p)), "les_sauts_de_la_chaine": sauts,
           "les_points_ou_la_spire_corrigee_differe_de_la_produite": int(differe.sum()),
           "le_premier_saut_du_temoin_contre_la_spire_produite_ecart_max_voxels": round(ecart_premier, 4),
           "la_reproduction": la_reproduction(juges, publie),
           "les_sauts": [le_bilan_du_saut(pt[h], pc[h], verite[h]) for h in range(sauts)],
           "la_reprise": la_reprise(pt[0], pc[0], pt[1], pc[1], verite[0], verite[1]),
           "les_temoins_sans_lecture": [(j.get("le_temoin_sans_lecture") or {}).get("la_part_sur_la_bonne_spire")
                                        for j in juges],
           "la_lecture": {"chunks_lus": stats["lus"], "chunks_absents": stats["absents"],
                          "mo_lus": round(stats["octets"] / 1e6, 1), "les_pannes": stats["pannes"][:20],
                          "combien_de_pannes": len(stats["pannes"])},
           "le_deuxieme_saut": LE_DEUXIEME_SAUT.name}
    out["decidable"] = (out["la_reproduction"]["tous"] and ecart_premier == 0.0
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

    # ⭐⭐⭐⭐ LA CHAÎNE, sur la prédiction fabriquée de `248` : quatre feuilles à des écarts qui ne sont pas un pas.
    f = 4
    pred = {"shape": [128, 32, 32], "chunks": [16, 16, 16], "fill_value": 0}
    vol = np.zeros(pred["shape"], np.uint8)
    z0 = 10
    zs = [z0] + list(z0 + np.cumsum([20, 26, 20, 26]))
    for z in zs:
        vol[z, :, :] = 255

    def lire(c):
        a = np.asarray(c) * 16
        return vol[a[0]:a[0] + 16, a[1]:a[1] + 16, a[2]:a[2] + 16]

    H, W = 9, 9
    gi_, gj_ = np.nonzero(np.ones((H, W), bool))
    pts = np.stack([gj_ * 8.0 + 20.0, gi_ * 8.0 + 20.0, np.full(H * W, z0 * f + 2.0)], axis=-1)
    nor = np.tile([0.0, 0.0, 1.0], (H * W, 1))
    lectures = []

    def grille_(val):
        c = np.full((H, W), np.nan)
        c[gi_, gj_] = val
        return c

    def lire_rayon(q, nq, cote, portee):
        lectures.append(1)
        return lire_le_rayon(q, nq, cote, portee, f, pred, lire)

    vrai = [(z - z0) * f - 2.0 for z in zs[1:]]
    ch = enchainer(pts, nor, 1.0, 3, lire_rayon, grille_, gi_, gj_, True)
    lectures.clear()
    ch2 = enchainer(pts, nor, 1.0, 3, lire_rayon, grille_, gi_, gj_, True, premier=ch[0]["le_pas"])
    v("★★★★ partie du premier pas qu'elle aurait fait, la chaîne redonne ses sauts, un à un",
      all(np.allclose(a["q"], b["q"]) and np.allclose(a["n"], b["n"]) for a, b in zip(ch, ch2)))
    v("★★★ le premier saut donné n'est pas lu : trois sauts, deux lectures", len(lectures) == 2, str(len(lectures)))
    juste = np.full(H * W, vrai[0])
    faux = np.full(H * W, vrai[1])
    pj = les_profondeurs(enchainer(pts, nor, 1.0, 2, lire_rayon, grille_, gi_, gj_, True, premier=juste), pts, nor)
    pf = les_profondeurs(enchainer(pts, nor, 1.0, 2, lire_rayon, grille_, gi_, gj_, True, premier=faux), pts, nor)
    v("★★★★ un premier saut juste donné rend le deuxième juste",
      abs(np.median(pj[1]) - vrai[1]) <= f, f"{np.median(pj[1])} contre {vrai[1]}")
    v("★★★★ un premier saut qui a sauté une spire la fait sauter au deuxième aussi",
      abs(np.median(pf[1]) - vrai[2]) <= f, f"{np.median(pf[1])} contre {vrai[2]}")

    # Le bilan d'un saut : un point non noté ne compte pas, et le gain net est la différence des deux comptes.
    ver = np.array([100.0, 100.0, 100.0, 100.0, np.nan])
    t_ = np.array([100.0, 170.0, 100.0, 170.0, 0.0])
    c_ = np.array([100.0, 100.0, 170.0, 100.0, 50.0])
    b = le_bilan_du_saut(t_, c_, ver)
    v("★★★★ le bilan d'un saut compte les ratés rendus justes et les justes rendus ratés sur les seuls points notés",
      b["les_points_notes"] == 4 and b["les_rates_rendus_justes"] == 2 and b["les_justes_rendus_rates"] == 1
      and b["le_gain_net"] == 1 and b["le_temoin"] == 0.5 and b["partie_de_la_spire_corrigee"] == 0.75
      and b["les_points_ou_les_deux_chaines_different"] == 3, str(b))
    rp = la_reprise(np.array([10.0, 80.0, 80.0, 80.0]), np.array([10.0, 10.0, 10.0, 10.0]),
                    np.array([0.0, 80.0, 150.0, 0.0]), np.array([0.0, 80.0, 80.0, 0.0]),
                    np.array([10.0, 10.0, 10.0, 10.0]), np.array([80.0, 80.0, 80.0, np.nan]))
    v("★★★ la reprise ne prend que les points dont le premier saut passe de raté à juste, notés au deuxième",
      rp == {"les_points": 2, "le_temoin": 0.5, "partie_de_la_spire_corrigee": 1.0}, str(rp))

    # La reproduction et les issues.
    pub = [{"les_points_notes": 3, "la_chaine": {"la_part_sur_la_bonne_spire": 0.6667}}]
    j_ = [{"les_points_notes": 3, "le_transfert": {"la_part_sur_la_bonne_spire": 0.6667}}]
    v("★★★★ la reproduction exige les points notés ET la part publiés, saut par saut",
      la_reproduction(j_, pub)["tous"]
      and not la_reproduction([{"les_points_notes": 3, "le_transfert": {"la_part_sur_la_bonne_spire": 0.5}}], pub)["tous"]
      and not la_reproduction([{"les_points_notes": 4, "le_transfert": {"la_part_sur_la_bonne_spire": 0.6667}}],
                              pub)["tous"]
      and not la_reproduction([], pub)["tous"])
    s_ = lambda g: {"decidable": True, "les_sauts": [{"le_gain_net": 99}, {"le_gain_net": g}]}  # noqa: E731
    v("★★★★ les issues se lisent au deuxième saut : plus juste si le gain net y est positif, sinon non",
      "rend le saut suivant plus juste" in le_verdict(s_(1))["lissue"]
      and "ne rend pas" in le_verdict(s_(0))["lissue"] and "indécidable" in le_verdict({"decidable": False})["lissue"])

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
    r = mesurer()
    print(json.dumps({k: r[k] for k in r if k not in ("la_reproduction",)}, ensure_ascii=False, indent=1))
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=1))
        print(f"\nécrit : {a.json}")
    return 0 if r.get("decidable") else 2


if __name__ == "__main__":
    raise SystemExit(main())
