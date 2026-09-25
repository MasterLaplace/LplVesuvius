"""Une décision faite de la seule marche, qui pèse glissé contre juste, sait-elle où ne pas corriger ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LA DÉCISION NE SOIT APPLIQUÉE À UN SEUL BLOC. Ce qui était vu avant d'écrire : tout ce
que `257` à `263` publient, dont les parts après chaque passe de la règle fixe sur les dix blocs.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P95`. `263` montre que la règle de `261` défait plus qu'elle ne corrige là où la
spire produite est déjà juste : son seuil est fixe, un demi-feuillet, et le bruit de la marche le franchit. Un seuil fixe
ne sait pas combien de chunks ont glissé dans un bloc ; il déplace autant de bruit dans un bloc presque juste que dans un
bloc qui a glissé. Ce qui manque est de peser, dans chaque bloc, ce qu'un écart dit d'un glissement contre ce qu'il dit du
bruit.

## La décision, et le seul changement

Dans chaque bloc, les écarts de la différence des marches à son ancre, aux centres des chunks, sont lus comme un mélange de
trois gaussiennes de même largeur : le bruit autour de zéro, et une spire glissée d'un côté ou de l'autre, autour de
`± 69,458` voxels, ce que la marche retrouve d'un pas plein (`261`, `R4-F441`). Les poids et la largeur sont ajustés au
bloc par EM ; les centres ne bougent pas. Un point de la maille n'est corrigé que si son écart est plus probablement celui
d'une spire glissée que celui du bruit ; il est alors ramené de son écart, comme en `261`. ⚠ C'est le seul changement :
l'ancre, la carte aux points et le déplacement sont ceux de `261`. Aucun réglage : les centres sont mesurés, le reste est
ajusté au bloc.

## Sur quoi, et une seule passe

Les dix blocs déjà rendus : les deux de `262`, dont la différence est celle que `260` publie, et les huit de `263`, dont la
différence est relue sur leurs piles. Une passe : le juge note la carte du transfert elle-même, sans rendu. ⚠ Contrôle : la
règle fixe, refaite sur les mêmes différences, rend les parts de la première passe que `261` et `263` publient.

## Les issues, exclusives

Sur les blocs pris à pas réguliers, la part réunie après la passe contre celle d'avant ; sur les deux blocs de `262`, la
part de chacun.

- réunie, elle ne baisse pas sur les blocs réguliers, et elle monte sur les deux blocs de `262` : elle sait où ne pas
  corriger, et corrige encore là où il faut ;
- réunie, elle ne baisse pas sur les blocs réguliers, mais ne monte pas sur l'un des deux blocs de `262` au moins : elle
  ne défait plus, mais ne corrige plus assez ;
- réunie, elle baisse sur les blocs réguliers : elle défait encore.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : la décision répétée, une boucle, un autre côté, des blocs neufs.

⚠ AJOUTÉ APRÈS LA PREMIÈRE MESURE, HORS DU VERDICT : `les_deux_bosses`, deux gaussiennes à centres libres, écrites après
avoir vu l'histogramme des écarts du bloc de `257` ; elles décrivent, elles ne décident rien.

Usage :
    uv run python src/nappe/la_marche_sait_elle_ou_ne_pas_corriger.py --verifier
    uv run python src/nappe/la_marche_sait_elle_ou_ne_pas_corriger.py \\
        --json docs/mesures/la_marche_sait_elle_ou_ne_pas_corriger.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))

from la_correction_tient_elle_sur_des_blocs_reguliers import la_part_reunie  # noqa: E402
from la_marche_corrige_t_elle_la_spire_produite import (corriger, la_carte_aux_points,  # noqa: E402
                                                        la_part_juste)
from la_spire_produite_se_lit_elle_dans_le_treillis import (LA_PREDICTION, LE_BLOC, LE_COTE,  # noqa: E402
                                                            LE_DOSSIER, LES_JUGES, lerreur_jugee, lire_la_pile)
from la_spire_voisine_est_elle_a_un_pas import DEMI_PAS_EN_VOXELS, LE_CACHE, LE_SEGMENT  # noqa: E402
from le_pas_de_fenetre_en_fenetre_voit_il_la_rampe import la_grille, la_marche  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_260_A_PUBLIE = LES_MESURES / "le_pas_de_fenetre_en_fenetre_voit_il_la_rampe.json"
CE_QUE_261_A_PUBLIE = LES_MESURES / "la_marche_corrige_t_elle_la_spire_produite.json"
CE_QUE_263_A_PUBLIE = LES_MESURES / "la_correction_tient_elle_sur_des_blocs_reguliers.json"
LES_ITERATIONS = 500


def le_melange(x: np.ndarray, glissade: float, iterations: int = LES_ITERATIONS) -> dict:
    """Le bruit et les deux glissements, centres en 0 et ±`glissade`, même largeur ; poids et largeur par EM."""
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    centres = np.array([0.0, glissade, -glissade])
    w = np.array([0.9, 0.05, 0.05])
    s = max(1.4826 * float(np.median(np.abs(x - np.median(x)))), 1.0)
    for _ in range(iterations):
        z = (x[:, None] - centres[None, :]) / s
        dens = w[None, :] * np.exp(-0.5 * z * z)
        tot = dens.sum(axis=1, keepdims=True)
        r = dens / np.where(tot > 0, tot, 1.0)
        w_n = r.mean(axis=0)
        s_n = max(float(np.sqrt((r * (x[:, None] - centres[None, :]) ** 2).sum() / len(x))), 1.0)
        fini = np.allclose(w_n, w, atol=1e-10) and abs(s_n - s) < 1e-8
        w, s = w_n, s_n
        if fini:
            break
    return {"le_bruit": round(float(w[0]), 4), "glissee_au_dessus": round(float(w[1]), 4),
            "glissee_au_dessous": round(float(w[2]), 4), "la_largeur_voxels": round(s, 4), "la_glissade_voxels": glissade,
            "les_chunks": int(len(x)), "_w": w.tolist(), "_s": s}


def les_deux_bosses(x: np.ndarray, iterations: int = LES_ITERATIONS) -> dict:
    """VU APRÈS COUP, HORS DU VERDICT : deux gaussiennes de même largeur, centres libres, partant des quartiles.

    Elle dit si les écarts d'un bloc forment deux populations, et à quelle distance l'une de l'autre ; elle ne dit pas
    laquelle est sur la bonne spire.
    """
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    c = np.array([np.quantile(x, 0.25), np.quantile(x, 0.75)])
    w = np.array([0.5, 0.5])
    s = max(float(np.std(x)) / 2.0, 1.0)
    for _ in range(iterations):
        z = (x[:, None] - c[None, :]) / s
        dens = w[None, :] * np.exp(-0.5 * z * z)
        tot = dens.sum(axis=1, keepdims=True)
        r = dens / np.where(tot > 0, tot, 1.0)
        n = np.maximum(r.sum(axis=0), 1e-12)
        c_n = (r * x[:, None]).sum(axis=0) / n
        w_n = n / len(x)
        s_n = max(float(np.sqrt((r * (x[:, None] - c_n[None, :]) ** 2).sum() / len(x))), 1.0)
        fini = np.allclose(c_n, c, atol=1e-8) and abs(s_n - s) < 1e-8
        c, w, s = c_n, w_n, s_n
        if fini:
            break
    o = np.argsort(c)
    return {"les_centres_voxels": [round(float(c[i]), 4) for i in o], "les_poids": [round(float(w[i]), 4) for i in o],
            "la_largeur_voxels": round(s, 4), "lecart_voxels": round(float(c[o[1]] - c[o[0]]), 4)}


def la_decision(ecart: np.ndarray, melange: dict) -> np.ndarray:
    """Les points dont l'écart est plus probablement celui d'une spire glissée que celui du bruit."""
    w, s, g = np.array(melange["_w"]), melange["_s"], melange["la_glissade_voxels"]
    ok = np.isfinite(ecart)
    x = np.where(ok, ecart, 0.0)
    p = [w[k] * np.exp(-0.5 * ((x - c) / s) ** 2) for k, c in enumerate((0.0, g, -g))]
    return ok & (np.maximum(p[1], p[2]) > p[0])


def corriger_decide(tau: np.ndarray, ecart: np.ndarray, decide: np.ndarray) -> np.ndarray:
    t = tau.copy()
    t[decide] = tau[decide] - ecart[decide]
    return t


def le_bilan(tau0, tau1, verite, err, dedans, decide) -> dict:
    note = dedans & np.isfinite(err)
    with np.errstate(invalid="ignore"):
        rate = np.abs(err) >= DEMI_PAS_EN_VOXELS
        e1 = tau1 - verite
        return {"les_points_corriges": int((decide & dedans).sum()),
                "apres": la_part_juste(tau1, verite, dedans),
                "les_rates_rendus_justes": int((note & rate & (np.abs(e1) < DEMI_PAS_EN_VOXELS)).sum()),
                "les_justes_rendus_rates": int((note & ~rate & (np.abs(e1) >= DEMI_PAS_EN_VOXELS)).sum())}


def un_bloc(nom: str, by: int, bx: int, diff: np.ndarray, tau0, err, glissade: float) -> dict:
    verite = tau0 - err
    ancre = float(np.nanmedian(diff))
    ecart, dedans = la_carte_aux_points(diff - ancre, by, bx, tau0.shape)
    ecart = np.where(dedans, ecart, np.nan)
    melange = le_melange(diff - ancre, glissade)
    decide = la_decision(ecart, melange)
    t_fixe, fixe = corriger(tau0, ecart)
    r = {"la_rangee": by, "la_colonne": bx, "lancre_voxels": round(ancre, 4),
         "le_melange": {k: v for k, v in melange.items() if not k.startswith("_")},
         "avant": la_part_juste(tau0, verite, dedans),
         "la_regle_fixe": le_bilan(tau0, t_fixe, verite, err, dedans, fixe),
         "la_decision": le_bilan(tau0, corriger_decide(tau0, ecart, decide), verite, err, dedans, decide),
         "vu_apres_coup": {"les_deux_bosses": les_deux_bosses(diff - ancre)},
         "la_difference": [[None if not np.isfinite(v) else round(float(v), 2) for v in rr] for rr in diff]}
    return r


def la_difference_relue(by: int, bx: int) -> list:
    """La différence des marches de la spire produite et du segment, relue sur les piles que `263` a rendues."""
    s = la_marche(lire_la_pile(LE_DOSSIER / "le_segment_reduit" / f"bloc_{by}_{bx}"), by, bx)["la_profondeur"]
    p = la_marche(lire_la_pile(LE_DOSSIER / "la_spire_produite" / f"bloc_{by}_{bx}"), by, bx)["la_profondeur"]
    return [[None if not np.isfinite(v) else float(v) for v in rr] for rr in (p - s)]


def le_controle(blocs: dict, publie: dict) -> dict:
    """La règle fixe refaite contre les parts de première passe publiées ; seuls comptent les blocs que le juge note."""
    ecarts = {n: (blocs[n]["la_regle_fixe"]["apres"]["la_part_sur_la_bonne_spire"], p) for n, p in publie.items()}
    return {"les_parts": ecarts, "tient": all(a == p for a, p in ecarts.values())}


def les_reunions(blocs: dict, noms: list[str]) -> dict:
    sel = {n: blocs[n] for n in noms if blocs[n]["avant"]["la_part_sur_la_bonne_spire"] is not None}
    out = {"les_blocs": len(sel), "avant": la_part_reunie(sel, "avant")}
    for regle in ("la_regle_fixe", "la_decision"):
        vue = {n: {"apres": b[regle]["apres"]} for n, b in sel.items()}
        out[regle] = {"apres": la_part_reunie(vue, "apres"),
                      "les_rates_rendus_justes": sum(b[regle]["les_rates_rendus_justes"] for b in sel.values()),
                      "les_justes_rendus_rates": sum(b[regle]["les_justes_rendus_rates"] for b in sel.values()),
                      "les_points_corriges": sum(b[regle]["les_points_corriges"] for b in sel.values())}
    return out


def mesurer(cache: Path = LE_CACHE) -> dict:
    debut = time.monotonic()
    d260 = json.loads(CE_QUE_260_A_PUBLIE.read_text())
    d261 = json.loads(CE_QUE_261_A_PUBLIE.read_text())
    d263 = json.loads(CE_QUE_263_A_PUBLIE.read_text())
    glissade = float(d261["le_signe"]["lecart_retrouve_voxels"])
    tau0 = np.load(cache / f"transfert_suivante_{LE_SEGMENT}_{LA_PREDICTION}_{LE_COTE}.npy")
    err = lerreur_jugee(tau0, [np.load(cache / f"verite_{LE_SEGMENT}_{j}_{LE_COTE}.npy") for j in LES_JUGES])
    entrees, publie = {}, {}
    for nom, b in d260["les_blocs"].items():
        entrees[nom] = (b["la_rangee"], b["la_colonne"], la_grille(b["les_cartes"]["la_difference"]))
        publie[nom] = d261["les_blocs"][nom]["apres"]["la_part_sur_la_bonne_spire"]
    reguliers = [(n, b["la_rangee"], b["la_colonne"]) for n, b in d263["les_blocs"].items()]
    with ProcessPoolExecutor(max_workers=4) as pool:
        relues = list(pool.map(la_difference_relue, [r for _, r, _ in reguliers], [c for _, _, c in reguliers]))
    for (n, by, bx), d in zip(reguliers, relues):
        entrees[n] = (by, bx, la_grille(d))
        p1 = d263["les_blocs"][n]["les_passes"][0]["la_part_sur_la_bonne_spire_apres"]
        if p1 is not None:
            publie[n] = p1
    blocs = {n: un_bloc(n, by, bx, diff, tau0, err, glissade) for n, (by, bx, diff) in entrees.items()}
    out = {"la_glissade_voxels": glissade, "le_controle": le_controle(blocs, publie), "les_blocs": blocs,
           "les_reguliers": les_reunions(blocs, [n for n, _, _ in reguliers]),
           "les_choisis": les_reunions(blocs, list(d260["les_blocs"]))}
    out["les_secondes"] = round(time.monotonic() - debut, 1)
    out["decidable"] = out["le_controle"]["tient"]
    return out


def le_verdict(r: dict) -> dict:
    if not r.get("decidable"):
        return {"lissue": "indécidable : la règle fixe refaite ne rend pas les parts publiées"}
    reg = r["les_reguliers"]
    tient = reg["la_decision"]["apres"] >= reg["avant"]
    monte = {n: r["les_blocs"][n]["la_decision"]["apres"]["la_part_sur_la_bonne_spire"]
             > r["les_blocs"][n]["avant"]["la_part_sur_la_bonne_spire"] for n in ("le_bloc_de_257", "le_bloc_de_259")}
    if tient and all(monte.values()):
        return {"lissue": "elle sait où ne pas corriger, et corrige encore là où il faut", "monte": monte}
    if tient:
        return {"lissue": "elle ne défait plus, mais ne corrige plus assez", "monte": monte}
    return {"lissue": "elle défait encore", "monte": monte}


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

    g = 69.458
    rng = np.random.default_rng(7)
    bruit = rng.normal(0.0, 15.0, 256)
    m0 = le_melange(bruit, g)
    v("★★★★ sur du bruit seul, le mélange ne voit presque aucune spire glissée",
      lambda: m0["glissee_au_dessus"] + m0["glissee_au_dessous"] < 0.03 and 12.0 < m0["la_largeur_voxels"] < 18.0, str(m0))
    xs = np.linspace(-50, 50, 201)
    v("★★★★ sur du bruit seul, aucun écart de moins de cinquante voxels n'est corrigé",
      lambda: not la_decision(xs, m0).any())
    v("★★★ alors que le seuil fixe en corrige", lambda: (np.abs(xs) >= DEMI_PAS_EN_VOXELS).any())
    glisse = np.concatenate([rng.normal(0.0, 15.0, 180), rng.normal(g, 15.0, 76)])
    m1 = le_melange(glisse, g)
    v("★★★★ quand un chunk sur trois a glissé, le mélange en retrouve le poids",
      lambda: abs(m1["glissee_au_dessus"] - 76 / 256) < 0.05 and m1["glissee_au_dessous"] < 0.03, str(m1))
    v("★★★★ et la décision corrige alors un écart d'un demi-feuillet et plus, du bon côté",
      lambda: la_decision(np.array([45.0, 69.0]), m1).all() and not la_decision(np.array([-45.0, 10.0]), m1).any())
    v("★★★ un écart absent n'est jamais corrigé", lambda: not la_decision(np.array([np.nan]), m1).any())
    deux = les_deux_bosses(np.concatenate([rng.normal(-40.0, 12.0, 128), rng.normal(32.0, 12.0, 128)]))
    v("★★★ deux populations sont retrouvées là où elles sont, et une seule ne s'écarte pas",
      lambda: abs(deux["lecart_voxels"] - 72.0) < 6.0 and les_deux_bosses(bruit)["lecart_voxels"] < 30.0, str(deux))
    tau = np.full((5, 5), 72.0)
    ec = np.full((5, 5), np.nan)
    ec[2, 2] = 60.0
    dec = la_decision(ec, m1)
    v("★★★ la correction ramène de leur écart les seuls points décidés",
      lambda: corriger_decide(tau, ec, dec)[2, 2] == 12.0 and (corriger_decide(tau, ec, dec) == 72.0).sum() == 24)
    v("★★★★ le contrôle exige l'égalité sur chaque bloc publié",
      lambda: le_controle({"a": {"la_regle_fixe": {"apres": {"la_part_sur_la_bonne_spire": 0.5}}}}, {"a": 0.5})["tient"]
      and not le_controle({"a": {"la_regle_fixe": {"apres": {"la_part_sur_la_bonne_spire": 0.5}}}}, {"a": 0.51})["tient"])

    def faux(avant, apres, a257, a259):
        blocs = {"le_bloc_de_257": {"avant": {"la_part_sur_la_bonne_spire": 0.5},
                                    "la_decision": {"apres": {"la_part_sur_la_bonne_spire": a257}}},
                 "le_bloc_de_259": {"avant": {"la_part_sur_la_bonne_spire": 0.6},
                                    "la_decision": {"apres": {"la_part_sur_la_bonne_spire": a259}}}}
        return le_verdict({"decidable": True, "les_blocs": blocs,
                           "les_reguliers": {"avant": avant, "la_decision": {"apres": apres}}})["lissue"]
    v("★★★★ les issues : sait, ne corrige plus assez, défait encore",
      lambda: "sait où ne pas corriger" in faux(0.9, 0.9, 0.6, 0.7) and "plus assez" in faux(0.9, 0.91, 0.5, 0.7)
      and "défait encore" in faux(0.9, 0.89, 0.6, 0.7))

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
    print(json.dumps({k: r[k] for k in ("le_controle", "les_reguliers", "les_choisis", "le_verdict")},
                     indent=1, ensure_ascii=False))
    return 0 if r.get("decidable") else 2


if __name__ == "__main__":
    raise SystemExit(main())
